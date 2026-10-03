import {climateSourceLabel} from '../../climateDomain';
import {esc,text,svg,colorbar,glyphCells} from './plots';
import type {WindViewModel} from './viewModel';
function originalWindCredits(vm:WindViewModel):string[]{
 const source=vm.metadata.source as {profile?:string;attribution?:{metadata?:Record<string,any>}}|undefined,m=source?.attribution?.metadata;
 if(vm.kind!=='climate'||source?.profile!=='original-utc-wind'||!m)return [];
 const credit=m.attribution??{},license=m.license;
 return [m.citation,m.dataset_doi?`資料 DOI: ${m.dataset_doi}`:null,
  license?`利用条件: ${license.spdx} ${license.url}`:credit.license?`利用条件: ${credit.license} ${credit.license_url??''}`:null,
  credit.acknowledgement,credit.responsibility_notice_ja,
  '元の風データからUTC時刻・気圧面・格子を選び、風速分布を集計した図。']
  .filter((v):v is string=>typeof v==='string'&&v.length>0);
}
export function createWindExport(vm:WindViewModel,view:'annual'|'spatial'|'profile'|'rose'|'quantiles',elements:SVGSVGElement[],options:{mode:'wind'|'steady';scale:'all'|'level';page:number;background:boolean;legend:string;keySvg?:string}){
 const annual=view==='annual',spatial=view==='spatial',backgroundUsed=spatial&&options.background,columns=annual?1:Math.min(4,Math.max(1,elements.length)),cellW=annual?1100:270,cellH=280,W=Math.max(columns*cellW+30,options.keySvg?770:0);
 const heading=annual?'いつ、どの層の風が強く、向きが揃うか':spatial?'同じ地域で、風の強さと安定度はどう違うか':view==='rose'?'季節による風の分布（代表地点の実風配）':view==='quantiles'?'月ごとの風速分布（前半・後半中央値と月10–90%幅）':'季節ごとの平均風速の高度構造';
 const periods=spatial?vm.spatialPeriods:vm.annualPeriods;
 const metadata={...structuredClone(vm.metadata),...vm.identity,view,artificial:vm.kind==='fixture',populationLabel:vm.populationLabel,countDefinition:vm.countDefinition,heightDefinition:vm.heightDefinition,annualDefinition:vm.annualDefinition,spatialDefinition:vm.spatialDefinition,periods:annual?periods:periods.slice(options.page*12,options.page*12+12),levels:vm.levels,selectedLevel:vm.levels[vm.levelIndex],spatialScaleMode:options.scale,spatialSpeedMax:options.scale==='all'?vm.spatialAllMax:vm.spatialLevelMax,displayedGlyphCellIds:spatial?[...glyphCells(vm)]:[],nativeCellCount:vm.cells.length,...options,background:backgroundUsed,version:'0.58'};
 let b='<rect width="100%" height="100%" fill="white"/>'+`<metadata>${esc(JSON.stringify(metadata))}</metadata>`+text(15,25,heading+(vm.kind==='fixture'?' — 人工データ':' — '+climateSourceLabel(vm.metadata.source)),18)+text(15,46,vm.populationLabel,11);
 const lines=options.legend.match(/.{1,75}/gu)||[];lines.forEach((s,i)=>b+=text(15,65+i*15,s,10));let top=90+lines.length*15;
 if(spatial||view==='rose'){const l=vm.levels[vm.levelIndex];b+=text(15,top,`${l.pressure} hPa / ${l.heightDescription}`,11);top+=20;}
 if(spatial){b+=`<g transform="translate(15 ${top})">${colorbar(options.mode==='wind'?metadata.spatialSpeedMax:1,options.mode==='wind'?'共通 平均風速 [m/s]':'全期間・高度共通 定常度 R',270,45,.78).replace(/^<svg[^>]*>|<\/svg>$/g,'')}</g>`;top+=55;}
 if(options.keySvg){b+=`<g transform="translate(15 ${top})">${options.keySvg.replace(/^<svg[^>]*>|<\/svg>$/g,'')}</g>`;top+=48;}
 let annualY=top;elements.forEach((el,i)=>{const vb=el.viewBox.baseVal,scale=annual?(cellW-20)/vb.width:Math.min((cellW-20)/vb.width,(cellH-30)/vb.height),label=el.closest('.plot-card')?.querySelector('h3')?.textContent||el.getAttribute('aria-label')||'',x=15+i%columns*cellW,y=annual?annualY:top+Math.floor(i/columns)*cellH;const embeddedPeriod=(view==='profile'||view==='rose'||view==='quantiles')&&el.querySelector?.('[data-period-label="true"]');b+=(embeddedPeriod?'':text(x,y,label,12))+`<g transform="translate(${x} ${y+8}) scale(${scale})">${el.innerHTML}</g>`;if(annual)annualY+=vb.height*scale+30;});
 let y=(annual?annualY:top+Math.ceil(elements.length/columns)*cellH)+5;
 const footer=[vm.countDefinition,vm.heightDefinition,vm.kind==='climate'?'資料出典・supplier-declared利用条件・固定analysis/query/result hashはSVG metadataに保持。':'人工の気象標本。実気象の受入ではありません。',backgroundUsed?'地理背景：国土地理院 地理院タイル（標準地図） https://maps.gsi.go.jp/development/ichiran.html#std':annual?'地理背景：この年間図には使用していません':spatial?'地理背景：未接続':'地理背景：この分布・高度図には使用していません'];
 for(const t of [...footer,...originalWindCredits(vm)])for(const s of t.match(/.{1,100}/gu)??[]){b+=text(15,y,s,9);y+=13;}
 return {source:svg(W,y+15,b,heading).replace('<svg ',`<svg width="${W}" height="${y+15}" `),metadata};
}
export async function embedWindBackground(r:{source:string;metadata:Record<string,any>},signal?:AbortSignal){const urls=[...new Set([...r.source.matchAll(/href="(https:\/\/cyberjapandata\.gsi\.go\.jp[^" ]+)"/g)].map(m=>m[1]))],entries=await Promise.all(urls.map(async url=>{const response=await fetch(url,{signal});if(!response.ok)throw new Error(`地図取得 ${response.status}`);const blob=await response.blob(),data=await new Promise<string>((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(String(reader.result));reader.onerror=reject;reader.readAsDataURL(blob);});return [url,data];}));for(const[url,data]of entries)r.source=r.source.split(url).join(data);r.metadata.embeddedMapTileCount=entries.length;r.metadata.mapCapture=r.metadata.background?'表示範囲の地理院標準地図を保存時に埋込み':r.metadata.view==='annual'?'年間図は地理背景を使わない':r.metadata.view==='spatial'?'背景未接続':'分布・高度図は地理背景を使わない';r.source=r.source.replace(/<metadata>[\s\S]*?<\/metadata>/,`<metadata>${esc(JSON.stringify(r.metadata))}</metadata>`);return r;}

export function windDownloadConditions(metadata:Record<string,any>){
 const source=climateSourceLabel(metadata.source),level=(metadata.view==='rose'||metadata.view==='spatial')&&metadata.selectedLevel?`${metadata.selectedLevel.pressure} hPa`:null;
 const point=metadata.view==='rose'&&metadata.wind_rose?.available?metadata.wind_rose.point:null;
 const pointLabel=point?`風配の元格子 ${point.cell_id}（${Number(point.lat).toFixed(4)}°N / ${Number(point.lon).toFixed(4)}°E）`:null;
 return [source,String(metadata.populationLabel??''),level,pointLabel].filter(Boolean).join(' · ');
}

/** A generated SVG stays available for an explicit browser download request.
 * No timer or click result is treated as evidence that a file was saved. */
export function createPreparedWindDownload(anchor:HTMLAnchorElement,note:HTMLElement,conditions:HTMLElement){
 let currentUrl:string|null=null,disposed=false;
 anchor.hidden=true;conditions.hidden=true;
 anchor.onclick=()=>{note.textContent='ブラウザへ保存を要求しました。ダウンロード一覧を確認してください。リンクから同じ生成済みSVGを保存し直せます。';};
 return {
  begin(){if(!disposed)note.textContent='表示中の固定図からSVGを準備しています…'+(currentUrl?' 下のリンクは前回生成分です。':'');},
  publish(source:string,filename:string,label:string,population:string){
   if(disposed)return false;
   const next=URL.createObjectURL(new Blob([source],{type:'image/svg+xml;charset=utf-8'})),previous=currentUrl;
   currentUrl=next;anchor.href=next;anchor.download=filename;anchor.textContent='生成済みSVGを保存：'+label;anchor.title=filename;anchor.hidden=false;conditions.textContent='生成時の条件：'+population;conditions.hidden=false;
   note.textContent='SVGを準備しました。リンクから保存してください。図を変更した後も、再生成するまでこの内容を保持します。';
   if(previous)URL.revokeObjectURL(previous);return true;
  },
  failed(message='SVGの準備を完了できませんでした。'){
   if(!disposed)note.textContent=message+(currentUrl?' リンクは前回生成分のままです。':' 表示中の集計は保持しています。');
  },
  dispose(){if(disposed)return;disposed=true;if(currentUrl)URL.revokeObjectURL(currentUrl);currentUrl=null;anchor.removeAttribute('href');anchor.hidden=true;conditions.hidden=true;anchor.onclick=null;}
 };
}
