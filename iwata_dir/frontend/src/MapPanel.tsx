import { useEffect, useRef, useState } from "react";
import L from "leaflet";
import type { DisplayRun } from "./domain";
import { phases, pointAt, supportAreas } from "./domain";

export function MapPanel({ runs, time }: { runs: DisplayRun[]; time: number }) {
  const host = useRef<HTMLDivElement>(null),
    map = useRef<L.Map | null>(null);
  const layers = useRef<L.LayerGroup | null>(null),
    tiles = useRef<L.TileLayer | null>(null);
  const [background, setBackground] = useState("none"),
    [tileError, setTileError] = useState(false);
  const [height, setHeight] = useState<number | null>(null);
  useEffect(() => {
    const m = L.map(host.current!, { preferCanvas: true }).setView(
      [43, 141.5],
      8,
    );
    map.current = m;
    layers.current = L.layerGroup().addTo(m);
    const observer = new ResizeObserver(() => m.invalidateSize({ pan: false }));
    observer.observe(host.current!);
    return () => {
      observer.disconnect();
      m.remove();
      map.current = null;
    };
  }, []);
  useEffect(() => {
    const m = map.current!;
    setTileError(false);
    tiles.current?.remove();
    tiles.current = null;
    if (background !== "none") {
      const url =
        background === "std"
          ? "https://cyberjapandata.gsi.go.jp/xyz/std/{z}/{x}/{y}.png"
          : "https://cyberjapandata.gsi.go.jp/xyz/seamlessphoto/{z}/{x}/{y}.jpg";
      const layer = L.tileLayer(url, {
        maxZoom: 18,
        attribution:
          '<a href="https://maps.gsi.go.jp/development/ichiran.html" target="_blank" rel="noopener">地理院タイル</a>',
      }).addTo(m);
      layer.on("tileerror", () => setTileError(true));
      tiles.current = layer;
    }
  }, [background]);
  useEffect(() => {
    const group = layers.current!;
    group.clearLayers();
    for (const area of supportAreas(runs)) {
      const label = document.createElement("span");
      label.textContent = `保存気象の水平範囲: ${area.label}`;
      L.rectangle(
        [
          [area.lat[0], area.lon[0]],
          [area.lat[1], area.lon[1]],
        ],
        { color: "#667b84", weight: 1.5, dashArray: "6 5", fill: false },
      )
        .addTo(group)
        .bindTooltip(label);
    }
    for (const r of runs.filter((x) => x.visible)) {
      const result = r.envelope.result;
      for (const part of phases(result.records)) {
        if (part.length < 2) continue;
        L.polyline(
          part.map((p) => [p.latitude_deg, p.longitude_deg] as L.LatLngTuple),
          {
            color: r.color,
            weight: 3,
            dashArray: part[0].phase === "descent" ? "7 5" : undefined,
          },
        )
          .addTo(group)
          .bindTooltip(
            document.createTextNode(
              `${r.label} / ${part[0].phase === "descent" ? "下降" : "上昇"}`,
            ) as unknown as HTMLElement,
          );
      }
      for (const e of result.events) {
        const el = document.createElement("span");
        el.textContent = `${r.label} ${e.type} ${(e.elapsed_s / 60).toFixed(1)}分 / ${(e.altitude_m / 1000).toFixed(2)} km ASL`;
        L.circleMarker([e.latitude_deg, e.longitude_deg], {
          radius: e.type === "landing" ? 7 : 5,
          color: r.color,
          fillColor: "#fff",
          fillOpacity: 1,
          weight: 2,
        })
          .addTo(group)
          .bindTooltip(el);
      }
      const end = result.records.at(-1);
      if (end && result.status === "stopped") {
        const label = document.createElement("span");
        label.textContent = `${r.label} 停止: ${result.stop_reason?.code ?? "不明"}（着地点ではありません）`;
        L.circleMarker([end.latitude_deg, end.longitude_deg], {
          radius: 8,
          color: r.color,
          fillColor: r.color,
          fillOpacity: 0.25,
          dashArray: "2 3",
        })
          .addTo(group)
          .bindTooltip(label);
      }
      const cursor = pointAt(result.records, time);
      if (cursor) {
        const label = document.createElement("span");
        label.textContent = `${r.label} ${(cursor.elapsed_s / 60).toFixed(1)}分 / ${(cursor.altitude_m / 1000).toFixed(2)} km ASL${end && time >= end.elapsed_s ? "（終了）" : ""}`;
        L.circleMarker([cursor.latitude_deg, cursor.longitude_deg], {
          radius: 5,
          color: "#fff",
          fillColor: r.color,
          fillOpacity: 1,
          weight: 2,
        })
          .addTo(group)
          .bindTooltip(label);
      }
    }
  }, [runs, time]);
  const fit = () => {
    const points = runs
      .filter((r) => r.visible)
      .flatMap((r) =>
        r.envelope.result.records.map(
          (p) => [p.latitude_deg, p.longitude_deg] as L.LatLngTuple,
        ),
      );
    if (points.length)
      map.current?.fitBounds(L.latLngBounds(points).pad(0.12), { maxZoom: 12 });
  };
  const fitted = useRef(false);
  useEffect(() => {
    if (!fitted.current && runs.some((r) => r.envelope.result.records.length)) {
      fit();
      fitted.current = true;
    }
  }, [runs]);
  return (
    <section className="panel map-panel" aria-label="比較する二結果の地図">
      <div className="section-heading">
        <div>
          <h2>同じ地図で軌道を比べる</h2>
          <p>
            候補の色を保ち、上昇は実線、下降は破線。丸はイベント、破線の丸は停止点です。
          </p>
        </div>
        <div className="toolbar">
          <label>
            背景
            <select
              value={background}
              onChange={(e) => setBackground(e.target.value)}
            >
              <option value="none">背景なし（通信なし）</option>
              <option value="std">地理院・標準地図</option>
              <option value="photo">地理院・写真（航空・衛星）</option>
            </select>
          </label>
          <button onClick={fit} disabled={!runs.length}>
            表示軌道を全体表示
          </button>
        </div>
      </div>
      {tileError && (
        <p className="notice" role="status">
          背景を取得できないタイルがあります。軌道と履歴は保存結果から表示しています。背景なしにも切り替えられます。
        </p>
      )}
      <div ref={host} className="map" style={height ? { height } : undefined} />
      {supportAreas(runs).length > 0 && (
        <p className="small">
          灰色の破線:{" "}
          {supportAreas(runs)
            .map((s) => s.label)
            .join(" / ")}{" "}
          の水平範囲。時刻・高度・欠測の支持は別です。
        </p>
      )}
      {!runs.length && (
        <p className="empty">
          計算済みの結果をここに重ねます。入力を編集しても、表示中の旧結果は消えません。
        </p>
      )}
      <div className="map-size">
        <label>
          地図の高さ
          <input
            type="range"
            min="280"
            max="1100"
            step="20"
            value={height ?? 520}
            onChange={(e) => setHeight(Number(e.target.value))}
          />
        </label>
        <button onClick={() => setHeight(null)}>画面に合わせる</button>
        <span>{height ? `${height} px` : "自動"}</span>
      </div>
      <small>
        背景を選ぶと地理院へ画像を取得します。写真の撮影時期や解像度は場所によって異なります。幾何高度と背景地形・建物の高さは別です。{" "}
        <a
          href="https://maps.gsi.go.jp/help/termsofuse.html"
          target="_blank"
          rel="noopener"
        >
          出典・利用条件
        </a>
      </small>
    </section>
  );
}
