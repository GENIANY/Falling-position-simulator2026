"""Read-only adapter for the supplied JRA-3Q half-month summary database.

Native moments and empirical wind-rose counts are aggregated by UTC period.
An optional original-sample companion supplies monthly empirical quantiles;
neither observations nor flight fields are reconstructed from stored moments.
The limits below describe this first adapter/profile, not all future climate
sources. File stat guards detect ordinary changes; they are not protection
against an adversary restoring metadata. verify_full() explicitly rehashes.
"""
from __future__ import annotations

from collections import OrderedDict
from contextlib import contextmanager
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import re
from threading import RLock

from .contracts import ADAPTER_VERSION, STATISTICS_VERSION, Bounds, ClimateError, ClimateQuery
from .statistics import ROUNDING_RELATIVE_TOLERANCE, utc_half_months
from . import aggregation
from .periods import periods
from .extensions import inspect_extensions, wind_rose
from .samples import MonthlySamples

PROFILE = "provided-hokkaido-2016-2025-half-v1"
MAX_LEVELS = 38
MAX_CELLS = 570
CONFIG = {"enable_external_access": "false", "threads": "1", "memory_limit": "128MB",
          "autoload_known_extensions": "false", "autoinstall_known_extensions": "false",
          "allow_community_extensions": "false", "max_temp_directory_size": "0B"}
REQUIRED = {
    "meta_dataset": {"key": "text", "value": "text", "note": "text"},
    "meta_column": {"table_name": "text", "column_name": "text", "units": "text"},
    "dim_grid": {"cell_id": "integer", "lat": "number", "lon": "number", "gauss_weight": "number"},
    "dim_level": {"level_id": "integer", "level_hpa": "number", "isa_alt_m": "number",
                  "alt_geom_mean_m": "number", "alt_geom_min_m": "number", "alt_geom_max_m": "number"},
    "dim_timebin": {k: "integer" for k in ("timebin_id", "month", "bin", "start_day", "end_day_min",
                                           "end_day_max", "n_days_total", "n_analyses_expected")},
    "fact_wind": {"timebin_id": "integer", "level_id": "integer", "cell_id": "integer", "n": "integer",
                  "u_mean": "number", "v_mean": "number", "speed_mean": "number"},
}
INTEGER_TYPES = {"TINYINT", "SMALLINT", "INTEGER", "BIGINT", "UTINYINT", "USMALLINT", "UINTEGER", "UBIGINT"}
NUMBER_TYPES = INTEGER_TYPES | {"FLOAT", "DOUBLE"}
GRID_WHERE = "g.lon BETWEEN ? AND ? AND g.lat BETWEEN ? AND ?"


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _hash_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def adapter_source_snapshot():
    """Every file in this adapter, separate from the app's wider source guard."""
    root = Path(__file__).parent
    files = {p.name: _hash_file(p) for p in sorted(root.glob("*.py"))}
    return {"files": files, "sha256": hashlib.sha256(_canonical(files)).hexdigest()}


def _identity(path):
    try:
        stat = path.stat()
        if not path.is_file():
            raise OSError("Not a regular file")
        return (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns)
    except OSError as exc:
        raise ClimateError("CLIMATE_SOURCE_CHANGED", "The configured climate database is unavailable.") from exc


def _rows(connection, sql, params=()):
    cursor = connection.execute(sql, params)
    keys = [item[0] for item in cursor.description]
    return [dict(zip(keys, row)) for row in cursor.fetchall()]


class ClimateSource:
    """An identified local source. This class does not own HTTP or saved results."""

    def __init__(self, path, expected_sha256=None, samples_path=None):
        # Preserve a configured symlink path so retargeting it is detected too.
        self.path = Path(path).absolute()
        if expected_sha256 is not None and (not isinstance(expected_sha256, str) or
                                            not re.fullmatch(r"[0-9a-f]{64}", expected_sha256)):
            raise ClimateError("CLIMATE_INPUT", "expected_sha256 must be a lowercase SHA256 digest.")
        self._lock = RLock()
        self._annual_cache = OrderedDict()
        self._samples = None
        self._identity = _identity(self.path)
        try:
            self.dataset_sha256 = _hash_file(self.path)
        except OSError as exc:
            raise ClimateError("CLIMATE_SOURCE_CHANGED", "Cannot read the configured database.") from exc
        self._assert_current()
        if expected_sha256 is not None and self.dataset_sha256 != expected_sha256:
            raise ClimateError("CLIMATE_SOURCE_CHANGED", "Database content differs from its expected SHA256.")
        self.source_id = "climate-" + hashlib.sha256(_canonical([PROFILE, ADAPTER_VERSION, self.dataset_sha256])).hexdigest()
        self._adapter_snapshot = adapter_source_snapshot()
        with self._connection() as connection:
            self._inspect(connection)
        if samples_path is not None:
            self._samples = MonthlySamples(samples_path, self.dataset_sha256, self._grid, self._levels)
            self.source_id = "climate-" + hashlib.sha256(_canonical(
                [PROFILE, ADAPTER_VERSION, self.dataset_sha256, self._samples.bundle_sha256])).hexdigest()
        self._assert_current()

    def _assert_current(self):
        if _identity(self.path) != self._identity:
            raise ClimateError("CLIMATE_SOURCE_CHANGED", "The database changed after registration; register it again explicitly.")
        if hasattr(self, "_adapter_snapshot") and adapter_source_snapshot() != self._adapter_snapshot:
            raise ClimateError("CLIMATE_ADAPTER_CHANGED", "Adapter source files changed after registration; restart and identify the source again.")
        if self._samples is not None:
            self._samples.assert_current()

    @contextmanager
    def _connection(self):
        self._assert_current()
        try:
            import duckdb
        except ImportError as exc:
            raise ClimateError("CLIMATE_DEPENDENCY", "DuckDB is not installed in the backend environment.") from exc
        connection = None
        try:
            connection = duckdb.connect(str(self.path), read_only=True, config=CONFIG)
            self.duckdb_version = duckdb.__version__
            yield connection
            self._assert_current()
        except ClimateError:
            raise
        except duckdb.Error as exc:
            self._assert_current()
            raise ClimateError("CLIMATE_DATABASE", "The local climate database query failed; no partial result is published.") from exc
        finally:
            if connection is not None:
                connection.close()

    def verify_full(self):
        """Explicit full-content check; called at activation, not each slider tick."""
        with self._lock:
            self._assert_current()
            try:
                current = _hash_file(self.path)
            except OSError as exc:
                raise ClimateError("CLIMATE_SOURCE_CHANGED", "Database content is no longer readable.") from exc
            self._assert_current()
            if current != self.dataset_sha256:
                raise ClimateError("CLIMATE_SOURCE_CHANGED", "Database content no longer matches its registered SHA256.")
            return {"source_id": self.source_id, "dataset_sha256": current, "bytes": self._identity[2],
                    **({"raw_samples": self._samples.verify_full()} if self._samples is not None else {})}

    def _inspect(self, con):
        tables = dict(con.execute("SELECT table_name,table_type FROM information_schema.tables WHERE table_schema='main'").fetchall())
        for table, required in REQUIRED.items():
            if tables.get(table) != "BASE TABLE":
                raise ClimateError("CLIMATE_SCHEMA", f"Required base table {table} is absent; views are not accepted in its place.")
            columns = dict(con.execute("SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='main' AND table_name=?", [table]).fetchall())
            for column, kind in required.items():
                dtype = columns.get(column)
                allowed = {"VARCHAR"} if kind == "text" else INTEGER_TYPES if kind == "integer" else NUMBER_TYPES
                if dtype not in allowed:
                    raise ClimateError("CLIMATE_SCHEMA", f"Unsupported or missing {table}.{column} type.")
        # Reject unsupported dimensions before fetching arbitrary-size tables.
        for table, maximum in (("meta_dataset",128),("dim_timebin",24),("dim_level",MAX_LEVELS),("dim_grid",MAX_CELLS)):
            if not 1 <= con.execute(f"SELECT count(*) FROM main.{table}").fetchone()[0] <= maximum:
                raise ClimateError("CLIMATE_SUPPORT", f"{table} exceeds this adapter's dimension limit.")
        if con.execute('SELECT count(*) FROM main.meta_dataset WHERE length("key")>256 OR length(value)>16384 OR length(note)>16384').fetchone()[0]:
            raise ClimateError("CLIMATE_SCHEMA", "Dataset metadata exceeds this adapter's text limits.")
        meta = _rows(con, 'SELECT "key",value,note FROM main.meta_dataset')
        if len(meta) != len({r["key"] for r in meta}) or any(r["key"] is None for r in meta):
            raise ClimateError("CLIMATE_SCHEMA", "Dataset metadata keys must be unique and non-null.")
        self._metadata = {r["key"]: {"value": r["value"], "note": r["note"]} for r in meta}
        for key, expected in {"years": "2016-2025", "region": "hokkaido", "source_product": "anl_p", "bin_scheme": "half", "date_convention": "utc"}.items():
            if self._metadata.get(key, {}).get("value") != expected:
                raise ClimateError("CLIMATE_UNSUPPORTED", f"This adapter profile does not support metadata {key}.")
        units = con.execute("SELECT column_name,units FROM main.meta_column WHERE table_name='fact_wind' AND column_name IN ('u_mean','v_mean','speed_mean')").fetchall()
        if len(units) != 3 or dict(units) != {k: "m s-1" for k in ("u_mean", "v_mean", "speed_mean")}:
            raise ClimateError("CLIMATE_UNSUPPORTED", "Wind moments must be declared in the supported m s-1 units.")
        fields = ",".join(REQUIRED["dim_timebin"])
        self._timebins = _rows(con, f"SELECT {fields} FROM main.dim_timebin ORDER BY timebin_id")
        if self._timebins != utc_half_months():
            raise ClimateError("CLIMATE_COUNTS", "UTC half-month support differs from the 2016-2025 profile.")
        self._levels = _rows(con, "SELECT level_id,level_hpa,isa_alt_m,alt_geom_mean_m,alt_geom_min_m,alt_geom_max_m FROM main.dim_level ORDER BY level_hpa")
        if not 1 <= len(self._levels) <= MAX_LEVELS or len({r["level_id"] for r in self._levels}) != len(self._levels):
            raise ClimateError("CLIMATE_SUPPORT", "Invalid native levels or adapter level-count limit exceeded.")
        if len({r["level_hpa"] for r in self._levels}) != len(self._levels):
            raise ClimateError("CLIMATE_SUPPORT", "Native pressures must be unique.")
        for row in self._levels:
            if row["level_id"] is None or any(v is None or not math.isfinite(v) for k, v in row.items() if k != "level_id"):
                raise ClimateError("CLIMATE_SUPPORT", "Level metadata is incomplete or non-finite.")
            if not 3 <= row["level_hpa"] <= 1000 or not row["alt_geom_min_m"] <= row["alt_geom_mean_m"] <= row["alt_geom_max_m"]:
                raise ClimateError("CLIMATE_SUPPORT", "Native pressure or altitude metadata is outside this profile.")
        self._grid = _rows(con, "SELECT cell_id,lat,lon,gauss_weight FROM main.dim_grid ORDER BY cell_id")
        if not 1 <= len(self._grid) <= MAX_CELLS or len({r["cell_id"] for r in self._grid}) != len(self._grid):
            raise ClimateError("CLIMATE_SUPPORT", "Invalid grid or adapter grid-count limit exceeded.")
        if len({(r["lat"], r["lon"]) for r in self._grid}) != len(self._grid):
            raise ClimateError("CLIMATE_SUPPORT", "Native grid coordinates must be unique.")
        for row in self._grid:
            if row["cell_id"] is None or any(v is None or not math.isfinite(v) for k, v in row.items() if k != "cell_id"):
                raise ClimateError("CLIMATE_SUPPORT", "Grid metadata is incomplete or non-finite.")
            if not (-90 <= row["lat"] <= 90 and -180 <= row["lon"] <= 180 and row["gauss_weight"] > 0):
                raise ClimateError("CLIMATE_WEIGHTS", "Native grid positions/weights are invalid.")
        self._bounds = Bounds(min(r["lon"] for r in self._grid), max(r["lon"] for r in self._grid),
                              min(r["lat"] for r in self._grid), max(r["lat"] for r in self._grid))
        count = con.execute("SELECT count(*) FROM main.fact_wind").fetchone()[0]
        if count != len(self._timebins)*len(self._levels)*len(self._grid):
            raise ClimateError("CLIMATE_COUNTS", "Wind summaries must cover the full native time/level/grid product.")
        duplicate = con.execute("SELECT 1 FROM main.fact_wind GROUP BY timebin_id,level_id,cell_id HAVING count(*)<>1 LIMIT 1").fetchone()
        if duplicate:
            raise ClimateError("CLIMATE_COUNTS", "Duplicate summary keys are unsupported.")
        invalid = con.execute("""SELECT count(*) FROM main.fact_wind w
            LEFT JOIN main.dim_timebin t USING(timebin_id)
            LEFT JOIN main.dim_level l USING(level_id)
            LEFT JOIN main.dim_grid g USING(cell_id)
            WHERE t.timebin_id IS NULL OR l.level_id IS NULL OR g.cell_id IS NULL
               OR w.n IS NULL OR w.n<>t.n_analyses_expected
               OR w.u_mean IS NULL OR w.v_mean IS NULL OR w.speed_mean IS NULL
               OR NOT isfinite(w.u_mean) OR NOT isfinite(w.v_mean) OR NOT isfinite(w.speed_mean)
               OR w.speed_mean<0
               OR sqrt(pow(cast(w.u_mean AS DOUBLE),2)+pow(cast(w.v_mean AS DOUBLE),2))>
                  cast(w.speed_mean AS DOUBLE)+?*greatest(1,cast(w.speed_mean AS DOUBLE))
               OR (w.speed_mean=0 AND (w.u_mean<>0 OR w.v_mean<>0))""", [ROUNDING_RELATIVE_TOLERANCE]).fetchone()[0]
        if invalid:
            raise ClimateError("CLIMATE_COUNTS", "Missing/invalid moments or unequal UTC time support are unsupported; no cells were silently dropped.")

        self._extensions = inspect_extensions(con, self._levels, self._grid)

    def descriptor(self):
        with self._lock:
            self._assert_current()
            return deepcopy({"source_id": self.source_id, "dataset_sha256": self.dataset_sha256,
                "dataset_bytes": self._identity[2], "adapter_version": ADAPTER_VERSION,
                "statistics_version": STATISTICS_VERSION, "profile": PROFILE,
                "units": {"wind": "m/s", "pressure": "hPa", "altitude": "m", "direction": "degree"},
                "source_code": self._adapter_snapshot, "duckdb_version": self.duckdb_version,
                **({"numerical_dependencies": {"numpy": self._samples.numpy_version}} if self._samples is not None else {}),
                "capabilities": {"annual": True, "spatial": True, "years_fixed": [2016, 2025],
                    "date_convention": "UTC", "native_hours_utc": [0, 6, 12, 18], "grain": "half",
                    "raw_observations": False, "year_filter": False,
                    "display_grains": ["half", "month", "season"],
                    "hour_filter": bool(self._extensions["hour_level_ids"]),
                    "hour_level_ids": self._extensions["hour_level_ids"],
                    "wind_rose": self._extensions["rose"] is not None, "wind_rose_hours_utc": [0, 6, 12, 18],
                    "quantile_reconstruction": False, "flight_weather_field": False,
                    "empirical_monthly_profiles": self._samples is not None,
                    "adapter_resource_caps": {"levels": MAX_LEVELS, "grid_cells": MAX_CELLS},
                    "missing_policy": "reject_incomplete_or_unequal_support"},
                "wind_rose_point": self._extensions["rose"]["point"] if self._extensions["rose"] else None,
                "raw_samples": ({"schema": "balloon.climate.raw-months/1",
                    "bundle_sha256": self._samples.bundle_sha256, "complete_months": sorted(self._samples.months),
                    "years_fixed": [2016, 2025], "profile_method": "inverted_cdf"}
                    if self._samples is not None else None),
                "bounds": self._bounds.as_dict(), "native_grid_count": len(self._grid), "native_grid": self._grid,
                "grid_geometry": "native centers; drawn cell bounds are visualization only, not continuous field support",
                "levels": self._levels, "timebins": self._timebins,
                "height_definition": "ISA altitude for fixed pressure display; supplied dataset-wide geometric summaries are ancillary, not selected-region heights or terrain coverage",
                "attribution": {"status": "supplier-declared; source NetCDF and legal terms not revalidated",
                    "metadata": {k: self._metadata[k] for k in ("title", "years", "source_product", "source_netcdf",
                        "source_sha256", "license_spdx", "product_version", "built_at") if k in self._metadata}},
                "read_policy": {"read_only": True, "external_access": False, "threads": 1,
                    "buffer_manager_limit": "128MB", "process_rss_limit_guaranteed": False,
                    "change_detection": "file stat before/after read; explicit verify_full SHA256; not adversarial stat-tampering protection"}})

    def query(self, query):
        if not isinstance(query, ClimateQuery):
            query = ClimateQuery.from_mapping(query)
        with self._lock:
            self._assert_current()
            if query.source_id != self.source_id:
                raise ClimateError("CLIMATE_SOURCE_CHANGED", "The requested source ID does not identify this database.")
            if query.rose_cell_id is not None:
                raise ClimateError("CLIMATE_UNSUPPORTED", "This summary database has a fixed wind-rose point; native point selection requires original samples.")
            if query.level_id not in {r["level_id"] for r in self._levels}:
                raise ClimateError("CLIMATE_SUPPORT", "The selected pressure level is not supported.")
            bounds = query.bounds or self._bounds
            if (bounds.west < self._bounds.west or bounds.east > self._bounds.east or
                    bounds.south < self._bounds.south or bounds.north > self._bounds.north):
                raise ClimateError("CLIMATE_BOUNDS", "The region extends beyond the native grid-center bounds.")
            hours = query.hours_utc
            levels = [r for r in self._levels if not hours or r['level_id'] in self._extensions['hour_level_ids']]
            if hours and query.level_id not in self._extensions['hour_level_ids']:
                raise ClimateError("CLIMATE_HOUR_SUPPORT", "Hourly selection is supported only at this source's diurnal levels (300–1000 hPa).")
            params = [bounds.west, bounds.east, bounds.south, bounds.north]
            region_key = (*params, hours)
            groups = {}
            with self._connection() as con:
                if region_key not in self._annual_cache:
                    grid = _rows(con, f"SELECT g.cell_id,g.lat,g.lon,g.gauss_weight FROM main.dim_grid g WHERE {GRID_WHERE} ORDER BY g.cell_id", params)
                    if not grid:
                        raise ClimateError("CLIMATE_EMPTY_REGION", "No native grid centers fall inside the selected region.")
                    grouped_annual = {grain: aggregation.annual(con, params, grain, hours, len(grid), len(levels))
                                      for grain in ('half', 'month', 'season')}
                    profiles = self._samples.profiles(grid, levels, hours) if self._samples is not None else None
                    self._annual_cache[region_key] = (grid, grouped_annual, profiles)
                    if len(self._annual_cache) > 4:
                        self._annual_cache.popitem(last=False)
                self._annual_cache.move_to_end(region_key)
                grid, grouped_annual, profiles = self._annual_cache[region_key]
                for grain, annual in grouped_annual.items():
                    groups[grain] = {
                        'timebins': periods(grain, len(hours) if hours else 4), 'annual': annual,
                        'spatial_rows': aggregation.spatial(con, params, grain, hours, query.level_id, len(grid)),
                        'display_scales': aggregation.scales(annual, query.level_id),
                        'wind_rose': wind_rose(con, self._extensions, grain, hours, query.level_id, bounds)}
            half = groups.pop('half')
            resolved_query = {**query.as_dict(), "bounds": bounds.as_dict()}
            query_hash = hashlib.sha256(_canonical({"query": resolved_query, "statistics_version": STATISTICS_VERSION,
                                                    "source_code": self._adapter_snapshot["sha256"], "duckdb_version": self.duckdb_version,
                                                    **({"numpy_version": self._samples.numpy_version} if self._samples is not None else {})})).hexdigest()
            result = {"schema": "climate-summary/1", "source": self.descriptor(), "query": resolved_query,
                "population": {"years_fixed": [2016, 2025], "date_convention": "UTC", "native_hours_utc": list(hours or (0, 6, 12, 18)),
                    "timebins": half["timebins"], "selected_cell_ids": [r["cell_id"] for r in grid],
                    "native_grid_count": len(self._grid), "selected_cell_count": len(grid),
                    "spatial_weighting": "provided_gaussian_grid_weights",
                    "missing_policy": "reject_incomplete_or_unequal_support", "missing_cell_count": 0,
                    "effective_independent_time_count": None,
                    "count_definition": "time_count is per-cell UTC analyses, not cell_count*time_count independent weather samples"},
                "levels": levels, "annual": half['annual'],
                "spatial": {"level_id": query.level_id, "grid": grid, "rows": half['spatial_rows']},
                "display_scales": half['display_scales'], "wind_rose": half['wind_rose'],
                "summaries_by_grain": groups,
                **({"monthly_profiles": profiles} if profiles is not None else {}),
                "provenance": {"query_hash": query_hash, "adapter_version": ADAPTER_VERSION,
                    "statistics_version": STATISTICS_VERSION,
                    "definitions": {"period_pooling": "count-weighted moments per cell, then Gaussian spatial average; UTC calendar even when hours are labelled JST; DJF pools included December/January/February, not ten contiguous winters",
                        "distributions": "one native point's empirical wind-rose counts pooled by sum(count)/sum(n); no quantile or fitted parameter pooling",
                        "pooled_constancy": "hypot(weighted mean u,weighted mean v)/weighted mean scalar speed",
                        "constancy": "hypot(cell mean u,cell mean v)/cell mean scalar speed",
                        "from_deg": "meteorological FROM north=0 clockwise; null at zero mean vector",
                        "undefined": "constancy null when scalar mean speed is zero; no direction for zero mean vector",
                        "roundoff": "FLOAT-source vector/scalar inequality tolerated to relative 1e-6; R clipped only within this tolerance"}}}
            self._assert_current()
            result = deepcopy(result)
            result["provenance"]["result_hash"] = hashlib.sha256(_canonical(result)).hexdigest()
            return result
