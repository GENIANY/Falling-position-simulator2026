import {readFailure,type FixedResultRead} from './fixedResultRead';
import {createJobObserver,type JobObservation} from './jobObservation';
import {singleRunIds} from './ensembleDomain';
import { useEffect, useReducer, useRef, useState } from "react";
import { api, uncertainWrite } from "./api";
import {createSingleSubmissionQueue,type SingleFamily} from './singleSubmission';
import {putSubmission,removeSubmission,snapshotSubmissions,type SavedSubmission} from './submissionLedger';
import { stableString } from "./domain";
import {serviceIdentity,setServiceIdentity} from './serviceIdentity';
import {claimWriteLease,observeWriteLease,releaseWriteLease,requireWriteLease,writeLeaseState,beginWriteOperation} from './writeLease';
import type { Candidate, Project, Run, WeatherSource,ResultEnvelope } from "./domain";
import {
  initialState,
  projectSaveSignature,
  workspaceReducer,
} from "./workspaceState";

const errorText = (e: unknown) => (e instanceof Error ? e.message : String(e));
const stateLabel: Record<string, string> = {
  queued: "待機中",
  running: "計算中",
  completed: "計算終了",
  failed: "計算失敗",
  cancelled: "取消済み",
  interrupted: "中断",
};

export function useWorkspace() {
  const [state, dispatch] = useReducer(
    workspaceReducer,
    undefined,
    initialState,
  );
  const current = useRef(state);
  current.current = state;
  const [restoration,setRestoration]=useState(0);
  const [resultReads,setResultReads]=useState<Record<string,FixedResultRead>>({});
  const resultReloads=useRef(new Map<string,Promise<void>>());
  const [sources, setSources] = useState<WeatherSource[]>([]);
  const [sourceWarnings, setSourceWarnings] = useState<string[]>([]);
  const [loading, setLoading] = useState(true),
    [saving, setSaving] = useState(false);
  const [message, setMessage] = useState(""),
    [error, setError] = useState("");
  const [pending, setPending] = useState<Record<string, string>>({});
  const epochs = useRef<Record<string, number>>({});
  const [families,setFamilies]=useState<SingleFamily[]>([]),[saveIntent,setSaveIntent]=useState<SavedSubmission|null>(()=>snapshotSubmissions('project-save').requests[0]??null);
  const familyQueue=useRef<ReturnType<typeof createSingleSubmissionQueue>|null>(null);
  const submissionEpochs=useRef<Record<string,number>>({});
  const [readErrors,setReadErrors]=useState<Record<string,string>>({}),[projectAvailable,setProjectAvailable]=useState(false);
  const [serviceHealth,setServiceHealth]=useState<Awaited<ReturnType<typeof api.health>>|null>(null),[healthError,setHealthError]=useState(''),[ledgerNotice,setLedgerNotice]=useState('');
  const healthReading=useRef<Promise<void>|null>(null);
  const [writeLease,setWriteLease]=useState(writeLeaseState);
  const loadGeneration = useRef(0),
    alive = useRef(true);
  type Watch={run:Run;candidateId:string;epoch:number;intent:'complete'|'restore';recoveryCandidate?:Candidate;loaded:boolean;observation?:JobObservation};
  const watches=useRef(new Map<string,Watch>());
  const observer=useRef<ReturnType<typeof createJobObserver<{run:Run;result?:ResultEnvelope}>>|null>(null);
  const [observations,setObservations]=useState<Record<string,JobObservation>>({});
  const dirty = state.savedSignature !== stableString(state.project);

  function watchingNeeded(id:string){const w=watches.current.get(id);return !!w&&(['queued','running'].includes(w.run.state??'')||!!w.run.result_available&&!w.loaded);}
  function syncPending(candidateId:string){
   // Observation ownership is independent from the latest result owner. Keep an
   // older active run visible even when a newer run has already been cancelled.
   const owner=[...watches.current.entries()].reverse().find(([id,w])=>w.candidateId===candidateId&&watchingNeeded(id));
   if(owner){const [,w]=owner;setPending(old=>({...old,[candidateId]:w.observation?.unavailable?'状態未確認（再送なし）':stateLabel[w.run.state??'queued']??String(w.run.state)}));}
   else setPending(old=>{const next={...old};delete next[candidateId];return next;});
  }
  function getObserver(){
   if(observer.current)return observer.current;const generation=loadGeneration.current;
   observer.current=createJobObserver<{run:Run;result?:ResultEnvelope}>({isCurrent:()=>alive.current&&generation===loadGeneration.current,active:watchingNeeded,
    read:async(id,signal)=>{const run=await api.run(id,signal);if(run.run_id!==id)throw Error('確認した計算の識別が応答と一致しません。');if(!alive.current||generation!==loadGeneration.current)return {run};const w=watches.current.get(id);if(w)w.run=run;dispatch({type:'polled',run});if(run.result_available){const result=await api.result(id,signal);if(result.run_id!==id)throw Error('固定結果の識別が要求と一致しません。');return {run,result};}if(run.state==='completed')throw Error('計算は終了しましたが保存結果を取得できません。状態の再確認が必要です。');return {run};},
    accept:(id,{run,result})=>{const w=watches.current.get(id);if(!w)return;w.run=run;if(result){w.loaded=true;dispatch({type:'result',run,result,candidateId:w.candidateId,epoch:w.epoch,intent:w.intent,recoveryCandidate:w.recoveryCandidate});setMessage(`${run.label??w.candidateId} の固定結果を確認しました。${result.result.status==='landed'?'着地':'停止: '+result.result.stop_reason?.code}。編集した入力と、待機中に選び直した結果は保持します。`);}syncPending(w.candidateId);familyQueue.current?.observe(run);},
    observe:(id,observation)=>{setObservations(old=>({...old,[id]:observation}));const w=watches.current.get(id);if(w){w.observation=observation;syncPending(w.candidateId);}}
   });return observer.current;
  }
  function watch(run:Run,candidateId:string,epoch:number,generation:number,intent:'complete'|'restore'='complete',recoveryCandidate?:Candidate){
   if(!alive.current||generation!==loadGeneration.current)return Promise.resolve();
   if(!watches.current.has(run.run_id))watches.current.set(run.run_id,{run,candidateId,epoch,intent,loaded:false});
   const existing=watches.current.get(run.run_id);if(existing&&recoveryCandidate){existing.recoveryCandidate=structuredClone(recoveryCandidate);existing.intent='restore';existing.epoch=epoch;}
   return getObserver().refresh(run.run_id);
  }
  function refreshRun(id:string){return watches.current.has(id)?getObserver().refresh(id):Promise.resolve();}
  function submissions(){
   if(!familyQueue.current){familyQueue.current=createSingleSubmissionQueue({send:api.start,lookup:api.runRequest,changed:setFamilies,error:e=>setError(errorText(e)),observe:async(run,candidate,recovered)=>{if(!alive.current)return;dispatch({type:'accepted',run,candidateId:candidate.id});await watch(run,candidate.id,submissionEpochs.current[candidate.id]??0,loadGeneration.current,recovered?'restore':'complete',recovered?candidate:undefined);}});familyQueue.current.restore();}
   return familyQueue.current;
  }

  const sourceGeneration=useRef(0);
  async function refreshSources() {
    const sourceEpoch=++sourceGeneration.current,generation=loadGeneration.current;
    const weather=await api.weather();
    if(alive.current&&generation===loadGeneration.current&&sourceEpoch===sourceGeneration.current){setSources(weather.sources);setSourceWarnings((weather.source_errors??[]).map(e=>`${e.label??e.id}: ${e.message}`));}
    return weather.sources;
  }
  async function load() {
    familyQueue.current?.dispose();familyQueue.current=null;setProjectAvailable(false);
    observer.current?.dispose();observer.current=null;watches.current.clear();setObservations({});
    sourceGeneration.current++;
    const generation = ++loadGeneration.current;
    setLoading(true);
    setResultReads({});
    resultReloads.current.clear();
    setPending({});
    setSaving(false);
    setError("");
    try {
      // Fix the state-directory identity before reading a plan or replay ledger.
      // A missing health response does not prevent read-only saved-result access.
      setServiceIdentity(null);setServiceHealth(null);setHealthError('');
      await claimWriteLease();if(!alive.current||generation!==loadGeneration.current)return;setWriteLease(writeLeaseState());
      let identified=false;
      try{const health=await api.health();if(!alive.current||generation!==loadGeneration.current)return;setServiceIdentity(health.instance_id);setServiceHealth(health);identified=true;}catch(e){if(!alive.current||generation!==loadGeneration.current)return;setHealthError(errorText(e));}
      const ledger=snapshotSubmissions();setLedgerNotice(ledger.notice??'');setSaveIntent(ledger.requests.find(r=>r.kind==='project-save')??null);
      const [weatherRead, savedRead, runsRead] = await Promise.allSettled([
        api.weather(),
        api.project(),
        api.runs(),
      ]);
      if (!alive.current || generation !== loadGeneration.current) return;
      const failed:Record<string,string>={};
      if(weatherRead.status==='fulfilled'){setSources(weatherRead.value.sources);setSourceWarnings((weatherRead.value.source_errors??[]).map(e=>`${e.label??e.id}: ${e.message}`));}else failed.weather=errorText(weatherRead.reason);
      if(runsRead.status==='rejected')failed.runs=errorText(runsRead.reason);
      if(savedRead.status==='rejected'){failed.project=errorText(savedRead.reason);setReadErrors(failed);return;}
      const saved=savedRead.value,available=runsRead.status==='fulfilled'?runsRead.value:{runs:[]};
      setReadErrors(failed);setProjectAvailable(identified);
      epochs.current = {};
      setRestoration(generation);
      dispatch({
        type: "restore",
        project: saved.project,
        revision: saved.revision,
        runs: available.runs,
      });
      setResultReads(Object.fromEntries(singleRunIds(saved.project).map(id=>[id,{state:'loading' as const}])));
      const selected = await Promise.allSettled(
        singleRunIds(saved.project).map(async (id) => {
          const [run, result] = await Promise.all([
            api.run(id),
            api.result(id),
          ]);
          return { run, result };
        }),
      );
      if (!alive.current || generation !== loadGeneration.current) return;
      selected.forEach((item, i) => {
        const id=singleRunIds(saved.project)[i];
        setResultReads(old=>({...old,[id]:item.status==='fulfilled'?{state:'ready'}:readFailure(item.reason)}));
        if (item.status === "fulfilled")
          dispatch({
            type: "result",
            ...item.value,
            candidateId: item.value.run.candidate_id ?? "",
            epoch: 0,
            intent: "restore",
          });
      });
      setMessage(
        saved.project.candidates.length
          ? "保存した草案と比較を開きました。実行中の処理は状態だけを確認し、再送しません。"
          : "保存気象から候補を作り、条件・延期時刻を比較できます。",
      );
      const orderedRuns=available.runs.filter(r=>r.kind!=="ensemble_trial"&&r.candidate_id)
        .sort((a,b)=>String(a.created_at??"").localeCompare(String(b.created_at??"")));
      const latestByCandidate=new Map<string,Run>();
      for(const run of orderedRuns)latestByCandidate.set(run.candidate_id!,run);
      // Latest result ownership must not be changed by observing older work.
      for(const [candidateId,run] of latestByCandidate)dispatch({type:"accepted",run,candidateId});
      for(const run of orderedRuns){
        const active=["queued","running"].includes(run.state??'');
        const latestFailure=latestByCandidate.get(run.candidate_id!)===run&&["failed","cancelled","interrupted"].includes(run.state??'');
        if(active||latestFailure)void watch(run,run.candidate_id!,0,generation,"restore");
      }
      submissions();
    } catch (e) {
      if (alive.current && generation === loadGeneration.current)
        setError(errorText(e));
    } finally {
      if (alive.current && generation === loadGeneration.current)
        setLoading(false);
    }
  }
  useEffect(() => {
    alive.current = true;
    void load();
    return () => {
      alive.current = false;
      loadGeneration.current++;
      observer.current?.dispose();observer.current=null;
      familyQueue.current?.dispose();familyQueue.current=null;
      releaseWriteLease();
    };
  }, []);
  useEffect(()=>observeWriteLease(value=>{
    setWriteLease(value);
    // A later holder must reread the outbox; an old queue may not resume itself.
    familyQueue.current?.dispose();familyQueue.current=null;
    if(value.state==='owner'&&serviceIdentity()){
      submissions();setSaveIntent(snapshotSubmissions('project-save').requests[0]??null);
    }
  }),[]);
  function refreshHealth():Promise<void>{
    if(healthReading.current)return healthReading.current;
    const generation=loadGeneration.current,expected=serviceIdentity();
    const work=(async()=>{try{const health=await api.health();if(!alive.current||generation!==loadGeneration.current)return;
      if(!expected||health.instance_id!==expected){setHealthError('接続先の保存状態が変わったか、まだ識別できていません。固定要求と現在の草案を保持しました。保存計画を明示的に読み直して接続先を確認してください。');return;}
      setServiceHealth(health);setHealthError('');
    }catch(e){if(alive.current&&generation===loadGeneration.current)setHealthError(errorText(e));}})().finally(()=>{if(healthReading.current===work)healthReading.current=null;});healthReading.current=work;return work;
  }
  useEffect(()=>{if(loading||!serviceIdentity())return;let disposed=false,timer:ReturnType<typeof setTimeout>;const next=()=>{timer=setTimeout(async()=>{await refreshHealth();if(!disposed)next();},15000);};next();return()=>{disposed=true;clearTimeout(timer);};},[loading,restoration]);
  useEffect(() => {
    const warn = (e: BeforeUnloadEvent) => {
      if (dirty && !loading) e.preventDefault();
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [dirty, loading]);

  async function selectResult(id: string, candidateId: string) {
    const generation = loadGeneration.current;
    const epoch = (epochs.current[candidateId] =
      (epochs.current[candidateId] ?? 0) + 1);
    dispatch({ type: "selection_requested", candidateId, epoch });
    try {
      const [run, result] = await Promise.all([api.run(id), api.result(id)]);
      if (alive.current && generation === loadGeneration.current)
        dispatch({
          type: "result",
          run,
          result,
          candidateId,
          epoch,
          intent: "select",
        });
    } catch (e) {
      if (alive.current && generation === loadGeneration.current)
        setError(errorText(e));
    }
  }
  // Re-read an already selected artifact. This never reselects it or starts a run.
  function reloadResult(id:string){
    const pending=resultReloads.current.get(id);if(pending)return pending;
    const generation=loadGeneration.current;
    setResultReads(old=>({...old,[id]:{state:'loading'}}));
    const work=(async()=>{try{const [run,result]=await Promise.all([api.run(id),api.result(id)]);
      if(!alive.current||generation!==loadGeneration.current)return;
      dispatch({type:'result',run,result,candidateId:run.candidate_id??'',epoch:0,intent:'restore'});
      setResultReads(old=>({...old,[id]:{state:'ready'}}));
    }catch(error){if(alive.current&&generation===loadGeneration.current)setResultReads(old=>({...old,[id]:readFailure(error)}));}
    })().finally(()=>{if(resultReloads.current.get(id)===work)resultReloads.current.delete(id);});
    resultReloads.current.set(id,work);return work;
  }
  async function startFamily(candidates:Candidate[]){
    setError('');for(const c of candidates)submissionEpochs.current[c.id]=epochs.current[c.id]??0;
    try{await submissions().start(candidates);}catch(e){setError(errorText(e));}
  }
  async function start(candidate:Candidate){await startFamily([candidate]);}
  async function confirmSave(){
    const intent=saveIntent??snapshotSubmissions('project-save').requests[0];if(!intent)return;
    setSaving(true);setError('');const generation=loadGeneration.current;
    let finish=()=>{};
    try{finish=beginWriteOperation();const actual=await api.project();if(!alive.current||generation!==loadGeneration.current)return;
      if(projectSaveSignature(actual.project)===projectSaveSignature(intent.payload.project)){
        removeSubmission(intent.id);dispatch({type:'saved',project:intent.payload.project,revision:actual.revision});setSaveIntent(null);setMessage('保存先の内容が送信した計画と一致しました。現在の編集は保持しています。');
      }else{const next={...intent,payload:{...intent.payload,confirmedRevision:actual.revision,confirmedProject:actual.project,notApplied:actual.revision===intent.payload.revision}};putSubmission(next);setSaveIntent(next);setError(actual.revision===intent.payload.revision?'この確認時点では送信した保存を確認できません。同じ固定内容を明示的に再送できます。':'保存先には別の版があります。編集と固定要求は保持しました。再読前に未確認の草案を確認してください。');}
    }catch(e){setError(errorText(e)+' 保存基準と草案は変更せず、固定要求を保持しています。照合の確定には送信権とブラウザへの記録が必要です。');}finally{finish();if(alive.current&&generation===loadGeneration.current)setSaving(false);}
  }
  function resolveSaveConflict(){
    if(!saveIntent?.payload.confirmedProject)return;
    try{requireWriteLease();removeSubmission(saveIntent.id);dispatch({type:'saved',project:saveIntent.payload.confirmedProject,revision:saveIntent.payload.confirmedRevision});setSaveIntent(null);setError('');setMessage('確認した保存先の版を基準にしました。草案は未保存のまま保持しています。内容を比較した上で改めて保存してください。');}
    catch(e){setError(errorText(e)+' 保存基準と草案は変更せず、固定要求を保持しています。');}
  }
  async function save(retry=false){
    if(!projectAvailable){setError('保存計画をまだ読めていません。保存先を確認してから保存してください。');return;}
    const existing=saveIntent??snapshotSubmissions('project-save').requests[0];
    if(existing&&(!retry||!existing.payload.notApplied)){setError('先の保存受付を確認してください。現在の草案で上書き送信しません。');return;}
    const intent:SavedSubmission=existing??{id:'project-save',kind:'project-save',createdAt:new Date().toISOString(),payload:{revision:current.current.revision,project:structuredClone(current.current.project)}};
    const generation=loadGeneration.current;setSaving(true);setError('');
    let finish=()=>{};
    try{finish=beginWriteOperation();putSubmission(intent);setSaveIntent(intent);const saved=await api.save(intent.payload.revision,intent.payload.project);if(!alive.current||generation!==loadGeneration.current)return;
      dispatch({type:'saved',project:intent.payload.project,revision:saved.revision});removeSubmission(intent.id);setSaveIntent(null);setMessage('草案と固定結果の組合せを保存しました。送信後の編集は保持しています。');
    }catch(e){if(alive.current&&generation===loadGeneration.current){if(!uncertainWrite(e)&&!existing){removeSubmission(intent.id);setSaveIntent(null);}setError(errorText(e)+' 編集と固定要求は保持しています。受付不明の場合は保存先を照合してください。');}}
    finally{finish();if(alive.current&&generation===loadGeneration.current)setSaving(false);}
  }
  async function retryRead(kind:string){
    const generation=loadGeneration.current;
    try{if(kind==='weather')await refreshSources();else if(kind==='runs'){const available=await api.runs();if(generation!==loadGeneration.current)return;for(const run of available.runs){dispatch({type:'polled',run});if(run.kind!=='ensemble_trial'&&run.candidate_id&&['queued','running'].includes(run.state??''))void watch(run,run.candidate_id,0,generation,'restore');}}else{await load();return;}
      if(generation===loadGeneration.current)setReadErrors(old=>{const next={...old};delete next[kind];return next;});
    }catch(e){if(generation===loadGeneration.current)setReadErrors(old=>({...old,[kind]:errorText(e)}));}
  }
  return {
    ...state,
    families,readErrors,retryRead,projectAvailable,saveIntent,confirmSave,serviceHealth,healthError,refreshHealth,ledgerNotice,writeLease,
    claimWriteLease:async()=>{await claimWriteLease(true);setWriteLease(writeLeaseState());if(writeLeaseState().state==='owner'){familyQueue.current?.dispose();familyQueue.current=null;submissions();setSaveIntent(snapshotSubmissions('project-save').requests[0]??null);setError('');setMessage('このタブへ送信担当を切り替えました。編集中の条件・表示結果は保持し、未確認要求は自動で再送していません。');}},
    retrySave:()=>save(true),
    resolveSaveConflict,
    restoreSubmissionDraft:()=>{if(saveIntent)dispatch({type:'project',project:structuredClone(saveIntent.payload.project)});},
    confirmFamily:async(id:string)=>{try{await submissions().confirm(id);}catch(e){setError(errorText(e));}},
    resumeFamily:async(id:string)=>{try{await submissions().resume(id);}catch(e){setError(errorText(e));}},
    discardUnsent:(id:string)=>{try{submissions().discardUnsent(id);}catch(e){setError(errorText(e));}},
    familyBusy:(id:string)=>families.some(f=>f.payload.rows.some(r=>r.candidate.id===id)&&f.payload.rows.some(r=>!['finished','rejected','cancelled'].includes(r.state))),
    startFamily,
    restoration,
    resultReads,
    reloadResult,
    runs: Object.values(state.runs),
    sources,
    sourceWarnings,
    loading,
    saving,
    message,
    error,
    pending,
    observations,
    refreshRun,
    dirty,
    setProject: (project: Project) => dispatch({ type: "project", project }),
    updateCandidate: (candidate: Candidate) =>
      dispatch({ type: "candidate", candidate }),
    setMessage,
    load,
    refreshSources,
    selectResult,
    claimSelection:(candidateId:string)=>{const epoch=(epochs.current[candidateId]??0)+1;epochs.current[candidateId]=epoch;dispatch({type:'selection_requested',candidateId,epoch});return epoch;},
    selectionToken:(candidateId:string)=>epochs.current[candidateId]??0,
    start,
    save,
  };
}
