#!/bin/sh
# Managed by antigravity-obsidian-wsl
export DISPLAY="${DISPLAY:-:0}"
export GTK_IM_MODULE=ibus
export QT_IM_MODULE=ibus
export XMODIFIERS=@im=ibus
export GDK_BACKEND=x11
uid=$(id -u)
export IBUS_ADDRESS="unix:abstract=wsl-notes-ibus-$uid"

# systemd mode uses the user service; direct mode starts the session bus and IBus itself,
# for WSL with [boot] systemd=false (on some PCs systemd breaks WSLg window output).
if [ -z "${WSL_NOTES_IME_MODE:-}" ]; then
    if [ -d /run/systemd/system ] && [ -S "/run/user/$uid/bus" ]; then
        WSL_NOTES_IME_MODE=systemd
    else
        WSL_NOTES_IME_MODE=direct
    fi
fi
export WSL_NOTES_IME_MODE

if [ "$WSL_NOTES_IME_MODE" = systemd ]; then
    export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$uid/bus"
else
    runtime_dir="${XDG_RUNTIME_DIR:-/tmp/runtime-$uid}"
    if [ ! -d "$runtime_dir" ]; then
        mkdir -p "$runtime_dir" && chmod 700 "$runtime_dir" || exit 1
    fi
    bus_path="$runtime_dir/bus"
    export DBUS_SESSION_BUS_ADDRESS="unix:path=$bus_path"
    # A socket left from a previous WSL session may have no daemon behind it.
    if ! timeout 2 dbus-send --session --print-reply --dest=org.freedesktop.DBus \
            /org/freedesktop/DBus org.freedesktop.DBus.GetId >/dev/null 2>&1; then
        rm -f "$bus_path"
        dbus-daemon --session --address="$DBUS_SESSION_BUS_ADDRESS" --fork >/dev/null || exit 1
    fi
fi

# The installer only needs the bus to write IBus settings.
[ -n "${WSL_NOTES_IME_BUS_ONLY:-}" ] && exec "$@"

if [ "$WSL_NOTES_IME_MODE" = systemd ]; then
    systemctl --user start wsl-notes-ibus.service || exit 1
else
    daemon="ibus-daemon --address=$IBUS_ADDRESS "
    if [ -n "${WSL_NOTES_IME_RESTART:-}" ]; then
        pkill -u "$uid" -f "$daemon" && sleep 0.5
    fi
    if ! pgrep -u "$uid" -f "$daemon" >/dev/null 2>&1; then
        /usr/bin/ibus-daemon --address="$IBUS_ADDRESS" --xim --config=/usr/libexec/ibus-dconf \
            --panel=disable --emoji-extension=disable --daemonize || exit 1
    fi
fi
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
