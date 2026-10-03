// Derived from the archived 0.40.1 r2 screen; see frontend/SCREEN_PROVENANCE.md.
export function install(scope) {
const {window,document}=scope;
(function(root){
'use strict';
const S=root.BJP_STYLE,xml=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
const names={'contour':'輪郭','contour-band':'輪郭間の帯','landing':'干渉した着地','mean-landing':'平均着地点','launch':'放球点','stop':'停止（着地未定義）','mean-route':'平均形状・地表線','flight-route':'平均形状・立体線（模式AGL）','route-curtain':'地表への投影面（模式）','region':'指定領域','support-boundary':'気象の支持境界'};
function icon(kind,color){const shape=kind==='stop'?`<path d="M7 7L25 25M25 7L7 25" stroke="white" stroke-width="7"/><path d="M7 7L25 25M25 7L7 25" stroke="${color}" stroke-width="3"/>`:`<circle cx="16" cy="16" r="10" fill="${kind==='mean-landing'?'white':color}" stroke="${kind==='mean-landing'?color:'white'}" stroke-width="3"/>`;return 'data:image/svg+xml,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32">${shape}</svg>`);}
function coordinates(ps){return ps.map(p=>p.join(',')).join(' ');}
function geometry(g,p){const mode=p.altitudeMode||'clampToGround';if(g.type==='Point')return `<Point><altitudeMode>${mode}</altitudeMode><coordinates>${coordinates([g.coordinates])}</coordinates></Point>`;
 if(g.type==='LineString')return `<LineString><extrude>${p.kind==='route-curtain'?1:0}</extrude><tessellate>${mode==='clampToGround'?1:0}</tessellate><altitudeMode>${mode}</altitudeMode><coordinates>${coordinates(g.coordinates)}</coordinates></LineString>`;
 const polys=g.type==='Polygon'?[g.coordinates]:g.coordinates;return '<MultiGeometry>'+polys.map(poly=>'<Polygon><altitudeMode>clampToGround</altitudeMode>'+poly.map((ring,i)=>`<${i?'inner':'outer'}BoundaryIs><LinearRing><coordinates>${coordinates(S.close(ring))}</coordinates></LinearRing></${i?'inner':'outer'}BoundaryIs>`).join('')+'</Polygon>').join('')+'</MultiGeometry>';
}
function output(document){const styles=new Map();
 function placemark(f){const p=f.properties,isFill=['contour-band','region','route-curtain'].includes(p.kind),isPoint=f.geometry.type==='Point',color=S.hex(p.color||'#526775'),fill=isFill?(p.fillOpacity??.12):0,contourIndex=S.bandLevels.indexOf(p.level),width=p.kind==='contour'?(p.focused?[3.2,2.4,1.6]:[2,1.5,1])[contourIndex]:p.kind==='mean-route'||p.kind==='flight-route'?2.5:p.kind==='route-curtain'?0:2;
  const key=JSON.stringify([color,fill,width,isPoint,p.kind]);if(!styles.has(key)){const id='style-'+(styles.size+1);styles.set(key,{id,xml:`<Style id="${id}"><LineStyle><color>${S.kmlColor(color,p.kind==='route-curtain'?0:1)}</color><width>${width}</width></LineStyle><PolyStyle><color>${S.kmlColor(color,fill)}</color><fill>${isFill?1:0}</fill><outline>${p.kind==='contour-band'?0:1}</outline></PolyStyle>${isPoint?`<IconStyle><color>ffffffff</color><scale>${p.kind==='mean-landing'?.8:.55}</scale><Icon><href>${xml(icon(p.kind,color))}</href></Icon><hotSpot x="0.5" y="0.5" xunits="fraction" yunits="fraction"/></IconStyle><LabelStyle><scale>0</scale></LabelStyle>`:''}</Style>`});}
  const label=p.label||`${p.candidateId||''} ${(document.artificial===false?({'mean-route':'固定結果の相別経路・地表投影','flight-route':'固定結果の相別経路（海抜高度 ASL）','route-curtain':'固定結果の相別経路から地表への投影面'}[p.kind]||names[p.kind]):names[p.kind])||p.kind}${p.level?' '+p.level*100+'%':''}${p.phase?' '+(p.phase==='up'?'上昇':'下降'):''}${p.sampleId?' '+p.sampleId:''}`;
  const data=Object.entries(p).filter(([,v])=>v!==undefined&&v!==null).map(([k,v])=>`<Data name="${xml(k)}"><value>${xml(typeof v==='object'?JSON.stringify(v):v)}</value></Data>`).join('');
  return `<Placemark><name>${xml(label)}</name><visibility>${(p.localVisible??p.visible)===false?0:1}</visibility><description>${xml(p.definition||p.levelName||(document.artificial===false?'保存された固定実結果の描画':'人工の操作模型'))}</description><styleUrl>#${styles.get(key).id}</styleUrl><ExtendedData>${data}</ExtendedData>${geometry(f.geometry,p)}</Placemark>`;
 }
 const folder=(name,body,visibility=1)=>`<Folder><name>${xml(name)}</name><visibility>${visibility}</visibility>${body}</Folder>`;
 let body='';const candidates=document.candidates||[];
 const candidateBody=c=>{const objects=document.features.filter(f=>f.properties.candidateId===c.candidateId);return folder(c.label+' / '+(c.resultId||'未計算'),`<description>${xml((c.conditions||'')+(c.fixedConditions?.length?'\n'+c.fixedConditions.map(f=>f.label+': '+f.value).join('\n'):'')+(c.probabilityDefinition?'\n'+c.probabilityDefinition:''))}${c.pending?' / 入力未反映・変更前の結果':''}</description>`+objects.map(placemark).join(''),c.visible?1:0);};
 for(const c of candidates.filter(c=>!c.parentId))body+=folder(c.candidateId+' 系列',candidateBody(c)+candidates.filter(x=>x.parentId===c.candidateId).map(candidateBody).join(''));
 // Preserve any catalog row whose parent is absent without inventing a new relation.
 for(const c of candidates.filter(c=>c.parentId&&!candidates.some(x=>x.candidateId===c.parentId)))body+=candidateBody(c);
 body+=folder('指定領域',document.features.filter(f=>f.properties.kind==='region').map(placemark).join(''));
 body+=document.features.filter(f=>!f.properties.candidateId&&f.properties.kind!=='region').map(placemark).join('');
 return '<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Document><name>'+xml(document.title||'分析地図・人工模型')+'</name><description>'+xml((document.description||'人工結果。初期表示は保存時の設定。KMLのチェックはアプリの注目変更・再集計ではありません。')+(document.features.some(f=>f.properties.kind==='contour')?' 輪郭は50%太線・90%中線・95%細線（画面の破線の代替）。':''))+'</description>'+[...styles.values()].map(s=>s.xml).join('')+body+'</Document></kml>';
}
root.BJP_EXPORT={output,geometry};
})(typeof window==='undefined'?globalThis:window);

}
