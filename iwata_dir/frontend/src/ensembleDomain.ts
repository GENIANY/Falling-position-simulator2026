import type {Candidate, Config, FlightEvent, FlightPoint, Project, Run} from './domain';
import {candidateFamily,stableString} from './domain';
import type {HistoricalSampling,HistoricalWindow} from './historicalTypes';

export type SamplingSpec={variable:'gas_mass_kg'|'burst_altitude_m'|'reference_descent_speed_m_s';unit:string;distribution:{family:'uniform';low:number;high:number};reason:string;seed:number;n:number};
export type FixedResultRef={kind:'single_run';run_id:string}|{kind:'ensemble_case';ensemble_id:string;snapshot_id:string;case_id:string;analysis_id?:string|null};
export type TrialState='unstarted'|'queued'|'running'|'landed'|'stopped'|'invalid_input'|'failed'|'cancelled'|'interrupted';
export type Trial={trial_id:string;draw_id:string;ordinal:number;weight:number;parameter:{id:string;value:number;unit:string}|null;weather_window?:HistoricalWindow;state:TrialState;attempt:number;run_id:string|null;result_available:boolean;landing:FlightEvent|null;burst:FlightEvent|null;last_valid_point:FlightPoint|null;stop:{code:string;message:string}|null;error:unknown};
export type CaseResult={schema:string;mode?:'equipment_sensitivity'|'historical_windows';weather_windows?:HistoricalWindow[]|null;selection_context?:Record<string,unknown>|null;ensemble_id:string;snapshot_id:string;case_id:string;plan_id:string;drawset_id:string;epoch:number;candidate:{id:string;revision:number;label:string};sampling:SamplingSpec|HistoricalSampling;submitted_config:Config;resolved_base_config:Config;weather_snapshot:Record<string,any>;source_snapshot:Record<string,unknown>;settled:boolean;all_requested_have_physical_result:boolean;counts:Record<TrialState|'planned',number>;trials:Trial[];overview_analysis_id?:string|null;overview_analysis?:EnsembleAnalysis};
export type Geometry={type:'Point';coordinates:number[]}|{type:'LineString';coordinates:number[][]}|{type:'Polygon';coordinates:number[][][]};
export type Metric={mean:number|null;low:number|null;high:number|null;n:number};
export type HistoryRow={elapsed_s:number;n:number;metrics:Record<string,Metric>};
export type EnsembleAnalysis={schema:string;method:string;selected_trial_ids:string[];selected_count:number;completed_count:number;history_count:number;landing:{n:number;mean:{latitude_deg:number;longitude_deg:number}|null;rank:number|null;extent:Geometry|null;bands:{probability:number;rank_index:number;count:number;total:number;trial_ids:string[];geometry:Geometry|null;threshold:number|null}[]};history:{method:string;band:number[];grid_s:number[];unavailable_reason?:string|null;omitted_count?:number;available_history_count?:number;result_bytes?:number;byte_limit?:number;phases:{ascent:HistoryRow[];descent:HistoryRow[]}}};
export type AnalysisArtifact={analysis_id:string;snapshot_id:string;case_id:string;ensemble_id:string;selected_trial_ids:string[];analysis:EnsembleAnalysis;region_set:unknown;groups:unknown[];[key:string]:unknown};
export type EnsemblePlan={plan_id:string;plan_hash:string;status:string;sampling:SamplingSpec;drawset_id:string;draw_count:number;case_count:number;trial_count:number;runnable_trial_count:number;invalid_trial_count:number;cases:{case_id:string;candidate_id:string;candidate_revision:number;label:string;submitted_config:Config;resolved_base_config:Config}[];required_window:{start:string;end:string};weather_snapshot:{label?:string;id:string;valid_times_utc:string[]};draws:{draw_id:string;value:number;unit:string}[];blockers:{code:string;message:string;case_id?:string}[];warnings:{code:string;message:string}[];[key:string]:unknown};
export type EnsembleJob={ensemble_id:string;plan_id:string;state:string;epoch:number;state_revision:number;planned_trials:number;latest_snapshot_id:string|null;snapshots?:{snapshot_id:string;epoch:number}[];counts:Record<TrialState,number>;cancellable:boolean;retryable:boolean;cases:{case_id:string;planned:number}[];error:unknown};
export type PlanRequest={client_request_id:string;label:string;weather_source_id:string;sampling:SamplingSpec;cases:{case_id:string;candidate_id:string;candidate_revision:number;label:string;parent_case_id:string|null;delay_minutes:number|null;config:Config}[]};
export const samplingVariables=[{id:'gas_mass_kg',label:'ガス質量',unit:'kg',group:'ascent',field:'gas_mass_kg',mode:'isothermal'},{id:'burst_altitude_m',label:'破裂高度',unit:'m',group:'burst',field:'altitude_m',mode:'altitude'},{id:'reference_descent_speed_m_s',label:'基準下降速度',unit:'m/s',group:'descent',field:'reference_speed_m_s',mode:'rated_speed'}] as const;
export function samplingIssue(spec:SamplingSpec,candidates:Candidate[]):string|null{
 const v=samplingVariables.find(v=>v.id===spec.variable);if(!v||v.unit!==spec.unit)return '元量と単位の対応を確認してください。';
 if(!Number.isInteger(spec.n)||spec.n<1||spec.n*candidates.length>256)return '標本数は正の整数で、候補を含む総試行数を256以下にしてください。';
 if(!Number.isSafeInteger(spec.seed)||spec.seed<0||spec.seed>4294967295)return 'seed に0〜4294967295の整数を入力してください。';
 if(!Number.isFinite(spec.distribution.low)||!Number.isFinite(spec.distribution.high)||spec.distribution.low>=spec.distribution.high)return '仮幅の下端・上端を下端 < 上端で入力してください。';
 if(!spec.reason.trim())return 'この仮幅を置く理由を記してください。';
 const unsupported=candidates.find(c=>v.id==='gas_mass_kg'?c.config.ascent.mode==='constant_speed':c.config[v.group].mode!==v.mode);
 if(unsupported)return `${unsupported.label} の方式では ${v.label} を使いません。方式か元量を選び直してください。`;
 if(new Set(candidates.map(c=>c.weather_source_id)).size!==1)return '対応標本は同じ固定気象を使う候補で計画してください。';return null;
}
export function planInput(candidates:Candidate[],candidate:Candidate,requestId:string,additionalIds:string[]=[]):PlanRequest{
 const family=candidateFamily(candidates,[candidate.id,...additionalIds]),parent=candidates.find(c=>c.id===(candidate.parent_id??candidate.id))??candidate,sampling=parent.sampling;
 if(!sampling)throw Error('一変量の仮幅が指定されていません。');const issue=samplingIssue(sampling,family);if(issue)throw Error(issue);
 return {client_request_id:requestId,label:parent.label,weather_source_id:parent.weather_source_id,sampling:structuredClone(sampling),cases:family.map(c=>({case_id:c.id,candidate_id:c.id,candidate_revision:c.revision,label:c.label,parent_case_id:c.parent_id??null,delay_minutes:c.delay_minutes??null,config:structuredClone(c.config)}))};
}
export const caseKey=(snapshotId:string,caseId:string)=>snapshotId+':'+caseId;
export const selectionKey=(snapshotId:string,caseId:string,ids:string[],regions:unknown=null)=>stableString([snapshotId,caseId,[...ids].sort(),regions]);
export function comparisonRefs(project:Project):FixedResultRef[]{return project.compare_results??project.compare_run_ids.map(run_id=>({kind:'single_run',run_id}));}
export function singleRunIds(project:Project):string[]{return comparisonRefs(project).flatMap(r=>r.kind==='single_run'?[r.run_id]:[]);}
export function replaceFixedComparison(project:Project,ref:FixedResultRef,candidateId:string,runs:Record<string,Run>,cases:Record<string,CaseResult>):Project{
 const refs=comparisonRefs(project).filter(r=>r.kind==='single_run'?runs[r.run_id]?.candidate_id!==candidateId:(cases[caseKey(r.snapshot_id,r.case_id)]?.candidate.id??r.case_id)!==candidateId);
 refs.push(ref);return {...project,compare_results:refs,compare_run_ids:refs.flatMap(r=>r.kind==='single_run'?[r.run_id]:[])};
}
export const stateLabels:Record<TrialState,string>={unstarted:'未投入',queued:'待機',running:'実行中',landed:'着地',stopped:'物理停止',invalid_input:'入力不成立',failed:'実行失敗',cancelled:'取消',interrupted:'中断'};

/** Read the frozen plan, never the currently edited candidate, for support diagnostics. */
export function planTimeSupport(plan:EnsemblePlan){
 const times=plan.weather_snapshot.valid_times_utc,weatherStart=times[0],weatherEnd=times[times.length-1];
 return {weatherStart,weatherEnd,rows:plan.cases.map(c=>{
  const config=c.resolved_base_config,start=config.launch.time_utc,duration=config.integration?.max_duration_s;
  const end=typeof duration==='number'&&Number.isFinite(duration)?new Date(Date.parse(start)+duration*1000).toISOString():null;
  return {caseId:c.case_id,label:c.label,start,end,durationHours:typeof duration==='number'?duration/3600:null,unsupported:plan.blockers.some(b=>b.code==='WEATHER_WINDOW_UNSUPPORTED'&&b.case_id===c.case_id)};
 })};
}

export const jobStateLabels:Record<string,string>={queued:"待機",running:"実行中",cancelling:"取消処理中",completed:"完了",cancelled:"取消済み",failed:"失敗",interrupted:"中断"};

/** Saved JSON key order is not part of selection identity; array/coordinate order remains significant. */
export function savedSelectionMatches(encoded:unknown,value:unknown):boolean{if(typeof encoded!=='string')return false;try{return stableString(JSON.parse(encoded))===stableString(value);}catch{return false;}}
