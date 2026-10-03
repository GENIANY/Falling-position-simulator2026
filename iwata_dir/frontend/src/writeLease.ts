/** One tab owns ledger writes. Explicit handoff never steals an active lock. */
export type WriteLeaseState={state:'unclaimed'|'requesting'|'owner'|'reader'|'unavailable';message:string};
const LOCK='balloon.request-ledger-writer/1',CHANNEL=LOCK+'/handoff',TIMEOUT=8000;
let state:WriteLeaseState={state:'unclaimed',message:'送信担当の確認前です。'},generation=0,release:(()=>void)|null=null,pending:Promise<void>|null=null;
let channel:BroadcastChannel|null=null,cancelHandoff:(()=>void)|null=null,releaseWhenIdle=false;
const operations=new Set<object>();
const listeners=new Set<(value:WriteLeaseState)=>void>();
const emit=(value:WriteLeaseState)=>{state=value;for(const fn of listeners)fn({...value});};
export const writeLeaseState=()=>({...state});
export const ownsWriteLease=()=>state.state==='owner';
export function observeWriteLease(fn:(value:WriteLeaseState)=>void){listeners.add(fn);return()=>{listeners.delete(fn);};}
export function requireWriteLease(){if(!ownsWriteLease())throw Error('このタブには送信権がありません。「このタブで送信権を取得」で担当を切り替えてください。編集・保存結果・未確認要求は保持しています。');}
/** Include the response AND ledger cleanup in the caller's try/finally. */
export function beginWriteOperation(){requireWriteLease();const token={};operations.add(token);return()=>{if(!operations.delete(token))return;if(!operations.size&&releaseWhenIdle){releaseWhenIdle=false;release?.();release=null;}};}
function ensureChannel(){
 if(channel||typeof window==='undefined'||typeof BroadcastChannel==='undefined')return;
 try{channel=new BroadcastChannel(CHANNEL);channel.onmessage=event=>{
  const message=event.data;if(message?.type!=='handoff-request'||typeof message.id!=='string'||!ownsWriteLease())return;
  if(operations.size){channel?.postMessage({type:'handoff-busy',id:message.id});return;}
  generation++;emit({state:'reader',message:'別のタブへ送信担当を引き継ぎました。編集中の条件・地図・3D接続は保持しています。'});
  release?.();release=null;channel?.postMessage({type:'handoff-released',id:message.id});
 };}catch{/* Normal lock acquisition remains available. */}
}
function acquire(epoch:number):Promise<boolean>{return new Promise(resolve=>{
 try{void navigator.locks.request(LOCK,{mode:'exclusive',ifAvailable:true},async lock=>{
  if(epoch!==generation||!lock){resolve(false);return;}
  const held=new Promise<void>(done=>{release=done;});
  emit({state:'owner',message:'このタブが保存・計算要求を送信します。未確認要求は自動で再送しません。'});resolve(true);await held;
 }).catch(error=>{if(epoch===generation)emit({state:'unavailable',message:error instanceof Error?error.message:String(error)});resolve(false);});}
 catch(error){if(epoch===generation)emit({state:'unavailable',message:error instanceof Error?error.message:String(error)});resolve(false);}
});}
async function handoff(epoch:number){
 if(!channel){emit({state:'reader',message:'別のタブが送信担当です。この環境ではタブ間の引継ぎ通信が使えません。担当タブの編集を保全して閉じた後、もう一度取得してください。'});return;}
 emit({state:'requesting',message:'別のタブから送信担当を引き継いでいます（最大8秒）。'});
 const id=crypto.randomUUID();
 await new Promise<void>(resolve=>{
  let ended=false,checking=false;
  const finish=()=>{if(ended)return;ended=true;if(epoch===generation&&!ownsWriteLease())generation++;clearTimeout(timeout);clearInterval(poll);channel?.removeEventListener('message',reply);if(cancelHandoff===finish)cancelHandoff=null;resolve();};
  const check=async()=>{if(ended||checking)return;if(epoch!==generation){finish();return;}checking=true;const granted=await acquire(epoch);checking=false;if(granted||state.state==='unavailable')finish();};
  const reply=(event:MessageEvent)=>{if(event.data?.id!==id)return;if(event.data.type==='handoff-busy'){if(epoch===generation)emit({state:'reader',message:'別のタブが要求の受付・記録を処理中です。処理完了後に、もう一度取得してください。計算や保存を二重送信していません。'});finish();}else if(event.data.type==='handoff-released')void check();};
  const timeout=setTimeout(()=>{if(epoch===generation)emit({state:'reader',message:'送信担当から8秒以内に応答がありません。古い版や休止中のタブが担当の可能性があります。担当タブの編集を保全して更新するか閉じた後、もう一度取得してください。この画面の編集・3D接続は保持しています。'});finish();},TIMEOUT);
  const poll=setInterval(()=>void check(),100);cancelHandoff=finish;channel!.addEventListener('message',reply);channel!.postMessage({type:'handoff-request',id});
 });
}
/** Startup only tries an available lock; explicit clicks may request handoff. */
export function claimWriteLease(takeOver=false):Promise<void>{
 if(ownsWriteLease())return Promise.resolve();if(pending)return pending;
 if(typeof navigator==='undefined'||!navigator.locks){emit({state:'unavailable',message:'このブラウザではタブ間の送信担当を固定できません。Web Locksに対応したブラウザのlocalhost画面で開いてください。保存結果の閲覧は続けられます。'});return Promise.resolve();}
 ensureChannel();const epoch=++generation;emit({state:'requesting',message:'送信担当を確認しています。'});
 const work=(async()=>{if(await acquire(epoch)||epoch!==generation||state.state==='unavailable')return;if(takeOver)await handoff(epoch);else emit({state:'reader',message:'別のタブが送信担当です。保存した結果の詳細はこのタブでも読めます。保存・再計算・新しい群集計は下のボタンで担当を切り替えて行います。'});})();
 pending=work;void work.finally(()=>{if(pending===work)pending=null;});return work;
}
export function releaseWriteLease(){generation++;cancelHandoff?.();pending=null;channel?.close();channel=null;emit({state:'unclaimed',message:'送信担当の確認前です。'});if(operations.size)releaseWhenIdle=true;else{release?.();release=null;}}
