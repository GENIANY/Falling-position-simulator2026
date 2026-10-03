import { useRef } from "react";
import type { DisplayRun } from "./domain";
import { jstLabel, phases, pointAt } from "./domain";

export function HistoryPanel({
  runs,
  time,
  onTime,
}: {
  runs: DisplayRun[];
  time: number;
  onTime: (n: number) => void;
}) {
  const svg = useRef<SVGSVGElement>(null);
  const visible = runs.filter((r) => r.visible);
  const maxTime = Math.max(
    1,
    ...visible.map((r) => r.envelope.result.summary.duration_s),
  );
  const maxAltitude =
    Math.max(
      1000,
      ...visible.map((r) => r.envelope.result.summary.maximum_altitude_m ?? 0),
    ) * 1.06;
  const minAltitude = visible.reduce(
    (min, r) =>
      r.envelope.result.records.reduce(
        (a, p) => Math.min(a, p.altitude_m),
        min,
      ),
    0,
  );
  const width = 1000,
    height = 420,
    left = 70,
    right = 25,
    top = 92,
    bottom = 65;
  const x = (t: number) => left + (t / maxTime) * (width - left - right);
  const y = (h: number) =>
    height -
    bottom -
    ((h - minAltitude) / (maxAltitude - minAltitude)) * (height - top - bottom);
  const exportSvg = () => {
    const doc = svg.current!.cloneNode(true) as SVGSVGElement;
    doc.setAttribute("xmlns", "http://www.w3.org/2000/svg");
    const metadata = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "metadata",
    );
    metadata.textContent = JSON.stringify(
      visible.map((r) => ({
        label: r.label,
        run_id: r.id,
        n: 1,
        config: r.envelope.result.config,
        weather: r.envelope.weather_snapshot,
        source: r.envelope.source_snapshot,
      })),
    );
    doc.prepend(metadata);
    const url = URL.createObjectURL(
      new Blob([new XMLSerializer().serializeToString(doc)], {
        type: "image/svg+xml",
      }),
    );
    const link = document.createElement("a");
    link.href = url;
    link.download = "balloon-flight-comparison.svg";
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
  return (
    <section className="panel history-panel">
      <div className="section-heading">
        <div>
          <h2>経過時間と高度</h2>
          <p>
            二つの実計算結果を放球からの経過時間で比較します。各
            n=1。分散や確率の輪郭は表示しません。
          </p>
        </div>
        <button onClick={exportSvg} disabled={!visible.length}>
          履歴図をSVG保存
        </button>
      </div>
      <div className="legend">
        {visible.map((r) => (
          <span key={r.id} style={{ color: r.color }}>
            <b>━ {r.label}</b> · {r.id.slice(0, 12)}
          </span>
        ))}
        <span>上昇 ━　下降 ┄</span>
      </div>
      <svg
        ref={svg}
        viewBox={`0 0 ${width} ${height}`}
        role="img"
        aria-label="候補別の高度・経過時間"
        style={{
          width: "100%",
          background: "#fff",
          fontFamily: "sans-serif",
          fontSize: 13,
        }}
      >
        <title>バルーン飛行比較：幾何高度ASLと経過時間</title>
        <rect width={width} height={height} fill="white" />
        <text x={left} y="20" fill="#193944" fontSize="15">
          保存GFS・一飛行比較（各 n=1）　上昇 ━ / 下降 ┄
        </text>
        {visible.map((r, i) => (
          <text
            key={r.id}
            x={left}
            y={43 + 20 * i}
            fill={r.color}
            fontSize="12"
          >
            {r.label} · 放球{" "}
            {jstLabel(r.envelope.result.config.launch.time_utc)} ·{" "}
            {r.envelope.result.status === "landed" ? "着地" : "停止"}
          </text>
        ))}
        {[0, 1, 2, 3, 4].map((i) => {
          const value = minAltitude + ((maxAltitude - minAltitude) * i) / 4;
          return (
            <g key={i}>
              <line
                x1={left}
                x2={width - right}
                y1={y(value)}
                y2={y(value)}
                stroke="#dce5e9"
              />
              <text
                x={left - 10}
                y={y(value) + 4}
                textAnchor="end"
                fill="#36515b"
              >
                {(value / 1000).toFixed(1)}
              </text>
              <text
                x={x((maxTime * i) / 4)}
                y={height - bottom + 20}
                textAnchor="middle"
                fill="#36515b"
              >
                {((maxTime * i) / 240).toFixed(0)}
              </text>
            </g>
          );
        })}
        <text x="8" y={top - 7} fill="#36515b">
          km ASL
        </text>
        <text
          x={(left + width - right) / 2}
          y={height - 23}
          textAnchor="middle"
          fill="#36515b"
        >
          経過時間 [分]
        </text>
        {visible.map((r) => (
          <g key={r.id}>
            {phases(r.envelope.result.records).map((part, i) => (
              <polyline
                key={i}
                fill="none"
                stroke={r.color}
                strokeWidth="2.5"
                strokeDasharray={
                  part[0].phase === "descent" ? "8 5" : undefined
                }
                points={part
                  .map((p) => `${x(p.elapsed_s)},${y(p.altitude_m)}`)
                  .join(" ")}
              />
            ))}
            {r.envelope.result.events.map((e, i) => (
              <circle
                key={i}
                cx={x(e.elapsed_s)}
                cy={y(e.altitude_m)}
                r="4"
                fill="white"
                stroke={r.color}
              >
                <title>
                  {r.label} {e.type} {(e.elapsed_s / 60).toFixed(2)}分
                </title>
              </circle>
            ))}
          </g>
        ))}
        <line
          x1={x(Math.min(time, maxTime))}
          x2={x(Math.min(time, maxTime))}
          y1={top}
          y2={height - bottom}
          stroke="#485f67"
          strokeDasharray="3 3"
        />
        <text x={left} y={height - 2} fontSize="9" fill="#4c6068">
          {visible.map((r) => `${r.label}: ${r.id}`).join(" / ")}
        </text>
      </svg>
      <label className="time-control">
        経過 <output>{(time / 60).toFixed(1)} 分</output>
        <input
          aria-label="共通の経過時間"
          type="range"
          min="0"
          max={maxTime}
          step="1"
          value={Math.min(time, maxTime)}
          onChange={(e) => onTime(Number(e.target.value))}
        />
      </label>
      <div className="cursor-values">
        {visible.map((r) => {
          const rows = r.envelope.result.records,
            p = pointAt(rows, time);
          return (
            <div key={r.id} style={{ borderColor: r.color }}>
              <b>{r.label}</b>
              {p ? (
                <>
                  <span>
                    {(p.altitude_m / 1000).toFixed(2)} km ASL ·{" "}
                    {p.latitude_deg.toFixed(4)}°N, {p.longitude_deg.toFixed(4)}
                    °E
                  </span>
                  <small>
                    {time >= rows.at(-1)!.elapsed_s
                      ? "終了した時点の位置"
                      : "保存履歴の表示用内挿"}{" "}
                    · 放球 {jstLabel(r.envelope.result.config.launch.time_utc)}
                  </small>
                </>
              ) : (
                <span>記録なし</span>
              )}
            </div>
          );
        })}
      </div>
      <div className="events">
        {visible.map((r) => (
          <details key={r.id}>
            <summary>{r.label} のイベントと停止理由</summary>
            <ul>
              {r.envelope.result.events.map((e, i) => (
                <li key={i}>
                  {e.type} · {(e.elapsed_s / 60).toFixed(2)}分 ·{" "}
                  {e.altitude_m.toFixed(1)} m ASL
                </li>
              ))}
            </ul>
            {r.envelope.result.stop_reason && (
              <p>
                停止: {r.envelope.result.stop_reason.code} —{" "}
                {r.envelope.result.stop_reason.message}
              </p>
            )}
          </details>
        ))}
      </div>
    </section>
  );
}
