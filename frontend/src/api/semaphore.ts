// Tawhiriへの同時リクエスト数を全体で制限するセマフォ。
// 無料公開APIへの配慮として上限5、429/503受信時は全体を10秒停止する。

export class Semaphore {
  private queue: (() => void)[] = []
  private active = 0
  private pausedUntil = 0

  private readonly limit: number

  constructor(limit: number) {
    this.limit = limit
  }

  async acquire(): Promise<void> {
    const now = Date.now()
    if (now < this.pausedUntil) {
      await new Promise((r) => setTimeout(r, this.pausedUntil - now))
    }
    if (this.active < this.limit) {
      this.active++
      return
    }
    await new Promise<void>((resolve) => this.queue.push(resolve))
    this.active++
  }

  release(): void {
    this.active--
    const next = this.queue.shift()
    if (next) next()
  }

  /** レート制限応答を受けた際に全体を一時停止 */
  pause(ms: number): void {
    this.pausedUntil = Math.max(this.pausedUntil, Date.now() + ms)
  }

  async run<T>(fn: () => Promise<T>): Promise<T> {
    await this.acquire()
    try {
      return await fn()
    } finally {
      this.release()
    }
  }
}

export const MAX_CONCURRENT_TAWHIRI = 5
export const tawhiriSemaphore = new Semaphore(MAX_CONCURRENT_TAWHIRI)

/** リクエスト開始間の小さなジッタ (混雑緩和) */
export function jitterMs(): number {
  return 50 + Math.random() * 100
}
