import type {Inventory,AcquisitionRequest,AcquisitionPlan,AcquisitionJob,Dependencies} from './weatherAcquisition';
import {requireServiceIdentity,serviceIdentity} from './serviceIdentity';
import {requireWriteLease,beginWriteOperation} from './writeLease';
import type {
  Project,
  ResultEnvelope,
  Run,
  WeatherSource,
  Candidate,
} from "./domain";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?:string,
  ) {
    super(message);
  }
}
export type GroundQuery={time_utc:string;latitude_deg:number;longitude_deg:number;launch_altitude_m:number};
export type GroundObservation={schema:'balloon.weather-ground/1';weather_source_id:string;weather_sha256:string;query:GroundQuery;ground_altitude_m:number;clearance_m:number;below_model_ground:boolean;ground_model:string;height_reference:string;is_fine_dem:false;scope:string};
export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const write = !['GET', 'HEAD', 'OPTIONS'].includes((init?.method ?? 'GET').toUpperCase());
  if (write) requireWriteLease();
  const instance = write ? requireServiceIdentity() : serviceIdentity();
  const finish=write?beginWriteOperation():()=>{};
  const abort=()=>finish();
  init?.signal?.addEventListener('abort',abort,{once:true});
  try {
  if(init?.signal?.aborted)throw new DOMException('要求の待機を終了しました。','AbortError');
  const response = await fetch("/api/v1" + path, {
    ...init,
    headers: { "Content-Type": "application/json", ...(path!=='/health'&&instance?{'X-Balloon-Instance-Id':instance}:{}), ...init?.headers, ...(write?{'X-Balloon-Instance-Id':instance!}:{}) },
  });
  let data: unknown;
  try {
    data = await response.json();
  } catch {
    throw new ApiError(
      "サービスから読める応答がありません。接続を確認してください。",
      response.status,
    );
  }
  if(init?.signal?.aborted)throw new DOMException('要求の待機を終了しました。','AbortError');
  if (!response.ok) {
    const d = data as { detail?: any; error?: any };
    throw new ApiError(
      typeof d.detail === "string"
        ? d.detail
        : JSON.stringify(d.detail ?? d.error ?? data),
      response.status,
      d.error?.code??d.detail?.code,
    );
  }
  return data as T;
  } finally {init?.signal?.removeEventListener('abort',abort);finish();}
}
export class WriteResponseUnknown extends Error {constructor(){super('60秒以内に受付応答を確認できませんでした。処理が取り消された・未受付とは判断しません。固定した要求を保持して、受付を確認してください。');this.name='WriteResponseUnknown';}}
export const uncertainWrite=(error:unknown)=>!(error instanceof ApiError)||error.code==='INSTANCE_MISMATCH'||error.status<400||error.status>=500;
/** A timeout ends only this wait. It never repeats a mutation. */
export function writeRequest<T>(path:string,init:RequestInit):Promise<T>{
 requireWriteLease();
 const instance=requireServiceIdentity();
 return new Promise<T>((resolve,reject)=>{const controller=new AbortController();let settled=false;
  const timer=setTimeout(()=>{if(settled)return;settled=true;controller.abort();reject(new WriteResponseUnknown());},60000);
  request<T>(path,{...init,headers:{...init.headers,'X-Balloon-Instance-Id':instance},signal:controller.signal}).then(value=>{if(settled)return;settled=true;clearTimeout(timer);resolve(value);},error=>{if(settled)return;settled=true;clearTimeout(timer);reject(error);});
 });
}
/** Deadline covers headers and body, even if a transport ignores abort. No POST is retried. */
export function readRequest<T>(path:string,signal?:AbortSignal):Promise<T>{
 return new Promise<T>((resolve,reject)=>{
  const controller=new AbortController();let settled=false,timer:ReturnType<typeof setTimeout>|undefined;
  const cleanup=()=>{if(timer!==undefined)clearTimeout(timer);signal?.removeEventListener('abort',abort);};
  const fail=(error:unknown)=>{if(settled)return;settled=true;cleanup();controller.abort();reject(error);};
  const abort=()=>fail(new DOMException('この画面での読取りを終了しました。','AbortError'));
  if(signal?.aborted){abort();return;}signal?.addEventListener('abort',abort,{once:true});
  timer=setTimeout(()=>fail(new Error('状態の読取りが20秒以内に終わりませんでした。処理の失敗とは限りません。再送せず再確認できます。')),20000);
  Promise.resolve().then(()=>settled?undefined:request<T>(path,{signal:controller.signal})).then(value=>{if(settled)return;settled=true;cleanup();resolve(value as T);},fail);
 });
}
export const api = {
  health:()=>readRequest<{instance_id:string;status:string;flight_execution:{available:boolean;restart_required:boolean;error?:{code:string;message:string}|null;queued_policy:string}}>('/health'),
  ground:(sourceId:string,expectedSha:string,query:GroundQuery)=>readRequest<GroundObservation>('/weather-sources/'+encodeURIComponent(sourceId)+'/ground?'+new URLSearchParams({expected_sha256:expectedSha,...Object.fromEntries(Object.entries(query).map(([key,value])=>[key,String(value)]))})),
  inventories:()=>readRequest<{inventories:Inventory[]}>('/weather-inventories'),
  refreshInventory:(body:{run_utc?:string;run_limit?:number})=>writeRequest<Inventory>('/weather-inventories/refresh',{method:'POST',body:JSON.stringify(body)}),
  weatherPlan:(body:AcquisitionRequest)=>writeRequest<AcquisitionPlan>('/weather-plans',{method:'POST',body:JSON.stringify(body)}),
  getWeatherPlan:(id:string)=>readRequest<AcquisitionPlan>('/weather-plans/'+encodeURIComponent(id)),
  acquisitions:()=>readRequest<{acquisitions:AcquisitionJob[]}>('/weather-acquisitions'),
  acquisition:(id:string,signal?:AbortSignal)=>readRequest<AcquisitionJob>('/weather-acquisitions/'+encodeURIComponent(id),signal),
  acquireWeather:(planId:string,requestId:string)=>writeRequest<AcquisitionJob>('/weather-acquisitions',{method:'POST',body:JSON.stringify({plan_id:planId,client_request_id:requestId})}),
  cancelAcquisition:(id:string)=>writeRequest<AcquisitionJob>('/weather-acquisitions/'+encodeURIComponent(id)+'/cancel',{method:'POST',body:'{}'}),
  retryAcquisition:(id:string)=>writeRequest<AcquisitionJob>('/weather-acquisitions/'+encodeURIComponent(id)+'/retry',{method:'POST',body:'{}'}),
  weatherStatus:()=>readRequest<{dependencies:Dependencies;max_queued:number;workers:number}>('/weather-status'),
  weather: () =>
    readRequest<{
      sources: WeatherSource[];
      source_errors?: {
        id: string;
        label?: string;
        code: string;
        message: string;
      }[];
    }>("/weather-sources"),
  project: () => readRequest<{ revision: number; project: Project }>("/project"),
  save: (revision: number, project: Project) =>
    writeRequest<{ revision: number; project: Project }>("/project", {
      method: "PUT",
      body: JSON.stringify({ expected_revision: revision, project }),
    }),
  runs: () => readRequest<{ runs: Run[] }>("/runs"),
  run: (id: string,signal?:AbortSignal) => readRequest<Run>("/runs/" + encodeURIComponent(id),signal),
  runRequest:(id:string)=>readRequest<Run>('/run-requests?'+new URLSearchParams({client_request_id:id})),
  result: (id: string,signal?:AbortSignal) =>
    readRequest<ResultEnvelope>("/runs/" + encodeURIComponent(id) + "/result",signal),
  start: (candidate: Candidate, clientRequestId: string) =>
    writeRequest<Run>("/runs", {
      method: "POST",
      body: JSON.stringify({
        client_request_id: clientRequestId,
        candidate_id: candidate.id,
        candidate_revision: candidate.revision,
        label: candidate.label,
        weather_source_id: candidate.weather_source_id,
        config: candidate.config,
      }),
    }),
};
