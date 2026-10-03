import {climateSourceLabel} from '../../climateDomain';
import {annualPlots,spatialPlot,spatialDefinition,colorbar,esc} from './plots';
import {createWindExport,embedWindBackground,createPreparedWindDownload,windDownloadConditions} from './export';
import {checkedRose,climateRosePlot,meanProfilePlot,roseLegend,roseLocationMap,rosePointLabel,roseScale,roseUnavailable,rosePopulationLabel,roseMethod,nativeRosePointMap,nearestRosePoint} from './climateDistributions';
import {monthlyProfileDefinition,monthlyProfileMethod,monthlyProfileLegend,monthlyProfilePlot,monthlyProfileView} from './monthlyProfiles';
const grains=['half','month','season'];
const grainLabels={quarter:'月内4区分・48区分',half:'半月・24区分',month:'月・12区分',season:'季節・4区分'};
export function climateDisplayState(input={},hasProfiles=false){
 const grain=(value,fallback)=>grains.includes(value)?value:fallback;
 const page=value=>Number.isInteger(value)&&value>=0?value:0;
 return {...input,view:['annual','monthly','spatial','landing'].includes(input.view)?input.view:'annual',annual_grain:input.annual_grain==='quarter'?'quarter':grain(input.annual_grain,'half'),spatial_grain:grain(input.spatial_grain,'month'),monthly_grain:grain(input.monthly_grain,'month'),monthly_mode:['profile','rose','quantiles'].includes(input.monthly_mode)?input.monthly_mode:hasProfiles?'quantiles':'profile',monthly_page:page(input.monthly_page),spatial_mode:input.spatial_mode==='steady'?'steady':'wind',spatial_scale:input.spatial_scale==='level'?'level':'all',spatial_page:page(input.spatial_page)};
}

// Fixed source adapters supply every grain. These controls change the view, not the query.
export function mountClimate(scope,bridge){
 const {document,window,requestAnimationFrame,cancelAnimationFrame}=scope,$=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
 const downloads=new Map();let models=null,lastModel=null,lastDisplay='',disposed=false,frame=0,exportAbort=null,exportPending=null,state=climateDisplayState(bridge.saved);
 let pendingState={},pointVm=null,selectedPoint=null;
 if(!bridge.saved?.applied)$('#population').open=true;
 const prep=$('#population .population-grid');prep.id='climate-preparation';prep.replaceChildren();
 const flight=$('#landing');flight.replaceChildren();
 $('.intro .artificial').textContent='保存気象集計。原時刻の気象場や飛行結果は再構成しません。';
 $('#annual .section-title p').textContent='同じ地域・気象有効時刻の平均速さ・平均来向・定常度を読みます。時間の細かさを選び、同じ条件で季節内の変化を比べます。';
 $('.annual-controls span').textContent='区切りの変更は保存結果内で行います。中央値と月の幅は「季節による分布」で確認できます。';
 for(const node of $$('[data-view]')){node.disabled=false;node.removeAttribute('title');node.onclick=()=>intent({view:node.dataset.view});}
 const support=document.createElement('p');support.id='climate-support-note';support.className='definition';$('#view-nav').after(support);
 $('.methods').innerHTML='<summary>集計・データ・原図対応</summary><div id="climate-methods"></div>';
 $('footer').textContent='保存気象集計の閲覧。経験頻度と期間平均であり、将来の飛行安全性の保証ではありません。';
 $('#point-minimap').setAttribute('aria-label','実風配の代表地点と選択地域');
 const pointAction=document.createElement('p'),pointNote=document.createElement('span'),pointRetry=document.createElement('button');pointAction.className='definition';pointAction.hidden=true;pointAction.id='climate-point-action';pointNote.setAttribute('role','status');pointRetry.textContent='この地点を再試行';pointRetry.onclick=()=>bridge.retryPoint();pointAction.append(pointNote,pointRetry);$('#point-minimap').after(pointAction);
 const pointDialog=$('#point-dialog'),pointSelect=document.createElement('select'),pointConfirm=document.createElement('button'),pointLabel=document.createElement('label');pointSelect.setAttribute('aria-label','風配の元格子点');pointLabel.textContent='選択する元格子 ';pointLabel.append(pointSelect);pointConfirm.textContent='この地点の風配へ切替';pointConfirm.className='primary';$('#point-coordinates').after(pointLabel,pointConfirm);
 pointDialog.querySelector('.point-dialog-head + p').textContent='地図をクリックすると最も近い元格子を選択します。赤い輪が選択中、橙の点が表示中の地点です。補間した地点は作りません。';
 pointDialog.querySelector('small').textContent='破線：集計する地域。風配は選択した1元格子の時刻標本で、地域全体の分布とは異なります。';
 $('#close-point-dialog').onclick=()=>pointDialog.close();
 function pointLabelText(c){return `元格子 ${c.cell_id}：${c.lat.toFixed(4)}°N / ${c.lon.toFixed(4)}°E`;}
 function drawPointChoice(){
  if(!pointVm)return;const c=pointVm.metadata.source.native_grid.find(c=>c.cell_id===selectedPoint);if(!c)return;
  pointSelect.value=String(c.cell_id);$('#point-dialog-map').innerHTML=nativeRosePointMap(pointVm,c.cell_id,scope.local.backgroundEnabled);$('#point-coordinates').textContent='選択中 '+pointLabelText(c)+' ／ 表示中 '+rosePointLabel(checkedRose(pointVm));
  $('#point-map-status').textContent=scope.local.backgroundEnabled?'地理背景：国土地理院 標準地図。地域・UTC時刻・気圧面の未適用編集は適用せず、表示中の条件で地点だけを切り替えます。':'背景未接続。元格子の位置と座標を表示しています。表示中の条件で地点だけを切り替えます。';
 }
 function openPointChoice(){
  const vm=choose('monthly'),r=vm&&checkedRose(vm);if(!r||!pendingState.pointAvailable||pendingState.sourceId!==vm.identity.source_id)return;
  pointVm=vm;selectedPoint=pendingState.point?.cell_id??r.point.cell_id;pointSelect.replaceChildren();for(const c of vm.metadata.source.native_grid){const option=document.createElement('option');option.value=String(c.cell_id);option.textContent=pointLabelText(c);pointSelect.append(option);}drawPointChoice();pointDialog.showModal();
 }
 pointSelect.onchange=()=>{selectedPoint=Number(pointSelect.value);drawPointChoice();};
 $('#point-dialog-map').onclick=e=>{if(!pointVm)return;const svg=$('#point-dialog-map svg'),matrix=svg?.getScreenCTM();if(!matrix)return;const p=svg.createSVGPoint();p.x=e.clientX;p.y=e.clientY;const local=p.matrixTransform(matrix.inverse()),id=nearestRosePoint(pointVm,local.x,local.y);if(id!==null){selectedPoint=id;drawPointChoice();}};
 $('#point-dialog-map').addEventListener('error',e=>{if(e.target?.matches?.('[data-basemap]'))$('#point-map-status').textContent='背景の取得に失敗しました。元格子・座標・選択は保持しています。';},true);
 pointConfirm.onclick=()=>{if(!pointVm||models?.half.metadata.source.source_id!==pointVm.metadata.source.source_id)return;pointDialog.close();bridge.point(selectedPoint);};
 function syncPointControls(){
  const isRose=state.view==='monthly'&&state.monthly_mode==='rose';
  // Monthly quantile cards have their own twelve periods; point controls belong to the rose view only.
  const vm=isRose?choose('monthly'):null,r=vm&&checkedRose(vm),supported=pendingState.pointAvailable||vm?.metadata.source.capabilities.wind_rose_point_select===true,p=pendingState.point,same=pendingState.sourceId===vm?.identity.source_id;
  pointAction.hidden=!r;
  pointNote.textContent=p?.message??(supported?'風配は元格子点を選んで比較できます。地域全体の中央値・幅は変えません。':'この保存資料の風配は固定代表地点のみです。');
  if(supported&&(!pendingState.pointAvailable||!same))pointNote.textContent+=' 表示中の資料を現在選択していないため、地点切替は利用できません。';
  pointRetry.hidden=!p;pointRetry.disabled=!p||['waiting','running'].includes(p.state);let chooseButton=$('#choose-native-rose-point');if(supported&&r&&state.monthly_mode==='rose'&&!chooseButton){chooseButton=document.createElement('button');chooseButton.id='choose-native-rose-point';chooseButton.textContent='地点を選ぶ';chooseButton.onclick=openPointChoice;$('#point-minimap').append(chooseButton);}if(chooseButton){chooseButton.hidden=!supported;chooseButton.disabled=!pendingState.pointAvailable||!same;}
  pointConfirm.disabled=!pendingState.pointAvailable||!same;
 }
 const quantiles=document.createElement('button');quantiles.dataset.monthly='quantiles';quantiles.textContent='中央値と月の幅';$('#monthly [data-monthly="profile"]').before(quantiles);
 $('#monthly [data-monthly="profile"]').textContent='平均風速（補助図）';
 $('#monthly [data-monthly="rose"]').textContent='代表地点の風配';
 const roseAction=document.createElement('p');roseAction.id='climate-rose-action';roseAction.className='definition';$('#monthly-definition').after(roseAction);
 const allHours=document.createElement('button');allHours.textContent='全時刻の条件へ戻す（未適用）';allHours.onclick=()=>{bridge.allHours();$('#population').open=true;};roseAction.append(allHours);
 for(const e of $$('[data-spatial]'))e.onclick=()=>intent({spatial_mode:e.dataset.spatial,spatial_page:0});
 for(const e of $$('[data-monthly]'))e.onclick=()=>intent({monthly_mode:e.dataset.monthly,monthly_page:0});
 $('#spatial-scale').onchange=e=>intent({spatial_scale:e.target.value});
 $('#annual-grain').onchange=e=>intent({annual_grain:e.target.value});
 $('#map-grain').onchange=e=>intent({spatial_grain:e.target.value,spatial_page:0});
 $('#rose-grain').onchange=e=>intent({monthly_grain:e.target.value,monthly_page:0});
 function pressureReadout(selector,applied,selected=applied){const output=$(selector).closest('label').querySelector('output');output.classList.add('climate-level-readout');output.innerHTML=`<span>選択中 ${esc(selected.pressure)} hPa</span><span>表示中 ${esc(applied.pressure)} hPa<small>ISA ${esc(applied.height.toFixed(2))} km（参考高度）</small></span>`;}
 for(const selector of ['#map-level','#rose-level']){
  const control=$(selector).closest('label');control.classList.add('climate-level-control');control.closest('.layer-controls').classList.add('climate-level-toolbar');$(selector).setAttribute('aria-label',selector==='#map-level'?'地域図の気圧面':'風配の気圧面');
  const action=document.createElement('span');action.id=selector.slice(1)+'-apply';action.className='climate-level-apply';const button=document.createElement('button'),note=document.createElement('small');button.textContent='この気圧面を再試行';button.disabled=true;button.onclick=()=>bridge.apply();note.setAttribute('role','status');action.append(button,note);$(selector).closest('label').after(action);
  $(selector).oninput=e=>{const vm=choose(selector==='#map-level'?'spatial':'monthly');if(!vm)return;const l=vm.levels[+e.target.value];pressureReadout(selector,vm.levels[vm.levelIndex],l);bridge.level(l.id);};
  $(selector).onchange=null;
 }
 function choose(view){if(!models)return null;if(view==='monthly'&&state.monthly_mode==='quantiles')return monthlyProfileView(models.half);return models[state[view+'_grain']]??models.half;}
 function fields(){return {view:state.view,annual_grain:state.annual_grain,spatial_grain:state.spatial_grain,monthly_grain:state.monthly_grain,monthly_mode:state.monthly_mode,monthly_page:state.monthly_page,spatial_mode:state.spatial_mode,spatial_scale:state.spatial_scale,spatial_page:state.spatial_page};}
 function intent(patch){state=climateDisplayState({...state,...patch});bridge.onView(fields());render();}
 function grainControl(selector,view){const node=$(selector),vm=choose(view);node.innerHTML=(view==='annual'?['quarter',...grains]:grains).map(g=>`<option value="${g}" ${models?.[g]?'':'disabled'}>${grainLabels[g]}${models?.[g]?'':'（この保存結果は未対応）'}</option>`).join('');node.value=vm?.metadata.grain??'half';node.disabled=!vm;node.closest('label').hidden=view==='monthly'&&state.monthly_mode==='quantiles';}
 function render(){
  if(disposed)return;const display=JSON.stringify(fields());if(lastModel===models&&lastDisplay===display)return;lastModel=models;lastDisplay=display;
  $$('[data-view]').forEach(e=>e.setAttribute('aria-selected',String(e.dataset.view===state.view)));$$('.view').forEach(e=>e.hidden=e.id!==state.view);
  $$('[data-spatial]').forEach(e=>e.setAttribute('aria-pressed',String(e.dataset.spatial===state.spatial_mode)));$$('[data-monthly]').forEach(e=>e.setAttribute('aria-pressed',String(e.dataset.monthly===state.monthly_mode)));
  $('#spatial-scale').value=state.spatial_scale;$('#scale-control').hidden=state.spatial_mode!=='wind';
  grainControl('#annual-grain','annual');grainControl('#map-grain','spatial');grainControl('#rose-grain','monthly');
  if(!models){for(const id of ['annual','spatial','monthly'])$('#'+id+'-plots').textContent='固定集計はまだ表示していません。資料と対象を確認し、集計を適用してください。';$$('.save').forEach(e=>e.disabled=true);roseAction.hidden=true;return;}
  $$('.save').forEach(e=>e.disabled=false);const vm=choose(state.view)??models.half;
  $('.intro .artificial').textContent=climateSourceLabel(models.half.metadata.source)+'。原時刻の気象場や飛行結果は再構成しません。';
  $('#applied-summary').textContent=climateSourceLabel(models.half.metadata.source)+' · '+models.half.populationLabel;$('#population-line').textContent='表示中：'+vm.populationLabel+' ／ '+vm.countDefinition;
  for(const id of ['annual','spatial','monthly'])$('#'+id+' .workspace-context').textContent=choose(id).populationLabel;
  support.textContent=(models.quarter?'年間の高度構造は原標本からの48区分にも対応します。':models.half.metadata.source?.capabilities?.raw_observations?'この保存結果には48区分がありません。現在利用できる原標本資料を選び、対象を確認して再集計すると48区分を追加できます。':'この資料は半月までの集計値です。48区分には時刻別の原データが必要です。')+' '+(models.month?'各図の区切りは固定結果内で切替できます。':'旧保存結果：半月図を保持しています。月・季節・風配の追加は新しい集計を明示的に適用してください。')+(models.half.metadata.query?.hours_utc?' 表示中のUTC時刻に絞った集計です。風配の支持は代表地点の図に明記します。':'');
  for(const selector of ['#map-level','#rose-level']){const levelVm=choose(selector==='#map-level'?'spatial':'monthly'),l=levelVm.levels[levelVm.levelIndex];$(selector).max=levelVm.levels.length-1;$(selector).value=levelVm.levelIndex;pressureReadout(selector,l);}
  const methods=$('#climate-methods');methods.replaceChildren();for(const value of [vm.annualDefinition,...(models.half.monthlyProfiles&&state.monthly_mode!=='quantiles'?[monthlyProfileMethod(models.half)]:[]),vm.countDefinition,vm.heightDefinition,vm.spatialDefinition,roseMethod(vm.windRose),'平均来向はFROM、地域図の矢印は移流先TO。R<0.3は平均方向の代表性が弱いとする表示上の区分です。','元資料の出典・利用条件（提供資料の申告）: '+JSON.stringify(vm.metadata.source?.attribution??{})]){const p=document.createElement('p');p.textContent=value;methods.append(p);}
  if(state.view==='annual')$('#annual-plots').innerHTML=annualPlots(choose('annual'),window.WindDirection);
  if(state.view==='spatial')renderSpatial();if(state.view==='monthly')renderMonthly();syncPointControls();
  document.documentElement.style.setProperty('--nav-h',$('#view-nav').getBoundingClientRect().height+'px');
 }
 function smallMultiples(section,vm,draw){
  const periods=section==='spatial'?vm.spatialPeriods:vm.annualPeriods,target=$('#'+section+'-plots'),toolbar=$('#'+section+' .workspace-toolbar'),nav=$('#view-nav').getBoundingClientRect().height,available=Math.max(240,globalThis.innerHeight-nav-toolbar.getBoundingClientRect().height-56),width=target.getBoundingClientRect().width,capacity=Math.min(12,periods.length),pages=Math.ceil(periods.length/capacity),choices=capacity===4?[4,2,1]:[6,4,3,2,1],candidates=choices.map(cols=>{const rows=Math.ceil(capacity/cols),cellW=(width-(cols-1)*8)/cols,plotH=(available-(rows-1)*8)/rows-30;return{cols,rows,scale:Math.min((cellW-12)/190,plotH/175),cellW,plotH};}).filter(q=>q.cellW>=150),best=(candidates.length?candidates:[{cols:1,rows:capacity,scale:1,cellW:width,plotH:175}]).sort((a,b)=>b.scale-a.scale)[0];
  const key=section+'_page';state[key]=Math.max(0,Math.min(state[key]??0,pages-1));const start=state[key]*capacity,end=Math.min(periods.length,start+capacity);
  target.style.setProperty('--columns',best.cols);target.style.setProperty('--plot-height',Math.max(145,Math.min(270,best.plotH,(best.cellW-12)*175/190))+'px');target.dataset.capacity=capacity;target.dataset.columns=best.cols;target.dataset.rows=best.rows;target.dataset.grain=vm.metadata.grain;
  target.innerHTML=Array.from({length:end-start},(_,j)=>{const i=start+j,p=periods[i];return `<article class="plot-card"><h3 title="${esc(p.description)}">${esc(p.label)}</h3>${draw(i)}</article>`;}).join('');
  const pager=$('#'+section+'-pager');pager.replaceChildren();const prev=document.createElement('button'),next=document.createElement('button'),label=document.createElement('span');prev.textContent='←';next.textContent='→';prev.disabled=state[key]===0;next.disabled=state[key]===pages-1;label.textContent=`${periods[start].label} ～ ${periods[end-1].label} ／ ${state[key]+1}/${pages}頁`;prev.onclick=()=>intent({[key]:state[key]-1});next.onclick=()=>intent({[key]:state[key]+1});pager.append(prev,label,next);
 }
 function renderSpatial(){const vm=choose('spatial');$('#spatial-definition').textContent=spatialDefinition(vm,state.spatial_mode,state.spatial_scale);$('#spatial-legend').innerHTML=colorbar(state.spatial_mode==='wind'?(state.spatial_scale==='all'?vm.spatialAllMax:vm.spatialLevelMax):1,state.spatial_mode==='wind'?'共通 平均風速 [m/s]':'全期間・高度共通 定常度R',190,43,.78);smallMultiples('spatial',vm,i=>spatialPlot(vm,i,state.spatial_mode,state.spatial_scale,scope.local.backgroundEnabled));$('#map-status').hidden=false;$('#map-status').textContent=scope.local.backgroundEnabled?'地理背景を読み込みます。集計値は表示中の保存資料に由来します。':'背景未接続。集計値と範囲は保持しています。';}
 function renderMonthly(){
  const vm=choose('monthly'),isQuantiles=state.monthly_mode==='quantiles',isRose=state.monthly_mode==='rose',r=isRose?checkedRose(vm):null;$('#rose-controls').hidden=isQuantiles;$('#rose-level').closest('label').hidden=!isRose;$('#rose-level-apply').hidden=!isRose;$('#rose-point-name').hidden=!isRose;$('#point-minimap').hidden=!isRose;$('#rose-legend').hidden=isQuantiles?!vm.monthlyProfiles:(!isRose||!r);roseAction.hidden=!isRose||vm.windRose?.reason!=='hour_subset_not_available';
  if(isQuantiles){
   $('#point-minimap').replaceChildren();
   if(!vm.monthlyProfiles){$('#monthly-definition').textContent='この保存結果には中央値と月の10–90%幅が含まれていません。原標本に対応した資料で新しく集計すると追加できます。';$('#monthly-plots').textContent='保存済みの平均風速と風配は、各ボタンから引き続き閲覧できます。';$('#monthly-pager').replaceChildren();$('#monthly .save').disabled=true;return;}
   const acquired=vm.monthlyProfiles.months.filter(m=>m.available).length;
   $('#monthly-definition').textContent=monthlyProfileDefinition+` 原標本の取得済み ${acquired}/12か月。未取得月は空枠で残します。`;
   $('#rose-legend').innerHTML=monthlyProfileLegend();smallMultiples('monthly',vm,i=>monthlyProfilePlot(vm,i));return;
  }
  if(isRose&&!r){$('#monthly-definition').textContent=roseUnavailable(vm);$('#monthly-plots').textContent='この条件の風配は表示していません。';$('#monthly-pager').replaceChildren();$('#point-minimap').replaceChildren();$('#rose-point-name').textContent='';$('#monthly .save').disabled=true;return;}
  if(isRose){$('#monthly .workspace-context').textContent=vm.populationLabel.replace(/対象\d+\/\d+元格子/,'風配は代表1元格子');const upper=roseScale(vm);$('#monthly-definition').textContent=`${rosePopulationLabel(r)}。半径0–${upper}%はこの面・区切りの全期間で共通（頁間固定）。`;$('#rose-point-name').textContent=rosePointLabel(r);$('#point-minimap').innerHTML=roseLocationMap(vm);$('#rose-legend').innerHTML=roseLegend(r);smallMultiples('monthly',vm,i=>climateRosePlot(vm,i,upper));syncPointControls();}
  else{$('#monthly-definition').textContent='線は選択地域の格子面積を考慮した平均風速です。'+(vm.monthlyProfiles?'中央値と月の10–90%幅は「中央値と月の幅」で比較できます。':'この保存結果に中央値と月の10–90%幅は含まれていません。');$('#point-minimap').replaceChildren();smallMultiples('monthly',vm,i=>meanProfilePlot(vm,i));}
 }
 const tileError=e=>{if(e.target?.matches?.('[data-basemap]')){$('#map-status').hidden=false;$('#map-status').textContent='地理背景の取得に失敗しました。気象の集計値・範囲・固定結果は保持しています。';}};$('#spatial-plots').addEventListener('error',tileError,true);
 async function prepareSvg(target){
  if(!models)return;const section=target==='annual-plots'?'annual':target==='spatial-plots'?'spatial':'monthly',vm=choose(section),view=section==='monthly'?state.monthly_mode:section,r=view==='rose'?checkedRose(vm):null;if((view==='rose'&&!r)||(view==='quantiles'&&!vm.monthlyProfiles))return;
  const legend=view==='annual'?vm.annualDefinition:view==='spatial'?$('#spatial-definition').textContent:$('#monthly-definition').textContent+(r?' '+rosePointLabel(r):view==='quantiles'?' '+monthlyProfileMethod(vm):'');
  const snapshot=createWindExport(view==='rose'?{...vm,populationLabel:vm.populationLabel.replace(/対象\d+\/\d+元格子/,'風配は代表1元格子')}:vm,view,[...$('#'+target).querySelectorAll('svg')],{mode:state.spatial_mode,scale:state.spatial_scale,page:section==='monthly'?state.monthly_page:state.spatial_page,background:scope.local.backgroundEnabled,legend,...(r?{keySvg:roseLegend(r)}:view==='quantiles'?{keySvg:monthlyProfileLegend()}:{})});
  exportAbort?.abort();exportPending?.failed('別の図の準備を開始したため、この準備を中断しました。');const ac=new AbortController(),download=downloads.get(target);exportAbort=ac;exportPending=download;download.begin();$$('.save').forEach(e=>e.disabled=true);
  try{const output=await embedWindBackground(snapshot,ac.signal);if(disposed||exportAbort!==ac)return;const page=section==='annual'?'':` / ${output.metadata.page+1}頁`,label=(view==='annual'?'年間の高度構造':view==='spatial'?'地域図':view==='rose'?'代表地点の風配':view==='quantiles'?'中央値と月の幅':'平均風速の高度構造')+` / ${grainLabels[output.metadata.grain]}${page} / ${String(output.metadata.analysis_id).slice(0,8)}`;download.publish(output.source,`weather-${view}-${output.metadata.grain}-${output.metadata.analysis_id}-p${output.metadata.page+1}.svg`,label,windDownloadConditions(output.metadata));}
  catch(e){if(!disposed&&exportAbort===ac)download.failed();}
  finally{if(!disposed&&exportAbort===ac){exportPending=null;lastDisplay='';render();}}
 }
 $$('.save').forEach(button=>{const group=document.createElement('div'),anchor=document.createElement('a'),note=document.createElement('p'),conditions=document.createElement('small');group.className='climate-export-controls';note.setAttribute('role','status');button.replaceWith(group);group.append(button,note,anchor,conditions);button.textContent='SVGを準備';downloads.set(button.dataset.target,createPreparedWindDownload(anchor,note,conditions));button.onclick=()=>prepareSvg(button.dataset.target);});scope.addEventListener('resize',()=>{cancelAnimationFrame(frame);frame=requestAnimationFrame(()=>{if(!models)return;if(state.view==='spatial')renderSpatial();if(state.view==='monthly')renderMonthly();});});
 render();return {preparationElement:prep,flightElement:flight,snapshot:()=>({...state}),sync(model,next,pending){
  if(models!==model&&pointDialog.open)pointDialog.close();models=model;pendingState=pending;state=climateDisplayState({...state,...next,monthly_mode:next.monthly_mode},!!model?.half.monthlyProfiles);render();syncPointControls();if(model&&next.monthly_mode===undefined)bridge.onView(fields());$('#work-status').textContent=pending.status??'';
  for(const selector of ['#map-level-apply','#rose-level-apply']){const action=$(selector);action.querySelector('button').disabled=!pending.pressure||['waiting','running'].includes(pending.pressure.state);action.querySelector('button').textContent='この気圧面を再試行';action.querySelector('small').textContent=(pending.pressure?.message??'スライダーで気圧面だけを自動更新します。')+(pending.otherDraftChanged?' 地域・UTC時刻の未適用編集は適用しません。':'');}
  if(!models&&pending.restoreLabel)for(const id of ['annual','spatial','monthly'])$('#'+id+'-plots').textContent=pending.restoreLabel+'。保存した図を復元します。';
  if(models)for(const selector of ['#map-level','#rose-level']){const vm=choose(selector==='#map-level'?'spatial':'monthly'),applied=vm.levels[vm.levelIndex],sameSource=pending.sourceId===vm.identity.source_id,pointBusy=pending.point&&['waiting','running'].includes(pending.point.state),selected=sameSource?vm.levels.find(l=>l.id===(pending.pressure?.level_id??applied.id)):null;$(selector).disabled=!sameSource||pointBusy;$(selector).value=selected?vm.levels.indexOf(selected):vm.levelIndex;pressureReadout(selector,applied,selected??applied);if(pointBusy||pending.sourceId&&!sameSource)$(selector+'-apply small').textContent=pointBusy?'地点切替の完了後に操作できます。':'別資料を選択中です。共通の対象を適用すると気圧面を探索できます。';}
 },dispose(){disposed=true;exportAbort?.abort();downloads.forEach(download=>download.dispose());downloads.clear();cancelAnimationFrame(frame);$('#spatial-plots').removeEventListener('error',tileError,true);scope.dispose();}};
}
