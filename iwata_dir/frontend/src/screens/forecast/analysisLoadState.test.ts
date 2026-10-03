import {describe,it,expect,vi} from 'vitest';
import {createAnalysisLoadState,reusableOverviewAnalysis} from './analysisLoadState';
import {createHistoryLoadQueue,historyLoadContext,type HistoryTask} from './historyLoadQueue';
import type {CaseResult,EnsembleAnalysis} from '../../ensembleDomain';

const collection={snapshot_id:'S',case_id:'A',trials:[{trial_id:'T0',result_available:true},{trial_id:'T1',result_available:true},{trial_id:'T2',result_available:false}]} as CaseResult;
const analysis={selected_trial_ids:['T0','T1','T2'],selected_count:3,history:{unavailable_reason:'HISTORY_ANALYSIS_BYTE_LIMIT'}} as EnsembleAnalysis;
async function flush(){for(let i=0;i<16;i++)await Promise.resolve();}
function deferred<T>(){let resolve!:(value:T)=>void,reject!:(error:unknown)=>void;const promise=new Promise<T>((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};}

describe('reuse belongs to the complete fixed trial set',()=>{
 it('reuses the overview for implicit/all/reordered IDs even when aggregate history is unavailable',()=>{
  for(const ids of [null,['T0','T1','T2'],['T2','T0','T1']])expect(reusableOverviewAnalysis(collection,analysis,ids,null)).toBe(analysis);
 });
 it('does not show full-case analysis for subsets, duplicates, different sets, regions or stale analysis IDs/counts',()=>{
  for(const ids of [[],['T0'],['T0','T1','other'],['T0','T0','T2']])expect(reusableOverviewAnalysis(collection,analysis,ids,null)).toBeNull();
  expect(reusableOverviewAnalysis(collection,analysis,null,{regions:[]})).toBeNull();
  expect(reusableOverviewAnalysis(collection,{...analysis,selected_count:2},null,null)).toBeNull();
  expect(reusableOverviewAnalysis(collection,{...analysis,selected_trial_ids:['T0','T1','old']},null,null)).toBeNull();
  expect(reusableOverviewAnalysis(collection,undefined,null,null)).toBeNull();
 });
});

describe('aggregate reads and writes have distinct recovery rules',()=>{
 it('deduplicates pending/successful work and allows saved artifact GET without a writer',async()=>{
  const changed=vi.fn(),store=createAnalysisLoadState<string>({canWrite:()=>false,changed}),d=deferred<string>(),load=vi.fn(()=>d.promise),request={readOnly:true,load};
  expect(store.read('saved',request)).toBeNull();store.read('saved',request);await flush();expect(load).toHaveBeenCalledTimes(1);expect(store.status('saved').state).toBe('pending');
  d.resolve('artifact');await flush();expect(store.read('saved',request)).toBe('artifact');store.retry();store.read('saved',request);expect(load).toHaveBeenCalledTimes(1);expect(changed).toHaveBeenCalledTimes(1);
 });
 it('keeps reader requests blocked without calling writes and resumes only the current demand after ownership',async()=>{
  let owner=false;const load=vi.fn(async()=>'artifact'),store=createAnalysisLoadState<string>({canWrite:()=>owner,changed:vi.fn()}),request={readOnly:false,load};
  store.read('old-selection',request);store.read('current-selection',request);await flush();expect(load).not.toHaveBeenCalled();expect(store.status('current-selection').state).toBe('blocked');
  store.retry();store.read('current-selection',request);await flush();expect(load).not.toHaveBeenCalled();
  owner=true;store.resumeBlocked();store.read('current-selection',request);await flush();expect(load).toHaveBeenCalledTimes(1);expect(store.status('old-selection').state).toBe('idle');
 });
 it('rechecks ownership at dispatch and blocks a request scheduled before relinquishing',async()=>{
  let owner=true;const load=vi.fn(async()=>'artifact'),store=createAnalysisLoadState<string>({canWrite:()=>owner,changed:vi.fn()});
  store.read('selection',{readOnly:false,load});owner=false;await flush();expect(load).not.toHaveBeenCalled();expect(store.status('selection').state).toBe('blocked');
 });
 it('opens a saved artifact GET arriving after a never-sent write was blocked',async()=>{
  const store=createAnalysisLoadState<string>({canWrite:()=>false,changed:vi.fn()}),post=vi.fn(async()=>'new'),get=vi.fn(async()=>'saved');
  store.read('selection',{readOnly:false,load:post});store.read('selection',{readOnly:true,load:get});await flush();
  expect(post).not.toHaveBeenCalled();expect(get).toHaveBeenCalledTimes(1);expect(store.read('selection',{readOnly:true,load:get})).toBe('saved');
 });
 it('retains failed or uncertain requests through refresh and ownership changes until explicit retry',async()=>{
  let owner=true;const load=vi.fn<()=>Promise<string>>().mockRejectedValueOnce(Error('response lost')).mockResolvedValue('artifact'),store=createAnalysisLoadState<string>({canWrite:()=>owner,changed:vi.fn()}),request={readOnly:false,load};
  store.read('selection',request);await flush();expect(store.status('selection')).toEqual({state:'failed',message:'response lost'});
  owner=false;store.read('selection',request);owner=true;store.resumeBlocked();store.read('selection',request);await flush();expect(load).toHaveBeenCalledTimes(1);
  store.retry(['different']);store.read('selection',request);await flush();expect(load).toHaveBeenCalledTimes(1);
  store.retry(['selection']);store.read('selection',request);await flush();expect(load).toHaveBeenCalledTimes(2);expect(store.read('selection',request)).toBe('artifact');
 });
 it('does not expose a mismatched saved artifact when validation rejects it',async()=>{
  const store=createAnalysisLoadState<string>({canWrite:()=>false,changed:vi.fn()}),request={readOnly:true,load:async()=>{throw Error('selection mismatch');}};
  store.read('saved',request);await flush();expect(store.read('saved',request)).toBeNull();expect(store.status('saved')).toEqual({state:'failed',message:'selection mismatch'});
 });
 it('disposal suppresses scheduled writes and late results/callbacks',async()=>{
  const changed=vi.fn(),load=vi.fn(async()=>'artifact'),store=createAnalysisLoadState<string>({canWrite:()=>true,changed});store.read('scheduled',{readOnly:false,load});store.dispose();await flush();expect(load).not.toHaveBeenCalled();expect(changed).not.toHaveBeenCalled();
  const late=createAnalysisLoadState<string>({canWrite:()=>true,changed}),d=deferred<string>(),accepted=vi.fn();late.read('pending',{readOnly:false,load:()=>d.promise,accepted});await flush();late.dispose();d.resolve('artifact');await flush();expect(accepted).not.toHaveBeenCalled();expect(changed).not.toHaveBeenCalled();
 });
});

describe('detail histories do not wait for aggregate writes',()=>{
 it('reads original records in a reader tab while the partial aggregate remains visibly blocked',async()=>{
  const store=createAnalysisLoadState<string>({canWrite:()=>false,changed:vi.fn()}),post=vi.fn(async()=>'artifact'),get=vi.fn(async(_task:HistoryTask)=>{});
  const context=historyLoadContext({enabled:true,collection,selectedIds:['T1'],loadedIds:[],bindingKey:'S:A'});
  const queue=createHistoryLoadQueue({context:()=>context,read:get,failed:vi.fn()});store.read('subset',{readOnly:false,load:post});queue.sync();await flush();
  expect(post).not.toHaveBeenCalled();expect(store.status('subset').state).toBe('blocked');expect(get).toHaveBeenCalledWith({snapshotId:'S',trialId:'T1'});queue.dispose();store.dispose();
 });
 it('loads raw histories after aggregate failure and does not invent records for unexecuted trials',async()=>{
  const store=createAnalysisLoadState<string>({canWrite:()=>true,changed:vi.fn()}),get=vi.fn(async(_task:HistoryTask)=>{});
  store.read('all',{readOnly:false,load:async()=>{throw Error('analysis failed');}});await flush();
  const context=historyLoadContext({enabled:true,collection,selectedIds:['T0','T1','T2'],loadedIds:[],bindingKey:'S:A'}),queue=createHistoryLoadQueue({context:()=>context,read:get,failed:vi.fn()});queue.sync();await flush();
  expect(store.status('all').state).toBe('failed');expect(get.mock.calls.map(args=>args[0])).toEqual([{snapshotId:'S',trialId:'T0'},{snapshotId:'S',trialId:'T1'}]);queue.dispose();store.dispose();
 });
});
