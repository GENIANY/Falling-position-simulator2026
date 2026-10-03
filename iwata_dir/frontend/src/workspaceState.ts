import {comparisonRefs} from './ensembleDomain';
import type { Project, ResultEnvelope, Run } from "./domain";
import { emptyProject, stableString } from "./domain";
import type { Candidate } from "./domain";

/** Match the HTTP JSON representation and only backend.contracts.Project defaults.
 * Physics, window selection, fixed references and nested UI state stay exact. */
export function projectSaveSignature(value:Project):string {
  const p=JSON.parse(JSON.stringify(value));
  return stableString({schema:'balloon.project/1',ui_state:{},...p,
    candidates:p.candidates.map((c:Candidate)=>({parent_id:null,delay_minutes:null,sampling:null,analysis_mode:'forecast',...c})),
    compare_results:p.compare_results?.map((r:any)=>r.kind==='ensemble_case'?{analysis_id:null,...r}:r)??null});
}

// An unknown POST response is a retransmission of one intent. Acknowledged
// submission ends that intent, even if the job later fails or is interrupted.
export class SubmissionIntents {
  private pending = new Map<string, string>();
  constructor(private createId: () => string = () => crypto.randomUUID()) {}
  forAttempt(candidate: Candidate): string {
    const key = stableString(candidate);
    let id = this.pending.get(key);
    if (!id) {
      id = this.createId();
      this.pending.set(key, id);
    }
    return id;
  }
  acknowledge(candidate: Candidate, id: string): void {
    const key = stableString(candidate);
    if (this.pending.get(key) === id) this.pending.delete(key);
  }
  reject(candidate: Candidate, id: string, status: number): void {
    // A server/proxy 5xx may follow acceptance; keep the retransmission ID.
    if (status >= 400 && status < 500) this.acknowledge(candidate, id);
  }
}

// Reloaded polling can replace an older generation's watch immediately.
// The older finally block must not release the new generation's ownership.
export class RunWatchOwners {
  private owners = new Map<string, number>();
  acquire(runId: string, generation: number): boolean {
    if (this.owners.get(runId) === generation) return false;
    this.owners.set(runId, generation);
    return true;
  }
  release(runId: string, generation: number): void {
    if (this.owners.get(runId) === generation) this.owners.delete(runId);
  }
}

export type WorkspaceState = {
  project: Project;
  revision: number;
  savedSignature: string;
  runs: Record<string, Run>;
  results: Record<string, ResultEnvelope>;
  selectionEpoch: Record<string, number>;
  latestRun: Record<string, string>;
};
export const initialState = (): WorkspaceState => ({
  project: emptyProject(),
  revision: 0,
  savedSignature: "",
  runs: {},
  results: {},
  selectionEpoch: {},
  latestRun: {},
});
export type Action =
  | { type: "restore"; project: Project; revision: number; runs: Run[] }
  | { type: "project"; project: Project }
  | { type: "candidate"; candidate: Project["candidates"][number] }
  | { type: "saved"; project: Project; revision: number }
  | { type: "accepted"; run: Run; candidateId: string }
  | { type: "polled"; run: Run }
  | { type: "selection_requested"; candidateId: string; epoch: number }
  | {
      type: "result";
      run: Run;
      result: ResultEnvelope;
      candidateId: string;
      epoch: number;
      intent: "complete" | "select" | "restore";
      recoveryCandidate?: Candidate;
    };

function replaceComparison(
  project: Project,
  runs: Record<string, Run>,
  candidateId: string,
  id: string,
): Project {
  return {
    ...project,
    ...(project.compare_results ? {compare_results:[...comparisonRefs(project).filter(r=>r.kind==='single_run'?r.run_id!==id&&runs[r.run_id]?.candidate_id!==candidateId:r.case_id!==candidateId),{kind:'single_run' as const,run_id:id}]}:{}),
    compare_run_ids: [
      ...project.compare_run_ids.filter(
        (old) => old !== id && runs[old]?.candidate_id !== candidateId,
      ),
      id,
    ],
  };
}
export function workspaceReducer(
  state: WorkspaceState,
  action: Action,
): WorkspaceState {
  switch (action.type) {
    case "restore":
      return {
        ...initialState(),
        project: action.project,
        revision: action.revision,
        savedSignature: stableString(action.project),
        runs: Object.fromEntries(action.runs.map((r) => [r.run_id, r])),
      };
    case "project":
      return { ...state, project: action.project };
    case "candidate":
      return {
        ...state,
        project: {
          ...state.project,
          candidates: state.project.candidates.map((c) =>
            c.id === action.candidate.id ? action.candidate : c,
          ),
        },
      };
    case "saved":
      return {
        ...state,
        revision: action.revision,
        savedSignature: stableString(action.project),
      };
    case "accepted":
      return {
        ...state,
        runs: { ...state.runs, [action.run.run_id]: action.run },
        latestRun: {
          ...state.latestRun,
          [action.candidateId]: action.run.run_id,
        },
      };
    case "polled":
      return {
        ...state,
        runs: { ...state.runs, [action.run.run_id]: action.run },
      };
    case "selection_requested":
      return {
        ...state,
        selectionEpoch: {
          ...state.selectionEpoch,
          [action.candidateId]: action.epoch,
        },
      };
    case "result": {
      const runs = { ...state.runs, [action.run.run_id]: action.run };
      const epochMatches =
        (state.selectionEpoch[action.candidateId] ?? 0) === action.epoch;
      // Only explicit recovery of a previously unknown request may fill an
      // empty selection. Generic restoration keeps the saved view unchanged.
      const recoveredInitial = action.intent === 'restore' && !!action.recoveryCandidate &&
        state.project.candidates.some(c => c.id === action.candidateId && stableString(c) === stableString(action.recoveryCandidate)) &&
        !comparisonRefs(state.project).some(r => r.kind === 'ensemble_case'
          ? r.case_id === action.candidateId
          : !runs[r.run_id] || runs[r.run_id].candidate_id === action.candidateId);
      const choose =
        (action.intent==='select'||state.project.candidates.some(c => c.id === action.candidateId)) &&
        epochMatches &&
        (action.intent === "select" || recoveredInitial ||
          (action.intent === "complete" &&
            state.latestRun[action.candidateId] === action.run.run_id));
      return {
        ...state,
        runs,
        results: { ...state.results, [action.run.run_id]: action.result },
        project: choose
          ? replaceComparison(
              state.project,
              runs,
              action.candidateId,
              action.run.run_id,
            )
          : state.project,
      };
    }
  }
}
