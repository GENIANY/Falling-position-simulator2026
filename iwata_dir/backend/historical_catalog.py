"""Explicit local original-date assets, configured at service startup only."""
import copy
import zlib
from pathlib import Path

from balloon_sim.environment.jra3q import SCHEMA, SURFACE_SCHEMA
from balloon_sim.environment.storage import load_weather, read_json
from balloon_sim.flight.config import validate_config
from .storage import file_hash


def load_historical_sources(catalog_path):
    """Return independently verified entries and errors without hiding old runs.

    No URL/path is accepted from HTTP. An operator prepares a small catalog with
    an expected SHA for every bundle. A malformed entry does not register a
    partial field or disable unrelated saved results.
    """
    if not catalog_path:
        return {}, []
    catalog = Path(catalog_path).expanduser().resolve()
    sources, errors = {}, []
    try:
        if catalog.stat().st_size > 2 * 1024 * 1024:
            raise ValueError("Historical catalog exceeds 2 MiB.")
        document = read_json(catalog)
        if not isinstance(document, dict) or document.get("schema") != "balloon.historical-catalog/1" or not isinstance(document.get("sources"), list):
            raise ValueError("Expected balloon.historical-catalog/1 with sources.")
        entries = document["sources"]
        if len(entries) > 256:
            raise ValueError("Historical catalog exceeds 256 assets.")
        ids = [e["id"] for e in entries]
        if len(set(ids)) != len(ids) or any(not isinstance(x, str) or not x.startswith("historical-") or len(x) > 128 for x in ids):
            raise ValueError("Use unique historical- prefixed source IDs, at most 128 characters.")
    except (OSError, ValueError, KeyError, TypeError, EOFError, zlib.error) as exc:
        return {}, [{"id": "historical-catalog", "code": "SOURCE_UNAVAILABLE", "message": str(exc)}]
    for entry in entries:
        identity = entry["id"]
        try:
            path = (catalog.parent / entry["path"]).resolve()
            expected = entry["sha256"]
            if file_hash(path) != expected:
                raise ValueError("Historical bundle differs from the catalog's expected SHA256.")
            bundle = read_json(path)
            if not isinstance(bundle, dict) or bundle.get("schema") not in {SCHEMA, SURFACE_SCHEMA}:
                raise ValueError("Only original-UTC JRA model fields are supported in this catalog.")
            weather = load_weather(path)
            axes = bundle["axes"]
            default = validate_config(entry["default_config"]) if entry.get("default_config") is not None else None
            snapshot = {"id": identity, "label": str(entry["label"]), "sha256": expected,
                        "bytes": path.stat().st_size, "kind": "saved_jra3q",
                        "schema": bundle["schema"], "product": weather.metadata.get("product"),
                        "time_kind": "analysis_valid_utc", "run_utc": None,
                        "valid_times_utc": list(axes["time_utc"]),
                        "bounds": {"lat": [min(axes["latitude_deg"]), max(axes["latitude_deg"])],
                                   "lon": [min(axes["longitude_deg"]), max(axes["longitude_deg"])],
                                   "model_level": [min(axes["model_level"]), max(axes["model_level"])]},
                        "metadata": copy.deepcopy(weather.metadata)}
            if file_hash(path) != expected:
                raise ValueError("Historical bundle changed during registration.")
            sources[identity] = {"path": path, "snapshot": snapshot, "default_config": default}
        except (OSError, ValueError, KeyError, TypeError, EOFError, zlib.error) as exc:
            errors.append({"id": identity, "label": entry.get("label", identity),
                           "code": "SOURCE_UNAVAILABLE", "message": str(exc)})
    return sources, errors
