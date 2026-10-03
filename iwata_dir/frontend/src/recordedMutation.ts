import {uncertainWrite,writeRequest} from './api';
import {stableString} from './domain';
import {putSubmission,removeSubmission,snapshotSubmissions,type SavedSubmission} from './submissionLedger';
import {beginWriteOperation} from './writeLease';
/** Persist the exact body before sending; a recovery call is always explicit. */
export async function recordedMutation<T>(kind:string,path:string,body:Record<string,unknown>):Promise<T>{
 const finish=beginWriteOperation();
 try{
 const id=kind+':'+String(body.client_request_id),previous=snapshotSubmissions(kind).requests.find(r=>r.id===id);
 const entry:SavedSubmission=previous??{id,kind,createdAt:new Date().toISOString(),payload:{path,body:structuredClone(body)}};
 if(stableString(entry.payload)!==stableString({path,body}))throw Error('同じ受付IDに異なる要求を割り当てません。保存した固定要求を確認してください。');
 putSubmission(entry);
 try{const result=await writeRequest<T>(entry.payload.path,{method:'POST',body:JSON.stringify(entry.payload.body)});removeSubmission(id);return result;}
 catch(e){if(!uncertainWrite(e))removeSubmission(id);throw e;}
 }finally{finish();}
}
