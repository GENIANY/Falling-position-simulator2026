import { describe, expect, it } from "vitest";
import {
  differences,
  draftIssue,
  jstInputToUtc,
  phases,
  pointAt,
  stableString,
  utcToJstInput,
  supportAreas,
} from "./domain";
import type { FlightPoint } from "./domain";

const row = (
  elapsed_s: number,
  altitude_m: number,
  phase = "ascent",
  longitude_deg = 140,
): FlightPoint => ({
  elapsed_s,
  altitude_m,
  phase,
  longitude_deg,
  latitude_deg: 35,
  time_utc: "",
});
describe("saved flight display semantics", () => {
  it("draws one horizontal support boundary for a shared saved field and excludes hidden fields", () => {
    const source = {
      id: "gfs",
      sha256: "same-field",
      label: "saved",
      bounds: { lat: [33, 34], lon: [135, 136] },
    };
    const view = {
      visible: true,
      envelope: { weather_snapshot: source },
    };
    expect(supportAreas([view, structuredClone(view)])).toHaveLength(1);
    expect(supportAreas([{ ...view, visible: false }])).toHaveLength(0);
  });
  it("converts JST without depending on the host timezone, including day changes", () => {
    expect(jstInputToUtc("2026-09-23T03:30")).toBe("2026-09-22T18:30:00.000Z");
    expect(utcToJstInput("2026-09-22T18:30:00Z")).toBe("2026-09-23T03:30:00");
  });
  it("interpolates irregular records, clamps terminated flights, and preserves originals", () => {
    const rows = [row(0, 100), row(13, 230), row(31, 50, "descent")],
      before = structuredClone(rows);
    expect(pointAt(rows, 20)?.altitude_m).toBeCloseTo(160);
    expect(pointAt(rows, 100)).toEqual(rows[2]);
    expect(pointAt([], 0)).toBeNull();
    expect(rows).toEqual(before);
  });
  it("interpolates the short longitude crossing instead of drawing the cursor around Earth", () => {
    expect(
      Math.abs(
        pointAt([row(0, 0, "ascent", 179), row(10, 0, "ascent", -179)], 5)!
          .longitude_deg,
      ),
    ).toBe(180);
  });
  it("keeps the transition point attached to both drawing phases without altering records", () => {
    const rows = [
      row(0, 0),
      row(10, 10),
      row(10, 10, "descent"),
      row(20, 0, "descent"),
    ];
    expect(phases(rows).map((x) => x[0].phase)).toEqual(["ascent", "descent"]);
    expect(rows).toHaveLength(4);
  });
  it("detects model and physical value changes independently from object key order", () => {
    expect(stableString({ a: 2, b: 1 })).toBe(stableString({ b: 1, a: 2 }));
    expect(
      differences(
        { ascent: { mode: "constant_speed", speed: 5 } },
        { ascent: { mode: "constant_speed", speed: 6 } },
      ),
    ).toEqual(["ascent.speed"]);
  });
  it("does not replace an unsupported diameter condition with a different physical event", () => {
    const c = {
      schema: "balloon.flight.config/1",
      launch: {
        time_utc: "2026-09-23T03:30:00Z",
        latitude_deg: 43,
        longitude_deg: 141.5,
        altitude_m: 74,
      },
      ascent: { mode: "constant_speed", speed_m_s: 5 },
      burst: { mode: "diameter", diameter_m: 8 },
      descent: { mode: "rated_speed", reference_speed_m_s: 5 },
    };
    expect(draftIssue(c)).toContain("未対応");
    expect(c.burst).toEqual({ mode: "diameter", diameter_m: 8 });
    c.burst = { mode: "altitude", diameter_m: NaN };
    expect(draftIssue(c)).toContain("空欄");
  });
});
