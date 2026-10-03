"""Offline acquisition boundary tests. No service or user cache is accessed."""
from datetime import datetime, timedelta, timezone
import hashlib
import http.client
import io
import json
from pathlib import Path
import shutil
import struct
import tempfile
import uuid

import numpy as np
import pytest

from tools import acquire_jra3q_climate_samples as acquisition


@pytest.fixture
def tmp_path():
    # pytest's mode=0700 temp directories are inaccessible in the Windows
    # sandbox used for this project; ordinary newly created test paths work.
    root = Path(tempfile.gettempdir()) / "balloon-jra-acquisition-tests"
    path = root / uuid.uuid4().hex
    path.mkdir(parents=True)
    yield path
    assert path.resolve().parent == root.resolve()
    shutil.rmtree(path)


def dods(wind=None, times=None, lat=None, levels=None, lon=None, variable="ugrd-pres-an-gauss", path="fixture.nc"):
    if wind is None:
        wind = np.arange(2 * 3 * 2 * 2, dtype=np.float32).reshape(2, 3, 2, 2)
    nt, nz, ny, nx = wind.shape
    times = np.array([1086960 + 6 * i for i in range(nt)] if times is None else times)
    levels = np.arange(nz) + 3 if levels is None else levels
    lat = np.arange(ny)[::-1] + 40 if lat is None else lat
    lon = np.arange(nx) * .375 + 138 if lon is None else lon
    header = f"""Dataset {{
 Grid {{ ARRAY:
 Float32 {variable}[time = {nt}][pressure_level = {nz}][lat = {ny}][lon = {nx}];
 MAPS: Int32 time[time = {nt}]; Float64 pressure_level[pressure_level = {nz}];
 Float64 lat[lat = {ny}]; Float64 lon[lon = {nx}];
 }} {variable};
}} {path};
""".encode("ascii")
    payload = b""
    for values, dtype in [(wind, ">f4"), (times, ">i4"), (levels, ">f8"), (lat, ">f8"), (lon, ">f8")]:
        flat = np.asarray(values, dtype=dtype).ravel()
        payload += struct.pack(">II", len(flat), len(flat)) + flat.tobytes()
    return header + b"\nData:\n" + payload


def catalog(year=2024, month=1):
    nodes = []
    end = acquisition.calendar.monthrange(year, month)[1]
    for component, variable in acquisition.VARIABLES.items():
        for day in (1, 6, 11, 16, 21, 26):
            last = day + 4 if day < 26 else end
            path = f"files/g/d640000/anl_p/{year}{month:02d}/jra3q.anl_p.0_2_{2 if component == 'u' else 3}.{variable}.{year}{month:02d}{day:02d}00_{year}{month:02d}{last:02d}18.nc"
            nodes.append(f'<dataset urlPath="{path}"/>')
    return ('<catalog xmlns="http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0">' + "".join(nodes) + "</catalog>").encode()


def test_binary_grid_preserves_float32_bits_and_coordinates():
    original = np.linspace(-33.25, 61.875, 24, dtype=np.float32).reshape(2, 3, 2, 2)
    actual, axes = acquisition.decode_dods(dods(original), "ugrd-pres-an-gauss", "fixture.nc")
    assert np.array_equal(actual.astype(np.float32).view(np.uint32), original.view(np.uint32))
    assert axes["time"].tolist() == [1086960, 1086966]
    assert axes["lat"].tolist() == [41., 40.]


@pytest.mark.parametrize("alter", [lambda d: d[:-1], lambda d: d + b"extra", lambda d: d.replace(b"Float32", b"Float64", 1), lambda d: d.replace(b"\nData:\n", b"\nData\n", 1)])
def test_decoder_rejects_truncation_trailing_and_wrong_layout(alter):
    with pytest.raises(ValueError):
        acquisition.decode_dods(alter(dods()), "ugrd-pres-an-gauss")


def test_decoder_rejects_counts_and_wrong_source():
    data = dods()
    head, payload = data.split(b"\nData:\n", 1)
    with pytest.raises(ValueError, match="count"):
        acquisition.decode_dods(head + b"\nData:\n" + struct.pack(">I", 25) + payload[4:], "ugrd-pres-an-gauss")
    with pytest.raises(ValueError, match="source"):
        acquisition.decode_dods(data, "ugrd-pres-an-gauss", "another.nc")


@pytest.mark.parametrize("value", [np.nan, np.inf, 9.999e20, -1001.])
def test_decoder_rejects_missing_and_nonphysical_values(value):
    wind = np.zeros((2, 3, 2, 2), dtype=np.float32)
    wind.flat[0] = value
    with pytest.raises(ValueError):
        acquisition.decode_dods(dods(wind), "ugrd-pres-an-gauss")


def test_declared_small_finite_fill_is_rejected():
    wind = np.zeros((2, 3, 2, 2), dtype=np.float32)
    wind.flat[0] = -99.
    with pytest.raises(ValueError, match="declared"):
        acquisition.decode_dods(dods(wind), "ugrd-pres-an-gauss", fill_values=[-99.])


def test_reorder_matches_db_cell_order_without_changing_wind_bits():
    lat = np.linspace(46.6, 39.9, 19)
    lon = np.arange(30) * .375 + 138
    levels = np.arange(38, dtype=float) + 3
    # Deliberately shuffle DB level order and reverse the native latitude order.
    basis = {"levels": [{"level_id": i, "level_hpa": p} for i, p in enumerate(levels[::-1])],
             "grid": [{"cell_id": j * 30 + i, "lat": float(np.float32(y)), "lon": float(x)} for j, y in enumerate(lat[::-1]) for i, x in enumerate(lon)]}
    values = (np.arange(2 * 38 * 19 * 30, dtype=np.float32) / 1000).reshape(2, 38, 19, 30)
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    entry = {"path": "fixture.nc", "component": "u", "start": start, "end": start + timedelta(hours=6)}
    actual, times = acquisition.reorder_subset(dods(values, lat=lat, lon=lon, levels=levels), entry, basis)
    assert actual.dtype == np.float32
    assert actual.shape == (2, 38, 570)
    assert np.array_equal(actual, values[:, ::-1, ::-1, :].reshape(2, 38, 570))
    assert times == [start, start + timedelta(hours=6)]
    with pytest.raises(ValueError, match="UTC"):
        acquisition.reorder_subset(dods(values, times=[1086960, 1086972], lat=lat, lon=lon, levels=levels), entry, basis)


@pytest.mark.parametrize("year,month,expected_count", [(2024, 2, 116), (2023, 2, 112), (2024, 1, 124)])
def test_catalog_requires_complete_real_calendar(year, month, expected_count):
    entries = acquisition.catalog_entries(catalog(year, month), year, month)
    assert len(entries["u"]) == len(entries["v"]) == 6
    assert len(acquisition.month_times(year, month)) == expected_count
    bad = catalog(year, month).replace(b"2600_", b"2700_", 1)
    with pytest.raises(ValueError):
        acquisition.catalog_entries(bad, year, month)


def test_request_constraint_uses_exact_indices_not_box_interpolation():
    entry = acquisition.catalog_entries(catalog(), 2024, 1)["u"][0]
    url = acquisition.data_url(entry, {"pressure_level": [7, 44], "lat": [115, 133], "lon": [368, 397]})
    assert acquisition.urllib.parse.unquote(url).endswith(".dods?ugrd-pres-an-gauss[0:1:19][7:1:44][115:1:133][368:1:397]")


def test_verified_seed_reuse_is_offline_and_tampering_fails(tmp_path, monkeypatch):
    seed = tmp_path / "seed"
    seed.mkdir()
    (seed / "a.body").write_bytes(b"fixture")
    url = acquisition.ORIGIN + "/thredds/fixture"
    (seed / "a-receipt.json").write_text(json.dumps({"url": url, "status": 200, "body": "a.body", "bytes": 7, "sha256": hashlib.sha256(b"fixture").hexdigest()}))
    output = tmp_path / "out"
    output.mkdir()
    monkeypatch.setattr(acquisition.urllib.request, "build_opener", lambda *a: pytest.fail("network must not be used"))
    cache = acquisition.HttpCache(output, 1, 100, seed=seed)
    path, receipt = cache.get(url, 100)
    assert path.read_bytes() == b"fixture" and cache.requests == 0
    assert cache.get(url, 100)[1] == receipt
    path.write_bytes(b"changed")
    with pytest.raises(ValueError, match="hash"):
        cache.get(url, 100)


def test_budget_is_checked_before_network_and_requests_do_not_retry(tmp_path, monkeypatch):
    monkeypatch.setattr(acquisition.urllib.request, "build_opener", lambda *a: pytest.fail("network must not be used"))
    cache = acquisition.HttpCache(tmp_path, 1, 10)
    with pytest.raises(ValueError, match="budget"):
        cache.get(acquisition.ORIGIN + "/thredds/fixture", 11)
    assert cache.requests == cache.bytes == 0


def test_partial_year_never_publishes_a_ten_year_month(tmp_path):
    class EmptyCache:
        def cached(self, url):
            return None
    assert acquisition.publish_complete_months(tmp_path, EmptyCache(), {}, {}, tmp_path / "unused.duckdb", {"u": [9.999e20], "v": [9.999e20]}) == []
    assert not (tmp_path / "manifest.json").exists()


def test_dry_plan_never_opens_network_and_labels_selected_year(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(acquisition, "read_basis", lambda p: {"dataset_sha256": "test"})
    monkeypatch.setattr(acquisition, "HttpCache", lambda *a, **k: pytest.fail("dry plan must not acquire"))
    assert acquisition.main(["--database", "unused", "--output", str(tmp_path / "not-created"), "--months", "1", "--years", "2024"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["data_requests_before_reuse"] == 12
    assert result["manifest_years"] == [2024, 2024]
    assert result["schema"] == "balloon.wind-samples/1"
    assert not (tmp_path / "not-created").exists()


def test_complete_selected_year_publishes_separate_source_with_no_climatology_claim(tmp_path):
    lat = np.linspace(46.6, 39.9, 19)
    lon = np.arange(30) * .375 + 138
    levels = np.arange(38, dtype=float) + 3
    basis = {"dataset_sha256": "basis-hash", "levels": [{"level_id": i, "level_hpa": p} for i, p in enumerate(levels)],
             "grid": [{"cell_id": j * 30 + i, "lat": float(np.float32(y)), "lon": float(x)} for j, y in enumerate(lat[::-1]) for i, x in enumerate(lon)],
             "gaussian_weights": [.005] * 570}
    indices = {"pressure_level": [7, 44], "lat": [115, 133], "lon": [368, 397]}
    records = {}
    body = tmp_path / "catalog.xml"
    body.write_bytes(catalog())
    records[acquisition.catalog_url(2024, 1)] = (body, {})
    entries = acquisition.catalog_entries(body.read_bytes(), 2024, 1)
    for component in ("u", "v"):
        for i, entry in enumerate(entries[component]):
            count = int((entry["end"] - entry["start"]).total_seconds() / 21600) + 1
            start = int((entry["start"] - datetime(1900, 1, 1, tzinfo=timezone.utc)).total_seconds() / 3600)
            values = np.full((count, 38, 19, 30), 3 if component == "u" else 4, dtype=np.float32)
            path = tmp_path / f"{component}-{i}.dods"
            path.write_bytes(dods(values, times=np.arange(count) * 6 + start, levels=levels, lat=lat, lon=lon, variable=acquisition.VARIABLES[component], path=entry["path"]))
            url = acquisition.data_url(entry, indices)
            records[url] = (path, {"url": url, "sha256": acquisition.digest(path), "bytes": path.stat().st_size})

    class FixtureCache:
        def cached(self, url):
            return records.get(url)

    published = acquisition.publish_complete_months(tmp_path, FixtureCache(), basis, indices, tmp_path / "not-opened.duckdb", {"u": [9.999e20], "v": [9.999e20]}, [2024])
    assert published == [1]
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema"] == "balloon.wind-samples/1"
    assert manifest["years"] == [2024, 2024]
    assert "2016" not in manifest["label"]
    assert manifest["grid"][0]["weight"] == .005
    assert len(manifest["months"][0]["times_utc"]) == 124
    assert len(manifest["provenance"]["requests"]) == 12
    assert "not comparable" in manifest["provenance"]["validation"]["1"]["comparison"]
    array = np.load(tmp_path / "month-01/u.npy", mmap_mode="r")
    assert array.shape == (124, 38, 570) and array.dtype == np.float32 and np.all(array == 3)
    del array
    assert acquisition.publish_complete_months(tmp_path, FixtureCache(), basis, indices, tmp_path / "not-opened.duckdb", {"u": [9.999e20], "v": [9.999e20]}, [2024]) == [1]


def test_dry_plan_rejects_year_gap_instead_of_false_contiguous_label(tmp_path, monkeypatch):
    monkeypatch.setattr(acquisition, "read_basis", lambda p: pytest.fail("must reject before opening DB"))
    with pytest.raises(ValueError, match="contiguous"):
        acquisition.main(["--database", "unused", "--output", str(tmp_path), "--months", "1", "--years", "2016", "2024"])


def test_metadata_requires_units_product_and_declared_missing_values():
    lat = np.linspace(90, -90, 480)
    lon = np.arange(960) * .375
    levels = np.arange(45)
    basis = {"levels": [{"level_hpa": int(p)} for p in levels[7:45]],
             "grid": [{"lat": float(np.float32(y)), "lon": float(x)} for y in lat[115:134] for x in lon[368:398]]}
    axes = ''.join(f'<axis name="{name}"><values>{" ".join(str(float(x)) for x in values)}</values></axis>' for name, values in [('lat', lat), ('lon', lon), ('pressure_level', levels)])
    xml = ('<gridDataset><gridSet><grid name="ugrd-pres-an-gauss" type="float">'
           '<attribute name="units" value="m s-1"/><attribute name="data_type" value="analysis"/>'
           '<attribute name="group" value="anl_p"/><attribute name="_FillValue" value="9.999E20"/>'
           '</grid></gridSet>' + axes + '</gridDataset>').encode()
    _, indices, fills = acquisition.metadata_axes(xml, 'u', basis)
    assert indices == {'pressure_level': [7, 44], 'lat': [115, 133], 'lon': [368, 397]}
    assert fills == [9.999e20]
    for invalid in [xml.replace(b'm s-1', b'knots'), xml.replace(b'value="anl_p"', b'value="anl_p125"'), xml.replace(b'name="_FillValue"', b'name="unrelated"')]:
        with pytest.raises(ValueError):
            acquisition.metadata_axes(invalid, 'u', basis)


def test_http_over_cap_retains_failure_without_publishing_and_stops_next_call(tmp_path, monkeypatch):
    calls = []

    class Response(io.BytesIO):
        status = 200
        headers = {}

    class Opener:
        def open(self, request, timeout):
            calls.append(request.full_url)
            return Response(b'123456')

    monkeypatch.setattr(acquisition.urllib.request, 'build_opener', lambda *a: Opener())
    cache = acquisition.HttpCache(tmp_path, 3, 100)
    url = acquisition.ORIGIN + '/thredds/fixture'
    with pytest.raises(ValueError, match='cap exceeded'):
        cache.get(url, 5)
    assert cache.stopped and cache.requests == 1 and cache.bytes == 6
    assert cache.cached(url) is None
    assert len(list((tmp_path / 'download-cache').glob('*.failure-*.json'))) == 1
    assert len(list((tmp_path / 'download-cache').glob('*.partial-*'))) == 1
    with pytest.raises(ValueError, match='stopped'):
        cache.get(url, 5)
    assert len(calls) == 1


def test_seed_path_cannot_escape_declared_seed_root(tmp_path, monkeypatch):
    seed = tmp_path / 'seed'
    seed.mkdir()
    (tmp_path / 'outside').write_bytes(b'outside')
    url = acquisition.ORIGIN + '/thredds/fixture'
    (seed / 'a-receipt.json').write_text(json.dumps({'url': url, 'status': 200, 'body': '../outside', 'bytes': 7, 'sha256': hashlib.sha256(b'outside').hexdigest()}))
    output = tmp_path / 'out'
    output.mkdir()
    monkeypatch.setattr(acquisition.urllib.request, 'build_opener', lambda *a: pytest.fail('network must not be used'))
    with pytest.raises(ValueError, match='escapes'):
        acquisition.HttpCache(output, 1, 100, seed=seed).get(url, 100)


def test_recorded_retry_retains_incomplete_fragment_and_reuses_success(tmp_path, monkeypatch):
    calls=[]
    class Response(io.BytesIO):
        status=200
        headers={}
        def read(self, n=-1):
            if len(calls)==1:
                raise http.client.IncompleteRead(b'header')
            return super().read(n)
    class Opener:
        def open(self, request, timeout):
            calls.append(request.full_url)
            return Response(b'complete')
    monkeypatch.setattr(acquisition.urllib.request,'build_opener',lambda *a:Opener())
    monkeypatch.setattr(acquisition.time,'sleep',lambda seconds:None)
    cache=acquisition.HttpCache(tmp_path,3,1000,attempts=2)
    url=acquisition.ORIGIN+'/thredds/fixture'
    path, receipt=cache.get(url,100)
    assert path.read_bytes()==b'complete' and receipt['attempt']==2
    failures=list((tmp_path/'download-cache').glob('*.failure-*.json'))
    failure=json.loads(failures[0].read_bytes())
    assert failure['retained_partial_bytes']==6 and failure['elapsed_seconds']>=0
    assert (tmp_path/'download-cache'/failure['partial_file']).read_bytes()==b'header'
    assert cache.get(url,100)[0]==path and len(calls)==2


def test_http_error_does_not_retry_even_with_three_attempts(tmp_path, monkeypatch):
    calls=[]
    class Opener:
        def open(self, request, timeout):
            calls.append(request.full_url)
            raise acquisition.urllib.error.HTTPError(request.full_url,429,'rate limit',{},None)
    monkeypatch.setattr(acquisition.urllib.request,'build_opener',lambda *a:Opener())
    monkeypatch.setattr(acquisition.time,'sleep',lambda seconds:pytest.fail('no retry'))
    cache=acquisition.HttpCache(tmp_path,3,1000,attempts=3)
    with pytest.raises(acquisition.urllib.error.HTTPError):
        cache.get(acquisition.ORIGIN+'/thredds/fixture',100)
    assert len(calls)==1 and cache.stopped


def native_basis_path():
    return Path(__file__).resolve().parents[1] / 'references/climate_demo_057/jra3q-native-basis.json'


@pytest.mark.parametrize('alter', [
    lambda b: b['gaussian_weights'].__setitem__(0, float('nan')),
    lambda b: b['gaussian_weights'].__setitem__(0, .1),
    lambda b: b['grid'][0].__setitem__('lon', 137.625),
    lambda b: b['grid'][0].__setitem__('lat', 40.),
    lambda b: b['levels'][0].__setitem__('level_hpa', -3.),
    lambda b: b['grid'][0].__setitem__('cell_id', 570),
    lambda b: b.__setitem__('dataset_sha256', 'bad'),
])
def test_basis_corruption_is_rejected_before_any_network(tmp_path, alter, monkeypatch):
    basis = json.loads(native_basis_path().read_bytes())
    alter(basis)
    path = tmp_path / 'basis.json'
    path.write_text(json.dumps(basis), encoding='utf-8')
    monkeypatch.setattr(acquisition.urllib.request, 'build_opener', lambda *a: pytest.fail('no network'))
    with pytest.raises(ValueError):
        acquisition.read_basis_file(path)


def test_basis_only_dry_plan_has_fixed_support_and_does_not_open_database(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(acquisition, 'read_basis', lambda *a: pytest.fail('no aggregate DB dependency'))
    monkeypatch.setattr(acquisition, 'HttpCache', lambda *a, **k: pytest.fail('no HTTP/output in dry plan'))
    path = native_basis_path()
    basis = acquisition.read_basis_file(path)
    assert len(basis['grid']) == 570 and len(basis['levels']) == 38
    assert basis['basis_file_sha256'] == acquisition.digest(path)
    assert acquisition.main(['--basis-json', str(path), '--output', str(tmp_path/'not-created'), '--months', '1', '--years', '2024']) == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan['manifest_years'] == [2024,2024]
    assert plan['basis_file_sha256'] == acquisition.digest(path)
    assert not (tmp_path/'not-created').exists()


@pytest.mark.parametrize('wrapped_timeout', [False, True])
def test_short_content_length_and_wrapped_timeout_retry_without_publishing_partial(tmp_path, monkeypatch, wrapped_timeout):
    calls = []
    class Response(io.BytesIO):
        status = 200
        headers = {'Content-Length': '8'}
    class Opener:
        def open(self, request, timeout):
            calls.append(request.full_url)
            if len(calls) == 1 and wrapped_timeout:
                raise acquisition.urllib.error.URLError(TimeoutError('transfer timed out'))
            return Response(b'short' if len(calls) == 1 else b'complete')
    monkeypatch.setattr(acquisition.urllib.request, 'build_opener', lambda *a: Opener())
    monkeypatch.setattr(acquisition.time, 'sleep', lambda seconds: None)
    cache = acquisition.HttpCache(tmp_path, 3, 1000, attempts=2)
    body, receipt = cache.get(acquisition.ORIGIN+'/thredds/fixture', 100)
    assert body.read_bytes() == b'complete' and receipt['attempt'] == 2
    failure = json.loads(next((tmp_path/'download-cache').glob('*.failure-*.json')).read_bytes())
    assert failure['retained_partial_bytes'] == (0 if wrapped_timeout else 5)
    assert len(calls) == 2
