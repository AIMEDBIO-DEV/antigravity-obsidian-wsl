#!/usr/bin/env python3
"""Apply a vault rule template to a local Obsidian vault without touching notes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import urllib.request

REPO = Path(__file__).resolve().parents[1]
TEMPLATES = REPO / 'vault-templates'
LINKS = {'CLAUDE.md': 'AGENTS.md', 'GEMINI.md': 'AGENTS.md',
         '.agents/skills': '../.claude/skills'}
# Files the installer generates for the generic vault; the rule set expects
# typed folders instead, so they are only moved when the user opts in.
STARTER_NOTE = '시작하기.md'
STARTER_MARKER = '# 로컬 노트 시작하기'


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1 << 20), b''):
            value.update(block)
    return value.hexdigest()


def templates():
    return sorted(item.name for item in TEMPLATES.iterdir()
                  if item.is_dir() and (item / 'config/vault-schema.yaml').is_file())


def addons(template):
    # Pinned separately from versions.json, which lists only the apps install.py
    # downloads and turns into launchers.
    names = json.loads((TEMPLATES / 'addons.json').read_text())
    used = {}
    for name, spec in names.items():
        folder = 'themes' if spec['kind'] == 'theme' else 'plugins'
        if (template / '.obsidian' / folder / name).is_dir():
            used[name] = spec
    return used


def fetch(name, filename, spec, cache, offline):
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / f'{name}-{spec["sha256"][:16]}-{filename}'
    if path.exists():
        if digest(path) == spec['sha256']:
            return path
        path.unlink()
    if offline:
        raise RuntimeError(f'{name}/{filename} is not cached; run without --offline')
    handle, temp = tempfile.mkstemp(dir=cache, prefix='.download')
    os.close(handle)
    temp = Path(temp)
    try:
        with urllib.request.urlopen(spec['url'], timeout=120) as response, temp.open('wb') as out:
            shutil.copyfileobj(response, out)
        found = digest(temp)
        if found != spec['sha256']:
            raise RuntimeError(f'{name}/{filename} SHA-256 mismatch: expected '
                               f'{spec["sha256"]}, got {found}')
        temp.replace(path)
    finally:
        if temp.exists():
            temp.unlink()
    return path


def copy_rules(template, vault):
    """Copy template files, never replacing a file the user already has."""
    created, kept = [], []
    for source in sorted(template.rglob('*')):
        relative = source.relative_to(template)
        target = vault / relative
        if source.is_symlink() or relative.name == '.gitkeep':
            continue
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        if target.exists():
            if digest(source) != digest(target):
                kept.append(relative.as_posix())
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        created.append(relative.as_posix())
    for name in ('Daily', 'Projects', 'People', 'Organizations', 'Products',
                 'Meetings', 'Email_Drafts', 'References', 'Attachments'):
        (vault / name).mkdir(parents=True, exist_ok=True)
    return created, kept


def create_links(vault):
    made, wrong = [], []
    for name, destination in LINKS.items():
        path = vault / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.is_symlink():
            if os.readlink(path) != destination:
                wrong.append(f'{name} -> {os.readlink(path)}')
            continue
        if path.exists():
            wrong.append(f'{name} (일반 파일)')
            continue
        path.symlink_to(destination)
        made.append(name)
    return made, wrong


def install_addons(template, vault, cache, offline):
    installed = []
    for name, spec in addons(template).items():
        folder = 'themes' if spec['kind'] == 'theme' else 'plugins'
        for filename, file_spec in spec['files'].items():
            target = vault / '.obsidian' / folder / name / filename
            if target.exists() and digest(target) == file_spec['sha256']:
                continue
            # Obsidian appends a marker to an installed plugin bundle, so an
            # existing file with another hash is kept instead of overwritten.
            if target.exists():
                continue
            source = fetch(name, filename, file_spec, cache, offline)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            installed.append(f'{folder}/{name}/{filename}')
    return installed


def adopt_starter_note(vault):
    """Move the installer's unedited starter note into the typed folder."""
    note = vault / STARTER_NOTE
    if not note.is_file():
        return None
    text = note.read_text(encoding='utf-8-sig')
    if not text.startswith(STARTER_MARKER):
        raise RuntimeError(f'{STARTER_NOTE} was edited; move it yourself and rerun')
    target = vault / 'References' / STARTER_NOTE
    if target.exists():
        raise RuntimeError(f'Already present: {target}')
    target.parent.mkdir(parents=True, exist_ok=True)
    note.replace(target)
    target.write_text('---\ntype: reference\nstatus: stable\n---\n\n' + text, encoding='utf-8')
    return target


def validate(vault):
    script = vault / 'scripts/validate-vault.py'
    if not script.is_file():
        raise RuntimeError(f'Validator is missing: {script}')
    # Flush first so the validator's report stays below this script's output
    # when stdout is a pipe rather than a terminal.
    sys.stdout.flush()
    return subprocess.run([sys.executable, str(script)]).returncode


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template', default='cmc', help='Template under vault-templates/')
    parser.add_argument('--vault', type=Path, help='Default: current Linux user home/Obsidian/CMC')
    parser.add_argument('--cache', type=Path)
    parser.add_argument('--plan', action='store_true', help='Show steps without making changes')
    parser.add_argument('--offline', action='store_true', help='Use cached add-on files only')
    parser.add_argument('--no-addons', action='store_true', help='Skip plugin/theme downloads')
    parser.add_argument('--adopt-starter-note', action='store_true',
                        help='Move an unedited 시작하기.md into References/')
    parser.add_argument('--validate', action='store_true', help='Run the vault validator afterwards')
    args = parser.parse_args(argv)

    available = templates()
    if args.template not in available:
        parser.error(f'Unknown template {args.template}; available: {", ".join(available)}')
    template = TEMPLATES / args.template
    home = Path.home()
    vault = (args.vault or home / 'Obsidian/CMC').expanduser().resolve()
    cache = (args.cache or home / '.cache/wsl-notes/obsidian-addons').expanduser().resolve()
    if any(character in str(vault) for character in '\n\r\x00'):
        raise RuntimeError('Vault path contains a control character')

    print(json.dumps({'template': str(template), 'vault': str(vault), 'cache': str(cache),
                      'addons': {name: spec['version'] for name, spec in addons(template).items()}},
                     ensure_ascii=False, indent=2))
    if args.plan:
        print('Steps: rule files → agent document links → pinned plugins/theme → validator')
        print('Existing notes and settings are kept; only missing files are written.')
        return 0

    if os.geteuid() == 0:
        raise RuntimeError('Run as the normal WSL user, not sudo/root.')
    vault.mkdir(parents=True, exist_ok=True)
    created, kept = copy_rules(template, vault)
    made, wrong = create_links(vault)
    installed = [] if args.no_addons else install_addons(template, vault, cache, args.offline)
    moved = adopt_starter_note(vault) if args.adopt_starter_note else None

    print(f'\n규칙 파일 {len(created)}개 생성, 기존 파일 {len(kept)}개 유지')
    for name in kept:
        print('  유지:', name)
    if made:
        print('링크 생성:', ', '.join(made))
    for name in wrong:
        print('  확인 필요(링크 아님):', name)
    if installed:
        print('부가 기능 설치:', ', '.join(installed))
    if moved:
        print('시작하기 노트 이동:', moved)
    print('보관함:', vault)
    print('다음: Obsidian에서 Open folder as vault로 위 경로를 열고 SETUP.md를 확인하세요.')

    if args.validate:
        return validate(vault)
    print('검증 명령: bash', vault / 'scripts/validate-vault.sh')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (RuntimeError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print('ERROR:', error, file=sys.stderr)
        sys.exit(1)
