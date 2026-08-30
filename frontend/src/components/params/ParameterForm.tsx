import { useParamsStore } from '../../store/paramsStore'
import { useResultsStore } from '../../store/resultsStore'
import { useRunPrediction } from '../../hooks/useRunPrediction'
import { SitePicker } from './SitePicker'

function NumberField({
  label,
  value,
  onChange,
  step = 0.1,
  unit,
}: {
  label: string
  value: number
  onChange: (v: number) => void
  step?: number
  unit?: string
}) {
  return (
    <label>
      {label} {unit && <span className="unit">[{unit}]</span>}
      <input
        type="number"
        value={value}
        step={step}
        onChange={(e) => onChange(parseFloat(e.target.value))}
      />
    </label>
  )
}

export function ParameterForm() {
  const p = useParamsStore()
  const running = useResultsStore((s) => s.running)
  const progress = useResultsStore((s) => s.progress)
  const runError = useResultsStore((s) => s.runError)
  const { runSingle, runHourly, cancel } = useRunPrediction()

  return (
    <div className="param-form">
      <h2>発射条件</h2>
      <SitePicker />
      <p className="hint">
        発射地点は地図クリック / マーカーのドラッグ / 下の緯度経度入力でも設定できます
      </p>
      <NumberField
        label="緯度"
        value={p.latitude}
        step={0.0001}
        onChange={(v) => p.set({ latitude: v })}
      />
      <NumberField
        label="経度"
        value={p.longitude}
        step={0.0001}
        onChange={(v) => p.set({ longitude: v })}
      />
      <NumberField
        label="発射高度"
        unit="m"
        step={1}
        value={p.launchAltitude}
        onChange={(v) => p.set({ launchAltitude: v })}
      />
      <label>
        発射日時 (JST)
        <input
          type="datetime-local"
          value={p.launchTimeJst}
          onChange={(e) => p.set({ launchTimeJst: e.target.value })}
        />
      </label>
      <label>
        飛行プロファイル
        <select
          value={p.profile}
          onChange={(e) =>
            p.set({ profile: e.target.value as typeof p.profile })
          }
        >
          <option value="standard_profile">標準 (上昇→バースト→降下)</option>
          <option value="float_profile">フロート</option>
        </select>
      </label>
      <NumberField
        label="上昇速度"
        unit="m/s"
        value={p.ascentRate}
        onChange={(v) => p.set({ ascentRate: v })}
      />
      <NumberField
        label={p.profile === 'standard_profile' ? 'バースト高度' : 'フロート高度'}
        unit="m"
        step={100}
        value={p.burstAltitude}
        onChange={(v) => p.set({ burstAltitude: v })}
      />
      {p.profile === 'standard_profile' && (
        <NumberField
          label="降下速度 (海面)"
          unit="m/s"
          value={p.descentRate}
          onChange={(v) => p.set({ descentRate: v })}
        />
      )}

      <div className="run-buttons">
        <button onClick={runSingle} disabled={running}>
          単発予測
        </button>
        <button onClick={runHourly} disabled={running}>
          時系列予測
        </button>
        {running && <button onClick={cancel}>キャンセル</button>}
      </div>
      {running && progress && (
        <progress value={progress.done} max={progress.total} />
      )}
      {runError && <p className="error">{runError}</p>}

      <details>
        <summary>時系列予測の設定</summary>
        <NumberField
          label="間隔"
          unit="h"
          step={1}
          value={p.hourlyStepH}
          onChange={(v) => p.set({ hourlyStepH: Math.max(1, v) })}
        />
        <NumberField
          label="期間"
          unit="h"
          step={1}
          value={p.hourlyDurationH}
          onChange={(v) => p.set({ hourlyDurationH: Math.min(168, Math.max(1, v)) })}
        />
      </details>
    </div>
  )
}
