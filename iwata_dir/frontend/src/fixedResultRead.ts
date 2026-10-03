import {ApiError} from './api';
/** Observation of a saved reference; not a numerical run state or a persisted result. */
export type FixedResultRead={state:'loading'|'missing'|'error'|'ready';message?:string};
export function readFailure(error:unknown):FixedResultRead {
 return {state:error instanceof ApiError&&error.status===404?'missing':'error',message:error instanceof Error?error.message:String(error)};
}
export function fixedResultLabel(read:FixedResultRead|undefined):string {
 return !read?'未計算':read.state==='loading'?'保存結果を読込中':read.state==='missing'?'保存先に結果が見つかりません':read.state==='error'?'保存結果を読み込めません':'保存結果を表示中';
}
/** A missing artifact must not normalize the saved group/selection/time to empty. */
export function waitingDetail(state:{detail:boolean;active:string;tabs:any[];groups:any[]}):boolean {
 if(!state.detail)return false;
 const group=state.groups.find(g=>g.id===state.active),ids=group?.members??[state.active];
 return ids.some((id:string)=>{const tab=state.tabs.find(t=>t.id===id);return !!tab?.resultRead&&!tab.result;});
}
