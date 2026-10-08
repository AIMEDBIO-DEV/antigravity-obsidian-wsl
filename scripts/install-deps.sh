#!/usr/bin/env bash
set -euo pipefail
if ! grep -qi microsoft /proc/sys/kernel/osrelease; then
  echo 'Run this script inside WSL2 Ubuntu.' >&2; exit 1
fi
. /etc/os-release
if [[ "${ID:-}" != ubuntu ]]; then
  echo 'Supported distribution: Ubuntu 22.04 or newer.' >&2; exit 1
fi
if (( EUID == 0 )); then elevate=(); else elevate=(sudo); fi
"${elevate[@]}" apt-get update
packages=(python3 curl ca-certificates git xdg-utils dbus-user-session dbus-x11
  libnss3 libgbm1 libxss1 libxtst6 libx11-xcb1 libdrm2
  fonts-nanum fonts-noto-color-emoji desktop-file-utils
  ibus ibus-hangul ibus-gtk3 dconf-cli gir1.2-ibus-1.0 python3-yaml)
for family in libgtk-3-0 libasound2; do
  if apt-cache show "${family}t64" >/dev/null 2>&1; then
    packages+=("${family}t64")
  else packages+=("$family"); fi
done
# officecli is a .NET binary that aborts without ICU. Ubuntu 26.04's base image no longer pulls it in,
# and the package name carries the ICU version (libicu70/74/78...), so pick the newest available.
icu=$(apt-cache search --names-only '^libicu[0-9]+$' | awk '{print $1}' | sort -V | tail -n 1)
if [[ -z $icu ]]; then
  echo 'No libicu package found in apt sources; officecli needs it.' >&2; exit 1
fi
packages+=("$icu")
"${elevate[@]}" apt-get install -y "${packages[@]}"
echo 'Dependencies installed. Next: ./install.sh (as your normal Linux user).'
