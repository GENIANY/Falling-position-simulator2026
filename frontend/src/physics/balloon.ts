// legacy js/calc/calc.js のバルーンサイジング計算の移植。
// 修正点:
//  - 三次方程式ソルバーの未定義変数バグ (K/k) と g係数の括弧ミスを、
//    汎用の実根探索 (二分法) に置き換えて根本解消
//  - alert() の代わりに正の最小実根を返す

import {
  AIR_DENSITY_SL,
  ATMOSPHERE_SCALE_HEIGHT,
  GAS_DENSITY,
  GRAVITY,
} from './constants'
import type { GasType } from './constants'
import { BALLOON_SPECS } from './balloonData'

export interface BalloonInputs {
  payloadMassG: number
  balloonModel: string // BALLOON_SPECSのキー
  gas: GasType
  target:
    | { kind: 'ascentRate'; value: number } // m/s
    | { kind: 'burstAltitude'; value: number } // m
  /** 上書き可能な定数 (既定はlegacyと同一) */
  airDensity?: number
  scaleHeight?: number
  gravity?: number
  burstDiameterM?: number
  dragCoefficient?: number
}

export interface BalloonResult {
  ascentRate: number // m/s
  burstAltitude: number // m
  timeToBurstMin: number
  neckLiftG: number
  launchVolumeM3: number
  launchRadiusM: number
}

export class BalloonPhysicsError extends Error {}

/**
 * 三次方程式 a*r^3 + b*r^2 + c*r + d = 0 の正の実根 (最小) を二分法で求める。
 * バルーン問題では a>0, d<0 のため正の実根が必ず1つ以上存在する。
 */
export function solveCubicLaunchRadius(
  a: number,
  b: number,
  c: number,
  d: number,
): number {
  const f = (r: number) => ((a * r + b) * r + c) * r + d
  // 上限を指数的に拡大して符号反転区間を探す
  let hi = 1
  let iterations = 0
  while (f(hi) < 0 && iterations < 60) {
    hi *= 2
    iterations++
  }
  if (f(hi) < 0) {
    throw new BalloonPhysicsError('物理的に妥当な打ち上げ半径が見つかりません')
  }
  let lo = 0
  for (let i = 0; i < 100; i++) {
    const mid = (lo + hi) / 2
    if (f(mid) < 0) lo = mid
    else hi = mid
  }
  return (lo + hi) / 2
}

export function computeBalloon(inputs: BalloonInputs): BalloonResult {
  const spec = BALLOON_SPECS[inputs.balloonModel]
  if (!spec) {
    throw new BalloonPhysicsError(`不明なバルーン型番: ${inputs.balloonModel}`)
  }
  const rhoA = inputs.airDensity ?? AIR_DENSITY_SL
  const rhoG = GAS_DENSITY[inputs.gas]
  const adm = inputs.scaleHeight ?? ATMOSPHERE_SCALE_HEIGHT
  const g = inputs.gravity ?? GRAVITY
  const bd = inputs.burstDiameterM ?? spec.burstDiameterM
  const cd = inputs.dragCoefficient ?? spec.dragCoefficient
  const mb = spec.massKg
  const mp = inputs.payloadMassG / 1000

  const burstVolume = (4 / 3) * Math.PI * Math.pow(bd / 2, 3)

  let launchRadius: number
  if (inputs.target.kind === 'burstAltitude') {
    const launchVolume = burstVolume * Math.exp(-inputs.target.value / adm)
    launchRadius = Math.pow((3 * launchVolume) / (4 * Math.PI), 1 / 3)
  } else {
    // 浮力・抗力・重力のつり合い:
    //   g*(ρa-ρg)*(4/3)πr^3 - 0.5*v^2*cd*ρa*πr^2 - (mp+mb)*g = 0
    const tar = inputs.target.value
    const a = g * (rhoA - rhoG) * (4 / 3) * Math.PI
    const b = -0.5 * tar * tar * cd * rhoA * Math.PI
    const c = 0
    const d = -(mp + mb) * g
    launchRadius = solveCubicLaunchRadius(a, b, c, d)
  }

  const launchArea = Math.PI * launchRadius * launchRadius
  const launchVolume = (4 / 3) * Math.PI * Math.pow(launchRadius, 3)
  const grossLift = launchVolume * (rhoA - rhoG)
  const neckLiftG = (grossLift - mb) * 1000
  const freeLift = (grossLift - (mp + mb)) * g
  if (freeLift <= 0) {
    throw new BalloonPhysicsError(
      'この構成では浮力が不足しています (ペイロードが重すぎるかガスが少なすぎます)',
    )
  }
  const ascentRate = Math.sqrt(freeLift / (0.5 * cd * launchArea * rhoA))
  const burstAltitude = -adm * Math.log(launchVolume / burstVolume)
  if (!Number.isFinite(ascentRate) || burstAltitude <= 0) {
    throw new BalloonPhysicsError('この構成では目標高度に到達できません')
  }
  const timeToBurstMin = burstAltitude / ascentRate / 60

  return {
    ascentRate,
    burstAltitude,
    timeToBurstMin,
    neckLiftG,
    launchVolumeM3: launchVolume,
    launchRadiusM: launchRadius,
  }
}
