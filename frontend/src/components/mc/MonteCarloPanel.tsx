import { useState } from 'react'
import { buildBaseRequest, validateLaunchTime } from '../../hooks/useRunPrediction'
import { MC_MAX_SAMPLES, useMonteCarlo } from '../../mc/useMonteCarlo'
import { useParamsStore } from '../../store/paramsStore'
import { useResultsStore } from '../../store/resultsStore'

export function MonteCarloPanel() {
  const [samples, setSamples] = useState(100)
  const [sigmaAscent, setSigmaAscent] = useState(0.5)
  const [sigmaBurstPct, setSigmaBurstPct] = useState(5)
  const [sigmaDescent, setSigmaDescent] = useState(0.5)
  const [burstModel, setBurstModel] = useState<'gaussian' | 'weibull'>(
    'gaussian',
  )
  const [seed, setSeed] = useState(42)
  const profile = useParamsStore((s) => s.profile)
  const running = useResultsStore((s) => s.running)
  const { run, cancel } = useMonteCarlo()

  const start = () => {
    const base = buildBaseRequest()
    if (base.profile !== 'standard_profile') return
    const err = validateLaunchTime(base.launch_datetime)
    if (err) {
      useResultsStore.getState().setError(err)
      return
    }
    void run({
      base,
      samples,
      sigma: {
        ascentRate: sigmaAscent,
        burstAltitudePct: sigmaBurstPct,
        descentRate: sigmaDescent,
      },
      burstModel,
      seed,
    })
  }

  if (profile !== 'standard_profile') {
    return <p>モンテカルロは標準プロファイルのみ対応です</p>
  }

  return (
    <div className="mc-panel">
      <h3>モンテカルロ設定</h3>
      <label>
        試行回数 (最大 {MC_MAX_SAMPLES})
        <input
          type="number"
          value={samples}
          min={10}
          max={MC_MAX_SAMPLES}
          step={10}
          onChange={(e) =>
            setSamples(
              Math.min(MC_MAX_SAMPLES, Math.max(10, parseInt(e.target.value))),
            )
          }
        />
      </label>
      <label>
        分布モデル
        <select
          value={burstModel}
          onChange={(e) =>
            setBurstModel(e.target.value as 'gaussian' | 'weibull')
          }
        >
          <option value="gaussian">正規分布 (3パラメータ)</option>
          <option value="weibull">Weibull (バースト高度のみ)</option>
        </select>
      </label>
      {burstModel === 'gaussian' && (
        <>
          <label>
            上昇速度 σ [m/s]
            <input
              type="number"
              value={sigmaAscent}
              step={0.1}
              min={0}
              onChange={(e) => setSigmaAscent(parseFloat(e.target.value))}
            />
          </label>
          <label>
            バースト高度 σ [%]
            <input
              type="number"
              value={sigmaBurstPct}
              step={1}
              min={0}
              onChange={(e) => setSigmaBurstPct(parseFloat(e.target.value))}
            />
          </label>
          <label>
            降下速度 σ [m/s]
            <input
              type="number"
              value={sigmaDescent}
              step={0.1}
              min={0}
              onChange={(e) => setSigmaDescent(parseFloat(e.target.value))}
            />
          </label>
        </>
      )}
      <label>
        乱数シード
        <input
          type="number"
          value={seed}
          onChange={(e) => setSeed(parseInt(e.target.value))}
        />
      </label>
      <div className="run-buttons">
        <button onClick={start} disabled={running}>
          モンテカルロ実行
        </button>
        {running && <button onClick={cancel}>キャンセル</button>}
      </div>
    </div>
  )
}
