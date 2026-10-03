// Derived from the archived 0.40.1 r2 screen; see frontend/SCREEN_PROVENANCE.md.
export function install(scope) {
const {window,document}=scope;
(function(root){
'use strict';
const S=root.BJP_STYLE;
const feature=(kind,properties,geometry)=>({type:'Feature',properties:{kind,...properties},geometry});
// This is an analysis object inventory, not a copy of any renderer's live layers.
function build(input,{allObjects=false,includeElevatedRoutes=false}={}){
 const detail=input.context.kind==='detail',features=[],candidates=input.cases.map(c=>({...c.catalog}));
 for(const c of input.cases){
  const t=c.catalog;if(!t.available||(!allObjects&&!detail&&!t.visible))continue;
  const common={candidateId:t.candidateId,resultId:t.resultId,color:t.color,focused:t.focused},visible=detail||t.visible,cls=c.classification;
  if(!detail){
   c.ellipses.forEach((e,i)=>{if(!e)return;const level=S.bandLevels[i],localVisible=input.bands.includes(level),v=visible&&localVisible;if(v||allObjects)features.push(feature('contour',{...common,visible:v,localVisible,level,count:e.count,denominator:c.landed.length,definition:'全着地標本に対する経験被覆。平均の信頼区間ではない。'},e.geometry||{type:'Polygon',coordinates:[S.close(e.points.map(([lat,lon])=>[lon,lat]))]}));});
   for(const band of S.bands(c.ellipses)){const localVisible=t.focused&&input.bands.includes(band.level),v=visible&&localVisible;if(v||allObjects)features.push(feature('contour-band',{...common,visible:v,localVisible,level:band.level,lowerLevel:band.lowerLevel,fillOpacity:band.fillOpacity,upperContourCount:band.upperContourCount,lowerContourCount:band.lowerContourCount,denominator:c.landed.length,definition:`${band.lowerLevel*100}–${band.level*100}%輪郭間の区間。上下のcountは各輪郭内の累積被覆数であり、帯内の人数・確率値ではない。`},band.geometry));}
  }
  // Interference is represented by landed sample IDs, not an enclosing hull.
  const selected=detail?c.landed.filter(x=>input.context.selection.sampleIds.includes(x.id)):c.landed.filter(x=>cls.hits.includes(x.id));
  const showPoints=visible&&(detail||input.showHits);
  if(showPoints||allObjects)for(const x of selected){const hit=cls.hitDetails[x.id];features.push(feature('landing',{...common,visible:showPoints,localVisible:detail||input.showHits,sampleId:x.id,color:hit?.color||t.color,candidateColor:t.color,interference:!!hit,hitRegionIds:hit?.regionIds||[],levelId:hit?.levelId||null,levelName:hit?.levelName||null,selected:detail,definition:detail?'詳細で選択した着地ID':'全着地中の指定領域に干渉したID'},{type:'Point',coordinates:[x.lon,x.lat]}));}
  if(!detail&&c.landed.length)features.push(feature('mean-landing',{...common,visible,localVisible:true,definition:'全着地の平均位置'},{type:'Point',coordinates:[c.mean[1],c.mean[0]]}));
  features.push(feature('launch',{...common,visible,localVisible:true,color:'#183843'},{type:'Point',coordinates:[c.origin[1],c.origin[0]]}));
  for(const x of c.samples.filter(x=>x.status!=='landed'&&(!detail||input.context.selection.sampleIds.includes(x.id))))features.push(feature('stop',{...common,visible,localVisible:true,sampleId:x.id,color:'#26383e',definition:'着地未定義。非干渉着地とは別。'},{type:'Point',coordinates:[x.lon,x.lat]}));
  const routeVisible=visible&&t.focused;
  if(routeVisible||allObjects)for(const route of c.routes){if(route.points.length<2)continue;
   const props={...common,visible:routeVisible,localVisible:t.focused,phase:route.phase,color:route.color,definition:t.resultKind==='ensemble'?'固定集合の選択結果を同経過時刻・相ごとに平均した軌道。平均の一機が実在する意味ではない。':input.real?'保存実結果の相別軌道。地表へ投影した位置関係。':(detail?'選択群':'全着地群')+'の相別進行率を揃えた平均形状。実時間の一飛行ではない。'};
   features.push(feature('mean-route',props,{type:'LineString',coordinates:route.points.map(([lat,lon])=>[lon,lat])}));
   if(allObjects||(includeElevatedRoutes&&routeVisible)){
    const geometry={type:'LineString',coordinates:route.points.map(([lat,lon],i)=>[lon,lat,route.heights[i]*1000])};
    const flight={...props,altitudeMode:input.real?'absolute':'relativeToGround',definition:props.definition+' '+(input.real?'実結果の海抜高度 ASL。':S.heightAssumption)};
    features.push(feature('flight-route',flight,geometry));
    features.push(feature('route-curtain',{...flight,fillOpacity:S.curtainOpacity},geometry));
   }
  }
 }
 for(const z of input.zones){if(!z.visible&&!allObjects)continue;features.push(feature('region',{regionId:z.id,label:z.name,visible:z.visible,color:z.level.color,levelId:z.level.id,levelName:z.level.name,priority:z.level.priority,fillOpacity:S.zoneOpacity,zoneVersion:input.zoneVersion},{type:'MultiPolygon',coordinates:z.polygons.map(p=>p.map(S.close))}));}
 for(const s of input.supports??[{ring:input.support}])features.push(feature('support-boundary',{visible:true,color:'#526775',label:s.label,definition:input.supportDefinition},{type:'Polygon',coordinates:[S.close(s.ring)]}));
 return {candidates,features,artificial:!input.real};
}
root.BJP_SCENE_DOCUMENT={build};
})(typeof window==='undefined'?globalThis:window);

}
