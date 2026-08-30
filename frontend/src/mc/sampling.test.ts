import { describe, expect, it } from 'vitest'
import { partitionIndices, perturbationForIndex } from './sampling'
import type { MCConfig } from './mcTypes'

const config: MCConfig = {
  base: {
    profile: 'standard_profile',
    launch_latitude: 33.1,
    launch_longitude: 132.5,
    launch_altitude: 0,
    launch_datetime: '2026-08-05T00:00:00.000Z',
    ascent_rate: 5,
    burst_altitude: 30000,
    descent_rate: 5,
  },
  samples: 100,
  sigma: { ascentRate: 0.5, burstAltitudePct: 5, descentRate: 0.5 },
  burstModel: 'gaussian',
  seed: 42,
}

describe('perturbationForIndex', () => {
  it('is deterministic per (seed, index) regardless of worker split', () => {
    const a = perturbationForIndex(config, 7)
    const b = perturbationForIndex(config, 7)
    expect(a).toEqual(b)
  })

  it('different indices differ', () => {
    expect(perturbationForIndex(config, 1)).not.toEqual(
      perturbationForIndex(config, 2),
    )
  })

  it('gaussian: sample moments近似', () => {
    const perts = Array.from({ length: 3000 }, (_, i) =>
      perturbationForIndex(config, i),
    )
    const mean =
      perts.reduce((s, p) => s + p.burstAltitude, 0) / perts.length
    expect(mean).toBeGreaterThan(29500)
    expect(mean).toBeLessThan(30500)
    const ascMean = perts.reduce((s, p) => s + p.ascentRate, 0) / perts.length
    expect(ascMean).toBeCloseTo(5, 0)
  })

  it('weibull: burst高度のみ摂動', () => {
    const w = perturbationForIndex({ ...config, burstModel: 'weibull' }, 3)
    expect(w.ascentRate).toBe(5)
    expect(w.descentRate).toBe(5)
    expect(w.burstAltitude).not.toBe(30000)
    expect(w.burstAltitude).toBeGreaterThan(0)
  })
})

describe('partitionIndices', () => {
  it('covers all indices exactly once', () => {
    const parts = partitionIndices(100, 4)
    const all = parts.flat().sort((a, b) => a - b)
    expect(all).toEqual(Array.from({ length: 100 }, (_, i) => i))
  })

  it('handles fewer items than parts', () => {
    const parts = partitionIndices(2, 4)
    expect(parts.flat().sort()).toEqual([0, 1])
    expect(parts.every((p) => p.length > 0)).toBe(true)
  })
})
