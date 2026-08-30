# Falling-position-simulator Backend

Falling-position-simulator のPythonバックエンド骨組み。大規模モンテカルロ・自前軌道シミュレーション・発射条件最適化を提供する。

## 実行

```bash
cd backend
uv sync
uv run uvicorn bfps.main:app --reload --port 8000
```

## テスト

```bash
uv run pytest          # ネットワーク不要のテストのみ (既定)
uv run pytest -m network   # Open-Meteo等を実際に叩くテスト
```

## API

| エンドポイント | 内容 |
|---|---|
| `GET /api/health` | 死活確認 |
| `POST /api/simulate` | 単発軌道シミュレーション。`engine: native`(自前RK4積分) / `tawhiri`(プロキシ)。`wind_source: openmeteo` / `constant` |
| `POST /api/montecarlo` | n≤2000のモンテカルロ。着地点群・95%信頼楕円・パーセンタイル半径・飛行時間統計を返す |
| `POST /api/optimize` | 発射時刻×上昇率のグリッドサーチ。目的関数=目標地点距離+分布広がりペナルティ |

curl例:

```bash
curl -X POST localhost:8000/api/montecarlo -H 'Content-Type: application/json' -d '{
  "profile": {"launch_latitude":33.1,"launch_longitude":132.5,"launch_altitude":0,
    "launch_datetime":"2026-08-05T00:00:00Z","ascent_rate":5,"burst_altitude":30000,"descent_rate":5},
  "n_samples": 500
}'
```

## 既知の制約 (骨組み段階)

- **Open-Meteoの風データは30hPa (≈24km) まで**。バースト高度30km超の上部は最上層風を保持して外挿する (レスポンスの`warnings`に明記)。高精度が必要な場合は`engine: tawhiri`を使うこと。中期的にはNOAA NOMADSのGFS GRIB直取得へ移行予定
- 風プロファイルは発射点・発射時刻で1回取得し飛行中は固定 (Tawhiriは4D補間)
- optimizeは全セルで同一風プロファイルを共有 (時刻セルごとの再取得は未実装)
- MC/最適化は同期実行。応答30秒超の規模になったらジョブキュー化する

## デプロイ

`docker build -t bfps-backend .` → port 8080 (Cloud Run / Fly.io想定)。デプロイ設定は次フェーズ。
