#!/usr/bin/env bash
set -euo pipefail

vault_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -d "$vault_root/.git" ]]; then
  echo "ERROR: not a git repository: $vault_root" >&2
  exit 1
fi

git -C "$vault_root" config core.hooksPath .githooks
chmod +x "$vault_root/.githooks/pre-commit"

echo "OK: tracked pre-commit hook 활성화 (.githooks/pre-commit)"
echo "검증 명령: bash scripts/validate-vault.sh"
