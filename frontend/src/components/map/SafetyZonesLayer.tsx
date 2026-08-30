import { useEffect, useState } from 'react'
import { Circle, Tooltip } from 'react-leaflet'
import {
  getSafetyZones,
  loadSafetyData,
} from '../../safety/landingSafety'
import type { CircleZone } from '../../safety/landingSafety'
import { useUiStore } from '../../store/uiStore'

export function SafetyZonesLayer() {
  const show = useUiStore((s) => s.showSafetyZones)
  const [zones, setZones] = useState<{
    towns: CircleZone[]
    restricted: CircleZone[]
  } | null>(null)

  useEffect(() => {
    if (!show || zones) return
    loadSafetyData(import.meta.env.BASE_URL)
      .then(() => setZones(getSafetyZones()))
      .catch(() => {
        /* データ無しでも地図は使える */
      })
  }, [show, zones])

  if (!show || !zones) return null

  return (
    <>
      {zones.restricted.map((z) => (
        <Circle
          key={`r-${z.name}`}
          center={[z.lat, z.lon]}
          radius={z.radiusM}
          pathOptions={{
            color: '#c62828',
            fillColor: '#c62828',
            fillOpacity: 0.12,
            weight: 1,
          }}
        >
          <Tooltip sticky>{z.name} (立入回避)</Tooltip>
        </Circle>
      ))}
      {zones.towns.map((z) => (
        <Circle
          key={`t-${z.name}-${z.lat}`}
          center={[z.lat, z.lon]}
          radius={z.radiusM}
          pathOptions={{
            color: '#ef6c00',
            fillColor: '#ef6c00',
            fillOpacity: 0.08,
            weight: 1,
          }}
        >
          <Tooltip sticky>{z.name} (市街地)</Tooltip>
        </Circle>
      ))}
    </>
  )
}
