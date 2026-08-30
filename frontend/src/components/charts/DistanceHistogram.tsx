import Plot from 'react-plotly.js'
import type { Data } from 'plotly.js'
import { useResultsStore } from '../../store/resultsStore'
import { haversineM } from '../../stats/landing'
import { BASE_CONFIG, BASE_LAYOUT } from './plotlyDefaults'

export function DistanceHistogram() {
  const mcSamples = useResultsStore((s) => s.mcSamples)
  const mcStats = useResultsStore((s) => s.mcStats)
  if (!mcStats) return null

  const distancesKm = mcSamples.map(
    (s) =>
      haversineM(
        { lat: s.flight.landing.latitude, lon: s.flight.landing.longitude },
        mcStats.mean,
      ) / 1000,
  )

  return (
    <Plot
      data={[
        {
          x: distancesKm,
          type: 'histogram',
          nbinsx: 25,
          marker: { color: '#5c6bc0' },
        } as Data,
      ]}
      layout={{
        ...BASE_LAYOUT,
        title: { text: '平均着地点からの距離分布' },
        xaxis: { title: { text: '距離 [km]' } },
        yaxis: { title: { text: '件数' } },
      }}
      config={BASE_CONFIG}
      style={{ width: '100%' }}
    />
  )
}
