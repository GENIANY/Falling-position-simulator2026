import {claimWriteLease,releaseWriteLease} from './writeLease';
import {setServiceIdentity} from './serviceIdentity';
import {createElement} from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {SamplingEditor} from './SamplingEditor';
import {describe,it,expect,vi,afterEach,beforeEach} from 'vitest';
beforeEach(async()=>{releaseWriteLease();vi.stubGlobal('navigator',{locks:{request:(_name:any,_options:any,callback:any)=>Promise.resolve(callback({name:'test-lock'}))}});await claimWriteLease();setServiceIdentity('test-instance');});
import {createEnsembleObserver} from './useEnsembleWorkspace';
import {ensembleApi,ENSEMBLE_READ_TIMEOUT_MS} from './ensembleApi';
import type {EnsembleObservation} from './useEnsembleWorkspace';
import {planInput,samplingIssue,replaceFixedComparison,selectionKey,planTimeSupport,savedSelectionMatches} from './ensembleDomain';
import type {CaseResult,EnsembleAnalysis,EnsemblePlan,SamplingSpec,EnsembleJob} from './ensembleDomain';
import type {Candidate,Config} from './domain';
import {collectionResult,empiricalContours,aggregateTraces,analysisRoutes,pairedRows,pairedInterference} from './screens/forecast/ensembleProjection';
import {contourIndices} from './screens/forecast/hover-geometry400.mjs';
import {install as installStyle} from './screens/shared/scene-style.js';
import {validatePayload} from '../scene3d/src/protocol.js';
const config:Config={schema:'balloon.flight.config/1',launch:{time_utc:'2026-09-23T03:30:00Z',latitude_deg:34,longitude_deg:135,altitude_m:0},ascent:{mode:'constant_speed',speed_m_s:5},burst:{mode:'altitude',altitude_m:30000},descent:{mode:'rated_speed',reference_speed_m_s:5}};
const sampling:SamplingSpec={variable:'burst_altitude_m',unit:'m',distribution:{family:'uniform',low:28000,high:32000},n:4,seed:1701,reason:'感度を調べる仮幅'};
const parent:Candidate={id:'A',label:'予定',revision:1,weather_source_id:'W',config,sampling};
const child:Candidate={...structuredClone(parent),id:'B',label:'延期',parent_id:'A',delay_minutes:30,config:{...config,launch:{...config.launch,time_utc:'2026-09-23T04:00:00Z'}}};
function caseResult():CaseResult{return {schema:'balloon.ensemble.case-result/1',ensemble_id:'E',snapshot_id:'S1',case_id:'A',plan_id:'P',drawset_id:'D',epoch:1,candidate:{id:'A',label:'予定',revision:1},sampling,submitted_config:config,resolved_base_config:config,weather_snapshot:{id:'W'},source_snapshot:{},settled:true,all_requested_have_physical_result:false,counts:{planned:4,landed:1,stopped:1,invalid_input:1,cancelled:1,unstarted:0,queued:0,running:0,failed:0,interrupted:0},trials:['landed','stopped','invalid_input','cancelled'].map((state,i)=>({trial_id:'T'+i,draw_id:'D'+i,ordinal:i+1,weight:1,parameter:{id:sampling.variable,value:28000+i*1000,unit:'m'},state,attempt:i<2?1:0,run_id:i<2?'R'+i:null,result_available:i<2,landing:i===0?{type:'landing',elapsed_s:100,latitude_deg:34.1,longitude_deg:135.1,altitude_m:0}:null,burst:null,last_valid_point:null,stop:state==='stopped'?{code:'NO_ASCENT',message:'停止'}:null,error:null})) as CaseResult['trials']};}
function analysis():EnsembleAnalysis{const metric=(mean:number|null,n=2)=>({mean,low:mean===null?null:mean-1,high:mean===null?null:mean+1,n});return {schema:'balloon.ensemble.analysis/1',method:'empirical-covariance-and-elapsed-phase/1',selected_trial_ids:['T0','T1'],selected_count:2,completed_count:2,history_count:1,landing:{n:1,mean:{latitude_deg:34.1,longitude_deg:135.1},rank:0,extent:{type:'Point',coordinates:[135.1,34.1]},bands:[.5,.9,.95].map(p=>({probability:p,rank_index:1,count:1,total:1,trial_ids:['T0'],geometry:{type:'Point',coordinates:[135.1,34.1]},threshold:0}))},history:{method:'elapsed-phase-linear/1',band:[.1,.9],grid_s:[0,31.5,100],phases:{ascent:[0,31.5].map(t=>({elapsed_s:t,n:2,metrics:{altitude_m:metric(t*5),latitude_deg:metric(34+t*.001),longitude_deg:metric(135+t*.001),vertical_speed_m_s:metric(5)}})),descent:[{elapsed_s:100,n:1,metrics:{altitude_m:metric(0,1),latitude_deg:metric(34.1,1),longitude_deg:metric(135.1,1)}}]}}};}
describe('ensemble preserves identity, populations and geometry',()=>{
 it('freezes one shared drawset request for parent, delays and independent model comparison',()=>{const independent={...parent,id:'C',label:'比較',config:{...config,ascent:{mode:'constant_speed',speed_m_s:6}}};const body=planInput([parent,child,independent],parent,'request',['C']);expect(body.cases.map(c=>c.case_id)).toEqual(['A','B','C']);expect(body.cases[1].delay_minutes).toBe(30);expect(body.sampling).toEqual(sampling);expect(body.cases[2].config.ascent.speed_m_s).toBe(6);expect(samplingIssue({...sampling,n:100},[parent,child,independent])).toContain('256');});
 it('explains the frozen delayed case window against the fixed weather support',()=>{const plan:EnsemblePlan={plan_id:'P',plan_hash:'H',status:'unavailable',sampling,drawset_id:'D',draw_count:4,case_count:1,trial_count:4,runnable_trial_count:4,invalid_trial_count:0,draws:[],warnings:[],required_window:{start:'2026-09-23T03:30:00Z',end:'2026-09-23T08:30:00Z'},weather_snapshot:{id:'W',valid_times_utc:['2026-09-23T03:00:00Z','2026-09-23T08:00:00Z']},cases:[{case_id:'delay60',candidate_id:'delay60',candidate_revision:1,label:'予定 +60分',submitted_config:config,resolved_base_config:{...config,launch:{...config.launch,time_utc:'2026-09-23T04:30:00Z'},integration:{max_duration_s:14400}}}],blockers:[{code:'WEATHER_WINDOW_UNSUPPORTED',case_id:'delay60',message:'unsupported'}]};const support=planTimeSupport(plan);expect(support.rows[0]).toMatchObject({label:'予定 +60分',start:'2026-09-23T04:30:00Z',end:'2026-09-23T08:30:00.000Z',durationHours:4,unsupported:true});expect(support.weatherEnd).toBe('2026-09-23T08:00:00Z');});
 it('restores a saved selection when JSON object keys reorder but rejects a changed region or snapshot',()=>{const before=[{id:'L1-Z1',name:'穴あり',polygons:[[[[136,33],[136.1,33],[136.1,33.1]]]],levelId:'normal'}],after=before.map(r=>({id:r.id,levelId:r.levelId,name:r.name,polygons:r.polygons}));expect(JSON.stringify(before)).not.toBe(JSON.stringify(after));expect(savedSelectionMatches(JSON.stringify(before),after)).toBe(true);const changed=structuredClone(after);changed[0].polygons[0][0][0][0]=136.2;expect(savedSelectionMatches(JSON.stringify(before),changed)).toBe(false);const oldKey=JSON.stringify(['S1','A',['T0'],{zoneVersion:1,regions:before}]);expect(savedSelectionMatches(oldKey,['S1','A',['T0'],{regions:after,zoneVersion:1}])).toBe(true);expect(savedSelectionMatches(oldKey,['S2','A',['T0'],{regions:after,zoneVersion:1}])).toBe(false);});
 it('rejects unused gas parameters and oversized seeds rather than silently injecting values',()=>{expect(samplingIssue({...sampling,variable:'gas_mass_kg',unit:'kg'},[parent])).toContain('使いません');expect(samplingIssue({...sampling,seed:4294967296},[parent])).toContain('4294967295');});
 it('keeps all planned non-spatial states while rendering only the one valid landing',()=>{const value=caseResult(),before=structuredClone(value),projected=collectionResult(value,{});expect(projected.collection.trials).toHaveLength(4);expect(projected.realSamples).toHaveLength(1);expect(projected.realSamples[0].id).toBe('T0');expect(projected.realSamples[0].history).toEqual([]);expect(value).toEqual(before);});
 it('uses fixed IDs, not ordinal reuse or latest attempts, for saved result selection',()=>{const v=caseResult(),project={schema:'balloon.project/1' as const,title:'p',candidates:[parent],compare_run_ids:['R0'],compare_results:[{kind:'single_run' as const,run_id:'R0'}]};const selected=replaceFixedComparison(project,{kind:'ensemble_case',ensemble_id:'E',snapshot_id:'S1',case_id:'A'},'A',{R0:{run_id:'R0',candidate_id:'A'}},{'S1:A':v});expect(selected.compare_run_ids).toEqual([]);expect(selected.compare_results?.[0].kind).toBe('ensemble_case');expect(selectionKey('S1','A',['T0'])).not.toBe(selectionKey('S2','A',['T0']));});
 it('draws rank-zero and rank-one contours without adding artificial area',()=>{const a=analysis(),point=empiricalContours(a);expect(point[0]?.geometry.type).toBe('Point');const scope:any={window:{},document:{}};installStyle(scope);expect(scope.window.BJP_STYLE.bands(point)).toEqual([]);a.landing.rank=1;a.landing.bands.forEach(b=>b.geometry={type:'LineString',coordinates:[[135,34],[135.1,34.1]]});const line=empiricalContours(a);expect(line[0]?.points).toEqual([[34,135],[34.1,135.1]]);expect(scope.window.BJP_STYLE.bands(line)).toEqual([]);});
 it('uses common elapsed-phase rows for means, bands and routes, preserving exact event time',()=>{const a=analysis(),traces=aggregateTraces(a,'h','','#08788b',true),routes=analysisRoutes(a);expect(traces[2].x).toEqual([0,31.5/60]);expect(traces[2].y).toEqual([0,.1575]);expect(traces[2].customdata).toEqual([2,2]);expect(routes[0].elapsed_s).toEqual([0,31.5]);expect(routes[1].heights).toEqual([0]);});
 it('joins paired cases by frozen draw ID and leaves failed landing pairs undefined',()=>{const a=caseResult(),b=caseResult();b.case_id='B';b.trials.reverse();b.trials.find(t=>t.state==='landed')!.landing!.elapsed_s=130;const result=pairedRows(a,b);expect(result.rows[0].deltaMinutes).toBe(.5);expect(result.missing).toBe(3);b.drawset_id='other';expect(pairedRows(a,b).paired).toBe(false);});
 it('compares interference transitions in an explicit direction and excludes missing landing pairs',()=>{const a=caseResult(),b=caseResult(),base=a.trials[0];a.trials=Array.from({length:8},(_,i)=>({...structuredClone(base),trial_id:'A'+i,draw_id:'D'+i,ordinal:i+1}));b.trials=a.trials.map((t,i)=>({...structuredClone(t),trial_id:'B'+i}));const first=['A0','A1','A2','A3','A4'],second=['B0','B1','B2'];expect(pairedInterference(a,b,first,second).transitions).toEqual({retained:3,exited:2,entered:0,clear:3,unresolved:0});expect(pairedInterference(b,a,second,first).transitions).toEqual({retained:3,exited:0,entered:2,clear:3,unresolved:0});b.trials[4].state='stopped';b.trials[4].landing=null;expect(pairedInterference(a,b,first,second).transitions).toEqual({retained:3,exited:1,entered:0,clear:3,unresolved:1});expect(pairedInterference(a,b,null,null).transitions).toBeNull();expect(pairedInterference(a,b,null,null).rows.every(r=>r.transition==='unconfigured')).toBe(true);});
 it('picks point and line contour labels with screen tolerance without modifying geometry',()=>{const features=[{properties:{kind:'contour'},geometry:{type:'Point',coordinates:[10,10]}},{properties:{kind:'contour'},geometry:{type:'LineString',coordinates:[[20,0],[20,30]]}}],project=([x,y]:number[])=>({x,y});expect(contourIndices(features,{x:11,y:10},project)).toEqual([0]);expect(contourIndices(features,{x:20,y:17},project)).toEqual([1]);});
 it('requires an explicit spatial/non-spatial partition for selected ensemble trials in 3D',()=>{const raw:any={snapshotId:'scene',collectionKey:'S1:A',artificial:false,context:{kind:'detail',activeCandidateId:'A',contours:'none',selection:{sampleIds:['T0','T1'],count:2,denominator:4,spatialSampleIds:['T0'],nonSpatialCount:1,binding:{snapshotId:'S1',caseId:'A',resultId:'S1:A'}}},candidates:[{candidateId:'A',resultId:'S1:A',available:true,visible:true,focused:true,parentId:null,delayMinutes:0}],geojson:{type:'FeatureCollection',features:[{type:'Feature',properties:{kind:'landing',candidateId:'A',resultId:'S1:A',sampleId:'T0'},geometry:{type:'Point',coordinates:[135,34]}}]},camera:{center:[135,34],bounds:[134,33,136,35]}};expect(()=>validatePayload(raw)).not.toThrow();raw.context.selection.nonSpatialCount=0;expect(()=>validatePayload(raw)).toThrow();});
});


describe('ensemble status observation survives read failures without resubmitting work',()=>{
 afterEach(()=>{vi.useRealTimers();vi.unstubAllGlobals();});
 const job=(id='E',epoch=1,revision=1,state='running'):EnsembleJob=>({ensemble_id:id,plan_id:'P',state,epoch,state_revision:revision,planned_trials:48,latest_snapshot_id:null,counts:{unstarted:0,queued:47,running:1,landed:0,stopped:0,invalid_input:0,failed:0,cancelled:0,interrupted:0},cancellable:true,retryable:false,cases:[{case_id:'A',planned:16},{case_id:'B',planned:16},{case_id:'C',planned:16}],error:null});
 function deferred<T>(){let resolve!:(v:T)=>void,reject!:(e:unknown)=>void;const promise=new Promise<T>((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};}
 function setup(read:(id:string,signal:AbortSignal)=>Promise<EnsembleJob>,initial:Record<string,EnsembleJob>={E:job()}){
  let current=true,jobs=initial;const observations:Record<string,EnsembleObservation>={};
  const accept=vi.fn((next:EnsembleJob)=>{jobs={...jobs,[next.ensemble_id]:next};});
  const observe=vi.fn((id:string,state:EnsembleObservation)=>{observations[id]=state;});
  const watcher=createEnsembleObserver({jobs:()=>jobs,read,accept,observe,isCurrent:()=>current});
  return {watcher,accept,observe,observations,get jobs(){return jobs;},setJob(next:EnsembleJob){jobs={...jobs,[next.ensemble_id]:next};},invalidate(){current=false;watcher.dispose();}};
 }
 it('keeps both jobs and their old counts after all GETs fail, then automatically observes recovery',async()=>{
  vi.useFakeTimers();let online=false;const read=vi.fn(async(id:string)=>{if(!online)throw Error('network disconnected');return job(id,1,2,'completed');});
  const s=setup(read,{E:job('E'),F:job('F')}),before=structuredClone(s.jobs);s.watcher.sync();
  await vi.advanceTimersByTimeAsync(900);expect(read).toHaveBeenCalledTimes(2);expect(s.jobs).toEqual(before);expect(s.accept).not.toHaveBeenCalled();
  expect(s.observations.E).toMatchObject({checking:false,unavailable:true,failures:1,nextRetryMs:1800,lastConfirmedAt:null});expect(s.observations.F.unavailable).toBe(true);
  online=true;await vi.advanceTimersByTimeAsync(1800);expect(read).toHaveBeenCalledTimes(4);expect(s.jobs.E.state).toBe('completed');expect(s.jobs.F.state).toBe('completed');
  expect(s.observations.E).toMatchObject({unavailable:false,failures:0,message:null,nextRetryMs:null});expect(s.observations.E.lastConfirmedAt).not.toBeNull();expect(vi.getTimerCount()).toBe(0);s.watcher.dispose();
 });
 it('caps automatic backoff at 15 seconds, while an explicit GET bypasses the wait and deduplicates an in-flight read',async()=>{
  vi.useFakeTimers();const last=deferred<EnsembleJob>();let recover=false;const read=vi.fn(()=>recover?last.promise:Promise.reject(Error('offline'))),s=setup(read);s.watcher.sync();
  for(const delay of [900,1800,3600,7200,14400,15000])await vi.advanceTimersByTimeAsync(delay);
  expect(read).toHaveBeenCalledTimes(6);expect(s.observations.E.nextRetryMs).toBe(15000);expect(vi.getTimerCount()).toBe(1);
  recover=true;const first=s.watcher.refresh('E'),again=s.watcher.refresh('E');expect(first).toBe(again);await Promise.resolve();expect(read).toHaveBeenCalledTimes(7);expect(vi.getTimerCount()).toBe(0);
  last.resolve(job('E',1,2));await first;expect(s.observations.E).toMatchObject({unavailable:false,failures:0,message:null,nextRetryMs:900});s.watcher.dispose();expect(vi.getTimerCount()).toBe(0);
 });
 it('does not roll a newer epoch or revision back when an older GET arrives after a command response',async()=>{
  vi.useFakeTimers();const first=deferred<EnsembleJob>(),second=deferred<EnsembleJob>(),read=vi.fn().mockReturnValueOnce(first.promise).mockReturnValueOnce(second.promise),s=setup(read);
  const pending=s.watcher.refresh('E');await Promise.resolve();s.setJob(job('E',2,1));first.resolve(job('E',1,99,'completed'));await pending;
  expect(s.jobs.E.epoch).toBe(2);expect(s.accept).not.toHaveBeenCalled();expect(s.observations.E.lastConfirmedAt).toBeNull();
  const pending2=s.watcher.refresh('E');await Promise.resolve();s.setJob(job('E',2,5));second.resolve(job('E',2,4,'completed'));await pending2;
  expect(s.jobs.E.state_revision).toBe(5);expect(s.accept).not.toHaveBeenCalled();s.watcher.dispose();
 });
 it('discards both late success and late failure from the previous restoration generation',async()=>{
  vi.useFakeTimers();const success=deferred<EnsembleJob>(),failure=deferred<EnsembleJob>();const read=vi.fn((id:string)=>id==='E'?success.promise:failure.promise),s=setup(read,{E:job('E'),F:job('F')});
  const a=s.watcher.refresh('E'),b=s.watcher.refresh('F');await Promise.resolve();s.invalidate();const observations=s.observe.mock.calls.length;
  const newer=setup(async id=>job(id,2,1,'completed'));await newer.watcher.refresh('E');success.resolve(job('E',1,5,'completed'));failure.reject(Error('old failure'));await Promise.all([a,b]);
  expect(s.accept).not.toHaveBeenCalled();expect(s.observe).toHaveBeenCalledTimes(observations);expect(newer.jobs.E.epoch).toBe(2);expect(newer.observations.E.unavailable).toBe(false);expect(vi.getTimerCount()).toBe(0);newer.watcher.dispose();
 });
 it('releases scheduled timers and suppresses later reads after unmount disposal',async()=>{
  vi.useFakeTimers();const read=vi.fn(async (id:string)=>job(id)),s=setup(read);s.watcher.sync();expect(vi.getTimerCount()).toBe(1);s.watcher.dispose();s.watcher.sync();await s.watcher.refresh('E');await vi.advanceTimersByTimeAsync(60000);expect(read).not.toHaveBeenCalled();expect(s.observe).not.toHaveBeenCalled();expect(vi.getTimerCount()).toBe(0);
 });
 it('uses the production status GET endpoint for manual recovery, never a calculation or retry POST',async()=>{
  vi.useFakeTimers();let online=false;const fetchStatus=vi.fn(async()=>{if(!online)throw Error('status offline');return {ok:true,status:200,json:async()=>job('E',1,3,'completed')};});vi.stubGlobal('fetch',fetchStatus);
  const s=setup((id,signal)=>ensembleApi.job(id,signal));await s.watcher.refresh('E');expect(s.observations.E.unavailable).toBe(true);online=true;await s.watcher.refresh('E');expect(s.observations.E.message).toBeNull();
  expect(fetchStatus).toHaveBeenCalledTimes(2);for(const [url,init]of fetchStatus.mock.calls as unknown as [string,RequestInit][]){expect(url).toBe('/api/v1/ensembles/E');expect(init.method??'GET').toBe('GET');expect(init.body).toBeUndefined();}s.watcher.dispose();
 });
 it('labels stale counts as last observed while keeping the separate command error visible after recovery',()=>{
  const observed={checking:false,unavailable:true,lastConfirmedAt:'2026-09-30T01:02:03Z',failures:1,nextRetryMs:1800,message:'状態GETのみの失敗'};
  const ensemble:any={jobs:{E:job()},plans:{},busy:{},observations:{E:observed},error:'計算受付POSTの失敗',refreshJob:vi.fn(),cancel:vi.fn(),retry:vi.fn(),selectJob:vi.fn()};
  const props:any={candidate:{...parent,sampling:null},candidates:[parent],ensemble,onChange:vi.fn(),onRemember:vi.fn(),additionalIds:[],onTargets:vi.fn()};
  const missing=renderToStaticMarkup(createElement(SamplingEditor,props));expect(missing).toContain('最後に確認した状態：');expect(missing).toContain('現在の状態は未確認');expect(missing).toContain('計算の失敗・停止を意味しません');expect(missing).toContain('状況を確認');
  ensemble.observations.E={...observed,unavailable:false,failures:0,nextRetryMs:900,message:null};const recovered=renderToStaticMarkup(createElement(SamplingEditor,props));expect(recovered).not.toContain('現在の状態は未確認');expect(recovered).not.toContain('状態GETのみの失敗');expect(recovered).toContain('計算受付POSTの失敗');
 });

 it('bounds a never-returning status fetch, aborts its actual signal and permits a fresh manual GET',async()=>{
  vi.useFakeTimers();let recover=false;const signals:AbortSignal[]=[],fetchStatus=vi.fn((_url:string,init:RequestInit)=>{signals.push(init.signal as AbortSignal);return recover?Promise.resolve({ok:true,status:200,json:async()=>job('E',1,2,'completed')}):new Promise<never>(()=>{});});vi.stubGlobal('fetch',fetchStatus);
  const s=setup((id,signal)=>ensembleApi.job(id,signal)),before=structuredClone(s.jobs),first=s.watcher.refresh('E');expect(s.watcher.refresh('E')).toBe(first);
  await vi.advanceTimersByTimeAsync(ENSEMBLE_READ_TIMEOUT_MS-1);expect(fetchStatus).toHaveBeenCalledTimes(1);expect(signals[0].aborted).toBe(false);expect(s.observations.E.checking).toBe(true);
  await vi.advanceTimersByTimeAsync(1);await first;expect(signals[0].aborted).toBe(true);expect(s.jobs).toEqual(before);expect(s.observations.E).toMatchObject({checking:false,unavailable:true,failures:1,nextRetryMs:1800});expect(s.observations.E.message).toContain('計算は取り消していません');
  recover=true;await s.watcher.refresh('E');expect(fetchStatus).toHaveBeenCalledTimes(2);expect(signals[1]).not.toBe(signals[0]);expect(signals[1].aborted).toBe(false);expect(s.jobs.E.state).toBe('completed');expect(s.observations.E.unavailable).toBe(false);expect(vi.getTimerCount()).toBe(0);s.watcher.dispose();
 });
 it('includes a stalled JSON body in the same deadline and ignores that old body after recovery',async()=>{
  vi.useFakeTimers();const body=deferred<EnsembleJob>(),signals:AbortSignal[]=[];let count=0;vi.stubGlobal('fetch',vi.fn(async(_url:string,init:RequestInit)=>{signals.push(init.signal as AbortSignal);return {ok:true,status:200,json:()=>++count===1?body.promise:Promise.resolve(job('E',2,1,'completed'))};}));
  const s=setup((id,signal)=>ensembleApi.job(id,signal)),first=s.watcher.refresh('E');await vi.advanceTimersByTimeAsync(1);expect(count).toBe(1);expect(s.observations.E.checking).toBe(true);
  await vi.advanceTimersByTimeAsync(ENSEMBLE_READ_TIMEOUT_MS-1);await first;expect(signals[0].aborted).toBe(true);expect(s.accept).not.toHaveBeenCalled();await s.watcher.refresh('E');body.resolve(job('E',1,99,'completed'));await Promise.resolve();await Promise.resolve();
  expect(s.accept).toHaveBeenCalledTimes(1);expect(s.jobs.E.epoch).toBe(2);expect(s.observations.E.unavailable).toBe(false);expect(vi.getTimerCount()).toBe(0);s.watcher.dispose();
 });
 it('aborts real pending GETs on restoration disposal without surfacing their errors in the next generation',async()=>{
  vi.useFakeTimers();const signals:AbortSignal[]=[];let restored=false;vi.stubGlobal('fetch',vi.fn((_url:string,init:RequestInit)=>{const signal=init.signal as AbortSignal;signals.push(signal);if(restored)return Promise.resolve({ok:true,status:200,json:async()=>job('E',2,1,'completed')});return new Promise((_resolve,reject)=>signal.addEventListener('abort',()=>reject(new DOMException('old read aborted','AbortError')),{once:true}));}));
  const old=setup((id,signal)=>ensembleApi.job(id,signal),{E:job('E'),F:job('F')}),a=old.watcher.refresh('E'),b=old.watcher.refresh('F');await vi.advanceTimersByTimeAsync(1);expect(signals).toHaveLength(2);const observed=old.observe.mock.calls.length;old.invalidate();await Promise.all([a,b]);
  expect(signals.every(s=>s.aborted)).toBe(true);expect(old.accept).not.toHaveBeenCalled();expect(old.observe).toHaveBeenCalledTimes(observed);expect(vi.getTimerCount()).toBe(0);
  restored=true;const newer=setup((id,signal)=>ensembleApi.job(id,signal));await newer.watcher.refresh('E');expect(newer.jobs.E.epoch).toBe(2);expect(newer.observations.E).toMatchObject({checking:false,unavailable:false,message:null});newer.watcher.dispose();
 });
 it('never starts a status fetch when disposal wins before its deferred reader starts',async()=>{
  vi.useFakeTimers();const fetchStatus=vi.fn();vi.stubGlobal('fetch',fetchStatus);const s=setup((id,signal)=>ensembleApi.job(id,signal)),pending=s.watcher.refresh('E');s.invalidate();await pending;expect(fetchStatus).not.toHaveBeenCalled();expect(s.accept).not.toHaveBeenCalled();expect(vi.getTimerCount()).toBe(0);
 });
 it('uses one caller lifetime for all restoration GETs, including JSON reads, and cancels none of the server work',async()=>{
  vi.useFakeTimers();const scope=new AbortController(),signals:AbortSignal[]=[],fetchRead=vi.fn(async(_url:string,init:RequestInit)=>{signals.push(init.signal as AbortSignal);return {ok:true,status:200,json:()=>new Promise<never>(()=>{})};});vi.stubGlobal('fetch',fetchRead);
  const reads=[ensembleApi.jobs(scope.signal),ensembleApi.getPlan('P',scope.signal),ensembleApi.snapshot('S',scope.signal),ensembleApi.case('S','A',scope.signal),ensembleApi.result('S','T',scope.signal),ensembleApi.getAnalysis('AN',scope.signal)],settled=Promise.allSettled(reads);
  await vi.advanceTimersByTimeAsync(1);expect(fetchRead).toHaveBeenCalledTimes(6);scope.abort();const values=await settled;expect(values.every(v=>v.status==='rejected'&&v.reason.name==='AbortError')).toBe(true);expect(signals.every(s=>s.aborted)).toBe(true);expect(vi.getTimerCount()).toBe(0);
  for(const [,init]of fetchRead.mock.calls){expect(init.method??'GET').toBe('GET');expect(init.body).toBeUndefined();}
  await expect(ensembleApi.jobs(scope.signal)).rejects.toHaveProperty('name','AbortError');expect(fetchRead).toHaveBeenCalledTimes(6);
 });
 it('releases deadline timers and the caller listener after success, preserving ordinary API error details',async()=>{
  vi.useFakeTimers();const scope=new AbortController(),remove=vi.spyOn(scope.signal,'removeEventListener');let ok=true;const signals:AbortSignal[]=[];vi.stubGlobal('fetch',vi.fn(async(_url:string,init:RequestInit)=>{signals.push(init.signal as AbortSignal);return {ok,status:ok?200:409,json:async()=>ok?job():{detail:'固定した場が変更されました'}};}));
  await ensembleApi.job('E',scope.signal);expect(vi.getTimerCount()).toBe(0);expect(remove).toHaveBeenCalledWith('abort',expect.any(Function));ok=false;await expect(ensembleApi.job('E',scope.signal)).rejects.toMatchObject({status:409,message:'固定した場が変更されました'});expect(vi.getTimerCount()).toBe(0);scope.abort();expect(signals.every(s=>!s.aborted)).toBe(true);
 });
 it('uses a distinct 60 second write deadline without automatically resending a calculation',async()=>{
  vi.useFakeTimers();const saved=new Map<string,string>();vi.stubGlobal('localStorage',{getItem:(k:string)=>saved.get(k)??null,setItem:(k:string,v:string)=>saved.set(k,v)});
  const body=deferred<EnsembleJob>(),fetchPost=vi.fn(async()=>({ok:true,status:200,json:()=>body.promise}));vi.stubGlobal('fetch',fetchPost);const pending=ensembleApi.start({plan_id:'P',plan_hash:'H'} as EnsemblePlan,'request-one'),assertion=expect(pending).rejects.toThrow('受付応答');await vi.advanceTimersByTimeAsync(60000);await assertion;
  expect(fetchPost).toHaveBeenCalledTimes(1);const [url,init]=fetchPost.mock.calls[0] as unknown as [string,RequestInit];expect(url).toBe('/api/v1/ensembles');expect(init.method).toBe('POST');expect(init.signal?.aborted).toBe(true);expect(vi.getTimerCount()).toBe(0);body.resolve(job());await Promise.resolve();expect(fetchPost).toHaveBeenCalledTimes(1);expect([...saved.values()].join('')).toContain('request-one');
 });

});
