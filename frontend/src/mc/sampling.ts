// パラメータ摂動の生成ロジック (Worker非依存・テスト可能)

import { gaussian, mulberry32, weibull } from '../stats/random'
import type { MCConfig, MCPerturbation } from './mcTypes'

export const WEIBULL_SHAPE = 3.0

/**
 * sample index に対する摂動を決定的に生成する。
 * seed + index からPRNGを作るため、worker分割に依存せず同じ結果になる。
 */
export function perturbationForIndex(
  config: MCConfig,
  index: number,
): MCPerturbation {
  const rng = mulberry32(config.seed * 0x9e3779b9 + index)
  const base = config.base
  if (config.burstModel === 'weibull') {
    return {
      ascentRate: base.ascent_rate,
      burstAltitude: weibull(rng, WEIBULL_SHAPE, base.burst_altitude),
      descentRate: base.descent_rate,
    }
  }
  const burstStd = (base.burst_altitude * config.sigma.burstAltitudePct) / 100
  return {
    ascentRate: Math.max(
      0.1,
      gaussian(rng, base.ascent_rate, config.sigma.ascentRate),
    ),
    burstAltitude: Math.max(
      1000,
      gaussian(rng, base.burst_altitude, burstStd),
    ),
    descentRate: Math.max(
      0.5,
      gaussian(rng, base.descent_rate, config.sigma.descentRate),
    ),
  }
}

/** 摂動をTawhiriリクエストに適用 */
export function requestForPerturbation(
  config: MCConfig,
  p: MCPerturbation,
): MCConfig['base'] {
  return {
    ...config.base,
    ascent_rate: p.ascentRate,
    burst_altitude: p.burstAltitude,
    descent_rate: p.descentRate,
  }
}

/** worker数に応じてサンプルindexを分割 */
export function partitionIndices(total: number, parts: number): number[][] {
  const result: number[][] = Array.from({ length: parts }, () => [])
  for (let i = 0; i < total; i++) {
    result[i % parts].push(i)
  }
  return result.filter((arr) => arr.length > 0)
}
