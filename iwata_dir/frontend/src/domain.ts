import type {SamplingSpec,FixedResultRef} from './ensembleDomain';
export type Config = {
  schema: string;
  label?: string;
  purpose?: string;
  launch: {
    time_utc: string;
    latitude_deg: number;
    longitude_deg: number;
    altitude_m: number;
  };
  ascent: Record<string, number | string>;
  burst: Record<string, number | string>;
  descent: Record<string, number | string>;
  integration?: Record<string, unknown>;
};
export type Candidate = {
  id: string;
  label: string;
  revision: number;
  weather_source_id: string;
  parent_id?: string | null;
  delay_minutes?: number | null;
  config: Config;
  sampling?: SamplingSpec | null;
  analysis_mode?: 'forecast' | 'historical_windows';
};
export type Project = {
  schema: "balloon.project/1";
  title: string;
  candidates: Candidate[];
  compare_run_ids: string[];
  compare_results?: FixedResultRef[] | null;
  ui_state?: Record<string, any>;
};
export type WeatherSource = {
  id: string;
  label?: string;
  sha256?: string;
  run_utc?: string | null;
  schema?: string;
  product?: string;
  time_kind?: string;
  metadata?: Record<string, unknown>;
  valid_times_utc?: string[];
  bounds?: { lat: number[]; lon: number[]; pressure_pa?: number[]; model_level?: number[] };
  default_config: Config | null;
  [key: string]: unknown;
};
export type FlightPoint = {
  elapsed_s: number;
  time_utc: string;
  latitude_deg: number;
  longitude_deg: number;
  altitude_m: number;
  phase: string;
  ground_altitude_m?: number;
  [key: string]: unknown;
};
export type FlightEvent = {
  type: string;
  elapsed_s: number;
  time_utc?: string;
  latitude_deg: number;
  longitude_deg: number;
  altitude_m: number;
};
export type FlightResult = {
  schema: string;
  status: "landed" | "stopped";
  config: Config;
  records: FlightPoint[];
  events: FlightEvent[];
  stop_reason: { code: string; message: string } | null;
  summary: {
    duration_s: number;
    maximum_altitude_m: number | null;
    landing: FlightEvent | null;
  };
  model_assumptions?: string[];
};
export type ResultEnvelope = {
  run_id: string;
  trial_id: string;
  n: 1;
  weight: 1;
  result: FlightResult;
  weather_snapshot: Record<string, unknown>;
  source_snapshot: Record<string, unknown>;
};
export type Run = {
  kind?: "single_run" | "ensemble_trial";
  ensemble?: Record<string,unknown> | null;
  run_id: string;
  job_id?: string;
  candidate_id?: string;
  candidate_revision?: number;
  label?: string;
  state?: string;
  result_available?: boolean;
  weather_source_id?: string;
  spec?: {
    submitted_input: { config: Config; weather_source_id: string };
    weather_snapshot?: Record<string, unknown>;
    [key: string]: unknown;
  };
  [key: string]: unknown;
};
export type DisplayRun = {
  id: string;
  label: string;
  color: string;
  envelope: ResultEnvelope;
  visible: boolean;
};
export const COLORS = ["#006f8b", "#b45617", "#6653a6", "#8b374f"];
export const emptyProject = (): Project => ({
  schema: "balloon.project/1",
  title: "保存気象で条件を比較",
  candidates: [],
  compare_run_ids: [],
});
export function utcToJstInput(utc: string): string {
  const d = new Date(utc);
  return Number.isNaN(d.valueOf())
    ? ""
    : new Date(d.valueOf() + 9 * 3600_000).toISOString().slice(0, 19);
}
export function jstInputToUtc(local: string): string {
  const d = new Date(local + "+09:00");
  if (!local || Number.isNaN(d.valueOf()))
    throw Error("日時を入力してください。");
  return d.toISOString();
}
export const jstLabel = (utc: string) =>
  utcToJstInput(utc).replace("T", " ") + " JST";
export const utcLabel = (value: string) =>
  Number.isFinite(Date.parse(value)) ? new Date(value).toISOString().slice(0, 19).replace("T", " ") + " UTC" : "時刻不明";
export function stableString(value: unknown): string {
  if (Array.isArray(value))
    return "[" + value.map(stableString).join(",") + "]";
  if (value && typeof value === "object")
    return (
      "{" +
      Object.entries(value)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([k, v]) => JSON.stringify(k) + ":" + stableString(v))
        .join(",") +
      "}"
    );
  return JSON.stringify(value);
}
export function pointAt(
  rows: FlightPoint[],
  elapsed: number,
): FlightPoint | null {
  if (!rows.length) return null;
  if (elapsed <= rows[0].elapsed_s) return rows[0];
  const end = rows.at(-1)!;
  if (elapsed >= end.elapsed_s) return end;
  let lo = 0,
    hi = rows.length - 1;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (rows[mid].elapsed_s <= elapsed) lo = mid;
    else hi = mid;
  }
  const a = rows[lo],
    b = rows[hi],
    f = (elapsed - a.elapsed_s) / (b.elapsed_s - a.elapsed_s);
  // Interpolation is for the cursor only; original records and events remain unchanged.
  const dlon = ((b.longitude_deg - a.longitude_deg + 540) % 360) - 180;
  return {
    ...a,
    elapsed_s: elapsed,
    latitude_deg: a.latitude_deg + (b.latitude_deg - a.latitude_deg) * f,
    longitude_deg: ((a.longitude_deg + dlon * f + 540) % 360) - 180,
    altitude_m: a.altitude_m + (b.altitude_m - a.altitude_m) * f,
  };
}
export function phases(rows: FlightPoint[]): FlightPoint[][] {
  const parts: FlightPoint[][] = [];
  for (const p of rows) {
    const last = parts.at(-1);
    if (!last) parts.push([p]);
    else if (last.at(-1)!.phase === p.phase) last.push(p);
    else {
      last.push(p);
      parts.push([p]);
    }
  }
  return parts;
}
export function differences(a: unknown, b: unknown, prefix = ""): string[] {
  if (stableString(a) === stableString(b)) return [];
  if (
    a &&
    b &&
    typeof a === "object" &&
    typeof b === "object" &&
    !Array.isArray(a) &&
    !Array.isArray(b)
  ) {
    const aa = a as Record<string, unknown>,
      bb = b as Record<string, unknown>;
    return [...new Set([...Object.keys(aa), ...Object.keys(bb)])]
      .sort()
      .flatMap((k) => differences(aa[k], bb[k], prefix ? prefix + "." + k : k));
  }
  return [prefix];
}
export function describeConfig(c: Config): string {
  const ascent =
    c.ascent.mode === "constant_speed"
      ? `定速 ${c.ascent.speed_m_s} m/s`
      : "等温浮力";
  const burst =
    c.burst.mode === "altitude"
      ? `破裂高度 ${Number(c.burst.altitude_m) / 1000} km`
      : `破裂径 ${c.burst.diameter_m} m`;
  return `${ascent} / ${burst} / ${c.descent.mode === "rated_speed" ? "基準下降速度 " + c.descent.reference_speed_m_s + " m/s" : "定CdA降下"}`;
}
export function draftInputsMatchRun(candidate: Candidate, run: Run): boolean {
  if(candidate.sampling)return false;
  const submitted = run.spec?.submitted_input;
  if (!submitted)
    return (
      candidate.revision === run.candidate_revision &&
      candidate.weather_source_id === run.weather_source_id
    );
  return (
    candidate.weather_source_id === submitted.weather_source_id &&
    stableString(candidate.config) === stableString(submitted.config)
  );
}
/** Current catalogue identity never replaces a frozen result's weather snapshot. */
export function weatherIdentity(source?: Record<string, unknown> | null) {
  const metadata = source?.metadata as Record<string, unknown> | undefined;
  const reconstruction = source?.reconstruction as Record<string, unknown> | undefined;
  return {
    sha256: source?.sha256,
    schema: source?.schema ?? metadata?.schema,
    product: source?.product ?? metadata?.product,
    policy: metadata?.reconstruction_policy ?? reconstruction?.policy,
    joins: metadata?.join_model_levels ?? reconstruction?.join_model_levels,
  };
}
export type WeatherMatch = { state: 'same' | 'changed' | 'unavailable' | 'unverified'; message: string };
export function weatherMatch(current?: Record<string, unknown> | null, fixed?: Record<string, unknown> | null): WeatherMatch {
  if (!current) return {state:'unavailable',message:'現在の保存気象が利用できず、一致を確認できません。表示中の固定結果は保持しています。'};
  const a=weatherIdentity(current), b=weatherIdentity(fixed);
  if (typeof a.sha256 !== 'string' || !/^[0-9a-f]{64}$/i.test(a.sha256) || typeof b.sha256 !== 'string' || !/^[0-9a-f]{64}$/i.test(b.sha256))
    return {state:'unverified',message:'気象資料の照合情報が不足しています。表示中の固定結果と現在条件の一致は未確認です。'};
  if (a.sha256.toLowerCase()!==b.sha256.toLowerCase() || (['schema','product','policy','joins'] as const).some(k=>a[k]!=null&&b[k]!=null&&stableString(a[k])!==stableString(b[k])))
    return {state:'changed',message:'固定結果の計算時から気象資料の内容が変わっています。現在の資料で計算し直すまで、表示結果は以前の資料によるものです。'};
  if ((['schema','product','policy','joins'] as const).some(k=>(a[k]==null)!==(b[k]==null)))
    return {state:'unverified',message:'気象資料の照合情報が揃っていません。表示中の固定結果と現在条件の一致は未確認です。'};
  return {state:'same',message:''};
}
export function runWeatherSnapshot(run: Run, envelope?: ResultEnvelope): Record<string, unknown> | undefined {
  return run.spec?.weather_snapshot ?? envelope?.weather_snapshot;
}
export function draftMatchesRun(candidate: Candidate, run: Run, current?: WeatherSource, envelope?: ResultEnvelope): boolean {
  return draftInputsMatchRun(candidate,run) && weatherMatch(current,runWeatherSnapshot(run,envelope)).state==='same';
}
/** Describes actual saved data, separately from the GFS acquisition controls. */
export function weatherSourceSummary(source: WeatherSource): string[] {
  const jra=source.kind==='saved_jra3q'||String(source.product??'').startsWith('jra3q.');
  const times=source.valid_times_utc??[];
  const rows=[jra?'JRA-3Qの保存解析場（予報ではありません）':source.kind==='acquired_gfs'?'取得して保存したGFS予報':'保存GFSの例'];
  if(!jra&&source.run_utc)rows.push('予報初期時刻 '+utcLabel(source.run_utc));
  if(times.length)rows.push('場の有効時刻 '+utcLabel(times[0])+' ～ '+utcLabel(times.at(-1)!)+' · '+times.length+'時刻');
  if(jra){
    if(source.bounds?.model_level)rows.push('モデル面 '+source.bounds.model_level.join('–')+'（気圧面ではありません）');
    rows.push('地表の温湿度（2 m）・風（10 m）からモデル面へつなぐ暫定方式です。');
    rows.push('着地は気象モデルの地形で判定します。実地形・建物との接触計算ではありません。');
  }
  return rows;
}
export function differenceLabel(path: string): string {
  return (
    (
      {
        "launch.time_utc": "放球日時（UTC）",
        "launch.latitude_deg": "緯度 °N",
        "launch.longitude_deg": "経度 °E",
        "launch.altitude_m": "放球高度 m ASL",
        "ascent.mode": "上昇モデル",
        "ascent.speed_m_s": "上昇速度 m/s",
        "ascent.gas_mass_kg": "ガス質量 kg",
        "ascent.envelope_mass_kg": "膜質量 kg",
        "ascent.payload_mass_kg": "搭載質量 kg",
        "ascent.drag_coefficient": "抗力係数 Cd",
        "burst.mode": "破裂方式",
        "burst.altitude_m": "破裂高度 m ASL",
        "burst.diameter_m": "破裂径 m",
        "descent.mode": "降下モデル",
        "descent.reference_speed_m_s": "基準下降速度 m/s",
        "descent.density_model": "下降の密度則",
      } as Record<string, string>
    )[path] ?? path
  );
}
export function valueAt(config: Config, path: string): string {
  const value = path
    .split(".")
    .reduce<unknown>(
      (v, key) =>
        v && typeof v === "object"
          ? (v as Record<string, unknown>)[key]
          : undefined,
      config,
    );
  return value === undefined ? "使用しない" : String(value);
}
export function draftIssue(c: Config): string | null {
  const maximum=c.integration?.max_duration_s??14400;
  if(typeof maximum!=='number'||!Number.isFinite(maximum)||maximum<=0)return '飛行を追う最大時間に正の数を入力してください。';
  if (c.ascent.mode === "constant_speed" && c.burst.mode === "diameter")
    return "定速上昇＋径破裂は未対応です。破裂方式か上昇モデルを選び直してください。";
  const groups = [c.launch, c.ascent, c.burst, c.descent];
  if (
    groups.some((group) =>
      Object.entries(group).some(
        ([key, value]) =>
          !["mode", "time_utc", "density_model"].includes(key) &&
          (typeof value !== "number" || !Number.isFinite(value)),
      ),
    )
  )
    return "空欄の数値を入力してから計算してください。";
  return null;
}
export function supportAreas(
  runs: {
    visible: boolean;
    envelope: Pick<ResultEnvelope, "weather_snapshot">;
  }[],
): { key: string; label: string; lat: number[]; lon: number[] }[] {
  const seen = new Map<
    string,
    { key: string; label: string; lat: number[]; lon: number[] }
  >();
  for (const run of runs.filter((r) => r.visible)) {
    const source = run.envelope.weather_snapshot;
    const bounds = source.bounds as
      | { lat?: unknown; lon?: unknown }
      | undefined;
    if (
      !Array.isArray(bounds?.lat) ||
      !Array.isArray(bounds?.lon) ||
      bounds.lat.length !== 2 ||
      bounds.lon.length !== 2
    )
      continue;
    if (
      ![...bounds.lat, ...bounds.lon].every(
        (v) => typeof v === "number" && Number.isFinite(v),
      )
    )
      continue;
    const key = String(source.sha256 ?? source.id) + stableString(bounds);
    seen.set(key, {
      key,
      label: String(source.label ?? source.id ?? "保存気象"),
      lat: bounds.lat,
      lon: bounds.lon,
    });
  }
  return [...seen.values()];
}

/** A selected child represents its dependent family until it is detached. */
export function candidateFamily(candidates:Candidate[],ids:string[]):Candidate[]{
 const selected=new Set(ids.filter(id=>candidates.some(c=>c.id===id)));
 let changed=true;while(changed){changed=false;for(const c of candidates)if(selected.has(c.id)&&c.parent_id&&!selected.has(c.parent_id)){selected.add(c.parent_id);changed=true;}}
 changed=true;while(changed){changed=false;for(const c of candidates)if(c.parent_id&&selected.has(c.parent_id)&&!selected.has(c.id)){selected.add(c.id);changed=true;}}
 return candidates.filter(c=>selected.has(c.id));
}
