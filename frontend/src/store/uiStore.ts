import { create } from 'zustand'

export interface UiState {
  mapMode: '2d' | '3d'
  showHeatmap: boolean
  showCharts: boolean
  showCalc: boolean
  showOptimizer: boolean
  showSafetyZones: boolean
  set: (partial: Partial<UiState>) => void
}

export const useUiStore = create<UiState>((set) => ({
  mapMode: '2d',
  showHeatmap: true,
  showCharts: false,
  showCalc: false,
  showOptimizer: false,
  showSafetyZones: false,
  set: (partial) => set(partial),
}))
