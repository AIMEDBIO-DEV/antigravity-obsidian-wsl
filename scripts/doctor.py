#!/usr/bin/env python3
"""Read-only checks; never starts an app or contacts a remote server."""
from pathlib import Path
import json
import os
import platform
import shutil
import subprocess
import sys

checks = []
def check(label, success, detail):
    checks.append(success)
    print(f'{"OK" if success else "CHECK"}: {label}: {detail}')

home = Path.home()
check('WSL2', 'wsl2' in platform.release().lower(), platform.release())
check('CPU', platform.machine() == 'x86_64', platform.machine())
check('WSLg', Path('/mnt/wslg').exists() and bool(os.getenv('DISPLAY') or os.getenv('WAYLAND_DISPLAY')),
      'DISPLAY=' + str(os.getenv('DISPLAY')) + ', WAYLAND_DISPLAY=' + str(os.getenv('WAYLAND_DISPLAY')))
print('INFO: GPU device:', 'present' if Path('/dev/dxg').exists() else 'not visible; rendering needs checking')
for cmd in ('curl', 'python3', 'dpkg-deb', 'xdg-mime', 'fc-match', 'ibus', 'ibus-daemon', 'gsettings', 'dconf'):
    check(cmd, bool(shutil.which(cmd)), shutil.which(cmd) or 'run scripts/install-deps.sh')
for name in ('antigravity', 'obsidian'):
    path = home / '.local/bin' / (name + '-wsl')
    check(name + ' launcher', path.is_file(), str(path))
record = home / '.local/share/wsl-notes/install.json'
if record.exists():
    data = json.loads(record.read_text())
    vault = Path(data['vault'])
    check('vault', vault.is_dir() and os.access(vault, os.W_OK), str(vault))
else:
    check('installation record', False, str(record))
if shutil.which('fc-list'):
    fonts = subprocess.check_output(['fc-list', ':lang=ko', 'family'], text=True).strip()
    check('Korean font', bool(fonts), fonts.splitlines()[0] if fonts else 'install fonts-nanum')
service = home / '.config/systemd/user/wsl-notes-ibus.service'
check('Korean input service', service.is_file(), str(service))
if shutil.which('gsettings'):
    keys = subprocess.run(['gsettings', 'get', 'org.freedesktop.ibus.engine.hangul', 'switch-keys'],
                          capture_output=True, text=True)
    check('Korean toggle keys', keys.returncode == 0 and all(k in keys.stdout for k in ('Hangul', 'Alt_R', 'Shift+space')),
          keys.stdout.strip() or 'run the installer to configure IBus Hangul')
print('Manual check: type Korean using Hangul/Right Alt or Shift+Space in each app.')
print('Manual check: login → Notes project → Local mode → create Inbox/test.md → view in Obsidian.')
sys.exit(0 if all(checks) else 1)
