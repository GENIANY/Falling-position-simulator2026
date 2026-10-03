import {resolveHover,tooltipPosition,shortenHoverText} from '../shared/hover-labels.mjs';
import {contourIndices} from './hover-geometry400.mjs';

export function mount(scope) {
const {window,document,setTimeout,clearTimeout}=scope;
// The 2D host supplies the displayed inventory; no computation or provider call.
const host=window.BJP_HOVER_HOST,container=host.map.getContainer();
const tip=document.createElement('div');tip.id='mapNameHover';tip.className='map-name-hover';tip.hidden=true;tip.setAttribute('role','tooltip');document.body.append(tip);
let timer=null,generation=0,moving=false,zooming=false,inventory=host.document();
function invalidate(){generation++;clearTimeout(timer);timer=null;tip.hidden=true;tip.replaceChildren();}
function canRead(){return !moving&&!zooming&&!document.hidden&&host.canRead()&&container.getBoundingClientRect().height>0&&!container.querySelector('.leaflet-tooltip');}
function move(event){
 invalidate();
 if(event.pointerType==='touch'||event.buttons||event.altKey||event.ctrlKey||event.shiftKey||event.metaKey||!canRead()||event.target.closest('.leaflet-control,.leaflet-marker-icon'))return;
 const token=generation,client={x:event.clientX,y:event.clientY};
 timer=setTimeout(()=>{
  if(token!==generation||!canRead())return;
  const rect=container.getBoundingClientRect(),point={x:client.x-rect.left,y:client.y-rect.top};
  if(point.x<0||point.y<0||point.x>rect.width||point.y>rect.height)return;
  const d=inventory,payload={context:d.context,candidates:d.candidates,geojson:{features:d.features}};
  const geo=host.map.containerPointToLatLng(point),indices=contourIndices(d.features,point,([lon,lat])=>host.map.latLngToContainerPoint([lat,lon]));
  const result=resolveHover(payload,[geo.lng,geo.lat],{lineFeatureIndices:indices});
  if(!result.targets.length)return;
  const rows=[];for(const item of result.targets){const line=document.createElement('div');line.textContent=item.text;rows.push(line);tip.append(line);}
  tip.setAttribute('aria-label',result.targets.map(t=>t.text).join(' / ')+(result.otherCount?` / 他 ${result.otherCount} 件`:''));
  if(result.otherCount){const more=document.createElement('div');more.className='hover-other';more.textContent=`他 ${result.otherCount} 件`;tip.append(more);}
  const bounds={left:Math.max(0,rect.left),top:Math.max(0,rect.top),right:Math.min(innerWidth,rect.right),bottom:Math.min(innerHeight,rect.bottom)};
  bounds.width=bounds.right-bounds.left;bounds.height=bounds.bottom-bounds.top;
  if(bounds.width<24||bounds.height<24)return;
  tip.style.maxWidth=`${Math.min(340,bounds.width-12)}px`;tip.hidden=false;
  for(const limit of [120,80,48,24]){if(tip.getBoundingClientRect().height<=bounds.height-12)break;rows.forEach((row,i)=>{row.textContent=shortenHoverText(result.targets[i].text,limit);});}
  const placement=tooltipPosition(client,tip.getBoundingClientRect(),bounds);tip.style.left=`${placement.left}px`;tip.style.top=`${placement.top}px`;
 },260);
}
container.addEventListener('pointermove',move);
for(const event of ['pointerleave','pointercancel','wheel'])container.addEventListener(event,invalidate,{passive:true});
for(const event of ['pointerdown','pointerup','keydown','scroll','visibilitychange'])document.addEventListener(event,invalidate,{capture:true,passive:true});
for(const event of ['blur','resize'])window.addEventListener(event,invalidate);
host.map.on('movestart',()=>{moving=true;invalidate();});host.map.on('moveend',()=>{moving=false;invalidate();});
host.map.on('zoomstart',()=>{zooming=true;invalidate();});host.map.on('zoomend',()=>{zooming=false;invalidate();});
window.BJP_MAP_HOVER={invalidate,commit(document){invalidate();inventory=document;}};

return ()=>{invalidate();tip.remove();};
}
