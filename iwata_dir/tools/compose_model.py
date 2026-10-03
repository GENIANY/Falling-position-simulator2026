"""Resolve a selected model's inputs and reject contradictory composition.

Introduced in 0.18.0 for RPT-033 / D-148 / ENVIRONMENT_CONTRACT. This module
compiles declarations only: no force evaluation, coefficients, ODE solver,
weather acquisition, height conversion, or scientific acceptance. Each stage
owns one vertical dynamics family. Selected closures are a dependency graph,
not a list of mutually exclusive complete models. Required weather quantities
are compatible with the JRA adapter names; terrain remains a separate source.

Public entry: compose_model(spec, capabilities=None). The optional capability
check compares declared names and units ONLY. Actual coordinate/time support,
missing values and height conversion still need adapter/solver checks. Errors
have a stable code and input path. Results and inputs do not share mutable data.
The small closed catalogue is a candidate, to be revised alongside the first
force evaluator rather than grown into a general-purpose plugin framework.
Standard library only; tests/test_model_composition.py exercises dependencies
and counterexamples without evaluating balloon flight or accessing a network.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import math
from types import MappingProxyType


SCHEMA = "balloon.model.composition/1"
FIELD_UNITS = MappingProxyType({
    "pressure_pa": "Pa", "temperature_k": "K",
    "specific_humidity_kg_kg": "kg kg-1",
    "eastward_wind_m_s": "m s-1", "northward_wind_m_s": "m s-1",
    "geometric_vertical_wind_m_s": "m s-1",
})


class CompositionError(ValueError):
    """A rejected declaration, not a failed weather query or flight."""

    def __init__(self, code, path, message):
        self.code, self.path = code, path
        super().__init__(f"{code} at {path}: {message}")


@dataclass(frozen=True)
class Component:
    """Immutable dependency description; parameter units are part of the ID contract."""

    provides: tuple[str, ...]
    requires: tuple[str, ...] = ()
    fields: tuple[str, ...] = ()
    parameters: tuple[str, ...] = ()


# No coefficients are evaluated or supplied here. Values must be supplied in
# stage.parameters; accepting their shape does not endorse their applicability.
_COMPONENTS = MappingProxyType({
    "rate.constant": Component(("rate",), parameters=("vertical_rate_m_s",)),
    "rate.tawhiri_legacy": Component(("rate",), parameters=("descent_reference_speed_m_s",)),
    "rate.reference_density": Component(("rate",), ("density",),
                                        parameters=("descent_reference_speed_m_s", "reference_density_kg_m3")),
    "density.legacy_altitude": Component(("density",)),
    "density.dry": Component(("density",), fields=("pressure_pa", "temperature_k"),
                             parameters=("dry_air_gas_constant_j_kg_k",)),
    "density.moist": Component(("density",), fields=("pressure_pa", "temperature_k", "specific_humidity_kg_kg"),
                               parameters=("dry_air_gas_constant_j_kg_k", "vapour_gas_constant_j_kg_k")),
    "temperature.equal_air": Component(("gas_temperature",), fields=("temperature_k",)),
    "pressure.equal_air": Component(("gas_pressure",), fields=("pressure_pa",)),
    "pressure.overpressure": Component(("gas_pressure",), fields=("pressure_pa",), parameters=("overpressure_pa",)),
    "pressure.fixed": Component(("gas_pressure",), parameters=("gas_pressure_pa",)),
    "volume.ideal_gas": Component(("volume",), ("gas_temperature", "gas_pressure"),
                                  parameters=("helium_mass_kg", "helium_gas_constant_j_kg_k")),
    "geometry.sphere": Component(("area", "diameter"), ("volume",)),
    "area.fixed": Component(("area",), parameters=("reference_area_m2",)),
    "diameter.fixed": Component(("diameter",), parameters=("reference_diameter_m",)),
    "viscosity.sutherland": Component(("viscosity",), fields=("temperature_k",),
                                      parameters=("viscosity_reference_pa_s", "viscosity_reference_temperature_k", "sutherland_temperature_k")),
    "drag.constant_cd": Component(("drag_acceleration",), ("density", "area"), parameters=("mass_kg", "drag_coefficient")),
    "drag.reynolds": Component(("drag_acceleration",), ("density", "area", "diameter", "viscosity"),
                               parameters=("mass_kg", "drag_correlation_id")),
    "drag.cda_over_mass": Component(("drag_acceleration",), ("density",), parameters=("cda_over_mass_m2_kg",)),
    "drag.reference_rate": Component(("drag_acceleration",), ("density",),
                                     parameters=("descent_reference_speed_m_s", "reference_density_kg_m3", "gravity_m_s2")),
    "buoyancy.volume": Component(("buoyancy_acceleration",), ("density", "volume"), parameters=("mass_kg", "gravity_m_s2")),
})

_EVENTS = MappingProxyType({
    "burst.altitude": {"kind": "transition", "parameters": ("burst_geometric_height_m",)},
    "burst.diameter": {"kind": "transition", "parameters": ("burst_diameter_m",), "requires": ("volume", "diameter")},
    "landing.terrain": {"kind": "complete", "terrain": "terrain_geometric_height_m"},
    "time_limit": {"kind": "incomplete", "parameters": ("max_duration_s",)},
})


def _mapping(value, path, allowed=None, required=()):
    if not isinstance(value, dict) or any(not isinstance(k, str) for k in value):
        raise CompositionError("INVALID_SCHEMA", path, "expected an object with string keys")
    if allowed is not None and set(value) - set(allowed):
        raise CompositionError("UNKNOWN_KEY", path, str(sorted(set(value) - set(allowed))))
    if set(required) - set(value):
        raise CompositionError("MISSING_KEY", path, str(sorted(set(required) - set(value))))
    return value


def _names(value, path):
    if not isinstance(value, (list, tuple)) or any(not isinstance(x, str) or not x for x in value):
        raise CompositionError("INVALID_SCHEMA", path, "expected a list of nonempty identifiers")
    if len(value) != len(set(value)):
        raise CompositionError("DUPLICATE_SELECTION", path, "repeated identifier")
    return list(value)


def _number(value, path, positive=False, nonnegative=False):
    try:
        valid = (isinstance(value, (int, float)) and not isinstance(value, bool)
                 and math.isfinite(value))
    except (OverflowError, ValueError):
        valid = False
    if not valid or (positive and value <= 0) or (nonnegative and value < 0):
        raise CompositionError("INVALID_PARAMETER", path, "expected a finite number in the declared range")
    return value


def _parameter(name, values, path):
    if name not in values:
        raise CompositionError("MISSING_PARAMETER", path, name)
    value = values[name]
    if name == "drag_correlation_id":
        if not isinstance(value, str) or not value.strip():
            raise CompositionError("INVALID_PARAMETER", path + "." + name, "a candidate correlation ID is required")
    else:
        signed = name in {"vertical_rate_m_s", "burst_geometric_height_m"}
        _number(value, path + "." + name, positive=not signed and name != "overpressure_pa",
                nonnegative=name == "overpressure_pa")


def _entry_velocity(stage, previous, path):
    """Declare physical ground velocity transfer, never infer a zero/reset value."""
    entry = stage.get("entry_velocity")
    inertial = stage["family"] == "inertial"
    previous_inertial = previous is not None and previous["family"] == "inertial"
    if not inertial and not previous_inertial:
        if entry is not None:
            raise CompositionError("UNUSED_INITIAL_STATE", path, "this stage has no velocity state to initialize/discard")
        return None
    if entry is None:
        raise CompositionError("MISSING_INITIAL_STATE", path, "velocity initialization/transfer/discard must be declared")
    _mapping(entry, path, {"mode", "ground_velocity_m_s"}, ("mode",))
    mode = entry["mode"]
    allowed = {"explicit"} if inertial and previous is None else (
        {"explicit", "carry"} if inertial and previous_inertial else
        {"explicit", "from_previous_rate"} if inertial else {"discard"})
    if not isinstance(mode, str) or mode not in allowed:
        raise CompositionError("INVALID_STATE_TRANSFER", path, f"expected one of {sorted(allowed)}")
    if mode == "explicit":
        if "ground_velocity_m_s" not in entry:
            raise CompositionError("MISSING_INITIAL_STATE", path, "explicit ground_velocity_m_s required")
        _number(entry["ground_velocity_m_s"], path + ".ground_velocity_m_s")
    elif "ground_velocity_m_s" in entry:
        raise CompositionError("UNUSED_INITIAL_STATE", path, "only explicit transfer consumes a numeric velocity")
    result = deepcopy(entry)
    result["quantity"] = "ground_vertical_velocity_m_s"
    if mode == "from_previous_rate":
        # The prior stage owns conversion to ground rate. Its air-wind field
        # requirement is already in the model union; do not add wind a second time.
        result["source_stage"] = previous["id"]
        result["source"] = "previous_resolved_ground_rate"
        result["source_vertical_wind_use"] = previous["vertical_wind_use"]
    return result


def _compose_stage(stage, previous, index, is_last):
    path = f"stages[{index}]"
    allowed = {"id", "family", "components", "parameters", "events", "horizontal",
               "vertical_air", "rate_reference", "entry_velocity", "diagnostics"}
    required = {"id", "family", "components", "parameters", "events", "horizontal", "vertical_air"}
    _mapping(stage, path, allowed, required)
    if not isinstance(stage["id"], str) or not stage["id"].strip():
        raise CompositionError("INVALID_SCHEMA", path + ".id", "a nonempty ID is required")
    family = stage["family"]
    if family not in ("prescribed", "quasisteady", "inertial"):
        raise CompositionError("UNKNOWN_FAMILY", path, str(family))
    if stage["horizontal"] != "wind_advection":
        raise CompositionError("UNSUPPORTED_HORIZONTAL", path, "only one wind-advection owner is implemented")
    wind = stage["vertical_air"]
    if wind not in ("ignore", "geometric"):
        raise CompositionError("UNSUPPORTED_VERTICAL_WIND", path, "omega conversion needs a separate future model")
    if family == "prescribed":
        reference = stage.get("rate_reference")
        if reference not in ("ground", "air"):
            raise CompositionError("MISSING_RATE_REFERENCE", path, "choose ground or air explicitly")
        if reference == "ground" and wind != "ignore":
            raise CompositionError("DOUBLE_VERTICAL_WIND", path, "ground rate must not receive another wind term")
        wind_use = "ground_rate_no_addition" if reference == "ground" else "air_rate_plus_wind_once"
    else:
        if "rate_reference" in stage:
            raise CompositionError("UNUSED_RATE_REFERENCE", path, "force families derive their relative velocity")
        wind_use = "relative_rate_plus_wind_once" if family == "quasisteady" else "ground_state_relative_force_only"
    selections = _names(stage["components"], path + ".components")
    parameters = _mapping(stage["parameters"], path + ".parameters")
    events = _names(stage["events"], path + ".events")
    diagnostics = _names(stage.get("diagnostics", []), path + ".diagnostics")
    providers = {}
    for name in selections:
        if name not in _COMPONENTS:
            raise CompositionError("UNKNOWN_COMPONENT", path, name)
        for output in _COMPONENTS[name].provides:
            if output in providers:
                raise CompositionError("DUPLICATE_PROVIDER", path, f"{output}: {providers[output]}, {name}")
            providers[output] = name
    fields = {"eastward_wind_m_s": {"horizontal.wind_advection"},
              "northward_wind_m_s": {"horizontal.wind_advection"}}
    if wind == "geometric":
        fields["geometric_vertical_wind_m_s"] = {"vertical." + family}
    used_parameters, used_components, visiting, order = set(), set(), set(), []

    def require_parameter(name):
        _parameter(name, parameters, path + ".parameters")
        used_parameters.add(name)

    def resolve(resource, consumer):
        if resource not in providers:
            raise CompositionError("MISSING_CLOSURE", path, f"{consumer} needs {resource}")
        component_id = providers[resource]
        if component_id in used_components:
            return
        if component_id in visiting:
            raise CompositionError("DEPENDENCY_CYCLE", path, component_id)
        visiting.add(component_id)
        component = _COMPONENTS[component_id]
        for dependency in component.requires:
            resolve(dependency, component_id)
        for field in component.fields:
            fields.setdefault(field, set()).add(component_id)
        for parameter in component.parameters:
            require_parameter(parameter)
        visiting.remove(component_id)
        used_components.add(component_id)
        order.append(component_id)

    roots = ["rate"] if family == "prescribed" else ["drag_acceleration"]
    if family != "prescribed":
        require_parameter("gravity_m_s2")
        if "buoyancy_acceleration" in providers:
            roots.append("buoyancy_acceleration")
    for resource in roots + diagnostics:
        resolve(resource, "vertical." + family if resource in roots else "diagnostic")
    compiled_events, terrain = [], {}
    for event_id in events:
        if event_id not in _EVENTS:
            raise CompositionError("UNKNOWN_EVENT", path, event_id)
        event = _EVENTS[event_id]
        if event_id == "burst.diameter" and providers.get("diameter") == "diameter.fixed":
            raise CompositionError("INCOMPATIBLE_EVENT_GEOMETRY", path,
                                   "diameter burst needs volume-derived evolving geometry, not a fixed drag reference diameter")
        for dependency in event.get("requires", ()):
            resolve(dependency, event_id)
        for parameter in event.get("parameters", ()):
            require_parameter(parameter)
        if "terrain" in event:
            terrain[event["terrain"]] = {"unit": "m", "consumers": [event_id]}
        compiled_events.append({"id": event_id, "outcome": event["kind"]})
    transitions = sum(e["outcome"] == "transition" for e in compiled_events)
    if (not is_last and transitions != 1) or (is_last and transitions != 0):
        raise CompositionError("INVALID_PHASE_EVENT", path, "one transition per nonfinal stage; none on final stage")
    if is_last and not any(e["outcome"] in ("complete", "incomplete") for e in compiled_events):
        raise CompositionError("MISSING_TERMINATION", path, "final stage needs an explicit end condition")
    if set(selections) - used_components:
        raise CompositionError("UNUSED_COMPONENT", path, str(sorted(set(selections) - used_components)))
    if set(parameters) - used_parameters:
        raise CompositionError("UNUSED_PARAMETER", path, str(sorted(set(parameters) - used_parameters)))
    transfer = _entry_velocity(stage, previous, path + ".entry_velocity")
    state = {"latitude_degrees": "degree_north", "longitude_degrees": "degree_east", "geometric_height_m": "m"}
    owners = {name: "horizontal.wind_advection" for name in ("latitude_degrees", "longitude_degrees")}
    owners["geometric_height_m"] = "vertical." + family
    if family == "inertial":
        state["ground_vertical_velocity_m_s"] = "m s-1"
        owners["ground_vertical_velocity_m_s"] = "vertical.inertial"
    return {"id": stage["id"], "family": family, "state_schema": state,
            "derivative_owners": owners, "vertical_wind_use": wind_use,
            "vertical_air": wind, "entry_velocity": transfer,
            "evaluation_order": order, "parameters": deepcopy(parameters),
            "required_fields": {k: {"unit": FIELD_UNITS[k], "consumers": sorted(v)} for k, v in sorted(fields.items())},
            "required_terrain_fields": terrain, "events": compiled_events,
            "diagnostics": diagnostics}


def compose_model(spec, capabilities=None):
    """Validate the selected graph and return a detached, deterministic plan.

    spec: schema + ordered stages. Each stage explicitly selects family,
    horizontal/vertical wind, components, parameters and events. Entry velocity
    maps are mandatory exactly when a velocity state is introduced/retained/
    discarded. A from_previous_rate map consumes the previous physical GROUND
    rate, including its declared wind conversion once; it is not a numeric
    initialization until the future evaluator has evaluated that prior rate.
    """
    _mapping(spec, "model", {"schema", "stages"}, {"schema", "stages"})
    if spec["schema"] != SCHEMA:
        raise CompositionError("UNKNOWN_SCHEMA", "model.schema", str(spec["schema"]))
    if not isinstance(spec["stages"], (list, tuple)) or not spec["stages"]:
        raise CompositionError("INVALID_SCHEMA", "model.stages", "at least one ordered stage required")
    stages, ids, fields, terrain = [], set(), {}, {}
    for i, stage in enumerate(spec["stages"]):
        compiled = _compose_stage(stage, stages[-1] if stages else None, i, i == len(spec["stages"]) - 1)
        if compiled["id"] in ids:
            raise CompositionError("DUPLICATE_STAGE", f"stages[{i}].id", compiled["id"])
        ids.add(compiled["id"])
        stages.append(compiled)
        for name, item in compiled["required_fields"].items():
            target = fields.setdefault(name, {"unit": item["unit"], "consumers": []})
            target["consumers"].extend(compiled["id"] + ":" + x for x in item["consumers"])
        for name, item in compiled["required_terrain_fields"].items():
            target = terrain.setdefault(name, {"unit": item["unit"], "consumers": []})
            target["consumers"].extend(compiled["id"] + ":" + x for x in item["consumers"])
    if capabilities is not None:
        _mapping(capabilities, "capabilities", required=("fields",))
        available = _mapping(capabilities["fields"], "capabilities.fields")
        for field, requirement in fields.items():
            if field not in available:
                raise CompositionError("MISSING_CAPABILITY", "capabilities.fields", field)
            if available[field] != requirement["unit"]:
                raise CompositionError("CAPABILITY_UNIT_MISMATCH", "capabilities.fields." + field,
                                       f"expected {requirement['unit']}")
    return {"schema": SCHEMA, "status": "composition_valid", "stages": stages,
            "required_fields": dict(sorted(fields.items())), "required_terrain_fields": terrain,
            "capability_check": "declared_field_units_only" if capabilities is not None else "not_requested",
            "capability_context": deepcopy(capabilities),
            "unresolved_contracts": ["weather_query_support_and_missing_values",
                                     "launch_time_position_and_initial_height",
                                     "geometric_state_to_weather_height_coordinate",
                                     "terrain_height_datum_and_query_support",
                                     "force_and_rate_evaluation_and_applicability",
                                     "event_location_priority_and_initial_contact",
                                     "state_transfer_evaluation_and_numerical_integration"]}


def tawhiri_like_spec(ascent_rate_m_s, descent_reference_speed_m_s, burst_geometric_height_m):
    """A dependency-only simple profile, NOT a numerical Tawhiri reproduction."""
    _number(ascent_rate_m_s, "ascent_rate_m_s", positive=True)
    _number(descent_reference_speed_m_s, "descent_reference_speed_m_s", positive=True)
    _number(burst_geometric_height_m, "burst_geometric_height_m")
    return {"schema": SCHEMA, "stages": [
        {"id": "ascent", "family": "prescribed", "horizontal": "wind_advection",
         "vertical_air": "ignore", "rate_reference": "ground", "components": ["rate.constant"],
         "parameters": {"vertical_rate_m_s": ascent_rate_m_s, "burst_geometric_height_m": burst_geometric_height_m},
         "events": ["burst.altitude"]},
        {"id": "descent", "family": "prescribed", "horizontal": "wind_advection",
         "vertical_air": "ignore", "rate_reference": "ground", "components": ["rate.tawhiri_legacy"],
         "parameters": {"descent_reference_speed_m_s": descent_reference_speed_m_s},
         "events": ["landing.terrain"]},
    ]}
