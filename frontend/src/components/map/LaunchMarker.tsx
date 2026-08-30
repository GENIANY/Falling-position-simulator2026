import { useMemo, useRef } from 'react'
import { Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import { useParamsStore } from '../../store/paramsStore'

// Leaflet既定アイコンはバンドラでパスが壊れるためSVGで自前定義
const launchIcon = L.divIcon({
  className: 'launch-marker-icon',
  html: `<svg width="34" height="44" viewBox="0 0 34 44" xmlns="http://www.w3.org/2000/svg">
    <path d="M17 43 C17 43 3 24 3 15 A14 14 0 1 1 31 15 C31 24 17 43 17 43Z"
      fill="#1976d2" stroke="#fff" stroke-width="2"/>
    <circle cx="17" cy="15" r="5.5" fill="#fff"/>
  </svg>`,
  iconSize: [34, 44],
  iconAnchor: [17, 43],
  popupAnchor: [0, -40],
})

export function LaunchMarker() {
  const latitude = useParamsStore((s) => s.latitude)
  const longitude = useParamsStore((s) => s.longitude)
  const set = useParamsStore((s) => s.set)
  const markerRef = useRef<L.Marker>(null)

  const eventHandlers = useMemo(
    () => ({
      dragend() {
        const marker = markerRef.current
        if (!marker) return
        const pos = marker.getLatLng()
        set({
          latitude: Number(pos.lat.toFixed(5)),
          longitude: Number(pos.lng.toFixed(5)),
        })
      },
    }),
    [set],
  )

  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return null

  return (
    <Marker
      position={[latitude, longitude]}
      draggable
      icon={launchIcon}
      eventHandlers={eventHandlers}
      ref={markerRef}
      zIndexOffset={2000}
    >
      <Popup>
        発射地点 ({latitude.toFixed(4)}, {longitude.toFixed(4)})
        <br />
        ドラッグまたは地図クリックで移動できます
      </Popup>
    </Marker>
  )
}
