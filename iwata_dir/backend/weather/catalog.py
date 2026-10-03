"""Read only the fixed NOMADS directory hierarchy; store bounded observations."""
from datetime import datetime, timezone
from html.parser import HTMLParser
import re
from urllib.parse import urljoin, urlsplit
from urllib.error import URLError

from balloon_sim.environment.fields import WeatherError, _utc
from balloon_sim.environment.gfs_contract import LEADS
from balloon_sim.environment.nomads import check_cancel

BASE = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/"
MAX_LIST_BYTES = 2_000_000


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.extend(value for key, value in attrs if key == "href" and value)


def observe_inventory(request, gateway, cancel=None, recorder=None):
    observations = []
    observation_errors = []
    def names(url, pattern, branch=None):
        check_cancel(cancel)
        try:
            data, meta = gateway.fetch(url, MAX_LIST_BYTES, cancel=cancel)
        except (WeatherError, URLError, TimeoutError, ConnectionError) as exc:
            # Only independent provider-observation failures are partial results.
            # Cancellation, local transport-state errors and recorder failures
            # must still abort instead of pretending another branch succeeded.
            check_cancel(cancel)
            recoverable = not isinstance(exc, WeatherError) or exc.code in {
                "HTTP_STATUS", "DOWNLOAD_TIMEOUT", "DOWNLOAD_LIMIT", "INCOMPLETE_DOWNLOAD"}
            if branch is None or not recoverable:
                raise
            observation_errors.append({**branch, "url": url,
                "code": getattr(exc, "code", "INVENTORY_NETWORK_ERROR"), "message": str(exc)})
            return None
        check_cancel(cancel)
        if recorder:
            meta = recorder(url, data, meta)
        observations.append(meta)
        parser = Links()
        parser.feed(data.decode("utf-8", errors="replace"))
        result = set()
        for href in parser.links:
            absolute = urljoin(url, href)
            parsed = urlsplit(absolute)
            if parsed.scheme != "https" or parsed.netloc != "nomads.ncep.noaa.gov" or parsed.query or parsed.fragment:
                continue
            if not absolute.startswith(url):
                continue
            suffix = absolute[len(url):]
            if re.fullmatch(pattern, suffix):
                result.add(suffix)
        return sorted(result, reverse=True)
    if request["run_utc"]:
        run = _utc(request["run_utc"])
        if run.hour not in (0, 6, 12, 18) or (run.minute, run.second, run.microsecond) != (0, 0, 0):
            raise WeatherError("INVALID_RUN", "GFS init must be an exact 00/06/12/18 UTC cycle.")
        runs = [run]
        selection = "fixed_run"
    else:
        runs = []
        selection = "latest_observed"
        days = names(BASE, r"gfs\.\d{8}/")[:2]
        for day in days:
            cycles = names(BASE + day, r"(?:00|06|12|18)/", {"stage": "day", "day": day[4:12]})
            if cycles is None:
                continue
            for cycle in cycles:
                run = datetime.strptime(day[4:12]+cycle[:2], "%Y%m%d%H").replace(tzinfo=timezone.utc)
                if run <= datetime.now(timezone.utc):
                    runs.append(run)
            if len(runs) >= request["run_limit"]:
                break
        runs = sorted(runs, reverse=True)[:request["run_limit"]]
    result = []
    for run in runs:
        url = BASE + f"gfs.{run:%Y%m%d}/{run:%H}/atmos/"
        files = names(url, rf"gfs\.t{run:%H}z\.pgrb2\.0p25\.f\d{{3}}",
                      {"stage": "run", "run_utc": run.isoformat()})
        if files is None:
            continue
        leads = sorted({int(name[-3:]) for name in files} & set(LEADS))
        result.append({"run_utc": run.isoformat(), "available_leads": leads,
                       "complete_lead_set": leads == list(LEADS)})
    return {"product": "gfs.pgrb2.0p25", "selection": selection, "runs": result,
            "observations": observations,
            "observation_errors": observation_errors,
            "observation_status": "partial" if observation_errors and result else
                                  "unavailable" if not result else "complete",
            "scope": "Only these bounded directory observations; listed files are not decoded or scientifically accepted."}
