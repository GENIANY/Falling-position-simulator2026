"""Explicit bounded GFS acquisition, product validation and raw replay.

Only this provider adapter performs HTTP or imports ecCodes/NumPy. Offline field
queries do not depend on it. Replay validates the original bytes before decoding.
"""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import urllib.parse
import uuid
from .fields import WeatherError, SCHEMA, _utc, _number, _bracket, geometric_to_geopotential
from .bundle import WeatherField
from .storage import read_json, write_bundle
from .gfs_contract import LEVELS_HPA, LEADS, FILTER_URL, UPPER_KEYS
from .nomads import NomadsGateway, check_cancel

MAX_DECODE_BYTES=536870912


def estimate_decode_bytes(spec):
    """Conservative admission estimate, not an RSS bound or compressed size."""
    b=spec["bounds"]
    cells=(round((b["east"]-b["west"])*4)+1)*(round((b["north"]-b["south"])*4)+1)
    return 64*1024*1024+(len(LEVELS_HPA)*len(UPPER_KEYS)+6)*cells*len(spec["lead_hours"])*192


def _decoder_identity():
    # Import before contacting the provider, including the native ecCodes check.
    import eccodes as ec
    import numpy as np
    return {"eccodes":ec.__version__,"eccodes_api":str(ec.codes_get_api_version()),
            "numpy":np.__version__,"decoder_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}

def _request(request):
    if not isinstance(request,dict):
        raise WeatherError("INVALID_REQUEST","object required")
    allowed={"run_utc","start_utc","end_utc","bounds","max_bytes"}
    if set(request)-allowed or allowed-{"max_bytes"}-set(request):
        raise WeatherError("INVALID_REQUEST","run_utc,start_utc,end_utc,bounds; optional max_bytes")
    run,start,end=(_utc(request[k]) for k in ("run_utc","start_utc","end_utc"))
    if run.hour not in (0,6,12,18) or (run.minute,run.second,run.microsecond)!=(0,0,0):
        raise WeatherError("INVALID_RUN",run)
    if not run<=start<=end<=run+timedelta(hours=384):
        raise WeatherError("INVALID_WINDOW","must fit fixed run 0..384h")
    bounds=request["bounds"]
    if not isinstance(bounds,dict) or set(bounds)!={"west","east","south","north"}:
        raise WeatherError("INVALID_BOUNDS","west/east/south/north required")
    b={k:_number(v,k) for k,v in bounds.items()}
    if not (-90<=b["south"]<b["north"]<=90 and -180<=b["west"]<b["east"]<=360
            and b["east"]-b["west"]<360):
        raise WeatherError("INVALID_BOUNDS","ascending, nonseam rectangle required")
    if b["west"]<0:
        if b["east"]>0:
            raise WeatherError("UNSUPPORTED_SEAM","split acquisition across zero longitude")
        b["west"]+=360; b["east"]+=360
    b={k:(math.floor(v*4)/4 if k in ("west","south") else math.ceil(v*4)/4) for k,v in b.items()}
    maximum=request.get("max_bytes",50_000_000)
    if type(maximum) is not int or not 1024<=maximum<=50_000_000:
        raise WeatherError("INVALID_BYTE_LIMIT","1024..50000000")
    schedule=tuple(run+timedelta(hours=h) for h in LEADS)
    left=min(i for i,w in _bracket(schedule,start,"TIME_OUT_OF_RANGE"))
    right=max(i for i,w in _bracket(schedule,end,"TIME_OUT_OF_RANGE"))
    return {"run_utc":run.isoformat(),"start_utc":start.isoformat(),"end_utc":end.isoformat(),
            "bounds":b,"max_bytes":maximum,"lead_hours":list(LEADS[left:right+1])}


def _url(spec,lead):
    run=_utc(spec["run_utc"])
    query={"file":f"gfs.t{run:%H}z.pgrb2.0p25.f{lead:03d}",
           "dir":f"/gfs.{run:%Y%m%d}/{run:%H}/atmos", "subregion":""}
    query.update({"lev_"+str(n)+"_mb":"on" for n in LEVELS_HPA})
    query.update({"lev_surface":"on","lev_2_m_above_ground":"on","lev_10_m_above_ground":"on"})
    query.update({"var_"+v:"on" for v in ("HGT","TMP","UGRD","VGRD","SPFH","PRES")})
    b=spec["bounds"]
    query.update(leftlon=b["west"],rightlon=b["east"],bottomlat=b["south"],toplat=b["north"])
    return FILTER_URL+"?"+urllib.parse.urlencode(query)


def _download(url,path,remaining,*,cancel=None):
    path=Path(path)
    if path.exists():
        raise WeatherError("OUTPUT_EXISTS",path)
    partial=path.with_name(path.name+"."+uuid.uuid4().hex+".partial")
    info=NomadsGateway().download_to(url,partial,remaining,cancel)
    with partial.open("rb") as stream:
        if stream.read(4)!=b"GRIB":
            raise WeatherError("NOT_GRIB","response retained for diagnosis")
    # Only a complete, bounded response becomes a reusable raw file.
    partial.rename(path)
    return {**info,"file":path.name}


def decode_gfs(paths, specification, provenance):
    """Deterministic raw-GRIB replay; validate product/grid/field/run metadata."""
    import eccodes as ec
    import numpy as np
    spec=specification
    run=_utc(spec["run_utc"])
    all_fields={name:[] for name in UPPER_KEYS.values()}
    all_surface={name:[] for name in ("geopotential_height_gpm","pressure_pa","temperature_2m_k",
                 "specific_humidity_2m_kg_kg","eastward_wind_10m_m_s","northward_wind_10m_m_s")}
    grid=None; summaries=[]
    surface_keys={("orog","surface",0):("geopotential_height_gpm","m"),
                  ("sp","surface",0):("pressure_pa","Pa"),
                  ("2t","heightAboveGround",2):("temperature_2m_k","K"),
                  ("2sh","heightAboveGround",2):("specific_humidity_2m_kg_kg","kg kg**-1"),
                  ("10u","heightAboveGround",10):("eastward_wind_10m_m_s","m s**-1"),
                  ("10v","heightAboveGround",10):("northward_wind_10m_m_s","m s**-1")}
    units={"gh":"gpm","t":"K","u":"m s**-1","v":"m s**-1","q":"kg kg**-1"}
    if len(paths)!=len(spec["lead_hours"]):
        raise WeatherError("RAW_COUNT_MISMATCH","one raw file per planned valid")
    for path,lead in zip(paths,spec["lead_hours"]):
        arrays={}; surfaces={}; message_count=0
        with Path(path).open("rb") as stream:
            while True:
                handle=ec.codes_grib_new_from_file(stream)
                if handle is None: break
                try:
                    get=lambda key:ec.codes_get(handle,key)
                    valid=run+timedelta(hours=lead)
                    checks={"edition":2,"centre":"kwbc","stepUnits":1,
                            "gridType":"regular_ll","dataDate":int(run.strftime("%Y%m%d")),
                            "dataTime":int(run.strftime("%H%M")),"validityDate":int(valid.strftime("%Y%m%d")),
                            "validityTime":int(valid.strftime("%H%M")),"stepType":"instant",
                            "iDirectionIncrementInDegrees":0.25,"jDirectionIncrementInDegrees":0.25,
                            "numberOfMissing":0,"uvRelativeToGrid":0}
                    for key,value in checks.items():
                        if get(key)!=value: raise WeatherError("GRIB_METADATA_MISMATCH",f"{Path(path).name}:{key}")
                    lat=ec.codes_get_array(handle,"latitudes"); lon=ec.codes_get_array(handle,"longitudes")
                    ys=np.unique(lat); xs=np.unique(lon)
                    expected_y=np.arange(spec["bounds"]["south"],spec["bounds"]["north"]+0.125,0.25)
                    expected_x=np.arange(spec["bounds"]["west"],spec["bounds"]["east"]+0.125,0.25)
                    if not np.array_equal(ys,expected_y) or not np.array_equal(xs,expected_x):
                        raise WeatherError("GRIB_GRID_MISMATCH","requested rectangle not returned")
                    order=np.lexsort((lon,lat)); shape=(len(ys),len(xs))
                    if len(order)!=shape[0]*shape[1] or len(set(zip(lat.tolist(),lon.tolist())))!=len(order):
                        raise WeatherError("GRIB_GRID_MISMATCH","duplicated or incomplete coordinates")
                    values=ec.codes_get_values(handle)[order]
                    if not np.isfinite(values).all(): raise WeatherError("MISSING_DATA",Path(path).name)
                    key=(get("shortName"),get("typeOfLevel"),get("level"))
                    if key[0] in UPPER_KEYS and key[1]=="isobaricInhPa" and key[2] in LEVELS_HPA:
                        if get("units")!=units[key[0]] or key in arrays:
                            raise WeatherError("GRIB_FIELD_MISMATCH",key)
                        arrays[key]=values.reshape(shape).tolist()
                    elif key in surface_keys:
                        name,unit=surface_keys[key]
                        if get("units")!=unit or name in surfaces:
                            raise WeatherError("GRIB_FIELD_MISMATCH",key)
                        # GFS orog is WMO discipline0/category3/number5:
                        # geopotential height, despite ecCodes unit label 'm'.
                        if key[0]=="orog" and (get("discipline"),get("parameterCategory"),get("parameterNumber"))!=(0,3,5):
                            raise WeatherError("GRIB_FIELD_MISMATCH","orography parameter")
                        surfaces[name]=values.reshape(shape).tolist()
                    # Filter level/variable cross-products also return e.g. surface T;
                    # they are validated for grid/time but explicitly not substituted.
                    message_count+=1; grid=(ys.tolist(),xs.tolist())
                finally:
                    ec.codes_release(handle)
        expected={(name,"isobaricInhPa",level) for name in UPPER_KEYS for level in LEVELS_HPA}
        if set(arrays)!=expected or set(surfaces)!=set(all_surface):
            raise WeatherError("MISSING_GRIB_FIELDS",f"upper:{sorted(expected-set(arrays))}; surface:{set(all_surface)-set(surfaces)}")
        for short,name in UPPER_KEYS.items():
            all_fields[name].append([arrays[(short,"isobaricInhPa",p)] for p in LEVELS_HPA])
        for name in all_surface:
            all_surface[name].append(surfaces[name])
        summaries.append({"file":Path(path).name,"messages":message_count,"lead_hours":lead})
    metadata={"source":"NOAA NCEP GFS pgrb2.0p25 via NOMADS GRIB filter", "run_utc":spec["run_utc"],
              "request":deepcopy(spec),"provenance":deepcopy(provenance),"raw_summary":summaries,
              "decoder":{"eccodes":ec.__version__,"eccodes_api":ec.codes_get_api_version(),"numpy":np.__version__},
              "interpolation":"per-column linear geopotential height and log pressure; then horizontal/time linear values",
              "surface_bridge":"Each column first above-ground pressure level to surface pressure / 2m T,q / 10m u,v. T,q and wind held below their anchors. Terrain stencil uses explicit surface clamp below a contributing column ground. No log-law or thermal boundary-layer resolution.",
              "vertical_wind":"not acquired or applied; horizontal advection only",
              "limitations":["coarse GFS terrain, not a fine DEM","no forecast accuracy validation","no longitude seam interpolation"]}
    bundle={"schema":SCHEMA,"metadata":metadata,"axes":{"time_utc":[(run+timedelta(hours=h)).isoformat() for h in spec["lead_hours"]],
            "pressure_pa":[p*100 for p in LEVELS_HPA],"latitude_deg":grid[0],"longitude_deg":grid[1]},
            "fields":all_fields,"surface":all_surface}
    field=WeatherField(bundle)
    if min(v for a in all_fields["geopotential_height_gpm"] for row in a[-1] for v in row)<geometric_to_geopotential(30000):
        raise WeatherError("INSUFFICIENT_TOP","30000 geometric metres not supported everywhere")
    return bundle


def replay_gfs(acquisition_dir, output_path):
    """Hash-check saved raw inputs and re-decode without any network access.

    An existing output is refused. Current decoder/library versions are recorded;
    bit-identical output is expected only with the same decoder versions.
    """
    directory=Path(acquisition_dir)
    spec=read_json(directory/"request.json")
    if not isinstance(spec,dict):
        raise WeatherError("INVALID_REQUEST","saved request must be an object")
    validated=_request({k:v for k,v in spec.items() if k!="lead_hours"})
    if validated!=spec:
        raise WeatherError("REQUEST_MISMATCH","saved schedule differs from request")
    provenance=read_json(directory/"provenance.json")
    if not isinstance(provenance,list):
        raise WeatherError("PROVENANCE_MISMATCH","saved provenance must be an array")
    if len(provenance)!=len(spec["lead_hours"]):
        raise WeatherError("RAW_COUNT_MISMATCH","incomplete acquisition")
    paths=[]; total=0
    for item,lead in zip(provenance,spec["lead_hours"]):
        if not isinstance(item,dict) or not {"file","url","bytes","sha256"}<=set(item):
            raise WeatherError("PROVENANCE_MISMATCH","incomplete raw entry")
        if item["file"]!=f"f{lead:03d}.grib2" or item["url"]!=_url(spec,lead):
            raise WeatherError("PROVENANCE_MISMATCH","filename or source URL")
        path=directory/item["file"]
        data=path.read_bytes(); total+=len(data)
        if len(data)!=item["bytes"] or hashlib.sha256(data).hexdigest()!=item["sha256"]:
            raise WeatherError("RAW_HASH_MISMATCH",path.name)
        if total>spec["max_bytes"]:
            raise WeatherError("DOWNLOAD_LIMIT","saved raw bytes exceed request limit")
        paths.append(path)
    target=Path(output_path)
    if target.exists():
        raise WeatherError("OUTPUT_EXISTS",target)
    write_bundle(target,decode_gfs(paths,spec,provenance))
    return target


def _raw_partials(directory):
    """Charge all partial bytes, but never label a local copy as HTTP transfer."""
    paths=list(directory.glob("*.grib2.*.partial"))
    total=sum(path.stat().st_size for path in paths)
    copied=sum(path.stat().st_size for path in paths if path.name.endswith(".reuse.partial"))
    return total,total-copied


def _verified_raw_candidates(spec, leads, provider, cancel):
    """Internal provider supplies only registered completed-asset candidates.

    Exact URL includes run/lead, all selectors and the normalized rectangle.
    It identifies a request, not unique provider bytes: conflicting saved bytes
    for one URL are refused. All candidates are checked before starting HTTP.
    """
    if provider is None or not leads:
        return {}
    result={}
    for candidate in provider(spec,tuple(leads)):
        check_cancel(cancel)
        lead=candidate["lead_hours"]; item=candidate["provenance"]
        path=Path(candidate["path"])
        if (type(lead) is not int or lead not in leads or item.get("file")!=f"f{lead:03d}.grib2"
                or item.get("url")!=_url(spec,lead) or path.name!=item["file"]
                or path.is_symlink() or not path.is_file()):
            raise WeatherError("RAW_REUSE_IDENTITY_MISMATCH","Saved raw candidate identity/path differs.")
        size=item.get("bytes"); expected=item.get("sha256")
        if type(size) is not int or not 4<=size<=50_000_000 or not isinstance(expected,str) or len(expected)!=64:
            raise WeatherError("RAW_REUSE_IDENTITY_MISMATCH","Invalid raw size or digest.")
        before=path.stat(); digest=hashlib.sha256(); count=0
        with path.open("rb") as stream:
            first=stream.read(4)
            if first!=b"GRIB": raise WeatherError("RAW_HASH_MISMATCH",path.name)
            digest.update(first); count=4
            while True:
                check_cancel(cancel)
                chunk=stream.read(65536)
                if not chunk: break
                count+=len(chunk)
                if count>size: raise WeatherError("RAW_HASH_MISMATCH",path.name)
                digest.update(chunk)
        after=path.stat()
        stamp=lambda st:(st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns)
        if count!=size or digest.hexdigest()!=expected or stamp(before)!=stamp(after):
            raise WeatherError("RAW_HASH_MISMATCH",path.name)
        checked={**candidate,"provenance":deepcopy(item),"stat":stamp(after)}
        previous=result.get(lead)
        if previous and (previous["provenance"]["sha256"],previous["provenance"]["bytes"])!=(expected,size):
            raise WeatherError("AMBIGUOUS_SAVED_RAW","The same raw request has different verified saved bytes.")
        if previous is None: result[lead]=checked  # Provider order is deterministic.
    return result


def _copy_verified_raw(candidate, path, remaining, cancel):
    """Independent, bounded copy. Preserve the original HTTP observation."""
    item=deepcopy(candidate["provenance"]); source=Path(candidate["path"])
    if remaining<item["bytes"]: raise WeatherError("DOWNLOAD_LIMIT","Saved raw exceeds remaining input budget.")
    if path.exists(): raise WeatherError("OUTPUT_EXISTS",path)
    check_cancel(cancel)
    before=source.stat()
    stamp=lambda st:(st.st_dev,st.st_ino,st.st_size,st.st_mtime_ns)
    if source.is_symlink() or stamp(before)!=candidate["stat"]:
        raise WeatherError("RAW_HASH_MISMATCH","Saved raw changed after verification.")
    partial=path.with_name(path.name+"."+uuid.uuid4().hex+".reuse.partial")
    digest=hashlib.sha256(); count=0
    with source.open("rb") as original,partial.open("xb") as output:
        while True:
            check_cancel(cancel)
            chunk=original.read(min(65536,item["bytes"]-count+1))
            if not chunk: break
            if count+len(chunk)>item["bytes"]:
                raise WeatherError("RAW_HASH_MISMATCH","Saved raw grew while copying.")
            output.write(chunk); digest.update(chunk); count+=len(chunk)
        output.flush(); os.fsync(output.fileno())
    check_cancel(cancel)
    # Verify stored destination bytes, not merely the source chunks sent to write.
    destination_digest=hashlib.sha256(); destination_count=0
    with partial.open("rb") as saved:
        while True:
            check_cancel(cancel)
            chunk=saved.read(min(65536,item["bytes"]-destination_count+1))
            if not chunk: break
            destination_count+=len(chunk)
            if destination_count>item["bytes"]:
                raise WeatherError("RAW_HASH_MISMATCH","Copied raw size differs on readback.")
            destination_digest.update(chunk)
    if (destination_count!=item["bytes"] or destination_digest.hexdigest()!=item["sha256"]
            or partial.stat().st_size!=item["bytes"]):
        raise WeatherError("RAW_HASH_MISMATCH","Copied raw failed destination readback.")
    check_cancel(cancel)
    if (count!=item["bytes"] or digest.hexdigest()!=item["sha256"]
            or stamp(source.stat())!=candidate["stat"]):
        raise WeatherError("RAW_HASH_MISMATCH","Saved raw changed while copying.")
    item.setdefault("reuse_history",[]).append({**candidate["donor"],
        "copied_at_utc":datetime.now(timezone.utc).isoformat(),
        "source_provenance_sha256":hashlib.sha256(json.dumps(candidate["provenance"],sort_keys=True,
             separators=(",",":"),ensure_ascii=False,allow_nan=False).encode("utf-8")).hexdigest()})
    # Crash before provenance commit is handled by the existing orphan rule.
    partial.rename(path)
    return item


def acquire_gfs(request, output_dir, *, resume=False, progress=None, cancel=None, raw_provider=None):
    """Download one fixed run and complete scheduled time window, bounded to50MB.

    Existing output is refused unless resume is explicit. Resume reuses only
    complete raw files with matching request, URL and hash; partial bytes remain
    separate and count against the total raw byte budget. No retry/run fallback
    is implicit. Cancellation is cooperative between reads and before decoding.
    raw_provider is an internal completed-asset source, never an HTTP filepath.
    Reuse preserves original HTTP provenance and revalidates the new full window.
    """
    spec=_request(request)
    directory=Path(output_dir)
    existed=directory.exists()
    if existed and not resume: raise WeatherError("OUTPUT_EXISTS",directory)
    if estimate_decode_bytes(spec)>MAX_DECODE_BYTES:
        raise WeatherError("DECODE_MEMORY_LIMIT","Estimated working memory exceeds the 512 MiB admission limit.")
    decoder=_decoder_identity()
    directory.mkdir(parents=True,exist_ok=resume)
    def save(name,value):
        temporary=directory/(name+"."+uuid.uuid4().hex+".tmp")
        with temporary.open("x",encoding="utf-8") as stream:
            json.dump(value,stream,ensure_ascii=False,indent=2,allow_nan=False)
            stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary,directory/name)
    if existed:
        if read_json(directory/"request.json")!=spec:
            raise WeatherError("REQUEST_MISMATCH","Resume cannot change the fixed request.")
        if not (directory/"decoder.json").exists() or read_json(directory/"decoder.json")!=decoder:
            raise WeatherError("DECODER_CHANGED","Resume requires the same decoder; preserve old raw data for explicit replay.")
        provenance=read_json(directory/"provenance.json") if (directory/"provenance.json").exists() else []
    else:
        save("request.json",spec)
        save("decoder.json",decoder)
        provenance=[]
        save("provenance.json",provenance)
    if not isinstance(provenance,list) or len(provenance)>len(spec["lead_hours"]):
        raise WeatherError("PROVENANCE_MISMATCH","Invalid completed raw entries.")
    paths=[]; reused=0; downloaded=0
    for item,lead in zip(provenance,spec["lead_hours"]):
        if not isinstance(item,dict) or item.get("file")!=f"f{lead:03d}.grib2" or item.get("url")!=_url(spec,lead):
            raise WeatherError("PROVENANCE_MISMATCH","Completed entries must be the exact schedule prefix.")
        path=directory/item["file"]
        data=path.read_bytes()
        if len(data)!=item.get("bytes") or hashlib.sha256(data).hexdigest()!=item.get("sha256") or data[:4]!=b"GRIB":
            raise WeatherError("RAW_HASH_MISMATCH",path.name)
        paths.append(path); reused+=len(data)
    # Incomplete bytes are retained for diagnosis, never silently re-used or deleted.
    for lead in spec["lead_hours"][len(paths):]:
        orphan=directory/f"f{lead:03d}.grib2"
        if orphan.exists():
            # A crash may occur after the raw rename and before its receipt.
            # Without a receipt do not trust/reuse it; preserve it as partial.
            orphan.rename(orphan.with_name(orphan.name+"."+uuid.uuid4().hex+".partial"))
    retained,initial_http_partial=_raw_partials(directory)
    remaining=spec["max_bytes"]-reused-retained
    if remaining<0: raise WeatherError("DOWNLOAD_LIMIT","Retained raw bytes exceed the input budget.")
    def report(phase,lead=None):
        if progress:
            progress({"phase":phase,"completed_files":len(paths),"total_files":len(spec["lead_hours"]),
                      "bytes_downloaded":downloaded,"bytes_reused":reused,"retained_partial_bytes":retained,"lead":lead})
    target=directory/"weather.json.gz"
    if target.exists():
        if len(paths)!=len(spec["lead_hours"]) or not (directory/"receipt.json").exists():
            raise WeatherError("INCOMPLETE_PUBLICATION","Existing bundle has no complete receipt; inspect before retry.")
        receipt=read_json(directory/"receipt.json")
        if hashlib.sha256(target.read_bytes()).hexdigest()!=receipt.get("bundle_sha256"):
            raise WeatherError("BUNDLE_HASH_MISMATCH",target.name)
        report("completed")
        return target
    try:
        check_cancel(cancel)
        needed=spec["lead_hours"][len(paths):]
        report("checking_saved_raw")
        donors=_verified_raw_candidates(spec,needed,raw_provider,cancel)
        reserved=sum(item["provenance"]["bytes"] for item in donors.values())
        if reserved>remaining:
            raise WeatherError("DOWNLOAD_LIMIT","Saved raw plus retained bytes exceed the input budget.")
        for lead in needed:
            phase="reusing_raw" if lead in donors else "downloading"
            report(phase,lead)
            check_cancel(cancel)
            path=directory/f"f{lead:03d}.grib2"
            if lead in donors:
                info=_copy_verified_raw(donors[lead],path,remaining,cancel)
                reserved-=info["bytes"]; reused+=info["bytes"]
            else:
                # Reserve known future local inputs before admitting an HTTP body.
                info=_download(_url(spec,lead),path,remaining-reserved,cancel=cancel)
                downloaded+=info["bytes"]
            remaining-=info["bytes"]; provenance.append(info); paths.append(path)
            save("provenance.json",provenance)
            report(phase,lead)
        check_cancel(cancel)
        report("decoding")
        bundle=decode_gfs(paths,spec,provenance)
        check_cancel(cancel)
        temporary=directory/("weather."+uuid.uuid4().hex+".json.gz.partial")
        write_bundle(temporary,bundle)
        save("receipt.json",{"bundle":target.name,"bundle_sha256":hashlib.sha256(temporary.read_bytes()).hexdigest(),
                            "downloaded_bytes":downloaded,"reused_bytes":reused,"retained_partial_bytes":retained,
                            "raw_files":len(paths)})
        temporary.rename(target)
        report("completed")
        return target
    except Exception as exc:
        current_retained,current_http_partial=_raw_partials(directory)
        downloaded+=max(0,current_http_partial-initial_http_partial)
        retained=current_retained
        save("failure.json",{"type":type(exc).__name__,"detail":str(exc),"completed_raw_files":len(paths),
                             "bytes_downloaded":downloaded,"bytes_reused":reused,"retained_partial_bytes":retained})
        report("cancelled" if getattr(exc,"code",None)=="ACQUISITION_CANCELLED" else "failed")
        raise
