// Derived from the archived 0.40.1 r2 screen; see frontend/SCREEN_PROVENANCE.md.
export function install(scope) {
const {window,document}=scope;
(function(root){
'use strict';

// Local stylesheet recovery only. No Viewer, iframe, provider, storage or fetch API.
function createController({check,load,capture,restore,present,timeoutMs=8000,setTimer=setTimeout,clearTimer=clearTimeout}){
 let attempts=0,automaticAttempted=false,phase='checking',pending=null,disposed=false,revision=0,abort=null,timer=null;
 const state=()=>({phase,attempts,automaticAttempted,busy:!!pending,ready:phase==='ready'});
 function show(next){phase=next;present(state());}
 function inspect(){try{return check()===true;}catch{return false;}}
 function ensure(){
  if(disposed||pending)return false;const ok=inspect();show(ok?'ready':'unavailable');
  if(!ok&&!automaticAttempted){automaticAttempted=true;retry();}
  return ok;
 }
 async function retry(){
  if(disposed)return false;if(pending)return pending;
  if(inspect()){show('ready');return true;}
  const own=++revision,signalOwner=new AbortController();abort=signalOwner;attempts++;
  const timeout=new Promise(resolve=>{timer=setTimer(()=>{signalOwner.abort();resolve(null);},timeoutMs);});
  // The loader must return a transaction and honor cancellation. It cannot
  // remove the previous stylesheet before the new one passes computed checks.
  const work=Promise.resolve().then(()=>load({signal:signalOwner.signal,attempt:attempts}));
  pending=Promise.race([work,timeout]).then(transaction=>{
   if(!transaction||disposed||own!==revision||signalOwner.signal.aborted){transaction?.rollback();return false;}
   try{
    if(!inspect())throw new Error('style verification');
    // Outside controls can change the view while the stylesheet is loading.
    // Preserve the latest intent, never a snapshot from the start of a wait.
    restore(capture());
    if(disposed||own!==revision||signalOwner.signal.aborted)throw new Error('cancelled');
    transaction.commit();return true;
   }catch{transaction.rollback();return false;}
  }).catch(()=>false).then(ok=>{
   if(!ok)signalOwner.abort();
   if(!disposed&&own===revision)show(ok?'ready':'unavailable');
   return ok;
  }).finally(()=>{if(own===revision){clearTimer(timer);timer=null;abort=null;pending=null;if(!disposed)present(state());}});
  show('loading');return pending;
 }
 function cancel(){revision++;abort?.abort();abort=null;clearTimer(timer);timer=null;pending=null;}
 return {ensure,retry,state,isReady:()=>!disposed&&phase==='ready',suspend(){if(disposed)return;cancel();if(phase==='loading')show('unavailable');},destroy(){if(disposed)return;disposed=true;cancel();}};
}

function mount({document:doc,window:win,mapElement,styleLink,notice,text,retryButton,captureView,restoreView,onUnavailable=()=>{},timeoutMs=8000}){
 const probeRoot=doc.createElement('div');probeRoot.setAttribute('aria-hidden','true');
 probeRoot.style.cssText='position:fixed;left:-10000px;top:0;width:2px;height:2px;overflow:hidden;visibility:hidden;pointer-events:none;';
 const container=doc.createElement('div'),pane=doc.createElement('div'),tiles=doc.createElement('div'),tile=doc.createElement('img');
 container.className='leaflet-container';pane.className='leaflet-pane';tiles.className='leaflet-tile-container';tile.className='leaflet-tile';
 tiles.append(tile);pane.append(tiles);container.append(pane);probeRoot.append(container);doc.body.append(probeRoot);
 let currentLink=styleLink,destroyed=false;
 const source=new URL(styleLink.getAttribute('href'),doc.baseURI),nonce=Date.now().toString(36);
 const page=new URL(win.location.href);
 if(source.origin!==page.origin||source.protocol!==page.protocol||!['http:','https:','file:'].includes(source.protocol)||!/^\/(?:assets\/leaflet-[A-Za-z0-9_-]+|node_modules\/leaflet\/dist\/leaflet)\.css$/.test(source.pathname)||source.search||source.hash){probeRoot.remove();throw new Error('Expected the pinned local Leaflet stylesheet');}
 // A stylesheet's sheet property is neither the success proof nor a dependency
 // on a particular browser/automation mirror. Read actual computed properties.
 function computedReady(){
  const style=e=>win.getComputedStyle(e);
  if(style(container).overflowX!=='hidden'||style(container).overflowY!=='hidden')return false;
  if([pane,tiles,tile].some(e=>{const s=style(e);return s.position!=='absolute'||s.left!=='0px'||s.top!=='0px';}))return false;
  const actualPane=mapElement.querySelector('.leaflet-pane');
  if(!actualPane||style(actualPane).position!=='absolute')return false;
  for(const selector of ['.leaflet-tile-container','.leaflet-tile']){const actual=mapElement.querySelector(selector);if(actual&&style(actual).position!=='absolute')return false;}
  // Do not count our own emergency clipping as Leaflet's correct map overflow.
  // Keep panes invisible, remove clipping only for this synchronous measurement,
  // then restore before a browser paint or asynchronous continuation can occur.
  const previous=mapElement.getAttribute('data-map-style-probe');
  mapElement.setAttribute('data-map-style-probe','');
  try{return style(mapElement).overflowX==='hidden'&&style(mapElement).overflowY==='hidden';}
  finally{if(previous===null)mapElement.removeAttribute('data-map-style-probe');else mapElement.setAttribute('data-map-style-probe',previous);}
 }
 function load({signal,attempt}){
  return new Promise((resolve,reject)=>{
   if(destroyed||signal.aborted){reject(new DOMException('Cancelled','AbortError'));return;}
   const old=currentLink,oldDisabled=old.disabled,next=doc.createElement('link'),url=new URL(source);
   url.searchParams.set('bjp-style-retry',nonce+'-'+attempt);next.rel='stylesheet';next.href=url.href;
   let settled=false,closed=false;
   const detachEvents=()=>{next.removeEventListener('load',loaded);next.removeEventListener('error',failed);};
   function rollback(){if(closed)return;closed=true;detachEvents();signal.removeEventListener('abort',cancelled);old.disabled=oldDisabled;next.remove();}
   function fail(){if(settled){rollback();return;}settled=true;rollback();reject(new Error('Local stylesheet unavailable'));}
   function cancelled(){fail();}
   function failed(){fail();}
   function loaded(){
    if(settled||closed||signal.aborted||destroyed)return;
    // Verify the replacement by itself; complementary partial rules from the
    // previous sheet must not produce a false success.
    old.disabled=true;
    let valid=false;try{valid=computedReady();}catch{}
    if(!valid){fail();return;}
    settled=true;detachEvents();
    resolve({commit(){if(closed)return;if(signal.aborted||destroyed){rollback();return;}closed=true;signal.removeEventListener('abort',cancelled);next.id=old.id;currentLink=next;old.remove();},rollback});
   }
   next.addEventListener('load',loaded);next.addEventListener('error',failed);signal.addEventListener('abort',cancelled,{once:true});
   // Preserve vendor-before-application cascade order through every retry.
   old.parentNode.insertBefore(next,old.nextSibling);
  });
 }
 function present(s){
  mapElement.dataset.mapDisplay=s.ready?'ready':s.phase;notice.hidden=s.ready;retryButton.disabled=s.busy;
  text.textContent=s.ready?'':s.phase==='loading'?'2D地図の表示を読み直しています。ほかの画面の状態は保持しています。':s.attempts?'2D地図の表示を復旧できませんでした。表示を再取得できます。復旧するまでこの地図は使用できません。':'2D地図の表示を確認できません。表示を読み直します。';
  retryButton.textContent='地図表示を再取得';
  if(!s.ready)onUnavailable();
 }
 const controller=createController({check:computedReady,load,capture:captureView,restore:restoreView,present,timeoutMs});
 const retry=event=>{event.preventDefault();event.stopPropagation();controller.retry();};retryButton.addEventListener('click',retry);
 const stop=event=>event.stopPropagation(),stopped=['click','dblclick','mousedown','mouseup','pointerdown','pointerup','touchstart','touchmove','wheel'];
 for(const event of stopped)notice.addEventListener(event,stop);
 const pagehide=event=>{if(event.persisted)controller.suspend();else destroy();};
 const pageshow=event=>{if(event.persisted&&!destroyed)controller.ensure();};
 const destroy=()=>{if(destroyed)return;destroyed=true;controller.destroy();probeRoot.remove();retryButton.removeEventListener('click',retry);for(const event of stopped)notice.removeEventListener(event,stop);win.removeEventListener('pagehide',pagehide);win.removeEventListener('pageshow',pageshow);};
 win.addEventListener('pagehide',pagehide);win.addEventListener('pageshow',pageshow);
 return {ensure:controller.ensure,retry:controller.retry,isReady:controller.isReady,state:controller.state,destroy};
}

const api={createController,mount};root.BJP_MAP_STYLE=api;
})(typeof window==='undefined'?globalThis:window);

}
