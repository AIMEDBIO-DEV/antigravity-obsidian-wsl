#!/usr/bin/env bash
set -euo pipefail
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if ! command -v python3 >/dev/null; then
  echo 'Python 3 is required: sudo apt update && sudo apt install python3' >&2
  exit 1
fi
exec python3 "$repo_dir/scripts/install.py" "$@"
