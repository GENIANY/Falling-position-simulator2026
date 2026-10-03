"""Only registered completed assets donate raw; all network/GRIB inputs are local."""
import copy
from datetime import timedelta
import hashlib
from pathlib import Path

import pytest

from backend.tests.test_weather import DirectoryGateway, RUN, deps, request, wait_job
from backend.weather.service import WeatherService
from backend.worker import REPO_ROOT
from backend.storage import file_hash
from balloon_sim.environment import gfs
from balloon_sim.environment.fields import _utc
from balloon_sim.environment.storage import read_json


@pytest.fixture
def offline_acquisition(monkeypatch):
    calls=[];decoded=[]
    def download(url,path,remaining,**kwargs):
        data=b'GRIB'+path.name.encode()
        assert len(data)<=remaining
        path.write_bytes(data);calls.append(path.name)
        return {'file':path.name,'url':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
                'headers':{'ETag':'first observation'},'started_at_utc':RUN,'completed_at_utc':RUN}
    def decode(paths,spec,provenance):
        bundle=read_json(REPO_ROOT/'references/flight_fixture/wakayama-weather.json.gz')
        times=[(_utc(spec['run_utc'])+timedelta(hours=lead)).isoformat() for lead in spec['lead_hours']]
        indices=[bundle['axes']['time_utc'].index(t) for t in times]
        bundle['axes']['time_utc']=times
        for category in ('fields','surface'):
            bundle[category]={name:[values[i] for i in indices] for name,values in bundle[category].items()}
        bundle['metadata']['request']=copy.deepcopy(spec)
        bundle['metadata']['provenance']=copy.deepcopy(provenance)
        decoded.append((len(paths),copy.deepcopy(provenance)))
        return bundle
    monkeypatch.setattr(gfs,'_decoder_identity',lambda:{'test':'current decoder'})
    monkeypatch.setattr(gfs,'_download',download)
    monkeypatch.setattr(gfs,'decode_gfs',decode)
    return calls,decoded


def planned(weather, duration):
    inventory=weather.refresh_inventory({'run_utc':RUN})
    return weather.plan(request(inventory['inventory_id'],candidate_windows=[{
        'candidate_id':'C1','launch_time_utc':'2026-09-23T03:30:00Z','max_duration_s':duration}]))


def start(weather,plan,label):
    job=weather.submit({'plan_id':plan['plan_id'],'client_request_id':label})
    return wait_job(weather,job['acquisition_id'])


def test_registered_six_to_seven_downloads_only_missing_and_keeps_old_asset(tmp_path,offline_acquisition):
    calls,decoded=offline_acquisition
    weather=WeatherService(tmp_path,gateway=DirectoryGateway(),dependency_check=deps,source_guard=lambda:None).start()
    try:
        first=start(weather,planned(weather,16200),'six');assert first['state']=='completed',first
        folder=weather.root/'acquisitions'/first['acquisition_id']
        original={p.name:file_hash(p) for p in folder.iterdir() if p.is_file()}
        assert calls==[f'f{x:03d}.grib2' for x in range(9,15)]
        plan=planned(weather,19800)
        second=start(weather,plan,'seven');assert second['state']=='completed',second
        assert calls==[f'f{x:03d}.grib2' for x in range(9,16)]
        assert second['reused'] is False and first['weather_source_id']!=second['weather_source_id']
        assert second['progress']['bytes_downloaded']==len(b'GRIBf015.grib2')
        assert second['progress']['bytes_reused']==6*len(b'GRIBf009.grib2')
        assert decoded[-1][0]==7 and all('reuse_history' in row for row in decoded[-1][1][:6])
        assert original=={p.name:file_hash(p) for p in folder.iterdir() if p.is_file()}
        third=start(weather,plan,'same-seven')
        assert third['state']=='completed' and third['reused'] is True
        assert third['progress']['bytes_downloaded']==0 and len(calls)==7
    finally:weather.close()


def test_corrupt_matching_donor_refuses_before_new_transfer(tmp_path,offline_acquisition):
    calls,_=offline_acquisition
    weather=WeatherService(tmp_path,gateway=DirectoryGateway(),dependency_check=deps,source_guard=lambda:None).start()
    try:
        first=start(weather,planned(weather,16200),'six')
        raw=weather.root/'acquisitions'/first['acquisition_id']/'f013.grib2';raw.write_bytes(b'GRIB corrupt')
        second=start(weather,planned(weather,19800),'seven')
        assert second['state']=='failed' and second['error']['code']=='RAW_HASH_MISMATCH'
        assert len(calls)==6 and second['weather_source_id'] is None
        assert not (weather.root/'acquisitions'/second['acquisition_id']/'ASSET.json').exists()
        assert raw.read_bytes()==b'GRIB corrupt'
    finally:weather.close()


def test_marker_failure_is_not_a_cache_miss(tmp_path,offline_acquisition):
    calls,_=offline_acquisition
    weather=WeatherService(tmp_path,gateway=DirectoryGateway(),dependency_check=deps,source_guard=lambda:None).start()
    try:
        first=start(weather,planned(weather,16200),'six')
        marker=weather.root/'acquisitions'/first['acquisition_id']/'ASSET.json';marker.write_bytes(b'changed marker')
        second=start(weather,planned(weather,19800),'seven')
        assert second['state']=='failed' and second['error']['code']=='ASSET_INTEGRITY_ERROR'
        assert len(calls)==6
    finally:weather.close()


def test_unregistered_raw_directory_cannot_donate(tmp_path,offline_acquisition):
    calls,_=offline_acquisition
    weather=WeatherService(tmp_path,gateway=DirectoryGateway(),dependency_check=deps,source_guard=lambda:None).start()
    try:
        orphan=weather.root/'acquisitions'/'unregistered';orphan.mkdir()
        (orphan/'f009.grib2').write_bytes(b'GRIB incomplete unregistered')
        completed=start(weather,planned(weather,19800),'seven')
        assert completed['state']=='completed' and len(calls)==7
        assert completed['progress']['bytes_reused']==0
        assert (orphan/'f009.grib2').read_bytes()==b'GRIB incomplete unregistered'
    finally:weather.close()


def test_wrong_run_bounds_or_full_selectors_are_cache_misses(tmp_path,offline_acquisition,monkeypatch):
    weather=WeatherService(tmp_path,gateway=DirectoryGateway(),dependency_check=deps,source_guard=lambda:None).start()
    try:
        first=start(weather,planned(weather,16200),'six');assert first['state']=='completed'
        with weather._guard:asset=copy.deepcopy(weather._list('asset')[0])
        target=gfs._request({'run_utc':RUN,'start_utc':'2026-09-23T03:00:00Z','end_utc':'2026-09-23T09:00:00Z',
                             'bounds':{'west':135.,'east':136.25,'south':33.5,'north':34.75}})
        assert len(list(weather._raw_donors(target,[9,10])))==2
        for kind in ('run','bounds','selectors'):
            changed=copy.deepcopy(asset)
            if kind=='run':changed['snapshot']['metadata']['request']['run_utc']='2026-09-22T12:00:00+00:00'
            if kind=='bounds':changed['snapshot']['metadata']['request']['bounds']['west']+=.25
            if kind=='selectors':
                for row in changed['snapshot']['metadata']['provenance']:row['url']+='&var_FOO=on'
            monkeypatch.setattr(weather,'_list',lambda key:[changed])
            assert list(weather._raw_donors(target,[9,10]))==[]
    finally:weather.close()