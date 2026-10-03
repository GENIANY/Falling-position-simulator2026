#!/usr/bin/env python3
"""Inspect purpose/lifecycle/narrative contracts; stdlib, Python >=3.10.

Read only. No Git/network, approvals, fingerprint refresh, deletion, or source edits.
--base compares meaningful narrative units and requires matching change+rationale
records. --views prints derived inventory for CONTENT_MAP, never writes it.
Nonempty fields/consistent hashes do NOT prove reasoning quality or true reports.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys
from html.parser import HTMLParser

CONTRACT = 'docs/CONTINUITY_CONTRACT.json'
THREAD_ONLY = re.compile(r'(?:この|前の|過去の|上の)(?:スレッド|会話).*(?:参照|見て)|(?:see|refer to) (?:the )?(?:previous|earlier) (?:chat|conversation)', re.I)
TEXT_FIELDS = ('purpose','current_role','retire_when','origin')
NODE_FIELDS = ('question','premises','argument','result','contribution','order_reason')


def load(root: Path) -> dict:
    return json.loads((root/CONTRACT).read_text(encoding='utf-8'))


def safe(root: Path, name: str) -> Path:
    p = PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name:
        raise ValueError('unsafe contract path: '+name)
    out = (root/name).resolve()
    if not out.is_relative_to(root.resolve()):
        raise ValueError('out-of-tree contract path: '+name)
    return out


def paths(root: Path) -> set[str]:
    text = (root/'CONTENT_MAP.md').read_text(encoding='utf-8')
    m = re.search(r'<!-- CURRENT_PATHS_BEGIN -->\s*```text\s*\n(.*?)\n```\s*<!-- CURRENT_PATHS_END -->',text,re.S)
    if not m: raise ValueError('no current-path inventory')
    return set(m[1].splitlines())


def body(root: Path, node: dict) -> str:
    text = safe(root,node['path']).read_text(encoding='utf-8')
    start,end = node['start'],node['end']
    if text.count(start)!=1 or text.count(end)!=1:
        raise ValueError('narrative boundary missing or duplicated: '+node['id'])
    a,b = text.index(start)+len(start),text.index(end)
    if b<=a: raise ValueError('narrative boundary reversed: '+node['id'])
    return text[a:b]


def digest(root: Path, node: dict) -> str:
    raw=body(root,node)
    # Ignore time stamps only, not rationale, wording, ordering, or arguments.
    raw=re.sub(r'\[(?:更新|確認):[^\]]+\]', '', raw)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def asset_view(data: dict) -> str:
    lines=['| 実体 | 現在の位置づけ・目的 | 使用先 | 退役を検討できる条件 |',
           '|---|---|---|---|']
    def cell(s):return str(s).replace('|','／').replace('\n',' ')
    for a in sorted(data['assets'],key=lambda x:x['path']):
        lines.append('| `'+a['path']+'` | '+cell(a['lifecycle']+'：'+a['purpose']+'。'+a['current_role'])+' | '+cell('、'.join(a['needed_by']))+' | '+cell(a['retire_when'])+' |')
    return '\n'.join(lines)


def acyclic(graph: dict[str,list[str]], kind: str) -> None:
    done=set();stack=set()
    def visit(n):
        if n in stack:raise ValueError(kind+' cycle: '+n)
        if n in done:return
        stack.add(n)
        for v in graph[n]:
            if v not in graph:raise ValueError(kind+' target missing: '+v)
            visit(v)
        stack.remove(n);done.add(n)
    for n in graph:visit(n)


def canonical_digest(value) -> str:
    """Stable JSON comparison, independent of object-key order."""
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,
                                     separators=(',',':')).encode('utf-8')).hexdigest()


def snapshot_digest(root: Path) -> str:
    """Bind comparison to the complete declared path/byte set, not a folder name.

    This is NOT a commit authenticator. Obtain the commit/tree through Git first.
    Unknown files are rejected by check_state; this digest covers declared files.
    """
    return canonical_digest({n:hashlib.sha256(safe(root,n).read_bytes()).hexdigest()
                             for n in sorted(paths(root))})


def local_digest(root: Path, node: dict, nodes: list[dict]) -> str:
    """Fingerprint a node's own argument plus ordered direct-child identities.

    A leaf wording edit does not pretend that each ancestor's own text changed.
    Ancestors still require an impact review, reported separately by inspect().
    """
    raw=body(root,node);cuts=[]
    for child in nodes:
        if child.get('parent')!=node['id']:continue
        a=raw.find(child['start']);b=raw.find(child['end'])
        if a<0 or b<a:raise ValueError('local child boundary missing: '+child['id'])
        cuts.append((a,b+len(child['end']),child['id']))
    cuts.sort()
    if any(cuts[i][1]>cuts[i+1][0] for i in range(len(cuts)-1)):
        raise ValueError('narrative siblings overlap: '+node['id'])
    for a,b,uid in reversed(cuts):raw=raw[:a]+'[[CHILD:'+uid+']]'+raw[b:]
    raw=re.sub(r'\[(?:更新|確認):[^\]]+\]','',raw)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


# These guards are deliberately owned by THIS (possibly previous-version)
# checker, not by the candidate. Removing a candidate's guard list cannot hide it.
GUARD_PATHS=('tools/check_state.py','tools/check_health.py','tools/check_contract.py',
             'tests/test_state.py','tests/test_health.py','tests/test_contract.py',
             'tests/test_workspace.py','tests/test_check_run.py',
             'tools/prepare_workspace.py','tools/run_checks.py','tools/build_docs.py')


# Entry copies are data projections, not independently edited instructions.
ENTRY_LOCATIONS = {'copy-recovery': 'current', 'h01-new-thread': 'current',
                   'copy-new-thread': 'historical_s08'}
ENTRY_REQUIRED = ('現在コミットを確認', 'そのコミットに固定', 'ルートの README.md',
                  '復旧・作業開始手順', '取得したファイルを根拠',
                  '現在状態、未確認事項、次の作業', '会話の記憶だけで補完せず',
                  '取得できない範囲を明示',
                  '別途指示するまで、書込み・削除・権限変更は行わないでください。')


def entry_normalize(text: str) -> str:
    """Only transport EOL / final line terminators may differ; spaces matter."""
    return text.replace('\r\n', '\n').rstrip('\n')


def entry_sha(text: str) -> str:
    return hashlib.sha256(entry_normalize(text).encode('utf-8')).hexdigest()


class EntryBlocks(HTMLParser):
    """Read visible <pre> text and disposition; no HTML execution or writes."""
    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.blocks = {}; self.active = None; self.parts = []; self.attrs = {}
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'pre':
            if self.active is not None: raise ValueError('nested entry pre')
            self.active = a.get('id', ''); self.parts = []; self.attrs = a
    def handle_data(self, data):
        if self.active is not None: self.parts.append(data)
    def handle_endtag(self, tag):
        if tag == 'pre' and self.active is not None:
            if self.active in self.blocks: raise ValueError('duplicate entry block: '+self.active)
            self.blocks[self.active] = (''.join(self.parts), self.attrs)
            self.active = None


def entry_checks(root: Path, d: dict, check, external_copy: Path|None = None) -> dict:
    """Check source/copies/README compatibility, never claim current UI access."""
    entry = d.get('entry_contract')
    check(isinstance(entry, dict), 'entry contract missing')
    if not isinstance(entry, dict): return {'status': 'missing'}
    text = entry.get('text', '')
    check(isinstance(text, str) and bool(text), 'entry text missing')
    if not isinstance(text, str): return {'status': 'invalid'}
    history = json.loads((root/'docs/VERSION_HISTORY.json').read_text(encoding='utf-8'))
    target = entry.get('target', {})
    check(target == {'repository': history['repository'], 'branch': history['branch'],
                     'readme': 'README.md'}, 'entry target differs from repository identity')
    check(target.get('repository', 'NO-TARGET') in text and
          (' の '+str(target.get('branch'))+' の現在コミット') in text,
          'entry text target mismatch')
    for phrase in ENTRY_REQUIRED:
        check(phrase in text, 'entry requirement absent: '+phrase)
    check(not re.search(r'[0-9a-f]{40}|(?<![A-Za-z0-9_])(?:S|U|H|F|E|A)\d{2}(?:-\d+)?(?![A-Za-z0-9_])|\b0\.\d+\.\d+\b', text),
          'reusable entry contains a transient SHA/version/task')
    check(entry.get('text_sha256') == entry_sha(text), 'entry source fingerprint mismatch')
    check(entry.get('text_revision') and entry.get('id') == 'ENTRY-01', 'entry identity missing')
    blocks = EntryBlocks((root/'BOOTSTRAP_RUNBOOK.html').read_text(encoding='utf-8')).blocks
    declared = entry.get('surfaces', [])
    actual = {key:a.get('data-entry-kind') for key,(_,a) in blocks.items() if a.get('data-entry-id')}
    check(actual == ENTRY_LOCATIONS and declared == sorted(ENTRY_LOCATIONS), 'entry surface coverage mismatch')
    for key,kind in ENTRY_LOCATIONS.items():
        check(key in blocks, 'entry copy missing: '+key)
        if key not in blocks: continue
        value,attrs = blocks[key]
        check(attrs.get('data-entry-id') == 'ENTRY-01' and attrs.get('data-entry-kind') == kind,
              'entry classification missing: '+key)
        if kind == 'current':
            check(entry_normalize(value) == entry_normalize(text), 'entry copy differs from source: '+key)
        else:
            historical = entry.get('historical_s08', {})
            check(entry_sha(value) == historical.get('sha256'), 'historical S08 prompt changed')
            check(bool(historical.get('purpose')) and historical.get('reuse_as_current') is False,
                  'historical entry reuse boundary missing')
    readme = (root/'README.md').read_text(encoding='utf-8')
    for heading in ('## R0：','## R1：','## R2：','## R3：','## R4：','## R5：'):
        check(readme.count(heading) == 1, 'entry README procedure boundary missing: '+heading)
    marker = re.search(r'<!-- ENTRY-CONTRACT:BEGIN -->\n(.*?)\n<!-- ENTRY-CONTRACT:END -->',readme,re.S)
    check(marker is not None, 'README entry contract missing')
    if marker:
        for term in ('ENTRY-01', 'docs/CONTINUITY_CONTRACT.json', '不一致', '停止', '設定画面'):
            check(term in marker[1], 'README entry compatibility requirement absent: '+term)
    review = entry.get('review', {})
    check(review.get('version') == history['candidate_version'], 'entry compatibility review not current')
    check(review.get('source_sha256') == entry_sha(text), 'entry review source differs')
    for name in ('README.md','AGENTS.md'):
        check(review.get('dependencies',{}).get(name) == hashlib.sha256((root/name).read_bytes()).hexdigest(),
              'entry compatibility dependency changed: '+name)
    evidence = json.loads((root/'docs/CONTENT_HEALTH.json').read_text(encoding='utf-8')).get('evidence',{})
    check(review.get('evidence_id') in evidence, 'entry review evidence missing')
    check(entry.get('ui_sync') == 'manual_readback_required_when_unobserved_or_changed',
          'entry cannot claim automatic Project setting sync')
    observed = []
    for item in entry.get('observations',[]):
        check(item.get('method') in ('visible_project_context','user_ui_readback'), 'unknown entry observation method')
        check(all(item.get(k) for k in ('evidence','observed_on','text_sha256','limits')), 'entry observation incomplete')
        observed.append({'id':item.get('id'), 'method':item.get('method'),
                         'status':'recorded_match' if item.get('text_sha256') == entry_sha(text) else 'needs_recheck',
                         'current_ui_verified':False})
    copy_result = 'not_provided'
    if external_copy is not None:
        supplied = external_copy.read_text(encoding='utf-8-sig')
        match = entry_normalize(supplied) == entry_normalize(text)
        check(match, 'supplied external entry copy differs from source')
        copy_result = 'matches_supplied_file' if match else 'mismatch'
    return {'status':'checked', 'id':'ENTRY-01', 'text_sha256':entry_sha(text),
            'external_copy':copy_result, 'observations':observed,
            'current_project_ui':'not_accessed_by_checker',
            'required_at_use':'Compare the actually visible instruction; if not visible, obtain user readback. A stored receipt is not a live UI query.'}


def structural_projection(root: Path, data: dict|None=None) -> dict:
    """Compare identities/relations/rules, not transient progress or review stamps."""
    d=load(root) if data is None else data
    h=json.loads((root/'docs/CONTENT_HEALTH.json').read_text(encoding='utf-8'))
    out={}
    def add(key,value):
        if key in out:raise ValueError('duplicate structural identity: '+key)
        out[key]=value
    for a in d['assets']:add('asset:'+a['path'],a)
    for n in d['narrative_units']:add('node:'+n['id'],n)
    for v in d['document_designs']:add('design:'+v['path'],v)
    for v in d['external_artifacts']:add('external:'+v['id'],v)
    for u in h['units']:
        add('scope:'+u['id'],{k:u[k] for k in ('path','parent','depends_on','selector',
                        'text_range','binary','role','control_mode','inline_marker','initial_review_due','purpose') if k in u})
    for k in ('policy','recovery_contract','procedure_contract'):add('health:'+k,h[k])
    hand=d['handoff']
    add('handoff:contract',{k:v for k,v in hand.items()
                           if k not in ('status','readback_evidence','accepted_residuals')})
    for key in ('scope','time_basis','initial_inventory'):add('contract:'+key,d.get(key))
    with (root/'docs/BACKLOG.csv').open(encoding='utf-8-sig',newline='') as stream:
        for row in csv.DictReader(stream):
            add('task:'+row['id'],{k:row[k] for k in ('phase','title','depends_on','acceptance_criteria')})
    add('schema:continuity',d['schema_version'])
    add('policy:stability',d.get('stability_policy'))
    entry=d.get('entry_contract')
    add('contract:entry', {k:v for k,v in entry.items() if k not in ('review','observations','transition_records')} if entry else None)
    for name in GUARD_PATHS:
        p=safe(root,name)
        add('guard:'+name,hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None)
    return out


def compare_structure(root: Path, base: Path, current: dict, previous: dict,
                      check) -> dict:
    """Fail closed on undeclared transitions, including changes to the guards.

    The signed/approved human decision is outside this offline check. Records
    with valid hashes demonstrate correspondence, NOT truth or authorization.
    """
    old=structural_projection(base,previous);new=structural_projection(root,current)
    changed=sorted(k for k in set(old)|set(new) if old.get(k)!=new.get(k))
    snapshot=snapshot_digest(base)
    check(current.get('comparison_base_sha256')==snapshot,
          'comparison baseline bytes not bound to candidate')
    check(current['schema_version']==previous['schema_version'],
          'schema change needs a separately reviewed migration; not an ordinary transition')
    # New entry records stay with their extension. Previous checkers can still
    # validate their known structural domain; only this checker validates ENTRY.
    records=current.get('structural_changes',[]) + current.get('entry_contract',{}).get('transition_records',[])
    for key in changed:
        matches=[r for r in records if r.get('key')==key and r.get('version')==current['version']
                 and r.get('comparison_basis')==current['basis_commit']
                 and r.get('base_snapshot_sha256')==snapshot]
        check(len(matches)==1,'structural transition record missing or ambiguous: '+key)
        if len(matches)!=1:continue
        event=matches[0]
        check(event.get('before_sha256')==canonical_digest(old.get(key)),
              'structural before evidence mismatch: '+key)
        check(event.get('after_sha256')==canonical_digest(new.get(key)),
              'structural after evidence mismatch: '+key)
        for field in ('reason','preserved','impact','recovery'):
            text=event.get(field)
            check(isinstance(text,str) and bool(text.strip()) and not THREAD_ONLY.search(text),
                  'structural transition rationale incomplete: '+key+':'+field)
        check(event.get('kind') in ('compatible','migration','guard'),
              'unknown transition class: '+key)
        if key.startswith('guard:'):
            check(event.get('kind')=='guard','guard change must be explicit: '+key)
        if key not in old or key not in new:
            check(event.get('kind') in ('migration','guard') and bool(event.get('replacement')),
                  'added/removed identity needs explicit disposition: '+key)
    # Do not recycle stale removals or include fabricated transition rows.
    active=[r for r in records if r.get('version')==current['version']
            and r.get('base_snapshot_sha256')==snapshot]
    check(all(r.get('key') in changed for r in active),'structural record has no corresponding transition')
    old_nodes={n['id'] for n in previous['narrative_units']}
    new_nodes={n['id'] for n in current['narrative_units']}
    return {'status':'checked','base_snapshot_sha256':snapshot,'changes':changed,
            'preserved_asset_paths':len(set(paths(base))&paths(root)),
            'added_paths':sorted(paths(root)-paths(base)),
            'removed_paths':sorted(paths(base)-paths(root)),
            'preserved_narrative_ids':len(old_nodes&new_nodes),
            'added_narrative_ids':sorted(new_nodes-old_nodes),
            'removed_narrative_ids':sorted(old_nodes-new_nodes)}


def inspect(root: Path, base: Path|None=None, *, require_transition: bool=False,
            entry_copy: Path|None=None) -> dict:
    root=root.resolve();errors=[];checks=0;warnings=[];deltas=[]; impact=[]
    transition={"status":"not_run_without_base"}; entry_result={"status":"not_run"}
    def ck(ok,message):
        nonlocal checks
        checks+=1
        if not ok:errors.append(message)
    try:
        d=load(root); names=paths(root);assets=d['assets'];by_path={a['path']:a for a in assets}
        if require_transition and base is None: raise ValueError('transition requires a complete base')
        entry_result=entry_checks(root,d,ck,entry_copy)
        ck(d['schema_version']==1,'unsupported continuity schema')
        ck(bool(re.fullmatch(r'[0-9a-f]{40}',d.get('basis_commit',''))),'continuity basis must be a full SHA')
        ck(len(by_path)==len(assets),'duplicate asset path')
        ck(set(by_path)==names,'asset coverage differs from current paths')
        for a in assets:
            ck(safe(root,a['path']).is_file(),'asset missing: '+a['path'])
            for f in TEXT_FIELDS:
                value=a.get(f,'')
                ck(isinstance(value,str) and bool(value.strip()),'asset field missing: '+a['path']+':'+f)
                ck(not THREAD_ONLY.search(value),'thread-only asset purpose: '+a['path']+':'+f)
            ck(a.get('lifecycle') in {'active','conditional','reference','generated'},'unknown lifecycle: '+a['path'])
            ck(bool(a.get('needed_by')),'asset consumer missing: '+a['path'])
            for consumer in a.get('needed_by',[]):
                ck(consumer.startswith('role:') or consumer.split('#')[0] in names,'unknown consumer: '+consumer)
            for src in a.get('source_paths',[]):ck(src in names and src!=a['path'],'invalid derivation source: '+src)
            if a['lifecycle']=='generated':ck(bool(a.get('source_paths')),'generated asset lacks source: '+a['path'])
        acyclic({a['path']:a.get('source_paths',[]) for a in assets},'derivation')
        reg=json.loads((root/'docs/CONTENT_HEALTH.json').read_text(encoding='utf-8'))
        ck(d.get('version')==reg['files'][CONTRACT]['document_version'],
           'continuity document version differs from registry')
        ck(set(reg['files'])==names,'health file coverage differs from current paths')
        for unit in reg['units']:
            ck(not THREAD_ONLY.search(unit.get('purpose','')),'thread-only review purpose: '+unit['id'])
        for a in d['external_artifacts']:
            for f in ('pattern','purpose','producer','retention','reproduction','if_unavailable'):
                ck(bool(a.get(f)),'external-artifact rule incomplete: '+str(a.get('id'))+':'+f)
        with (root/'docs/BACKLOG.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
        acyclic({r['id']:list(filter(None,r['depends_on'].split(';'))) for r in rows},'task')
        nodes=d['narrative_units'];index={n['id']:n for n in nodes}
        ck(len(index)==len(nodes),'duplicate narrative ID')
        acyclic({n['id']:[n['parent']] if n.get('parent') else [] for n in nodes},'narrative parent')
        for n in nodes:
            for f in NODE_FIELDS:
                ck(bool(n.get(f,'').strip()),'narrative field missing: '+n['id']+':'+f)
                ck(not THREAD_ONLY.search(n.get(f,'')),'thread-only narrative rationale: '+n['id'])
            raw=body(root,n)
            ck(bool(raw.strip()),'empty narrative body: '+n['id'])
            if n.get('parent'):
                parent=index[n['parent']]
                ck(n['path']==parent['path'] and n['start'] in body(root,parent) and n['end'] in body(root,parent),
                   'narrative child outside parent: '+n['id'])
            ck(n.get('status') in {'reviewed_structure','inventory_only'},'narrative review level missing: '+n['id'])
            for ref in n.get('feeds',[]):ck(ref in index,'narrative result target missing: '+ref)
        text=(root/'CONTENT_MAP.md').read_text(encoding='utf-8')
        m=re.search(r'<!-- ASSET_VIEW_BEGIN -->\n(.*?)\n<!-- ASSET_VIEW_END -->',text,re.S)
        ck(bool(m) and m[1]==asset_view(d),'derived asset view stale or missing')
        for doc in d['document_designs']:
            ck(doc['path'] in names,'document design target missing')
            ck(bool(doc.get('thesis')) and bool(doc.get('ordering_reason')) and bool(doc.get('coverage')),'document design incomplete: '+doc['path'])
            for n in doc['unit_ids']:ck(n in index,'document design unit missing: '+n)
        hand=d['handoff']
        ck(hand['status'] in {'pending_integration','integrated_pending_readback','ready'},'invalid handoff status')
        ck(len(hand['questions'])>=5 and bool(hand['stop_conditions']),'handoff challenge missing')
        # Do not convert labels into true approval: ready requires observed evidence.
        if hand['status']=='ready':
            ck(bool(hand.get('readback_evidence')) and bool(hand.get('accepted_residuals')),'ready handoff lacks evidence')
        if base:
            base=base.resolve(strict=True)
            if not base.is_dir(): raise ValueError('comparison base is not a directory')
            snapshot_digest(base)  # Reject empty/incomplete baseline before any bootstrap exception.
            if require_transition and not (base/CONTRACT).is_file():
                raise ValueError('transition requires a predecessor continuity contract')
            old=load(base) if (base/CONTRACT).is_file() else None
            events=d.get('changes',[]);oldnodes={n['id']:n for n in old['narrative_units']} if old else {}
            if not old:
                init=d.get('initial_inventory',{})
                ck(bool(init.get('basis_commit')) and bool(init.get('method')),'initial inventory lacks basis')
                warnings.append('initial inventory: no predecessor narrative registry; coverage is an explicit baseline, not a fabricated history')
            else:
                transition=compare_structure(root,base,d,old,ck)
                for uid,n in index.items():
                    previous=oldnodes.get(uid)
                    if previous is None or local_digest(base,previous,old['narrative_units'])!=local_digest(root,n,nodes) or previous!=n:
                        deltas.append(uid)
                        candidates=[e for e in events if uid in e.get('units',[]) and e.get('version')==d['version']]
                        ck(bool(candidates),'narrative changed without reason record: '+uid)
                        if candidates:
                            e=candidates[-1]
                            ck(bool(e.get('reason')) and bool(e.get('preserved')),'change rationale incomplete: '+uid)
                            expected=digest(base,previous) if previous else 'new'
                            ck(e.get('before_digests',{}).get(uid)==expected,'prior comparison evidence missing: '+uid)
                            ck(e.get('after_digests',{}).get(uid)==digest(root,n),'change target digest mismatch: '+uid)
                removed=set(oldnodes)-set(index)
                for uid in removed:
                    ck(any(uid in e.get('removed_units',[]) and e.get('reason') and e.get('replacement') for e in events if e.get('version')==d['version']),'removed narrative lacks disposition: '+uid)
                oldassets={a['path']:a for a in old['assets']}
                for path,asset in by_path.items():
                    if oldassets.get(path)!=asset:
                        uid='asset:'+path;deltas.append(uid)
                        matches=[e for e in events if uid in e.get('units',[]) and e.get('version')==d['version']]
                        ck(bool(matches) and bool(matches[-1].get('reason')) and bool(matches[-1].get('preserved')),
                           'asset contract changed without reason: '+path)
                for path in set(a['path'] for a in old['assets'])-set(by_path):
                    ck(any(path in e.get('removed_assets',[]) and e.get('reason') and e.get('replacement') for e in events if e.get('version')==d['version']),'removed asset lacks disposition: '+path)
        else:warnings.append('before-state semantic comparison not run (--base omitted)')
        if require_transition: ck(transition['status']=='checked','requested transition was not executed')
        # Revalidation impact is not an assertion of ancestor content edits.
        affected=set()
        for uid in deltas:
            n=index.get(uid)
            while n and n.get('parent'):
                parent=n['parent'];affected.add(parent);n=index.get(parent)
        impact=sorted(affected-set(deltas))
    except (OSError,ValueError,KeyError,TypeError,RecursionError) as e:
        errors.append(type(e).__name__+': '+str(e))
    return {'ok':not errors,'checks':checks,'errors':errors,'warnings':warnings,'changed_narrative_units':deltas,'ancestor_impact_review':impact,
            'transition':transition,'entry':entry_result,
            'limits':['Structural coverage only; semantic reasoning and truth require review.',
                      'No GitHub or user-PC access; no deletion or automatic approval.',
                      'Examples of thread-only references are rejected; this is not natural-language completeness detection.']}


def main() -> int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root',nargs='?',type=Path,default=Path('.'))
    p.add_argument('--base',type=Path);p.add_argument('--views',action='store_true')
    p.add_argument('--transition',action='store_true',help='require a pinned before-state comparison')
    p.add_argument('--entry-copy',type=Path,help='Compare a supplied external plain-text entry, read only; not a UI read')
    p.add_argument('--entry-text',action='store_true',help='Print the current shared entry source only')
    a=p.parse_args()
    if (a.views or a.entry_text) and (a.transition or a.base or a.entry_copy):
        p.error('display-only options cannot claim verification or transition')
    if a.transition and a.base is None:p.error('--transition requires --base; current-state checks are not a transition check')
    if a.views:print(asset_view(load(a.root)));return 0
    if a.entry_text:print(load(a.root)['entry_contract']['text']);return 0
    r=inspect(a.root,a.base,require_transition=a.transition,entry_copy=a.entry_copy);print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r['ok'] else 1

if __name__=='__main__':sys.exit(main())
