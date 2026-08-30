import { useEffect, useState } from 'react'
import { useParamsStore } from '../../store/paramsStore'
import type { LaunchSite } from '../../store/paramsStore'

interface SiteEntry {
  latitude: number
  longitude: number
  altitude: number
}

/** 地域別 sites.json: { "北海道 (十勝)": { name: {lat,lon,alt} }, ... } */
type RegionalSitesJson = Record<string, Record<string, SiteEntry>>

const DEFAULT_REGION = '北海道 (十勝)'

export function SitePicker() {
  const sites = useParamsStore((s) => s.sites)
  const setSites = useParamsStore((s) => s.setSites)
  const applySite = useParamsStore((s) => s.applySite)
  const [regions, setRegions] = useState<RegionalSitesJson | null>(null)
  const [region, setRegion] = useState(DEFAULT_REGION)

  useEffect(() => {
    if (regions) return
    fetch(`${import.meta.env.BASE_URL}sites.json`)
      .then((r) => r.json() as Promise<RegionalSitesJson>)
      .then((data) => {
        setRegions(data)
        const first = data[DEFAULT_REGION] ? DEFAULT_REGION : Object.keys(data)[0]
        setRegion(first)
      })
      .catch(() => {
        /* sites.json無しでも動作継続 */
      })
  }, [regions])

  useEffect(() => {
    if (!regions || !regions[region]) return
    const parsed: LaunchSite[] = Object.entries(regions[region]).map(
      ([name, v]) => ({ name, ...v }),
    )
    setSites(parsed)
  }, [regions, region, setSites])

  return (
    <>
      <label>
        地域
        <select value={region} onChange={(e) => setRegion(e.target.value)}>
          {regions &&
            Object.keys(regions).map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
        </select>
      </label>
      <label>
        発射地点プリセット ({sites.length}件)
        <select
          defaultValue=""
          onChange={(e) => {
            const site = sites.find((s) => s.name === e.target.value)
            if (site) applySite(site)
          }}
        >
          <option value="" disabled>
            選択...
          </option>
          {sites.map((s) => (
            <option key={s.name} value={s.name}>
              {s.name}
            </option>
          ))}
        </select>
      </label>
    </>
  )
}
