import type { TawhiriRequest, TrajectoryPoint, Flight } from '../api/tawhiriTypes'

export interface MCSigma {
  ascentRate: number // m/s
  burstAltitudePct: number // 中心値に対する%
  descentRate: number // m/s
}

export interface MCConfig {
  base: TawhiriRequest & { profile: 'standard_profile' }
  samples: number // 上限500
  sigma: MCSigma
  burstModel: 'gaussian' | 'weibull' // weibull: shape=3.0, バースト高度のみ摂動
  seed: number
}

export interface MCPerturbation {
  ascentRate: number
  burstAltitude: number
  descentRate: number
}

export type MCWorkerMsg =
  | { type: 'run'; config: MCConfig; indices: number[]; concurrency: number }
  | { type: 'cancel' }

export type MCWorkerReply =
  | {
      type: 'sample'
      index: number
      flight: Flight
      perturbed: MCPerturbation
    }
  | { type: 'error'; index: number; message: string }
  | { type: 'done' }

export type { TrajectoryPoint }
