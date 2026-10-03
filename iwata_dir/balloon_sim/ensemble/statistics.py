"""Join selection identity, landing geometry and time summaries without I/O."""
from .landing import landing_analysis
from .histories import history_analysis

METHOD = "empirical-covariance-and-elapsed-phase/1"


def analyze_results(items, *, selected_trial_ids=None):
    """Analyze full ledger rows {trial_id, result: FlightResult | None}.

    Missing results and empty-record physical stops remain selected. The caller
    owns run/attempt/source hashes and supplies only verified immutable results.
    Equal weights are a contract of the current drawset, not guessed here.
    """
    ids = [i["trial_id"] for i in items]
    if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
        raise ValueError("trial IDs must be distinct nonempty strings")
    selection = ids if selected_trial_ids is None else list(selected_trial_ids)
    if any(not isinstance(i, str) for i in selection) or len(set(selection)) != len(selection) or not set(selection) <= set(ids):
        raise ValueError("selection must contain distinct trial IDs from this ledger")
    selected = set(selection)
    rows = [i for i in items if i["trial_id"] in selected]
    for row in rows:
        result = row["result"]
        if result is None:
            continue
        if (not isinstance(result, dict) or result.get("status") not in ("landed", "stopped")
                or not isinstance(result.get("records"), list)
                or not isinstance(result.get("summary"), dict)
                or not isinstance(result.get("config"), dict)):
            raise ValueError("only completed scientific results or null belong in analysis")
        if result["status"] == "landed" and not isinstance(result["summary"].get("landing"), dict):
            raise ValueError("landed results require a landing location")
    completed = sum(i["result"] is not None for i in rows)
    history_count = sum(bool(i["result"] and i["result"]["records"]) for i in rows)
    return {"schema": "balloon.ensemble.analysis/1", "method": METHOD,
            "selected_trial_ids": [i for i in ids if i in selected],
            "selected_count": len(rows), "completed_count": completed,
            "missing_result_count": len(rows) - completed, "history_count": history_count,
            "landing": landing_analysis(rows), "history": history_analysis(rows)}
