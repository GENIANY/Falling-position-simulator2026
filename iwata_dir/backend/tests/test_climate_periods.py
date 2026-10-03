"""Unequal-calendar, hourly-population and empirical-count counterexamples."""
import json
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4

import duckdb
from test_climate import create_fixture
from backend.climate.contracts import Bounds, ClimateError, ClimateQuery
from backend.climate.source import ClimateSource
from backend.climate.service import ClimateService


def add_extensions(path):
    with duckdb.connect(str(path)) as con:
        con.executemany('INSERT INTO meta_column VALUES (?,?,?)', [('fact_wind_diurnal',k,'m s-1') for k in ('u_mean','v_mean','speed_mean')])
        con.execute('''CREATE TABLE fact_wind_diurnal AS SELECT timebin_id,level_id,cell_id,
            CAST(h AS INTEGER) AS hour_utc,CAST(n/4 AS INTEGER) AS n,
            CAST(CASE WHEN h IN (0,6) THEN u_mean ELSE -u_mean END AS FLOAT) AS u_mean,
            v_mean,speed_mean FROM fact_wind CROSS JOIN (VALUES (0),(6),(12),(18)) hours(h)''')
        con.execute('CREATE TABLE dim_sector(sector INTEGER,centre_deg DOUBLE,lo_deg DOUBLE,hi_deg DOUBLE,wraps_north BOOLEAN,compass_16 VARCHAR)')
        names='N NNE NE ENE E ESE SE SSE S SSW SW WSW W WNW NW NNW'.split()
        con.executemany('INSERT INTO dim_sector VALUES (?,?,?,?,?,?)',[(i,i*22.5,(i*22.5-11.25)%360,i*22.5+11.25,i==0,n) for i,n in enumerate(names)])
        con.execute('CREATE TABLE dim_speed_class(speed_class INTEGER,lo_ms DOUBLE,hi_ms DOUBLE,label VARCHAR)')
        con.executemany('INSERT INTO dim_speed_class VALUES (?,?,?,?)',[(i,*x) for i,x in enumerate(zip([0,5,10,20,30,50],[5,10,20,30,50,None],['0-5','5-10','10-20','20-30','30-50','50+']))])
        con.execute('''CREATE TABLE fact_wind_rose AS SELECT w.timebin_id,w.level_id,w.cell_id,s.sector,c.speed_class,
            CAST(CASE WHEN s.sector=CASE WHEN w.timebin_id%2=0 THEN 0 ELSE 4 END AND c.speed_class=2 THEN w.n ELSE 0 END AS INTEGER) AS count
            FROM fact_wind w CROSS JOIN dim_sector s CROSS JOIN dim_speed_class c WHERE w.cell_id=2''')


class PeriodTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='climate-periods-')
        self.path=Path(self.temp.name)/'input.duckdb'
        create_fixture(self.path)
        add_extensions(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_month_pooling_recomputes_spatial_range_and_constancy(self):
        with duckdb.connect(str(self.path)) as con:
            # Unequal Jan halves: cell maxima swap, so averaging half ranges is wrong.
            con.execute('UPDATE fact_wind SET u_mean=0,v_mean=0,speed_mean=0 WHERE timebin_id IN (0,1)')
            con.execute('UPDATE fact_wind SET u_mean=10,speed_mean=10 WHERE (timebin_id=0 AND cell_id=0) OR (timebin_id=1 AND cell_id=1)')
        s=ClimateSource(self.path)
        r=s.query(ClimateQuery(s.source_id,1,Bounds(140,141,40,41)))
        month=r['summaries_by_grain']['month']
        row=next(v for v in month['annual'] if v['timebin_id']==0 and v['level_id']==1)
        a,b=6000/1240,6400/1240
        self.assertAlmostEqual(row['mean_speed'],(a+3*b)/4)
        self.assertAlmostEqual(row['spatial_mean_speed_range'],b-a)
        self.assertEqual(row['time_count'],1240)
        self.assertEqual(row['pooled_constancy'],1)
        self.assertEqual(len(r['summaries_by_grain']['season']['timebins']),4)
        self.assertEqual(r['summaries_by_grain']['season']['timebins'][0]['member_timebin_ids'],[0,1,2,3,22,23])

    def test_hour_population_is_distinct_normalized_and_not_silently_filled(self):
        s=ClimateSource(self.path)
        r=s.query(ClimateQuery(s.source_id,1,hours_utc=[18,0]))
        self.assertEqual(r['query']['hours_utc'],[0,18])
        self.assertEqual(r['population']['native_hours_utc'],[0,18])
        self.assertEqual(r['annual'][0]['time_count'],300)
        self.assertEqual(r['annual'][0]['mean_u'],0)
        self.assertEqual(r['population']['timebins'][0]['n_analyses_expected'],300)
        self.assertEqual(r['source']['timebins'][0]['n_analyses_expected'],600)
        self.assertEqual(r['wind_rose'],{'available':False,'reason':'hour_subset_not_available'})
        self.assertEqual(ClimateQuery(s.source_id,1,hours_utc=[18,6,0,12]).as_dict(),ClimateQuery(s.source_id,1).as_dict())
        for h in ([],[1],[0,0],[True],['0']):
            with self.subTest(h=h),self.assertRaises(ClimateError): ClimateQuery(s.source_id,1,hours_utc=h)
        # Legacy means-only database has no hourly capability.
        other=Path(self.temp.name)/'legacy.duckdb';create_fixture(other); legacy=ClimateSource(other)
        with self.assertRaises(ClimateError) as e: legacy.query(ClimateQuery(legacy.source_id,1,hours_utc=[0]))
        self.assertEqual(e.exception.code,'CLIMATE_HOUR_SUPPORT')

    def test_rose_sums_counts_not_percentages_and_identifies_external_point(self):
        s=ClimateSource(self.path)
        r=s.query(ClimateQuery(s.source_id,1,Bounds(140,141,40,41)))
        rose=r['summaries_by_grain']['month']['wind_rose']
        feb=next(v for v in rose['rows'] if v['timebin_id']==1 and v['sector']==0 and v['speed_class']==2)
        self.assertAlmostEqual(feb['frequency'],600/(600+532))
        self.assertNotEqual(feb['frequency'],.5)
        self.assertEqual(rose['point']['cell_id'],2)
        self.assertFalse(rose['point_in_selected_region'])
        self.assertIsNone(rose['speed_classes'][-1]['hi_ms'])
        for period in range(12):
            self.assertAlmostEqual(sum(v['frequency'] for v in rose['rows'] if v['timebin_id']==period),1)

    def test_present_incomplete_extensions_fail_instead_of_falling_back(self):
        for index,sql in enumerate([
            'UPDATE fact_wind_diurnal SET n=n-1 WHERE timebin_id=0 AND hour_utc=0',
            'UPDATE fact_wind_diurnal SET hour_utc=6 WHERE timebin_id=0 AND hour_utc=0',
            'UPDATE fact_wind_rose SET count=count+1 WHERE timebin_id=0 AND sector=0',
            'UPDATE dim_sector SET centre_deg=1 WHERE sector=0',
            "UPDATE meta_column SET units='kt' WHERE table_name='fact_wind_diurnal' AND column_name='u_mean'",
        ]):
            p=Path(self.temp.name)/f'bad{index}.duckdb';create_fixture(p);add_extensions(p)
            with duckdb.connect(str(p)) as con: con.execute(sql)
            with self.subTest(sql=sql),self.assertRaises(ClimateError): ClimateSource(p)

    def test_saved_subset_restores_without_source_and_queries_do_not_collide(self):
        root=Path(self.temp.name)/'store';service=ClimateService(root,self.path)
        source=service.sources()['sources'][0]['source_id']
        a=service.create_analysis({'client_request_id':str(uuid4()),'query':ClimateQuery(source,1,hours_utc=[0]).as_dict()})
        b=service.create_analysis({'client_request_id':str(uuid4()),'query':ClimateQuery(source,1,hours_utc=[18]).as_dict()})
        self.assertNotEqual(a['analysis_id'],b['analysis_id'])
        self.assertNotEqual(a['result_hash'],b['result_hash'])
        restored=ClimateService(root).get_analysis(a['analysis_id'])
        self.assertEqual(json.dumps(a,sort_keys=True),json.dumps(restored,sort_keys=True))
