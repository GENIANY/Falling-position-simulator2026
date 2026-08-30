import { MapView } from './components/map/MapView'
const Map3D = lazy(() => import('./components/map/Map3D'))
import { ParameterForm } from './components/params/ParameterForm'
import { CalcPanel } from './components/params/CalcPanel'
import { MonteCarloPanel } from './components/mc/MonteCarloPanel'
import { OptimizerPanel } from './components/optimizer/OptimizerPanel'
import { Suspense, lazy } from 'react'
const TornadoChart = lazy(() =>
  import('./components/charts/TornadoChart').then((m) => ({ default: m.TornadoChart })),
)
import { ChartsPanel } from './components/charts/ChartsPanel'
import { ScenarioInfo } from './components/ScenarioInfo'
import { useUiStore } from './store/uiStore'
import './App.css'

export default function App() {
  const mapMode = useUiStore((s) => s.mapMode)
  const showCharts = useUiStore((s) => s.showCharts)
  const showSafetyZones = useUiStore((s) => s.showSafetyZones)
  const setUi = useUiStore((s) => s.set)

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h1>Falling-position-simulator</h1>
        <p className="subtitle">高高度バルーン着地位置シミュレーター</p>
        <ParameterForm />
        <details>
          <summary>モンテカルロ (確率分布)</summary>
          <MonteCarloPanel />
        </details>
        <details>
          <summary>バルーン計算 (サイジング)</summary>
          <CalcPanel />
        </details>
        <details>
          <summary>発射条件最適化</summary>
          <OptimizerPanel />
        </details>
        <details>
          <summary>感度分析</summary>
          <Suspense fallback={<p>読み込み中...</p>}>
            <TornadoChart />
          </Suspense>
        </details>
        <ScenarioInfo />
        <button
          className="charts-toggle"
          onClick={() => setUi({ showCharts: !showCharts })}
        >
          {showCharts ? 'グラフを隠す' : 'グラフを表示'}
        </button>
        <button
          className="charts-toggle"
          onClick={() => setUi({ showSafetyZones: !showSafetyZones })}
        >
          {showSafetyZones ? '回避区域を隠す' : '回避区域を表示 (市街地・空港/基地)'}
        </button>
        <button
          className="charts-toggle"
          onClick={() => setUi({ mapMode: mapMode === '2d' ? '3d' : '2d' })}
        >
          {mapMode === '2d' ? '3D地図に切替 (Navara)' : '2D地図に切替'}
        </button>
      </aside>
      <main className="map-area">
        {mapMode === '2d' ? (
          <MapView />
        ) : (
          <Suspense fallback={<p style={{ padding: '1rem' }}>3D地図読み込み中...</p>}>
            <Map3D />
          </Suspense>
        )}
        {showCharts && (
          <div className="charts-drawer">
            <ChartsPanel />
          </div>
        )}
      </main>
    </div>
  )
}
