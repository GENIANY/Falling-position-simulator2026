// 着地点群の統計処理: 平均・共分散・信頼楕円
// 局所ENU (メートル) 平面に投影して2x2共分散を固有分解する。

export interface LatLon {
  lat: number
  lon: number
}

export interface ConfidenceEllipse {
  semiMajorM: number
  semiMinorM: number
  /** 東基準・反時計回りの長軸角度 [deg] */
  angleDeg: number
  probability: number
}

export interface LandingStats {
  mean: LatLon
  /** 局所ENUメートル系での2x2共分散 [[xx,xy],[xy,yy]] */
  covariance: [[number, number], [number, number]]
  ellipses: ConfidenceEllipse[]
  /** 平均点からの距離パーセンタイル [m] */
  percentileRadiiM: Record<number, number>
}

const M_PER_DEG_LAT = 110574
const M_PER_DEG_LON_EQ = 111320

export function toLocalMeters(points: LatLon[], origin: LatLon): [number, number][] {
  const cosLat = Math.cos((origin.lat * Math.PI) / 180)
  return points.map((p) => [
    (p.lon - origin.lon) * M_PER_DEG_LON_EQ * cosLat,
    (p.lat - origin.lat) * M_PER_DEG_LAT,
  ])
}

export function metersToLatLon(xy: [number, number], origin: LatLon): LatLon {
  const cosLat = Math.cos((origin.lat * Math.PI) / 180)
  return {
    lat: origin.lat + xy[1] / M_PER_DEG_LAT,
    lon: origin.lon + xy[0] / (M_PER_DEG_LON_EQ * cosLat),
  }
}

export function haversineM(a: LatLon, b: LatLon): number {
  const R = 6371000
  const dLat = ((b.lat - a.lat) * Math.PI) / 180
  const dLon = ((b.lon - a.lon) * Math.PI) / 180
  const la1 = (a.lat * Math.PI) / 180
  const la2 = (b.lat * Math.PI) / 180
  const h =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(la1) * Math.cos(la2) * Math.sin(dLon / 2) ** 2
  return 2 * R * Math.asin(Math.sqrt(h))
}

export function computeLandingStats(
  points: LatLon[],
  probs: number[] = [0.5, 0.9, 0.95],
): LandingStats {
  if (points.length === 0) {
    throw new Error('no landing points')
  }
  const mean: LatLon = {
    lat: points.reduce((s, p) => s + p.lat, 0) / points.length,
    lon: points.reduce((s, p) => s + p.lon, 0) / points.length,
  }
  const xy = toLocalMeters(points, mean)
  const n = xy.length
  let sxx = 0
  let syy = 0
  let sxy = 0
  for (const [x, y] of xy) {
    sxx += x * x
    syy += y * y
    sxy += x * y
  }
  const denom = Math.max(n - 1, 1)
  sxx /= denom
  syy /= denom
  sxy /= denom

  // 2x2対称行列の固有分解 (閉形式)
  const trace = sxx + syy
  const det = sxx * syy - sxy * sxy
  const disc = Math.sqrt(Math.max((trace / 2) ** 2 - det, 0))
  const l1 = trace / 2 + disc // 大きい固有値
  const l2 = trace / 2 - disc
  const angleRad = Math.abs(sxy) < 1e-12 && sxx >= syy ? 0 : Math.atan2(l1 - sxx, sxy)

  const ellipses: ConfidenceEllipse[] = probs.map((p) => {
    // 2自由度カイ二乗: k = sqrt(-2 ln(1-p))
    const k = Math.sqrt(-2 * Math.log(1 - p))
    return {
      semiMajorM: k * Math.sqrt(Math.max(l1, 0)),
      semiMinorM: k * Math.sqrt(Math.max(l2, 0)),
      angleDeg: (angleRad * 180) / Math.PI,
      probability: p,
    }
  })

  const dists = points.map((p) => haversineM(p, mean)).sort((a, b) => a - b)
  const percentileRadiiM: Record<number, number> = {}
  for (const q of [50, 90, 95]) {
    const idx = Math.min(
      dists.length - 1,
      Math.floor((q / 100) * dists.length),
    )
    percentileRadiiM[q] = dists[idx]
  }

  return {
    mean,
    covariance: [
      [sxx, sxy],
      [sxy, syy],
    ],
    ellipses,
    percentileRadiiM,
  }
}

/** 信頼楕円をLeafletポリゴン用のlat/lng点列に変換 */
export function ellipseToLatLngs(
  center: LatLon,
  e: ConfidenceEllipse,
  nPoints = 64,
): [number, number][] {
  const angleRad = (e.angleDeg * Math.PI) / 180
  const cosA = Math.cos(angleRad)
  const sinA = Math.sin(angleRad)
  const pts: [number, number][] = []
  for (let i = 0; i < nPoints; i++) {
    const t = (2 * Math.PI * i) / nPoints
    const x0 = e.semiMajorM * Math.cos(t)
    const y0 = e.semiMinorM * Math.sin(t)
    const x = x0 * cosA - y0 * sinA
    const y = x0 * sinA + y0 * cosA
    const ll = metersToLatLon([x, y], center)
    pts.push([ll.lat, ll.lon])
  }
  return pts
}
