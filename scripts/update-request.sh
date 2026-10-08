#!/bin/bash
# Sends a signed request to the updater (manual trigger / status check).
#
# Usage:
#   UPDATE_SECRET=... scripts/update-request.sh [update|status] [base-url]
#
# Defaults: action "update", base URL http://127.0.0.1:6560

set -euo pipefail

action="${1:-update}"
base="${2:-http://127.0.0.1:6560}"
: "${UPDATE_SECRET:?UPDATE_SECRET must be set}"

ts="$(date +%s)"

if [ "$action" = "update" ]; then
    method=POST
    path=/hooks/update
    body='{"ref":"refs/heads/main"}'
elif [ "$action" = "status" ]; then
    method=GET
    path=/hooks/update/status
    body=''
else
    echo "Unknown action: $action (use update or status)" >&2
    exit 1
fi

sig="sha256=$(printf '%s.%s' "$ts" "$body" | openssl dgst -sha256 -hmac "$UPDATE_SECRET" -hex | sed 's/^.* //')"

curl -fsS -X "$method" "$base$path" \
    -H "X-Timestamp: $ts" \
    -H "X-Signature: $sig" \
    -H "Content-Type: application/json" \
    ${body:+-d "$body"}
echo
