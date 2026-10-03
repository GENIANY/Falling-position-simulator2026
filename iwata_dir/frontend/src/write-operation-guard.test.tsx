import {afterEach,beforeEach,describe,expect,it,vi} from 'vitest';
const {lease,net,h}=vi.hoisted(()=>({
 lease:{owned:true,active:0,listeners:new Set<(value:any)=>void>()},h:{current:null as any},
 net:{write:vi.fn(),analysis:vi.fn(),case:vi.fn(),retry:vi.fn(),acquire:vi.fn()},
}));
vi.mock('./writeLease',()=>({
 ownsWriteLease:()=>lease.owned,
 requireWriteLease:()=>{if(!lease.owned)throw Error('送信権がありません');},
 beginWriteOperation:()=>{if(!lease.owned)throw Error('送信権がありません');lease.active++;let done=false;return()=>{if(!done){done=true;lease.active--;}};},
 observeWriteLease:(fn:any)=>{lease.listeners.add(fn);return()=>lease.listeners.delete(fn);},
}));
vi.mock('react',()=>({useRef:(v:any)=>h.current.ref(v),useState:(v:any)=>h.current.state(v),useEffect:(f:any,d:any[])=>h.current.effect(f,d)}));
vi.mock('./api',async()=>{const actual=await vi.importActual<any>('./api');return {...actual,writeRequest:net.write,api:{...actual.api,inventories:async()=>({inventories:[]}),acquisitions:async()=>({acquisitions:[]}),weatherStatus:async()=>({}),acquireWeather:net.acquire}};});
vi.mock('./ensembleApi',()=>({ensembleApi:{jobs:async()=>({ensembles:[]}),case:net.case,analysis:net.analysis,retry:net.retry}}));
import {setServiceIdentity} from './serviceIdentity';
import {readSubmissions,putSubmission} from './submissionLedger';
import {recordedMutation} from './recordedMutation';
import {createSingleSubmissionQueue,submittedRun} from './singleSubmission';
import {useEnsembleWorkspace} from './useEnsembleWorkspace';
import {selectionKey} from './ensembleDomain';
import {WeatherPreparation} from './WeatherPreparation';
import {HistoricalPreparation} from './HistoricalPreparation';

const flush=async()=>{for(let i=0;i<20;i++)await Promise.resolve();};
function deferred(){let resolve!:(value?:any)=>void;const promise=new Promise<any>(yes=>{resolve=yes;});return {promise,resolve};}
function ownership(owned:boolean){lease.owned=owned;for(const fn of lease.listeners)fn({state:owned?'owner':'reader'});}
function harness(fn:()=>any){
 let cursor=0;const slots:any[]=[],effects:any[]=[],cleanups:any[]=[];
 const hooks={ref:(value:any)=>{const i=cursor++;return slots[i]??(slots[i]={current:value});},state:(value:any)=>{const i=cursor++;if(!(i in slots))slots[i]=typeof value==='function'?value():value;return [slots[i],(next:any)=>{slots[i]=typeof next==='function'?next(slots[i]):next;}];},effect:(effect:any,deps:any[])=>{const i=cursor++;if(!slots[i]||deps.some((v,j)=>!Object.is(v,slots[i][j]))){slots[i]=deps;effects.push(()=>{cleanups[i]?.();cleanups[i]=effect();});}}};
 return {render:()=>{cursor=0;h.current=hooks;const value=fn();effects.splice(0).forEach(run=>run());return value;},unmount:()=>cleanups.forEach(fn=>fn?.())};
}
const treeNodes=(node:any):any[]=>Array.isArray(node)?node.flatMap(treeNodes):node&&typeof node==='object'?[node,...treeNodes(node.props?.children)]:[];
const treeText=(node:any):string=>Array.isArray(node)?node.map(treeText).join(''):node&&typeof node==='object'?treeText(node.props?.children):node==null||typeof node==='boolean'?'':String(node);
function click(tree:any,label:string){const button=treeNodes(tree).find(n=>n.type==='button'&&treeText(n)===label);expect(button,label).toBeTruthy();return button.props.onClick();}
const candidate:any={id:'A',label:'A',revision:1,weather_source_id:'w',config:{launch:{time_utc:'2026-09-30T01:00:00Z',latitude_deg:34,longitude_deg:135},ascent:{mode:'constant_speed',speed_m_s:5},burst:{mode:'altitude',altitude_m:30000},descent:{mode:'rated_speed',reference_speed_m_s:5}}};
const accepted=(requestId:string)=>({run_id:'R',state:'completed',spec:{submitted_input:submittedRun(candidate,requestId)}}) as any;
let storage:Map<string,string>,writes:number[];
beforeEach(()=>{lease.owned=true;lease.active=0;lease.listeners.clear();Object.values(net).forEach(mock=>mock.mockReset());storage=new Map();writes=[];vi.stubGlobal('localStorage',{getItem:(key:string)=>storage.get(key)??null,setItem:(key:string,value:string)=>{writes.push(lease.active);storage.set(key,value);}});setServiceIdentity('test-instance');});
afterEach(()=>{expect(lease.active).toBe(0);vi.unstubAllGlobals();});

describe('write operations cover the complete asynchronous ledger transaction',()=>{
 it('keeps the recorded request protected until the response and its ledger removal finish',async()=>{
  const response=deferred();net.write.mockReturnValue(response.promise);const work=recordedMutation('ensemble-write','/ensembles',{client_request_id:'request'});
  expect(lease.active).toBe(1);expect(readSubmissions()).toHaveLength(1);response.resolve({ensemble_id:'E'});await work;
  expect(readSubmissions()).toHaveLength(0);expect(writes.every(count=>count>0)).toBe(true);expect(lease.active).toBe(0);
 });
 it('releases after a pre-send storage failure and retains an unknown request after transport failure',async()=>{
  const set=vi.spyOn(localStorage,'setItem').mockImplementationOnce(()=>{throw Error('quota');});
  await expect(recordedMutation('ensemble-write','/ensembles',{client_request_id:'quota'})).rejects.toThrow('quota');expect(lease.active).toBe(0);expect(net.write).not.toHaveBeenCalled();set.mockRestore();
  net.write.mockRejectedValue(new Error('unknown'));await expect(recordedMutation('ensemble-write','/ensembles',{client_request_id:'unknown'})).rejects.toThrow('unknown');expect(readSubmissions()[0].payload.body.client_request_id).toBe('unknown');
 });
 it('keeps a single-family send protected through observation and never advances a reader queue',async()=>{
  const observation=deferred(),send=vi.fn(async(_c,id)=>accepted(id)),q=createSingleSubmissionQueue({send,lookup:vi.fn(),observe:()=>observation.promise,changed:vi.fn(),error:vi.fn()});
  const work=q.start([candidate,{...candidate,id:'B'}]);await flush();expect(lease.active).toBe(1);observation.resolve();await work;
  ownership(false);q.observe(accepted(q.snapshot()[0].payload.rows[0].requestId));await flush();expect(send).toHaveBeenCalledOnce();expect(writes.slice(1).every(count=>count>0)).toBe(true);q.dispose();
 });
 it('keeps confirmation protected through lookup, observation and final ledger cleanup',async()=>{
  const lookup=deferred(),observation=deferred(),q=createSingleSubmissionQueue({send:vi.fn().mockRejectedValue(new Error('unknown')),lookup:()=>lookup.promise,observe:()=>observation.promise,changed:vi.fn(),error:vi.fn()});
  await q.start([candidate]);const family=q.snapshot()[0],work=q.confirm(family.id);expect(lease.active).toBe(1);
  lookup.resolve(accepted(family.payload.rows[0].requestId));await flush();expect(lease.active).toBe(1);observation.resolve();await work;expect(readSubmissions()).toHaveLength(0);q.dispose();
 });
 it('reloads an intent replaced by another owner and does not POST an unknown analysis again',async()=>{
  const project:any={schema:'balloon.project/1',candidates:[],compare_run_ids:[]},x=harness(()=>useEnsembleWorkspace(project,[],0,true,vi.fn(),{claim:()=>0,current:()=>0}));
  net.analysis.mockRejectedValue(new Error('before transport'));await expect(x.render().analysis('S','A',['T'],null)).rejects.toThrow('before transport');
  const key='analysis:'+selectionKey('S','A',['T'],null);ownership(false);
  storage.set('balloon.pending-requests/1',JSON.stringify({schema:'balloon.pending-requests/1',requests:[
   {id:'ensemble-intent:other',kind:'ensemble-intent',createdAt:'now',instance_id:'test-instance',payload:{key,requestId:'other'}},
   {id:'ensemble-write:other',kind:'ensemble-write',createdAt:'now',instance_id:'test-instance',payload:{path:'/ensemble-analyses',body:{client_request_id:'other'}}},
  ]}));ownership(true);expect(x.render().pendingMutations.map((r:any)=>r.id)).toEqual(['ensemble-write:other']);
  await expect(x.render().analysis('S','A',['T'],null)).rejects.toThrow('受付が未確認');expect(net.analysis).toHaveBeenCalledOnce();expect(readSubmissions()).toHaveLength(2);x.unmount();
 });
 it('covers recovery until both ensemble-write and ensemble-intent entries are removed',async()=>{
  putSubmission({id:'ensemble-write:recover',kind:'ensemble-write',createdAt:'now',payload:{path:'/ensembles',body:{client_request_id:'recover'}}});putSubmission({id:'ensemble-intent:recover',kind:'ensemble-intent',createdAt:'now',payload:{key:'start:P',requestId:'recover'}});writes=[];
  const response=deferred();net.write.mockReturnValue(response.promise);const project:any={schema:'balloon.project/1',candidates:[],compare_run_ids:[]},x=harness(()=>useEnsembleWorkspace(project,[],0,true,vi.fn(),{claim:()=>0,current:()=>0}));
  const work=x.render().recoverMutation('ensemble-write:recover');expect(lease.active).toBe(2);response.resolve({});await work;expect(readSubmissions()).toHaveLength(0);expect(writes.every(count=>count>0)).toBe(true);x.unmount();
 });
 it('holds the retry scope while reading its fixed cases and releases after disposal without POST',async()=>{
  const response=deferred();net.case.mockReturnValue(response.promise);const project:any={schema:'balloon.project/1',candidates:[],compare_run_ids:[]},x=harness(()=>useEnsembleWorkspace(project,[],0,true,vi.fn(),{claim:()=>0,current:()=>0}));
  const work=x.render().retry({ensemble_id:'E',latest_snapshot_id:'S',cases:[{case_id:'A'}]} as any);expect(lease.active).toBe(1);x.unmount();response.resolve({snapshot_id:'S',case_id:'A',trials:[]});await work;expect(net.retry).not.toHaveBeenCalled();
 });
 it('keeps weather acquisition acceptance and outbox cleanup within the operation',async()=>{
  putSubmission({id:'weather',kind:'weather-acquisition',createdAt:'now',payload:{plan_id:'P',client_request_id:'weather'}});writes=[];
  const response=deferred();net.acquire.mockReturnValue(response.promise);const x=harness(()=>WeatherPreparation({candidates:[candidate],sources:[],saved:{},onState:vi.fn(),refreshSources:async()=>[],apply:vi.fn(),add:vi.fn()} as any));
  x.render();await flush();const work=click(x.render(),'この同じ要求IDで受付を確認');expect(lease.active).toBe(1);
  response.resolve({acquisition_id:'W',plan_id:'P',state:'failed',attempt:1});await work;await flush();expect(readSubmissions()).toHaveLength(0);expect(writes.every(count=>count>0)).toBe(true);x.unmount();
 });
 it.each([false,true])('keeps historical acceptance protected through completion or disposal (dispose=%s)',async(dispose)=>{
  putSubmission({id:'historical',kind:'historical-request',createdAt:'now',payload:{candidate_id:'A',action:'submit',path:'/ensembles',body:{client_request_id:'historical'}}});writes=[];
  const response=deferred();net.write.mockReturnValue(response.promise);const x=harness(()=>HistoricalPreparation({candidate,sources:[],onState:vi.fn(),ensemble:{jobs:{},acceptJob:vi.fn()}} as any));
  click(x.render(),'同一要求で確認・再送');expect(lease.active).toBe(1);if(dispose)x.unmount();response.resolve({ensemble_id:'E'});await flush();expect(readSubmissions()).toHaveLength(dispose?1:0);expect(writes.every(count=>count>0)).toBe(true);expect(lease.active).toBe(0);if(!dispose)x.unmount();
 });
});
