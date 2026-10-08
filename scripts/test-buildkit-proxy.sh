#!/bin/bash
# Experiment: does the updater's Docker access work through the socket proxy
# (classic image build, compose up, image listing and removal)?
#
# Everything runs in throwaway containers with the prefix "bktest" on its own
# network. Your running stack is not touched. All test containers, networks and
# images are removed at the end.
#
# What is tested (all through tecnativa/docker-socket-proxy, like the updater):
#   1. docker build through the proxy
#        E: classic builder (what the updater uses today), proxy as in compose.yaml
#        C: BuildKit with SESSION=1 GRPC=1 (for reference: known to fail, because
#           buildx uses the docker-container driver which needs "docker exec")
#      On a failure the script prints which requests the proxy denied.
#   2. docker image ls / image rm          (used for pruning old images)
#   3. docker compose up --wait            (start a container, wait until healthy)
#   4. docker compose up with a new tag    (the version switch of an update)
#
# Usage (needs access to the Docker socket, so usually with sudo):
#   sudo scripts/test-buildkit-proxy.sh            # quick test with a tiny Dockerfile
#   sudo scripts/test-buildkit-proxy.sh --full     # additionally build the real api/web images
#
# Exit code: 0 if a build configuration worked and all following tests passed, else 1.

set -uo pipefail

PREFIX=bktest
NET="${PREFIX}-net"
PROXY="${PREFIX}-proxy"
PROXY_IMAGE="${PROXY_IMAGE:-tecnativa/docker-socket-proxy:v0.4.2}"
CLI_IMAGE="${CLI_IMAGE:-docker:29-cli}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
FULL=0
[ "${1:-}" = "--full" ] && FULL=1

CTX="$(mktemp -d /tmp/${PREFIX}-ctx.XXXXXX)"
declare -a RESULTS=()
BEST=""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

say()  { printf '\n\033[1m== %s\033[0m\n' "$*"; }
ok()   { printf '  \033[32mPASS\033[0m  %s\n' "$*"; }
bad()  { printf '  \033[31mFAIL\033[0m  %s\n' "$*"; }
tail_of() { sed 's/^/        | /' | tail -n "${1:-12}"; }

# Run a command in a client container that talks to the proxy only.
EXTRA_ENV=()
set_builder_env() {   # classic = legacy builder (what the updater uses); - = BuildKit default
    case "$1" in
        classic) EXTRA_ENV=(-e DOCKER_BUILDKIT=0) ;;
        *)       EXTRA_ENV=() ;;
    esac
}
cli() {
    docker run --rm --network "$NET" --security-opt label=disable \
        -e DOCKER_HOST="tcp://${PROXY}:2375" \
        -e DOCKER_BUILDKIT=1 -e BUILDKIT_PROGRESS=plain "${EXTRA_ENV[@]}" \
        -v "$CTX:/ctx:ro" -v "$REPO:/repo:ro" \
        "$CLI_IMAGE" "$@"
}

start_proxy() {   # $1 = SESSION, $2 = GRPC
    docker rm -f "$PROXY" >/dev/null 2>&1
    docker run -d --name "$PROXY" --network "$NET" --security-opt label=disable \
        -e CONTAINERS=1 -e IMAGES=1 -e NETWORKS=1 -e BUILD=1 -e INFO=1 -e POST=1 \
        -e SESSION="$1" -e GRPC="$2" \
        -v /var/run/docker.sock:/var/run/docker.sock \
        "$PROXY_IMAGE" >/dev/null || return 1
    for _ in $(seq 1 20); do
        cli docker version --format '{{.Server.Version}}' >/dev/null 2>&1 && return 0
        sleep 1
    done
    return 1
}

show_denied() {
    echo "      - requests the proxy denied (HTTP 403):"
    docker logs "$PROXY" 2>&1 | grep -E ' 403 [0-9]+ ' | sed -E 's/.*"((GET|POST|PUT|DELETE|HEAD) [^"]*)".*/\1/' | sort | uniq -c | tail_of 10
}

cleanup() {
    say "Cleaning up"
    docker ps -aq --filter "label=com.docker.compose.project=${PREFIX}" | xargs -r docker rm -f >/dev/null 2>&1
    docker rm -f "$PROXY" >/dev/null 2>&1
    docker network rm "${PREFIX}_default" "$NET" >/dev/null 2>&1
    docker images --format '{{.Repository}}:{{.Tag}}' | grep "^${PREFIX}-" | xargs -r docker rmi -f >/dev/null 2>&1
    rm -rf "$CTX" "$CTX.out"
    echo "  done"
}
trap cleanup EXIT

# ---------------------------------------------------------------------------
# Preparation
# ---------------------------------------------------------------------------

if ! docker info >/dev/null 2>&1; then
    echo "Cannot talk to the Docker daemon. Is it running, and are you root or in the docker group?" >&2
    echo "Try: sudo $0 $*" >&2
    trap - EXIT
    rm -rf "$CTX"
    exit 1
fi

say "Preparing (images: $PROXY_IMAGE, $CLI_IMAGE)"
docker pull -q "$PROXY_IMAGE" >/dev/null && docker pull -q "$CLI_IMAGE" >/dev/null || { echo "Could not pull images." >&2; exit 1; }
docker network create --internal "$NET" >/dev/null || exit 1

echo "hello from the build context" > "$CTX/hello.txt"
cat > "$CTX/Dockerfile" <<'EOF'
FROM alpine:3.20 AS base
COPY hello.txt /hello.txt
RUN echo built > /msg

FROM base AS web
HEALTHCHECK --interval=2s --timeout=2s --retries=3 CMD test -f /msg
CMD ["sh", "-c", "sleep 600"]
EOF
cat > "$CTX/compose.yaml" <<'EOF'
name: bktest
services:
  web:
    image: bktest-web:${IMAGE_TAG:-test}
EOF

# ---------------------------------------------------------------------------
# Test 1: BuildKit build with different proxy settings
# ---------------------------------------------------------------------------

say "1. Image build through the proxy"
for cfg in "E 0 0 classic" "C 1 1 -"; do
    set -- $cfg; name="$1"; session="$2"; grpc="$3"; builder="$4"
    label="config $name (SESSION=$session GRPC=$grpc, $([ "$builder" = classic ] && echo "classic builder" || echo "BuildKit"))"
    set_builder_env "$builder"

    if ! start_proxy "$session" "$grpc"; then
        bad "$label: proxy did not start"; RESULTS+=("$label: proxy did not start"); continue
    fi

    docker rmi -f "${PREFIX}-web:test" >/dev/null 2>&1
    cli docker build --no-cache --target web -t "${PREFIX}-web:test" /ctx 2>&1 | tr -d '\0' > "$CTX.out"; rc=${PIPESTATUS[0]}
    if [ $rc -eq 0 ] && docker image inspect "${PREFIX}-web:test" >/dev/null 2>&1; then
        ok "$label: build works"
        if [ -z "$BEST" ]; then BEST="$name"; BEST_SESSION="$session"; BEST_GRPC="$grpc"; BEST_BUILDER="$builder"; fi
        RESULTS+=("$label: build PASS")
    else
        bad "$label: build failed (exit $rc)"
        tail_of 6 < "$CTX.out"
        echo "      diagnostics:"
        show_denied
        echo "      - builders the client sees:"
        cli docker buildx ls 2>&1 | tr -d '\0' | tail_of 6
        RESULTS+=("$label: build FAIL")
    fi
done
set_builder_env "${BEST_BUILDER:--}"

if [ -z "$BEST" ]; then
    say "Result"
    echo "  Neither the classic builder nor BuildKit works through the proxy."
    echo "  The updater's build step would not work. Send the output above."
    printf '  %s\n' "${RESULTS[@]}"
    exit 1
fi

# ---------------------------------------------------------------------------
# Tests 2-4 with the first working configuration
# ---------------------------------------------------------------------------

say "Using config $BEST (SESSION=$BEST_SESSION GRPC=$BEST_GRPC) for the remaining tests"
start_proxy "$BEST_SESSION" "$BEST_GRPC" || { bad "proxy did not start"; exit 1; }
# Earlier configurations may have removed the test image: build it again with the chosen setup.
cli docker build --target web -t "${PREFIX}-web:test" /ctx >/dev/null 2>&1 \
    || { bad "could not rebuild the test image with config $BEST"; exit 1; }
ALL_OK=1
check() {   # check <description> <command...>
    local desc="$1"; shift
    local out; out="$("$@" 2>&1)"
    if [ $? -eq 0 ]; then ok "$desc"; RESULTS+=("$desc: PASS"); else bad "$desc"; echo "$out" | tail_of 10; show_denied; RESULTS+=("$desc: FAIL"); ALL_OK=0; fi
}

say "2. List images through the proxy (used when pruning)"
image_listed() {
    cli docker image ls --filter "reference=${PREFIX}-*" --format '{{.Repository}}:{{.Tag}}' | grep -q "^${PREFIX}-web:test$"
}
check "docker image ls with a filter" image_listed

say "3. docker compose up --wait through the proxy"
COMPOSE=(docker compose -p "$PREFIX" -f /ctx/compose.yaml --project-directory /ctx)
check "compose up -d --wait (container becomes healthy)" \
    cli "${COMPOSE[@]}" up -d --no-build --no-deps --pull never --wait --wait-timeout 60 web
running="$(docker ps --filter "label=com.docker.compose.project=${PREFIX}" --format '{{.Image}}')"
[ "$running" = "${PREFIX}-web:test" ] && ok "container runs ${PREFIX}-web:test" || { bad "unexpected container image: '$running'"; ALL_OK=0; }

say "4. Version switch (what an update does)"
docker tag "${PREFIX}-web:test" "${PREFIX}-web:test2"
check "compose up with IMAGE_TAG=test2" \
    docker run --rm --network "$NET" --security-opt label=disable \
        -e DOCKER_HOST="tcp://${PROXY}:2375" -e IMAGE_TAG=test2 -v "$CTX:/ctx:ro" "$CLI_IMAGE" \
        docker compose -p "$PREFIX" -f /ctx/compose.yaml --project-directory /ctx \
        up -d --no-build --no-deps --pull never --wait --wait-timeout 60 web
running="$(docker ps --filter "label=com.docker.compose.project=${PREFIX}" --format '{{.Image}}')"
[ "$running" = "${PREFIX}-web:test2" ] && ok "container was replaced and runs ${PREFIX}-web:test2" || { bad "unexpected container image: '$running'"; ALL_OK=0; }

check "remove the old image tag (rollback target cleanup)" \
    cli docker image rm "${PREFIX}-web:test"

# ---------------------------------------------------------------------------
# Optional: the real images
# ---------------------------------------------------------------------------

if [ $FULL -eq 1 ]; then
    say "5. Build the real images from the repository (this takes a few minutes)"
    for target in api web; do
        check "BuildKit build of target $target from $REPO" \
            cli docker build --target "$target" -t "${PREFIX}-real-${target}:full" /repo
    done
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

say "Summary"
printf '  %s\n' "${RESULTS[@]}"
echo
if [ $ALL_OK -eq 1 ]; then
    echo "  Working setup: config $BEST (SESSION=$BEST_SESSION GRPC=$BEST_GRPC, builder=$BEST_BUILDER)."
    [ "$BEST_BUILDER" = classic ] && echo "  The classic builder works through the proxy, so the updater's build step is fine as it is."
    exit 0
fi
echo "  Some tests failed. Send the output above to continue."
exit 1
