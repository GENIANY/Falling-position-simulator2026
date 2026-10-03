import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { parseEgm96 } from '../scene3d/src/vertical-datum.js';

const bytes = readFileSync(new URL('../scene3d/data/WW15MGH.DAC', import.meta.url));
const arrayBuffer = () => Uint8Array.from(bytes).buffer;
const grid = parseEgm96(arrayBuffer());

describe('display-only EGM96 datum', () => {
  it('pins the distributed public dataset, including its byte order and extent', () => {
    expect(bytes.byteLength).toBe(2_076_480);
    expect(createHash('sha256').update(bytes).digest('hex'))
      .toBe('9dcaf4efd6857aaa2e1e2e2c574d3f5264eacf47024cdcd5291c40ddad5e5acc');
  });

  // NGA's published WW15MGH.GRD has millimetre text precision. DAC has
  // centimetre precision: the full grids differ by at most 0.006 m.
  // These are source reference numbers, not values calculated by this sampler.
  it.each([
    [0, 0, 17.162], [0, 90, 13.606], [0, -90, -29.534],
    [180, 0, 21.153], [141.5, 43, 31.335], [139.75, 35.75, 36.812],
    [77.25, 11.75, -90.111], [270, 38.75, -31.717],
  ])('agrees with NGA grid anchor (%s, %s)', (lon, lat, expected) => {
    expect(Math.abs(grid.heightOffset(lon, lat) - expected)).toBeLessThanOrEqual(0.0061);
  });

  // Reference coordinates/numbers: Cesium Native EGM96 tests, attributed
  // there to UNAVCO's geoid calculator; Apache-2.0, see data/README.md.
  // Selection only; no Cesium test code or sampler implementation is copied.
  it.each([
    [135.89012584487307, 11.046411138991914, 57.79],
    [179.78766535213848, -66.77911223257036, -57.37],
    [281.9977024865146, -81.38156198351201, -27.93],
    [77.26636943208759, 11.790177979066698, -90.03],
    [140.1466268002612, 21.545270556717682, 47.96],
    [359.50010262934694, 1.6307925009477486, 16.99],
  ])('agrees with a published off-grid reference (%s, %s)', (lon, lat, expected) => {
    expect(Math.abs(grid.heightOffset(lon, lat) - expected)).toBeLessThanOrEqual(0.01);
  });

  it('adds positive and negative geoid offsets without altering scientific ASL values', () => {
    const source = Object.freeze({ longitude: 141.5, latitude: 43, altitude_m_asl: 30_000 });
    expect(source.altitude_m_asl + grid.heightOffset(source.longitude, source.latitude))
      .toBeCloseTo(30_031.33, 8);
    expect(1000 + grid.heightOffset(77.25, 11.75)).toBeCloseTo(909.89, 8);
    expect(source.altitude_m_asl).toBe(30_000);
  });

  it('is periodic at Greenwich and the date line, including non-grid positions', () => {
    for (const lat of [-90, -89.875, -12.345, 0, 43.123, 89.875, 90]) {
      expect(grid.heightOffset(-0.125, lat)).toBe(grid.heightOffset(359.875, lat));
      expect(grid.heightOffset(0, lat)).toBe(grid.heightOffset(360, lat));
      expect(grid.heightOffset(-180, lat)).toBe(grid.heightOffset(180, lat));
      expect(grid.heightOffset(-179.875, lat)).toBe(grid.heightOffset(180.125, lat));
      expect(grid.heightOffset(539.875, lat)).toBe(grid.heightOffset(179.875, lat));
      expect(Math.abs(grid.heightOffset(179.999999, lat) - grid.heightOffset(-179.999999, lat)))
        .toBeLessThan(0.0001);
    }
  });

  it('wraps within each row instead of interpolating across adjacent rows', () => {
    const buffer = new ArrayBuffer(2_076_480);
    const view = new DataView(buffer);
    const set = (row: number, column: number, cm: number) =>
      view.setInt16((row * 1440 + column) * 2, cm, false);
    set(360, 1439, 1000); set(360, 0, 3000);
    set(361, 1439, -2000); set(361, 0, 6000);
    set(362, 0, 30000); // poison the accidental next-row lookup
    const synthetic = parseEgm96(buffer);
    expect(synthetic.heightOffset(359.875, -0.125)).toBe(20);
    expect(synthetic.heightOffset(-0.125, -0.125)).toBe(20);
  });

  it('keeps both poles independent of longitude and approaches them continuously', () => {
    for (const lon of [-720, -180, -0.125, 0, 139.75, 359.875, 720]) {
      expect(grid.heightOffset(lon, 90)).toBe(13.61);
      expect(grid.heightOffset(lon, -90)).toBe(-29.53);
      expect(Math.abs(grid.heightOffset(lon, 89.999999) - 13.61)).toBeLessThan(0.0001);
      expect(Math.abs(grid.heightOffset(lon, -89.999999) + 29.53)).toBeLessThan(0.0001);
    }
  });

  it('owns its input bytes after parsing', () => {
    const buffer = arrayBuffer();
    const stable = parseEgm96(buffer);
    new Uint8Array(buffer).fill(0);
    expect(stable.heightOffset(141.5, 43)).toBe(31.33);
  });

  it('rejects partial, trailing, incorrectly typed and inconsistent polar data', () => {
    expect(() => parseEgm96(new ArrayBuffer(2_076_478))).toThrow(RangeError);
    expect(() => parseEgm96(new ArrayBuffer(2_076_482))).toThrow(RangeError);
    expect(() => parseEgm96(bytes as unknown as ArrayBuffer)).toThrow(TypeError);
    const malformed = arrayBuffer();
    new DataView(malformed).setInt16(2, 1234, false);
    expect(() => parseEgm96(malformed)).toThrow(/polar rows/);
  });

  it.each([
    [NaN, 0], [Infinity, 0], [-Infinity, 0], [0, NaN], [0, Infinity],
    [0, 90.000001], [0, -90.000001], ['139', 35], [139, '35'], [null, 0],
  ])('rejects invalid coordinates (%s, %s)', (lon, lat) => {
    expect(() => grid.heightOffset(lon as number, lat as number)).toThrow();
  });
});
