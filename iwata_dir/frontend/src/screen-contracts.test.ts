import {describe,it,expect} from 'vitest';
import {sample,projectTabs,elapsedSliderValue} from './screens/forecast/projection';
import {install as installStyle} from './screens/shared/scene-style.js';
import {install as installScene} from './screens/forecast/scene-document.js';
import {install as installExport} from './screens/forecast/export390.js';
import {install as installFixture} from './screens/weather/fixture.js';
import {install as installSeason} from './screens/forecast/season-adapter.js';
import {resolveHover as hover2D} from './screens/shared/hover-labels.mjs';
import {resolveHover as hover3D} from '../scene3d/src/hover-labels.js';
import {validatePayload} from '../scene3d/src/protocol.js';
import {initialState,workspaceReducer} from './workspaceState';
import {realModeCopy} from './screens/forecast/controller.js';
import type {Candidate,Config,ResultEnvelope,Run} from './domain';
const config:Config={schema:'balloon.flight.config/1',launch:{latitude_deg:43,longitude_deg:141,altitude_m:100,time_utc:'2026-09-23T03:30:00Z'},ascent:{mode:'constant_speed',speed_m_s:5},burst:{mode:'altitude',altitude_m:30000},descent:{mode:'rated_speed',reference_speed_m_s:5}};
const envelope:ResultEnvelope={run_id:'fixed',trial_id:'fixed:0',n:1,weight:1,weather_snapshot:{id:'saved'},source_snapshot:{},result:{schema:'balloon.flight.result/1',config,status:'stopped',stop_reason:{code:'OUT_OF_BOUNDS',message:'edge'},events:[],records:[0,31.5,78.3].map((t,i)=>({elapsed_s:t,time_utc:'',latitude_deg:43+i*.01,longitude_deg:141+i*.01,altitude_m:100+t*5,phase:'ascent',eastward_wind_m_s:i===0?null:2,northward_wind_m_s:3,vertical_speed_m_s:5})),summary:{duration_s:78.3,maximum_altitude_m:491.5,landing:null}}};
const candidate:Candidate={id:'C-uuid',label:'条件',revision:3,weather_source_id:'saved',config};
const run:Run={run_id:'fixed',candidate_id:candidate.id,candidate_revision:2,result_available:true,weather_source_id:'saved',spec:{submitted_input:{config,weather_source_id:'saved'}}};
function scope(){const s:any={window:{},document:{}};installStyle(s);installScene(s);installExport(s);return s;}
describe('screen handoff preserves accepted results',()=>{
 it('keeps original-window meaning before selection and during restoration instead of calling an empty view n=1',()=>{
  const draft=realModeCopy(true,[]),restoring=realModeCopy(true,[{resultRead:{state:'loading'},result:null}]),loaded=realModeCopy(true,[{result:{kind:'ensemble',collection:{sampling:{mode:'historical_windows'}}}}]);
  expect(draft.notice).toBe(restoring.notice);expect(draft.notice).toBe(loaded.notice);expect(draft.notice).toContain('選んだ原日時');expect(draft.notice).toContain('多年を代表する季節確率ではなく');expect(draft.notice).not.toContain('機体感度');expect(draft.emptyLegend).toContain('まだ表示していません');expect(restoring.emptyLegend).toContain('復元後');expect(draft.emptyLegend+restoring.emptyLegend).not.toContain('n=1');
  expect(realModeCopy(false,[]).notice).toContain('仮の機体感度');expect(realModeCopy(false,[]).emptyLegend).toBe('n=1 · 分位域を表示しません');
 });
 it('keeps irregular elapsed times, missing wind, and absence of burst for a stop',()=>{const x=sample(envelope)[0];expect(x.history.map(p=>p.t)).toEqual([0,31.5/60,78.3/60]);expect(x.duration).toBe(78.3/60);expect(x.burst).toBeNull();expect(x.history[0].speed).toBeNull();expect(x.status).toBe('stopped');});
 it('compares drafts to submitted input while rendering the normalized fixed record',()=>{const normalized=structuredClone(envelope);normalized.result.config.launch.time_utc='2026-09-23T03:30:00+00:00';const tab=projectTabs([candidate],[run],{fixed:normalized},['fixed'],{codes:{'C-uuid':'候補1'},visibility:{'候補1':false}})[0];expect(tab.pending).toBe(false);expect(tab.visible).toBe(false);expect(tab.id).toBe('候補1');expect(tab.result?.conditions.realConfig.launch.time_utc).toContain('+00:00');});
 it('separates an unread saved result from a draft that still matches submitted input',()=>{
  for(const state of ['loading','missing','error'] as const){const tab=projectTabs([candidate],[run],{},['fixed'],{}, {fixed:{state}})[0];expect(tab.result).toBeNull();expect(tab.resultRead?.state).toBe(state);expect(tab.pending).toBe(false);}
 });
 it('retains known draft changes while its saved result is unread',()=>{
  const edited=structuredClone(candidate);edited.config.ascent.speed_m_s=7;
  const changedSource={...candidate,weather_source_id:'another-source'};
  const changedMode={...candidate,sampling:{schema:'draft'} as any};
  for(const c of [edited,changedSource,changedMode])for(const state of ['loading','missing','error'] as const){const tab=projectTabs([c],[run],{},['fixed'],{}, {fixed:{state}})[0];expect(tab.resultRead?.state).toBe(state);expect(tab.result).toBeNull();expect(tab.pending).toBe(true);}
 });
 it('keeps legacy revision fallback and genuinely uncomputed drafts distinct from read failures',()=>{
  const legacy={...run,candidate_revision:candidate.revision,spec:undefined};
  expect(projectTabs([candidate],[legacy],{},['fixed'])[0].pending).toBe(false);
  expect(projectTabs([{...candidate,revision:candidate.revision+1}],[legacy],{},['fixed'])[0].pending).toBe(true);
  const uncomputed=projectTabs([candidate],[],{},[])[0];expect(uncomputed.resultRead).toBeUndefined();expect(uncomputed.result).toBeNull();expect(uncomputed.pending).toBe(true);
 });
 it('does not reselect a deleted candidate when its old job completes',()=>{let state=initialState();state=workspaceReducer(state,{type:'project',project:{...state.project,candidates:[candidate]}});state=workspaceReducer(state,{type:'accepted',candidateId:candidate.id,run:{...run,state:'running'}});state=workspaceReducer(state,{type:'project',project:{...state.project,candidates:[]}});state=workspaceReducer(state,{type:'result',candidateId:candidate.id,epoch:0,intent:'complete',run,result:envelope});expect(state.project.candidates).toEqual([]);expect(state.project.compare_run_ids).toEqual([]);expect(state.results.fixed).toBeDefined();});
 it('hands a stopped selected record to 3D and exports its original ASL route',()=>{const s=scope(),point=sample(envelope)[0],catalog={candidateId:'A',resultId:'fixed',available:true,visible:true,focused:true,parentId:null,delayMinutes:0,label:'A',color:'#006f8b'};const context={kind:'detail',activeCandidateId:'A',selection:{sampleIds:[point.id],count:1,denominator:1},contours:'none'};const input={real:true,context,cases:[{catalog,samples:[point],landed:[],classification:{hits:[],hitDetails:{}},ellipses:[],mean:[null,null],origin:[43,141],routes:[{phase:'up',color:'#1472b9',points:[[43,141],[43.02,141.02]],heights:[.1,.4915]}]}],zones:[],bands:[],support:[[140,42],[142,42],[142,44],[140,44]]};const doc=s.window.BJP_SCENE_DOCUMENT.build(input);expect(()=>validatePayload({...doc,snapshotId:'s',collectionKey:'c',artificial:false,context,geojson:{type:'FeatureCollection',features:doc.features},camera:{center:[141,43],bounds:[140,42,142,44]}})).not.toThrow();const kml=s.window.BJP_EXPORT.output({...s.window.BJP_SCENE_DOCUMENT.build(input,{allObjects:true}),title:'実計算',description:'固定記録'});expect(kml).toContain('<altitudeMode>absolute</altitudeMode>');expect(kml).not.toContain('模式AGL');expect(kml).not.toContain('人工の操作模型');expect(kml).not.toContain('輪郭は50%');});
 it('runs the retained seasonal adapter against its explicitly scoped fixture',()=>{const s:any={window:{},document:{}};installFixture(s);installSeason(s);const r=s.window.SEASON_ADAPTER.evaluate({origin:[43.05,141.35],years:[2020,2020],validHours:[3],period:{grain:'month',index:6}});expect(r.samples.length).toBe(31);expect(r.samples[0].history.length).toBeGreaterThan(1);});
});


describe('retained fixture surface semantics',()=>{
 const square=(r:number)=>[[-r,-r],[-r,r],[r,r],[r,-r]];
 function payload(){const s=scope(),landed=Array.from({length:20},(_,i)=>({id:'S'+i,lat:0,lon:0,status:'landed'}));const doc=s.window.BJP_SCENE_DOCUMENT.build({context:{kind:'overview'},cases:[{catalog:{candidateId:'A',resultId:'r1',label:'A 標準案',focused:true,visible:true,available:true,color:'#08788b'},classification:{hits:[],hitDetails:{}},samples:landed,landed,ellipses:[1,2,3].map((r,i)=>({points:square(r),threshold:r,count:[10,18,19][i]})),mean:[0,0],origin:[0,0],routes:[]}],zones:[{id:'R1',name:s.window.BJP_STYLE.regionLabel('禁止域','禁止域'),visible:true,polygons:[[square(.8)]],level:{id:'normal',name:'指定領域',color:'#df2948',priority:1}}],bands:[.5,.9,.95],showHits:true,zoneVersion:1,support:square(4)});return {...doc,context:{kind:'overview'},geojson:{type:'FeatureCollection',features:doc.features}};}
 it('retains all three disjoint fill intervals and interior hover in 2D and 3D',()=>{const p=payload(),bands=p.geojson.features.filter((f:any)=>f.properties.kind==='contour-band');expect(bands.map((f:any)=>f.properties.level)).toEqual([.5,.9,.95]);expect(bands.map((f:any)=>f.geometry.coordinates.length)).toEqual([1,2,2]);for(const resolver of [hover2D,hover3D]){const labels=resolver(p,[.4,.4]).targets.map((x:any)=>x.text);expect(labels).toEqual(['落下分散：A 標準案','領域：禁止域 · 指定領域']);expect(resolver(p,[2.5,0]).targets.map((x:any)=>x.label)).toEqual(['A 標準案']);expect(resolver(p,[3.5,0]).targets).toEqual([]);}});
 it('does not name hidden surfaces or repeat one region through duplicated geometry',()=>{const p=payload(),region=p.geojson.features.find((f:any)=>f.properties.kind==='region');p.geojson.features.push(structuredClone(region));for(const resolver of [hover2D,hover3D]){expect(resolver(p,[.4,.4]).total).toBe(2);expect(resolver(p,[.4,.4],{bandsVisible:false}).targets.map((x:any)=>x.label)).toEqual(['禁止域']);expect(resolver(p,[.4,.4],{bandsVisible:false,regionsVisible:false,linesVisible:false}).targets).toEqual([]);}});
});


describe('display slider endpoint',()=>{
 it('excludes the last landed record despite range-input decimal shortening',()=>{
  const end=145.0498965416491;const displayed=Number('145.049896541649');
  expect(displayed<end).toBe(true);expect(elapsedSliderValue(displayed,end)<end).toBe(false);
  expect(elapsedSliderValue(end-1e-6,end)).toBe(end-1e-6);
  expect(elapsedSliderValue(0,end)).toBe(0);
 });
});
