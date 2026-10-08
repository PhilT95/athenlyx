# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage 1: build the static site (zensical + SEO post-processing)
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS site-build
WORKDIR /src

RUN pip install --no-cache-dir zensical==0.0.57 mkdocs-ultralytics-plugin

COPY zensical.toml ./
COPY docs ./docs
COPY includes ./includes
COPY overrides ./overrides
COPY scripts/ultralytics.py ./scripts/ultralytics.py

RUN zensical build --strict \
 && python3 scripts/ultralytics.py


# ---------------------------------------------------------------------------
# Target "api": FastAPI content API (reads the built search index)
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS api
WORKDIR /app

COPY api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY api/main.py api/search.py ./
COPY --from=site-build /src/site /www

ENV SITE_DIR=/www
RUN useradd --system --no-create-home athenlyx
USER athenlyx

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health').status == 200 else 1)"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


# ---------------------------------------------------------------------------
# Target "web": nginx serving the static site and proxying /api/ to the API
# ---------------------------------------------------------------------------
FROM nginx:1-alpine AS web

COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=site-build /src/site /usr/share/nginx/html

EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget -q --spider http://127.0.0.1/ || exit 1
