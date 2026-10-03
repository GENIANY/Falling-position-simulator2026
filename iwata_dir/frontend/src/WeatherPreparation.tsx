import {useEffect,useRef,useState} from 'react';
import {api,uncertainWrite} from './api';
import {putSubmission,removeSubmission,snapshotSubmissions,type SavedSubmission} from './submissionLedger';
import {beginWriteOperation} from './writeLease';
import {createJobObserver,type JobObservation} from './jobObservation';
import {jstLabel,weatherSourceSummary,utcLabel,stableString} from './domain';
import type {Candidate,WeatherSource} from './domain';
import {acquisitionRequest,familyCandidates,sourceApplicationIssue,forecastValidTimes,boundsForCandidates,launchRegionIssue} from './weatherAcquisition';
import type {AcquisitionForm,AcquisitionJob,AcquisitionPlan,Inventory,Dependencies} from './weatherAcquisition';

type Step='input'|'plan'|'job';
type InitialRead='inventories'|'acquisitions'|'dependencies'|'plan';
const initialLabels:Record<InitialRead,string>={inventories:'保存した配布一覧',acquisitions:'取得履歴',dependencies:'取得環境',plan:'保存した固定計画'};
type Saved={step?:Step;preview?:{bounds:{west:number;east:number;south:number;north:number};stale:boolean;status:string;planId:string;runUtc?:string;windowStart?:string;windowEnd?:string};form?:AcquisitionForm;planId?:string;jobId?:string;requestId?:string;requestPlanId?:string};
type Props={candidates:Candidate[];sources:WeatherSource[];saved?:Saved;onState:(v:Saved)=>void;refreshSources:()=>Promise<WeatherSource[]>;apply:(ids:string[],sourceId:string)=>void;add:(source:WeatherSource)=>void;active?:Candidate;sourceWarnings?:string[];focusPreview:()=>void};
const phaseNames:Record<string,string>={queued:'待機',running:'取得中',cancelling:'取消処理中',completed:'取得完了',failed:'取得失敗',cancelled:'取消済',interrupted:'中断'};
const issueNames:Record<string,string>={LAUNCH_OUTSIDE_REGION:'対象候補の放球点が取得範囲の外です。地点を含む範囲へ調整して再計画してください。',RUN_NOT_OBSERVED:'選択した初期時刻は、この保存一覧では配布を確認できません。',REQUIRED_LEADS_NOT_LISTED:'必要な時刻のファイルが配布一覧にありません。別の初期時刻へ自動変更はしません。',DEPENDENCIES_UNAVAILABLE:'気象を解読するための依存ライブラリが不足しています。',MEMORY_BUDGET_EXCEEDED:'推定作業メモリが上限を超えます。取得範囲や飛行時間窓を見直してください。'};
const sourceHeight=(s:WeatherSource)=>{const h=(s.support as {minimum_top_geometric_m?:number}|undefined)?.minimum_top_geometric_m;return typeof h==='number'&&Number.isFinite(h)?`取得場上端の最小値 ${(h/1000).toFixed(2)} km ASL（全格子・全時刻）`:null;};
const mb=(bytes:number)=>Number.isFinite(bytes)?(bytes/1000000).toLocaleString('ja-JP',{maximumFractionDigits:1})+' MB':'—';
const message=(e:unknown)=>e instanceof Error?e.message:String(e);
const ongoing=(j:AcquisitionJob|null)=>!!j&&['queued','running','cancelling'].includes(j.state);

export function WeatherPreparation(props:Props){
 const seed=props.active??props.candidates[0],launch=seed?.config.launch??props.sources.find(s=>s.default_config)?.default_config?.launch;
 const [saved,setSaved]=useState<Saved>(()=>props.saved??{}),savedRef=useRef(saved),latest=useRef(props);latest.current=props;
 const [form,setForm]=useState<AcquisitionForm>(()=>props.saved?.form??{inventoryId:'',runUtc:'',fixedRun:'',latitude:launch?.latitude_deg??33.8,longitude:launch?.longitude_deg??135.4,halfWidth:50,halfHeight:50,maxMB:50,memoryMB:268.435456,targetIds:props.candidates.filter(c=>!c.parent_id).map(c=>c.id)});
 const formRef=useRef(form);formRef.current=form;
 const [inventories,setInventories]=useState<Inventory[]>([]),[jobs,setJobs]=useState<AcquisitionJob[]>([]),[job,setJob]=useState<AcquisitionJob|null>(null),[plan,setPlan]=useState<AcquisitionPlan|null>(null);
 const [acquisitionOpen,setAcquisitionOpen]=useState(false);
 const [step,setStep]=useState<Step>(()=>props.saved?.step??'input');
 const [busy,setBusy]=useState(''),[error,setError]=useState(''),[notice,setNotice]=useState(''),[dependencies,setDependencies]=useState<Dependencies|null>(null);
 const [outbox,setOutbox]=useState(()=>snapshotSubmissions('weather-acquisition'));
 const [unconfirmed,setUnconfirmed]=useState('');
 const life=useRef(0),alive=useRef(false),announced=useRef(new Set<string>()),selectedJob=useRef(''),planEpoch=useRef(0);
 const jobRef=useRef(job);jobRef.current=job;
 const observer=useRef<ReturnType<typeof createJobObserver<AcquisitionJob>>|null>(null);
 const [observation,setObservation]=useState<JobObservation|null>(null);
 const explicitJobEpoch=useRef(0);
 const [initialReads,setInitialReads]=useState<Partial<Record<InitialRead,{checking:boolean;error:string|null}>>>({});
 const initialRequests=useRef(new Map<InitialRead,Promise<void>>());
 function remember(patch:Partial<Saved>){const next={...savedRef.current,...patch};savedRef.current=next;setSaved(next);latest.current.onState(next);}
 function go(next:Step){setAcquisitionOpen(true);setStep(next);remember({step:next});}
 function edit(patch:Partial<AcquisitionForm>){const next={...formRef.current,...patch};formRef.current=next;setForm(next);remember({form:next});setNotice('');}
 function acceptJob(next:AcquisitionJob){selectedJob.current=next.acquisition_id;jobRef.current=next;setJob(next);setJobs(old=>[next,...old.filter(j=>j.acquisition_id!==next.acquisition_id)]);remember({jobId:next.acquisition_id});}
 function acceptExplicitJob(next:AcquisitionJob){explicitJobEpoch.current++;acceptJob(next);}
 async function perform<T>(label:string,operation:()=>Promise<T>,accept:(value:T)=>void,write=false){
  const generation=life.current;let finish:(()=>void)|undefined;setBusy(label);setError('');
  try{if(write)finish=beginWriteOperation();const value=await operation();if(alive.current&&generation===life.current)accept(value);}
  catch(e){if(alive.current&&generation===life.current){setError(message(e));if(write&&uncertainWrite(e))setUnconfirmed(label);}}
  finally{finish?.();if(alive.current&&generation===life.current)setBusy('');}
 }
 function loadInitial(kind:InitialRead):Promise<void>{
  const pending=initialRequests.current.get(kind);if(pending)return pending;
  const generation=life.current,restorePlanEpoch=planEpoch.current,current=()=>alive.current&&generation===life.current;
  setInitialReads(old=>({...old,[kind]:{checking:true,error:old[kind]?.error??null}}));
  const work=(async()=>{try{
   if(kind==='inventories'){const a=await api.inventories();if(current())setInventories(old=>[...old,...a.inventories.filter(i=>!old.some(x=>x.inventory_id===i.inventory_id))]);}
   else if(kind==='acquisitions'){
    const b=await api.acquisitions();if(!current())return;
    setJobs(old=>[...old,...b.acquisitions.filter(j=>!old.some(x=>x.acquisition_id===j.acquisition_id))]);
    const j=b.acquisitions.find(j=>j.acquisition_id===latest.current.saved?.jobId);
    if(j&&!selectedJob.current){selectedJob.current=j.acquisition_id;jobRef.current=j;setJob(j);}
   }else if(kind==='dependencies'){const c=await api.weatherStatus();if(current())setDependencies(c.dependencies);}
   else{const id=latest.current.saved?.planId;if(id){const p=await api.getWeatherPlan(id);if(current()&&restorePlanEpoch===planEpoch.current)setPlan(p);}}
   if(current())setInitialReads(old=>({...old,[kind]:{checking:false,error:null}}));
  }catch(e){if(current())setInitialReads(old=>({...old,[kind]:{checking:false,error:message(e)}}));}
  })().finally(()=>{if(initialRequests.current.get(kind)===work)initialRequests.current.delete(kind);});
  initialRequests.current.set(kind,work);return work;
 }
 useEffect(()=>{
  alive.current=true;life.current++;
  for(const kind of ['inventories','acquisitions','dependencies','plan'] as InitialRead[])void loadInitial(kind);
  return()=>{alive.current=false;life.current++;initialRequests.current.clear();};
 },[]);
 useEffect(()=>{
  setObservation(null);if(!job)return;const id=job.acquisition_id,generation=life.current;
  const watcher=createJobObserver<AcquisitionJob>({isCurrent:()=>alive.current&&generation===life.current&&selectedJob.current===id,active:()=>ongoing(jobRef.current),read:async(identity,signal)=>{const epoch=explicitJobEpoch.current;const value=await api.acquisition(identity,signal);if(epoch!==explicitJobEpoch.current)throw Error('操作前の状態応答は適用せず、改めて確認します。');if(value.acquisition_id!==identity)throw Error('取得処理の識別が応答と一致しません。');return value;},accept:(_id,value)=>{if(value.attempt<(jobRef.current?.attempt??0))throw Error('古い試行の状態を受信したため、現在の確認値を保持しました。');acceptJob(value);},observe:(_id,value)=>setObservation(value)});
  observer.current=watcher;watcher.track(id);return()=>{watcher.dispose();if(observer.current===watcher)observer.current=null;};
 },[job?.acquisition_id]);
 useEffect(()=>{if(job&&ongoing(job))observer.current?.track(job.acquisition_id);},[job?.state,job?.attempt]);
 useEffect(()=>{
  if(job?.state!=='completed'||announced.current.has(job.acquisition_id))return;
  announced.current.add(job.acquisition_id);let current=true;
  void latest.current.refreshSources().then(()=>{if(current)setNotice('取得が完了しました。候補の入力と表示中の計算結果は変更していません。適用先を確認してください。');}).catch(e=>{if(current)setError('保存気象一覧を更新できません。'+message(e));announced.current.delete(job.acquisition_id);});
  return()=>{current=false;};
 },[job?.acquisition_id,job?.state]);

 const family=familyCandidates(props.candidates,form.targetIds),inventory=inventories.find(i=>i.inventory_id===form.inventoryId);
 let request:ReturnType<typeof acquisitionRequest>|null=null,requestError='';try{request=acquisitionRequest(form,props.candidates);}catch(e){requestError=message(e);}
 const stale=!!plan&&(!request||stableString(plan.request)!==stableString(request));
 const locationIssue=plan?launchRegionIssue(plan.normalized_request.bounds,family):null;
 useEffect(()=>{if(plan)remember({preview:{bounds:plan.normalized_request.bounds,stale,status:plan.status,planId:plan.plan_id,runUtc:plan.normalized_request.run_utc,windowStart:plan.required_window.start_utc,windowEnd:plan.required_window.end_utc}});},[plan,stale]);
 const validTimes=plan?forecastValidTimes(plan):[];
 const sameAcquisition=!!(plan?.cache_key&&job?.cache_key&&plan.cache_key===job.cache_key);
 const jobPlanLabel=!plan?'保存した取得':job?.plan_id===plan.plan_id?'表示中の固定計画の取得':sameAcquisition?'同じ取得内容の保存処理':'別の固定計画の取得（前回・履歴）';
 const completed=job?.state==='completed'?props.sources.find(s=>s.id===job.weather_source_id):undefined;
 const applyIssue=sourceApplicationIssue(completed,family);
 const number=(key:'latitude'|'longitude'|'halfWidth'|'halfHeight'|'maxMB'|'memoryMB',label:string)=> <label>{label}<input type="number" step="any" value={Number.isFinite(form[key])?form[key]:''} onChange={e=>edit({[key]:e.target.value===''?NaN:Number(e.target.value)})}/></label>;
 async function refreshInventory(){
  let run:string|undefined;try{if(form.fixedRun){const d=new Date(form.fixedRun+'Z');if(!Number.isFinite(d.valueOf()))throw Error('初期時刻をUTCで入力してください。');run=d.toISOString();}}catch(e){setError(message(e));return;}
  const selectedBefore=[formRef.current.inventoryId,formRef.current.runUtc];
  await perform('配布一覧を確認中',()=>api.refreshInventory(run?{run_utc:run}:{run_limit:2}),value=>{
   setInventories(old=>[value,...old.filter(x=>x.inventory_id!==value.inventory_id)]);
   // An observation refresh never silently replaces an already selected cycle.
   const previous=formRef.current.runUtc;if(selectedBefore[0]===formRef.current.inventoryId&&selectedBefore[1]===previous)edit({inventoryId:value.inventory_id,runUtc:previous||value.runs[0]?.run_utc||''});
   setNotice('配布元の観測を保存しました。選択済みの初期時刻は保持しています。新しい予報を使う場合は明示的に選んでください。データ内容は取得時に検査します。');
  },true);
 }
 async function makePlan(){if(!request)return;planEpoch.current++;const captured=structuredClone(request);await perform('取得計画を作成中',()=>api.weatherPlan(captured),value=>{setPlan(value);remember({planId:value.plan_id});go('plan');},true);}
 async function submitSaved(entry:SavedSubmission){
  const p=entry.payload;if(typeof p?.plan_id!=='string'||typeof p?.client_request_id!=='string'||p.client_request_id!==entry.id){setError('保存した取得要求の内容を確認できません。元の記録を保持しています。');return;}
  await perform('固定した取得要求の受付を確認中',async()=>{try{return await api.acquireWeather(p.plan_id,p.client_request_id);}catch(e){if(!uncertainWrite(e)){removeSubmission(entry.id);setOutbox(snapshotSubmissions('weather-acquisition'));}throw e;}},value=>{
   acceptExplicitJob(value);go('job');setUnconfirmed('');
   try{removeSubmission(entry.id);}catch(e){setError('受付は確認できましたが、ブラウザの未確認要求記録を解消できません。'+message(e));}
   setOutbox(snapshotSubmissions('weather-acquisition'));
  },true);
 }
 async function start(){if(!plan||stale||locationIssue||plan.status!=='ready')return;const id=savedRef.current.requestPlanId===plan.plan_id&&savedRef.current.requestId?savedRef.current.requestId:crypto.randomUUID();const entry={id,kind:'weather-acquisition',createdAt:new Date().toISOString(),payload:{plan_id:plan.plan_id,client_request_id:id}};try{putSubmission(entry);}catch(e){setError(message(e));return;}setOutbox(snapshotSubmissions('weather-acquisition'));remember({requestId:id,requestPlanId:plan.plan_id});await submitSaved(entry);}
 async function selectJob(selected:AcquisitionJob){planEpoch.current++;await perform('保存した取得状態を読込中',async()=>({job:await api.acquisition(selected.acquisition_id),plan:await api.getWeatherPlan(selected.plan_id)}),value=>{acceptJob(value.job);setPlan(value.plan);remember({planId:value.plan.plan_id});go('job');});}

  return <section className="weather-preparation"><h2>使う気象を準備する</h2><p className="muted">保存した気象を選び、候補へ明示的に適用します。物理条件と計算済みの固定結果は保持します。</p>
  {unconfirmed&&<div className="weather-observation"><p role="status">{unconfirmed}：応答未確認です。処理の失敗・取消とは判断しません。配布一覧や取得履歴を読み直して確認してください。取消・再試行の応答が不明な場合は、再度操作する前に「状況を確認」で現在の状態を読み直してください。</p><button disabled={!!initialReads.inventories?.checking} onClick={()=>void loadInitial('inventories')}>配布観測の結果を読み直す</button><button disabled={!!initialReads.acquisitions?.checking} onClick={()=>void loadInitial('acquisitions')}>取得の受付状況を読み直す</button></div>}
  {outbox.error&&<p role="alert">{outbox.error}</p>}{outbox.requests.length>0&&<div className="weather-observation"><p>受付未確認の固定取得要求が{outbox.requests.length}件あります。現在編集中の取得条件とは別に保持しています。</p>{outbox.requests.map(entry=><p key={entry.id}>固定計画 {String(entry.payload?.plan_id??'不明').slice(0,8)} · 要求 {entry.id.slice(0,8)} <button disabled={!!busy} onClick={()=>void submitSaved(entry)}>この同じ要求IDで受付を確認</button></p>)}<small>同じIDの明示送信です。受付済なら同じ仕事を返し、未受付なら保存した固定計画の取得を開始します。現在の入力へ差し替えません。</small></div>}
  {(Object.entries(initialReads) as [InitialRead,{checking:boolean;error:string|null}][]).filter(([,read])=>read.error).map(([kind,read])=><div key={kind} className="weather-observation"><p role="status">{initialLabels[kind]}を確認できません。{read.error} 確認できた他の情報は保持しています。</p><button disabled={read.checking} onClick={()=>void loadInitial(kind)}>{initialLabels[kind]}を再読込</button></div>)}
<fieldset><legend>気象を適用する候補</legend><div className="weather-targets">{props.candidates.filter(c=>!c.parent_id).map(c=><label key={c.id}><input type="checkbox" checked={form.targetIds.includes(c.id)} onChange={e=>edit({targetIds:e.target.checked?[...form.targetIds,c.id]:form.targetIds.filter(id=>id!==c.id)})}/>{c.label} <small>延期子{familyCandidates(props.candidates,[c.id]).length-1}件を含む</small></label>)}{!props.candidates.length&&<p>保存例から候補を作り、放球日時とモデル条件を入力してください。</p>}</div>
   {family.length>0&&<><p className="family-window-summary">独立候補 {family.filter(c=>!c.parent_id).length}件＋延期 {family.filter(c=>c.parent_id).length}件 · {family.every(c=>Number.isFinite(Date.parse(c.config.launch.time_utc))&&Number.isFinite(Number(c.config.integration?.max_duration_s??14400)))?`${jstLabel(new Date(Math.min(...family.map(c=>Date.parse(c.config.launch.time_utc)))).toISOString())} ～ ${jstLabel(new Date(Math.max(...family.map(c=>Date.parse(c.config.launch.time_utc)+Number(c.config.integration?.max_duration_s??14400)*1000))).toISOString())}`:'日時・飛行時間を確認してください'}</p><details><summary>全対象の放球・飛行上限・高度条件を見る（閉じても全件を計画に含む）</summary><table><thead><tr><th>対象</th><th>放球 JST</th><th>最大飛行時間</th><th>高度の条件</th></tr></thead><tbody>{family.map(c=><tr key={c.id}><td>{c.label}</td><td>{jstLabel(c.config.launch.time_utc)}</td><td>{Number(c.config.integration?.max_duration_s??14400)/3600} h</td><td>{c.config.burst.mode==='altitude'?Number(c.config.burst.altitude_m)/1000+' km ASLで破裂':'径破裂 · 到達高度は事前未確定'}</td></tr>)}</tbody></table></details></>}
</fieldset>
  <details className="saved-weather" open><summary>保存済みの気象 · {props.sources.length}件</summary>{props.sources.map(s=><div className="weather-source" key={s.id}><b>{s.label??s.id}</b>{weatherSourceSummary(s).map(text=><small key={text}>{text}</small>)}{(s.valid_times_utc?.length??0)>0&&<details><summary>全ての有効時刻（UTC）</summary>{s.valid_times_utc!.map(t=><small key={t}>{utcLabel(t)}</small>)}</details>}{sourceHeight(s)&&<small>{sourceHeight(s)}</small>}{s.default_config&&<button onClick={()=>props.add(s)}>この保存例から候補を作る</button>}<button disabled={!family.length||!!sourceApplicationIssue(s,family)} onClick={()=>{props.apply(form.targetIds,s.id);setNotice('選択した候補と延期子へ保存気象を適用しました。物理条件と旧結果は保持しています。');}}>選択候補へ適用</button>{family.length>0&&sourceApplicationIssue(s,family)&&<small>{sourceApplicationIssue(s,family)}</small>}</div>)}<button disabled={!!busy} onClick={()=>void perform('保存気象一覧を更新中',props.refreshSources,()=>setNotice('保存気象一覧だけを更新しました。入力と比較結果は保持しています。'))}>保存気象一覧を更新</button></details>
  {job&&<div className="weather-job-summary"><span>{jobPlanLabel} · <b>{phaseNames[job.state]??job.state}</b> · {job.progress.completed_files}/{job.progress.total_files}ファイル · {job.reused?'保存資産を再利用 · ':''}新規取得 {mb(job.progress.bytes_downloaded)}{job.state==='completed'?' · 候補への適用は明示操作':''}</span><button onClick={()=>go('job')}>取得状況へ</button></div>}
  {job&&observation&&<div className="weather-observation"><p role="status">{observation.unavailable?'現在の取得状況を確認できません。上の状態と件数は最後に確認した値です。取得の失敗を意味しません。':observation.checking?'取得状況を確認中…':''}{observation.lastConfirmedAt&&' 最終確認 '+jstLabel(observation.lastConfirmedAt)}{observation.unavailable&&observation.nextRetryMs!==null&&` · 最大${observation.nextRetryMs/1000}秒後に再確認`}</p>{observation.message&&<p>{observation.message}</p>}<button disabled={observation.checking} onClick={()=>void observer.current?.refresh(job.acquisition_id)}>状況を再確認（取得の再送なし）</button></div>}
  <details className="gfs-acquisition" open={acquisitionOpen} onToggle={e=>setAcquisitionOpen(e.currentTarget.open)}><summary>GFS予報を取得する</summary><p>予報初期時刻を固定し、対象候補と延期列の飛行時間を含めて取得します。保存JRAを使う場合は上の一覧から選びます。GFS取得の操作は不要です。</p>
  <nav className="weather-steps" aria-label="気象を準備する行程">{([['input','1 取得条件'],['plan','2 固定計画'],['job','3 取得・適用']] as [Step,string][]).map(([id,label])=><button type="button" key={id} data-weather-step={id} aria-current={step===id?'step':undefined} onClick={()=>go(id)}>{label}{id==='plan'&&stale?' · 入力変更あり':''}</button>)}</nav>


  <div className="weather-input-stage" hidden={step!=='input'}><fieldset><legend>使う予報を選ぶ</legend><div className="weather-fields"><label>調べる初期時刻（任意・UTC）<input type="datetime-local" step="3600" value={form.fixedRun} onChange={e=>edit({fixedRun:e.target.value})}/><small>空欄なら直近の配布候補2件を確認します。</small></label><button disabled={!!busy} onClick={()=>void refreshInventory()}>配布一覧を更新</button></div>
   <InventoryObservation inventory={inventory} selectedRun={form.runUtc} select={runUtc=>edit({runUtc})}/>
   <label>保存した一覧<select value={form.inventoryId} onChange={e=>{const i=inventories.find(i=>i.inventory_id===e.target.value);edit({inventoryId:e.target.value,runUtc:i?.runs[0]?.run_utc??''});}}><option value="">一覧を選ぶ</option>{inventories.map(i=><option key={i.inventory_id} value={i.inventory_id}>{jstLabel(i.observed_at_utc)} に観測 · {i.runs.length}初期時刻</option>)}</select></label>
   <label>使用する初期時刻（UTC）<select value={form.runUtc} onChange={e=>edit({runUtc:e.target.value})}><option value="">初期時刻を選ぶ</option>{form.runUtc&&!inventory?.runs.some(r=>r.run_utc===form.runUtc)&&<option value={form.runUtc}>{form.runUtc} · この観測で配布未確認</option>}{inventory?.runs.map(r=><option key={r.run_utc} value={r.run_utc}>{r.run_utc} · 配布名を確認 {r.available_leads.length}時刻</option>)}</select></label><small>最新の全世界予報を保証する一覧ではありません。選択した初期時刻から別のrunへ自動で切り替えません。</small>
  </fieldset>
  <fieldset><legend>GFSの取得範囲</legend>
   {form.bounds?<><div className="weather-fields">{([['south','南端 °N'],['north','北端 °N'],['west','西端 °E'],['east','東端 °E']] as const).map(([key,label])=><label key={key}>{label}<input type="number" step="0.01" value={Number.isFinite(form.bounds![key])?form.bounds![key]:''} onChange={e=>edit({bounds:{...form.bounds!,[key]:e.target.value===''?NaN:Number(e.target.value)}})}/></label>)}</div><p>四端を直接調整できます。放球点を含む初期範囲で、全軌道を含む保証ではありません。</p></>:<div className="weather-fields">{number('latitude','取得中心 緯度 °N')}{number('longitude','取得中心 経度 °E')}{number('halfWidth','東西の片幅 km')}{number('halfHeight','南北の片幅 km')}</div>}<button disabled={!props.active} onClick={()=>props.active&&edit({bounds:undefined,latitude:props.active.config.launch.latitude_deg,longitude:props.active.config.launch.longitude_deg})}>注目地点と片幅から指定し直す</button><button disabled={!family.length} onClick={()=>{try{edit({bounds:boundsForCandidates(family)});}catch(e){setError(message(e));}}}>対象地点を含む範囲へ合わせる</button><small>全対象の放球点に各端0.25度以上の余白を置きます。飛行の広がりは固定計画の地図で確認し、必要な範囲へ調整してください。</small>
   <details><summary>取得量の上限</summary><div className="weather-fields">{number('maxMB','取得rawの合計上限 MB')}{number('memoryMB','推定作業メモリ上限 MB')}</div></details>
   <button disabled={!!busy||!request} onClick={()=>void makePlan()}>取得計画を確認</button>{requestError&&<small>{requestError}</small>}
  </fieldset></div>
  <div hidden={step!=='plan'}>{!plan&&<p>取得条件を入力して「取得計画を確認」を押すと、丸めた範囲・時間窓・取得量がここに表示されます。<button onClick={()=>go('input')}>取得条件へ</button></p>}
  {plan&&<fieldset className="acquisition-preview"><legend>固定した取得計画</legend>{stale&&<p className="notice">候補の放球地点・時間窓または取得条件が、この計画の作成後に変わりました。取得を始める前に計画を作り直してください。</p>}<dl><dt>初期時刻 UTC</dt><dd>{plan.normalized_request.run_utc}</dd><dt>必要な飛行時間窓</dt><dd>{jstLabel(plan.required_window.start_utc)} ～ {jstLabel(plan.required_window.end_utc)}</dd><dt>取得する気象の有効時刻</dt><dd>{validTimes.length?`${jstLabel(validTimes[0])} ～ ${jstLabel(validTimes.at(-1)!)}`:'—'}<details><summary>全{validTimes.length}時刻</summary>{validTimes.map(t=><div key={t}>{jstLabel(t)}</div>)}</details></dd><dt>格子へ外向きに丸めた範囲</dt><dd>{plan.normalized_request.bounds.south}–{plan.normalized_request.bounds.north}°N / {plan.normalized_request.bounds.west}–{plan.normalized_request.bounds.east}°E</dd><dt>地図での確認</dt><dd><button onClick={props.focusPreview}>取得範囲を地図で確認</button> 橙色の破線が取得計画。計算結果に使用した気象の境界とは区別します。</dd><dt>必要予報時間</dt><dd>{plan.normalized_request.lead_hours.join(', ')} h</dd><dt>取得量の見積り</dt><dd>{plan.estimate.grid_points.toLocaleString()}格子点 × {plan.estimate.time_count}時刻 · 配列 {mb(plan.estimate.float64_bytes)} / 作業メモリ推定 {mb(plan.estimate.estimated_working_memory_bytes)}<br/>raw合計上限 {mb(plan.estimate.max_download_bytes)}（新規取得・再利用・保全した未完了分の合計。通信量の見積りではありません）</dd></dl>
   {locationIssue&&<p role="alert">{locationIssue}</p>}{!locationIssue&&family.length>0&&<p>現在の全対象の放球点はこの矩形内です。飛行途中の支持は別に判定します。</p>}{plan.missing_leads.length>0&&<p role="alert">配布未確認の予報時間: {plan.missing_leads.join(', ')} h</p>}{plan.issues.map((issue,i)=><p key={i} role="alert">{issueNames[issue.code]??issue.message} ({issue.code})</p>)}<p>{stale?'現在の入力とは異なる計画です。取得を始めるには計画を作り直してください。':plan.status==='ready'?'この計画は取得を開始できます。':'この計画では取得を開始できません。'} 取得後も、軌道が領域や時間・高度支持を外れる場合は停止します。指定した破裂高度まで飛べることを保証する判定ではありません。</p><button className="primary" disabled={!!busy||stale||!!locationIssue||plan.status!=='ready'||dependencies?.available===false} onClick={()=>void start()}>この固定計画で気象を取得</button>
  </fieldset>}
  </div>
  {dependencies&&!dependencies.available&&<p role="alert">GFS取得の前提が不足（保存気象の選択とは別）: {dependencies.missing.map(d=>d.name+': '+d.message).join(' / ')}</p>}
  <div hidden={step!=='job'}>{!job&&(initialReads.acquisitions?.checking?<p>保存した取得履歴を確認中です…</p>:initialReads.acquisitions?.error?<p>保存した取得履歴をまだ確認できません。未開始とは判断しません。</p>:saved.jobId?<p>保存した取得が一覧に見つかりません。保存先と取得履歴を確認してください。<button onClick={()=>void loadInitial('acquisitions')}>取得履歴を再読込</button></p>:<p>まだ取得を開始していません。固定計画を確認した上で開始してください。<button onClick={()=>go('plan')}>固定計画へ</button></p>)}
  {job&&<fieldset className="acquisition-progress"><legend>取得状況と適用</legend><p>{jobPlanLabel}{plan&&job.plan_id!==plan.plan_id&&!sameAcquisition?'。この完了表示は、現在表示している計画を取得済みという意味ではありません。':''}</p><b>{phaseNames[job.state]??job.state} · 試行{job.attempt}{job.reused?' · 検査済み資産を再利用':''}</b><p>{{queued:'待機中',checking_saved_raw:'保存rawを照合',reusing_raw:'保存rawを再利用',downloading:'気象ファイルを取得',decoding:'物理量を解読・検査',completed:'保存済み',reused:'保存資産を再利用'}[job.progress.phase]??job.progress.phase} · {job.reused?'完成した資産を再利用':`${job.progress.completed_files}/${job.progress.total_files}ファイル`} · 新規{mb(job.progress.bytes_downloaded)} / 再利用{mb(job.progress.bytes_reused)}</p><progress max={Math.max(1,job.progress.total_files)} value={job.state==='completed'?Math.max(1,job.progress.total_files):job.progress.completed_files}/>{job.error&&<p role="alert">{job.error.message} ({job.error.code})</p>}<div className="row"><button disabled={!!busy||!job.cancellable} onClick={()=>void perform('取消を要求中',()=>api.cancelAcquisition(job.acquisition_id),acceptExplicitJob,true)}>取得を取り消す</button><button disabled={!!busy||!job.retryable} onClick={()=>void perform('取得を再試行中',()=>api.retryAcquisition(job.acquisition_id),acceptExplicitJob,true)}>同じ計画を再試行</button><button disabled={!!busy||!!observation?.checking} onClick={()=>void observer.current?.refresh(job.acquisition_id)}>状況を確認</button></div>{job.state==='completed'&&<>{completed&&sourceHeight(completed)&&<p>{sourceHeight(completed)}</p>}<p>適用先: {family.map(c=>c.label).join('・')||'未選択'}。現在の物理条件を保ち、使う気象だけを変更します。</p><button className="primary" disabled={!!applyIssue||!!busy} onClick={()=>{if(completed){props.apply(form.targetIds,completed.id);setNotice('完成した気象を選択候補と延期子へ適用しました。再計算は明示操作で行います。');}}}>完成した気象を選択候補へ適用</button>{applyIssue&&<p>{applyIssue}</p>}</>}</fieldset>}
  {jobs.length>0&&<details><summary>保存した取得履歴 · {jobs.length}件</summary>{jobs.map(j=><p key={j.acquisition_id}>{phaseNames[j.state]} · {j.acquisition_id.slice(0,8)} <button disabled={!!busy} onClick={()=>void selectJob(j)}>この取得を確認</button></p>)}</details>}
  </div>
  </details>
  {props.sourceWarnings?.map((text,i)=><p role="alert" key={i}>{text}</p>)}
  {busy&&<p role="status">{busy}…</p>}{error&&<p role="alert">{error}</p>}{notice&&<p role="status">{notice}</p>}
 </section>;
}

export function InventoryObservation({inventory,selectedRun,select}:{inventory:Inventory|undefined;selectedRun:string;select:(run:string)=>void}){
 if(!inventory)return null;const newest=[...inventory.runs].sort((a,b)=>Date.parse(b.run_utc)-Date.parse(a.run_utc))[0],errors=inventory.observation_errors??[];
 return <div className="inventory-observation"><p>観測 {jstLabel(inventory.observed_at_utc)} · {inventory.observation_status==='unavailable'?'今回の観測では利用可能な初期時刻を確認できません':inventory.observation_status==='partial'?'一部の一覧を確認できません':'保存した配布名の観測'}。一覧の観測と予報の選択は別です。</p>{selectedRun&&<p>選択中：{utcLabel(selectedRun)}{!inventory.runs.some(r=>r.run_utc===selectedRun)&&'（この一覧では配布未確認）'}</p>}{newest&&selectedRun!==newest.run_utc&&<p>今回観測した最も新しい初期時刻：{utcLabel(newest.run_utc)} <button onClick={()=>select(newest.run_utc)}>この初期時刻を選ぶ</button></p>}{errors.map((e,i)=><p key={i} role="status">{e.run_utc?utcLabel(e.run_utc):e.day??'配布日'} の一覧を確認できません：{e.message} ({e.code})。未配布とは断定しません。</p>)}</div>;
}
