import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { setLandData } from '../optimizer/landSea'
import { scoreLanding, CATEGORY_PENALTY_KM } from '../optimizer/objectives'
import { classify, setSafetyData } from './landingSafety'
import { clearElevationCache, fetchElevations } from './elevation'

// 北海道全域をカバーする矩形陸地 (テスト用: 139-146E, 41-46N)
const hokkaidoLand = {
  features: [
    {
      geometry: {
        type: 'MultiPolygon' as const,
        coordinates: [
          [
            [
              [139, 41],
              [146, 41],
              [146, 46],
              [139, 46],
              [139, 41],
            ],
          ],
        ],
      },
    },
  ],
}

const testTowns = [
  { name: '帯広', lat: 42.9236, lon: 143.1966, radiusM: 5000, kind: 'city' },
]
const testRestricted = [
  {
    name: '新千歳空港',
    lat: 42.7752,
    lon: 141.6923,
    radiusM: 7000,
    kind: 'airport',
  },
]

beforeEach(() => {
  setLandData(hokkaidoLand)
  setSafetyData(testTowns, testRestricted)
})

afterEach(() => {
  setLandData(null)
  setSafetyData(null, null)
  vi.unstubAllGlobals()
  clearElevationCache()
})

describe('classify', () => {
  it('sea: 陸地ポリゴン外', () => {
    expect(classify(41.5, 148.0, 10)).toBe('sea') // 太平洋沖
  })

  it('restricted: 新千歳空港近傍', () => {
    expect(classify(42.78, 141.69, 20)).toBe('restricted')
  })

  it('residential: 帯広市街', () => {
    expect(classify(42.9236, 143.1966, 40)).toBe('residential')
  })

  it('mountain: 標高閾値超え', () => {
    expect(classify(43.3, 142.9, 1200)).toBe('mountain')
  })

  it('mountain閾値はオプションで変更可能', () => {
    expect(classify(43.3, 142.9, 450, { mountainElevationM: 400 })).toBe(
      'mountain',
    )
    expect(classify(43.3, 142.9, 450, { mountainElevationM: 500 })).toBe(
      'safe',
    )
  })

  it('safe: 十勝平野の農地相当', () => {
    expect(classify(42.65, 143.2, 75)).toBe('safe')
  })

  it('標高null時は山判定スキップ', () => {
    expect(classify(43.3, 142.9, null)).toBe('safe')
  })

  it('優先順: restrictedはresidentialより先', () => {
    // 空港円内かつ町円内の点を作る
    setSafetyData(
      [{ name: 'x', lat: 42.775, lon: 141.69, radiusM: 10000, kind: 'city' }],
      testRestricted,
    )
    expect(classify(42.78, 141.69, 10)).toBe('restricted')
  })
})

describe('scoreLanding safeLanding', () => {
  const launch = { lat: 42.5, lon: 143.44 }

  it('ペナルティ順: restricted > sea ≈ residential > mountain > safe', () => {
    const safe = scoreLanding({ lat: 42.65, lon: 143.2 }, launch, {
      kind: 'safeLanding',
    }, 75)
    const mountain = scoreLanding({ lat: 43.3, lon: 142.9 }, launch, {
      kind: 'safeLanding',
    }, 1200)
    const residential = scoreLanding({ lat: 42.9236, lon: 143.1966 }, launch, {
      kind: 'safeLanding',
    }, 40)
    const sea = scoreLanding({ lat: 41.5, lon: 148.0 }, launch, {
      kind: 'safeLanding',
    }, 0)
    const restricted = scoreLanding({ lat: 42.78, lon: 141.69 }, launch, {
      kind: 'safeLanding',
    }, 20)

    expect(safe.category).toBe('safe')
    expect(mountain.category).toBe('mountain')
    expect(residential.category).toBe('residential')
    expect(sea.category).toBe('sea')
    expect(restricted.category).toBe('restricted')

    expect(safe.score).toBeLessThan(mountain.score)
    expect(mountain.score).toBeLessThan(residential.score)
    expect(residential.score).toBeLessThan(restricted.score)
  })

  it('ペナルティ定数の順序', () => {
    expect(CATEGORY_PENALTY_KM.safe).toBe(0)
    expect(CATEGORY_PENALTY_KM.mountain).toBeLessThan(
      CATEGORY_PENALTY_KM.residential,
    )
    expect(CATEGORY_PENALTY_KM.residential).toBeLessThan(
      CATEGORY_PENALTY_KM.restricted,
    )
  })
})

describe('fetchElevations', () => {
  it('batches 150 points into 2 requests and caches', async () => {
    const calls: string[] = []
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string) => {
        calls.push(url)
        const n = url.split('latitude=')[1].split('&')[0].split(',').length
        return new Response(
          JSON.stringify({ elevation: Array.from({ length: n }, () => 123) }),
          { status: 200 },
        )
      }),
    )
    const points = Array.from({ length: 150 }, (_, i) => ({
      lat: 42 + i * 0.01,
      lon: 143 + i * 0.01,
    }))
    const result = await fetchElevations(points)
    expect(calls).toHaveLength(2)
    expect(result.every((e) => e === 123)).toBe(true)

    // 2回目はキャッシュヒットでリクエストなし
    const again = await fetchElevations(points.slice(0, 50))
    expect(calls).toHaveLength(2)
    expect(again.every((e) => e === 123)).toBe(true)
  })

  it('fetch失敗時はnull', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => new Response('err', { status: 500 })),
    )
    const result = await fetchElevations([{ lat: 42, lon: 143 }])
    expect(result).toEqual([null])
  })
})
