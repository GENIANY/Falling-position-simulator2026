import { afterEach, describe, expect, it, vi } from 'vitest'
import {
  normalizeLon,
  parseFlight,
  requestPrediction,
  toTawhiriLon,
} from './tawhiri'
import type { TawhiriRequest, TawhiriResponse } from './tawhiriTypes'
import { TawhiriError } from './tawhiriTypes'

const fixture: TawhiriResponse = {
  request: {},
  prediction: [
    {
      stage: 'ascent',
      trajectory: [
        {
          latitude: 33.1,
          longitude: 132.5,
          altitude: 0,
          datetime: '2026-08-05T00:00:00Z',
        },
        {
          latitude: 33.2,
          longitude: 132.7,
          altitude: 30000,
          datetime: '2026-08-05T01:40:00Z',
        },
      ],
    },
    {
      stage: 'descent',
      trajectory: [
        {
          latitude: 33.2,
          longitude: 132.7,
          altitude: 30000,
          datetime: '2026-08-05T01:40:00Z',
        },
        {
          latitude: 33.25,
          longitude: 192.8, // 意図的に180超え: -167.2に正規化されるべき
          altitude: 0,
          datetime: '2026-08-05T02:30:00Z',
        },
      ],
    },
  ],
  metadata: {
    start_datetime: '2026-08-05T00:00:00Z',
    complete_datetime: '2026-08-05T02:30:00Z',
  },
}

const baseReq: TawhiriRequest = {
  profile: 'standard_profile',
  launch_latitude: 33.1,
  launch_longitude: -132.5,
  launch_altitude: 0,
  launch_datetime: '2026-08-05T00:00:00.000Z',
  ascent_rate: 5,
  burst_altitude: 30000,
  descent_rate: 5,
}

afterEach(() => {
  vi.unstubAllGlobals()
  vi.useRealTimers()
})

describe('lon conversion', () => {
  it('normalizes >180 to negative', () => {
    expect(normalizeLon(192.8)).toBeCloseTo(-167.2)
    expect(normalizeLon(132.5)).toBe(132.5)
  })
  it('converts negative to 0..360', () => {
    expect(toTawhiriLon(-132.5)).toBe(227.5)
    expect(toTawhiriLon(132.5)).toBe(132.5)
  })
})

describe('parseFlight', () => {
  it('splits stages and extracts markers', () => {
    const f = parseFlight(fixture)
    expect(f.launch.latitude).toBe(33.1)
    expect(f.burst?.altitude).toBe(30000)
    expect(f.landing.longitude).toBeCloseTo(-167.2)
    expect(f.flightTimeS).toBe(9000)
  })
})

describe('requestPrediction', () => {
  it('sends 0-360 longitude and parses response', async () => {
    let requestedUrl = ''
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string) => {
        requestedUrl = url
        return new Response(JSON.stringify(fixture), { status: 200 })
      }),
    )
    const flight = await requestPrediction(baseReq)
    expect(requestedUrl).toContain('launch_longitude=227.5')
    expect(flight.landing.latitude).toBeCloseTo(33.25)
  })

  it('retries on 500 then succeeds', async () => {
    let calls = 0
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => {
        calls++
        if (calls === 1) return new Response('oops', { status: 500 })
        return new Response(JSON.stringify(fixture), { status: 200 })
      }),
    )
    const flight = await requestPrediction(baseReq)
    expect(calls).toBe(2)
    expect(flight.launch.latitude).toBe(33.1)
  }, 10000)

  it('does not retry on 400 and surfaces description', async () => {
    let calls = 0
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => {
        calls++
        return new Response(
          JSON.stringify({ error: { description: 'outside dataset' } }),
          { status: 400 },
        )
      }),
    )
    await expect(requestPrediction(baseReq)).rejects.toThrow('outside dataset')
    expect(calls).toBe(1)
  })

  it('aborts', async () => {
    const controller = new AbortController()
    vi.stubGlobal(
      'fetch',
      vi.fn(
        (_url: string, opts: { signal?: AbortSignal }) =>
          new Promise((_resolve, reject) => {
            opts.signal?.addEventListener('abort', () =>
              reject(new DOMException('Aborted', 'AbortError')),
            )
          }),
      ),
    )
    const p = requestPrediction(baseReq, { signal: controller.signal })
    controller.abort()
    await expect(p).rejects.toThrow('Aborted')
  })

  it('throws TawhiriError type on 4xx', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => new Response('{}', { status: 404 })),
    )
    await expect(requestPrediction(baseReq)).rejects.toBeInstanceOf(
      TawhiriError,
    )
  })
})
