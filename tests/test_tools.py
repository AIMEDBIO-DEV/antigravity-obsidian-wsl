import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('tools', ROOT / 'scripts/tools.py')
tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tools)

SPECS = json.loads((ROOT / 'tools.json').read_text())
# Real names, vendors and project codes must never return to the public sample bundle.
# Stored as SHA-256 of the lower-cased word so this file does not itself publish them.
FORBIDDEN_HASHES = {
    'd9b047fe305300c2302e01f468fb627cbd59fad2121a1751da0e520363b843fe',
    '0075296402ee557d61c9f6e8e4d7d30303712d6de276b5bd14a7b6d9d05f4454',
    '8f2ccb383557c7d98945e0f0824f78940b22f1bdb21af0a055303d5be31c8474',
    '968e2d5b08687bf42997461cbdef6c844eabbf04f440cee888c95b864c2a4bcc',
    '59315225b42259b88f8570d1b61d180ae8c6cb86eae219bfab7c357544fdf8c8',
    '0165a1848293ed70d3e24ee1fbd5bf5df29e3ad0ecd7b47eedb35c3727f3bd6f',
    '4a68a24be61efd35298ebcab022574e30a1befc51f7713e1a2d4e70f9eb12840',
    '1879f5420046e0199a59f16bc7e5bf5f63df6a658cca06dc22c3bb956a3b09ae',
    '634d52cf055335860429e312726a2996b1858ac8f10c6e0b3a9ae25646d4703e',
    '67835746fa46f5a5bd71d848f9f0ba833b32d85009cef0261288a5f3f3c7b11c',
    'c052275bd9ec1ea66004b35e7f4c8006b4ed269a11c4f130a023481b8e6f6eac',
    '0d8f0f0a12711e0df11a94196503adf86a80ad37f4bcf3f6663f2f8892f3f4b5',
    '9ac697294230c4344d236be2396efc8e3148a9c54e87ea788b5fcf18f9e60da5',
    '1f09e49825b8994a61eb75e81544babbe4eeded70f0e9b73dc441e55e85bdc06',
    'd83f9ae7abfa668540fdc6aaf912f92156b09775e1fd68903284a9c42bdaac61',
}


class ToolsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "user ' $dollar `tick`"
        self.home.mkdir()

    def workspace(self, modules=True):
        slides = self.home / 'Slides'
        slides.mkdir()
        (slides / 'package.json').write_text('{}')
        if modules:
            (slides / 'node_modules').mkdir()
        return slides

    def test_node_range_matches_open_slide_engines(self):
        for version, expected in (('v20.18.9', False), ('v20.19.0', True), ('v21.7.0', False), ('v22.11.0', False),
                                  ('v22.12.0', True), ('v24.21.0', True), ('', False), ('garbage', False)):
            self.assertEqual(tools.supported_node(version), expected, version)

    def test_pinned_metadata_is_well_formed(self):
        self.assertRegex(SPECS['node']['sha256'], r'^[0-9a-f]{64}$')
        self.assertTrue(SPECS['node']['url'].startswith('https://nodejs.org/dist/v' + SPECS['node']['version']))
        self.assertTrue(SPECS['node']['suffix'].endswith('.xz'))
        for url in (SPECS['officecli']['installer_url'], SPECS['officecli']['skill_url']):
            self.assertTrue(url.startswith('https://'))
        for theme in SPECS['themes']:
            self.assertTrue((ROOT / 'slide-templates' / theme / 'themes' / (theme + '.md')).is_file())

    def test_theme_bundle_has_no_real_names_and_resolves_its_assets(self):
        for bundle in (ROOT / 'slide-templates').iterdir():
            if not bundle.is_dir():
                continue
            for path in bundle.rglob('*'):
                if path.suffix in ('.md', '.tsx'):
                    text = path.read_text()
                    for word in re.findall(r'[A-Za-z0-9가-힣]+', text):
                        self.assertNotIn(hashlib.sha256(word.lower().encode()).hexdigest(), FORBIDDEN_HASHES,
                                         f'forbidden word (hashed) found in {path}')
                    for asset in re.findall(r"from '\.\./assets/([^']+)'", text):
                        self.assertTrue((bundle / 'assets' / asset).is_file(), f'{asset} missing for {path}')
                    for asset in re.findall(r"from '@assets/([^']+)'", text):
                        self.assertTrue((bundle / 'assets' / asset).is_file(), f'@assets/{asset} missing for {path}')
                    for script in re.findall(r'`(scripts/[\w.-]+)`', text):
                        self.assertTrue((bundle / script).is_file(), f'{script} missing for {path}')

    def test_theme_copies_missing_files_and_never_overwrites(self):
        slides = self.workspace()
        bundle = ROOT / 'slide-templates/cmc-weekly'
        written, kept = tools.apply_theme(slides, bundle)
        self.assertIn('themes/cmc-weekly.md', written)
        self.assertEqual(kept, [])
        (slides / 'themes/cmc-weekly.md').write_text('team edited')
        written, kept = tools.apply_theme(slides, bundle)
        self.assertEqual(written, [])
        self.assertIn('themes/cmc-weekly.md', kept)
        self.assertEqual((slides / 'themes/cmc-weekly.md').read_text(), 'team edited')

    def test_theme_ships_fonts_and_pptx_table_scripts(self):
        slides = self.workspace()
        written, _ = tools.apply_theme(slides, ROOT / 'slide-templates/cmc-weekly')
        for relative in ('assets/cmc-weekly/image1.png', 'assets/fonts/pretendard/LICENSE.txt',
                         'assets/fonts/pretendard/Pretendard-Regular.subset.woff2',
                         'scripts/extract-tables.js', 'scripts/pptx-native-tables.py'):
            self.assertIn(relative, written)
            self.assertTrue((slides / relative).is_file())

    def test_scaffold_refuses_foreign_folder(self):
        slides = self.home / 'Slides'
        slides.mkdir()
        (slides / 'note.txt').write_text('mine')
        with patch.object(tools.subprocess, 'run') as run:
            with self.assertRaises(RuntimeError):
                tools.scaffold_slides(slides, {}, False)
        run.assert_not_called()
        self.assertEqual((slides / 'note.txt').read_text(), 'mine')

    def test_scaffold_keeps_existing_workspace(self):
        slides = self.workspace()
        with patch.object(tools.subprocess, 'run') as run:
            self.assertEqual(tools.scaffold_slides(slides, {}, False), 'present')
        run.assert_not_called()

    def test_scaffold_offline_creates_nothing(self):
        slides = self.home / 'Slides'
        with patch.object(tools.subprocess, 'run') as run:
            self.assertEqual(tools.scaffold_slides(slides, {}, True), 'skipped-offline')
        run.assert_not_called()
        self.assertFalse(slides.exists())

    def test_scaffold_passes_folder_name_only_and_installs_when_scaffolder_did_not(self):
        slides = self.home / 'Slides'

        def fake_run(command, **kwargs):
            if command[0] == 'npx':
                slides.mkdir()
                (slides / 'package.json').write_text('{}')
        with patch.object(tools.subprocess, 'run', side_effect=fake_run) as run:
            self.assertEqual(tools.scaffold_slides(slides, {}, False), 'created')
        npx, pnpm = run.call_args_list[0], run.call_args_list[1]
        self.assertEqual(npx.args[0][:4], ['npx', '--yes', '@open-slide/cli@latest', 'init'])
        self.assertEqual(npx.args[0][4], 'Slides')
        self.assertEqual(npx.kwargs['cwd'], slides.parent)
        self.assertEqual(pnpm.args[0], ['pnpm', 'install'])  # node_modules was missing

    def test_launcher_quotes_paths_and_refuses_unmanaged_file(self):
        slides = self.home / "My Slides ' $x"
        path = tools.create_launcher(self.home, slides, self.home / 'node bin', self.home / 'tools', 5173)
        text = path.read_text()
        self.assertIn(tools.core.MARKER, text)
        self.assertIn("slides='" + str(slides).replace("'", "'\"'\"'") + "'", text)
        self.assertIn('port=5173', text)
        for command in ('start)', 'status)', 'stop)', 'setsid nohup', '--no-skills-check'):
            self.assertIn(command, text)
        self.assertTrue(path.stat().st_mode & 0o100)
        subprocess.run(['bash', '-n', str(path)], check=True)
        path.write_text('#!/bin/sh\necho mine\n')
        with self.assertRaises(RuntimeError):
            tools.create_launcher(self.home, slides, None, self.home / 'tools', 5173)
        self.assertEqual(path.read_text(), '#!/bin/sh\necho mine\n')

    def test_launcher_rejects_unknown_command_without_starting(self):
        path = tools.create_launcher(self.home, self.home / 'Slides', None, self.home / 'tools', 5173)
        result = subprocess.run(['bash', str(path), 'bogus'], capture_output=True, text=True,
                                env={'PATH': '/usr/bin:/bin', 'HOME': str(self.home)})
        self.assertEqual(result.returncode, 2)
        self.assertIn('usage', result.stderr)

    def test_preview_skill_is_managed_and_never_replaces_a_user_skill(self):
        path = self.home / '.gemini/config/skills/slides-preview/SKILL.md'
        self.assertEqual(tools.install_preview_skill(self.home), 'ok')
        text = path.read_text()
        self.assertTrue(text.startswith('---\nname: slides-preview\n'))
        self.assertIn(tools.core.MARKER, text)
        self.assertIn('slides-wsl start', text)
        self.assertEqual(tools.install_preview_skill(self.home), 'ok')  # managed: refreshed in place
        path.write_text('my own skill')
        self.assertEqual(tools.install_preview_skill(self.home), 'kept-unmanaged')
        self.assertEqual(path.read_text(), 'my own skill')

    def test_officecli_present_skips_installer_and_keeps_skill(self):
        binary = self.home / '.local/bin/officecli'
        binary.parent.mkdir(parents=True)
        binary.write_text('#!/bin/sh\n')
        skill = self.home / '.agents/skills/officecli/SKILL.md'
        skill.parent.mkdir(parents=True)
        skill.write_text('local skill')
        with patch.object(tools.shutil, 'which', return_value=None), \
             patch.object(tools, 'command_output', return_value='1.0.152'), \
             patch.object(tools.subprocess, 'run') as run:
            self.assertEqual(tools.ensure_officecli(self.home, SPECS['officecli'], False), ('1.0.152', 'present'))
        run.assert_not_called()
        self.assertEqual(skill.read_text(), 'local skill')

    def test_officecli_offline_without_binary_is_skipped(self):
        with patch.object(tools.shutil, 'which', return_value=None), patch.object(tools.subprocess, 'run') as run:
            self.assertEqual(tools.ensure_officecli(self.home, SPECS['officecli'], True), (None, 'skipped-offline'))
        run.assert_not_called()

    def test_plan_changes_nothing(self):
        with patch.object(tools.Path, 'home', return_value=self.home), redirect_stdout(io.StringIO()) as out:
            self.assertIsNone(tools.main(['--plan', '--slides', str(self.home / '내 슬라이드')]))
        self.assertIn('내 슬라이드', out.getvalue())
        self.assertEqual(list(self.home.iterdir()), [])

    def test_workspace_version_is_read_from_installed_core(self):
        slides = self.workspace()
        self.assertIsNone(tools.workspace_version(slides))
        manifest = slides / 'node_modules/@open-slide/core/package.json'
        manifest.parent.mkdir(parents=True)
        manifest.write_text('{"version": "9.8.7"}')
        self.assertEqual(tools.workspace_version(slides), '9.8.7')

    def test_missing_command_reports_empty_instead_of_raising(self):
        self.assertEqual(tools.command_output(['definitely-not-installed-command']), '')


if __name__ == '__main__':
    unittest.main()
