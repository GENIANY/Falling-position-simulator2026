既知の疑問点・課題の棚卸し
============================

現状把握の過程で見つかった、動作確認や次期リニューアルの判断材料に
なりうる点をまとめる。**いずれもコード読解に基づく推定であり、実機
確認は未実施**。

JST時刻変換の疑い
--------------------

``js/pred/pred-new.js`` の ``runPrediction()``:

.. code-block:: javascript

   var launch_time_plus_8_hours = moment.utc([year, month-1, day, hour, minute, 0, 0]);
   var launch_time = launch_time_plus_8_hours.subtract(8, 'hours');

入力フォームのラベルは「JST」(コミット ``77d97e2`` でMSTから変更)だが、
JSTはUTC+9であるにもかかわらず、コードは8時間しか引いていない。
変数名 ``launch_time_plus_8_hours`` 自体も「UTC+8相当」を前提とした命名で
あり、ラベル変更(MST→JST)の際にこの計算式が追随していない可能性が高い。
1時間のずれが生じるバグの疑いがある。

calc.js の三次方程式ソルバーの未定義変数
--------------------------------------------

``js/calc/calc.js`` ``calc_update()`` 内、三根が実数かつ異なるケース
(``h <= 0``)の分岐:

.. code-block:: javascript

   var i = Math.sqrt((Math.pow(g,2)/4.0) - h);
   var j = Math.pow(i, 1.0/3.0);
   var k = Math.acos(-g / (2*i));
   var L = -1 * j;
   var M = Math.cos(K/3.0);       // ← K は未定義 (kの誤記?)
   var N = Math.sqrt(3) * Math.sin(K/3.0);  // ← 同上

小文字 ``k`` は定義されているが、参照時は大文字 ``K``。このパスに入ると
``ReferenceError`` で ``calc_update()`` が例外終了する。目標上昇速度指定
かつ判別式が負(三実根)になる入力の組み合わせで再現すると推測される。

README とコードのR/G/B対応の不一致
--------------------------------------

:doc:`monte_carlo` に詳細記載。READMEは「G=バースト高度σ, B=降下率σ」と
説明しているが、実装の ``diffToColor`` は「G=降下率σ, B=バースト高度σ」。

未使用/レガシーコード
------------------------

- ``js/pred/pred.js``: 旧CUSF v2実装(Google Maps、サーバーサイドUUID
  ポーリング方式)。``pred-new.js`` (Tawhiri v3クライアント)が主体となった
  現在もなお ``index.html`` から読み込まれている。実際に使用されている
  関数があるか要確認、無ければ削除候補
- ``css/bootstrap.min.css``: ``index.html`` 内でコメントアウトされ未使用

未実装の告知機能
-------------------

README「Upcoming Feature」記載分:

- ガス計算シートの実装(:doc:`ascent_calculator` の電卓はあるが、
  「シート」形式の一覧比較機能は無い)
- CUSF提供APIの統合
- リアルタイム予測対応
- 誤差の修正(本ページで挙げた項目が該当する可能性)

UI上にも「NOTAM/Airspace設定パネル」が存在するが、明示的に
「not yet functional」とマークされている。

これらの課題は、次期リニューアル(:doc:`proposal`)で解消することを
前提に設計する。
