import os
from pathlib import Path
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
BOOTSTRAP = REPO / 'bootstrap.sh'


def run_bootstrap(home, *args, **env):
    full_env = {**os.environ, 'HOME': str(home), 'WSL_NOTES_SKIP_WSL_CHECK': '1', **env}
    return subprocess.run(['bash', str(BOOTSTRAP), *args], env=full_env,
                          stdin=subprocess.DEVNULL, capture_output=True, text=True)


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / '사용자 home'
        self.home.mkdir()
        # Serve the current checkout (including uncommitted bootstrap.sh) as the remote.
        self.remote = Path(self.tmp.name) / 'remote'
        subprocess.run(['git', 'clone', '--quiet', str(REPO), str(self.remote)], check=True)
        subprocess.run(['cp', str(BOOTSTRAP), str(self.remote / 'bootstrap.sh')], check=True)
        # CI checks out a detached merge commit, so pin a named branch for the clone to track.
        self.branch = 'bootstrap-test'
        subprocess.run(['git', '-C', str(self.remote), 'checkout', '--quiet', '-B', self.branch], check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_fresh_plan_clones_and_runs_setup_plan(self):
        result = run_bootstrap(self.home, '--plan', WSL_NOTES_REPO_URL=str(self.remote),
                               WSL_NOTES_BRANCH=self.branch)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.home / 'apps/antigravity-obsidian-wsl/setup.sh').is_file())
        self.assertIn('Steps:', result.stdout)

    def test_rerun_updates_existing_checkout(self):
        env = dict(WSL_NOTES_REPO_URL=str(self.remote), WSL_NOTES_BRANCH=self.branch)
        self.assertEqual(run_bootstrap(self.home, '--plan', **env).returncode, 0)
        result = run_bootstrap(self.home, '--plan', '--profile', 'cmc', **env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Updating', result.stdout)
        self.assertIn('--profile cmc', result.stdout)

    def test_refuses_non_git_target(self):
        target = self.home / 'apps/antigravity-obsidian-wsl'
        target.mkdir(parents=True)
        (target / '내 파일.txt').write_text('keep', encoding='utf-8')
        result = run_bootstrap(self.home, '--plan')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('not a git checkout', result.stderr)
        self.assertEqual((target / '내 파일.txt').read_text(encoding='utf-8'), 'keep')


if __name__ == '__main__':
    unittest.main()
