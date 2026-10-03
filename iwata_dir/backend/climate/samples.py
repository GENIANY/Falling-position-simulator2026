"""Optional original wind samples for empirical monthly profiles.

The supplied moments database remains intact. This companion binds complete
months to that database's exact years, levels and cells. It cannot manufacture
monthly quantiles from the database's few half-month quantiles.
"""
from __future__ import annotations

import calendar
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from .contracts import ClimateError

SCHEMA = "balloon.climate.raw-months/1"
PROFILE_SCHEMA = "climate-month-profiles/1"


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def identity(path):
    s = path.stat()
    return s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns


def expected_times(month, years=(2016, 2025)):
    return [f"{year:04d}-{month:02d}-{day:02d}T{hour:02d}:00:00Z"
            for year in range(years[0], years[1]+1)
            for day in range(1, calendar.monthrange(year, month)[1] + 1)
            for hour in (0, 6, 12, 18)]


class MonthlySamples:
    """Read-only complete-month arrays; hashes at activation, stats at reads.

    File metadata checks detect ordinary changes, not adversarial replacement
    with restored metadata. Explicit verify_full rehashes every array.
    """

    @property
    def numpy_version(self):
        return np.__version__

    def __init__(self, path, dataset_sha256=None, grid=None, levels=None):
        self.path = Path(path).absolute()
        self._files = {}
        try:
            if self.path.stat().st_size > 5 * 1024 * 1024:
                raise ValueError("manifest too large")
            self._manifest_identity = identity(self.path)
            data = self.path.read_bytes()
            self.bundle_sha256 = hashlib.sha256(data).hexdigest()
            manifest = json.loads(data)
            self.schema = manifest['schema']
            self.years = manifest['years']
            self.weighting = 'gaussian-area-equal-times'
            if self.schema == 'balloon.wind-samples/1' and dataset_sha256 is None:
                if (len(self.years) != 2 or any(type(y) is not int for y in self.years)
                        or not 1940 <= self.years[0] <= self.years[1] <= 2100
                        or self.years[1]-self.years[0] > 9):
                    raise ValueError('year range')
                if manifest['hours_utc'] != [0, 6, 12, 18] or manifest['date_convention'] != 'UTC':
                    raise ValueError('UTC support')
                self.weighting = manifest['weighting']
                if self.weighting not in ('gaussian-area-equal-times', 'spherical-area-equal-times'):
                    raise ValueError('spatial weights')
                if manifest['provider'] not in ('JRA-3Q', 'ERA5') or not isinstance(manifest['label'], str):
                    raise ValueError('provider')
                grid = [{**r, 'gauss_weight': r['weight']} for r in manifest['grid']]
                levels = manifest['levels']
                if not 1 <= len(grid) <= 2000 or not 1 <= len(levels) <= 45:
                    raise ValueError('dimensions')
                if len({r['cell_id'] for r in grid}) != len(grid) or len({r['level_id'] for r in levels}) != len(levels):
                    raise ValueError('duplicated ID')
                if len({(r['lat'],r['lon']) for r in grid}) != len(grid) or len({r['level_hpa'] for r in levels}) != len(levels):
                    raise ValueError('duplicated coordinates')
                if any(type(r['cell_id']) is not int or not -90 <= r['lat'] <= 90 or not -180 <= r['lon'] <= 180
                       or not math.isfinite(r['weight']) or r['weight'] <= 0 for r in grid):
                    raise ValueError('grid values')
                if any(type(r['level_id']) is not int or not 1 <= r['level_hpa'] <= 1000 for r in levels):
                    raise ValueError('level values')
            else:
                if (self.schema != SCHEMA or manifest['dataset_sha256'] != dataset_sha256
                        or self.years != [2016, 2025]):
                    raise ValueError("source binding")
                if manifest['grid'] != [{k: r[k] for k in ('cell_id', 'lat', 'lon')} for r in grid]:
                    raise ValueError("grid binding")
                if manifest['levels'] != [{k: r[k] for k in ('level_id', 'level_hpa')} for r in levels]:
                    raise ValueError("level binding")
            self.manifest = manifest
            self.grid, self.levels = grid, levels
            self.months = {}
            if not isinstance(manifest['months'], list) or len(manifest['months']) > 12:
                raise ValueError("month list")
            for item in manifest['months']:
                m = item['month']
                if type(m) is not int or not 1 <= m <= 12 or m in self.months:
                    raise ValueError("month identity")
                times = expected_times(m, self.years)
                if item['times_utc'] != times:
                    raise ValueError("incomplete or duplicated original UTC times")
                shape = (len(times), len(levels), len(grid))
                files = {}
                for component in ('u', 'v'):
                    entry = item[component]
                    relative = Path(entry['file'])
                    if relative.is_absolute() or '..' in relative.parts:
                        raise ValueError("array path")
                    file = (self.path.parent / relative).resolve(strict=True)
                    if not file.is_relative_to(self.path.parent.resolve()) or not file.is_file():
                        raise ValueError("array outside bundle")
                    if file in self._files:
                        raise ValueError("reused component file")
                    if not 0 < entry['bytes'] <= 550 * 1024 * 1024 or file.stat().st_size != entry['bytes']:
                        raise ValueError("array byte bound")
                    before = identity(file)
                    if digest(file) != entry['sha256']:
                        raise ValueError("array digest")
                    array = np.load(file, allow_pickle=False, mmap_mode='r')
                    if not isinstance(array, np.ndarray) or array.shape != shape or array.dtype != np.dtype('float32'):
                        if hasattr(array, 'close'):
                            array.close()
                        raise ValueError("array shape or type")
                    # Check one pressure at a time; no silent NaN deletion.
                    if any(not np.isfinite(array[:, l, :]).all() for l in range(len(levels))):
                        raise ValueError("missing or nonfinite wind")
                    del array
                    if identity(file) != before:
                        raise ValueError("array changed while registering")
                    self._files[file] = (before, entry['sha256'])
                    files[component] = file
                self.months[m] = {'times': times, 'files': files}
            if not self.months:
                raise ValueError("no complete months")
            self.assert_current()
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise ClimateError('CLIMATE_SAMPLES', '原標本束の支持・出典・内容を確認できません。部分的な分位図は作りません。') from exc

    def assert_current(self):
        try:
            if identity(self.path) != self._manifest_identity or any(identity(p) != item[0] for p, item in self._files.items()):
                raise ValueError('changed')
        except (OSError, ValueError) as exc:
            raise ClimateError('CLIMATE_SOURCE_CHANGED', '原標本束が登録時から変わりました。起動時に再登録してください。') from exc

    def verify_full(self):
        self.assert_current()
        try:
            if digest(self.path) != self.bundle_sha256 or any(digest(p) != item[1] for p, item in self._files.items()):
                raise ValueError('digest')
        except (OSError, ValueError) as exc:
            raise ClimateError('CLIMATE_SOURCE_CHANGED', '原標本束のSHA256が一致しません。') from exc
        self.assert_current()
        return {'bundle_sha256': self.bundle_sha256, 'months': sorted(self.months), 'array_count': len(self._files)}

    def profiles(self, grid, levels, hours):
        try:
            return self._profiles(grid, levels, hours)
        except ClimateError:
            raise
        except (OSError, ValueError, EOFError) as exc:
            self.assert_current()
            raise ClimateError('CLIMATE_SAMPLES', '原標本の読取・分位集計に失敗しました。固定結果は更新しません。') from exc

    def _profiles(self, grid, levels, hours):
        self.assert_current()
        hours = tuple(hours or (0, 6, 12, 18))
        cell_indices = [next(i for i, c in enumerate(self.grid) if c['cell_id'] == r['cell_id']) for r in grid]
        weights = np.array([r['gauss_weight'] for r in grid], dtype=np.float64)
        level_indices = [next(i for i, l in enumerate(self.levels) if l['level_id'] == r['level_id']) for r in levels]
        result = {'schema': PROFILE_SCHEMA, 'method': 'inverted_cdf',
                  'weighting': self.weighting, 'date_convention': 'UTC',
                  'population': {'years_fixed': self.years, 'hours_utc': list(hours),
                                 'selected_cell_ids': [r['cell_id'] for r in grid],
                                 'level_ids': [r['level_id'] for r in levels]},
                  'months': [], 'provenance': {'bundle_sha256': self.bundle_sha256,
                      'manifest_schema': self.schema, 'numpy_version': np.__version__}}
        for month in range(1, 13):
            times = expected_times(month, self.years)
            expected = len(times) * len(hours) // 4
            item = {'month': month, 'expected_time_count': expected}
            if month not in self.months:
                result['months'].append({**item, 'available': False, 'reason': 'month_not_acquired'})
                continue
            subset = np.array([i for i, t in enumerate(times) if int(t[11:13]) in hours])
            half = np.array([int(times[i][8:10]) <= 15 for i in subset])
            counts = [int(half.sum()), int((~half).sum())]
            w = np.tile(weights, len(subset))
            wh = [np.tile(weights, count) for count in counts]
            files = self.months[month]['files']
            u = np.load(files['u'], mmap_mode='r', allow_pickle=False)
            v = np.load(files['v'], mmap_mode='r', allow_pickle=False)
            rows = []
            for l, li in zip(levels, level_indices):
                a = u[subset, li, :][:, cell_indices].astype(np.float64)
                b = v[subset, li, :][:, cell_indices].astype(np.float64)
                speed = np.hypot(a, b)
                p10, p90 = np.quantile(speed.ravel(), [.1, .9], method='inverted_cdf', weights=w)
                medians = [float(np.quantile(speed[mask].ravel(), .5, method='inverted_cdf', weights=weight))
                           for mask, weight in zip((half, ~half), wh)]
                rows.append({'level_id': l['level_id'], 'p10': float(p10), 'p90': float(p90), 'half_medians': medians})
            del u, v
            result['months'].append({**item, 'available': True, 'time_count': len(subset),
                                     'half_time_counts': counts, 'cell_count': len(grid),
                                     'sample_count': len(subset) * len(grid), 'rows': rows})
            self.assert_current()
        return result
