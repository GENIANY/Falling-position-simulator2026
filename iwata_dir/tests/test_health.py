"""Intentional corruption checks for the temporal-document contract (offline)."""
from __future__ import annotations
import importlib.util
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('health',ROOT/'tools/check_health.py')
assert spec and spec.loader
health=importlib.util.module_from_spec(spec);spec.loader.exec_module(health)

class HealthTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
        self.r=Path(self.t.name)/'state';shutil.copytree(ROOT,self.r,ignore=lambda src, names: [n for n in names if n in {'.git', '__pycache__'} or n.endswith('.pyc') or (Path(src) / n).relative_to(ROOT).as_posix() in {'frontend/node_modules', 'frontend/dist', 'backend/.venv'}])
    def read(self,name='CONTENT_HEALTH'):return json.loads((self.r/f'docs/{name}.json').read_text(encoding='utf-8'))
    def write(self,data,name='CONTENT_HEALTH'):
        if name=='CONTENT_HEALTH':
            try:data['scan_index']=health.scan_index(data)
            except ValueError:pass
        (self.r/f'docs/{name}.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8', newline="\n")
    def result(self,**kwargs):
        baseline=max(u['review']['on'] for u in self.read()['units'] if u.get('review'))
        return health.inspect(self.r,as_of=kwargs.pop('as_of',baseline),**kwargs)
    def bad(self,text,**kwargs):
        r=self.result(**kwargs);self.assertFalse(r['ok'],r)
        self.assertTrue(any(text in e for e in r['errors']),r['errors'])
    def unit(self,data,id):return next(u for u in data['units'] if u['id']==id)
    def unreviewed_fixture(self):
        # The declared test source supplies opaque bytes, not a claim that PLAN
        # or any other project document must remain unreviewed forever. Reusing
        # a declared path also keeps before-state inventory validation active.
        from datetime import date,timedelta
        d=self.read();current=self.read('VERSION_HISTORY')['candidate_version']
        today=max(u['review']['on'] for u in d['units'] if u.get('review'))
        due=(date.fromisoformat(today)+timedelta(days=1)).isoformat()
        d['units'].append({'id':'FIXTURE-UNREVIEWED','path':'tests/test_health.py',
                          'parent':None,'role':'test fixture','purpose':'synthetic initial-review state',
                          'depends_on':[],'updated_in':current,'reviewed_in':None,
                          'review':None,'initial_review_due':due})
        self.write(d)
        return today,due
    def parent_child_fixture(self,*,review_parent=False,inherit_child=False):
        # Only synthetic HTML and receipts are added inside this test's copy.
        # No project scope is re-stamped to make the fixture pass.
        from datetime import date,timedelta
        d=self.read();current=self.read('VERSION_HISTORY')['candidate_version']
        today=max(u['review']['on'] for u in d['units'] if u.get('review'))
        due=(date.fromisoformat(today)+timedelta(days=1)).isoformat()
        path='tests/review-scope-fixture.html';p=self.r/path
        parent_mark=current if review_parent else '未確認'
        p.write_text('<article id="fixture-parent">\n'
                     f'<p class="revstamp">[更新:{current}] [確認:{parent_mark}]</p>\n'
                     '<p>Known parent remainder.</p>\n<section id="fixture-child">\n'
                     f'<p class="revstamp">[更新:{current}] [確認:{current}]</p>\n'
                     '<p>Known child content.</p>\n</section>\n</article>\n',
                     encoding='utf-8',newline='\n')
        d['files'][path]={'purpose':'synthetic parent/child review fixture'}
        d['evidence']['FIXTURE-REVIEW']={'method':'synthetic test fixture',
            'result':'known test content and explicitly chosen review state',
            'limits':'does not review project documents'}
        for uid,selector,parent,reviewed in (
                ('FIXTURE-PARENT','fixture-parent',None,review_parent),
                ('FIXTURE-CHILD','fixture-child','FIXTURE-PARENT',True)):
            inherited=bool(parent and inherit_child)
            d['units'].append({'id':uid,'path':path,'selector':selector,'parent':parent,
                'role':'test fixture','purpose':'synthetic scope boundaries and review inheritance',
                'depends_on':[],'inline_marker':True,'updated_in':None if inherited else current,
                'reviewed_in':current if reviewed and not inherited else None,
                'initial_review_due':due,'review':{'version':current,'on':today,
                    'evidence_id':'FIXTURE-REVIEW','dependency_sha256':{}} if reviewed else None})
        contents=health.Contents(self.r,d['units'])
        for uid in ('FIXTURE-PARENT','FIXTURE-CHILD'):
            u=self.unit(d,uid)
            if u['review']:u['review']['content_sha256']=contents.digest(u)
        self.write(d)
        return p
    def test_current_contract(self):
        r=self.result();self.assertTrue(r['ok'],r['errors'])
        expected={u['id'] for u in self.read()['units']
                  if not u.get('review') and u.get('control_mode')!='live_input'}
        self.assertEqual(expected,set(r['initial_unreviewed_scopes']))
    def test_before_comparison_optional_is_reported(self):
        self.assertTrue(any('--base omitted' in w for w in self.result()['warnings']))
    def test_complete_unchanged_before_state_is_accepted(self):
        before=Path(self.t.name)/'before';shutil.copytree(self.r,before)
        r=self.result(base=before)
        self.assertTrue(r['ok'],r['errors']);self.assertEqual([],r['changed_scopes'])
        self.assertFalse(any('--base omitted' in w for w in r['warnings']))
    def test_incomplete_before_state_is_not_a_successful_comparison(self):
        for missing in ('docs/CONTENT_HEALTH.json','docs/VERSION_HISTORY.json','.gitattributes'):
            with self.subTest(missing=missing):
                before=Path(self.t.name)/('before-'+Path(missing).name)
                shutil.copytree(self.r,before);(before/missing).unlink()
                self.bad('incomplete comparison base',base=before)
    def test_nonexistent_or_empty_before_state_is_rejected(self):
        for name,create in (('absent',False),('empty',True)):
            with self.subTest(name=name):
                before=Path(self.t.name)/name
                if create:before.mkdir()
                self.assertFalse(self.result(base=before)['ok'])
    def test_before_state_registry_must_cover_declared_files(self):
        before=Path(self.t.name)/'before';shutil.copytree(self.r,before)
        p=before/'docs/CONTENT_HEALTH.json';d=json.loads(p.read_text(encoding='utf-8'))
        d['files'].pop('.gitattributes')
        p.write_text(json.dumps(d),encoding='utf-8',newline='\n')
        self.bad('comparison base file coverage',base=before)
    def test_display_options_cannot_bypass_requested_checks(self):
        import subprocess,sys
        for flag in ('--index','--fingerprints'):
            for check in (['--base',str(self.r)],['--scope','PLAN'],['--as-of','2026-10-01']):
                with self.subTest(flag=flag,check=check):
                    r=subprocess.run([sys.executable,'-B',str(ROOT/'tools/check_health.py'),
                                      str(self.r),flag,*check],capture_output=True)
                    self.assertNotEqual(0,r.returncode)
                    self.assertIn(b'display-only',r.stderr)
    def test_display_modes_are_mutually_exclusive(self):
        import subprocess,sys
        r=subprocess.run([sys.executable,'-B',str(ROOT/'tools/check_health.py'),
                          str(self.r),'--index','--fingerprints'],capture_output=True)
        self.assertNotEqual(0,r.returncode)
    def test_unknown_focus(self):
        d=self.read();d['focus'].append('NOT-A-SCOPE');self.write(d);self.bad('unknown focus')
    def test_changed_content_invalidates_receipt(self):
        p=self.r/'README.md';p.write_text(p.read_text(encoding="utf-8")+'\n内容を無断変更\n',encoding='utf-8', newline="\n");self.bad('review fingerprint mismatch: ENTRY')
    def test_stamp_without_receipt(self):
        d=self.read();self.unit(d,'ENTRY')['review']=None;self.write(d);self.bad('review stamp without receipt')
    def test_missing_evidence(self):
        d=self.read();d['evidence'].pop(self.unit(d,'ENTRY')['review']['evidence_id']);self.write(d);self.bad('review evidence incomplete')
    def test_inline_evidence_must_exist(self):
        evidence=self.unit(self.read(),'ENTRY')['review']['evidence_id']
        p=self.r/'README.md';p.write_text(p.read_text(encoding="utf-8").replace(evidence,'REV-999-NO-RECORD'),encoding='utf-8', newline="\n")
        self.bad('inline evidence reference missing')
    def test_days_threshold(self):
        baseline=__import__('datetime').date.fromisoformat(self.unit(self.read(),'ENTRY')['review']['on'])
        future=(baseline+__import__('datetime').timedelta(days=30)).isoformat()
        r=self.result(as_of=future);self.assertFalse(r['ok']);self.assertIn('review_expired',r['due_scopes']['ENTRY'])
    def test_unfocused_initial_due_is_not_ignored(self):
        today,due=self.unreviewed_fixture()
        r=self.result(as_of=today);self.assertTrue(r['ok'],r['errors'])
        self.assertNotIn('FIXTURE-UNREVIEWED',r['required_scopes'])
        r=self.result(as_of=due);self.assertFalse(r['ok'])
        self.assertIn('initial_review_due',r['due_scopes']['FIXTURE-UNREVIEWED'])
        self.assertIn('FIXTURE-UNREVIEWED',r['required_scopes'])
    def test_requesting_unreviewed_scope_requires_review_now(self):
        self.unreviewed_fixture()
        self.bad('required scope not reviewed: FIXTURE-UNREVIEWED',extra=['FIXTURE-UNREVIEWED'])
    def version_age_fixture(self,mode='advisory'):
        # Synthetic scopes isolate the age trigger from the live document focus.
        # Receipts below are test data only, not reviews of project material.
        d=self.read();history=self.read('VERSION_HISTORY');current=history['candidate_version']
        if mode is None:d['policy'].pop('version_age_mode',None)
        else:d['policy']['version_age_mode']=mode
        old=history['version_order'][-d['policy']['max_versions']-1]
        today=max(u['review']['on'] for u in d['units'] if u.get('review'))
        d['evidence']['FIXTURE-AGE']={'method':'synthetic test fixture','result':'known test bytes',
                                     'limits':'does not review project content'}
        for uid in ('FIXTURE-AGE','FIXTURE-CHILD','FIXTURE-DEP'):
            path='tests/'+uid.lower()+'.txt'
            (self.r/path).write_text(uid+'\n',encoding='utf-8',newline='\n')
            d['files'][path]={'purpose':'synthetic test fixture'}
            version=old if uid=='FIXTURE-AGE' else current
            d['units'].append({'id':uid,'path':path,'role':'test fixture','purpose':'isolate review triggers',
                               'parent':'FIXTURE-AGE' if uid=='FIXTURE-CHILD' else None,
                               'depends_on':['FIXTURE-DEP'] if uid=='FIXTURE-AGE' else [],
                               'updated_in':version,'reviewed_in':version,
                               'review':{'version':version,'on':today,'evidence_id':'FIXTURE-AGE'}})
        c=health.Contents(self.r,d['units'])
        for uid in ('FIXTURE-AGE','FIXTURE-CHILD','FIXTURE-DEP'):
            u=self.unit(d,uid);u['review']['content_sha256']=c.digest(u)
            u['review']['dependency_sha256']={dep:c.digest(c.units[dep],False) for dep in u['depends_on']}
        self.write(d)
        return today
    def test_version_threshold(self):
        self.version_age_fixture(mode=None)
        for mode in (None,'required'):
            with self.subTest(mode=mode):
                d=self.read()
                if mode is not None:d['policy']['version_age_mode']=mode
                self.write(d);r=self.result()
                self.assertFalse(r['ok']);self.assertIn('review_expired',r['due_scopes']['FIXTURE-AGE'])
                self.assertTrue({'FIXTURE-AGE','FIXTURE-CHILD','FIXTURE-DEP'}.issubset(r['required_scopes']))
                self.assertEqual({},r['version_age_advisories'])
    def test_version_age_mode_rejects_unknown_values(self):
        for mode in ('optional','ADVISORY',None,[],{}):
            with self.subTest(mode=mode):
                d=self.read();d['policy']['version_age_mode']=mode;self.write(d)
                self.bad('invalid policy version_age_mode')
    def test_version_age_advisory_does_not_expand_scope_or_stamp(self):
        self.version_age_fixture()
        p=self.r/'docs/CONTENT_HEALTH.json';before=p.read_bytes();r=self.result()
        self.assertTrue(r['ok'],r['errors']);self.assertEqual(before,p.read_bytes())
        for uid in ('FIXTURE-AGE','FIXTURE-CHILD','FIXTURE-DEP'):
            self.assertNotIn(uid,r['required_scopes']);self.assertNotIn(uid,r['due_scopes'])
        advisory=r['version_age_advisories']['FIXTURE-AGE']
        self.assertEqual('version_age_threshold',advisory['reason'])
        self.assertEqual(self.read()['policy']['max_versions'],advisory['version_age'])
        self.assertTrue(any('version-age review advisories:' in w for w in r['warnings']))
        d=self.read();u=self.unit(d,'FIXTURE-AGE')
        newer=self.read('VERSION_HISTORY')['version_order'][-d['policy']['max_versions']]
        u['updated_in']=newer;u['reviewed_in']=newer;u['review']['version']=newer;self.write(d)
        r=self.result();self.assertTrue(r['ok'],r['errors']);self.assertNotIn('FIXTURE-AGE',r['version_age_advisories'])
    def test_version_age_advisory_keeps_calendar_expiry_mandatory(self):
        from datetime import date,timedelta
        today=self.version_age_fixture()
        r=self.result(as_of=(date.fromisoformat(today)+timedelta(days=30)).isoformat())
        self.assertFalse(r['ok']);self.assertIn('review_expired',r['due_scopes']['FIXTURE-AGE'])
        self.assertIn('FIXTURE-AGE',r['required_scopes'])
    def test_version_age_advisory_keeps_first_review_mandatory(self):
        from datetime import date,timedelta
        today=self.version_age_fixture();d=self.read();u=self.unit(d,'FIXTURE-AGE')
        u['review']=None;u['reviewed_in']=None
        u['initial_review_due']=(date.fromisoformat(today)+timedelta(days=1)).isoformat();self.write(d)
        r=self.result();self.assertTrue(r['ok'],r['errors'])
        self.bad('required scope not reviewed: FIXTURE-AGE',extra=['FIXTURE-AGE'])
        u['initial_review_due']=today;self.write(d);r=self.result()
        self.assertFalse(r['ok']);self.assertIn('initial_review_due',r['due_scopes']['FIXTURE-AGE'])
    def test_version_age_advisory_keeps_content_change_mandatory(self):
        self.version_age_fixture();p=self.r/'tests/fixture-age.txt'
        p.write_text('changed fixture\n',encoding='utf-8',newline='\n');r=self.result()
        self.assertFalse(r['ok']);self.assertIn('content_changed_since_review',r['due_scopes']['FIXTURE-AGE'])
        self.assertIn('review fingerprint mismatch: FIXTURE-AGE',r['errors'])
        self.assertIn('FIXTURE-AGE',r['required_scopes'])
    def test_version_age_advisory_keeps_dependency_change_mandatory(self):
        self.version_age_fixture();p=self.r/'tests/fixture-dep.txt'
        p.write_text('changed dependency\n',encoding='utf-8',newline='\n');r=self.result()
        self.assertFalse(r['ok']);self.assertIn('dependency_changed_since_review',r['due_scopes']['FIXTURE-AGE'])
        self.assertIn('review dependency mismatch: FIXTURE-AGE',r['errors'])
        self.assertIn('FIXTURE-AGE',r['required_scopes'])
    def test_marker_mismatch(self):
        p=self.r/'README.md';p.write_text(p.read_text(encoding="utf-8").replace('[更新:'+self.read('VERSION_HISTORY')['candidate_version']+']','[更新:0.2.0]',1),encoding='utf-8', newline="\n");self.bad('update marker mismatch: ENTRY')
    def test_child_inherits_parent_marker(self):
        self.parent_child_fixture(review_parent=True,inherit_child=True)
        d=self.read();u=self.unit(d,'FIXTURE-CHILD');c=health.Contents(self.r,d['units'])
        self.assertIsNone(u['updated_in']);self.assertIsNone(u['reviewed_in'])
        for field in ('updated_in','reviewed_in'):
            self.assertEqual(c.effective(self.unit(d,'FIXTURE-PARENT'),field),c.effective(u,field))
        r=self.result();self.assertTrue(r['ok'],r['errors'])
    def test_inherited_review_still_requires_matching_child_receipt(self):
        self.parent_child_fixture(review_parent=True,inherit_child=True)
        d=self.read();u=self.unit(d,'FIXTURE-CHILD')
        u['review']['version']=self.read('VERSION_HISTORY')['version_order'][-2]
        self.write(d);self.bad('receipt/review version mismatch: FIXTURE-CHILD')
    def test_dependency_edit_invalidates_dependent(self):
        p=self.r/'docs/DOCUMENT_CONTROL.md';p.write_text(p.read_text(encoding="utf-8")+'\n新しい規則\n',encoding='utf-8', newline="\n");self.bad('review dependency mismatch: ENTRY')
    def test_dependency_cycle(self):
        d=self.read();self.unit(d,'CONTROL')['depends_on']=['ENTRY'];self.write(d);self.bad('dependency cycle')
    def test_parent_cycle(self):
        d=self.read();self.unit(d,'RUNBOOK')['parent']='RB-S06';self.write(d);self.bad('parent cycle')
    def test_missing_selector(self):
        d=self.read();self.unit(d,'RB-S06')['selector']='missing-id';self.write(d);self.bad('scope selector missing')
    def test_git_cycle(self):
        d=self.read('VERSION_HISTORY');d['transitions'][0]['parents']=[d['transitions'][-1]['sha']];self.write(d,'VERSION_HISTORY');self.bad('Git cycle')
    def test_candidate_cannot_claim_future_sha(self):
        d=self.read('VERSION_HISTORY');d['versions'][-1]['integrated_commit']='a'*40;self.write(d,'VERSION_HISTORY');self.bad('candidate has invented integrated SHA')
    def test_timeline_view_mismatch(self):
        d=self.read('VERSION_HISTORY');d['versions'][0]['summary']='Changed only in JSON';self.write(d,'VERSION_HISTORY');self.bad('timeline summary differs')
    def test_changed_content_needs_current_version_even_with_new_fingerprint(self):
        before=Path(self.t.name)/'before';shutil.copytree(self.r,before)
        p=self.r/'README.md';p.write_text(p.read_text(encoding="utf-8").replace('[更新:'+self.read('VERSION_HISTORY')['candidate_version']+']','[更新:0.3.0]',1)+'\n新しい操作\n',encoding='utf-8', newline="\n")
        d=self.read();u=self.unit(d,'ENTRY');u['updated_in']='0.3.0';u['review']['content_sha256']=health.Contents(self.r,d['units']).digest(u);self.write(d)
        self.bad('changed content without current update marker: ENTRY',base=before)
    def test_initial_due_cannot_be_rolled_forward_silently(self):
        from datetime import date,timedelta
        _,due=self.unreviewed_fixture()
        before=Path(self.t.name)/'before';shutil.copytree(self.r,before)
        self.assertTrue(self.result(base=before)['ok'])
        d=self.read();self.unit(d,'FIXTURE-UNREVIEWED')['initial_review_due']=(
            date.fromisoformat(due)+timedelta(days=30)).isoformat();self.write(d)
        self.bad('initial due postponed without review: FIXTURE-UNREVIEWED',base=before)
    def test_positive_threshold_required(self):
        d=self.read();d['policy']['max_days']=0;self.write(d);self.bad('invalid policy threshold')
    def test_empty_focus_is_rejected(self):
        d=self.read();d['focus']=[];self.write(d);self.bad('core entry scope missing')
    def test_live_probe_change_is_not_a_document_review(self):
        p=self.r/'ACCESS_PROBE.md';p.write_text('# probe\nprobe_revision: 2\nprobe_value: new non-secret value\n',encoding='utf-8', newline="\n")
        r=self.result();self.assertTrue(r['ok'],r['errors'])
        self.assertEqual(r['live_checks_required'][0]['status'],'not_performed_by_offline_checker')
    def test_scan_index_corruption_is_rejected(self):
        p=self.r/'docs/CONTENT_HEALTH.json';d=self.read();d['scan_index'][0][1]='0.1.0'
        p.write_text(json.dumps(d,ensure_ascii=False),encoding='utf-8', newline="\n");self.bad('scan index is stale')

    def test_recovery_vision_survives_narrow_focus(self):
        d=self.read();d['focus']=['ENTRY','CTX','MAP','REFS','CONTROL','HISTORY'];self.write(d)
        r=self.result();self.assertTrue(r['ok'],r['errors'])
        self.assertIn('PLAN-ROADMAP',r['required_scopes']);self.assertIn('PLAN-ROLES',r['required_scopes'])
    def test_recovery_required_scope_cannot_be_removed(self):
        d=self.read();d['recovery_contract']['required_scopes'].remove('PLAN-ROADMAP');self.write(d)
        self.bad('recovery minimum scopes missing')
    def test_recovery_outcome_cannot_be_removed(self):
        d=self.read();d['recovery_contract']['required_outcomes']=[x for x in d['recovery_contract']['required_outcomes'] if x['id']!='RC-HORIZON'];self.write(d)
        self.bad('recovery outcomes missing')
    def test_recovery_readme_result_cannot_be_omitted(self):
        p=self.r/'README.md';p.write_text(p.read_text(encoding="utf-8").replace('| RC-HORIZON |','| Removed |'),encoding='utf-8', newline="\n")
        self.bad('README recovery outcome missing: RC-HORIZON')
    def test_recovery_html_result_cannot_be_omitted(self):
        p=self.r/'BOOTSTRAP_RUNBOOK.html';p.write_text(p.read_text(encoding="utf-8").replace('data-recovery-outcome="RC-HORIZON"','data-removed="RC-HORIZON"'),encoding='utf-8', newline="\n")
        self.bad('HTML recovery outcome missing or duplicated: RC-HORIZON')
    def test_procedure_stop_field_missing(self):
        p=self.r/'BOOTSTRAP_RUNBOOK.html';text=p.read_text(encoding="utf-8");a,b=health.Spans(text).spans['S08-1a']
        text=text[:a]+text[a:b].replace('data-role="stop"','data-removed="stop"')+text[b:];p.write_text(text,encoding='utf-8', newline="\n")
        self.bad('procedure field missing or repeated: RB-S08-1a: stop')
    def test_procedure_previous_instruction_shortcut(self):
        p=self.r/'BOOTSTRAP_RUNBOOK.html';text=p.read_text(encoding="utf-8");a,b=health.Spans(text).spans['S08-1c']
        part=text[a:b].replace('Commit changes…','U01と同じ方法で操作する')
        p.write_text(text[:a]+part+text[b:],encoding='utf-8', newline="\n");self.bad('procedure shortcut')
    def test_text_range_requires_unique_start(self):
        p=self.r/'docs/PROJECT_PLAN.md';d=self.read();u=self.unit(d,'PLAN-ROADMAP')
        p.write_text(p.read_text(encoding="utf-8")+u['text_range']['start'],encoding='utf-8', newline="\n");self.bad('text range must have unique boundaries')
    def test_text_range_requires_end(self):
        d=self.read();self.unit(d,'PLAN-ROADMAP')['text_range']['end']='not present';self.write(d)
        self.bad('text range must have unique boundaries')
    def test_text_range_requires_order(self):
        d=self.read();u=self.unit(d,'PLAN-ROADMAP');u['text_range']['start'],u['text_range']['end']=u['text_range']['end'],u['text_range']['start'];self.write(d)
        self.bad('reversed text range')
    def test_scoped_review_does_not_review_parent_remainder(self):
        p=self.parent_child_fixture();d=self.read();c=health.Contents(self.r,d['units'])
        u=self.unit(d,'FIXTURE-CHILD');before=c.digest(u)
        parent=self.unit(d,'FIXTURE-PARENT');parent_before=c.digest(parent)
        p.write_text(p.read_text(encoding='utf-8').replace('Known parent remainder.','Changed parent remainder.'),
                     encoding='utf-8',newline='\n')
        self.assertEqual(before,health.Contents(self.r,d['units']).digest(u))
        self.assertNotEqual(parent_before,health.Contents(self.r,d['units']).digest(parent))
        r=self.result();self.assertTrue(r['ok'],r['errors'])
        self.assertIn('FIXTURE-PARENT',r['initial_unreviewed_scopes'])
        self.assertNotIn('FIXTURE-CHILD',r['initial_unreviewed_scopes'])
        self.bad('required scope not reviewed: FIXTURE-PARENT',extra=['FIXTURE-PARENT'])
    def test_reviewed_parent_remainder_change_invalidates_only_parent(self):
        p=self.parent_child_fixture(review_parent=True)
        p.write_text(p.read_text(encoding='utf-8').replace('Known parent remainder.','Changed parent remainder.'),
                     encoding='utf-8',newline='\n')
        r=self.result();self.assertFalse(r['ok'])
        self.assertIn('review fingerprint mismatch: FIXTURE-PARENT',r['errors'])
        self.assertNotIn('review fingerprint mismatch: FIXTURE-CHILD',r['errors'])
    def test_scoped_vision_change_invalidates_review(self):
        p=self.r/'docs/PROJECT_PLAN.md';p.write_text(p.read_text(encoding="utf-8").replace('P1から始める','P5から始める'),encoding='utf-8', newline="\n")
        self.bad('review fingerprint mismatch: PLAN-ROADMAP')

    def edit_scope(self, selector, old, new):
        p=self.r/'BOOTSTRAP_RUNBOOK.html';text=p.read_text(encoding='utf-8')
        a,b=health.Spans(text).spans[selector]
        self.assertIn(old,text[a:b])
        p.write_text(text[:a]+text[a:b].replace(old,new,1)+text[b:],encoding='utf-8', newline="\n")
    def test_s09_requires_stop_condition(self):
        self.edit_scope('S09-1b','data-role="stop"','data-missing="stop"')
        self.bad('procedure field missing or repeated: RB-S09-1b: stop')
    def test_s09_cannot_defer_to_old_instructions(self):
        self.edit_scope('S09-1b','Propose changes','U02と同様に進める')
        self.bad('procedure shortcut')
    def test_s09_contract_cannot_be_weakened(self):
        d=self.read();d['procedure_contract']['scopes'].remove('RB-S09-2');self.write(d)
        self.bad('procedure contract scope missing')
    def test_completed_s08_requires_user_confirmation(self):
        self.edit_scope('S08-acceptance','data-user-confirmed="true"','data-user-confirmed="false"')
        self.bad('completed S08 lacks user confirmation')
    def test_completed_s08_requires_evidence_identity(self):
        self.edit_scope('S08-acceptance','data-answer="RC-004"','data-answer=""')
        self.bad('completed S08 lacks report or answer evidence')
    def test_completed_s08_requires_pinned_commit(self):
        self.edit_scope('S08-acceptance','data-commit="114f88cfc2593fbb75296823e174126f8b7557a3"','data-commit="main"')
        self.bad('completed S08 lacks pinned commit')
    def test_completed_s08_requires_all_outcomes(self):
        self.edit_scope('S08-3','data-acceptance="passed"','data-acceptance="waiting"')
        self.bad('completed S08 outcome not accepted')
    def test_retention_limits_cannot_disappear(self):
        self.edit_scope('retention','data-retention-rule="RET-03"','data-removed="RET-03"')
        self.bad('retention rules missing or duplicated')


    def test_environment_readonly_command_contract(self):
        text=(self.r/'BOOTSTRAP_RUNBOOK.html').read_text(encoding='utf-8')
        spans=health.Spans(text).spans
        for command_id in ('CMD-ENV-01','CMD-ENV-02'):
            self.assertIn(command_id,spans)
            a,b=spans[command_id]
            code=__import__('html').unescape(re.sub('<[^>]+>','',text[a:b]))
            active='\n'.join(line for line in code.splitlines() if not line.lstrip().startswith('#'))
            self.assertNotRegex(active, r'(?im)^\s*(?:conda\s+(?:install|update|create|init)|pip\s+install|Set-ExecutionPolicy|Remove-Item)\b')
        a,b=spans['CMD-ENV-02'];code=text[a:b]
        self.assertIn('--no-optional-locks',code)
        self.assertIn('core.fsmonitor=false',code)
        self.assertIn('Read-Host',code)
        self.assertNotIn('remote.origin.url: $origin',code)

    def test_environment_acceptance_preserves_failure_history(self):
        text=(self.r/'BOOTSTRAP_RUNBOOK.html').read_text(encoding='utf-8')
        spans=health.Spans(text).spans
        # Accepted historical events stay true; the next task is not frozen here.
        for ident,status in {'E02':'done','E02-1':'done','E02-2':'done',
                             'E02-3':'done','E02-4':'done',
                             'F01':'done','F01-1':'done','F01-2':'done','F01-3':'done'}.items():
            a,b=spans[ident]
            self.assertIn('data-status="'+status+'"',text[a:text.index('>',a)])
        for value in ('RPT-008','77','RPT-010','CHK-010','ER-081-01','E02-4','CMD-CHECK-02','CMD-GIT-02','@@@'):
            self.assertIn(value,text)

    def test_fixture_text_writes_explicitly_use_lf(self):
        import ast
        for file in ('test_health.py','test_state.py'):
            tree=ast.parse((ROOT/'tests'/file).read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='write_text':
                    options={kw.arg:kw.value for kw in node.keywords}
                    self.assertIn('newline',options,(file,node.lineno))
                    self.assertEqual(ast.literal_eval(options['newline']),'\n',(file,node.lineno))

    def test_real_crlf_corruption_is_still_rejected(self):
        p=self.r/'docs/PROJECT_PLAN.md'
        p.write_bytes(p.read_bytes().replace(b'\n',b'\r\n'))
        self.bad('text range must have unique boundaries')

    def test_emulated_windows_default_preserves_scoped_mutations(self):
        from unittest.mock import patch
        original=Path.open
        def win_open(path,mode='r',buffering=-1,encoding=None,errors=None,newline=None):
            if any(c in mode for c in 'wax+') and 'b' not in mode and newline is None:
                newline='\r\n'
            return original(path,mode,buffering,encoding,errors,newline)
        names=('test_scoped_review_does_not_review_parent_remainder',
               'test_scoped_vision_change_invalidates_review')
        for name in names:
            with self.subTest(name=name):
                inner=HealthTests(name)
                inner.setUp()
                try:
                    with patch.object(Path,'open',win_open):getattr(inner,name)()
                finally:inner.doCleanups()

if __name__=='__main__':unittest.main()
