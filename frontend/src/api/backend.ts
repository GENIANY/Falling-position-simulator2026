// 将来のFastAPIバックエンド (backend/) への接続シーム。
// VITE_API_BASE が未設定なら null を返し、呼び出し側はTawhiri直叩きにフォールバックする。
// GitHub Pages 配信時はバックエンド無しで全機能が動作する設計。

export function backendBaseUrl(): string | null {
  const base = import.meta.env.VITE_API_BASE as string | undefined
  return base && base.length > 0 ? base.replace(/\/$/, '') : null
}

export function backendEnabled(): boolean {
  return backendBaseUrl() !== null
}

export interface BackendHealth {
  status: string
  version: string
}

export async function checkHealth(): Promise<BackendHealth | null> {
  const base = backendBaseUrl()
  if (!base) return null
  try {
    const res = await fetch(`${base}/api/health`)
    if (!res.ok) return null
    return (await res.json()) as BackendHealth
  } catch {
    return null
  }
}

// バックエンド実装後にここへ /api/simulate, /api/montecarlo, /api/optimize の
// クライアント関数を追加する (schemas は backend/bfps/models/schemas.py と対応させる)
