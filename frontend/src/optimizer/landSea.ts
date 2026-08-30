// 陸/海判定: Natural Earth 50m陸地ポリゴン (西日本bboxクリップ済み) に対する
// point-in-polygon (ray casting)。データは public/geo/land.json。

export interface MultiPolygonFeature {
  geometry: { type: 'MultiPolygon'; coordinates: number[][][][] }
}

export interface LandData {
  features: MultiPolygonFeature[]
}

let landData: LandData | null = null

export async function loadLandData(baseUrl = ''): Promise<LandData> {
  if (landData) return landData
  const res = await fetch(`${baseUrl}geo/land.json`)
  landData = (await res.json()) as LandData
  return landData
}

/** テスト用: データを直接注入 */
export function setLandData(data: LandData | null): void {
  landData = data
}

export function pointInRing(
  lon: number,
  lat: number,
  ring: number[][],
): boolean {
  let inside = false
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i]
    const [xj, yj] = ring[j]
    if (
      yi > lat !== yj > lat &&
      lon < ((xj - xi) * (lat - yi)) / (yj - yi) + xi
    ) {
      inside = !inside
    }
  }
  return inside
}

/** 陸上ならtrue。データ未ロード時はfalse (安全側=海扱い) */
export function isOnLand(lat: number, lon: number): boolean {
  if (!landData) return false
  for (const f of landData.features) {
    for (const polygon of f.geometry.coordinates) {
      // polygon[0] = 外環, polygon[1..] = 穴
      if (pointInRing(lon, lat, polygon[0])) {
        let inHole = false
        for (let h = 1; h < polygon.length; h++) {
          if (pointInRing(lon, lat, polygon[h])) {
            inHole = true
            break
          }
        }
        if (!inHole) return true
      }
    }
  }
  return false
}
