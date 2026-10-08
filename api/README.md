# AthenlyX Content API

A small, read-only REST API that exposes the documentation content as JSON.
It exists for **automated consumers** (bots, AI agents, scripts) that prefer
structured data over crawling HTML.

It is **not** the search box on the website. That search runs in the visitor's
browser and is provided by Zensical. This API is a separate, server-side
interface that reads the same data (see [Relationship to the site search](#relationship-to-the-site-search)).

- [Overview](#overview)
- [Files](#files)
- [How it runs](#how-it-runs)
- [Configuration](#configuration)
- [Endpoints](#endpoints)
- [How the code works](#how-the-code-works)
- [Search ranking (BM25)](#search-ranking-bm25)
- [Data flow and lifecycle](#data-flow-and-lifecycle)
- [Security notes](#security-notes)
- [Running and testing locally](#running-and-testing-locally)
- [Known limitations](#known-limitations)

---

## Overview

```
 search.json (built by Zensical) ──load once at startup──▶ in-memory index ──▶ JSON responses
```

- Python, [FastAPI](https://fastapi.tiangolo.com/), served by `uvicorn`.
- **No database and no writes.** All data comes from the `search.json` file
  that Zensical generates when the site is built.
- The site and its index are **baked into the container image**. The index
  therefore always matches the site version in the same image. To publish new
  content, the container is replaced (done by the [updater](../updater/README.md)).
  The API never reloads the index while running.

## Files

| File | Purpose |
|---|---|
| `main.py` | The FastAPI application: routes, startup (loading the index), error handling. |
| `search.py` | `SearchIndex`: loads `search.json`, builds the page index, ranks search results. |
| `requirements.txt` | Python dependencies (`fastapi`, `uvicorn`). |
| `api.env.example`, `api.service` | **Legacy.** Old systemd/env setup for running without Docker. Not used by the Docker setup and planned for removal. |

The image is built from the `api` stage of the repository's root `Dockerfile`
(not from a Dockerfile in this directory), because the image needs the built
site from an earlier stage.

## How it runs

In the Docker setup the API runs in the `api` service of `compose.yaml`:

- Listens on port **8000** inside the container, and has **no published port**.
- Is reachable only from the `web` container (nginx), which forwards every
  request under `/api/` to `http://api:8000`. The host nginx only talks to `web`.
- Runs as a non-root user (`athenlyx`) with a read-only root filesystem.
- Has a Docker `HEALTHCHECK` that calls `/api/v1/health` every 30 seconds.
  The `web` service waits for it to be healthy before starting, and the
  updater uses it to decide whether a new version works.

Start command (from the Dockerfile): `uvicorn main:app --host 0.0.0.0 --port 8000`

## Configuration

| Variable | Default | Meaning |
|---|---|---|
| `SITE_DIR` | `/www` | Directory containing the built site. The API reads `search.json` from it. The Dockerfile copies the site to `/www` and sets this variable. |

There is nothing else to configure. There are no secrets and no tokens.

## Endpoints

All endpoints use `GET`. Replace the host with your own domain.

### `GET /api/v1/health`

Liveness and readiness check.

```json
{ "status": "ok", "index_loaded": true }
```

`index_loaded` is `false` if no index could be loaded (see [startup](#startup-lifespan)).
The endpoint itself still answers `200`, so the container counts as healthy
even without an index. The other endpoints answer `503` in that case.

### `GET /api/v1/pages`

Lists every documentation page.

```json
{
  "count": 59,
  "pages": [
    { "url": "/index.html/", "title": "Welcome to Athenlyx.com", "section_count": 3 }
  ]
}
```

### `GET /api/v1/pages/{path}`

Returns one page, with its full text and all of its sections. `{path}` is the
page's URL path without the leading slash, for example
`/api/v1/pages/infra-mgmt/linux-admin/commands.html`.

```json
{
  "url": "/infra-mgmt/linux-admin/commands.html/",
  "title": "Linux commands",
  "text": "...page-level text...",
  "sections": [
    { "anchor": "curl", "title": "curl", "text": "..." }
  ]
}
```

Responds `404` if the page does not exist.

### `GET /api/v1/search`

Full-text search across all pages and sections, ranked by relevance.

| Parameter | Required | Default | Meaning |
|---|---|---|---|
| `q` | yes | | Search query (at least 1 character). |
| `limit` | no | 10 | Maximum number of results (1 to 50). |

```
GET /api/v1/search?q=docker+network&limit=3
```
```json
{
  "query": "docker network",
  "count": 3,
  "results": [
    {
      "url": "/infra-mgmt/linux-admin/rhel-alma/docker_network_troubleshooting.html#step-1-...",
      "title": "Step 1: Test the network the container uses",
      "score": 11.3021,
      "excerpt": "...text around the first matching word..."
    }
  ]
}
```

- Each result is a **page or a single section** (the URL contains an `#anchor` for sections).
- `score` is the BM25 relevance score. It has no fixed upper bound and is only
  meaningful for comparing results of the same query. Consumers such as AI
  agents can use it to choose the best matches.
- `excerpt` is about 220 characters around the first matching term.

### Error responses

| Status | When |
|---|---|
| `404` | `/pages/{path}` for a page that does not exist. |
| `422` | Invalid parameters (for example a missing `q`, or `limit` outside 1 to 50). Standard FastAPI validation. |
| `503` | No index is loaded (the site was not built into the image, or `search.json` is missing). |

### Interactive documentation

FastAPI generates `/docs` (Swagger UI) and `/openapi.json` inside the
container. In the standard setup these are **not reachable from outside**,
because the `web` nginx only forwards `/api/` to the API. To expose them, add a
proxy rule for them, or move the API's docs under `/api/`.

## How the code works

### `main.py`

**Module-level setup**

```python
SITE_DIR = os.environ.get("SITE_DIR", "/www")
index = SearchIndex(SITE_DIR)
```

A single `SearchIndex` instance is created when the module is imported. All
requests share it.

**Startup (`lifespan`)**<a id="startup-lifespan"></a>

`lifespan` is an async context manager that FastAPI runs once when the app
starts. It calls `index.load()`:

- On success it logs how many documents were loaded.
- If the index file does not exist (`FileNotFoundError`) it logs a warning and
  **still starts**. The app is then up, but `index.loaded` is `False`.

**Route handlers**

Every route that needs data first checks `index.loaded`. If it is `False`, the
handler raises `HTTPException(503)`. Otherwise it delegates to a `SearchIndex`
method and returns the result. The route functions contain no logic beyond
validation and error mapping. The work is done in `search.py`.

### `search.py`

#### `SearchIndex`

Holds the in-memory data. State (all set by `load()`):

| Attribute | Type | Content |
|---|---|---|
| `_docs` | `list[dict]` | Every entry of `search.json`, plus pre-computed token lists `_body_tokens` and `_title_tokens`. Used by `search()`. |
| `_pages` | `dict[str, dict]` | One entry per page, keyed by its path without anchor. Holds the page text and a list of its sections. Used by `list_pages()` and `get_page()`. |
| `_avg_doc_len` | `float` | Average number of body tokens per document. Needed for BM25 length normalization. |
| `_lock` | `RLock` | Guards the three attributes above (see below). |

**`load()`**

1. Opens `SITE_DIR/search.json`. If it does not exist, it falls back to
   `SITE_DIR/search/search_index.json` (the MkDocs layout).
2. Reads the entries from the `items` key (Zensical). If missing, it uses
   `docs` (MkDocs).
3. For each entry it computes the token lists, which are the lowercase words
   (`_tokenize`) of the body text and of the title. Doing this once at load
   time means a search does not need to parse text.
4. Computes `_avg_doc_len`.
5. Builds the page index with `_build_page_index`.
6. Under the lock, replaces `_docs`, `_pages` and `_avg_doc_len` in one step.

The entries in `search.json` look like this. A page and each of its sections
are separate entries, and sections have an `#anchor` in `location`:

```json
{ "location": "guide.html",        "title": "Guide",  "text": "..." }
{ "location": "guide.html#step-1", "title": "Step 1", "text": "..." }
```

**`search(query, limit)`** is described in [Search ranking](#search-ranking-bm25).

**`list_pages()`** returns `{url, title, section_count}` for each page.

**`get_page(path)`** strips slashes from `path` and looks it up in `_pages`
directly. If that fails, it compares against every key with slashes stripped
(a fallback for trailing-slash differences). It returns `None` if nothing
matches.

**`loaded`** is `True` if `_docs` is not empty.

#### Why a lock?

`load()` swaps in new data while other threads (request handlers) may read it.
The lock ensures a reader never sees a half-updated index. Readers copy the
references they need while holding the lock and then work on those, so the lock
is held only briefly. In the current design the index is loaded once at startup,
so this is a safety measure.

#### `_build_page_index(raw_docs)`

Groups entries by page. For each entry:

- `base` is the `location` without the `#anchor` and without a trailing `/`.
- An entry with `#` is added to the page's `sections` list as
  `{anchor, title, text}`.
- An entry without `#` is the page-level entry. It sets the page's `title`
  and `text`.

The `url` shown for a page is built as `"/" + base + "/"`.

#### `_tokenize(text)`

```python
re.findall(r"\b\w+\b", text.lower())
```

Lowercases the text and returns every word, where a word is a sequence of
letters, digits or underscores. There is no stemming (`network` and `networks`
are different terms) and no stop-word list. Rare-word weighting (IDF, below)
reduces the influence of very common words.

## Search ranking (BM25)

BM25 (Okapi BM25) is a standard ranking function used by most keyword search
engines. This implementation is in `search()` and `_bm25()`.

### Procedure for a query

1. Tokenize the query into a set of unique terms. If there are no terms, return no results.
2. Compute the **document frequency** for each term: in how many entries the
   term appears in the title or the body (`_document_frequencies`).
3. Score every entry with `_bm25()`.
4. Discard entries with score 0.
5. If the **entire query string** (lowercased) appears in the title plus body, multiply the score by `_PHRASE_BONUS` (1.5).
6. Sort by score, highest first, and return the first `limit` entries with an excerpt.

### The score of one entry

For each query term that appears in the collection:

```
idf        = ln( (N - df + 0.5) / (df + 0.5) + 1 )
body_score = idf * ( tf * (k1 + 1) ) / ( tf + k1 * (1 - b + b * len / avg_len) )
title_score = idf * title_tf * TITLE_WEIGHT
```

and the entry's score is the sum over all terms of `body_score + title_score`.

| Symbol | Meaning |
|---|---|
| `N` | Total number of entries. |
| `df` | Number of entries containing the term. |
| `tf` | Number of times the term appears in this entry's body. |
| `len`, `avg_len` | Body length of this entry and the average length, in tokens. |
| `title_tf` | Number of times the term appears in the title. |

| Constant | Value | Effect |
|---|---|---|
| `_K1` | 1.5 | Saturation of term frequency. A higher value gives repeated terms more weight. |
| `_B` | 0.75 | Length normalization. `0` disables it, `1` is full normalization. |
| `_TITLE_WEIGHT` | 4.0 | Multiplier for title matches. Title matches use plain term frequency, because titles are short. |
| `_PHRASE_BONUS` | 1.5 | Multiplier when the exact query phrase appears. |

**In practice:** rare words matter more, repetition helps with diminishing
returns, long entries are slightly penalized, and title matches are strongly
favored.

### Excerpts

`_excerpt(text, terms)` finds the first query term in the text. It starts 60
characters before the match and returns up to 220 characters, adding `...` at
the start or end when the text is cut.

### Performance

Scoring touches every entry for every query. With a few hundred entries this
takes milliseconds. If the site grows to tens of thousands of entries, an
inverted index would be needed.

## Data flow and lifecycle

```
Docker build (site-build stage)
  zensical build ──▶ /src/site/search.json
        │
        └─ COPY into the api image as /www/search.json
                │
Container start │
  uvicorn imports main.py ──▶ SearchIndex(SITE_DIR)
  lifespan ──▶ index.load() ──▶ tokenized docs + page index in memory
                │
Requests        ▼
  /api/v1/search ──▶ index.search()  ──▶ JSON
  /api/v1/pages  ──▶ index.list_pages() / get_page()
```

On a site update the updater builds a new image and replaces the container.
The new container loads the new index at startup. There is no reload endpoint.

## Security notes

- **Read-only.** There are no endpoints that change state, so no
  authentication is needed.
- **No user-supplied file paths.** `get_page()` looks up a key in a dictionary
  and never touches the filesystem, so there is no path traversal.
- **CORS.** The headers `Access-Control-Allow-Origin: *` etc. are set by
  `docker/nginx.conf`, not by the API itself. Browser-based clients on other
  origins are allowed to call it.
- **Content is public already.** The API only exposes text that is on the website.
- **Abuse protection** (rate limiting) is not part of the API. Apply it in the
  host nginx or in the WAF in front of it if you need it.

## Running and testing locally

With the full stack (recommended):

```bash
docker compose up --build
curl 'http://127.0.0.1:6559/api/v1/search?q=docker&limit=3'
```

Without Docker, against a locally built site:

```bash
zensical build                       # creates ./site/search.json
cd api
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
SITE_DIR=../site uvicorn main:app --port 8000
curl 'http://127.0.0.1:8000/api/v1/health'
```

There is no automated test suite for the API yet.

## Known limitations

- **HTML in the text.** Zensical stores section text as HTML (for example
  `<p>...</p>`). The tokenizer does not strip tags, so tag names such as `p`
  can count as search terms, and excerpts can contain raw HTML.
- **Page URLs.** `_build_page_index` builds URLs as `/<path>/`, which gives
  `/index.html/` for a site that uses `.html` URLs (`use_directory_urls = false`).
  `get_page()` accepts the path with or without the trailing slash, but the
  `url` field in `/pages` is not the real URL of the page.
- **No stemming.** `network` and `networks` are different terms.
- **Single process, in-memory.** Every worker process loads its own copy of the
  index. With the default single `uvicorn` process this is not an issue.
