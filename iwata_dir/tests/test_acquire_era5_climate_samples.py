"""Offline ERA5 acquisition contract tests; no network or existing cache access."""
from datetime import date, datetime, timezone
import io
import http.client
import json
from pathlib import Path
import struct
import tempfile
import uuid

import numpy as np
import pytest

from tools import acquire_era5_climate_samples as acquisition


@pytest.fixture
def work():
    root = Path(tempfile.gettempdir())/"balloon-era5-acquisition-tests"/uuid.uuid4().hex
    root.mkdir(parents=True)
    return root


def response(axes, *, component="U", hours=None, lat=None, levels=None, fill=None, day=None):
    day = day or datetime(2024, 1, 1, tzinfo=timezone.utc)
    epoch = datetime(1900, 1, 1, tzinfo=timezone.utc)
    start = int((day-epoch).total_seconds()/3600)
    shape = axes["shape"]
    data = np.arange(np.prod(shape), dtype=np.float32).reshape(shape)/100
    if fill is not None:
        data.reshape(-1)[0] = fill
    arrays = [("Float32", component, data, ["time", "level", "latitude", "longitude"]),
              ("Int32", "time", np.array([start+h for h in (hours or [0, 6, 12, 18])]), ["time"]),
              ("Float64", "level", np.array(levels or acquisition.LEVELS), ["level"]),
              ("Float64", "latitude", np.array(lat or axes["latitude"]), ["latitude"]),
              ("Float64", "longitude", np.array(axes["longitude"]), ["longitude"])]
    header, body = [], bytearray()
    for dtype, name, values, names in arrays:
        dims = "".join(f"[{n} = {v}]" for n, v in zip(names, values.shape))
        header.append(f"{dtype} {name}{dims};")
        body.extend(struct.pack(">II", values.size, values.size))
        body.extend(values.astype({"Float32": ">f4", "Int32": ">i4", "Float64": ">f8"}[dtype]).tobytes())
    return ("Dataset {\n"+"\n".join(header)+"\n}\nData:\n").encode()+bytes(body)


def test_native_grid_is_inside_jra_box_but_not_remapped_to_jra():
    axes = acquisition.selection()
    assert axes["lat_indices"] == [174, 200]
    assert axes["lon_indices"] == [552, 595]
    assert axes["shape"] == [4, 37, 27, 44]
    cells = acquisition.grid_cells(axes)
    assert len(cells) == len({c["cell_id"] for c in cells}) == 1188
    assert cells[0]["lat"] == 46.5 and cells[-1]["lat"] == 40
    assert cells[0]["lon"] == 138 and cells[-1]["lon"] == 148.75
    assert cells[0]["weight"] < cells[-1]["weight"]
    assert all(0 < c["weight"] < 1 for c in cells)


def test_subset_is_four_analysis_hours_all_37_levels_and_encoded():
    axes = acquisition.selection()
    url = acquisition.subset_url("files/g/d633000/e5.oper.an.pl/test.nc", "v", axes)
    assert "V%5B0%3A6%3A18%5D%5B0%3A1%3A36%5D" in url
    with pytest.raises(ValueError):
        acquisition.subset_url("https://example.com/foreign", "u", axes)


def test_decode_preserves_coordinates_times_native_order_and_float32():
    axes = acquisition.selection()
    array, times = acquisition.decode_grid(response(axes), "u", axes, date(2024, 1, 1))
    assert array.shape == (4, 37, 1188)
    assert array.dtype == np.float32
    assert times == [f"2024-01-01T{h:02}:00:00Z" for h in [0, 6, 12, 18]]
    assert array[0, 0, 44] == np.float32(.44)


@pytest.mark.parametrize("alter", [lambda b: b[:-1], lambda b: b+b"x", lambda b: b.replace(b"Float32 U", b"Float32 V"), lambda b: b.replace(b"\nData:\n", b"\nERROR\n")])
def test_decode_rejects_truncation_extra_bytes_wrong_variable_and_error_text(alter):
    axes = acquisition.selection()
    with pytest.raises(ValueError):
        acquisition.decode_grid(alter(response(axes)), "u", axes, date(2024, 1, 1))


@pytest.mark.parametrize("options", [{"hours": [0, 1, 2, 3]}, {"lat": [46.5]*27}, {"levels": [1000]*37}, {"fill": np.nan}, {"fill": 9.999e20}])
def test_decode_rejects_wrong_support_or_missing_samples(options):
    axes = acquisition.selection()
    with pytest.raises(ValueError):
        acquisition.decode_grid(response(axes, **options), "u", axes, date(2024, 1, 1))


def test_catalog_requires_complete_distinct_daily_components():
    nodes = ['<service serviceType="OpenDAP" base="/thredds/dodsC/"/>']
    for day in range(1, 30):
        for parameter in ["131_u", "132_v"]:
            path = f"files/g/d633000/e5.oper.an.pl/202402/e5.oper.an.pl.128_{parameter}.ll025uv.202402{day:02}00_202402{day:02}23.nc"
            nodes.append(f'<dataset urlPath="{path}"/>')
    cat = ("<catalog>"+"".join(nodes)+"</catalog>").encode()
    assert len(acquisition.wind_paths(cat, 2024, 2)) == 58
    for changed in [nodes[:-1], nodes+[nodes[-1]]]:
        with pytest.raises(ValueError):
            acquisition.wind_paths(("<catalog>"+"".join(changed)+"</catalog>").encode(), 2024, 2)


def test_fetch_caps_and_preserves_failure_and_requires_explicit_verified_resume(work, monkeypatch):
    class Reply(io.BytesIO):
        status = 200
        headers = {"content-type": "application/octet-stream"}
    calls = []
    class Opener:
        def open(self, request, timeout):
            calls.append(request.full_url)
            return Reply(b"abcdef")
    monkeypatch.setattr(acquisition.urllib.request, "build_opener", lambda *_: Opener())
    url = acquisition.HOST+"/thredds/test"
    with pytest.raises(ValueError, match="byte limit"):
        acquisition.fetch(url, work/"limited", 4)
    assert (work/"limited.partial").read_bytes() == b"abcd"
    assert not json.loads((work/"limited.receipt.json").read_text())["complete"]
    assert acquisition.fetch(url, work/"ok", 10) == b"abcdef"
    with pytest.raises(ValueError, match="Existing observation"):
        acquisition.fetch(url, work/"ok", 10)
    assert acquisition.fetch(url, work/"ok", 10, resume=True) == b"abcdef"
    assert len(calls) == 2
    (work/"ok.body").write_bytes(b"changed")
    with pytest.raises(ValueError, match="changed"):
        acquisition.fetch(url, work/"ok", 10, resume=True)


def test_month_publish_requires_both_components_and_complete_leap_february(work):
    axes = acquisition.selection({"west": 140, "east": 140, "south": 40, "north": 40})
    times = [f"2024-02-{d:02}T{h:02}:00:00Z" for d in range(1, 30) for h in [0, 6, 12, 18]]
    u = np.zeros((116, 37, 1), dtype=np.float32)
    v = np.ones_like(u)
    for wrong_u, wrong_v, wrong_times in [(u[:-1], v, times), (u, v[:-1], times), (u, v, times[:-1]), (u.astype(np.float64), v, times)]:
        with pytest.raises(ValueError, match="complete monthly"):
            acquisition.month_record(work, 2024, 2, wrong_u, wrong_v, wrong_times, axes, resume=False)
    assert list(work.iterdir()) == []
    row = acquisition.month_record(work, 2024, 2, u, v, times, axes, resume=False)
    assert row["times_utc"][-1] == "2024-02-29T18:00:00Z"
    assert np.load(work/row["u"]["file"], allow_pickle=False).dtype == np.float32
    assert acquisition.sha((work/row["v"]["file"]).read_bytes()) == row["v"]["sha256"]
    assert acquisition.month_record(work, 2024, 2, u, v, times, axes, resume=True) == row
    v[0, 0, 0] = 2
    with pytest.raises(ValueError, match="differs"):
        acquisition.month_record(work, 2024, 2, u, v, times, axes, resume=True)


def test_chunked_incomplete_read_preserves_exception_partial_bytes(work, monkeypatch):
    class Reply(io.BytesIO):
        status = 200
        headers = {}
        def read(self, _size):
            raise http.client.IncompleteRead(b"received fragment")
    class Opener:
        def open(self, *_args, **_kwargs):
            return Reply()
    monkeypatch.setattr(acquisition.urllib.request, "build_opener", lambda *_: Opener())
    with pytest.raises(http.client.IncompleteRead):
        acquisition.fetch(acquisition.HOST+"/thredds/test", work/"truncated", 100)
    assert (work/"truncated.partial").read_bytes() == b"received fragment"
    receipt = json.loads((work/"truncated.receipt.json").read_text())
    assert receipt["complete"] is False and receipt["bytes"] == 17
    assert receipt["sha256"] == acquisition.sha(b"received fragment")


@pytest.mark.parametrize("status", [403, 429, 503])
def test_http_rejection_is_not_retried_in_run_or_resume(work, monkeypatch, status):
    calls = []
    url = acquisition.HOST+"/thredds/test"
    def reject(*_args, **_kwargs):
        calls.append(1)
        raise acquisition.urllib.error.HTTPError(url, status, "rejected", {}, None)
    monkeypatch.setattr(acquisition, "fetch", reject)
    with pytest.raises(acquisition.urllib.error.HTTPError):
        acquisition.observation(url, work/"http", 100, resume=False, attempts=3, timeout=120)
    assert len(calls) == 1
    acquisition.write_json(work/"http-attempt01.receipt.json", {"url": url, "complete": False, "http_status": status})
    with pytest.raises(ValueError, match="HTTP rejection"):
        acquisition.observation(url, work/"http", 100, resume=True, attempts=3)
    assert len(calls) == 1


def test_transport_retry_is_finite_explicit_timeout_and_stop_prevents_retry(work, monkeypatch):
    calls = []
    url = acquisition.HOST+"/thredds/test"
    def fail(_url, stem, _cap, **kwargs):
        calls.append((stem.name, kwargs["timeout"]))
        raise http.client.IncompleteRead(b"header")
    monkeypatch.setattr(acquisition, "fetch", fail)
    monkeypatch.setattr(acquisition.time, "sleep", lambda _: None)
    with pytest.raises(RuntimeError, match="3 recorded"):
        acquisition.observation(url, work/"transport", 100, resume=False, attempts=3, timeout=120)
    assert calls == [(f"transport-attempt{i:02}", 120) for i in [1, 2, 3]]
    stop = acquisition.threading.Event()
    stop.set()
    with pytest.raises(RuntimeError, match="no further"):
        acquisition.observation(url, work/"stopped", 100, resume=False, attempts=3, stop=stop)
    assert len(calls) == 3


def test_validation_failure_is_not_retried(work, monkeypatch):
    calls = []
    def fail(*_args, **_kwargs):
        calls.append(1)
        raise ValueError("invalid or oversized response")
    monkeypatch.setattr(acquisition, "fetch", fail)
    with pytest.raises(ValueError):
        acquisition.observation(acquisition.HOST+"/thredds/test", work/"bad", 100, resume=False, attempts=3)
    assert len(calls) == 1


def test_explicit_recovery_complete_bytes_can_be_reused_after_http_rejection(work, monkeypatch):
    url=acquisition.HOST+"/thredds/test"
    acquisition.write_json(work/"probe-attempt01.receipt.json", {"url":url,"complete":False,"http_status":503})
    data=b"explicit separate recovery response"
    (work/"probe-attempt02.body").write_bytes(data)
    acquisition.write_json(work/"probe-attempt02.receipt.json", {"url":url,"complete":True,"http_status":200,"bytes":len(data),"sha256":acquisition.sha(data)})
    def forbidden(*_args, **_kwargs):
        raise AssertionError("resume must not issue HTTP")
    monkeypatch.setattr(acquisition.urllib.request,"build_opener",forbidden)
    assert acquisition.observation(url,work/"probe",100,resume=True,attempts=3)[0]==data


def test_http_error_preserves_retry_after_and_body_without_cookie(work, monkeypatch):
    url=acquisition.HOST+"/thredds/test"
    class Opener:
        def open(self,*_args,**_kwargs):
            raise acquisition.urllib.error.HTTPError(url,503,"temporary",{"Retry-After":"300","Set-Cookie":"not retained"},io.BytesIO(b"unavailable"))
    monkeypatch.setattr(acquisition.urllib.request,"build_opener",lambda *_:Opener())
    with pytest.raises(acquisition.urllib.error.HTTPError):
        acquisition.fetch(url,work/"http",100)
    row=json.loads((work/"http.receipt.json").read_text());assert row["headers"]=={"Retry-After":"300"}
    assert (work/"http.partial").read_bytes()==b"unavailable"


def netcdf_response(axes, *, component="U", day=None, wind_dtype="f", hours=None,
                    latitude=None, units="m s**-1", fill=None, scaled=False, reverse=False):
    from scipy.io import netcdf_file
    stream = io.BytesIO()
    with netcdf_file(stream, "w") as f:
        dimensions = ("time", "level", "latitude", "longitude")
        for name, n in zip(dimensions, axes["shape"]):
            f.createDimension(name, n)
        start = int(((day or datetime(2024, 1, 1, tzinfo=timezone.utc))-datetime(1900, 1, 1, tzinfo=timezone.utc)).total_seconds()/3600)
        for name, dtype, values, unit in [
            ("time", "i", [start+h for h in (hours or [0, 6, 12, 18])], "hours since 1900-01-01 00:00:00"),
            ("level", "d", acquisition.LEVELS, "hPa"),
            ("latitude", "d", latitude or axes["latitude"], "degrees_north"),
            ("longitude", "d", axes["longitude"], "degrees_east")]:
            var = f.createVariable(name, dtype, (name,));var.units = unit;var[:] = values
            if name == "time":var.calendar = "gregorian"
        dims = dimensions[::-1] if reverse else dimensions
        v = f.createVariable(component, wind_dtype, dims);v.units = units
        a = np.arange(np.prod(axes["shape"]), dtype=np.float32).reshape(axes["shape"])/100
        if fill is not None:
            v._FillValue = np.float32(fill);a.reshape(-1)[0] = fill
        if scaled:v.scale_factor = np.float32(2)
        v[:] = a.transpose(3, 2, 1, 0) if reverse else a
        f.flush()
        output = stream.getvalue()
    return output


def dataset_path(day="20240101", component="u"):
    code = {"u": "131_u", "v": "132_v"}[component]
    return f"files/g/d633000/e5.oper.an.pl/{day[:6]}/e5.oper.an.pl.128_{code}.ll025uv.{day}00_{day}23.nc"


def saved_observation(stem, url, data, *, number=1, complete=True, status=200):
    stem.parent.mkdir(parents=True, exist_ok=True)
    p = stem.parent/(stem.name+f"-attempt{number:02}")
    p.with_suffix(".body" if complete else ".partial").write_bytes(data)
    acquisition.write_json(p.with_suffix(".request.json"), {"url": url})
    acquisition.write_json(p.with_suffix(".receipt.json"), {"url": url, "complete": complete,
        "http_status": status, "bytes": len(data), "sha256": acquisition.sha(data)})


def test_ncss_url_and_exact_native_decode_matches_dods_bits():
    axes = acquisition.selection()
    url = acquisition.ncss_url(dataset_path(), "u", axes, date(2024, 1, 1))
    assert "/ncss/grid/" in url and "time=all&timeStride=6&accept=netCDF" in url
    assert "north=46.5&south=40&west=138&east=148.75" in url
    a, t = acquisition.decode_ncss(netcdf_response(axes), "u", axes, date(2024, 1, 1))
    b, u = acquisition.decode_grid(response(axes), "u", axes, date(2024, 1, 1))
    assert a.tobytes() == b.tobytes() and t == u
    with pytest.raises(ValueError, match="date"):
        acquisition.ncss_url(dataset_path(), "u", axes, date(2024, 1, 2))


@pytest.mark.parametrize("options", [{"wind_dtype": "d"}, {"hours": [0, 6, 12, 19]},
    {"latitude": [46.5]*27}, {"units": "knots"}, {"fill": -9999}, {"fill": np.nan},
    {"scaled": True}, {"reverse": True}])
def test_ncss_rejects_type_units_support_packing_fill_and_order(options):
    axes = acquisition.selection()
    with pytest.raises(ValueError):
        acquisition.decode_ncss(netcdf_response(axes, **options), "u", axes, date(2024, 1, 1))


def test_ncss_rejects_header_only_or_wrong_variable():
    axes = acquisition.selection()
    for b in [b"Dataset {}\nData:\n", netcdf_response(axes, component="V")]:
        with pytest.raises(ValueError):
            acquisition.decode_ncss(b, "u", axes, date(2024, 1, 1))


def test_ncss_attempt_one_reuses_dods_attempt_three_without_http(work, monkeypatch):
    axes = acquisition.selection();path = dataset_path();url = acquisition.subset_url(path, "u", axes)
    stem = work/"responses/u-20240101"
    for n in [1, 2]:saved_observation(stem, url, b"DDS only", number=n, complete=False)
    saved_observation(stem, url, response(axes), number=3)
    before = {p.name: p.read_bytes() for p in stem.parent.iterdir()}
    monkeypatch.setattr(acquisition.urllib.request, "build_opener", lambda *_: pytest.fail("No HTTP on cached sample"))
    a, _, row = acquisition.daily_observation(work, path, "u", axes, date(2024, 1, 1),
        transport="ncss", resume=True, attempts=1, timeout=120)
    assert a.shape == (4, 37, 1188) and row["receipt"].endswith("attempt03.receipt.json")
    assert "transport" not in row and before == {p.name: p.read_bytes() for p in stem.parent.iterdir()}


@pytest.mark.parametrize("change", ["body", "request", "receipt", "pending"])
def test_ncss_does_not_hide_corrupt_or_pending_cache_with_new_request(work, monkeypatch, change):
    axes = acquisition.selection();url = acquisition.ncss_url(dataset_path(), "u", axes, date(2024, 1, 1))
    stem = work/"responses/ncss-u-20240101"
    if change == "pending":
        stem.parent.mkdir();acquisition.write_json(stem.parent/(stem.name+"-attempt01.request.json"), {"url": url})
    else:
        saved_observation(stem, url, netcdf_response(axes))
        suffix = {"body": ".body", "request": ".request.json", "receipt": ".receipt.json"}[change]
        p = stem.parent/(stem.name+"-attempt01"+suffix)
        if change == "body":p.write_bytes(b"corrupt")
        else:
            obj = json.loads(p.read_text());obj["url"] += "&changed=true";p.write_text(json.dumps(obj))
    monkeypatch.setattr(acquisition.urllib.request, "build_opener", lambda *_: pytest.fail("No HTTP on invalid cache"))
    with pytest.raises(ValueError):
        acquisition.daily_observation(work, dataset_path(), "u", axes, date(2024, 1, 1),
            transport="ncss", resume=True, attempts=1, timeout=120)


def test_exhausted_dods_and_distinct_ncss_keep_both_histories(work, monkeypatch):
    axes = acquisition.selection();path = dataset_path();durl = acquisition.subset_url(path, "u", axes)
    nurl = acquisition.ncss_url(path, "u", axes, date(2024, 1, 1))
    for n in [1, 2, 3]:saved_observation(work/"responses/u-20240101", durl, b"DDS only", number=n, complete=False)
    raw = netcdf_response(axes);saved_observation(work/"responses/ncss-u-20240101", nurl, raw)
    monkeypatch.setattr(acquisition.urllib.request, "build_opener", lambda *_: pytest.fail("No HTTP on imported sample"))
    _, _, r = acquisition.daily_observation(work, path, "u", axes, date(2024, 1, 1),
        transport="ncss", resume=True, attempts=1, timeout=120)
    assert r["transport"] == "ncss" and r["sha256"] == acquisition.sha(raw)
    assert len(r["prior_dods_attempts"]) == 3 and r["canonical_request"]["hours_utc"] == [0, 6, 12, 18]
    assert all(not x["complete"] for x in r["prior_dods_attempts"])


def test_existing_ncss_failure_cannot_reset_attempt_budget(work, monkeypatch):
    axes = acquisition.selection();url = acquisition.ncss_url(dataset_path(), "u", axes, date(2024, 1, 1))
    saved_observation(work/"responses/ncss-u-20240101", url, b"stopped", complete=False, status=503)
    monkeypatch.setattr(acquisition.urllib.request, "build_opener", lambda *_: pytest.fail("No retry after HTTP rejection"))
    with pytest.raises(ValueError, match="HTTP rejection"):
        acquisition.daily_observation(work, dataset_path(), "u", axes, date(2024, 1, 1),
            transport="ncss", resume=True, attempts=3, timeout=120)


def mock_month_service(monkeypatch, *, fail_on=None):
    axes = acquisition.selection({"west": 140, "east": 140, "south": 40, "north": 40})
    monkeypatch.setattr(acquisition, "selection", lambda *_: axes)
    calls = []
    class Reply(io.BytesIO):
        status = 200
        headers = {}
    class Opener:
        def open(self, request, timeout):
            url = request.full_url;calls.append(url)
            if fail_on and fail_on(url):raise ValueError("intentional response validation boundary")
            if "/catalog/" in url:
                nodes = ['<service serviceType="OpenDAP" base="/thredds/dodsC/"/>', '<service serviceType="NetcdfSubset" base="/thredds/ncss/grid/"/>']
                nodes += [f'<dataset urlPath="{dataset_path(f"202401{d:02}", c)}"/>' for d in range(1,32) for c in ["u","v"]]
                return Reply(("<catalog>"+"".join(nodes)+"</catalog>").encode())
            component = "U" if "128_131_u" in url else "V"
            if url.endswith(".dds"):
                return Reply(f"Float32 {component}[time=24][level=37][latitude=721][longitude=1440]".encode())
            if url.endswith(".das"):
                return Reply(b' units "m s**-1"; units "hPa"; hours since 1900-01-01 00:00:00; calendar "gregorian"; 0.25 degree x 0.25 degree')
            import re
            day = datetime.strptime(re.search(r'\.(202401\d\d)00_',url)[1], "%Y%m%d").replace(tzinfo=timezone.utc)
            return Reply(netcdf_response(axes, component=component, day=day) if "/ncss/" in url else response(axes, component=component, day=day))
    monkeypatch.setattr(acquisition.urllib.request, "build_opener", lambda *_: Opener())
    return calls


def test_ncss_resume_preserves_existing_complete_dods_checkpoint_without_http(work, monkeypatch):
    calls = mock_month_service(monkeypatch)
    acquisition.acquire(work, 2024, [1], resume=False, attempts=1)
    before = {p.name: p.read_bytes() for p in work.iterdir() if p.is_file()}
    n = len(calls)
    acquisition.acquire(work, 2024, [1], resume=True, attempts=1, transport="ncss")
    assert len(calls) == n and before == {p.name: p.read_bytes() for p in work.iterdir() if p.is_file()}


def test_mixed_month_uses_real_service_receipts_and_failure_never_publishes(work, monkeypatch):
    calls = mock_month_service(monkeypatch, fail_on=lambda url: "2024010200_" in url and "132_v" in url and ".dods?" in url)
    with pytest.raises(ValueError):acquisition.acquire(work, 2024, [1], resume=False, attempts=1)
    assert not (work/"manifest.json").exists()
    calls = mock_month_service(monkeypatch)
    acquisition.acquire(work, 2024, [1], resume=True, attempts=1, transport="ncss")
    assert all("/ncss/" in url for url in calls)
    m = json.loads((work/"manifest.json").read_text())
    assert len(m["provenance"]["requests"]) == 62 and "NCSS" in m["provenance"]["conversion"]
    assert sum(r.get("transport") == "ncss" for r in m["provenance"]["requests"]) == 59
    assert len(m["months"][0]["times_utc"]) == 124


def test_ncss_failure_keeps_previous_manifest_and_stops_new_requests(work, monkeypatch):
    prior = b'{"schema":"balloon.wind-samples/1","provider":"ERA5","years":[2024,2024],"months":[],"observation":"older pointer retained"}'
    (work/"manifest.json").write_bytes(prior)
    calls = mock_month_service(monkeypatch, fail_on=lambda url: "/ncss/" in url and "2024010200_" in url and "132_v" in url)
    with pytest.raises(ValueError):
        acquisition.acquire(work, 2024, [1], resume=True, attempts=1, transport="ncss")
    assert (work/"manifest.json").read_bytes() == prior
    assert not (work/"manifest-through-01.json").exists()
    assert len([url for url in calls if "/ncss/" in url]) == 4
    assert not any("/dodsC/" in url for url in calls)


def test_resume_cannot_replace_published_months_with_disjoint_months(work, monkeypatch):
    acquisition.write_json(work/"manifest.json", {"schema":"balloon.wind-samples/1", "provider":"ERA5", "years":[2024,2024], "months":[{"month":m} for m in [1,2,3]]})
    prior = (work/"manifest.json").read_bytes()
    monkeypatch.setattr(acquisition.urllib.request,"build_opener",lambda *_: pytest.fail("No HTTP for invalid resume scope"))
    with pytest.raises(ValueError, match="published calendar prefix"):
        acquisition.acquire(work,2024,[4,5,6],resume=True,attempts=1,transport="ncss")
    assert (work/"manifest.json").read_bytes() == prior


def test_probe_cannot_silently_ignore_explicit_ncss_transport(work, monkeypatch):
    monkeypatch.setattr(acquisition, "probe", lambda *_: pytest.fail("No accidental DODS probe"))
    import sys
    monkeypatch.setattr(sys, "argv", ["tool", "probe", "--output", str(work), "--transport", "ncss", "--metadata", str(work)])
    with pytest.raises(SystemExit) as exc:
        acquisition.main()
    assert exc.value.code == 2
