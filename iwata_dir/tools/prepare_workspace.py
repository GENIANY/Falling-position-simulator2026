#!/usr/bin/env python3
"""Guarded local workspace preparation (Python >= 3.10; Git >= 2.23).

inspect: no network or content changes.
sync: fetch origin/main; fast-forward clean main ONLY to --expected-head.
normalize: preview, or --apply a CRLF-to-LF-only conversion that equals HEAD.
verify: require all tracked worktree bytes to equal HEAD.
No push, clone, reset, clean, automatic stash, or persistent Git configuration.
Close editors and pause concurrent Git/sync writers while using mutating modes.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile

REPOSITORY = 'GENIANY/space-balloon-simulator-jp'
ORIGINS = {
    'https://github.com/' + REPOSITORY + '.git',
    'https://github.com/' + REPOSITORY,
    'git@github.com:' + REPOSITORY + '.git',
    'ssh://git@github.com/' + REPOSITORY + '.git',
}
TEXT_SUFFIXES = {'.md', '.html', '.json', '.csv', '.py', '.tex', '.ps1', '.yml', '.yaml'}
SHA = re.compile(r'[0-9a-f]{40}\Z')

class Stop(RuntimeError):
    """Safe stop. Existing partial success is not rolled back destructively."""

class Workspace:
    def __init__(self, path: Path, git: str = 'git'):
        self.path = path.expanduser().resolve(strict=True)
        self.git = git
        if not self.path.is_dir():
            raise Stop('Not a directory.')
        # Capture native stdout as BYTES; never decode paths through a shell.
        raw = self.run('rev-parse', '--show-toplevel').rstrip(b'\r\n')
        self.root = Path(os.fsdecode(raw) if os.name != 'nt' else raw.decode('utf-8')).resolve(strict=True)
        if not self.path.samefile(self.root):
            raise Stop('Choose the clone root, not one of its subdirectories.')
        self.path = self.root
        origin = self.run('config', '--get-all', 'remote.origin.url').decode('utf-8').splitlines()
        if len(origin) != 1 or origin[0] not in ORIGINS:
            raise Stop('Origin is not a single standard URL for the expected repository. Do not share credentials.')
        self.origin = origin[0]

    def run(self, *args: str, data: bytes | None = None,
            accepted: tuple[int, ...] = (0,)) -> bytes:
        env = os.environ.copy()
        # Honor credentials, but prevent optional status writes and recursive fetches.
        env['GIT_OPTIONAL_LOCKS'] = '0'
        result = subprocess.run(
            [self.git, '--no-optional-locks', '-c', 'core.fsmonitor=false',
             '-c', 'core.quotepath=false', '-C', str(self.path), *args],
            input=data, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env=env, check=False,
        )
        if result.returncode not in accepted:
            # Raw transport stderr can include credentials/URLs: do not print it.
            raise Stop(f'Git operation {args[0]} failed (exit {result.returncode}); '
                       'inspect the cause locally without sharing credentials.')
        return result.stdout

    def head(self) -> str:
        return self.run('rev-parse', 'HEAD').decode('ascii').strip()

    def guard(self, expected: str | None = None) -> str:
        head = self.head()
        if expected is not None and head != expected:
            raise Stop(f'HEAD mismatch: actual={head}; expected={expected}. No file repair performed.')
        if self.run('symbolic-ref', '--short', 'HEAD').decode('utf-8').strip() != 'main':
            raise Stop('Only the existing main branch is accepted; do not switch automatically.')
        for name in ('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply'):
            raw = self.run('rev-parse', '--git-path', name).decode('utf-8').strip()
            p = Path(raw)
            if not p.is_absolute(): p = self.root / p
            if p.exists(): raise Stop('An unfinished Git operation exists: ' + name)
        if self.run('status', '--porcelain=v1', '-z', '--untracked-files=all'):
            raise Stop('Tracked or untracked changes exist. Preserve them; do not reset, clean, or auto-stash.')
        # Verify that no staged/skip-worktree/assume-unchanged flags hide local data.
        for record in self.run('ls-files', '-v', '-z').split(b'\0'):
            if record and not record.startswith(b'H '):
                raise Stop('Special index flags or unresolved entries require manual inspection.')
        if self.run('diff', '--cached', '--name-only', 'HEAD', '--'):
            raise Stop('The index differs from HEAD.')
        return head

    def entries(self, ref: str = 'HEAD') -> list[tuple[str, str]]:
        out = []
        for item in self.run('ls-tree', '-rz', '--full-tree', ref).split(b'\0'):
            if not item: continue
            meta, raw_name = item.split(b'\t', 1)
            mode, kind, oid = meta.split()
            if mode not in (b'100644', b'100755') or kind != b'blob':
                raise Stop('Symlinks/submodules/special entries are not supported.')
            name = raw_name.decode('utf-8')
            path = Path(name)
            if path.is_absolute() or '..' in path.parts or '\\' in name:
                raise Stop('Unsafe tracked path.')
            out.append((name, oid.decode('ascii')))
        return out

    def raw_plan(self) -> tuple[list[tuple[Path, bytes, bytes]], int]:
        """Accept ONLY exact bytes or reversible CRLF expansion of known LF text."""
        planned = []
        entries = self.entries()
        for name, oid in entries:
            p = self.root / name
            if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(self.root):
                raise Stop('Missing, linked, or out-of-tree tracked file: ' + name)
            old = p.read_bytes()
            stored = self.run('cat-file', 'blob', oid)
            if old == stored: continue
            is_text = name == '.gitattributes' or p.suffix in TEXT_SUFFIXES
            if (not is_text or b'\0' in stored or b'\r' in stored
                    or old.replace(b'\r\n', b'\n') != stored):
                raise Stop('Difference beyond CRLF/LF; no files changed: ' + name)
            try: stored.decode('utf-8')
            except UnicodeDecodeError as exc:
                raise Stop('Tracked text is not UTF-8: ' + name) from exc
            planned.append((p, old, stored))
        return planned, len(entries)

    def attributes_ok(self, plans: list[tuple[Path, bytes, bytes]]) -> None:
        # Check ALL governed text, not only files being converted.
        names = [n for n, _ in self.entries()
                 if n == '.gitattributes' or Path(n).suffix in TEXT_SUFFIXES]
        attrs = self.run('check-attr', '-z', '--stdin', 'text', 'eol',
                         'filter', 'working-tree-encoding', 'ident',
                         data=b''.join(n.encode('utf-8') + b'\0' for n in names))
        parts = attrs.split(b'\0')[:-1]
        if len(parts) != len(names) * 15: raise Stop('Unexpected attribute response.')
        values: dict[str, dict[str, str]] = {}
        for i in range(0, len(parts), 3):
            n, key, val = [v.decode('utf-8') for v in parts[i:i+3]]
            values.setdefault(n, {})[key] = val
        for n in names:
            a = values[n]
            if a['text'] != 'set' or a['eol'] != 'lf':
                raise Stop('Effective text/eol contract is not text+lf: ' + n)
            if any(a[k] not in ('unspecified', 'unset') for k in ('filter', 'working-tree-encoding', 'ident')):
                raise Stop('Content-transforming attribute requires manual review: ' + n)

    def inspect(self) -> dict:
        head = self.guard()
        plan, count = self.raw_plan()
        return {'ok': True, 'operation': 'inspect', 'head': head,
                'root': str(self.root), 'root_matches_input': True,
                'origin_matches': True, 'branch': 'main', 'tracked_files': count,
                'crlf_only_paths': [p.relative_to(self.root).as_posix() for p, _, _ in plan],
                'network_used': False, 'working_files_changed': False}

    def sync(self, target: str) -> dict:
        before = self.guard()
        self.raw_plan()  # refuse hidden content edits even before fetch
        # Restrict transport to a validated URL and suppress local hooks for this call.
        with tempfile.TemporaryDirectory(prefix='balloon-no-hooks-') as empty_hooks:
            self.run('-c', 'core.hooksPath=' + empty_hooks,
                     'fetch', '--no-tags', '--no-recurse-submodules', self.origin, 'refs/heads/main:refs/remotes/origin/main')
            fetched = self.run('rev-parse', 'FETCH_HEAD^{commit}').decode('ascii').strip()
            if fetched != target:
                raise Stop(f'Remote main is {fetched}, not requested {target}. '
                           'Fetch completed, but working files were not updated.')
            self.guard(before)
            ancestor = self.run('merge-base', before, target).decode('ascii').strip()
            if ancestor != before:
                raise Stop('Local HEAD is not an ancestor of target. No merge performed.')
            self.run('-c', 'core.hooksPath=' + empty_hooks,
                     'merge', '--ff-only', '--no-edit', '--no-overwrite-ignore', target)
        self.guard(target)
        # The explicit refspec refreshes origin/main; the working branch is pinned to target.
        return {'ok': True, 'operation': 'sync', 'before': before, 'head': target,
                'fast_forward_only': True, 'network_used': True,
                'note': 'FETCH_HEAD, origin/main and object database updated; no push or persistent config changes.'}

    def normalize(self, expected: str, apply: bool = False) -> dict:
        self.guard(expected)
        plan, count = self.raw_plan()   # validate the entire tree BEFORE any writes
        self.attributes_ok(plan)
        changed = []
        if apply:
            for p, old, stored in plan:
                self.guard(expected)
                if p.is_symlink() or p.read_bytes() != old:
                    raise Stop('Concurrent file change detected; stop and preserve both states.')
                # Each file is replaced atomically. The operation is NOT atomic across all files.
                fd, temporary = tempfile.mkstemp(prefix='.balloon-lf-', dir=str(p.parent))
                try:
                    with os.fdopen(fd, 'wb') as f:
                        f.write(stored); f.flush(); os.fsync(f.fileno())
                    os.chmod(temporary, stat.S_IMODE(p.stat().st_mode))
                    if p.is_symlink() or p.read_bytes() != old:
                        raise Stop('Concurrent file change detected before replacement.')
                    os.replace(temporary, p)
                finally:
                    if os.path.exists(temporary): os.unlink(temporary)
                # Git can retain a stale conversion/stat cache after an EOL-only rewrite.
                # Re-add ONLY this proven-identical path; guard() verifies no staged diff.
                if p.read_bytes() != stored or self.head() != expected:
                    raise Stop('Concurrent change before index refresh; inspect locally.')
                self.run('add', '--renormalize', '--', p.relative_to(self.root).as_posix())
                changed.append(p.relative_to(self.root).as_posix())
            self.guard(expected)
            remaining, _ = self.raw_plan()
            if remaining: raise Stop('Conversion incomplete. Rerun preview; do not force overwrite.')
        return {'ok': True, 'operation': 'normalize', 'apply': apply, 'head': expected,
                'tracked_files': count,
                'planned': [p.relative_to(self.root).as_posix() for p, _, _ in plan],
                'changed': changed, 'head_bytes_equal': not plan or apply,
                'index_refreshed_without_tree_change': bool(changed),
                'persistent_git_config_changed': False, 'network_used': False}

    def verify(self, expected: str) -> dict:
        result = self.normalize(expected, False)
        if result['planned']: raise Stop('CRLF-only differences remain; run normalization preview first.')
        return {'ok': True, 'operation': 'verify', 'head': expected,
                'head_bytes_equal': True, 'tracked_files': result['tracked_files']}

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation', choices=['inspect', 'sync', 'normalize', 'verify'])
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--git', default='git')
    p.add_argument('--expected-head')
    p.add_argument('--apply', action='store_true')
    args = p.parse_args()
    try:
        if args.operation != 'inspect' and not SHA.fullmatch(args.expected_head or ''):
            raise Stop('A lowercase 40-character --expected-head is required.')
        if args.apply and args.operation != 'normalize': raise Stop('--apply is only valid for normalize.')
        ws = Workspace(args.repo, args.git)
        if args.operation == 'inspect': result = ws.inspect()
        elif args.operation == 'sync': result = ws.sync(args.expected_head)
        elif args.operation == 'verify': result = ws.verify(args.expected_head)
        else: result = ws.normalize(args.expected_head, args.apply)
        # ASCII JSON survives native-console code-page mismatches; paths are escaped, not renamed.
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 0
    except (Stop, OSError, ValueError, UnicodeError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc),
                          'note': 'Stop here; no reset/clean/automatic rollback. Preserve any partial success.'},
                         ensure_ascii=True, indent=2))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
