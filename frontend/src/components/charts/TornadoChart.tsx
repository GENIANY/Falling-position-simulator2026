import Plot from 'react-plotly.js'
import type { Data } from 'plotly.js'
import { useSensitivity } from '../../hooks/useSensitivity'
import { BASE_CONFIG, BASE_LAYOUT } from './plotlyDefaults'

export function TornadoChart() {
  const { results, running, error, run } = useSensitivity()

  return (
    <div>
      <button
        onClick={() =>
          run({ ascentRate: 0.5, burstAltitudePct: 5, descentRate: 0.5 })
        }
        disabled={running}
      >
        {running ? '感度分析 実行中...' : '感度分析を実行 (±1σ, 7コール)'}
      </button>
      {error && <p className="error">{error}</p>}
      {results && (
        <Plot
          data={[
            {
              y: results.map((r) => r.parameter),
              x: results.map((r) => -r.minusKm),
              type: 'bar',
              orientation: 'h',
              name: '-1σ',
              marker: { color: '#42a5f5' },
            } as Data,
            {
              y: results.map((r) => r.parameter),
              x: results.map((r) => r.plusKm),
              type: 'bar',
              orientation: 'h',
              name: '+1σ',
              marker: { color: '#ef5350' },
            } as Data,
          ]}
          layout={{
            ...BASE_LAYOUT,
            title: { text: '感度分析: ±1σでの着地点変位' },
            xaxis: { title: { text: '着地点の変位 [km]' } },
            barmode: 'overlay',
          }}
          config={BASE_CONFIG}
          style={{ width: '100%' }}
        />
      )}
    </div>
  )
}
