import { useEffect } from 'react'
import { useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet.heat'
import { useResultsStore } from '../../store/resultsStore'
import { useUiStore } from '../../store/uiStore'

// leaflet.heat はL.heatLayerをグローバル追加する (型定義なし)
type HeatLayerFactory = (
  points: [number, number, number][],
  options?: Record<string, unknown>,
) => L.Layer

export function HeatmapLayer() {
  const map = useMap()
  const mcSamples = useResultsStore((s) => s.mcSamples)
  const showHeatmap = useUiStore((s) => s.showHeatmap)

  useEffect(() => {
    if (!showHeatmap || mcSamples.length < 5) return
    const heatLayer = (
      L as unknown as { heatLayer: HeatLayerFactory }
    ).heatLayer(
      mcSamples.map((s) => [
        s.flight.landing.latitude,
        s.flight.landing.longitude,
        1,
      ]),
      { radius: 25, blur: 20 },
    )
    heatLayer.addTo(map)
    return () => {
      map.removeLayer(heatLayer)
    }
  }, [map, mcSamples, showHeatmap])

  return null
}
