import { afterEach, describe, expect, it } from 'vitest'
import { isOnLand, pointInRing, setLandData } from './landSea'
import { scoreLanding } from './objectives'

// 単位正方形 (0,0)-(1,1) の陸地
const squareLand = {
  features: [
    {
      geometry: {
        type: 'MultiPolygon' as const,
        coordinates: [
          [
            [
              [0, 0],
              [1, 0],
              [1, 1],
              [0, 1],
              [0, 0],
            ],
          ],
        ],
      },
    },
  ],
}

afterEach(() => setLandData(null))

describe('pointInRing', () => {
  const ring = [
    [0, 0],
    [1, 0],
    [1, 1],
    [0, 1],
    [0, 0],
  ]
  it('inside', () => {
    expect(pointInRing(0.5, 0.5, ring)).toBe(true)
  })
  it('outside', () => {
    expect(pointInRing(1.5, 0.5, ring)).toBe(false)
    expect(pointInRing(0.5, -0.1, ring)).toBe(false)
  })
})

describe('isOnLand', () => {
  it('respects injected land polygons', () => {
    setLandData(squareLand)
    expect(isOnLand(0.5, 0.5)).toBe(true) // lat, lon
    expect(isOnLand(2, 2)).toBe(false)
  })

  it('holes are sea', () => {
    setLandData({
      features: [
        {
          geometry: {
            type: 'MultiPolygon',
            coordinates: [
              [
                [
                  [0, 0],
                  [10, 0],
                  [10, 10],
                  [0, 10],
                  [0, 0],
                ],
                [
                  [4, 4],
                  [6, 4],
                  [6, 6],
                  [4, 6],
                  [4, 4],
                ],
              ],
            ],
          },
        },
      ],
    })
    expect(isOnLand(2, 2)).toBe(true)
    expect(isOnLand(5, 5)).toBe(false) // 穴の中は海
  })

  it('unloaded data means sea (safe side)', () => {
    expect(isOnLand(0.5, 0.5)).toBe(false)
  })
})

describe('scoreLanding', () => {
  it('sea landing penalized vs land landing', () => {
    setLandData(squareLand)
    const launch = { lat: 0.5, lon: 0.5 }
    const landScore = scoreLanding({ lat: 0.6, lon: 0.6 }, launch, {
      kind: 'avoidSea',
      seaPenaltyKm: 1000,
    })
    const seaScore = scoreLanding({ lat: 5, lon: 5 }, launch, {
      kind: 'avoidSea',
      seaPenaltyKm: 1000,
    })
    expect(landScore.onLand).toBe(true)
    expect(seaScore.onLand).toBe(false)
    expect(seaScore.score).toBeGreaterThan(landScore.score + 900)
  })

  it('minDistance measures to target', () => {
    setLandData(squareLand)
    const s = scoreLanding(
      { lat: 0.5, lon: 0.5 },
      { lat: 0, lon: 0 },
      { kind: 'minDistance', target: { lat: 0.5, lon: 0.5 } },
    )
    expect(s.distanceKm).toBeCloseTo(0, 3)
    expect(s.score).toBeCloseTo(0, 3)
  })
})
