import {claimWriteLease,releaseWriteLease} from './writeLease';
import {setServiceIdentity} from './serviceIdentity';
import {afterEach,beforeEach,describe,expect,it,vi} from 'vitest';
const {h,normal}=vi.hoisted(()=>({h:{current:null as any},normal:{health:vi.fn(),weather:vi.fn(),project:vi.fn(),runs:vi.fn(),run:vi.fn(),result:vi.fn(),start:vi.fn(),save:vi.fn(),runRequest:vi.fn()}}));
vi.mock('react',()=>({useRef:(v:any)=>h.current.ref(v),useState:(v:any)=>h.current.state(v),useEffect:(f:any,d:any[])=>h.current.effect(f,d),useReducer:(f:any,a:any,init:any)=>h.current.reducer(f,a,init)}));
vi.mock('./api',async()=>({...await vi.importActual<any>('./api'),api:normal}));
import {WriteResponseUnknown} from './api';
import {snapshotSubmissions} from './submissionLedger';
import {submittedRun} from './singleSubmission';
import {useWorkspace} from './useWorkspace';
function harness(fn:()=>any){let cursor=0;const slots:any[]=[],effects:any[]=[],cleanups:any[]=[];const owner={ref:(v:any)=>{const i=cursor++;return slots[i]??(slots[i]={current:v});},state:(v:any)=>{const i=cursor++;if(!(i in slots))slots[i]=typeof v==='function'?v():v;return [slots[i],(n:any)=>{slots[i]=typeof n==='function'?n(slots[i]):n;}];},reducer:(f:any,v:any,init:any)=>{const [s,set]=owner.state(()=>init(v));return [s,(a:any)=>set((old:any)=>f(old,a))];},effect:(f:any,d:any[])=>{const i=cursor++;if(!slots[i]||d.some((v,j)=>!Object.is(v,slots[i][j]))){slots[i]=d;effects.push(()=>{cleanups[i]?.();cleanups[i]=f();});}}};return {render:()=>{cursor=0;h.current=owner;const r=fn();effects.splice(0).forEach(f=>f());return r;},unmount:()=>cleanups.forEach(f=>f?.())};}
const flush=async()=>{for(let i=0;i<20;i++)await Promise.resolve();};
const deferred=()=>{let resolve!:(v:any)=>void,reject!:(e:any)=>void;const promise=new Promise<any>((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};};

const config:any={launch:{time_utc:'2026-09-30T01:17:13Z',latitude_deg:34,longitude_deg:135,altitude_m:150},ascent:{mode:'constant_speed',speed_m_s:5},burst:{mode:'altitude',altitude_m:30000},descent:{mode:'rated_speed'}};
const candidate:any={id:'A',label:'original',revision:1,weather_source_id:'w',config};
const original:any={schema:'balloon.project/1',title:'p',candidates:[candidate],compare_run_ids:['old'],ui_state:{forecast_real:{active:'A'}}};
const oldRun={run_id:'old',candidate_id:'A',state:'completed',result_available:true};
const result={run_id:'old',result:{status:'landed',config},weather_snapshot:{id:'w'}};
beforeEach(async()=>{releaseWriteLease();vi.stubGlobal('navigator',{locks:{request:(_name:any,_options:any,callback:any)=>Promise.resolve(callback({name:'test-lock'}))}});await claimWriteLease();setServiceIdentity('test-instance');vi.useFakeTimers();const storage=new Map<string,string>();vi.stubGlobal('localStorage',{getItem:(k:string)=>storage.get(k)??null,setItem:(k:string,v:string)=>storage.set(k,v),removeItem:(k:string)=>storage.delete(k)});vi.stubGlobal('window',{addEventListener:vi.fn(),removeEventListener:vi.fn()});Object.values(normal).forEach(f=>f.mockReset());normal.health.mockResolvedValue({instance_id:'test-instance',status:'ok',flight_execution:{available:true,restart_required:false,queued_policy:'preserved_without_automatic_resubmission'}});normal.weather.mockResolvedValue({sources:[]});normal.project.mockResolvedValue({revision:4,project:structuredClone(original)});normal.runs.mockResolvedValue({runs:[oldRun]});normal.run.mockResolvedValue(oldRun);normal.result.mockResolvedValue(result);});
afterEach(()=>{vi.useRealTimers();vi.unstubAllGlobals();});
async function setup(){const x=harness(useWorkspace);x.render();await flush();expect(x.render().loading).toBe(false);return x;}
const edited=(label:string)=>({...structuredClone(original),candidates:[{...structuredClone(candidate),label,revision:2}]});
describe('fixed project write recovery',()=>{
 it('keeps the sent draft across reload and confirms it without replacing newer edits or repeating PUT',async()=>{
  const x=await setup(),sent=edited('sent'),later=edited('edited after submission');x.render().setProject(sent);x.render();normal.save.mockRejectedValueOnce(new WriteResponseUnknown());await x.render().save();expect(snapshotSubmissions('project-save').requests[0].payload.project).toEqual(sent);x.unmount();
  const y=await setup();y.render().setProject(later);y.render();normal.project.mockResolvedValue({revision:5,project:sent});await y.render().confirmSave();const w=y.render();expect(w.project).toEqual(later);expect(w.dirty).toBe(true);expect(w.revision).toBe(5);expect(w.saveIntent).toBeNull();expect(snapshotSubmissions('project-save').requests).toEqual([]);expect(normal.save).toHaveBeenCalledTimes(1);y.unmount();
 });
 it('recognizes backend-added envelope defaults after an ambiguous PUT while keeping later graph edits',async()=>{
  const x=await setup(),sent:any={...edited('historical'),candidates:[{...candidate,analysis_mode:'historical_windows'}],compare_results:[{kind:'ensemble_case',ensemble_id:'e',snapshot_id:'s',case_id:'A'}],ui_state:{season_real:{metric:'h',optional:undefined}}};x.render().setProject(sent);x.render();normal.save.mockRejectedValueOnce(new WriteResponseUnknown());await x.render().save();const later=structuredClone(sent);later.ui_state.season_real.metric='en';x.render().setProject(later);x.render();
  const stored=JSON.parse(JSON.stringify(sent));stored.candidates=stored.candidates.map((c:any)=>({parent_id:null,delay_minutes:null,sampling:null,analysis_mode:'forecast',...c}));stored.compare_results=stored.compare_results.map((r:any)=>({...r,analysis_id:null}));normal.project.mockRejectedValueOnce(Error('one GET reply lost')).mockResolvedValueOnce({revision:5,project:stored});
  await x.render().confirmSave();expect(x.render().saveIntent).not.toBeNull();expect(x.render().revision).toBe(4);await x.render().confirmSave();expect(x.render().saveIntent).toBeNull();expect(x.render().revision).toBe(5);expect(x.render().project.ui_state.season_real.metric).toBe('en');expect(x.render().dirty).toBe(true);expect(normal.save).toHaveBeenCalledOnce();x.unmount();
 });
 it('only resends the captured body after a read proves the old revision is still current',async()=>{
  const x=await setup(),sent=edited('sent'),later=edited('later');x.render().setProject(sent);x.render();normal.save.mockRejectedValueOnce(new WriteResponseUnknown()).mockResolvedValueOnce({revision:5});await x.render().save();x.render().setProject(later);x.render();await x.render().retrySave();expect(normal.save).toHaveBeenCalledTimes(1);await x.render().confirmSave();expect(x.render().saveIntent.payload.notApplied).toBe(true);await x.render().retrySave();expect(normal.save.mock.calls).toEqual([[4,sent],[4,sent]]);expect(x.render().project).toEqual(later);expect(x.render().dirty).toBe(true);x.unmount();
 });
 it('refuses a changed remote revision until an explicit conflict decision and preserves both drafts',async()=>{
  const x=await setup(),sent=edited('sent'),later=edited('later'),remote=edited('someone else');x.render().setProject(sent);x.render();normal.save.mockRejectedValueOnce(new WriteResponseUnknown());await x.render().save();x.render().setProject(later);x.render();normal.project.mockResolvedValue({revision:6,project:remote});await x.render().confirmSave();await x.render().retrySave();expect(normal.save).toHaveBeenCalledTimes(1);expect(x.render().saveIntent.payload.project).toEqual(sent);expect(x.render().saveIntent.payload.confirmedProject).toEqual(remote);x.render().resolveSaveConflict();expect(x.render().project).toEqual(later);expect(x.render().revision).toBe(6);expect(x.render().dirty).toBe(true);x.unmount();
 });
 it('refuses any write if the request could not be durably preserved',async()=>{const x=await setup();vi.stubGlobal('localStorage',{getItem:()=>null,setItem:()=>{throw Error('quota');}});await x.render().save();expect(normal.save).not.toHaveBeenCalled();expect(x.render().error).toContain('quota');expect(x.render().project).toEqual(original);x.unmount();});
 it('keeps the baseline and pending request when a reader tries confirmation or conflict resolution',async()=>{
  const x=await setup(),sent=edited('sent'),later=edited('later'),remote=edited('other owner');x.render().setProject(sent);x.render();normal.save.mockRejectedValueOnce(new WriteResponseUnknown());await x.render().save();x.render().setProject(later);x.render();normal.project.mockResolvedValue({revision:6,project:remote});await x.render().confirmSave();const raw=localStorage.getItem('balloon.pending-requests/1'),reads=normal.project.mock.calls.length;releaseWriteLease();
  await x.render().confirmSave();expect(normal.project).toHaveBeenCalledTimes(reads);expect(()=>x.render().resolveSaveConflict()).not.toThrow();expect(x.render().revision).toBe(4);expect(x.render().project).toEqual(later);expect(x.render().dirty).toBe(true);expect(x.render().saveIntent.payload.project).toEqual(sent);expect(x.render().error).toContain('送信権');expect(localStorage.getItem('balloon.pending-requests/1')).toBe(raw);x.unmount();
 });
 it('does not apply a confirmed save if write ownership is lost while the GET is in flight',async()=>{
  const x=await setup(),sent=edited('sent'),later=edited('later');x.render().setProject(sent);x.render();normal.save.mockRejectedValueOnce(new WriteResponseUnknown());await x.render().save();x.render().setProject(later);x.render();const response=deferred(),raw=localStorage.getItem('balloon.pending-requests/1');normal.project.mockReturnValueOnce(response.promise);const pending=x.render().confirmSave();await flush();releaseWriteLease();response.resolve({revision:5,project:sent});await pending;
  expect(x.render().revision).toBe(4);expect(x.render().project).toEqual(later);expect(x.render().saveIntent.payload.project).toEqual(sent);expect(x.render().error).toContain('保存基準と草案は変更せず');expect(localStorage.getItem('balloon.pending-requests/1')).toBe(raw);x.unmount();
 });
 it('retains the conflict and baseline if clearing the durable request fails',async()=>{
  const x=await setup(),sent=edited('sent'),later=edited('later'),remote=edited('remote');x.render().setProject(sent);x.render();normal.save.mockRejectedValueOnce(new WriteResponseUnknown());await x.render().save();x.render().setProject(later);x.render();normal.project.mockResolvedValue({revision:6,project:remote});await x.render().confirmSave();const storage=localStorage,raw=storage.getItem('balloon.pending-requests/1');vi.stubGlobal('localStorage',{getItem:(k:string)=>storage.getItem(k),setItem:()=>{throw Error('quota after read');}});
  expect(()=>x.render().resolveSaveConflict()).not.toThrow();expect(x.render().revision).toBe(4);expect(x.render().project).toEqual(later);expect(x.render().saveIntent.payload.confirmedProject).toEqual(remote);expect(x.render().error).toContain('quota after read');expect(storage.getItem('balloon.pending-requests/1')).toBe(raw);x.unmount();
 });
});
describe('independent workspace restoration',()=>{
 it('shows the first matching fixed result when explicitly recovering an unknown POST, without another POST',async()=>{
  normal.project.mockResolvedValue({revision:4,project:{...structuredClone(original),compare_run_ids:[]}});normal.runs.mockResolvedValue({runs:[]});const x=await setup();normal.start.mockRejectedValueOnce(new WriteResponseUnknown());await x.render().start(candidate);const pending=x.render().families[0],requestId=pending.payload.rows[0].requestId,recovered={...oldRun,spec:{submitted_input:submittedRun(candidate,requestId)}};normal.runRequest.mockResolvedValue(recovered);normal.run.mockResolvedValue(recovered);await x.render().confirmFamily(pending.id);await flush();
  expect(x.render().project.compare_run_ids).toEqual(['old']);expect(x.render().results.old).toEqual(result);expect(normal.start).toHaveBeenCalledOnce();expect(normal.runRequest).toHaveBeenCalledWith(requestId);x.unmount();
 });
 it('keeps saved result and edits when weather read fails and only retries that read',async()=>{
  normal.weather.mockRejectedValueOnce(Error('source offline')).mockResolvedValueOnce({sources:[{id:'later'}]});const x=await setup();expect(x.render().results.old).toEqual(result);expect(x.render().readErrors.weather).toBe('source offline');const later=edited('retained');x.render().setProject(later);x.render();await x.render().retryRead('weather');const w=x.render();expect(w.project).toEqual(later);expect(w.results.old).toEqual(result);expect(w.sources).toEqual([{id:'later'}]);expect(w.readErrors.weather).toBeUndefined();expect(normal.project).toHaveBeenCalledTimes(1);expect(normal.runs).toHaveBeenCalledTimes(1);expect(normal.start).not.toHaveBeenCalled();x.unmount();
 });
 it('reads selected artifacts even if listing runs fails, without treating them as absent',async()=>{
  normal.runs.mockRejectedValueOnce(Error('list offline'));const x=await setup();expect(x.render().project.compare_run_ids).toEqual(['old']);expect(x.render().results.old).toEqual(result);expect(x.render().resultReads.old.state).toBe('ready');expect(x.render().readErrors.runs).toBe('list offline');expect(normal.start).not.toHaveBeenCalled();x.unmount();
 });
 it('does not overwrite a saved plan that it could not read',async()=>{normal.project.mockRejectedValueOnce(Error('plan offline'));const x=await setup();expect(x.render().readErrors.project).toBe('plan offline');await x.render().save();expect(normal.save).not.toHaveBeenCalled();expect(x.render().projectAvailable).toBe(false);x.unmount();});
});


describe('malformed pending requests are isolated from saved results',()=>{
 it('keeps the original bytes and never renders malformed family rows',async()=>{
  const raw=JSON.stringify({schema:'balloon.pending-requests/1',requests:[{id:'bad',kind:'single-family',createdAt:'2026-09-30',payload:{}}]});localStorage.setItem('balloon.pending-requests/1',raw);
  const x=await setup();expect(x.render().families).toEqual([]);expect(x.render().error).toContain('形式を読めません');expect(x.render().results.old).toEqual(result);expect(localStorage.getItem('balloon.pending-requests/1')).toBe(raw);await x.render().start(candidate);expect(normal.start).not.toHaveBeenCalled();expect(localStorage.getItem('balloon.pending-requests/1')).toBe(raw);x.unmount();
 });
});


describe('service identity and execution health',()=>{
 it('keeps reads available but prevents writing when initial identity is unavailable',async()=>{normal.health.mockRejectedValueOnce(Error('health offline'));const x=await setup();expect(x.render().results.old).toEqual(result);expect(x.render().healthError).toBe('health offline');await x.render().save();expect(normal.save).not.toHaveBeenCalled();x.unmount();});
 it('observes a broken pool without relabelling saved flight results or resubmitting',async()=>{const x=await setup();normal.health.mockResolvedValue({instance_id:'test-instance',status:'degraded',flight_execution:{available:false,restart_required:true,error:{code:'WORKER_PROCESS_BROKEN',message:'restart'},queued_policy:'preserved_without_automatic_resubmission'}});await vi.advanceTimersByTimeAsync(15000);expect(x.render().serviceHealth.flight_execution.restart_required).toBe(true);expect(x.render().results.old).toEqual(result);expect(normal.start).not.toHaveBeenCalled();expect(normal.save).not.toHaveBeenCalled();x.unmount();});
 it('does not adopt another service identity during background health observation',async()=>{const x=await setup();normal.health.mockResolvedValue({instance_id:'different-state',status:'ok',flight_execution:{available:true}});await x.render().refreshHealth();expect(x.render().healthError).toContain('接続先');expect(x.render().serviceHealth.instance_id).toBe('test-instance');expect(x.render().project).toEqual(original);x.unmount();});
});


it('persists an incomplete draft separately from a runnable flight request',async()=>{
 const x=await setup(),unfinished={...structuredClone(original),candidates:[{...candidate,weather_source_id:'',config:{}}]};x.render().setProject(unfinished);x.render();normal.save.mockRejectedValueOnce(new WriteResponseUnknown());await x.render().save();expect(normal.save).toHaveBeenCalledWith(4,unfinished);expect(x.render().saveIntent.payload.project).toEqual(unfinished);normal.project.mockResolvedValue({revision:5,project:unfinished});await x.render().confirmSave();expect(x.render().saveIntent).toBeNull();expect(x.render().project).toEqual(unfinished);x.unmount();
});
