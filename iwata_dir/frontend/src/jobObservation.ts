/** Read-only monitoring shared by jobs whose last confirmed state must survive a lost response. */
export type JobObservation={checking:boolean;unavailable:boolean;lastConfirmedAt:string|null;failures:number;nextRetryMs:number|null;message:string|null};
export function createJobObserver<T>(options:{read:(id:string,signal:AbortSignal)=>Promise<T>;accept:(id:string,value:T)=>void;active:(id:string)=>boolean;observe:(id:string,state:JobObservation)=>void;isCurrent:()=>boolean}){
 type Entry={timer:ReturnType<typeof setTimeout>|null;flight:Promise<void>|null;controller:AbortController|null;state:JobObservation};
 const entries=new Map<string,Entry>();let disposed=false;
 const current=()=>!disposed&&options.isCurrent();
 function entry(id:string){let e=entries.get(id);if(!e){e={timer:null,flight:null,controller:null,state:{checking:false,unavailable:false,lastConfirmedAt:null,failures:0,nextRetryMs:null,message:null}};entries.set(id,e);}return e;}
 function clear(e:Entry){if(e.timer!==null)clearTimeout(e.timer);e.timer=null;}
 function emit(id:string,e:Entry){if(current())options.observe(id,{...e.state});}
 function schedule(id:string,e:Entry){clear(e);e.state.nextRetryMs=null;if(!current()||!options.active(id))return;const ms=e.state.failures?Math.min(15000,900*2**Math.min(e.state.failures,5)):900;e.state.nextRetryMs=ms;e.timer=setTimeout(()=>{e.timer=null;void refresh(id);},ms);}
 function refresh(id:string):Promise<void>{if(!current())return Promise.resolve();const e=entry(id);if(e.flight)return e.flight;clear(e);e.state={...e.state,checking:true,nextRetryMs:null};emit(id,e);const controller=new AbortController();e.controller=controller;
  const work=Promise.resolve().then(()=>current()?options.read(id,controller.signal):undefined).then(value=>{if(!current())return;options.accept(id,value as T);e.state={checking:false,unavailable:false,lastConfirmedAt:new Date().toISOString(),failures:0,nextRetryMs:null,message:null};}).catch(error=>{if(current())e.state={...e.state,unavailable:true,failures:e.state.failures+1,message:error instanceof Error?error.message:String(error)};}).finally(()=>{e.flight=null;e.controller=null;if(!current())return;e.state.checking=false;schedule(id,e);emit(id,e);});e.flight=work;return work;
 }
 function track(id:string){if(!current())return;const e=entry(id);if(!e.flight&&e.timer===null){schedule(id,e);emit(id,e);}}
 function dispose(){disposed=true;for(const e of entries.values()){clear(e);e.controller?.abort();}entries.clear();}
 return {refresh,track,dispose};
}
