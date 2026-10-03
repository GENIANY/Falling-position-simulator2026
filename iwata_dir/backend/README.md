# Local application adapter (0.58 candidate)

The 0.58 change adds `annual_quarters` for original-UTC archives: 48 calendar bins, nested within the existing half-months, for the annual chart only. Half-month/month/season results and old saved artifacts keep their existing meanings. The adapter reuses pressure-independent annual summaries within the same source, region and UTC-hour population; this is runtime computation reuse, separate from immutable result storage. Quarter bins are not added to spatial rows or historical-flight interests. See [IMPLEMENTATION_NOTES](../docs/IMPLEMENTATION_NOTES.md) for the contract, [COMMANDS C-09](../docs/COMMANDS.md#C-CLIMATE-RAW) for operation, and [THEORY_GUIDE](../docs/THEORY_GUIDE.pdf) for the calendar and statistical meaning. This paragraph describes the implementation, not a new scientific or UI acceptance result.

The 0.57 candidate connects original-UTC JRA-3Q and ERA5 wind samples to two half-month median curves and a whole-month p10–p90 band, while retaining the supplied ten-year database and its 0.56 mean/period/rose analyses as separate sources. Acquisition uses CLI tools; only the public-source reacquisition UI is deferred, not the analysis graphs, filters or saved-view workflow. The acquisition target is the same complete year, 2024, for both products. Both 2024 twelve-month acquisitions are now complete, independently checked against original response values and preserved locally. A four-native-cell sample of each full year is included in the repository for offline replay. The real-data GUI and existing-result preservation were checked at the local deployment; [S36](../BOOTSTRAP_RUNBOOK.html#s36-climate-final570) records the finite evidence and limits. This is not scientific acceptance or completion of representative multi-year seasonal flight analysis.

The 0.55 candidate keeps the existing planning GUI and connects bounded GFS preparation, launch-location checks, explicit request recovery and original-UTC historical windows to the same flight worker. A stable service-state identity helps the GUI distinguish its saved destination. Fixed results, current fields, edited drafts and unconfirmed submissions remain separate. Exact API contracts are in [IMPLEMENTATION_NOTES](../docs/IMPLEMENTATION_NOTES.md), operations in [COMMANDS](../docs/COMMANDS.md), and finite observations and remaining limits in [S36](../BOOTSTRAP_RUNBOOK.html#s36-plan550).

The saved-JRA GUI connection and earlier comparisons are evidence from 0.53; the 0.54 inventory, source-bound ground GET, delayed-read recovery and saved-view checks remain their own historical evidence. The 0.55 explicit historical windows do not turn half-month wind statistics into instantaneous fields or representative seasonal draws. Scientific accuracy, arbitrary historical acquisition and seasonal Monte Carlo remain separate, unfinished acceptance scopes.

This adapter calls the existing `balloon_sim` kernel without moving or changing it.
The declared saved JRA example remains available alongside saved GFS examples, one flight per run (`n=1`), fixed results for
comparison, candidate families, persistent screen context and reopening after a server restart.
Explicit GFS inventory observation and bounded acquisition add immutable weather
sources to the same run workflow. They require no API key. Saved examples remain
separate from newly acquired forecasts. The additional ensemble route freezes one
explicit, provisional uniform distribution and shares its primitive draws across
selected conditions. A separate original-date mode holds the vehicle inputs fixed
within each case and pairs cases by explicitly selected analysis windows. It reuses the same single-flight worker; acquiring weather
alone does not create a distribution or an ensemble.

From the repository root, with Python 3.12 (Windows PowerShell):

```powershell
python -m venv backend/.venv
backend/.venv/Scripts/python -m pip install -r backend/requirements.lock
backend/.venv/Scripts/python -B -m uvicorn backend.app:create_app --factory --host 127.0.0.1 --port 8451
```

`requirements.lock` fixes the complete runtime and test dependency set used for
this implementation. It is a version lock, not a wheel hash lock. The kernel uses
NumPy/SciPy in that environment. Forecast acquisition also uses ecCodes and
GeographicLib from the declared environment. Do not install these into an unrelated base
environment. No editable installation or root packaging change is required.

Build `frontend/dist` with the frontend instructions before the normal launch.
The server then serves `/`, `/assets`, `/scene3d`, and `/cesium` from the build; otherwise `/` explains the missing
build. API paths are under `/api/v1`, and an unknown API path remains a 404.
Set `BALLOON_FRONTEND_DIST` to a separate built directory when reviewing a new
frontend without replacing an existing build or connection.
Use the Vite port 8450 development proxy to the API port 8451. No permissive CORS
policy is enabled. Keep the server bound to loopback; this is a single-user local
application, not a public/multi-tenant service. POST/PUT require application/json.
Single-flight and weather cancellation use `{}`; ensemble operations use their
declared request IDs as described below.

State lives outside the repository, by default `%LOCALAPPDATA%/BalloonSimulator/state`
(on non-Windows, `~/.local/share/BalloonSimulator/state`). Set `BALLOON_DATA_DIR`,
or pass `data_dir` to `create_app` / `ApplicationService`, for an isolated location.
Only one service can own a directory at a time. Do not edit its DB or files while
running. A persistent UUID identifies that registry across restart; malformed existing
identity state is rejected rather than silently rekeyed. `/health` exposes `instance_id`.
Requests carrying `X-Balloon-Instance-Id` for another state return 409
`INSTANCE_MISMATCH` before route handling (health remains readable). Header-free
local API/CLI clients remain compatible; this is destination checking, not authentication.
There is no delete endpoint. Copying/exporting projects between computers is not yet
a supported workflow.

## Entry points and storage

`backend.application.ApplicationService` is usable without HTTP as a context
manager. `submit`, `list_runs`, `get_run`, `get_result`, `get_project`,
`save_project`, `weather_sources`, and `cancel` are synchronous service operations.
`backend.app.create_app` wraps them with FastAPI. The process entry point
`backend.worker.execute_run` loads a saved field, calls `simulate`, and uses the
existing `export_result`. Windows uses `spawn`; never start the service during
module import, and protect a standalone script entry with `if __name__ == '__main__':`.

SQLite stores draft revisions, immutable run specifications, and mutable job
states. Each accepted run also has fixed `specs/<run_id>/run.json` and config.
The worker writes the kernel's seven output files into a fresh staging directory.
The parent verifies all manifest hashes, adds the run specification and a
`COMMITTED.json` covering all outputs, renames the directory, then records a DB
pointer. Existence of a staging/output directory alone is not success. Interrupted
or failed staging folders remain diagnostic evidence and are not reused.
On startup, a fully renamed result lacking its DB completion update can be recovered
only after the original run/config and inner/outer manifests match. The previous
state/error and recovery outcome remain in `run_recoveries`; a staging directory,
partial result or changed artifact is not accepted as completed. The same check
handles publication exceptions within a running service. Result reads verify the
committed files and do not reload weather. Old results
remain readable if source weather is missing; that does not guarantee rerunning.

For the direct single-flight route, one process computes at a time; at most four additional runs wait. A full waiting
queue returns 429 without creating a run. Only waiting work can be cancelled.
Running work returns 409 and `cancellable:false`. Graceful shutdown waits for the
running computation; a forced server exit leaves unfinished states that become
`interrupted` on restart. Remaining queued work also becomes `interrupted` after
restart, with no automatic resubmission. A new explicit request ID is a new run.
A broken process pool stops further flight starts and reports `flight_execution`
as unavailable/restart-required through `/health`; queued work and readable
results remain. It does not silently recreate the pool or retry the queue.

## API and meaning

`GET /api/v1/weather-sources` returns sources and isolated `source_errors`, with source ID, label,
byte hash/size, schema/product, product-specific time identity, valid UTC times,
latitude/longitude bounds, vertical-coordinate identification and effective metadata.
Saved GFS `kind:fixture` and JRA `kind:saved_jra3q` have an example `default_config`;
`kind:acquired_gfs` has `default_config:null`. Acquiring weather must not silently
invent or replace a launch altitude, physical model or candidate. No client path or URL is used.
Unavailable sources are isolated in `source_errors`; other sources and saved
results remain accessible. Malformed source data may also fail an attempted run.
The rectangular bounds are not a promise that every altitude/flight is supported.
An acquired source exposes its inspected minimum top geometric altitude and the
coarse GFS ground assumption. A diameter-based burst altitude remains model-dependent.

`POST /api/v1/runs` takes
`{client_request_id,candidate_id,candidate_revision,label,weather_source_id,config}`.
The kernel validates/default-expands physical input. The response is 202 with
`{run_id,job_id,state,frozen_input_hash}`. Repeating the same request ID and content
returns the same run; reusing it with changed input returns 409. Candidate metadata,
original input, normalized config, weather identity, kernel/adapter source hashes
and numerical environment versions are frozen. The hash identifies resolved
scientific input, field and implementation; it is not an accuracy score.
For `acquired_gfs` and the new `saved_jra3q` source, submission also checks support from the current launch
time through the complete `integration.max_duration_s`. Existing GFS fixtures retain their support-stop diagnostics. Time/delay/duration edits
can require another supported saved field or, for GFS acquisition, a new weather plan.
They do not invoke an arbitrary JRA date download. Horizontal exits or other
unsupported queries are still handled truthfully by the numerical kernel.

`GET /api/v1/runs` returns direct single-flight summaries by default; ensemble
attempts have an explicit `kind` and ensemble join and must not be selected as
independent candidate results. A summary includes run/job IDs,
label, candidate ID/revision, source ID, creation UTC, state, result availability,
cancellability, frozen input hash, and error. `GET /runs/{id}` adds `spec`,
`started_at`, `finished_at` and recovery events. `GET /run-requests?client_request_id=...`
looks up an accepted intent without checking current weather or resubmitting it.
A 404 means not accepted at that observation time; it does not authorize a new ID
or prove that an earlier POST cannot still arrive. `POST /runs/{id}/cancel` cancels
queued work only.

`GET /api/v1/runs/{id}/result` returns
`{run_id,trial_id,n:1,weight:1,weather_snapshot,source_snapshot,result}`.
`result` is the existing `balloon.flight.result/1`: UTC timestamps, elapsed seconds,
latitude/longitude in degrees, geometric ASL altitude in metres, ground altitude
and AGL height in metres, phase, records, events, numerics and model assumptions.
GeoJSON output coordinate order is longitude, latitude, altitude. Original event
rows can share a timestamp at a phase transition; keep both. Display interpolation
must not redefine scientific events.

Job `completed` means a valid result was committed, including a physically
`stopped` trajectory. Only `result.complete` with `summary.landing` denotes
landing. Keep `landing:null`, stop reasons, and the final valid point when stopped;
an empty record list is also possible. `failed` means no committed result, not a
landing prediction. `n=1` does not define an ensemble distribution or probability.

`GET /api/v1/project` returns `{revision,project}`. Project schema is
`balloon.project/1`, with title, candidates (id, label, revision, source ID, config)
and `compare_run_ids` (committed result run IDs). The former two-candidate limit
was a 0.45 trial restriction and is removed. A candidate can carry `parent_id`
and a finite non-negative `delay_minutes`, either both present or both absent.
Parents must exist and cannot form cycles. These fields record the relationship;
they do not instruct the backend to resolve or rewrite physical inputs. The UI
materializes each child's full config and updates affected drafts together.
Immutable runs retain their own submitted inputs even when a parent is edited.
Candidates may also carry `sampling`; absent/null preserves the single-flight
route. Incomplete sampling drafts can be saved, while planning validates them
strictly. Optional `compare_results` holds typed single-run or fixed
ensemble-snapshot/case references, alongside the backward-compatible
`compare_run_ids`. Saving checks those references and any bound analysis.

Optional `ui_state` (default `{}` for old projects) stores finite JSON owned by
the screen layer: its schema, data-source namespaces, selection, comparison
groups, regions and view context. It is not an alternative result store or a
place for API keys. Real flight results remain fixed run references; artificial
screen data must remain distinguishable from them. Saving a view never submits
a calculation. `PUT` takes
`{expected_revision,project}` and rejects a stale revision with 409. Draft configs
can be incomplete. Saving a draft or changing compare selections never changes or
recalculates old runs. Duplicate run references are rejected. Selecting run IDs does not assert that their settings
are a scientifically controlled comparison.

## Fixed sensitivity ensembles

The user workflow is [COMMANDS C-09](../docs/COMMANDS.md).
The [implementation notes](../docs/IMPLEMENTATION_NOTES.md) describe storage and
the retained limits. `backend/ensemble/` separates request contracts, fixed
planning, shared-queue lifecycle, artifact storage and result views. Sampling and
statistical formulas remain in `balloon_sim/ensemble/`.

| API under `/api/v1` | Action |
|---|---|
| `GET /ensemble-capabilities` | Current deployment bounds and supported primitive variables. |
| `POST /ensemble-plans`, `GET /ensemble-plans/{id}` | Freeze/read explicit sampling, candidate inputs, resolved draws, field and source identities. |
| `POST /ensembles` | Explicitly submit the fixed plan and its hash with a request ID. |
| `GET /ensembles`, `GET /ensembles/{id}` | Read the ensemble and every planned trial state. |
| `POST /ensembles/{id}/cancel` or `/retry` | Request cancellation or retry with an idempotent request ID. |
| `GET /ensemble-snapshots/{id}` and its case/trial routes | Reopen a fixed epoch and obtain compact trials or original committed histories. |
| `POST /ensemble-analyses`, `GET /ensemble-analyses/{id}` | Fix/read an analysis of caller-selected trial IDs and selection provenance. |

The first route accepts one of gas mass, altitude-based burst height, or rated
descent speed only when that primitive is active in the selected model. The
uniform bounds, unit, reason, seed and trial count are explicit. It supplies no
calibrated product distribution or weather-error model. Corresponding conditions
share realized primitive values and draw IDs; changing the distribution requires
a new plan. Time support is checked before acceptance, but spatial and vertical
flight support is still determined by the kernel.

The deployment admits at most 256 total trials across a plan and four active
ensembles, through the existing flight dispatcher and worker. These are resource
limits, not scientific sample-size recommendations. Every planned trial remains
in the ledger: invalid input, unstarted work, failure, interruption and physical
stops must not disappear from the denominator or be replaced by new draws.
Cancellation prevents further starts and allows already running work to finish.
Explicit retry preserves the old snapshot and fixed draws, recovers any verified
committed artifact first, and submits only eligible unfinished/failed attempts.
New work requires the original field and checked source/environment identity;
saved result/analysis reads do not require the original field.

The overview separates planned, completed and landed counts. The server analyzes
selected IDs; forbidden-region membership is supplied by the frontend classifier
with its provenance and is not independently certified by the server. Changing a
region can therefore request a new fixed selection analysis without recalculating
flights. Above the 64 MiB aggregate raw-history JSON analysis limit, landing
statistics remain available and history omission is explicit; this limit is not
an RSS guarantee and does not delete stored histories.

Since 0.49 the frozen `source_snapshot.environment` records the Python version
and implementation, NumPy, SciPy and GeographicLib. The ensemble runtime guard
compares that installed subset; DuckDB is recorded separately in the climate
analysis identity. Source and field hashes plus this subset must not be
described as a complete dependency-environment fingerprint.

## Forecast acquisition and its separate lifetime

The actual service branch is `backend/weather/`:

- `contracts.py`: bounded HTTP request shapes; no external URL or file-path input.
- `catalog.py`: fixed-origin NOMADS directory observations; filenames are evidence
  of observed availability, not accepted GRIB contents.
- `planning.py`: candidate time-window union, WGS84 center/half-width conversion,
  native GFS bracketing, memory estimate, dependency and decoder identity.
- `service.py`: durable plans, one acquisition worker, cancellation/retry,
  completed-asset registration and hash-verified reuse. Numerical decoding stays
  in `balloon_sim.environment.gfs`, and CLI/API share its NOMADS gateway.

| API under `/api/v1` | Action |
|---|---|
| `POST /weather-inventories/refresh` | Explicit bounded provider observation; `{run_utc:null,run_limit:2}` observes recent listed runs, or set a fixed run. |
| `GET /weather-inventories`, `GET /weather-inventories/{id}` | Saved snapshots; no HTTP to the provider. |
| `POST /weather-plans`, `GET /weather-plans/{id}` | Persist/read an immutable fixed-run acquisition plan. |
| `POST /weather-acquisitions` | Submit `{plan_id,client_request_id}`. |
| `GET /weather-acquisitions`, `GET /weather-acquisitions/{id}` | Read progress without provider polling. |
| `POST /weather-acquisitions/{id}/cancel` or `/retry` | Cooperative cancellation or explicit retry; body `{}`. |
| `GET /weather-status` | Local dependency availability and queue limits. |

A plan takes `inventory_id`, `run_utc`, `region`, `candidate_windows`, optional
`end_margin_s`, `max_bytes` (default/cap 50,000,000), and `max_memory_bytes`
(default 256 MiB, cap 512 MiB). Region is either
`{kind:bounds,west,east,south,north}` or
`{kind:center,latitude_deg,longitude_deg,half_width_km,half_height_km}`. The latter
uses WGS84 cardinal destinations to define a latitude/longitude rectangle, then
rounds outward to the 0.25 degree grid; it is not an equal-width distance buffer.
Each candidate window contains `candidate_id`, explicit UTC `launch_time_utc`,
`latitude_deg`, `longitude_deg`, and the candidate's actual `max_duration_s`. The
plan records each launch location against the rounded acquisition bounds. An
outside point adds `LAUNCH_OUTSIDE_REGION` and makes the plan unavailable; planning
does not silently enlarge the requested region. All parent/delay windows must be
included when preparing one shared field. Unsupported seams reject explicitly.

`status:ready` means acquisition is admissible, not that an entire future flight
has been spatially or vertically verified. Missing listed leads, dependencies and
excess estimated decoded memory produce `status:unavailable` with `issues`, while
still returning the normalized bounds/window and estimate. Malformed requests
return 422. There is no automatic older-run fallback. A fresh explicit observation
and plan are required to select another initialization or change an unavailable plan.
New acquisition acceptance and explicit retry revalidate the fixed launch-inclusion
evidence. Older plans without the now-required coordinates/evidence return
`PLAN_REPLAN_REQUIRED`; their GET, already accepted request-ID readback and
completed assets remain available.

The weather registry lives in `BALLOON_DATA_DIR/weather/registry.sqlite3`.
`inventories/<id>/` retains original HTML responses, their metadata, the fixed
inventory manifest or a failure record. Plans recheck those saved response hashes.
`acquisitions/<id>/` retains the fixed request, decoder identity, raw files,
provenance, partial failures and the normalized bundle. Only a verified receipt
and complete `ASSET.json` permit registration. Marker writing uses a separate
partial file then atomic rename, so interruption does not expose a truncated
completion marker. Raw acquisition verification and resume are owned by the GFS adapter.

One acquisition runs at a time, with at most four waiting. Flight calculation has
its own worker. Cancellation can remain `cancelling` until the current operation
cooperates. Restart turns unfinished acquisitions into `interrupted`; it never
automatically reconnects. Retry retains the prior attempt and rechecks the fixed
decoder/plan and available raw files. A matching active job prevents a duplicate
download; a complete matching asset is reused only after hash verification.
Reused progress reports complete file counts, zero new download bytes, saved raw
bytes as `bytes_reused`, and normalized gzip size separately as `bundle_bytes_reused`.

The shared NOMADS gateway enforces the provider interval across these local API
and CLI processes. Refresh can therefore take tens of seconds. Download volume is
bounded, not known exactly in advance. The conservative decoded-memory estimate
is admission control rather than measured RSS. Completion adds a source to the
selector; applying it to a candidate remains a separate explicit UI operation.
Existing fixed runs retain their original source and input. Keep completed assets
to enable rerunning; reopening a committed result does not require provider access.

The application fixes its Python source/numerical-environment snapshot at startup.
New inventory observation, planning, acquisition submission and retry compare the
current files with that snapshot; the acquisition worker repeats this check during
progress and around completion. A mismatch returns/fails with `SOURCE_CHANGED`,
retains diagnostic inputs, and prevents a new completed asset from being registered.
Restart the application after editing Python source; there is no hot-reload workflow.
Saved GET requests, cancellation and readback of an already accepted request ID
remain available. This detects observable disk/environment drift after startup;
it is not atomic filesystem locking or proof against a change-and-restore between
checks. It avoids assigning new on-disk source hashes to work knowingly continuing
under an older running application.

## Saved JRA source and fixed-result identity (0.53 connection retained)

`ApplicationService._load_sources` registers `jra3q-surface-fixture` from the declared
`jra3q-weather.json.gz` and `jra3q-ground-flight.json` example. The schema is
`balloon.weather.jra3q_surface/1`, with product
`jra3q.ncar.regular_gaussian.model_surface_analysis`. Registration uses `load_weather`
and checks the bundle hash before/after reading. The snapshot records validated
effective metadata, including the explicit B reconstruction policy. It has
`time_kind:analysis_valid_utc`, `run_utc:null` and no forecast lead. Its
`bounds.model_level:[1,100]` identifies native levels; there is no fixed
`pressure_pa` axis and these level IDs are not an altitude-support guarantee.

The same worker loads the field, runs the existing kernel and exports the actual
`weather.metadata`. This aligns the metadata boundary with the CLI without adding
another solver or acquisition branch. GFS acquisition remains in `backend/weather`;
this registration is not an arbitrary JRA path/URL or past-date download API.

Missing or invalid sources at startup appear in `source_errors`; selecting an
unregistered ID returns 422 `UNKNOWN_WEATHER_SOURCE`. If a registered path becomes
unreadable, a new submission returns 409 `WEATHER_UNAVAILABLE`; a changed hash
returns 409 `WEATHER_CHANGED`. Neither invalidates a committed result. Result GET
checks its saved artifact and does not reload the original weather bundle.

Source IDs alone do not establish byte identity across restarts. The GUI comparison
uses the current catalogue identity and the fixed run/case weather snapshot, while
retaining old project references. Matching input, observed weather changes, current
weather unavailability and insufficient legacy identity information are distinct.
`unverified` does not mean changed; current weather `unavailable` does not mean a
saved result GET returned 404 (`missing`). A catalogue refresh must not rewrite old
result metadata or silently create a new run. The fixed frontend candidate uses `weatherIdentity / weatherMatch` and
`runWeatherSnapshot`; actual observed UI states and untested states remain separately recorded in S36.

The 0.53 connection above used one saved analysis window. Model terrain, the provisional surface bridge,
and B interpolation are the existing 0.52 choices, not new accuracy claims. It does
not itself connect half-month wind statistics to original-date field selection or implement
seasonal weather ensembles. The 0.55 route below adds explicit original-date windows
without changing that scientific limit. The candidate GUI steps are in COMMANDS C-09; the retained
CLI reference is C-11. Actual tests, numerical comparisons and UI observations belong
in S36, with test boundaries distinct from this specification.

## Explicit original-date windows (0.55)

`BALLOON_HISTORICAL_CATALOG` is an operator-supplied local JSON path used at startup,
not an HTTP path/URL input. Schema `balloon.historical-catalog/1` lists at most 256
unique `historical-` source IDs, label, bundle path, expected SHA256 and optional
`default_config`; relative bundle paths resolve beside the catalogue. Only the
existing original-UTC JRA model-field schemas are accepted. Registration checks
bytes before/after loading and isolates unavailable entries in `source_errors`.
Catalogue-level corruption does not invalidate already committed results.

`POST /ensemble-plans` also accepts `mode:historical_windows`, request ID, label,
reason, optional `selection_context`, common vehicle `cases`, and explicit
`windows` (`window_id`, label, optional `weather_source_id`, `launch_time_utc`,
selection reason). Each window owns the launch UTC; forecast delay-parent fields
are rejected in this mode. Case IDs, candidate IDs, window IDs and original UTCs
must be unique within their applicable sets. Total cases times windows is at most
256. Registered fields must identify `analysis_valid_utc`; forecasts and aggregate
statistics are not accepted as original analysis windows.

Every selected window stays in the equal-weight trial ledger. Unregistered fields
and unsupported launch origins/full declared time windows remain invalid rows,
not new draws. At least one runnable row is needed for a ready plan. Execution
freezes each row's actual weather identity and reuses the existing worker; a changed
registered asset stops the fixed plan rather than selecting another field. Fixed
case results retain `mode`, `weather_windows` and `selection_context`. Their trial
`parameter` is null and `weather_window` identifies the original field/time, so no
invented equipment draw or calibrated weather-error distribution is implied.

These selected dates are not a representative seasonal population or a probability
forecast for a future July. Statistical interest and original-date field selection
are separate; the climate summary is never passed to the flight kernel as a field.

## Finite checks

```powershell
backend/.venv/Scripts/python -B -m pytest backend/tests -p no:cacheprovider
```

Tests use offline saved weather and temporary state. They exercise the real
spawn worker, physical stops, idempotency, persistence, draft/result separation,
finite queue and cancellation, restart interruption, artifact integrity and API
validation. Ensemble tests additionally cover fixed draws, the complete trial
ledger, shared-queue execution, cancel/retry, committed-artifact recovery and
immutable snapshots/selection analysis. These checks do not establish model
accuracy or complete past-weather, seasonal or calibrated uncertainty workflows.
Weather-service tests inject a directory gateway and a declared saved-field
acquirer. They exercise persistence, missing native leads, full time windows,
memory/dependency admission, partial failure/retry, cancellation, cache identity,
completion-marker interruption and acquisition-to-real-worker wiring. They do not
claim a fresh network download; transport/GRIB tests and bounded live observations
are recorded separately.

## Saved climate analyses (0.49–0.58)

Point-selection update and source review: 0.57.0, 2026-10-02. This check covers the climate query, archive/legacy distinction and saved-output boundaries below; it is not a recheck of every backend feature.

`GET /api/v1/climate-sources`, `POST /api/v1/climate-analyses` and `GET /api/v1/climate-analyses/{id}` connect the independent `backend/climate` service. The POST freezes resolved source/level/bounds and any explicit rose point, data/code/statistics/runtime identity and result hash in a separate `climate.sqlite3`. A null request bounds means that source's full native extent; the artifact records the resolved bounds while the request-ID binding retains the original query. Repeating that ID with identical input returns the accepted artifact, and changed input conflicts. Saved GET needs neither the original DB nor the raw bundle and does not recalculate. The query lock is separate from the flight lock. The frontend saves fixed references under `ui_state.weather_real`, retaining unapplied draft inputs separately.

### Original-UTC archives (0.57)

Set `BALLOON_CLIMATE_ARCHIVES` before startup to a JSON array of up to eight absolute manifest paths. Each `balloon.wind-samples/1` bundle is a separate source; the service checks all twelve complete calendar months, UTC/level/grid axes, finite Float32 u/v arrays and their byte hashes. The current target is JRA-3Q 2024 at 38 levels/570 native cells and ERA5 2024 at 37 levels/1,188 native cells, each using 00/06/12/18 UTC. An incomplete acquisition is not an annual source. The source's fixed years are not an implemented year-subset filter. The supplied 2016–2025 DB can coexist; a new archive does not replace its source identity or rewrite old saved results. `BALLOON_CLIMATE_SAMPLES` is instead an optional companion bound to that old DB's exact years/grid/levels, not a slot for a different 2024 product.

ERA acquisition now accepts explicit `--transport ncss` as well as the default `dods`; the analysis service does not start either downloader. NCSS reads the same NCAR pressure-level source through original NetCDF3 responses, with native Float32 U/V, axes, units, UTC and fill checks. `--resume` retains verified DODS responses, failed-attempt receipts and matching completed-month checkpoints; new NCSS bytes have separate receipts and manifest provenance. There is no automatic service fallback or retry-budget reset. The documented full-year command requests months 1–12 with one worker, a 120-second socket timeout and two cumulative attempts per NCSS request; see [COMMANDS](../docs/COMMANDS.md#公開元から原標本を再取得するcli). The two finite V probes establish native-bit agreement with DODS for January 1 and valid native support for April 25 only; U and the whole year are not covered by that comparison. The complete-year original-response-to-array checks are separate from this two-probe transport comparison; see the final receipts in S36. Data DOI/license, modified Copernicus attribution and provider responsibility remain attached to the source; [WEATHER](../docs/WEATHER_DATA_GUIDE.md) and [S36](../BOOTSTRAP_RUNBOOK.html#s36-era-ncss-plan570) hold the evidence boundaries and progress.

Archive analyses use native area weights and equal selected UTC times. `monthly_profiles` contains the two half-month medians and the whole-month p10–p90 weighted empirical inverse-CDF band from original scalar speeds. This is a grid-by-time mixture, not the time distribution of a regionally averaged wind. Means remain supplementary. All acquired archive levels support UTC subsets; the selected native-point rose uses those hours, with calm counts retained separately. UTC day 1–15/16–month-end boundaries remain UTC under JST labels. Data/code identity includes NumPy for sample calculations; a previously accepted request still returns its fixed artifact before consulting the current source.

Raw descriptors advertise `wind_rose_point_select:true`. Optional `rose_cell_id` is a nonnegative integer ID in that source’s native grid, not an array index; booleans, non-integers and unknown IDs are rejected. Omission/null preserves the old query bytes and default point, with no default ID inserted into the query. The descriptor retains its default `wind_rose_point`; each result records the effective `wind_rose.point` and whether it lies in the selected region. An outside point is allowed. Point-only requests reuse regional moments/profile caches and leave regional median bands and means unchanged. The one-point rose denominator is the selected UTC count, not a grid-weighted regional distribution.

The frontend sends point changes as a separate apply kind through the same one-active/latest-pending queue as pressure exploration. It changes only the displayed artifact’s point, retains unapplied region/UTC/pressure drafts and disables pressure exploration while the point request is pending. Earlier pressure responses cannot replace the selected point. A raw artifact saved before this feature can start an explicit point request when the same source ID is currently registered with the capability and selected in the draft; the old artifact itself remains immutable. Saved GET/retry retain the fixed point without requiring the archive. SVG content and the prepared-download conditions retain the captured point ID/coordinates until another SVG is successfully generated.

Only pressure-level u/v are acquired in this path. Temperature, humidity, actual heights and surface fields are absent; ISA altitude is a reference axis. Twelve months of complete wind samples are not a complete flight weather field, and one year does not establish multi-year representativeness or forecast-error probabilities. Full-region archives remain local outside the repository. The included small Git demo selects only 2×2 original cells per product while retaining the same times and pressure levels; it supports functional reproduction, not regional climatological representativeness. Current package availability and acquisition progress remain in S36.

Use [COMMANDS: original-sample analysis](../docs/COMMANDS.md#C-CLIMATE-RAW) for extraction/CLI registration, explicit source and region/UTC choice, pressure exploration of the displayed fixed population, the SVG preparation/download steps and saved reopening. The analysis service does not call the acquisition tools or accept browser paths/URLs/SQL. [WEATHER_DATA_GUIDE](../docs/WEATHER_DATA_GUIDE.md) defines product support and attribution, [IMPLEMENTATION_NOTES](../docs/IMPLEMENTATION_NOTES.md) owns the API/storage boundaries, and [THEORY](../docs/THEORY_GUIDE.pdf) defines weights and distributions.

### Supplied ten-year database (0.49 connection, 0.56 extensions)

The optional `BALLOON_CLIMATE_DB` points to the supplied JRA-3Q Hokkaido v1 DuckDB outside the repository. `BALLOON_CLIMATE_SHA256` may pin its expected bytes. DuckDB 1.5.5 is locked; the source is read-only and has no HTTP path/SQL input. Startup inspects the fixed profile (2016–2025, UTC 00/06/12/18, 24 half-month bins, 38 levels and 570 native cells). These aggregated moments are not a continuous flight WeatherField. Unsupported year/hour masks and raw-observation quantiles are not fabricated.

The query keeps `grain: "half"`; optional `hours_utc` accepts a nonempty, duplicate-free subset of integer `0/6/12/18`. Ordering is normalized; explicit all-four and omission/null have the same identity. With all hours, the source supports 38 pressure levels (3–1000 hPa); a subset uses only the 20 supplied diurnal levels (300–1000 hPa). Unsupported hourly levels return `CLIMATE_HOUR_SUPPORT` rather than silently reverting to all hours. Year filters and non-native hourly interpolation remain unsupported.

`climate-summary/1` retains its half-month fields and adds `summaries_by_grain.month` and `.season`, each containing `timebins`, `annual`, `spatial_rows`, `display_scales` and `wind_rose`. Per-cell means are pooled by source `n` before Gaussian spatial weighting; directions and constancy are recomputed from pooled u/v/scalar speed. Months and seasons use the UTC calendar even when the hour labels are JST. DJF pools the included Dec/Jan/Feb observations, not ten contiguous winters. The frontend keeps each chart's grain in its saved view rather than sending a new query for a display-only change.

The empirical wind rose uses one fixed native cell (285; 43.267398834228516 N, 143.625 E), all four hours and the selected level. Period counts are summed over the original 16 FROM-direction sectors and six speed classes; `frequency=count/sum(n)`. It is not a regional distribution. This legacy DB does not advertise point selection and rejects any non-null `rose_cell_id` with `CLIMATE_UNSUPPORTED`. `point_in_selected_region` identifies an out-of-region point without inventing another distribution. Hour subsets return `available:false` with `hour_subset_not_available`; absent rose tables report `source_has_no_wind_rose`. A 0–5 m/s class is not a separate calm category, and 50+ has no finite upper bound.

For the supplied DB, artifact/storage schemas remain `/1`; adapter/statistics identities are `jra3q-halfmonth-summary/3` and `gaussian-pooled-wind/3`. Old artifacts can still be hash-verified and read without their source. Missing month/season/rose fields are not synthesized and old saved results are not overwritten by a new adapter. Optional tables may be absent, but malformed present tables fail registration. Original quantiles/covariances/fitted distributions remain potential source material; this adapter does not pool quantiles or fit parameters into new empirical distributions.

The visualizations consume the fixed summary through a dedicated adapter; they do not convert it to invented raw samples. Exact commands, API failure boundaries and statistical definitions are maintained in `docs/COMMANDS.md`, `docs/IMPLEMENTATION_NOTES.md` and `docs/THEORY_GUIDE.pdf`. Actual validation and costs are in S36; the connection does not certify flight accuracy or seasonal trajectory support. The worker runtime fingerprint now includes GeographicLib; DuckDB identity is recorded by the climate path separately.
