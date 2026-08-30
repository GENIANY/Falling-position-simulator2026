import { useMemo, useState } from 'react'
import {
  BalloonPhysicsError,
  computeBalloon,
} from '../../physics/balloon'
import type { BalloonResult } from '../../physics/balloon'
import { BALLOON_SPECS } from '../../physics/balloonData'
import type { GasType } from '../../physics/constants'
import { useParamsStore } from '../../store/paramsStore'

export function CalcPanel() {
  const [payloadMassG, setPayloadMassG] = useState(1000)
  const [balloonModel, setBalloonModel] = useState('k1200')
  const [gas, setGas] = useState<GasType>('helium')
  const [targetKind, setTargetKind] = useState<'ascentRate' | 'burstAltitude'>(
    'burstAltitude',
  )
  const [targetValue, setTargetValue] = useState(30000)
  const setParams = useParamsStore((s) => s.set)

  const result = useMemo<
    { ok: true; value: BalloonResult } | { ok: false; error: string }
  >(() => {
    try {
      return {
        ok: true,
        value: computeBalloon({
          payloadMassG,
          balloonModel,
          gas,
          target: { kind: targetKind, value: targetValue },
        }),
      }
    } catch (e) {
      return {
        ok: false,
        error: e instanceof BalloonPhysicsError ? e.message : '計算エラー',
      }
    }
  }, [payloadMassG, balloonModel, gas, targetKind, targetValue])

  return (
    <div className="calc-panel">
      <h3>バルーン計算</h3>
      <label>
        ペイロード質量 [g]
        <input
          type="number"
          value={payloadMassG}
          min={20}
          max={20000}
          onChange={(e) => setPayloadMassG(parseFloat(e.target.value))}
        />
      </label>
      <label>
        バルーン型番
        <select
          value={balloonModel}
          onChange={(e) => setBalloonModel(e.target.value)}
        >
          {Object.entries(BALLOON_SPECS).map(([id, spec]) => (
            <option key={id} value={id}>
              {spec.label}
            </option>
          ))}
        </select>
      </label>
      <label>
        ガス
        <select value={gas} onChange={(e) => setGas(e.target.value as GasType)}>
          <option value="helium">ヘリウム</option>
          <option value="hydrogen">水素</option>
          <option value="methane">メタン</option>
        </select>
      </label>
      <label>
        目標
        <select
          value={targetKind}
          onChange={(e) => {
            const kind = e.target.value as typeof targetKind
            setTargetKind(kind)
            setTargetValue(kind === 'burstAltitude' ? 30000 : 5)
          }}
        >
          <option value="burstAltitude">バースト高度 [m]</option>
          <option value="ascentRate">上昇速度 [m/s]</option>
        </select>
        <input
          type="number"
          value={targetValue}
          step={targetKind === 'burstAltitude' ? 500 : 0.1}
          onChange={(e) => setTargetValue(parseFloat(e.target.value))}
        />
      </label>

      {result.ok ? (
        <>
          <dl className="calc-results">
            <dt>上昇速度</dt>
            <dd>{result.value.ascentRate.toFixed(2)} m/s</dd>
            <dt>バースト高度</dt>
            <dd>{Math.round(result.value.burstAltitude)} m</dd>
            <dt>バースト到達</dt>
            <dd>{Math.round(result.value.timeToBurstMin)} 分</dd>
            <dt>ネックリフト</dt>
            <dd>{Math.round(result.value.neckLiftG)} g</dd>
            <dt>ガス量</dt>
            <dd>
              {result.value.launchVolumeM3.toFixed(2)} m³ (
              {Math.round(result.value.launchVolumeM3 * 1000)} L)
            </dd>
          </dl>
          <button
            onClick={() =>
              setParams({
                ascentRate: Number(result.value.ascentRate.toFixed(2)),
                burstAltitude: Math.round(result.value.burstAltitude),
              })
            }
          >
            この値を発射条件に反映
          </button>
        </>
      ) : (
        <p className="error">{result.error}</p>
      )}
    </div>
  )
}
