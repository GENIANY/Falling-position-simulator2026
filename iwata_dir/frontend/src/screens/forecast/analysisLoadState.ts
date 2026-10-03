import type {CaseResult,EnsembleAnalysis} from '../../ensembleDomain';

export function sameTrialIds(a:string[],b:string[]):boolean{
 return a.length===b.length&&new Set(a).size===a.length&&new Set(b).size===b.length&&a.every(id=>b.includes(id));
}

/** The overview belongs to this fixed case; only its complete, unchanged set is reusable. */
export function reusableOverviewAnalysis(collection:CaseResult,analysis:EnsembleAnalysis|null|undefined,ids:string[]|null,regionSet:unknown):EnsembleAnalysis|null{
 const all=collection.trials.map(t=>t.trial_id),selected=ids??all;
 return regionSet==null&&analysis&&sameTrialIds(selected,all)&&analysis.selected_count===all.length&&sameTrialIds(analysis.selected_trial_ids,all)?analysis:null;
}

export type AnalysisLoadStatus={state:'idle'|'pending'|'blocked'|'failed'|'ready';message:string};
type Entry<T>={status:AnalysisLoadStatus;value?:T};

/** Read-only restoration may run in any tab. Only never-sent writes resume on lease acquisition. */
export function createAnalysisLoadState<T>(options:{canWrite:()=>boolean;changed:()=>void}){
 const entries=new Map<string,Entry<T>>();let disposed=false;
 function read(key:string,request:{readOnly:boolean;load:()=>Promise<T>;accepted?:(value:T)=>void}):T|null{
  if(disposed)return null;
  const prior=entries.get(key);
  // A saved artifact reference may arrive after the first render. Its GET needs no lease.
  if(prior&&!(prior.status.state==='blocked'&&request.readOnly))return prior.status.state==='ready'?prior.value!:null;
  const entry:Entry<T>={status:{state:request.readOnly||options.canWrite()?'pending':'blocked',message:''}};
  entries.set(key,entry);if(entry.status.state==='blocked')return null;
  void Promise.resolve().then(async()=>{
   if(disposed)return;
   // Ownership can change between scheduling and dispatch. No ledger/write is touched here.
   if(!request.readOnly&&!options.canWrite()){entry.status={state:'blocked',message:''};return;}
   const value=await request.load();if(disposed)return;
   request.accepted?.(value);entry.value=value;entry.status={state:'ready',message:''};
  }).catch(error=>{if(!disposed)entry.status={state:'failed',message:error instanceof Error?error.message:String(error)};})
   .finally(()=>{if(!disposed)options.changed();});
  return null;
 }
 function retry(keys?:string[]){for(const [key,entry]of entries)if((!keys||keys.includes(key))&&['failed','blocked'].includes(entry.status.state))entries.delete(key);}
 function resumeBlocked(){if(options.canWrite())for(const [key,entry]of entries)if(entry.status.state==='blocked')entries.delete(key);}
 return {read,status:(key:string):AnalysisLoadStatus=>entries.get(key)?.status??{state:'idle',message:''},retry,resumeBlocked,dispose(){disposed=true;entries.clear();}};
}
