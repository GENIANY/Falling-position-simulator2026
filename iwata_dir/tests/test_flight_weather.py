"""Flight weather tests: independent fields, boundaries, terrain and acquisition.

Synthetic values prove numerical contracts, not atmospheric/forecast accuracy.
Real bounded GFS acquisition/replay evidence is kept in the external release.
"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from balloon_sim.weather import (SCHEMA, WeatherError, WeatherField, acquire_gfs,
    load_weather, geometric_to_geopotential, geopotential_to_geometric,
    _request, _url, _download, _write_bundle, replay_gfs)

T0=datetime(2026,9,22,18,tzinfo=timezone.utc)


def fixture():
    """Two times, two-by-two rectangle, three heights; simple affine wind."""
    heights=[100.0,1000.0,40000.0]
    fields={k:[] for k in ("geopotential_height_gpm","temperature_k",
             "eastward_wind_m_s","northward_wind_m_s","specific_humidity_kg_kg")}
    for name in fields:
        for t in range(2):
            levels=[]
            for h in heights:
                plane=[]
                for j in range(2):
                    row=[]
                    for i in range(2):
                        value={"geopotential_height_gpm":h,"temperature_k":280-h*.001,
                               "eastward_wind_m_s":2*t+3*j+4*i+h*.01,
                               "northward_wind_m_s":-5+t+j+i,
                               "specific_humidity_kg_kg":.01}[name]
                        row.append(value)
                    plane.append(row)
                levels.append(plane)
            fields[name].append(levels)
    surface={name:[[[value,value],[value,value]],[[value,value],[value,value]]]
             for name,value in {"geopotential_height_gpm":0.,"pressure_pa":101000.,
                  "temperature_2m_k":285.,"specific_humidity_2m_kg_kg":.015,
                  "eastward_wind_10m_m_s":1.,"northward_wind_10m_m_s":-2.}.items()}
    return {"schema":SCHEMA,"metadata":{"run_utc":T0.isoformat()},
            "axes":{"time_utc":[T0.isoformat(),(T0+timedelta(hours=1)).isoformat()],
                    "latitude_deg":[33.,34.],"longitude_deg":[135.,136.],
                    "pressure_pa":[100000.,90000.,100.]},"fields":fields,"surface":surface}


class WeatherTests(unittest.TestCase):
    def query(self,field=None,**changes):
        values=dict(time_utc=T0+timedelta(minutes=30),latitude_deg=33.5,
                    longitude_deg=135.5,altitude_m=geopotential_to_geometric(500.))
        values.update(changes)
        return (field or WeatherField(fixture())).sample(**values)

    def error(self,code,call):
        with self.assertRaises(WeatherError) as caught: call()
        self.assertEqual(caught.exception.code,code)

    def test_affine_time_lat_lon_height(self):
        q=self.query()
        self.assertAlmostEqual(q['eastward_wind_m_s'],9.5,12)
        self.assertAlmostEqual(q['northward_wind_m_s'],-3.5,12)
        self.assertAlmostEqual(q['temperature_k'],279.5,12)

    def test_pressure_log_linear_in_each_column(self):
        q=self.query()
        expected=100000.**(5/9)*90000.**(4/9)
        self.assertAlmostEqual(q['pressure_pa'],expected,7)

    def test_height_inverse_and_difference(self):
        self.assertAlmostEqual(geopotential_to_geometric(geometric_to_geopotential(30000)),30000,8)
        self.assertLess(geometric_to_geopotential(30000),30000)
        self.assertGreater(30000-geometric_to_geopotential(30000),100)

    def test_exact_endpoints_have_no_zero_weight_dependencies(self):
        b=fixture(); b['fields']['temperature_k'][1][0][1][1]=None
        q=self.query(WeatherField(b),time_utc=T0,latitude_deg=33,longitude_deg=135,
                     altitude_m=geopotential_to_geometric(100))
        self.assertAlmostEqual(q['temperature_k'],279.9)

    def test_missing_positive_field_rejects(self):
        b=fixture(); b['fields']['temperature_k'][1][0][1][1]=None
        self.error('MISSING_DATA',lambda:self.query(WeatherField(b)))

    def test_unused_field_missing_does_not_stop_wind(self):
        b=fixture(); b['fields']['temperature_k'][1][0][1][1]=None
        q=self.query(WeatherField(b),fields=['eastward_wind_m_s'])
        self.assertEqual(set(q)&{'pressure_pa','temperature_k','specific_humidity_kg_kg'},set())

    def test_unknown_field_rejects(self):
        self.error('UNKNOWN_FIELD',lambda:self.query(fields=['relative_humidity']))

    def test_duplicate_field_cannot_double_wind(self):
        self.error('UNKNOWN_FIELD',lambda:self.query(fields=['eastward_wind_m_s','eastward_wind_m_s']))

    def test_invalid_field_declaration_rejects(self):
        for fields in ('eastward_wind_m_s',[{}],[]):
            self.error('UNKNOWN_FIELD',lambda:self.query(fields=fields))

    def test_temporal_boundaries(self):
        for t in (T0-timedelta(microseconds=1),T0+timedelta(hours=1,microseconds=1)):
            self.error('TIME_OUT_OF_RANGE',lambda:self.query(time_utc=t))

    def test_naive_time_rejects(self):
        self.error('NON_UTC_TIME',lambda:self.query(time_utc=T0.replace(tzinfo=None)))

    def test_horizontal_boundaries(self):
        self.error('LATITUDE_OUT_OF_RANGE',lambda:self.query(latitude_deg=32.999))
        self.error('LONGITUDE_OUT_OF_RANGE',lambda:self.query(longitude_deg=136.001))

    def test_zero_longitude_equivalent_to_360_endpoint(self):
        b=fixture(); b['axes']['longitude_deg']=[359.,360.]
        f=WeatherField(b)
        a=self.query(f,longitude_deg=0.)
        b=self.query(f,longitude_deg=360.)
        self.assertEqual(a,b)
        self.error('LONGITUDE_OUT_OF_RANGE',lambda:self.query(f,longitude_deg=-224.))

    def test_surface_and_top_boundaries(self):
        self.error('BELOW_GROUND',lambda:self.query(altitude_m=-.1))
        self.error('HEIGHT_OUT_OF_RANGE',lambda:self.query(altitude_m=geopotential_to_geometric(40001)))
        self.assertEqual(self.query(altitude_m=0)['ground_altitude_m'],0)

    def test_surface_anchor_values_and_quality(self):
        q=self.query(altitude_m=0)
        self.assertEqual(q['eastward_wind_m_s'],1.)
        self.assertEqual(q['temperature_k'],285.)
        self.assertAlmostEqual(q['pressure_pa'],101000.)
        self.assertIn('10m_wind_held_below_anchor',q['quality'])
        self.assertIn('2m_thermodynamics_held_below_anchor',q['quality'])

    def test_anchor_to_pressure_bridge_continuity(self):
        field=WeatherField(fixture())
        for height in (2.,10.,geopotential_to_geometric(100)):
            a=self.query(field,altitude_m=height-1e-6)
            b=self.query(field,altitude_m=height+1e-6)
            for name in ('eastward_wind_m_s','temperature_k','pressure_pa'):
                self.assertLess(abs(a[name]-b[name]),.01)

    def test_underground_pressure_values_never_used(self):
        b=fixture()
        for t in range(2):
            for j in range(2):
                for i in range(2):
                    b['surface']['pressure_pa'][t][j][i]=95000
                    b['fields']['eastward_wind_m_s'][t][0][j][i]=999999
        q=self.query(WeatherField(b),altitude_m=50)
        self.assertLess(q['eastward_wind_m_s'],20)

    def test_terrain_stencil_surface_extension_is_explicit(self):
        b=fixture()
        for t in range(2):
            for j in range(2):
                b['surface']['geopotential_height_gpm'][t][j][1]=200
                b['surface']['pressure_pa'][t][j][1]=95000
        field=WeatherField(b)
        terrain=field.ground_altitude(T0,33.5,135.5)
        q=self.query(field,time_utc=T0,altitude_m=terrain)
        self.assertIn('terrain_stencil_surface_clamp',q['quality'])
        self.assertGreater(q['terrain_stencil_clamp_depth_m'],99)
        self.error('BELOW_GROUND',lambda:self.query(field,time_utc=T0,altitude_m=terrain-1))

    def test_terrain_values_continuous_at_spatial_endpoint(self):
        b=fixture()
        for t in range(2):
            for j in range(2):
                b['surface']['geopotential_height_gpm'][t][j][1]=200
                b['surface']['pressure_pa'][t][j][1]=95000
        field=WeatherField(b)
        a=self.query(field,longitude_deg=135,altitude_m=50)
        b=self.query(field,longitude_deg=135+1e-9,altitude_m=50)
        self.assertLess(abs(a['eastward_wind_m_s']-b['eastward_wind_m_s']),1e-7)

    def test_time_changing_height_order_is_column_then_time(self):
        b=fixture()
        for j in range(2):
            for i in range(2):
                b['fields']['geopotential_height_gpm'][1][1][j][i]=1500
                b['fields']['eastward_wind_m_s'][0][0][j][i]=0
                b['fields']['eastward_wind_m_s'][0][1][j][i]=9
                b['fields']['eastward_wind_m_s'][1][0][j][i]=0
                b['fields']['eastward_wind_m_s'][1][1][j][i]=14
        q=self.query(WeatherField(b))
        # Both reconstructed columns give4; mixing heights first also happens
        # to do so for these slopes, so set second high wind to28 independently.
        b['fields']['eastward_wind_m_s'][1][1]=[[28,28],[28,28]]
        q=self.query(WeatherField(b))
        self.assertAlmostEqual(q['eastward_wind_m_s'],6.)
        mixed_first=(.5*9+.5*28)*(500-100)/(1250-100)
        self.assertNotAlmostEqual(q['eastward_wind_m_s'],mixed_first,6)

    def test_time_terrain_endpoint_continuity(self):
        b=fixture()
        b['surface']['geopotential_height_gpm'][1]=[[200,200],[200,200]]
        b['surface']['pressure_pa'][1]=[[95000,95000],[95000,95000]]
        field=WeatherField(b)
        a=self.query(field,time_utc=T0,altitude_m=50)
        b=self.query(field,time_utc=T0+timedelta(microseconds=1),altitude_m=50)
        self.assertLess(abs(a['eastward_wind_m_s']-b['eastward_wind_m_s']),1e-7)

    def test_missing_valid_schedule_rejected(self):
        b=fixture(); b['axes']['time_utc'][1]=(T0+timedelta(hours=2)).isoformat()
        self.error('MISSING_VALID_TIME',lambda:WeatherField(b))

    def test_nonmonotonic_height_rejected(self):
        b=fixture(); b['fields']['geopotential_height_gpm'][0][1][0][0]=90
        self.error('INVALID_HEIGHT_PROFILE',lambda:WeatherField(b))

    def test_boolean_nan_query_rejected(self):
        for value in (True,float('nan'),float('inf')):
            self.error('INVALID_NUMBER',lambda:self.query(altitude_m=value))

    def test_missing_surface_rejected(self):
        b=fixture(); b['surface']['temperature_2m_k'][0][0][0]=None
        self.error('MISSING_SURFACE',lambda:WeatherField(b))

    def test_negative_q_rejected(self):
        b=fixture(); b['fields']['specific_humidity_kg_kg'][0][0][0][0]=-1
        self.error('INVALID_FIELD_VALUE',lambda:self.query(WeatherField(b)))

    def test_invalid_source_cannot_hide_in_positive_interpolated_value(self):
        for name,bad in (('specific_humidity_kg_kg',-.001),('temperature_k',-1)):
            b=fixture(); b['fields'][name][0][0][0][0]=bad
            self.error('INVALID_FIELD_VALUE',lambda:self.query(WeatherField(b)))

    def test_invalid_surface_anchor_cannot_hide_in_bridge(self):
        b=fixture(); b['surface']['specific_humidity_2m_kg_kg'][0][0][0]=-.001
        self.error('INVALID_FIELD_VALUE',lambda:self.query(WeatherField(b),altitude_m=90))

    def test_bundle_is_independent_of_caller_changes(self):
        b=fixture(); f=WeatherField(b)
        b['fields']['eastward_wind_m_s'][0][0][0][0]=9999
        self.assertAlmostEqual(self.query(f)['eastward_wind_m_s'],9.5)

    def test_malformed_bundle_structure_has_weather_error(self):
        cases=[{},[],{'schema':SCHEMA}]
        for section in ('axes','fields','surface','metadata'):
            b=fixture(); b[section]=None; cases.append(b)
        for name in ('time_utc','latitude_deg','longitude_deg','pressure_pa'):
            b=fixture(); del b['axes'][name]; cases.append(b)
        b=fixture(); b['axes']['time_utc']=None; cases.append(b)
        for b in cases:
            with self.subTest(bundle=str(b)[:60]):
                with self.assertRaises(WeatherError): WeatherField(b)


class AcquisitionTests(unittest.TestCase):
    def request(self):
        return {'run_utc':T0.isoformat(),'start_utc':(T0+timedelta(minutes=30)).isoformat(),
                'end_utc':(T0+timedelta(hours=2)).isoformat(),
                'bounds':{'west':135.1,'east':136.1,'south':33.1,'north':34.1}}

    def test_planned_closed_window_and_outward_bounds(self):
        r=_request(self.request())
        self.assertEqual(r['lead_hours'],[0,1,2])
        self.assertEqual(r['bounds'],{'west':135.,'east':136.25,'south':33.,'north':34.25})

    def test_120_to_123_schedule(self):
        r=self.request()
        r.update(start_utc=(T0+timedelta(hours=120,minutes=1)).isoformat(),
                 end_utc=(T0+timedelta(hours=123)).isoformat())
        self.assertEqual(_request(r)['lead_hours'],[120,123])

    def test_exact_instant_only_requires_one_file(self):
        r=self.request(); r['start_utc']=r['end_utc']
        self.assertEqual(_request(r)['lead_hours'],[2])

    def test_invalid_request_bounds_and_budget(self):
        for updates in ({'max_bytes':True},{'max_bytes':50_000_001},{'run_utc':'2026-09-22T19:00:00Z'},
                        {'bounds':{'west':-1,'east':1,'south':30,'north':31}}):
            with self.assertRaises(WeatherError): _request({**self.request(),**updates})

    def test_url_has_all_required_fields_and_grid(self):
        url=_url(_request(self.request()),0)
        for text in ('var_SPFH=on','lev_1_mb=on','lev_1000_mb=on','lev_2_m_above_ground=on',
                     'subregion=','leftlon=135.0','file=gfs.t18z.pgrb2.0p25.f000'):
            self.assertIn(text,url)

    def test_existing_output_is_refused_without_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch('urllib.request.urlopen') as mocked:
                with self.assertRaises(WeatherError) as caught: acquire_gfs(self.request(),tmp)
                self.assertEqual(caught.exception.code,'OUTPUT_EXISTS'); mocked.assert_not_called()

    def test_standalone_load_and_deterministic_gzip(self):
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/'a.gz',Path(tmp)/'b.gz'
            _write_bundle(a,fixture()); _write_bundle(b,fixture())
            self.assertEqual(a.read_bytes(),b.read_bytes())
            with patch('urllib.request.urlopen',side_effect=AssertionError('offline')):
                q=load_weather(a).sample(T0,33,135,100)
                self.assertGreater(q['temperature_k'],0)

    def test_download_stream_budget_is_enforced(self):
        from balloon_sim.environment.nomads import NomadsGateway
        class Response(io.BytesIO):
            status=200
            headers={}
        with tempfile.TemporaryDirectory() as tmp:
            gateway=NomadsGateway(Path(tmp)/'transport',opener=lambda *a,**k:Response(b'GRIB'+b'x'*100))
            with patch('balloon_sim.environment.gfs.NomadsGateway',return_value=gateway):
                with self.assertRaises(WeatherError) as caught: _download('https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl',Path(tmp)/'raw',10)
                self.assertEqual(caught.exception.code,'DOWNLOAD_LIMIT')

    def test_raw_replay_rejects_tampering_before_decoder(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); r=self.request(); r['start_utc']=r['end_utc']; spec=_request(r)
            (p/'request.json').write_text(json.dumps(spec),encoding='utf-8')
            (p/'f002.grib2').write_bytes(b'wrong')
            (p/'provenance.json').write_text(json.dumps([{'file':'f002.grib2','url':_url(spec,2),
                'bytes':5,'sha256':hashlib.sha256(b'right').hexdigest()}]),encoding='utf-8')
            with patch('balloon_sim.environment.gfs.decode_gfs',side_effect=AssertionError('not reached')) as decoder:
                with self.assertRaises(WeatherError) as caught: replay_gfs(p,p/'result.gz')
                self.assertEqual(caught.exception.code,'RAW_HASH_MISMATCH')
                decoder.assert_not_called()

    def test_load_rejects_duplicate_and_nonfinite_json_plain_and_gzip(self):
        texts=['{"schema":"bad","schema":"balloon.weather/1"}',
               json.dumps(fixture()).replace('"metadata": {','"metadata": {"bad": NaN,',1),
               json.dumps(fixture()).replace('"metadata": {','"metadata": {"bad": Infinity,',1),
               json.dumps(fixture()).replace('"metadata": {','"metadata": {"bad": 1e999,',1)]
        with tempfile.TemporaryDirectory() as tmp:
            for i,text in enumerate(texts):
                for zipped in (False,True):
                    path=Path(tmp)/(str(i)+('.json.gz' if zipped else '.json'))
                    if zipped:
                        with gzip.open(path,'wt',encoding='utf-8') as stream: stream.write(text)
                    else: path.write_text(text,encoding='utf-8')
                    with self.assertRaises(WeatherError) as caught: load_weather(path)
                    self.assertEqual(caught.exception.code,'INVALID_JSON')

    def test_load_accepts_utf8_bom_plain_and_gzip(self):
        with tempfile.TemporaryDirectory() as tmp:
            for zipped in (False,True):
                path=Path(tmp)/('bom.json.gz' if zipped else 'bom.json')
                opener=gzip.open if zipped else open
                with opener(path,'wt',encoding='utf-8-sig') as stream: json.dump(fixture(),stream)
                self.assertEqual(load_weather(path).times[0],T0)

    def test_replay_rejects_ambiguous_request_before_decoder(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            (p/'request.json').write_text('{"run_utc":"bad","run_utc":"other"}',encoding='utf-8')
            with patch('balloon_sim.environment.gfs.decode_gfs',side_effect=AssertionError('not reached')) as decoder:
                with self.assertRaises(WeatherError) as caught: replay_gfs(p,p/'out.gz')
                self.assertEqual(caught.exception.code,'INVALID_JSON')
                decoder.assert_not_called()

    def test_replay_rejects_malformed_provenance_with_weather_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); r=self.request(); r['start_utc']=r['end_utc']
            (p/'request.json').write_text(json.dumps(_request(r)),encoding='utf-8')
            for value in ({},[{}],[None]):
                (p/'provenance.json').write_text(json.dumps(value),encoding='utf-8')
                with self.assertRaises(WeatherError) as caught: replay_gfs(p,p/'out.gz')
                self.assertEqual(caught.exception.code,'PROVENANCE_MISMATCH')


if __name__=='__main__':
    unittest.main()
