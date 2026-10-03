/** Fixed requests survive a browser restart. This is an outbox, not a result store. */
import {requireServiceIdentity} from './serviceIdentity';
import {requireWriteLease} from './writeLease';
export type SavedSubmission={id:string;kind:string;createdAt:string;payload:any;instance_id?:string};
const KEY='balloon.pending-requests/1';
const object=(v:any)=>v!==null&&typeof v==='object'&&!Array.isArray(v);
const string=(v:any)=>typeof v==='string'&&v.length>0;
const candidate=(v:any)=>object(v)&&string(v.id)&&typeof v.label==='string'&&Number.isInteger(v.revision)&&string(v.weather_source_id)&&object(v.config)&&object(v.config.launch)&&string(v.config.launch.time_utc);
const project=(v:any)=>object(v)&&v.schema==='balloon.project/1'&&Array.isArray(v.candidates)&&v.candidates.every((c:any)=>object(c)&&string(c.id)&&typeof c.label==='string'&&Number.isInteger(c.revision)&&typeof c.weather_source_id==='string'&&object(c.config))&&Array.isArray(v.compare_run_ids);
function valid(value:any):boolean{
 if(!object(value)||!string(value.id)||!string(value.kind)||!string(value.createdAt)||!object(value.payload))return false;
 const p=value.payload;
 switch(value.kind){
  case 'single-family':return typeof p.paused==='boolean'&&Array.isArray(p.rows)&&p.rows.length>0&&p.rows.every((r:any)=>object(r)&&string(r.requestId)&&candidate(r.candidate)&&['unsubmitted','unknown','accepted','finished','rejected','cancelled'].includes(r.state)&&(!r.run||object(r.run)&&string(r.run.run_id)));
  case 'project-save':return Number.isInteger(p.revision)&&project(p.project)&&(!p.confirmedProject||project(p.confirmedProject));
  case 'ensemble-intent':return string(p.key)&&string(p.requestId);
  case 'ensemble-write':return string(p.path)&&p.path.startsWith('/ensemble')&&object(p.body)&&string(p.body.client_request_id);
  case 'weather-acquisition':return string(p.plan_id)&&string(p.client_request_id);
  case 'historical-request':return string(p.candidate_id)&&['plan','submit'].includes(p.action)&&['/ensemble-plans','/ensembles'].includes(p.path)&&object(p.body)&&string(p.body.client_request_id)&&(p.action!=='plan'||string(p.input));
  default:return false;
 }
}
function storage():Storage {
 try { if(typeof localStorage!=='undefined')return localStorage; } catch { /* Report before any POST. */ }
 throw Error('送信前の固定要求をブラウザへ保存できません。ブラウザの保存設定を確認してください。処理は開始していません。');
}
function rawSubmissions():SavedSubmission[]{
 const raw=storage().getItem(KEY);if(!raw)return [];
 const value=JSON.parse(raw);
 if(value?.schema!==KEY||!Array.isArray(value.requests)||!value.requests.every(valid))throw Error('保存した未確認要求の形式を読めません。元の記録を保持して再送を止めています。保存済み結果の読取りは続けられます。');
 return value.requests;
}
export function readSubmissions():SavedSubmission[]{const instance=requireServiceIdentity();return rawSubmissions().filter(r=>r.instance_id===instance);}
export function putSubmission(value:SavedSubmission){
 requireWriteLease();
 if(!valid(value))throw Error('固定要求の内容が保存形式と一致しません。送信を開始していません。');
 const instance=requireServiceIdentity();if(value.instance_id&&value.instance_id!==instance)throw Error('固定要求と現在の保存先が異なります。元の要求を保持し、別の保存先には送信しません。');
 value.instance_id=instance;
 const rows=rawSubmissions(),next=[...rows.filter(r=>r.id!==value.id||r.instance_id!==instance),structuredClone(value)];
 const encoded=JSON.stringify({schema:KEY,requests:next});storage().setItem(KEY,encoded);
 if(storage().getItem(KEY)!==encoded)throw Error('固定要求の保存を確認できません。送信を開始していません。');
}
export function removeSubmission(id:string){
 requireWriteLease();
 const instance=requireServiceIdentity(),rows=rawSubmissions();storage().setItem(KEY,JSON.stringify({schema:KEY,requests:rows.filter(r=>r.id!==id||r.instance_id!==instance)}));
}
export function snapshotSubmissions(kind?:string):{requests:SavedSubmission[];error:string;notice?:string}{
 try{const instance=requireServiceIdentity(),all=rawSubmissions(),foreign=all.filter(r=>r.instance_id!==instance);return {requests:all.filter(r=>r.instance_id===instance&&(!kind||r.kind===kind)),error:'',notice:foreign.length?`現在の保存先に結び付かない固定要求 ${foreign.length}件を元のまま保留しています。別の保存先・旧未識別の要求は再送しません。元のサービスへ戻して確認してください。`:''};}
 catch(e){return {requests:[],error:e instanceof Error?e.message:String(e)};}
}
