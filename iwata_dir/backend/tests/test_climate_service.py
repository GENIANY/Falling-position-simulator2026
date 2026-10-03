"""Storage/lifetime counterexamples; only disposable artificial databases."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
from threading import Barrier, Event
import unittest
from unittest.mock import patch
from uuid import uuid4

from backend.climate.service import ClimateService, ClimateServiceError, ARTIFACT_SCHEMA
from backend.tests.test_climate import create_fixture


class ClimateServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='climate-service-')
        self.root=Path(self.temp.name)
        self.path=self.root/'source.duckdb'
        create_fixture(self.path)
        self.service=ClimateService(self.root/'store',self.path)
        self.descriptor=self.service.sources()['sources'][0]
        self.query={'source_id':self.descriptor['source_id'],'level_id':0,'bounds':None,'grain':'half'}

    def tearDown(self):
        self.temp.cleanup()

    def body(self,request_id='request-1',query=None):
        return {'client_request_id':request_id,'query':query or self.query}

    def counts(self):
        with closing(sqlite3.connect(self.service.database_path)) as con, con:
            return tuple(con.execute(f'SELECT count(*) FROM {name}').fetchone()[0] for name in ('climate_analyses','climate_requests','climate_query_cache'))

    def test_fixed_artifact_restart_and_idempotency_without_original_source(self):
        artifact=self.service.create_analysis(self.body())
        self.assertEqual(artifact['schema'],ARTIFACT_SCHEMA)
        self.assertEqual(artifact['query'],artifact['summary']['query'])
        self.assertEqual(self.service.get_analysis(artifact['analysis_id']),artifact)
        restarted=ClimateService(self.root/'store')
        self.assertEqual(restarted.sources()['sources'],[])
        self.assertEqual(restarted.get_analysis(artifact['analysis_id']),artifact)
        self.assertEqual(restarted.create_analysis(self.body()),artifact)
        with self.assertRaises(ClimateServiceError) as ctx:
            restarted.create_analysis(self.body(query={**self.query,'level_id':1}))
        self.assertEqual((ctx.exception.code,ctx.exception.status_code),('CLIMATE_IDEMPOTENCY',409))
        with self.assertRaises(ClimateServiceError) as ctx:
            restarted.create_analysis(self.body('new-request'))
        self.assertEqual(ctx.exception.status_code,503)

    def test_same_source_query_reuses_bytes_without_requery_or_duplicate_artifact(self):
        artifact=self.service.create_analysis(self.body())
        with patch.object(self.service._source,'query',side_effect=AssertionError('cache reuse must not reaggregate')):
            self.assertEqual(self.service.create_analysis(self.body('second-request')),artifact)
            self.assertEqual(self.service.create_analysis(self.body('explicit-bounds',{**self.query,'bounds':self.descriptor['bounds']})),artifact)
        self.assertEqual(self.counts(),(1,3,1))
        restarted=ClimateService(self.root/'store',self.path)
        with patch.object(restarted._source,'query',side_effect=AssertionError('restart reuse must not reaggregate')):
            self.assertEqual(restarted.create_analysis(self.body('fourth-request')),artifact)
        self.assertEqual(self.counts(),(1,4,1))

    def test_legacy_request_key_omits_null_point_and_rejects_explicit_selection(self):
        original=self.service.create_analysis(self.body())
        canonical=json.dumps(self.query,sort_keys=True,separators=(',',':'))
        with closing(sqlite3.connect(self.service.database_path)) as con:
            stored=con.execute('SELECT query_json FROM climate_requests').fetchone()[0]
        self.assertEqual(stored,canonical)
        with patch.object(self.service._source,'query',side_effect=AssertionError('legacy cache must be reusable')):
            self.assertEqual(self.service.create_analysis(self.body('null',{**self.query,'rose_cell_id':None})),original)
        with self.assertRaises(ClimateServiceError) as ctx:
            self.service.create_analysis(self.body('unsupported',{**self.query,'rose_cell_id':0}))
        self.assertEqual((ctx.exception.code,ctx.exception.status_code),('CLIMATE_UNSUPPORTED',422))
        self.assertEqual(self.counts(),(1,2,1))

    def test_source_missing_or_incompatible_does_not_destroy_saved_results(self):
        artifact=self.service.create_analysis(self.body())
        self.path.unlink()
        self.assertEqual(self.service.sources()['errors'][0]['code'],'CLIMATE_SOURCE_CHANGED')
        self.assertEqual(self.service.get_analysis(artifact['analysis_id']),artifact)
        self.assertEqual(self.service.create_analysis(self.body()),artifact)
        with self.assertRaises(ClimateServiceError) as ctx:
            self.service.create_analysis(self.body('new-request'))
        self.assertEqual(ctx.exception.status_code,409)
        invalid=self.root/'invalid.duckdb'
        invalid.write_bytes(b'not a DuckDB database')
        unavailable=ClimateService(self.root/'store',invalid)
        self.assertEqual(unavailable.sources()['sources'],[])
        self.assertEqual(unavailable.get_analysis(artifact['analysis_id']),artifact)

    def test_artifact_tampering_is_detected_and_never_repaired_silently(self):
        artifact=self.service.create_analysis(self.body())
        with closing(sqlite3.connect(self.service.database_path)) as con, con:
            row=con.execute('SELECT artifact_json FROM climate_analyses').fetchone()[0]
            changed=json.loads(row)
            changed['summary']['annual'][0]['mean_speed']+=1
            con.execute('UPDATE climate_analyses SET artifact_json=?',(json.dumps(changed),))
        for action in (lambda:self.service.get_analysis(artifact['analysis_id']),lambda:self.service.create_analysis(self.body()),lambda:self.service.create_analysis(self.body('new'))):
            with self.assertRaises(ClimateServiceError) as ctx:
                action()
            self.assertEqual(ctx.exception.code,'CLIMATE_CORRUPT')
        self.assertEqual(self.counts(),(1,1,1))

    def test_request_and_cache_binding_corruption_is_detected(self):
        artifact=self.service.create_analysis(self.body())
        with closing(sqlite3.connect(self.service.database_path)) as con, con:
            con.execute('UPDATE climate_requests SET binding_sha256=?',('0'*64,))
        with self.assertRaises(ClimateServiceError) as ctx:
            self.service.create_analysis(self.body())
        self.assertEqual(ctx.exception.code,'CLIMATE_CORRUPT')
        with closing(sqlite3.connect(self.service.database_path)) as con, con:
            con.execute('UPDATE climate_query_cache SET binding_sha256=?',('0'*64,))
        with self.assertRaises(ClimateServiceError) as ctx:
            self.service.create_analysis(self.body('new'))
        self.assertEqual(ctx.exception.code,'CLIMATE_CORRUPT')
        # The fixed artifact remains independently readable.
        self.assertEqual(self.service.get_analysis(artifact['analysis_id']),artifact)

    def test_source_guard_rejects_mid_aggregation_change_without_publication(self):
        changed=False
        def guard():
            if changed:
                raise ClimateServiceError('SOURCE_CHANGED','changed source',409)
        self.service._source_guard=guard
        original=self.service._source.query
        def change_after_query(query):
            nonlocal changed
            result=original(query)
            changed=True
            return result
        with patch.object(self.service._source,'query',side_effect=change_after_query):
            with self.assertRaises(ClimateServiceError) as ctx:
                self.service.create_analysis(self.body())
            self.assertEqual(ctx.exception.code,'SOURCE_CHANGED')
        self.assertEqual(self.counts(),(0,0,0))
        changed=False
        artifact=self.service.create_analysis(self.body())
        changed=True
        self.assertEqual(self.service.create_analysis(self.body()),artifact)
        self.assertEqual(self.service.get_analysis(artifact['analysis_id']),artifact)

    def test_new_source_code_fingerprint_does_not_relabel_old_artifact(self):
        old=self.service.create_analysis(self.body())
        snapshot=deepcopy(self.descriptor['source_code'])
        snapshot['files']['service.py']='a'*64
        snapshot['sha256']=hashlib.sha256(json.dumps(snapshot['files'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
        # Simulate a new registered code generation without modifying candidate files.
        with patch('backend.climate.source.adapter_source_snapshot',return_value=snapshot):
            restarted=ClimateService(self.root/'store',self.path)
            self.assertEqual(restarted.get_analysis(old['analysis_id']),old)
            self.assertEqual(restarted.create_analysis(self.body()),old)
            new=restarted.create_analysis(self.body('new-generation'))
            self.assertNotEqual(new['analysis_id'],old['analysis_id'])
            self.assertNotEqual(new['query_hash'],old['query_hash'])
            self.assertEqual(new['summary']['annual'],old['summary']['annual'])
        self.assertEqual(self.counts(),(2,2,2))

    def test_transaction_failure_leaves_no_half_published_result(self):
        with patch.object(self.service,'_bind_request',side_effect=RuntimeError('artificial interruption before acceptance')):
            with self.assertRaises(RuntimeError):
                self.service.create_analysis(self.body())
        self.assertEqual(self.counts(),(0,0,0))
        artifact=ClimateService(self.root/'store',self.path).create_analysis(self.body())
        self.assertEqual(self.counts(),(1,1,1))
        self.assertEqual(self.service.get_analysis(artifact['analysis_id']),artifact)

    def test_saved_get_is_not_locked_behind_duckdb_aggregation(self):
        artifact=self.service.create_analysis(self.body())
        entered,release,read_done=Event(),Event(),Event()
        original=self.service._source.query
        def delayed(query):
            entered.set()
            if not release.wait(10):
                raise RuntimeError('test release not received')
            return original(query)
        def saved_read():
            value=self.service.get_analysis(artifact['analysis_id'])
            read_done.set()
            return value
        with patch.object(self.service._source,'query',side_effect=delayed), ThreadPoolExecutor(max_workers=2) as pool:
            pending=pool.submit(self.service.create_analysis,self.body('level-1',{**self.query,'level_id':1}))
            self.assertTrue(entered.wait(5))
            reading=pool.submit(saved_read)
            try:
                self.assertTrue(read_done.wait(5),'fixed GET was blocked by work lock')
                self.assertEqual(reading.result(),artifact)
            finally:
                release.set()
            self.assertNotEqual(pending.result()['analysis_id'],artifact['analysis_id'])

    def test_two_instances_same_request_accept_only_one_transaction(self):
        other=ClimateService(self.root/'store',self.path)
        barrier=Barrier(2)
        first=self.service._source.query
        second=other._source.query
        def query1(query):
            barrier.wait(timeout=5)
            return first(query)
        def query2(query):
            barrier.wait(timeout=5)
            return second(query)
        with patch.object(self.service._source,'query',side_effect=query1),patch.object(other._source,'query',side_effect=query2),ThreadPoolExecutor(max_workers=2) as pool:
            a=pool.submit(self.service.create_analysis,self.body())
            b=pool.submit(other.create_analysis,self.body())
            self.assertEqual(a.result(),b.result())
        self.assertEqual(self.counts(),(1,1,1))

    def test_input_paths_sql_and_missing_store_do_not_create_hidden_state(self):
        for body in [self.body()|{'path':str(self.path)},self.body(query=self.query|{'sql':'select 1'}),{'client_request_id':'','query':self.query}]:
            with self.assertRaises(ClimateServiceError) as ctx:
                self.service.create_analysis(body)
            self.assertEqual(ctx.exception.status_code,422)
        with self.assertRaises(ClimateServiceError) as ctx:
            self.service.get_analysis('../other')
        self.assertEqual(ctx.exception.status_code,404)
        self.service.database_path.unlink()
        with self.assertRaises(ClimateServiceError) as ctx:
            self.service.get_analysis(str(uuid4()))
        self.assertEqual(ctx.exception.status_code,503)
        self.assertFalse(self.service.database_path.exists())


if __name__=='__main__':
    unittest.main()
