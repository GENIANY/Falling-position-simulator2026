import {useEffect,useRef,useState} from 'react';
import {readRequest,writeRequest,uncertainWrite} from './api';
import {putSubmission,removeSubmission,snapshotSubmissions} from './submissionLedger';
import {beginWriteOperation} from './writeLease';
import {historicalInput,sourceWindowIssue,type HistoricalSaved,type HistoricalDraft,type HistoricalPlan} from './historicalDomain';
import {utcToJstInput,jstInputToUtc,stableString,type Candidate,type WeatherSource} from './domain';
import {jobStateLabels,type EnsembleJob} from './ensembleDomain';

type Props={candidate:Candidate;sources:WeatherSource[];saved?:HistoricalSaved;historicalInterest?:Record<string,unknown>;onState:(v:HistoricalSaved)=>void;ensemble:any};
export function HistoricalPreparation(props:Props){
 const fallback:HistoricalDraft={windows:[],reason:'',selection_context:props.historicalInterest??{}};
 const value=props.saved??{draft:fallback},current=useRef({props,value});current.current={props,value};
 const [plan,setPlan]=useState<HistoricalPlan|null>(null),[busy,setBusy]=useState(''),[error,setError]=useState(''),[notice,setNotice]=useState(''),[refresh,setRefresh]=useState(0),alive=useRef(true);
 useEffect(()=>{alive.current=true;return()=>{alive.current=false;};},[]);
 const pending=snapshotSubmissions('historical-request'),unconfirmed=pending.requests.filter(r=>(r.payload as any)?.candidate_id===props.candidate.id);
 const fields=props.sources.filter(s=>s.time_kind==='analysis_valid_utc');
 function remember(patch:Partial<HistoricalSaved>){const c=current.current;const next={...c.value,...patch};current.current={...c,value:next};c.props.onState(next);}
 function draft(patch:Partial<HistoricalDraft>){remember({draft:{...current.current.value.draft,...patch}});}
 useEffect(()=>{const controller=new AbortController();if(value.plan_id&&plan?.plan_id!==value.plan_id)void readRequest<HistoricalPlan>('/ensemble-plans/'+encodeURIComponent(value.plan_id),controller.signal).then(p=>{if(!controller.signal.aborted)setPlan(p);}).catch(e=>{if(!controller.signal.aborted)setError(String(e));});return()=>controller.abort();},[value.plan_id,refresh]);
 let input='',issue='';try{input=stableString(historicalInput(props.candidate,value.draft));}catch(e){issue=e instanceof Error?e.message:String(e);}
 const stale=!!plan&&value.plan_input!==input;
 async function send(entry:{id:string;kind:string;createdAt:string;payload:any}){
  if(busy)return;let finish:(()=>void)|undefined;setBusy(entry.payload.action==='plan'?'原日時と入力を固定中':'原日時の試行を受付中');setError('');setNotice('');
  try{
   finish=beginWriteOperation();
   // A local write failure prevents the request. The original full body is the
   // only body that may be explicitly retried after an unknown response.
   putSubmission(entry);
   const result=await writeRequest<any>(entry.payload.path,{method:'POST',body:JSON.stringify(entry.payload.body)});
   if(!alive.current||current.current.props.candidate.id!==entry.payload.candidate_id)return;
   if(entry.payload.action==='plan'){
    setPlan(result);remember({plan_id:result.plan_id,plan_input:entry.payload.input});
    setNotice('原日時と共通機体を固定しました。未取得・支持不足の行も確認してください。');
   }else{props.ensemble.acceptJob(result);setNotice('固定した原日時の集合を受け付けました。完了後に地図へ表示できます。');}
   removeSubmission(entry.id);setRefresh(n=>n+1);
  }catch(e){if(!uncertainWrite(e))removeSubmission(entry.id);if(alive.current){setError((uncertainWrite(e)?'受付は未確認です。入力と要求IDを保っています。下の同一要求の確認・再送を利用してください。 ':'')+(e instanceof Error?e.message:String(e)));setRefresh(n=>n+1);}}
  finally{finish?.();if(alive.current)setBusy('');}
 }
 function prepare(){try{const body=historicalInput(props.candidate,value.draft),id=crypto.randomUUID();void send({id,kind:'historical-request',createdAt:new Date().toISOString(),payload:{candidate_id:props.candidate.id,action:'plan',path:'/ensemble-plans',body:{...body,client_request_id:id},input:stableString(body)}});}catch(e){setError(String(e));}}
 function submit(){if(!plan||stale)return;const id=crypto.randomUUID();void send({id,kind:'historical-request',createdAt:new Date().toISOString(),payload:{candidate_id:props.candidate.id,action:'submit',path:'/ensembles',body:{client_request_id:id,plan_id:plan.plan_id,plan_hash:plan.plan_hash}}});}
 function add(){const s=fields.find(s=>s.id===props.candidate.weather_source_id)??fields[0],time=s?.valid_times_utc?.[0]??props.candidate.config.launch.time_utc;draft({windows:[...value.draft.windows,{window_id:'W-'+crypto.randomUUID(),label:'原日時 '+(value.draft.windows.length+1),weather_source_id:s?.id??null,launch_time_utc:time,reason:''}]});}
 const jobs=(Object.values(props.ensemble.jobs) as EnsembleJob[]).filter(j=>j.cases.some(c=>c.case_id===props.candidate.id));
 return <section className="historical-preparation"><h3>原日時の気象窓で飛行を比較する</h3>
 <p>機体・地点・高度は上の入力を全日時に共通で使います。放球日時は各行で指定します。等重みの明示選択で、季節を代表する抽選や気象誤差分布ではありません。</p>
 {Object.keys(value.draft.selection_context).length>0&&<details><summary>気象分析から受け取った関心条件</summary><p>{String(value.draft.selection_context.label??'固定した気象分析')}</p><p>集計対象と飛行場の支持は別です。下の実日時をこの関心に合わせて明示選択します。</p><code>{String(value.draft.selection_context.analysis_id??'')}</code></details>}
 <label>この原日時集合を選ぶ理由<textarea value={value.draft.reason} onChange={e=>draft({reason:e.target.value})}/></label>
 {value.draft.windows.map((w,i)=>{const problem=sourceWindowIssue(w,props.candidate.config,props.sources);const change=(patch:Partial<typeof w>)=>draft({windows:value.draft.windows.map((x,k)=>k===i?{...x,...patch}:x)});return <fieldset key={w.window_id}><legend>原日時 {i+1}</legend><label>名称<input value={w.label} onChange={e=>change({label:e.target.value})}/></label><label>原日時の気象場<select value={w.weather_source_id??''} onChange={e=>change({weather_source_id:e.target.value||null})}><option value="">未取得・未登録（対象として残す）</option>{w.weather_source_id&&!fields.some(s=>s.id===w.weather_source_id)&&<option value={w.weather_source_id}>現在利用できない場</option>}{fields.map(s=><option key={s.id} value={s.id}>{s.label}</option>)}</select></label><label>原放球日時（JST）<input type="datetime-local" step="1" value={utcToJstInput(w.launch_time_utc)} onChange={e=>{if(e.target.value)change({launch_time_utc:jstInputToUtc(e.target.value)});}}/></label><small>UTC {w.launch_time_utc}</small><label>この日時を選ぶ理由<input value={w.reason} onChange={e=>change({reason:e.target.value})}/></label>{problem&&<p role="status">{problem}</p>}<button onClick={()=>draft({windows:value.draft.windows.filter((_,k)=>k!==i)})}>この日時を草案から外す</button></fieldset>;})}
 <button disabled={value.draft.windows.length>=256} onClick={add}>原日時を追加</button><p>予定 {value.draft.windows.length}日時。未取得や支持不足の行は計画・結果の台帳に残し、着地分布には含めません。</p>
 <button disabled={!!busy||!!issue||!!pending.error||unconfirmed.length>0} onClick={prepare}>{busy||'原日時と計算入力を固定して確認'}</button>
 {issue&&<p>{issue}</p>}{pending.error&&<p role="alert">{pending.error}</p>}{error&&<p role="alert">{error}</p>}{notice&&<p role="status">{notice}</p>}
 {unconfirmed.map(r=><div key={r.id} role="status"><p>受付未確認の{(r.payload as any).action==='plan'?'計画':'実行'}要求 · {r.createdAt}。現在の編集を混ぜず、保存した同じID・本文で受付結果を確かめます。</p><button disabled={!!busy} onClick={()=>void send(r)}>同一要求で確認・再送</button></div>)}
 {plan&&<div className="ensemble-plan"><h4>固定計画：実行可能 {plan.runnable_trial_count} / 予定 {plan.trial_count}</h4>{stale&&<p role="alert">入力・原日時・理由が変わっています。固定計画を作り直してください。</p>}<table><thead><tr><th>原日時（UTC）</th><th>場</th><th>計画状態</th></tr></thead><tbody>{plan.trials.map(t=><tr key={t.case_id+':'+t.draw_id}><td>{t.weather_window.launch_time_utc}</td><td>{t.weather_window.weather_snapshot?.label??'未登録'}</td><td>{t.preflight_error?.message??'時刻・放球点は支持内（全飛行の保証ではありません）'}</td></tr>)}</tbody></table><button className="primary" disabled={!!busy||stale||plan.status!=='ready'||unconfirmed.length>0} onClick={submit}>この原日時集合で実計算</button></div>}
 {jobs.map(j=><div className="ensemble-job" key={j.ensemble_id}><b>{jobStateLabels[j.state]??j.state} · {j.ensemble_id.slice(-10)}</b><p>予定 {j.planned_trials} / 着地 {j.counts.landed} / 支持停止 {j.counts.stopped} / 入力・気象不成立 {j.counts.invalid_input} / 未投入 {j.counts.unstarted} / 失敗 {j.counts.failed} / 中断 {j.counts.interrupted}</p><button onClick={()=>void props.ensemble.refreshJob(j.ensemble_id)}>状態を再確認</button>{j.cancellable&&<button onClick={()=>void props.ensemble.cancel(j)}>残る試行を取り消す</button>}{j.retryable&&<button onClick={()=>void props.ensemble.retry(j)}>未完了の試行を再開</button>}{j.latest_snapshot_id&&<button onClick={()=>void props.ensemble.selectJob(j)}>この原日時集合を地図へ表示</button>}</div>)}
 </section>;
}
