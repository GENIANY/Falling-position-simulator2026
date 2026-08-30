import { formatInTimeZone, fromZonedTime } from 'date-fns-tz'

export const JST = 'Asia/Tokyo'

/**
 * <input type="datetime-local"> の値 (例 "2026-08-05T09:00") を
 * JSTのローカル時刻として解釈し、UTCのISO文字列を返す。
 * 旧実装の「−8時間」手計算バグをタイムゾーンライブラリで構造的に排除する。
 */
export function jstInputToUtcIso(localInput: string): string {
  return fromZonedTime(localInput, JST).toISOString()
}

/** UTC ISO文字列をJST表示用文字列に変換 */
export function utcIsoToJstDisplay(
  iso: string,
  fmt = 'yyyy-MM-dd HH:mm',
): string {
  return formatInTimeZone(iso, JST, fmt)
}

/** 現在時刻をdatetime-local入力用のJST文字列で返す (分単位) */
export function nowJstInputValue(): string {
  return formatInTimeZone(new Date(), JST, "yyyy-MM-dd'T'HH:mm")
}

/** UTC ISO文字列をdatetime-local入力用のJST文字列へ */
export function utcIsoToJstInputValue(iso: string): string {
  return formatInTimeZone(iso, JST, "yyyy-MM-dd'T'HH:mm")
}
