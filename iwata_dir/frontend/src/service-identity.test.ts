import {claimWriteLease,releaseWriteLease} from './writeLease';
import {afterEach,beforeEach,expect,it,vi} from 'vitest';
import {setServiceIdentity,serviceIdentity} from './serviceIdentity';
import {putSubmission,snapshotSubmissions,removeSubmission} from './submissionLedger';
import {recordedMutation} from './recordedMutation';
import {request,writeRequest} from './api';
beforeEach(async()=>{releaseWriteLease();vi.stubGlobal('navigator',{locks:{request:(_name:any,_options:any,callback:any)=>Promise.resolve(callback({name:'test-lock'}))}});await claimWriteLease();setServiceIdentity('instance-A');const data=new Map<string,string>();vi.stubGlobal('localStorage',{getItem:(k:string)=>data.get(k)??null,setItem:(k:string,v:string)=>data.set(k,v)});});
afterEach(()=>{setServiceIdentity(null);vi.unstubAllGlobals();});
const entry=()=>({id:'same',kind:'weather-acquisition',createdAt:'2026-09-30T00:00:00Z',payload:{plan_id:'p',client_request_id:'same'}});
it('quarantines requests from another state and does not silently adopt legacy unbound requests',()=>{
 const first=entry();putSubmission(first);const raw=localStorage.getItem('balloon.pending-requests/1')!;setServiceIdentity('instance-B');expect(snapshotSubmissions().requests).toEqual([]);expect(snapshotSubmissions().notice).toContain('1件');expect(()=>putSubmission(first)).toThrow('保存先が異なり');putSubmission(entry());removeSubmission('same');setServiceIdentity('instance-A');expect(snapshotSubmissions().requests).toEqual([first]);expect(localStorage.getItem('balloon.pending-requests/1')).toBe(raw);
 const legacy=entry();localStorage.setItem('balloon.pending-requests/1',JSON.stringify({schema:'balloon.pending-requests/1',requests:[legacy]}));expect(snapshotSubmissions().requests).toEqual([]);expect(snapshotSubmissions().notice).toContain('旧未識別');expect((legacy as any).instance_id).toBeUndefined();
});
it('refuses writes before health identity and leaves read-only access available',async()=>{
 setServiceIdentity(null);const fetch=vi.fn().mockResolvedValue({ok:true,json:async()=>({result:'saved'})});vi.stubGlobal('fetch',fetch);expect(()=>writeRequest('/runs',{method:'POST',body:'{}'})).toThrow('保存先の識別');expect(fetch).not.toHaveBeenCalled();expect(await request('/runs/old')).toEqual({result:'saved'});expect(fetch.mock.calls[0][1].headers['X-Balloon-Instance-Id']).toBeUndefined();
});
it('pins GET and POST to the known state and retains a request rejected by a different state',async()=>{
 const fetch=vi.fn().mockResolvedValue({ok:false,status:409,json:async()=>({error:{code:'INSTANCE_MISMATCH',message:'different state'}})});vi.stubGlobal('fetch',fetch);await expect(recordedMutation('ensemble-write','/ensembles',{client_request_id:'same',plan_id:'p'})).rejects.toThrow('INSTANCE_MISMATCH');expect(snapshotSubmissions('ensemble-write').requests).toHaveLength(1);expect(fetch.mock.calls[0][1].headers['X-Balloon-Instance-Id']).toBe('instance-A');await expect(request('/run-requests?client_request_id=same')).rejects.toThrow('INSTANCE_MISMATCH');expect(fetch.mock.calls[1][1].headers['X-Balloon-Instance-Id']).toBe('instance-A');await expect(request('/health')).rejects.toThrow();expect(fetch.mock.calls[2][1].headers['X-Balloon-Instance-Id']).toBeUndefined();expect(serviceIdentity()).toBe('instance-A');
});
