"""大気モデル: 指数大気 (legacy calc.js互換) + ISA標準大気 (〜32km)."""

from __future__ import annotations

import numpy as np

# legacy calc.js と同一の既定値
SCALE_HEIGHT_DEFAULT = 7238.3  # m
RHO_SL_EXP = 1.2050  # kg/m^3 (legacy rho_a default)

# ISA定数
G0 = 9.80665  # m/s^2
R_AIR = 287.05287  # J/(kg K)
P0 = 101325.0  # Pa
T0 = 288.15  # K
RHO0_ISA = 1.2250  # kg/m^3

# ISA層 (基準高度 [m], 基準温度 [K], 温度勾配 [K/m]) 〜32km
_ISA_LAYERS = [
    (0.0, 288.15, -0.0065),
    (11000.0, 216.65, 0.0),
    (20000.0, 216.65, 0.001),
    (32000.0, 228.65, 0.0028),  # 32km以遠はこの層の式で外挿
]


def _isa_layer_base_pressures() -> list[float]:
    """各層の基準気圧を逐次計算."""
    pressures = [P0]
    for i in range(1, len(_ISA_LAYERS)):
        h_b, t_b, lapse = _ISA_LAYERS[i - 1]
        h_top = _ISA_LAYERS[i][0]
        p_b = pressures[-1]
        if lapse == 0.0:
            p = p_b * np.exp(-G0 * (h_top - h_b) / (R_AIR * t_b))
        else:
            p = p_b * (1 + lapse * (h_top - h_b) / t_b) ** (-G0 / (R_AIR * lapse))
        pressures.append(float(p))
    return pressures


_ISA_BASE_P = _isa_layer_base_pressures()


def density_exponential(
    alt_m: float | np.ndarray,
    scale_height: float = SCALE_HEIGHT_DEFAULT,
    rho0: float = RHO_SL_EXP,
) -> float | np.ndarray:
    """指数大気モデル (calc.jsのバースト高度式と整合)."""
    return rho0 * np.exp(-np.asarray(alt_m, dtype=float) / scale_height)


def _layer_index(alt_m: float) -> int:
    for i in range(len(_ISA_LAYERS) - 1, -1, -1):
        if alt_m >= _ISA_LAYERS[i][0]:
            return i
    return 0


def temperature_isa(alt_m: float) -> float:
    i = _layer_index(alt_m)
    h_b, t_b, lapse = _ISA_LAYERS[i]
    return t_b + lapse * (alt_m - h_b)


def pressure_isa(alt_m: float) -> float:
    i = _layer_index(alt_m)
    h_b, t_b, lapse = _ISA_LAYERS[i]
    p_b = _ISA_BASE_P[i]
    if lapse == 0.0:
        return p_b * float(np.exp(-G0 * (alt_m - h_b) / (R_AIR * t_b)))
    return p_b * float(
        (1 + lapse * (alt_m - h_b) / t_b) ** (-G0 / (R_AIR * lapse))
    )


def density_isa(alt_m: float) -> float:
    return pressure_isa(alt_m) / (R_AIR * temperature_isa(alt_m))


def altitude_from_pressure(p_hpa: float) -> float:
    """気圧 [hPa] からISA高度 [m] を逆算 (二分法)。Open-Meteo気圧面の変換用."""
    p_pa = p_hpa * 100.0
    lo, hi = 0.0, 50000.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if pressure_isa(mid) > p_pa:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
