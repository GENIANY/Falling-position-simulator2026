import {request} from './api';
import {recordedMutation} from './recordedMutation';
import type {ResultEnvelope} from './domain';
import type {AnalysisArtifact,CaseResult,EnsembleJob,EnsemblePlan,PlanRequest} from './ensembleDomain';
const part=encodeURIComponent;
export const ENSEMBLE_READ_TIMEOUT_MS=30000;

/** Deadline includes both response headers and JSON body. Aborting this GET never cancels a calculation. */
function read<T>(path:string,signal?:AbortSignal):Promise<T>{
 return new Promise<T>((resolve,reject)=>{
  const controller=new AbortController();let settled=false,timer:ReturnType<typeof setTimeout>|undefined;
  const cleanup=()=>{if(timer!==undefined)clearTimeout(timer);signal?.removeEventListener('abort',abort);};
  const fail=(error:unknown,cancelRead=false)=>{if(settled)return;settled=true;cleanup();if(cancelRead)controller.abort();reject(error);};
  const abort=()=>fail(new DOMException('この画面での読取りを終了しました。','AbortError'),true);
  if(signal?.aborted){abort();return;}signal?.addEventListener('abort',abort,{once:true});
  timer=setTimeout(()=>{const error=new Error('読取りが30秒以内に完了しませんでした。計算は取り消していません。状態を再確認できます。');error.name='EnsembleReadTimeout';fail(error,true);},ENSEMBLE_READ_TIMEOUT_MS);
  // Racing the complete request also settles a caller when a transport ignores abort.
  Promise.resolve().then(()=>settled?undefined:request<T>(path,{signal:controller.signal})).then(value=>{
   if(settled)return;settled=true;cleanup();resolve(value as T);
  },error=>fail(error));
 });
}

export const ensembleApi={
 plan:(body:PlanRequest)=>recordedMutation<EnsemblePlan>('ensemble-write','/ensemble-plans',body as unknown as Record<string,unknown>),
 getPlan:(id:string,signal?:AbortSignal)=>read<EnsemblePlan>('/ensemble-plans/'+part(id),signal),
 jobs:(signal?:AbortSignal)=>read<{ensembles:EnsembleJob[]}>('/ensembles',signal),
 job:(id:string,signal?:AbortSignal)=>read<EnsembleJob>('/ensembles/'+part(id),signal),
 start:(plan:EnsemblePlan,id:string)=>recordedMutation<EnsembleJob>('ensemble-write','/ensembles',{client_request_id:id,plan_id:plan.plan_id,plan_hash:plan.plan_hash}),
 cancel:(id:string,requestId:string)=>recordedMutation<EnsembleJob>('ensemble-write','/ensembles/'+part(id)+'/cancel',{client_request_id:requestId}),
 retry:(id:string,trialIds:string[],requestId:string)=>recordedMutation<EnsembleJob>('ensemble-write','/ensembles/'+part(id)+'/retry',{client_request_id:requestId,trial_ids:trialIds}),
 snapshot:(id:string,signal?:AbortSignal)=>read<{snapshot_id:string;cases:{case_id:string}[]}>('/ensemble-snapshots/'+part(id),signal),
 case:(snapshotId:string,caseId:string,signal?:AbortSignal)=>read<CaseResult>('/ensemble-snapshots/'+part(snapshotId)+'/cases/'+part(caseId),signal),
 result:(snapshotId:string,trialId:string,signal?:AbortSignal)=>read<ResultEnvelope>('/ensemble-snapshots/'+part(snapshotId)+'/trials/'+part(trialId)+'/result',signal),
 analysis:(snapshotId:string,caseId:string,ids:string[]|null,regions:unknown,requestId:string)=>recordedMutation<AnalysisArtifact>('ensemble-write','/ensemble-analyses',{client_request_id:requestId,snapshot_id:snapshotId,case_id:caseId,selected_trial_ids:ids,region_set:regions,selection_origin:regions?'frontend-region-classifier':'manual',classifier_version:regions?'forecast-math/1':null}),
 getAnalysis:(id:string,signal?:AbortSignal)=>read<AnalysisArtifact>('/ensemble-analyses/'+part(id),signal),
};
