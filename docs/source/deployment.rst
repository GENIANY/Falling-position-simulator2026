デプロイ・配信の仕組み
========================

GitHub Pages自動デプロイ
---------------------------

``.github/workflows/pages.yml`` により、``main`` ブランチへのpush
(または手動 ``workflow_dispatch``)をトリガーに、以下の手順でGitHub Pages
へ配信される:

.. mermaid::

   flowchart LR
       A["push to main"] --> B["actions/checkout@v4"]
       B --> C["actions/configure-pages@v5"]
       C --> D["actions/upload-pages-artifact@v3<br/>path: '.' (リポジトリ全体をそのまま)"]
       D --> E["actions/deploy-pages@v4"]
       E --> F["GitHub Pages公開<br/>wasa-rockoon.github.io/Falling-position-simulator/"]

ポイント:

- **ビルド工程が一切無い**。``upload-pages-artifact`` の対象パスは
  ``.`` (リポジトリルート全体)であり、トランスパイル・バンドル・
  minifyの類は行われない。リポジトリの中身がそのまま公開URLの中身になる
- テスト・Lintの実行も無し
- 権限: ``contents: read``, ``pages: write``, ``id-token: write``。
  同時実行は ``concurrency: group: "pages", cancel-in-progress: true``
  でグループ化(同時デプロイの競合を防止)

ローカル開発
------------

``test.py`` はPython標準ライブラリ ``http.server`` をラップした簡易サーバー
で、CORSヘッダーを付与しているだけ(Tawhiri APIへのブラウザからの直接
リクエストをローカルでも動作確認できるようにするため)。ビルドや
ホットリロードの仕組みは無い。
