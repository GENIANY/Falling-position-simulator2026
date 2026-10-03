import {claimWriteLease,releaseWriteLease} from './writeLease';
import {setServiceIdentity} from './serviceIdentity';
import {afterEach,beforeEach,describe,expect,it,vi} from 'vitest';
import {ApiError,writeRequest} from './api';
import {createSingleSubmissionQueue,submittedRun} from './singleSubmission';
import {recordedMutation} from './recordedMutation';
import {readSubmissions} from './submissionLedger';
const candidate=(id='A'):any=>({id,label:id,revision:1,weather_source_id:'fixed',config:{launch:{time_utc:'2026-09-30T01:17:13Z'}}});
const flush=async()=>{for(let i=0;i<30;i++)await Promise.resolve();};
const accepted=(c:any,id:string,state='running'):any=>({run_id:'run-'+id,candidate_id:c.id,state,result_available:false,spec:{submitted_input:submittedRun(c,id)}});
beforeEach(async()=>{releaseWriteLease();vi.stubGlobal('navigator',{locks:{request:(_name:any,_options:any,callback:any)=>Promise.resolve(callback({name:'test-lock'}))}});await claimWriteLease();setServiceIdentity('test-instance');const data=new Map<string,string>();vi.stubGlobal('localStorage',{getItem:(k:string)=>data.get(k)??null,setItem:(k:string,v:string)=>data.set(k,v),removeItem:(k:string)=>data.delete(k)});});
afterEach(()=>{vi.useRealTimers();vi.unstubAllGlobals();});
describe('fixed flight family and unknown acceptance',()=>{
 it('runs seven fixed candidates one at a time and rejects a duplicate family during child work',async()=>{
  const send=vi.fn(async(c,id)=>accepted(c,id)),changed=vi.fn(),q=createSingleSubmissionQueue({send,lookup:vi.fn(),observe:vi.fn(),changed,error:vi.fn()}),input=Array.from({length:7},(_,i)=>candidate('C'+i));
  await q.start(input);input[2].label='edited later';expect(send).toHaveBeenCalledTimes(1);
  for(let i=0;i<7;i++){const [c,id]=send.mock.calls[i];q.observe(accepted(c,id,'completed'));await flush();if(i<6){expect(send).toHaveBeenCalledTimes(i+2);await expect(q.start([candidate('C'+(i+1))])).rejects.toThrow('未完了');}}
  expect(send.mock.calls[2][0].label).toBe('C2');expect(q.snapshot()).toEqual([]);expect(readSubmissions()).toEqual([]);
 });
 it('restores an unknown POST and confirms the exact request without another POST',async()=>{
  const send=vi.fn().mockRejectedValue(new TypeError('response lost')),q=createSingleSubmissionQueue({send,lookup:vi.fn(),observe:vi.fn(),changed:vi.fn(),error:vi.fn()});await q.start([candidate()]);const saved=q.snapshot()[0],row=saved.payload.rows[0];q.dispose();
  const observe=vi.fn(),lookup=vi.fn().mockResolvedValue(accepted(row.candidate,row.requestId,'completed')),restored=createSingleSubmissionQueue({send,lookup,observe,changed:vi.fn(),error:vi.fn()});restored.restore();await flush();expect(send).toHaveBeenCalledOnce();await restored.confirm(saved.id);expect(lookup).toHaveBeenCalledWith(row.requestId);expect(observe).toHaveBeenCalled();expect(send).toHaveBeenCalledOnce();expect(readSubmissions()).toEqual([]);
 });
 it('uses the identical ID and body only after explicit 404 confirmation and resume',async()=>{
  const send=vi.fn().mockRejectedValueOnce(new TypeError('lost')).mockImplementation(async(c,id)=>accepted(c,id)),lookup=vi.fn().mockRejectedValue(new ApiError('not observed',404)),q=createSingleSubmissionQueue({send,lookup,observe:vi.fn(),changed:vi.fn(),error:vi.fn()});await q.start([candidate()]);const f=q.snapshot()[0];await expect(q.resume(f.id)).rejects.toThrow('先に受付');await q.confirm(f.id);expect(send).toHaveBeenCalledOnce();await q.resume(f.id);expect(send).toHaveBeenCalledTimes(2);expect(send.mock.calls[1]).toEqual(send.mock.calls[0]);
 });
 it('does not replay after restore, and does not continue untouched rows during confirmation',async()=>{
  const send=vi.fn(async(c,id)=>accepted(c,id)),q=createSingleSubmissionQueue({send,lookup:vi.fn(),observe:vi.fn(),changed:vi.fn(),error:vi.fn()});await q.start([candidate('A'),candidate('B')]);const first=q.snapshot()[0],row=first.payload.rows[0];q.dispose();const restored=createSingleSubmissionQueue({send,lookup:vi.fn().mockResolvedValue(accepted(row.candidate,row.requestId,'completed')),observe:vi.fn(),changed:vi.fn(),error:vi.fn()});restored.restore();await restored.confirm(first.id);expect(send).toHaveBeenCalledOnce();await restored.resume(first.id);expect(send).toHaveBeenCalledTimes(2);
 });
 it('refuses a lookup for another body and fails before sending when durable storage fails',async()=>{
  const send=vi.fn().mockRejectedValue(new TypeError('lost')),error=vi.fn(),q=createSingleSubmissionQueue({send,lookup:vi.fn().mockResolvedValue(accepted(candidate('other'),'wrong')),observe:vi.fn(),changed:vi.fn(),error});await q.start([candidate()]);await q.confirm(q.snapshot()[0].id);expect(q.snapshot()[0].payload.rows[0].notFound).toBe(false);expect(error.mock.calls.at(-1)![0].message).toContain('一致しません');
  vi.stubGlobal('localStorage',{getItem:()=>null,setItem:()=>{throw Error('quota');}});const send2=vi.fn(),fresh=createSingleSubmissionQueue({send:send2,lookup:vi.fn(),observe:vi.fn(),changed:vi.fn(),error:vi.fn()});await expect(fresh.start([candidate()])).rejects.toThrow('quota');expect(send2).not.toHaveBeenCalled();
 });
});
describe('bounded recorded mutation',()=>{
 it('replays an ambiguous ensemble start with the original ID and body only after an explicit call',async()=>{
  const fetch=vi.fn().mockResolvedValueOnce({ok:false,status:503,json:async()=>({detail:'accepted but reply lost'})}).mockResolvedValueOnce({ok:true,status:202,json:async()=>({ensemble_id:'same-job'})});vi.stubGlobal('fetch',fetch);const body={client_request_id:'fixed-id',plan_id:'p',plan_hash:'h'};
  await expect(recordedMutation('ensemble-write','/ensembles',body)).rejects.toThrow();await flush();expect(fetch).toHaveBeenCalledOnce();expect(readSubmissions()[0].payload.body).toEqual(body);
  await expect(recordedMutation('ensemble-write','/ensembles',{...body,plan_hash:'changed'})).rejects.toThrow('異なる要求');expect(fetch).toHaveBeenCalledOnce();
  expect(await recordedMutation('ensemble-write','/ensembles',body)).toEqual({ensemble_id:'same-job'});expect(fetch.mock.calls[1][1].body).toBe(fetch.mock.calls[0][1].body);expect(readSubmissions()).toEqual([]);
 });
 it('settles a stuck response body once, retains the exact request and ignores a late success',async()=>{
  vi.useFakeTimers();let finish!:(v:any)=>void;const body=new Promise(resolve=>{finish=resolve;}),fetch=vi.fn().mockResolvedValue({ok:true,status:202,json:()=>body});vi.stubGlobal('fetch',fetch);
  const p=recordedMutation('ensemble-write','/ensembles',{client_request_id:'same',plan_id:'p',plan_hash:'h'}),assertion=expect(p).rejects.toThrow('受付応答');await vi.advanceTimersByTimeAsync(60000);await assertion;expect(fetch).toHaveBeenCalledOnce();expect(readSubmissions()[0].payload.body.plan_hash).toBe('h');finish({ensemble_id:'e'});await flush();expect(readSubmissions()).toHaveLength(1);expect(fetch).toHaveBeenCalledOnce();
 });
 it('a definitive rejection clears only its intent; a hanging PUT never resends',async()=>{
  vi.stubGlobal('fetch',vi.fn().mockResolvedValue({ok:false,status:422,json:async()=>({detail:'invalid'})}));await expect(recordedMutation('ensemble-write','/ensembles',{client_request_id:'rejected'})).rejects.toThrow('invalid');expect(readSubmissions()).toEqual([]);
  vi.useFakeTimers();const fetch=vi.fn(()=>new Promise(()=>{}));vi.stubGlobal('fetch',fetch);const p=writeRequest('/project',{method:'PUT',body:'{}'}),assertion=expect(p).rejects.toThrow('受付応答');await vi.advanceTimersByTimeAsync(60000);await assertion;expect(fetch).toHaveBeenCalledOnce();
 });
});
