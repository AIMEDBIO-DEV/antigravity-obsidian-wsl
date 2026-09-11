#!/usr/bin/env python3
"""User-local WSLg installation. Python standard library only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import posixpath
import shlex
import shutil
import struct
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.parse

REPO = Path(__file__).resolve().parents[1]
MARKER = '# Managed by antigravity-obsidian-wsl'


def atomic_write(path, content, mode=0o644):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            out.write(content)
        os.chmod(temp, mode)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def managed_write(path, content, mode=0o644):
    if path.exists() and MARKER not in path.read_text():
        raise RuntimeError(f'Existing unmanaged file; will not overwrite: {path}')
    atomic_write(path, content, mode)


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as source:
        for data in iter(lambda: source.read(1024 * 1024), b''):
            value.update(data)
    return value.hexdigest()


def download(name, spec, cache, offline=False):
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / (name + '-' + spec['sha256'] + ('.tar.gz' if name == 'antigravity' else '.deb'))
    if path.exists():
        if digest(path) != spec['sha256']:
            raise RuntimeError(f'Cached checksum mismatch: {path}; remove this cache file and retry.')
        return path
    if offline:
        raise RuntimeError(f'Offline cache miss: {path}')
    partial = path.with_suffix(path.suffix + '.partial')
    try:
        subprocess.run(['curl', '--fail', '--location', '--proto', '=https',
                        '--proto-redir', '=https', '--retry', '3', '--connect-timeout', '20',
                        '--max-time', '1200', '--output', str(partial), spec['url']], check=True)
        if digest(partial) != spec['sha256']:
            raise RuntimeError(f'Download checksum mismatch: {name}')
        partial.replace(path)
    finally:
        partial.unlink(missing_ok=True)
    return path


def safe_extract(archive, destination):
    with tarfile.open(archive, 'r:gz') as source:
        for member in source.getmembers():
            name = posixpath.normpath(member.name)
            if name.startswith('/') or name == '..' or name.startswith('../'):
                raise RuntimeError('Unsafe archive path')
            if not (member.isfile() or member.isdir() or member.issym() or member.islnk()):
                raise RuntimeError('Unsupported archive entry')
            if member.issym() or member.islnk():
                target = posixpath.normpath(posixpath.join(
                    posixpath.dirname(name) if member.issym() else '', member.linkname))
                if target.startswith('/') or target == '..' or target.startswith('../'):
                    raise RuntimeError('Unsafe archive link')
        if hasattr(tarfile, 'data_filter'):
            source.extractall(destination, filter='data')
        else:
            source.extractall(destination)


def extract_icon(asar, target):
    with asar.open('rb') as source:
        header = struct.unpack('<4I', source.read(16))
        tree = json.loads(source.read(header[3]))
        entry = tree['files']['icon.png']
        source.seek(8 + header[1] + int(entry['offset']))
        target.write_bytes(source.read(entry['size']))


def install_app(name, spec, archive, root):
    target = root / 'apps' / name / spec['version']
    expected = {'version': spec['version'], 'sha256': spec['sha256']}
    receipt = target / '.wsl-notes-receipt.json'
    if target.exists():
        if not receipt.exists() or json.loads(receipt.read_text()) != expected:
            raise RuntimeError(f'Incomplete or unmanaged install: {target}')
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.install-', dir=target.parent) as temp:
        staging = Path(temp)
        if name == 'antigravity':
            safe_extract(archive, staging)
            source = staging / 'Antigravity-x64'
            extract_icon(source / 'resources/app.asar', source / 'icon.png')
        else:
            subprocess.run(['dpkg-deb', '-x', str(archive), str(staging)], check=True)
            source = staging / 'opt/Obsidian'
        binary = source / name
        if not binary.is_file():
            raise RuntimeError(f'Expected application binary missing: {binary}')
        result = subprocess.run(['ldd', str(binary)], capture_output=True, text=True, check=True)
        missing = [line.strip() for line in result.stdout.splitlines() if 'not found' in line]
        if missing:
            raise RuntimeError('Missing libraries; run scripts/install-deps.sh: ' + ', '.join(missing))
        (source / '.wsl-notes-receipt.json').write_text(json.dumps(expected))
        source.rename(target)
    return target


def desktop_quote(value):
    # Desktop Exec uses its own escaping, then desktop-entry string escaping.
    value = str(value).replace('%', '%%')
    for char in ('\\', '"', '`', '$'):
        value = value.replace(char, '\\' + char)
    return '"' + value.replace('\\', '\\\\') + '"'


def desktop_value(value):
    return str(value).replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r')


def create_input_method(home, root):
    helper = (REPO / 'scripts/wsl-notes-ime.sh').read_text()
    managed_write(root / 'bin/wsl-notes-ime', helper, 0o755)
    service = MARKER + "\n" + """[Unit]
Description=Korean input for WSL Notes apps

[Service]
Environment=DISPLAY=:0
Environment=GDK_BACKEND=x11
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=%t/bus
ExecStart=/usr/bin/ibus-daemon --address=unix:abstract=wsl-notes-ibus-%U --xim --config=/usr/libexec/ibus-dconf --panel=disable --emoji-extension=disable
Restart=on-failure
RestartSec=2
"""
    managed_write(home / '.config/systemd/user/wsl-notes-ibus.service', service)


def configure_input_method(home, root):
    env = dict(os.environ, DBUS_SESSION_BUS_ADDRESS=f'unix:path=/run/user/{os.getuid()}/bus')
    settings = {
        'org.freedesktop.ibus.general': {
            'preload-engines': "['hangul']", 'engines-order': "['hangul']",
            'use-global-engine': 'true', 'use-system-keyboard-layout': 'true',
        },
        'org.freedesktop.ibus.general.hotkey': {'triggers': '[]'},
        'org.freedesktop.ibus.engine.hangul': {
            'hangul-keyboard': "'2'", 'initial-input-mode': "'latin'",
            'switch-keys': "'Hangul,Alt_R,Shift+space'",
        },
    }
    backup = root / 'backups/before-korean-input'
    for path, name in (('/desktop/ibus/', 'general.dconf'),
                       ('/org/freedesktop/ibus/engine/hangul/', 'hangul.dconf')):
        if not (backup / name).exists():
            data = subprocess.check_output(['dconf', 'dump', path], text=True, env=env)
            atomic_write(backup / name, data, 0o600)
    for schema, keys in settings.items():
        for key, value in keys.items():
            subprocess.run(['gsettings', 'set', schema, key, value], check=True, env=env)
    subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True, env=env)
    subprocess.run(['systemctl', '--user', 'restart', 'wsl-notes-ibus.service'], check=True, env=env)
    subprocess.run([str(root / 'bin/wsl-notes-ime'), '/usr/bin/true'], check=True, env=env)


def create_launchers(home, root, applications):
    create_input_method(home, root)
    private_bin = root / 'bin'
    opener = '''#!/usr/bin/env python3
# Managed by antigravity-obsidian-wsl
import os, subprocess, sys
from pathlib import Path
uri = sys.argv[1] if len(sys.argv) > 1 else ''
if not uri: sys.exit(2)
if uri.startswith(('http://', 'https://')):
    # Ask WSL to locate Windows itself; never assume a Windows account name.
    windows = subprocess.check_output(['cmd.exe', '/d', '/c', 'echo %SystemRoot%'], cwd='/mnt/c', stderr=subprocess.DEVNULL).decode().strip()
    windows = subprocess.check_output(['wslpath', '-u', windows], text=True).strip()
    command = [str(Path(windows)/'System32/rundll32.exe'), 'url.dll,FileProtocolHandler', uri]
elif uri.startswith('antigravity://'):
    command = [str(Path.home()/'.local/bin/antigravity-wsl'), uri]
elif uri.startswith('obsidian://'):
    command = [str(Path.home()/'.local/bin/obsidian-wsl'), uri]
else:
    command = ['/usr/bin/xdg-open', uri]
os.execv(command[0], command)
'''
    managed_write(private_bin / 'xdg-open', opener, 0o755)
    for name, target in applications.items():
        binary = home / '.local/bin' / (name + '-wsl')
        wrapper = '#!/bin/sh\n' + MARKER + '\n'
        wrapper += 'export PATH=' + shlex.quote(str(private_bin)) + ':"$PATH"\n'
        wrapper += 'exec ' + shlex.quote(str(private_bin / 'wsl-notes-ime')) + ' '
        wrapper += shlex.quote(str(target / name)) + ' --ozone-platform=x11 "$@"\n'
        managed_write(binary, wrapper, 0o755)
        icon = target / ('icon.png' if name == 'antigravity' else 'resources/icon.png')
        desktop = '[Desktop Entry]\n' + MARKER + '\nType=Application\n'
        desktop += f'Name={name.capitalize()} (WSL)\nExec={desktop_quote(binary)} %U\n'
        desktop += f'Icon={desktop_value(icon)}\nTerminal=false\nCategories=Office;\n'
        desktop += f'MimeType=x-scheme-handler/{name};\n'
        managed_write(home / '.local/share/applications' / (name + '-wsl.desktop'), desktop)


def starter_note(vault):
    """Text of the generated starter note; scripts/vault.py compares against it."""
    return f'''# 로컬 노트 시작하기

보관함 경로: `{vault}`

1. Antigravity에서 로그인 후 프로젝트 폴더로 위 경로를 선택합니다.
2. Local 환경에서 `Inbox/첫 메모.md에 오늘의 아이디어를 정리해 줘`처럼 요청합니다.
3. Obsidian에서 작성된 Markdown 파일을 확인합니다.

새 메모는 `Inbox`, 일일 노트는 `Daily`, 첨부 파일은 `Attachments`에 저장합니다.
노트 연결은 `[[노트 제목]]` 형식을 사용합니다.
기존 노트와 `.obsidian` 설정은 필요할 때만 변경하도록 요청하세요.
'''


def create_vault(vault):
    for folder in ('Inbox', 'Daily', 'Attachments', '.obsidian'):
        (vault / folder).mkdir(parents=True, exist_ok=True)
    config = vault / '.obsidian/app.json'
    if not config.exists():
        atomic_write(config, json.dumps({'attachmentFolderPath': 'Attachments',
                     'newFileLocation': 'folder', 'newFileFolderPath': 'Inbox'}, indent=2) + '\n')
    note = vault / '시작하기.md'
    if not note.exists():
        atomic_write(note, starter_note(vault))


def register_vault(home, vault):
    # Do not edit Obsidian's registry while its process can write it back.
    for entry in Path('/proc').glob('[0-9]*/cmdline'):
        try:
            args = entry.read_bytes().split(b'\0')
            if args and Path(os.fsdecode(args[0])).name.lower() == 'obsidian':
                if not any(arg.startswith(b'--type=') for arg in args):
                    print('Obsidian is running: use Open folder as vault for', vault)
                    return False
        except (OSError, ValueError):
            continue
    path = home / '.config/obsidian/obsidian.json'
    data = json.loads(path.read_text()) if path.exists() else {}
    vaults = data.setdefault('vaults', {})
    if any(item.get('path') == str(vault) for item in vaults.values()):
        return True
    identity = hashlib.sha256(str(vault).encode()).hexdigest()[:16]
    if identity in vaults:
        raise RuntimeError('Vault registration ID collision')
    vaults[identity] = {'path': str(vault), 'ts': int(time.time() * 1000), 'open': True}
    if path.exists():
        shutil.copy2(path, path.with_name(f'obsidian.json.backup-{time.time_ns()}'))
    atomic_write(path, json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    return True


def check_environment():
    if os.geteuid() == 0:
        raise RuntimeError('Run as your normal WSL user, not sudo/root.')
    if 'microsoft' not in platform.release().lower() or 'wsl2' not in platform.release().lower():
        raise RuntimeError('WSL2 is required.')
    if platform.machine() not in ('x86_64', 'amd64'):
        raise RuntimeError('This release supports x64 PCs only; ARM64 is not yet validated.')
    if not Path('/mnt/wslg').exists() or not (os.getenv('DISPLAY') or os.getenv('WAYLAND_DISPLAY')):
        raise RuntimeError('WSLg is unavailable. Run wsl --update in Windows, then reopen Ubuntu.')
    for command in ('curl', 'dpkg-deb', 'ldd', 'xdg-mime', 'fc-match', 'ibus', 'ibus-daemon', 'gsettings', 'dconf', 'systemctl', 'timeout'):
        if not shutil.which(command):
            raise RuntimeError(f'Missing {command}; run scripts/install-deps.sh first.')


def select_profile(home, requested=None, vault_override=None):
    profiles = json.loads((REPO / 'vault-templates/profiles.json').read_text())
    record = home / '.local/share/wsl-notes/install.json'
    previous = json.loads(record.read_text()) if record.exists() else {}
    name = requested or previous.get('profile', 'minimal')
    if name not in profiles:
        raise RuntimeError(f'Unknown profile: {name}')
    info = profiles[name]
    previous_vault = previous.get('vault') if name == previous.get('profile', 'minimal') else None
    vault = Path(vault_override or previous_vault or home / 'Obsidian' / info['folder']).expanduser().resolve()
    return name, info, vault


def create_profile_vault(vault, profile, cache, offline):
    if profile == 'minimal':
        create_vault(vault)
    else:
        command = [sys.executable, str(REPO / 'scripts/vault.py'), '--template', profile,
                   '--vault', str(vault), '--cache', str(cache / 'obsidian-addons'), '--validate']
        if offline:
            command.append('--offline')
        subprocess.run(command, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=('minimal', 'cmc'), help='CMC includes team rules; default keeps the previous profile or minimal')
    parser.add_argument('--vault', type=Path, help='Default: previous vault, or ~/Obsidian/Notes')
    parser.add_argument('--cache', type=Path, help='Default: ~/.cache/wsl-notes')
    parser.add_argument('--offline', action='store_true', help='Require previously verified cache files')
    parser.add_argument('--plan', action='store_true', help='Print paths and versions without changes/downloads')
    args = parser.parse_args()
    home = Path.home().resolve()
    profile, profile_info, vault = select_profile(home, args.profile, args.vault)
    if any(c in str(vault) + str(home) for c in '\n\r\x00'):
        raise RuntimeError('Paths must not contain newline or NUL characters.')
    root = home / '.local/share/wsl-notes'
    specs = json.loads((REPO / 'versions.json').read_text())
    print(json.dumps({'home': str(home), 'vault': str(vault), 'install': str(root),
                      'profile': profile, 'welcome_note': profile_info['welcome_note'],
                      'versions': {key: val['version'] for key, val in specs.items()}}, indent=2, ensure_ascii=False))
    if args.plan:
        return
    check_environment()
    if profile == 'cmc':
        try:
            __import__('yaml')
        except ImportError:
            raise RuntimeError('PyYAML is missing; run scripts/install-deps.sh using system Python.')
    # Fail before downloads or vault changes if old/unmanaged launchers exist.
    for name in specs:
        for path in (home / '.local/bin' / (name + '-wsl'),
                     home / '.local/share/applications' / (name + '-wsl.desktop')):
            if path.exists() and MARKER not in path.read_text():
                raise RuntimeError(f'Existing unmanaged launcher: {path}. Back it up/rename it before installation.')
    for path in (root / 'bin/wsl-notes-ime', home / '.config/systemd/user/wsl-notes-ibus.service'):
        if path.exists() and MARKER not in path.read_text():
            raise RuntimeError(f'Existing unmanaged input method file: {path}. Back it up/rename it before installation.')
    cache = (args.cache or home / '.cache/wsl-notes').expanduser().resolve()
    applications = {name: install_app(name, spec, download(name, spec, cache, args.offline), root)
                    for name, spec in specs.items()}
    create_launchers(home, root, applications)
    configure_input_method(home, root)
    create_profile_vault(vault, profile, cache, args.offline)
    registered = register_vault(home, vault)
    for name in specs:
        subprocess.run(['xdg-mime', 'default', name + '-wsl.desktop', 'x-scheme-handler/' + name], check=True)
    subprocess.run(['update-desktop-database', str(home / '.local/share/applications')], check=False)
    atomic_write(root / 'install.json', json.dumps({'vault': str(vault), 'versions': specs, 'profile': profile,
                                                  'welcome_note': profile_info['welcome_note'],
                                                  'test_note_folder': profile_info['test_note_folder'],
                                                  'template_revision': profile_info.get('template_revision'),
                                                  'vault_registered': registered}, indent=2) + '\n')
    print('\nInstallation complete. Launch from the Windows Start menu, or:')
    print(home / '.local/bin/antigravity-wsl')
    print(home / '.local/bin/obsidian-wsl')
    print('In Antigravity: sign in, create a project, choose this folder:', vault)
    print('Use Local mode. Authentication and folder selection are manual.')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print('ERROR:', error, file=sys.stderr)
        sys.exit(1)
