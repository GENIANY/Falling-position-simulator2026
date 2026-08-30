import type {
  Flight,
  TawhiriRequest,
  TawhiriResponse,
  TrajectoryPoint,
} from './tawhiriTypes'
import { TawhiriError } from './tawhiriTypes'

export const TAWHIRI_URL = 'https://api.v2.sondehub.org/tawhiri'

/** 0..360 -> -180..180 */
export function normalizeLon(lon: number): number {
  return lon > 180 ? lon - 360 : lon
}

/** -180..180 -> 0..360 (Tawhiri wants 0..360) */
export function toTawhiriLon(lon: number): number {
  return lon < 0 ? lon + 360 : lon
}

function normalizePoint(p: TrajectoryPoint): TrajectoryPoint {
  return { ...p, longitude: normalizeLon(p.longitude) }
}

export function parseFlight(res: TawhiriResponse): Flight {
  const stages = res.prediction
  const ascentStage = stages.find((s) => s.stage === 'ascent')
  const secondStage = stages.find((s) => s.stage !== 'ascent')
  if (!ascentStage || !secondStage) {
    throw new TawhiriError('Unexpected Tawhiri response: missing stages')
  }
  const ascent = ascentStage.trajectory.map(normalizePoint)
  const descent = secondStage.trajectory.map(normalizePoint)
  const launch = ascent[0]
  const landing = descent[descent.length - 1]
  const burst =
    secondStage.stage === 'descent' ? ascent[ascent.length - 1] : null
  const flightTimeS =
    (Date.parse(landing.datetime) - Date.parse(launch.datetime)) / 1000
  return { ascent, descent, launch, burst, landing, flightTimeS }
}

export interface RequestOptions {
  signal?: AbortSignal
  retries?: number
  baseUrl?: string
}

const RETRY_DELAYS_MS = [1000, 3000]

function sleep(ms: number, signal?: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    const t = setTimeout(resolve, ms)
    signal?.addEventListener('abort', () => {
      clearTimeout(t)
      reject(new DOMException('Aborted', 'AbortError'))
    })
  })
}

export async function requestPrediction(
  req: TawhiriRequest,
  opts: RequestOptions = {},
): Promise<Flight> {
  const { signal, retries = 2, baseUrl = TAWHIRI_URL } = opts
  const params = new URLSearchParams()
  for (const [k, v] of Object.entries(req)) {
    params.set(k, String(v))
  }
  params.set('launch_longitude', String(toTawhiriLon(req.launch_longitude)))
  const url = `${baseUrl}?${params.toString()}`

  let lastError: unknown
  for (let attempt = 0; attempt <= retries; attempt++) {
    if (attempt > 0) {
      await sleep(RETRY_DELAYS_MS[attempt - 1] ?? 3000, signal)
    }
    try {
      const res = await fetch(url, { signal })
      if (res.status >= 500) {
        lastError = new TawhiriError(`Tawhiri server error ${res.status}`, res.status)
        continue // retry
      }
      if (!res.ok) {
        // 4xx: do not retry — usually out-of-dataset-window or bad params
        let detail = ''
        try {
          const body = (await res.json()) as {
            error?: { description?: string }
          }
          detail = body.error?.description ?? ''
        } catch {
          /* ignore body parse failure */
        }
        throw new TawhiriError(
          `Tawhiri rejected request (${res.status}): ${detail}`,
          res.status,
        )
      }
      const body = (await res.json()) as TawhiriResponse
      return parseFlight(body)
    } catch (e) {
      if (e instanceof TawhiriError && e.status && e.status < 500) throw e
      if (e instanceof DOMException && e.name === 'AbortError') throw e
      lastError = e
    }
  }
  throw lastError instanceof Error
    ? lastError
    : new TawhiriError('Tawhiri request failed')
}

/** Export URLs for Tawhiri-generated KML/CSV downloads. */
export function exportUrls(req: TawhiriRequest): { csv: string; kml: string } {
  const params = new URLSearchParams()
  for (const [k, v] of Object.entries(req)) params.set(k, String(v))
  params.set('launch_longitude', String(toTawhiriLon(req.launch_longitude)))
  const base = `${TAWHIRI_URL}?${params.toString()}`
  return { csv: `${base}&format=csv`, kml: `${base}&format=kml` }
}
