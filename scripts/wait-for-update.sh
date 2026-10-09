#!/bin/bash
# Waits until the updater has finished the update that was triggered, and
# reports whether it succeeded. Used by the Deploy workflow after the trigger.
#
# Usage:
#   UPDATE_SECRET=... scripts/wait-for-update.sh <base-url> <since-epoch> [timeout-seconds]
#
#   base-url        e.g. https://athenlyx.com
#   since-epoch     unix time taken BEFORE the update was triggered; only a
#                   result that finished at or after this time is accepted
#   timeout-seconds default 1200
#
# Exit codes: 0 success (or already up to date), 1 update failed, 2 timed out.

set -uo pipefail

base="${1:?base URL required}"
since="${2:?since epoch required}"
timeout="${3:-1200}"
interval="${POLL_INTERVAL:-15}"
: "${UPDATE_SECRET:?UPDATE_SECRET must be set}"

here="$(cd "$(dirname "$0")" && pwd)"
deadline=$(( $(date +%s) + timeout ))

while [ "$(date +%s)" -lt "$deadline" ]; do
    if ! json="$("$here/update-request.sh" status "$base" 2>/dev/null)"; then
        # Network hiccup or the updater restarting: keep trying until the deadline.
        echo "Status request failed, retrying ..."
        sleep "$interval"
        continue
    fi

    running="$(jq -r '.running' <<<"$json")"
    pending="$(jq -r '.pending' <<<"$json")"
    outcome="$(jq -r '.last_result.outcome // "none"' <<<"$json")"
    finished="$(jq -r '.last_result.finished // empty' <<<"$json")"
    finished_epoch=0
    [ -n "$finished" ] && finished_epoch="$(date -d "$finished" +%s 2>/dev/null || echo 0)"

    if [ "$running" = "false" ] && [ "$pending" = "false" ] && [ "$finished_epoch" -ge "$since" ]; then
        echo "--- updater log ---"
        jq -r '.log[]' <<<"$json"
        echo "-------------------"
        case "$outcome" in
            success|up-to-date)
                echo "Update finished: $outcome ($(jq -r '.current_tag' <<<"$json"))"
                exit 0 ;;
            *)
                echo "Update FAILED: $(jq -r '.last_result.error // "unknown error"' <<<"$json")"
                exit 1 ;;
        esac
    fi

    echo "Update in progress (running=$running pending=$pending) ..."
    sleep "$interval"
done

echo "Timed out after ${timeout}s waiting for the update to finish. Check the updater log on the server."
exit 2
