#!/usr/bin/env bash
# Run any script from src/, analysis/ or scripts/ inside a fresh timestamped data folder.
# Usage (from the repo root, on the Pi):   tools/run.sh src/pcom_client.py [args...]
# Why: the scripts write their output files into the current folder. This makes that
# folder data/runs/<time>_<script>/ so output never lands next to your code.
set -euo pipefail
[ $# -ge 1 ] || { echo "usage: tools/run.sh <script.py> [args...]"; exit 1; }
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPT="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
shift
RUN="$REPO/data/runs/$(date +%Y-%m-%d_%H%M%S)_$(basename "$SCRIPT" .py)"
mkdir -p "$RUN"
{
  echo "script:  $SCRIPT"
  echo "args:    $*"
  echo "commit:  $(git -C "$REPO" rev-parse --short HEAD)$(git -C "$REPO" diff --quiet || echo ' (+uncommitted changes)')"
  echo "started: $(date -Is)"
  echo "host:    $(hostname)"
} > "$RUN/meta.txt"
echo "Run folder: $RUN"
cd "$RUN"
PYTHONPATH="$REPO/src" python3 "$SCRIPT" "$@"
