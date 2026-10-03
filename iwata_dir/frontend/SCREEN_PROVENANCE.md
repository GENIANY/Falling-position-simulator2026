# 画面の出典と現役化境界

**現在の読み方（0.59文書監査／実装0.58）：** 本書は育てた操作模型の具体的な画面・用途を、どの現役ソースへ引き継いだかを記す。下の版別追補は当時の境界であり、現在の未実装一覧ではない。現操作は[COMMANDS](../docs/COMMANDS.md)、処理と保存契約は[実装ノート](../docs/IMPLEMENTATION_NOTES.md)、受入範囲は[S36](../BOOTSTRAP_RUNBOOK.html#S36)を読む。

0.53の追補は保存JRAと既存の候補・固定結果の接点を記す。現source照合と、実JRAの親子比較・合成領域・選択詳細・保存再読の代表行程を限定確認した。以下の原資料対応と0.49までの記録を保持し、今回の全画面再受入へ読み替えない。

元資料は `references/design_trials/hover_surface_pick_correction_0401.zip`（SHA256 `8356df3cc8f2184d5418fe3d84d1e1d274b7646f3b81be6210c07094b3d7a214`）内の `workflow-ui-0401/`。原ZIPは変更しない。完成していた用途別の画面配置、候補と延期列、概要から選択詳細、気象の4画面、季節計画、2Dと3Dの関係を具体的なDOM/CSS/描画として引き継ぐ。

## 現役ソースの対応

| 元資料内の実体 | 現役の実体 | 変更する境界 |
|---|---|---|
| forecast/index.html, style.css | src/screens/forecast/markup.html, screen.css | 共通headerをAppへ。rootスコープのCSS。実入力と保存気象の専用portal |
| forecast/app.js, core340.js | src/screens/forecast/controller.js | coreの宣言を同じcontrollerのlexical scopeへ統合。実モードではReactのreadonly投影と操作意図を使う |
| forecast/data.js, math.js, season-adapter.js | 同名のsrc/screens/forecast/下 | data/season-adapterは人工例の経路。mathの領域包含判定は実着地点にも使用し、経験域の実集合統計はPython共通分析から受ける。install(scope)で局所依存にする |
| forecast/scene-document.js, export390.js, appearance390.js, map-style-guard401.js, hover400.mjs, hover-geometry400.mjs | 同名のsrc/screens/forecast/下 | 実結果の出所、ASL、停止点、スコープ寿命と独立した固定Leaflet stylesheetの検証へ適応 |
| weather/index.html, style.css, app.js | src/screens/weather/markup.html, screen.css, controller.js | 共通shell、保存した分析条件、季節提案への受渡し |
| weather/fixture.js, direction-key.js, impact-map.js | 同名のsrc/screens/weather/下 | 実過去場へ接続済みと扱わず人工例を保持。0.47では通常地図を初期表示し、写真へ切替 |
| shared/scene-style.js, hover-labels.mjs, band-readout.mjs | src/screens/shared/下 | 2D/3D/出力の共通表示定義 |
| scene3d/index.html, style.css, src/*, fixtures/* | frontend/scene3d/下 | 既存rendererのiframe境界を保持。人工/実source flag、原実軌道、停止群を受領 |

Reactの `App` / `useWorkspace` が実候補、草案、固定runの選択、保存計画の正本。`ForecastScreen`→`projection`→controllerはその読取投影で、controllerは再び候補を勝手に計算・上書きしない。controllerから編集・候補追加・延期作成・実行・削除・復元の意図をAppへ返す。map視点、選択ID、色、表示状態はcontrollerの局所状態を `ui_state.forecast_real` へ保存する。

`forecast_fixture` / `weather_fixture` / `season_fixture` は同じ保存計画の別namespace。実の風や履歴の欠測を人工データで補完しない。実n=1では原recordの不等間隔時刻、相境界、着地/停止を保持し、50/90/95%域は標本不足のため生成しない。0.46時点の季節・気象画面は人工例だった。0.49の実集計接続は下記へ分け、実季節飛行は未接続のまま保持する。

## 配布と依存

`npm ci` のlockfileでLeaflet 1.9.4、Plotly 4.1.1、Cesium 1.145.0を固定。旧ZIPのvendor巨大bundleを別に複製せずnpmの同版を使用する。`vite.config.ts` がbuild時に `frontend/scene3d`→`<build.outDir>/scene3d`、npm Cesium build→`<build.outDir>/cesium`、Leaflet画像→`<build.outDir>/assets/images` を生成し、Python APIが同URLで配信する。Google写真タイルとキーは保存しない。写真接続は手動操作であり、自動で再接続しない。

`scene3d/THIRD_PARTY_NOTICES.txt` は当該固定npmパッケージのLICENSEとCesium ThirdParty情報を収録する。旧ZIPの説明だけを現パッケージのライセンス根拠にしない。

## 保持する旧実体

0.45の `src/MapPanel.tsx`, `src/HistoryPanel.tsx`, `src/style.css` は比較用の過去実装として保持されるが、現 `App`/`main` からimportされない。`src/screens/forecast/core340.js` は元分割の照合用保持で、現controllerでは同内容を同一scopeへ統合して使う。`scene3d/src/receipt-status.js` は旧rendererの受領状態補助で現importなし。これらを現役の画面依存として構造図へ描かない。

本資料は出典・所有境界を示す。現在の操作行程の受入と未確認はS36、0.46の統合履歴はS35へ戻る。


## 機能照合後の補修

0.40.1 r2の画面機能を照合し、旧headにあった `mapDisplayGuardStyle` を予報markup内のrootスコープinline CSSへ復元した。これはLeaflet stylesheetの再取得とは別に、CSS故障中のpane不可視化と画面外への流出防止を担う。人工候補JSONの保存は旧処理を保持し、候補管理の「人工候補JSONを開く」から旧形式を復元する。共通APIの計画・実固定結果の読込とは区別する。

同じForecast画面での2D/3D往復はrenderer iframeと接続を保持する。一方、実/人工の表示データ切替、気象/季節への用途変更、保存計画reloadでは画面をunmountするため3D接続も終了する。接続を保ったままこれらを切り替えられるとは扱わない。人工候補の削除直後undoは保持し、実候補では固定runを残して草案から外す。実候補の即時undoは未接続と表示する。

## 0.47 実取得と条件編集の接点

旧画面の共通準備に `WeatherPreparation` をportalとして置く。保存した配布一覧を明示更新し、初期時刻を固定、候補familyの放球〜最大飛行時間から取得計画を作り、進捗・取消・再試行を経て完成気象を明示適用する。`weatherAcquisition` はこのAPI形と入力/適用前の必要条件を扱い、`api` が実APIへ送る。`useWorkspace.refreshSources` は源一覧だけを更新し、草案・固定run・表示選択をreloadしない。取得する気象の有効時刻はrun+leadから示す。地図の橙破線は取得計画、灰破線は表示結果の保存気象で、人工分散とは別の情報である。

`ConfigEditor` は現在選択中の科学入力をCandidate.configに置く。非選択方式の編集値は `ui_state.forecast_real.editor_models[candidateId]` へ保持し、`modelDrafts` の純粋な切替関数で退避/復元する。AppはconfigとこのUI値を一つの更新として保存する。既存保存計画に退避値がない場合、別方式は初期値から始める。取得フォーム・選択plan/job IDは同namespaceのweatherPreparationへ置き、計画内容/取得状態の正本はAPIに保存される。

通常地図stdを初期表示し、noneを製品選択肢から除いた。地図の通信失敗は背景の案内と再試行に局在させ、計算結果/入力/領域/3D接続を再作成しない。用途の終了後に古いタイルや気象図用画像の応答が新画面へ書き込まないよう寿命・世代で破棄する。Google写真3Dの接続方法・キー寿命は変更しない。0.47の有限検査と実操作はS36に記録する。

共通準備は地図を覆う旧絶対配置から通常の文書flowへ変更し、気象/禁止領域を切り替える。気象の取得条件・固定計画・取得適用は表示段階のみを切り替え、DOMと入力を維持する。全段に取得状況の短い表示を残し、取得完了だけでは段階遷移・候補適用を起こさない。地図での確認は準備を畳み、run/必要窓/新旧境界の区別と条件へ戻る入口を地図側に残す。これは実取得行程を成熟画面へ接続するための面積・導線変更であり、候補や分散の表示構造を再発明する変更ではない。


## 0.48 固定標本集合への接点

`Candidate.sampling` は選択中の科学草案（nullは一飛行）。`SamplingEditor` は元量・単位・一様な仮幅・理由・N・seedと共通実現値で比較する候補を編集する。`ensembleDomain` はこの契約と表示参照、`ensembleApi` は保存計画／集合／snapshot／選択分析／原履歴の通信、`useEnsembleWorkspace` は受付・取消・再開・明示表示を受け持つ。延期は親の元実現値と対応し、独立モデル比較も同じplanへ含められる。抽選や物理積分をfrontendでは行わない。

表示の正本は `Project.compare_results` の判別型。既存runと `ensemble_id/snapshot_id/case_id` を区別する。集合内部の一飛行runは通常のn=1選択へ紛れ込ませない。計算が完了しただけでは表示中の固定結果を切り替えず、ユーザーの明示選択で切り替える。n=1と集合は候補ごとの表示選択世代を共有し、遅い通信が新しい選択を上書きしない。jobのepoch/state_revisionを逆戻りさせない。取消・再開・計画・分析の不明応答には同じ要求IDを再利用する。

`ForecastScreen` → `ensembleProjection` がコンパクト台帳・原履歴・共通分析をcontroller向けに投影する。全予定N、物理結果、位置のある試行、読込済み履歴、各相／量で有効な記録を分ける。未実行・失敗・位置を持たない停止へ人工の位置や風を補わない。概要の経験域／全干渉着地点の外周／相別の平均と帯は `balloon_sim.ensemble.statistics` の固定出力を描く。点・線に退化した経験域へ面積を付けず、点線のカーソル読取幅は表示操作だけの許容幅とする。実履歴の風は必要時に原runから読む。

選択は固定結果ID・領域・trial ID集合へ束縛し、保存した選択分析IDを読戻す。領域群は既存mathの実着地点判定が正本で、分析serverは受け取った選択IDの統計と判定来歴を保存する。再読時に固定点と固定領域のID集合を照合する。母数や選択が合わない状態を同番号の新集合へ再結合しない。干渉外周だけの読込失敗でも、元の点と件数は保持する。

2D／3D／KMLは同じscene documentのPoint／LineString／Polygonを使用する。3D詳細の選択母数には非空間試行も含め、位置を持つID部分集合と非空間数を明示検査する。経過時刻ごとの平均経路は実在する代表一機ではない。相の終端を含む平均・10–90分位と、着地後を除外する瞬間風の分布は別の母集団定義を表示する。64MiBの履歴分析上限に達した場合も着地の経験域・件数・台帳を保ち、標本を絞る入口と未生成理由を示す。

この境界は一つの固定GFSに対する一変量の仮の機体感度である。校正された気象誤差・多変量依存・実過去場・科学的精度の採用へは広げない。人工画面と既存n=1、写真3Dのキーと接続寿命は引き続き別管理。有限試験と実UIの確認範囲はS36に記録する。

## 0.49 実風統計と実集合の待機・保存を結ぶ

既存の年間4図・地域12面/頁・凡例・SVG保存を継承し、`weather/sources`の人工/実adapterが共通`viewModel`へ渡す。`plots`と`export`を両者で共有する。実側は`useClimateWorkspace`が草案・固定artifact・要求寿命を持ち、`WeatherScreen`とruntimeは表示意図を結ぶ。人工profile/風配/打上げ影響の経路は保持するが、提供期間統計から作った実飛行や原分布として表示しない。

`weather_real`は固定集計参照と未適用query、表示面/頁/尺度を保存する。地理院背景は地域図だけで要求し、年間図の保存物に未使用背景の出典を付けない。入力変更だけでは旧図を描き替えず、固定集計の適用時に更新する。実MCの原履歴は現在の選択に対応した集計の受入後に最大4件ずつ読み、終了画面や旧選択の待機要求を増やさない。時刻スライダーと復元の機械精度内の終端丸めは表示側で補正し、元飛行recordsを変えない。

有限UI・実データ・保存図の受入/未確認はS36、式はTHEORY、実階層はPROGRAMに戻る。0.49でGoogle接続や全3D操作を再受入したとは扱わない。

## 0.53候補 保存JRAと、現在の気象・固定結果の照合

0.52の保存JRA地上接続例を、既存の実計算側の共通準備・候補・延期列へ渡す。0.40.1 r2由来の地図、禁止領域、概要→同じ標本の詳細、保存再読を使い、新しい一窓専用画面や地図rendererへ置き換えない。上の0.48「固定GFS」の範囲は当時の接続として保持し、今回の後続範囲をここへ分ける。

`WeatherPreparation`は保存例の選択と既存GFS取得操作を区別する。保存例からの候補作成はdefault_configを複写し、既存候補への適用は物理入力を保持する。`ConfigEditor`と既存日時変換はJSTの秒を保持してUTCへ渡し、Appは親の機体入力と延期差から子の完全入力を具体化する。JRAは解析有効時刻として表示し、GFSのrun/leadや固定pressure軸へ偽装しない。地図で位置だけ動かしても旧ASL高度を新地点の地表とみなさない。

n=1と集合の表示投影は、現在のsource内容と固定run/caseのweather snapshotを照合する。既存の草案入力差分とは別に、`same`（整合）、`changed`（内容差を確認）、`unavailable`（現在場が利用不能）、`unverified`（旧hash等の照合情報不足）を扱う。旧snapshotの不足欄を現在値で埋めない。これは固定結果GETの `loading / missing / error / ready` とは別軸で、結果GETの404と現在場の欠落を混同しない。

`ForecastScreen`はsource一覧だけの更新も表示判定へ渡すが、固定map/履歴/支持境界は計算時のsnapshotを使う。一覧の更新で候補revision・表示選択・保存済み状態を変えず、原場が無くても保存結果を保持する。旧workspaceへ必須欄を増やして閲覧を拒否する移行にはしない。固定frontend候補の`domain.weatherIdentity / weatherMatch / runWeatherSnapshot`と、`ForecastScreen.sourceSignature`がこの境界を担う。入力差分は`draftInputsMatchRun / collectionInputsMatch`へ分離する。実UIで観察した注記と、四照合状態の専用試験の範囲はS36へ分ける。

実風統計の年間・地域図は引き続き固定集計artifactを読む。今回の東海一窓を北海道統計から選んだ実証にはせず、実集計から原日時窓へのhandoff、任意過去窓の取得UI、季節の複数窓集合は未接続として残す。n=1に分散面や確率を作らず、B近似の精度・全GUI・Google写真3Dを今回再受入したとは記さない。有限実行・画面観察はS36、保存契約は実装ノート、操作はCOMMANDS C-09/C-11へ戻る。


## 0.55 立体経路の追補

0.40.1 r2由来の写真3D、地表の点/帯/領域・ホバー・視点を保持し、既存scene-documentから同じ原経路の空中線と連続カーテンを追加した。実ASLは同梱EGM96で表示座標だけ換算し、KMLや固定結果を変えない。地表線との一組切替、幕のみOFF、明示fitを追加し、通常更新で接続や視点を作り直さない。部分幕の初稿を目的不適合として撤回した判断はD-195、批評と実画面はS36へ戻る。人工AGLは地物高が必要な別の限定経路である。


## 0.55〜0.58の後続接続を読む

0.55の干渉表示修復では、概要の干渉着地点を個別点・件数・同じ群の詳細へ戻した。上の0.48「全干渉着地点の外周」は当時の表示であり、現在の点表示の仕様ではない（D-174、S36 `s36-hit-fix550`）。原日時JRA窓と気象関心の受渡しは有限例を共通計算へ接続したが、任意過去取得や代表季節飛行の完成を意味しない（D-194）。

0.56〜0.58の実気象分析は、人工例で育てた問いと図の関係を保持し、支持する実資料で同じ中心・幅・条件選択を扱う。`weather/sources` は提供十年集計DBとJRA-3Q/ERA5の2024年原時刻標本を区別し、共通 `viewModel`・`plots`・`export` へ渡す。原標本の半月中央値2本と月全体p10–p90、UTCマスク、地点風配、年間48区分と面探索はD-198/199とCOMMANDSへ戻る。旧十年DBの24半月を原標本48区分や瞬時の共同場へ読み替えず、保存済み結果を現在sourceで無断再計算しない。画面の共通化は資料にない統計を埋める理由にならない。
