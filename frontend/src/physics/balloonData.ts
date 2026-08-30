// バルーン諸元テーブル (legacy calc.js find_bd / find_cd から移植)
// burstDiameter: バースト時直径 [m], dragCoefficient: 抗力係数, massKg: バルーン質量 [kg]

export interface BalloonSpec {
  label: string
  massKg: number
  burstDiameterM: number
  dragCoefficient: number
}

export const BALLOON_SPECS: Record<string, BalloonSpec> = {
  // Kaymont Totex sounding balloon data
  k50: { label: 'Kaymont 50', massKg: 0.05, burstDiameterM: 0.88, dragCoefficient: 0.25 },
  k100: { label: 'Kaymont 100', massKg: 0.1, burstDiameterM: 1.96, dragCoefficient: 0.25 },
  k150: { label: 'Kaymont 150', massKg: 0.15, burstDiameterM: 2.52, dragCoefficient: 0.25 },
  k200: { label: 'Kaymont 200', massKg: 0.2, burstDiameterM: 3.0, dragCoefficient: 0.25 },
  k300: { label: 'Kaymont 300', massKg: 0.3, burstDiameterM: 3.78, dragCoefficient: 0.25 },
  k350: { label: 'Kaymont 350', massKg: 0.35, burstDiameterM: 4.12, dragCoefficient: 0.25 },
  k600: { label: 'Kaymont 600', massKg: 0.6, burstDiameterM: 6.02, dragCoefficient: 0.3 },
  k800: { label: 'Kaymont 800', massKg: 0.8, burstDiameterM: 7.0, dragCoefficient: 0.3 },
  k1000: { label: 'Kaymont 1000', massKg: 1.0, burstDiameterM: 7.86, dragCoefficient: 0.3 },
  k1200: { label: 'Kaymont 1200', massKg: 1.2, burstDiameterM: 8.63, dragCoefficient: 0.25 },
  k1500: { label: 'Kaymont 1500', massKg: 1.5, burstDiameterM: 9.44, dragCoefficient: 0.25 },
  k1600: { label: 'Kaymont 1600', massKg: 1.6, burstDiameterM: 9.71, dragCoefficient: 0.25 },
  k1800: { label: 'Kaymont 1800', massKg: 1.8, burstDiameterM: 9.98, dragCoefficient: 0.25 },
  k2000: { label: 'Kaymont 2000', massKg: 2.0, burstDiameterM: 10.54, dragCoefficient: 0.25 },
  k3000: { label: 'Kaymont 3000', massKg: 3.0, burstDiameterM: 13.0, dragCoefficient: 0.25 },
  k4000: { label: 'Kaymont 4000', massKg: 4.0, burstDiameterM: 15.06, dragCoefficient: 0.25 },
  // Hwoyee (burst diameters from vendor, Cd is guesswork per legacy comment)
  h200: { label: 'Hwoyee 200', massKg: 0.2, burstDiameterM: 3.0, dragCoefficient: 0.25 },
  h300: { label: 'Hwoyee 300', massKg: 0.3, burstDiameterM: 3.8, dragCoefficient: 0.25 },
  h350: { label: 'Hwoyee 350', massKg: 0.35, burstDiameterM: 4.1, dragCoefficient: 0.25 },
  h400: { label: 'Hwoyee 400', massKg: 0.4, burstDiameterM: 4.5, dragCoefficient: 0.25 },
  h500: { label: 'Hwoyee 500', massKg: 0.5, burstDiameterM: 5.0, dragCoefficient: 0.25 },
  h600: { label: 'Hwoyee 600', massKg: 0.6, burstDiameterM: 5.8, dragCoefficient: 0.3 },
  h750: { label: 'Hwoyee 750', massKg: 0.75, burstDiameterM: 6.5, dragCoefficient: 0.3 },
  h800: { label: 'Hwoyee 800', massKg: 0.8, burstDiameterM: 6.8, dragCoefficient: 0.3 },
  h950: { label: 'Hwoyee 950', massKg: 0.95, burstDiameterM: 7.2, dragCoefficient: 0.3 },
  h1000: { label: 'Hwoyee 1000', massKg: 1.0, burstDiameterM: 7.5, dragCoefficient: 0.3 },
  h1200: { label: 'Hwoyee 1200', massKg: 1.2, burstDiameterM: 8.5, dragCoefficient: 0.25 },
  h1500: { label: 'Hwoyee 1500', massKg: 1.5, burstDiameterM: 9.5, dragCoefficient: 0.25 },
  h1600: { label: 'Hwoyee 1600', massKg: 1.6, burstDiameterM: 10.5, dragCoefficient: 0.25 },
  h2000: { label: 'Hwoyee 2000', massKg: 2.0, burstDiameterM: 11.0, dragCoefficient: 0.25 },
  h3000: { label: 'Hwoyee 3000', massKg: 3.0, burstDiameterM: 12.5, dragCoefficient: 0.25 },
  // PAWAN
  p1200: { label: 'PAWAN 1200', massKg: 1.2, burstDiameterM: 8.0, dragCoefficient: 0.25 },
}
