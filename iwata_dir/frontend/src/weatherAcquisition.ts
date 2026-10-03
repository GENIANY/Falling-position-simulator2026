import type {Candidate,WeatherSource} from './domain';
import {candidateFamily} from './domain';
export type Dependencies={available:boolean;missing:{name:string;message:string}[];versions?:Record<string,string>};
export type Inventory={inventory_id:string;observed_at_utc:string;selection:string;runs:{run_utc:string;available_leads:number[];complete_lead_set:boolean}[];observation_status?:'complete'|'partial'|'unavailable';observation_errors?:{stage:'day'|'run';url:string;code:string;message:string;run_utc?:string;day?:string}[]};
export type AcquisitionBounds={west:number;east:number;south:number;north:number};
export type WeatherRegion={kind:'center';latitude_deg:number;longitude_deg:number;half_width_km:number;half_height_km:number}|({kind:'bounds'}&AcquisitionBounds);
export type AcquisitionRequest={inventory_id:string;run_utc:string;region:WeatherRegion;candidate_windows:{candidate_id:string;launch_time_utc:string;latitude_deg:number;longitude_deg:number;max_duration_s:number}[];end_margin_s:number;max_bytes:number;max_memory_bytes:number};
export type AcquisitionPlan={plan_id:string;cache_key?:string;status:'ready'|'unavailable';request:AcquisitionRequest;normalized_request:{run_utc:string;start_utc:string;end_utc:string;bounds:{west:number;east:number;south:number;north:number};lead_hours:number[]};required_window:{start_utc:string;end_utc:string};missing_leads:number[];issues:{code:string;message:string}[];estimate:{grid_points:number;time_count:number;scalar_values:number;float64_bytes:number;estimated_working_memory_bytes:number;max_memory_bytes:number;max_download_bytes:number;download_bytes_exact:boolean};dependencies:Dependencies;inventory_observed_at_utc:string};
export type AcquisitionJob={acquisition_id:string;plan_id:string;cache_key?:string;state:'queued'|'running'|'cancelling'|'completed'|'failed'|'cancelled'|'interrupted';attempt:number;progress:{phase:string;completed_files:number;total_files:number;bytes_downloaded:number;bytes_reused:number};weather_source_id:string|null;reused:boolean;cancellable:boolean;retryable:boolean;error:{code:string;message:string}|null};
export type AcquisitionForm={inventoryId:string;runUtc:string;fixedRun:string;latitude:number;longitude:number;halfWidth:number;halfHeight:number;maxMB:number;memoryMB:number;targetIds:string[];bounds?:AcquisitionBounds};
export const familyCandidates=candidateFamily;
function launchPoint(c:Candidate){const p=c.config.launch;if(!Number.isFinite(p.latitude_deg)||!Number.isFinite(p.longitude_deg)||p.latitude_deg<=-90||p.latitude_deg>=90||p.longitude_deg<-180||p.longitude_deg>180)throw Error(c.label+'の放球座標を確認してください。');return p;}
/** Explicit region edit only. This margin includes launch points, not trajectories. */
export function boundsForCandidates(candidates:Candidate[]):AcquisitionBounds{
 if(!candidates.length)throw Error('取得範囲へ含める候補を選んでください。');
 const points=candidates.map(launchPoint),lats=points.map(p=>p.latitude_deg),lons=points.map(p=>p.longitude_deg);
 if(Math.max(...lons)-Math.min(...lons)>180)throw Error('経度の継ぎ目をまたぐ候補は別の取得範囲に分けてください。');
 return{west:Math.max(-180,Math.floor((Math.min(...lons)-.25)*4)/4),east:Math.min(180,Math.ceil((Math.max(...lons)+.25)*4)/4),south:Math.max(-90,Math.floor((Math.min(...lats)-.25)*4)/4),north:Math.min(90,Math.ceil((Math.max(...lats)+.25)*4)/4)};
}
export function launchRegionIssue(bounds:AcquisitionBounds,candidates:Candidate[]):string|null{
 try{const outside=candidates.filter(c=>{const p=launchPoint(c);return p.latitude_deg<bounds.south||p.latitude_deg>bounds.north||![p.longitude_deg-360,p.longitude_deg,p.longitude_deg+360].some(lon=>lon>=bounds.west&&lon<=bounds.east);});return outside.length?'取得範囲外の放球点：'+outside.map(c=>c.label).join('・')+'。範囲を調整して計画を作り直してください。':null;}catch(e){return e instanceof Error?e.message:String(e);}
}
export function acquisitionRequest(form:AcquisitionForm,candidates:Candidate[]):AcquisitionRequest{
 const selected=familyCandidates(candidates,form.targetIds);
 if(!form.inventoryId||!form.runUtc)throw Error('配布一覧を確認し、使う初期時刻を選んでください。');
 if(!selected.length)throw Error('取得する気象を使う候補を選んでください。');
 for(const [name,value] of Object.entries({転送上限:form.maxMB,メモリ上限:form.memoryMB,...(form.bounds?form.bounds:{緯度:form.latitude,経度:form.longitude,東西片幅:form.halfWidth,南北片幅:form.halfHeight})}))if(!Number.isFinite(value))throw Error(name+'を数値で入力してください。');
 if(Math.min(form.maxMB,form.memoryMB)<=0||(!form.bounds&&(form.latitude<-85||form.latitude>85||form.longitude<-180||form.longitude>180||Math.min(form.halfWidth,form.halfHeight)<=0)))throw Error('座標と片幅・容量の範囲を確認してください。');
 if(form.bounds){const b=form.bounds;if(!(b.south>=-90&&b.south<b.north&&b.north<=90&&b.west>=-180&&b.west<b.east&&b.east<=180))throw Error('取得矩形の南北・東西端を確認してください。');if(b.west<0&&b.east>0)throw Error('経度0度の継ぎ目をまたぐ取得は未対応です。別の範囲へ分けてください。');}
 const windows=selected.map(c=>{const max=c.config.integration?.max_duration_s??14400,p=launchPoint(c);if(typeof max!=='number'||!Number.isFinite(max)||max<=0||!Number.isFinite(Date.parse(c.config.launch.time_utc)))throw Error(c.label+'の放球日時・最大飛行時間を確認してください。');return{candidate_id:c.id,launch_time_utc:p.time_utc,latitude_deg:p.latitude_deg,longitude_deg:p.longitude_deg,max_duration_s:max};});
 return{inventory_id:form.inventoryId,run_utc:form.runUtc,region:form.bounds?{kind:'bounds',...form.bounds}:{kind:'center',latitude_deg:form.latitude,longitude_deg:form.longitude,half_width_km:form.halfWidth,half_height_km:form.halfHeight},candidate_windows:windows,end_margin_s:0,max_bytes:Math.round(form.maxMB*1000000),max_memory_bytes:Math.round(form.memoryMB*1000000)};
}
/** A necessary support check, not trajectory or height assurance. */
export function sourceApplicationIssue(source:WeatherSource|undefined,candidates:Candidate[]):string|null{
 if(!source)return '完成した保存気象の情報を読み込んでください。';
 if(!candidates.length)return '適用する候補を選んでください。';
 const times=(source.valid_times_utc??[]).map(Date.parse).filter(Number.isFinite).sort((a,b)=>a-b);
 if(times.length<2)return 'この保存気象の時間支持を確認できません。';
 for(const c of candidates){const begin=Date.parse(c.config.launch.time_utc),duration=c.config.integration?.max_duration_s??14400,end=begin+Number(duration)*1000;
  if(!Number.isFinite(begin)||typeof duration!=='number'||!Number.isFinite(duration)||duration<=0)return c.label+'の日時・最大飛行時間を確認してください。';
  if(begin<times[0]||end>times.at(-1)!)return c.label+'の現在の飛行時間窓がこの保存気象の時間支持外です。'+(source.kind==='saved_jra3q'?'放球日時・最大時間または保存気象を見直してください。':'取得計画を見直してください。');
  const b=source.bounds,l=c.config.launch;if(!Number.isFinite(l.latitude_deg)||!Number.isFinite(l.longitude_deg))return c.label+'の放球座標を数値で入力してください。';if(!b||![...b.lat,...b.lon].every(Number.isFinite)||l.latitude_deg<b.lat[0]||l.latitude_deg>b.lat[1]||![l.longitude_deg-360,l.longitude_deg,l.longitude_deg+360].some(lon=>lon>=b.lon[0]&&lon<=b.lon[1]))return c.label+'の現在の放球地点がこの保存気象の領域外です。';
 }
 return null;
}

export function forecastValidTimes(plan:Pick<AcquisitionPlan,'normalized_request'>):string[]{const run=Date.parse(plan.normalized_request.run_utc);return plan.normalized_request.lead_hours.map(lead=>new Date(run+lead*3600000).toISOString());}
