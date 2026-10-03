"""Prepare small original-wind demos without a network request.

Default: verify and extract the repository's fixed JRA/ERA demo archive.
--source: select four native cells around a point from one complete source.
No spatial interpolation, quantization, or synthetic completion is performed.
The output must be a new directory; incomplete output is retained on failure.
"""
from pathlib import Path
import argparse
from copy import deepcopy
import hashlib
import json
import zipfile

import numpy as np

from backend.climate.samples import MonthlySamples, digest


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf8')


def subset(source, output, latitude, longitude):
    data = MonthlySamples(source)
    if data.schema != 'balloon.wind-samples/1' or set(data.months) != set(range(1, 13)):
        raise ValueError('A complete twelve-month original source is required.')
    latitudes = sorted({c['lat'] for c in data.grid})
    longitudes = sorted({c['lon'] for c in data.grid})

    def bracket(values, centre):
        if len(values) < 2 or not values[0] <= centre <= values[-1]:
            raise ValueError('The point must lie within a two-dimensional native grid.')
        upper = min(max(int(np.searchsorted(values, centre, side='right')), 1), len(values)-1)
        return values[upper-1:upper+1]

    lat, lon = bracket(latitudes, latitude), bracket(longitudes, longitude)
    indices = [i for i, c in enumerate(data.grid) if c['lat'] in lat and c['lon'] in lon]
    if len(indices) != 4:
        raise ValueError('Four complete native cells are required.')
    result = deepcopy(data.manifest)
    result['label'] = (f"{result['provider']} {data.years[0]}–{data.years[1]} / "
                       f"指定点({latitude:g}, {longitude:g})周辺2×2元格子 / 機能確認用")
    result['grid'] = [result['grid'][i] for i in indices]
    result['provenance']['derived_subset'] = {
        'source_manifest_sha256': data.bundle_sha256,
        'original_cell_ids': [c['cell_id'] for c in result['grid']],
        'selection_point': {'latitude': latitude, 'longitude': longitude},
        'operation': 'exact native-cell selection; all original UTC times and pressure levels retained',
        'scope': 'small functional demo, not a regional climatological sample or flight weather field',
        'tool_sha256': digest(Path(__file__)),
    }
    output.mkdir(parents=True, exist_ok=False)
    for item in result['months']:
        month = item['month']
        directory = output/f'month-{month:02d}'
        directory.mkdir()
        for component in ('u', 'v'):
            original = np.load(data.months[month]['files'][component], mmap_mode='r', allow_pickle=False)
            selected = np.ascontiguousarray(original[:, :, indices])
            path = directory/f'{component}.npy'
            np.save(path, selected, allow_pickle=False)
            if not np.array_equal(np.load(path, allow_pickle=False), original[:, :, indices]):
                raise ValueError('The saved native values do not match their source.')
            item[component] = {'file': path.relative_to(output).as_posix(), 'sha256': digest(path), 'bytes': path.stat().st_size}
            del original, selected
    data.assert_current()
    write_json(output/'manifest.json', result)
    checked = MonthlySamples(output/'manifest.json')
    return {'manifest': str(output/'manifest.json'), **checked.verify_full(),
            'original_manifest_sha256': data.bundle_sha256, 'cells': 4}


def extract_repository_demo(root, output):
    package = root/'references/climate_demo_057'
    inventory = json.loads((package/'archive.json').read_bytes())
    archive = package/'wind-samples.zip'
    if digest(archive) != inventory['sha256'] or archive.stat().st_size != inventory['bytes']:
        raise ValueError('The fixed repository demo archive does not match its inventory.')
    with zipfile.ZipFile(archive) as bundle:
        entries = bundle.infolist()
        if len(entries) != len(inventory['members']) or {i.filename for i in entries} != set(inventory['members']):
            raise ValueError('Archive members differ from the fixed inventory.')
        for item in entries:
            relative = Path(item.filename)
            if relative.is_absolute() or '..' in relative.parts or item.is_dir() or item.file_size > 5*1024*1024:
                raise ValueError('Unexpected archive path or member size.')
            expected = inventory['members'][item.filename]
            if item.file_size != expected['bytes'] or hashlib.sha256(bundle.read(item)).hexdigest() != expected['sha256']:
                raise ValueError('Archive member content differs from the fixed inventory.')
        output.mkdir(parents=True, exist_ok=False)
        for item in entries:
            path = output/item.filename
            if not path.resolve().is_relative_to(output.resolve()):
                raise ValueError('Archive member escaped its output directory.')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(bundle.read(item))
    manifests = [output/provider/'manifest.json' for provider in ('jra3q', 'era5')]
    for path in manifests:
        source = MonthlySamples(path)
        if set(source.months) != set(range(1, 13)):
            raise ValueError('Repository demo must contain all twelve months.')
        source.verify_full()
    return {'manifests': [str(p) for p in manifests], 'network_requests': 0,
            'scope': 'two independent four-cell functional demos; all 2024 UTC times and native pressure levels'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--source', type=Path, help='derive a native-cell subset instead of extracting the repository package')
    parser.add_argument('--latitude', type=float, default=43.2)
    parser.add_argument('--longitude', type=float, default=141.4)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error('Existing output is preserved; choose a new directory.')
    result = subset(args.source, args.output, args.latitude, args.longitude) if args.source else extract_repository_demo(Path(__file__).resolve().parents[1], args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
