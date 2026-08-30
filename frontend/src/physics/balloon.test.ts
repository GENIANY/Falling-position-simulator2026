import { describe, expect, it } from 'vitest'
import {
  BalloonPhysicsError,
  computeBalloon,
  solveCubicLaunchRadius,
} from './balloon'

// legacy calc.js の burst-altitude パスをNodeで忠実実行して得た黄金値
const GOLDEN = [
  {
    name: 'k1200 + 1000g + He + tba30000',
    inputs: {
      payloadMassG: 1000,
      balloonModel: 'k1200',
      gas: 'helium' as const,
      target: { kind: 'burstAltitude' as const, value: 30000 },
    },
    expected: {
      ascentRate: 7.600437042636673,
      burstAltitude: 30000.000000000007,
      timeToBurstMin: 65.7856906379353,
      neckLiftG: 4274.724053407592,
      launchVolumeM3: 5.33390885951636,
    },
  },
  {
    name: 'h500 + 250g + H2 + tba25000',
    inputs: {
      payloadMassG: 250,
      balloonModel: 'h500',
      gas: 'hydrogen' as const,
      target: { kind: 'burstAltitude' as const, value: 25000 },
    },
    expected: {
      ascentRate: 7.187463439286281,
      burstAltitude: 25000.000000000004,
      timeToBurstMin: 57.97130937587655,
      neckLiftG: 1807.993610160845,
      launchVolumeM3: 2.0697637971131244,
    },
  },
  {
    name: 'k1500 + 2000g + He + tba33000',
    inputs: {
      payloadMassG: 2000,
      balloonModel: 'k1500',
      gas: 'helium' as const,
      target: { kind: 'burstAltitude' as const, value: 33000 },
    },
    expected: {
      ascentRate: 4.89760340988275,
      burstAltitude: 33000,
      timeToBurstMin: 112.2998238056942,
      neckLiftG: 3234.2074864071365,
      launchVolumeM3: 4.612439094317163,
    },
  },
]

describe('computeBalloon parity with legacy calc.js', () => {
  for (const g of GOLDEN) {
    it(g.name, () => {
      const r = computeBalloon(g.inputs)
      expect(r.ascentRate).toBeCloseTo(g.expected.ascentRate, 6)
      expect(r.burstAltitude).toBeCloseTo(g.expected.burstAltitude, 3)
      expect(r.timeToBurstMin).toBeCloseTo(g.expected.timeToBurstMin, 4)
      expect(r.neckLiftG).toBeCloseTo(g.expected.neckLiftG, 3)
      expect(r.launchVolumeM3).toBeCloseTo(g.expected.launchVolumeM3, 6)
    })
  }
})

describe('ascent-rate target (legacy Cardano was broken here)', () => {
  it('round-trips: target ascent rate -> radius -> performance -> same ascent rate', () => {
    for (const tar of [2, 3.5, 5, 7]) {
      const r = computeBalloon({
        payloadMassG: 1000,
        balloonModel: 'k1200',
        gas: 'helium',
        target: { kind: 'ascentRate', value: tar },
      })
      expect(r.ascentRate).toBeCloseTo(tar, 4)
    }
  })

  it('monotonic: faster target ascent needs more gas, gives lower burst altitude', () => {
    const slow = computeBalloon({
      payloadMassG: 1000,
      balloonModel: 'k1200',
      gas: 'helium',
      target: { kind: 'ascentRate', value: 3 },
    })
    const fast = computeBalloon({
      payloadMassG: 1000,
      balloonModel: 'k1200',
      gas: 'helium',
      target: { kind: 'ascentRate', value: 7 },
    })
    expect(fast.launchVolumeM3).toBeGreaterThan(slow.launchVolumeM3)
    expect(fast.burstAltitude).toBeLessThan(slow.burstAltitude)
  })
})

describe('solveCubicLaunchRadius', () => {
  it('matches numeric root for balloon-shaped cubics', () => {
    // a>0, b<0, c=0, d<0 の典型形状
    const cases = [
      { a: 42.2, b: -9.5, c: 0, d: -21.6 },
      { a: 10, b: -0.1, c: 0, d: -5 },
      { a: 1, b: -3, c: 0, d: -1 },
    ]
    for (const { a, b, c, d } of cases) {
      const r = solveCubicLaunchRadius(a, b, c, d)
      const residual = a * r ** 3 + b * r ** 2 + c * r + d
      expect(Math.abs(residual)).toBeLessThan(1e-6)
      expect(r).toBeGreaterThan(0)
    }
  })

  it('throws when no positive root reachable', () => {
    // a<0 だと正方向で発散しない → 探索失敗
    expect(() => solveCubicLaunchRadius(-1, 0, 0, -1)).toThrow(
      BalloonPhysicsError,
    )
  })
})

describe('input validation', () => {
  it('rejects unknown balloon model', () => {
    expect(() =>
      computeBalloon({
        payloadMassG: 100,
        balloonModel: 'nope',
        gas: 'helium',
        target: { kind: 'burstAltitude', value: 30000 },
      }),
    ).toThrow(BalloonPhysicsError)
  })

  it('rejects unreachable configuration (too heavy payload)', () => {
    expect(() =>
      computeBalloon({
        payloadMassG: 50000,
        balloonModel: 'k50',
        gas: 'helium',
        target: { kind: 'burstAltitude', value: 30000 },
      }),
    ).toThrow(BalloonPhysicsError)
  })
})
