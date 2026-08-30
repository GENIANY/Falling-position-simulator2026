import type { Layout, Config } from 'plotly.js'

export const BASE_LAYOUT: Partial<Layout> = {
  margin: { l: 55, r: 15, t: 40, b: 45 },
  height: 300,
  font: { size: 11 },
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
}

export const BASE_CONFIG: Partial<Config> = {
  displaylogo: false,
  responsive: true,
  modeBarButtonsToRemove: ['lasso2d', 'select2d'],
}
