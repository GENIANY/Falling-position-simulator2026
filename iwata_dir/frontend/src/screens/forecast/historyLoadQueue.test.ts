import {describe,it,expect,vi} from 'vitest';
import {historyLoadContext,createHistoryLoadQueue} from './historyLoadQueue';
import type {HistoryLoadContext,HistoryTask} from './historyLoadQueue';
import type {CaseResult} from '../../ensembleDomain';

function collection():CaseResult{return {snapshot_id:'S',case_id:'A',trials:[{trial_id:'T0',result_available:true,state:'landed'},{trial_id:'T1',result_available:true,state:'stopped'},{trial_id:'T2',result_available:false,state:'cancelled'}]} as CaseResult;}
function deferred(){let resolve!:(value?:unknown)=>void,reject!:(error:unknown)=>void;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};}
async function flush(){for(let i=0;i<12;i++)await Promise.resolve();}
function context(key:string,count=8,snapshotId=key):HistoryLoadContext{return {key,tasks:Array.from({length:count},(_,i)=>({snapshotId,trialId:'T'+i}))};}

describe('raw history demand is independent of aggregate availability',()=>{
 it('loads selected available records without an analysis and preserves the trial ledger',()=>{
  const value=collection(),before=structuredClone(value),input={enabled:true,collection:value,selectedIds:['T0','T1','T2'],loadedIds:[],bindingKey:'result1'};
  expect(historyLoadContext(input)?.tasks.map(t=>t.trialId)).toEqual(['T0','T1']);expect(value).toEqual(before);
 });
 it('accepts a partial or reordered selection, excludes loaded/unavailable records and rejects invalid IDs',()=>{
  const input={enabled:true,collection:collection(),selectedIds:['T1','T0'],loadedIds:['T0'],bindingKey:'result1'};
  expect(historyLoadContext(input)?.tasks.map(t=>t.trialId)).toEqual(['T1']);
  expect(historyLoadContext({...input,selectedIds:['T1']})?.tasks.map(t=>t.trialId)).toEqual(['T1']);
  expect(historyLoadContext({...input,selectedIds:['T2']})?.tasks).toEqual([]);
  for(const selectedIds of [['T1','T1'],['UNKNOWN']])expect(historyLoadContext({...input,selectedIds})).toBeNull();
  expect(historyLoadContext({...input,enabled:false})).toBeNull();
  expect(historyLoadContext(input)?.key).toBe(historyLoadContext({...input,selectedIds:['T0','T1']})?.key);
  expect(historyLoadContext(input)?.key).not.toBe(historyLoadContext({...input,bindingKey:'result2'})?.key);
 });
});

describe('raw history queue follows current screen demand',()=>{
 it('sends no read until a selected snapshot context is ready and deduplicates refreshes at four concurrent reads',async()=>{
  let current:HistoryLoadContext|null=null,active=0,peak=0;const flights:ReturnType<typeof deferred>[]=[],read=vi.fn(()=>{active++;peak=Math.max(peak,active);const d=deferred();flights.push(d);return d.promise.finally(()=>active--);});
  const queue=createHistoryLoadQueue({context:()=>current,read,failed:vi.fn()});queue.sync();await flush();expect(read).not.toHaveBeenCalled();current=context('S');queue.sync();queue.sync();await flush();expect(read).toHaveBeenCalledTimes(4);expect(peak).toBe(4);
  flights[0].resolve();await flush();expect(read).toHaveBeenCalledTimes(5);queue.sync();await flush();expect(read).toHaveBeenCalledTimes(5);queue.dispose();flights.forEach(x=>x.resolve());await flush();expect(read).toHaveBeenCalledTimes(5);
 });
 it('drops unsent old-selection work and shares the same four slots with the next selection',async()=>{
  let current:HistoryLoadContext|null=context('old'),active=0,peak=0;const flights:{task:HistoryTask;d:ReturnType<typeof deferred>}[]=[],read=vi.fn((task:HistoryTask)=>{active++;peak=Math.max(peak,active);const d=deferred();flights.push({task,d});return d.promise.finally(()=>active--);});
  const queue=createHistoryLoadQueue({context:()=>current,read,failed:vi.fn()});queue.sync();await flush();current=context('new',2);queue.sync();await flush();expect(read).toHaveBeenCalledTimes(4);
  flights[0].d.resolve();await flush();expect(flights.at(-1)?.task.snapshotId).toBe('new');expect(read).toHaveBeenCalledTimes(5);flights[1].d.resolve();await flush();expect(read).toHaveBeenCalledTimes(6);expect(peak).toBe(4);
  expect(flights.filter(x=>x.task.snapshotId==='old').map(x=>x.task.trialId)).toEqual(['T0','T1','T2','T3']);queue.dispose();flights.forEach(x=>x.d.resolve());await flush();
 });
 it('rechecks context before a scheduled read and after each response even without another sync',async()=>{
  let current:HistoryLoadContext|null=context('A');const read=vi.fn(async()=>{}),queue=createHistoryLoadQueue({context:()=>current,read,failed:vi.fn()});queue.sync();current=null;await flush();expect(read).not.toHaveBeenCalled();
  current=context('A',6);const pending=deferred();read.mockImplementation(()=>pending.promise as Promise<void>);queue.sync();await flush();expect(read).toHaveBeenCalledTimes(4);current=null;pending.resolve();await flush();expect(read).toHaveBeenCalledTimes(4);queue.dispose();
 });
 it('does not reload successful histories and makes a failed read available to explicit retry',async()=>{
  const current=context('S',2);let recover=false;const failed=vi.fn(),read=vi.fn(async(task:HistoryTask)=>{if(task.trialId==='T1'&&!recover)throw Error('network failure');});
  const queue=createHistoryLoadQueue({context:()=>current,read,failed});queue.sync();await flush();expect(read).toHaveBeenCalledTimes(2);expect(failed).toHaveBeenCalledTimes(1);expect(queue.status()).toEqual({pending:0,failures:[{task:{snapshotId:'S',trialId:'T1'},message:'network failure'}]});queue.sync();await flush();expect(read).toHaveBeenCalledTimes(2);
  recover=true;queue.retry();await flush();expect(read).toHaveBeenCalledTimes(3);expect(read.mock.calls[2][0].trialId).toBe('T1');expect(queue.status()).toEqual({pending:0,failures:[]});queue.retry();await flush();expect(read).toHaveBeenCalledTimes(3);queue.dispose();
 });
 it('keeps late errors from an old selection out of the current screen, without blocking a later explicit retry',async()=>{
  let current:HistoryLoadContext|null=context('old',1);const pending=deferred(),failed=vi.fn(),read=vi.fn(()=>pending.promise);const queue=createHistoryLoadQueue({context:()=>current,read,failed});queue.sync();await flush();current=null;pending.reject(Error('old read error'));await flush();expect(failed).not.toHaveBeenCalled();
  current=context('old',1);queue.sync();await flush();expect(read).toHaveBeenCalledTimes(1);read.mockImplementation(async()=>{});queue.retry();await flush();expect(read).toHaveBeenCalledTimes(2);queue.dispose();
 });
 it('distinguishes immutable snapshot/trial tuples and disposal never starts a replacement read',async()=>{
  let current:HistoryLoadContext|null={key:'one',tasks:[{snapshotId:'ab',trialId:'c'},{snapshotId:'a',trialId:'bc'}]};const read=vi.fn(async()=>{}),failed=vi.fn(),queue=createHistoryLoadQueue({context:()=>current,read,failed});queue.sync();await flush();expect(read).toHaveBeenCalledTimes(2);
  current=context('next');queue.sync();queue.dispose();await flush();expect(read).toHaveBeenCalledTimes(2);queue.retry();queue.sync();await flush();expect(read).toHaveBeenCalledTimes(2);expect(failed).not.toHaveBeenCalled();
 });
});
