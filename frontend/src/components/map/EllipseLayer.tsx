import { Polygon, Tooltip } from 'react-leaflet'
import { useResultsStore } from '../../store/resultsStore'
import { ellipseToLatLngs } from '../../stats/landing'

const ELLIPSE_COLORS: Record<number, string> = {
  0.5: '#2e7d32',
  0.9: '#f9a825',
  0.95: '#c62828',
}

export function EllipseLayer() {
  const stats = useResultsStore((s) => s.mcStats)
  if (!stats) return null
  return (
    <>
      {stats.ellipses.map((e) => (
        <Polygon
          key={e.probability}
          positions={ellipseToLatLngs(stats.mean, e)}
          pathOptions={{
            color: ELLIPSE_COLORS[e.probability] ?? '#555',
            fillOpacity: 0.05,
            weight: 2,
          }}
        >
          <Tooltip sticky>
            {Math.round(e.probability * 100)}% 信頼楕円 (長軸{' '}
            {(e.semiMajorM / 1000).toFixed(1)} km)
          </Tooltip>
        </Polygon>
      ))}
    </>
  )
}
