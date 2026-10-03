"""Orchestrate one flight, retaining support failures and accepted records.

Depends on weather's sample/ground_altitude protocol rather than a product,
filesystem or network implementation. Models own physical evaluations; numerical
kernels own trial arithmetic. This driver owns phases, event priority and results.
"""
from copy import deepcopy
from datetime import timedelta
import math
from .config import FlightError, validate_config, _number, _utc, EARTH_RADIUS_M
from .models import compile_models
from .numerics import AdaptiveRK45, locate_crossing, numerical_metadata

def _longitude(value):
    return (value + 180) % 360 - 180


def simulate(config, weather):
    """Integrate ascent, burst and descent using SciPy RK45 and dense event roots.

    A stopped result preserves accepted records and carries the original weather
    failure code.  Only a located ground intersection during descent is complete.
    RK stage queries below ground are evaluated at the local ground solely to
    continue the mathematical event bracket.  No below-ground point is accepted.
    Finite steps can miss terrain features narrower than the sampled trajectory;
    step refinement and terrain resolution remain required for operational use.
    """
    c = validate_config(config)
    models = compile_models(c)
    launch = c["launch"]
    start = _utc(launch["time_utc"])
    controls = c["integration"]
    tolerance = controls["event_tolerance_s"]
    records, events = [], []
    stage_clamps = 0
    accepted_steps = 0
    state = (launch["latitude_deg"], launch["longitude_deg"], launch["altitude_m"])
    elapsed = 0.0
    phase = "ascent"
    stop_reason = None

    def stamp(t):
        return start + timedelta(seconds=t)

    def ground(t, y):
        value = weather.ground_altitude(stamp(t), y[0], _longitude(y[1]))
        try:
            return _number(value, "ground_altitude_m")
        except FlightError as exc:
            raise FlightError("INVALID_WEATHER", str(exc)) from None

    def sample_at(t, y, current_phase, allow_ground_clamp=False):
        nonlocal stage_clamps
        if not all(math.isfinite(v) for v in y) or abs(y[0]) >= 90 or y[2] <= -EARTH_RADIUS_M:
            raise FlightError("NUMERIC_UNSUPPORTED", "state leaves spherical coordinate domain")
        terrain = ground(t, y)
        height = y[2]
        clamped = height < terrain
        if clamped and not allow_ground_clamp:
            raise FlightError("BELOW_GROUND", "accepted state would lie below terrain")
        if clamped:
            height = terrain
            stage_clamps += 1
        fields = list(models.phase(current_phase).required_fields)
        sample = weather.sample(stamp(t), y[0], _longitude(y[1]), height, fields=fields)
        if not isinstance(sample, dict):
            raise FlightError("INVALID_WEATHER", "weather sample must be an object")
        for name in fields:
            if name not in sample:
                raise FlightError("MISSING_WEATHER_FIELD", name)
            try:
                _number(sample[name], name)
            except FlightError as exc:
                raise FlightError("INVALID_WEATHER", str(exc)) from None
        return sample, terrain, clamped

    def rhs(t, y, current_phase):
        sample, _, _ = sample_at(t, y, current_phase, True)
        radius = EARTH_RADIUS_M + y[2]
        cosine = math.cos(math.radians(y[0]))
        if abs(cosine) < 1e-8:
            raise FlightError("POLAR_SINGULARITY", "longitude derivative is singular near the pole")
        dz = models.phase(current_phase).evaluate(y[2], sample)["vertical_speed_m_s"]
        return (math.degrees(sample["northward_wind_m_s"] / radius),
                math.degrees(sample["eastward_wind_m_s"] / (radius * cosine)), dz)

    def burst_value(t, y):
        sample = None
        if models.burst.requires_sample:
            sample, _, _ = sample_at(t, y, "ascent", True)
        return models.burst.value(y[2], sample)

    def make_record(t, y, current_phase, event=None):
        sample, terrain, _ = sample_at(t, y, current_phase)
        physics = models.phase(current_phase).evaluate(y[2], sample)
        quality = sample.get("quality", [])
        if not isinstance(quality, list):
            raise FlightError("INVALID_WEATHER", "weather quality must be a list")
        point = {"time_utc": stamp(t).isoformat(), "elapsed_s": t,
                 "latitude_deg": y[0], "longitude_deg": _longitude(y[1]),
                 "altitude_m": y[2], "ground_altitude_m": terrain,
                 "height_agl_m": y[2] - terrain, "phase": current_phase,
                 "eastward_wind_m_s": sample["eastward_wind_m_s"],
                 "northward_wind_m_s": sample["northward_wind_m_s"],
                 "weather_quality": deepcopy(quality), **physics}
        for key in ("pressure_pa", "temperature_k", "specific_humidity_kg_kg",
                    "surface_bridge_height_m", "terrain_stencil_clamp_depth_m"):
            if key in sample:
                point[key] = sample[key]
        if event:
            point["event"] = event
        return point

    def accept(t, y, current_phase, event_name=None, event_detail=None, *, count_step=True):
        """Commit only a fully validated point and its matching event together."""
        nonlocal elapsed, state, phase, accepted_steps
        point = make_record(t, y, current_phase, event_name)
        elapsed, state, phase = t, y, current_phase
        if count_step:
            accepted_steps += 1
        records.append(point)
        if event_detail is not None:
            events.append(event_detail)

    def failure(exc):
        return {"code": getattr(exc, "code", "WEATHER_ERROR"), "message": str(exc),
                "elapsed_s": elapsed, "time_utc": stamp(elapsed).isoformat()}

    def make_burst_event(t, y):
        event = {"type": "burst", "elapsed_s": t, "time_utc": stamp(t).isoformat(),
                 "latitude_deg": y[0], "longitude_deg": _longitude(y[1]), "altitude_m": y[2]}
        sample = None
        if models.burst.has_diagnostics:
            sample, _, _ = sample_at(t, y, "ascent")
        event.update(models.burst.diagnostics(sample))
        return event

    integrator = AdaptiveRK45(lambda time, state: rhs(time, state, phase),
                              controls["max_duration_s"],
                              relative_tolerance=controls["relative_tolerance"],
                              absolute_tolerance=[controls["absolute_tolerance"][name]
                                  for name in ("latitude_deg","longitude_deg","altitude_m")])
    try:
        if state[2] < ground(0, state):
            raise FlightError("LAUNCH_BELOW_GROUND", "launch height is below selected terrain")
        accept(0, state, phase, "launch", count_step=False)
        if burst_value(0, state) >= 0:
            detail = make_burst_event(0, state)
            accept(0, state, "ascent", "burst", detail, count_step=False)
            accept(0, state, "descent", "burst", count_step=False)
            integrator.reset()
        while elapsed < controls["max_duration_s"] and accepted_steps < controls["max_steps"]:
            dt = min(controls["max_step_s"], controls["max_duration_s"] - elapsed)
            exact_altitude_burst_dt = None
            if phase == "ascent":
                exact_altitude_burst_dt = models.burst.exact_step(state[2])
                if exact_altitude_burst_dt is not None:
                    dt = min(dt, exact_altitude_burst_dt)
            if dt < 1e-6:
                raise FlightError("NUMERIC_UNSUPPORTED", "remaining step cannot resolve UTC microseconds")
            # A failed trial is never accepted. Smaller trials approach the actual
            # support boundary while preserving the provider's failure code.
            while True:
                try:
                    clamps_before = stage_clamps
                    trial = integrator.trial(elapsed, state, dt)
                    dt = trial.end_time - elapsed
                    if dt < 1e-6:
                        raise FlightError("NUMERIC_UNSUPPORTED", "adaptive step cannot resolve UTC microseconds")
                    candidate = trial.state
                    exact_burst_reached = (exact_altitude_burst_dt is not None and
                        math.isclose(dt,exact_altitude_burst_dt,rel_tol=1e-12,abs_tol=1e-9))
                    if exact_burst_reached:
                        # This constant-speed event time is analytical. Floating
                        # roundoff must not leave a sub-microsecond final ascent.
                        candidate = (candidate[0], candidate[1], models.burst.project_altitude(candidate[2]))
                    terrain_gap = candidate[2] - ground(elapsed + dt, candidate)
                    midpoint_time = elapsed + dt / 2
                    midpoint = trial.state_at(midpoint_time)
                    midpoint_gap = midpoint[2] - ground(midpoint_time, midpoint)
                    burst_crossed = phase == "ascent" and burst_value(elapsed + dt, candidate) >= 0
                    # A stage may detect terrain between two above-ground end
                    # states. Subdivide that interval rather than accept a jump
                    # over a detected ridge. Features not sampled remain a
                    # finite-step/resolution limitation.
                    if ((stage_clamps > clamps_before or midpoint_gap <= 0) and terrain_gap > 0
                            and dt > max(tolerance, 1e-6)):
                        dt /= 2
                        continue
                    break
                except (ValueError, KeyError, OverflowError, ArithmeticError) as exc:
                    if dt <= max(tolerance, 1e-6):
                        raise
                    dt /= 2
            hits = []
            if terrain_gap <= 0:
                terrain_value = lambda t, y: y[2] - ground(t, y)
                left = elapsed
                initial_contact = phase == "ascent" and terrain_value(elapsed,state) == 0
                if initial_contact:
                    # A zero launch gap is allowed only while departing ground.
                    # Brent would otherwise return the initial zero even when a
                    # later hillside is the actual descending crossing.
                    probe = min(trial.end_time, elapsed + max(1e-6,min(tolerance,dt/2)))
                    probe_gap = terrain_value(probe,trial.state_at(probe))
                    if probe_gap > 0:
                        left = probe
                        initial_contact = False
                if initial_contact:
                    delta, event_state = 0.0, state
                else:
                    delta, event_state = locate_crossing(trial, terrain_value, tolerance,start_time=left)
                hits.append((delta, "landing" if phase == "descent" else "terrain_collision", event_state))
            if burst_crossed:
                if exact_burst_reached:
                    delta, event_state = dt, candidate
                else:
                    delta, event_state = locate_crossing(trial, burst_value, tolerance)
                hits.append((delta, "burst", event_state))
            if hits:
                delta, event, event_state = min(hits, key=lambda item: item[0])
                event_time = elapsed + delta
                if event == "burst":
                    event_state = (event_state[0], event_state[1], models.burst.project_altitude(event_state[2]))
                    detail = make_burst_event(event_time, event_state)
                    # Reaching burst is a valid ascent result even if the next
                    # phase lacks required inputs. Preserve that actual point.
                    accept(event_time, event_state, "ascent", "burst", detail)
                    accept(event_time, event_state, "descent", "burst", count_step=False)
                    integrator.reset()
                else:
                    event_state = (event_state[0], event_state[1], ground(event_time, event_state))
                    detail = {"type": event, "elapsed_s": event_time, "time_utc": stamp(event_time).isoformat(),
                              "latitude_deg": event_state[0], "longitude_deg": _longitude(event_state[1]), "altitude_m": event_state[2]}
                    accept(event_time, event_state, phase, event, detail)
                    if event == "terrain_collision":
                        stop_reason = {"code": "TERRAIN_COLLISION", "message": "terrain intersects ascent", "elapsed_s": elapsed}
                    break
            else:
                accept(elapsed + dt, candidate, phase)
        else:
            code = "MAX_STEPS" if accepted_steps >= controls["max_steps"] else "MAX_DURATION"
            stop_reason = {"code": code, "message": "flight did not reach terrain within integration limits", "elapsed_s": elapsed}
    except (ValueError, KeyError, OverflowError, ArithmeticError) as exc:
        stop_reason = failure(exc)
    complete = bool(events and events[-1]["type"] == "landing" and stop_reason is None)
    return {"schema": "balloon.flight.result/1", "status": "landed" if complete else "stopped",
            "complete": complete, "stop_reason": stop_reason, "config": c,
            "numerics": numerical_metadata(controls),
            "records": records, "events": events,
            "summary": {"duration_s": records[-1]["elapsed_s"] if records else 0,
                        "maximum_altitude_m": max((row["altitude_m"] for row in records), default=None),
                        "accepted_steps": accepted_steps, "record_count": len(records),
                        "ground_clamped_stage_queries": stage_clamps,
                        "landing": deepcopy(events[-1]) if complete else None},
            "model_assumptions": ["horizontal motion equals east/north wind on a spherical Earth",
                "constant gravity 9.80665 m/s2; geometric ASL altitude",
                *models.assumptions(),
                "terrain is the selected environment surface; finite steps do not guarantee narrow-obstacle detection",
                "below-ground RK stage samples use local ground only to bracket a terminal event"]}
