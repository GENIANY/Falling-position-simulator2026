バルーンサイジング電卓 (calc.js)
====================================

概要
----

``js/calc/calc.js`` は打ち上げ前にバルーンサイズを決めるための、
**ブラウザ内で完結する数値計算ツール**。Tawhiri APIは呼ばず、
入力値が変わるたびに ``calc_update()`` が同期的に再計算する。

入力パラメータ
----------------

.. list-table::
   :header-rows: 1

   * - 変数名
     - 意味
     - 既定値/備考
   * - ``mp``
     - ペイロード質量 [g]
     - 20g〜20kgの範囲チェックあり
   * - ``mb``
     - バルーン種別
     - Kaymont/Hwoyee/PAWANの型番プルダウン。バースト直径 ``bd`` と抗力係数
       ``cd`` を内蔵テーブルから引く(手入力での上書きも可)
   * - ``tar``
     - 目標上昇速度 [m/s]
     - ``tba`` と排他。0〜10m/sの範囲チェック
   * - ``tba``
     - 目標バースト高度 [m]
     - ``tar`` と排他。10km〜40kmの範囲チェック
   * - ガス種別
     - He / H2 / CH4 / カスタム
     - ガス密度 ``rho_g`` を自動設定(He: 0.1786, H2: 0.0899, CH4: 0.6672
       kg/m³)
   * - ``rho_a``
     - 空気密度 [kg/m³]
     - 既定値 1.2050
   * - ``adm``
     - 大気密度スケール高 [m]
     - 既定値 7238.3(指数大気モデルのパラメータ)
   * - ``ga``
     - 重力加速度 [m/s²]
     - 既定値 9.80665

計算の流れ
----------

1. バースト時のバルーン体積を球体として算出

   .. math::

      V_{burst} = \frac{4}{3}\pi \left(\frac{d_{burst}}{2}\right)^3

2. **目標バースト高度が指定された場合**: 指数大気モデルで打ち上げ時体積を逆算

   .. math::

      V_{launch} = V_{burst} \cdot e^{-h_{target}/H}

   (:math:`H` は大気密度スケール高 ``adm``)

3. **目標上昇速度が指定された場合**: 浮力・抗力・重力のつり合いから導かれる
   打ち上げ半径 :math:`r` についての三次方程式を、Cardanoの解法(判別式
   ``h`` の符号で場合分けし、複数実根のケースは三角関数法)で数値的に解く。
   コード中の変数 ``a, b, c, d, f, g, h`` はCardano法の標準記法。

   .. note::

      三根が異なる実根を持つケース(``h <= 0``)の分岐に
      ``K`` (未定義、``k`` の誤記と思われる)を参照している箇所があり、
      **実行時エラーになるバグの疑いがある**。詳細は :doc:`known_issues` を
      参照。

4. 打ち上げ体積・半径から各種出力値を算出:

   .. math::

      \begin{aligned}
      A_{launch} &= \pi r^2 \\
      GrossLift &= V_{launch} (\rho_{air} - \rho_{gas}) \\
      NeckLift &= (GrossLift - m_{balloon}) \times 1000 \\
      FreeLift &= (GrossLift - (m_{payload}+m_{balloon})) \cdot g \\
      AscentRate &= \sqrt{\dfrac{FreeLift}{0.5\, C_d\, A_{launch}\, \rho_{air}}} \\
      BurstAltitude &= -H \ln\!\left(\dfrac{V_{launch}}{V_{burst}}\right) \\
      TimeToBurst &= \dfrac{BurstAltitude}{AscentRate \times 60}
      \end{aligned}

出力
----

- 上昇速度 [m/s]
- バースト高度 [m]
- バースト到達時間 [min]
- ネックリフト [g]
- 打ち上げ時ガス体積 [m³ / L / ft³]

「Use Values」ボタンで、これらの計算結果(上昇速度・バースト高度)を
メインの発射カード(:doc:`trajectory_prediction`)にそのまま反映できる。
