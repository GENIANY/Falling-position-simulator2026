着地位置予測 (pred-new.js)
============================

概要
----

``js/pred/pred-new.js`` (2078行) が本アプリの中核。ユーザーが入力した
発射条件を Tawhiri API 形式のリクエストに変換し、返ってきた軌道点列を
地図に描画する。軌道の物理計算自体は行わず、あくまで **Tawhiriクライアント**
である。

.. mermaid::

   sequenceDiagram
       participant U as ユーザー
       participant UI as index.html / pred-new.js
       participant API as Tawhiri API

       U->>UI: 発射地点・日時・上昇率・バースト高度等を入力
       U->>UI: 「Run Prediction」クリック
       UI->>UI: runPrediction() で入力値を検証・整形
       UI->>API: GET /tawhiri?launch_latitude=...&profile=...
       API-->>UI: {prediction: [ascent軌道, descent軌道], request: {...}}
       UI->>UI: parsePrediction() で軌道点列をポリラインに変換
       UI->>U: Leaflet地図上に飛行経路・打上/バースト/着地マーカーを表示

入力パラメータ (runPrediction)
-------------------------------

.. list-table::
   :header-rows: 1

   * - パラメータ
     - 説明
   * - ``launch_latitude`` / ``launch_longitude``
     - 発射地点(経度はTawhiri仕様に合わせ0〜360に正規化)
   * - ``launch_altitude``
     - 発射地点の標高 [m]
   * - ``launch_datetime``
     - 発射日時。入力フォームは「JST」表記だが、変換処理は
       ``moment.utc(...).subtract(8, 'hours')`` — 詳細は :doc:`known_issues`
   * - ``ascent_rate``
     - 上昇速度 [m/s](:doc:`ascent_calculator` の結果を転記可)
   * - ``profile``
     - ``standard_profile`` (打上→バースト→降下) /
       ``float_profile`` (指定高度で浮遊) / ``reverse_profile``
   * - ``burst_altitude`` + ``descent_rate``
     - standard_profile時。降下率は抗力から求めた値
   * - ``float_altitude`` + ``stop_datetime``
     - float_profile時。既定で発射時刻+1日を終了時刻とする

日時の範囲チェック: 発射時刻が「現在-12時間」より過去、または
「現在+7日」より未来の場合はエラーとして弾く(Tawhiriが参照するGFSモデルの
予報時間幅=約169時間に対応)。

予測モード (``tawhiriRequest`` の ``pred_type``)
--------------------------------------------------

.. list-table::
   :header-rows: 1

   * - モード
     - 動作
   * - ``single``
     - Tawhiriへ1回だけリクエストし、飛行経路を1本描画
   * - ``1_hour`` / ``3_hour`` / ``6_hour`` / ``12_hour`` / ``daily``
     - 発射時刻を指定間隔でずらしながら ``MAX_PRED_HOURS = 169`` 時間分
       繰り返しリクエストし、各着地点をターボカラーマップ
       (``evaluate_cmap(current_hour/MAX_PRED_HOURS, 'turbo')``、
       ``js/colour-map.js``)で経過時間に応じて色分けプロット
   * - ``Gaussian_distribution`` / ``Weibull_distribution``
     - :doc:`monte_carlo` を参照

レスポンス処理 (``parsePrediction``)
--------------------------------------

Tawhiriのレスポンスは ``prediction[0].trajectory`` (上昇脚) と
``prediction[1].trajectory`` (降下 or 浮遊脚) の2本の軌道配列を持つ
(各要素は ``{latitude, longitude, altitude, datetime}``)。
これらは **既にTawhiri側でGFS風データを用いて積分済み** の点列であり、
このクライアントは以下の処理のみを行う:

- 経度180度超過分の補正(``_lon > 180`` なら ``-360``)
- 2本の軌道を結合して1本のポリラインに
- 先頭点=打上、上昇脚末尾=バースト、降下脚末尾=着地としてマーカー抽出

出力・エクスポート
--------------------

- Leaflet地図上に黒色ポリライン(飛行経路)+打上/バースト/着地アイコン
- 「Scenario Info」パネル: 打上〜着地間の距離(ハーバサイン)、飛行時間、
  使用したTawhiriデータセットのタイムスタンプ
- CSV/KMLダウンロードリンクは、Tawhiriへのクエリパラメータに
  ``&format=csv`` / ``&format=kml`` を付与するだけで、Tawhiri自身が
  生成したファイルを直接ダウンロードさせている(このリポジトリ側では
  ファイル生成をしていない)

Tawhiri APIエンドポイント
----------------------------

.. code-block:: javascript

   var tawhiri_api = "https://api.v2.sondehub.org/tawhiri";
   // var tawhiri_api = "https://predict.cusf.co.uk/api/v1/"; (コメントアウト、旧CUSF公式)

APIキー不要。ブラウザから直接 ``$.get`` でクロスオリジンリクエストして
いる(CORSはTawhiri側が許可)。
