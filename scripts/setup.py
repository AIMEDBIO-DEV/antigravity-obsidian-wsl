#!/usr/bin/env python3
"""Install, register Windows shortcuts, check, and open the WSL Notes apps."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.parse

REPO = Path(__file__).resolve().parents[1]


def run(command, **kwargs):
    subprocess.run([str(item) for item in command], check=True, **kwargs)


def finish(home, distribution, powershell):
    root = home / '.local/share/wsl-notes'
    record = root / 'install.json'
    data = json.loads(record.read_text())
    vault = Path(data['vault'])
    if not vault.is_absolute() or not vault.is_dir():
        raise RuntimeError(f'Installed vault is missing: {vault}')
    report_path = root / 'setup-status.json'
    report_path.write_text(json.dumps({
        'vault': str(vault), 'automation_complete': False,
        'user_checks_pending': ['desktop_login', 'antigravity_local_project',
                               'physical_keyboard', 'note_round_trip'],
    }, ensure_ascii=False, indent=2) + '\n')
    script = subprocess.check_output(
        ['wslpath', '-w', str(REPO / 'scripts/create-windows-shortcuts.ps1')], text=True).strip()
    run([powershell, '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass',
         '-File', script, '-Distribution', distribution])
    run([sys.executable, REPO / 'scripts/doctor.py'])
    for key in ('Shift+Space', 'Alt_R', 'Hangul'):
        run(['/usr/bin/python3', REPO / 'scripts/verify-korean-input.py', key])
    logs = root / 'logs'
    logs.mkdir(parents=True, exist_ok=True)
    # The registered vault is opened by absolute path, including non-ASCII/spaces.
    uri = 'obsidian://open?' + urllib.parse.urlencode(
        {'path': str(vault / '시작하기.md')}, quote_via=urllib.parse.quote)
    processes = {}
    for name, args in (('obsidian', [uri]), ('antigravity', [])):
        with (logs / (name + '-setup.log')).open('a') as log:
            child = subprocess.Popen([str(home / '.local/bin' / (name + '-wsl')), *args],
                                     stdin=subprocess.DEVNULL, stdout=log,
                                     stderr=subprocess.STDOUT, start_new_session=True)
        time.sleep(1)
        code = child.poll()
        if code is not None and code != 0:
            raise RuntimeError(f'{name} failed to start ({code}); see {logs}')
        # A launcher may hand off to an existing process and exit successfully.
        processes[name] = {'launch_requested': True, 'launcher_pid': child.pid}
    report = {
        'vault': str(vault), 'automation_complete': True, 'shortcuts_verified': True, 'doctor_passed': True,
        'input_engine_passed': True, 'apps': processes,
        'user_checks_pending': ['desktop_login', 'antigravity_local_project',
                                'physical_keyboard', 'note_round_trip'],
    }
    report_path = root / 'setup-status.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('\n자동 설정 완료. 전체 사용 확인은 아직 남아 있습니다.')
    print('1. Antigravity 데스크톱 앱에서 본인 계정으로 로그인하세요.')
    print('2. Create New Project → New Project에서 다음 폴더를 선택하고 Local 모드를 사용하세요:')
    print(vault)
    print('3. 앱 입력창에서 한/영 키로 한글을 입력해 보세요.')
    print('4. Antigravity에 새 Inbox 메모 작성을 요청하고 Obsidian에서 같은 파일을 확인하세요.')
    print('Obsidian이 보관함을 열지 못하면 Open folder as vault로 위 폴더를 선택하세요.')
    print('상태 기록:', report_path)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', action='store_true', help='Show steps without making changes')
    parser.add_argument('--finish-only', action='store_true', help='Resume shortcut/check/app steps after installation')
    parser.add_argument('--vault', type=Path)
    parser.add_argument('--cache', type=Path)
    parser.add_argument('--offline', action='store_true', help='Use installed dependencies and cached apps; do not run apt')
    args = parser.parse_args(argv)
    if args.finish_only and (args.vault or args.cache or args.offline):
        parser.error('--finish-only uses the existing install.json; omit --vault, --cache, and --offline')
    install_args = []
    for flag, value in (('--vault', args.vault), ('--cache', args.cache)):
        if value is not None:
            install_args.extend([flag, str(value)])
    if args.offline:
        install_args.append('--offline')
    if args.plan:
        if not args.finish_only:
            run([sys.executable, REPO / 'scripts/install.py', '--plan', *install_args])
        print('Steps: dependencies → apps/vault/IME → hidden Windows shortcuts → checks → open apps')
        print('Then guide desktop login → Local project → physical Korean input → note round trip.')
        return
    if os.geteuid() == 0:
        raise RuntimeError('Run ./setup.sh as the normal WSL user, not sudo/root.')
    distribution = os.environ.get('WSL_DISTRO_NAME')
    powershell = shutil.which('powershell.exe')
    if not distribution or not powershell or not shutil.which('wslpath'):
        raise RuntimeError('Run inside WSL Ubuntu with Windows interop enabled (powershell.exe and wslpath required).')
    if not args.finish_only:
        if not args.offline:
            run(['bash', REPO / 'scripts/install-deps.sh'])
        run([sys.executable, REPO / 'scripts/install.py', *install_args])
    finish(Path.home(), distribution, powershell)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print('SETUP INCOMPLETE:', error, file=sys.stderr)
        sys.exit(1)
