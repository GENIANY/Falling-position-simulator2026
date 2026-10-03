#!/usr/bin/env python3
"""Record the existing checks without depending on terminal scrollback.

Python 3.12/64-bit dedicated prefix; no package or Git changes. Each child has
its own raw stdout/stderr files OUTSIDE the repository and environment. The
post-test byte check runs even after failure. Logs are evidence, not automatic
review approval. A forced process kill or disk failure may leave partial logs.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time
import uuid


def write_json(path: Path, data: dict) -> None:
    """Write LF/UTF-8 deterministically; publish complete summary atomically."""
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=True, indent=2) + '\n',
                         encoding='utf-8', newline='\n')
    temporary.replace(path)


def environment_record(expected_prefix: Path) -> dict:
    actual = Path(sys.prefix).resolve()
    expected = expected_prefix.resolve(strict=True)
    ok = (actual == expected and sys.version_info[:2] == (3, 12)
          and struct.calcsize('P') == 8
          and (expected / 'conda-meta/history').is_file())
    return {'ok': ok, 'version': sys.version, 'executable': sys.executable,
            'prefix': str(actual), 'expected_prefix': str(expected),
            'bits': struct.calcsize('P') * 8,
            'requirement': 'dedicated conda prefix, Python 3.12, 64 bit'}


def output_directory(parent: Path, repo: Path, prefix: Path) -> Path:
    parent = parent.expanduser().resolve()
    if parent.is_relative_to(repo.resolve()) or parent.is_relative_to(prefix.resolve()):
        raise ValueError('Log location must be outside the repository and conda prefix.')
    parent.mkdir(parents=True, exist_ok=True)
    name = 'checks-' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:10]
    out = parent / name
    out.mkdir(exist_ok=False)
    return out


def execute_stage(stage: tuple[str, list[str]], repo: Path, out: Path) -> dict:
    name, argv = stage
    stdout = out / (name + '.stdout.txt')
    stderr = out / (name + '.stderr.txt')
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
    began = time.monotonic()
    error = None
    with stdout.open('xb') as so, stderr.open('xb') as se:
        try:
            result = subprocess.run(argv, cwd=repo, stdout=so, stderr=se,
                                    stdin=subprocess.DEVNULL, env=env, check=False)
            code = result.returncode
        except (OSError, KeyboardInterrupt) as exc:
            code = 130 if isinstance(exc, KeyboardInterrupt) else 127
            error = type(exc).__name__ + ': ' + str(exc)
            se.write((error + '\n').encode('utf-8', errors='backslashreplace'))
    result = {'id': name, 'argv': argv, 'returncode': code,
              'seconds': round(time.monotonic() - began, 3),
              'stdout': stdout.name, 'stderr': stderr.name,
              'stdout_sha256': hashlib.sha256(stdout.read_bytes()).hexdigest(),
              'stderr_sha256': hashlib.sha256(stderr.read_bytes()).hexdigest()}
    if error:
        result['launch_error'] = error
    if name == '03-regression':
        text = stderr.read_bytes().decode('utf-8', errors='replace')
        count = re.search(r'Ran (\d+) tests? in ', text)
        skips = re.search(r'\bskipped=(\d+)', text)
        result['tests_run'] = int(count[1]) if count else None
        result['skipped'] = int(skips[1]) if skips else 0
        # A skipped or empty suite is not complete acceptance, even with exit=0.
        result['complete_suite'] = code == 0 and bool(count) and int(count[1]) > 0 and not skips
    return result


def run_stages(repo: Path, out: Path, stages: list[tuple[str, list[str]]],
               post_stage: tuple[str, list[str]], summary: dict,
               executor=execute_stage) -> dict:
    """Stop substantive work on first error, but always attempt post verification."""
    summary.update(ok=False, status='running', stages=[], skipped_stages=[])
    write_json(out / 'summary.json', summary)
    failure = False
    try:
        for i, stage in enumerate(stages):
            item = executor(stage, repo, out)
            summary['stages'].append(item)
            write_json(out / 'summary.json', summary)
            if item['returncode'] != 0 or item.get('complete_suite') is False:
                failure = True
                summary['skipped_stages'] = [s[0] for s in stages[i+1:]]
                break
    except (OSError, ValueError, KeyboardInterrupt) as exc:
        failure = True
        summary['runner_error'] = type(exc).__name__ + ': ' + str(exc)
    finally:
        try:
            item = executor(post_stage, repo, out)
            summary['stages'].append(item)
            failure = failure or item['returncode'] != 0
        except (OSError, ValueError, KeyboardInterrupt) as exc:
            failure = True
            summary['post_error'] = type(exc).__name__ + ': ' + str(exc)
        summary['ok'] = not failure
        summary['status'] = 'passed' if not failure else 'failed'
        summary['finished_at_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
        write_json(out / 'summary.json', summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--expected-head', required=True)
    p.add_argument('--expected-prefix', type=Path, required=True)
    p.add_argument('--output-parent', type=Path, required=True)
    p.add_argument('--git', default='git')
    a = p.parse_args(argv)
    out = None
    try:
        repo = a.repo.resolve(strict=True)
        if not re.fullmatch(r'[0-9a-f]{40}', a.expected_head):
            raise ValueError('A complete lowercase commit SHA is required.')
        if Path(__file__).resolve() != repo / 'tools/run_checks.py':
            raise ValueError('Run the tool from the specified clone, not a delivery copy.')
        out = output_directory(a.output_parent, repo, a.expected_prefix)
        info = environment_record(a.expected_prefix)
        write_json(out / '00-environment.json', info)
        if not info['ok']:
            raise ValueError('Dedicated interpreter mismatch; do not recreate or update automatically.')
        cmd = [sys.executable, '-X', 'utf8', '-B']
        verify = cmd + ['tools/prepare_workspace.py', 'verify', '--repo', '.', '--git', a.git,
                        '--expected-head', a.expected_head]
        stages = [('00-pre-verify', verify),
                  ('01-state', cmd + ['tools/check_state.py', '.']),
                  ('02-health', cmd + ['tools/check_health.py', '.']),
                  ('03-regression', cmd + ['-m', 'unittest', 'discover', '-s', 'tests', '-v'])]
        summary = run_stages(repo, out, stages, ('04-post-verify', verify),
                             {'schema_version': 1, 'expected_head': a.expected_head,
                              'repo': str(repo), 'environment': info,
                              'log_directory': str(out),
                              'started_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
                              'network_required': False,
                              'limits': ['No GitHub freshness check.', 'No scientific/PDF validation.',
                                         'Raw child outputs are evidence; review before sharing.',
                                         'Logs do not override initial-review deadlines.']})
        print(json.dumps({'ok': summary['ok'], 'log_directory': str(out),
                          'summary': str(out / 'summary.json'),
                          'stages': [{k: v for k, v in s.items()
                                      if k in ('id', 'returncode', 'tests_run', 'skipped', 'complete_suite')}
                                     for s in summary['stages']]}, ensure_ascii=True, indent=2))
        return 0 if summary['ok'] else 1
    except (OSError, ValueError) as exc:
        result = {'ok': False, 'status': 'startup_failed', 'error': str(exc),
                  'log_directory': str(out) if out else None}
        if out:
            write_json(out / 'summary.json', result)
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
