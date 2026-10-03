import {claimWriteLease,releaseWriteLease} from './writeLease';
import {beforeEach} from 'vitest';
beforeEach(async()=>{releaseWriteLease();vi.stubGlobal('navigator',{locks:{request:(_name:any,_options:any,callback:any)=>Promise.resolve(callback({name:'test-lock'}))}});await claimWriteLease();setServiceIdentity('test-instance');});
import {setServiceIdentity} from './serviceIdentity';
import {afterEach,describe,expect,it,vi} from 'vitest';
import {switchModel,applyCandidateWeather} from './modelDrafts';
import {acquisitionRequest,familyCandidates,sourceApplicationIssue,forecastValidTimes,boundsForCandidates,launchRegionIssue} from './weatherAcquisition';
import {api} from './api';
import type {Candidate,Config,Project,WeatherSource} from './domain';
const config:Config={schema:'balloon.flight.config/1',launch:{time_utc:'2026-09-29T01:17:00Z',latitude_deg:33.8,longitude_deg:135.4,altitude_m:100},ascent:{mode:'constant_speed',speed_m_s:6.2},burst:{mode:'altitude',altitude_m:31000},descent:{mode:'rated_speed',reference_speed_m_s:4.2,density_model:'weather',reference_density_kg_m3:1.19}};
const parent:Candidate={id:'parent',label:'親',revision:3,weather_source_id:'old',config};
const child:Candidate={...parent,id:'child',label:'延期',parent_id:'parent',delay_minutes:90,config:{...config,launch:{...config.launch,time_utc:'2026-09-29T02:47:00Z'}}};
const independent:Candidate={...parent,id:'independent'};
const form={inventoryId:'inventory',runUtc:'2026-09-29T00:00:00Z',fixedRun:'',latitude:33.8,longitude:135.4,halfWidth:50,halfHeight:70,maxMB:50,memoryMB:256,targetIds:['parent']};
describe('candidate model and acquired weather boundaries',()=>{
 it('binds edited locations without silently moving the chosen region',()=>{
  const first=acquisitionRequest(form,[parent]),moved={...parent,config:{...config,launch:{...config.launch,latitude_deg:43,longitude_deg:141.5}}};
  const next=acquisitionRequest(form,[moved]);expect(next.region).toEqual(first.region);expect(next.candidate_windows).not.toEqual(first.candidate_windows);
  expect(launchRegionIssue({west:135,east:136,south:33,north:35},[moved])).toContain('親');
 });
 it('fits every selected launch explicitly while keeping a separate trajectory-support boundary',()=>{
  const northern={...child,config:{...config,launch:{...config.launch,latitude_deg:43,longitude_deg:141.5}}};
  const points=[parent,northern],bounds=boundsForCandidates(points);expect(bounds).toEqual({west:135,east:141.75,south:33.5,north:43.25});expect(launchRegionIssue(bounds,points)).toBeNull();
  expect(acquisitionRequest({...form,bounds},points).region).toEqual({kind:'bounds',...bounds});
  const again={...northern,config:{...config,launch:{...config.launch,longitude_deg:145}}};expect(launchRegionIssue(bounds,[again])).toContain('延期');
 });
 it('refuses invalid and seam-spanning fits without changing the input candidates',()=>{
  const saved=structuredClone(parent);expect(()=>boundsForCandidates([{...parent,config:{...config,launch:{...config.launch,latitude_deg:NaN}}}])).toThrow();
  expect(()=>boundsForCandidates([parent,{...child,config:{...config,launch:{...config.launch,longitude_deg:-170}}}])).toThrow('継ぎ目');expect(parent).toEqual(saved);
 });
 it('restores both ascent alternatives without sending inactive parameters',()=>{
  const original=structuredClone(config);let {config:c,cache}=switchModel(config,{},'ascent','isothermal_buoyancy');c.ascent.gas_mass_kg=.63;
  ({config:c,cache}=switchModel(c,cache,'ascent','constant_speed'));expect(c.ascent).toEqual(original.ascent);
  ({config:c,cache}=switchModel(c,JSON.parse(JSON.stringify(cache)),'ascent','isothermal_buoyancy'));expect(c.ascent.gas_mass_kg).toBe(.63);expect(c.ascent).not.toHaveProperty('speed_m_s');expect(config).toEqual(original);
 });
 it('retains diameter, altitude, CdA and rated-speed values through saved caches',()=>{
  let {config:c,cache}=switchModel(config,{},'burst','diameter');c.burst.diameter_m=9.7;({config:c,cache}=switchModel(c,cache,'burst','altitude'));expect(c.burst.altitude_m).toBe(31000);({config:c,cache}=switchModel(c,cache,'burst','diameter'));expect(c.burst.diameter_m).toBe(9.7);
  ({config:c,cache}=switchModel(c,cache,'descent','constant_cda'));c.descent.drag_area_m2=.77;({config:c,cache}=switchModel(c,cache,'descent','rated_speed'));expect(c.descent.reference_speed_m_s).toBe(4.2);({config:c}=switchModel(c,cache,'descent','constant_cda'));expect(c.descent.drag_area_m2).toBe(.77);
 });
 it('preserves density-specific values and the shared rated speed',()=>{
  let {config:c,cache}=switchModel(config,{},'density','exponential');c.descent.scale_height_m=9000;c.descent.reference_speed_m_s=5.3;
  ({config:c,cache}=switchModel(c,cache,'density','weather'));expect(c.descent.reference_density_kg_m3).toBe(1.19);expect(c.descent.reference_speed_m_s).toBe(5.3);expect(c.descent).not.toHaveProperty('scale_height_m');
  ({config:c}=switchModel(c,cache,'density','exponential'));expect(c.descent.scale_height_m).toBe(9000);
 });
 it('applies weather to a family without rewriting physical drafts, fixed comparison, or another candidate',()=>{
  const project:Project={schema:'balloon.project/1',title:'p',candidates:[parent,child,independent],compare_run_ids:['fixed-old'],ui_state:{forecast_real:{metric:'vertical'}}};const original=structuredClone(project);
  const result=applyCandidateWeather(project,['child'],'new-source');expect(result.candidates.slice(0,2).map(c=>c.weather_source_id)).toEqual(['new-source','new-source']);expect(result.candidates[2]).toBe(independent);expect(result.candidates[0].config).toBe(config);expect(result.compare_run_ids).toEqual(['fixed-old']);expect(result.ui_state).toBe(project.ui_state);expect(project).toEqual(original);
 });
 it('plans every selected family flight window including the latest delay and default duration',()=>{
  const c={...child,config:{...child.config,integration:{max_duration_s:18000}}};expect(familyCandidates([parent,c,independent],['parent']).map(c=>c.id)).toEqual(['parent','child']);
  const request=acquisitionRequest(form,[parent,c,independent]);expect(request.candidate_windows).toEqual([{candidate_id:'parent',launch_time_utc:config.launch.time_utc,latitude_deg:33.8,longitude_deg:135.4,max_duration_s:14400},{candidate_id:'child',launch_time_utc:c.config.launch.time_utc,latitude_deg:33.8,longitude_deg:135.4,max_duration_s:18000}]);expect(request.region).toMatchObject({kind:'center',half_height_km:70});
 });
 it('shows actual valid samples around a non-hour launch separately from requested times',()=>{
  expect(forecastValidTimes({normalized_request:{run_utc:'2026-09-29T00:00:00Z',lead_hours:[1,2,3,4,5,6],start_utc:'2026-09-29T01:17:00Z',end_utc:'2026-09-29T05:17:00Z',bounds:{west:135,east:136,south:33,north:34}}})).toEqual([1,2,3,4,5,6].map(h=>`2026-09-29T0${h}:00:00.000Z`));
  expect(familyCandidates([parent,child,independent],['child']).map(c=>c.id)).toEqual(['parent','child']);
 });
 it('rejects incomplete inputs rather than sending zero or a shortened window',()=>{
  expect(()=>acquisitionRequest({...form,halfWidth:NaN},[parent])).toThrow();expect(()=>acquisitionRequest(form,[{...parent,config:{...config,integration:{max_duration_s:NaN}}}])).toThrow();expect(()=>acquisitionRequest({...form,targetIds:['deleted']},[parent])).toThrow();
 });
 it('checks current support with equivalent longitudes and finite coordinates',()=>{
  const source:WeatherSource={id:'weather',default_config:null,valid_times_utc:['2026-09-29T00:00:00Z','2026-09-29T10:00:00Z'],bounds:{lat:[33,35],lon:[339,341],pressure_pa:[500,100000]}};
  const c={...parent,config:{...config,launch:{...config.launch,longitude_deg:-20}}};expect(sourceApplicationIssue(source,[c])).toBeNull();expect(sourceApplicationIssue(source,[{...c,config:{...c.config,launch:{...c.config.launch,latitude_deg:NaN}}}])).toContain('数値');expect(sourceApplicationIssue({...source,valid_times_utc:source.valid_times_utc?.slice(0,1)},[c])).toContain('時間支持');
 });
 it('rechecks edited launch windows before application',()=>{
  const source:WeatherSource={id:'weather',default_config:null,valid_times_utc:['2026-09-29T00:00:00Z','2026-09-29T06:00:00Z'],bounds:{lat:[33,35],lon:[135,136],pressure_pa:[500,100000]}};expect(sourceApplicationIssue(source,[parent])).toBeNull();expect(sourceApplicationIssue(source,[child])).toContain('時間支持外');
 });
});
afterEach(()=>vi.unstubAllGlobals());
describe('weather API transport is explicit',()=>{
 it('does not fetch on import; posts exact inventory, plan and idempotent acquisition bodies',async()=>{
  const fetch=vi.fn().mockResolvedValue({ok:true,status:200,json:async()=>({})});vi.stubGlobal('fetch',fetch);expect(fetch).not.toHaveBeenCalled();
  await api.refreshInventory({run_utc:form.runUtc});const request=acquisitionRequest(form,[parent]);await api.weatherPlan(request);await api.acquireWeather('plan','same-id');await api.acquireWeather('plan','same-id');
  expect(fetch.mock.calls.map(a=>a[0])).toEqual(['/api/v1/weather-inventories/refresh','/api/v1/weather-plans','/api/v1/weather-acquisitions','/api/v1/weather-acquisitions']);expect(JSON.parse(fetch.mock.calls[1][1].body)).toEqual(request);expect(fetch.mock.calls[2][1].body).toBe(fetch.mock.calls[3][1].body);
 });
 it('keeps polling GET separate from explicit cancellation and retry POST',async()=>{
  const fetch=vi.fn().mockResolvedValue({ok:true,status:200,json:async()=>({})});vi.stubGlobal('fetch',fetch);await api.acquisition('job');await api.cancelAcquisition('job');await api.retryAcquisition('job');
  expect(fetch.mock.calls.map(a=>[a[0],a[1].method??'GET'])).toEqual([['/api/v1/weather-acquisitions/job','GET'],['/api/v1/weather-acquisitions/job/cancel','POST'],['/api/v1/weather-acquisitions/job/retry','POST']]);
 });
});
