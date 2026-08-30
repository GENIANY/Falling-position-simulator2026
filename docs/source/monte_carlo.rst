モンテカルロ分布モード
========================

概要
----

このフォーク独自の機能。標準のTawhiriクライアントには無い、
「発射パラメータを確率的にばらつかせて何度もTawhiriへ問い合わせ、
着地点の散らばりを可視化する」機能が2種類実装されている。

.. important::

   サーバー側でモンテカルロを回しているわけではない。ブラウザ側で
   100個の乱数パラメータセットを生成し、Tawhiri APIへ101回
   (サンプル100+中心点1)のHTTPリクエストを個別に送信して結果を
   集計している。これは以下の制約に直結する:

   - サンプル数を増やすほどTawhiriへの負荷とブラウザの待ち時間が線形に増える
   - 各サンプルは独立したTawhiri呼び出しであり、Tawhiri側の風データが
     揺らぐわけではない(揺らすのは上昇率・バースト高度・降下率のみ)
   - 大気そのもののばらつき(風速誤差・GFSアンサンブル等)は考慮されない

Gaussian_distribution モード
-------------------------------

``plotGaussianDistribution()`` (``js/pred/pred-new.js``)

1. 現在の上昇率・バースト高度・降下率を中心値として、正規分布
   (Box-Muller法、``gaussianRandom(mean, stdDev)``)で100サンプル生成:

   .. list-table::
      :header-rows: 1

      * - パラメータ
        - 標準偏差
      * - 上昇率
        - ±0.5 m/s
      * - バースト高度
        - 中心値の ±5%
      * - 降下率
        - ±0.5 m/s

2. 中心値1点 + サンプル100点 = 計101回、Tawhiriへ個別リクエスト
3. 各着地点を ``diffToColor(ascent_diff, burst_diff, descent_diff)`` で
   色分け:

   .. code-block:: javascript

      function diffToColor(ascent_diff, burst_diff, descent_diff) {
          var red   = 255 - Math.round(255 * ascent_diff  / 3);
          var blue  = 255 - Math.round(255 * burst_diff   / 3);
          var green = 255 - Math.round(255 * descent_diff / 3);
          return 'rgb(' + red + ',' + green + ',' + blue + ')';
      }

   実装上の対応関係は **R=上昇率のσ、G=降下率のσ、B=バースト高度のσ**。
   中心点(平均値)は差分0のため赤 (255,255,255→補正後ほぼ白ではなく
   実装上は最大値になる点に注意)。差分が大きいほど各色成分が減衰する。

   .. warning::

      README(日本語)の説明文では「Rが上昇速度、**Gがバースト高度**、
      **Bが降下速度**」と書かれているが、実装は **G=降下率、B=バースト高度**
      で **G/Bが逆**。ドキュメント化にあたり実装を正とした。README側の
      修正、または実装側の意図確認が必要(:doc:`known_issues` 参照)。

Weibull_distribution モード
------------------------------

``plotWeibullDistribution()``

- バースト高度のみを対象に、逆CDF法によるWeibull分布サンプリングを実施:

  .. code-block:: javascript

     function weibullRandom(shape, scale) {
         var u = Math.random();
         // F^{-1}(u) = scale * (-ln(u))^{1/shape}
         return scale * Math.pow(-Math.log(u), 1 / shape);
     }

  形状パラメータ ``shape = 3.0``(固定)、尺度パラメータ ``scale`` は
  目標バースト高度そのもの。上昇率・降下率は揺らがない。
- 中心値1点+サンプル100点=101回リクエスト(Gaussianモードと同構成)
- 着地点は ``burstDiffToColor(burst_diff)`` で、目標バースト高度からの
  乖離率に応じて緑(誤差小)→赤(誤差大)のグラデーションで着色

共通の後処理
------------

両モードとも、全サンプルの着地点・入力設定を配列に蓄積し、以下を提供:

- 地図上への全着地点プロット(``plotMultiplePredictionWithColor``)
- 個別着地点のポップアップにσ値・緯度経度(10進・DMS)・KML/CSVリンク・
  クリップボードコピーボタン
- 全サンプルをまとめたKML/CSVの一括ダウンロード

現状の限界(次期リニューアルの動機)
--------------------------------------

- サンプル数が固定100件で、ユーザーが試行回数を調整できない
- 1サンプル=1 HTTPリクエストのため、数百〜数千規模のモンテカルロは
  現実的な時間で終わらない
- ばらつかせられるパラメータが上昇率・バースト高度・降下率の3つのみ
  (発射地点や発射時刻のばらつき、風の不確実性そのものは非対応)
- 着地分布の統計サマリ(信頼楕円・ヒストグラム・確率密度等)が無く、
  生の点群プロットのみ
- 「この条件ならどこから打ち上げるべきか」「ヘリウム量はどれくらいが
  最適か」を提案する最適化機能は存在しない

これらを踏まえた新技術提案は :doc:`proposal` にまとめる。
