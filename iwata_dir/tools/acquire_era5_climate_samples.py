"""Bounded NCAR ERA5 pressure-level U/V acquisition for climate demos.

Every response is retained with its exact request, bytes and SHA256. The native
0.25 degree grid and 37 pressure levels are not remapped to JRA. Only 00/06/12/18
UTC are selected from the hourly analysis. This is not a flight weather adapter.
"""
from __future__ import annotations

import argparse
import calendar
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
import hashlib
import http.client
import io
import json
import math
from pathlib import Path
import re
import struct
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

import numpy as np

HOST = "https://tds.gdex.ucar.edu"
CATALOG = HOST + "/thredds/catalog/files/g/d633000/e5.oper.an.pl/{ym}/catalog.xml"
DODS = HOST + "/thredds/dodsC/"
NCSS = HOST + "/thredds/ncss/grid/"
HOURS = [0, 6, 12, 18]
# Grid centres within the supplied JRA statistical DB bounds, not matched cells.
JRA_BOUNDS = {"west": 138.0, "east": 148.875, "south": 39.89591598510742, "north": 46.638885498046875}
LEVELS = [1, 2, 3, 5, 7, 10, 20, 30, 50, 70, 100, 125, 150, 175, 200, 225, 250, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 775, 800, 825, 850, 875, 900, 925, 950, 975, 1000]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        return None


def fetch(url: str, stem: Path, cap: int, *, resume: bool = False, timeout: int = 60) -> bytes:
    """One request, no hidden retries, no credential lookup, preserve failures."""
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc != "tds.gdex.ucar.edu" or not parsed.path.startswith("/thredds/"):
        raise ValueError("Only the reviewed public NCAR THREDDS endpoint is allowed")
    body, receipt = stem.with_suffix(".body"), stem.with_suffix(".receipt.json")
    if receipt.exists() or body.exists():
        if not resume or not receipt.exists() or not body.exists():
            raise ValueError("Existing observation preserved; use an explicit verified resume or a new output directory")
        saved = json.loads(receipt.read_text(encoding="utf-8"))
        data = body.read_bytes()
        request_path = stem.with_suffix(".request.json")
        if request_path.exists() and json.loads(request_path.read_text(encoding="utf-8")).get("url") != url:
            raise ValueError("Recorded request and expected URL differ")
        if not saved.get("complete") or saved.get("http_status") != 200 or saved.get("url") != url or saved.get("sha256") != sha(data) or saved.get("bytes") != len(data) or len(data) > cap:
            raise ValueError("Existing observation is incomplete, changed or belongs to another request")
        return data
    stem.parent.mkdir(parents=True, exist_ok=True)
    row = {"url": url, "cap_bytes": cap, "timeout_s": timeout, "retries": 0, "redirects": False,
           "credentials_read": False, "started_utc": datetime.now(timezone.utc).isoformat()}
    write_json(stem.with_suffix(".request.json"), row)
    start, data = time.monotonic(), bytearray()
    error = None
    try:
        request = urllib.request.Request(url, headers={"Accept-Encoding": "identity", "User-Agent": "Balloon-climate-raw-acquisition/0.57"})
        with urllib.request.build_opener(NoRedirect).open(request, timeout=timeout) as response:
            row["http_status"] = response.status
            row["headers"] = {k: v for k, v in response.headers.items() if k.lower() not in ("set-cookie", "authorization", "proxy-authorization")}
            if response.status != 200:
                raise ValueError("Only a complete HTTP200 response is accepted")
            while len(data) < cap:
                chunk = response.read(min(65536, cap - len(data)))
                if not chunk:
                    break
                data.extend(chunk)
            else:
                raise ValueError("Response reached the planned byte limit before proving EOF")
        row["complete"] = True
        with body.open("xb") as stream:
            stream.write(data)
    except Exception as exc:
        error = exc
        row["complete"] = False
        row["error"] = f"{type(exc).__name__}: {exc}"
        if isinstance(exc, http.client.IncompleteRead):
            data.extend(exc.partial[:max(0, cap-len(data))])
        if isinstance(exc, urllib.error.HTTPError):
            row["http_status"] = exc.code
            row["headers"] = {k: v for k, v in exc.headers.items() if k.lower() not in ("set-cookie", "authorization", "proxy-authorization")}
            try:
                data.extend(exc.read(max(0, cap-len(data))))
            except http.client.IncompleteRead as partial:
                data.extend(partial.partial[:max(0, cap-len(data))])
        with stem.with_suffix(".partial").open("xb") as stream:
            stream.write(data)
    row.update(bytes=len(data), sha256=sha(data), elapsed_seconds=time.monotonic()-start,
               finished_utc=datetime.now(timezone.utc).isoformat())
    write_json(receipt, row)
    print(json.dumps({"response": stem.name, **{k: row[k] for k in ("complete", "bytes", "elapsed_seconds")}}, ensure_ascii=False), flush=True)
    if error:
        raise error
    return bytes(data)


def wind_paths(catalog: bytes, year: int, month: int, transport: str = "dods") -> dict[tuple[int, str], str]:
    tree = ET.fromstring(catalog)
    service, base = {"dods": ("opendap", "/thredds/dodsC/"), "ncss": ("netcdfsubset", "/thredds/ncss/grid/")}[transport]
    if not any(e.attrib.get("serviceType", "").lower() == service and e.attrib.get("base") == base for e in tree.iter()):
        raise ValueError("Catalog no longer declares the reviewed transport service")
    result = {}
    for element in tree.iter():
        path = element.attrib.get("urlPath", "")
        m = re.fullmatch(r"files/g/d633000/e5\.oper\.an\.pl/(\d{6})/e5\.oper\.an\.pl\.128_(131_u|132_v)\.ll025uv\.(\d{8})00_(\d{8})23\.nc", path)
        if not m or m[1] != f"{year:04}{month:02}":
            continue
        if m[3] != m[4] or m[3][:6] != m[1]:
            raise ValueError("Unexpected daily analysis boundaries")
        day = date.fromisoformat(f"{m[3][:4]}-{m[3][4:6]}-{m[3][6:]}")
        key = (day.day, m[2][-1])
        if key in result:
            raise ValueError("Duplicate wind file in catalog")
        result[key] = path
    expected = {(day, component) for day in range(1, calendar.monthrange(year, month)[1]+1) for component in ("u", "v")}
    if set(result) != expected:
        raise ValueError("Catalog does not contain every daily U/V analysis for this month")
    return result


def selection(bounds=JRA_BOUNDS) -> dict:
    y0, y1 = math.ceil((90-bounds["north"])*4), math.floor((90-bounds["south"])*4)
    x0, x1 = math.ceil(bounds["west"]*4), math.floor(bounds["east"]*4)
    if not (0 <= y0 <= y1 <= 720 and 0 <= x0 <= x1 <= 1439):
        raise ValueError("Empty or unsupported non-wrapping bounds")
    return {"lat_indices": [y0, y1], "lon_indices": [x0, x1], "shape": [4, 37, y1-y0+1, x1-x0+1],
            "latitude": [90-i*.25 for i in range(y0, y1+1)], "longitude": [i*.25 for i in range(x0, x1+1)]}


def subset_url(path: str, component: str, axes: dict) -> str:
    if component not in ("u", "v") or not path.startswith("files/g/d633000/e5.oper.an.pl/"):
        raise ValueError("Unexpected wind source")
    y0, y1 = axes["lat_indices"]
    x0, x1 = axes["lon_indices"]
    constraint = f"{component.upper()}[0:6:18][0:1:36][{y0}:1:{y1}][{x0}:1:{x1}]"
    return DODS + path + ".dods?" + urllib.parse.quote(constraint, safe="")


def canonical_request(path: str, component: str, axes: dict, day: date) -> dict:
    parameter = {"u": "131_u", "v": "132_v"}.get(component)
    stamp = day.strftime("%Y%m%d")
    expected = f"files/g/d633000/e5.oper.an.pl/{stamp[:6]}/e5.oper.an.pl.128_{parameter}.ll025uv.{stamp}00_{stamp}23.nc"
    if parameter is None or path != expected:
        raise ValueError("Dataset path, component and requested date do not agree")
    return {"dataset": "d633000", "dataset_path": path, "component": component,
            "date_utc": day.isoformat(), "hours_utc": HOURS, "levels_hpa": LEVELS,
            "latitude": axes["latitude"], "longitude": axes["longitude"], "units": "m s**-1"}


def ncss_url(path: str, component: str, axes: dict, day: date) -> str:
    canonical_request(path, component, axes, day)
    query = {"var": component.upper(), "north": f"{max(axes['latitude']):g}",
             "south": f"{min(axes['latitude']):g}", "west": f"{min(axes['longitude']):g}",
             "east": f"{max(axes['longitude']):g}", "horizStride": "1",
             "time": "all", "timeStride": "6", "accept": "netCDF"}
    return NCSS + path + "?" + urllib.parse.urlencode(query)


def decode_ncss(body: bytes, component: str, axes: dict, day: date) -> tuple[np.ndarray, list[str]]:
    """Read original NetCDF3 bytes from the explicitly chosen NCSS service."""
    from scipy.io import netcdf_file
    if not body.startswith((b"CDF\x01", b"CDF\x02")):
        raise ValueError("NCSS did not return NetCDF3")
    def attribute(variable, name):
        value = getattr(variable, name, None)
        return value.decode("utf-8") if isinstance(value, bytes) else value
    with netcdf_file(io.BytesIO(body), "r", mmap=False) as source:
        names = [component.upper(), "time", "level", "latitude", "longitude"]
        if any(name not in source.variables for name in names):
            raise ValueError("Missing NCSS wind or coordinate variable")
        variables = source.variables
        wind = variables[component.upper()]
        if wind.dimensions != ("time", "level", "latitude", "longitude") or wind.data.dtype.kind != "f" or wind.data.dtype.itemsize != 4:
            raise ValueError("NCSS wind must retain Float32 and native dimension order")
        expected_units = {component.upper(): "m s**-1", "time": "hours since 1900-01-01 00:00:00",
                          "level": "hPa", "latitude": "degrees_north", "longitude": "degrees_east"}
        if any(attribute(variables[name], "units") != units for name, units in expected_units.items()) or attribute(variables["time"], "calendar") != "gregorian":
            raise ValueError("NCSS units or calendar differ from the reviewed source")
        for name in names[1:]:
            if variables[name].dimensions != (name,):
                raise ValueError("NCSS coordinate dimension differs")
            expected_type = ("i", 4) if name == "time" else ("f", 8)
            if (variables[name].data.dtype.kind, variables[name].data.dtype.itemsize) != expected_type:
                raise ValueError("NCSS coordinate type differs from the native source")
        if any(hasattr(variables[name], key) for name in names for key in ("scale_factor", "add_offset")):
            raise ValueError("Packed or scaled NCSS values are outside this exact native decoder")
        arrays = {name: variables[name].data.copy() for name in names}
        values = arrays[component.upper()]
        for key in ("_FillValue", "missing_value"):
            fill = getattr(wind, key, None)
            if fill is not None and np.any(values == fill):
                raise ValueError("NCSS contains a missing wind sample")
    expected_times = [datetime(day.year, day.month, day.day, hour, tzinfo=timezone.utc) for hour in HOURS]
    epoch = datetime(1900, 1, 1, tzinfo=timezone.utc)
    hours = [(t-epoch).total_seconds()/3600 for t in expected_times]
    if list(values.shape) != axes["shape"] or not all(np.array_equal(arrays[name], expected) for name, expected in
            (("time", hours), ("level", LEVELS), ("latitude", axes["latitude"]), ("longitude", axes["longitude"]))):
        raise ValueError("NCSS native coordinates or UTC support differ from the canonical request")
    if not np.isfinite(values).all() or (np.abs(values) >= 9e20).any():
        raise ValueError("NCSS wind contains nonfinite or fill values")
    return values.astype(np.float32).reshape(4, 37, -1), [t.isoformat().replace("+00:00", "Z") for t in expected_times]


def check_metadata(dds: bytes, das: bytes, component: str) -> None:
    d, a = dds.decode("ascii"), das.decode("utf-8")
    expected = rf"Float32\s+{component.upper()}\[time\s*=\s*24\]\[level\s*=\s*37\]\[latitude\s*=\s*721\]\[longitude\s*=\s*1440\]"
    if not re.search(expected, d) or not all(s in a for s in ('units "m s**-1"', 'units "hPa"', 'hours since 1900-01-01 00:00:00', 'calendar "gregorian"', '0.25 degree x 0.25 degree')):
        raise ValueError("ERA5 variable, units, axes or calendar no longer match the reviewed contract")


def decode_grid(body: bytes, component: str, axes: dict, day: date) -> tuple[np.ndarray, list[str]]:
    """Decode only the checked DAP2 Grid of primitive numeric arrays, exactly."""
    header, separator, binary = body.partition(b"\nData:\n")
    if not separator:
        raise ValueError("Not a DAP2 binary response")
    declarations = re.findall(r"(Float32|Float64|Int32)\s+([A-Za-z_][A-Za-z_0-9]*)\s*((?:\[[^\]]+\])+);", header.decode("ascii"))
    expected_names = [component.upper(), "time", "level", "latitude", "longitude"]
    if [r[1] for r in declarations] != expected_names:
        raise ValueError("Unexpected DAP2 arrays or order")
    if [r[0] for r in declarations] != ["Float32", "Int32", "Float64", "Float64", "Float64"]:
        raise ValueError("Unexpected native DAP2 value or coordinate type")
    offset, arrays = 0, {}
    for dtype, name, dimensions in declarations:
        sizes = [int(n) for n in re.findall(r"=\s*(\d+)\]", dimensions)]
        n = math.prod(sizes)
        if len(binary) < offset+8:
            raise ValueError("Truncated DAP2 count")
        if struct.unpack_from(">II", binary, offset) != (n, n):
            raise ValueError("DAP2 array count mismatch")
        offset += 8
        dt = np.dtype({"Float32": ">f4", "Float64": ">f8", "Int32": ">i4"}[dtype])
        if len(binary) < offset+n*dt.itemsize:
            raise ValueError("Truncated DAP2 values")
        arrays[name] = np.frombuffer(binary, dtype=dt, count=n, offset=offset).reshape(sizes).copy()
        offset += n*dt.itemsize
    if offset != len(binary):
        raise ValueError("Unexpected trailing DAP2 data")
    values = arrays[component.upper()]
    epoch = datetime(1900, 1, 1, tzinfo=timezone.utc)
    expected_times = [datetime(day.year, day.month, day.day, h, tzinfo=timezone.utc) for h in HOURS]
    if list(values.shape) != axes["shape"] or not np.array_equal(arrays["latitude"], axes["latitude"]) or not np.array_equal(arrays["longitude"], axes["longitude"]) or not np.array_equal(arrays["level"], LEVELS):
        raise ValueError("Returned native coordinates or level support do not match the request")
    if [epoch+timedelta(hours=int(t)) for t in arrays["time"]] != expected_times:
        raise ValueError("Returned UTC analysis times do not match the selected hours")
    if not np.isfinite(values).all() or (np.abs(values) >= 9e20).any():
        raise ValueError("Missing or nonfinite wind sample; do not publish partial month")
    return values.astype(np.float32).reshape(4, 37, -1), [t.isoformat().replace("+00:00", "Z") for t in expected_times]


def grid_cells(axes: dict) -> list[dict]:
    cells = []
    for iy, lat in enumerate(axes["latitude"], axes["lat_indices"][0]):
        # Exact spherical strip area, with a common longitude width factor omitted.
        weight = math.sin(math.radians(lat+.125))-math.sin(math.radians(lat-.125))
        for ix, lon in enumerate(axes["longitude"], axes["lon_indices"][0]):
            cells.append({"cell_id": iy*1440+ix, "lat": lat, "lon": lon, "weight": weight})
    return cells


def probe(output: Path, metadata: Path) -> None:
    paths = wind_paths((metadata/"catalog-202401.body").read_bytes(), 2024, 1)
    check_metadata((metadata/"u-20240101-dds.body").read_bytes(), (metadata/"u-20240101-das.body").read_bytes(), "u")
    axes = selection()
    url = subset_url(paths[(1, "u")], "u", axes)
    body = fetch(url, output/"u-20240101", 1_500_000)
    values, times = decode_grid(body, "u", axes, date(2024, 1, 1))
    write_json(output/"decoded.json", {"shape": list(values.shape), "times_utc": times, "axes": axes,
               "levels_hpa": LEVELS, "finite": bool(np.isfinite(values).all()), "u_min": float(values.min()), "u_max": float(values.max()),
               "first_values": values.reshape(-1)[:8].tolist(), "grid_count": len(grid_cells(axes)),
               "numeric_bytes_per_uv_year_2024": 366*4*37*len(grid_cells(axes))*4*2,
               "scope": "one U day only, not a complete U/V day, month or year"})


def cached_observation(url: str, stem: Path, cap: int, *, resume: bool,
                       require_request: bool = False) -> tuple[bytes, dict] | None:
    """Read all three recorded slots; this never grants a new attempt."""
    found = None
    recorded = [number for number in range(1, 4) if (stem.parent/(stem.name+f"-attempt{number:02}.receipt.json")).exists()]
    if recorded and recorded != list(range(1, max(recorded)+1)):
        raise ValueError("Recorded attempts contain a gap; preserve and review the history")
    for number in range(1, 4):
        target = stem.parent/(stem.name+f"-attempt{number:02}")
        receipt = target.with_suffix(".receipt.json")
        request = target.with_suffix(".request.json")
        body = target.with_suffix(".body")
        if not receipt.exists():
            if request.exists() or body.exists() or target.with_suffix(".partial").exists():
                raise ValueError("Pending or incomplete observation has no receipt; review before resume")
            continue
        row = json.loads(receipt.read_text(encoding="utf-8"))
        if not resume or row.get("url") != url:
            raise ValueError("Existing attempt preserved; explicit matching resume required")
        if require_request and not request.exists():
            raise ValueError("Recorded request is required for canonical sample reuse")
        if request.exists() and json.loads(request.read_text(encoding="utf-8")).get("url") != url:
            raise ValueError("Recorded request and expected URL differ")
        if row.get("complete"):
            data = fetch(url, target, cap, resume=True)
            record = {"receipt": str(receipt), "url": url, "bytes": len(data), "sha256": sha(data)}
            if found is not None and data != found[0]:
                raise ValueError("Conflicting complete observations for one exact request")
            if found is None:
                found = data, record
    return found


def observation(url: str, stem: Path, cap: int, *, resume: bool, attempts: int,
                timeout: int = 60, stop: threading.Event | None = None) -> tuple[bytes, dict]:
    """Keep each bounded attempt distinct; resume only this acquisition's output."""
    if not 1 <= attempts <= 3:
        raise ValueError("At most three recorded attempts per response")
    # An explicitly reviewed recovery probe may have supplied a later complete
    # observation. Reuse verified bytes without making a new HTTP request; this
    # does not permit automatic retry of any recorded HTTP rejection.
    cached = cached_observation(url, stem, cap, resume=resume)
    if cached is not None:
        return cached
    for number in range(1, attempts+1):
        target = stem.parent/(stem.name+f"-attempt{number:02}")
        receipt = target.with_suffix(".receipt.json")
        if receipt.exists():
            row = json.loads(receipt.read_text(encoding="utf-8"))
            if not resume or row.get("url") != url:
                raise ValueError("Existing attempt preserved; explicit matching resume required")
            if not row.get("complete"):
                if row.get("http_status", 0) >= 400:
                    raise ValueError("Recorded HTTP rejection requires review, not automatic retry")
                continue
            data = fetch(url, target, cap, resume=True)
            return data, {"receipt": str(receipt), "url": url, "bytes": len(data), "sha256": sha(data)}
        if stop is not None and stop.is_set():
            raise RuntimeError("Earlier request failed; no further request started")
        if number > 1:
            if stop is None:
                time.sleep(5)
            elif stop.wait(5):
                raise RuntimeError("Earlier request failed; no retry started")
        try:
            data = fetch(url, target, cap, timeout=timeout)
            return data, {"receipt": str(receipt), "url": url, "bytes": len(data), "sha256": sha(data)}
        except (OSError, http.client.HTTPException) as exc:
            if isinstance(exc, urllib.error.HTTPError):
                raise
            if number == attempts:
                raise RuntimeError(f"Response failed after {number} recorded attempt(s): {url}") from exc
    raise ValueError("All configured attempts are already recorded as failed; inspect them before another run")


def attempt_history(stem: Path) -> list[dict]:
    rows = []
    for number in range(1, 4):
        path = stem.parent/(stem.name+f"-attempt{number:02}.receipt.json")
        if path.exists():
            row = json.loads(path.read_text(encoding="utf-8"))
            rows.append({"attempt": number, "receipt": str(path), "complete": bool(row.get("complete")),
                         "http_status": row.get("http_status"), "sha256": row.get("sha256")})
    return rows


def daily_observation(output: Path, path: str, component: str, axes: dict, day: date, *,
                      transport: str, resume: bool, attempts: int, timeout: int,
                      stop: threading.Event | None = None) -> tuple[np.ndarray, list[str], dict]:
    canonical = canonical_request(path, component, axes, day)
    stamp = day.strftime("%Y%m%d")
    dods_stem = output/"responses"/f"{component}-{stamp}"
    dods_url = subset_url(path, component, axes)
    if transport == "dods":
        body, record = observation(dods_url, dods_stem, 1_500_000, resume=resume, attempts=attempts, timeout=timeout, stop=stop)
        array, times = decode_grid(body, component, axes, day)
        return array, times, record
    if transport != "ncss":
        raise ValueError("Choose an explicit supported transport")
    saved = cached_observation(dods_url, dods_stem, 1_500_000, resume=resume, require_request=True)
    url = ncss_url(path, component, axes, day)
    ncss_stem = output/"responses"/f"ncss-{component}-{stamp}"
    saved_ncss = cached_observation(url, ncss_stem, 5*1024*1024, resume=resume, require_request=True)
    if saved is not None:
        array, times = decode_grid(saved[0], component, axes, day)
        if saved_ncss is not None:
            other, other_times = decode_ncss(saved_ncss[0], component, axes, day)
            if array.tobytes() != other.tobytes() or times != other_times:
                raise ValueError("DODS and NCSS cached values disagree for the same canonical request")
        return array, times, saved[1]
    body, record = saved_ncss if saved_ncss is not None else observation(
        url, ncss_stem, 5*1024*1024, resume=resume, attempts=attempts, timeout=timeout, stop=stop)
    array, times = decode_ncss(body, component, axes, day)
    canonical_sha = sha(json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    prior = attempt_history(dods_stem)
    record.update(transport="ncss", canonical_request=canonical, canonical_sha256=canonical_sha,
                  prior_dods_attempts=[{**r, "receipt": str(Path(r["receipt"]).relative_to(output)).replace('\\', '/')} for r in prior])
    print(json.dumps({"sample": f"{component}-{stamp}", "transport": "ncss",
                      "dods_recorded_attempts": len(prior), "dods_lifetime_limit": 3,
                      "ncss_recorded_attempts": len(attempt_history(ncss_stem)), "ncss_configured_limit": attempts}), flush=True)
    return array, times, record


def save_npy(path: Path, array: np.ndarray, *, resume: bool) -> dict:
    import io
    stream = io.BytesIO()
    np.save(stream, array, allow_pickle=False)
    content = stream.getvalue()
    if path.exists():
        if not resume or path.read_bytes() != content:
            raise ValueError("Existing month array differs; original is preserved")
    else:
        with path.open("xb") as output:
            output.write(content)
    return {"file": path.name, "sha256": sha(content), "bytes": len(content)}


def month_record(output: Path, year: int, month: int, u: np.ndarray, v: np.ndarray,
                 times: list[str], axes: dict, *, resume: bool) -> dict:
    expected = [f"{year:04}-{month:02}-{day:02}T{hour:02}:00:00Z"
                for day in range(1, calendar.monthrange(year, month)[1]+1) for hour in HOURS]
    shape = (len(expected), len(LEVELS), len(grid_cells(axes)))
    if times != expected or u.shape != shape or v.shape != shape or u.dtype != np.float32 or v.dtype != np.float32 or not np.isfinite(u).all() or not np.isfinite(v).all() or (np.abs(u) >= 9e20).any() or (np.abs(v) >= 9e20).any():
        raise ValueError("Both complete monthly component arrays and every requested UTC time are required")
    return {"month": month, "times_utc": times,
            "u": save_npy(output/f"u-{year:04}-{month:02}.npy", u, resume=resume),
            "v": save_npy(output/f"v-{year:04}-{month:02}.npy", v, resume=resume)}


def acquire(output: Path, year: int, months: list[int], *, resume: bool, attempts: int, workers: int = 1,
            timeout: int = 60, transport: str = "dods") -> None:
    if year < 1940 or year > datetime.now(timezone.utc).year or len(months) != len(set(months)) or not months or any(m not in range(1, 13) for m in months):
        raise ValueError("Explicit distinct calendar months and a supported calendar year are required")
    if workers not in range(1, 5):
        raise ValueError("Explicit local concurrency limit is 1–4 workers, not a provider limit")
    if timeout not in (60, 120):
        raise ValueError("Explicit finite timeout must be 60 or 120 seconds")
    if transport not in ("dods", "ncss"):
        raise ValueError("Choose an explicit supported transport")
    current = output/"manifest.json"
    if current.exists():
        prior = json.loads(current.read_text(encoding="utf-8"))
        published = [row["month"] for row in prior["months"]]
        if not resume or prior.get("schema") != "balloon.wind-samples/1" or prior.get("provider") != "ERA5" or prior.get("years") != [year, year] or published != sorted(months)[:len(published)]:
            raise ValueError("Resume months must reproduce the already published calendar prefix and source")
    if transport == "ncss":
        from scipy.io import netcdf_file  # Fail before HTTP if the existing runtime lacks this decoder.
    print(json.dumps({"explicit_transport": transport, "new_transport_attempt_limit": attempts,
                      "dods_historical_limit": 3, "workers": workers, "automatic_transport_fallback": False}), flush=True)
    output.mkdir(parents=True, exist_ok=True)
    axes = selection()
    completed, requests, metadata = [], [], []
    for month in sorted(months):
        ym = f"{year:04}{month:02}"
        catalog, record = observation(CATALOG.format(ym=ym), output/"responses"/f"catalog-{ym}", 1_048_576, resume=resume, attempts=attempts, timeout=timeout)
        metadata.append(record)
        paths = wind_paths(catalog, year, month, transport)
        for component in ("u", "v"):
            base = DODS+paths[(1, component)]
            if transport == "dods":
                dds, rd = observation(base+".dds", output/"responses"/f"{component}-{ym}-dds", 65536, resume=resume, attempts=attempts, timeout=timeout)
                das, ra = observation(base+".das", output/"responses"/f"{component}-{ym}-das", 65536, resume=resume, attempts=attempts, timeout=timeout)
                check_metadata(dds, das, component)
                metadata.extend([rd, ra])
            else:
                # Preserve old metadata order/checkpoints; never send DODS for NCSS.
                dds = cached_observation(base+".dds", output/"responses"/f"{component}-{ym}-dds", 65536, resume=resume)
                das = cached_observation(base+".das", output/"responses"/f"{component}-{ym}-das", 65536, resume=resume)
                if dds is not None and das is not None:
                    check_metadata(dds[0], das[0], component)
                metadata.extend(r[1] for r in (dds, das) if r is not None)
        arrays = {c: [] for c in ("u", "v")}
        times = []
        stop = threading.Event()
        def one(item):
            day, component = item
            if stop.is_set():
                raise RuntimeError("Earlier request failed; no further request started")
            try:
                array, returned_times, record = daily_observation(output, paths[item], component, axes, date(year, month, day),
                    transport=transport, resume=resume, attempts=attempts, timeout=timeout, stop=stop)
                return day, component, array, returned_times, record
            except Exception:
                stop.set()
                raise
        tasks = [(day, component) for day in range(1, calendar.monthrange(year, month)[1]+1) for component in ("u", "v")]
        pool = ThreadPoolExecutor(max_workers=workers)
        try:
            day_times = None
            for day, component, array, returned_times, record in pool.map(one, tasks):
                if component == "u":
                    day_times = returned_times
                elif day_times != returned_times:
                    raise ValueError("U/V times differ")
                else:
                    times.extend(returned_times)
                arrays[component].append(array)
                requests.append(record)
        finally:
            pool.shutdown(wait=True, cancel_futures=True)
        completed.append(month_record(output, year, month, np.concatenate(arrays["u"]), np.concatenate(arrays["v"]), times, axes, resume=resume))
        manifest = {"schema": "balloon.wind-samples/1", "provider": "ERA5",
                    "label": f"ERA5 / NCAR 0.25° · {year}年原標本（UTC 00/06/12/18）",
                    "years": [year, year], "date_convention": "UTC", "hours_utc": HOURS,
                    "grid": grid_cells(axes), "levels": [{"level_id": i, "level_hpa": p} for i, p in enumerate(LEVELS)],
                    "months": completed, "weighting": "spherical-area-equal-times",
                    "provenance": {"dataset": "d633000", "dataset_url": "https://gdex.ucar.edu/datasets/d633000/",
                                   "dataset_doi": "10.5065/BH6N-5N20", "source_grid": "0.25 degree latitude-longitude, no remapping",
                                   "attribution": {"license": "Creative Commons Attribution 4.0 International",
                                                   "license_url": "https://creativecommons.org/licenses/by/4.0/",
                                                   "acknowledgement": "Contains modified Copernicus Climate Change Service information.",
                                                   "responsibility_notice_ja": "含まれるCopernicus情報・データの利用について欧州委員会およびECMWFは責任を負わない旨を配布元が示す。",
                                                   "source_page_observed_utc": "2026-10-02", "provider": "ECMWF / Copernicus Climate Change Service, distributed by NSF NCAR GDEX"},
                                   "selection_bounds": JRA_BOUNDS, "native_hourly_subset": HOURS,
                                   "pressure_level_warning": "Finite pressure-level winds may include below-ground extrapolation; not a flight weather field",
                                   "conversion": "DAP2 Float32 to numpy float32, native time/level/lat/lon order, cells latitude-major",
                                   "weight_definition": "sin(latitude+0.125deg)-sin(latitude-0.125deg), equal UTC times; common longitude width omitted",
                                   "requests": [{**r, "receipt": str(Path(r["receipt"]).relative_to(output)).replace('\\', '/')} for r in requests],
                                   "metadata": [{**r, "receipt": str(Path(r["receipt"]).relative_to(output)).replace('\\', '/')} for r in metadata]}}
        if any(r.get("transport") == "ncss" for r in requests):
            manifest["provenance"]["conversion"] = "NCAR DAP2 and/or NCSS NetCDF3 Float32 to numpy float32; same native time/level/lat/lon order, cells latitude-major; each original service response retained"
            manifest["provenance"]["service_policy"] = "NCSS explicitly selected for missing samples; verified earlier DODS samples reused; no automatic service fallback"
        checkpoint = output/f"manifest-through-{month:02}.json"
        if checkpoint.exists():
            if not resume or json.loads(checkpoint.read_text(encoding="utf-8")) != manifest:
                raise ValueError("Existing complete-month checkpoint differs")
        else:
            write_json(checkpoint, manifest)
        # The public pointer changes only after both full arrays and their hashes exist.
        current = output/"manifest.json"
        old_months = json.loads(current.read_text(encoding="utf-8"))["months"] if current.exists() else []
        if len(completed) >= len(old_months):
            pending = output/"manifest.next.json"
            write_json(pending, manifest)
            pending.replace(current)
        print(json.dumps({"month_complete": f"{year}-{month:02}", "times": len(times), "cells": len(grid_cells(axes)),
                          "manifest_sha256": sha((output/"manifest.json").read_bytes())}), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["probe", "acquire"])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--months", type=int, nargs="+")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--attempts", type=int, choices=[1, 2, 3], default=1)
    parser.add_argument("--workers", type=int, choices=[1, 2, 3, 4], default=1)
    parser.add_argument("--timeout", type=int, choices=[60, 120], default=60)
    parser.add_argument("--transport", choices=["dods", "ncss"], default="dods")
    args = parser.parse_args()
    if args.command == "probe":
        if args.transport != "dods":
            parser.error("probe only supports the original DODS transport; use an explicitly reviewed NCSS acquisition")
        if args.metadata is None:
            parser.error("--metadata is required for the bounded probe")
        probe(args.output, args.metadata)
    else:
        if not args.months:
            parser.error("--months must explicitly name the calendar months to acquire")
        acquire(args.output, args.year, args.months, resume=args.resume, attempts=args.attempts, workers=args.workers, timeout=args.timeout, transport=args.transport)


if __name__ == "__main__":
    main()
