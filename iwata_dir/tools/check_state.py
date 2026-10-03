#!/usr/bin/env python3
"""Check the current working-tree contract (stdlib, Python >= 3.10).

This is not a freshness, authorization, scientific-validity, or visual-PDF test.
It never changes files or communicates with GitHub.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
import re
import stat
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

LABELS = {'done': '[完了]', 'doing': '[取組中]', 'partial': '[部分完了]',
          'todo': '[未着手]', 'waiting': '[確認待ち]', 'blocked': '[中断]',
          'deferred': '[保留]'}
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}

# These exact roots contain reproducible dependencies/build output, not project
# source or saved analyses. Do not interpret arbitrary .gitignore patterns here.
RUNTIME_ROOTS = frozenset({'frontend/node_modules', 'frontend/dist', 'backend/.venv'})


def source_files(root: Path, expected: list[str], check) -> set[str]:
    """Inventory source without traversing runtime roots or filesystem links.

    Registered source inside a runtime root is an error, even if absent. A link
    or file occupying such a root is also an error. Third-party contents inside
    an ordinary runtime directory are deliberately outside this source audit.
    """
    for name in expected:
        check(not any(name == d or name.startswith(d + '/') for d in RUNTIME_ROOTS),
              f'registered source inside runtime root: {name}')
    actual: set[str] = set()
    def walk_error(error):
        check(False, f'source tree unreadable: {error}')
    for folder, directories, files in os.walk(root, topdown=True, followlinks=False, onerror=walk_error):
        for name in sorted(directories + files):
            p = Path(folder) / name
            rel = p.relative_to(root)
            if name in {'.git', '__pycache__'}:
                if name in directories: directories.remove(name)
                continue
            try:
                info = p.lstat()
                is_link = stat.S_ISLNK(info.st_mode) or bool(
                    getattr(info, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 1024))
            except OSError as error:
                check(False, f'source tree unreadable: {rel}: {error}')
                if name in directories: directories.remove(name)
                continue
            if is_link:
                check(False, f'symlink/reparse point not allowed: {rel}')
                if name in directories: directories.remove(name)
                continue
            if rel.as_posix() in RUNTIME_ROOTS:
                check(stat.S_ISDIR(info.st_mode), f'runtime root must be a directory: {rel}')
                if name in directories: directories.remove(name)
                continue
            if stat.S_ISDIR(info.st_mode):
                # os.walk can classify an entry as a file after is_dir fails,
                # without forwarding that error to onerror. Do not silently
                # accept a directory whose children were never scheduled.
                check(name in directories, f'source directory was not traversed: {rel}')
                check(not any(part.lower() in {'legacy', 'archive', 'archives', '.versions'} or
                              re.fullmatch(r'v?\d+\.\d+(?:\.\d+)?', part) for part in rel.parts),
                      f'archive/version directory is outside current-state contract: {rel}')
            elif stat.S_ISREG(info.st_mode):
                if p.suffix != '.pyc':
                    actual.add(rel.as_posix())
            else:
                check(False, f'unsupported filesystem entry: {rel}')
    return actual

class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.links: list[str] = []
        self.units: list[dict] = []
        self.stack: list[tuple[str, dict]] = []
        self.headings: list[tuple[dict, list[str]]] = []
        self.copy_targets: list[str] = []
        self.version: str | None = None
        self.snapshot_id: str | None = None
    def handle_starttag(self, tag: str, attrs: list[tuple[str,str|None]]) -> None:
        a = dict(attrs)
        if a.get('id'): self.ids.append(a['id'])
        if a.get('href'): self.links.append(a['href'])
        if a.get('data-copy'): self.copy_targets.append(a['data-copy'])
        if tag == 'meta' and a.get('name') == 'document-version': self.version = a.get('content')
        if tag == 'meta' and a.get('name') == 'snapshot-id': self.snapshot_id = a.get('content')
        classes = (a.get('class') or '').split()
        if 'step' in classes or 'substep' in classes:
            self.units.append({'id': a.get('id'), 'status': a.get('data-status'), 'text': '',
                               'major': 'step' in classes})
        if tag in ('h2','h3'):
            # The nearest containing step/substep owns its heading.
            parent = next((s for _,s in reversed(self.stack)
                           if set((s.get('class') or '').split()) & {'step','substep'}), None)
            if parent:
                unit = next((u for u in reversed(self.units) if u['id'] == parent.get('id')), None)
                if unit is not None: self.headings.append((unit, []))
        if tag not in VOID: self.stack.append((tag, a))
    def handle_startendtag(self, tag: str, attrs: list[tuple[str,str|None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID: self.handle_endtag(tag)
    def handle_data(self, data: str) -> None:
        if self.headings: self.headings[-1][1].append(data)
    def handle_endtag(self, tag: str) -> None:
        if tag in ('h2','h3') and self.headings:
            unit, text = self.headings.pop()
            unit['text'] = ''.join(text)
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

def current_paths(root: Path) -> list[str]:
    text = (root/'CONTENT_MAP.md').read_text(encoding='utf-8')
    hit = re.search(r'<!-- CURRENT_PATHS_BEGIN -->\s*```text\s*\n(.*?)\n```\s*<!-- CURRENT_PATHS_END -->', text, re.S)
    if not hit: raise ValueError('CONTENT_MAP: missing CURRENT_PATHS block')
    return [s.strip() for s in hit.group(1).splitlines() if s.strip()]

def provided_pdf_paths(root: Path) -> tuple[set[str], list[str]]:
    """Accept only byte-pinned user-supplied references whose TeX was not supplied.

    This does not waive the TeX requirement for generated or unregistered PDFs.
    Every declaration is checked, even when its PDF was deleted or has a TeX pair.
    """
    accepted: set[str] = set()
    errors: list[str] = []
    root = root.resolve()
    try:
        contract = json.loads((root/'docs/CONTINUITY_CONTRACT.json').read_text(encoding='utf-8'))
        sources = json.loads((root/'references/SOURCES.json').read_text(encoding='utf-8'))
        assets, records = contract['assets'], sources['sources']
        if not isinstance(assets, list) or not all(isinstance(a, dict) for a in assets):
            raise ValueError('assets must be a list of objects')
        if not isinstance(records, list) or not all(isinstance(s, dict) for s in records):
            raise ValueError('sources must be a list of objects')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return accepted, ['provided PDF registry unreadable: '+str(exc)]
    for asset in assets:
        if 'provided_pdf' not in asset:
            continue
        name, declaration = asset.get('path'), asset['provided_pdf']
        prefix = f'provided PDF {name!r}: '
        if not isinstance(name, str):
            errors.append(prefix+'path must be a string'); continue
        path = PurePosixPath(name)
        if (path.is_absolute() or name != path.as_posix() or
                any(p in ('', '.', '..') for p in name.split('/')) or
                '\\' in name or ':' in name or path.parts[:2] != ('references', 'user_supplied') or
                len(path.parts) < 3 or path.suffix != '.pdf' or
                not (root/name).resolve().is_relative_to(root/'references/user_supplied')):
            errors.append(prefix+'unsafe path outside references/user_supplied'); continue
        if asset.get('lifecycle') != 'reference':
            errors.append(prefix+'lifecycle must be reference'); continue
        if sum(a.get('path') == name for a in assets) != 1:
            errors.append(prefix+'asset path must be unique'); continue
        if not isinstance(declaration, dict):
            errors.append(prefix+'provided_pdf must be an object'); continue
        if declaration.get('tex_source') != 'not_provided':
            errors.append(prefix+'tex_source must be not_provided'); continue
        reason = declaration.get('reason')
        if not isinstance(reason, str) or not reason.strip():
            errors.append(prefix+'reason must be nonempty'); continue
        fingerprint = declaration.get('sha256')
        if not isinstance(fingerprint, str) or not re.fullmatch(r'[0-9a-f]{64}', fingerprint):
            errors.append(prefix+'sha256 must be a lowercase SHA-256'); continue
        source_id = declaration.get('source_record')
        matching = [s for s in records if s.get('id') == source_id]
        if (not isinstance(source_id, str) or not source_id.strip() or len(matching) != 1 or
                matching[0].get('url') != 'local:'+name):
            errors.append(prefix+'source_record must uniquely identify its local path'); continue
        try:
            data = (root/name).read_bytes()
        except OSError as exc:
            errors.append(prefix+'original bytes unavailable: '+str(exc)); continue
        if hashlib.sha256(data).hexdigest() != fingerprint:
            errors.append(prefix+'original SHA-256 mismatch'); continue
        accepted.add(name)
    return accepted, errors


def inspect(root: Path) -> dict:
    root = root.resolve()
    failures: list[str] = []
    checks = 0
    def check(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition: failures.append(message)
    try:
        expected = current_paths(root)
    except (OSError, ValueError) as e:
        return {'ok':False, 'checks':1, 'errors':[str(e)]}
    check(len(expected) == len(set(expected)), 'duplicate path in CURRENT_PATHS')
    for name in expected:
        p = PurePosixPath(name)
        check(not p.is_absolute() and '..' not in p.parts and '\\' not in name, f'unsafe path: {name}')
    actual = source_files(root, expected, check)
    check(set(expected) == actual, f'path set mismatch: missing={sorted(set(expected)-actual)}; extra={sorted(actual-set(expected))}')
    page = Page()
    try:
        html = (root/'BOOTSTRAP_RUNBOOK.html').read_text(encoding='utf-8')
        page.feed(html)
    except (OSError, UnicodeError) as e:
        check(False, f'HTML unreadable: {e}')
        return {'ok':False,'checks':checks,'errors':failures}
    check(html.rstrip().endswith('</html>'), 'HTML missing closing html tag')
    try:
        registry = json.loads((root/'docs/CONTENT_HEALTH.json').read_text(encoding='utf-8'))
        for filename in ('README.md','PROJECT_CONTEXT.md','CONTENT_MAP.md','REFERENCE_LOG.md'):
            if (root/filename).is_file():
                value = re.search(r'^revision:\s*(\S+)\s*$', (root/filename).read_text(encoding='utf-8'), re.M)
                expected_version = registry['files'][filename]['document_version']
                check(value is not None and value.group(1)==expected_version, f'unregistered document revision: {filename}')
        check(page.version==registry['files']['BOOTSTRAP_RUNBOOK.html']['document_version'], 'HTML version differs from registry')
        check(page.snapshot_id=='BJP-current-'+str(page.version), 'HTML snapshot id differs from document version')
        check('END OF RUNBOOK · BJP-current-'+str(page.version) in html, 'HTML footer version differs from document version')
    except (OSError, KeyError, ValueError) as e:
        check(False, f'version registry unreadable: {e}')
    check(len(page.ids)==len(set(page.ids)), 'duplicate HTML id')
    check(bool(page.units), 'HTML has no steps')
    # These elements are consumed by the embedded display/copy script.
    for target in ('progress-summary','progress-links','show-all','show-open','filter-label','copy-status'):
        check(target in page.ids, 'script DOM target missing: '+target)
    for unit in page.units:
        status = unit['status']
        check(status in LABELS, f"invalid status at {unit['id']}: {status}")
        if status in LABELS:
            check(LABELS[status] in unit['text'], f"body status mismatch at {unit['id']}")
        check(unit['id'] in unit['text'], f"step id absent from heading: {unit['id']}")
        if unit['major']:
            kids = [u for u in page.units if not u['major'] and u['id'].startswith(unit['id']+'-')]
            if status=='done': check(all(u['status']=='done' for u in kids), f"done parent has unfinished children: {unit['id']}")
            if status=='partial': check(any(u['status']=='done' for u in kids) and any(u['status']!='done' for u in kids), f"partial parent needs done and unfinished children: {unit['id']}")
    for target in page.copy_targets:
        check(target in page.ids, f'copy target missing: {target}')
    def link_check(source: Path, href: str) -> None:
        url = urlsplit(href)
        if url.scheme or url.netloc: return
        path = (source.parent/unquote(url.path)).resolve() if url.path else source
        check(path.is_relative_to(root) and path.is_file(), f'broken local link: {source.relative_to(root)} -> {href}')
        if path==root/'BOOTSTRAP_RUNBOOK.html' and url.fragment:
            check(unquote(url.fragment) in page.ids, f'broken HTML anchor: {href}')
    for link in page.links: link_check(root/'BOOTSTRAP_RUNBOOK.html', link)
    for name in expected:
        if name.endswith('.md') and (root/name).exists():
            for link in re.findall(r'(?<!!)\[[^\]\n]*\]\(([^\s)]+)\)', (root/name).read_text(encoding='utf-8')):
                link_check(root/name, link)
    provided_pdfs, provided_errors = provided_pdf_paths(root)
    check(not provided_errors, 'provided PDF contract: '+'; '.join(provided_errors))
    for name in sorted(actual):
        if not name.endswith('.pdf'): continue
        pdf = root / name
        check(pdf.with_suffix('.tex').is_file() or pdf.relative_to(root).as_posix() in provided_pdfs,
              f'PDF without TeX: {pdf.relative_to(root)}')
        check(pdf.read_bytes().startswith(b'%PDF-'), f'bad PDF header: {pdf.relative_to(root)}')
    try:
        with (root/'docs/BACKLOG.csv').open(encoding='utf-8-sig',newline='') as f: tasks=list(csv.DictReader(f))
        ids=[r['id'] for r in tasks]
        check(len(ids)==len(set(ids)), 'duplicate task id')
        for r in tasks:
            check(bool(r['acceptance_criteria']), f"no acceptance criteria: {r['id']}")
            if r['status']=='完了': check(bool(r['evidence'].strip()), f"done task without evidence: {r['id']}")
            for dep in filter(None,r['depends_on'].split(';')):
                check(dep in ids and dep!=r['id'], f"invalid task dependency: {r['id']} -> {dep}")
        with (root/'docs/UNCERTAINTIES.csv').open(encoding='utf-8-sig',newline='') as f: unknowns=list(csv.DictReader(f))
        check(len(unknowns)==len({r['id'] for r in unknowns}), 'duplicate uncertainty id')
        for r in unknowns:
            for task in filter(None,r['resolution_task_ids'].split(';')):
                check(task in ids, f"uncertainty points to unknown task: {r['id']} -> {task}")
        json.loads((root/'references/SOURCES.json').read_text(encoding='utf-8'))
        check(True,'sources JSON parsed')
    except (OSError, KeyError, ValueError) as e: check(False,f'table/source parse failed: {e}')
    # Purpose/lifecycle and argument architecture are a separate responsibility.
    # This call keeps the normal runner on the full structural-check path.
    try:
        import importlib.util
        spec=importlib.util.spec_from_file_location('balloon_continuity',root/'tools/check_contract.py')
        if not spec or not spec.loader: raise ValueError('contract checker missing')
        contract=importlib.util.module_from_spec(spec)
        # Execute the local source without creating a loader bytecode cache,
        # including when this read-only command was started without -B.
        source=root/'tools/check_contract.py'
        exec(compile(source.read_bytes(),str(source),'exec'),contract.__dict__)
        result=contract.inspect(root)
        check(result['ok'], 'continuity contract: '+ '; '.join(result['errors']))
    except (OSError,ValueError,ImportError) as e:
        check(False,'continuity contract unavailable: '+str(e))
    return {'ok':not failures,'checks':checks,'file_count':len(actual),'document_version':page.version,
            'steps':{u['id']:u['status'] for u in page.units},'errors':failures,
            'limitations':['No GitHub freshness or permission check','No semantic completeness or scientific verification','No PDF rendering check','Does not validate arbitrary textual path mentions']}

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root',nargs='?',type=Path,default=Path('.'))
    args=parser.parse_args()
    result=inspect(args.root)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['ok'] else 1
if __name__=='__main__': raise SystemExit(main())
