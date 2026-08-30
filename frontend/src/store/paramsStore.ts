import { create } from 'zustand'
import { nowJstInputValue } from '../time/jst'

export type FlightProfile = 'standard_profile' | 'float_profile'
export type PredictionMode = 'single' | 'hourly' | 'montecarlo' | 'optimizer'

export interface LaunchSite {
  name: string
  latitude: number
  longitude: number
  altitude: number
}

export interface ParamsState {
  latitude: number
  longitude: number
  launchAltitude: number
  /** datetime-local形式のJST文字列 */
  launchTimeJst: string
  ascentRate: number
  burstAltitude: number // float時はfloat_altitudeとして扱う
  descentRate: number
  profile: FlightProfile
  mode: PredictionMode
  hourlyStepH: number
  hourlyDurationH: number
  sites: LaunchSite[]
  set: (partial: Partial<ParamsState>) => void
  applySite: (site: LaunchSite) => void
  setSites: (sites: LaunchSite[]) => void
}

export const useParamsStore = create<ParamsState>((set) => ({
  latitude: 42.50097,
  longitude: 143.4405,
  launchAltitude: 8,
  launchTimeJst: nowJstInputValue(),
  ascentRate: 5.0,
  burstAltitude: 30000,
  descentRate: 5.0,
  profile: 'standard_profile',
  mode: 'single',
  hourlyStepH: 3,
  hourlyDurationH: 48,
  sites: [],
  set: (partial) => set(partial),
  applySite: (site) =>
    set({
      latitude: site.latitude,
      longitude: site.longitude,
      launchAltitude: site.altitude,
    }),
  setSites: (sites) => set({ sites }),
}))
