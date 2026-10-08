# Updater: fetches the repository, builds the images and recreates the site
# containers through a restricted Docker socket proxy.
# Build context is the repository root: docker build -f updater/Dockerfile .
FROM docker:29-cli AS docker-cli

FROM python:3.12-slim
WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends git ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# docker CLI + compose plugin (talks to the socket proxy via DOCKER_HOST)
COPY --from=docker-cli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=docker-cli /usr/local/libexec/docker/cli-plugins/docker-compose /usr/local/libexec/docker/cli-plugins/docker-compose

COPY updater/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY updater/*.py ./

RUN useradd --system --uid 10001 --no-create-home updater \
 && mkdir -p /state /work && chown updater /state /work
USER updater
ENV HOME=/tmp PYTHONUNBUFFERED=1

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/hooks/health').status == 200 else 1)"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
