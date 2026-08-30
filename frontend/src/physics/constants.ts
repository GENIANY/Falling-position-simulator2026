// legacy calc.js と同一の物理定数 (パリティ担保のため値を変えないこと)

export const GRAVITY = 9.80665 // m/s^2
export const AIR_DENSITY_SL = 1.205 // kg/m^3 (legacy rho_a default)
export const ATMOSPHERE_SCALE_HEIGHT = 7238.3 // m (legacy adm default)

export const GAS_DENSITY = {
  helium: 0.1786,
  hydrogen: 0.0899,
  methane: 0.6672,
} as const

export type GasType = keyof typeof GAS_DENSITY
