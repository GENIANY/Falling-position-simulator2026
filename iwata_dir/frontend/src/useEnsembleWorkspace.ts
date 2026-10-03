import {readFailure,type FixedResultRead} from './fixedResultRead';
import {useEffect,useRef,useState} from 'react';
import type {Candidate,Project,ResultEnvelope,Run} from './domain';
import {stableString} from './domain';
import {ApiError,uncertainWrite} from './api';
import {ensembleApi} from './ensembleApi';
import {recordedMutation} from './recordedMutation';
import {putSubmission,removeSubmission,snapshotSubmissions} from './submissionLedger';
import {caseKey,comparisonRefs,planInput,replaceFixedComparison,selectionKey} from './ensembleDomain';
import type {AnalysisArtifact,CaseResult,EnsembleJob,EnsemblePlan} from './ensembleDomain';
import {beginWriteOperation,observeWriteLease,ownsWriteLease} from './writeLease';

export type EnsembleObservation={checking:boolean;unavailable:boolean;lastConfirmedAt:string|null;failures:number;nextRetryMs:number|null;message:string|null};
const activeJob=(job:EnsembleJob|undefined)=>!!job&&['queued','running','cancelling'].includes(job.state);
const earlierJob=(next:EnsembleJob,previous:EnsembleJob|undefined)=>!!previous&&(next.epoch<previous.epoch||next.epoch===previous.epoch&&(next.state_revision??0)<(previous.state_revision??0));

/** GET-only observation. A failed read never changes the server's last known job state. */
export function createEnsembleObserver(options:{jobs:()=>Record<string,EnsembleJob>;read:(id:string,signal:AbortSignal)=>Promise<EnsembleJob>;accept:(job:EnsembleJob)=>void;observe:(id:string,state:EnsembleObservation)=>void;isCurrent:()=>boolean}){
 type Entry={timer:ReturnType<typeof setTimeout>|null;flight:Promise<void>|null;controller:AbortController|null;state:EnsembleObservation};
 const entries=new Map<string,Entry>();let disposed=false;
 const current=()=>!disposed&&options.isCurrent();
 function entry(id:string){let value=entries.get(id);if(!value){value={timer:null,flight:null,controller:null,state:{checking:false,unavailable:false,lastConfirmedAt:null,failures:0,nextRetryMs:null,message:null}};entries.set(id,value);}return value;}
 function emit(id:string,value:Entry){if(current())options.observe(id,{...value.state});}
 function clear(value:Entry){if(value.timer!==null)clearTimeout(value.timer);value.timer=null;}
 function schedule(id:string,value:Entry){
  clear(value);if(!current()||!activeJob(options.jobs()[id])){value.state.nextRetryMs=null;return;}
  const delay=value.state.failures?Math.min(15000,900*2**Math.min(value.state.failures,5)):900;
  value.state.nextRetryMs=delay;value.timer=setTimeout(()=>{value.timer=null;void refresh(id);},delay);
 }
 function refresh(id:string):Promise<void>{
  if(!current()||!options.jobs()[id])return Promise.resolve();const value=entry(id);if(value.flight)return value.flight;
  clear(value);value.state={...value.state,checking:true,nextRetryMs:null};emit(id,value);
  // Install the promise before calling read, including a synchronously throwing reader.
  const controller=new AbortController();value.controller=controller;
  const work=Promise.resolve().then(()=>options.read(id,controller.signal)).then(next=>{
   if(!current())return;if(next.ensemble_id!==id)throw Error('確認した集合の識別が応答と一致しません。');
   const previous=options.jobs()[id];if(!previous||earlierJob(next,previous))return;
   options.accept(next);value.state={checking:false,unavailable:false,lastConfirmedAt:new Date().toISOString(),failures:0,nextRetryMs:null,message:null};
  }).catch(error=>{if(current())value.state={...value.state,unavailable:true,failures:value.state.failures+1,message:error instanceof Error?error.message:String(error)};}).finally(()=>{
   value.flight=null;value.controller=null;if(!current())return;value.state.checking=false;schedule(id,value);emit(id,value);
  });value.flight=work;return work;
 }
 function sync(){if(!current())return;const jobs=options.jobs();for(const [id,value]of entries)if(!activeJob(jobs[id]))clear(value);for(const job of Object.values(jobs))if(activeJob(job)){const value=entry(job.ensemble_id);if(!value.flight&&value.timer===null)schedule(job.ensemble_id,value);}}
 function dispose(){disposed=true;for(const value of entries.values()){clear(value);value.controller?.abort();}entries.clear();}
 return {refresh,sync,dispose};
}

/** Collection jobs are not n=1 runs. Completed snapshots are selected explicitly. */
export function useEnsembleWorkspace(project:Project,runs:Run[],restoration:number,loading:boolean,onProject:(project:Project)=>void,selection:{claim:(id:string)=>number;current:(id:string)=>number}){
 const [jobs,setJobs]=useState<Record<string,EnsembleJob>>({}),[plans,setPlans]=useState<Record<string,{plan:EnsemblePlan;input:string;additionalIds:string[]}>>({}),[cases,setCases]=useState<Record<string,CaseResult>>({}),[analyses,setAnalyses]=useState<Record<string,AnalysisArtifact>>({}),[histories,setHistories]=useState<Record<string,ResultEnvelope>>({}),[error,setError]=useState(''),[busy,setBusy]=useState<Record<string,string>>({});
 const [caseReads,setCaseReads]=useState<Record<string,FixedResultRead>>({});
 const [pendingMutations,setPendingMutations]=useState(()=>snapshotSubmissions('ensemble-write').requests),[recoveryBusy,setRecoveryBusy]=useState('');
 const [observations,setObservations]=useState<Record<string,EnsembleObservation>>({}),jobStore=useRef(jobs),observer=useRef<ReturnType<typeof createEnsembleObserver>|null>(null);
 const current=useRef({project,runs,onProject,cases});current.current={project,runs,onProject,cases};
 const life=useRef(0),mounted=useRef(true),requests=useRef(new Map<string,string>()),pending=useRef(new Map<string,Promise<any>>()),epochs=useRef<Record<string,number>>({}),reads=useRef(new AbortController());
 const isCurrent=(generation:number)=>mounted.current&&generation===life.current;
 const message=(e:unknown,generation=life.current)=>{if(isCurrent(generation))setError(e instanceof Error?e.message:String(e));};
 function commitProject(next:Project){const notify=current.current.onProject;current.current={...current.current,project:next};notify(next);}
 function mergeJob(job:EnsembleJob){if(earlierJob(job,jobStore.current[job.ensemble_id]))return;jobStore.current={...jobStore.current,[job.ensemble_id]:job};setJobs(jobStore.current);}
 function requestId(key:string){const saved=snapshotSubmissions('ensemble-intent').requests.find(r=>r.payload.key===key);if(saved||!requests.current.has(key))requests.current.set(key,saved?.payload.requestId??crypto.randomUUID());return requests.current.get(key)!;}
 async function mutation<T>(key:string,fn:(id:string)=>Promise<T>):Promise<T>{
  const finish=beginWriteOperation();try{
   const request=requestId(key),intent={id:'ensemble-intent:'+request,kind:'ensemble-intent',createdAt:new Date().toISOString(),payload:{key,requestId:request}};
   if(key.startsWith('analysis:')&&snapshotSubmissions('ensemble-write').requests.some(r=>r.payload.body?.client_request_id===request))throw Error('この群分析の受付が未確認です。保存した要求の明示確認から続けてください。自動で再送しません。');
   putSubmission(intent);try{const v=await fn(request);requests.current.delete(key);removeSubmission(intent.id);return v;}catch(e){if(!uncertainWrite(e)){requests.current.delete(key);removeSubmission(intent.id);}throw e;}
  }finally{finish();if(mounted.current)setPendingMutations(snapshotSubmissions('ensemble-write').requests);}
 }
 async function recoverMutation(id:string){
  if(recoveryBusy)return;const entry=snapshotSubmissions('ensemble-write').requests.find(r=>r.id===id);if(!entry)return;const generation=life.current;let finish:(()=>void)|undefined;setRecoveryBusy(id);
  try{finish=beginWriteOperation();const value:any=await recordedMutation('ensemble-write',entry.payload.path,entry.payload.body);if(!isCurrent(generation))return;
   if(value.ensemble_id&&value.counts&&value.cases)mergeJob(value);
   else if(value.analysis_id){const b=entry.payload.body;setAnalyses(old=>({...old,[selectionKey(b.snapshot_id,b.case_id,b.selected_trial_ids??['*'],b.region_set)]:value}));}
   else if(value.plan_id&&value.plan_hash){const body=entry.payload.body,candidateId=body.cases?.[0]?.candidate_id;if(candidateId){const input=stableString({...body,client_request_id:''}),additionalIds=body.cases.filter((c:any)=>!c.parent_case_id&&c.candidate_id!==candidateId).map((c:any)=>c.candidate_id);setPlans(old=>({...old,[candidateId]:{plan:value,input,additionalIds}}));}}
   for(const intent of snapshotSubmissions('ensemble-intent').requests)if(intent.payload.requestId===entry.payload.body.client_request_id){requests.current.delete(intent.payload.key);removeSubmission(intent.id);}
  }catch(e){message(e,generation);}finally{finish?.();if(isCurrent(generation)){setRecoveryBusy('');setPendingMutations(snapshotSubmissions('ensemble-write').requests);}}
 }
 async function loadCase(snapshotId:string,caseId:string){
  const key=caseKey(snapshotId,caseId),requestKey='case:'+key,generation=life.current;
  if(current.current.cases[key])return current.current.cases[key];
  const running=pending.current.get(requestKey);if(running)return running as Promise<CaseResult>;
  setCaseReads(old=>({...old,[key]:{state:'loading'}}));
  const work=ensembleApi.case(snapshotId,caseId,reads.current.signal).then(value=>{
   if(value.snapshot_id!==snapshotId||value.case_id!==caseId)throw Error('保存結果の識別が要求と一致しません。');
   if(isCurrent(generation)){current.current={...current.current,cases:{...current.current.cases,[key]:value}};setCases(old=>({...old,[key]:value}));setCaseReads(old=>({...old,[key]:{state:'ready'}}));}return value;
  }).catch(error=>{if(isCurrent(generation))setCaseReads(old=>({...old,[key]:readFailure(error)}));throw error;
  }).finally(()=>{if(pending.current.get(requestKey)===work)pending.current.delete(requestKey);});
  pending.current.set(requestKey,work);return work;
 }
 function reloadCase(snapshotId:string,caseId:string){return loadCase(snapshotId,caseId).catch(()=>undefined);}
 async function analysis(snapshotId:string,caseId:string,ids:string[]|null,regions:unknown=null){const key=selectionKey(snapshotId,caseId,ids??['*'],regions),generation=life.current;if(analyses[key])return analyses[key];const running=pending.current.get(key);if(running)return running as Promise<AnalysisArtifact>;const work=mutation('analysis:'+key,id=>ensembleApi.analysis(snapshotId,caseId,ids,regions,id)).then(value=>{if(mounted.current&&generation===life.current)setAnalyses(old=>({...old,[key]:value}));return value;}).finally(()=>{if(pending.current.get(key)===work)pending.current.delete(key);});pending.current.set(key,work);return work;}
 async function history(snapshotId:string,trialId:string){const key=caseKey(snapshotId,trialId),generation=life.current;if(histories[key])return histories[key];const running=pending.current.get(key);if(running)return running as Promise<ResultEnvelope>;const work=ensembleApi.result(snapshotId,trialId,reads.current.signal).then(value=>{if(mounted.current&&generation===life.current)setHistories(old=>({...old,[key]:value}));return value;}).finally(()=>{if(pending.current.get(key)===work)pending.current.delete(key);});pending.current.set(key,work);return work;}
 useEffect(()=>{mounted.current=true;return()=>{mounted.current=false;life.current++;reads.current.abort();};},[]);
 useEffect(()=>{
  let owned=ownsWriteLease();
  return observeWriteLease(value=>{const next=value.state==='owner';if(next&&!owned){
   // Another tab may have replaced an unresolved intent while this tab was a reader.
   requests.current.clear();for(const entry of snapshotSubmissions('ensemble-intent').requests)requests.current.set(entry.payload.key,entry.payload.requestId);
   setPendingMutations(snapshotSubmissions('ensemble-write').requests);
  }owned=next;});
 },[]);
 useEffect(()=>{
  const generation=++life.current;reads.current.abort();const scope=new AbortController();reads.current=scope;pending.current.clear();
  if(!loading){
   setPlans({});setBusy({});setCaseReads({});setPendingMutations(snapshotSubmissions('ensemble-write').requests);epochs.current={};
   void ensembleApi.jobs(scope.signal).then(v=>{if(isCurrent(generation))v.ensembles.forEach(mergeJob);}).catch(e=>message(e,generation));
   for(const ref of comparisonRefs(project))if(ref.kind==='ensemble_case')void loadCase(ref.snapshot_id,ref.case_id).catch(()=>undefined);
   for(const [candidateId,entry]of Object.entries(project.ui_state?.forecast_real?.ensemblePlans??{}) as [string,any][]){
    const epoch=epochs.current[candidateId]??0;
    void ensembleApi.getPlan(entry.plan_id,scope.signal).then(plan=>{if(isCurrent(generation)&&(epochs.current[candidateId]??0)===epoch)setPlans(old=>({...old,[candidateId]:{plan,input:entry.input,additionalIds:entry.additionalIds??[]}}));}).catch(e=>message(e,generation));
   }
  }
  return()=>scope.abort();
 },[restoration,loading]);
 useEffect(()=>{setObservations({});if(loading)return;const generation=life.current,watcher=createEnsembleObserver({jobs:()=>jobStore.current,read:(id,signal)=>ensembleApi.job(id,signal),accept:mergeJob,observe:(id,state)=>setObservations(old=>({...old,[id]:state})),isCurrent:()=>mounted.current&&generation===life.current});observer.current=watcher;watcher.sync();return()=>{watcher.dispose();if(observer.current===watcher)observer.current=null;};},[restoration,loading]);
 useEffect(()=>{observer.current?.sync();},[jobs]);
 function refreshJob(id:string){return observer.current?.refresh(id)??Promise.resolve();}
 async function prepare(candidate:Candidate,additionalIds:string[]=[]){const generation=life.current,epoch=(epochs.current[candidate.id]??0)+1;epochs.current[candidate.id]=epoch;setBusy(old=>({...old,[candidate.id]:'標本計画を固定中'}));setError('');try{const body=planInput(current.current.project.candidates,candidate,'',additionalIds);const key=stableString(body);const plan=await mutation('plan:'+key,id=>ensembleApi.plan({...body,client_request_id:id}));if(generation===life.current&&epochs.current[candidate.id]===epoch){setPlans(old=>({...old,[candidate.id]:{plan,input:key,additionalIds}}));const c=current.current,view=c.project.ui_state?.forecast_real??{};commitProject({...c.project,ui_state:{...c.project.ui_state,forecast_real:{...view,ensemblePlans:{...view.ensemblePlans,[candidate.id]:{plan_id:plan.plan_id,input:key,additionalIds}}}}});}}catch(e){if(generation===life.current)message(e);}finally{if(generation===life.current&&epochs.current[candidate.id]===epoch)setBusy(old=>({...old,[candidate.id]:''}));}}
 function stale(candidate:Candidate){const p=plans[candidate.id];if(!p)return false;try{return p.input!==stableString(planInput(current.current.project.candidates,candidate,'',current.current.project.ui_state?.forecast_real?.samplingComparisonIds?.[candidate.id]??[]));}catch{return true;}}
 async function start(candidate:Candidate){const captured=plans[candidate.id];if(!captured||stale(candidate))return;setBusy(old=>({...old,[candidate.id]:'集合を受付中'}));const generation=life.current;try{const job=await mutation('start:'+captured.plan.plan_id,id=>ensembleApi.start(captured.plan,id));if(generation===life.current)mergeJob(job);}catch(e){message(e,generation);}finally{if(generation===life.current)setBusy(old=>({...old,[candidate.id]:''}));}}
 async function select(snapshotId:string,caseId:string){const key='select:'+caseId,epoch=(epochs.current[key]??0)+1;epochs.current[key]=epoch;const generation=life.current,displayToken=selection.claim(caseId);try{const value=await loadCase(snapshotId,caseId);if(generation!==life.current||epochs.current[key]!==epoch||selection.current(caseId)!==displayToken)return;const c=current.current;const next=replaceFixedComparison(c.project,{kind:'ensemble_case',ensemble_id:value.ensemble_id,snapshot_id:snapshotId,case_id:caseId},value.candidate.id,Object.fromEntries(c.runs.map(r=>[r.run_id,r])),{...c.cases,[caseKey(snapshotId,caseId)]:value});commitProject(next);}catch(e){message(e,generation);}}
 async function selectJob(job:EnsembleJob){if(!job.latest_snapshot_id)return;const generation=life.current,tokens=new Map(job.cases.map(c=>[c.case_id,selection.claim(c.case_id)]));try{const values=await Promise.all(job.cases.map(c=>loadCase(job.latest_snapshot_id!,c.case_id)));if(generation!==life.current)return;const c=current.current,all={...c.cases,...Object.fromEntries(values.map(v=>[caseKey(v.snapshot_id,v.case_id),v]))};let next=c.project;for(const value of values)if(selection.current(value.candidate.id)===tokens.get(value.case_id))next=replaceFixedComparison(next,{kind:'ensemble_case',ensemble_id:value.ensemble_id,snapshot_id:value.snapshot_id,case_id:value.case_id},value.candidate.id,Object.fromEntries(c.runs.map(r=>[r.run_id,r])),all);commitProject(next);}catch(e){message(e,generation);}}
 async function cancel(job:EnsembleJob){const generation=life.current;try{const next=await mutation('cancel:'+job.ensemble_id+':'+job.epoch,id=>ensembleApi.cancel(job.ensemble_id,id));if(isCurrent(generation))mergeJob(next);}catch(e){message(e,generation);}}
 async function retry(job:EnsembleJob){const generation=life.current;let finish:(()=>void)|undefined;try{finish=beginWriteOperation();if(!job.latest_snapshot_id)throw Error('再開する固定台帳がまだありません。');const all=await Promise.all(job.cases.map(c=>loadCase(job.latest_snapshot_id!,c.case_id)));if(!isCurrent(generation))return;const ids=all.flatMap(c=>c.trials.filter(t=>['unstarted','cancelled','failed','interrupted'].includes(t.state)).map(t=>t.trial_id));const next=await mutation('retry:'+job.ensemble_id+':'+job.epoch+stableString(ids),id=>ensembleApi.retry(job.ensemble_id,ids,id));if(isCurrent(generation))mergeJob(next);}catch(e){message(e,generation);}finally{finish?.();}}
 return {jobs,plans,cases,caseReads,reloadCase,analyses,histories,error,busy,observations,refreshJob,prepare,start,stale,select,selectJob,cancel,retry,analysis,history,loadCase,acceptJob:mergeJob,pendingMutations,recoveryBusy,recoverMutation,getAnalysis:(id:string)=>ensembleApi.getAnalysis(id,reads.current.signal)};
}
