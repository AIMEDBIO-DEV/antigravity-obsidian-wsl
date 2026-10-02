#!/usr/bin/env bash
# One-command installer for WSL Ubuntu. Downloads (or updates) this repository and runs setup.sh.
#
#   curl -fsSL https://raw.githubusercontent.com/AIMEDBIO-DEV/antigravity-obsidian-wsl/main/bootstrap.sh | bash
#   curl -fsSL .../bootstrap.sh | bash -s -- --profile minimal
#
# The vault profile defaults to cmc on a first install; reinstalls keep the saved one.
# Any arguments are passed to setup.sh. Run as the normal Linux user, not with sudo.
set -euo pipefail

# Everything lives in main so a truncated `curl | bash` download never runs a partial script.
main() {
  local repo_url="${WSL_NOTES_REPO_URL:-https://github.com/AIMEDBIO-DEV/antigravity-obsidian-wsl.git}"
  local branch="${WSL_NOTES_BRANCH:-main}"
  local target="${WSL_NOTES_DIR:-$HOME/apps/antigravity-obsidian-wsl}"
  local args=("$@") plan=false offline=false arg

  for arg in "${args[@]}"; do
    case "$arg" in
      --plan) plan=true ;;
      --offline) offline=true ;;
    esac
  done

  if [[ "${WSL_NOTES_SKIP_WSL_CHECK:-}" != 1 ]] && ! grep -qi microsoft /proc/sys/kernel/osrelease; then
    echo 'Run this inside WSL2 Ubuntu (open the Ubuntu app on Windows).' >&2; return 1
  fi
  . /etc/os-release
  if [[ "${ID:-}" != ubuntu ]]; then
    echo 'Supported distribution: Ubuntu 22.04 or newer.' >&2; return 1
  fi
  if (( EUID == 0 )); then
    echo 'Run as your normal Linux user, not root or sudo. The script asks for the sudo password itself.' >&2; return 1
  fi

  # Ask for the sudo password up front so the rest runs without stopping (dependencies use apt).
  if ! $plan && ! $offline; then
    echo 'sudo 암호를 한 번 입력하세요 (패키지 설치용).'
    sudo -v
    if ! command -v git >/dev/null; then
      sudo apt-get update
      sudo apt-get install -y git ca-certificates curl
    fi
  fi
  command -v git >/dev/null || { echo 'git is required: sudo apt-get install -y git' >&2; return 1; }

  if [[ -d "$target/.git" ]]; then
    if [[ -n "$(git -C "$target" status --porcelain)" ]]; then
      echo "Local changes found in $target; using it as is without updating." >&2
    elif ! $offline; then
      echo "Updating $target"
      git -C "$target" fetch --quiet origin "$branch"
      git -C "$target" checkout --quiet "$branch"
      git -C "$target" merge --quiet --ff-only "origin/$branch"
    fi
  elif [[ -e "$target" ]]; then
    echo "$target exists but is not a git checkout. Move it away or set WSL_NOTES_DIR." >&2; return 1
  else
    $offline && { echo "--offline needs an existing checkout at $target" >&2; return 1; }
    echo "Downloading to $target"
    mkdir -p "$(dirname "$target")"
    git clone --quiet --branch "$branch" "$repo_url" "$target"
  fi

  echo "Running: setup.sh ${args[*]}"
  bash "$target/setup.sh" "${args[@]}"
}

main "$@"
