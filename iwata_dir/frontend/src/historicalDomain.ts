import type {Candidate,WeatherSource} from './domain';
import {stableString} from './domain';
import type {EnsemblePlan,PlanRequest} from './ensembleDomain';
import type {CaseResult} from './ensembleDomain';

import type {HistoricalWindow,HistoricalSampling} from './historicalTypes';
export type {HistoricalWindow,HistoricalSampling} from './historicalTypes';
export type HistoricalRequest={mode:'historical_windows';client_request_id:string;label:string;windows:HistoricalWindow[];reason:string;selection_context:Record<string,unknown>;cases:PlanRequest['cases']};
export type HistoricalPlan=Pick<EnsemblePlan,'plan_id'|'plan_hash'|'status'|'trial_count'|'runnable_trial_count'|'invalid_trial_count'> & {mode:'historical_windows';sampling:HistoricalSampling;weather_windows:HistoricalWindow[];draws:{draw_id:string;ordinal:number;weather_window:HistoricalWindow}[];trials:{case_id:string;draw_id:string;preflight_error:{code:string;message:string}|null;weather_window:HistoricalWindow}[]};
export type HistoricalDraft={windows:HistoricalWindow[];reason:string;selection_context:Record<string,unknown>};
export type HistoricalSaved={draft:HistoricalDraft;plan_id?:string;plan_input?:string;pending?:{kind:'plan'|'submit';request_id:string;body:any}};

export function historicalInput(candidate:Candidate,draft:HistoricalDraft):HistoricalRequest{
 if(!draft.windows.length)throw Error('試す原日時を追加してください。');
 if(!draft.reason.trim())throw Error('この原日時集合を選ぶ理由を記してください。');
 if(draft.windows.length>256)throw Error('この計画の運用上限は256原日時です。');
 if(draft.windows.some(w=>!w.reason.trim()))throw Error('各原日時を選ぶ理由も記してください。');
 const times=draft.windows.map(w=>Date.parse(w.launch_time_utc));
 if(times.some(t=>!Number.isFinite(t)))throw Error('全ての原放球日時を指定してください。');
 if(new Set(times).size!==times.length)throw Error('同じ原放球日時を重複して数えないようにしてください。');
 return {mode:'historical_windows',client_request_id:'',label:candidate.label,windows:structuredClone(draft.windows),reason:draft.reason,selection_context:structuredClone(draft.selection_context),cases:[{case_id:candidate.id,candidate_id:candidate.id,candidate_revision:candidate.revision,label:candidate.label,parent_case_id:null,delay_minutes:null,config:structuredClone(candidate.config)}]};
}
export function historicalMatches(candidate:Candidate,submitted:Candidate['config']):boolean{
 const normalize=(c:Candidate['config'])=>{const value=structuredClone(c) as any;delete value.launch.time_utc;return value;};
 return stableString(normalize(candidate.config))===stableString(normalize(submitted));
}
/** Compare user intent, not added availability metadata or UTC spelling. */
export function historicalSelectionMatches(draft:HistoricalDraft|undefined,value:CaseResult):boolean{
 if(!draft)return true; // Read-only orphan result has no current window draft.
 const windows=(rows:HistoricalWindow[])=>rows.map(w=>({window_id:w.window_id,label:w.label,weather_source_id:w.weather_source_id,launch_ms:Date.parse(w.launch_time_utc),reason:w.reason}));
 return stableString(windows(draft.windows))===stableString(windows(value.weather_windows??[]))&&draft.reason===value.sampling.reason&&stableString(draft.selection_context)===stableString(value.selection_context??{});
}
export function sourceWindowIssue(window:HistoricalWindow,config:Candidate['config'],sources:WeatherSource[]):string|null{
 const source=sources.find(s=>s.id===window.weather_source_id);if(!source)return '原日時場が未登録です。対象として残り、飛行は行えません。';
 if(source.time_kind!=='analysis_valid_utc')return '原UTCを持つ再解析場を選んでください。';
 const launch=Date.parse(window.launch_time_utc),end=launch+Number(config.integration?.max_duration_s??14400)*1000;
 if(!Number.isFinite(launch))return '原放球日時を指定してください。';
 const times=source.valid_times_utc,b=source.bounds;if(!times?.length||!b)return '登録場の時空間支持を確認できません。';
 if(launch<Date.parse(times[0])||end>Date.parse(times.at(-1)!))return '放球から最大計算時間までを、この場では支えられません。';
 if(config.launch.latitude_deg<b.lat[0]||config.launch.latitude_deg>b.lat[1]||config.launch.longitude_deg<b.lon[0]||config.launch.longitude_deg>b.lon[1])return '放球点がこの場の領域外です。';
 return null;
}
