"""Fixed local climate analyses, independent of HTTP and the flight-work lock."""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from threading import RLock
from uuid import UUID, uuid4

from .contracts import ClimateError, ClimateQuery
from .source import ClimateSource
from .archive import WindArchiveSource

ARTIFACT_SCHEMA = "balloon.climate.analysis-artifact/1"
STORAGE_SCHEMA = "balloon.climate.storage/1"
_SHA = re.compile(r"[0-9a-f]{64}")


class ClimateServiceError(ClimateError):
    def __init__(self, code, message, status_code):
        super().__init__(code, message)
        self.status_code = status_code


def _canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _corrupt(message="Saved climate analysis failed its integrity check."):
    return ClimateServiceError("CLIMATE_CORRUPT", message, 409)


def _valid_id(value):
    try:
        return isinstance(value, str) and str(UUID(value)) == value
    except (ValueError, TypeError, AttributeError):
        return False


def _promote(error):
    if isinstance(error, ClimateServiceError):
        return error
    code = error.code
    status = 409 if code in {"CLIMATE_SOURCE_CHANGED", "CLIMATE_ADAPTER_CHANGED"} else (
        503 if code in {"CLIMATE_DATABASE", "CLIMATE_DEPENDENCY"} else 422)
    return ClimateServiceError(code, str(error), status)


class ClimateService:
    """Source activation is startup-only. Saved reads do not need that source.

    data_root contains one service-owned SQLite file. source_path is a trusted
    startup option, never a browser/query field. New analyses are serialized by
    this service's own lock. No database transaction spans DuckDB aggregation;
    saved GETs use their own read connection and do not acquire that work lock.
    """

    def __init__(self, data_root, source_path=None, expected_sha256=None, source_guard=None, samples_path=None, archive_paths=None):
        self.data_root = Path(data_root).absolute()
        self.database_path = self.data_root / "climate.sqlite3"
        self._work_lock = RLock()
        self._source_guard = source_guard or (lambda: None)
        self._source = None
        self._archives = {}
        self._archive_errors = []
        self._source_error = {"code": "CLIMATE_UNCONFIGURED", "message": "実風統計DBが起動設定に指定されていません。保存済み分析は再閲覧できます。"}
        try:
            self.data_root.mkdir(parents=True, exist_ok=True)
            with self._connection(create=True, write=True) as con:
                # WAL permits saved readers during the short write transaction.
                con.execute("PRAGMA journal_mode=WAL")
                con.executescript("""
                    CREATE TABLE IF NOT EXISTS climate_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
                    CREATE TABLE IF NOT EXISTS climate_analyses(
                        analysis_id TEXT PRIMARY KEY,query_hash TEXT NOT NULL UNIQUE,
                        result_hash TEXT NOT NULL,artifact_json TEXT NOT NULL,artifact_sha256 TEXT NOT NULL,artifact_bytes INTEGER NOT NULL);
                    CREATE TABLE IF NOT EXISTS climate_requests(
                        client_request_id TEXT PRIMARY KEY,query_json TEXT NOT NULL,
                        analysis_id TEXT NOT NULL REFERENCES climate_analyses(analysis_id),binding_sha256 TEXT NOT NULL);
                    CREATE TABLE IF NOT EXISTS climate_query_cache(
                        cache_key TEXT PRIMARY KEY,identity_json TEXT NOT NULL,
                        analysis_id TEXT NOT NULL REFERENCES climate_analyses(analysis_id),binding_sha256 TEXT NOT NULL);
                """)
                con.execute("INSERT OR IGNORE INTO climate_meta(key,value) VALUES('schema',?)", (STORAGE_SCHEMA,))
                if con.execute("SELECT value FROM climate_meta WHERE key='schema'").fetchone()[0] != STORAGE_SCHEMA:
                    raise _corrupt("Unsupported climate storage schema.")
        except OSError as exc:
            raise ClimateServiceError("CLIMATE_STORAGE", "Cannot open the local climate analysis store.", 503) from exc
        if source_path is not None:
            try:
                self._source_guard()
                self._source = ClimateSource(source_path, expected_sha256, samples_path=samples_path)
                self._source_guard()
                self._source_error = None
            except ClimateError as exc:
                self._source = None
                self._source_error = {"code": exc.code, "message": str(exc)}
        if archive_paths is not None:
            if not isinstance(archive_paths, (tuple, list)) or len(archive_paths)>8 or any(not isinstance(p,(str,Path)) for p in archive_paths):
                raise ClimateError('CLIMATE_INPUT','起動設定の原標本pathは8個以下のリストで指定してください。')
            for path in archive_paths:
                try:
                    self._source_guard()
                    archive = WindArchiveSource(path)
                    self._archives[archive.source_id] = archive
                    self._source_guard()
                except ClimateError as exc:
                    self._archive_errors.append({'code':exc.code,'message':str(exc)})

    @contextmanager
    def _connection(self, *, create=False, write=False):
        connection = None
        try:
            location = str(self.database_path) if create else self.database_path.as_uri() + ("?mode=rw" if write else "?mode=ro")
            connection = sqlite3.connect(location, uri=not create, timeout=10., isolation_level=None)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys=ON")
            connection.execute("PRAGMA synchronous=FULL" if write else "PRAGMA query_only=ON")
            yield connection
        except sqlite3.Error as exc:
            raise ClimateServiceError("CLIMATE_STORAGE", "Local climate storage is unavailable or damaged.", 503) from exc
        finally:
            if connection is not None:
                connection.close()

    def sources(self):
        sources, errors = [], deepcopy(self._archive_errors)
        for source in [*self._archives.values(), *([self._source] if self._source is not None else [])]:
            try:
                sources.append(source.descriptor())
            except ClimateError as exc:
                errors.append({'code':exc.code,'message':str(exc)})
        if self._source_error is not None and (not sources or self._source_error['code'] != 'CLIMATE_UNCONFIGURED'):
            errors.append(deepcopy(self._source_error))
        return {'sources':sources,'errors':errors}

    def _selected_source(self, source_id):
        if source_id in self._archives:
            return self._archives[source_id]
        if self._source is not None and self._source.source_id == source_id:
            return self._source
        if self._source is not None or self._archives:
            raise ClimateServiceError('CLIMATE_SOURCE_CHANGED','指定した資料は現在の資料一覧にありません。別資料へは切り替えません。',409)
        raise ClimateServiceError('CLIMATE_UNAVAILABLE','指定した原標本資料を利用できません。',503)

    def verify_source(self, source_id=None):
        """Explicit full SHA check. Ordinary queries use the adapter's stat guard."""
        source = self._selected_source(source_id) if source_id is not None else self._source
        if source is None:
            raise ClimateServiceError("CLIMATE_UNAVAILABLE", "実風統計DBが利用できません。", 503)
        try:
            self._source_guard()
            result = source.verify_full()
            self._source_guard()
            return result
        except ClimateError as exc:
            raise _promote(exc) from exc

    @staticmethod
    def _body(body):
        if not isinstance(body, dict) or set(body) != {"client_request_id", "query"}:
            raise ClimateServiceError("CLIMATE_INPUT", "client_request_id and query are required; no startup path or SQL is accepted.", 422)
        request_id = body["client_request_id"]
        if not isinstance(request_id, str) or not 1 <= len(request_id) <= 128 or any(ord(c) < 32 for c in request_id):
            raise ClimateServiceError("CLIMATE_INPUT", "client_request_id must be a nonempty identifier of at most 128 characters.", 422)
        try:
            query = ClimateQuery.from_mapping(body["query"])
            return request_id, query, _canonical(query.as_dict())
        except ClimateError as exc:
            raise _promote(exc) from exc

    @staticmethod
    def _read_artifact(con, analysis_id):
        row = con.execute("SELECT * FROM climate_analyses WHERE analysis_id=?", (analysis_id,)).fetchone()
        if row is None:
            raise ClimateServiceError("CLIMATE_NOT_FOUND", "指定した保存分析がありません。", 404)
        try:
            if _digest(row["artifact_json"]) != row["artifact_sha256"] or len(row["artifact_json"].encode("utf-8")) != row["artifact_bytes"]:
                raise _corrupt()
            artifact = json.loads(row["artifact_json"])
            if _canonical(artifact) != row["artifact_json"] or artifact["schema"] != ARTIFACT_SCHEMA or artifact["analysis_id"] != analysis_id:
                raise _corrupt()
            if not _valid_id(artifact["analysis_id"]) or not isinstance(artifact["created_at"], str):
                raise _corrupt()
            summary = artifact["summary"]
            if summary["schema"] != "climate-summary/1" or artifact["query"] != summary["query"]:
                raise _corrupt()
            query_hash, result_hash = artifact["query_hash"], artifact["result_hash"]
            if not _SHA.fullmatch(query_hash) or not _SHA.fullmatch(result_hash):
                raise _corrupt()
            if query_hash != row["query_hash"] or result_hash != row["result_hash"]:
                raise _corrupt()
            if query_hash != summary["provenance"]["query_hash"] or result_hash != summary["provenance"]["result_hash"]:
                raise _corrupt()
            unsigned = deepcopy(summary)
            del unsigned["provenance"]["result_hash"]
            if _digest(_canonical(unsigned)) != result_hash:
                raise _corrupt()
            return artifact
        except (KeyError, TypeError, ValueError) as exc:
            if isinstance(exc, ClimateServiceError):
                raise
            raise _corrupt() from exc

    def get_analysis(self, analysis_id):
        if not _valid_id(analysis_id):
            raise ClimateServiceError("CLIMATE_NOT_FOUND", "指定した保存分析がありません。", 404)
        with self._connection() as con:
            return self._read_artifact(con, analysis_id)

    def _existing_request(self, con, request_id, query_json):
        row = con.execute("SELECT * FROM climate_requests WHERE client_request_id=?", (request_id,)).fetchone()
        if row is None:
            return None
        if _digest(_canonical([request_id, row["query_json"], row["analysis_id"]])) != row["binding_sha256"]:
            raise _corrupt("Saved request binding failed its integrity check.")
        if row["query_json"] != query_json:
            raise ClimateServiceError("CLIMATE_IDEMPOTENCY", "同じ要求IDに別の集計条件を指定できません。新しい条件は新しい要求として送ってください。", 409)
        return self._read_artifact(con, row["analysis_id"])

    @staticmethod
    def _identity(descriptor, query):
        normalized = query.as_dict()
        normalized["bounds"] = normalized["bounds"] or descriptor["bounds"]
        return {"query": normalized, "source_id": descriptor["source_id"],
                "dataset_sha256": descriptor["dataset_sha256"],
                "adapter_version": descriptor["adapter_version"], "statistics_version": descriptor["statistics_version"],
                "source_code_sha256": descriptor["source_code"]["sha256"], "duckdb_version": descriptor["duckdb_version"],
                **({"numerical_dependencies": descriptor["numerical_dependencies"]} if "numerical_dependencies" in descriptor else {})}

    @staticmethod
    def _bind_request(con, request_id, query_json, analysis_id):
        binding = _digest(_canonical([request_id, query_json, analysis_id]))
        con.execute("INSERT INTO climate_requests VALUES(?,?,?,?)", (request_id, query_json, analysis_id, binding))

    def _cached(self, con, cache_key, identity_json):
        row = con.execute("SELECT * FROM climate_query_cache WHERE cache_key=?", (cache_key,)).fetchone()
        if row is None:
            return None
        if row["identity_json"] != identity_json or _digest(_canonical([cache_key, row["identity_json"], row["analysis_id"]])) != row["binding_sha256"]:
            raise _corrupt("Saved query binding failed its integrity check.")
        artifact = self._read_artifact(con, row["analysis_id"])
        identity = self._identity(artifact["summary"]["source"], ClimateQuery.from_mapping(artifact["query"]))
        if _canonical(identity) != identity_json or _digest(identity_json) != cache_key:
            raise _corrupt("Saved query points to a different result identity.")
        return artifact

    def create_analysis(self, body):
        request_id, query, query_json = self._body(body)
        # Solve an already accepted retry before touching the current source.
        with self._connection() as con:
            existing = self._existing_request(con, request_id, query_json)
            if existing is not None:
                return existing
        with self._work_lock:
            with self._connection() as con:
                existing = self._existing_request(con, request_id, query_json)
                if existing is not None:
                    return existing
            if self._source is None and not self._archives:
                raise ClimateServiceError("CLIMATE_UNAVAILABLE", "実風統計DBが利用できません。保存済み分析は参照IDから再閲覧できます。", 503)
            try:
                self._source_guard()
                source = self._selected_source(query.source_id)
                descriptor = source.descriptor()
                if descriptor["source_id"] != query.source_id:
                    raise ClimateServiceError("CLIMATE_SOURCE_CHANGED", "指定sourceと現在の実DBが一致しません。", 409)
                identity_json = _canonical(self._identity(descriptor, query))
                cache_key = _digest(identity_json)
                with self._connection() as con:
                    artifact = self._cached(con, cache_key, identity_json)
                # Query outside SQLite and outside ApplicationService's common lock.
                summary = None if artifact is not None else source.query(query)
                source.descriptor()
                self._source_guard()
            except ClimateError as exc:
                raise _promote(exc) from exc
            with self._connection(write=True) as con:
                con.execute("BEGIN IMMEDIATE")
                try:
                    # Another service/process may have accepted this request meanwhile.
                    existing = self._existing_request(con, request_id, query_json)
                    if existing is not None:
                        con.execute("COMMIT")
                        return existing
                    try:
                        source.descriptor()
                    except ClimateError as exc:
                        raise _promote(exc) from exc
                    self._source_guard()
                    if artifact is None:
                        known = con.execute("SELECT analysis_id FROM climate_analyses WHERE query_hash=?", (summary["provenance"]["query_hash"],)).fetchone()
                        if known:
                            artifact = self._read_artifact(con, known["analysis_id"])
                            if artifact["result_hash"] != summary["provenance"]["result_hash"]:
                                raise ClimateServiceError("CLIMATE_RESULT_CONFLICT", "同じsource/query版から異なる集約結果が得られたため上書きしません。", 409)
                        else:
                            artifact = {"schema": ARTIFACT_SCHEMA, "analysis_id": str(uuid4()), "query": summary["query"],
                                "query_hash": summary["provenance"]["query_hash"], "result_hash": summary["provenance"]["result_hash"],
                                "created_at": datetime.now(timezone.utc).isoformat(), "summary": summary}
                            payload = _canonical(artifact)
                            con.execute("INSERT INTO climate_analyses VALUES(?,?,?,?,?,?)", (artifact["analysis_id"],artifact["query_hash"],artifact["result_hash"],payload,_digest(payload),len(payload.encode("utf-8"))))
                    self._bind_request(con, request_id, query_json, artifact["analysis_id"])
                    existing_cache = self._cached(con, cache_key, identity_json)
                    if existing_cache is None:
                        binding = _digest(_canonical([cache_key, identity_json, artifact["analysis_id"]]))
                        con.execute("INSERT INTO climate_query_cache VALUES(?,?,?,?)", (cache_key,identity_json,artifact["analysis_id"],binding))
                    elif existing_cache["analysis_id"] != artifact["analysis_id"]:
                        raise _corrupt("Query cache conflicts with its immutable artifact.")
                    con.execute("COMMIT")
                except Exception:
                    con.execute("ROLLBACK")
                    raise
            return deepcopy(artifact)
