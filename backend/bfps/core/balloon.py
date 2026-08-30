"""バルーンサイジング物理 (legacy js/calc/calc.js のPython移植).

修正点: 手書きCardano法 (未定義変数K・係数括弧ミスのバグあり) を
numpy.roots による実根探索に置き換え。
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .atmosphere import RHO_SL_EXP, SCALE_HEIGHT_DEFAULT

G = 9.80665  # m/s^2

GAS_DENSITY = {"he": 0.1786, "h2": 0.0899, "ch4": 0.6672}  # kg/m^3

# バースト直径 [m] (Kaymont / Hwoyee / PAWAN)
BURST_DIAMETER: dict[str, float] = {
    "k50": 0.88, "k100": 1.96, "k150": 2.52, "k200": 3.00, "k300": 3.78,
    "k350": 4.12, "k600": 6.02, "k800": 7.00, "k1000": 7.86, "k1200": 8.63,
    "k1500": 9.44, "k1600": 9.71, "k1800": 9.98, "k2000": 10.54,
    "k3000": 13.00, "k4000": 15.06,
    "h200": 3.00, "h300": 3.80, "h350": 4.10, "h400": 4.50, "h500": 5.00,
    "h600": 5.80, "h750": 6.50, "h800": 6.80, "h950": 7.20, "h1000": 7.50,
    "h1200": 8.50, "h1500": 9.50, "h1600": 10.50, "h2000": 11.00,
    "h3000": 12.50,
    "p1200": 8.0,
}

# 抗力係数
BALLOON_CD: dict[str, float] = {
    **{k: 0.25 for k in BURST_DIAMETER},
    "k600": 0.30, "k800": 0.30, "k1000": 0.30,
    "h600": 0.30, "h750": 0.30, "h800": 0.30, "h950": 0.30, "h1000": 0.30,
}


class BalloonPhysicsError(ValueError):
    pass


@dataclass(frozen=True)
class BalloonConfig:
    balloon_mass_kg: float
    payload_mass_kg: float
    burst_diameter_m: float
    drag_coefficient: float
    gas_density: float = GAS_DENSITY["he"]
    air_density: float = RHO_SL_EXP
    scale_height: float = SCALE_HEIGHT_DEFAULT


@dataclass(frozen=True)
class BalloonPerformance:
    ascent_rate_ms: float
    burst_altitude_m: float
    time_to_burst_min: float
    neck_lift_g: float
    launch_volume_m3: float
    launch_radius_m: float


def from_model(model: str, payload_mass_kg: float, gas: str = "he") -> BalloonConfig:
    if model not in BURST_DIAMETER:
        raise BalloonPhysicsError(f"unknown balloon model: {model}")
    if gas not in GAS_DENSITY:
        raise BalloonPhysicsError(f"unknown gas: {gas}")
    # 型番の数値部分 [g] がバルーン質量
    mass_g = float(model[1:])
    return BalloonConfig(
        balloon_mass_kg=mass_g / 1000.0,
        payload_mass_kg=payload_mass_kg,
        burst_diameter_m=BURST_DIAMETER[model],
        drag_coefficient=BALLOON_CD[model],
        gas_density=GAS_DENSITY[gas],
    )


def burst_volume(cfg: BalloonConfig) -> float:
    return (4.0 / 3.0) * math.pi * (cfg.burst_diameter_m / 2.0) ** 3


def launch_radius_for_burst_altitude(cfg: BalloonConfig, burst_alt_m: float) -> float:
    v_launch = burst_volume(cfg) * math.exp(-burst_alt_m / cfg.scale_height)
    return ((3.0 * v_launch) / (4.0 * math.pi)) ** (1.0 / 3.0)


def _solve_launch_radius(a: float, b: float, c: float, d: float) -> float:
    roots = np.roots([a, b, c, d])
    real = roots[np.isreal(roots)].real
    positive = real[real > 1e-9]
    if positive.size == 0:
        raise BalloonPhysicsError("no physical launch radius")
    return float(positive.min())


def launch_radius_for_ascent_rate(cfg: BalloonConfig, target_ascent_ms: float) -> float:
    """浮力・抗力・重力のつり合い三次方程式を解く.

    g*(ρa-ρg)*(4/3)πr³ - 0.5*v²*cd*ρa*πr² - (mp+mb)*g = 0
    """
    a = G * (cfg.air_density - cfg.gas_density) * (4.0 / 3.0) * math.pi
    b = -0.5 * target_ascent_ms**2 * cfg.drag_coefficient * cfg.air_density * math.pi
    c = 0.0
    d = -(cfg.payload_mass_kg + cfg.balloon_mass_kg) * G
    return _solve_launch_radius(a, b, c, d)


def performance(cfg: BalloonConfig, launch_radius_m: float) -> BalloonPerformance:
    launch_area = math.pi * launch_radius_m**2
    launch_vol = (4.0 / 3.0) * math.pi * launch_radius_m**3
    gross_lift = launch_vol * (cfg.air_density - cfg.gas_density)
    neck_lift_g = (gross_lift - cfg.balloon_mass_kg) * 1000.0
    free_lift = (gross_lift - (cfg.payload_mass_kg + cfg.balloon_mass_kg)) * G
    if free_lift <= 0:
        raise BalloonPhysicsError("insufficient buoyancy for this configuration")
    ascent_rate = math.sqrt(
        free_lift / (0.5 * cfg.drag_coefficient * launch_area * cfg.air_density)
    )
    burst_alt = -cfg.scale_height * math.log(launch_vol / burst_volume(cfg))
    if burst_alt <= 0 or not math.isfinite(ascent_rate):
        raise BalloonPhysicsError("altitude unreachable for this configuration")
    return BalloonPerformance(
        ascent_rate_ms=ascent_rate,
        burst_altitude_m=burst_alt,
        time_to_burst_min=burst_alt / ascent_rate / 60.0,
        neck_lift_g=neck_lift_g,
        launch_volume_m3=launch_vol,
        launch_radius_m=launch_radius_m,
    )
