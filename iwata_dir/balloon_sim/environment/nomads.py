"""Bounded NOMADS transport, shared by CLI acquisition and the local service.

One OS-user lock serializes requests across processes. The next request starts
at least ten seconds after the previous response finishes (including failures).
No automatic retry or redirect is performed. Scientific readers never use this
module. Clock/opener injection is only for offline transport tests.
"""
from contextlib import contextmanager
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import hashlib
import io
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

from .fields import WeatherError
from .. import __version__


def check_cancel(cancel):
    if cancel is not None and cancel.is_set():
        raise WeatherError("ACQUISITION_CANCELLED", "Acquisition cancelled; complete raw files are retained.")


def _check_url(url):
    part = urllib.parse.urlsplit(url)
    if (part.scheme != "https" or part.netloc != "nomads.ncep.noaa.gov" or part.fragment
            or not (part.path.startswith("/pub/data/nccf/com/gfs/prod/")
                    or part.path in ("/cgi-bin/filter_gfs_0p25.pl", "/gribfilter.php"))):
        raise WeatherError("UNSUPPORTED_SOURCE_URL", "Only fixed NOMADS GFS endpoints are allowed.")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class NomadsGateway:
    def __init__(self, state_dir=None, *, opener=None, clock=None, sleep=None, monotonic=None):
        base = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / ".local" / "share")))
        self.state_dir = Path(state_dir or base / "BalloonSimulator" / "network" / "nomads")
        self._open = opener or urllib.request.build_opener(_NoRedirect()).open
        self._clock = clock or time.time
        self._sleep = sleep or time.sleep
        self._monotonic = monotonic or time.monotonic

    def _wait(self, seconds, cancel):
        end = self._clock() + seconds
        while self._clock() < end:
            check_cancel(cancel)
            self._sleep(min(.1, max(0, end - self._clock())))

    @contextmanager
    def _locked(self, cancel):
        self.state_dir.mkdir(parents=True, exist_ok=True)
        with (self.state_dir / "transport.lock").open("a+b") as handle:
            if os.fstat(handle.fileno()).st_size == 0:
                handle.write(b"0")
                handle.flush()
            while True:
                check_cancel(cancel)
                handle.seek(0)
                try:
                    if os.name == "nt":
                        import msvcrt
                        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                    else:
                        import fcntl
                        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except OSError:
                    self._wait(.1, cancel)
            try:
                yield
            finally:
                handle.seek(0)
                if os.name == "nt":
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def _reserve(self, value, *, in_flight=False):
        target = self.state_dir / "schedule.json"
        temporary = self.state_dir / ("schedule-" + uuid.uuid4().hex + ".tmp")
        with temporary.open("x", encoding="utf-8") as output:
            json.dump({"next_allowed_at": value, "in_flight": in_flight}, output, allow_nan=False)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, target)

    def _transfer(self, url, output, max_bytes, cancel):
        _check_url(url)
        if type(max_bytes) is not int or not 0 < max_bytes <= 50_000_000:
            raise WeatherError("DOWNLOAD_LIMIT", "Positive remaining byte budget, at most 50MB, is required.")
        with self._locked(cancel):
            state = self.state_dir / "schedule.json"
            if state.exists():
                try:
                    saved = json.loads(state.read_text(encoding="utf-8"))
                    deadline = float(saved["next_allowed_at"])
                    if not 0 <= deadline < float("inf"):
                        raise ValueError("invalid deadline")
                    if saved.get("in_flight"):
                        # Owning the OS lock proves the previous owner has stopped.
                        # Wait again even if its initial reservation is long expired.
                        deadline = max(deadline, self._clock() + 10)
                except (ValueError, KeyError, TypeError) as exc:
                    raise WeatherError("TRANSPORT_STATE_INVALID", "Inspect the NOMADS schedule before retrying.") from exc
                self._wait(max(0, deadline - self._clock()), cancel)
            check_cancel(cancel)
            # A process killed during HTTP still leaves a conservative reservation.
            self._reserve(self._clock() + 100, in_flight=True)
            retry_at = 0
            start = datetime.now(timezone.utc).isoformat()
            count = 0
            digest = hashlib.sha256()
            deadline = self._monotonic() + 90
            def check_deadline():
                if self._monotonic() >= deadline:
                    raise WeatherError("DOWNLOAD_TIMEOUT", "NOMADS transfer exceeded the elapsed-time budget.")
            try:
                req = urllib.request.Request(url, headers={"User-Agent": f"space-balloon-simulator-jp/{__version__}"})
                with self._open(req, timeout=30) as response:
                    check_deadline()
                    if response.status != 200:
                        raise WeatherError("HTTP_STATUS", response.status)
                    headers = {k: response.headers.get(k) for k in ("Content-Type", "Content-Length", "Last-Modified", "ETag")}
                    length = headers["Content-Length"]
                    if length is not None and int(length) > max_bytes:
                        raise WeatherError("DOWNLOAD_LIMIT", "Content-Length exceeds remaining budget.")
                    while True:
                        check_cancel(cancel)
                        check_deadline()
                        # read1 returns after one underlying read instead of waiting
                        # for an entire 64KiB block from a slowly streaming server.
                        read = getattr(response, "read1", response.read)
                        chunk = read(min(65536, max_bytes - count + 1))
                        check_deadline()
                        if not chunk:
                            break
                        if count + len(chunk) > max_bytes:
                            output.write(chunk[:max_bytes - count])
                            raise WeatherError("DOWNLOAD_LIMIT", "Stream exceeds remaining budget; partial bytes retained.")
                        output.write(chunk)
                        digest.update(chunk)
                        count += len(chunk)
                    if length is not None and count != int(length):
                        raise WeatherError("INCOMPLETE_DOWNLOAD", "Response ended before its declared length.")
                return {"url": url, "bytes": count, "sha256": digest.hexdigest(), "headers": headers,
                        "started_at_utc": start, "completed_at_utc": datetime.now(timezone.utc).isoformat()}
            except urllib.error.HTTPError as exc:
                value = exc.headers.get("Retry-After")
                if value:
                    try:
                        retry_at = self._clock() + max(0, int(value))
                    except ValueError:
                        try:
                            retry_at = parsedate_to_datetime(value).timestamp()
                        except (ValueError, TypeError, OverflowError):
                            pass
                raise WeatherError("HTTP_STATUS", f"NOMADS returned {exc.code}; retry requires an explicit action.") from exc
            finally:
                self._reserve(max(self._clock() + 10, retry_at))

    def fetch(self, url, max_bytes, cancel=None):
        with io.BytesIO() as output:
            meta = self._transfer(url, output, max_bytes, cancel)
            return output.getvalue(), meta

    def download_to(self, url, path, remaining, cancel=None):
        # The caller uses a unique partial name and promotes it only after GRIB checks.
        with Path(path).open("xb") as output:
            meta = self._transfer(url, output, remaining, cancel)
            output.flush()
            os.fsync(output.fileno())
        return meta
