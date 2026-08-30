import { useCallback, useState } from 'react'
import { tawhiriSemaphore } from '../api/semaphore'
import { requestPrediction } from '../api/tawhiri'
import type { TawhiriRequest } from '../api/tawhiriTypes'
import { haversineM } from '../stats/landing'
import { buildBaseRequest } from './useRunPrediction'

export interface SensitivityResult {
  parameter: string
  /** -1σ側の着地変位 [km] */
  minusKm: number
  /** +1σ側の着地変位 [km] */
  plusKm: number
}

export interface SensitivitySigma {
  ascentRate: number
  burstAltitudePct: number
  descentRate: number
}

/** 各パラメータを±1σ動かした時の着地点変位を測る (One-at-a-time感度分析) */
export function useSensitivity() {
  const [results, setResults] = useState<SensitivityResult[] | null>(null)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const run = useCallback(async (sigma: SensitivitySigma) => {
    const base = buildBaseRequest()
    if (base.profile !== 'standard_profile') {
      setError('感度分析は標準プロファイルのみ対応です')
      return
    }
    setRunning(true)
    setError(null)
    try {
      const central = await tawhiriSemaphore.run(() => requestPrediction(base))
      const centralLanding = {
        lat: central.landing.latitude,
        lon: central.landing.longitude,
      }

      const variations: { parameter: string; mods: [Partial<TawhiriRequest>, Partial<TawhiriRequest>] }[] = [
        {
          parameter: '上昇速度',
          mods: [
            { ascent_rate: base.ascent_rate - sigma.ascentRate },
            { ascent_rate: base.ascent_rate + sigma.ascentRate },
          ],
        },
        {
          parameter: 'バースト高度',
          mods: [
            {
              burst_altitude:
                base.burst_altitude * (1 - sigma.burstAltitudePct / 100),
            },
            {
              burst_altitude:
                base.burst_altitude * (1 + sigma.burstAltitudePct / 100),
            },
          ],
        },
        {
          parameter: '降下速度',
          mods: [
            { descent_rate: Math.max(0.5, base.descent_rate - sigma.descentRate) },
            { descent_rate: base.descent_rate + sigma.descentRate },
          ],
        },
      ]

      const out: SensitivityResult[] = []
      for (const v of variations) {
        const [minus, plus] = await Promise.all(
          v.mods.map((mod) =>
            tawhiriSemaphore.run(() =>
              requestPrediction({ ...base, ...mod } as TawhiriRequest),
            ),
          ),
        )
        out.push({
          parameter: v.parameter,
          minusKm:
            haversineM(
              { lat: minus.landing.latitude, lon: minus.landing.longitude },
              centralLanding,
            ) / 1000,
          plusKm:
            haversineM(
              { lat: plus.landing.latitude, lon: plus.landing.longitude },
              centralLanding,
            ) / 1000,
        })
      }
      setResults(out)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setRunning(false)
    }
  }, [])

  return { results, running, error, run }
}
