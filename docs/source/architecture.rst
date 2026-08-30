全体アーキテクチャ
====================

概要
----

Falling-position-simulator は **ビルドステップを持たない静的Webアプリ** です。
サーバーサイドのコードはこのリポジトリには存在せず、軌道計算の実体は
外部の Tawhiri API (CUSFが開発したバルーン着地予測エンジンの
SondeHubホスティングインスタンス) に委譲しています。

.. mermaid::

   flowchart LR
       User["ユーザー<br/>(ブラウザ)"] -->|パラメータ入力| UI["index.html + jQuery UI<br/>フローティングパネル"]
       UI -->|"HTTP GET (単発 / 繰り返し)"| Tawhiri["Tawhiri API<br/>api.v2.sondehub.org/tawhiri"]
       Tawhiri -->|GFS風データで軌道積分| GFS["GFS 数値気象モデル<br/>(NOAA, Tawhiri側が参照)"]
       Tawhiri -->|"軌道点列 (緯度経度高度時刻)"| UI
       UI -->|Leaflet描画| Map["地図表示<br/>飛行経路 / 着地マーカー"]
       UI -->|"KML/CSV生成"| Export["ダウンロードリンク"]

       Local["js/calc/calc.js<br/>ブラウザ内バルーン<br/>サイジング計算"] -.->|"値を反映"| UI

ポイント:

- 実際の風・大気による軌道積分計算は **すべてTawhiri側(サーバー)で実行**
  される。本リポジトリはリクエストを組み立て、返ってきた軌道点列を
  地図に描画するだけの **薄いクライアント**
- 唯一ブラウザ内で完結する数値計算は、打ち上げ前のバルーンサイジング電卓
  (:doc:`ascent_calculator`) のみ
- モンテカルロ的な確率分散表示 (:doc:`monte_carlo`) は、Tawhiriへの
  リクエストをパラメータを揺らしながら何度も投げる、という形で実現されて
  いる(サーバー側でモンテカルロを回しているわけではない)

ディレクトリ構成
----------------

.. code-block:: text

   Falling-position-simulator/
   ├── index.html                  # 単一ページ。全UIマークアップ
   ├── sites.json                  # プリセット発射地点(緯度経度高度)
   ├── test.py                     # ローカル開発用HTTPサーバー(CORS付与のみ)
   ├── .github/workflows/pages.yml # GitHub Pages自動デプロイ
   ├── css/                        # Bootstrap(未使用) / jQuery UI / Leaflet / 独自CSS
   ├── images/                     # マーカーアイコン等
   └── js/
       ├── jquery-3.3.1.min.js, jquery-ui.min.js, jquery.form.js
       ├── jquery.jookie.js        # クッキー操作
       ├── jquery.tipsy.js         # ツールチップ
       ├── leaflet.js              # 地図ライブラリ (Google Mapsから移行済み)
       ├── moment.js                # 日時操作
       ├── colour-map.js            # ヒートマップ用turboカラーマップ
       ├── calc/
       │   └── calc.js               # バルーンサイジング電卓(ブラウザ内完結)
       └── pred/
           ├── pred-config.js        # 定数・グローバル設定
           ├── pred-cookie.js        # 保存済み発射地点のクッキー管理
           ├── pred-event.js         # jQuery UIイベント配線
           ├── pred-map.js           # Leaflet地図初期化・クリック処理
           ├── pred-new.js           # 本体: Tawhiriクライアント(v3) ★最重要ファイル
           ├── pred-ui.js            # 汎用UI補助(ウィンドウ・デバッグ・エラー表示)
           └── pred.js               # 旧v2実装(Google Maps・UUIDポーリング) ほぼ未使用

技術スタック
------------

.. list-table::
   :header-rows: 1

   * - 領域
     - 使用技術
   * - 言語
     - HTML5 / Vanilla JavaScript(ES5〜ES6混在) / CSS。TypeScriptやビルドツールは無し
   * - DOM/UI
     - jQuery 3.3.1, jQuery UI(ドラッグ可能パネル), jquery.tipsy, jquery.jookie
   * - 地図
     - Leaflet.js(旧Google Mapsから移行、Google Maps用の未使用コードが一部残存)
   * - 日時
     - moment.js
   * - 軌道計算
     - 外部Tawhiri API(自前実装なし)
   * - ホスティング
     - GitHub Pages(GitHub Actionsでリポジトリをそのまま配信、ビルド工程なし)

外部依存
--------

- **Tawhiri API**: ``https://api.v2.sondehub.org/tawhiri``
  (SondeHubがホストするCUSF Tawhiriのインスタンス。GFS風データを用いて
  バルーンの上昇・降下軌道を数値積分する)。APIキー不要、``$.get`` で直接
  ブラウザから叩いている
- 元々のCUSF公式エンドポイント ``https://predict.cusf.co.uk/api/v1/`` は
  コード内にコメントアウトで残存
- データベースやユーザー認証、独自バックエンドは一切無し
