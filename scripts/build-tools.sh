#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
docker compose --env-file /dev/null --profile tools build tools
mkdir -p .state
docker image inspect path-discovery-tools:20260902 > .state/tools-image.json
docker compose --env-file /dev/null run --rm --no-deps -T tools scamper -v
docker compose --env-file /dev/null run --rm --no-deps -T tools tshark -v
