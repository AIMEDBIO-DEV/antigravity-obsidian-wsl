import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('vault', Path(__file__).resolve().parents[1] / 'scripts/vault.py')
vault_tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vault_tool)

TEMPLATE = vault_tool.TEMPLATES / 'cmc'
HAS_YAML = importlib.util.find_spec('yaml') is not None


def stub_addons(vault):
    """Write placeholder bundles so the validator's plugin check can run offline."""
    for name, addon in vault_tool.addons(TEMPLATE).items():
        folder = 'themes' if addon['kind'] == 'theme' else 'plugins'
        for filename in addon['files']:
            path = vault / '.obsidian' / folder / name / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('/* placeholder */\n')


class VaultTemplateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "another user ' $dollar `tick` %percent"
        self.home.mkdir()
        self.vault = self.home / '내 노트'

    def apply(self, *extra):
        return vault_tool.main(['--vault', str(self.vault), '--no-addons', *extra])

    def test_plan_changes_nothing(self):
        self.assertEqual(vault_tool.main(['--plan', '--vault', str(self.vault)]), 0)
        self.assertFalse(self.vault.exists())

    def test_apply_writes_rules_links_and_note_folders(self):
        self.assertEqual(self.apply(), 0)
        self.assertTrue((self.vault / 'config/vault-schema.yaml').is_file())
        self.assertTrue((self.vault / 'Templates/Project.md').is_file())
        self.assertTrue((self.vault / 'scripts/validate-vault.py').is_file())
        self.assertEqual((self.vault / 'CLAUDE.md').readlink(), Path('AGENTS.md'))
        self.assertEqual((self.vault / '.agents/skills').readlink(), Path('../.claude/skills'))
        for folder in ('Daily', 'Projects', 'People', 'Email_Drafts', 'Attachments'):
            self.assertTrue((self.vault / folder).is_dir(), folder)

    def test_existing_notes_are_never_overwritten(self):
        self.vault.mkdir(parents=True)
        (self.vault / 'index.md').write_text('my own index\n')
        (self.vault / 'Projects').mkdir()
        (self.vault / 'Projects/P-Mine.md').write_text('---\ntype: project\n---\n\n# 내 프로젝트\n')
        with patch('sys.stdout', new_callable=io.StringIO) as out:
            self.assertEqual(self.apply(), 0)
        self.assertEqual((self.vault / 'index.md').read_text(), 'my own index\n')
        self.assertIn('index.md', out.getvalue())
        self.assertIn('# 내 프로젝트', (self.vault / 'Projects/P-Mine.md').read_text())

    def test_apply_is_idempotent(self):
        self.assertEqual(self.apply(), 0)
        with patch('sys.stdout', new_callable=io.StringIO) as out:
            self.assertEqual(self.apply(), 0)
        self.assertIn('규칙 파일 0개 생성', out.getvalue())

    def test_starter_note_moves_only_when_unedited(self):
        self.assertEqual(self.apply(), 0)
        note = self.vault / vault_tool.STARTER_NOTE
        note.write_text(vault_tool.STARTER_MARKER + '\n\n보관함 경로\n')
        self.assertEqual(self.apply('--adopt-starter-note'), 0)
        moved = self.vault / 'References' / vault_tool.STARTER_NOTE
        self.assertFalse(note.exists())
        self.assertTrue(moved.read_text().startswith('---\ntype: reference\n'))
        note.write_text('내가 직접 쓴 노트\n')
        with self.assertRaises(RuntimeError):
            self.apply('--adopt-starter-note')

    def test_addon_download_rejects_wrong_hash(self):
        cache = self.home / 'cache'
        payload = b'not the real bundle'
        with patch.object(vault_tool.urllib.request, 'urlopen') as urlopen:
            urlopen.return_value.__enter__.return_value = io.BytesIO(payload)
            with self.assertRaises(RuntimeError) as error:
                vault_tool.fetch('templater-obsidian', 'main.js',
                                 {'url': 'https://example.invalid/main.js', 'sha256': '0' * 64},
                                 cache, offline=False)
        self.assertIn('SHA-256 mismatch', str(error.exception))
        self.assertEqual(list(cache.glob('*')), [])

    def test_addon_versions_are_pinned_for_every_bundled_addon(self):
        pinned = vault_tool.addons(TEMPLATE)
        self.assertEqual(set(pinned), {'templater-obsidian', 'obsidian-minimal-settings', 'tray', 'Minimal'})
        for name, addon in pinned.items():
            folder = 'themes' if addon['kind'] == 'theme' else 'plugins'
            manifest = json.loads((TEMPLATE / '.obsidian' / folder / name / 'manifest.json').read_text())
            self.assertEqual(manifest['version'], addon['version'], name)
            for file_spec in addon['files'].values():
                self.assertRegex(file_spec['sha256'], r'^[0-9a-f]{64}$')
                self.assertTrue(file_spec['url'].startswith('https://github.com/'))

    def test_template_ships_no_large_bundles(self):
        for path in TEMPLATE.rglob('*'):
            if path.is_file():
                self.assertLess(path.stat().st_size, 200_000, path)

    @unittest.skipUnless(HAS_YAML, 'PyYAML is required by the vault validator')
    def test_applied_vault_passes_its_own_validator(self):
        self.assertEqual(self.apply(), 0)
        stub_addons(self.vault)
        self.assertEqual(vault_tool.validate(self.vault), 0)

    @unittest.skipUnless(HAS_YAML, 'PyYAML is required by the vault validator')
    def test_validator_rejects_unknown_tag_and_status(self):
        self.assertEqual(self.apply(), 0)
        stub_addons(self.vault)
        (self.vault / 'Projects/P-Bad.md').write_text(
            '---\ntype: project\nstatus: 아무거나\ntags: [made-up-tag]\n---\n\n# bad\n')
        self.assertEqual(vault_tool.validate(self.vault), 1)


if __name__ == '__main__':
    unittest.main()
