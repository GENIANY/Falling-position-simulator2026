import {jstLabel,stableString} from '../../domain';
/** A portable figure must carry its fixed conditions, even for one candidate. */
export function fixedConditionFields(result:any){
 const c=result.conditions.realConfig,s=result.collection?.weather_snapshot??result.envelope?.weather_snapshot??{},sampling=result.collection?.sampling??result.conditions.sampling;
 const historical=sampling?.mode==='historical_windows';
 const fields:{label:string;value:string}[]=[
  {label:'放球日時',value:historical?'明示選択した原日時窓（各標本の日時を使用）':jstLabel(c.launch.time_utc)+' / '+c.launch.time_utc},
  {label:'放球点',value:`${c.launch.latitude_deg}, ${c.launch.longitude_deg}° / ${c.launch.altitude_m} m ASL`},
  {label:'上昇',value:c.ascent.mode==='constant_speed'?`定速 ${c.ascent.speed_m_s} m/s`:`等温浮力・準定常 / He ${c.ascent.gas_mass_kg} kg / 膜 ${c.ascent.envelope_mass_kg} kg / 搭載 ${c.ascent.payload_mass_kg} kg / Cd ${c.ascent.drag_coefficient}`},
  {label:'破裂',value:c.burst.mode==='altitude'?`${c.burst.altitude_m} m ASL`:`径 ${c.burst.diameter_m} m`},
  {label:'降下',value:c.descent.mode==='constant_cda'?`質量 ${c.descent.mass_kg} kg / CdA ${c.descent.drag_area_m2} m²`:`基準 ${c.descent.reference_speed_m_s} m/s / ${c.descent.density_model==='weather'?`気象密度（基準 ${c.descent.reference_density_kg_m3} kg/m³）`:`指数則 ${c.descent.scale_height_m} m`}`},
  {label:'気象',value:historical?'原日時ごとに固定した保存場':String(s.label??s.id??result.conditions.weatherId)},
  {label:'標本',value:historical?`${sampling.n}原日時窓 / ${sampling.reason} / 季節代表性未評価`:sampling?`${sampling.n}標本 / ${sampling.variable} 一様 ${sampling.distribution.low}–${sampling.distribution.high} ${sampling.unit} / seed ${sampling.seed} / 理由 ${sampling.reason}`:'指定条件の一飛行（n=1）'}
 ];
 if(!historical){if(s.run_utc)fields.push({label:'予報初期時刻',value:s.run_utc});if(s.valid_times_utc?.length)fields.push({label:'気象の有効UTC',value:s.valid_times_utc[0]+' ～ '+s.valid_times_utc.at(-1)});if(s.sha256)fields.push({label:'気象SHA-256',value:s.sha256});}
 return fields;
}
export function fixedConditionSummary(tabs:any[]){
 const rows=tabs.map(t=>fixedConditionFields(t.result)),labels=[...new Set(rows.flatMap(row=>row.map(f=>f.label)))],common:{label:string;value:string}[]=[],different:{label:string;values:string[]}[]=[];
 for(const label of labels){const values=rows.map(row=>row.find(f=>f.label===label)?.value??'—');if(values.every(v=>v===values[0]))common.push({label,value:values[0]});else different.push({label,values});}
 // Numerical settings are compact unless they differ; preserve those differences.
 const numerics=tabs.map(t=>stableString(t.result.conditions.realConfig.integration??{}));if(new Set(numerics).size>1)different.push({label:'数値設定',values:numerics});
 return {common,different};
}
/** Wind distributions require all selected histories that are still in flight. */
export function figureReadIssue(target:string,tabs:any[],selectedIds:string[],time:number,group=false):string|null{
 for(const t of tabs){if(t.result?.kind!=='ensemble')continue;const a=t.renderAnalysis;if(!a)return '固定した選択群の分析を読込中です。';
  if(target==='historyChart'&&a.history?.unavailable_reason)return '履歴分析の上限に達したため、この履歴図を保存できません。標本を絞ってください。';
  if(target!=='historyChart'){
   const selected=new Set(selectedIds),expected=t.result.collection.trials.filter((r:any)=>selected.has(r.trial_id)&&r.result_available&&((r.state==='landed'?r.landing:r.last_valid_point)?.elapsed_s??0)>time*60);
   const loaded=new Set((t.result.realSamples??[]).filter((s:any)=>s.historyLoaded&&s.history?.length).map((s:any)=>s.id));
   const missing=expected.filter((r:any)=>!loaded.has(r.trial_id)).length;if(missing)return `飛行中の対象 ${expected.length}件のうち原履歴 ${missing}件が未読または読取失敗です。読込みを完了してから風の図を保存してください。`;
  }
 }return null;
}
