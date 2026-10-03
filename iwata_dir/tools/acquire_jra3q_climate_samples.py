"""Bounded, resumable acquisition of original JRA anl_p wind samples.

Only --execute performs network requests. --months/--years and both acquisition
budgets are explicit. Complete months for the explicitly selected contiguous
years form a separate balloon.wind-samples/1 source; a single year is never
labelled 2016--2025. Original responses and manifest versions remain on disk.
"""
from __future__ import annotations

import argparse
import calendar
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import shutil
import struct
import threading
import time
import urllib.parse
import urllib.request
import uuid
import xml.etree.ElementTree as ET

import numpy as np

ORIGIN = "https://tds.gdex.ucar.edu"
YEARS = list(range(2016, 2026))
META_CAP = 512 * 1024
DATA_CAP = 2560 * 1024
VARIABLES = {"u": "ugrd-pres-an-gauss", "v": "vgrd-pres-an-gauss"}
NS = {"t": "http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def atomic_json(path, value):
    path = Path(path)
    data = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    tmp = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    tmp.write_bytes(data)
    os.replace(tmp, path)
    return hashlib.sha256(data).hexdigest()


def regular_path(root, relative):
    path = root / relative
    require(path.resolve().is_relative_to(root.resolve()), "path escapes output")
    require(not any(p.is_symlink() for p in [path, *path.parents] if p != root.parent), "symlink is unsupported")
    return path


def read_basis(database):
    import duckdb
    database = Path(database).resolve()
    before = digest(database)
    with duckdb.connect(str(database), read_only=True, config={"enable_external_access": False, "threads": 1}) as con:
        meta = dict(con.execute("SELECT key,value FROM meta_dataset").fetchall())
        require(meta.get("source_product") == "anl_p" and meta.get("years") == "2016-2025", "expected supplied ten-year anl_p database")
        grid = [dict(zip(("cell_id", "lat", "lon"), row)) for row in con.execute("SELECT cell_id,lat,lon FROM dim_grid ORDER BY cell_id").fetchall()]
        levels = [dict(zip(("level_id", "level_hpa"), row)) for row in con.execute("SELECT level_id,level_hpa FROM dim_level ORDER BY level_id").fetchall()]
        weights = [row[0] for row in con.execute("SELECT gauss_weight FROM dim_grid ORDER BY cell_id").fetchall()]
    require(len(grid) == 570 and len(levels) == 38, "expected 570 cells and 38 levels")
    require(digest(database) == before, "database changed while reading")
    require(all(np.isfinite(w) and w > 0 for w in weights), "invalid Gaussian weights")
    return {"dataset_sha256": before, "years": [2016, 2025], "grid": grid, "levels": levels, "gaussian_weights": weights}


def read_basis_file(path):
    """Only coordinates/weights from the provided grid, without needing its DB."""
    require(path.is_file() and path.stat().st_size < 200000, 'basis file size')
    data = path.read_bytes()
    value = json.loads(data)
    require(value.get('schema') == 'balloon.jra3q.native-basis/1', 'basis schema')
    require(re.fullmatch('[0-9a-f]{64}', value.get('dataset_sha256', '')) is not None, 'basis dataset digest')
    grid, levels, weights = value['grid'], value['levels'], value['gaussian_weights']
    require(len(grid) == 570 and len(levels) == 38 and len(weights) == 570, 'basis dimensions')
    require([c['cell_id'] for c in grid] == list(range(570)) and [l['level_id'] for l in levels] == list(range(38)), 'basis IDs')
    # Check the grid independently against the Gaussian quadrature, not the DB.
    nodes, gaussian = np.polynomial.legendre.leggauss(480)
    latitudes = np.degrees(np.arcsin(nodes))
    expected_latitudes = latitudes[::-1][115:134][::-1].astype(np.float32)
    expected_levels = [3,5,7,10,20,30,40,50,60,70,85,100,125,150,175,200,225,250,300,350,400,450,500,550,600,650,700,750,775,800,825,850,875,900,925,950,975,1000]
    require([level['level_hpa'] for level in levels] == expected_levels, 'basis fixed pressure levels')
    for i, (cell, weight) in enumerate(zip(grid, weights)):
        matches = np.flatnonzero(latitudes.astype(np.float32) == np.float32(cell['lat']))
        require(len(matches) == 1 and abs(weight-gaussian[matches[0]]) < 1e-8, 'basis Gaussian latitude/weight')
        require(np.isfinite(cell['lon']) and 0 <= cell['lon'] < 360 and abs(cell['lon']/.375-round(cell['lon']/.375)) < 1e-8, 'basis longitude')
        require(cell['lat'] == float(expected_latitudes[i//30]) and cell['lon'] == 138 + .375 * (i%30), 'basis fixed Hokkaido grid/order')
    require(len({(c['lat'],c['lon']) for c in grid}) == 570 and len({l['level_hpa'] for l in levels}) == 38, 'basis duplicated coordinates')
    return {**value, 'basis_file_sha256': hashlib.sha256(data).hexdigest()}


def month_times(year, month):
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    return [start + timedelta(hours=6 * i) for i in range(calendar.monthrange(year, month)[1] * 4)]


def utc_string(value):
    return value.strftime("%Y-%m-%dT%H:%M:%SZ")


def catalog_url(year, month):
    return f"{ORIGIN}/thredds/catalog/files/g/d640000/anl_p/{year}{month:02d}/catalog.xml"


def catalog_entries(data, year, month):
    root = ET.fromstring(data)
    result = {}
    for component, variable in VARIABLES.items():
        entries = []
        pattern = re.compile(r"^files/g/d640000/anl_p/" + f"{year}{month:02d}/jra3q.anl_p.0_2_{2 if component == 'u' else 3}." + re.escape(variable) + r"\.(\d{10})_(\d{10})\.nc$")
        for element in root.findall(".//t:dataset", NS):
            path = element.get("urlPath", "")
            match = pattern.fullmatch(path)
            if match:
                start, end = [datetime.strptime(t, "%Y%m%d%H").replace(tzinfo=timezone.utc) for t in match.groups()]
                entries.append({"path": path, "component": component, "start": start, "end": end})
        entries.sort(key=lambda e: e["start"])
        require(len(entries) == 6, "expected six five-day/last-day files per component")
        observed = []
        for entry in entries:
            count = int((entry["end"] - entry["start"]).total_seconds() / 21600) + 1
            require(count in (12, 16, 20, 24) and entry["end"] >= entry["start"], "unsupported source interval")
            observed.extend(entry["start"] + timedelta(hours=6 * i) for i in range(count))
        require(observed == month_times(year, month), "catalog month has a gap, overlap or wrong UTC")
        result[component] = entries
    require([(r["start"], r["end"]) for r in result["u"]] == [(r["start"], r["end"]) for r in result["v"]], "u/v catalog intervals differ")
    return result


def metadata_axes(data, component, basis):
    root = ET.fromstring(data)
    grid = root.find("gridSet/grid")
    require(grid is not None and grid.get("name") == VARIABLES[component] and grid.get("type") == "float", "wrong NCSS wind variable")
    attributes = {e.get("name"): e.get("value") for e in grid}
    require(attributes.get("units") == "m s-1" and attributes.get("data_type") == "analysis" and attributes.get("group") == "anl_p", "unsupported wind units or product")
    axes = {}
    for name in ("pressure_level", "lat", "lon"):
        values = root.find(f"axis[@name='{name}']/values")
        require(values is not None, "coordinate metadata missing")
        if values.text and values.text.strip():
            axis = np.array([float(x) for x in values.text.split()], dtype=np.float64)
        else:
            axis = float(values.get("start")) + np.arange(int(values.get("npts"))) * float(values.get("resolution"))
        require(np.isfinite(axis).all() and len(np.unique(axis)) == len(axis), "coordinate axis is invalid")
        axes[name] = axis
    require(len(axes["lat"]) == 480 and len(axes["lon"]) == 960 and len(axes["pressure_level"]) == 45, "expected regular N240 pressure product")
    indices = {}
    for name, target in [("pressure_level", [r["level_hpa"] for r in basis["levels"]]), ("lat", sorted({r["lat"] for r in basis["grid"]})), ("lon", sorted({r["lon"] for r in basis["grid"]}))]:
        converted = axes[name].astype(np.float32)
        found = []
        for value in target:
            hits = np.flatnonzero(converted == np.float32(value))
            require(len(hits) == 1, "DB coordinate has no unique native Float32 match")
            found.append(int(hits[0]))
        unique = sorted(found)
        require(unique == list(range(unique[0], unique[-1] + 1)), "requested axis is not contiguous")
        indices[name] = [unique[0], unique[-1]]
    fills = [float(attributes[name]) for name in ("_FillValue", "missing_value") if name in attributes]
    require(fills and all(np.isfinite(f) for f in fills), "declared finite missing-value metadata is required")
    return axes, indices, fills


def data_url(entry, indices):
    count = int((entry["end"] - entry["start"]).total_seconds() / 21600) + 1
    slices = [(0, count - 1), *(indices[n] for n in ("pressure_level", "lat", "lon"))]
    constraint = VARIABLES[entry["component"]] + "".join(f"[{a}:1:{b}]" for a, b in slices)
    return ORIGIN + "/thredds/dodsC/" + entry["path"] + ".dods?" + urllib.parse.quote(constraint, safe="")


def decode_dods(data, variable, expected_path=None, fill_values=(9.999e20,)):
    """Strict DAP2 numeric Grid/XDR subset; never evaluate remote text."""
    require(len(data) <= DATA_CAP, "DODS body exceeds cap")
    parts = data.split(b"\nData:\n", 1)
    require(len(parts) == 2 and len(parts[0]) < 16384, "DODS header separator missing")
    header, payload = parts[0].decode("ascii"), parts[1]
    v = re.escape(variable)
    pattern = (r"\s*Dataset\s*\{\s*Grid\s*\{\s*ARRAY:\s*Float32\s+" + v +
        r"\[time = (\d+)\]\[pressure_level = (\d+)\]\[lat = (\d+)\]\[lon = (\d+)\];\s*MAPS:\s*" +
        r"Int32 time\[time = (\d+)\];\s*Float64 pressure_level\[pressure_level = (\d+)\];\s*" +
        r"Float64 lat\[lat = (\d+)\];\s*Float64 lon\[lon = (\d+)\];\s*\}\s*" + v + r";\s*\}\s*([^;]+);\s*")
    match = re.fullmatch(pattern, header)
    require(match is not None, "unsupported DODS Grid layout")
    dims = tuple(int(x) for x in match.groups()[:4])
    require(dims == tuple(int(x) for x in match.groups()[4:8]) and all(0 < n <= cap for n, cap in zip(dims, (24, 38, 19, 30))), "DODS map dimensions differ or exceed target bounds")
    require(np.prod(dims, dtype=np.int64) <= 24 * 38 * 570, "unexpected subset size")
    require(expected_path is None or match[9].strip() == expected_path, "DODS source path differs")
    offset = 0

    def array(count, dtype):
        nonlocal offset
        require(offset + 8 <= len(payload), "truncated XDR array count")
        first, second = struct.unpack_from(">II", payload, offset)
        require(first == second == count, "XDR array count differs")
        offset += 8
        size = np.dtype(dtype).itemsize * count
        require(offset + size <= len(payload), "truncated XDR values")
        value = np.frombuffer(payload, dtype=dtype, count=count, offset=offset).copy()
        offset += size
        return value

    wind = array(int(np.prod(dims)), ">f4").reshape(dims)
    axes = {name: array(n, dtype) for name, n, dtype in zip(("time", "pressure_level", "lat", "lon"), dims, (">i4", ">f8", ">f8", ">f8"))}
    require(offset == len(payload), "DODS has trailing data")
    require(not any(np.any(wind == np.float32(fill)) for fill in fill_values), "wind contains declared missing/fill value")
    require(np.isfinite(wind).all() and np.max(np.abs(wind)) < 1000, "wind is missing/nonfinite/outside physical guard")
    require(all(np.isfinite(a).all() and len(np.unique(a)) == len(a) for a in axes.values()), "DODS coordinate is invalid")
    return wind, axes


def reorder_subset(data, entry, basis, fill_values=(9.999e20,)):
    wind, axes = decode_dods(data, VARIABLES[entry["component"]], entry["path"], fill_values)
    times = [datetime(1900, 1, 1, tzinfo=timezone.utc) + timedelta(hours=int(h)) for h in axes["time"]]
    expected = [entry["start"] + timedelta(hours=6 * i) for i in range(int((entry["end"] - entry["start"]).total_seconds() / 21600) + 1)]
    require(times == expected, "returned UTC analyses differ from request")

    def index(name, values):
        a = axes[name].astype(np.float32)
        result = []
        for value in values:
            hits = np.flatnonzero(a == np.float32(value))
            require(len(hits) == 1, "returned coordinate does not match DB")
            result.append(int(hits[0]))
        return np.array(result)

    levels = index("pressure_level", [r["level_hpa"] for r in basis["levels"]])
    lat = index("lat", [r["lat"] for r in basis["grid"]])
    lon = index("lon", [r["lon"] for r in basis["grid"]])
    require(wind.shape[1:] == (len(basis["levels"]), 19, 30), "returned subset does not cover target population")
    return wind[:, levels, :, :][:, :, lat, lon].astype(np.float32), times


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class HttpCache:
    def __init__(self, root, max_requests, max_bytes, timeout=60, seed=None, attempts=1):
        self.root = root
        self.directory = root / "download-cache"
        self.directory.mkdir(exist_ok=True)
        self.max_requests, self.max_bytes, self.timeout = max_requests, max_bytes, timeout
        require(type(attempts) is int and 1 <= attempts <= 3, 'attempts must be 1--3')
        self.attempts = attempts
        self.requests = self.bytes = self.reserved = 0
        self.lock = threading.Lock()
        self.stopped = False
        self.seed = {}
        if seed:
            for path in Path(seed).glob("*receipt.json"):
                try:
                    record = json.loads(path.read_text(encoding="utf-8"))
                    if record.get("status") == 200 and record.get("complete") is not False and record.get("body") and record.get("url"):
                        self.seed[record["url"]] = (path.parent, record)
                except (OSError, ValueError):
                    pass

    def locations(self, url):
        key = hashlib.sha256(url.encode()).hexdigest()
        return self.directory / (key + ".body"), self.directory / (key + ".json")

    def cached(self, url):
        body, receipt = self.locations(url)
        if not body.exists() and not receipt.exists():
            return None
        require(body.is_file() and receipt.is_file() and not body.is_symlink() and not receipt.is_symlink(), "incomplete cache entry; preserve it and inspect")
        r = json.loads(receipt.read_text(encoding="utf-8"))
        require(r.get("url") == url and r.get("complete") is True and r["bytes"] == body.stat().st_size and r["sha256"] == digest(body), "cached response failed identity/hash verification")
        return body, r

    def get(self, url, cap):
        for attempt in range(1, self.attempts + 1):
            try:
                return self._get_once(url, cap, attempt)
            except Exception as exc:
                reason = exc.reason if isinstance(exc, urllib.error.URLError) and not isinstance(exc, urllib.error.HTTPError) else exc
                if isinstance(reason, (TimeoutError, http.client.IncompleteRead, ConnectionResetError)) and attempt < self.attempts and not self.stopped:
                    time.sleep(5)
                    continue
                with self.lock:
                    self.stopped = True
                raise

    def _get_once(self, url, cap, attempt):
        cached = self.cached(url)
        if cached:
            require(cached[1]["bytes"] <= cap, "cache exceeds request cap")
            return cached
        body, receipt = self.locations(url)
        if url in self.seed:
            directory, record = self.seed[url]
            original = regular_path(directory, record["body"])
            sha = record.get("body_sha256", record.get("sha256"))
            size = record.get("body_bytes", record.get("bytes"))
            require(original.is_file() and original.stat().st_size == size and size <= cap and digest(original) == sha, "seed response failed verification")
            shutil.copyfile(original, body)
            r = {"url": url, "complete": True, "bytes": size, "sha256": sha, "seed_receipt": record}
            atomic_json(receipt, r)
            return body, r
        require(url.startswith(ORIGIN + "/thredds/") and "@" not in urllib.parse.urlsplit(url).netloc, "unsupported data origin")
        with self.lock:
            require(not self.stopped, "acquisition stopped after another failure")
            require(self.requests < self.max_requests and self.bytes + self.reserved + cap <= self.max_bytes, "explicit request/byte budget exhausted")
            self.requests += 1
            self.reserved += cap
        started = time.monotonic()
        r = {"url": url, "complete": False, "started_utc": utc_string(datetime.now(timezone.utc)), "cap_bytes": cap, "timeout_seconds": self.timeout, "attempt": attempt, "retries": attempt-1, "redirects": False}
        partial = body.with_name(body.name + ".partial-" + uuid.uuid4().hex)
        size = 0
        try:
            opener = urllib.request.build_opener(NoRedirect)
            request = urllib.request.Request(url, headers={"Accept-Encoding": "identity", "User-Agent": "Balloon-JP-climate-samples/0.57"})
            with opener.open(request, timeout=self.timeout) as response, partial.open("xb") as stream:
                require(response.status == 200, "expected HTTP 200")
                r["status"] = response.status
                r["headers"] = dict(response.headers)
                while True:
                    if time.monotonic() - started > self.timeout:
                        raise TimeoutError('response wall-time budget exceeded')
                    block = response.read(min(65536, cap + 1 - size))
                    if not block:
                        break
                    stream.write(block)
                    size += len(block)
                    require(size <= cap, "response body cap exceeded")
                content_length = response.headers.get('Content-Length')
                if content_length is not None and size < int(content_length):
                    raise http.client.IncompleteRead(b'', int(content_length)-size)
            os.replace(partial, body)
            r.update(complete=True, bytes=size, sha256=digest(body))
            atomic_json(receipt, r)
            return body, r
        except Exception as exc:
            if isinstance(exc, http.client.IncompleteRead) and exc.partial:
                fragment = exc.partial[:max(0, cap+1-size)]
                with partial.open('ab') as stream:
                    stream.write(fragment)
                size += len(fragment)
            r.update(error=type(exc).__name__ + ": " + str(exc), retained_partial_bytes=size,
                     elapsed_seconds=time.monotonic()-started, partial_file=partial.name)
            atomic_json(body.with_name(body.name + ".failure-" + uuid.uuid4().hex + ".json"), r)
            raise
        finally:
            with self.lock:
                self.bytes += size
                self.reserved -= cap
            r["elapsed_seconds"] = time.monotonic() - started
            if r["complete"]:
                atomic_json(receipt, r)


def compare_database(database, month, u, v, basis):
    """Check original per-cell half-month counts/means/quantiles, not pooled bands."""
    import duckdb
    times = [t for year in YEARS for t in month_times(year, month)]
    errors = {key: 0.0 for key in ("u_mean", "v_mean", "speed_mean", "speed_p10", "speed_p50", "speed_p90")}
    with duckdb.connect(str(database), read_only=True, config={"enable_external_access": False, "threads": 1}) as con:
        for half in (1, 2):
            mask = np.array([(t.day <= 15) == (half == 1) for t in times])
            for j, level in enumerate(basis["levels"]):
                a, b = np.asarray(u[mask, j, :]), np.asarray(v[mask, j, :])
                speed = np.hypot(a, b)
                calculated = [a.mean(axis=0, dtype=np.float64), b.mean(axis=0, dtype=np.float64), speed.mean(axis=0, dtype=np.float64), *np.quantile(speed, [.1, .5, .9], axis=0, method="linear")]
                rows = con.execute("SELECT cell_id,n,u_mean,v_mean,speed_mean,speed_p10,speed_p50,speed_p90 FROM fact_wind WHERE month=? AND bin=? AND level_id=? ORDER BY cell_id", [month, half, level["level_id"]]).fetchall()
                require(len(rows) == len(basis["grid"]) and [r[0] for r in rows] == [r["cell_id"] for r in basis["grid"]] and all(r[1] == int(mask.sum()) for r in rows), "raw and DB populations differ")
                expected = np.array([r[2:] for r in rows], dtype=np.float64).T
                for k, (name, actual) in enumerate(zip(errors, calculated)):
                    errors[name] = max(errors[name], float(np.max(np.abs(actual - expected[k]))))
                    require(np.allclose(actual, expected[k], rtol=2e-6, atol=5e-5), f"raw/DB statistic mismatch: {month}/{half}/{name}")
    require(digest(database) == basis["dataset_sha256"], "database changed during acquisition")
    return {"absolute_max_errors": errors, "rtol": 2e-6, "atol": 5e-5, "quantile_method": "linear", "comparison": "all cells/levels; each original half-month; not new pooled distribution"}


def publish_complete_months(output, cache, basis, indices, database, fill_values, years=None, metadata_receipts=None):
    years = YEARS if years is None else sorted(years)
    months, requests, checks = [], {}, {}
    for month in range(1, 13):
        available = []
        for year in years:
            cat = cache.cached(catalog_url(year, month))
            if cat is None:
                break
            entries = catalog_entries(cat[0].read_bytes(), year, month)
            for component in VARIABLES:
                for entry in entries[component]:
                    saved = cache.cached(data_url(entry, indices))
                    if saved is not None:
                        available.append((entry, saved))
        if len(available) != len(years) * 12:
            continue
        directory = output / f"month-{month:02d}"
        directory.mkdir(exist_ok=True)
        times = [t for year in years for t in month_times(year, month)]
        positions = {t: i for i, t in enumerate(times)}
        arrays, temporary = {}, {}
        for component in VARIABLES:
            path = directory / (component + ".npy.tmp-" + uuid.uuid4().hex)
            temporary[component] = path
            arrays[component] = np.lib.format.open_memmap(path, mode="w+", dtype=np.float32, shape=(len(times), len(basis["levels"]), len(basis["grid"])))
        seen = {c: set() for c in VARIABLES}
        for entry, (path, receipt) in available:
            values, returned = reorder_subset(path.read_bytes(), entry, basis, fill_values[entry["component"]])
            component = entry["component"]
            require(not seen[component].intersection(returned), "duplicate raw UTC")
            seen[component].update(returned)
            arrays[component][[positions[t] for t in returned]] = values
            requests[receipt["url"]] = receipt
        require(all(set(times) == seen[c] for c in VARIABLES), "incomplete month is not publishable")
        checks[str(month)] = (compare_database(database, month, arrays["u"], arrays["v"], basis) if years == YEARS and database is not None else
            {"comparison": "not comparable to the 2016-2025 climatology: independently labelled selected-year source", "validation": "complete 4-UTC calendar; all DB grid/level axes; original Float32 values; paired u/v; no missing values"})
        item = {"month": month, "times_utc": [utc_string(t) for t in times]}
        for component in VARIABLES:
            arrays[component].flush()
            del arrays[component]
            source = temporary[component]
            target = regular_path(output, f"month-{month:02d}/{component}.npy")
            if target.exists():
                require(digest(target) == digest(source), "existing published month differs; preserved")
                source.unlink()
            else:
                os.replace(source, target)
            item[component] = {"file": target.relative_to(output).as_posix(), "bytes": target.stat().st_size, "sha256": digest(target)}
        months.append(item)
    if months:
        previous = output / "manifest.json"
        if previous.exists():
            prior = json.loads(previous.read_text(encoding="utf-8"))
            require(prior.get("schema") == "balloon.wind-samples/1" and prior.get("years") == [years[0], years[-1]] and prior.get("provenance", {}).get("basis_dataset_sha256") == basis["dataset_sha256"] and prior.get("levels") == basis["levels"], "existing manifest uses a different basis or period")
            require({m["month"] for m in prior["months"]}.issubset({m["month"] for m in months}), "refuse to remove already published months")
        manifest = {"schema": "balloon.wind-samples/1", "provider": "JRA-3Q", "label": f"JRA-3Q original anl_p / {years[0]}–{years[-1]} / Hokkaido / 4 UTC analyses",
            "years": [years[0], years[-1]], "date_convention": "UTC", "hours_utc": [0, 6, 12, 18],
            "weighting": "gaussian-area-equal-times", "grid": [{**cell, "weight": weight} for cell, weight in zip(basis["grid"], basis["gaussian_weights"])],
            "levels": basis["levels"], "months": months,
            "provenance": {"product": "anl_p", "dataset_url": "https://gdex.ucar.edu/datasets/d640000/", "citation": "JMA JRA-3Q; NSF NCAR GDEX DOI 10.5065/AVTZ-1H78; Kosaka et al. (2024), DOI 10.2151/jmsj.2024-004", "license": {"spdx": "CC-BY-NC-SA-4.0", "url": "https://creativecommons.org/licenses/by-nc-sa/4.0/", "source": "NCAR dataset page observed 2026-10-02", "changes": "original u/v subset by UTC, pressure and native cells; converted to Float32 NPY; no interpolation"}, "basis_dataset_sha256": basis["dataset_sha256"], "basis_file_sha256": basis.get("basis_file_sha256"), "basis_role": "grid/level/area-weight reference; source years are independently declared", "requests": list(requests.values()), "metadata_requests": metadata_receipts or [], "declared_missing_values": fill_values, "coordinate_mapping": "NCAR Float64 axes uniquely matched after Float32 rounding to supplied DB coordinates; output reordered by DB level_id/cell_id", "validation": checks, "quantile_input": "original scalar speeds derived from paired original UTC u/v; no interpolation, fit or synthetic fill", "source_code_sha256": digest(Path(__file__))}}
        sha = atomic_json(output / "manifest.json", manifest)
        version = output / ("manifest-" + sha + ".json")
        if not version.exists():
            shutil.copyfile(output / "manifest.json", version)
    return [m["month"] for m in months]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    basis_option = parser.add_mutually_exclusive_group(required=True)
    basis_option.add_argument("--database", type=Path)
    basis_option.add_argument("--basis-json", type=Path, help='fixed native-grid basis; acquisition does not need the supplied aggregate database')
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--months", type=int, nargs="+", required=True)
    parser.add_argument("--years", type=int, nargs="+", required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--max-requests", type=int)
    parser.add_argument("--max-bytes", type=int)
    parser.add_argument("--workers", type=int, choices=[1, 2], default=1)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--attempts", type=int, choices=[1, 2, 3], default=1, help='bounded retries only for transfer interruption/timeout; HTTP errors stop')
    parser.add_argument("--seed-directory", type=Path)
    args = parser.parse_args(argv)
    require(len(set(args.months)) == len(args.months) and all(1 <= m <= 12 for m in args.months), "invalid/duplicate month")
    require(len(set(args.years)) == len(args.years) and all(y in YEARS for y in args.years), "years must be selected from fixed 2016--2025")
    require(sorted(args.years) == list(range(min(args.years), max(args.years) + 1)), "selected years must be contiguous")
    require(1 <= args.timeout <= 120, "timeout must be 1--120 seconds")
    basis = read_basis(args.database) if args.database is not None else read_basis_file(args.basis_json)
    plan = {"months": sorted(args.months), "download_years": sorted(args.years), "manifest_years": [min(args.years), max(args.years)], "schema": "balloon.wind-samples/1", "data_requests_before_reuse": len(args.months) * len(args.years) * 12, "catalog_requests_before_reuse": len(args.months) * len(args.years), "metadata_requests_before_reuse": 2, "workers": args.workers, "execute": args.execute, "dataset_sha256": basis["dataset_sha256"], "basis_file_sha256": basis.get('basis_file_sha256'), "attempts": args.attempts, "timeout_seconds": args.timeout}
    if not args.execute:
        print(json.dumps(plan, indent=2))
        return 0
    require(args.max_requests is not None and args.max_requests > 0 and args.max_bytes is not None and args.max_bytes > 0, "execution requires positive request and byte budgets")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    require(not args.output.is_symlink(), "output symlink is unsupported")
    prior_plan = output / "download-plan.json"
    if prior_plan.exists():
        prior = json.loads(prior_plan.read_text(encoding="utf-8"))
        require(prior.get("manifest_years") == plan["manifest_years"] and prior.get("dataset_sha256") == plan["dataset_sha256"], "output belongs to a different period/basis; use a separate output")
    cache = HttpCache(output, args.max_requests, args.max_bytes, args.timeout, args.seed_directory, args.attempts)
    atomic_json(output / "download-plan.json", plan)
    jobs, indices, error, fill_values, metadata_receipts = [], None, None, {}, []
    try:
        for year in sorted(args.years):
            for month in sorted(args.months):
                cat = cache.get(catalog_url(year, month), META_CAP)
                metadata_receipts.append(cat[1])
                entries = catalog_entries(cat[0].read_bytes(), year, month)
                for component in VARIABLES:
                    if component not in fill_values:
                        first = entries[component][0]
                        meta = cache.get(ORIGIN + "/thredds/ncss/grid/" + first["path"] + "/dataset.xml", META_CAP)
                        _, current, fills = metadata_axes(meta[0].read_bytes(), component, basis)
                        metadata_receipts.append(meta[1])
                        require(indices is None or current == indices, "u/v metadata axes differ")
                        indices = current
                        fill_values[component] = fills
                    jobs.extend(entries[component])
        def acquire(entry):
            try:
                saved = cache.get(data_url(entry, indices), DATA_CAP)
                reorder_subset(saved[0].read_bytes(), entry, basis, fill_values[entry["component"]])
                return entry
            except Exception:
                with cache.lock:
                    cache.stopped = True
                raise
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(acquire, entry) for entry in jobs]
            completed = 0
            for future in as_completed(futures):
                future.result()
                completed += 1
                atomic_json(output / "progress.json", {"completed_data_jobs": completed, "planned_data_jobs": len(jobs), "new_http_requests": cache.requests, "new_response_bytes": cache.bytes, "state": "acquiring"})
    except Exception as exc:
        error = type(exc).__name__ + ": " + str(exc)
    published = []
    if indices is not None and set(fill_values) == set(VARIABLES):
        try:
            published = publish_complete_months(output, cache, basis, indices, args.database, fill_values, sorted(args.years), metadata_receipts)
        except Exception as exc:
            error = (error + "; " if error else "") + type(exc).__name__ + ": " + str(exc)
    result = {"new_http_requests": cache.requests, "new_response_bytes": cache.bytes, "manifest_years": plan["manifest_years"], "published_complete_months": published, "error": error, "state": "stopped" if error else "finished", "scope": "only months complete for all explicitly selected years are registered; a successful download step does not imply all twelve months complete"}
    atomic_json(output / "progress.json", result)
    print(json.dumps(result, indent=2))
    return 1 if error else 0


if __name__ == "__main__":
    raise SystemExit(main())
