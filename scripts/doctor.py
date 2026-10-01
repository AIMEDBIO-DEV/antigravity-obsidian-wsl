#!/usr/bin/env python3
"""Read-only checks; never starts an app or contacts a remote server."""
from pathlib import Path
import importlib.util
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
path = home / '.local/bin/obsidian-wsl'
check('obsidian launcher', path.is_file(), str(path))
record = home / '.local/share/wsl-notes/install.json'
if record.exists():
    data = json.loads(record.read_text())
    vault = Path(data['vault'])
    check('vault', vault.is_dir() and os.access(vault, os.W_OK), str(vault))
    if data.get('profile') == 'cmc':
        check('PyYAML', importlib.util.find_spec('yaml') is not None,
              'required for CMC validation')
        welcome = vault / data.get('welcome_note', 'SETUP.md')
        check('CMC welcome note', welcome.is_file(), str(welcome))
        print('Manual CMC checks: trust plugins; enable the device-local Templater new-file trigger; test folder and Daily templates.')
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
tools_record = home / '.local/share/wsl-notes/tools-install.json'
if tools_record.exists():
    tools = json.loads(tools_record.read_text())
    slides = Path(tools['slides'])
    check('tools install', tools.get('complete') is True, json.dumps(tools.get('steps'), ensure_ascii=False))
    officecli = shutil.which('officecli') or str(home / '.local/bin/officecli')
    check('officecli', Path(officecli).is_file(), officecli)
    check('open-slide workspace', (slides / 'package.json').is_file() and (slides / 'node_modules').is_dir(), str(slides))
    for theme in tools.get('themes', []):
        theme_file = slides / 'themes' / (theme + '.md')
        check('slide theme ' + theme, theme_file.is_file(), str(theme_file))
    launcher = Path(tools.get('launcher', home / '.local/bin/slides-wsl'))
    check('slides launcher', launcher.is_file(), str(launcher))
else:
    print('INFO: document/slide tools not installed (skipped or --no-tools); run ./setup.sh to add them.')
print('Manual check: type Korean using Hangul/Right Alt or Shift+Space in Obsidian (WSLg).')
print('Manual check: Windows Antigravity → connect to this WSL distro → open the vault → create a test note → view in Obsidian.')
sys.exit(0 if all(checks) else 1)
