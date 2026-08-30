import Plot from 'react-plotly.js'
import type { Data } from 'plotly.js'
import { useResultsStore } from '../../store/resultsStore'
import { BASE_CONFIG, BASE_LAYOUT } from './plotlyDefaults'

export function LandingScatter() {
  const mcSamples = useResultsStore((s) => s.mcSamples)
  const mcStats = useResultsStore((s) => s.mcStats)

  const lons = mcSamples.map((s) => s.flight.landing.longitude)
  const lats = mcSamples.map((s) => s.flight.landing.latitude)
  const bursts = mcSamples.map((s) => s.perturbed.burstAltitude)

  const traces: Data[] = [
    {
      x: lons,
      y: lats,
      type: 'scatter',
      mode: 'markers',
      name: '着地点',
      marker: {
        color: bursts,
        colorscale: 'Viridis',
        colorbar: { title: { text: 'バースト高度 [m]' }, thickness: 12 },
        size: 6,
      },
    } as Data,
    // マージナルヒストグラム
    {
      x: lons,
      type: 'histogram',
      yaxis: 'y2',
      showlegend: false,
      marker: { color: '#90a4ae' },
    } as Data,
    {
      y: lats,
      type: 'histogram',
      xaxis: 'x2',
      showlegend: false,
      marker: { color: '#90a4ae' },
    } as Data,
  ]
  if (mcStats) {
    traces.push({
      x: [mcStats.mean.lon],
      y: [mcStats.mean.lat],
      type: 'scatter',
      mode: 'markers',
      name: '平均',
      marker: { color: '#d32f2f', size: 12, symbol: 'x' },
    } as Data)
  }

  return (
    <Plot
      data={traces}
      layout={{
        ...BASE_LAYOUT,
        height: 420,
        title: { text: '着地分布 (マージナル付き)' },
        xaxis: { title: { text: '経度' }, domain: [0, 0.82] },
        yaxis: { title: { text: '緯度' }, domain: [0, 0.82] },
        xaxis2: { domain: [0.84, 1], showticklabels: false },
        yaxis2: { domain: [0.84, 1], showticklabels: false },
        bargap: 0.05,
        showlegend: false,
      }}
      config={BASE_CONFIG}
      style={{ width: '100%' }}
    />
  )
}
