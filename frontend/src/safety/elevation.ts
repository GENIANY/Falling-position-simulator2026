// Open-Meteo Elevation API クライアント (バッチ最大100点/リクエスト、キャッシュ付き)

export const ELEVATION_API = 'https://api.open-meteo.com/v1/elevation'
const BATCH_SIZE = 100

const cache = new Map<string, number>()

function key(lat: number, lon: number): string {
  // ~110m解像度でキャッシュ (APIの解像度は90m)
  return `${lat.toFixed(3)},${lon.toFixed(3)}`
}

export function clearElevationCache(): void {
  cache.clear()
}

/**
 * 複数地点の標高 [m] を一括取得。結果は入力順の配列。
 * 取得失敗時は該当要素が null (呼び出し側は山判定スキップ)。
 */
export async function fetchElevations(
  points: { lat: number; lon: number }[],
  baseUrl = ELEVATION_API,
): Promise<(number | null)[]> {
  const result: (number | null)[] = new Array(points.length).fill(null)
  const missing: number[] = []

  points.forEach((p, i) => {
    const cached = cache.get(key(p.lat, p.lon))
    if (cached !== undefined) {
      result[i] = cached
    } else {
      missing.push(i)
    }
  })

  for (let start = 0; start < missing.length; start += BATCH_SIZE) {
    const batch = missing.slice(start, start + BATCH_SIZE)
    const lats = batch.map((i) => points[i].lat.toFixed(5)).join(',')
    const lons = batch.map((i) => points[i].lon.toFixed(5)).join(',')
    try {
      const res = await fetch(`${baseUrl}?latitude=${lats}&longitude=${lons}`)
      if (!res.ok) continue
      const body = (await res.json()) as { elevation: number[] }
      batch.forEach((pointIndex, j) => {
        const elev = body.elevation[j]
        if (typeof elev === 'number') {
          result[pointIndex] = elev
          cache.set(
            key(points[pointIndex].lat, points[pointIndex].lon),
            elev,
          )
        }
      })
    } catch {
      // ネットワーク失敗時はnullのまま (山判定スキップ)
    }
  }
  return result
}
