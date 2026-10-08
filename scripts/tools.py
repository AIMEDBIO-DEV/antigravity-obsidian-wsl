#!/usr/bin/env python3
"""Install document/slide tools: officecli, Node + pnpm, an open-slide workspace and team themes."""
import argparse
import json
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import install as core  # noqa: E402  (reuses download/verify/extract and the managed-file marker)

REPO = Path(__file__).resolve().parents[1]
RECORD = 'tools-install.json'


def supported_node(version):
    """Mirror of the open-slide engines range: ^20.19.0 || >=22.12.0."""
    match = re.match(r'v?(\d+)\.(\d+)', version or '')
    if not match:
        return False
    major, minor = int(match.group(1)), int(match.group(2))
    return (major == 20 and minor >= 19) or (major == 22 and minor >= 12) or major >= 23


def command_output(command, env=None):
    try:
        result = subprocess.run([str(item) for item in command], capture_output=True, text=True, env=env)
    except OSError:  # command not installed
        return ''
    return result.stdout.strip() if result.returncode == 0 else ''


def tool_env(node_bin, tools_bin):
    env = os.environ.copy()
    extra = [str(path) for path in (node_bin, tools_bin) if path]
    env['PATH'] = os.pathsep.join(extra + [env.get('PATH', '')])
    return env


def ensure_node(root, cache, spec, offline):
    """Use a supported Node already on PATH, otherwise a private checksum-verified copy."""
    if supported_node(command_output(['node', '--version'])) and shutil.which('npm'):
        return None, command_output(['node', '--version']).lstrip('v'), 'system'
    target = root / 'node' / spec['version']
    expected = {'version': spec['version'], 'sha256': spec['sha256']}
    receipt = target / '.wsl-notes-receipt.json'
    if target.exists():
        if not receipt.exists() or json.loads(receipt.read_text()) != expected:
            raise RuntimeError(f'Incomplete or unmanaged Node install: {target}')
    else:
        archive = core.download('node', spec, cache, offline)
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.install-', dir=target.parent) as temp:
            core.safe_extract(archive, temp, 'r:xz')
            source = Path(temp) / f'node-v{spec["version"]}-linux-x64'
            if not (source / 'bin/node').is_file():
                raise RuntimeError(f'Expected Node binary missing: {source / "bin/node"}')
            (source / '.wsl-notes-receipt.json').write_text(json.dumps(expected))
            source.rename(target)
    return target / 'bin', spec['version'], 'private'


def ensure_pnpm(env, root, version):
    """Any working pnpm is kept; otherwise the pinned version goes to a private prefix (no global changes)."""
    existing = command_output(['pnpm', '--version'], env)
    if existing:
        return existing, root / 'tools/bin'
    subprocess.run(['npm', 'install', '--global', '--prefix', str(root / 'tools'), f'pnpm@{version}'],
                   check=True, env=env, stdin=subprocess.DEVNULL)
    installed = command_output([root / 'tools/bin/pnpm', '--version'], env)
    if not installed:
        raise RuntimeError('pnpm installation did not produce a working pnpm.')
    return installed, root / 'tools/bin'


def fetch(url, destination):
    subprocess.run(['curl', '--fail', '--silent', '--show-error', '--location', '--proto', '=https',
                    '--proto-redir', '=https', '--retry', '3', '--connect-timeout', '20',
                    '--max-time', '300', '--output', str(destination), url], check=True)


def ensure_officecli(home, spec, offline):
    """Official installer is trusted as-is (not hash-pinned). The Antigravity skill is placed separately
    because the installer only targets agent folders that already exist and only on its first run."""
    binary = home / '.local/bin/officecli'
    found = shutil.which('officecli') or (str(binary) if binary.exists() else None)
    status = 'present'
    if not found:
        if offline:
            return None, 'skipped-offline'
        with tempfile.TemporaryDirectory() as temp:
            script = Path(temp) / 'install.sh'
            fetch(spec['installer_url'], script)
            subprocess.run(['bash', str(script)], check=True, stdin=subprocess.DEVNULL)
        found, status = str(binary), 'installed'
    version = command_output([found, '--version'])
    if not version:
        raise RuntimeError(f'officecli is installed but did not report a version: {found}')
    skill = home / '.agents/skills/officecli/SKILL.md'
    if not skill.exists() and not offline:
        skill.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as temp:
            downloaded = Path(temp) / 'SKILL.md'
            fetch(spec['skill_url'], downloaded)
            shutil.copyfile(downloaded, skill)
    return version, status


def scaffold_slides(slides, env, offline):
    if slides.exists() and any(slides.iterdir()):
        if not (slides / 'package.json').is_file():
            raise RuntimeError(f'Existing folder is not an open-slide workspace; will not modify: {slides}')
        status = 'present'
    else:
        if offline:
            return 'skipped-offline'
        # Pass only the folder name: the scaffolder rejects some characters anywhere in an absolute path.
        slides.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['npx', '--yes', '@open-slide/cli@latest', 'init', slides.name,
                        '--use-pnpm', '--no-git'], check=True, cwd=slides.parent, env=env,
                       stdin=subprocess.DEVNULL)
        status = 'created'
    if not (slides / 'node_modules').is_dir():
        if offline:
            return 'skipped-offline'
        # The scaffolder can report success even when its own dependency install failed.
        subprocess.run(['pnpm', 'install'], check=True, cwd=slides, env=env, stdin=subprocess.DEVNULL)
    return status


def workspace_version(slides):
    """Installed open-slide version, read from the workspace (the scaffolder is not pinned)."""
    manifest = slides / 'node_modules/@open-slide/core/package.json'
    try:
        return json.loads(manifest.read_text()).get('version')
    except (OSError, ValueError):
        return None


def apply_theme(slides, bundle):
    """Copy only missing files; existing files (including edited themes) are never overwritten."""
    written, kept = [], []
    for source in sorted(path for path in bundle.rglob('*') if path.is_file()):
        relative = source.relative_to(bundle)
        if relative.parts[0] not in ('themes', 'assets', 'scripts'):
            continue
        destination = slides / relative
        if destination.exists():
            kept.append(str(relative))
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        written.append(str(relative))
    return written, kept


LAUNCHER = r"""#!/usr/bin/env bash
@MARKER@
# slides-wsl          foreground dev server (Ctrl+C to stop)
# slides-wsl start    background server for agents; returns once it answers, then opens the browser
# slides-wsl status   prints the URL while running (exit 3 when stopped)
# slides-wsl stop     stops the background server
set -euo pipefail
@PATH_LINE@
slides=@SLIDES@
port=@PORT@
state="${XDG_STATE_HOME:-$HOME/.local/state}/wsl-notes"
pid_file="$state/slides-dev.pid"
log_file="$state/slides-dev.log"

open_browser() { (cd /mnt/c 2>/dev/null; powershell.exe -NoProfile -Command "Start-Process '$1'" >/dev/null 2>&1) || true; }
running() { [[ -f $pid_file ]] && kill -0 "$(cat "$pid_file")" 2>/dev/null; }
server_url() { grep -o 'http://localhost:[0-9]*' "$log_file" 2>/dev/null | head -n 1 || true; }

case "${1:-}" in
  '')
    cd "$slides"
    echo "슬라이드 미리보기: http://localhost:$port (종료: Ctrl+C)"
    (sleep 5; open_browser "http://localhost:$port") &
    exec pnpm exec open-slide dev --port "$port"
    ;;
  start)
    mkdir -p "$state"
    url=$(server_url)
    if running && [[ -n $url ]] && curl -sf -o /dev/null "$url"; then
      echo "이미 실행 중: $url (종료: slides-wsl stop)"
      open_browser "$url"
      exit 0
    fi
    cd "$slides"
    # setsid + nohup: the server survives the agent's terminal and stops as one process group.
    # --no-skills-check: the drift prompt would wait forever without a terminal.
    setsid nohup pnpm exec open-slide dev --port "$port" --no-skills-check >"$log_file" 2>&1 </dev/null &
    echo $! >"$pid_file"
    for _ in $(seq 1 120); do
      url=$(server_url)
      if [[ -n $url ]] && curl -sf -o /dev/null "$url"; then
        echo "슬라이드 미리보기 실행됨: $url (종료: slides-wsl stop, 로그: $log_file)"
        open_browser "$url"
        exit 0
      fi
      running || break
      sleep 0.5
    done
    echo "미리보기 서버를 시작하지 못했습니다. 로그: $log_file" >&2
    tail -n 20 "$log_file" >&2 || true
    exit 1
    ;;
  status)
    url=$(server_url)
    if running && [[ -n $url ]] && curl -sf -o /dev/null "$url"; then echo "실행 중: $url"; else echo '중지됨'; exit 3; fi
    ;;
  stop)
    if running; then
      pid=$(cat "$pid_file")
      kill -TERM -- "-$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
      echo '미리보기 서버를 종료했습니다.'
    else
      echo '실행 중인 미리보기 서버가 없습니다.'
    fi
    rm -f "$pid_file"
    ;;
  *)
    echo 'usage: slides-wsl [start|status|stop]' >&2
    exit 2
    ;;
esac
"""


def create_launcher(home, slides, node_bin, tools_bin, port):
    path = home / '.local/bin/slides-wsl'
    prefix = ':'.join(str(item) for item in (node_bin, tools_bin) if item)
    content = (LAUNCHER.replace('@MARKER@', core.MARKER)
               .replace('@PATH_LINE@', f'export PATH={shlex.quote(prefix)}:"$PATH"' if prefix else ':')
               .replace('@SLIDES@', shlex.quote(str(slides)))
               .replace('@PORT@', str(int(port))))
    core.managed_write(path, content, 0o755)
    return path


def install_preview_skill(home):
    """Global Antigravity skill: the agent starts the preview when the user asks for it in chat."""
    path = home / '.gemini/config/skills/slides-preview/SKILL.md'
    try:
        core.managed_write(path, (REPO / 'agent-skills/slides-preview/SKILL.md').read_text())
    except RuntimeError:  # the user's own skill with the same name stays untouched
        return 'kept-unmanaged'
    return 'ok'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', action='store_true', help='Print paths and versions without changes/downloads')
    parser.add_argument('--slides', type=Path, help='Default: previous workspace, or ~/Slides')
    parser.add_argument('--cache', type=Path, help='Default: ~/.cache/wsl-notes')
    parser.add_argument('--offline', action='store_true', help='Skip steps that need the network')
    args = parser.parse_args(argv)
    home = Path.home().resolve()
    root = home / '.local/share/wsl-notes'
    specs = json.loads((REPO / 'tools.json').read_text())
    record_path = root / RECORD
    previous = json.loads(record_path.read_text()) if record_path.exists() else {}
    slides = Path(args.slides or previous.get('slides') or home / 'Slides').expanduser().resolve()
    if any(c in str(slides) + str(home) for c in '\n\r\x00'):
        raise RuntimeError('Paths must not contain newline or NUL characters.')
    print(json.dumps({'slides': str(slides), 'themes': specs['themes'],
                      'versions': {'node': specs['node']['version'], 'pnpm': specs['pnpm']['version'],
                                   'open-slide': 'latest (not pinned)',
                                   'officecli': 'official installer (latest, not pinned)'}},
                     indent=2, ensure_ascii=False))
    if args.plan:
        return None
    if os.geteuid() == 0:
        raise RuntimeError('Run as your normal WSL user, not sudo/root.')
    if platform.machine() not in ('x86_64', 'amd64'):
        raise RuntimeError('This release supports x64 PCs only; ARM64 is not yet validated.')
    if not shutil.which('curl'):
        raise RuntimeError('Missing curl; run scripts/install-deps.sh first.')
    launcher = home / '.local/bin/slides-wsl'
    if launcher.exists() and core.MARKER not in launcher.read_text():
        raise RuntimeError(f'Existing unmanaged launcher: {launcher}. Back it up/rename it before installation.')
    cache = (args.cache or home / '.cache/wsl-notes').expanduser().resolve()

    steps = {}
    officecli_version, steps['officecli'] = ensure_officecli(home, specs['officecli'], args.offline)
    node_bin, node_version, node_source = ensure_node(root, cache, specs['node'], args.offline)
    tools_bin = root / 'tools/bin'
    env = tool_env(node_bin, tools_bin)
    pnpm_version = None
    pnpm_found = command_output(['pnpm', '--version'], env)
    if pnpm_found or not args.offline:
        pnpm_version, tools_bin = ensure_pnpm(env, root, specs['pnpm']['version'])
        env = tool_env(node_bin, tools_bin)
    steps['pnpm'] = 'ok' if pnpm_version else 'skipped-offline'
    steps['workspace'] = scaffold_slides(slides, env, args.offline) \
        if pnpm_version else 'skipped-offline'
    written, kept = [], []
    if (slides / 'package.json').is_file():
        for theme in specs['themes']:
            done, existing = apply_theme(slides, REPO / 'slide-templates' / theme)
            written += done
            kept += existing
    steps['themes'] = 'ok' if (slides / 'package.json').is_file() else 'skipped-offline'
    launcher = create_launcher(home, slides, node_bin, tools_bin, specs['open-slide']['port'])
    steps['preview_skill'] = install_preview_skill(home)
    complete = all(not value.startswith('skipped') for value in steps.values())
    core.atomic_write(record_path, json.dumps({
        'slides': str(slides), 'complete': complete, 'steps': steps, 'launcher': str(launcher),
        'themes': specs['themes'],
        'versions': {'officecli': officecli_version, 'node': node_version, 'node_source': node_source,
                     'pnpm': pnpm_version, 'open_slide_core': workspace_version(slides)},
    }, ensure_ascii=False, indent=2) + '\n')
    print('\n도구 설치 결과:', json.dumps(steps, ensure_ascii=False))
    if written:
        print('테마 파일 추가:', ', '.join(written))
    if kept:
        print('기존 파일 유지(덮어쓰지 않음):', ', '.join(kept))
    if not complete:
        print('일부 단계가 오프라인 때문에 생략되었습니다. 네트워크 연결 후 다시 실행하세요.')
    print('슬라이드 미리보기 실행:', launcher)
    return complete


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print('TOOLS INCOMPLETE:', error, file=sys.stderr)
        sys.exit(1)
