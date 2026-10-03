import {afterEach,expect,it,vi} from 'vitest';
const flush=async()=>{for(let i=0;i<12;i++)await Promise.resolve();};
afterEach(()=>{vi.useRealTimers();vi.unstubAllGlobals();});
it('allows one writer across tabs and explicitly transfers ownership without changing reads',async()=>{
 const held=new Set<string>();vi.stubGlobal('navigator',{locks:{request:(name:string,_options:unknown,callback:any)=>{if(held.has(name))return Promise.resolve(callback(null));held.add(name);return Promise.resolve(callback({name})).finally(()=>held.delete(name));}}});
 vi.resetModules();const a=await import('./writeLease');vi.resetModules();const b=await import('./writeLease');await a.claimWriteLease();await b.claimWriteLease();expect(a.ownsWriteLease()).toBe(true);expect(b.ownsWriteLease()).toBe(false);expect(()=>b.requireWriteLease()).toThrow('送信権');a.releaseWriteLease();await flush();expect(b.ownsWriteLease()).toBe(false);await b.claimWriteLease();expect(b.ownsWriteLease()).toBe(true);b.releaseWriteLease();await flush();
});
it('does not seize ownership from a late grant after unmount',async()=>{
 let callback!:(lock:any)=>Promise<void>;vi.stubGlobal('navigator',{locks:{request:(_name:string,_options:unknown,fn:any)=>{callback=fn;return new Promise(()=>{});}}});vi.resetModules();const a=await import('./writeLease'),pending=a.claimWriteLease();a.releaseWriteLease();await callback({name:'late'});await pending;expect(a.ownsWriteLease()).toBe(false);
});
it('does not write a ledger or send POST from a reader tab',async()=>{
 vi.stubGlobal('navigator',{locks:{request:(_name:string,_options:unknown,callback:any)=>Promise.resolve(callback(null))}});const fetch=vi.fn(),setItem=vi.fn();vi.stubGlobal('fetch',fetch);vi.stubGlobal('localStorage',{getItem:()=>null,setItem});vi.resetModules();const lease=await import('./writeLease'),identity=await import('./serviceIdentity'),ledger=await import('./submissionLedger'),api=await import('./api');identity.setServiceIdentity('same');await lease.claimWriteLease();expect(()=>ledger.putSubmission({id:'p',kind:'weather-acquisition',createdAt:'today',payload:{plan_id:'p',client_request_id:'p'}})).toThrow('送信権');expect(()=>api.writeRequest('/runs',{method:'POST',body:'{}'})).toThrow('送信権');expect(setItem).not.toHaveBeenCalled();expect(fetch).not.toHaveBeenCalled();
});

async function tabs(count=2){
 const held=new Set<string>(),messages:any[]=[],channels=new Set<any>();
 vi.stubGlobal('window',{});
 vi.stubGlobal('BroadcastChannel',class {
  onmessage:((event:any)=>void)|null=null;listeners=new Set<(event:any)=>void>();
  constructor(public name:string){channels.add(this);}
  postMessage(data:any){messages.push(data);for(const channel of channels)if(channel!==this&&channel.name===this.name)queueMicrotask(()=>{if(!channels.has(channel))return;channel.onmessage?.({data});for(const fn of channel.listeners)fn({data});});}
  addEventListener(_type:string,fn:any){this.listeners.add(fn);}
  removeEventListener(_type:string,fn:any){this.listeners.delete(fn);}
  close(){channels.delete(this);}
 });
 vi.stubGlobal('navigator',{locks:{request:(name:string,options:any,callback:any)=>{expect(options.steal).toBeUndefined();if(held.has(name))return Promise.resolve(callback(null));held.add(name);return Promise.resolve(callback({name})).finally(()=>held.delete(name));}}});
 const modules:Array<typeof import('./writeLease')>=[];for(let i=0;i<count;i++){vi.resetModules();modules.push(await import('./writeLease'));}
 return {modules,messages,held,close:async()=>{for(const module of modules)module.releaseWriteLease();await flush();}};
}
it('hands off explicitly, reports the new owner, and never automatically takes it back',async()=>{
 const h=await tabs(),[a,b]=h.modules;await a.claimWriteLease();await b.claimWriteLease();expect(h.messages).toHaveLength(0);
 await b.claimWriteLease(true);expect(a.ownsWriteLease()).toBe(false);expect(b.ownsWriteLease()).toBe(true);expect(a.writeLeaseState().message).toContain('引き継ぎ');
 await a.claimWriteLease();expect(a.ownsWriteLease()).toBe(false);await h.close();
});
it('refuses handoff until nested request and ledger operations both finish',async()=>{
 const h=await tabs(),[a,b]=h.modules;await a.claimWriteLease();await b.claimWriteLease();const outer=a.beginWriteOperation(),inner=a.beginWriteOperation();
 inner();inner();await b.claimWriteLease(true);expect(a.ownsWriteLease()).toBe(true);expect(b.writeLeaseState().message).toContain('処理中');
 outer();await b.claimWriteLease(true);expect(b.ownsWriteLease()).toBe(true);await h.close();
});
it('keeps the physical lock through unmount cleanup so old continuations cannot write after reacquisition',async()=>{
 const h=await tabs(),[a,b]=h.modules;await a.claimWriteLease();const done=a.beginWriteOperation();a.releaseWriteLease();
 await b.claimWriteLease();expect(b.ownsWriteLease()).toBe(false);expect(()=>a.requireWriteLease()).toThrow();done();await flush();await b.claimWriteLease();expect(b.ownsWriteLease()).toBe(true);await h.close();
});
it('ends an unresponsive legacy handoff with an actionable message, without stealing',async()=>{
 vi.useFakeTimers();const h=await tabs(),[a,b]=h.modules;await a.claimWriteLease();a.releaseWriteLease();await flush();
 h.held.add('balloon.request-ledger-writer/1');await b.claimWriteLease();const work=b.claimWriteLease(true);await flush();await vi.advanceTimersByTimeAsync(8001);await work;
 expect(b.ownsWriteLease()).toBe(false);expect(b.writeLeaseState().message).toContain('8秒');expect(vi.getTimerCount()).toBe(0);await h.close();
});
it('arbitrates simultaneous explicit requests with exactly one real lock owner',async()=>{
 const h=await tabs(3),[a,b,c]=h.modules;await a.claimWriteLease();await b.claimWriteLease();await c.claimWriteLease();
 vi.useFakeTimers();const work=Promise.all([b.claimWriteLease(true),c.claimWriteLease(true)]);await flush();await vi.advanceTimersByTimeAsync(8100);await work;
 expect(h.modules.filter(tab=>tab.ownsWriteLease())).toHaveLength(1);expect(a.ownsWriteLease()).toBe(false);await h.close();
});
