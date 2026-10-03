"""Shared raw-source contract, tested with small complete-calendar arrays."""
import hashlib
import json
from collections import Counter
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock

import numpy as np

from backend.climate.archive import WindArchiveSource, isa_height
from backend.climate.contracts import ClimateError, ClimateQuery, Bounds
from backend.climate.samples import expected_times
from backend.climate.service import ClimateService


def archive_fixture(root, provider='ERA5'):
    root.mkdir(parents=True,exist_ok=True)
    grid=[{'cell_id':i,'lat':40.+i//2,'lon':140.+i%2,'weight':[1.,2.,3.,4.][i]} for i in range(4)]
    m={'schema':'balloon.wind-samples/1','provider':provider,'label':provider+' 2024 test',
       'years':[2024,2024],'date_convention':'UTC','hours_utc':[0,6,12,18],
       'weighting':'spherical-area-equal-times' if provider=='ERA5' else 'gaussian-area-equal-times',
       'grid':grid,'levels':[{'level_id':0,'level_hpa':1.},{'level_id':1,'level_hpa':1000.}],
       'months':[],'provenance':{'dataset_url':'https://example.invalid/offline-fixture'}}
    for month in range(1,13):
        times=expected_times(month,[2024,2024]); item={'month':month,'times_utc':times}
        u=np.empty((len(times),2,4),dtype='float32')
        for i,t in enumerate(times):
            u[i,:,:]=month+int(t[8:10])*.25+int(t[11:13])*.5+np.arange(4)
        if month==1:u[0,:,0]=0
        for component,a in [('u',u),('v',np.zeros_like(u))]:
            file=root/f'{month:02d}-{component}.npy';np.save(file,a,allow_pickle=False)
            item[component]={'file':file.name,'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
        m['months'].append(item)
    path=root/'manifest.json';path.write_text(json.dumps(m),encoding='utf8')
    return path


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='wind-archive-')
        self.root=Path(self.temp.name)
        self.path=archive_fixture(self.root/'era')
        self.source=WindArchiveSource(self.path)

    def tearDown(self):self.temp.cleanup()

    def test_calendar_high_altitude_hour_selection_and_weighted_population(self):
        q=ClimateQuery(self.source.source_id,0,Bounds(141,141,40,41),hours_utc=[0])
        a=self.source.query(q)
        self.assertEqual(a['population']['years_fixed'],[2024,2024])
        self.assertEqual(a['population']['selected_cell_ids'],[1,3])
        self.assertEqual(len(a['levels']),2)
        month=a['summaries_by_grain']['month'];feb=next(r for r in month['annual'] if r['timebin_id']==1 and r['level_id']==0)
        self.assertEqual(feb['time_count'],29)
        # At 00 UTC: February 2 + mean(day)*.25 + weighted cell index.
        expected=2+15*.25+(1*2+3*4)/6
        self.assertAlmostEqual(feb['mean_speed'],expected)
        self.assertEqual(a['monthly_profiles']['months'][1]['half_time_counts'],[15,14])
        self.assertEqual(a['monthly_profiles']['population']['years_fixed'],[2024,2024])
        self.assertIsNone(a['levels'][0]['alt_geom_mean_m'])
        self.assertGreater(a['levels'][0]['isa_alt_m'],47000)

    def test_wind_rose_accounts_for_calm_and_native_hour_filter(self):
        a=self.source.query(ClimateQuery(self.source.source_id,0,hours_utc=[0]))
        rose=a['summaries_by_grain']['month']['wind_rose']
        self.assertEqual(rose['native_hours_utc'],[0])
        jan=next(x for x in rose['calm_counts'] if x['timebin_id']==0)
        self.assertEqual(jan['count'],1)
        self.assertEqual(sum(r['count'] for r in rose['rows'] if r['timebin_id']==0)+jan['count'],31)
        self.assertAlmostEqual(sum(r['frequency'] for r in rose['rows'] if r['timebin_id']==0)+jan['frequency'],1)
        self.assertTrue(all(r['sector']==12 for r in rose['rows'] if r['count']))

    def test_native_point_id_is_not_array_index_and_region_cache_is_reused(self):
        manifest=json.loads(self.path.read_bytes())
        ids=[40,7,901,25]
        for cell,cell_id in zip(manifest['grid'],ids):cell['cell_id']=cell_id
        self.path.write_text(json.dumps(manifest),encoding='utf8')
        source=WindArchiveSource(self.path)
        default_point=source.descriptor()['wind_rose_point']
        self.assertTrue(source.descriptor()['capabilities']['wind_rose_point_select'])
        self.assertEqual(default_point['cell_id'],40)
        # The region contains only array column 0; wind rose may use column 3 outside it.
        base=dict(source_id=source.source_id,level_id=0,bounds=Bounds(140,140,40,40),hours_utc=[0])
        default=source.query(ClimateQuery(**base))
        with patch.object(source,'_moments',side_effect=AssertionError('point switch must reuse regional moments')), \
             patch.object(source._samples,'profiles',side_effect=AssertionError('point switch must reuse profiles')):
            selected=source.query(ClimateQuery(**base,rose_cell_id=25))
            again=source.query(ClimateQuery(**base))
        self.assertEqual(default,again)
        self.assertEqual(source.descriptor()['wind_rose_point'],default_point)
        self.assertNotIn('rose_cell_id',default['query'])
        self.assertEqual(selected['query']['rose_cell_id'],25)
        self.assertEqual(selected['population']['selected_cell_ids'],[40])
        for key in ('population','levels','annual','spatial','display_scales','monthly_profiles','source'):
            self.assertEqual(selected[key],default[key],key)
        for grain in ('month','season'):
            for key in ('timebins','annual','spatial_rows','display_scales'):
                self.assertEqual(selected['summaries_by_grain'][grain][key],default['summaries_by_grain'][grain][key])
        self.assertNotEqual(selected['wind_rose']['rows'],default['wind_rose']['rows'])
        # Independent scalar fixture counting, without adapter binning/period helpers.
        groups=[selected,*selected['summaries_by_grain'].values()]
        for group in groups:
            rose=group['wind_rose']
            self.assertEqual(rose['point'],{'cell_id':25,'lat':41.,'lon':141.})
            self.assertFalse(rose['point_in_selected_region'])
            for period in group.get('timebins',selected['population']['timebins']):
                expected=Counter()
                for month in manifest['months']:
                    for t in month['times_utc']:
                        half_id=(month['month']-1)*2+(int(t[8:10])>15)
                        if int(t[11:13])!=0 or half_id not in period['member_timebin_ids']:continue
                        speed=month['month']+int(t[8:10])*.25+3
                        expected[(12,sum(speed>=edge for edge in (5,10,20,30,50)))]+=1
                rows=[r for r in rose['rows'] if r['timebin_id']==period['timebin_id']]
                n=sum(expected.values())
                for row in rows:
                    self.assertEqual(row['count'],expected[(row['sector'],row['speed_class'])])
                    self.assertEqual(row['time_count'],n)
                    self.assertEqual(row['frequency'],row['count']/n)
                calm=next(r for r in rose['calm_counts'] if r['timebin_id']==period['timebin_id'])
                self.assertEqual(calm['count'],0)
        # A second nonconsecutive ID maps to its own native column, not ID 7 as an index.
        other=source.query(ClimateQuery(**base,rose_cell_id=7))
        self.assertEqual(other['wind_rose']['point'],{'cell_id':7,'lat':40.,'lon':141.})
        self.assertEqual(source.descriptor()['wind_rose_point'],default_point)
        self.assertTrue(default['wind_rose']['point_in_selected_region'])

    def test_unknown_native_point_is_rejected_before_loading_samples(self):
        with patch.object(self.source,'_moments',side_effect=AssertionError('invalid point must not aggregate')):
            with self.assertRaises(ClimateError) as ctx:
                self.source.query(ClimateQuery(self.source.source_id,0,rose_cell_id=99))
        self.assertEqual(ctx.exception.code,'CLIMATE_SUPPORT')

    def test_selected_point_is_bound_to_saved_request_and_offline_retry(self):
        service=ClimateService(self.root/'point-store',archive_paths=[self.path])
        query=ClimateQuery(service.sources()['sources'][0]['source_id'],0).as_dict()
        original=service.create_analysis({'client_request_id':'omitted','query':query})
        self.assertNotIn('rose_cell_id',original['query'])
        archive=next(iter(service._archives.values()))
        with patch.object(archive,'query',side_effect=AssertionError('null must preserve old cache key')):
            null=service.create_analysis({'client_request_id':'null','query':{**query,'rose_cell_id':None}})
        self.assertEqual(null,original)
        selected_body={'client_request_id':'selected','query':{**query,'rose_cell_id':3}}
        selected=service.create_analysis(selected_body)
        self.assertNotEqual(selected['analysis_id'],original['analysis_id'])
        self.assertEqual(selected['summary']['wind_rose']['point']['cell_id'],3)
        with patch.object(archive,'query',side_effect=AssertionError('point-aware cache must survive new request ID')):
            cached=service.create_analysis({**selected_body,'client_request_id':'selected-again'})
        self.assertEqual(cached,selected)
        offline=ClimateService(self.root/'point-store')
        for artifact,body in [(original,{'client_request_id':'omitted','query':query}),(selected,selected_body)]:
            self.assertEqual(offline.get_analysis(artifact['analysis_id']),artifact)
            self.assertEqual(offline.create_analysis(body),artifact)
        with self.assertRaises(ClimateError) as ctx:
            offline.create_analysis({**selected_body,'query':{**query,'rose_cell_id':2}})
        self.assertEqual(ctx.exception.code,'CLIMATE_IDEMPOTENCY')

    def test_complete_month_requirement_and_io_failure_are_explicit(self):
        with patch('backend.climate.archive.np.load',side_effect=OSError('read error')):
            with self.assertRaises(ClimateError) as c:self.source.query(ClimateQuery(self.source.source_id,0))
        self.assertEqual(c.exception.code,'CLIMATE_SAMPLES')
        m=json.loads(self.path.read_text());m['months'].pop();self.path.write_text(json.dumps(m))
        with self.assertRaises(ClimateError) as c:WindArchiveSource(self.path)
        self.assertEqual(c.exception.code,'CLIMATE_COUNTS')

    def test_two_providers_are_distinct_and_saved_read_requires_neither(self):
        jra=archive_fixture(self.root/'jra','JRA-3Q')
        service=ClimateService(self.root/'store',archive_paths=[self.path,jra])
        catalog=service.sources();self.assertEqual(len(catalog['sources']),2);self.assertEqual(catalog['errors'],[])
        self.assertEqual({d['provider'] for d in catalog['sources']},{'ERA5','JRA-3Q'})
        results=[service.create_analysis({'client_request_id':str(i),'query':ClimateQuery(d['source_id'],0).as_dict()})
                 for i,d in enumerate(catalog['sources'])]
        self.assertNotEqual(results[0]['analysis_id'],results[1]['analysis_id'])
        offline=ClimateService(self.root/'store')
        for a in results:self.assertEqual(offline.get_analysis(a['analysis_id']),a)

    def test_original_attribution_survives_saved_read_without_the_archive(self):
        m=json.loads(self.path.read_bytes())
        credit={'license':'CC BY 4.0','acknowledgement':'Original provider credit'}
        m['provenance'].update(dataset_doi='10.example/archive',attribution=credit)
        self.path.write_text(json.dumps(m),encoding='utf8')
        service=ClimateService(self.root/'credit-store',archive_paths=[self.path])
        descriptor=service.sources()['sources'][0]
        a=service.create_analysis({'client_request_id':'credit',
            'query':ClimateQuery(descriptor['source_id'],0).as_dict()})
        saved=ClimateService(self.root/'credit-store').get_analysis(a['analysis_id'])
        metadata=saved['summary']['source']['attribution']['metadata']
        self.assertEqual(metadata['dataset_doi'],'10.example/archive')
        self.assertEqual(metadata['attribution'],credit)
        self.assertEqual(metadata['dataset_url'],'https://example.invalid/offline-fixture')

    def test_display_height_matches_standard_layer_boundaries(self):
        self.assertAlmostEqual(isa_height(1013.25),0)
        self.assertAlmostEqual(isa_height(226.3204),11000,places=1)
        self.assertAlmostEqual(isa_height(54.7489),20000,places=1)

    def test_one_bad_source_is_reported_without_hiding_valid_raw_source(self):
        service=ClimateService(self.root/'mixed-store',source_path=self.root/'missing.db',archive_paths=[self.path])
        self.assertEqual(len(service.sources()['sources']),1)
        self.assertEqual(service.sources()['errors'][0]['code'],'CLIMATE_SOURCE_CHANGED')
        legacy=Mock(source_id='legacy');service._source=legacy
        with self.assertRaises(ClimateError) as c:service.verify_source('unknown')
        self.assertEqual(c.exception.code,'CLIMATE_SOURCE_CHANGED')
        legacy.verify_full.assert_not_called()

    def test_numerical_library_change_recomputes_new_request_but_preserves_accepted_retry(self):
        service=ClimateService(self.root/'version-store',archive_paths=[self.path])
        query=ClimateQuery(service.sources()['sources'][0]['source_id'],0).as_dict()
        original=service.create_analysis({'client_request_id':'original','query':query})
        with patch('backend.climate.archive.np.__version__','new-test-version'):
            changed=ClimateService(self.root/'version-store',archive_paths=[self.path])
            repeated=changed.create_analysis({'client_request_id':'original','query':query})
            self.assertEqual(repeated,original)
            new=changed.create_analysis({'client_request_id':'new-version','query':query})
            self.assertNotEqual(new['analysis_id'],original['analysis_id'])
            self.assertEqual(new['summary']['source']['numerical_dependencies']['numpy'],'new-test-version')


if __name__=='__main__':unittest.main()
