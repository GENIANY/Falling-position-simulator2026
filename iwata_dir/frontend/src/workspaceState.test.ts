import { describe, expect, it } from "vitest";
import {
  initialState,
  projectSaveSignature,
  RunWatchOwners,
  SubmissionIntents,
  workspaceReducer,
} from "./workspaceState";
import { draftInputsMatchRun, stableString } from "./domain";
import type { Candidate, Config, ResultEnvelope, Run } from "./domain";

const config: Config = {
  schema: "balloon.flight.config/1",
  launch: {
    time_utc: "2026-09-23T03:30:00Z",
    latitude_deg: 43,
    longitude_deg: 141.5,
    altitude_m: 74,
  },
  ascent: { mode: "constant_speed", speed_m_s: 5 },
  burst: { mode: "altitude", altitude_m: 30000 },
  descent: { mode: "rated_speed", reference_speed_m_s: 5 },
};
const candidate = (id: string): Candidate => ({
  id,
  label: id,
  revision: 1,
  weather_source_id: "saved",
  config,
});
const run = (id: string, candidateId: string, state = "completed"): Run => ({
  run_id: id,
  candidate_id: candidateId,
  candidate_revision: 1,
  state,
  result_available: state === "completed",
  weather_source_id: "saved",
  spec: { submitted_input: { config, weather_source_id: "saved" } },
});
const result = (id: string) =>
  ({
    run_id: id,
    trial_id: id + ":0",
    n: 1,
    weight: 1,
    weather_snapshot: {},
    source_snapshot: {},
    result: {
      schema: "balloon.flight.result/1",
      status: "stopped",
      config,
      records: [],
      events: [],
      stop_reason: { code: "OUT_OF_BOUNDS", message: "outside" },
      summary: { duration_s: 0, maximum_altitude_m: null, landing: null },
    },
  }) as ResultEnvelope;
function savedState() {
  return workspaceReducer(initialState(), {
    type: "restore",
    project: {
      schema: "balloon.project/1",
      title: "test",
      candidates: [candidate("A"), candidate("B")],
      compare_run_ids: ["a0", "b0"],
    },
    revision: 1,
    runs: [run("a0", "A"), run("b0", "B")],
  });
}
describe("immutable results and human selection", () => {
  it('normalizes only persisted envelope defaults and JSON omission, never a changed model, reference or UI value',()=>{
    const a={...savedState().project,ui_state:{season_real:{metric:'h',optional:undefined}},compare_results:[{kind:'ensemble_case' as const,ensemble_id:'e',snapshot_id:'s',case_id:'A'}]};
    const b:any=JSON.parse(JSON.stringify(a));b.candidates=b.candidates.map((c:Candidate)=>({parent_id:null,delay_minutes:null,sampling:null,analysis_mode:'forecast',...c}));b.compare_results=b.compare_results.map((r:any)=>({...r,analysis_id:null}));
    expect(projectSaveSignature(a)).toBe(projectSaveSignature(b));
    for(const change of [(p:any)=>{p.ui_state.season_real.metric='en';},(p:any)=>{p.compare_results[0].analysis_id='a';},(p:any)=>{p.candidates[0].config.ascent.speed_m_s=7;},(p:any)=>{p.candidates[0].analysis_mode='historical_windows';},(p:any)=>{p.ui_state.season_real.optional=null;}]){
      const changed=structuredClone(b);change(changed);expect(projectSaveSignature(a)).not.toBe(projectSaveSignature(changed));
    }
  });
  it('initially selects only an explicitly recovered request with unchanged draft and no selected result',()=>{
    const base=savedState(),empty={...base,project:{...base.project,compare_run_ids:[]}};
    const action={type:'result' as const,candidateId:'A',epoch:0,intent:'restore' as const,run:run('a1','A'),result:result('a1'),recoveryCandidate:candidate('A')};
    expect(workspaceReducer(empty,action).project.compare_run_ids).toEqual(['a1']);
    expect(workspaceReducer(empty,{...action,recoveryCandidate:undefined}).project.compare_run_ids).toEqual([]);
    expect(workspaceReducer(base,action).project.compare_run_ids).toEqual(['a0','b0']);
    const changed={...empty,project:{...empty.project,candidates:[{...candidate('A'),revision:2,config:{...config,launch:{...config.launch,latitude_deg:44}}},candidate('B')]}};
    expect(workspaceReducer(changed,action).project.compare_run_ids).toEqual([]);
    expect(workspaceReducer({...empty,selectionEpoch:{A:1}},action).project.compare_run_ids).toEqual([]);
    const collection={...empty,project:{...empty.project,compare_results:[{kind:'ensemble_case' as const,case_id:'A',ensemble_id:'e',snapshot_id:'s'}]}};
    expect(workspaceReducer(collection,action).project.compare_results).toEqual(collection.project.compare_results);
  });
  it("restarts a run watch on reconnect even before the old request finishes", () => {
    const watches = new RunWatchOwners();
    expect(watches.acquire("a1", 1)).toBe(true);
    expect(watches.acquire("a1", 2)).toBe(true);
    watches.release("a1", 1); // late old finally must leave the new watch owned
    expect(watches.acquire("a1", 2)).toBe(false);
    watches.release("a1", 2);
    expect(watches.acquire("a1", 2)).toBe(true);
  });
  it("retains one request after an ambiguous 5xx but releases a definite 4xx rejection", () => {
    let serial = 0;
    const intents = new SubmissionIntents(() => "request-" + ++serial);
    const a = candidate("A"),
      first = intents.forAttempt(a);
    intents.reject(a, first, 502); // accepted upstream, response path failed
    expect(intents.forAttempt(a)).toBe(first);
    intents.reject(a, first, 422); // definite validation rejection
    expect(intents.forAttempt(a)).not.toBe(first);
  });
  it("reconnects to an in-flight run without replacing the saved older comparison", () => {
    let s = savedState();
    s = workspaceReducer(s, {
      type: "accepted",
      candidateId: "A",
      run: run("a1", "A", "running"),
    });
    s = workspaceReducer(s, {
      type: "result",
      candidateId: "A",
      epoch: 0,
      intent: "restore",
      run: run("a1", "A"),
      result: result("a1"),
    });
    expect(s.project.compare_run_ids).toEqual(["a0", "b0"]);
    expect(s.results.a1).toBeDefined();
  });
  it("retransmits one unknown request but creates a new acknowledged retry after failure", () => {
    let serial = 0;
    const intents = new SubmissionIntents(() => "request-" + ++serial);
    const a = candidate("A");
    const first = intents.forAttempt(a);
    expect(intents.forAttempt(a)).toBe(first); // response was lost
    intents.acknowledge(a, first); // known run may later fail/interrupted
    const retry = intents.forAttempt(a);
    expect(retry).not.toBe(first);
    intents.acknowledge(a, first); // a late duplicate response cannot clear the new intent
    expect(intents.forAttempt(a)).toBe(retry);
  });
  it("replaces each candidate atomically when two jobs finish in either order", () => {
    let s = savedState();
    s = workspaceReducer(s, {
      type: "accepted",
      candidateId: "A",
      run: run("a1", "A", "running"),
    });
    s = workspaceReducer(s, {
      type: "accepted",
      candidateId: "B",
      run: run("b1", "B", "running"),
    });
    s = workspaceReducer(s, {
      type: "result",
      candidateId: "B",
      epoch: 0,
      intent: "complete",
      run: run("b1", "B"),
      result: result("b1"),
    });
    s = workspaceReducer(s, {
      type: "result",
      candidateId: "A",
      epoch: 0,
      intent: "complete",
      run: run("a1", "A"),
      result: result("a1"),
    });
    expect(s.project.compare_run_ids.sort()).toEqual(["a1", "b1"]);
    expect(s.runs.a0).toBeDefined();
  });
  it("keeps a manual old-result selection even when a pending job completes later", () => {
    let s = savedState();
    s = workspaceReducer(s, {
      type: "accepted",
      candidateId: "A",
      run: run("a1", "A", "running"),
    });
    s = workspaceReducer(s, {
      type: "selection_requested",
      candidateId: "A",
      epoch: 1,
    });
    s = workspaceReducer(s, {
      type: "result",
      candidateId: "A",
      epoch: 1,
      intent: "select",
      run: run("a0", "A"),
      result: result("a0"),
    });
    s = workspaceReducer(s, {
      type: "result",
      candidateId: "A",
      epoch: 0,
      intent: "complete",
      run: run("a1", "A"),
      result: result("a1"),
    });
    expect(s.project.compare_run_ids).toEqual(["b0", "a0"]);
    expect(s.results.a1).toBeDefined();
  });
  it("keeps a newer manual selection when an earlier fetch arrives last", () => {
    let s = savedState();
    s = workspaceReducer(s, {
      type: "selection_requested",
      candidateId: "A",
      epoch: 2,
    });
    s = workspaceReducer(s, {
      type: "result",
      candidateId: "A",
      epoch: 2,
      intent: "select",
      run: run("a2", "A"),
      result: result("a2"),
    });
    s = workspaceReducer(s, {
      type: "result",
      candidateId: "A",
      epoch: 1,
      intent: "select",
      run: run("a1", "A"),
      result: result("a1"),
    });
    expect(s.project.compare_run_ids).toEqual(["b0", "a2"]);
  });
  it("restores drafts and a readable result even when the other result is unavailable", () => {
    let s = savedState();
    s = workspaceReducer(s, {
      type: "result",
      candidateId: "B",
      epoch: 0,
      intent: "restore",
      run: run("b0", "B"),
      result: result("b0"),
    });
    expect(s.project.candidates).toHaveLength(2);
    expect(s.project.compare_run_ids).toEqual(["a0", "b0"]);
    expect(s.results.b0.result.status).toBe("stopped");
    expect(s.results.b0.result.summary.landing).toBeNull();
  });
  it("never turns edits made during save into saved edits", () => {
    const s = savedState(),
      saved = structuredClone(s.project);
    const changed = workspaceReducer(s, {
      type: "candidate",
      candidate: {
        ...candidate("A"),
        revision: 2,
        config: { ...config, ascent: { mode: "constant_speed", speed_m_s: 6 } },
      },
    });
    const finished = workspaceReducer(changed, {
      type: "saved",
      project: saved,
      revision: 2,
    });
    expect(finished.savedSignature).not.toBe(stableString(finished.project));
    expect(finished.project.compare_run_ids).toEqual(["a0", "b0"]);
  });
  it("compares submitted input and source ID independently of provenance observation", () => {
    expect(
      draftInputsMatchRun({ ...candidate("A"), revision: 99 }, run("a0", "A")),
    ).toBe(true);
    expect(
      draftInputsMatchRun(
        { ...candidate("A"), weather_source_id: "different" },
        run("a0", "A"),
      ),
    ).toBe(false);
  });
});
