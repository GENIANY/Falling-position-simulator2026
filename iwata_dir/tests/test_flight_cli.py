"""Offline, real-field user flow and artifact integrity acceptance tests."""
from contextlib import redirect_stdout, redirect_stderr
import ast
import csv
import hashlib
import importlib
import inspect
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from balloon_sim.cli import main, read_json
from balloon_sim.dynamics import simulate
from balloon_sim.weather import load_weather

ROOT=Path(__file__).resolve().parents[1]


class FlightCliTests(unittest.TestCase):
    def test_published_api_index_resolves_actual_signatures_and_tests(self):
        index=read_json(ROOT/'docs/IMPLEMENTATION_INDEX.json')
        self.assertEqual(len({entry['id'] for entry in index['entries']}),len(index['entries']))
        for entry in index['entries']:
            scope=ast.parse((ROOT/entry['path']).read_text(encoding='utf-8'))
            for part in entry['symbol'].split('.'):
                scope=next(n for n in scope.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name==part)
            self.assertEqual(ast.unparse(scope.args),entry['signature'],entry['id'])
            self.assertTrue((ROOT/entry['test_path']).is_file())
            if 'public_path' in entry:
                module_name=entry['public_path'].removesuffix('.py').replace('/','.')
                public=importlib.import_module(module_name)
                for part in entry.get('public_symbol',entry['symbol']).split('.'):
                    public=getattr(public,part)
                self.assertEqual(str(inspect.signature(public)), '('+entry['signature']+')', entry['id'])

    def invoke(self,args):
        out,err=io.StringIO(),io.StringIO()
        with redirect_stdout(out),redirect_stderr(err),patch('socket.socket',side_effect=AssertionError('network forbidden')):
            code=main(list(map(str,args)))
        return code,out.getvalue(),err.getvalue()

    def test_real_cases_landing_and_offline_repeat(self):
        for name,fixture in [('hokkaido-simple','hokkaido'),('wakayama-isothermal','wakayama')]:
            config=ROOT/'examples'/(name+'.json')
            bundle=ROOT/'references/flight_fixture'/(fixture+'-weather.json.gz')
            with self.subTest(name=name),tempfile.TemporaryDirectory() as tmp:
                a,b=Path(tmp)/'first',Path(tmp)/'second'
                for output in (a,b):
                    code,stdout,stderr=self.invoke(['simulate',config,'--weather',bundle,'--output',output])
                    self.assertEqual(code,0,stderr)
                    self.assertEqual(json.loads(stdout)['status'],'landed')
                self.assertEqual((a/'result.json').read_bytes(),(b/'result.json').read_bytes())
                result=json.loads((a/'result.json').read_text(encoding='utf-8'))
                self.assertEqual([e['type'] for e in result['events']],['burst','landing'])
                self.assertEqual(result['summary']['maximum_altitude_m'],30000)
                rows=result['records'];self.assertAlmostEqual(rows[-1]['height_agl_m'],0)
                self.assertTrue(all(r['height_agl_m']>=-1e-6 for r in rows))
                self.assertEqual(rows[0]['time_utc'][11:16],'03:30')
                self.assertGreater(rows[-1]['elapsed_s'],7200)
                manifest=read_json(a/'manifest.json')
                for file,expected in manifest['files'].items():
                    data=(a/file).read_bytes()
                    self.assertEqual(hashlib.sha256(data).hexdigest(),expected['sha256'])
                    self.assertEqual(len(data),expected['bytes'])
                provenance=read_json(a/'provenance.json')
                sources={p.relative_to(ROOT/'balloon_sim').as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in (ROOT/'balloon_sim').rglob('*.py')}
                self.assertEqual(provenance['source_sha256'],sources)
                self.assertIn('flight/trajectory.py',sources)
                self.assertIn('environment/fields.py',sources)
                geometry=read_json(a/'trajectory.geojson')['features'][0]['geometry']
                self.assertEqual(geometry['coordinates'][0],[rows[0][k] for k in ('longitude_deg','latitude_deg','altitude_m')])
                with (a/'trajectory.csv').open(encoding='utf-8-sig',newline='') as stream:
                    csvrows=list(csv.DictReader(stream))
                self.assertEqual(len(csvrows),len(rows))
                self.assertEqual((a/'input.json').read_bytes(),config.read_bytes())
                before=(a/'manifest.json').read_bytes()
                code,_,_=self.invoke(['simulate',config,'--weather',bundle,'--output',a])
                self.assertEqual(code,1)
                self.assertEqual(before,(a/'manifest.json').read_bytes())

    def test_incomplete_is_saved_and_exit_two(self):
        c=read_json(ROOT/'examples/hokkaido-simple.json');c['integration']['max_duration_s']=1
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'input.json';source.write_text(json.dumps(c),encoding='utf-8')
            out=Path(tmp)/'out'
            code,stdout,err=self.invoke(['simulate',source,'--weather',ROOT/'references/flight_fixture/hokkaido-weather.json.gz','--output',out])
            self.assertEqual(code,2,err)
            self.assertFalse(json.loads(stdout)['complete'])
            self.assertTrue((out/'report.html').is_file())
            self.assertEqual(read_json(out/'result.json')['stop_reason']['code'],'MAX_DURATION')

    def test_bad_input_rejected_before_output_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'input.json';source.write_text('{"launch":{},"launch":{}}')
            out=Path(tmp)/'out'
            code,_,stderr=self.invoke(['simulate',source,'--weather',ROOT/'references/flight_fixture/hokkaido-weather.json.gz','--output',out])
            self.assertEqual(code,1);self.assertIn('duplicate',stderr)
            self.assertFalse(out.exists())

    def test_strict_json_nonfinite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'input.json'
            for value in ('NaN','Infinity','1e999'):
                path.write_text('{"speed": '+value+'}')
                with self.assertRaises(ValueError):read_json(path)

    def test_inspect_offline(self):
        code,out,err=self.invoke(['inspect',ROOT/'references/flight_fixture/hokkaido-weather.json.gz'])
        self.assertEqual(code,0,err);self.assertIn('subset',json.loads(out))

    def test_real_field_step_refinement(self):
        config=read_json(ROOT/'examples/hokkaido-simple.json')
        weather=load_weather(ROOT/'references/flight_fixture/hokkaido-weather.json.gz')
        results=[]
        with patch('socket.socket',side_effect=AssertionError('network forbidden')):
            for step in (20,10,5):
                config['integration']['max_step_s']=step
                result=simulate(config,weather);self.assertTrue(result['complete'])
                results.append(result['records'][-1])
        # A numerical reproducibility criterion, not observed flight accuracy.
        coarse,fine=results[1:]
        self.assertLess(abs(coarse['elapsed_s']-fine['elapsed_s']),1)
        self.assertLess(abs(coarse['latitude_deg']-fine['latitude_deg']),0.001)
        self.assertLess(abs(coarse['longitude_deg']-fine['longitude_deg']),0.001)


if __name__=='__main__':unittest.main()
