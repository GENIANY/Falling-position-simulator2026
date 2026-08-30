Falling-position-simulator ドキュメント
=========================================

このドキュメントは、Falling-position-simulator (Balloon Falling
Position Simulator) の現行実装の仕組みを整理し、次期リニューアルに向けた
新技術スタックの提案をまとめたものです。

.. note::

   このドキュメントの目的は2つです。

   1. **現状把握** — 今このリポジトリが何をどう計算・表示しているかを、
      コードを読まなくても理解できる形でまとめる
   2. **新技術提案** — 現状の限界(モンテカルロ規模・可視化の幅・最適化機能の
      不在)を踏まえ、リニューアル時に選べる技術スタック案を複数提示する

.. toctree::
   :maxdepth: 2
   :caption: 現状の仕組み

   architecture
   ascent_calculator
   trajectory_prediction
   monte_carlo
   deployment
   known_issues

.. toctree::
   :maxdepth: 2
   :caption: 新技術提案

   proposal
