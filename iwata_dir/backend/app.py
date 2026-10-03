"""FastAPI transport and optional built frontend; no scientific computation here."""
from contextlib import asynccontextmanager
import os
from pathlib import Path

from fastapi import FastAPI, Request, Query
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .application import ApplicationService, ServiceError
from .contracts import ProjectUpdate, RunRequest
from .worker import REPO_ROOT
from .weather.contracts import AcquisitionRequest, InventoryRefresh, WeatherPlanRequest
from .ensemble.contracts import AnalysisRequest, CancelRequest, HistoricalPlanRequest, PlanRequest, RetryRequest, SubmitRequest
from .ensemble.planning import capabilities
from .climate.service import ClimateServiceError


def create_app(data_dir=None, *, weather_options=None, climate_options=None):
    service = ApplicationService(data_dir, weather_options=weather_options, climate_options=climate_options)

    @asynccontextmanager
    async def lifespan(app):
        service.start()
        try:
            yield
        finally:
            service.close()

    app = FastAPI(title="Balloon Simulator local application", version="0.58.0", lifespan=lifespan)
    app.state.service = service

    @app.middleware("http")
    async def json_mutations(request: Request, call_next):
        expected_instance = request.headers.get("X-Balloon-Instance-Id")
        if (request.url.path.startswith("/api/v1/") and request.url.path != "/api/v1/health"
                and expected_instance is not None and expected_instance != service.instance_id):
            return JSONResponse(status_code=409, content={"error": {"code": "INSTANCE_MISMATCH", "message": "The saved service instance differs from this request. Keep the original intent; inspect the connected state before continuing."}})
        if request.url.path.startswith("/api/") and request.method in {"POST", "PUT"}:
            content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
            if content_type != "application/json":
                return JSONResponse(status_code=415, content={"error": {"code": "JSON_REQUIRED", "message": "Use application/json."}})
        return await call_next(request)

    @app.exception_handler(ServiceError)
    async def service_error(request: Request, exc: ServiceError):
        return JSONResponse(status_code=exc.status, content={"error": {"code": exc.code, "message": str(exc)}})

    @app.exception_handler(ClimateServiceError)
    async def climate_error(request: Request, exc: ClimateServiceError):
        return JSONResponse(status_code=exc.status_code, content={"error": {"code": exc.code, "message": str(exc)}})

    @app.get("/api/v1/health")
    def health():
        execution = service.execution_status()
        return {"status": "ok" if execution["available"] else "degraded", "version": "0.58.0",
                "workers": 1, "max_queued": service.max_queued, "flight_execution": execution,
                "instance_id": service.instance_id}

    # Synchronous routes run in FastAPI's threadpool. Climate aggregation never
    # acquires the flight service lock or blocks the ASGI event loop.
    @app.get("/api/v1/climate-sources")
    def climate_sources():
        return service.climate.sources()

    @app.post("/api/v1/climate-analyses", status_code=201)
    def climate_analysis(body: dict):
        return service.climate.create_analysis(body)

    @app.get("/api/v1/climate-analyses/{identity}")
    def climate_analysis_saved(identity: str):
        return service.climate.get_analysis(identity)

    @app.get("/api/v1/ensemble-capabilities")
    def ensemble_capabilities():
        return capabilities()

    @app.post("/api/v1/ensemble-plans", status_code=201)
    def plan_ensemble(request: PlanRequest | HistoricalPlanRequest):
        return service.ensemble.plan(request.model_dump())

    @app.get("/api/v1/ensemble-plans")
    def ensemble_plans():
        return service.ensemble.list_plans()

    @app.get("/api/v1/ensemble-plans/{identity}")
    def ensemble_plan(identity: str):
        return service.ensemble.get_plan(identity)

    @app.post("/api/v1/ensembles", status_code=202)
    def submit_ensemble(request: SubmitRequest):
        return service.ensemble.submit(request.model_dump())

    @app.get("/api/v1/ensembles")
    def ensembles():
        return service.ensemble.list()

    @app.get("/api/v1/ensembles/{identity}")
    def ensemble(identity: str):
        return service.ensemble.get(identity)

    @app.get("/api/v1/ensembles/{identity}/trials")
    def ensemble_trials(identity: str, case_id: str | None = None,
                        offset: int = Query(default=0, ge=0), limit: int = Query(default=256, ge=1, le=256)):
        return service.ensemble.trials(identity, case_id, offset, limit)

    @app.post("/api/v1/ensembles/{identity}/cancel")
    def cancel_ensemble(identity: str, request: CancelRequest):
        return service.ensemble.cancel(identity, request.model_dump())

    @app.post("/api/v1/ensembles/{identity}/retry", status_code=202)
    def retry_ensemble(identity: str, request: RetryRequest):
        return service.ensemble.retry(identity, request.model_dump())

    @app.get("/api/v1/ensemble-snapshots/{identity}")
    def ensemble_snapshot(identity: str):
        return service.ensemble.snapshot(identity)

    @app.get("/api/v1/ensemble-snapshots/{identity}/cases/{case_id}")
    def ensemble_case(identity: str, case_id: str):
        return service.ensemble.case_result(identity, case_id)

    @app.get("/api/v1/ensemble-snapshots/{identity}/trials/{trial_id}/result")
    def ensemble_trial_result(identity: str, trial_id: str):
        return service.ensemble.trial_result(identity, trial_id)

    @app.post("/api/v1/ensemble-analyses", status_code=201)
    def ensemble_analysis(request: AnalysisRequest):
        return service.ensemble.analyze(request.model_dump())

    @app.get("/api/v1/ensemble-analyses/{identity}")
    def saved_ensemble_analysis(identity: str):
        return service.ensemble.analysis(identity)

    @app.get("/api/v1/weather-sources")
    def weather_sources():
        return service.weather_sources()

    @app.get("/api/v1/weather-sources/{identity}/ground")
    def weather_ground(identity: str,
                       expected_sha256: str = Query(pattern=r"^[0-9a-f]{64}$"),
                       time_utc: str = Query(),
                       latitude_deg: float = Query(gt=-90, lt=90, allow_inf_nan=False),
                       longitude_deg: float = Query(ge=-180, le=180, allow_inf_nan=False),
                       launch_altitude_m: float = Query(gt=-6371000, allow_inf_nan=False)):
        return service.weather_ground(identity, {
            "expected_sha256": expected_sha256, "time_utc": time_utc,
            "latitude_deg": latitude_deg, "longitude_deg": longitude_deg,
            "launch_altitude_m": launch_altitude_m})

    @app.get("/api/v1/weather-status")
    def weather_status():
        return service.weather.status()

    @app.post("/api/v1/weather-inventories/refresh")
    def refresh_weather_inventory(request: InventoryRefresh):
        return service.weather.refresh_inventory(request.model_dump())

    @app.get("/api/v1/weather-inventories")
    def weather_inventories():
        return service.weather.list_inventories()

    @app.get("/api/v1/weather-inventories/{identity}")
    def weather_inventory(identity: str):
        return service.weather.get_inventory(identity)

    @app.post("/api/v1/weather-plans", status_code=201)
    def plan_weather(request: WeatherPlanRequest):
        return service.weather.plan(request.model_dump())

    @app.get("/api/v1/weather-plans/{identity}")
    def weather_plan(identity: str):
        return service.weather.get_plan(identity)

    @app.post("/api/v1/weather-acquisitions", status_code=202)
    def acquire_weather(request: AcquisitionRequest):
        return service.weather.submit(request.model_dump())

    @app.get("/api/v1/weather-acquisitions")
    def weather_acquisitions():
        return service.weather.list_jobs()

    @app.get("/api/v1/weather-acquisitions/{identity}")
    def weather_acquisition(identity: str):
        return service.weather.get_job(identity)

    @app.post("/api/v1/weather-acquisitions/{identity}/cancel")
    def cancel_weather(identity: str):
        return service.weather.cancel(identity)

    @app.post("/api/v1/weather-acquisitions/{identity}/retry", status_code=202)
    def retry_weather(identity: str):
        return service.weather.retry(identity)

    @app.post("/api/v1/runs", status_code=202)
    def submit(request: RunRequest):
        return service.submit(request.model_dump())

    @app.get("/api/v1/runs")
    def runs(include_ensemble: bool = False):
        return service.list_runs(include_ensemble)

    @app.get("/api/v1/run-requests")
    def run_request(client_request_id: str = Query(min_length=1, max_length=128)):
        return service.get_run_request(client_request_id)

    @app.get("/api/v1/runs/{run_id}")
    def run(run_id: str):
        return service.get_run(run_id)

    @app.get("/api/v1/runs/{run_id}/result")
    def result(run_id: str):
        return service.get_result(run_id)

    @app.post("/api/v1/runs/{run_id}/cancel")
    def cancel(run_id: str):
        return service.cancel(run_id)

    @app.get("/api/v1/project")
    def project():
        return service.get_project()

    @app.put("/api/v1/project")
    def save_project(request: ProjectUpdate):
        return service.save_project(request.model_dump(by_alias=True))

    dist = Path(os.environ["BALLOON_FRONTEND_DIST"]).expanduser().resolve() if os.environ.get("BALLOON_FRONTEND_DIST") else REPO_ROOT / "frontend" / "dist"
    if (dist / "index.html").is_file():
        for name in ("assets", "scene3d", "cesium"):
            if (dist / name).is_dir():
                app.mount("/" + name, StaticFiles(directory=dist / name, html=True), name=name)

        @app.get("/")
        def index():
            return FileResponse(dist / "index.html")
    else:
        @app.get("/", response_class=HTMLResponse)
        def not_built():
            return "<h1>Frontend is not built</h1><p>Run npm ci and npm run build in frontend, then restart this server.</p><p>API: <a href='/docs'>/docs</a></p>"
    return app
