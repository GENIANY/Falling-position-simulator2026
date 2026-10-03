"""Pure local HTML/SVG presentation of supplied results; no simulation or I/O."""
import html
import json
import math
from .. import __version__

def _json(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def _trajectory_svg(records):
    if not records:
        return '<p>保存できる軌道点がありません。</p>'
    width, height, left, top = 740, 420, 65, 28
    plotw, ploth = width - left - 35, height - top - 55
    meanlat = math.fsum(r["latitude_deg"] for r in records) / len(records)
    c = math.cos(math.radians(meanlat))
    xs = [r["longitude_deg"] * c for r in records]
    ys = [r["latitude_deg"] for r in records]
    xmin, xmax = min(xs), max(xs); ymin, ymax = min(ys), max(ys)
    xspan, yspan = max(xmax-xmin, 0.02), max(ymax-ymin, 0.02)
    scale = min(plotw/xspan, ploth/yspan) * .92
    cx, cy = (xmin+xmax)/2, (ymin+ymax)/2
    coords = [(left+plotw/2+(x-cx)*scale, top+ploth/2-(y-cy)*scale) for x,y in zip(xs,ys)]
    segments = []
    for phase, color in (("ascent", "#126c8c"), ("descent", "#cd6623")):
        # Preserve each adjacent segment, including the shared burst point.
        paths = [f'M {coords[i-1][0]:.3f} {coords[i-1][1]:.3f} L {coords[i][0]:.3f} {coords[i][1]:.3f}'
                 for i in range(1,len(records)) if records[i-1]["phase"] == phase]
        segments.append(f'<path d="{" ".join(paths)}" fill="none" stroke="{color}" stroke-width="2"/>')
    marks = []
    for idx,label,color in ((0,"放球","#126c8c"),(len(records)-1,"最終点","#b13d30")):
        x,y=coords[idx];marks.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{color}"/><text x="{x+8}" y="{y-7}">{label}</text>')
    grid = []
    for i in range(5):
        x = left+plotw*i/4; lon=(cx+(x-left-plotw/2)/scale)/c
        y = top+ploth*i/4; lat=cy-(y-top-ploth/2)/scale
        grid.append(f'<path d="M{x} {top}V{top+ploth} M{left} {y}H{left+plotw}" stroke="#dce4e9"/>'
                    f'<text x="{x}" y="{top+ploth+22}" text-anchor="middle">{lon:.3f}°E</text>'
                    f'<text x="{left-7}" y="{y+4}" text-anchor="end">{lat:.3f}°N</text>')
    x,y=coords[0]
    return (f'<svg id="map" viewBox="0 0 {width} {height}" role="img" aria-label="緯度経度上の軌道">'
            +''.join(grid+segments+marks)+f'<circle id="cursor-map" cx="{x}" cy="{y}" r="6" fill="#29283e" stroke="white" stroke-width="2"/>'
            +'</svg><p class="caption">緯度経度の局所平面表示。縮尺には軌道の平均緯度を使う。積分自体は各時刻の緯度を使う。背景地図・海岸線・飛行許可範囲は表していない。</p>'
            +'<script type="application/json" id="map-coordinates">'+json.dumps(coords)+'</script>')


def _altitude_svg(records):
    if not records:
        return ""
    width,height,left,top=740,300,65,20
    pw,ph=width-left-35,height-top-50
    duration=max(records[-1]["elapsed_s"],1)
    ymax=max(max(r["altitude_m"] for r in records)*1.06,100)
    ymin=min(0,min(r["altitude_m"] for r in records))
    def xy(r,key):
        return left+pw*r["elapsed_s"]/duration,top+ph*(ymax-r[key])/(ymax-ymin)
    curves=[]
    for key,color in (("altitude_m","#126c8c"),("ground_altitude_m","#72824a")):
        pts=" ".join(f'{xy(r,key)[0]:.3f},{xy(r,key)[1]:.3f}' for r in records)
        curves.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2"/>')
    grid=[]
    for i in range(5):
        x=left+pw*i/4;y=top+ph*i/4
        grid.append(f'<path d="M{x} {top}V{top+ph} M{left} {y}H{left+pw}" stroke="#dce4e9"/>'
                    f'<text x="{x}" y="{top+ph+21}" text-anchor="middle">{duration*i/240:.1f}分</text>'
                    f'<text x="{left-8}" y="{y+4}" text-anchor="end">{(ymax-(ymax-ymin)*i/4)/1000:.1f}km</text>')
    return (f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="高度と時間">'
            +''.join(grid+curves)+f'<line id="cursor-time" x1="{left}" x2="{left}" y1="{top}" y2="{top+ph}" stroke="#29283e"/>'
            +'</svg><p class="caption">青：気球のモデル幾何高度、緑：使用した気象モデルの補間地形。標高基準の近似と細かな地形の未解像を含む。</p>')


def render_report(result, provenance):
    """Pure rendering, escaped input strings, no remote assets/network."""
    records=result["records"]
    status="着地まで計算完了" if result["complete"] else "計算は途中で停止"
    reason=html.escape(str(result.get("stop_reason") or "terrain_landing"))
    summary=html.escape(_json(result.get("summary",{})))
    assumptions=html.escape(_json(result.get("model_assumptions",[])))
    data=json.dumps(records,ensure_ascii=False,allow_nan=False).replace("<","\\u003c")
    config=html.escape(_json(result["config"]))
    prov=html.escape(_json(provenance))
    return f"""<!doctype html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Balloon-JP 軌道計算結果</title><style>
body{{font:16px/1.7 "Yu Gothic","Meiryo",sans-serif;color:#203445;background:#edf2f5;margin:0}}
main{{max-width:1050px;margin:24px auto;padding:28px;background:white}}
h1{{margin:0;font-size:29px}}h2{{margin:28px 0 10px;font-size:21px}}
.status{{padding:12px 16px;background:{"#e3f1ed" if result["complete"] else "#fff0df"};border-left:5px solid {"#258069" if result["complete"] else "#bc5d23"}}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:24px}}svg{{width:100%;height:auto}}svg text{{font-size:11px}}
.caption,.muted{{font-size:13px;color:#526575}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f7f8;padding:16px;font-size:13px}}
input[type=range]{{width:100%}}#sample{{font-variant-numeric:tabular-nums;padding:12px;background:#eef5f8;min-height:4em}}
a{{color:#076a90}}@media(max-width:760px){{.grid{{display:block}}main{{padding:16px}}}}
</style></head><body><main>
<p class="muted">Balloon-JP {__version__} / 保存気象場からの再現可能な候補計算</p><h1>軌道計算結果</h1>
<p class="status"><strong>{status}</strong><br>終了理由：{reason}</p>
<p>この結果は指定した気象場とモデル仮定から計算した軌道です。初期値は実打上げの機体条件に置き換えてください。着地点は細密地形・予報誤差・機体ばらつきを含む運用精度の検証済み位置ではありません。</p>
<div class="grid"><section><h2>水平軌道</h2>{_trajectory_svg(records)}</section><section><h2>高度と飛行時間</h2>{_altitude_svg(records)}</section></div>
<h2>飛行中の状態を確認</h2><label for="index">保存された時刻を選択</label>
<input id="index" type="range" min="0" max="{max(0,len(records)-1)}" value="0"><div id="sample"></div>
<h2>結果概要</h2><pre>{summary}</pre>
<details><summary>モデルの仮定</summary><pre>{assumptions}</pre></details>
<details><summary>今回の設定</summary><pre>{config}</pre></details>
<details><summary>入力とコードの来歴</summary><pre>{prov}</pre></details>
<p><a href="trajectory.csv">全軌道CSV</a> / <a href="trajectory.geojson">GeoJSON</a> / <a href="result.json">結果JSON</a> / <a href="manifest.json">出力ハッシュ</a></p>
<script type="application/json" id="records">{data}</script>
<script>
const rows=JSON.parse(document.getElementById('records').textContent);
const cnode=document.getElementById('map-coordinates'),coords=cnode?JSON.parse(cnode.textContent):[];
function show(){{let i=Number(document.getElementById('index').value),r=rows[i];
if(!r){{document.getElementById('sample').textContent='保存点なし';return;}}
document.getElementById('sample').textContent=r.time_utc+' | '+r.phase+' | '+r.latitude_deg.toFixed(5)+'°N, '+r.longitude_deg.toFixed(5)+'°E | 高度 '+r.altitude_m.toFixed(1)+' m | 地上高 '+r.height_agl_m.toFixed(1)+' m | '+(r.weather_quality||[]).join(', ');
let marker=document.getElementById('cursor-map');if(marker&&coords[i]){{marker.setAttribute('cx',coords[i][0]);marker.setAttribute('cy',coords[i][1]);}}
let line=document.getElementById('cursor-time');if(line){{let x=65+640*r.elapsed_s/Math.max(rows[rows.length-1].elapsed_s,1);line.setAttribute('x1',x);line.setAttribute('x2',x);}}
}}document.getElementById('index').addEventListener('input',show);show();
</script></main></body></html>
"""
