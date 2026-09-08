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

    def test_starter_note_moves_only_when_untouched(self):
        installer = vault_tool.installer()
        installer.create_vault(self.vault)
        self.assertEqual(self.apply('--adopt-starter-note'), 0)
        note = self.vault / vault_tool.STARTER_NOTE
        moved = self.vault / 'References' / vault_tool.STARTER_NOTE
        self.assertFalse(note.exists())
        self.assertTrue(moved.read_text().startswith('---\ntype: reference\n'))

    def test_starter_note_with_edited_body_is_refused(self):
        installer = vault_tool.installer()
        installer.create_vault(self.vault)
        note = self.vault / vault_tool.STARTER_NOTE
        # Same first line as the generated note, extra content below it.
        note.write_text(installer.starter_note(self.vault) + '\n내가 추가한 내용\n')
        with self.assertRaises(RuntimeError) as error:
            self.apply('--adopt-starter-note')
        self.assertIn('편집', str(error.exception))
        self.assertTrue(note.is_file())
        self.assertFalse((self.vault / 'References' / vault_tool.STARTER_NOTE).exists())

    @unittest.skipUnless(HAS_YAML, 'PyYAML is required by the vault validator')
    def test_adopted_starter_note_passes_validation(self):
        vault_tool.installer().create_vault(self.vault)
        self.assertEqual(self.apply('--adopt-starter-note'), 0)
        stub_addons(self.vault)
        moved = self.vault / 'References' / vault_tool.STARTER_NOTE
        self.assertNotIn('[[', moved.read_text())
        self.assertEqual(vault_tool.validate(self.vault), 0)

    def test_tampered_addon_file_is_reported_not_kept_silently(self):
        cache = self.home / 'cache'
        pinned = b'pinned bundle\n'
        spec = {'url': 'https://example.invalid/main.js',
                'sha256': __import__('hashlib').sha256(pinned).hexdigest()}
        with patch.object(vault_tool.urllib.request, 'urlopen') as urlopen:
            urlopen.return_value.__enter__.return_value = io.BytesIO(pinned)
            source = vault_tool.fetch('templater-obsidian', 'main.js', spec, cache, offline=False)
        self.assertEqual(source.read_bytes(), pinned)

        target = self.vault / '.obsidian/plugins/templater-obsidian/main.js'
        target.parent.mkdir(parents=True, exist_ok=True)
        one_file = {'templater-obsidian': {'kind': 'plugin', 'version': '2.25.0',
                                           'files': {'main.js': spec}}}
        with patch.object(vault_tool, 'addons', return_value=one_file):
            # What Obsidian itself leaves behind is accepted.
            target.write_bytes(pinned + vault_tool.OBSIDIAN_PLUGIN_SUFFIX)
            self.assertEqual(
                vault_tool.install_addons(TEMPLATE, self.vault, cache, offline=True), [])
            # Anything else stops the run instead of passing validation later.
            target.write_bytes(b'window.alert("tampered")\n')
            with self.assertRaises(RuntimeError) as error:
                vault_tool.install_addons(TEMPLATE, self.vault, cache, offline=True)
        self.assertIn('2.25.0', str(error.exception))

    def test_symlinked_target_folder_cannot_write_outside_the_vault(self):
        outside = self.home / 'outside'
        outside.mkdir()
        self.vault.mkdir(parents=True)
        (self.vault / 'config').symlink_to(outside)
        with self.assertRaises(RuntimeError) as error:
            self.apply()
        self.assertIn('보관함 밖', str(error.exception))
        self.assertEqual(list(outside.iterdir()), [])

    def test_new_note_folder_outside_the_rule_set_is_reported(self):
        vault_tool.installer().create_vault(self.vault)
        with patch('sys.stdout', new_callable=io.StringIO) as out:
            self.assertEqual(self.apply(), 0)
        self.assertIn('Inbox/', out.getvalue())
        self.assertIn('확인 필요', out.getvalue())

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
