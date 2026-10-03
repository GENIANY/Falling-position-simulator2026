import {describe,it,expect,vi,afterEach} from 'vitest';
const {h,mount}=vi.hoisted(()=>({h:{current:null as any},mount:vi.fn()}));
vi.mock('react',()=>({useRef:(v:any)=>h.current.ref(v),useState:(v:any)=>h.current.state(v),useEffect:(f:any,d:any[])=>h.current.effect(f,d),useMemo:(f:any,d:any[])=>h.current.memo(f,d)}));
vi.mock('./screens/forecast/runtime',()=>({mountForecast:mount}));
import {ForecastScreen} from './screens/ForecastScreen';
function harness(fn:()=>any){
 let cursor=0;const slots:any[]=[],effects:any[]=[],cleanups:any[]=[];
 const owner={ref:(v:any)=>{const i=cursor++;return slots[i]??(slots[i]={current:v});},state:(v:any)=>{const i=cursor++;if(!(i in slots))slots[i]=typeof v==='function'?v():v;return [slots[i],(n:any)=>{slots[i]=typeof n==='function'?n(slots[i]):n;}];},memo:(f:any,d:any[])=>{const i=cursor++;if(!slots[i]||d.some((v,j)=>!Object.is(v,slots[i].d[j])))slots[i]={d,v:f()};return slots[i].v;},effect:(f:any,d:any[])=>{const i=cursor++;if(!slots[i]||d.some((v,j)=>!Object.is(v,slots[i][j]))){slots[i]=d;effects.push(()=>{cleanups[i]?.();cleanups[i]=f();});}}};
 return {render:()=>{cursor=0;h.current=owner;const r=fn();effects.splice(0).forEach(f=>f());return r;},unmount:()=>cleanups.forEach(f=>f?.())};
}
afterEach(()=>vi.unstubAllGlobals());
describe('current source refresh reaches the retained forecast controller',()=>{
 it('rechecks both fixed n1 and fixed collection on catalog-only change while preserving selection and results',()=>{
  vi.stubGlobal('location',{origin:'http://local.invalid',protocol:'http:'});
  const source={id:'w',sha256:'a'.repeat(64),bounds:{lat:[30,40],lon:[130,145]},default_config:null};
  const config={launch:{time_utc:'2023-07-01T02:17:13Z',latitude_deg:35,longitude_deg:137,altitude_m:300},ascent:{mode:'constant_speed',speed_m_s:5},burst:{mode:'altitude',altitude_m:30000},descent:{mode:'rated_speed',reference_speed_m_s:5}};
  const sampling={variable:'burst_altitude_m',unit:'m',distribution:{family:'uniform',low:28000,high:30000},reason:'仮幅',n:2,seed:17};
  const candidates=[{id:'A',label:'n1',revision:1,weather_source_id:'w',config},{id:'B',label:'集合',revision:1,weather_source_id:'w',config,sampling}];
  const run={run_id:'r',candidate_id:'A',candidate_revision:1,spec:{submitted_input:{config,weather_source_id:'w'},weather_snapshot:source}};
  const env={run_id:'r',trial_id:'t',n:1,weather_snapshot:source,result:{config,status:'stopped',records:[],events:[]}};
  const value={snapshot_id:'S',case_id:'B',ensemble_id:'E',candidate:{id:'B'},submitted_config:config,sampling,weather_snapshot:source,trials:[]};
  const project={candidates,compare_run_ids:['r'],compare_results:[{kind:'single_run',run_id:'r'},{kind:'ensemble_case',ensemble_id:'E',snapshot_id:'S',case_id:'B'}]};
  const workspace:any={project,runs:[run],results:{r:env},sources:[source],resultReads:{},pending:{},ensemble:{cases:{'S:B':value},histories:{},analyses:{},caseReads:{}}};
  const rt:any={state:{active:'A',tabs:[],groups:[],detail:false},sync:vi.fn((tabs:any[])=>{rt.state.tabs=tabs;}),dispose:vi.fn()};mount.mockReturnValue(rt);
  const onView=vi.fn(),props:any={workspace,mode:'real',saved:{},proposal:null,onView,action:vi.fn()};
  const x=harness(()=>ForecastScreen(props));x.render();x.render();
  expect(rt.state.tabs.map((t:any)=>t.weatherMatch.state)).toEqual(['same','same']);
  const calls=rt.sync.mock.calls.length;
  workspace.sources=[{...source,sha256:'b'.repeat(64),bounds:{lat:[1,2],lon:[3,4]}}];x.render();
  expect(rt.sync.mock.calls.length).toBe(calls+1);expect(rt.state.tabs.map((t:any)=>t.weatherMatch.state)).toEqual(['changed','changed']);expect(rt.state.tabs.every((t:any)=>!t.pending)).toBe(true);
  expect(rt.state.tabs[0].result.envelope).toBe(env);expect(rt.state.tabs[1].result.collection).toBe(value);
  const bridge=mount.mock.calls.at(-1)![1];rt.state.tabs.forEach((t:any)=>t.visible=true);expect(bridge.supports()).toEqual([{label:'w',bounds:[[30,130],[40,145]]}]);
  workspace.sources=[];x.render();expect(rt.state.tabs.map((t:any)=>t.weatherMatch.state)).toEqual(['unavailable','unavailable']);expect(workspace.project).toBe(project);expect(onView).not.toHaveBeenCalled();
  x.unmount();expect(rt.dispose).toHaveBeenCalledOnce();
 });
});
