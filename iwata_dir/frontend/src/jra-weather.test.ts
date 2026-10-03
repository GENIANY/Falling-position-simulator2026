import {describe,it,expect} from 'vitest';
import {createElement} from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {readFileSync} from 'node:fs';
import {ConfigEditor} from './ConfigEditor';
import {WeatherPreparation} from './WeatherPreparation';
import {utcToJstInput,jstInputToUtc,jstLabel,utcLabel,draftInputsMatchRun,draftMatchesRun,weatherMatch,weatherIdentity,weatherSourceSummary,runWeatherSnapshot,stableString,supportAreas} from './domain';
import type {Config,Candidate,WeatherSource,Run,ResultEnvelope} from './domain';
import type {CaseResult,SamplingSpec} from './ensembleDomain';
import {projectTabs,conditions} from './screens/forecast/projection';
import {collectionInputsMatch,collectionMatches,collectionResult} from './screens/forecast/ensembleProjection';
import {sourceApplicationIssue} from './weatherAcquisition';
const config:Config={schema:'balloon.flight.config/1',launch:{latitude_deg:34.8129558713,longitude_deg:137.8125,altitude_m:300,time_utc:'2023-07-01T02:17:13Z'},ascent:{mode:'constant_speed',speed_m_s:5},burst:{mode:'altitude',altitude_m:30000},descent:{mode:'rated_speed',reference_speed_m_s:5},integration:{max_duration_s:14400}};
const source:WeatherSource={id:'jra3q-surface-fixture',kind:'saved_jra3q',label:'保存JRA-3Q解析例',sha256:'a'.repeat(64),schema:'balloon.weather.jra3q_surface/1',product:'jra3q.ncar.regular_gaussian.model_surface_analysis',time_kind:'analysis_valid_utc',run_utc:null,valid_times_utc:['2023-07-01T00:00:00Z','2023-07-01T06:00:00Z','2023-07-01T12:00:00Z'],bounds:{lat:[30,40],lon:[130,145],model_level:[1,100]},metadata:{reconstruction_policy:'native_horizontal_first_surface_v1',join_model_levels:{pressure_pa:1,temperature_k:1,specific_humidity_kg_kg:1,eastward_wind_m_s:2,northward_wind_m_s:2}},default_config:config};
const candidate:Candidate={id:'A',label:'予定',revision:2,weather_source_id:source.id,config};
const run:Run={run_id:'R',candidate_id:'A',candidate_revision:2,weather_source_id:source.id,spec:{submitted_input:{config,weather_source_id:source.id},weather_snapshot:source}};
const envelope:ResultEnvelope={run_id:'R',trial_id:'T',n:1,weight:1,weather_snapshot:source,source_snapshot:{},result:{schema:'balloon.flight.result/1',status:'stopped',config,records:[],events:[],stop_reason:{code:'LIMIT',message:'stop'},summary:{duration_s:0,maximum_altitude_m:null,landing:null}}};
const sampling:SamplingSpec={variable:'burst_altitude_m',unit:'m',distribution:{family:'uniform',low:28000,high:30000},reason:'仮幅',n:2,seed:17};
const collection:CaseResult={schema:'balloon.ensemble.case-result/1',ensemble_id:'E',snapshot_id:'S',case_id:'A',plan_id:'P',drawset_id:'D',epoch:1,candidate:{id:'A',revision:2,label:'予定'},sampling,submitted_config:config,resolved_base_config:config,weather_snapshot:source,source_snapshot:{},settled:true,all_requested_have_physical_result:false,counts:{planned:2,landed:0,stopped:0,failed:0,invalid_input:0,cancelled:2,queued:0,running:0,interrupted:0,unstarted:0},trials:[]};
describe('saved JRA seconds and source meaning',()=>{
 it('round-trips 13 seconds across the JST date boundary without changing the saved config',()=>{
  expect(utcToJstInput('2023-07-01T18:17:13Z')).toBe('2023-07-02T03:17:13');
  expect(jstInputToUtc('2023-07-02T03:17:13')).toBe('2023-07-01T18:17:13.000Z');
  expect(jstLabel(config.launch.time_utc)).toBe('2023-07-01 11:17:13 JST');
  expect(utcLabel(config.launch.time_utc)).toBe('2023-07-01 02:17:13 UTC');
  const saved=JSON.parse(JSON.stringify({candidates:[candidate],compare_run_ids:['R']}));
  expect(conditions(saved.candidates[0].config,source.id).time).toBe('11:17:13');
  expect(saved.candidates[0].config.launch.time_utc).toBe(config.launch.time_utc);
 });
 it('uses second-resolution input and states the JRA support without inventing pressure levels or forecast initialization',()=>{
  const html=renderToStaticMarkup(createElement(ConfigEditor,{candidate,sources:[source],onChange:()=>{}}));
  expect(html).toMatch(/type="datetime-local"[^>]*step="1"[^>]*value="2023-07-01T11:17:13"/);
  expect(html).toContain('使う保存気象');expect(html).toContain('モデル面 1–100');expect(html).toContain('地点を変えても高度は自動変更しません');expect(html).toContain('この地点・時刻のモデル地表を確認');
  const summary=weatherSourceSummary(source).join(' ');expect(summary).toContain('予報ではありません');expect(summary).not.toContain('予報初期時刻');expect(summary).toContain('暫定方式');expect(summary).toContain('3時刻');
 });
 it('puts saved sources and their application targets outside the GFS acquisition controls',()=>{
  const html=renderToStaticMarkup(createElement(WeatherPreparation,{candidates:[candidate],sources:[source],onState:()=>{},refreshSources:async()=>[source],apply:()=>{},add:()=>{},focusPreview:()=>{}}));
  const gfs=html.indexOf('class="gfs-acquisition"');expect(gfs).toBeGreaterThan(html.indexOf('気象を適用する候補'));expect(gfs).toBeGreaterThan(html.indexOf('保存JRA-3Q解析例'));expect(html).toContain('全ての有効時刻（UTC）');expect(html).not.toContain('初期時刻なし');
 });
 it('preserves 13 seconds in the actual retained controller delay rail, and keeps fixture minute formatting',()=>{
  const text=readFileSync(new URL('./screens/forecast/controller.js',import.meta.url),'utf8');
  const stamp=text.split('\n').find(l=>l.startsWith('const jstStamp='))!,shift=text.split('\n').find(l=>l.startsWith('function shiftLaunch('))!;
  const f=new Function(stamp+'\n'+shift+'\nreturn {jstStamp,shiftLaunch};')();
  expect(f.shiftLaunch({date:'2023-07-01',time:'23:17:13'},120)).toEqual({date:'2023-07-02',time:'01:17:13'});
  expect(f.shiftLaunch({date:'2023-07-01',time:'23:17'},120)).toEqual({date:'2023-07-02',time:'01:17'});
  expect(Number.isNaN(f.jstStamp({date:'2023-02-30',time:'11:17:13'}))).toBe(true);
 });
 it('does not send a saved JRA support failure to GFS acquisition planning',()=>{
  const late={...candidate,config:{...config,launch:{...config.launch,time_utc:'2023-07-01T11:00:00Z'}}};
  expect(sourceApplicationIssue(source,[late])).toContain('放球日時・最大時間または保存気象');expect(sourceApplicationIssue(source,[candidate])).toBeNull();
 });
});
describe('current weather observation stays separate from fixed result/input',()=>{
 it('detects same-ID byte or effective schema/policy changes and rejects legacy non-hashes as unverified',()=>{
  expect(weatherMatch({...source,sha256:source.sha256!.toUpperCase()},source).state).toBe('same');
  for(const changed of [{...source,sha256:'b'.repeat(64)},{...source,schema:'other'},{...source,product:'other'},{...source,metadata:{...source.metadata,reconstruction_policy:'other'}},{...source,metadata:{...source.metadata,join_model_levels:{temperature_k:2}}}])expect(weatherMatch(changed,source).state).toBe('changed');
  expect(weatherMatch({...source,sha256:'short'},{...source,sha256:'short'}).state).toBe('unverified');
  expect(weatherMatch(source,{id:source.id}).state).toBe('unverified');
  expect(weatherMatch(undefined,source).state).toBe('unavailable');
  expect(weatherMatch(source,{sha256:source.sha256}).state).toBe('unverified');
 });
 it('prefers the submitted run snapshot and reads older fixed envelopes without requiring a current source',()=>{
  const other={...envelope,weather_snapshot:{...source,sha256:'b'.repeat(64)}};
  expect(runWeatherSnapshot(run,other)).toBe(source);
  expect(runWeatherSnapshot({...run,spec:undefined},other)).toBe(other.weather_snapshot);
  const tab=projectTabs([candidate],[run],{R:envelope},['R'],{}, {},[])[0];
  expect(tab.result?.envelope).toBe(envelope);expect(tab.pending).toBe(false);expect(tab.weatherMatch?.state).toBe('unavailable');
 });
 it('re-observes changed catalog identity without marking unchanged input dirty or replacing fixed map support',()=>{
  const before=stableString({candidate,run,envelope}),changed={...source,sha256:'b'.repeat(64),bounds:{lat:[1,2],lon:[3,4]}};
  expect(draftMatchesRun(candidate,run,source,envelope)).toBe(true);expect(draftMatchesRun(candidate,run,changed,envelope)).toBe(false);expect(draftInputsMatchRun(candidate,run)).toBe(true);
  const a=projectTabs([candidate],[run],{R:envelope},['R'],{}, {},[source])[0],b=projectTabs([candidate],[run],{R:envelope},['R'],{}, {},[changed])[0];
  expect(a.weatherMatch?.state).toBe('same');expect(b.weatherMatch?.state).toBe('changed');expect(b.pending).toBe(false);expect(b.result?.envelope).toBe(envelope);
  expect(supportAreas([{visible:true,envelope}])[0].lat).toEqual([30,40]);expect(stableString({candidate,run,envelope})).toBe(before);
  expect(stableString([source.id,weatherIdentity(source)])).not.toBe(stableString([changed.id,weatherIdentity(changed)]));
 });
 it('applies the same content distinction to a fixed collection and preserves its old snapshot',()=>{
  const c={...candidate,sampling},old=stableString(collection);
  expect(collectionMatches(c,collection,source)).toBe(true);expect(collectionMatches(c,collection,{...source,sha256:'b'.repeat(64)})).toBe(false);
  expect(collectionInputsMatch(c,collection)).toBe(true);expect(collectionMatches(c,collection)).toBe(false);
  expect(collectionResult(collection,{}).collection.weather_snapshot).toBe(source);expect(stableString(collection)).toBe(old);
 });
 it('does not conflate unknown catalog identity with an unread result or a known changed input',()=>{
  const edited={...candidate,config:{...config,ascent:{mode:'constant_speed',speed_m_s:7}}};
  for(const c of [candidate,edited])for(const state of ['loading','error','missing'] as const){const t=projectTabs([c],[run],{},['R'],{}, {R:{state}},[])[0];expect(t.pending).toBe(c===edited);expect(t.resultRead?.state).toBe(state);expect(t.result).toBeNull();expect(t.weatherMatch?.state).toBe('unavailable');}
 });
});
