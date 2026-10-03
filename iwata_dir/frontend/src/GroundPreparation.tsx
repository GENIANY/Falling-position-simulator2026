import {useEffect, useRef, useState} from 'react';
import {api, type GroundObservation, type GroundQuery} from './api';
import type {Candidate, WeatherSource} from './domain';

// A ground observation belongs to one field, location and instant. The current
// launch altitude may change independently; its clearance is recomputed below.
export function groundBinding(candidate: Candidate, source?: WeatherSource) {
  const launch = candidate.config.launch;
  if (!source || !/^[0-9a-f]{64}$/i.test(source.sha256 ?? '') ||
      !Number.isFinite(Date.parse(launch.time_utc)) ||
      ![launch.latitude_deg, launch.longitude_deg, launch.altitude_m].every(Number.isFinite)) return null;
  return JSON.stringify([candidate.id, source.id, source.sha256!.toLowerCase(),
    new Date(launch.time_utc).toISOString(), launch.latitude_deg, launch.longitude_deg]);
}

export function groundMatches(value: GroundObservation, source: WeatherSource, query: GroundQuery) {
  return value.schema === 'balloon.weather-ground/1' && value.weather_source_id === source.id &&
    value.weather_sha256.toLowerCase() === source.sha256?.toLowerCase() &&
    Date.parse(value.query.time_utc) === Date.parse(query.time_utc) &&
    value.query.latitude_deg === query.latitude_deg && value.query.longitude_deg === query.longitude_deg &&
    value.query.launch_altitude_m === query.launch_altitude_m &&
    Number.isFinite(value.ground_altitude_m) && value.height_reference === 'geometric_asl_m' &&
    value.is_fine_dem === false;
}

export function GroundPreparation({candidate, source, onApply}: {
  candidate: Candidate; source?: WeatherSource; onApply: (altitude: number) => void;
}) {
  const binding = groundBinding(candidate, source);
  const current = useRef(binding); current.current = binding;
  const epoch = useRef(0), alive = useRef(true);
  const [reading, setReading] = useState<string | null>(null);
  const [observed, setObserved] = useState<{binding: string; value: GroundObservation} | null>(null);
  const [error, setError] = useState<{binding: string; message: string} | null>(null);
  const [clearance, setClearance] = useState(5);
  useEffect(() => { alive.current = true; return () => { alive.current = false; epoch.current++; }; }, []);
  async function inspect() {
    if (!binding || !source?.sha256) return;
    const requestEpoch = ++epoch.current;
    const launch = candidate.config.launch;
    const query = {time_utc: launch.time_utc, latitude_deg: launch.latitude_deg,
      longitude_deg: launch.longitude_deg, launch_altitude_m: launch.altitude_m};
    setReading(binding); setError(null);
    try {
      const value = await api.ground(source.id, source.sha256, query);
      if (!alive.current || requestEpoch !== epoch.current || current.current !== binding) return;
      if (!groundMatches(value, source, query)) throw Error('照会した気象・地点・時刻と応答が一致しません。保存気象を再確認してください。');
      setObserved({binding, value});
    } catch (reason) {
      if (alive.current && requestEpoch === epoch.current && current.current === binding)
        setError({binding, message: reason instanceof Error ? reason.message : String(reason)});
    } finally {
      if (alive.current && requestEpoch === epoch.current) setReading(null);
    }
  }
  const result = observed?.binding === binding ? observed.value : null;
  const problem = error?.binding === binding ? error.message : null;
  const difference = result ? candidate.config.launch.altitude_m - result.ground_altitude_m : null;
  return <div className="ground-preparation">
    <button type="button" disabled={!binding || reading === binding} onClick={() => void inspect()}>
      {reading === binding ? 'モデル地表を照会中…' : 'この地点・時刻のモデル地表を確認'}
    </button>
    {!binding && <small>気象の内容指紋と、有効な日時・座標・高度が必要です。</small>}
    {problem && <p role="alert">地表を確認できません：{problem}</p>}
    {observed && !result && <small>気象・地点・時刻が変わっています。地表を確認し直してください。</small>}
    {result && <>
      <p role="status">モデル地表 {result.ground_altitude_m.toFixed(2)} m ASL · 現在の放球高度との差 {difference!.toFixed(2)} m
        {difference! < 0 ? '（モデル地表より低い入力です）' : ''}</p>
      <label>モデル地表からの高さ m
        <input type="number" min="0" step="any" value={Number.isFinite(clearance) ? clearance : ''}
          onChange={event => setClearance(event.target.value === '' ? NaN : Number(event.target.value))}/>
      </label>
      <button type="button" disabled={!!problem || reading === binding || !Number.isFinite(clearance) || clearance < 0}
        onClick={() => onApply(result.ground_altitude_m + clearance)}>地表＋指定高さを放球高度へ反映</button>
    </>}
    <small>選んだ気象モデルの地形です。実測標高・詳細DEMとは異なります。地点を変えても高度は自動変更しません。時間窓と機体入力は計算前に検査し、飛行中に領域・高度支持を外れれば停止します。</small>
  </div>;
}
