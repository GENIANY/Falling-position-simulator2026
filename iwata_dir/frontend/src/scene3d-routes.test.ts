import {describe,it,expect} from 'vitest';
import {install as installStyle} from './screens/shared/scene-style.js';
import {install as installScene} from './screens/forecast/scene-document.js';
import {fixture} from '../scene3d/src/fixture.js';
import {receipt,SCHEMA,validatePayload} from '../scene3d/src/protocol.js';

const routeKinds=['mean-route','flight-route','route-curtain'];
function build(input:any,options={}){
 const scope:any={window:{},document:{}};installStyle(scope);installScene(scope);
 return scope.window.BJP_SCENE_DOCUMENT.build(input,options);
}
function candidate(id:string,visible:boolean,focused:boolean){
 const landed=[1,2].map(i=>({id:id+i,lat:35+i*.01,lon:139+i*.01,status:'landed'}));
 return {
  catalog:{candidateId:id,resultId:'result-'+id,available:true,visible,focused,parentId:null,delayMinutes:0,label:id,color:'#08788b'},
  samples:landed,landed,classification:{hits:[id+'1'],hitDetails:{}},
  ellipses:[.01,.02,.03].map((r,i)=>({points:[[35-r,139-r],[35-r,139+r],[35+r,139+r],[35+r,139-r]],threshold:r,count:[1,2,2][i]})),
  mean:[35.015,139.015],origin:[35,139],
  routes:[{phase:'up',color:'#1472b9',points:[[35,139],[35.01,139.02],[35.02,139.03]],heights:[-.02,1.25,2.25]},
   {phase:'down',color:'#c35915',points:[[35.02,139.03],[35.015,139.015]],heights:[2.25,.1]}],
 };
}
function input(){return {
 real:true,context:{kind:'overview'} as any,cases:[candidate('A',true,true),candidate('B',true,false),candidate('C',false,false)],
 zones:[],bands:[] as number[],showHits:false,support:[[138,34],[140,34],[140,36],[138,36]],
};}
function payload(source=input(),options={includeElevatedRoutes:true}){
 const doc=build(source,options);
 return {...doc,snapshotId:'snapshot-routes',collectionKey:'fixed-collection',context:source.context,
  geojson:{type:'FeatureCollection',features:doc.features},camera:{center:[139,35],bounds:[138,34,140,36]}};
}
function find(p:any,kind:string,phase='up'){return p.geojson.features.find((f:any)=>f.properties.kind===kind&&f.properties.phase===phase);}
function routes(doc:any){return doc.features.filter((f:any)=>routeKinds.includes(f.properties.kind));}

describe('visible analysis routes gain matching elevated geometry',()=>{
 it('adds only focused visible routes without restoring hidden candidates, points or disabled bands',()=>{
  const source=input(),plain=build(source),elevated=build(source,{includeElevatedRoutes:true});
  expect(elevated.features.filter((f:any)=>!['flight-route','route-curtain'].includes(f.properties.kind))).toEqual(plain.features);
  expect(routes(elevated).map((f:any)=>[f.properties.candidateId,f.properties.phase,f.properties.kind])).toEqual(
   ['up','down'].flatMap(phase=>routeKinds.map(kind=>['A',phase,kind])));
  expect(elevated.features.some((f:any)=>f.properties.candidateId==='C')).toBe(false);
  expect(elevated.features.some((f:any)=>['contour','contour-band','landing'].includes(f.properties.kind))).toBe(false);
  expect(()=>validatePayload(payload(source))).not.toThrow();
 });
 it('moves the whole route group with focus and does not revive a hidden focused candidate',()=>{
  const source=input();source.cases[0].catalog.focused=false;source.cases[1].catalog.focused=true;
  expect(new Set(routes(build(source,{includeElevatedRoutes:true})).map((f:any)=>f.properties.candidateId))).toEqual(new Set(['B']));
  source.cases[1].catalog.focused=false;source.cases[2].catalog.focused=true;
  expect(routes(build(source,{includeElevatedRoutes:true}))).toEqual([]);
 });
 it('keeps the existing allObjects export inventory independent of the 3D option',()=>{
  const doc=build(input(),{allObjects:true});
  expect(new Set(routes(doc).map((f:any)=>f.properties.candidateId))).toEqual(new Set(['A','B','C']));
  expect(doc.features.some((f:any)=>f.properties.kind==='contour-band'&&f.properties.visible===false)).toBe(true);
  expect(doc.features.find((f:any)=>f.properties.kind==='flight-route'&&f.properties.candidateId==='C').properties.visible).toBe(false);
 });
 it('preserves selected detail geometry while overview visibility is off',()=>{
  const source=input(),c=candidate('A',false,true);source.cases=[c];
  source.context={kind:'detail',activeCandidateId:'A',selection:{sampleIds:['A2'],count:1,denominator:2},contours:'none'};
  // The controller supplies the selected group's route, distinct from the overview route.
  c.routes=[{phase:'down',color:'#c35915',points:[[35.2,139.2],[35.02,139.02]],heights:[.9,.1]}];
  const p=payload(source);
  expect(routes(p).map((f:any)=>f.properties.kind)).toEqual(routeKinds);
  expect(find(p,'flight-route','down').geometry.coordinates).toEqual([[139.2,35.2,900],[139.02,35.02,100]]);
  expect(p.features.filter((f:any)=>f.properties.kind==='landing').map((f:any)=>f.properties.sampleId)).toEqual(['A2']);
  expect(p.features.some((f:any)=>['contour','contour-band'].includes(f.properties.kind))).toBe(false);
  expect(()=>validatePayload(p)).not.toThrow();
 });
 it('converts route km into real ASL meters, including negative ASL, without changing the source',()=>{
  const source=input(),before=structuredClone(source),p=payload(source);
  expect(find(p,'flight-route').geometry.coordinates).toEqual([[139,35,-20],[139.02,35.01,1250],[139.03,35.02,2250]]);
  expect(find(p,'flight-route').properties.altitudeMode).toBe('absolute');
  expect(find(p,'route-curtain').geometry).toEqual(find(p,'flight-route').geometry);
  expect(find(p,'route-curtain').properties.fillOpacity).toBe(.22);
  expect(source).toEqual(before);expect(()=>validatePayload(p)).not.toThrow();
 });
 it('labels artificial heights as schematic AGL and keeps the 2D-only v2 payload valid',()=>{
  const source=input();source.real=false;source.cases[0].routes[0].heights[0]=0;const p=payload(source);
  expect(find(p,'flight-route').properties.altitudeMode).toBe('relativeToGround');
  expect(find(p,'flight-route').properties.definition).toContain('模式表現');
  expect(()=>validatePayload(p)).not.toThrow();
  expect(()=>validatePayload(payload(input(),{includeElevatedRoutes:false}))).not.toThrow();
  expect(()=>validatePayload(fixture())).not.toThrow();
  expect(receipt(validatePayload(p)).featureCounts).toMatchObject({'mean-route':2,'flight-route':2,'route-curtain':2});
  expect(SCHEMA).toBe('bjp-scene3d-v2');
 });
});

describe('3D receiver rejects incompatible route geometry before rendering',()=>{
 it.each([-.01,1,.999,NaN,Infinity,-Infinity,undefined,null,'0.22'])('rejects curtain opacity %s that is invalid or can round to opaque byte alpha',fillOpacity=>{
  const p=payload();find(p,'route-curtain').properties.fillOpacity=fillOpacity;
  expect(()=>validatePayload(p)).toThrow(/幕の不透明度/);
 });
 it('accepts the transparent opacity range and preserves the default curtain opacity',()=>{
  const original=payload();expect(find(validatePayload(original),'route-curtain').properties.fillOpacity).toBe(.22);
  for(const fillOpacity of [0,.22,.99]){const p=payload();find(p,'route-curtain').properties.fillOpacity=fillOpacity;expect(()=>validatePayload(p)).not.toThrow();}
 });
 it('keeps curtain and paired-route switches separate from the retained geometry',()=>{
  const original=payload();expect(validatePayload(original).routeDisplay).toEqual({visible:true,curtain:true});
  expect(original.routeDisplay).toBeUndefined();
  for(const routeDisplay of [{visible:true,curtain:false},{visible:false,curtain:true},{visible:false,curtain:false}]){
   const validated=validatePayload({...original,routeDisplay});expect(validated.routeDisplay).toEqual(routeDisplay);
   expect(validated.geojson).toEqual(original.geojson);
  }
  for(const routeDisplay of [null,{visible:true},{visible:'false',curtain:true},{visible:true,curtain:0}]){
   expect(()=>validatePayload({...original,routeDisplay})).toThrow(/boolean/);
  }
 });
 it.each([
  ['missing height',[139,35]],['extra ordinate',[139,35,100,0]],['NaN height',[139,35,NaN]],
  ['infinite height',[139,35,Infinity]],['negative infinite height',[139,35,-Infinity]],
  ['string height',[139,35,'100']],['out-of-range longitude',[181,35,100]],['out-of-range latitude',[139,-91,100]],
 ])('rejects %s',(_name,coordinates)=>{
  const p=payload();find(p,'flight-route').geometry.coordinates[0]=coordinates;
  expect(()=>validatePayload(p)).toThrow(/有限/);
 });
 it.each(['flight-route','route-curtain'])('checks the altitude mode of %s against real or artificial provenance',kind=>{
  for(const artificial of [true,false]){
   const source=input();source.real=!artificial;const p=payload(source);
   find(p,kind).properties.altitudeMode=artificial?'absolute':'relativeToGround';
   expect(()=>validatePayload(p)).toThrow(/高度基準/);
  }
  const p=payload();delete find(p,kind).properties.altitudeMode;expect(()=>validatePayload(p)).toThrow(/高度基準/);
 });
 it.each(routeKinds)('requires the matching %s for every elevated group',kind=>{
  const p=payload();p.geojson.features=p.geojson.features.filter((f:any)=>!(f.properties.kind===kind&&f.properties.phase==='up'));
  expect(()=>validatePayload(p)).toThrow(/一組/);
 });
 it('rejects an extra or mismatched phase instead of connecting a different route',()=>{
  const p=payload();find(p,'flight-route').properties.phase='unpaired';expect(()=>validatePayload(p)).toThrow(/一組/);
  const duplicate=payload();duplicate.geojson.features.push(structuredClone(find(duplicate,'route-curtain')));expect(()=>validatePayload(duplicate)).toThrow(/一組/);
 });
 it('rejects ground/air point-count, position and ordering mismatches',()=>{
  for(const change of [(cs:number[][])=>cs.pop(),(cs:number[][])=>cs[1][0]+=.01,(cs:number[][])=>cs.reverse()]){
   const p=payload();change(find(p,'mean-route').geometry.coordinates);expect(()=>validatePayload(p)).toThrow(/地表線と空中線/);
  }
 });
 it('rejects curtain/air altitude, position and length mismatches',()=>{
  for(const change of [(cs:number[][])=>cs[1][2]+=1,(cs:number[][])=>cs[1][1]+=.01,(cs:number[][])=>cs.pop()]){
   const p=payload();
   // A receiver must also validate payloads whose geometries are separate objects.
   p.geojson=JSON.parse(JSON.stringify(p.geojson));change(find(p,'route-curtain').geometry.coordinates);
   expect(()=>validatePayload(p)).toThrow(/空中線と幕/);
  }
 });
 it('rejects result identity changes and newly hidden or unfocused candidates',()=>{
  const p=payload();find(p,'flight-route').properties.resultId='unrelated-result';expect(()=>validatePayload(p)).toThrow(/表示対象外/);
  for(const field of ['visible','focused'] as const){const changed=payload();changed.candidates[0][field]=false;expect(()=>validatePayload(changed)).toThrow();}
  const hiddenGround=payload();find(hiddenGround,'mean-route').properties.visible=false;expect(()=>validatePayload(hiddenGround)).toThrow(/非表示の地表経路/);
 });
});
