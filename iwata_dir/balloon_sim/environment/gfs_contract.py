"""GFS pressure-product constants and schedule validation; no HTTP or decoding."""
from datetime import timedelta
from .fields import WeatherError, _utc

LEVELS_HPA = (1000,975,950,925,900,850,800,750,700,650,600,550,500,450,
              400,350,300,250,200,150,100,70,50,40,30,20,15,10,7,5,3,2,1)
LEADS = tuple(range(121)) + tuple(range(123,385,3))
FILTER_URL = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl"
UPPER_KEYS = {"gh":"geopotential_height_gpm", "t":"temperature_k",
              "u":"eastward_wind_m_s", "v":"northward_wind_m_s",
              "q":"specific_humidity_kg_kg"}


def validate_gfs_times(metadata, times):
    """Check a declared GFS run against its complete native delivery schedule."""
    run = metadata.get("run_utc")
    if run is not None:
        run = _utc(run)
        if run.hour not in (0,6,12,18) or (run.minute,run.second,run.microsecond)!=(0,0,0):
            raise WeatherError("INVALID_RUN", run)
        expected = [run+timedelta(hours=h) for h in LEADS
                    if times[0] <= run+timedelta(hours=h) <= times[-1]]
        if tuple(expected) != times:
            raise WeatherError("MISSING_VALID_TIME", "GFS schedule must have no internal gaps")
