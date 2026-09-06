"""
Search index loader and BM25 ranking engine.

Reads the Zensical-generated search/search_index.json from the built site
directory and provides full-text search with relevance ranking.

BM25 parameters (Okapi BM25):
  k1 = 1.5  — term frequency saturation. Higher values give more weight to
               repeated terms; lower values saturate faster.
  b  = 0.75 — document length normalization. 1.0 fully normalizes by length;
               0.0 disables length normalization.
"""

import json
import math
import re
import threading
from pathlib import Path
from typing import Optional

# BM25 tuning parameters
_K1 = 1.5
_B = 0.75

# Title matches are weighted more heavily than body matches.
_TITLE_WEIGHT = 4.0

# Exact phrase match multiplier applied to the total score.
_PHRASE_BONUS = 1.5


class SearchIndex:
    def __init__(self, site_dir: str) -> None:
        self._site_dir = Path(site_dir)
        self._lock = threading.RLock()

        # Processed document list — each entry mirrors the search_index.json
        # "docs" array plus pre-tokenized fields for fast scoring.
        self._docs: list[dict] = []

        # Page-level index keyed by the base URL path (no anchor).
        self._pages: dict[str, dict] = {}

        # Average body token count across all documents; used in BM25 length
        # normalization.
        self._avg_doc_len: float = 1.0

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def load(self) -> None:
        """Load (or reload) the search index from disk.

        Safe to call from a background thread after a deployment; the lock
        ensures reads are never served against a partially-updated index.
        """
        index_path = self._site_dir / "search" / "search_index.json"
        with open(index_path, encoding="utf-8") as fh:
            data = json.load(fh)

        raw_docs: list[dict] = data.get("docs", [])

        # Pre-tokenize every document so scoring doesn't re-parse strings on
        # every query.
        processed: list[dict] = []
        total_tokens = 0
        for doc in raw_docs:
            body_tokens = _tokenize(doc.get("text", ""))
            title_tokens = _tokenize(doc.get("title", ""))
            total_tokens += len(body_tokens)
            processed.append({
                **doc,
                "_body_tokens": body_tokens,
                "_title_tokens": title_tokens,
            })

        avg = total_tokens / len(processed) if processed else 1.0
        page_index = _build_page_index(raw_docs)

        with self._lock:
            self._docs = processed
            self._pages = page_index
            self._avg_doc_len = avg

    def search(self, query: str, limit: int = 10) -> list[dict]:
        """Return up to *limit* results ranked by BM25 relevance score."""
        terms = list(set(_tokenize(query)))
        if not terms:
            return []

        with self._lock:
            docs = self._docs
            avg_len = self._avg_doc_len

        n_docs = len(docs)
        df = _document_frequencies(docs, terms)
        phrase = query.lower()

        scored: list[tuple[float, dict]] = []
        for doc in docs:
            score = _bm25(doc, terms, df, n_docs, avg_len)
            if score <= 0:
                continue

            # Bonus for an exact phrase appearing anywhere in title or body.
            combined = (doc.get("title", "") + " " + doc.get("text", "")).lower()
            if phrase in combined:
                score *= _PHRASE_BONUS

            location = doc.get("location", "")
            scored.append((score, {
                "url": "/" + location,
                "title": doc.get("title", ""),
                "score": round(score, 4),
                "excerpt": _excerpt(doc.get("text", ""), terms),
            }))

        scored.sort(key=lambda t: t[0], reverse=True)
        return [entry for _, entry in scored[:limit]]

    def list_pages(self) -> list[dict]:
        """Return a summary list of every top-level page."""
        with self._lock:
            pages = self._pages

        return [
            {
                "url": page["url"],
                "title": page["title"],
                "section_count": len(page["sections"]),
            }
            for page in pages.values()
        ]

    def get_page(self, path: str) -> Optional[dict]:
        """Return a page's full content by its URL path, or None if not found."""
        key = path.strip("/")
        with self._lock:
            pages = self._pages

        # Direct lookup first.
        if key in pages:
            return pages[key]

        # Fallback: normalise both sides and retry.
        for stored_key, page in pages.items():
            if stored_key.strip("/") == key:
                return page

        return None

    @property
    def loaded(self) -> bool:
        """True once the index has been populated at least once."""
        with self._lock:
            return bool(self._docs)


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())


def _build_page_index(raw_docs: list[dict]) -> dict[str, dict]:
    pages: dict[str, dict] = {}
    for doc in raw_docs:
        location = doc.get("location", "")
        base = location.split("#")[0].rstrip("/")
        if base not in pages:
            pages[base] = {
                "url": "/" + base + "/" if base else "/",
                "title": "",
                "text": "",
                "sections": [],
            }

        if "#" in location:
            anchor = location.split("#", 1)[1]
            pages[base]["sections"].append({
                "anchor": anchor,
                "title": doc.get("title", ""),
                "text": doc.get("text", ""),
            })
        else:
            # Page-level entry — prefer non-empty titles.
            pages[base]["title"] = doc.get("title", "") or pages[base]["title"]
            pages[base]["text"] = doc.get("text", "")

    return pages


def _document_frequencies(docs: list[dict], terms: list[str]) -> dict[str, int]:
    """Count how many documents contain each term (for IDF computation)."""
    df: dict[str, int] = {t: 0 for t in terms}
    for doc in docs:
        token_set = set(doc["_body_tokens"]) | set(doc["_title_tokens"])
        for term in terms:
            if term in token_set:
                df[term] += 1
    return df


def _bm25(
    doc: dict,
    terms: list[str],
    df: dict[str, int],
    n_docs: int,
    avg_doc_len: float,
) -> float:
    body_tokens = doc["_body_tokens"]
    title_tokens = doc["_title_tokens"]
    doc_len = len(body_tokens) or 1
    score = 0.0

    for term in terms:
        doc_freq = df.get(term, 0)
        if doc_freq == 0:
            continue

        # Robertson/Sparck Jones IDF with a smoothing floor of 1.
        idf = math.log((n_docs - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0)

        # BM25 TF for body text.
        tf = body_tokens.count(term)
        normed_tf = (tf * (_K1 + 1)) / (
            tf + _K1 * (1 - _B + _B * doc_len / avg_doc_len)
        )
        score += idf * normed_tf

        # Title boost — simple TF (no length norm, titles are short and uniform).
        title_tf = title_tokens.count(term)
        if title_tf:
            score += idf * title_tf * _TITLE_WEIGHT

    return score


def _excerpt(text: str, terms: list[str], max_len: int = 220) -> str:
    """Extract a short snippet from *text* centred around the first term hit."""
    lower = text.lower()
    start = 0
    for term in terms:
        pos = lower.find(term)
        if pos != -1:
            start = max(0, pos - 60)
            break

    snippet = text[start : start + max_len]
    prefix = "..." if start > 0 else ""
    suffix = "..." if start + max_len < len(text) else ""
    return (prefix + snippet + suffix).strip()
