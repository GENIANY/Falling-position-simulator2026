"""Regression checks for the current-tree verifier; no network, stdlib only."""
from __future__ import annotations
import csv
import hashlib
import json
import re
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('check_state',ROOT/'tools/check_state.py')
assert spec and spec.loader
checker=importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

class CurrentStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'current'
        shutil.copytree(ROOT,self.root,ignore=lambda src, names: [n for n in names if n in {'.git', '__pycache__'} or n.endswith('.pyc') or (Path(src) / n).relative_to(ROOT).as_posix() in {'frontend/node_modules', 'frontend/dist', 'backend/.venv'}])
    def version(self):
        return json.loads((self.root/'docs/VERSION_HISTORY.json').read_text(encoding='utf-8'))['candidate_version']
    def reject(self, substring: str) -> None:
        result=checker.inspect(self.root)
        self.assertFalse(result['ok'])
        self.assertTrue(any(substring in e for e in result['errors']),result['errors'])
    def test_current_tree_passes(self) -> None:
        result=checker.inspect(self.root)
        self.assertTrue(result['ok'],result['errors'])
    def test_plain_cli_does_not_create_bytecode_or_change_files(self) -> None:
        import os,subprocess,sys
        before={p.relative_to(self.root).as_posix():p.read_bytes()
                for p in self.root.rglob('*') if p.is_file()}
        env=os.environ.copy();env.pop('PYTHONDONTWRITEBYTECODE',None)
        result=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'tools/check_state.py'),
                               str(self.root)],env=env,capture_output=True,check=False)
        self.assertEqual(0,result.returncode,result.stderr.decode('utf-8',errors='replace'))
        self.assertTrue(json.loads(result.stdout.decode('utf-8'))['ok'])
        after={p.relative_to(self.root).as_posix():p.read_bytes()
               for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after)
    def test_missing_file(self) -> None:
        (self.root/'README.md').unlink(); self.reject('missing=')
    def test_extra_old_tree(self) -> None:
        (self.root/'legacy').mkdir(); (self.root/'legacy/old.md').write_text('old', encoding="utf-8", newline="\n")
        self.reject('archive/version directory')
    def test_body_status_mismatch(self) -> None:
        import re
        p=self.root/'BOOTSTRAP_RUNBOOK.html'
        text=p.read_text(encoding='utf-8')
        text=re.sub(r'<section[^>]*id="S01"[^>]*>',lambda m:m[0].replace('data-status="done"','data-status="todo"'),text,count=1)
        p.write_text(text,encoding='utf-8', newline="\n"); self.reject('body status mismatch at S01')
    def test_broken_local_link(self) -> None:
        with (self.root/'README.md').open('a',encoding='utf-8',newline='\n') as f: f.write('\n[bad](missing.md)\n')
        self.reject('broken local link')
    def test_pdf_loses_tex(self) -> None:
        (self.root/'docs/PROJECT_PLAN.tex').unlink(); self.reject('PDF without TeX')
    def test_done_without_evidence(self) -> None:
        p=self.root/'docs/BACKLOG.csv'
        with p.open(encoding='utf-8-sig',newline='') as f:
            reader=csv.DictReader(f); names=reader.fieldnames; rows=list(reader)
        rows[0]['status']='完了'; rows[0]['evidence']=''
        with p.open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=names); w.writeheader(); w.writerows(rows)
        self.reject('done task without evidence')
    def test_parent_cannot_close_waiting_child(self) -> None:
        import re
        p=self.root/'BOOTSTRAP_RUNBOOK.html'
        text=p.read_text(encoding='utf-8')
        text=re.sub(r'<section[^>]*id="S10"[^>]*>',lambda m:m[0].replace('data-status="partial"','data-status="done"'),text,count=1)
        p.write_text(text,encoding='utf-8', newline="\n"); self.reject('done parent has unfinished children')
    def test_mixed_document_revision(self) -> None:
        p=self.root/'PROJECT_CONTEXT.md'
        p.write_text(p.read_text(encoding='utf-8').replace('revision: '+self.version(),'revision: 0.2.0'),encoding='utf-8', newline="\n")
        self.reject('unregistered document revision')
    def test_stale_snapshot_id(self) -> None:
        p=self.root/'BOOTSTRAP_RUNBOOK.html'
        p.write_text(p.read_text(encoding='utf-8').replace('BJP-current-'+self.version(),'BJP-current-0.3.0'),encoding='utf-8', newline="\n")
        self.reject('HTML snapshot id differs')
    def test_stale_footer_version(self) -> None:
        p=self.root/'BOOTSTRAP_RUNBOOK.html'
        p.write_text(p.read_text(encoding='utf-8').replace('END OF RUNBOOK · BJP-current-'+self.version(),'END OF RUNBOOK · BJP-current-0.4.0'),encoding='utf-8', newline="\n")
        self.reject('HTML footer version differs')
    def test_integration_ignores_git_metadata(self) -> None:
        (self.root/'.git').mkdir(); (self.root/'.git/config').write_text('local test', encoding="utf-8", newline="\n")
        self.assertTrue(checker.inspect(self.root)['ok'])
    def test_script_target_missing(self) -> None:
        p=self.root/'BOOTSTRAP_RUNBOOK.html'
        p.write_text(p.read_text(encoding='utf-8').replace('id="progress-links"','id="removed-progress-links"'),encoding='utf-8', newline="\n")
        self.reject('script DOM target missing: progress-links')
class RuntimeSourceBoundaryTests(unittest.TestCase):
    """Independent small trees exercise the new source/runtime boundary."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def put(self, name):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b'fixture')

    def scan(self, expected=()):
        failures = []
        actual = checker.source_files(self.root, list(expected),
                                      lambda ok, message: failures.append(message) if not ok else None)
        return actual, failures

    def test_exact_runtime_roots_do_not_hide_other_source(self):
        visible = {'frontend/src/extra.ts', 'frontend/node_modules_extra/source.ts',
                   'docs/node_modules/source.ts', 'backend/app.py', '.gitignore'}
        for name in visible: self.put(name)
        for name in ('frontend/node_modules/vendor/src/source.ts', 'frontend/dist/bundle.js',
                     'backend/.venv/Lib/site-packages/vendor/code.py'):
            self.put(name)
        self.assertEqual((visible, []), self.scan())

    def test_registered_runtime_source_is_rejected_even_when_missing(self):
        for name in ('frontend/dist/missing.ts', 'frontend/node_modules', 'backend/.venv/app.py'):
            with self.subTest(name=name):
                _, errors = self.scan([name])
                self.assertTrue(any('registered source inside runtime root' in x for x in errors))

    def test_pyc_directory_does_not_hide_source(self):
        self.put('frontend/src/cache.pyc/hidden.ts')
        self.put('backend/module.pyc')
        self.assertEqual(({'frontend/src/cache.pyc/hidden.ts'}, []), self.scan())

    def test_directory_misclassified_by_walk_is_rejected(self):
        from unittest.mock import patch
        self.put('backend/nested/hidden.py')
        # A failed DirEntry.is_dir call in os.walk can yield a directory as a
        # file and never visit its contents, even when subsequent lstat works.
        walked = [(str(self.root), ['backend'], []),
                  (str(self.root / 'backend'), [], ['nested'])]
        with patch.object(checker.os, 'walk', return_value=iter(walked)):
            _, errors = self.scan()
        self.assertTrue(any('source directory was not traversed' in x for x in errors), errors)

    def test_runtime_root_cannot_be_a_file(self):
        self.put('frontend/node_modules')
        _, errors = self.scan()
        self.assertTrue(any('runtime root must be a directory' in x for x in errors), errors)

    def test_reparse_runtime_root_and_ancestor_are_rejected_without_descending(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        self.put('frontend/node_modules/vendor/hidden.py')
        self.put('frontend/src/app.ts')
        original = Path.lstat
        for name in ('frontend/node_modules', 'frontend'):
            target = self.root / name
            def tagged(path, *args, **kwargs):
                value = original(path, *args, **kwargs)
                if path == target:
                    return SimpleNamespace(st_mode=value.st_mode, st_file_attributes=1024)
                return value
            with self.subTest(name=name), patch.object(Path, 'lstat', tagged):
                actual, errors = self.scan()
                self.assertTrue(any('symlink/reparse point not allowed' in x for x in errors), errors)
                self.assertFalse(any(x.startswith(name + '/') for x in actual))

    def test_metadata_and_old_archive_rules_still_apply(self):
        self.put('.git/config')
        self.put('backend/__pycache__/app.pyc')
        self.put('legacy/old.py')
        self.put('frontend/v0.1/old.ts')
        actual, errors = self.scan()
        self.assertEqual({'legacy/old.py', 'frontend/v0.1/old.ts'}, actual)
        self.assertEqual(2, sum('archive/version directory' in x for x in errors))


class ProvidedPdfTests(unittest.TestCase):
    """Small original-reference fixtures, independent of rendered project PDFs."""
    def setUp(self) -> None:
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/'docs').mkdir()
        (self.root/'references/user_supplied').mkdir(parents=True)
        self.name='references/user_supplied/original.pdf'
        self.pdf=self.root/self.name
        self.pdf.write_bytes(b'%PDF-1.4\noriginal reference bytes\n')
        self.asset={'path':self.name,'lifecycle':'reference','provided_pdf':{
            'tex_source':'not_provided','sha256':hashlib.sha256(self.pdf.read_bytes()).hexdigest(),
            'source_record':'USER-PDF','reason':'Original supplied PDF; no TeX source supplied.'}}
        self.source={'id':'USER-PDF','url':'local:'+self.name}
    def inspect(self):
        (self.root/'docs/CONTINUITY_CONTRACT.json').write_text(
            json.dumps({'assets':[self.asset]}),encoding='utf-8',newline='\n')
        (self.root/'references/SOURCES.json').write_text(
            json.dumps({'sources':[self.source]}),encoding='utf-8',newline='\n')
        return checker.provided_pdf_paths(self.root)
    def reject(self, message):
        accepted,errors=self.inspect()
        self.assertFalse(accepted)
        self.assertTrue(any(message in e for e in errors),errors)
    def test_original_pdf_requires_exact_declared_bytes(self):
        self.assertEqual(({self.name},[]),self.inspect())
        self.pdf.write_bytes(self.pdf.read_bytes()+b'changed')
        self.reject('original SHA-256 mismatch')
    def test_missing_declared_original_is_rejected(self):
        self.pdf.unlink()
        self.reject('original bytes unavailable')
    def test_source_record_must_match_local_path(self):
        self.source['url']='local:references/user_supplied/another.pdf'
        self.reject('source_record must uniquely identify')
        self.source['id']='UNRELATED'
        self.reject('source_record must uniquely identify')
    def test_generated_pdf_cannot_use_original_exception(self):
        self.asset['lifecycle']='generated'
        self.reject('lifecycle must be reference')
    def test_original_exception_rejects_unsafe_or_nonreference_paths(self):
        for name in ('docs/PROJECT_PLAN.pdf','references/user_supplied/../outside.pdf',
                     '/references/user_supplied/original.pdf',
                     'references\\user_supplied\\original.pdf'):
            with self.subTest(path=name):
                self.asset['path']=name
                self.reject('unsafe path')
    def test_original_exception_requires_typed_declaration(self):
        declaration=self.asset['provided_pdf']
        for key,value,error in (('tex_source','generated','tex_source'),
                                ('sha256','not-a-hash','sha256'),
                                ('reason','  ','reason')):
            with self.subTest(field=key):
                self.asset['provided_pdf']=dict(declaration,**{key:value})
                self.reject(error)
        self.asset['provided_pdf']=None
        self.reject('must be an object')

if __name__=='__main__': unittest.main()
