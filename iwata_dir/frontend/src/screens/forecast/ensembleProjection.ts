import type {Candidate,ResultEnvelope,WeatherSource} from '../../domain';
import {stableString,weatherMatch} from '../../domain';
import type {CaseResult,EnsembleAnalysis,Geometry} from '../../ensembleDomain';
import {conditions,sample} from './projection';
import {historicalMatches} from '../../historicalDomain';
export function geometryPoints(g:Geometry|null):number[][]{if(!g)return [];if(g.type==='Point')return [[g.coordinates[1],g.coordinates[0]]];if(g.type==='LineString')return g.coordinates.map(([lon,lat])=>[lat,lon]);return g.coordinates[0].map(([lon,lat])=>[lat,lon]);}
export function empiricalContours(analysis?:EnsembleAnalysis){return [.5,.9,.95].map(p=>{const b=analysis?.landing.bands.find(b=>b.probability===p);if(!b?.geometry)return null;return {...b,p,geometry:b.geometry,points:geometryPoints(b.geometry),threshold:b.threshold,count:b.count,n:b.total,actualCoverage:b.total?b.count/b.total:0};});}
export function analysisRoutes(analysis?:EnsembleAnalysis){return (['ascent','descent'] as const).flatMap(phase=>{const rows=analysis?.history.phases[phase]??[];const valid=rows.filter(r=>[r.metrics.latitude_deg?.mean,r.metrics.longitude_deg?.mean,r.metrics.altitude_m?.mean].every(v=>typeof v==='number'&&Number.isFinite(v)));return valid.length?[{phase:phase==='ascent'?'up':'down',points:valid.map(r=>[r.metrics.latitude_deg.mean!,r.metrics.longitude_deg.mean!]),heights:valid.map(r=>r.metrics.altitude_m.mean!/1000),elapsed_s:valid.map(r=>r.elapsed_s),color:phase==='ascent'?'#1472b9':'#c35915'}]:[];});}
/** Compact positions, full trial ledger and lazy histories remain distinct. */
export function collectionResult(value:CaseResult,histories:Record<string,ResultEnvelope>,analysis?:EnsembleAnalysis){
 const spatial=value.trials.flatMap(trial=>{const endpoint=trial.state==='landed'?trial.landing:trial.last_valid_point;if(!endpoint||![endpoint.latitude_deg,endpoint.longitude_deg].every(Number.isFinite))return [];const full=histories[value.snapshot_id+':'+trial.trial_id],loaded=full?sample(full)[0]:null;return [{...(loaded??{duration:endpoint.elapsed_s/60,burst:trial.burst?trial.burst.elapsed_s/60:null,history:[],historyIsTimed:true}),id:trial.trial_id,drawId:trial.draw_id,status:trial.state,lat:endpoint.latitude_deg,lon:endpoint.longitude_deg,parameter:trial.parameter,weatherWindow:trial.weather_window,historyLoaded:!!full,stopReason:trial.stop}];});
 return {id:value.snapshot_id+':'+value.case_id,kind:'ensemble',conditions:{...conditions(value.submitted_config,String(value.weather_snapshot.id)),sampling:value.sampling,ensembleRef:{snapshot_id:value.snapshot_id,case_id:value.case_id}},artificial:false,realSamples:spatial,collection:value,analysis,envelope:null};
}
export function collectionInputsMatch(candidate:Candidate,value:CaseResult):boolean{if(value.mode==='historical_windows')return candidate.analysis_mode==='historical_windows'&&historicalMatches(candidate,value.submitted_config);return candidate.weather_source_id===value.weather_snapshot.id&&stableString(candidate.config)===stableString(value.submitted_config)&&stableString(samplingInput(candidate.sampling))===stableString(samplingInput(value.sampling));}
export function collectionMatches(candidate:Candidate,value:CaseResult,current?:WeatherSource):boolean{return collectionInputsMatch(candidate,value)&&weatherMatch(current,value.weather_snapshot).state==='same';}
export function aggregateTraces(analysis:EnsembleAnalysis,metric:string,name:string,color:string,bands:boolean){
 const metrics:Record<string,[string,number,string]>={h:['altitude_m',.001,''],e:['east_km',1,'東'],n:['north_km',1,'北'],distance:['distance_km',1,''],speed:['horizontal_speed_m_s',1,''],vertical:['vertical_speed_m_s',1,'']};
 const keys=metric==='en'?['e','n']:[metric],traces:any[]=[];
 for(const phase of ['ascent','descent'] as const)for(const key of keys){const definition=metrics[key];if(!definition)continue;const [field,scale,suffix]=definition,rows=analysis.history.phases[phase],phaseColor=name?color:phase==='ascent'?'#1472b9':'#c35915',label=[name,phase==='ascent'?'上昇':'降下',suffix].filter(Boolean).join(' '),x=rows.map(r=>r.elapsed_s/60),values=(part:'mean'|'low'|'high')=>rows.map(r=>r.metrics[field]?.[part]==null?null:r.metrics[field][part]!*scale),counts=rows.map(r=>r.metrics[field]?.n??0);
  if(bands){traces.push({x,y:values('low'),type:'scatter',mode:'lines',line:{width:0},showlegend:false,hoverinfo:'skip',connectgaps:false});traces.push({x,y:values('high'),type:'scatter',mode:'lines',line:{width:0},fill:'tonexty',fillcolor:phaseColor.startsWith('#')?phaseColor+'25':'rgba(70,110,140,.15)',showlegend:false,hoverinfo:'skip',connectgaps:false});}
  traces.push({x,y:values('mean'),type:'scatter',mode:'lines',name:label,line:{color:phaseColor,dash:key==='n'?'dot':'solid',width:2.3},customdata:counts,hovertemplate:'%{x:.2f}分 · %{y:.3f}<br>有効記録 n=%{customdata}<extra>'+label+'</extra>',connectgaps:false});
 }return traces;
}

function samplingInput(s:any){return s?{variable:s.variable,unit:s.unit,distribution:s.distribution,reason:s.reason,n:s.n,seed:s.seed}:null;}

/** Paired comparisons join the frozen original draw, never array position. */
export function pairedRows(a:CaseResult,b:CaseResult){
 if(a.drawset_id!==b.drawset_id)return {paired:false,rows:[],missing:null};
 const lookup=new Map(b.trials.map(t=>[t.draw_id,t]));
 const rows=a.trials.flatMap(x=>{const y=lookup.get(x.draw_id);if(!y)return [];return [{drawId:x.draw_id,value:x.parameter?.value??null,unit:x.parameter?.unit??'',weatherWindow:x.weather_window,a:x,b:y,landingPair:x.state==='landed'&&y.state==='landed'&&!!x.landing&&!!y.landing,deltaMinutes:x.state==='landed'&&y.state==='landed'&&x.landing&&y.landing?(y.landing.elapsed_s-x.landing.elapsed_s)/60:null}];});
 return {paired:true,rows,missing:rows.filter(r=>!r.landingPair).length};
}

/** Compare existing point-in-region results only for the same frozen draw's landing pair. */
export function pairedInterference(a:CaseResult,b:CaseResult,hitsA:string[]|null,hitsB:string[]|null){
 const paired=pairedRows(a,b),configured=hitsA!==null&&hitsB!==null,first=new Set(hitsA??[]),second=new Set(hitsB??[]),counts={retained:0,exited:0,entered:0,clear:0,unresolved:0};
 const rows=paired.rows.map(r=>{let transition:'retained'|'exited'|'entered'|'clear'|'unresolved'|'unconfigured';
  if(!configured)transition='unconfigured';else if(!r.landingPair)transition='unresolved';else transition=first.has(r.a.trial_id)?second.has(r.b.trial_id)?'retained':'exited':second.has(r.b.trial_id)?'entered':'clear';
  if(transition!=='unconfigured')counts[transition]++;return {...r,transition};
 });return {...paired,rows,configured,transitions:configured?counts:null};
}
