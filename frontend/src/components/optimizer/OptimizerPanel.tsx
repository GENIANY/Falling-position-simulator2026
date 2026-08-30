import { useMemo, useRef, useState } from 'react'
import { useMonteCarlo } from '../../mc/useMonteCarlo'
import {
  jstInputToUtcIso,
  utcIsoToJstDisplay,
  utcIsoToJstInputValue,
} from '../../time/jst'
import {
  OPTIMIZER_BATCH_PAUSE_MS,
  OPTIMIZER_BATCH_SIZE,
  enumerateCells,
  runGridSearch,
} from '../../optimizer/gridSearch'
import type { GridResult, GridSpec } from '../../optimizer/gridSearch'
import { useParamsStore } from '../../store/paramsStore'
import { useResultsStore } from '../../store/resultsStore'
import type { GasType } from '../../physics/constants'
import { CATEGORY_COLOR, CATEGORY_LABEL } from '../../safety/landingSafety'

export function OptimizerPanel() {
  const sites = useParamsStore((s) => s.sites)
  const launchTimeJst = useParamsStore((s) => s.launchTimeJst)
  const [selectedSites, setSelectedSites] = useState<string[]>([])
  const [balloonModel, setBalloonModel] = useState('k1200')
  const [payloadMassG, setPayloadMassG] = useState(1000)
  const [gas, setGas] = useState<GasType>('helium')
  const [burstMin, setBurstMin] = useState(25000)
  const [burstMax, setBurstMax] = useState(33000)
  const [burstStep, setBurstStep] = useState(2000)
  const [timeWindowH, setTimeWindowH] = useState(24)
  const [timeStepH, setTimeStepH] = useState(6)
  const [objective, setObjective] = useState<
    'avoidSea' | 'minDistance' | 'safeLanding'
  >('safeLanding')
  const [mountainElevationM, setMountainElevationM] = useState(500)
  const [descentRate] = useState(5)
  const [results, setResults] = useState<GridResult[] | null>(null)
  const [running, setRunning] = useState(false)
  const [progress, setProgress] = useState<[number, number] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)
  const { run: runMc } = useMonteCarlo()
  const mcRunning = useResultsStore((s) => s.running)

  const spec = useMemo<GridSpec>(() => {
    const burstAltitudes: number[] = []
    for (let b = burstMin; b <= burstMax; b += burstStep) burstAltitudes.push(b)
    const launchTimesUtc: string[] = []
    const startUtc = Date.parse(jstInputToUtcIso(launchTimeJst))
    for (let h = 0; h <= timeWindowH; h += timeStepH) {
      launchTimesUtc.push(new Date(startUtc + h * 3600 * 1000).toISOString())
    }
    return {
      sites: sites.filter((s) => selectedSites.includes(s.name)),
      burstAltitudes,
      balloonModel,
      payloadMassG,
      gas,
      launchTimesUtc,
      descentRate,
    }
  }, [
    sites,
    selectedSites,
    balloonModel,
    payloadMassG,
    gas,
    burstMin,
    burstMax,
    burstStep,
    launchTimeJst,
    timeWindowH,
    timeStepH,
    descentRate,
  ])

  const cellCount = useMemo(() => enumerateCells(spec).length, [spec])

  const startMcFromResult = (r: GridResult) => {
    // 発射条件をフォームに反映して同条件でモンテカルロを実行
    useParamsStore.getState().set({
      latitude: r.site.latitude,
      longitude: r.site.longitude,
      launchAltitude: r.site.altitude,
      launchTimeJst: utcIsoToJstInputValue(r.launchTimeUtc),
      ascentRate: Number(r.ascentRate.toFixed(2)),
      burstAltitude: Math.round(r.burstAltitude),
      descentRate,
      profile: 'standard_profile',
    })
    void runMc({
      base: {
        profile: 'standard_profile',
        launch_latitude: r.site.latitude,
        launch_longitude: r.site.longitude,
        launch_altitude: r.site.altitude,
        launch_datetime: r.launchTimeUtc,
        ascent_rate: Number(r.ascentRate.toFixed(2)),
        burst_altitude: Math.round(r.burstAltitude),
        descent_rate: descentRate,
      },
      samples: 100,
      sigma: { ascentRate: 0.5, burstAltitudePct: 5, descentRate: 0.5 },
      burstModel: 'gaussian',
      seed: 42,
    })
  }

  const start = async () => {
    setError(null)
    setResults(null)
    setRunning(true)
    setProgress(null)
    abortRef.current = new AbortController()
    try {
      const res = await runGridSearch(spec, {
        objective: { kind: objective, seaPenaltyKm: 1000, mountainElevationM },
        onProgress: (done, total) => setProgress([done, total]),
        signal: abortRef.current.signal,
      })
      setResults(res)
      useResultsStore.getState().setOptimizerResults(res.slice(0, 10))
    } catch (e) {
      if (!(e instanceof DOMException && e.name === 'AbortError')) {
        setError(e instanceof Error ? e.message : String(e))
      }
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="optimizer-panel">
      <h3>発射条件最適化 (グリッドサーチ)</h3>
      <label>
        発射地点候補 (複数選択)
        <select
          multiple
          size={5}
          value={selectedSites}
          onChange={(e) =>
            setSelectedSites(
              Array.from(e.target.selectedOptions, (o) => o.value),
            )
          }
        >
          {sites.map((s) => (
            <option key={s.name} value={s.name}>
              {s.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        ペイロード質量 [g]
        <input
          type="number"
          value={payloadMassG}
          onChange={(e) => setPayloadMassG(parseFloat(e.target.value))}
        />
      </label>
      <label>
        バルーン / ガス
        <select
          value={balloonModel}
          onChange={(e) => setBalloonModel(e.target.value)}
        >
          <option value="k800">Kaymont 800</option>
          <option value="k1000">Kaymont 1000</option>
          <option value="k1200">Kaymont 1200</option>
          <option value="k1500">Kaymont 1500</option>
          <option value="h1000">Hwoyee 1000</option>
          <option value="h1200">Hwoyee 1200</option>
        </select>
        <select value={gas} onChange={(e) => setGas(e.target.value as GasType)}>
          <option value="helium">ヘリウム</option>
          <option value="hydrogen">水素</option>
        </select>
      </label>
      <label>
        バースト高度スイープ [m] (ガス量の代理)
        <div className="triple-input">
          <input
            type="number"
            value={burstMin}
            step={1000}
            onChange={(e) => setBurstMin(parseFloat(e.target.value))}
          />
          〜
          <input
            type="number"
            value={burstMax}
            step={1000}
            onChange={(e) => setBurstMax(parseFloat(e.target.value))}
          />
          刻み
          <input
            type="number"
            value={burstStep}
            step={500}
            onChange={(e) => setBurstStep(Math.max(500, parseFloat(e.target.value)))}
          />
        </div>
      </label>
      <label>
        時刻窓 [h] / 刻み [h]
        <div className="triple-input">
          <input
            type="number"
            value={timeWindowH}
            onChange={(e) => setTimeWindowH(parseFloat(e.target.value))}
          />
          <input
            type="number"
            value={timeStepH}
            onChange={(e) => setTimeStepH(Math.max(1, parseFloat(e.target.value)))}
          />
        </div>
      </label>
      <label>
        目的関数
        <select
          value={objective}
          onChange={(e) =>
            setObjective(
              e.target.value as 'avoidSea' | 'minDistance' | 'safeLanding',
            )
          }
        >
          <option value="safeLanding">
            安全着地 (海・住宅街・空港/基地・山を回避)
          </option>
          <option value="avoidSea">海着水を避ける (陸で発射地点に近く)</option>
          <option value="minDistance">発射地点への近さ優先</option>
        </select>
      </label>
      {objective === 'safeLanding' && (
        <label>
          山地とみなす標高 [m]
          <input
            type="number"
            value={mountainElevationM}
            step={50}
            min={100}
            onChange={(e) =>
              setMountainElevationM(parseFloat(e.target.value))
            }
          />
        </label>
      )}

      <p>
        Tawhiriコール数: {cellCount}
        {cellCount > OPTIMIZER_BATCH_SIZE && (
          <>
            {' '}
            ({Math.ceil(cellCount / OPTIMIZER_BATCH_SIZE)}バッチ、バッチ間
            {OPTIMIZER_BATCH_PAUSE_MS / 1000}s休止)
          </>
        )}
        {' / 推定 '}
        {Math.ceil(
          (cellCount * 0.45) / 5 +
            Math.max(0, Math.ceil(cellCount / OPTIMIZER_BATCH_SIZE) - 1) *
              (OPTIMIZER_BATCH_PAUSE_MS / 1000),
        )}
        秒
      </p>
      {cellCount > 1000 && (
        <p className="hint">
          大規模実行です。無料APIのため負荷にご配慮を。キャンセルはいつでも可能。
        </p>
      )}

      <div className="run-buttons">
        <button
          onClick={start}
          disabled={running || cellCount === 0}
        >
          最適化実行
        </button>
        {running && (
          <button onClick={() => abortRef.current?.abort()}>キャンセル</button>
        )}
      </div>
      {running && progress && (
        <progress value={progress[0]} max={progress[1]} />
      )}
      {error && <p className="error">{error}</p>}

      {results && (
        <div className="optimizer-results">
          <h4>結果 (スコア順・上位10、経路は地図に表示中)</h4>
          <table>
            <thead>
              <tr>
                <th>地点</th>
                <th>バースト高度</th>
                <th>ガス量</th>
                <th>発射時刻(JST)</th>
                <th>判定</th>
                <th>距離</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {results.slice(0, 10).map((r, i) => (
                <tr key={i}>
                  <td>{r.site.name}</td>
                  <td>{Math.round(r.burstAltitude)} m</td>
                  <td>{r.launchVolumeM3.toFixed(2)} m³</td>
                  <td>{utcIsoToJstDisplay(r.launchTimeUtc, 'MM-dd HH:mm')}</td>
                  <td>
                    {r.category ? (
                      <span style={{ color: CATEGORY_COLOR[r.category] }}>
                        {CATEGORY_LABEL[r.category]}
                      </span>
                    ) : r.onLand ? (
                      '陸'
                    ) : (
                      '海'
                    )}
                  </td>
                  <td>
                    {r.distanceKm != null ? `${r.distanceKm.toFixed(1)} km` : '—'}
                  </td>
                  <td>
                    <button
                      className="mini-btn"
                      disabled={mcRunning || !r.flight}
                      onClick={() => startMcFromResult(r)}
                      title="この条件で100サンプルのモンテカルロを実行"
                    >
                      MC
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
