import L from 'leaflet';
import { screenScope } from '../lifecycle';
import { install as fixture } from './fixture.js';
import { install as direction } from './direction-key.js';
import { install as impact } from './impact-map.js';
import { mount } from './controller.js';
import markup from './markup.html?raw';
import './screen.css';
export function mountWeather(host:HTMLElement,bridge:any){
 host.innerHTML=markup;
 const scope=screenScope(host,{L,backgroundEnabled:bridge.background});
 for(const install of bridge.mode==='climate'?[direction]:[fixture,direction,impact])install(scope);
 let runtime:any;try{runtime=mount(scope,bridge);}catch(error){scope.dispose();(scope.local.WindUI as any)?.impact?.destroy?.();host.replaceChildren();throw error;}
 const openPlanning=(e:Event)=>{const link=(e.target as HTMLElement).closest<HTMLAnchorElement>('#open-planning');if(link){e.preventDefault();if(bridge.mode==='climate')return;const proposal=runtime.controller.handoff(runtime.controller.state.trialPoint).payload;bridge.handoff(proposal);}};host.addEventListener('click',openPlanning);
 return {...runtime,dispose(){host.removeEventListener('click',openPlanning);runtime.dispose();host.replaceChildren();}};
}
