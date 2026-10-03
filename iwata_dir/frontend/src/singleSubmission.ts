import {ApiError,uncertainWrite} from './api';
import {stableString,type Candidate,type Run} from './domain';
import {putSubmission,removeSubmission,snapshotSubmissions,type SavedSubmission} from './submissionLedger';
import {beginWriteOperation,ownsWriteLease} from './writeLease';
export type SubmissionRow={requestId:string;candidate:Candidate;state:'unsubmitted'|'unknown'|'accepted'|'finished'|'rejected'|'cancelled';run?:Run;message?:string;notFound?:boolean};
export type SingleFamily=Omit<SavedSubmission,'payload'|'kind'>&{kind:'single-family';payload:{rows:SubmissionRow[];paused:boolean}};
export const submittedRun=(candidate:Candidate,id:string)=>({client_request_id:id,candidate_id:candidate.id,candidate_revision:candidate.revision,label:candidate.label,weather_source_id:candidate.weather_source_id,config:candidate.config});
const terminal=(row:SubmissionRow)=>['finished','rejected','cancelled'].includes(row.state);
/** One newly submitted flight at a time. Restoring/observing never submits work. */
export function createSingleSubmissionQueue(options:{send:(c:Candidate,id:string)=>Promise<Run>;lookup:(id:string)=>Promise<Run>;observe:(run:Run,c:Candidate,recovered:boolean)=>Promise<void>|void;changed:(rows:SingleFamily[])=>void;error:(e:unknown)=>void}){
 const initial=snapshotSubmissions('single-family');let families=initial.requests as SingleFamily[],disposed=false;
 const sending=new Set<string>();
 function emit(){if(!disposed)options.changed(structuredClone(families));}
 function save(f:SingleFamily){putSubmission(f);families=families.filter(x=>x.id!==f.id).concat(f);emit();}
 function done(f:SingleFamily){if(f.payload.rows.every(terminal)){removeSubmission(f.id);families=families.filter(x=>x.id!==f.id);emit();return true;}return false;}
 function active(candidateId:string){return families.some(f=>f.payload.rows.some(r=>r.candidate.id===candidateId)&&f.payload.rows.some(r=>!terminal(r)));}
 async function advance(id:string){
  const f=families.find(x=>x.id===id);if(disposed||!ownsWriteLease()||!f||f.payload.paused||sending.has(id)||f.payload.rows.some(r=>r.state==='accepted'||r.state==='unknown'))return;
  if(done(f))return;const row=f.payload.rows.find(r=>r.state==='unsubmitted');if(!row)return;
  const finish=beginWriteOperation();sending.add(id);
  try{row.state='unknown';row.notFound=false;save(f);const run=await options.send(structuredClone(row.candidate),row.requestId);if(disposed)return;row.state='accepted';row.run=run;row.message=undefined;save(f);await options.observe(run,row.candidate,false);}
  catch(e){if(!disposed){row.message=e instanceof Error?e.message:String(e);if(!uncertainWrite(e))row.state='rejected';f.payload.paused=true;try{save(f);}catch(storageError){options.error(storageError);}options.error(e);}}
  finally{sending.delete(id);finish();if(!disposed)void advance(id);}
 }
 async function start(candidates:Candidate[]){
  if(!candidates.length)return;if(candidates.some(c=>active(c.id)))throw Error('この候補を含む固定要求が未完了です。受付確認・再開を先に行ってください。');
  const f:SingleFamily={id:crypto.randomUUID(),kind:'single-family',createdAt:new Date().toISOString(),payload:{rows:structuredClone(candidates).map(candidate=>({requestId:crypto.randomUUID(),candidate,state:'unsubmitted'})),paused:false}};
  save(f);await advance(f.id);
 }
 function observe(run:Run){
  if(!ownsWriteLease())return;
  for(const f of families){const row=f.payload.rows.find(r=>r.run?.run_id===run.run_id);if(!row)continue;row.run=run;if(!['queued','running'].includes(run.state??''))row.state='finished';save(f);if(!done(f))void advance(f.id);}
 }
 async function confirm(id:string){
  const f=families.find(x=>x.id===id);if(!f)return;const finish=beginWriteOperation();try{f.payload.paused=true;save(f);
  for(const row of f.payload.rows){if(row.state!=='unknown'&&row.state!=='accepted')continue;
   try{const run=await options.lookup(row.requestId);if(disposed)return;
    if(stableString(run.spec?.submitted_input)!==stableString(submittedRun(row.candidate,row.requestId)))throw Error('受付済み要求の本文が保存した要求と一致しません。再送せず保存先を確認してください。');
    row.run=run;row.state=['queued','running'].includes(run.state??'')?'accepted':'finished';row.notFound=false;row.message=undefined;save(f);await options.observe(run,row.candidate,true);
   }catch(e){if(disposed)return;row.message=e instanceof Error?e.message:String(e);row.notFound=e instanceof ApiError&&e.status===404;save(f);options.error(e);}
  }done(f);}finally{finish();}
 }
 async function resume(id:string){
  const f=families.find(x=>x.id===id);if(!f)return;
  if(f.payload.rows.some(r=>r.state==='unknown'&&!r.notFound))throw Error('先に受付を確認してください。未確認要求を自動で再送しません。');
  for(const row of f.payload.rows)if(row.state==='unknown'&&row.notFound)row.state='unsubmitted';
  f.payload.paused=false;save(f);await advance(id);
 }
 function discardUnsent(id:string){const f=families.find(x=>x.id===id);if(!f)return;for(const row of f.payload.rows)if(row.state==='unsubmitted')row.state='cancelled';f.payload.paused=true;save(f);done(f);}
 function restore(){for(const f of families)f.payload.paused=true;if(initial.error)options.error(initial.error);emit();}
 return {start,observe,confirm,resume,discardUnsent,restore,active,dispose:()=>{disposed=true;},snapshot:()=>structuredClone(families)};
}
