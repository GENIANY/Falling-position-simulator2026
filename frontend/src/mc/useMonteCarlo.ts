import { useCallback, useRef } from 'react'
import { MAX_CONCURRENT_TAWHIRI, tawhiriSemaphore } from '../api/semaphore'
import { requestPrediction } from '../api/tawhiri'
import { loadLandData } from '../optimizer/landSea'
import { fetchElevations } from '../safety/elevation'
import {
  classify,
  emptyBreakdown,
  loadSafetyData,
} from '../safety/landingSafety'
import type { SafetyCategory } from '../safety/landingSafety'
import { computeLandingStats } from '../stats/landing'
import { useResultsStore } from '../store/resultsStore'
import { partitionIndices } from './sampling'
import type { MCConfig, MCWorkerReply } from './mcTypes'

export const MC_MAX_SAMPLES = 500

export function useMonteCarlo() {
  const workersRef = useRef<Worker[]>([])

  const cancel = useCallback(() => {
    for (const w of workersRef.current) {
      w.postMessage({ type: 'cancel' })
      w.terminate()
    }
    workersRef.current = []
    useResultsStore.getState().setRunning(false)
  }, [])

  const run = useCallback(
    async (config: MCConfig) => {
      const results = useResultsStore.getState()
      const samples = Math.min(config.samples, MC_MAX_SAMPLES)
      results.clearAll()
      results.setRunning(true)
      results.setProgress({ done: 0, total: samples + 1 })

      // 中心点 (摂動なし) はメインスレッドで実行
      try {
        const central = await tawhiriSemaphore.run(() =>
          requestPrediction(config.base),
        )
        useResultsStore.getState().setMcCentral(central)
      } catch (e) {
        useResultsStore
          .getState()
          .setError(e instanceof Error ? e.message : String(e))
        useResultsStore.getState().setRunning(false)
        return
      }

      const poolSize = Math.min(4, navigator.hardwareConcurrency ?? 2)
      const partitions = partitionIndices(samples, poolSize)
      // グローバル上限5をworker数で分配
      const perWorkerConcurrency = Math.max(
        1,
        Math.floor(MAX_CONCURRENT_TAWHIRI / partitions.length),
      )

      let done = 1 // 中心点分
      let finishedWorkers = 0

      await new Promise<void>((resolve) => {
        workersRef.current = partitions.map((indices) => {
          const worker = new Worker(
            new URL('./mcWorker.ts', import.meta.url),
            { type: 'module' },
          )
          worker.onmessage = (ev: MessageEvent<MCWorkerReply>) => {
            const msg = ev.data
            const store = useResultsStore.getState()
            if (msg.type === 'sample') {
              store.addMcSample({
                index: msg.index,
                flight: msg.flight,
                perturbed: {
                  ascentRate: msg.perturbed.ascentRate,
                  burstAltitude: msg.perturbed.burstAltitude,
                  descentRate: msg.perturbed.descentRate,
                },
              })
              done++
              store.setProgress({ done, total: samples + 1 })
            } else if (msg.type === 'error') {
              done++
              store.setProgress({ done, total: samples + 1 })
            } else if (msg.type === 'done') {
              finishedWorkers++
              if (finishedWorkers === partitions.length) resolve()
            }
          }
          worker.postMessage({
            type: 'run',
            config: { ...config, samples },
            indices,
            concurrency: perWorkerConcurrency,
          })
          return worker
        })
      })

      for (const w of workersRef.current) w.terminate()
      workersRef.current = []

      // 統計計算
      const store = useResultsStore.getState()
      const landings = store.mcSamples.map((s) => ({
        lat: s.flight.landing.latitude,
        lon: s.flight.landing.longitude,
      }))
      if (landings.length >= 5) {
        store.setMcStats(computeLandingStats(landings))
      }

      // 安全カテゴリ判定 (陸海/除外区域データ+標高)
      try {
        const baseUrl = import.meta.env.BASE_URL
        await Promise.all([loadLandData(baseUrl), loadSafetyData(baseUrl)])
        const samplesSnapshot = useResultsStore.getState().mcSamples
        const elevations = await fetchElevations(
          samplesSnapshot.map((s) => ({
            lat: s.flight.landing.latitude,
            lon: s.flight.landing.longitude,
          })),
        )
        const categories = new Map<number, SafetyCategory>()
        const breakdown = emptyBreakdown()
        samplesSnapshot.forEach((s, i) => {
          const cat = classify(
            s.flight.landing.latitude,
            s.flight.landing.longitude,
            elevations[i],
          )
          categories.set(s.index, cat)
          breakdown[cat]++
        })
        const finalStore = useResultsStore.getState()
        finalStore.applyCategories(categories)
        finalStore.setMcSafety(breakdown)
      } catch {
        // 安全判定はベストエフォート (データ取得失敗でもMC結果自体は有効)
      }
      useResultsStore.getState().setRunning(false)
    },
    [],
  )

  return { run, cancel }
}
