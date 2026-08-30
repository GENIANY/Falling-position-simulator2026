// Navara (@navaramap/three) による3Dグローブ表示。
// 2D(Leaflet)と切替可能。飛行経路は高度付きLineString、着地点は
// 安全カテゴリ色のポイントで表示する。
// 注意 (公式スキルより): inline GeoJSONはsource.update()で再読込されないため
// データ変化時はlayer/sourceともdelete→再addする。非drapedポリラインは
// ライト無しだと黒くなるためambientライト必須。widthはpx値だがmaxWidth(m)で
// クランプされるため高高度視点用に大きく設定。

import { useEffect, useRef } from 'react'
import ThreeView, { Color } from '@navaramap/three'
import {
  DefaultPlugin,
  type DefaultDescriptions,
} from '@navaramap/three-default-plugin'
import { CATEGORY_COLOR } from '../../safety/landingSafety'
import type { SafetyCategory } from '../../safety/landingSafety'
import { useParamsStore } from '../../store/paramsStore'
import { useResultsStore } from '../../store/resultsStore'
import type { ResultsState } from '../../store/resultsStore'
import type { Flight } from '../../api/tawhiriTypes'

type SourceHandle = ReturnType<ThreeView['addSource']>
type LayerHandle = ReturnType<ThreeView['addLayer']>

interface DynamicLayers {
  sources: SourceHandle[]
  layers: LayerHandle[]
}

function flightLineFeature(f: Flight): GeoJSON.Feature {
  return {
    type: 'Feature',
    properties: {},
    geometry: {
      type: 'LineString',
      coordinates: [...f.ascent, ...f.descent].map((p) => [
        p.longitude,
        p.latitude,
        p.altitude,
      ]),
    },
  }
}

function buildGeojson(state: ResultsState): {
  lines: GeoJSON.FeatureCollection
  pointsByCategory: Map<SafetyCategory | 'default', GeoJSON.FeatureCollection>
} {
  const lineFeatures: GeoJSON.Feature[] = []
  const points = new Map<
    SafetyCategory | 'default',
    GeoJSON.Feature[]
  >()

  const addPoint = (
    lat: number,
    lon: number,
    category: SafetyCategory | 'default',
  ) => {
    if (!points.has(category)) points.set(category, [])
    points.get(category)!.push({
      type: 'Feature',
      properties: {},
      geometry: { type: 'Point', coordinates: [lon, lat, 0] },
    })
  }

  if (state.singleFlight) lineFeatures.push(flightLineFeature(state.singleFlight))
  if (state.mcCentral) lineFeatures.push(flightLineFeature(state.mcCentral))
  for (const h of state.hourlyResults) {
    lineFeatures.push(flightLineFeature(h.flight))
    addPoint(h.flight.landing.latitude, h.flight.landing.longitude, 'default')
  }
  for (const s of state.mcSamples) {
    addPoint(
      s.flight.landing.latitude,
      s.flight.landing.longitude,
      s.category ?? 'default',
    )
  }
  for (const r of state.optimizerResults) {
    if (!r.flight) continue
    lineFeatures.push(flightLineFeature(r.flight))
    addPoint(
      r.flight.landing.latitude,
      r.flight.landing.longitude,
      r.category ?? 'default',
    )
  }

  return {
    lines: { type: 'FeatureCollection', features: lineFeatures },
    pointsByCategory: new Map(
      [...points.entries()].map(([k, v]) => [
        k,
        { type: 'FeatureCollection', features: v } as GeoJSON.FeatureCollection,
      ]),
    ),
  }
}

const POINT_COLORS: Record<SafetyCategory | 'default', string> = {
  ...CATEGORY_COLOR,
  default: '#7b1fa2',
}

export function Map3D() {
  const containerRef = useRef<HTMLDivElement>(null)
  const viewRef = useRef<ThreeView<DefaultDescriptions> | null>(null)
  const dynamicRef = useRef<DynamicLayers>({ sources: [], layers: [] })
  const disposedRef = useRef(false)

  useEffect(() => {
    if (!containerRef.current) return
    disposedRef.current = false
    let unsubscribe: (() => void) | null = null

    const setup = async () => {
      const view = new ThreeView<DefaultDescriptions>({
        container: containerRef.current!,
        useNormal: true,
      })
      const plugin = new DefaultPlugin()
      view.addPlugin(plugin)
      await view.init()
      if (disposedRef.current) {
        view.dispose()
        return
      }
      viewRef.current = view

      // 非drapedポリラインが黒くならないようambientライト (公式スキルの注意点)
      view.addLight({ ambient: { intensity: 1.2 } })

      // 地形 (国土地理院DEM) + OSMラスタ
      const terrainSource = view.addSource({
        type: 'raster-dem',
        url: 'https://cyberjapandata.gsi.go.jp/xyz/dem_png/{z}/{x}/{y}.png',
        maxZoom: 14,
        minZoom: 5,
      })
      view.addLayer({ type: 'terrain', source: terrainSource, terrain: {} })
      const raster = view.addSource({
        type: 'raster-tile',
        url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        maxZoom: 18,
      })
      view.addLayer({ type: 'raster', source: raster, raster: {} })
      view.attribution?.add([
        {
          attributionHtml:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors · 標高: <a href="https://maps.gsi.go.jp/development/ichiran.html">国土地理院</a>',
        },
      ])

      // 発射地点へカメラ
      const p = useParamsStore.getState()
      view.setCamera({
        lng: p.longitude,
        lat: p.latitude,
        height: 120000,
        heading: 0,
        pitch: -55,
        roll: 0,
      })

      // 結果データの反映 (変化時はsource/layerを作り直す)
      const rebuild = (state: ResultsState) => {
        const v = viewRef.current
        if (!v) return
        for (const l of dynamicRef.current.layers) l.delete()
        for (const s of dynamicRef.current.sources) s.delete()
        dynamicRef.current = { sources: [], layers: [] }

        const { lines, pointsByCategory } = buildGeojson(state)
        if (lines.features.length > 0) {
          const src = v.addSource({ type: 'geojson', data: lines })
          const layer = v.addLayer({
            type: 'vector',
            source: src,
            polyline: {
              color: new Color().setStyle('#d32f2f'),
              width: 3,
              maxWidth: 100000,
              clampToGround: false,
            },
          })
          dynamicRef.current.sources.push(src)
          dynamicRef.current.layers.push(layer)
        }
        for (const [category, fc] of pointsByCategory) {
          const src = v.addSource({ type: 'geojson', data: fc })
          const layer = v.addLayer({
            type: 'vector',
            source: src,
            point: {
              color: new Color().setStyle(POINT_COLORS[category]),
              size: 8,
              clampToGround: true,
            },
          })
          dynamicRef.current.sources.push(src)
          dynamicRef.current.layers.push(layer)
        }
      }

      rebuild(useResultsStore.getState())
      let timer: ReturnType<typeof setTimeout> | null = null
      unsubscribe = useResultsStore.subscribe((state) => {
        // MC実行中の逐次サンプル追加で毎回作り直さないようデバウンス
        if (timer) clearTimeout(timer)
        timer = setTimeout(() => rebuild(state), 500)
      })
    }

    void setup()

    return () => {
      disposedRef.current = true
      unsubscribe?.()
      if (viewRef.current) {
        viewRef.current.dispose()
        viewRef.current = null
      }
      dynamicRef.current = { sources: [], layers: [] }
    }
  }, [])

  return <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
}

export default Map3D
