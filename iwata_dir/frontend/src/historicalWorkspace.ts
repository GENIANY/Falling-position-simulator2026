import type {Project,Run} from './domain';
import {comparisonRefs} from './ensembleDomain';

/** Climate interest is provenance; controller.selectionContext is a sample selection. */
export function readHistoricalInterest(view?:Record<string,any>):Record<string,unknown>|undefined{
 const value=view&&Object.prototype.hasOwnProperty.call(view,'historicalInterest')?view.historicalInterest:view?.selectionContext;
 if(!value||typeof value!=='object'||Array.isArray(value)||value.schema!=='balloon.climate-flight-interest/1')return undefined;
 const b=value.bounds,p=value.period;
 const half=p&&Number.isInteger(p.month)&&p.month>=1&&p.month<=12&&[1,2].includes(p.bin);
 const grouped=p&&['month','season'].includes(value.grain)&&typeof p.label==='string'&&Array.isArray(p.months)&&p.months.length===(value.grain==='month'?1:3)&&new Set(p.months).size===p.months.length&&p.months.every((m:unknown)=>typeof m==='number'&&Number.isInteger(m)&&m>=1&&m<=12)&&Array.isArray(p.member_timebin_ids)&&p.member_timebin_ids.length===p.months.length*2&&new Set(p.member_timebin_ids).size===p.member_timebin_ids.length&&p.member_timebin_ids.every((id:unknown)=>typeof id==='number'&&Number.isInteger(id)&&id>=0&&id<24&&p.months.includes(Math.floor(id/2)+1));
 const hours=value.hours_utc;
 if(!['analysis_id','query_hash','result_hash','dataset_sha256','label'].every(k=>typeof value[k]==='string'&&value[k].length>0)||
    !b||!['south','north','west','east'].every(k=>Number.isFinite(b[k]))||
     !p||!Number.isInteger(p.timebin_id)||(!half&&!grouped)||
     (hours!==undefined&&(!Array.isArray(hours)||!hours.length||new Set(hours).size!==hours.length||!hours.every((h:unknown)=>[0,6,12,18].includes(h as number)))))return undefined;
 return value;
}
export function mergeHistoricalView(current:Record<string,any>={},patch:Record<string,any>={}):Record<string,any>{
 const interest=readHistoricalInterest(current),next={...current,...patch};
 // Preserve an identifiable legacy interest before a detail snapshot replaces
 // selectionContext. Never manufacture interest from a sample-group label.
 if(!Object.prototype.hasOwnProperty.call(patch,'historicalInterest')&&interest)next.historicalInterest=structuredClone(interest);
 return next;
}

/** A view projection only. Persist and mutate the complete shared project. */
export function projectForAnalysis(project:Project,runs:Run[],historical:boolean):Project{
 const ids=new Set<string>([...(project.ui_state?.historicalCandidateIds??[]),...project.candidates.filter(c=>c.analysis_mode==='historical_windows').map(c=>c.id)]);
 const matches=(id:string|undefined)=>historical?!!id&&ids.has(id):!id||!ids.has(id);
 const refs=comparisonRefs(project).filter(r=>matches(r.kind==='ensemble_case'?r.case_id:runs.find(x=>x.run_id===r.run_id)?.candidate_id));
 return {...project,candidates:project.candidates.filter(c=>matches(c.id)),compare_results:refs,compare_run_ids:refs.flatMap(r=>r.kind==='single_run'?[r.run_id]:[])};
}
