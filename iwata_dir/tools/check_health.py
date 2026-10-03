#!/usr/bin/env python3
"""Readonly, stdlib-only scope/version/review contract checker (Python >= 3.10).

Does not connect to GitHub, certify semantic truth, or mark anything reviewed.
--base compares the before-state directory; omission is explicitly reported.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath

VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
MARK = re.compile(r'\[(更新|確認):([^\]\s]+)\]')
SHA = re.compile(r'[0-9a-f]{40}\Z')

class Spans(HTMLParser):
    """Exact source spans for IDs; no rendering or HTML normalization."""
    def __init__(self, text: str):
        super().__init__(convert_charrefs=False)
        self.text=text; self.offsets=[0]; self.stack=[]; self.spans={}
        for m in re.finditer('\n',text): self.offsets.append(m.end())
        self.feed(text); self.close()
    def position_offset(self):
        line,col=self.getpos(); return self.offsets[line-1]+col
    def handle_starttag(self,tag,attrs):
        a=dict(attrs); start=self.position_offset(); ident=a.get('id')
        if tag in VOID:
            if ident:self.spans[ident]=(start,start+len(self.get_starttag_text()))
        else:self.stack.append((tag,ident,start))
    def handle_startendtag(self,tag,attrs):
        ident=dict(attrs).get('id'); start=self.position_offset()
        if ident:self.spans[ident]=(start,start+len(self.get_starttag_text()))
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:
                end=self.text.find('>',self.position_offset())+1
                for _,ident,start in self.stack[i:]:
                    if ident:
                        if ident in self.spans: raise ValueError('duplicate HTML scope id: '+ident)
                        self.spans[ident]=(start,end)
                del self.stack[i:];break

def normalize(text: str) -> str:
    text=re.sub(r'<p\b[^>]*class="revstamp"[^>]*>.*?</p>', '',text,flags=re.S)
    text=re.sub(r'\s+data-(?:updated|reviewed)="[^"]*"','',text)
    return MARK.sub('',text)

def h(data: bytes) -> str:return hashlib.sha256(data).hexdigest()

class Contents:
    def __init__(self,root: Path,units: list[dict]):
        self.root=root.resolve();self.units={u['id']:u for u in units};self.cache={};self.span_cache={}
    def blob(self,path):
        if path not in self.cache:
            p=(self.root/path).resolve()
            if not p.is_relative_to(self.root):raise ValueError('unsafe scope path: '+path)
            self.cache[path]=p.read_bytes()
        return self.cache[path]
    def bounds(self,u):
        data=self.blob(u['path'])
        if u.get('selector') and u.get('text_range'):
            raise ValueError('two scope selectors: '+u['id'])
        if u.get('text_range'):
            text=data.decode('utf-8');bounds=u['text_range']
            start=bounds.get('start');end=bounds.get('end')
            if not isinstance(start,str) or not start or not isinstance(end,str) or not end:
                raise ValueError('invalid text range: '+u['id'])
            if text.count(start)!=1 or text.count(end)!=1:
                raise ValueError('text range must have unique boundaries: '+u['id'])
            a=text.index(start);b=text.index(end)
            if a>=b:raise ValueError('reversed text range: '+u['id'])
            return (a,b)
        if u.get('selector'):
            if u['path'] not in self.span_cache:self.span_cache[u['path']]=Spans(data.decode('utf-8')).spans
            span=self.span_cache[u['path']].get(u['selector'])
            if span is None:raise ValueError('scope selector missing: '+u['id'])
            return span
        return (0,len(data.decode('utf-8')))
    def text(self,u,own=True):
        data=self.blob(u['path'])
        if u.get('binary'):return None
        text=data.decode('utf-8');a,b=self.bounds(u);cuts=[]
        if own:
            for child in self.units.values():
                if child.get('parent')==u['id'] and child['path']==u['path']:
                    ca,cb=self.bounds(child)
                    if not a<=ca<cb<=b:raise ValueError('child outside parent: '+child['id'])
                    cuts.append((ca,cb,child['id']))
            cuts.sort()
            if any(cuts[i][1]>cuts[i+1][0] for i in range(len(cuts)-1)):
                raise ValueError('overlapping sibling scopes: '+u['id'])
        raw=text[a:b]
        for ca,cb,cid in reversed(cuts):raw=raw[:ca-a]+'[[UNIT:'+cid+']]'+raw[cb-a:]
        if u['path'].endswith('.html'):
            raw=re.sub(r'(\[\[UNIT:[^\]]+\]\])\s+(?=\[\[UNIT:)',r'\1',raw)
        return raw
    def digest(self,u,own=True):
        raw=self.text(u,own)
        return h(self.blob(u['path'])) if raw is None else h(normalize(raw).encode('utf-8'))
    def effective(self,u,field):
        visited=set()
        while u:
            if u['id'] in visited:raise ValueError('parent cycle: '+u['id'])
            visited.add(u['id'])
            if u.get(field) is not None:return u[field]
            pid=u.get('parent')
            if pid and pid not in self.units:raise ValueError('unknown parent: '+pid)
            u=self.units.get(pid)
        return None

def scan_index(reg: dict) -> list[list]:
    c=Contents(Path('.'),reg['units'])
    return [[u['id'],c.effective(u,'updated_in'),c.effective(u,'reviewed_in'),
             (u.get('review') or {}).get('on'),u.get('initial_review_due'),u.get('control_mode','document')]
            for u in reg['units']]


def comparison_registry(base: Path) -> dict:
    """Require a complete declared before-state; this does not authenticate Git."""
    base=base.resolve(strict=True)
    if not base.is_dir():raise ValueError('comparison base is not a directory')
    text=(base/'CONTENT_MAP.md').read_text(encoding='utf-8')
    block=re.search(r'<!-- CURRENT_PATHS_BEGIN -->\s*```text\s*\n(.*?)\n```\s*<!-- CURRENT_PATHS_END -->',text,re.S)
    if not block:raise ValueError('comparison base has no current-path inventory')
    names=[s.strip() for s in block[1].splitlines() if s.strip()]
    if len(names)!=len(set(names)):raise ValueError('comparison base has duplicate paths')
    required={'CONTENT_MAP.md','docs/CONTENT_HEALTH.json','docs/VERSION_HISTORY.json'}
    if not required.issubset(names):raise ValueError('comparison base lacks required metadata paths')
    for name in names:
        relative=PurePosixPath(name);path=(base/name).resolve()
        if (relative.is_absolute() or '..' in relative.parts or '\\' in name
                or not path.is_relative_to(base)):
            raise ValueError('unsafe comparison base path: '+name)
        if not path.is_file():raise ValueError('incomplete comparison base: missing '+name)
    reg=json.loads((base/'docs/CONTENT_HEALTH.json').read_text(encoding='utf-8'))
    if set(reg['files'])!=set(names):raise ValueError('comparison base file coverage differs from inventory')
    return reg


# Minimum recovery contract. These are release-reviewed invariants, not a
# claim that checking labels proves the quality of a recovery explanation.
RECOVERY_SCOPES = {'ENTRY','CTX','MAP','REFS','CONTROL','HISTORY',
                   'PLAN-POSITION','PLAN-ROLES','PLAN-ROADMAP',
                   'TASKS','UNKNOWNS','DECISIONS'}
RECOVERY_OUTCOMES = {'RC-IDENTITY','RC-GOALS','RC-HORIZON','RC-DEPENDENCIES',
                     'RC-DECISIONS','RC-STATE','RC-LIMITS','RC-NEXT'}
PROCEDURE_SCOPES = {'RB-U02-1','RB-U02-2','RB-U02-3',
                    *{'RB-S08-1'+s for s in 'abcdef'},
                    'RB-S09-1a','RB-S09-1b','RB-S09-1c','RB-S09-2','RB-S09-3'}
PROCEDURE_ROLES = {'precondition','actions','expected','stop','record'}
SHORTCUT = re.compile(r'(?:U\d+|S\d+)(?:[-–]\d+)?(?:と同じ|と同様|を参照して進め|を参照して実施)|(?:前回|以前|過去)(?:の手順)?(?:と同様|と同じ)|前と同様')

class ProcedureFields(HTMLParser):
    """Collect data-role fields without evaluating the HTML or JavaScript."""
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.fields={};self.stack=[];self.action_items=0
        self.feed(source);self.close()
    def handle_starttag(self,tag,attrs):
        role=dict(attrs).get('data-role')
        if role in PROCEDURE_ROLES:self.fields.setdefault(role,[]).append([])
        if tag=='li' and any(r=='actions' for _,r in self.stack):self.action_items+=1
        if tag not in VOID:self.stack.append((tag,role))
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.stack[i][0]==tag:del self.stack[i:];break
    def handle_data(self,data):
        for role in {r for _,r in self.stack if r in PROCEDURE_ROLES}:
            self.fields[role][-1].append(data)
    def texts(self,role):return [''.join(x).strip() for x in self.fields.get(role,[])]


class RecoveryAcceptance(HTMLParser):
    """Collect static acceptance and retention markers; never infer actual success."""
    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.completed=False;self.receipts=[];self.outcomes={};self.retention=[]
        self.feed(source);self.close()
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id')=='S08':self.completed=a.get('data-status')=='done'
        if a.get('id')=='S08-acceptance':self.receipts.append(a)
        if a.get('data-recovery-outcome'):
            self.outcomes.setdefault(a['data-recovery-outcome'],[]).append(a.get('data-acceptance'))
        if a.get('data-retention-rule'):self.retention.append(a['data-retention-rule'])


def inspect(root: Path,base: Path|None=None,as_of: str|None=None,extra: list[str]|None=None) -> dict:
    root=root.resolve(); errors=[]; checks=0; warnings=[];required=set();due={};changed=[];live_checks=[];version_age_advisories={}
    def ck(ok,msg):
        nonlocal checks
        checks+=1
        if not ok:errors.append(msg)
    try:
        today=dt.date.fromisoformat(as_of) if as_of else dt.datetime.now(dt.timezone.utc).date()
        reg=json.loads((root/'docs/CONTENT_HEALTH.json').read_text(encoding='utf-8'))
        hist=json.loads((root/'docs/VERSION_HISTORY.json').read_text(encoding='utf-8'))
        oldreg=comparison_registry(base) if base is not None else None
        units=reg['units']; ids=[u['id'] for u in units];c=Contents(root,units)
        current=hist['candidate_version'];order=hist['version_order'];versions={v['version']:v for v in hist['versions']}
        ck(len(order)==len(set(order)),'duplicate version order')
        ck(set(order)==set(versions),'version list and order differ')
        ck(current in order and current==order[-1],'current version not last in order')
        ck(len(ids)==len(set(ids)),'duplicate scope ID')
        ck(reg['document_version']==current,'registry version mismatch')
        ck(all(v.get('summary','').strip() for v in versions.values()),'version summary missing')
        transitions={x['sha']:x for x in hist['transitions']}
        ck(len(transitions)==len(hist['transitions']),'duplicate git transition')
        for v in versions.values():
            canonical=v.get('integrated_commit')
            ck(canonical is None or bool(SHA.fullmatch(canonical)),'invalid integrated SHA: '+v['version'])
            if v['kind']=='integrated':ck(canonical in transitions,'integrated version missing transition: '+v['version'])
            if v['kind']=='candidate':ck(canonical is None,'candidate has invented integrated SHA: '+v['version'])
        for key,tr in transitions.items():
            ck(bool(SHA.fullmatch(key)),'invalid git SHA')
            ck(tr['version'] in versions,'git transition version unknown')
            for p in tr.get('parents') or []:
                ck(p in transitions,'unknown git parent: '+p)
                ck(p!=key,'self-parent git transition')
        def acyclic(graph,name):
            visiting=set();finished=set()
            def visit(k):
                if k in visiting:raise ValueError(name+' cycle: '+k)
                if k in finished:return
                visiting.add(k)
                for d in graph.get(k,[]):
                    if d not in graph:raise ValueError(name+' missing target: '+d)
                    visit(d)
                visiting.remove(k);finished.add(k)
            for k in graph:visit(k)
        acyclic({k:t.get('parents') or [] for k,t in transitions.items()},'Git')
        acyclic({u['id']:[u['parent']] if u.get('parent') else [] for u in units},'parent')
        acyclic({u['id']:u.get('depends_on',[]) for u in units},'dependency')
        for file,rec in reg['files'].items():
            ck((root/file).is_file(),'registered file missing: '+file)
            ck(bool(rec.get('purpose')),'file purpose missing: '+file)
        # The small self-registry is the only content-hash exception; no recursive checksum.
        covered={u['path'] for u in units}|{'docs/CONTENT_HEALTH.json'}
        ck(set(reg['files'])==covered,'file coverage gap in scope registry')
        own={};aggregate={}
        for u in units:
            own[u['id']]=c.digest(u);aggregate[u['id']]=c.digest(u,own=False)
        core={'ENTRY','CTX','MAP','REFS','CONTROL','HISTORY'}
        ck(core.issubset(set(reg['focus'])),'core entry scope missing from focus')
        recovery=reg.get('recovery_contract',{})
        recovery_scopes=recovery.get('required_scopes',[])
        ck(RECOVERY_SCOPES.issubset(set(recovery_scopes)),'recovery minimum scopes missing')
        ck(all(s in c.units for s in recovery_scopes),'recovery scope target missing')
        outcomes=recovery.get('required_outcomes',[])
        outcome_ids=[x.get('id') for x in outcomes]
        ck(set(outcome_ids)==RECOVERY_OUTCOMES and len(outcome_ids)==len(set(outcome_ids)),
           'recovery outcomes missing or duplicated')
        readme=(root/'README.md').read_text(encoding='utf-8')
        runbook=(root/'BOOTSTRAP_RUNBOOK.html').read_text(encoding='utf-8')
        for outcome in outcomes:
            oid=outcome.get('id','')
            ck(bool(outcome.get('criterion','').strip()),'recovery criterion empty: '+oid)
            refs=outcome.get('scopes',[])
            ck(bool(refs) and all(s in c.units for s in refs),'recovery outcome scope missing: '+oid)
            required.update(refs)
            ck('| '+oid+' |' in readme,'README recovery outcome missing: '+oid)
            ck(runbook.count('data-recovery-outcome="'+oid+'"')==1,'HTML recovery outcome missing or duplicated: '+oid)
        acceptance=RecoveryAcceptance(runbook)
        if acceptance.completed:
            ck(len(acceptance.receipts)==1,'completed S08 acceptance receipt missing or duplicated')
            if len(acceptance.receipts)==1:
                receipt=acceptance.receipts[0]
                ck(receipt.get('data-user-confirmed')=='true','completed S08 lacks user confirmation')
                ck(bool(SHA.fullmatch(receipt.get('data-commit',''))),'completed S08 lacks pinned commit')
                ck(bool(receipt.get('data-report','').strip() and receipt.get('data-answer','').strip()),
                   'completed S08 lacks report or answer evidence')
            for oid in RECOVERY_OUTCOMES:
                ck(acceptance.outcomes.get(oid)==['passed'],'completed S08 outcome not accepted: '+oid)
        ck(sorted(acceptance.retention)==['RET-01','RET-02','RET-03','RET-04','RET-05'],
           'retention rules missing or duplicated')
        procedure_ids=set(reg.get('procedure_contract',{}).get('scopes',[]))
        ck(PROCEDURE_SCOPES.issubset(procedure_ids),'procedure contract scope missing')
        for pid in sorted(procedure_ids):
            ck(pid in c.units,'procedure scope target missing: '+pid)
            if pid not in c.units:continue
            fields=ProcedureFields(c.text(c.units[pid],own=False) or '')
            for role in PROCEDURE_ROLES:
                values=fields.texts(role)
                ck(len(values)==1 and bool(re.sub(r'^.*?：','',values[0],count=1).strip()),'procedure field missing or repeated: '+pid+': '+role)
            actions=' '.join(fields.texts('actions'))
            ck(fields.action_items>0,'procedure action list missing: '+pid)
            ck(not SHORTCUT.search(actions),'procedure shortcut is not executable detail: '+pid)
        required.update(reg['focus']);required.update(extra or []);required.update(recovery_scopes)
        for id in list(required):ck(id in c.units,'unknown focus/request scope: '+id)
        ck(reg['policy']['max_days']>0 and reg['policy']['max_versions']>0,'invalid policy threshold')
        version_age_mode=reg['policy'].get('version_age_mode','required')
        ck(version_age_mode in ('required','advisory'),'invalid policy version_age_mode')
        current_i=order.index(current)
        before=Contents(base,units) if base else None
        for u in units:
            uid=u['id'];updated=c.effective(u,'updated_in');reviewed=c.effective(u,'reviewed_in')
            if u.get('control_mode')=='live_input':
                ck(uid=='PROBE' and u['path']=='ACCESS_PROBE.md' and not u.get('selector'),'invalid live-input exception')
                live_checks.append({'scope':uid,'required_action':'read at the pinned Git SHA and obtain user comparison','status':'not_performed_by_offline_checker'})
                continue
            ck(updated in order or updated=='unknown','unknown update version: '+uid)
            ck(reviewed is None or reviewed in order,'unknown review version: '+uid)
            ck(bool(u.get('purpose')) and bool(u.get('role')),'scope role/purpose missing: '+uid)
            if updated in order:ck(order.index(updated)<=current_i,'future update version: '+uid)
            raw=c.text(u)
            if u.get('inline_marker'):
                markers=MARK.findall(raw or '')
                ck(('更新',updated) in markers,'update marker mismatch: '+uid)
                ck(('確認',reviewed or '未確認') in markers,'review marker mismatch: '+uid)
                for evidence_ref in re.findall(r'\bREV-[0-9]+-[A-Z][A-Z0-9_-]*\b',raw or ''):
                    ck(evidence_ref in reg['evidence'],'inline evidence reference missing: '+evidence_ref)
            receipt=u.get('review')
            if receipt:
                ck(receipt.get('version')==reviewed,'receipt/review version mismatch: '+uid)
                if updated in order and reviewed in order:ck(order.index(reviewed)>=order.index(updated),'review predates content update: '+uid)
                date=dt.date.fromisoformat(receipt['on'])
                ck(date<=today,'review date is in the future: '+uid)
                evidence=reg['evidence'].get(receipt.get('evidence_id',''))
                ck(bool(evidence and evidence.get('method') and evidence.get('result') and evidence.get('limits')),'review evidence incomplete: '+uid)
                if receipt.get('content_sha256')!=own[uid]:
                    due.setdefault(uid,[]).append('content_changed_since_review');ck(False,'review fingerprint mismatch: '+uid)
                observed=receipt.get('dependency_sha256',{})
                expected={d:aggregate[d] for d in u.get('depends_on',[])}
                if observed!=expected:
                    due.setdefault(uid,[]).append('dependency_changed_since_review');ck(False,'review dependency mismatch: '+uid)
                days_expired=(today-date).days>=reg['policy']['max_days']
                version_age=current_i-order.index(reviewed) if reviewed in order else None
                versions_expired=version_age is not None and version_age>=reg['policy']['max_versions']
                if versions_expired and version_age_mode=='advisory':
                    version_age_advisories[uid]={'reason':'version_age_threshold','reviewed_in':reviewed,
                                                'current_version':current,'version_age':version_age,
                                                'max_versions':reg['policy']['max_versions']}
                # Only the version-age trigger is optional. Content/dependency
                # mismatches, first-use requirements, and calendar expiry remain mandatory.
                if days_expired or (versions_expired and version_age_mode!='advisory'):
                    due.setdefault(uid,[]).append('review_expired')
            else:
                ck(reviewed is None,'review stamp without receipt: '+uid)
                date=dt.date.fromisoformat(u['initial_review_due'])
                if today>=date:due.setdefault(uid,[]).append('initial_review_due')
            if before:
                try:different=before.digest(u)!=own[uid]
                except (OSError,ValueError):different=True
                if different:
                    changed.append(uid);required.add(uid)
                    ck(updated==current,'changed content without current update marker: '+uid)
                if oldreg:
                    oldunit=next((x for x in oldreg['units'] if x['id']==uid),None)
                    if oldunit and not oldunit.get('review') and not receipt:
                        ck(u.get('initial_review_due')==oldunit.get('initial_review_due'),'initial due postponed without review: '+uid)
        if base and (base/'docs/VERSION_HISTORY.json').is_file():
            prior=json.loads((base/'docs/VERSION_HISTORY.json').read_text(encoding='utf-8'))
            if changed:ck(prior['candidate_version']!=current,'new project version required for changed distributed base')
        required.update(due)
        def expand(uid):
            if uid not in c.units:return
            related=c.units[uid].get('depends_on',[])+[u['id'] for u in units if u.get('parent')==uid]
            for d in related:
                if d not in required:required.add(d);expand(d)
        for uid in list(required):expand(uid)
        for uid in sorted(required):
            if uid not in c.units:continue
            if c.units[uid].get('control_mode')=='live_input':continue
            ck(bool(c.units[uid].get('review')),'required scope not reviewed: '+uid)
            if uid in due:ck(False,'scope review due: '+uid+': '+','.join(due[uid]))
        # Review policy itself cannot hide postponed overdue obligations in a before-state comparison.
        if oldreg:
            ck(reg['policy']['max_days']>0 and reg['policy']['max_versions']>0,'invalid policy threshold')
        # The human-readable timeline is derived, not a second hand-edited record.
        text=(root/'BOOTSTRAP_RUNBOOK.html').read_text(encoding='utf-8')
        for v in versions.values():
            m=re.search(r'<tr\b[^>]*data-history-version="'+re.escape(v['version'])+'"[^>]*>(.*?)</tr>',text,re.S)
            ck(bool(m),'timeline display missing: '+v['version'])
            if m:
                ck(v['summary'] in m.group(1),'timeline summary differs: '+v['version'])
                if v.get('integrated_commit'):ck(v['integrated_commit'] in m.group(1),'timeline SHA differs: '+v['version'])
        pending=[u['id'] for u in units if not u.get('review') and u.get('control_mode')!='live_input']
        ck(reg.get('scan_index')==scan_index(reg),'scan index is stale; regenerate from authoritative units')
        if not base:warnings.append('before-state comparison not run (--base omitted)')
        if pending:warnings.append('initial unreviewed scopes exist; must review before use or initial due date')
        if version_age_advisories:
            warnings.append('version-age review advisories: '+str(len(version_age_advisories))+
                            ' scopes reached max_versions; inspect version_age_advisories (no automatic review stamps)')
        return {'ok':not errors,'checks':checks,'version':current,'as_of':today.isoformat(),
                'required_scopes':sorted(required),'recovery_outcomes':outcome_ids,'procedure_scopes':sorted(procedure_ids),'changed_scopes':changed,'due_scopes':due,
                'version_age_advisories':version_age_advisories,
                'initial_unreviewed_scopes':pending,'live_checks_required':live_checks,'errors':errors,'warnings':warnings,
                'limits':['No GitHub live verification','No semantic or scientific truth certification','No automatic review stamps','Self-registry integrity relies on external hash/base review']}
    except (OSError,ValueError,KeyError,TypeError,RecursionError) as e:
        return {'ok':False,'checks':checks,'errors':errors+[str(e)],'warnings':warnings}

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('root',nargs='?',type=Path,default=Path('.'))
    p.add_argument('--base',type=Path)
    p.add_argument('--as-of',help='ISO date for reproducibility; do not backdate to bypass deadlines')
    p.add_argument('--scope',action='append',default=[],help='Additional scope required by this task')
    display=p.add_mutually_exclusive_group()
    display.add_argument('--index',action='store_true',help='Emit derived small scan index only; does not approve reviews')
    display.add_argument('--fingerprints',action='store_true',help='Emit current scope fingerprints only; does not approve reviews')
    a=p.parse_args()
    if (a.index or a.fingerprints) and (a.base is not None or a.as_of is not None or a.scope):
        p.error('display-only options cannot claim verification or before-state comparison')
    if a.index or a.fingerprints:
        reg=json.loads((a.root/'docs/CONTENT_HEALTH.json').read_text(encoding='utf-8'))
        c=Contents(a.root,reg['units'])
        result=scan_index(reg) if a.index else {u['id']:{'content_sha256':c.digest(u),'dependency_sha256':{d:c.digest(c.units[d],False) for d in u.get('depends_on',[])}} for u in reg['units']}
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    result=inspect(a.root,a.base,a.as_of,a.scope)
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if result['ok'] else 1
if __name__=='__main__':raise SystemExit(main())
