// Monte Carlo worker: 割り当てられたサンプルindexの摂動リクエストを
// 同時実行数制限つきでTawhiriへ投げ、結果を逐次postMessageで返す。

import { requestPrediction } from '../api/tawhiri'
import { perturbationForIndex, requestForPerturbation } from './sampling'
import type { MCWorkerMsg, MCWorkerReply } from './mcTypes'

let aborter: AbortController | null = null

function post(reply: MCWorkerReply) {
  self.postMessage(reply)
}

self.onmessage = async (ev: MessageEvent<MCWorkerMsg>) => {
  const msg = ev.data
  if (msg.type === 'cancel') {
    aborter?.abort()
    return
  }

  const { config, indices, concurrency } = msg
  aborter = new AbortController()
  const signal = aborter.signal

  let cursor = 0
  async function runNext(): Promise<void> {
    while (cursor < indices.length && !signal.aborted) {
      const index = indices[cursor++]
      // 混雑緩和のジッタ
      await new Promise((r) => setTimeout(r, 50 + Math.random() * 100))
      const perturbed = perturbationForIndex(config, index)
      const req = requestForPerturbation(config, perturbed)
      try {
        const flight = await requestPrediction(req, { signal })
        post({ type: 'sample', index, flight, perturbed })
      } catch (e) {
        if (signal.aborted) return
        post({
          type: 'error',
          index,
          message: e instanceof Error ? e.message : String(e),
        })
      }
    }
  }

  await Promise.all(
    Array.from({ length: Math.max(1, concurrency) }, () => runNext()),
  )
  post({ type: 'done' })
}
