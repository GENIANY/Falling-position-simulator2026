"""Annual-only calendar and pressure-cache counterexamples on original samples."""
import calendar
from copy import deepcopy
from datetime import date, timedelta
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from backend.climate.archive import WindArchiveSource
from backend.climate.contracts import Bounds, ClimateError, ClimateQuery
from backend.climate.periods import annual_quarters, periods
from test_climate_archive import archive_fixture


class QuarterCalendarTests(unittest.TestCase):
    def test_disjoint_complete_days_and_half_nesting_including_leap_boundaries(self):
        for years in ((2019, 2020), (2000, 2000), (2100, 2100), (2016, 2025)):
            bins = annual_quarters(2, years)
            self.assertEqual([p['timebin_id'] for p in bins], list(range(48)))
            self.assertTrue(all('member_timebin_ids' not in p for p in bins))
            counts = [0] * 48
            day = date(years[0], 1, 1)
            while day <= date(years[1], 12, 31):
                matches = [p for p in bins if p['month'] == day.month
                           and p['start_day'] <= day.day <= p['end_day_max']]
                self.assertEqual(len(matches), 1, day)
                period = matches[0]
                counts[period['timebin_id']] += 1
                self.assertEqual(period['parent_timebin_id'], (day.month-1)*2 + (day.day > 15))
                day += timedelta(days=1)
            self.assertEqual(counts, [p['n_days_total'] for p in bins])
            self.assertEqual([n*2 for n in counts], [p['n_analyses_expected'] for p in bins])
            for half in periods('half', 2, years):
                nested = [p for p in bins if p['parent_timebin_id'] == half['timebin_id']]
                self.assertEqual(sum(p['n_analyses_expected'] for p in nested), half['n_analyses_expected'])
            feb_end = bins[7]
            ends = [calendar.monthrange(y, 2)[1] for y in range(years[0], years[1]+1)]
            self.assertEqual((feb_end['end_day_min'], feb_end['end_day_max']), (min(ends), max(ends)))

    def test_quarter_is_not_a_query_or_shared_period_grain(self):
        with self.assertRaises(ValueError):
            periods('quarter')
        with self.assertRaises(ClimateError):
            ClimateQuery.from_mapping({'source_id':'example', 'level_id':0, 'grain':'quarter'})


class ArchiveInteractionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='climate-interaction-')
        self.root = Path(self.temp.name)
        self.path = archive_fixture(self.root)
        # Different levels, signs, nonuniform weights and hours rule out a mean
        # copied from another pressure, or a vector norm used as scalar speed.
        manifest = json.loads(self.path.read_bytes())
        rng = np.random.default_rng(580)
        for month in manifest['months']:
            for component in ('u', 'v'):
                p = self.root / month[component]['file']
                a = np.load(p)
                a = (rng.normal(size=a.shape) * (1 + month['month'])
                     + np.array([0., 10.])[None, :, None]).astype('float32')
                np.save(p, a, allow_pickle=False)
                month[component].update(bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
        self.path.write_text(json.dumps(manifest), encoding='utf8')
        self.manifest = manifest
        self.source = WindArchiveSource(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def query(self, level=0, hours=None, bounds=None):
        return ClimateQuery(self.source.source_id, level, bounds, hours_utc=hours)

    def test_all_48_raw_quarters_match_independent_scalar_weighting_and_utc_masks(self):
        for hours in (None, [0], [6, 18]):
            result = self.source.query(self.query(hours=hours, bounds=Bounds(141, 141, 40, 41)))
            quarters = result['annual_quarters']
            self.assertEqual(quarters['schema'], 'climate-annual-quarters/1')
            self.assertEqual(quarters['calendar_definition']['version'], 'utc-half-nested-quarters/1')
            self.assertEqual(len(quarters['annual']), 96)
            self.assertNotIn('spatial_rows', quarters)
            self.assertEqual(set(result['summaries_by_grain']), {'month', 'season'})
            self.assertEqual(len(result['population']['timebins']), 24)
            selected_hours = hours or [0, 6, 12, 18]
            for month in self.manifest['months']:
                u = np.load(self.root / month['u']['file'])
                v = np.load(self.root / month['v']['file'])
                for quarter, (lo, hi) in enumerate(((1, 7), (8, 15), (16, 22), (23, 31))):
                    take = [i for i, t in enumerate(month['times_utc'])
                            if lo <= int(t[8:10]) <= hi and int(t[11:13]) in selected_hours]
                    pid = (month['month']-1)*4 + quarter
                    for li in (0, 1):
                        row = next(r for r in quarters['annual'] if r['timebin_id']==pid and r['level_id']==li)
                        cell_means = []
                        for ci in (1, 3):
                            a = [float(u[i, li, ci]) for i in take]
                            b = [float(v[i, li, ci]) for i in take]
                            cell_means.append([math.fsum(a)/len(take), math.fsum(b)/len(take),
                                               math.fsum(math.hypot(x, y) for x, y in zip(a, b))/len(take)])
                        expected = [(cell_means[0][i]*2 + cell_means[1][i]*4)/6 for i in range(3)]
                        for key, value in zip(('mean_u', 'mean_v', 'mean_speed'), expected):
                            self.assertAlmostEqual(row[key], value, places=12)
                        self.assertAlmostEqual(row['pooled_constancy'], math.hypot(*expected[:2])/expected[2], places=12)
                        self.assertAlmostEqual(row['from_deg'], (math.degrees(math.atan2(*expected[:2]))+180)%360, places=12)
                        self.assertAlmostEqual(row['spatial_mean_speed_range'], abs(cell_means[0][2]-cell_means[1][2]), places=12)
                        self.assertEqual(row['time_count'], len(take))
                        self.assertEqual(row['valid_time_count'], quarters['timebins'][pid]['n_analyses_expected'])
                        self.assertEqual(row['cell_count'], 2)
                        self.assertEqual(row['missing_time_count'], 0)

    def test_pressure_switch_reuses_all_annual_profiles_but_reads_one_rose_column(self):
        first = self.source.query(self.query())
        with patch.object(self.source, '_moments', side_effect=AssertionError('no moment rebuild')), \
             patch.object(self.source, '_annual', side_effect=AssertionError('no annual rebuild')), \
             patch.object(self.source._samples, 'profiles', side_effect=AssertionError('no quantile rebuild')), \
             patch.object(self.source, '_rose_counts', wraps=self.source._rose_counts) as rose:
            other = self.source.query(self.query(level=1))
            self.assertEqual(rose.call_count, 1)
        for key in ('annual', 'monthly_profiles', 'population'):
            self.assertEqual(first[key], other[key])
        self.assertEqual(first['annual_quarters']['annual'], other['annual_quarters']['annual'])
        self.assertNotEqual(first['spatial']['rows'], other['spatial']['rows'])
        self.assertNotEqual(first['wind_rose']['rows'], other['wind_rose']['rows'])
        self.assertNotEqual(first['display_scales']['selected_level_cell_mean_speed_max'],
                            other['display_scales']['selected_level_cell_mean_speed_max'])

    def test_returned_nested_mutations_cannot_poison_cache_or_descriptor(self):
        result = self.source.query(self.query())
        original = deepcopy(result)
        result['annual'][0]['mean_speed'] = -99
        result['monthly_profiles']['months'][0]['rows'][0]['half_medians'][0] = -99
        result['summaries_by_grain']['month']['timebins'][0]['member_timebin_ids'].clear()
        result['summaries_by_grain']['season']['annual'].clear()
        result['annual_quarters']['annual'].clear()
        result['annual_quarters']['timebins'].clear()
        result['annual_quarters']['calendar_definition']['version'] = 'poison'
        result['source']['native_grid'][0]['lat'] = -99
        result['wind_rose']['rows'].clear()
        self.assertEqual(self.source.query(self.query()), original)

    def test_hours_region_and_lru_eviction_do_not_reuse_other_population(self):
        full = self.source.query(self.query())
        with patch.object(self.source, '_moments', wraps=self.source._moments) as moments:
            for hour in (0, 6, 12, 18):
                subset = self.source.query(self.query(hours=[hour]))
                self.assertEqual(subset['annual_quarters']['annual'][0]['time_count'], 7)
                self.assertEqual(subset['monthly_profiles']['population']['hours_utc'], [hour])
            region = self.source.query(self.query(hours=[18], bounds=Bounds(141,141,40,41)))
            self.assertEqual(region['annual_quarters']['annual'][0]['cell_count'], 2)
            self.assertEqual(len(self.source._cache), 4)
            restored = self.source.query(self.query())
            self.assertEqual(moments.call_count, 6)
        self.assertEqual(full, restored)

    def test_changed_source_or_adapter_is_rejected_even_after_cache_hit(self):
        self.source.query(self.query())
        with patch('backend.climate.archive.adapter_source_snapshot', return_value={'changed':True}):
            with self.assertRaises(ClimateError) as error:
                self.source.query(self.query())
            self.assertEqual(error.exception.code, 'CLIMATE_ADAPTER_CHANGED')
        self.path.write_bytes(self.path.read_bytes() + b'\n')
        with self.assertRaises(ClimateError) as error:
            self.source.query(self.query())
        self.assertEqual(error.exception.code, 'CLIMATE_SOURCE_CHANGED')
        new_source = WindArchiveSource(self.path)
        self.assertNotEqual(new_source.source_id, self.source.source_id)
        with self.assertRaises(ClimateError):
            new_source.query(self.query())
        self.assertEqual(new_source.query(ClimateQuery(new_source.source_id,0))['annual_quarters']['annual'][0]['time_count'],28)

    def test_failed_population_build_is_not_installed_as_partial_cache(self):
        with patch.object(self.source._samples, 'profiles', side_effect=ClimateError('CLIMATE_SAMPLES','fixture failure')):
            with self.assertRaises(ClimateError):
                self.source.query(self.query())
        self.assertFalse(self.source._cache)
        self.assertEqual(len(self.source.query(self.query())['annual_quarters']['annual']),96)


if __name__ == '__main__':
    unittest.main()
