#!/usr/bin/env bash
set -euo pipefail

vault_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$vault_root/scripts/validate-vault.py"
