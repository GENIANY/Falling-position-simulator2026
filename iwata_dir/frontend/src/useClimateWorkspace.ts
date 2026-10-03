import {readFailure,type FixedResultRead} from './fixedResultRead';
import {useEffect,useRef,useState} from 'react';
import {climateApi} from './climateApi';
import {ownsWriteLease} from './writeLease';
import {climateError,defaultClimateQuery,normalizeClimateQuery,queryIssue,queryKey,type ClimateArtifact,type ClimateDescriptor,type ClimateQuery,type ClimateView} from './climateDomain';
export type ClimatePressureState={level_id:number;source_id:string;state:'waiting'|'running'|'blocked'|'failed';message:string};
export type ClimatePointState={cell_id:number;source_id:string;state:'waiting'|'running'|'blocked'|'failed';message:string};
type PendingClimateCalculation={token:number;due:number;run:()=>Promise<void>;finish:()=>void};
export function useClimateWorkspace(saved:ClimateView|undefined,onView:(v:ClimateView)=>void){
 const [sources,setSources]=useState<ClimateDescriptor[]>([]),[sourceErrors,setSourceErrors]=useState<string[]>([]),[artifact,setArtifact]=useState<ClimateArtifact|null>(null),[view,setView]=useState<ClimateView>(()=>saved??{schema:'balloon.climate-view/1'}),[status,setStatus]=useState('保存した集計を確認しています。'),[error,setError]=useState(''),[restoreError,setRestoreError]=useState(''),[busy,setBusy]=useState(false),[pressure,setPressure]=useState<ClimatePressureState|null>(null);
 const [restoreRead,setRestoreRead]=useState<FixedResultRead|undefined>(saved?.applied?{state:'loading'}:undefined);const restorePending=useRef<Promise<void>|null>(null);
 const [point,setPoint]=useState<ClimatePointState|null>(null),pointIntent=useRef<ClimatePointState|null>(null);
 const latest=useRef({view,onView});latest.current={view,onView};const fixed=useRef<ClimateArtifact|null>(null),catalog=useRef<ClimateDescriptor[]>([]),pressureIntent=useRef<ClimatePressureState|null>(null);
 const life=useRef(0),epoch=useRef(0),accepted=useRef(0),controllers=useRef(new Map<AbortController,ReturnType<typeof setTimeout>>()),receipt=useRef<{key:string;id:string}|null>(null);
 const pressureCache=useRef({generation:0,rows:new Map<string,ClimateArtifact>()});
 const calculation=useRef<{active:boolean;pending:PendingClimateCalculation|null;timer:ReturnType<typeof setTimeout>|null}>({active:false,pending:null,timer:null});
 function change(patch:Partial<ClimateView>,persist=true){const next={...latest.current.view,...patch,schema:'balloon.climate-view/1' as const};latest.current={...latest.current,view:next};setView(next);if(persist)latest.current.onView(next);}
 function resetPressureCache(){pressureCache.current.generation++;pressureCache.current.rows.clear();}
 function populationKey(q:ClimateQuery){const {level_id,...population}=normalizeClimateQuery(q);return queryKey(population);}
 function cacheKey(a:ClimateArtifact,q:ClimateQuery=a.query){return a.summary.source.dataset_sha256+':'+queryKey(normalizeClimateQuery(q));}
 function rememberPressure(a:ClimateArtifact,generation:number){const current=fixed.current;if(generation!==pressureCache.current.generation||!current||populationKey(a.query)!==populationKey(current.query)||a.summary.source.dataset_sha256!==current.summary.source.dataset_sha256)return;const rows=pressureCache.current.rows,key=cacheKey(a);rows.delete(key);rows.set(key,a);while(rows.size>6)rows.delete(rows.keys().next().value!);}
 function pressureState(next:ClimatePressureState|null){pressureIntent.current=next;setPressure(next);}
 function pointState(next:ClimatePointState|null){pointIntent.current=next;setPoint(next);}
 function discardPending(){const queue=calculation.current;if(queue.timer!==null)clearTimeout(queue.timer);queue.timer=null;queue.pending?.finish();queue.pending=null;}
 function invalidate(){epoch.current++;discardPending();pressureState(null);pointState(null);setBusy(false);}
 async function call<T>(fn:(signal:AbortSignal)=>Promise<T>,ms:number){const ac=new AbortController();const timer=setTimeout(()=>ac.abort(),ms);controllers.current.set(ac,timer);try{return await fn(ac.signal);}finally{clearTimeout(timer);controllers.current.delete(ac);}}
 const refreshSources=async()=>{const generation=life.current;try{const r=await call(signal=>climateApi.sources(signal),20000);if(generation!==life.current)return;resetPressureCache();catalog.current=r.sources;setSources(r.sources);setSourceErrors(r.errors.map(e=>climateError(new Error(e.code+': '+e.message))));if(!latest.current.view.draft_query&&r.sources.length)change({draft_query:defaultClimateQuery(r.sources[0])},false);}catch(e){if(generation===life.current)setSourceErrors([climateError(e)]);}};
 function restoreSaved(){
  if(restorePending.current)return restorePending.current;
  const a=latest.current.view.applied;if(!a)return Promise.resolve();
  invalidate();resetPressureCache();const generation=life.current,token=epoch.current,displayVersion=accepted.current;
  setRestoreRead({state:'loading'});setRestoreError('');
  const work=call(signal=>climateApi.get(a.analysis_id,signal),20000).then(r=>{
   if(generation!==life.current||displayVersion!==accepted.current)return;
   if(r.analysis_id!==a.analysis_id||r.summary.source.source_id!==a.source_id||r.query_hash!==a.query_hash||r.result_hash!==a.result_hash||r.summary.source.dataset_sha256!==a.dataset_sha256)throw new Error('保存した図と固定集計の識別情報が一致しません。');
   fixed.current=r;setArtifact(r);setRestoreRead({state:'ready'});setRestoreError('');
   if(token===epoch.current)setStatus('保存した固定集計を再表示しました。再集計は行っていません。');
  }).catch(e=>{if(generation===life.current&&displayVersion===accepted.current){setRestoreRead(readFailure(e));setRestoreError(climateError(e));}}).finally(()=>{if(restorePending.current===work)restorePending.current=null;});
  restorePending.current=work;return work;
 }
 useEffect(()=>{++life.current;void refreshSources();if(saved?.applied)void restoreSaved();else setStatus('資料と範囲を確認し、「この対象で再集計」を押してください。');return()=>{life.current++;epoch.current++;discardPending();resetPressureCache();restorePending.current=null;controllers.current.forEach((timer,c)=>{clearTimeout(timer);c.abort();});controllers.current.clear();};},[]);
 function editQuery(query:ClimateQuery){
  const previous=latest.current.view.draft_query;
  // Region/hour drafts do not change the frozen population of pressure exploration.
  if((!pressureIntent.current&&!pointIntent.current)||previous?.source_id!==query.source_id||previous?.level_id!==query.level_id||previous?.rose_cell_id!==query.rose_cell_id)invalidate();
  if(previous?.source_id!==query.source_id)resetPressureCache();
  setError('');change({draft_query:normalizeClimateQuery(structuredClone(query))});setStatus(fixed.current?'入力中の条件は未適用です。図は表示中の固定集計を保持しています。':'入力条件を設定しています。');
 }
 function pump(){
  const queue=calculation.current;if(queue.active||!queue.pending)return;
  if(queue.timer!==null){clearTimeout(queue.timer);queue.timer=null;}
  const wait=queue.pending.due-Date.now();if(wait>0){queue.timer=setTimeout(()=>{queue.timer=null;pump();},wait);return;}
  const job=queue.pending;queue.pending=null;queue.active=true;
  void job.run().finally(()=>{queue.active=false;job.finish();pump();});
 }
 function enqueue(q:ClimateQuery,kind:'explicit'|'pressure'|'point',delay:number){
  discardPending();const token=++epoch.current,generation=life.current,cacheGeneration=pressureCache.current.generation;
  setBusy(true);setError('');setStatus(kind==='point'?'風配の地点切替を確認しています。表示中の図は受領まで保持します。':kind==='pressure'?'選択した気圧面を確認しています。表示中の図は受領まで保持します。':'固定する集計を読み出しています。表示中の図はまだ変更していません。');
  return new Promise<void>(finish=>{
   calculation.current.pending={token,due:Date.now()+delay,finish,run:async()=>{
    if(generation!==life.current||token!==epoch.current)return;
    try{
     if(kind!=='explicit'){
      const d=catalog.current.find(s=>s.source_id===q.source_id),issue=d?queryIssue(q,d):'表示中の資料を現在利用できません。保存図は保持しています。';
      if(issue)throw new Error(issue);
      if(!ownsWriteLease())throw new Error('このタブには送信権がありません。担当を取得した後、選択した条件を再試行してください。');
      if(kind==='pressure')pressureState({level_id:q.level_id,source_id:q.source_id,state:'running',message:'表示中の母集団のまま気圧面を更新しています。'});
      else pointState({cell_id:q.rose_cell_id!,source_id:q.source_id,state:'running',message:'表示中の時期・UTC時刻・気圧面のまま、風配の地点を更新しています。'});
     }
     const source=catalog.current.find(s=>s.source_id===q.source_id);
     if(!source)throw new Error('表示中の資料を現在利用できません。保存図は保持しています。');
     // Resolve only the response comparison. Preserve the original request bytes and receipt binding.
     const expectedQuery={...structuredClone(q),bounds:structuredClone(q.bounds??source.bounds)};
     const expectedSource={source_id:source.source_id,dataset_sha256:source.dataset_sha256};
     const key=queryKey(q);if(receipt.current?.key!==key)receipt.current={key,id:crypto.randomUUID()};
     const r=await call(signal=>climateApi.create(q,receipt.current!.id,signal),60000);
     if(generation!==life.current)return;
     if(queryKey(normalizeClimateQuery(r.query))!==queryKey(expectedQuery)||r.summary.source.source_id!==expectedSource.source_id||r.summary.source.dataset_sha256!==expectedSource.dataset_sha256)throw new Error('要求した条件と受領した集計が一致しません。');
     if(kind==='pressure')rememberPressure(r,cacheGeneration);
     if(token!==epoch.current)return;
     accepted.current++;fixed.current=r;setRestoreRead({state:'ready'});setRestoreError('');setArtifact(r);
     change({applied:{analysis_id:r.analysis_id,source_id:r.summary.source.source_id,dataset_sha256:r.summary.source.dataset_sha256,query_hash:r.query_hash,result_hash:r.result_hash},...(kind==='explicit'?{draft_query:structuredClone(r.query)}:{})});
     pressureState(null);pointState(null);setStatus(kind==='pressure'?'表示中の母集団のまま気圧面を更新しました。地域・UTC時刻の未適用編集は保持しています。':kind==='point'?'風配の元格子点を更新しました。地域・UTC時刻・気圧面の未適用編集は保持しています。':'固定集計を受領し、図を更新しました。');
    }catch(e){if(generation===life.current&&token===epoch.current){const message=climateError(e);setError(message);if(kind==='pressure')pressureState({level_id:q.level_id,source_id:q.source_id,state:ownsWriteLease()?'failed':'blocked',message});if(kind==='point')pointState({cell_id:q.rose_cell_id!,source_id:q.source_id,state:ownsWriteLease()?'failed':'blocked',message});setStatus('集計の応答を確認できません。図は保持しています。同じ入力の再試行は同じ受付IDで照合します。');}}
    finally{if(generation===life.current&&token===epoch.current)setBusy(false);}
   }};pump();
  });
 }
 function calculate(){
  invalidate();resetPressureCache();const raw=latest.current.view.draft_query,q=raw?normalizeClimateQuery(structuredClone(raw)):undefined,d=catalog.current.find(s=>s.source_id===q?.source_id);
  if(!q||!d){setError('利用できる資料を選択してください。');return Promise.resolve();}const issue=queryIssue(q,d);if(issue){setError(issue);return Promise.resolve();}
  return enqueue(q,'explicit',0);
 }
 function selectPressure(level_id:number){
  if(pointIntent.current&&['waiting','running'].includes(pointIntent.current.state))return;
  const a=fixed.current;if(!a)return;
  // Later input may replace the target, but never extend the first 300ms deadline.
  const due=calculation.current.pending?.due??Date.now()+300;
  invalidate();const q=normalizeClimateQuery({...structuredClone(a.query),level_id}),d=catalog.current.find(s=>s.source_id===q.source_id),draft=latest.current.view.draft_query;
  const issue=d?queryIssue(q,d):'表示中の資料を現在利用できません。保存図は保持しています。';
  if(issue||draft?.source_id!==q.source_id){pressureState({level_id,source_id:q.source_id,state:'blocked',message:issue??'別の資料を編集中です。共通対象を明示的に適用してから探索してください。'});return;}
  // Reflect only the user's pressure choice; response adoption never replaces the draft.
  if(draft.level_id!==level_id)change({draft_query:{...draft,level_id}});
  rememberPressure(a,pressureCache.current.generation);
  if(queryKey(q)===queryKey(normalizeClimateQuery(a.query))){setError('');setStatus('表示中の気圧面に戻りました。途中の更新要求は図へ適用しません。');return;}
  const cached=pressureCache.current.rows.get(cacheKey(a,q));
  if(cached){rememberPressure(cached,pressureCache.current.generation);accepted.current++;fixed.current=cached;setArtifact(cached);setRestoreRead({state:'ready'});setRestoreError('');setError('');change({applied:{analysis_id:cached.analysis_id,source_id:cached.summary.source.source_id,dataset_sha256:cached.summary.source.dataset_sha256,query_hash:cached.query_hash,result_hash:cached.result_hash}});setStatus('この画面で受領済みの気圧面を再表示しました。追加の再集計は行っていません。');return;}
  if(!ownsWriteLease()){pressureState({level_id,source_id:q.source_id,state:'blocked',message:'このタブには送信権がありません。担当を取得した後、この気圧面を再試行してください。'});return;}
  pressureState({level_id,source_id:q.source_id,state:'waiting',message:'表示中の母集団のまま、選択した気圧面を自動更新します。'});
  void enqueue(q,'pressure',Math.max(0,due-Date.now()));
 }

 function retryPressure(){const p=pressureIntent.current;if(p)selectPressure(p.level_id);}
 function selectPoint(cell_id:number){
  const a=fixed.current;if(!a)return;
  invalidate();const q=normalizeClimateQuery({...structuredClone(a.query),rose_cell_id:cell_id}),d=catalog.current.find(s=>s.source_id===q.source_id),draft=latest.current.view.draft_query;
  const issue=d?queryIssue(q,d):'表示中の資料を現在利用できません。保存図は保持しています。';
  if(issue||draft?.source_id!==q.source_id){pointState({cell_id,source_id:q.source_id,state:'blocked',message:issue??'別の資料を編集中です。共通対象を明示的に適用してから地点を選択してください。'});return;}
  // Only this native point is applied; other edits remain a draft, including pressure.
  if(draft.rose_cell_id!==cell_id)change({draft_query:{...draft,rose_cell_id:cell_id}});
  if(queryKey(q)===queryKey(normalizeClimateQuery(a.query))){setError('');setStatus('表示中の風配地点に戻りました。途中の更新要求は図へ適用しません。');return;}
  if(!ownsWriteLease()){pointState({cell_id,source_id:q.source_id,state:'blocked',message:'このタブには送信権がありません。担当を取得した後、この地点を再試行してください。'});return;}
  resetPressureCache();pointState({cell_id,source_id:q.source_id,state:'waiting',message:'表示中の条件のまま、選択した元格子の風配へ切り替えます。'});void enqueue(q,'point',0);
 }
 function retryPoint(){const p=pointIntent.current;if(p)selectPoint(p.cell_id);}
 function show(patch:Partial<ClimateView>){change(patch);}
 return {sources,sourceErrors,artifact,view,status,restoreRead,restoreSaved,error:error||restoreError,busy,pressure,point,refreshSources,editQuery,calculate,selectPressure,retryPressure,selectPoint,retryPoint,show};
}
