import {describe,it,expect,vi,afterEach} from 'vitest';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
import * as C from 'cesium';
import {FLIGHT_ALPHA,CURTAIN_FLOOR_M,MAX_GROUND_NODES,groundNodes,groundKey,routeSections,routeDefinitions} from '../scene3d/src/route-geometry.js';
import {createRouteLayer} from '../scene3d/src/route-layer.js';
const nodes=[[141,43,100],[141.001,43,200],[141.002,43,150],[141.003,43,0]];
function displayRoute(coordinates=nodes,mode='absolute',index=0){
 return {properties:{kind:'flight-route',color:'#1472b9',altitudeMode:mode,candidateId:`candidate-${Math.floor(index/2)}`,phase:index%2?'down':'up'},geometry:{coordinates},index,nodes:coordinates,fillOpacity:.22};
}
describe('continuous curtains show vertical correspondence without terrain measurement',()=>{
 it('converts ASL and draws the entire curtain without ground samples or source mutation',()=>{
  const before=structuredClone(nodes),value=routeSections(nodes,'absolute',()=>35,new Map());
  expect(value.flight).toHaveLength(1);expect(value.flight[0].map((p:any)=>p[2])).toEqual([135,235,185,35]);
  expect(value.walls).toHaveLength(1);expect(value.walls[0].map((p:any)=>p.position)).toEqual(value.flight[0]);
  expect(value.walls[0].map((p:any)=>p.low)).toEqual(nodes.map(()=>CURTAIN_FLOOR_M));expect(nodes).toEqual(before);
 });
 it('does not clip or raise ASL paths at roofs, missing mesh, or negative terrain heights',()=>{
  const ground=new Map([[groundKey(nodes[0]),5000],[groundKey(nodes[1]),-100],[groundKey(nodes[3]),100]]);
  expect(routeSections(nodes,'absolute',()=>-35,ground)).toEqual(routeSections(nodes,'absolute',()=>-35,new Map()));
  expect(routeSections(nodes,'absolute',()=>-35,ground).flight[0].map((p:any)=>p[2])).toEqual([65,165,115,-35]);
 });
 it('keeps a route below the normal display floor without reversing its wall or changing altitude',()=>{
  const points=[[141,43,-13000],[141.01,43,-10]],before=structuredClone(points);
  const value=routeSections(points,'absolute',()=>-5,new Map());
  expect(value.flight[0].map((p:any)=>p[2])).toEqual([-13005,-15]);
  expect(value.walls[0].map((p:any)=>p.low)).toEqual([-14005,-14005]);expect(points).toEqual(before);
 });
 it('holds all real elevated geometry until the datum is available, even with complete mesh',()=>{
  const ground=new Map(nodes.map(p=>[groundKey(p),20]));
  expect(routeSections(nodes,'absolute',null,ground)).toEqual({flight:[],walls:[]});
  expect(routeDefinitions(C,[displayRoute()],null,ground).entities).toHaveLength(0);
 });
 it('holds an incomplete artificial AGL path and never adds the geoid offset to mesh heights',()=>{
  const points=[[141,43,-10],[141.01,43,10]],ground=new Map([[groundKey(points[0]),-30]]);
  expect(routeSections(points,'relativeToGround',()=>99,ground)).toEqual({flight:[],walls:[]});
  ground.set(groundKey(points[1]),-30);const value=routeSections(points,'relativeToGround',()=>99,ground);
  expect(value.flight[0].map((p:any)=>p[2])).toEqual([-40,-20]);expect(value.walls[0]).toHaveLength(2);
 });
 it('holds every artificial candidate and phase until all their display nodes are available',()=>{
  const routes=Array.from({length:4},(_,i)=>displayRoute(nodes.map(p=>[p[0]+i,p[1],p[2]]),'relativeToGround',i));
  const ground=new Map(routes.flatMap(r=>r.nodes).map(p=>[groundKey(p),20])),missing=groundKey(routes[3].nodes[3]);ground.delete(missing);
  const partial=routeDefinitions(C,routes,null,ground);expect(partial.entities).toHaveLength(0);expect(partial.counts.resolved).toBe(15);
  ground.set(missing,20);const ready=routeDefinitions(C,routes,null,ground);
  expect(ready.entities.filter(e=>e.polyline)).toHaveLength(4);expect(ready.entities.filter(e=>e.wall)).toHaveLength(4);
 });
 it('retains complete artificial paths only when densification stays within its ground-query limit',()=>{
  const route=displayRoute(nodes,'relativeToGround');route.nodes=[];
  const ground=new Map(nodes.map(p=>[groundKey(p),20]));
  expect(routeDefinitions(C,[route],null,ground).entities).toHaveLength(0);
 });
 it('subdivides the short date-line crossing and shares every upper vertex between line and wall',()=>{
  const original=[[179.999,0,0],[-179.999,0,100]],before=structuredClone(original),rows=groundNodes(original,100);
  expect(rows).toHaveLength(4);expect(rows.every(p=>Math.abs(p[0])>179.9)).toBe(true);expect(rows.at(-1)?.[2]).toBe(100);expect(original).toEqual(before);
  const route=displayRoute(original);route.nodes=rows;const d=routeDefinitions(C,[route],()=>30,new Map());
  expect(d.entities.find(e=>e.polyline)?.polyline?.positions).toEqual(d.entities.find(e=>e.wall)?.wall?.positions);
  expect(d.counts).toMatchObject({flightSegments:3,wallSegments:3,requiresGround:false});
  expect(()=>groundNodes([[0,0,0],[10,0,100]],10,100)).toThrow(RangeError);
 });
 it('preserves every original real vertex when a dense route exceeds the 4096-node sampling cap',()=>{
  const coordinates=Array.from({length:MAX_GROUND_NODES+1},(_,i)=>[141+i*.00001,43,100+i]),before=structuredClone(coordinates);
  expect(()=>groundNodes(coordinates)).toThrow(RangeError);const route=displayRoute(coordinates);route.nodes=[];
  const d=routeDefinitions(C,[route],()=>35,new Map()),line=d.entities.find(e=>e.polyline),wall=d.entities.find(e=>e.wall);
  expect(d.counts).toMatchObject({flightSegments:coordinates.length-1,wallSegments:coordinates.length-1,requiresGround:false});
  expect(line?.polyline?.positions).toEqual(wall?.wall?.positions);expect(wall?.wall?.maximumHeights).toEqual(coordinates.map(p=>p[2]+35));expect(coordinates).toEqual(before);
 });
 it('keeps sparse long-route wall tops aligned with the geodesic flight line after the node-cap fallback',()=>{
  const coordinates=[[0,0,500],[50,0,1000]];expect(()=>groundNodes(coordinates)).toThrow(RangeError);
  const route=displayRoute(coordinates);route.nodes=[];const d=routeDefinitions(C,[route],()=>0,new Map());
  const line=d.entities.find(e=>e.polyline)!.polyline!,wall=d.entities.find(e=>e.wall)!.wall!;
  const lineGeometry=C.PolylineGeometry.createGeometry(new C.PolylineGeometry({...line,vertexFormat:C.VertexFormat.POSITION_ONLY}));
  const wallGeometry=C.WallGeometry.createGeometry(new C.WallGeometry({...wall,vertexFormat:C.VertexFormat.POSITION_ONLY}));
  const positions=(geometry:any)=>Array.from({length:geometry.attributes.position.values.length/3},(_,i)=>C.Cartesian3.fromArray(geometry.attributes.position.values,i*3));
  const linePoints=positions(lineGeometry),upperPoints=positions(wallGeometry).filter(p=>C.Cartographic.fromCartesian(p).height>0);
  expect(upperPoints.length).toBeGreaterThan(coordinates.length);
  expect(Math.max(...upperPoints.map(p=>Math.min(...linePoints.map(q=>C.Cartesian3.distance(p,q)))))).toBeLessThan(.001);
 });
 it('fits the upper path and sea-level footprint without including the underground display floor',()=>{
  const d=routeDefinitions(C,[displayRoute()],()=>35,new Map()),heights=d.extent.map(p=>C.Cartographic.fromCartesian(p).height);
  expect(heights).toHaveLength(nodes.length*2);expect(Math.min(...heights)).toBeCloseTo(35,5);expect(Math.max(...heights)).toBeCloseTo(235,5);
  expect(heights.slice(nodes.length).every(h=>Math.abs(h-35)<1e-5)).toBe(true);
 });
 it('uses translucent, depth-tested lines and outline-free walls that do not write ground depth',()=>{
  const d=routeDefinitions(C,[displayRoute()],()=>0,new Map()),line=d.entities.find(e=>e.polyline),wall=d.entities.find(e=>e.wall);
  expect(C.Color.floatToByte(FLIGHT_ALPHA)).toBe(253);expect(C.Color.floatToByte(.999)).toBe(255);expect(line?.polyline?.clampToGround).toBe(false);expect(line?.polyline?.arcType).toBe(C.ArcType.GEODESIC);expect(wall?.wall?.outline).toBe(false);
  expect(wall?.wall?.minimumHeights).toEqual(nodes.map(()=>CURTAIN_FLOOR_M));
  // Material's uniform type check references browser constructors; no canvas or GPU is created.
  for(const name of ['HTMLCanvasElement','HTMLImageElement','ImageBitmap','OffscreenCanvas'])vi.stubGlobal(name,class {});
  for(const color of [line?.polyline?.material,wall?.wall?.material]){
   const appearance=new C.MaterialAppearance({material:C.Material.fromType('Color',{color})});
   expect(appearance.getRenderState()).toMatchObject({depthTest:{enabled:true},depthMask:false});
  }
  const host=readFileSync(new URL('../scene3d/src/main.js',import.meta.url),'utf8'),assignment=host.match(/viewer\.scene\.pickTranslucentDepth\s*=\s*[^;]+;/)?.[0];
  expect(assignment).toBeTruthy();const context={viewer:{scene:{pickTranslucentDepth:true}}};runInNewContext(assignment!,context);expect(context.viewer.scene.pickTranslucentDepth).toBe(false);
 });
});
afterEach(()=>{vi.useRealTimers();vi.unstubAllGlobals();});
function harness(){
 const states:any[]=[];let ready=true;
 const scene={requestRender:vi.fn(),sampleHeight:vi.fn(()=>10)};
 const viewer:any={scene,dataSources:new C.DataSourceCollection(),dataSourceDisplay:{ready:true},camera:{positionWC:C.Cartesian3.ZERO,directionWC:C.Cartesian3.UNIT_Z,upWC:C.Cartesian3.UNIT_Y,frustum:{computeCullingVolume:()=>({computeVisibility:()=>C.Intersect.INSIDE})}}};
 const session={read:async(fn:any,{signal}:any)=>{if(signal.aborted)throw new DOMException('abort','AbortError');return fn();},afterScreenPick:vi.fn()};
 const layer=createRouteLayer(C,viewer,{session,exclusions:()=>[],canSample:()=>ready,onState:(s:any)=>states.push(s)});
 const payload={geojson:{features:[{properties:{kind:'flight-route',phase:'up',candidateId:'a',resultId:'r',altitudeMode:'relativeToGround',color:'#1472b9'},geometry:{coordinates:nodes}}]}};
 return {layer,scene,states,payload,session,setReady:(v:boolean)=>ready=v};
}
describe('route layer owns finite queries and their cancellation',()=>{
 it('shows complete real routes without calling sampleHeight even when the current mesh is not ready',async()=>{
  vi.useFakeTimers();vi.stubGlobal('fetch',vi.fn(async()=>({ok:true,arrayBuffer:async()=>new ArrayBuffer(721*1440*2)})));
  const h=harness();h.payload.geojson.features[0].properties.altitudeMode='absolute';h.setReady(false);
  await h.layer.setPayload(h.payload);expect(h.layer.entities.filter((e:any)=>e.polyline)).toHaveLength(1);expect(h.layer.entities.filter((e:any)=>e.wall)).toHaveLength(1);
  h.layer.changed();h.layer.refresh();h.layer.moving();h.setReady(true);h.layer.ready();h.layer.visibility(false,false);h.layer.visibility(true,true);await vi.runAllTimersAsync();
  expect(h.scene.sampleHeight).not.toHaveBeenCalled();expect(h.session.afterScreenPick).not.toHaveBeenCalled();expect(vi.getTimerCount()).toBe(0);expect(h.states.at(-1).requiresGround).toBe(false);h.layer.destroy();
 });
 it('keeps a full real route and curtain when the display-node cap is exceeded',async()=>{
  vi.useFakeTimers();vi.stubGlobal('fetch',vi.fn(async()=>({ok:true,arrayBuffer:async()=>new ArrayBuffer(721*1440*2)})));
  const h=harness();h.payload.geojson.features[0].properties.altitudeMode='absolute';h.payload.geojson.features[0].geometry.coordinates=Array.from({length:MAX_GROUND_NODES+1},(_,i)=>[141+i*.00001,43,100+i]);
  await h.layer.setPayload(h.payload);await vi.runAllTimersAsync();
  expect(h.states.at(-1)).toMatchObject({nodeLimit:true,requiresGround:false,flightSegments:MAX_GROUND_NODES,wallSegments:MAX_GROUND_NODES});
  expect(h.layer.entities.filter((e:any)=>e.polyline)).toHaveLength(1);expect(h.layer.entities.filter((e:any)=>e.wall)).toHaveLength(1);expect(h.scene.sampleHeight).not.toHaveBeenCalled();h.layer.destroy();
 });
 it('performs one pass per request and retains acquired heights when mesh is unloaded',async()=>{
  vi.useFakeTimers();const h=harness();await h.layer.setPayload(h.payload);await vi.runAllTimersAsync();expect(h.scene.sampleHeight).toHaveBeenCalledTimes(4);expect(h.session.afterScreenPick).toHaveBeenCalledTimes(4);expect(h.states.at(-1).resolved).toBe(4);
  h.scene.sampleHeight.mockReturnValue(undefined as any);h.layer.changed();await vi.runAllTimersAsync();expect(h.scene.sampleHeight).toHaveBeenCalledTimes(8);expect(h.states.at(-1).resolved).toBe(4);h.layer.destroy();
 });
 it('cancels before sampling when hidden and resumes once shown; toggles the two line layers as a group',async()=>{
  vi.useFakeTimers();const h=harness();await h.layer.setPayload(h.payload);h.layer.visibility(false,true);await vi.runAllTimersAsync();expect(h.scene.sampleHeight).not.toHaveBeenCalled();h.layer.visibility(true,true);await vi.runAllTimersAsync();expect(h.scene.sampleHeight).toHaveBeenCalledTimes(4);h.layer.visibility(true,false);expect(h.layer.entities.filter((e:any)=>e.wall).every((e:any)=>!e.show)).toBe(true);expect(h.layer.entities.filter((e:any)=>e.polyline).every((e:any)=>e.show)).toBe(true);h.layer.destroy();
 });
 it('destroyed and superseded payloads cannot publish an old mesh pass',async()=>{
  vi.useFakeTimers();const h=harness();await h.layer.setPayload(h.payload);await h.layer.setPayload({geojson:{features:[]}});await vi.runAllTimersAsync();expect(h.scene.sampleHeight).not.toHaveBeenCalled();expect(h.layer.entities).toHaveLength(0);h.layer.destroy();
 });
 it('restores acquired ground and elevated geometry without resampling after a failed presentation',async()=>{
  vi.useFakeTimers();const h=harness();await h.layer.setPayload(h.payload);await vi.runAllTimersAsync();const old=h.layer.checkpoint(),count=h.layer.entities.length;
  await h.layer.setPayload({geojson:{features:[]}});h.setReady(false);h.layer.restore(old);expect(h.layer.entities).toHaveLength(count);expect(h.states.at(-1).resolved).toBe(4);await vi.runAllTimersAsync();expect(h.scene.sampleHeight).toHaveBeenCalledTimes(4);h.layer.destroy();
 });
 it('reaches later valid points even when the first budget window is entirely missing',async()=>{
  vi.useFakeTimers();const h=harness();h.payload.geojson.features[0].geometry.coordinates=Array.from({length:700},(_,i)=>[141+i*.0001,43,100]);let index=0;
  h.scene.sampleHeight.mockImplementation(()=>++index>512?20:undefined as any);
  await h.layer.setPayload(h.payload);await vi.runAllTimersAsync();expect(index).toBe(512);expect(h.states.at(-1).resolved).toBe(0);expect(h.layer.entities).toHaveLength(0);
  h.layer.refresh();await vi.runAllTimersAsync();expect(index).toBe(1024);expect(h.states.at(-1).resolved).toBe(512);expect(h.layer.entities).toHaveLength(0);
  h.layer.refresh();await vi.runAllTimersAsync();expect(h.states.at(-1).resolved).toBe(700);expect(h.layer.entities).toHaveLength(2);h.layer.destroy();
 });
 it('resumes a dirty job once a normal ready frame arrives without polling while not ready',async()=>{
  vi.useFakeTimers();const h=harness();h.setReady(false);await h.layer.setPayload(h.payload);await vi.runAllTimersAsync();expect(h.scene.sampleHeight).not.toHaveBeenCalled();expect(vi.getTimerCount()).toBe(0);
  h.setReady(true);h.layer.ready();await vi.runAllTimersAsync();expect(h.scene.sampleHeight).toHaveBeenCalledTimes(4);h.layer.destroy();
 });
});

// Execute the host's actual transaction functions with a deferred route layer.
// This tests their async boundary without a browser, GPU, or provider request.
function presentationHarness(){
 const source=readFileSync(new URL('../scene3d/src/main.js',import.meta.url),'utf8');
 const functions=source.slice(source.indexOf('async function installPresentation('),source.indexOf('async function recordRenderedGeometry('));
 let release!:()=>void,entered!:()=>void;
 const pending=new Promise<void>(resolve=>{release=resolve;}),waiting=new Promise<void>(resolve=>{entered=resolve;});
 const nodes=new Map<string,any>();
 const next={snapshotId:'new',geojson:{features:[]}},prior={snapshotId:'old',geojson:{features:[]}};
 const renderer={overlayEntities:()=>[],PRESENTATION_REVISION:'test'},catalog={catalogView:()=>({}),PRESENTATION_REVISION:'test'};
 const state:any={
  C:{},parent:{},window:{},structuredClone,
  $:(id:string)=>{if(!nodes.has(id))nodes.set(id,{checked:true,childNodes:[],replaceChildren:vi.fn(),textContent:''});return nodes.get(id);},
  document:{getElementById:()=>null},hover:{invalidate:vi.fn()},
  viewer:{scene:{requestRender:vi.fn()}},overlayStore:{items:[],prepare:async()=>({items:[]}),commit:vi.fn(),rollback:vi.fn(()=>true),discard:vi.fn()},
  routeLayer:{checkpoint:()=>({}),setPayload:vi.fn(()=>{entered();return pending;}),restore:vi.fn(),visibility:vi.fn()},
  payload:next,renderedPayload:prior,renderRevision:0,previousPresentation:null,presentationError:null,entityItems:[],intentPending:null,
  overlayModule:renderer,catalogModule:catalog,diag:{snapshot:{snapshotId:'old'},renderedSnapshotId:'old'},
  sendIntent:vi.fn(),visibilityFor:()=>true,updateSummary:vi.fn(),clearReadout:vi.fn(),receipt:()=>({featureCounts:{}}),recordRenderedGeometry:vi.fn(),
  updateViewMemoryUI:vi.fn(),updateCatalog:vi.fn(),applyVisibility:vi.fn(),status:vi.fn(),resetCamera:vi.fn(),
 };
 const host=runInNewContext(`${functions}\n({installPresentation,restorePreviousPresentation});`,state);
 return {state,host,next,prior,waiting,release,start:()=>host.installPresentation(next,renderer,catalog,null,true)};
}

describe('presentation waits for the current elevated route transaction',()=>{
 it('reports success and resets the camera only after the current route is ready',async()=>{
  const h=presentationHarness(),work=h.start();await h.waiting;
  expect(h.state.resetCamera).not.toHaveBeenCalled();h.release();expect(await work).toBe(true);
  expect(h.state.renderedPayload).toBe(h.next);expect(h.state.routeLayer.visibility).toHaveBeenCalledOnce();expect(h.state.resetCamera).toHaveBeenCalledOnce();
  expect(h.state.status).toHaveBeenLastCalledWith('同じ結果を表示：0表示要素。');
 });
 it('invalidates an in-flight install when rollback restores the previous presentation',async()=>{
  const h=presentationHarness(),work=h.start();await h.waiting;const revision=h.state.renderRevision;
  expect(h.host.restorePreviousPresentation()).toBe(true);expect(h.state.renderRevision).toBe(revision+1);
  h.release();expect(await work).toBe(false);expect(h.state.renderedPayload).toBe(h.prior);expect(h.state.routeLayer.restore).toHaveBeenCalledOnce();
  expect(h.state.routeLayer.visibility).not.toHaveBeenCalled();expect(h.state.resetCamera).not.toHaveBeenCalled();expect(h.state.presentationError).toBeTruthy();
  expect(h.state.status.mock.calls.some(([text]:[string])=>text.startsWith('同じ結果を表示：'))).toBe(false);
 });
 it('does not complete successfully when rendering fails without a rollback target',async()=>{
  const h=presentationHarness(),work=h.start();await h.waiting;h.state.previousPresentation=null;h.state.presentationError='render failed';
  expect(h.host.restorePreviousPresentation()).toBe(false);h.release();expect(await work).toBe(false);
  expect(h.state.routeLayer.visibility).not.toHaveBeenCalled();expect(h.state.resetCamera).not.toHaveBeenCalled();
 });
});
