// Derived from the archived 0.40.1 r2 screen; see frontend/SCREEN_PROVENANCE.md.
export function install(scope) {
const {window,document}=scope;
(function(root){
'use strict';
const palette=[['teal','#08788b','青緑'],['purple','#8e4d91','紫'],['orange','#be6b23','橙'],['green','#397844','緑'],['blue','#355aac','青'],['rose','#9c415b','紅'],['red','#df2948','赤'],['gold','#b8860b','金'],['cyan','#00a5bf','水色'],['slate','#526775','灰青']].map(([id,color,label])=>({id,color,label}));
const bandLevels=[.5,.9,.95],alphas=[.24,.13,.065];
const close=ring=>{const out=ring.map(p=>[...p]);if(out.length&&JSON.stringify(out[0])!==JSON.stringify(out.at(-1)))out.push([...out[0]]);return out;};
function bands(ellipses){return ellipses.flatMap((e,i)=>{if(!e||e.geometry&&e.geometry.type!=='Polygon')return[];const prior=i?ellipses[i-1]:null;if(prior&&e.threshold<=prior.threshold+1e-9)return[];return [{level:bandLevels[i],lowerLevel:i?bandLevels[i-1]:0,fillOpacity:alphas[i],upperContourCount:e.count,lowerContourCount:prior?.count||0,geometry:{type:'Polygon',coordinates:[close(e.points.map(([lat,lon])=>[lon,lat])),...(prior&&(!prior.geometry||prior.geometry.type==='Polygon')?[close(prior.points.map(([lat,lon])=>[lon,lat])).reverse()]:[])]}}];});}
// Repeated parent/child text is display formatting, never object identity.
function regionLabel(layerName,regionName){return layerName===regionName?regionName:layerName+' / '+regionName;}
function levelFor(region,levels){return levels.find(l=>l.id===region.levelId)||levels.find(l=>l.id==='normal')||levels[0];}
function classify(result,regions,levels){const hitDetails={};for(const entry of result.perRegion){const region=regions.find(r=>r.id===entry.id),level=levelFor(region,levels);for(const id of entry.ids){const d=hitDetails[id]||(hitDetails[id]={regionIds:[],levelId:level.id,priority:level.priority,color:level.color,levelName:level.name});d.regionIds.push(entry.id);if(level.priority>d.priority)Object.assign(d,{levelId:level.id,priority:level.priority,color:level.color,levelName:level.name});}}return {...result,hitDetails};}
function hex(color){if(/^#[0-9a-f]{6}$/i.test(color))return color.toLowerCase();const m=/^hsl\(\s*([\d.]+)[ ,]+([\d.]+)%[ ,]+([\d.]+)%\s*\)$/i.exec(color);if(!m)throw Error('未対応の色です: '+color);const h=+m[1]/360,s=+m[2]/100,l=+m[3]/100,a=s*Math.min(l,1-l),f=n=>{const k=(n+h*12)%12;return l-a*Math.max(-1,Math.min(k-3,9-k,1));};return '#'+[f(0),f(8),f(4)].map(v=>Math.round(v*255).toString(16).padStart(2,'0')).join('');}
function kmlColor(color,alpha=1){const c=hex(color).slice(1);return Math.round(Math.max(0,Math.min(1,alpha))*255).toString(16).padStart(2,'0')+c.slice(4,6)+c.slice(2,4)+c.slice(0,2);}
const api={palette,bandLevels,bands,close,regionLabel,levelFor,classify,hex,kmlColor,zoneOpacity:.12,curtainOpacity:.22,flightColor:'#ffe34d',heightAssumption:'人工hをKML表示用に各点の地面からの高さと見立てる模式表現。実飛翔高度や鉛直基準の採用ではありません。'};
root.BJP_STYLE=api;
})(typeof window==='undefined'?globalThis:window);

}
