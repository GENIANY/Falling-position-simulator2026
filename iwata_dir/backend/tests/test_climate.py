"""Finite counterexamples for summary meanings and source identity.

The optional supplied-database check is separate from offline tests. No timing
assertions or operational performance claim is made by this test module.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import duckdb
from backend.climate.contracts import Bounds, ClimateError, ClimateQuery
from backend.climate.source import ClimateSource, adapter_source_snapshot
from backend.climate.statistics import combine_cells, utc_half_months, vector_summary


def create_fixture(path):
    """Small independent summary fixture; not a copy of source observations."""
    with duckdb.connect(str(path)) as con:
        con.execute('CREATE TABLE meta_dataset(key VARCHAR,value VARCHAR,note VARCHAR)')
        con.executemany('INSERT INTO meta_dataset VALUES (?,?,NULL)', list({
            'years': '2016-2025', 'region': 'hokkaido', 'source_product': 'anl_p',
            'bin_scheme': 'half', 'date_convention': 'utc'}.items()))
        con.execute('CREATE TABLE meta_column(table_name VARCHAR,column_name VARCHAR,units VARCHAR)')
        con.executemany('INSERT INTO meta_column VALUES (?,?,?)', [('fact_wind',k,'m s-1') for k in ('u_mean','v_mean','speed_mean')])
        con.execute('CREATE TABLE dim_grid(cell_id INTEGER,lat DOUBLE,lon DOUBLE,gauss_weight DOUBLE)')
        con.executemany('INSERT INTO dim_grid VALUES (?,?,?,?)', [(0,40.,140.,1.),(1,41.,141.,3.),(2,42.,142.,2.)])
        con.execute('CREATE TABLE dim_level(level_id INTEGER,level_hpa DOUBLE,isa_alt_m DOUBLE,alt_geom_mean_m DOUBLE,alt_geom_min_m DOUBLE,alt_geom_max_m DOUBLE)')
        con.executemany('INSERT INTO dim_level VALUES (?,?,?,?,?,?)', [(0,300.,9000.,9100.,8900.,9300.),(1,1000.,100.,110.,80.,130.)])
        con.execute('CREATE TABLE dim_timebin(timebin_id INTEGER,month INTEGER,bin INTEGER,start_day INTEGER,end_day_min INTEGER,end_day_max INTEGER,n_days_total INTEGER,n_analyses_expected INTEGER)')
        # Calendar counts are an independently enumerated 2016-2025 fixture.
        ends = [31,28,31,30,31,30,31,31,30,31,30,31]
        bins = []
        for month, end in enumerate(ends, 1):
            bins.append(((month-1)*2,month,1,1,15,15,150,600))
            days = (end-15)*10 + (3 if month == 2 else 0)
            bins.append(((month-1)*2+1,month,2,16,end,29 if month == 2 else end,days,days*4))
        con.executemany('INSERT INTO dim_timebin VALUES (?,?,?,?,?,?,?,?)', bins)
        con.execute('CREATE TABLE fact_wind(timebin_id INTEGER,level_id INTEGER,cell_id INTEGER,n INTEGER,u_mean FLOAT,v_mean FLOAT,speed_mean FLOAT)')
        rows = []
        for timebin in bins:
            for level, factor in [(0,2.),(1,1.)]:
                for cell, u, v, s in [(0,10.,0.,10.),(1,-10.,0.,10.),(2,0.,6.,6.)]:
                    rows.append((timebin[0],level,cell,timebin[-1],u*factor,v*factor,s*factor))
        con.executemany('INSERT INTO fact_wind VALUES (?,?,?,?,?,?,?)', rows)


class StatisticsTests(unittest.TestCase):
    def test_optional_rose_cell_id_preserves_legacy_query_bytes_and_rejects_non_ids(self):
        old = {'source_id':'x','level_id':0,'bounds':None,'grain':'half'}
        canonical = lambda value: json.dumps(value,sort_keys=True,separators=(',',':'))
        expected = '{"bounds":null,"grain":"half","level_id":0,"source_id":"x"}'
        for extra in ({},{'rose_cell_id':None}):
            self.assertEqual(canonical(ClimateQuery.from_mapping({**old,**extra}).as_dict()),expected)
        for value in (0,37):
            query=ClimateQuery.from_mapping({**old,'rose_cell_id':value})
            self.assertEqual(query.rose_cell_id,value)
            self.assertEqual(query.as_dict(),{**old,'rose_cell_id':value})
        for value in (True,False,-1,1.0,1.5,'1',[],{},float('nan'),float('inf')):
            with self.subTest(value=value):
                for create in (lambda:ClimateQuery('x',0,rose_cell_id=value),
                               lambda:ClimateQuery.from_mapping({**old,'rose_cell_id':value})):
                    with self.assertRaises(ClimateError) as ctx:create()
                    self.assertEqual(ctx.exception.code,'CLIMATE_INPUT')

    def test_pooling_is_not_mean_local_constancy_or_angle_mean(self):
        rows = [dict(mean_u=10.,mean_v=0.,mean_speed=10.,weight=1.,time_count=600),
                dict(mean_u=-10.,mean_v=0.,mean_speed=10.,weight=1.,time_count=600)]
        pooled = combine_cells(rows)
        self.assertEqual(pooled['pooled_constancy'],0.)
        self.assertIsNone(pooled['from_deg'])
        self.assertEqual(vector_summary(10.,0.,10.)['constancy'],1.)
        winds = []
        for direction in (359.,1.):
            radians=math.radians(direction)
            winds.append(dict(mean_u=-math.sin(radians),mean_v=-math.cos(radians),mean_speed=1.,weight=1.,time_count=600))
        wrapped = combine_cells(winds)
        self.assertAlmostEqual(wrapped['from_deg'] % 360,0.,places=10)
        self.assertGreater(wrapped['pooled_constancy'],.99)

    def test_zero_undefined_invalid_and_unequal_support(self):
        self.assertEqual(vector_summary(0.,0.,0.),dict(mean_u=0.,mean_v=0.,mean_speed=0.,constancy=None,from_deg=None))
        for values in [(1.,0.,0.),(2.,0.,1.),(0.,0.,-1.),(math.nan,0.,1.)]:
            with self.subTest(values=values), self.assertRaises(ClimateError):
                vector_summary(*values)
        base=dict(mean_u=1.,mean_v=0.,mean_speed=1.,weight=1.,time_count=600)
        for change in [dict(weight=0.),dict(weight=-1.),dict(weight=math.nan),dict(time_count=599),dict(time_count=True)]:
            with self.subTest(change=change),self.assertRaises(ClimateError):
                combine_cells([base,{**base,**change}])

    def test_utc_support_is_not_jst_calendar_or_even_month_partition(self):
        bins=utc_half_months()
        self.assertEqual(sum(r['n_analyses_expected'] for r in bins),14612)
        self.assertEqual(bins[3],dict(timebin_id=3,month=2,bin=2,start_day=16,end_day_min=28,end_day_max=29,n_days_total=133,n_analyses_expected=532))
        self.assertEqual(bins[0]['end_day_max'],15)
        for field,value in [('years',[2020,2025]),('hours',[0]),('quantiles',[.1,.9]),('sql','select 1')]:
            with self.subTest(field=field),self.assertRaises(ClimateError) as ctx:
                ClimateQuery.from_mapping(dict(source_id='x',level_id=0,**{field:value}))
            self.assertEqual(ctx.exception.code,'CLIMATE_UNSUPPORTED')
        with self.assertRaises(ClimateError):
            ClimateQuery('x',0,grain='month')


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='climate-fixture-')
        self.path=Path(self.temp.name)/'fixture.duckdb'
        create_fixture(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def mutate(self,sql):
        with duckdb.connect(str(self.path)) as con:
            con.execute(sql)

    def test_summary_database_rejects_explicit_wind_rose_point(self):
        source=ClimateSource(self.path)
        self.assertFalse(source.descriptor()['capabilities'].get('wind_rose_point_select',False))
        # Even an existing native ID cannot invent per-point rose observations.
        for cell_id in (0,2,999):
            with self.subTest(cell_id=cell_id),self.assertRaises(ClimateError) as ctx:
                source.query(ClimateQuery(source.source_id,0,rose_cell_id=cell_id))
            self.assertEqual(ctx.exception.code,'CLIMATE_UNSUPPORTED')

    def test_sql_weight_selection_and_pressure_shapes_match_independent_aggregation(self):
        source=ClimateSource(self.path)
        before=source.verify_full()
        query=ClimateQuery(source.source_id,1,Bounds(140,141,40,41))
        response=source.query(query)
        self.assertEqual(len(response['annual']),48)
        self.assertEqual(len(response['spatial']['rows']),48)
        self.assertEqual(response['population']['selected_cell_ids'],[0,1])
        expected=combine_cells([dict(mean_u=10.,mean_v=0.,mean_speed=10.,weight=1.,time_count=600),
                                dict(mean_u=-10.,mean_v=0.,mean_speed=10.,weight=3.,time_count=600)])
        row=next(r for r in response['annual'] if r['timebin_id']==0 and r['level_id']==1)
        for key in ('mean_u','mean_v','mean_speed','pooled_constancy','time_count','cell_count','spatial_mean_speed_range'):
            self.assertAlmostEqual(row[key],expected[key])
        self.assertEqual(response['display_scales']['all_level_cell_mean_speed_max'],20.)
        self.assertEqual(response['display_scales']['selected_level_cell_mean_speed_max'],10.)
        self.assertEqual(response['source']['capabilities']['native_hours_utc'],[0,6,12,18])
        # Boundary equality includes a native center; a narrow gap does not invent interpolated cells.
        single=source.query(ClimateQuery(source.source_id,0,Bounds(141,141,41,41)))
        self.assertEqual(single['population']['selected_cell_ids'],[1])
        self.assertEqual(len(single['spatial']['rows']),24)
        self.assertEqual(source.verify_full(),before)
        self.assertEqual(len(single['source']['native_grid']),3)
        # Caller mutation must not poison the internal region cache or future result hashes.
        response['annual'][0]['mean_speed']=-100.
        self.assertGreater(source.query(query)['annual'][0]['mean_speed'],0.)
        self.assertEqual(adapter_source_snapshot(),source.descriptor()['source_code'])

    def test_unsupported_empty_region_level_source_rejected(self):
        source=ClimateSource(self.path)
        for query,code in [(ClimateQuery(source.source_id,1,Bounds(140.1,140.9,40,42)),'CLIMATE_EMPTY_REGION'),
                           (ClimateQuery(source.source_id,1,Bounds(139,142,40,42)),'CLIMATE_BOUNDS'),
                           (ClimateQuery(source.source_id,99),'CLIMATE_SUPPORT'),
                           (ClimateQuery('other',1),'CLIMATE_SOURCE_CHANGED')]:
            with self.subTest(code=code),self.assertRaises(ClimateError) as ctx:
                source.query(query)
            self.assertEqual(ctx.exception.code,code)

    def test_read_only_external_access_and_resource_configuration(self):
        source=ClimateSource(self.path)
        with source._connection() as con:
            self.assertEqual(con.execute("SELECT current_setting('enable_external_access'),current_setting('threads'),current_setting('memory_limit'),current_setting('autoload_known_extensions'),current_setting('autoinstall_known_extensions')").fetchone(),(False,1,'122.0 MiB',False,False))
            with self.assertRaises(duckdb.Error):
                con.execute('CREATE TABLE forbidden(i INTEGER)')
            with self.assertRaises(duckdb.Error):
                con.execute("SELECT * FROM read_csv('no-file-is-read.csv')")

    def test_same_path_replacement_missing_and_expected_digest(self):
        source=ClimateSource(self.path)
        other=Path(self.temp.name)/'replacement.duckdb'
        create_fixture(other)
        os.replace(other,self.path)
        with self.assertRaises(ClimateError) as ctx:
            source.query(ClimateQuery(source.source_id,0))
        self.assertEqual(ctx.exception.code,'CLIMATE_SOURCE_CHANGED')
        with self.assertRaises(ClimateError):
            ClimateSource(self.path,expected_sha256='0'*64)
        new=ClimateSource(self.path)
        self.path.unlink()
        with self.assertRaises(ClimateError):
            new.descriptor()

    def test_adapter_change_and_mid_query_source_change_do_not_publish_results(self):
        source=ClimateSource(self.path)
        with patch('backend.climate.source.adapter_source_snapshot',return_value={'files':{},'sha256':'changed'}):
            with self.assertRaises(ClimateError) as ctx:
                source.query(ClimateQuery(source.source_id,0))
            self.assertEqual(ctx.exception.code,'CLIMATE_ADAPTER_CHANGED')
        # An observed stat change at the read boundary invalidates even a cached query.
        source.query(ClimateQuery(source.source_id,0))
        identity=source._identity
        calls=0
        def replaced(_path):
            nonlocal calls
            calls+=1
            return identity if calls<3 else (*identity[:-1],identity[-1]+1)
        with patch('backend.climate.source._identity',side_effect=replaced):
            with self.assertRaises(ClimateError) as ctx:
                source.query(ClimateQuery(source.source_id,1))
            self.assertEqual(ctx.exception.code,'CLIMATE_SOURCE_CHANGED')

    def test_missing_moments_unequal_counts_duplicates_and_schema_are_not_silently_dropped(self):
        mutations=["UPDATE fact_wind SET n=599 WHERE timebin_id=0 AND cell_id=1",
                   "UPDATE fact_wind SET speed_mean=NULL WHERE timebin_id=0 AND cell_id=1",
                   "UPDATE fact_wind SET u_mean='NaN' WHERE timebin_id=0 AND cell_id=1",
                   "UPDATE fact_wind SET cell_id=999 WHERE timebin_id=0 AND cell_id=1",
                   "DELETE FROM fact_wind WHERE timebin_id=0 AND cell_id=1",
                   "UPDATE fact_wind SET cell_id=0 WHERE timebin_id=0 AND cell_id=1",
                   "UPDATE dim_grid SET gauss_weight=0 WHERE cell_id=1",
                   "UPDATE dim_timebin SET n_analyses_expected=531 WHERE timebin_id=3",
                   "UPDATE meta_dataset SET value='jst' WHERE key='date_convention'",
                   "UPDATE meta_column SET units='kt' WHERE column_name='speed_mean'",
                   "ALTER TABLE fact_wind RENAME TO actual_wind; CREATE VIEW fact_wind AS SELECT * FROM actual_wind"]
        for index,mutation in enumerate(mutations):
            path=Path(self.temp.name)/f'invalid-{index}.duckdb'
            create_fixture(path)
            with duckdb.connect(str(path)) as con:
                con.execute(mutation)
            with self.subTest(mutation=mutation),self.assertRaises(ClimateError):
                ClimateSource(path)


@unittest.skipUnless(os.environ.get('BALLOON_TEST_CLIMATE_DB'),'Supplied DB read-only check is explicitly opt-in.')
class SuppliedDatabaseTests(unittest.TestCase):
    def test_finite_real_values_and_shapes(self):
        source=ClimateSource(os.environ['BALLOON_TEST_CLIMATE_DB'],expected_sha256='1af26d91500252c285f89e2cc50eb32fd325f6df9905ad0c5162282791d5137a')
        before=source.verify_full()
        result=source.query(ClimateQuery(source.source_id,18))
        self.assertEqual(len(result['annual']),24*38)
        self.assertEqual(len(result['spatial']['rows']),24*570)
        self.assertEqual(result['population']['selected_cell_count'],570)
        expected=[(0,18,31.59429732888654,-.4515257082481805,35.01718787522183),
                  (12,18,15.454726414676394,-.8054795726636831,20.839402561431665),
                  (0,0,-10.886632834857146,4.042305194569853,23.92140282890817),
                  (12,0,-27.442859536188525,.05483967042498146,27.574885478517608),
                  (0,37,4.8586555542681165,-3.019848643221088,8.484247838086972),
                  (12,37,-.40816329708299853,1.5603453854975968,5.683507441147442)]
        for timebin,level,u,v,s in expected:
            row=next(r for r in result['annual'] if r['timebin_id']==timebin and r['level_id']==level)
            for name,value in [('mean_u',u),('mean_v',v),('mean_speed',s)]:
                self.assertAlmostEqual(row[name],value,places=10)
            self.assertAlmostEqual(row['pooled_constancy'],math.hypot(u,v)/s,places=12)
            self.assertEqual(row['time_count'],600)
        self.assertEqual(source.verify_full(),before)
        # Optional bounded evidence includes selected comparisons, not a full data export.
        if os.environ.get('BALLOON_TEST_CLIMATE_EVIDENCE'):
            evidence={'before':before,'after':source.verify_full(),'unchanged':True,
                      'duckdb_version':source.duckdb_version,'source_code':source.descriptor()['source_code'],
                      'annual_rows':len(result['annual']),'spatial_rows':len(result['spatial']['rows']),
                      'selected_cell_count':570,'source_capabilities':result['source']['capabilities'],
                      'query_hash':result['provenance']['query_hash'],'result_hash':result['provenance']['result_hash'],
                      'json_bytes':len(json.dumps(result,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')),
                      'compared_rows':[r for r in result['annual'] if (r['timebin_id'],r['level_id']) in {(e[0],e[1]) for e in expected}],
                      'limits':['Supplied summary database, not original JRA reanalysis validation.','No performance timing collected; other managed tests may run concurrently.','No UI/API/save/HTTP integration tested.']}
            Path(os.environ['BALLOON_TEST_CLIMATE_EVIDENCE']).write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    unittest.main()
