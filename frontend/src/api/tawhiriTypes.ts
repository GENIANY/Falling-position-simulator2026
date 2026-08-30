// Tawhiri API (https://tawhiri.readthedocs.io/en/latest/api.html)
// SondeHub hosted instance: https://api.v2.sondehub.org/tawhiri

export interface TawhiriRequestBase {
  launch_latitude: number // -90..90
  launch_longitude: number // 0..360 (convert with toTawhiriLon before send)
  launch_altitude: number // m
  launch_datetime: string // ISO 8601 UTC
  ascent_rate: number // m/s
}

export type TawhiriRequest = TawhiriRequestBase &
  (
    | {
        profile: 'standard_profile'
        burst_altitude: number
        descent_rate: number
      }
    | {
        profile: 'float_profile'
        float_altitude: number
        stop_datetime: string
      }
  )

export interface TrajectoryPoint {
  latitude: number
  longitude: number // normalized to -180..180 after parsing
  altitude: number
  datetime: string // ISO 8601 UTC
}

export interface TawhiriStage {
  stage: 'ascent' | 'descent' | 'float'
  trajectory: TrajectoryPoint[]
}

export interface TawhiriResponse {
  request: Record<string, unknown>
  prediction: TawhiriStage[]
  metadata: {
    start_datetime: string
    complete_datetime: string
  }
}

/** Normalized flight result used across the app. */
export interface Flight {
  ascent: TrajectoryPoint[]
  descent: TrajectoryPoint[]
  launch: TrajectoryPoint
  burst: TrajectoryPoint | null // null for float profiles
  landing: TrajectoryPoint
  flightTimeS: number
}

export class TawhiriError extends Error {
  readonly status?: number

  constructor(message: string, status?: number) {
    super(message)
    this.name = 'TawhiriError'
    this.status = status
  }
}
