import type {FixedResultRead} from '../../fixedResultRead';
import type { Candidate, Config, FlightPoint, ResultEnvelope, Run, WeatherSource } from '../../domain';
import { utcToJstInput, COLORS, draftInputsMatchRun, weatherMatch, runWeatherSnapshot } from '../../domain';
export function conditions(config: Config, weatherId: string) {
 const input=utcToJstInput(config.launch.time_utc);
 return {realConfig:structuredClone(config),weatherId,model:config.ascent.mode==='constant_speed'?'simple':'isothermal',origin:[config.launch.latitude_deg,config.launch.longitude_deg],date:input.slice(0,10),time:input.slice(11,19),mass:typeof config.ascent.payload_mass_kg==='number'?config.ascent.payload_mass_kg:null,forecast:weatherId,burstDiameter:config.burst.diameter_m??null};
}
/** Draw-only interpolation of accepted irregular records. Original results remain unchanged. */
export function recordAt(records: FlightPoint[], elapsed: number): FlightPoint | null {
 if(!records.length)return null;
 if(elapsed<=records[0].elapsed_s)return records[0];
 if(elapsed>=records.at(-1)!.elapsed_s)return records.at(-1)!;
 let i=0;while(i+1<records.length&&records[i+1].elapsed_s<=elapsed)i++;
 const a=records[i],b=records[i+1],f=(elapsed-a.elapsed_s)/(b.elapsed_s-a.elapsed_s);
 const out:FlightPoint={...a,elapsed_s:elapsed};
 for(const key of ['latitude_deg','longitude_deg','altitude_m','eastward_wind_m_s','northward_wind_m_s','vertical_speed_m_s']){const av=a[key],bv=b[key];out[key]=typeof av==='number'&&typeof bv==='number'?av+(bv-av)*f:null;}
 return out;
}
export function sample(envelope: ResultEnvelope) {
 const r=envelope.result,rows=r.records,last=rows.at(-1);if(!last)return [];
 const origin=r.config.launch,cos=Math.cos(origin.latitude_deg*Math.PI/180),duration=last.elapsed_s/60;
 let distance=0,previous:{e:number;n:number}|null=null;
 const history=rows.map(p=>{
  const e=(p.longitude_deg-origin.longitude_deg)*111.2*cos,n=(p.latitude_deg-origin.latitude_deg)*111.2;
  if(previous)distance+=Math.hypot(e-previous.e,n-previous.n);previous={e,n};
  const u=typeof p.eastward_wind_m_s==='number'?p.eastward_wind_m_s:null,v=typeof p.northward_wind_m_s==='number'?p.northward_wind_m_s:null;
  return {t:p.elapsed_s/60,e,n,h:p.altitude_m/1000,phase:p.phase==='ascent'?'up':'down',distance,speed:u!==null&&v!==null?Math.hypot(u,v):null,vertical:typeof p.vertical_speed_m_s==='number'?p.vertical_speed_m_s:null,u,v};
 });
 const burstEvent=r.events.find(e=>e.type==='burst');const burst=burstEvent?burstEvent.elapsed_s/60:null;
 return [{id:envelope.trial_id||envelope.run_id,status:r.status==='landed'?'landed':'stopped',lat:last.latitude_deg,lon:last.longitude_deg,duration,burst,history,historyIsTimed:true,stopReason:r.stop_reason}];
}
export function projectTabs(candidates: Candidate[],runs:Run[],results:Record<string,ResultEnvelope>,selected:string[],view:Record<string,any>={},reads:Record<string,FixedResultRead>={},sources:WeatherSource[]=[]) {
 return candidates.map((c,index)=>{const run=runs.find(r=>r.candidate_id===c.id&&selected.includes(r.run_id)),env=run?results[run.run_id]:undefined;
  const result=env?{id:env.run_id,conditions:conditions(env.result.config,String(env.weather_snapshot.id??run?.weather_source_id??c.weather_source_id)),artificial:false,realSamples:sample(env),envelope:env}:null;
  const resultRead=env?{state:'ready' as const}:run?reads[run.run_id]??{state:'loading' as const}:undefined;
  return {resultRead,id:view.codes?.[c.id]??c.id,sourceId:c.id,pending:run?!draftInputsMatchRun(c,run):true,weatherMatch:run?weatherMatch(sources.find(s=>s.id===c.weather_source_id),runWeatherSnapshot(run,env)):undefined,name:c.label,color:view.colors?.[view.codes?.[c.id]??c.id]??COLORS[index%COLORS.length],draft:conditions(c.config,c.weather_source_id),parentId:c.parent_id?(view.codes?.[c.parent_id]??c.parent_id):undefined,delay:c.delay_minutes??undefined,result,results:result?[result]:[],visible:view.visibility?.[view.codes?.[c.id]??c.id]!==false};
 });
}

// A range input may serialize its maximum with fewer digits than the source
// duration. Snap only floating-point roundoff at the display endpoint; never
// extend a physical history or change the saved integration event.
export function elapsedSliderValue(value:number,maximum:number):number {
 return Math.abs(value-maximum)<=16*Number.EPSILON*Math.max(1,Math.abs(maximum))?maximum:value;
}
