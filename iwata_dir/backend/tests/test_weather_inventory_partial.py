"""A broken provider branch does not erase separately observed forecast runs."""
import threading

import pytest

from backend.weather.catalog import BASE, observe_inventory
from balloon_sim.environment.fields import WeatherError


class Gateway:
    def __init__(self, failures=None):
        self.failures = failures or {}
        self.calls = []

    def fetch(self, url, maximum, cancel=None):
        self.calls.append(url)
        if url in self.failures:
            raise self.failures[url]
        if url == BASE:
            names = ["gfs.20260922/", "gfs.20260921/"]
        elif url.endswith("gfs.20260922/") or url.endswith("gfs.20260921/"):
            names = ["18/", "12/"]
        else:
            cycle = url.split("/")[-3]
            names = [f"gfs.t{cycle}z.pgrb2.0p25.f006", f"gfs.t{cycle}z.pgrb2.0p25.f007"]
        return "".join(f'<a href="{name}">{name}</a>' for name in names).encode(), {"url": url}


def test_run_failure_keeps_other_observed_run_without_substitution():
    failed_url = BASE + "gfs.20260922/18/atmos/"
    result = observe_inventory({"run_utc": None, "run_limit": 2},
        Gateway({failed_url: WeatherError("HTTP_STATUS", "503") }))
    assert result["observation_status"] == "partial"
    assert [run["run_utc"] for run in result["runs"]] == ["2026-09-22T12:00:00+00:00"]
    assert result["observation_errors"] == [{"stage": "run", "url": failed_url,
        "run_utc": "2026-09-22T18:00:00+00:00", "code": "HTTP_STATUS", "message": "HTTP_STATUS: 503"}]
    assert result["selection"] == "latest_observed"


def test_failed_day_keeps_previous_day_and_failure_identity():
    failed_url = BASE + "gfs.20260922/"
    gateway = Gateway({failed_url: TimeoutError("day timeout")})
    result = observe_inventory({"run_utc": None, "run_limit": 2}, gateway)
    assert len(result["runs"]) == 2
    assert all(run["run_utc"].startswith("2026-09-21") for run in result["runs"])
    assert result["observation_errors"][0]["day"] == "20260922"
    assert result["observation_errors"][0]["stage"] == "day"
    assert result["observation_status"] == "partial"
    assert len(gateway.calls) == 5


def test_fixed_run_failure_is_saved_as_unavailable_not_empty_success():
    run = "2026-09-22T18:00:00+00:00"
    url = BASE + "gfs.20260922/18/atmos/"
    result = observe_inventory({"run_utc": run, "run_limit": 2},
        Gateway({url: WeatherError("HTTP_STATUS", "404") }))
    assert result["selection"] == "fixed_run" and result["runs"] == []
    assert result["observation_status"] == "unavailable"
    assert result["observation_errors"][0]["run_utc"] == run


@pytest.mark.parametrize("stage", ["root", "day", "run"])
def test_cancellation_never_becomes_partial_success(stage):
    urls = {"root": BASE, "day": BASE + "gfs.20260922/",
            "run": BASE + "gfs.20260922/18/atmos/"}
    with pytest.raises(WeatherError) as cancelled:
        observe_inventory({"run_utc": None, "run_limit": 2},
            Gateway({urls[stage]: WeatherError("ACQUISITION_CANCELLED", "cancel") }))
    assert cancelled.value.code == "ACQUISITION_CANCELLED"


def test_cancel_set_during_failed_fetch_stops_other_branches():
    cancel = threading.Event()
    gateway = Gateway()
    original = gateway.fetch
    def fetch(url, *args, **kwargs):
        if url.endswith("gfs.20260922/"):
            cancel.set()
            raise WeatherError("HTTP_STATUS", "503 after cancel")
        return original(url, *args, **kwargs)
    gateway.fetch = fetch
    with pytest.raises(WeatherError) as cancelled:
        observe_inventory({"run_utc": None, "run_limit": 2}, gateway, cancel)
    assert cancelled.value.code == "ACQUISITION_CANCELLED"
    assert len(gateway.calls) == 1


def test_root_transport_state_and_local_recording_failure_still_abort():
    with pytest.raises(WeatherError):
        observe_inventory({"run_utc": None, "run_limit": 2},
                          Gateway({BASE: WeatherError("HTTP_STATUS", "503") }))
    with pytest.raises(WeatherError) as invalid:
        observe_inventory({"run_utc": None, "run_limit": 2},
            Gateway({BASE + "gfs.20260922/": WeatherError("TRANSPORT_STATE_INVALID", "broken") }))
    assert invalid.value.code == "TRANSPORT_STATE_INVALID"
    def recorder(*_):
        raise OSError("disk full")
    with pytest.raises(OSError, match="disk full"):
        observe_inventory({"run_utc": None, "run_limit": 2}, Gateway(), recorder=recorder)
