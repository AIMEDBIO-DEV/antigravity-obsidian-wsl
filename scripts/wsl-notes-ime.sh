#!/bin/sh
# Managed by antigravity-obsidian-wsl
export DISPLAY="${DISPLAY:-:0}"
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus"
export IBUS_ADDRESS="unix:abstract=wsl-notes-ibus-$(id -u)"
export GTK_IM_MODULE=ibus
export QT_IM_MODULE=ibus
export XMODIFIERS=@im=ibus
export GDK_BACKEND=x11
systemctl --user start wsl-notes-ibus.service || exit 1
attempt=0
until timeout 2 ibus engine hangul >/dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ "$attempt" -ge 20 ]; then
        echo "WSL Notes: Korean input engine did not start" >&2
        exit 1
    fi
    sleep 0.2
done
exec "$@"
