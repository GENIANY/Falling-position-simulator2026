"""Operational failure/retry boundaries; all HTTP and decoder inputs are local."""
import hashlib
import io
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
import urllib.error

from balloon_sim.environment.fields import WeatherError
from balloon_sim.environment.gfs import acquire_gfs
from balloon_sim.environment.nomads import NomadsGateway

URL="https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl"


class Clock:
    def __init__(self): self.time=1_000.
    def now(self): return self.time
    def sleep(self, seconds): self.time+=seconds


class Response(io.BytesIO):
    status=200
    def __init__(self,data,headers=None):
        super().__init__(data); self.headers=headers or {}


class NomadsTransportTest(unittest.TestCase):
    def test_shared_schedule_waits_after_success_and_failed_response(self):
        with tempfile.TemporaryDirectory() as tmp:
            clock=Clock(); calls=[]
            def opened(*args,**kwargs):
                calls.append(clock.now()); clock.sleep(3)
                return Response(b'abc')
            a=NomadsGateway(tmp,opener=opened,clock=clock.now,sleep=clock.sleep)
            b=NomadsGateway(tmp,opener=opened,clock=clock.now,sleep=clock.sleep)
            self.assertEqual(a.fetch(URL,100)[0],b'abc')
            b.fetch(URL,100)
            self.assertGreaterEqual(calls[1]-calls[0],13)
            def limited(*args,**kwargs):
                raise urllib.error.HTTPError(URL,429,'limit',{'Retry-After':'25'},None)
            c=NomadsGateway(tmp,opener=limited,clock=clock.now,sleep=clock.sleep)
            with self.assertRaises(WeatherError): c.fetch(URL,100)
            end=clock.now(); a.fetch(URL,100)
            self.assertGreaterEqual(calls[-1]-end,25)

    def test_cancel_wait_and_foreign_origin_never_contact_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            opener=unittest.mock.Mock(side_effect=AssertionError('no HTTP'))
            clock=Clock(); cancel=threading.Event()
            def wait(seconds): clock.sleep(seconds); cancel.set()
            gateway=NomadsGateway(tmp,opener=opener,clock=clock.now,sleep=wait)
            gateway._reserve(clock.now()+10)
            with self.assertRaises(WeatherError) as caught: gateway.fetch(URL,100,cancel)
            self.assertEqual(caught.exception.code,'ACQUISITION_CANCELLED')
            with self.assertRaises(WeatherError): gateway.fetch('https://example.invalid/',100)
            opener.assert_not_called()

    def test_truncated_length_and_stream_limit(self):
        for payload, headers, limit, code in [(b'abc',{'Content-Length':'5'},10,'INCOMPLETE_DOWNLOAD'),
                                              (b'abcde',{},4,'DOWNLOAD_LIMIT')]:
            with self.subTest(code=code), tempfile.TemporaryDirectory() as tmp:
                gateway=NomadsGateway(tmp,opener=lambda *a,**k:Response(payload,headers))
                partial=Path(tmp)/'raw.partial'
                with self.assertRaises(WeatherError) as caught: gateway.download_to(URL,partial,limit)
                self.assertEqual(caught.exception.code,code)
                self.assertLessEqual(partial.stat().st_size,limit)

    def test_unclean_owner_waits_again_and_slow_stream_has_deadline(self):
        with tempfile.TemporaryDirectory() as tmp:
            clock=Clock(); calls=[]
            class Slow(Response):
                def read1(self,size): clock.sleep(40); return b'x'
            def opened(*a,**k): calls.append(clock.now()); return Slow(b'')
            gateway=NomadsGateway(tmp,opener=opened,clock=clock.now,sleep=clock.sleep,monotonic=clock.now)
            gateway._reserve(clock.now()-500,in_flight=True)
            before=clock.now()
            with self.assertRaises(WeatherError) as caught: gateway.fetch(URL,100)
            self.assertEqual(caught.exception.code,'DOWNLOAD_TIMEOUT')
            self.assertGreaterEqual(calls[0]-before,10)


class AcquisitionResumeTest(unittest.TestCase):
    def request(self):
        return {'run_utc':'2026-09-29T00:00:00Z','start_utc':'2026-09-29T00:00:00Z',
                'end_utc':'2026-09-29T01:00:00Z','bounds':{'west':135.,'east':135.25,'south':33.,'north':33.25}}

    @staticmethod
    def download(url,path,remaining,**kwargs):
        data=b'GRIB local complete bytes'
        path.write_bytes(data)
        return {'file':path.name,'url':url,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}

    def test_retry_reuses_only_verified_prefix_and_never_replaces_request(self):
        with tempfile.TemporaryDirectory() as tmp, patch('balloon_sim.environment.gfs._decoder_identity',return_value={'version':'same'}), \
             patch('balloon_sim.environment.gfs.decode_gfs',return_value={}), \
             patch('balloon_sim.environment.gfs.write_bundle',side_effect=lambda path,bundle:path.write_bytes(b'normalized')):
            folder=Path(tmp)/'acquisition'; count=[]
            def first(url,path,remaining,**kwargs):
                count.append(path.name)
                if path.name=='f001.grib2': raise WeatherError('HTTP_STATUS','503')
                return self.download(url,path,remaining,**kwargs)
            with patch('balloon_sim.environment.gfs._download',side_effect=first):
                with self.assertRaises(WeatherError): acquire_gfs(self.request(),folder)
            self.assertFalse((folder/'weather.json.gz').exists())
            progress=[]
            with patch('balloon_sim.environment.gfs._download',side_effect=self.download) as download:
                target=acquire_gfs(self.request(),folder,resume=True,progress=progress.append)
                self.assertEqual(download.call_count,1)
                self.assertEqual(download.call_args.args[1].name,'f001.grib2')
                self.assertTrue(target.exists()); self.assertGreater(progress[-1]['bytes_reused'],0)
                again=acquire_gfs(self.request(),folder,resume=True)
                self.assertEqual(again,target); self.assertEqual(download.call_count,1)
            different=self.request(); different['end_utc']='2026-09-29T02:00:00Z'
            with self.assertRaises(WeatherError) as caught: acquire_gfs(different,folder,resume=True)
            self.assertEqual(caught.exception.code,'REQUEST_MISMATCH')
            (folder/'f000.grib2').write_bytes(b'corrupt')
            with self.assertRaises(WeatherError) as caught: acquire_gfs(self.request(),folder,resume=True)
            self.assertEqual(caught.exception.code,'RAW_HASH_MISMATCH')

    def test_cancelled_and_memory_limited_requests_do_not_start_http(self):
        with tempfile.TemporaryDirectory() as tmp, patch('balloon_sim.environment.gfs._decoder_identity',return_value={}), \
             patch('balloon_sim.environment.gfs._download') as download:
            cancel=threading.Event(); cancel.set()
            with self.assertRaises(WeatherError) as caught: acquire_gfs(self.request(),Path(tmp)/'cancel',cancel=cancel)
            self.assertEqual(caught.exception.code,'ACQUISITION_CANCELLED')
            wide=self.request(); wide['bounds']={'west':1,'east':359,'south':-89,'north':89}
            with self.assertRaises(WeatherError) as caught: acquire_gfs(wide,Path(tmp)/'wide')
            self.assertEqual(caught.exception.code,'DECODE_MEMORY_LIMIT')
            download.assert_not_called()

    def test_resume_preserves_unreceipted_raw_and_charges_retained_bytes(self):
        with tempfile.TemporaryDirectory() as tmp, patch('balloon_sim.environment.gfs._decoder_identity',return_value={}), \
             patch('balloon_sim.environment.gfs.decode_gfs',return_value={}), \
             patch('balloon_sim.environment.gfs.write_bundle',side_effect=lambda path,bundle:path.write_bytes(b'normalized')):
            folder=Path(tmp)/'acquisition'
            with patch('balloon_sim.environment.gfs._download',side_effect=WeatherError('HTTP_STATUS','503')):
                with self.assertRaises(WeatherError): acquire_gfs(self.request(),folder)
            # Simulate a process stop after the raw rename, before provenance commit.
            (folder/'f000.grib2').write_bytes(b'GRIB orphan')
            with patch('balloon_sim.environment.gfs._download',side_effect=self.download) as download:
                acquire_gfs(self.request(),folder,resume=True)
                self.assertEqual(download.call_count,2)
                self.assertEqual(download.call_args_list[0].args[2],50_000_000-len(b'GRIB orphan'))
            self.assertEqual([p.read_bytes() for p in folder.glob('*.grib2.*.partial')],[b'GRIB orphan'])

    def test_failed_transfer_reports_partial_bytes_before_retry(self):
        with tempfile.TemporaryDirectory() as tmp, patch('balloon_sim.environment.gfs._decoder_identity',return_value={}):
            folder=Path(tmp)/'acquisition'; updates=[]
            def failed(url,path,remaining,**kwargs):
                path.with_name(path.name+'.example.partial').write_bytes(b'GRIB partial')
                raise WeatherError('DOWNLOAD_TIMEOUT','stopped')
            with patch('balloon_sim.environment.gfs._download',side_effect=failed):
                with self.assertRaises(WeatherError): acquire_gfs(self.request(),folder,progress=updates.append)
            self.assertEqual(updates[-1]['phase'],'failed')
            self.assertEqual(updates[-1]['bytes_downloaded'],len(b'GRIB partial'))
            self.assertEqual(updates[-1]['retained_partial_bytes'],len(b'GRIB partial'))


if __name__=='__main__': unittest.main()
