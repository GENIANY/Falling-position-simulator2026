"""Cross-window raw reuse counterexamples; all transport/decoding are local fakes."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from balloon_sim.environment import gfs
from balloon_sim.environment.fields import WeatherError


def request(end=6, **extra):
    return {'run_utc':'2026-09-29T00:00:00Z','start_utc':'2026-09-29T00:00:00Z',
            'end_utc':f'2026-09-29T{end:02d}:00:00Z',
            'bounds':{'west':135.,'east':135.25,'south':33.,'north':33.25},**extra}


def payload(lead):
    return b'GRIB'+str(lead).encode()*30


def donors(root, leads=range(6), variant=b''):
    root.mkdir()
    spec=gfs._request(request())
    result=[]
    for lead in leads:
        data=payload(lead)+variant; path=root/f'f{lead:03d}.grib2';path.write_bytes(data)
        item={'file':path.name,'url':gfs._url(spec,lead),'bytes':len(data),
              'sha256':hashlib.sha256(data).hexdigest(),'headers':{'ETag':'old'},
              'started_at_utc':'2026-09-29T00:01:00Z','completed_at_utc':'2026-09-29T00:01:01Z'}
        result.append({'lead_hours':lead,'path':path,'provenance':item,
                       'donor':{'asset_id':root.name,'acquisition_id':root.name,'bundle_sha256':'b'*64,'marker_sha256':'c'*64}})
    return result


def fake_download(url,path,remaining,**kwargs):
    lead=int(path.stem[1:]);data=payload(lead)
    if len(data)>remaining:raise WeatherError('DOWNLOAD_LIMIT','fake checked limit')
    path.write_bytes(data)
    return {'file':path.name,'url':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}


class RawReuseTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.identity=patch.object(gfs,'_decoder_identity',return_value={'test':'new decoder'})
        self.identity.start();self.addCleanup(self.identity.stop)
        self.decoded=[]
        def decode(paths,spec,provenance):
            self.decoded.append({'raw':[p.read_bytes() for p in paths],'spec':copy.deepcopy(spec),'provenance':copy.deepcopy(provenance)})
            return {'physical_inputs':[p.read_bytes().hex() for p in paths],'provenance':provenance}
        d=patch.object(gfs,'decode_gfs',side_effect=decode);self.decoder=d.start();self.addCleanup(d.stop)
        # Real deterministic gzip writer is retained: provenance changes bundle bytes.
        download=patch.object(gfs,'_download',side_effect=fake_download)
        self.download=download.start();self.addCleanup(download.stop)

    def test_six_to_seven_one_transfer_and_full_current_decode(self):
        rows=donors(self.root/'registered');old={str(x['path']):x['path'].read_bytes() for x in rows}
        changes=[];used=gfs.acquire_gfs(request(),self.root/'reused',raw_provider=lambda *_:rows,progress=changes.append)
        self.assertEqual(self.download.call_count,1)
        self.assertEqual(self.download.call_args.args[1].name,'f006.grib2')
        self.assertEqual(self.decoded[-1]['raw'],[payload(x) for x in range(7)])
        self.assertEqual(changes[-1]['bytes_reused'],sum(len(payload(x)) for x in range(6)))
        self.assertEqual(changes[-1]['bytes_downloaded'],len(payload(6)))
        for entry in self.decoded[-1]['provenance'][:6]:
            self.assertEqual(entry['headers'],{'ETag':'old'});self.assertEqual(entry['started_at_utc'],'2026-09-29T00:01:00Z')
            self.assertEqual(len(entry['reuse_history']),1)
        fresh=gfs.acquire_gfs(request(),self.root/'fresh')
        self.assertEqual(self.decoded[0]['raw'],self.decoded[1]['raw'])
        self.assertNotEqual(used.read_bytes(),fresh.read_bytes())
        for path,data in old.items():self.assertEqual(Path(path).read_bytes(),data)
        # Independent copies: altering a new output does not alter its donor.
        (used.parent/'f000.grib2').write_bytes(b'modified new raw')
        self.assertEqual(rows[0]['path'].read_bytes(),payload(0))

    def test_corrupt_future_donor_refuses_before_any_http(self):
        rows=donors(self.root/'registered',[5]);rows[0]['path'].write_bytes(b'GRIBcorrupt')
        with self.assertRaises(WeatherError) as caught:gfs.acquire_gfs(request(),self.root/'run',raw_provider=lambda *_:rows)
        self.assertEqual(caught.exception.code,'RAW_HASH_MISMATCH');self.download.assert_not_called()
        self.assertFalse((self.root/'run/weather.json.gz').exists())

    def test_same_request_different_bytes_is_ambiguous_before_http(self):
        a=donors(self.root/'a',[5]);b=donors(self.root/'b',[5],b'variant')
        with self.assertRaises(WeatherError) as caught:gfs.acquire_gfs(request(),self.root/'run',raw_provider=lambda *_:a+b)
        self.assertEqual(caught.exception.code,'AMBIGUOUS_SAVED_RAW');self.download.assert_not_called()

    def test_identical_bytes_have_one_deterministic_donor(self):
        a=donors(self.root/'a',[0]);b=donors(self.root/'b',[0])
        gfs.acquire_gfs(request(1),self.root/'run',raw_provider=lambda *_:a+b)
        self.assertEqual(self.download.call_count,1)
        self.assertEqual(self.decoded[-1]['provenance'][0]['reuse_history'][0]['asset_id'],'a')

    def test_raw_input_budget_includes_all_known_copies_before_http(self):
        rows=donors(self.root/'registered',[0,1])
        for row in rows:
            data=b'GRIB'+b'x'*600;row['path'].write_bytes(data)
            row['provenance'].update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
        with self.assertRaises(WeatherError) as caught:gfs.acquire_gfs(request(2,max_bytes=1024),self.root/'run',raw_provider=lambda *_:rows)
        self.assertEqual(caught.exception.code,'DOWNLOAD_LIMIT');self.download.assert_not_called()

    def test_completed_resume_still_rejects_excess_retained_partial(self):
        folder=self.root/'run'
        gfs.acquire_gfs(request(1,max_bytes=1024),folder)
        before=(folder/'weather.json.gz').read_bytes()
        (folder/'f001.grib2.retained.partial').write_bytes(b'x'*1024)
        self.download.reset_mock()
        with self.assertRaises(WeatherError) as caught:
            gfs.acquire_gfs(request(1,max_bytes=1024),folder,resume=True)
        self.assertEqual(caught.exception.code,'DOWNLOAD_LIMIT')
        self.download.assert_not_called()
        self.assertEqual((folder/'weather.json.gz').read_bytes(),before)

    def test_later_copy_budget_is_reserved_from_earlier_download(self):
        rows=donors(self.root/'registered',[1]);size=rows[0]['provenance']['bytes']
        gfs.acquire_gfs(request(1,max_bytes=1024),self.root/'run',raw_provider=lambda *_:rows)
        self.assertEqual(self.download.call_args.args[2],1024-size)

    def test_url_identity_rejects_changed_run_selector_or_rectangle(self):
        for name,suffix in [('run','/other'),('selector','&var_FOO=on'),('rectangle','&leftlon=135.5')]:
            with self.subTest(name=name):
                rows=donors(self.root/name,[0]);rows[0]['provenance']['url']+=suffix
                with self.assertRaises(WeatherError) as caught:gfs.acquire_gfs(request(1),self.root/(name+'run'),raw_provider=lambda *_:rows)
                self.assertEqual(caught.exception.code,'RAW_REUSE_IDENTITY_MISMATCH')
        self.download.assert_not_called()

    def test_copy_cancel_keeps_partial_without_http_bytes_and_can_resume(self):
        rows=donors(self.root/'registered',[0]);data=b'GRIB'+b'a'*150000
        rows[0]['path'].write_bytes(data);rows[0]['provenance'].update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
        cancel=threading.Event()
        original_open=Path.open
        class Reader:
            def __init__(self,stream):self.stream=stream;self.count=0
            def __enter__(self):return self
            def __exit__(self,*args):self.stream.close()
            def read(self,n=-1):
                value=self.stream.read(n);self.count+=len(value)
                if n==65536 and self.count==65536:cancel.set()
                return value
        # Only copy has source read(65536) without the verifier's initial read(4).
        def opening(path,*args,**kwargs):
            stream=original_open(path,*args,**kwargs)
            return Reader(stream) if path==rows[0]['path'] and args==('rb',) else stream
        with patch.object(Path,'open',opening):
            with self.assertRaises(WeatherError) as caught:gfs.acquire_gfs(request(1),self.root/'run',raw_provider=lambda *_:rows,cancel=cancel)
        self.assertEqual(caught.exception.code,'ACQUISITION_CANCELLED');self.download.assert_not_called()
        failure=json.loads((self.root/'run/failure.json').read_text())
        self.assertEqual(failure['bytes_downloaded'],0);self.assertEqual(failure['bytes_reused'],0)
        self.assertGreater(failure['retained_partial_bytes'],0)
        cancel.clear();gfs.acquire_gfs(request(1),self.root/'run',resume=True,raw_provider=lambda *_:rows,cancel=cancel)
        self.assertEqual(self.download.call_count,1);self.assertEqual(rows[0]['path'].read_bytes(),data)

    def test_corrupted_destination_readback_refuses_before_publication(self):
        rows=donors(self.root/'registered',[0]);original_open=Path.open;broken=[]
        def opening(path,*args,**kwargs):
            if path.name.endswith('.reuse.partial') and args==('rb',) and not broken:
                with original_open(path,'r+b') as bad:bad.write(b'BAD!')
                broken.append(True)
            return original_open(path,*args,**kwargs)
        with patch.object(Path,'open',opening):
            with self.assertRaises(WeatherError) as caught:
                gfs.acquire_gfs(request(1),self.root/'run',raw_provider=lambda *_:rows)
        self.assertEqual(caught.exception.code,'RAW_HASH_MISMATCH')
        self.assertTrue(broken);self.download.assert_not_called();self.decoder.assert_not_called()
        self.assertFalse((self.root/'run/f000.grib2').exists())
        self.assertFalse((self.root/'run/weather.json.gz').exists())
        self.assertEqual(rows[0]['path'].read_bytes(),payload(0))
        failure=json.loads((self.root/'run/failure.json').read_text())
        self.assertEqual(failure['bytes_downloaded'],0)
        self.assertEqual(failure['bytes_reused'],0)

    def test_source_change_between_check_and_copy_does_not_fall_back(self):
        rows=donors(self.root/'registered',[0]);changed=[]
        def progress(update):
            if update['phase']=='reusing_raw' and not changed:
                rows[0]['path'].write_bytes(b'GRIB changed');changed.append(True)
        with self.assertRaises(WeatherError) as caught:gfs.acquire_gfs(request(1),self.root/'run',raw_provider=lambda *_:rows,progress=progress)
        self.assertEqual(caught.exception.code,'RAW_HASH_MISMATCH');self.download.assert_not_called()

    def test_existing_prefix_limits_provider_to_missing_leads(self):
        rows=donors(self.root/'registered',[0]);folder=self.root/'run';seen=[]
        with patch.object(gfs,'decode_gfs',side_effect=WeatherError('BAD_CURRENT_DECODE','test')):
            with self.assertRaises(WeatherError):gfs.acquire_gfs(request(1),folder,raw_provider=lambda *_:rows)
        self.assertFalse((folder/'weather.json.gz').exists())
        rows[0]['path'].write_bytes(b'corrupt original after prior complete copy')
        def provider(spec,needed):seen.append(needed);raise AssertionError('all local prefix means no donor scan')
        gfs.acquire_gfs(request(1),folder,resume=True,raw_provider=provider)
        self.assertEqual(seen,[]);self.assertEqual(self.download.call_count,1)

    def test_unreceipted_copied_raw_is_preserved_not_trusted(self):
        rows=donors(self.root/'registered',[0]);folder=self.root/'run'
        with patch.object(gfs.os,'replace',side_effect=lambda source,target:(_ for _ in ()).throw(OSError('receipt')) if Path(target).name=='provenance.json' and Path(source).stat().st_size>5 else source.rename(target)):
            with self.assertRaises(OSError):gfs.acquire_gfs(request(1),folder,raw_provider=lambda *_:rows)
        self.assertTrue((folder/'f000.grib2').exists())
        gfs.acquire_gfs(request(1),folder,resume=True,raw_provider=lambda *_:rows)
        partial=list(folder.glob('f000.grib2.*.partial'))
        self.assertEqual(len(partial),1);self.assertEqual(partial[0].read_bytes(),payload(0))
        self.assertEqual(self.download.call_count,1)


if __name__=='__main__':unittest.main()