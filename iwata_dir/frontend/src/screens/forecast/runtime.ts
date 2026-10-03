import L from 'leaflet';
import Plotly from 'plotly.js-dist-min';
import { screenScope } from '../lifecycle';
import { install as data } from './data.js';
import { install as math } from './math.js';
import { install as fixture } from '../weather/fixture.js';
import { install as style } from '../shared/scene-style.js';
import { install as season } from './season-adapter.js';
import { install as scene } from './scene-document.js';
import { install as exports } from './export390.js';
import { install as appearance } from './appearance390.js';
import { install as mapStyle } from './map-style-guard401.js';
import { mount } from './controller.js';
import { mount as hover } from './hover400.mjs';
import markup from './markup.html?raw';
import './screen.css';
export function mountForecast(host: HTMLElement, bridge: any) {
 host.innerHTML=markup;
 const scope=screenScope(host,{L,Plotly});
 for(const install of [data,math,fixture,style,season,scene,exports,appearance,mapStyle])install(scope);
 let runtime:any,removeHover:(()=>void)|undefined;
 try{runtime=mount(scope,bridge);removeHover=hover(scope);}catch(error){scope.dispose();(scope.local.disposeMap as (()=>void)|undefined)?.();host.replaceChildren();throw error;}
 let alive=true;const capture=()=>queueMicrotask(()=>{if(alive)bridge.changed?.(runtime.snapshot());});
 for(const event of ['click','change','input'])host.addEventListener(event,capture);
 return {...runtime,dispose(){alive=false;for(const event of ['click','change','input'])host.removeEventListener(event,capture);removeHover?.();runtime.dispose();host.replaceChildren();}};
}
