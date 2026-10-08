#!/usr/bin/env python3
"""Install Obsidian, register Windows shortcuts, check, and open Obsidian (Antigravity runs on Windows via its WSL connection)."""
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
TOOL_CHECKS = ['officecli_smoke', 'open_slide_preview', 'cmc_weekly_theme']


def run(command, **kwargs):
    subprocess.run([str(item) for item in command], check=True, **kwargs)


def finish(home, distribution, powershell):
    root = home / '.local/share/wsl-notes'
    record = root / 'install.json'
    data = json.loads(record.read_text())
    vault = Path(data['vault'])
    profile = data.get('profile', 'minimal')
    profiles = json.loads((REPO / 'vault-templates/profiles.json').read_text())
    if profile not in profiles:
        raise RuntimeError(f'Unknown installed profile: {profile}')
    info = profiles[profile]
    welcome = data.get('welcome_note', info['welcome_note'])
    if Path(welcome).is_absolute() or '..' in Path(welcome).parts:
        raise RuntimeError('Invalid welcome note path')
    pending = ['antigravity_wsl_connect', 'antigravity_vault_open', 'physical_keyboard', 'note_round_trip'] + info['user_checks']
    tools_record = root / 'tools-install.json'
    tools = json.loads(tools_record.read_text()) if tools_record.exists() else None
    if tools and tools.get('complete'):
        pending += TOOL_CHECKS
    if not vault.is_absolute() or not vault.is_dir():
        raise RuntimeError(f'Installed vault is missing: {vault}')
    report_path = root / 'setup-status.json'
    report_path.write_text(json.dumps({
        'vault': str(vault), 'automation_complete': False,
        'profile': profile, 'user_checks_pending': pending,
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
        {'path': str(vault / welcome)}, quote_via=urllib.parse.quote)
    processes = {}
    for name, args in (('obsidian', [uri]),):
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
        'profile': profile, 'user_checks_pending': pending,
    }
    report_path = root / 'setup-status.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('\n자동 설정 완료. 전체 사용 확인은 아직 남아 있습니다.')
    print('1. Windows의 Antigravity 2.0에서 본인 계정으로 로그인하세요.')
    print('2. Windows Subsystem for Linux 기능으로 이 WSL 배포판에 연결하세요(연결하면 앱이 해당 배포판으로 다시 시작됩니다).')
    print('3. 연결된 Antigravity에서 다음 폴더를 프로젝트로 여세요:')
    print(vault)
    print('4. Obsidian 입력창에서 한/영 키로 한글을 입력해 보세요.')
    print(f'5. Antigravity에 {info["test_note_folder"]}/에 새 메모 작성을 요청하고 Obsidian에서 확인하세요.')
    if profile == 'cmc':
        print('CMC: 플러그인 신뢰를 확인한 뒤 Settings → Templater → Trigger Templater on new file creation을 켜세요.')
        print('이 설정은 PC별입니다. 8개 폴더와 Daily의 실제 템플릿 적용까지 확인해야 완료입니다.')
        print('규칙 점검:', vault / 'scripts/validate-vault.sh')
    if tools and tools.get('complete'):
        print('문서·슬라이드 도구:')
        print('6. officecli로 임시 docx 한 개를 만들고 열어 보세요 (예: officecli create /tmp/test.docx).')
        print('7. Antigravity에 "슬라이드 미리보기 열어줘"라고 요청해 미리보기를 열고, 테마 패널에서 cmc-weekly 데모가 보이는지 확인하세요.')
        print(f'   (에이전트가 {tools["launcher"]} start 를 실행합니다. 터미널에서는 같은 명령으로 직접 열 수 있습니다.)')
        print('작업공간:', tools['slides'])
    elif tools:
        print('문서·슬라이드 도구 설치가 완료되지 않았습니다. 네트워크 연결 후 ./setup.sh를 다시 실행하세요.')
    print('Obsidian이 보관함을 열지 못하면 Open folder as vault로 위 폴더를 선택하세요.')
    print('상태 기록:', report_path)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', action='store_true', help='Show steps without making changes')
    parser.add_argument('--finish-only', action='store_true', help='Resume shortcut/check/Obsidian steps after installation')
    parser.add_argument('--profile', choices=('minimal', 'cmc'))
    parser.add_argument('--vault', type=Path)
    parser.add_argument('--cache', type=Path)
    parser.add_argument('--offline', action='store_true', help='Use installed dependencies and cached apps; do not run apt')
    parser.add_argument('--no-tools', action='store_true', help='Skip officecli, Node/pnpm and the open-slide workspace')
    parser.add_argument('--slides', type=Path, help='open-slide workspace folder (default: previous, or ~/Slides)')
    args = parser.parse_args(argv)
    if args.finish_only and (args.vault or args.cache or args.offline or args.profile or args.slides):
        parser.error('--finish-only uses the existing install.json; omit --profile, --vault, --slides, --cache, and --offline')
    if args.no_tools and args.slides:
        parser.error('--slides cannot be combined with --no-tools')
    install_args = []
    for flag, value in (('--profile', args.profile), ('--vault', args.vault), ('--cache', args.cache)):
        if value is not None:
            install_args.extend([flag, str(value)])
    if args.offline:
        install_args.append('--offline')
    tools_args = [flag_value for flag, value in (('--slides', args.slides), ('--cache', args.cache))
                  if value is not None for flag_value in (flag, str(value))]
    if args.offline:
        tools_args.append('--offline')
    if args.plan:
        if not args.finish_only:
            run([sys.executable, REPO / 'scripts/install.py', '--plan', *install_args])
            if not args.no_tools:
                run([sys.executable, REPO / 'scripts/tools.py', '--plan', *tools_args])
        print('Steps: dependencies → Obsidian/vault/IME → officecli/Node/open-slide (skip: --no-tools) → hidden Windows shortcut → checks → open Obsidian')
        print('Then guide Windows Antigravity login → WSL connect → open vault → physical Korean input in Obsidian → note round trip.')
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
        if not args.no_tools:
            run([sys.executable, REPO / 'scripts/tools.py', *tools_args])
    finish(Path.home(), distribution, powershell)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print('SETUP INCOMPLETE:', error, file=sys.stderr)
        sys.exit(1)
