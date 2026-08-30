import { MapContainer, TileLayer, useMapEvents } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { useParamsStore } from '../../store/paramsStore'
import { LaunchMarker } from './LaunchMarker'
import { OptimizerLayer } from './OptimizerLayer'
import { SafetyZonesLayer } from './SafetyZonesLayer'
import { TrajectoryLayer } from './TrajectoryLayer'
import { EllipseLayer } from './EllipseLayer'
import { HeatmapLayer } from './HeatmapLayer'

function ClickToSetLaunch() {
  const set = useParamsStore((s) => s.set)
  useMapEvents({
    click: (e) => {
      set({
        latitude: Number(e.latlng.lat.toFixed(5)),
        longitude: Number(e.latlng.lng.toFixed(5)),
      })
    },
  })
  return null
}

export function MapView() {
  return (
    <MapContainer
      center={[42.7, 143.2]}
      zoom={9}
      style={{ width: '100%', height: '100%' }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <ClickToSetLaunch />
      <LaunchMarker />
      <SafetyZonesLayer />
      <OptimizerLayer />
      <TrajectoryLayer />
      <EllipseLayer />
      <HeatmapLayer />
    </MapContainer>
  )
}
