"""Extract a grid-aligned rectangle without changing values or interpolating.

Preserve upstream metadata and bind the derivative to the exact input bytes.
Used for small offline flight examples; this is not weather acquisition.
"""
from pathlib import Path
import argparse
from copy import deepcopy
import gzip
import hashlib
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from balloon_sim.weather import WeatherField, _write_bundle, _read_json


def subset(source, bounds):
    path=Path(source)
    b=_read_json(path)
    WeatherField(b)
    south,north,west,east=bounds
    if not south<north or not west<east:
        raise ValueError('ascending rectangle required')
    ys=b['axes']['latitude_deg'];xs=b['axes']['longitude_deg']
    if south not in ys or north not in ys or west not in xs or east not in xs:
        raise ValueError('bounds must be exact existing grid points')
    j0,j1=ys.index(south),ys.index(north)+1
    i0,i1=xs.index(west),xs.index(east)+1
    out=deepcopy(b)
    out['axes']['latitude_deg']=ys[j0:j1];out['axes']['longitude_deg']=xs[i0:i1]
    cut=lambda plane:[row[i0:i1] for row in plane[j0:j1]]
    out['fields']={k:[[cut(plane) for plane in t] for t in a] for k,a in b['fields'].items()}
    out['surface']={k:[cut(plane) for plane in a] for k,a in b['surface'].items()}
    out['metadata']['subset']={'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'bounds':{'south':south,'north':north,'west':west,'east':east},
        'method':'exact index slices, no resampling; original request describes acquisition, subset bounds describe stored coverage'}
    WeatherField(out)
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path)
    p.add_argument('--bounds',type=float,nargs=4,metavar=('SOUTH','NORTH','WEST','EAST'),required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():p.error('output exists')
    result=subset(a.source,a.bounds)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    _write_bundle(a.output,result)
    print(a.output)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
