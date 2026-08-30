import { Suspense, lazy } from 'react'
import { useResultsStore } from '../../store/resultsStore'

// Plotlyは重いので遅延ロード
const AltitudeProfile = lazy(() =>
  import('./AltitudeProfile').then((m) => ({ default: m.AltitudeProfile })),
)
const LandingScatter = lazy(() =>
  import('./LandingScatter').then((m) => ({ default: m.LandingScatter })),
)
const DistanceHistogram = lazy(() =>
  import('./DistanceHistogram').then((m) => ({ default: m.DistanceHistogram })),
)

export function ChartsPanel() {
  const single = useResultsStore((s) => s.singleFlight)
  const hourly = useResultsStore((s) => s.hourlyResults)
  const mcSamples = useResultsStore((s) => s.mcSamples)

  const hasAnything = single || hourly.length > 0 || mcSamples.length > 0
  if (!hasAnything) {
    return <p className="charts-empty">予測を実行するとグラフが表示されます</p>
  }

  return (
    <Suspense fallback={<p>グラフ読み込み中...</p>}>
      <div className="charts-panel">
        {(single || hourly.length > 0 || mcSamples.length > 0) && (
          <AltitudeProfile />
        )}
        {mcSamples.length >= 5 && <LandingScatter />}
        {mcSamples.length >= 5 && <DistanceHistogram />}
      </div>
    </Suspense>
  )
}
