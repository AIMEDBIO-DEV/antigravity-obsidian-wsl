import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch, Mock

spec = importlib.util.spec_from_file_location('setup', Path(__file__).resolve().parents[1] / 'scripts/setup.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class SetupTests(unittest.TestCase):
    def test_plan_does_not_install_or_start_apps(self):
        with patch.object(setup, 'run') as run, patch.object(setup, 'finish') as finish:
            setup.main(['--plan', '--vault', '/tmp/내 노트'])
        self.assertEqual(run.call_count, 1)
        self.assertIn('--plan', run.call_args.args[0])
        self.assertIn('/tmp/내 노트', run.call_args.args[0])
        finish.assert_not_called()

    def test_failed_install_does_not_proceed_to_finish(self):
        with patch.object(setup.os, 'geteuid', return_value=1000), \
             patch.dict(os.environ, WSL_DISTRO_NAME='Ubuntu'), \
             patch.object(setup.shutil, 'which', return_value='/bin/tool'), \
             patch.object(setup, 'run', side_effect=subprocess.CalledProcessError(1, 'apt')), \
             patch.object(setup, 'finish') as finish:
            with self.assertRaises(subprocess.CalledProcessError):
                setup.main([])
        finish.assert_not_called()

    def test_finish_only_does_not_reinstall(self):
        with patch.object(setup.os, 'geteuid', return_value=1000), \
             patch.dict(os.environ, WSL_DISTRO_NAME='Ubuntu'), \
             patch.object(setup.shutil, 'which', return_value='/bin/tool'), \
             patch.object(setup, 'run') as run, patch.object(setup, 'finish') as finish:
            setup.main(['--finish-only'])
        run.assert_not_called()
        finish.assert_called_once()

    def test_finish_opens_encoded_vault_and_preserves_manual_checks(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            root = home / '.local/share/wsl-notes'
            root.mkdir(parents=True)
            vault = home / '내 노트'
            vault.mkdir()
            (root / 'install.json').write_text(json.dumps({'vault': str(vault)}))
            child = Mock(pid=123)
            child.poll.return_value = 0  # existing app may accept launch and exit
            with patch.object(setup, 'run'), \
                 patch.object(setup.subprocess, 'check_output', return_value='C:\\script.ps1\n'), \
                 patch.object(setup.subprocess, 'Popen', return_value=child) as popen, \
                 patch.object(setup.time, 'sleep'):
                report = setup.finish(home, 'Ubuntu', '/windows/powershell.exe')
            uri = popen.call_args_list[0].args[0][1]
            self.assertIn('%20', uri)
            self.assertNotIn('내', uri)
            self.assertTrue(report['automation_complete'])
            self.assertEqual(len(report['user_checks_pending']), 4)
            self.assertTrue(report['apps']['antigravity']['launch_requested'])
            # A failed retry must not leave the previous automation success report.
            with patch.object(setup, 'run', side_effect=subprocess.CalledProcessError(1, 'shortcut')), \
                 patch.object(setup.subprocess, 'check_output', return_value='C:\\script.ps1\n'), \
                 patch.object(setup.subprocess, 'Popen') as popen:
                with self.assertRaises(subprocess.CalledProcessError):
                    setup.finish(home, 'Ubuntu', '/windows/powershell.exe')
                popen.assert_not_called()
            self.assertFalse(json.loads((root / 'setup-status.json').read_text())['automation_complete'])
