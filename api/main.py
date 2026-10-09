"""
AthenlyX API

A FastAPI application exposing the documentation content:

  GET  /api/v1/health         — health check
  GET  /api/v1/pages          — list all documentation pages
  GET  /api/v1/pages/{path}   — get content and sections of a single page
  GET  /api/v1/search?q=      — full-text search with BM25 relevance ranking

Configuration is read from environment variables (SITE_DIR).
Run with: uvicorn main:app --host 0.0.0.0 --port 8000
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, status

from search import SearchIndex

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SITE_DIR = os.environ.get("SITE_DIR", "/www")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Search index (module-level singleton)
# ---------------------------------------------------------------------------

index = SearchIndex(SITE_DIR)

# ---------------------------------------------------------------------------
# Application lifecycle
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info("Loading search index from %s …", SITE_DIR)
    try:
        index.load()
        log.info("Search index loaded (%d documents).", len(index._docs))
    except FileNotFoundError:
        log.warning(
            "search index not found at startup — the site may not have been "
            "built yet."
        )
    yield


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AthenlyX API",
    description=(
        "Public REST API for querying AthenlyX documentation content. "
        "Designed for bots and AI agents that prefer structured data over HTML crawling."
    ),
    version="1.0.0",
    lifespan=lifespan,
    # Disable the default /docs and /redoc if you do not want them public.
    # docs_url=None,
    # redoc_url=None,
)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get(
    "/api/v1/health",
    summary="Health check",
    tags=["Meta"],
)
def health():
    return {
        "status": "ok",
        "index_loaded": index.loaded,
    }


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------


@app.get(
    "/api/v1/pages",
    summary="List all pages",
    description="Returns a summary list of every top-level documentation page.",
    tags=["Content"],
)
def list_pages():
    if not index.loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search index not yet available. Try again later.",
        )
    pages = index.list_pages()
    return {"count": len(pages), "pages": pages}


@app.get(
    "/api/v1/pages/{path:path}",
    summary="Get a page",
    description=(
        "Returns the full text, title, and all sub-sections for a single page. "
        "Use the URL path as returned by /api/v1/pages (without the leading slash)."
    ),
    tags=["Content"],
)
def get_page(path: str):
    if not index.loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search index not yet available. Try again later.",
        )
    page = index.get_page(path)
    if page is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found.")
    return page


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


@app.get(
    "/api/v1/search",
    summary="Search documentation",
    description=(
        "Full-text search across all documentation pages and sections. "
        "Results are ranked by BM25 relevance score and include a short excerpt "
        "centred around the first matching term. "
        "The `score` field can be used by AI agents to select the most relevant "
        "context to include in a prompt."
    ),
    tags=["Content"],
)
def search(
    q: str = Query(..., min_length=1, description="Search query."),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of results to return."),
):
    if not index.loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search index not yet available. Try again later.",
        )
    results = index.search(q, limit=limit)
    return {
        "query": q,
        "count": len(results),
        "results": results,
    }
