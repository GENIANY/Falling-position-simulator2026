"""Checks for durable capture and failure-safe post verification; no network."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('check_run', ROOT / 'tools/run_checks.py')
runner = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(runner)

class CheckRunTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.repo = self.base / 'repo'; self.repo.mkdir()
        self.out = self.base / 'logs'; self.out.mkdir()
    def exercise(self, codes, raises=None):
        seen = []
        def execute(stage, repo, out):
            seen.append(stage[0])
            if stage[0] == raises: raise OSError('simulated launch failure')
            return {'id': stage[0], 'returncode': codes.get(stage[0], 0)}
        result = runner.run_stages(self.repo, self.out, [('pre', []), ('tests', [])],
                                   ('post', []), {}, executor=execute)
        return seen, result
    def test_failed_regression_still_checks_post(self):
        seen, r = self.exercise({'tests': 1})
        self.assertEqual(seen, ['pre', 'tests', 'post']); self.assertFalse(r['ok'])
        self.assertEqual(json.loads((self.out/'summary.json').read_text(encoding='utf-8')), r)
    def test_failed_precheck_skips_work_but_runs_post(self):
        seen, r = self.exercise({'pre': 1})
        self.assertEqual(seen, ['pre', 'post']); self.assertEqual(r['skipped_stages'], ['tests'])
    def test_launch_failure_still_checks_post(self):
        seen, r = self.exercise({}, raises='tests')
        self.assertEqual(seen, ['pre', 'tests', 'post']); self.assertIn('runner_error', r)
    def test_post_failure_is_not_success(self):
        _, r = self.exercise({'post': 1}); self.assertFalse(r['ok'])
    def test_complete_sequence_is_success(self):
        _, r = self.exercise({}); self.assertTrue(r['ok'])
    def test_raw_output_is_preserved_not_rendered(self):
        payload = b'before\r\x1b[2Kafter\n'
        command = [sys.executable, '-c', "import os;os.write(1," + repr(payload) + ");os.write(2,b'error\\n')"]
        r = runner.execute_stage(('capture', command), self.repo, self.out)
        self.assertEqual((self.out/r['stdout']).read_bytes(), payload)
        self.assertEqual((self.out/r['stderr']).read_bytes(), b'error\n')
        with self.assertRaises(FileExistsError): runner.execute_stage(('capture', command), self.repo, self.out)
    def test_log_directory_excludes_repo_and_environment(self):
        prefix=self.base/'env';prefix.mkdir()
        for parent in (self.repo/'logs',prefix/'logs'):
            with self.assertRaises(ValueError):runner.output_directory(parent,self.repo,prefix)
            self.assertFalse(parent.exists())
    def test_each_log_directory_is_new(self):
        prefix=self.base/'env';prefix.mkdir()
        a=runner.output_directory(self.out,self.repo,prefix)
        b=runner.output_directory(self.out,self.repo,prefix)
        self.assertNotEqual(a,b)
    def test_unittest_skips_are_not_full_acceptance(self):
        code="import sys;sys.stderr.write('Ran 3 tests in 0.1s\\nOK (skipped=1)\\n')"
        r=runner.execute_stage(('03-regression',[sys.executable,'-c',code]),self.repo,self.out)
        self.assertEqual(r['skipped'],1);self.assertFalse(r['complete_suite'])

if __name__=='__main__':unittest.main()
