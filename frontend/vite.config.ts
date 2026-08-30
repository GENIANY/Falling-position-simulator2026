/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// GitHub Pages はプロジェクトサイト配下 (/Falling-position-simulator/) で配信されるため
// CI では GHPAGES_BASE を設定してビルドする。ローカル開発は '/'。
export default defineConfig({
  plugins: [react()],
  base: process.env.GHPAGES_BASE ?? '/',
  test: {
    environment: 'node',
  },
})
