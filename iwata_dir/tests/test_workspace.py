"""Offline Git fixtures for workspace guards; no user repository or network."""
from __future__ import annotations
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('prepare_workspace', ROOT/'tools/prepare_workspace.py')
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

@unittest.skipUnless(shutil.which('git'), 'Git executable required for offline workspace fixtures')
class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='balloon-test-')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        template = self.base/'empty-template'
        template.mkdir()
        self.git_env = mock.patch.dict(os.environ, {
            'GIT_CONFIG_NOSYSTEM': '1',
            'GIT_CONFIG_GLOBAL': str(self.base/'empty-config'),
            'GIT_TEMPLATE_DIR': str(template),
        })
        self.git_env.start()
        self.addCleanup(self.git_env.stop)
        self.remote = self.base/'remote'
        self.remote.mkdir()
        self.git(self.remote, 'init', '-b', 'main')
        self.git(self.remote, 'config', 'user.name', 'Offline Fixture')
        self.git(self.remote, 'config', 'user.email', 'fixture@example.invalid')
        self.git(self.remote, 'config', 'core.autocrlf', 'false')
        (self.remote/'README.md').write_bytes('日本語の本文\nsecond line\n'.encode())
        (self.remote/'binary.pdf').write_bytes(b'%PDF\x00\r\nunchanged\r\n')
        # Stage 1 intentionally has no attributes: mimics the reported clone.
        self.git(self.remote, 'add', '.')
        self.git(self.remote, 'commit', '-m', 'initial')
        self.first = self.git(self.remote, 'rev-parse', 'HEAD').decode().strip()
        self.repo = self.base/'日本語 と 空白'/'clone'
        self.repo.parent.mkdir()
        self.git(self.base, 'clone', '-c', 'core.autocrlf=true', str(self.remote), str(self.repo))
        self.git(self.repo, 'config', 'remote.origin.url', 'https://github.com/'+mod.REPOSITORY+'.git')
        self.ws = mod.Workspace(self.repo)

    def git(self, where, *args):
        proc = subprocess.run(['git','-C',str(where),*args],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if proc.returncode:
            self.fail(str(args)+': '+proc.stderr.decode('utf-8',errors='replace'))
        return proc.stdout

    def add_attributes(self):
        (self.repo/'.gitattributes').write_bytes((ROOT/'.gitattributes').read_bytes())
        self.git(self.repo,'-c','user.name=Offline Fixture','-c','user.email=fixture@example.invalid','add','.gitattributes')
        self.git(self.repo,'-c','user.name=Offline Fixture','-c','user.email=fixture@example.invalid','commit','-m','attributes')
        return self.ws.head()

    def publish(self):
        (self.remote/'.gitattributes').write_bytes((ROOT/'.gitattributes').read_bytes())
        (self.remote/'NEXT.md').write_bytes(b'next\n')
        self.git(self.remote,'add','.')
        self.git(self.remote,'commit','-m','next')
        return self.git(self.remote,'rev-parse','HEAD').decode().strip()

    def local_transport(self):
        # Test-only redirect; production constructor still allows only known GitHub URLs.
        self.ws.origin = str(self.remote)

    def test_unicode_root_and_read_only_inspection(self):
        result=self.ws.inspect()
        self.assertTrue(result['root_matches_input'])
        self.assertEqual(Path(result['root']),self.repo)
        self.assertIn('README.md',result['crlf_only_paths'])
        self.assertFalse(result['network_used'])

    def test_preview_does_not_write(self):
        target=self.add_attributes();old=(self.repo/'README.md').read_bytes()
        result=self.ws.normalize(target)
        self.assertEqual(result['planned'],['README.md'])
        self.assertEqual(old,(self.repo/'README.md').read_bytes())

    def test_apply_restores_exact_head_and_preserves_binary_config(self):
        target=self.add_attributes();before=self.git(self.repo,'config','--local','--list')
        binary=(self.repo/'binary.pdf').read_bytes()
        self.assertEqual(self.ws.normalize(target,True)['changed'],['README.md'])
        self.assertEqual((self.repo/'README.md').read_bytes(),self.git(self.repo,'show','HEAD:README.md'))
        self.assertEqual((self.repo/'binary.pdf').read_bytes(),binary)
        self.assertEqual(self.git(self.repo,'config','--local','--list'),before)
        self.assertTrue(self.ws.verify(target)['head_bytes_equal'])

    def test_apply_is_idempotent(self):
        target=self.add_attributes();self.ws.normalize(target,True)
        self.assertEqual(self.ws.normalize(target,True)['changed'],[])

    def test_missing_lf_contract_rejected(self):
        with self.assertRaisesRegex(mod.Stop,'contract'):
            self.ws.normalize(self.first,True)

    def test_modified_text_is_never_overwritten(self):
        target=self.add_attributes();p=self.repo/'README.md';p.write_bytes(p.read_bytes()+b'edit\n');old=p.read_bytes()
        with self.assertRaises(mod.Stop):self.ws.normalize(target,True)
        self.assertEqual(p.read_bytes(),old)

    def test_staged_change_is_never_overwritten(self):
        target=self.add_attributes();p=self.repo/'README.md';p.write_bytes(b'new\n');self.git(self.repo,'add','README.md')
        with self.assertRaises(mod.Stop):self.ws.normalize(target,True)
        self.assertEqual(p.read_bytes(),b'new\n')

    def test_untracked_file_preserved(self):
        target=self.add_attributes();p=self.repo/'my_notes.txt';p.write_bytes(b'notes')
        with self.assertRaises(mod.Stop):self.ws.normalize(target,True)
        self.assertEqual(p.read_bytes(),b'notes')

    def test_wrong_sha_is_rejected(self):
        self.add_attributes()
        with self.assertRaisesRegex(mod.Stop,'HEAD mismatch'):
            self.ws.normalize(self.first,True)

    def test_assume_unchanged_is_rejected(self):
        target=self.add_attributes();self.git(self.repo,'update-index','--assume-unchanged','README.md')
        with self.assertRaisesRegex(mod.Stop,'flags'):
            self.ws.normalize(target,True)

    def test_binary_change_is_rejected(self):
        target=self.add_attributes();p=self.repo/'binary.pdf';p.write_bytes(b'new\r\nbinary')
        with self.assertRaises(mod.Stop):self.ws.normalize(target,True)
        self.assertEqual(p.read_bytes(),b'new\r\nbinary')

    def test_overridden_attributes_are_rejected(self):
        target=self.add_attributes()
        (self.repo/'.git/info').mkdir(exist_ok=True)
        (self.repo/'.git/info/attributes').write_bytes(b'*.md text eol=crlf\n')
        with self.assertRaisesRegex(mod.Stop,'contract'):self.ws.normalize(target,True)

    def test_sync_fast_forward_and_cached_ref(self):
        target=self.publish();self.local_transport();self.ws.sync(target)
        self.assertEqual(self.ws.head(),target)
        self.assertEqual(self.git(self.repo,'rev-parse','origin/main').decode().strip(),target)
        self.ws.normalize(target,True)
        self.assertTrue(self.ws.verify(target)['head_bytes_equal'])

    def test_remote_advance_stops_before_worktree_change(self):
        target=self.publish();self.local_transport()
        with self.assertRaisesRegex(mod.Stop,'not requested'):self.ws.sync(self.first)
        self.assertEqual(self.ws.head(),self.first)
        self.assertFalse((self.repo/'NEXT.md').exists())

    def test_dirty_sync_does_not_fetch(self):
        (self.repo/'notes').write_bytes(b'keep');self.local_transport()
        with self.assertRaises(mod.Stop):self.ws.sync(self.publish())
        self.assertFalse((self.repo/'.git/FETCH_HEAD').exists())

    def test_sync_preserves_ignored_file_when_target_tracks_same_path(self):
        (self.repo/'.git/info').mkdir(exist_ok=True)
        (self.repo/'.git/info/exclude').write_bytes(b'NEXT.md\n')
        note=self.repo/'NEXT.md';note.write_bytes(b'user-only ignored notes\n')
        before=self.ws.head();original=note.read_bytes()
        target=self.publish();self.local_transport()
        with self.assertRaises(mod.Stop):self.ws.sync(target)
        self.assertEqual(self.ws.head(),before)
        self.assertEqual(note.read_bytes(),original)
        self.assertFalse((self.repo/'.gitattributes').exists())
        # Fetch may have succeeded; the stop must precede worktree replacement.
        self.assertEqual(self.git(self.repo,'rev-parse','FETCH_HEAD').decode().strip(),target)

    def test_sync_keeps_unrelated_ignored_file_without_blocking(self):
        (self.repo/'.git/info').mkdir(exist_ok=True)
        (self.repo/'.git/info/exclude').write_bytes(b'local-notes.txt\n')
        note=self.repo/'local-notes.txt';note.write_bytes(b'user-only ignored notes\n')
        target=self.publish();self.local_transport()
        self.assertTrue(self.ws.sync(target)['ok'])
        self.assertEqual(self.ws.head(),target)
        self.assertEqual(note.read_bytes(),b'user-only ignored notes\n')

    def test_divergent_branch_stops(self):
        self.add_attributes();before=self.ws.head();target=self.publish();self.local_transport()
        with self.assertRaisesRegex(mod.Stop,'not an ancestor'):self.ws.sync(target)
        self.assertEqual(self.ws.head(),before)

    def test_subdirectory_rejected(self):
        d=self.repo/'child';d.mkdir()
        with self.assertRaisesRegex(mod.Stop,'root'):mod.Workspace(d)

    def test_credential_origin_never_echoed(self):
        self.git(self.repo,'config','remote.origin.url','https://secret-token@github.com/'+mod.REPOSITORY+'.git')
        with self.assertRaises(mod.Stop) as cm:mod.Workspace(self.repo)
        self.assertNotIn('secret-token',str(cm.exception))



# The HTML copy original is part of the tested calling interface. These tests
# execute extracted Python/Git argv, not the whole PowerShell interpreter.
def documented_sync_calls(source: str) -> list[list[str]]:
    import html
    import re
    pre = re.findall(r'<pre\b[^>]*id="cmd-git-02"[^>]*>(.*?)</pre>', source, re.S)
    if len(pre) != 1:
        raise ValueError('Exactly one documented CMD-GIT-02 block is required.')
    code = html.unescape(re.sub(r'<[^>]*>', '', pre[0]))
    calls = []
    for line in code.splitlines():
        m = re.fullmatch(r'\s*& \$py -X utf8 -B \$tool (.*)', line)
        if m:
            calls.append(m[1].split())
    expected = [
        ['verify', '--repo', '$repo', '--git', '$git', '--expected-head', '$before'],
        ['sync', '--repo', '$repo', '--git', '$git', '--expected-head', '$target'],
        ['verify', '--repo', '$repo', '--git', '$git', '--expected-head', '$target'],
    ]
    if calls != expected:
        raise ValueError('Documented CLI requires before for pre-verify and target for sync/post.')
    if code.index('rev-parse --verify HEAD') >= code.index('$tool verify'):
        raise ValueError('Read local HEAD before pre-verification.')
    return calls


@unittest.skipUnless(shutil.which('git'), 'Git executable required for offline CLI fixtures')
class DocumentedCallTests(unittest.TestCase):
    # Reuse setup functions, NOT existing test methods or test counts.
    git = WorkspaceTests.git
    publish = WorkspaceTests.publish
    local_transport = WorkspaceTests.local_transport

    def setUp(self):
        WorkspaceTests.setUp(self)
        self.target = self.publish()
        self.local_transport()
        self.ws.sync(self.target)
        self.ws.normalize(self.target, True)
        self.calls = documented_sync_calls((ROOT/'BOOTSTRAP_RUNBOOK.html').read_text(encoding='utf-8'))

    def call(self, args, *, before=None, target=None):
        import json
        import sys
        values = {'$repo': str(self.repo), '$git': shutil.which('git'),
                  '$before': before or self.ws.head(), '$target': target or self.target}
        argv = [values.get(x, x) for x in args]
        env = os.environ.copy()
        # Offline transport only: the production URL validation is kept intact.
        env.update(GIT_CONFIG_COUNT='1',
                   GIT_CONFIG_KEY_0='url.'+self.remote.as_uri()+'.insteadOf',
                   GIT_CONFIG_VALUE_0='https://github.com/'+mod.REPOSITORY+'.git',
                   GIT_TERMINAL_PROMPT='0', PYTHONDONTWRITEBYTECODE='1')
        p = subprocess.run([sys.executable,'-X','utf8','-B',str(ROOT/'tools/prepare_workspace.py'),*argv],
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,check=False)
        return p.returncode, json.loads(p.stdout.decode('utf-8'))

    def test_documented_call_contract_is_complete(self):
        self.assertEqual([x[0] for x in self.calls], ['verify','sync','verify'])

    def test_original_missing_head_is_rejected(self):
        source=(ROOT/'BOOTSTRAP_RUNBOOK.html').read_text(encoding='utf-8')
        source=source.replace('--git $git --expected-head $before','--git $git',1)
        with self.assertRaisesRegex(ValueError,'requires before'):
            documented_sync_calls(source)

    def test_future_target_in_precheck_is_rejected(self):
        source=(ROOT/'BOOTSTRAP_RUNBOOK.html').read_text(encoding='utf-8')
        source=source.replace('--git $git --expected-head $before','--git $git --expected-head $target',1)
        with self.assertRaisesRegex(ValueError,'requires before'):
            documented_sync_calls(source)

    def test_extracted_pre_and_post_accept_same_head(self):
        for i in (0,2):
            code,result=self.call(self.calls[i])
            self.assertEqual(code,0,result)
            self.assertTrue(result['head_bytes_equal'])

    def test_missing_expected_head_cli_stops_before_workspace(self):
        code,result=self.call(self.calls[0][:-2])
        self.assertEqual(code,1)
        self.assertIn('--expected-head is required',result['error'])
        self.assertEqual(self.ws.head(),self.target)

    def test_wrong_before_cli_fails_without_repair(self):
        code,result=self.call(self.calls[0],before='0'*40)
        self.assertEqual(code,1)
        self.assertIn('HEAD mismatch',result['error'])
        self.assertEqual(self.ws.head(),self.target)

    def test_documented_sequence_advances_only_to_target(self):
        before=self.ws.head()
        (self.remote/'NEXT.md').write_bytes(b'later\n')
        self.git(self.remote,'add','NEXT.md');self.git(self.remote,'commit','-m','later')
        target=self.git(self.remote,'rev-parse','HEAD').decode().strip()
        for argv in self.calls:
            code,result=self.call(argv,before=before,target=target)
            self.assertEqual(code,0,result)
        self.assertEqual(self.ws.head(),target)
        self.assertEqual((self.repo/'NEXT.md').read_bytes(),b'later\n')

    def test_documented_sequence_same_head_is_idempotent(self):
        before=self.ws.head()
        for argv in self.calls:
            code,result=self.call(argv,before=before)
            self.assertEqual(code,0,result)
        self.assertEqual(self.ws.head(),before)

    def test_dirty_precheck_keeps_user_edit(self):
        p=self.repo/'README.md';p.write_bytes(b'user edit\n')
        code,result=self.call(self.calls[0]);self.assertEqual(code,1,result)
        self.assertEqual(p.read_bytes(),b'user edit\n')

    def test_untracked_precheck_keeps_user_file(self):
        p=self.repo/'notes.txt';p.write_bytes(b'keep')
        code,result=self.call(self.calls[0]);self.assertEqual(code,1,result)
        self.assertEqual(p.read_bytes(),b'keep')

    def test_other_branch_is_not_switched(self):
        self.git(self.repo,'switch','-c','user-work')
        code,result=self.call(self.calls[0]);self.assertEqual(code,1,result)
        self.assertEqual(self.git(self.repo,'branch','--show-current').strip(),b'user-work')

    def test_new_crlf_difference_is_not_implicitly_normalized(self):
        p=self.repo/'README.md';original=p.read_bytes();p.write_bytes(original.replace(b'\n',b'\r\n'))
        code,result=self.call(self.calls[0]);self.assertEqual(code,1,result)
        self.assertEqual(p.read_bytes(),original.replace(b'\n',b'\r\n'))

if __name__=='__main__':unittest.main()
