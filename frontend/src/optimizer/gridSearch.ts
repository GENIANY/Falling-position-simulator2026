// 発射地点 × ガス量(上昇率/バースト高度に変換) × 発射時刻 のグリッドサーチ。
// 300コールごとのバッチに分割し、バッチ間に3s休止を挟んで任意のセル数を実行できる。
// safeLanding目的関数の場合は全飛行完了後に標高をバッチ取得してから採点する。

import { jitterMs, tawhiriSemaphore } from '../api/semaphore'
import { requestPrediction } from '../api/tawhiri'
import type { TawhiriRequest, Flight } from '../api/tawhiriTypes'
import { computeBalloon } from '../physics/balloon'
import type { GasType } from '../physics/constants'
import { fetchElevations } from '../safety/elevation'
import { loadSafetyData } from '../safety/landingSafety'
import type { SafetyCategory } from '../safety/landingSafety'
import type { LaunchSite } from '../store/paramsStore'
import { loadLandData } from './landSea'
import { scoreLanding } from './objectives'
import type { ObjectiveConfig } from './objectives'

/** 1バッチあたりのTawhiriコール数。バッチ間に休止を挟んで無制限に実行できる */
export const OPTIMIZER_BATCH_SIZE = 300
/** バッチ間の休止 [ms] (無料APIへの配慮) */
export const OPTIMIZER_BATCH_PAUSE_MS = 3000

export interface GridSpec {
  sites: LaunchSite[]
  /** 試すバースト高度のリスト (ガス量スイープ) */
  burstAltitudes: number[]
  balloonModel: string
  payloadMassG: number
  gas: GasType
  /** 発射時刻候補 (UTC ISO) */
  launchTimesUtc: string[]
  descentRate: number
}

export interface GridCell {
  site: LaunchSite
  burstAltitude: number
  ascentRate: number
  launchVolumeM3: number
  launchTimeUtc: string
}

export interface GridResult extends GridCell {
  flight: Flight | null
  score: number
  onLand: boolean
  distanceKm: number | null
  category?: SafetyCategory
  elevationM?: number | null
  error?: string
}

export function enumerateCells(spec: GridSpec): GridCell[] {
  const cells: GridCell[] = []
  for (const site of spec.sites) {
    for (const burstAltitude of spec.burstAltitudes) {
      let ascentRate: number
      let launchVolumeM3: number
      try {
        const r = computeBalloon({
          payloadMassG: spec.payloadMassG,
          balloonModel: spec.balloonModel,
          gas: spec.gas,
          target: { kind: 'burstAltitude', value: burstAltitude },
        })
        ascentRate = r.ascentRate
        launchVolumeM3 = r.launchVolumeM3
      } catch {
        continue // 物理的に不可能な構成はスキップ
      }
      for (const launchTimeUtc of spec.launchTimesUtc) {
        cells.push({
          site,
          burstAltitude,
          ascentRate,
          launchVolumeM3,
          launchTimeUtc,
        })
      }
    }
  }
  return cells
}

export interface RunGridOptions {
  objective: ObjectiveConfig
  onProgress?: (done: number, total: number) => void
  signal?: AbortSignal
  baseUrl?: string
}

interface FlightOutcome extends GridCell {
  flight: Flight | null
  error?: string
}

export async function runGridSearch(
  spec: GridSpec,
  opts: RunGridOptions,
): Promise<GridResult[]> {
  const cells = enumerateCells(spec)
  const baseUrl = opts.baseUrl ?? import.meta.env.BASE_URL
  await loadLandData(baseUrl)
  if (opts.objective.kind === 'safeLanding') {
    await loadSafetyData(baseUrl)
  }

  // フェーズ1: 全セルの飛行予測。OPTIMIZER_BATCH_SIZEずつに分割し、
  // バッチ間にOPTIMIZER_BATCH_PAUSE_MS休止を挟むことで何セルでも実行可能。
  let done = 0
  const runCell = async (cell: GridCell): Promise<FlightOutcome> => {
    await new Promise((r) => setTimeout(r, jitterMs()))
    const req: TawhiriRequest = {
      profile: 'standard_profile',
      launch_latitude: cell.site.latitude,
      launch_longitude: cell.site.longitude,
      launch_altitude: cell.site.altitude,
      launch_datetime: cell.launchTimeUtc,
      ascent_rate: Number(cell.ascentRate.toFixed(2)),
      burst_altitude: Math.round(cell.burstAltitude),
      descent_rate: spec.descentRate,
    }
    try {
      const flight = await tawhiriSemaphore.run(() =>
        requestPrediction(req, { signal: opts.signal }),
      )
      return { ...cell, flight }
    } catch (e) {
      return {
        ...cell,
        flight: null,
        error: e instanceof Error ? e.message : String(e),
      }
    } finally {
      done++
      opts.onProgress?.(done, cells.length)
    }
  }

  const outcomes: FlightOutcome[] = []
  for (let start = 0; start < cells.length; start += OPTIMIZER_BATCH_SIZE) {
    if (opts.signal?.aborted) {
      throw new DOMException('Aborted', 'AbortError')
    }
    if (start > 0) {
      // バッチ間休止 (API配慮)
      await new Promise((r) => setTimeout(r, OPTIMIZER_BATCH_PAUSE_MS))
    }
    const batch = cells.slice(start, start + OPTIMIZER_BATCH_SIZE)
    const batchResults = await Promise.all(batch.map(runCell))
    outcomes.push(...batchResults)
  }

  // フェーズ2: safeLanding時は着地点の標高を一括取得
  let elevations: (number | null)[] = new Array(outcomes.length).fill(null)
  if (opts.objective.kind === 'safeLanding') {
    const landedIdx = outcomes
      .map((o, i) => (o.flight ? i : -1))
      .filter((i) => i >= 0)
    const elevs = await fetchElevations(
      landedIdx.map((i) => ({
        lat: outcomes[i].flight!.landing.latitude,
        lon: outcomes[i].flight!.landing.longitude,
      })),
    )
    landedIdx.forEach((originalIdx, j) => {
      elevations[originalIdx] = elevs[j]
    })
  }

  // フェーズ3: 採点
  const results: GridResult[] = outcomes.map((o, i) => {
    if (!o.flight) {
      return {
        ...o,
        score: Number.POSITIVE_INFINITY,
        onLand: false,
        distanceKm: null,
      }
    }
    const scored = scoreLanding(
      { lat: o.flight.landing.latitude, lon: o.flight.landing.longitude },
      { lat: o.site.latitude, lon: o.site.longitude },
      opts.objective,
      elevations[i],
    )
    return { ...o, ...scored, elevationM: elevations[i] }
  })

  return results.sort((a, b) => a.score - b.score)
}
