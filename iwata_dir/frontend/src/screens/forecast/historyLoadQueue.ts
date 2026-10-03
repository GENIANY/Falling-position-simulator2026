import type {CaseResult} from '../../ensembleDomain';

export type HistoryTask={snapshotId:string;trialId:string};
export type HistoryLoadContext={key:string;tasks:HistoryTask[]};
const taskKey=(task:HistoryTask)=>JSON.stringify([task.snapshotId,task.trialId]);

/** Original records are snapshot/trial GETs, independent of any aggregate or region analysis. */
export function historyLoadContext(input:{enabled:boolean;collection:CaseResult;selectedIds:string[];loadedIds:string[];bindingKey:string}):HistoryLoadContext|null{
 const {collection,selectedIds,loadedIds,bindingKey}=input;
 if(!input.enabled)return null;
 const selected=[...selectedIds].sort();
 const known=new Set(collection.trials.map(row=>row.trial_id));
 if(new Set(selected).size!==selected.length||selected.some(id=>!known.has(id)))return null;
 const selectedSet=new Set(selected),loaded=new Set(loadedIds);
 return {key:JSON.stringify([collection.snapshot_id,collection.case_id,selected,bindingKey]),tasks:collection.trials.filter(row=>selectedSet.has(row.trial_id)&&row.result_available&&!loaded.has(row.trial_id)).map(row=>({snapshotId:collection.snapshot_id,trialId:row.trial_id}))};
}

/** One bounded queue for the screen. Changing selection replaces unsent work. */
export function createHistoryLoadQueue(options:{context:()=>HistoryLoadContext|null;read:(task:HistoryTask)=>Promise<unknown>;failed:(error:unknown,task:HistoryTask)=>void;changed?:()=>void}){
 const running=new Map<string,{contextKey:string;started:boolean}>(),completed=new Set<string>(),failed=new Map<string,{task:HistoryTask;message:string}>();
 let disposed=false,pumping=false;
 function relevant(context:HistoryLoadContext|null,key:string,contextKey:string){return context?.key===contextKey&&context.tasks.some(task=>taskKey(task)===key);}
 function sync(){
  if(disposed||pumping)return;pumping=true;
  try{
   while(running.size<4){
    const context=options.context();if(!context)break;
    const task=context.tasks.find(row=>{const key=taskKey(row);return !running.has(key)&&!completed.has(key)&&!failed.has(key);});if(!task)break;
    const key=taskKey(task),entry={contextKey:context.key,started:false};running.set(key,entry);
    void Promise.resolve().then(()=>{
     if(disposed||!relevant(options.context(),key,entry.contextKey))return;
     entry.started=true;return options.read(task);
    }).then(()=>{if(entry.started&&!disposed)completed.add(key);}).catch(error=>{
     if(disposed)return;failed.set(key,{task,message:error instanceof Error?error.message:String(error)});if(relevant(options.context(),key,entry.contextKey))options.failed(error,task);
    }).finally(()=>{if(running.get(key)===entry)running.delete(key);sync();if(!disposed)options.changed?.();});
   }
  }finally{pumping=false;}
 }
 // Explicit retry reopens only failures. Successful and in-flight reads remain deduplicated.
 function retry(){failed.clear();sync();}
 function dispose(){disposed=true;completed.clear();failed.clear();}
 function status(){
  const context=options.context(),tasks=context?.tasks??[];
  return {pending:tasks.filter(task=>!completed.has(taskKey(task))&&!failed.has(taskKey(task))).length,failures:tasks.flatMap(task=>{const value=failed.get(taskKey(task));return value?[value]:[];})};
 }
 return {sync,retry,dispose,status};
}
