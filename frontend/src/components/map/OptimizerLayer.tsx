import { CircleMarker, Polyline, Popup } from 'react-leaflet'
import { CATEGORY_COLOR, CATEGORY_LABEL } from '../../safety/landingSafety'
import { useResultsStore } from '../../store/resultsStore'
import { utcIsoToJstDisplay } from '../../time/jst'
import type { Flight } from '../../api/tawhiriTypes'

function flightPath(f: Flight): [number, number][] {
  return [...f.ascent, ...f.descent].map((p) => [p.latitude, p.longitude])
}

/** 最適化結果 (上位N件) の飛行経路+着地点を表示 */
export function OptimizerLayer() {
  const results = useResultsStore((s) => s.optimizerResults)
  if (results.length === 0) return null

  return (
    <>
      {results.map((r, rank) => {
        if (!r.flight) return null
        const color = r.category ? CATEGORY_COLOR[r.category] : '#555'
        const best = rank === 0
        return (
          <span key={`${r.site.name}-${r.burstAltitude}-${r.launchTimeUtc}`}>
            <Polyline
              positions={flightPath(r.flight)}
              color={color}
              weight={best ? 3 : 1.5}
              opacity={best ? 0.9 : 0.45}
              dashArray={best ? undefined : '4 4'}
            />
            <CircleMarker
              center={[
                r.flight.landing.latitude,
                r.flight.landing.longitude,
              ]}
              radius={best ? 8 : 5}
              pathOptions={{
                fillColor: color,
                fillOpacity: 0.9,
                color: '#000',
                weight: 1,
              }}
            >
              <Popup>
                <b>#{rank + 1}</b>{' '}
                {r.category && `[${CATEGORY_LABEL[r.category]}]`}
                <br />
                {r.site.name}
                <br />
                発射 {utcIsoToJstDisplay(r.launchTimeUtc)} JST
                <br />
                バースト {Math.round(r.burstAltitude)} m / ガス{' '}
                {r.launchVolumeM3.toFixed(2)} m³
                <br />
                {r.distanceKm != null && `距離 ${r.distanceKm.toFixed(1)} km`}
              </Popup>
            </CircleMarker>
          </span>
        )
      })}
    </>
  )
}
