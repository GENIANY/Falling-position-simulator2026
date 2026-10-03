"""Raw-sample quantiles: populations, weighting, persistence and corrupt input."""
import calendar
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from test_climate import create_fixture
from test_climate_periods import add_extensions
from backend.climate.contracts import Bounds, ClimateError, ClimateQuery
from backend.climate.source import ClimateSource
from backend.climate.service import ClimateService


def make_samples(root, source):
    # Independent timestamp enumeration, including the three leap Februaries.
    times = [f'{y:04d}-02-{d:02d}T{h:02d}:00:00Z' for y in range(2016, 2026)
             for d in range(1, calendar.monthrange(y, 2)[1]+1) for h in (0, 6, 12, 18)]
    rng = np.random.default_rng(570)
    u = rng.integers(-30, 50, (len(times), 2, 3)).astype('float32')
    v = rng.integers(-20, 20, u.shape).astype('float32')
    month = {'month': 2, 'times_utc': times}
    for name, a in [('u', u), ('v', v)]:
        f = root / (name+'.npy'); np.save(f, a, allow_pickle=False)
        month[name] = {'file': f.name, 'bytes': f.stat().st_size,
                       'sha256': hashlib.sha256(f.read_bytes()).hexdigest()}
    desc = source.descriptor()
    manifest = {'schema': 'balloon.climate.raw-months/1', 'years': [2016, 2025],
                'dataset_sha256': source.dataset_sha256,
                'grid': [{k: c[k] for k in ('cell_id', 'lat', 'lon')} for c in desc['native_grid']],
                'levels': [{k: l[k] for k in ('level_id', 'level_hpa')} for l in desc['levels']],
                'months': [month]}
    path = root / 'manifest.json'; path.write_text(json.dumps(manifest), encoding='utf-8')
    return path, manifest, u, v, times


def independent_cdf(values, weights, probability):
    pairs = sorted(zip(values, weights))
    target = sum(weights) * probability
    cumulative = 0
    for value, weight in pairs:
        cumulative += weight
        if cumulative >= target:
            return value
    raise AssertionError('empty CDF')


class RawProfilesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='climate-raw-')
        self.root = Path(self.temp.name)
        self.db = self.root / 'input.duckdb'; create_fixture(self.db); add_extensions(self.db)
        self.base = ClimateSource(self.db)
        self.path, self.manifest, self.u, self.v, self.times = make_samples(self.root, self.base)
        self.source = ClimateSource(self.db, samples_path=self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_monthly_width_and_half_medians_match_independent_weighted_sort(self):
        query = ClimateQuery(self.source.source_id, 0)
        p = self.source.query(query)['monthly_profiles']
        self.assertEqual(len(p['months']), 12)
        self.assertEqual([r['month'] for r in p['months'] if r['available']], [2])
        feb = p['months'][1]
        self.assertEqual(feb['time_count'], 1132)
        self.assertEqual(feb['half_time_counts'], [600, 532])
        self.assertEqual(feb['sample_count'], 1132*3)
        speed = np.hypot(self.u[:, 0, :].astype(float), self.v[:, 0, :].astype(float))
        row = feb['rows'][0]
        for key, q in [('p10', .1), ('p90', .9)]:
            self.assertEqual(row[key], independent_cdf(speed.ravel().tolist(), [1, 3, 2]*1132, q))
        for half, value in enumerate(row['half_medians']):
            chosen = [i for i, t in enumerate(self.times) if (int(t[8:10])<=15) == (half==0)]
            self.assertEqual(value, independent_cdf(speed[chosen].ravel().tolist(), [1, 3, 2]*len(chosen), .5))
        self.assertNotEqual(self.base.source_id, self.source.source_id)

    def test_region_and_hour_masks_use_original_records_and_pressure_reuses_profile(self):
        q = ClimateQuery(self.source.source_id, 0, Bounds(140,141,40,41), hours_utc=[6])
        with patch.object(self.source._samples, 'profiles', wraps=self.source._samples.profiles) as compute:
            a = self.source.query(q)
            b = self.source.query(ClimateQuery(self.source.source_id, 1, q.bounds, hours_utc=[6]))
            self.assertEqual(compute.call_count, 1)
        p = a['monthly_profiles']; feb = p['months'][1]
        self.assertEqual(feb['time_count'], 283)
        self.assertEqual(feb['cell_count'], 2)
        chosen = [i for i,t in enumerate(self.times) if t[11:13]=='06']
        s = np.hypot(self.u[chosen,0,:2].astype(float), self.v[chosen,0,:2].astype(float))
        self.assertEqual(feb['rows'][0]['p90'], independent_cdf(s.ravel().tolist(), [1,3]*283, .9))
        self.assertEqual(a['monthly_profiles'], b['monthly_profiles'])
        # Returned data must not mutate a cached fixed profile.
        a['monthly_profiles']['months'][1]['rows'][0]['p10'] = -1
        self.assertGreaterEqual(self.source.query(q)['monthly_profiles']['months'][1]['rows'][0]['p10'], 0)

    def test_incomplete_timestamp_binding_nan_and_changed_files_fail(self):
        self.manifest['months'][0]['times_utc'][1] = self.times[0]
        self.path.write_text(json.dumps(self.manifest), encoding='utf-8')
        with self.assertRaises(ClimateError): ClimateSource(self.db, samples_path=self.path)
        with self.assertRaises(ClimateError): self.source.descriptor()
        self.manifest['months'][0]['times_utc'] = self.times
        self.u[0,0,0] = np.nan
        np.save(self.root/'u.npy', self.u, allow_pickle=False)
        self.manifest['months'][0]['u']['sha256'] = hashlib.sha256((self.root/'u.npy').read_bytes()).hexdigest()
        self.path.write_text(json.dumps(self.manifest), encoding='utf-8')
        with self.assertRaises(ClimateError): ClimateSource(self.db, samples_path=self.path)

    def test_saved_profiles_read_back_without_db_or_samples(self):
        service = ClimateService(self.root/'store', self.db, samples_path=self.path)
        sid = service.sources()['sources'][0]['source_id']
        result = service.create_analysis({'client_request_id':'raw-feb', 'query':ClimateQuery(sid,0).as_dict()})
        recovered = ClimateService(self.root/'store').get_analysis(result['analysis_id'])
        self.assertEqual(result, recovered)
        self.assertEqual(service.verify_source()['raw_samples']['months'], [2])


if __name__ == '__main__':
    unittest.main()
