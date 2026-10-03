import {switchModel,type ModelDrafts} from './modelDrafts';
import {GroundPreparation} from './GroundPreparation';
import type { Candidate, Config, WeatherSource } from "./domain";
import { jstInputToUtc, utcToJstInput, weatherSourceSummary } from "./domain";

export function ConfigEditor({
  candidate,
  sources,
  onChange,
  models = {},
}: {
  candidate: Candidate;
  sources: WeatherSource[];
  models?: ModelDrafts;
  onChange: (c: Candidate, cache?:ModelDrafts) => void;
}) {
  const c = candidate.config;
  const choose=(section:keyof ModelDrafts, mode:string)=>{const next=switchModel(c,models,section,mode);onChange({...candidate,revision:candidate.revision+1,config:next.config},next.cache);};
  const update = (patch: Partial<Config>) =>
    onChange({
      ...candidate,
      revision: candidate.revision + 1,
      config: { ...c, ...patch },
    });
  const number = (
    section: "launch" | "ascent" | "burst" | "descent",
    key: string,
    label: string,
    step = "any",
  ) => {
    const value = (c[section] as Record<string, unknown>)[key];
    return (
      <label>
        {label}
        <input
          type="number"
          step={step}
          value={
            typeof value === "number" && Number.isFinite(value) ? value : ""
          }
          onChange={(e) =>
            update({
              [section]: {
                ...c[section],
                [key]: e.target.value === "" ? NaN : Number(e.target.value),
              },
            })
          }
        />
      </label>
    );
  };
  return (
    <div className="editor">
      <label>
        候補名
        <input
          value={candidate.label}
          onChange={(e) =>
            onChange({
              ...candidate,
              label: e.target.value,
              revision: candidate.revision + 1,
            })
          }
        />
      </label>
      {candidate.analysis_mode!=='historical_windows'&&<><label>
        使う保存気象
        <select
          value={candidate.weather_source_id}
          onChange={(e) =>
            onChange({
              ...candidate,
              weather_source_id: e.target.value,
              revision: candidate.revision + 1,
            })
          }
        >
          {!sources.some(s=>s.id===candidate.weather_source_id)&&<option value={candidate.weather_source_id}>{candidate.weather_source_id}（現在利用できません・固定結果は保持）</option>}
          {sources.map((s) => (
            <option key={s.id} value={s.id}>
              {s.label ?? s.id}
            </option>
          ))}
        </select>
      </label>
      {sources.find(s=>s.id===candidate.weather_source_id)&&<div className="muted">{weatherSourceSummary(sources.find(s=>s.id===candidate.weather_source_id)!).map(text=><p key={text}>{text}</p>)}</div>}</>}
      <fieldset>
        <legend>放球条件</legend>
        {candidate.analysis_mode==='historical_windows'?<p>放球日時と気象場は下の「原日時の気象窓」で指定します。ここでは全日時で共通の地点・ASL・機体を編集します。</p>:<label>
          放球日時（JST）
          <input
            type="datetime-local"
            step="1"
            value={utcToJstInput(c.launch.time_utc)}
            onChange={(e) => {
              if (e.target.value)
                update({
                  launch: {
                    ...c.launch,
                    time_utc: jstInputToUtc(e.target.value),
                  },
                });
            }}
          />
        </label>}
        <div className="fields">
          {number("launch", "latitude_deg", "緯度 °N")}
          {number("launch", "longitude_deg", "経度 °E")}
          {number("launch", "altitude_m", "高度 m（幾何ASL）")}
        </div>
        {candidate.analysis_mode!=='historical_windows'&&<GroundPreparation candidate={candidate} source={sources.find(s=>s.id===candidate.weather_source_id)}
          onApply={altitude_m=>update({launch:{...c.launch,altitude_m}})}/>}
      </fieldset>
      <fieldset>
        <legend>上昇</legend>
        <label>
          上昇モデル
          <select
            value={c.ascent.mode}
            onChange={e=>choose('ascent',e.target.value)}
          >
            <option value="constant_speed">定速上昇</option>
            <option value="isothermal_buoyancy">等温浮力・準定常</option>
          </select>
        </label>
        <div className="fields">
          {c.ascent.mode === "constant_speed" ? (
            number("ascent", "speed_m_s", "上昇速度 m/s")
          ) : (
            <>
              {number("ascent", "gas_mass_kg", "Heガス質量 kg")}
              {number("ascent", "envelope_mass_kg", "膜質量 kg")}
              {number("ascent", "payload_mass_kg", "搭載質量 kg")}
              {number("ascent", "drag_coefficient", "抗力係数 Cd")}
            </>
          )}
        </div>
      </fieldset>
      <fieldset>
        <legend>破裂</legend>
        <label>
          破裂条件
          <select
            value={c.burst.mode}
            onChange={e=>choose('burst',e.target.value)}
          >
            <option value="altitude">指定高度</option>
            <option
              value="diameter"
              disabled={c.ascent.mode !== "isothermal_buoyancy"}
            >
              指定径（等温浮力のとき）
            </option>
          </select>
        </label>
        {c.burst.mode === "altitude"
          ? number("burst", "altitude_m", "破裂高度 m（幾何ASL）")
          : number("burst", "diameter_m", "破裂径 m")}
        {c.ascent.mode === "constant_speed" && c.burst.mode === "diameter" && (
          <p className="notice">
            定速上昇＋径破裂は現核で未対応です。径は保持しています。指定高度へ明示的に変更するか、上昇を等温浮力へ戻してください。
          </p>
        )}
      </fieldset>
      <fieldset>
        <legend>降下</legend>
        <label>
          降下モデル
          <select
            value={c.descent.mode}
            onChange={e=>choose('descent',e.target.value)}
          >
            <option value="rated_speed">基準下降速度</option>
            <option value="constant_cda">質量と定CdA</option>
          </select>
        </label>
        <div className="fields">
          {c.descent.mode === "rated_speed" ? (
            <>
              {number("descent", "reference_speed_m_s", "基準下降速度 m/s")}
              <label>
                密度則
                <select
                  value={c.descent.density_model}
                  onChange={e=>choose('density',e.target.value)}
                >
                  <option value="weather">保存気象の密度</option>
                  <option value="exponential">高度の指数則</option>
                </select>
              </label>
              {c.descent.density_model === "weather"
                ? number("descent", "reference_density_kg_m3", "基準密度 kg/m³")
                : number("descent", "scale_height_m", "スケール高さ m")}
            </>
          ) : (
            <>
              {number("descent", "mass_kg", "降下質量 kg")}
              {number("descent", "drag_area_m2", "CdA m²")}
            </>
          )}
        </div>
      </fieldset>
      <small>
        方式ごとの編集値を保持します。初めて選ぶ方式だけ初期値を使用し、計算には現在選んだ方式の入力を渡します。
      </small>
      <label>飛行を追う最大時間 h
        <input type="number" min="0.01" step="0.5" value={typeof c.integration?.max_duration_s==='number'?c.integration.max_duration_s/3600:4} onChange={e=>update({integration:{...c.integration,max_duration_s:e.target.value===''?NaN:Number(e.target.value)*3600}})}/>
        <small>放球からこの時間まで、選んだ保存気象の時間支持が必要です。GFSの取得計画にもこの窓を含めます。到達前に場が尽きた飛行は停止します。</small>
      </label>
      <details>
        <summary>数値積分の設定</summary>
        <pre>{JSON.stringify(c.integration, null, 2)}</pre>
        <p>最大時間以外は保存例の数値設定を使用します。</p>
      </details>
    </div>
  );
}
