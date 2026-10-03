import {install as installStyle} from '../shared/scene-style.js';
import {install as installExport} from './export390.js';
import {describe,expect,it} from 'vitest';
import {figureReadIssue,fixedConditionSummary,fixedConditionFields} from './exportContext';
const config={launch:{time_utc:'2026-09-30T01:17:13Z',latitude_deg:43.1,longitude_deg:141.2,altitude_m:120},ascent:{mode:'constant_speed',speed_m_s:5},burst:{mode:'altitude',altitude_m:30000},descent:{mode:'rated_speed',reference_speed_m_s:5,density_model:'weather',reference_density_kg_m3:1.225}};
describe('portable fixed figures',()=>{
 it('retains shared actual conditions and fixed forecast identity for a single result',()=>{
  const value=fixedConditionSummary([{result:{conditions:{realConfig:config,weatherId:'w'},envelope:{weather_snapshot:{id:'w',run_utc:'2026-09-30T00:00:00Z',sha256:'abc',valid_times_utc:['a','b']}}}}]);const text=JSON.stringify(value);expect(text).toContain('01:17:13Z');expect(text).toContain('43.1');expect(text).toContain('30000');expect(text).toContain('00:00:00Z');expect(text).toContain('abc');expect(value.different).toEqual([]);
 });
 it('blocks a wind figure while one still-flying selected history is missing, but not the server aggregate',()=>{
  const t:any={renderAnalysis:{history:{}},result:{kind:'ensemble',collection:{trials:[{trial_id:'a',state:'landed',result_available:true,landing:{elapsed_s:1200}},{trial_id:'b',state:'landed',result_available:true,landing:{elapsed_s:1800}}]},realSamples:[{id:'a',historyLoaded:true,history:[{}]},{id:'b',historyLoaded:false,history:[]}]}};
  expect(figureReadIssue('roseChart',[t],['a','b'],10)).toContain('1件');expect(figureReadIssue('historyChart',[t],['a','b'],10)).toBeNull();expect(figureReadIssue('roseChart',[t],['a','b'],30)).toBeNull();t.renderAnalysis.history.unavailable_reason='limit';expect(figureReadIssue('historyChart',[t],['a','b'],10)).toContain('上限');
 });
 it('does not label explicit historical windows as equipment draws or one fixed forecast',()=>{
  const text=JSON.stringify(fixedConditionSummary([{result:{conditions:{realConfig:config},collection:{sampling:{mode:'historical_windows',n:3,reason:'選択理由'}}}}]));expect(text).toContain('原日時');expect(text).toContain('季節代表性未評価');expect(text).not.toContain('一様');expect(text).not.toContain('01:17:13Z');
 });
});


it('carries actual fixed inputs and their empirical meaning in the portable map',()=>{
 const scope:any={window:{},document:{}};installStyle(scope);installExport(scope);const fixedConditions=fixedConditionFields({conditions:{realConfig:config},envelope:{weather_snapshot:{id:'fixed-w',run_utc:'2026-09-30T00:00:00Z'}}});
 const kml=scope.window.BJP_EXPORT.output({artificial:false,title:'Fixed map',description:'Saved result',features:[],candidates:[{candidateId:'A',label:'A',resultId:'fixed-result',visible:true,conditions:'fixed',fixedConditions,probabilityDefinition:'n=1。分位域は定義しない。'}]});expect(kml).toContain('43.1');expect(kml).toContain('01:17:13Z');expect(kml).toContain('30000');expect(kml).toContain('fixed-w');expect(kml).toContain('分位域は定義しない');
});
