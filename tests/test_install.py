import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('installer', Path(__file__).resolve().parents[1] / 'scripts/install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name) / "another user ' $dollar `tick` %percent"
        self.home.mkdir()

    def test_vault_is_dynamic_and_preserves_existing_content(self):
        vault = self.home / '내 노트'
        installer.create_vault(vault)
        self.assertIn(str(vault), (vault / '시작하기.md').read_text())
        (vault / '시작하기.md').write_text('personal note')
        (vault / '.obsidian/app.json').write_text('{"existing":true}')
        installer.create_vault(vault)
        self.assertEqual((vault / '시작하기.md').read_text(), 'personal note')
        self.assertEqual(json.loads((vault / '.obsidian/app.json').read_text()), {'existing': True})

    def test_launchers_quote_paths_and_arguments(self):
        root = self.home / '.local/share/wsl-notes'
        app = root / 'apps/antigravity/1'
        app.mkdir(parents=True)
        executable = app / 'antigravity'
        executable.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n')
        executable.chmod(0o755)
        installer.create_launchers(self.home, root, {'antigravity': app})
        launcher = self.home / '.local/bin/antigravity-wsl'
        result = subprocess.check_output([str(launcher), 'note with spaces', '$(false)'], text=True)
        self.assertEqual(result, 'note with spaces\n$(false)\n')
        desktop = self.home / '.local/share/applications/antigravity-wsl.desktop'
        self.assertIn('%%percent', desktop.read_text())
        if __import__('shutil').which('desktop-file-validate'):
            subprocess.run(['desktop-file-validate', str(desktop)], check=True)
        installer.create_launchers(self.home, root, {'antigravity': app})

    def test_unmanaged_file_not_overwritten(self):
        path = self.home / 'launcher'
        path.write_text('keep me')
        with self.assertRaises(RuntimeError):
            installer.managed_write(path, installer.MARKER)
        self.assertEqual(path.read_text(), 'keep me')

    def test_vault_registry_merges_and_is_idempotent(self):
        path = self.home / '.config/obsidian/obsidian.json'
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({'vaults': {'old': {'path': '/old', 'open': True}}, 'cli': True}))
        with patch.object(Path, 'glob', return_value=[]):
            installer.register_vault(self.home, self.home / 'Notes')
            before = path.read_text()
            installer.register_vault(self.home, self.home / 'Notes')
        self.assertEqual(path.read_text(), before)
        data = json.loads(before)
        self.assertTrue(data['cli'])
        self.assertEqual(data['vaults']['old']['path'], '/old')
        self.assertEqual(len(data['vaults']), 2)
        self.assertEqual(len(list(path.parent.glob('*.backup-*'))), 1)

    def test_archive_rejects_traversal_and_escaping_links(self):
        for name, link in [('../escape', None), ('link', '/etc'), ('link', '../../etc')]:
            archive = self.home / 'bad.tar.gz'
            with tarfile.open(archive, 'w:gz') as out:
                member = tarfile.TarInfo(name)
                if link:
                    member.type = tarfile.SYMTYPE
                    member.linkname = link
                    out.addfile(member)
                else:
                    member.size = 1
                    out.addfile(member, io.BytesIO(b'x'))
            with self.assertRaises(RuntimeError):
                installer.safe_extract(archive, self.home / 'out')

    def test_checksum_mismatch_is_rejected_without_network(self):
        cache = self.home / 'cache'
        cache.mkdir()
        expected = '0' * 64
        (cache / ('obsidian-' + expected + '.deb')).write_bytes(b'bad')
        with self.assertRaisesRegex(RuntimeError, 'checksum mismatch'):
            installer.download('obsidian', {'sha256': expected}, cache, offline=True)

    def test_offline_cache_and_miss(self):
        cache = self.home / 'cache'
        cache.mkdir()
        source = cache / 'data'
        source.write_bytes(b'test')
        expected = installer.digest(source)
        target = cache / ('obsidian-' + expected + '.deb')
        source.rename(target)
        self.assertEqual(installer.download('obsidian', {'sha256': expected}, cache, True), target)
        with self.assertRaisesRegex(RuntimeError, 'Offline cache miss'):
            installer.download('antigravity', {'sha256': expected}, cache, True)


if __name__ == '__main__':
    unittest.main()
