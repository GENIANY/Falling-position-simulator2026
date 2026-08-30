import { describe, expect, it } from 'vitest'
import { jstInputToUtcIso, utcIsoToJstDisplay } from './jst'

describe('jst', () => {
  it('converts JST input to UTC with -9h offset (legacy bug was -8h)', () => {
    expect(jstInputToUtcIso('2026-08-05T09:00')).toBe(
      '2026-08-05T00:00:00.000Z',
    )
  })

  it('handles day boundary', () => {
    expect(jstInputToUtcIso('2026-08-05T08:59')).toBe(
      '2026-08-04T23:59:00.000Z',
    )
  })

  it('handles month boundary', () => {
    expect(jstInputToUtcIso('2026-09-01T00:30')).toBe(
      '2026-08-31T15:30:00.000Z',
    )
  })

  it('round-trips display', () => {
    expect(utcIsoToJstDisplay('2026-08-05T00:00:00.000Z')).toBe(
      '2026-08-05 09:00',
    )
  })
})
