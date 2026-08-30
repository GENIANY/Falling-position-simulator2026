import { describe, expect, it } from 'vitest'
import {
  computeLandingStats,
  ellipseToLatLngs,
  haversineM,
  metersToLatLon,
  toLocalMeters,
} from './landing'
import { gaussian, mulberry32, weibull } from './random'

describe('projections', () => {
  it('round-trips meters<->latlon', () => {
    const origin = { lat: 33.1, lon: 132.5 }
    const ll = metersToLatLon([1000, 2000], origin)
    const [xy] = toLocalMeters([ll], origin)
    expect(xy[0]).toBeCloseTo(1000, 0)
    expect(xy[1]).toBeCloseTo(2000, 0)
  })

  it('haversine known distance', () => {
    // 緯度1度 ≈ 111km
    const d = haversineM({ lat: 33, lon: 132 }, { lat: 34, lon: 132 })
    expect(d / 1000).toBeGreaterThan(110)
    expect(d / 1000).toBeLessThan(112)
  })
})

describe('computeLandingStats', () => {
  it('axis-aligned gaussian cloud gives sensible covariance and ellipse', () => {
    const rng = mulberry32(42)
    const origin = { lat: 33.1, lon: 132.5 }
    // x方向σ=2000m, y方向σ=500mの点群
    const points = Array.from({ length: 2000 }, () =>
      metersToLatLon([gaussian(rng, 0, 2000), gaussian(rng, 0, 500)], origin),
    )
    const stats = computeLandingStats(points)
    expect(stats.mean.lat).toBeCloseTo(origin.lat, 2)
    expect(stats.mean.lon).toBeCloseTo(origin.lon, 2)
    const sxx = Math.sqrt(stats.covariance[0][0])
    const syy = Math.sqrt(stats.covariance[1][1])
    expect(sxx).toBeGreaterThan(1800)
    expect(sxx).toBeLessThan(2200)
    expect(syy).toBeGreaterThan(430)
    expect(syy).toBeLessThan(570)
    // 長軸はほぼ東西 (角度 ~0deg or ~180deg)
    const e95 = stats.ellipses.find((e) => e.probability === 0.95)!
    const angle = Math.abs(e95.angleDeg % 180)
    expect(Math.min(angle, 180 - angle)).toBeLessThan(10)
    // 95%楕円長半径 ≈ sqrt(5.99)*2000 ≈ 4900m
    expect(e95.semiMajorM).toBeGreaterThan(4300)
    expect(e95.semiMajorM).toBeLessThan(5500)
  })

  it('95% ellipse covers roughly 95% of points', () => {
    const rng = mulberry32(7)
    const origin = { lat: 33.1, lon: 132.5 }
    const xy: [number, number][] = Array.from({ length: 3000 }, () => [
      gaussian(rng, 0, 1000),
      gaussian(rng, 0, 1000),
    ])
    const points = xy.map((p) => metersToLatLon(p, origin))
    const stats = computeLandingStats(points)
    const e95 = stats.ellipses.find((e) => e.probability === 0.95)!
    // 等方なので楕円内判定は半径比較で近似できる
    const covered = xy.filter(
      ([x, y]) =>
        (x / e95.semiMajorM) ** 2 + (y / e95.semiMinorM) ** 2 <= 1,
    ).length
    const ratio = covered / xy.length
    expect(ratio).toBeGreaterThan(0.93)
    expect(ratio).toBeLessThan(0.97)
  })

  it('ellipseToLatLngs produces closed ring around center', () => {
    const stats = computeLandingStats([
      { lat: 33.1, lon: 132.5 },
      { lat: 33.11, lon: 132.51 },
      { lat: 33.09, lon: 132.49 },
    ])
    const ring = ellipseToLatLngs(stats.mean, stats.ellipses[0], 32)
    expect(ring).toHaveLength(32)
    for (const [lat, lon] of ring) {
      expect(Math.abs(lat - stats.mean.lat)).toBeLessThan(0.5)
      expect(Math.abs(lon - stats.mean.lon)).toBeLessThan(0.5)
    }
  })
})

describe('random', () => {
  it('gaussian moments', () => {
    const rng = mulberry32(1)
    const xs = Array.from({ length: 10000 }, () => gaussian(rng, 5, 0.5))
    const mean = xs.reduce((a, b) => a + b, 0) / xs.length
    const sd = Math.sqrt(
      xs.reduce((a, b) => a + (b - mean) ** 2, 0) / xs.length,
    )
    expect(mean).toBeCloseTo(5, 1)
    expect(sd).toBeCloseTo(0.5, 1)
  })

  it('weibull is positive and scales with scale param', () => {
    const rng = mulberry32(2)
    const xs = Array.from({ length: 10000 }, () => weibull(rng, 3.0, 30000))
    expect(Math.min(...xs)).toBeGreaterThan(0)
    const mean = xs.reduce((a, b) => a + b, 0) / xs.length
    // Weibull mean = scale * Γ(1+1/k) ≈ 30000 * 0.8930 ≈ 26790
    expect(mean).toBeGreaterThan(26000)
    expect(mean).toBeLessThan(27600)
  })

  it('is reproducible with same seed', () => {
    const a = mulberry32(99)
    const b = mulberry32(99)
    for (let i = 0; i < 100; i++) {
      expect(a()).toBe(b())
    }
  })
})
