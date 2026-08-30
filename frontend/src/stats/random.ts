// シード可能なPRNG + 分布サンプラー
// mulberry32: 高速・十分な品質の32bit PRNG (再現性のため)

export type Rng = () => number

export function mulberry32(seed: number): Rng {
  let a = seed >>> 0
  return () => {
    a |= 0
    a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

/** Box-Muller法による正規分布サンプル */
export function gaussian(rng: Rng, mean = 0, stdDev = 1): number {
  let u = 0
  let v = 0
  while (u === 0) u = rng()
  while (v === 0) v = rng()
  const z = Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v)
  return z * stdDev + mean
}

/** 逆CDF法によるWeibull分布サンプル (旧実装と同形: scale * (-ln u)^(1/shape)) */
export function weibull(rng: Rng, shape: number, scale: number): number {
  let u = 0
  while (u === 0) u = rng()
  return scale * Math.pow(-Math.log(u), 1 / shape)
}
