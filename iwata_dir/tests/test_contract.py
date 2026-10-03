"""Isolated mutation tests for rationale/lifecycle/argument-structure coverage.

No network or writes to the original. These tests are not semantic truth review.
"""
from __future__ import annotations
import importlib.util
import csv
import json
import re
from html.parser import HTMLParser
from pathlib import Path
import shutil
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('continuity',ROOT/'tools/check_contract.py')
assert spec and spec.loader
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)


class CurrentPreconditions(HTMLParser):
    """Test-only reading of the existing current-procedure/precondition markup."""
    VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
    def __init__(self,text):
        super().__init__();self.stack=[];self.values=[];self.feed(text);self.close()
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        activity=self.stack[-1][1] if self.stack else None
        activity=attrs.get('data-activity',activity)
        capture=self.stack[-1][2] if self.stack else None
        if attrs.get('data-role')=='precondition' and activity=='current':
            capture=len(self.values);self.values.append([])
        if activity!='current':capture=None
        if tag not in self.VOID:self.stack.append((tag,activity,capture))
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                del self.stack[i:];break
    def handle_data(self,data):
        if self.stack and self.stack[-1][2] is not None:
            self.values[self.stack[-1][2]].append(data)


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.r=Path(self.tmp.name)/'state'
        shutil.copytree(ROOT,self.r,ignore=lambda src, names: [n for n in names if n in {'.git', '__pycache__'} or n.endswith('.pyc') or (Path(src) / n).relative_to(ROOT).as_posix() in {'frontend/node_modules', 'frontend/dist', 'backend/.venv'}])
    def data(self):return c.load(self.r)
    def save(self,d,view=False):
        (self.r/c.CONTRACT).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
        if view:
            f=self.r/'CONTENT_MAP.md';s=f.read_text(encoding='utf8');start=s.index('<!-- ASSET_VIEW_BEGIN -->')+len('<!-- ASSET_VIEW_BEGIN -->\n');end=s.index('\n<!-- ASSET_VIEW_END -->',start)
            f.write_text(s[:start]+c.asset_view(d)+s[end:],encoding='utf8',newline='\n')
    def bad(self,term,base=None):
        r=c.inspect(self.r,base);self.assertFalse(r['ok'],r)
        self.assertTrue(any(term in e for e in r['errors']),r)
    def assert_current_main_observation(self,text,sha):
        fields=CurrentPreconditions(text).values
        self.assertTrue(fields,'current procedure has no precondition')
        values=' '.join(''.join(parts) for parts in fields)
        self.assertIn(sha,re.findall(r'(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])',values),
                      'observed main missing from current precondition')
    def change(self,d,field,value):
        next(x for x in d['assets'] if x['path']=='tools/run_checks.py')[field]=value
        self.save(d)
    def before(self):
        p=Path(self.tmp.name)/'before';shutil.copytree(self.r,p)
        d=self.data();d['comparison_base_sha256']=c.snapshot_digest(p);self.save(d);return p
    def edit_argument(self):
        f=self.r/'CONTENT_MAP.md';s=f.read_text(encoding='utf8')
        f.write_text(s.replace('その内容について、何を検査できるのか','その内容の保証をどう変更するのか'),encoding='utf8',newline='\n')
    def test_current_contract(self):
        r=c.inspect(self.r);self.assertTrue(r['ok'],r)
    def test_document_version_must_match_its_registry_record(self):
        d=self.data();d['version']='0.0.0';self.save(d)
        self.bad('continuity document version differs from registry')
    def test_document_version_may_predate_current_project_version(self):
        d=self.data();d['version']='0.10.0';self.save(d)
        p=self.r/'docs/CONTENT_HEALTH.json';h=json.loads(p.read_text(encoding='utf-8'))
        h['files'][c.CONTRACT]['document_version']=d['version']
        p.write_text(json.dumps(h),encoding='utf-8',newline='\n')
        r=c.inspect(self.r);self.assertTrue(r['ok'],r)
    def test_all_assets_have_exact_coverage(self):
        d=self.data();d['assets'].pop();self.save(d);self.bad('coverage differs')
    def test_empty_purpose_rejected(self):
        d=self.data();self.change(d,'purpose','');self.bad('asset field missing')
    def test_thread_only_purpose_rejected(self):
        d=self.data();self.change(d,'purpose','このスレッドの前半を参照');self.bad('thread-only asset')
    def test_thread_only_health_role_rejected(self):
        f=self.r/'docs/CONTENT_HEALTH.json';d=json.loads(f.read_text(encoding='utf8'))
        next(x for x in d['units'] if x['id']=='WORKSPACE-TOOL')['purpose']='このスレッドの前半を参照'
        f.write_text(json.dumps(d,ensure_ascii=False),encoding='utf8',newline='\n');self.bad('thread-only review')
    def test_retirement_condition_required(self):
        d=self.data();self.change(d,'retire_when','');self.bad('retire_when')
    def test_consumer_required(self):
        d=self.data();self.change(d,'needed_by',[]);self.bad('consumer missing')
    def test_unknown_consumer_rejected(self):
        d=self.data();self.change(d,'needed_by',['not_a_file.py']);self.bad('unknown consumer')
    def test_generated_asset_has_source(self):
        d=self.data();next(a for a in d['assets'] if a['path']=='docs/PROJECT_PLAN.pdf')['source_paths']=[];self.save(d);self.bad('generated asset lacks source')
    def test_derivation_cycle_rejected(self):
        d=self.data();next(a for a in d['assets'] if a['path']=='docs/PROJECT_PLAN.md')['source_paths']=['docs/PROJECT_PLAN.pdf'];self.save(d);self.bad('derivation cycle')
    def test_task_cycle_rejected(self):
        p=self.r/'docs/BACKLOG.csv'
        with p.open(encoding='utf8',newline='') as f:r=csv.DictReader(f);fields=r.fieldnames;rows=list(r)
        next(x for x in rows if x['id']=='T-006')['depends_on']='T-005'
        with p.open('w',encoding='utf8',newline='') as f:w=csv.DictWriter(f,fields,lineterminator='\n');w.writeheader();w.writerows(rows)
        self.bad('task cycle')
    def test_narrative_purpose_required(self):
        d=self.data();d['narrative_units'][0]['contribution']='';self.save(d);self.bad('narrative field missing')
    def test_narrative_cannot_depend_on_chat(self):
        d=self.data();d['narrative_units'][0]['order_reason']='前の会話を参照';self.save(d);self.bad('thread-only narrative')
    def test_narrative_boundary_deleted(self):
        d=self.data();n=d['narrative_units'][0];p=self.r/n['path'];p.write_text(p.read_text(encoding='utf8').replace(n['start'],''),encoding='utf8',newline='\n');self.bad('boundary missing')
    def test_narrative_cycle_rejected(self):
        d=self.data();d['narrative_units'][0]['parent']=d['narrative_units'][0]['id'];self.save(d);self.bad('narrative parent cycle')
    def test_narrative_child_must_be_in_parent(self):
        d=self.data();n=next(n for n in d['narrative_units'] if n['id']=='TOOL-CHECKS');n['parent']='C-A';self.save(d);self.bad('child outside parent')
    def test_asset_view_removed(self):
        p=self.r/'CONTENT_MAP.md';s=p.read_text(encoding='utf8');p.write_text(s.replace('<!-- ASSET_VIEW_BEGIN -->','<!-- not inventory -->'),encoding='utf8',newline='\n');self.bad('derived asset view')
    def test_external_artifact_provenance_required(self):
        d=self.data();d['external_artifacts'][0]['reproduction']='';self.save(d);self.bad('external-artifact rule incomplete')
    def test_handoff_no_fake_ready(self):
        # Construct missing evidence explicitly. The released source may already
        # contain a legitimately completed handoff; that is not this fixture.
        d=self.data();d['handoff']['status']='ready'
        d['handoff']['readback_evidence']=None
        d['handoff']['accepted_residuals']=[]
        self.save(d);self.bad('ready handoff lacks evidence')
    def test_ready_requires_readback_even_with_residuals(self):
        d=self.data();d['handoff']['status']='ready'
        d['handoff']['readback_evidence']=None
        d['handoff']['accepted_residuals']=['fixture: scientific validity not certified']
        self.save(d);self.bad('ready handoff lacks evidence')
    def test_ready_requires_residuals_even_with_readback(self):
        d=self.data();d['handoff']['status']='ready'
        d['handoff']['readback_evidence']={'id':'fixture', 'method':'fixture only'}
        d['handoff']['accepted_residuals']=[]
        self.save(d);self.bad('ready handoff lacks evidence')
    def test_handoff_challenge_cannot_disappear(self):
        d=self.data();d['handoff']['questions']=[];self.save(d);self.bad('handoff challenge')
    def test_changed_argument_requires_actual_previous_comparison(self):
        before=self.before();self.edit_argument();d=self.data()
        # Make the missing-comparison precondition explicit. Do not rely on
        # whichever narrative IDs happened to be changed by this release.
        d['changes']=[{'id':'missing-digests','version':d['version'],
                      'units':['TOOL-CHECKS'],'reason':'説明を明確化','preserved':'既存制約'}]
        self.save(d);self.bad('prior comparison evidence missing',before)
    def test_changed_argument_without_event(self):
        before=self.before();self.edit_argument();d=self.data();d['changes']=[];self.save(d);self.bad('changed without reason record',before)
    def test_matching_comparison_and_rationale_accepted(self):
        before=self.before();self.edit_argument();d=self.data();old=c.load(before);oldnodes={n['id']:n for n in old['narrative_units']}
        ids=[n['id'] for n in d['narrative_units'] if c.digest(before,oldnodes[n['id']])!=c.digest(self.r,n)]
        event={'id':'example','version':d['version'],'units':ids,'reason':'結論を維持して問いの言い方を改める','preserved':'検査境界の全説明','before_digests':{},'after_digests':{}}
        for n in d['narrative_units']:
            if n['id'] in ids:event['before_digests'][n['id']]=c.digest(before,oldnodes[n['id']]);event['after_digests'][n['id']]=c.digest(self.r,n)
        d['changes'].append(event);self.save(d);r=c.inspect(self.r,before);self.assertTrue(r['ok'],r)
    def test_asset_role_change_needs_reason(self):
        before=self.before();d=self.data();next(a for a in d['assets'] if a['path']=='tools/run_checks.py')['current_role']='新しい役割';self.save(d,view=True);self.bad('asset contract changed without reason',before)
    def test_unsafe_path_rejected(self):
        d=self.data();d['assets'][0]['path']='../outside';self.save(d);self.bad('unsafe contract path')
    def test_checker_does_not_write(self):
        before={p.relative_to(self.r).as_posix():p.read_bytes() for p in self.r.rglob('*') if p.is_file()}
        c.inspect(self.r)
        after={p.relative_to(self.r).as_posix():p.read_bytes() for p in self.r.rglob('*') if p.is_file()}
        self.assertEqual(before,after)


class EvolutionTests(ContractTests):
    """Multi-version fixtures test legitimate edits as well as forbidden ones."""
    # Do not inherit the base suite's test methods twice.
    def record_structure(self,base,reason='責務境界を維持した明示的な変更'):
        d=self.data();old=c.load(base);left=c.structural_projection(base,old);right=c.structural_projection(self.r,d)
        snap=c.snapshot_digest(base);d['comparison_base_sha256']=snap
        d['structural_changes']=[r for r in d.get('structural_changes',[]) if r.get('base_snapshot_sha256')!=snap]
        for key in sorted(set(left)|set(right)):
            if left.get(key)==right.get(key):continue
            d['structural_changes'].append({'key':key,'version':d['version'],
                'comparison_basis':d['basis_commit'],'base_snapshot_sha256':snap,
                'before_sha256':c.canonical_digest(left.get(key)),
                'after_sha256':c.canonical_digest(right.get(key)),
                'kind':'guard' if key.startswith('guard:') else 'migration' if key not in left or key not in right else 'compatible',
                'reason':reason,'preserved':'既存の安全境界','impact':'該当利用箇所を再確認',
                'recovery':'元の固定版で読取を再開','replacement':'明示的な後継または当該役割の終了'})
        self.save(d)
    def record_body(self,base):
        d=self.data();old={n['id']:n for n in c.load(base)['narrative_units']}
        ns=[n for n in d['narrative_units'] if c.digest(base,old[n['id']])!=c.digest(self.r,n) or old[n['id']]!=n]
        d['changes'].append({'id':'fixture','version':d['version'],'units':[n['id'] for n in ns],
            'reason':'用語を明確化して前提を保持','preserved':'既存の制約と根拠',
            'comparison_basis':d['basis_commit'],
            'before_digests':{n['id']:c.digest(base,old[n['id']]) for n in ns},
            'after_digests':{n['id']:c.digest(self.r,n) for n in ns}})
        self.save(d)
    def test_design_order_change_rejected(self):
        b=self.before();d=self.data();d['document_designs'][0]['ordering_reason']='別の順番';self.save(d)
        self.bad('structural transition record missing',b)
    def test_feeds_change_rejected(self):
        b=self.before();d=self.data();d['narrative_units'][0]['feeds']=['TOOL-BUILD'];self.save(d)
        self.bad('structural transition record missing',b)
    def test_external_retention_change_rejected(self):
        b=self.before();d=self.data();d['external_artifacts'][0]['retention']='原報告を確認なしで廃棄';self.save(d)
        self.bad('structural transition record missing',b)
    def test_guard_change_rejected_by_fixed_comparator(self):
        b=self.before();(self.r/'tools/check_state.py').write_text('print("ok")\n',encoding='utf8',newline='\n')
        self.bad('structural transition record missing',b)
    def test_validator_itself_is_guarded(self):
        b=self.before();(self.r/'tools/check_contract.py').write_text('print("ok")\n',encoding='utf8',newline='\n')
        self.bad('guard:tools/check_contract.py',b)
    def test_policy_change_needs_record(self):
        b=self.before();p=self.r/'docs/CONTENT_HEALTH.json';d=json.loads(p.read_text(encoding='utf-8'));d['policy']['max_days']=3000
        p.write_text(json.dumps(d),encoding='utf8',newline='\n');self.bad('health:policy',b)
    def test_wrong_baseline_rejected(self):
        b=self.before();(b/'README.md').write_bytes((b/'README.md').read_bytes()+b'\nchanged base\n')
        self.bad('comparison baseline bytes not bound',b)
    def test_scope_dependency_change_needs_record(self):
        b=self.before();p=self.r/'docs/CONTENT_HEALTH.json';d=json.loads(p.read_text(encoding='utf-8'));d['units'][0]['depends_on']=[]
        p.write_text(json.dumps(d),encoding='utf8',newline='\n');self.bad('structural transition record missing',b)
    def test_noop_and_dictionary_reorder_stable(self):
        b=self.before();d=self.data();d['assets'].reverse();d['narrative_units'].reverse();self.save(d,view=True)
        r=c.inspect(self.r,b);self.assertTrue(r['ok'],r);self.assertEqual([],r['transition']['changes'])
    def test_status_progress_does_not_change_topology(self):
        b=self.before();d=self.data();d['handoff']['status']='integrated_pending_readback';self.save(d)
        r=c.inspect(self.r,b);self.assertTrue(r['ok'],r);self.assertEqual([],r['transition']['changes'])
    def test_local_leaf_edit_not_counted_as_ancestor_edit(self):
        b=self.before();p=self.r/'docs/DOCUMENT_CONTROL.md';s=p.read_text(encoding='utf-8');s=s.replace('現在の版と採否を別々に復元できる。','現在の版と採否を区別して復元できる。',1);p.write_text(s,encoding='utf8',newline='\n')
        self.record_body(b);r=c.inspect(self.r,b);self.assertTrue(r['ok'],r)
        self.assertEqual(['DC-TIME'],r['changed_narrative_units'])
        self.assertEqual(['C-A','CONTROL-LOGIC'],r['ancestor_impact_review'])
    def test_matching_structural_change_accepted(self):
        b=self.before();d=self.data();d['document_designs'][0]['ordering_reason']+='（順序理由を明確化）';self.save(d)
        self.record_structure(b);r=c.inspect(self.r,b);self.assertTrue(r['ok'],r)
        self.assertEqual(['design:docs/DOCUMENT_CONTROL.md'],r['transition']['changes'])
    def test_forged_after_evidence_rejected(self):
        b=self.before();d=self.data();d['document_designs'][0]['ordering_reason']='理由';self.save(d);self.record_structure(b)
        d=self.data();d['structural_changes'][-1]['after_sha256']='0'*64;self.save(d);self.bad('after evidence mismatch',b)
    def test_recycled_change_record_rejected(self):
        b=self.before();d=self.data();d['document_designs'][0]['ordering_reason']='理由';self.save(d);self.record_structure(b)
        d=self.data();d['structural_changes'][-1]['comparison_basis']='0'*40;self.save(d);self.bad('missing or ambiguous',b)
    def test_guard_cannot_be_disguised_as_compatible(self):
        b=self.before();(self.r/'tools/check_state.py').write_bytes((self.r/'tools/check_state.py').read_bytes()+b'\n# changed\n');self.record_structure(b)
        d=self.data();d['structural_changes'][-1]['kind']='compatible';self.save(d);self.bad('guard change must be explicit',b)
    def test_deleted_rule_without_disposition_rejected(self):
        b=self.before();d=self.data();d['external_artifacts'].pop();self.save(d);self.record_structure(b)
        d=self.data();d['structural_changes'][-1]['replacement']='';self.save(d);self.bad('explicit disposition',b)
    def test_new_role_with_migration_record_allowed(self):
        b=self.before();d=self.data();x=dict(d['external_artifacts'][0]);x['id']='EXT-FIXTURE';d['external_artifacts'].append(x);self.save(d);self.record_structure(b)
        self.assertTrue(c.inspect(self.r,b)['ok'])
    def test_unsupported_schema_requires_migration(self):
        b=self.before();d=self.data();d['schema_version']=2;self.save(d);self.bad('schema change needs',b)
    def test_transition_requires_base_on_cli(self):
        import subprocess,sys
        r=subprocess.run([sys.executable,'-B',str(ROOT/'tools/check_contract.py'),str(self.r),'--transition'],capture_output=True)
        self.assertNotEqual(r.returncode,0);self.assertIn(b'requires --base',r.stderr)
    def test_three_successive_ordinary_edits_preserve_structure(self):
        original=c.structural_projection(self.r)
        for step in range(3):
            b=Path(self.tmp.name)/('version'+str(step));shutil.copytree(self.r,b)
            d=self.data();d['comparison_base_sha256']=c.snapshot_digest(b);d['version']='0.10.'+str(step);self.save(d)
            p=self.r/'docs/CONTENT_HEALTH.json';h=json.loads(p.read_text(encoding='utf-8'))
            h['files'][c.CONTRACT]['document_version']=d['version']
            p.write_text(json.dumps(h),encoding='utf-8',newline='\n')
            p=self.r/'docs/DOCUMENT_CONTROL.md';s=p.read_text(encoding='utf-8');needle='現在の版と採否を別々に復元できる。'
            s=s.replace(needle,needle+' 検査用の意味保持補足'+str(step)+'。',1);p.write_text(s,encoding='utf8',newline='\n')
            self.record_body(b);r=c.inspect(self.r,b);self.assertTrue(r['ok'],r)
            self.assertEqual(['DC-TIME'],r['changed_narrative_units']);self.assertEqual([],r['transition']['changes'])
            self.assertEqual(original,c.structural_projection(self.r))
    def test_document_unit_order_is_significant(self):
        b=self.before();d=self.data();d['document_designs'][0]['unit_ids'].reverse();self.save(d);self.bad('structural transition record missing',b)
    def test_explicit_reparenting_with_preserved_identity_accepted(self):
        b=self.before();d=self.data();node=next(n for n in d['narrative_units'] if n['id']=='DC-ASSET')
        p=self.r/node['path'];s=p.read_text(encoding='utf8')
        a=s.index(node['start']);end=s.index(node['end'])+len(node['end']);part=s[a:end]
        s=s[:a]+s[end:];position=s.index('<!-- LOGIC:C-D:END -->');s=s[:position]+part+'\n'+s[position:]
        p.write_text(s,encoding='utf8',newline='\n');node['parent']='C-D'
        design=next(x for x in d['document_designs'] if x['path']==node['path'])
        design['unit_ids'].remove('DC-ASSET');design['unit_ids'].insert(design['unit_ids'].index('C-D'),'DC-ASSET')
        design['ordering_reason']+='（fixture:退役判断を変更の枝で説明する）'
        self.save(d);self.record_body(b);self.record_structure(b,'同じIDを保って説明場所を変更する検査用移行')
        r=c.inspect(self.r,b);self.assertTrue(r['ok'],r)
        expected_ids={n['id'] for n in json.loads((b/c.CONTRACT).read_text(encoding='utf-8'))['narrative_units']}
        self.assertEqual(expected_ids,{n['id'] for n in self.data()['narrative_units']})
        self.assertEqual(len(expected_ids),r['transition']['preserved_narrative_ids'])
        self.assertIn('node:DC-ASSET',r['transition']['changes'])
    def test_record_without_real_transition_rejected(self):
        b=self.before();d=self.data();d['structural_changes'].append({'key':'node:DC-ASSET',
            'version':d['version'],'base_snapshot_sha256':c.snapshot_digest(b)})
        self.save(d);self.bad('no corresponding transition',b)
    def test_repeated_projection_is_deterministic(self):
        one=c.structural_projection(self.r);self.assertEqual(one,c.structural_projection(self.r))
    def test_omitted_base_not_called_transition_success(self):
        self.assertEqual('not_run_without_base',c.inspect(self.r)['transition']['status'])
    def test_stability_policy_cannot_be_dropped_silently(self):
        b=self.before();d=self.data();d.pop('stability_policy');self.save(d);self.bad('policy:stability',b)

    def test_current_precondition_observation_matches_version_history(self):
        text=(self.r/'BOOTSTRAP_RUNBOOK.html').read_text(encoding='utf-8')
        history=json.loads((self.r/'docs/VERSION_HISTORY.json').read_text(encoding='utf-8'))
        self.assert_current_main_observation(text,history['last_observed_main']['sha'])
    def test_current_observation_fixture_allows_short_cover_and_nested_code(self):
        sha='a'*40
        text=('<header>A short current guide</header><section data-activity="current">'
              f'<p data-role="precondition">Pinned main <code>{sha}</code></p></section>')
        self.assert_current_main_observation(text,sha)
    def test_current_observation_fixture_rejects_history_only_or_wrong_role(self):
        sha='a'*40;wrong='b'*40
        history=(f'<header>{sha}</header><section data-activity="history">'
                 f'<p data-role="precondition"><code>{sha}</code></p></section>')
        for current in (
                f'<section data-activity="current"><p data-role="precondition">{wrong}</p></section>',
                f'<section data-activity="current"><p data-role="record">{sha}</p></section>',
                '<section data-activity="current"><p data-role="precondition">missing</p></section>',
                ''):
            with self.subTest(current=current),self.assertRaises(AssertionError):
                self.assert_current_main_observation(history+current,sha)


# Reuse only fixture helpers, not the existing test cases (unittest inheritance
# otherwise silently inflates the apparent coverage).
for _name in list(ContractTests.__dict__):
    if _name.startswith('test_') and _name not in EvolutionTests.__dict__:
        setattr(EvolutionTests,_name,None)


class EntryBoundaryTests(ContractTests):
    """Exercise real external entry text and failed comparison prerequisites."""
    def alter_html(self, old, new):
        p=self.r/'BOOTSTRAP_RUNBOOK.html';text=p.read_text(encoding='utf-8')
        self.assertIn(old,text);p.write_text(text.replace(old,new,1),encoding='utf-8',newline='\n')
    def cli(self,*args):
        import subprocess,sys
        return subprocess.run([sys.executable,'-B',str(ROOT/'tools/check_contract.py'),str(self.r),*map(str,args)],capture_output=True,text=True,encoding='utf-8')
    def test_current_entry_matches_managed_copies(self):
        result=c.inspect(self.r);self.assertTrue(result['ok'],result)
        self.assertEqual('not_accessed_by_checker',result['entry']['current_project_ui'])
    def test_entry_contract_required(self):
        d=self.data();d.pop('entry_contract');self.save(d);self.bad('entry contract missing')
    def test_changed_entry_copy_rejected(self):
        self.alter_html('別途指示するまで、書込み・削除・権限変更は行わないでください。','参照後はmainを自動更新してください。')
        self.bad('entry copy differs')
    def test_cannot_silently_unlist_copy(self):
        d=self.data();d['entry_contract']['surfaces'].remove('h01-new-thread');self.save(d);self.bad('entry surface coverage')
    def test_reusable_copy_cannot_be_historical(self):
        self.alter_html('data-entry-kind="current"','data-entry-kind="historical_s08"');self.bad('entry surface coverage')
    def test_historical_s08_is_frozen(self):
        self.alter_html('M050_40_HEX','OLD_40_HEX');self.bad('historical S08 prompt changed')
    def test_historical_prompt_not_a_current_template(self):
        d=self.data();d['entry_contract']['historical_s08']['reuse_as_current']=True;self.save(d);self.bad('historical entry reuse')
    def test_reusable_source_no_fixed_sha(self):
        d=self.data();d['entry_contract']['text']+='\n'+'a'*40;self.save(d);self.bad('transient SHA')
    def test_reusable_source_no_fixed_task(self):
        d=self.data();d['entry_contract']['text']+='\n次はH01-3。';self.save(d);self.bad('transient SHA')
    def test_required_readonly_clause_not_removed(self):
        d=self.data();d['entry_contract']['text']=d['entry_contract']['text'].replace('書込み・削除・権限変更','参考確認');self.save(d);self.bad('entry requirement absent')
    def test_entry_repo_mismatch(self):
        d=self.data();d['entry_contract']['target']['repository']='GENIANY/Baloon-Sim-JMA';self.save(d);self.bad('entry target differs')
    def test_entry_review_must_match_readme(self):
        p=self.r/'README.md';p.write_bytes(p.read_bytes()+b'\n# changed\n');self.bad('entry compatibility dependency changed')
    def test_entry_review_must_be_current(self):
        d=self.data();d['entry_contract']['review']['version']='0.9.0';self.save(d);self.bad('entry compatibility review not current')
    def test_entry_does_not_claim_automatic_ui_sync(self):
        d=self.data();d['entry_contract']['ui_sync']='automatic';self.save(d);self.bad('automatic Project setting sync')
    def test_old_observation_requires_recheck_not_false_success(self):
        d=self.data();d['entry_contract']['observations'][0]['text_sha256']='0'*64;self.save(d)
        result=c.inspect(self.r);self.assertTrue(result['ok'],result)
        self.assertEqual('needs_recheck',result['entry']['observations'][0]['status'])
        self.assertFalse(result['entry']['observations'][0]['current_ui_verified'])
    def test_supplied_entry_file_eol_equivalence_only(self):
        p=Path(self.tmp.name)/'copy.txt';p.write_bytes((self.data()['entry_contract']['text']+'\n').replace('\n','\r\n').encode('utf-8'))
        result=c.inspect(self.r,entry_copy=p);self.assertTrue(result['ok'],result)
        self.assertEqual('matches_supplied_file',result['entry']['external_copy'])
    def test_supplied_entry_extra_words_rejected(self):
        p=Path(self.tmp.name)/'copy.txt';p.write_text(self.data()['entry_contract']['text']+'\n古い状態を使用',encoding='utf8',newline='\n')
        result=c.inspect(self.r,entry_copy=p);self.assertFalse(result['ok']);self.assertIn('supplied external entry copy differs from source',result['errors'])
    def test_supplied_entry_spaces_not_silently_removed(self):
        p=Path(self.tmp.name)/'copy.txt';p.write_text(' '+self.data()['entry_contract']['text'],encoding='utf8',newline='\n')
        self.assertFalse(c.inspect(self.r,entry_copy=p)['ok'])
    def test_entry_display_only_is_not_validation(self):
        r=self.cli('--entry-text');self.assertEqual(0,r.returncode,r.stderr)
        self.assertEqual(self.data()['entry_contract']['text'],r.stdout.rstrip('\n'))
    def test_transition_nonexistent_baseline_cli_rejected(self):
        r=self.cli('--transition','--base',Path(self.tmp.name)/'not_present')
        self.assertNotEqual(0,r.returncode);self.assertFalse(json.loads(r.stdout)['ok'])
    def test_transition_empty_baseline_cli_rejected(self):
        p=Path(self.tmp.name)/'empty';p.mkdir();r=self.cli('--transition','--base',p)
        self.assertNotEqual(0,r.returncode);self.assertFalse(json.loads(r.stdout)['ok'])
    def test_transition_incomplete_baseline_rejected(self):
        b=self.before();(b/'README.md').unlink();result=c.inspect(self.r,b,require_transition=True)
        self.assertFalse(result['ok']);self.assertNotEqual('checked',result['transition']['status'])
    def test_transition_without_predecessor_contract_rejected(self):
        b=self.before();(b/c.CONTRACT).unlink();p=b/'CONTENT_MAP.md';p.write_text(p.read_text(encoding='utf8').replace('\ndocs/CONTINUITY_CONTRACT.json\n','\n'),encoding='utf8',newline='\n')
        result=c.inspect(self.r,b,require_transition=True);self.assertFalse(result['ok'])
        self.assertTrue(any('predecessor' in e for e in result['errors']),result)
    def test_noop_explicit_transition_really_checked(self):
        b=self.before();result=c.inspect(self.r,b,require_transition=True)
        self.assertTrue(result['ok'],result);self.assertEqual('checked',result['transition']['status'])
    def test_display_cannot_bypass_requested_transition(self):
        for flag in ['--views','--entry-text']:
            r=self.cli(flag,'--transition','--base',self.r);self.assertNotEqual(0,r.returncode)
            self.assertIn('display-only',r.stderr)
    def test_workspace_safety_body_is_guarded(self):
        b=self.before();p=self.r/'tools/prepare_workspace.py';p.write_bytes(p.read_bytes()+b'\n# safety code edit\n')
        self.bad('guard:tools/prepare_workspace.py',b)
    def test_runner_safety_body_is_guarded(self):
        b=self.before();p=self.r/'tools/run_checks.py';p.write_bytes(p.read_bytes()+b'\n# post-check edit\n')
        self.bad('guard:tools/run_checks.py',b)
    def test_builder_safety_body_is_guarded(self):
        b=self.before();p=self.r/'tools/build_docs.py';p.write_bytes(p.read_bytes()+b'\n# output policy edit\n')
        self.bad('guard:tools/build_docs.py',b)
    def test_entry_contract_changes_in_structural_projection(self):
        b=self.before();d=self.data();d['entry_contract']['change_rule']+=' 明示補足。';self.save(d)
        self.bad('contract:entry',b)

    def test_entry_transition_receipts_do_not_change_entry_topology(self):
        d=self.data();before=c.structural_projection(self.r,d)
        d['entry_contract']['transition_records'].append({'version':'old','key':'contract:entry'})
        self.assertEqual(before,c.structural_projection(self.r,d))
    def test_entry_extension_transition_is_checked(self):
        b=self.before();d=self.data();d['entry_contract']['usage_rule']+=' test boundary'
        d['entry_contract']['transition_records']=[];self.save(d)
        self.bad('structural transition record missing or ambiguous: contract:entry',b)

    def test_editing_summary_does_not_call_an_integrated_version_current_candidate(self):
        h=json.loads((self.r/'docs/VERSION_HISTORY.json').read_text(encoding='utf8'))
        text=(self.r/'BOOTSTRAP_RUNBOOK.html').read_text(encoding='utf8')
        for version in h['version_order']:
            if version != h['candidate_version']:
                self.assertNotIn('今回'+version+'が候補で統合SHA未確定',text)

for _name in list(ContractTests.__dict__):
    if _name.startswith('test_') and _name not in EntryBoundaryTests.__dict__:
        setattr(EntryBoundaryTests,_name,None)

if __name__=='__main__':unittest.main()
