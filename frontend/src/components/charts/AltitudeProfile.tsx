import Plot from 'react-plotly.js'
import type { Data } from 'plotly.js'
import { useResultsStore } from '../../store/resultsStore'
import type { Flight } from '../../api/tawhiriTypes'
import { BASE_CONFIG, BASE_LAYOUT } from './plotlyDefaults'

function flightTrace(f: Flight, name: string, opts: Partial<Data> = {}): Data {
  const points = [...f.ascent, ...f.descent]
  return {
    x: points.map((p) => new Date(p.datetime)),
    y: points.map((p) => p.altitude),
    type: 'scatter',
    mode: 'lines',
    name,
    ...opts,
  } as Data
}

export function AltitudeProfile() {
  const single = useResultsStore((s) => s.singleFlight)
  const hourly = useResultsStore((s) => s.hourlyResults)
  const mcSamples = useResultsStore((s) => s.mcSamples)
  const mcCentral = useResultsStore((s) => s.mcCentral)

  const traces: Data[] = []
  if (single) traces.push(flightTrace(single, '単発予測'))
  for (const h of hourly.slice(0, 30)) {
    traces.push(
      flightTrace(h.flight, `+${h.hourOffset}h`, {
        opacity: 0.5,
        showlegend: false,
      }),
    )
  }
  // MCスパゲッティ: 最大30本に間引き
  const step = Math.max(1, Math.ceil(mcSamples.length / 30))
  for (let i = 0; i < mcSamples.length; i += step) {
    traces.push(
      flightTrace(mcSamples[i].flight, `#${mcSamples[i].index}`, {
        opacity: 0.25,
        showlegend: false,
        line: { color: '#7b1fa2', width: 1 },
      } as Partial<Data>),
    )
  }
  if (mcCentral) {
    traces.push(
      flightTrace(mcCentral, '中心予測', {
        line: { color: '#d32f2f', width: 2 },
      } as Partial<Data>),
    )
  }

  return (
    <Plot
      data={traces}
      layout={{
        ...BASE_LAYOUT,
        title: { text: '高度プロファイル' },
        xaxis: { title: { text: '時刻 (JST表示)' } },
        yaxis: { title: { text: '高度 [m]' } },
      }}
      config={BASE_CONFIG}
      style={{ width: '100%' }}
    />
  )
}
