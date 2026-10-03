---
document_id: BJP-CONTENT-MAP
revision: 0.59.0
as_of: 2026-10-02
role: 現行ファイルの内容・契約・探索と一度限りの受入先
---

# 現在のファイル内容マップ

[更新:0.59.0] [確認:0.59.0] — MAP

このマップは現行の一組を表す。版別フォルダーを増やさない。各行は「今なぜここにあるか」を示す。現在のタスク状態はHTML/BACKLOGの担当範囲で編集し、ここへ重複記入しない。

## 1. 読む目的から探す

<a id="document-roles"></a>
### 文書ごとの問いと編集元

目的に合う行から担当資料へ進む。以下の全表を順番に読む必要はない。実体の役割・存続条件はCONTINUITY、点検の時点・範囲はHEALTHが正本。本表はその読み方を示し、進捗や採否を別に管理する台帳にはしない。

| 読者が答えたい問い | 担当資料・編集元 | 更新するときに守る責務 |
|---|---|---|
| 今どの版を、どこから読むか | [README](README.md)、作業者への短い入口は[AGENTS](AGENTS.md) | 現在入口と安定した開始/終了規則。過去各版の進捗全文を積み上げない |
| 何を目指し、何を優先するか | [PROJECT_CONTEXT](PROJECT_CONTEXT.md) | 現在の要求・採用方針・重点と、RPTの原意。実施ログを第1節へ複写しない |
| どんな利用像を、どんな責務へ具体化するか | [SIMULATOR_VISION](docs/SIMULATOR_VISION.html)、[INTEGRATION_DESIGN](docs/INTEGRATION_DESIGN.html) | 用途・問い・画面の意図と、入力/計算/保存/分析の設計。模型や提案を実装済みとしない |
| 目的地へどう進み、何をもって次へ進むか | [PROJECT_PLAN.md](docs/PROJECT_PLAN.md) | 中長期の工程・依存・受入。TeX/PDFは生成物。過去の状態表を現在の未実装一覧へ流用しない |
| なぜその案を採り、何を捨てたか | [DECISIONS](docs/DECISIONS.md) | 選択肢・証拠・採否・代償・再検討条件。原決定の時点を保持し、訂正・追加採否を対応する記録へ結ぶ |
| 次に誰が何を閉じるか／何がまだ分からないか | [BACKLOG](docs/BACKLOG.csv)／[UNCERTAINTIES](docs/UNCERTAINTIES.csv) | 前者は作業の依存と受入、後者は未決・不足が妨げる判断。部分実装を未着手へ戻さず、未検証を完了にしない |
| 今誰が何を行い、実際には何が起きたか | [BOOTSTRAP_RUNBOOK](BOOTSTRAP_RUNBOOK.html#start) | startは現在案内、本文は指示→行動→結果・理由の時系列。人間への次の依頼も現在節へ置く。旧H01等の完了手順を再実行せず、発行した指示・失敗・当時の未了を遡及して消さない |
| 同じ情報からどう良い仕事を継続するか | [DOCUMENT_CONTROL](docs/DOCUMENT_CONTROL.md)、[WORK_ORDER_TEMPLATE](docs/WORK_ORDER_TEMPLATE.md)、[LESSONS](docs/LESSONS.md) | 原則/運用契約、未発行の依頼様式、具体的な失敗と改善を分ける。テンプレートや古い教訓を現在の命令にしない |
| どう起動し、一巡使い、失敗から戻るか | [COMMANDS](docs/COMMANDS.md)、[backend/README](backend/README.md) | 目的→前提→入力/副作用→結果→再開。通常起動と任意の気象資料登録を区別し、過去試験コマンドで代用しない |
| 実装はどの階層と依存で成り立つか | [PROGRAM_GUIDE](docs/PROGRAM_GUIDE.pdf)（編集元[TeX](docs/PROGRAM_GUIDE.tex)）、[IMPLEMENTATION_INDEX](docs/IMPLEMENTATION_INDEX.json) | ガイドは実階層を図と短い責務/横依存で読む。索引は実symbol・署名・検査への逆引き。処理の羅列や索引の全行掲載で代用しない |
| 何を仮定し、どの量をどう計算するか | [THEORY_GUIDE](docs/THEORY_GUIDE.pdf)（編集元[TeX](docs/THEORY_GUIDE.tex)） | 仮定・式・単位・母数・適用域から実装/検査へ結ぶ。式の掲載や実行成功を精度保証にしない |
| 入出力・保存・失敗・互換性をどう実装するか | [IMPLEMENTATION_NOTES](docs/IMPLEMENTATION_NOTES.md) | API/schema、状態遷移、固定結果と草案、再開の詳細。構造ガイドや利用者画面へ詳細を散らさない |
| 気象と物理モデルは何を要求・提供するか | [ENVIRONMENT_CONTRACT](docs/ENVIRONMENT_CONTRACT.md) | 内部の場API、能力・構成・支持不足の契約。未実装のモデルと既存APIの動作を区別する |
| 外部データをどこから、どの時刻/高さで得られるか | [WEATHER_DATA_GUIDE](docs/WEATHER_DATA_GUIDE.md) | 配布経路・量・暦・鉛直支持・取得の落とし穴。調査時点と実取得範囲を明記し、内部API仕様と混同しない |
| 環境と文書をどう再生成するか | [BUILD](docs/BUILD.md) | 依存、生成元、コマンド、失敗時の扱い。直近の生成/表示実績はREFERENCE_LOG、元の科学内容の受入は別 |
| どこに何があり、今回どこまで確かめたか | [CONTENT_MAP](#document-roles)／[REFERENCE_LOG](REFERENCE_LOG.md) | 前者は目的別の探索、後者は実読の理由・範囲・原票・未確認。対象SHAで必要本文を取得し、確認印だけで科学やUIの完全性を主張しない |
| 版・保存・確認の事実をどう同定するか | [VERSION_HISTORY](docs/VERSION_HISTORY.json)／[CONTENT_HEALTH](docs/CONTENT_HEALTH.json)／[CONTINUITY_CONTRACT](docs/CONTINUITY_CONTRACT.json) | 版とGit遷移（HTML editingは表示）／範囲・指紋・期限・証拠（DC-START/CLOSE）／役割・寿命・論証・理由。機械整合は文書の効用を自動証明しない |
| 外部研究や提供資料をどう設計へ戻すか | [研究入口](docs/research/README.md)、[SOURCES](references/SOURCES.json)、[風](references/WIND_REPORT_REVIEW.md)／[Excel](references/EXCEL_ANALYSIS_REVIEW.md)／[研究返却](references/research_returns/Q420-00/2026-09-29-r7/CODEX_REVIEW.md)のレビュー | 依頼・根拠束・受領原本・採否を分ける。発行済み研究依頼と参考原本を現在仕様へ書き換えず、現行の採否へ導く |
| 成熟した模型の何を引き継いだか | [SCREEN_PROVENANCE](frontend/SCREEN_PROVENANCE.md)、[模型の保存入口](docs/SIMULATOR_VISION.html#model-archive) | 原DOM/CSS/操作の出典と現役ソースの境界。現在の操作/契約/実績は担当資料へ戻す |

### 実装・判断の具体的な接点から深掘りする

現在の設計を議論するときは、[CONTEXT第1節](PROJECT_CONTEXT.md)で三用途と到達点を確認し、[接続設計](docs/INTEGRATION_DESIGN.html)から入力・計算・保存・分析の関係を読む。現在の操作・実績は[指示書start](BOOTSTRAP_RUNBOOK.html#start)が案内するS36の節へ進む。設計の経緯はD-180/181、参考器の比較はD-182と[INTEGRATION7.2](docs/INTEGRATION_DESIGN.html#framework-candidate)、第7巡研究の採否はD-183と[受領評価](references/research_returns/Q420-00/2026-09-29-r7/CODEX_REVIEW.md)、育てた画面を素材にする方針はD-185と[INTEGRATION7.3](docs/INTEGRATION_DESIGN.html#gui-integration460)へ戻る。次表は具体的な実装接点・過去記録を探すための逆引きであり、上の文書役割表をもう一度管理するものではない。

Chatへ研究を渡す場合は[研究入口](docs/research/README.md)から始める。[BRIEF](docs/research/BRIEF.md)がニーズと相互依存、[UI_WALKTHROUGH](docs/research/UI_WALKTHROUGH.md)が比較・掘下げ・次の操作の実像を共有する。[課題一覧](docs/research/TASKS.md)のQ420-00から重点を選び直し、必要なら旧5課題を深める。[回答様式](docs/research/RESPONSE_TEMPLATE.md)は研究を設計へ戻す編集の助けであり、欄の充足を目的にしない。内容をどう批評して直したかは[REVIEW_042](docs/research/REVIEW_042.md)へ戻る。配布する版と抽出範囲はpacket_sources.jsonと生成した根拠束で固定し、現在の採否や進捗の別原本にはしない。原資料の全体が必要なら、下記の正本から追加する。外側の一時フォルダーだけにある証拠を、Gitコピーに含まれるものとして依頼しない。

| 目的 | 最初 | 次に読むもの |
|---|---|---|
| 育てた具体画面が現役ソースのどこに移ったか | frontend/SCREEN_PROVENANCE.md | 原本はreferences/design_trials/hover_surface_pick_correction_0401.zipのworkflow-ui-0401。予報/詳細/季節はfrontend/src/screens/forecast、気象4画面はweather、独立3D rendererはfrontend/scene3d。原本を消さず、各用途の具体画面と変更点を対応させる。PROGRAMのfrontend枝から責務へ降りる |
| 同じ計画で画面を行き来し、入力と固定結果を読む | frontend/src/App.tsx → screens/ForecastScreen.tsx・WeatherScreen.tsx | useWorkspace/workspaceStateが共通候補・固定run・保存を担当する。ForecastScreenは実入力の専用領域とprojectionを介して既存画面へ接続し、WeatherScreenは気象表示と季節提案をつなぐ。実n=1/集合、実風の固定集計、人工例を区別する。入力・保存の詳細はIMPLEMENTATION_NOTES、行程の観察はS35の履歴とS36 |
| 保存結果の未読・失敗から、同じ選択へ戻る | frontend/src/fixedResultRead.ts → useWorkspace/useEnsembleWorkspace/useClimateWorkspace → screens | 共通型/表示判定と各hookの読取り寿命を分ける。草案差分とGET状態を混ぜず、詳細の群/時刻を保持して明示再読へ戻す。操作はCOMMANDS、反例と有限受入はS36/D189 |
| 気象窓を延ばす際に既存rawを使う | backend/weather/service.py → balloon_sim/environment/gfs.py | 登録済み完成assetだけを提供し、要求とbytesを照合して独立コピー。不足時刻を取得し、新全窓を復号・検査する。原本を変えず、通信量とコピーを含む総保全量を区別する。詳細はWEATHER_DATA_GUIDE/IMPLEMENTATION_NOTES |
| 現在予報を取得し、通信が途切れても状況を確認する | WeatherPreparation/useWorkspace → jobObservation → api.readRequest、backend/weather/catalog | GET観測不能と計算状態・入力/表示結果を分ける。一覧の部分失敗は表示し、POSTを自動再送しない。実運用の有限確認はS36/D-193、契約はIMPLEMENTATION_NOTES |
| 受付が不明でも同じ計算と編集へ戻る | serviceIdentity / writeLease / submissionLedger → singleSubmission / recordedMutation → useWorkspace / useEnsembleWorkspace | 台帳instance・単一送信タブ・固定送信前要求・受付GET照合を分ける。応答欠落を自動新規POSTへ変えず、保存照合はHTTP既定値だけを正規化して後続編集を残す。契約はIMPLEMENTATION_NOTES、有限故障検査はS36/D-194。明示した協調引継ぎとAPI受付＋台帳更新までの所有、固定case分析/原履歴GETと部分群の分離はD-196/今回修復のS36へ戻る |
| 気象分析で選んだ関心を、原日時の飛行比較へ進める | ClimateFlightHandoff → historicalDomain / historicalWorkspace → HistoricalPreparation、backend/historical_catalog → ensemble/historical_planning | 集計への関心historicalInterestと詳細標本selectionContextを分ける。原UTC窓・全予定数・未取得理由を固定し、既存worker/飛行核/集合結果へつなぐ。historicalTypesは共有型の末端。期間平均を瞬時場へ変換せず、2窓の例を代表季節MCへ読み替えない |
| 別地点の放球高度を、モデル地表から明示的に決める | ConfigEditor → GroundPreparation → api.ground → ApplicationService.weather_ground | 場/hash・地点・UTCに束縛して照会し、現在ASLとの差と余裕の明示適用を返す。ASLだけの編集では地表を再利用できる。別地形式・飛行workerへ複製せず、実DEMと区別する |
| 元量を共有して延期・モデル・干渉群を比較する | balloon_sim/ensemble → backend/ensemble → frontend/src/useEnsembleWorkspace.ts | 純粋核が元量固定・解決と経験域/相別統計、backendが全N台帳/attempt/固定snapshotと保存、frontendが条件棚と既存画面への受渡しを担当する。式はTHEORY第8章、構造はPROGRAM、操作はCOMMANDS C09、厳密契約はIMPLEMENTATION_NOTES。有限実績はS36/D187 |
| 元UTCの保存JRAを飛行へつなぎ、支持と近似を読む | 保存bundle → balloon_sim/environment/storage.py → Jra3qModelField / Jra3qSurfaceField → ModelLevelField / ModelSurfaceField | 原応答の検査/変換と現役照会を分ける。旧strictの支持停止はCOMMANDS C-10/S36/D190、明示Bの地上完飛行はC-11/S36/D-191。既存GUIの保存例・秒/延期・現在sourceと固定結果の照合はbackend/application.py、frontend/src/domain.tsとForecastScreen、COMMANDS C-09/S36/D-192へ戻る。Bは全高度の内挿順と仮想支持を変える暫定再構成で、2m/10m近似を隠さない。式はTHEORY、階層はPROGRAM。半月DBから瞬時場を作らない |
| 実風の中心・幅・方向を、月/UTC/面/地点を変えて比べる | backend/climate/{source,archive,service} → useClimateWorkspace → weather/climateController | 旧2016–2025年DBの24半月と、JRA-3Q/ERA5の2024年原標本を別資料に保つ。原標本の半月中央値2本＋月p10–p90、地域集計と選択元格子1点の風配、年間図だけの48区分、月/季節、UTC、面探索を分ける。保存済み集計・未適用草案・生成時条件付きSVGの境界はIMPLEMENTATION_NOTES、操作は[COMMANDS C-09](docs/COMMANDS.md#c-09同じ計画で画面を使い計算保存再開する)、登録/再取得CLIは[C-CLIMATE-RAW](docs/COMMANDS.md#C-CLIMATE-RAW)、母数/重みはTHEORYの気象統計、責務はPROGRAMへ。採否はD-197〜199、有限実績はS36の0.56〜0.58節。期間統計から瞬時の飛行場は作らない |
| 画面内の描画・名称・表示復元を変更する | frontend/src/screens/{forecast,weather}/runtime.ts → controller.js | runtimeがmarkup.html/screen.cssと補助moduleを読み、lifecycle.tsのscopeを渡す。予報controllerの操作/図表/地図と、気象controllerから実資料を担当するclimateControllerへの委譲を分ける。weatherのplotsは年間/地域、monthlyProfilesは月分位、climateDistributionsは平均補助/一点風配、exportは生成時条件を固定する。sharedは帯・名称・色、forecast/projection.tsは実固定結果の描画変換。旧MapPanel/HistoryPanel/styleは現Appの表示経路外として保持する |
| 3Dへの受渡し、地物への投影と接続状態を追う | frontend/src/screens/forecast/scene-document.js → frontend/scene3d/src/{protocol,main}.js | 独立rendererへ同じ表示対象のsnapshotを送る。scene3dは現役sourceで、vite.config.tsがdist/scene3dへコピーする。Cesiumの配布実体はnpm解決物からdist/cesiumへ生成し、Gitの独自sourceとは分ける。無通信の人工surface fixtureとGoogle写真接続の観察を区別する |
| 0.43〜0.48の器の比較と画面統合の経緯を読む | docs/INTEGRATION_DESIGN.html#framework-candidate | 参考FE/BEと既存模型/核の再利用・作替え、正本・再現開発、三用途の行程を比較した記録。固定参考と担当レビューはreferences/design_trials/framework_assessment_043.zip。0.45の計算/保存はframework_integration_045.zip、0.46は0.40.1 r2の具体画面、0.47は実GFS取得、0.48は元量共有/集合分析へ接続した。当時の未了を現行機能一覧にせず、現在の操作/実階層/APIはCOMMANDS/PROGRAM/IMPLEMENTATION_NOTES、受入はstartが案内する最新節へ戻る。簡略二枚カードを後続UIの基準にしない方針と、科学採用の境界を保つ |
| 模型を実計算へつなぐ設計を読む | docs/INTEGRATION_DESIGN.html | 三用途の入力例、標本対応、結果/分析/図の寿命、長期重み、ジョブと保存。未決が変える設計と代案から、ENVの現契約・PLAN10.6・研究課題へ進む |
| Chatへ研究を依頼し、返答を設計へ戻す | docs/research/README.md | BRIEF/UI_WALKTHROUGH、Q420-00と深掘り課題、RESPONSE_TEMPLATE、packet_sources.jsonと生成器から発行時の資料束を固定する。既受領0.42 rev7、未発行の生成候補、現行実装との差を区別する。発行/受領はT-017と現行手順、当時の受領・採否はS35/D-183へ戻る |
| 気象のAPI/時刻/鉛直支持/取得経路を調べる | docs/WEATHER_DATA_GUIDE.md | 実装済みAPIはENVIRONMENT_CONTRACT、現在の行動はHTML start、採否はDECISIONS。過去の用途再読はACT-210、本体初版の検査/再現はACT-200、JRA試作はACT-180、モデル面原取得はACT-170、初回調査はACT-160。最新の検査はREFERENCE_LOGの現行欄へ戻る |
| 全作業へ適用する根本原則 | docs/DOCUMENT_CONTROL.mdのDC-JUDGMENT | 開始はREADME R1-J/DC-START、作業依頼はWORK_ORDER、終了はDC-CLOSE。原則導入の履歴はS31/D-160、現在の適用はHTML start |
| 将来の分析用途から現在の設計を考える | docs/PROJECT_PLAN.md 10.5 / 5.2 | 風資料の問い→標本と比較→必要責務→現構造の費用→最初の一体成果。D-164、AUD-250、T-016。実装済みの地図はPROGRAM_GUIDE |
| 具体的な失敗の分析と設計課題 | docs/LESSONS.md GAP-024 | S30の設計課題からS32の修復/再評価へ接続する。根本原則はLESSONSだけに置かずDC-JUDGMENTへ戻る |
| 環境の確定値と未確認 | docs/BUILD.md | 現在の環境・生成手順はBUILD、最新の生成実績はREFERENCE_LOG。導入履歴はCONTEXT第22節とHTML S12/GEN-120、PLAN 0.15.0の当時の生成と全22頁表示はACT-150。過去環境はCONTEXT第12/15節とHTML S10-1/2、残件はT-012 |
| 初期環境点検の失敗・訂正を遡る | HTML F01-2/3 | ER-081-01の正式原文とCHK-010の当時の記録。現在の実行操作はCOMMANDS/start、今回の根拠はREFERENCE_LOGへ進む |
| 完了した0.3移行を監査する | 本書第3節 | HTML S06の実施記録 |
| ローカルZIPを残す/整理する条件 | HTML retention（RET-01〜05） | DOCUMENT_CONTROLのDC-RETENTION、Gitにない固有原資料の保管 |
| 開始文・Projectの実際の指示を確認する | README R0-E / HTML S07-2・H01-2 | CONTINUITY_CONTRACTのentry_contract。過去S08の試験文と通常入口を区別 |
| 引継ぎの実証 | HTML S07〜S09 | READMEと現在のACCESS_PROBE.md |
| 構造ガイドの説明例 | references/Program_Guide_FractalJP_Settings.pdf | 同名TeX。理論/実装の検証は未実施 |

### 0.51で導入した元時刻場の接点を探す

| 追加対象のパス | 役割と読む境界 |
|---|---|
| `balloon_sim/environment/model_levels.py` | 製品暦・I/Oから分離した列Hの再構成。全正重み列の支持を要求し、地表未支持を補外しない。 |
| `balloon_sim/environment/jra3q.py` | JRA解析UTC・100層・既知半層係数とfull圧力を検証してモデル面場へ渡す。 |
| `tools/prepare_jra3q_flight_fixture.py` | 固定原応答を保存bundleへ変換・読戻しする。飛行runtimeから旧toolを呼ぶ経路とは分ける。 |
| `tests/test_jra3q_flight_field.py` | 圧力・支持・保存dispatchと既存飛行の有限反例。任意取得や実機精度の受入ではない。 |
| `examples/jra3q-support-flight.json` | 空中開始・指定破裂・下端停止を読むCLI診断入力。実打上げの既定条件ではない。 |
| `references/development_evidence/historical_field510.zip` | 固定原本変換・5診断行程・回帰・批評の有限証拠束。154実体のbyte/hash/CRCを照合。Git保存の状態はREFERENCE_LOGとS36。 |

上は役割から探す索引である。登録の編集元と下の二つの生成一覧は管理処理で同期し、生成した証拠束とGit保存の状態は区別する。

### 本体を使い、説明と検査をたどる

| 目的 | 担当実体 | 読み取る範囲 |
|---|---|---|
| 保存GFSから全飛行を再現 | docs/COMMANDS.md、examples、references/flight_fixture | 任意UTCの設定、標本と来歴、実行/終了理由、オフライン再現 |
| 式・仮定・近似を検討 | docs/THEORY_GUIDE.tex / .pdf / .txt | 座標と高さ、同高度再構成、湿潤密度、上昇/破裂/降下、SciPy RK45/event、独立検証と限界 |
| 実装を変更 | docs/PROGRAM_GUIDE.tex / .pdf / .txt、docs/IMPLEMENTATION_INDEX.json | 実在ファイル→class/function→内部helperの階層、包含/import/call/dataの区別、逆引きと変更の影響 |
| 処理・失敗・拡張の詳細を読む | docs/IMPLEMENTATION_NOTES.md | 構造図から分離した実装上の動作説明。式はTHEORY、操作はCOMMANDSへ接続 |
| 添付風報告と受入根拠を確認 | references/user_supplied/wind_analysis_report.pdf / .txt、references/WIND_REPORT_REVIEW.md | 原PDF、用途と判断の動機、原本hash/範囲、独立検算、不一致と未再現結果 |
| 機体入力・補助式・既存飛行の根拠を探す | references/EXCEL_ANALYSIS_REVIEW.md | §4の問い→Handbook章→設計方向から、原ZIPの対応本文へ進む。原計算書と改訂案、著者の検査と本プロジェクトの採用を区別する |
| 今回の原フィードバックへ戻る | references/user_supplied/feedback_v_0_40_1.pdf / .txt | PDFが原本、txtは検索補助。RPT-067の直接要求、具体案、Codexの解釈と採否はCONTEXT/S35/D-180で区別する |

## 2. 現在の実在パスと契約

0.24のD-162/AUD-240では、比較元C2-230の83実体に対して本体責務・資料・入口を修復し、S32で有限の受入を行った。これは当時の配置変更の根拠である。現在の全実在パスと役割は下の派生一覧を参照し、過去の件数や復帰手順を現在へ適用しない。今回の基準と変更範囲はCONTEXT第1節/S36、各実装の受入境界はENVと担当ガイドへ戻る。
「編集元」が自己以外のものは派生物であり独立編集しない。PDFの見た目を確認する人と、パスを読むAIの両方を想定する。

必要性・現在の立場・退役条件の編集元は`docs/CONTINUITY_CONTRACT.json`。下表は `python tools/check_contract.py . --views` の出力を挿入した表示であり、単独で編集しない。詳細仕様・実施状態・時点の編集元は変えない。

<!-- ASSET_VIEW_BEGIN -->
| 実体 | 現在の位置づけ・目的 | 使用先 | 退役を検討できる条件 |
|---|---|---|---|
| `.gitattributes` | active：既知テキストのLF契約。Gitの全体設定に依存させない | role:Git | 別の改行契約を全OSと指紋検査で受入後 |
| `.gitignore` | active：ローカル依存・生成ビルド・PythonキャッシュをGit保存対象から除外する。。ローカル依存・生成ビルド・PythonキャッシュをGit保存対象から除外する。。現役の画面・APIと既存核の接続を担当し、n=1の受入を分散/科学的精度へ広げない。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `ACCESS_PROBE.md` | active：非秘密の実取得試験入力。過去の取得経路の検証に使用。通常進捗ではない | README.md | 代替の実取得試験を受入れ、旧記録の意味を残した後 |
| `AGENTS.md` | active：コード作業者の短い入口。READMEへ導き独自の規約を複写しない | role:作業AI | 利用する作業者の入口を代替し参照を移した後 |
| `BOOTSTRAP_RUNBOOK.html` | active：実用操作と実施記録。操作本文・実施状態・コマンド原文の編集元。共通開始文だけはENTRY-01からの派生表示として扱う | role:ユーザー | 操作と実績を後継へ移行し復旧試験を受入後 |
| `CONTENT_MAP.md` | active：所在と管理ツールの説明。実体一覧の派生表示と意味による探索 | README.md | 所在探索と目的説明の後継を受入後 |
| `PROJECT_CONTEXT.md` | active：現在の要求・採用方針・焦点。短期の行動と中長期を結ぶ判断の編集元 | README.md | 要求と判断を後継へ移し利用者が承認後 |
| `README.md` | active：固定パスの復旧入口。毎作業のH確定と必読手順 | AGENTS.md | 外部Project入口を含めた移行を受入後 |
| `REFERENCE_LOG.md` | active：直近の読取と制約。何をなぜ読んだかと次の取得先を維持 | README.md | 参照理由を持つ後継入口ができた後 |
| `backend/README.md` | active：ローカルサービスの導入・起動・保存契約と検証の限界を案内する。。ローカルサービスの導入・起動・保存契約と検証の限界を案内する。。現役の画面・APIと既存核の接続を担当し、n=1の受入を分散/科学的精度へ広げない。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `backend/__init__.py` | active：既存計算核を利用するローカルアプリケーションのPythonパッケージを識別する。。既存計算核を利用するローカルアプリケーションのPythonパッケージを識別する。。現役の画面・APIと既存核の接続を担当し、n=1の受入を分散/科学的精度へ広げない。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `backend/app.py` | active：HTTPの受付をアプリケーションサービスへ接続し完成済み画面を配信する。。既存飛行/取得APIと保存風統計APIを接続する。長い風集約は同期def routeで実行し固定読出しと分ける。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `backend/application.py` | active：保存先UUID・固定source・単便受付/復旧・worker状態・明示原日時カタログを所有し、既存結果読取りを保持する。。保存先UUID・固定source・単便受付/復旧・worker状態・明示原日時カタログを所有し、既存結果読取りを保持する。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `backend/climate/__init__.py` | active：瞬時の飛行用気象場とは分けた保存風統計のpackageを識別する。。瞬時の飛行用気象場とは分けた保存風統計のpackageを識別する。 | backend/climate/source.py、backend/climate/service.py | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/climate/aggregation.py` | active：各格子の元件数で時間平均を結合してからGaussian地域平均・合成後cell平均の尺度を求め、異なる支持を拒否する。。既存集計を期間/時刻の比較へつなぐ0.56の現役実体。 | backend/climate/source.py、backend/climate/extensions.py | 固有の責務/根拠を後継へ引き継ぎ、利用先と対応検証を受け入れた後。 |
| `backend/climate/archive.py` | active：独立した原UTC風束を資料固有の支持で読み、地域平均・経験分位と選択native点の風配を固定summaryへ組み立てる。地域内外の一点と静穏分母を区別し、地点のみの変更で地域集計を再利用する。。原標本の取得・固定支持・統計図・保存をつなぐ0.57の実体。機能検証と科学的受入は分ける。 | backend/climate/service.py | 固有の責務・来歴・利用先を後継へ引き継ぎ、対応検証を受け入れた後。 |
| `backend/climate/contracts.py` | active：保存風統計の資料ID・native面・矩形・UTC半月query、元UTC時刻subsetと任意native風配点を正規化し、省略互換と非対応条件の明示拒否を保つ。。保存風統計の資料ID・native面・矩形範囲・UTC半月だけを有限入力として受け、非対応操作を明示拒否する。 | backend/climate/source.py、backend/climate/statistics.py、backend/climate/service.py | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/climate/extensions.py` | active：提供時刻別平均と固定一点の経験風配の型/単位/件数/支持を検査し、正当な期間合算と未対応理由を返す。。既存集計を期間/時刻の比較へつなぐ0.56の現役実体。 | backend/climate/source.py | 固有の責務/根拠を後継へ引き継ぎ、利用先と対応検証を受け入れた後。 |
| `backend/climate/periods.py` | active：UTC半月の支持を月/季節へ対応付け、構成bin・日数・選択時刻数を原年や連続冬へ捏造せず返す。。既存集計を期間/時刻の比較へつなぐ0.56の現役実体。 | backend/climate/aggregation.py、backend/climate/extensions.py、backend/climate/source.py | 固有の責務/根拠を後継へ引き継ぎ、利用先と対応検証を受け入れた後。 |
| `backend/climate/samples.py` | active：元風manifestの年・UTC・native格子/面・重みと月配列の同一性を検査し、格子×実時刻の加重経験分位を求める。。原標本の取得・固定支持・統計図・保存をつなぐ0.57の実体。機能検証と科学的受入は分ける。 | backend/climate/source.py、backend/climate/archive.py、tools/prepare_climate_demo.py | 固有の責務・来歴・利用先を後継へ引き継ぎ、対応検証を受け入れた後。 |
| `backend/climate/service.py` | active：起動時に登録した複数資料をIDで選び、数値依存を含む同一性で固定analysisと要求IDを保存する。固定GETを現資料から独立させる。。原DBの集約から独立したSQLiteへ要求・querycache・固定analysisを保存し、元DB不在でも固定読出しを提供する。飛行work lockとは分ける。 | backend/application.py、backend/app.py、backend/tests/test_climate_service.py | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/climate/source.py` | active：提供JRA-3Q DBと任意の同支持原標本を束縛し、旧期間平均・固定一点風配と取得済み月の原標本分位を区別して供給する。。提供JRA-3Q DBを読取り専用で検査し、全native面の年間集計と指定面の地域集計を指紋・支持件数・規模制限付きで供給する。 | backend/climate/service.py、backend/tests/test_climate.py | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/climate/statistics.py` | active：保存された風成分/速さから定常度・来向・格子重み集約を定義し、UTC半月の期待時刻数と未定義値を分ける。。保存された風成分/速さから定常度・来向・格子重み集約を定義し、UTC半月の期待時刻数と未定義値を分ける。 | backend/climate/source.py、backend/tests/test_climate.py、docs/THEORY_GUIDE.tex | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/contracts.py` | active：直接実行と草案保存のHTTP外枠を定義し、未完成sampling草案と一飛行/集合caseの固定表示参照を区別する。。保存可能な編集中の入力と、ensemble側の厳密な計画受付を分ける。既存n=1参照も維持する。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `backend/ensemble/__init__.py` | active：単一飛行workerを利用する永続集合のアプリケーション枝を識別する。。単一飛行workerを利用する永続集合のアプリケーション枝を識別する。 | backend/ensemble/service.py | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/ensemble/contracts.py` | active：未完成の候補草案と分けて、標本計画・明示開始・取消・再開・固定選択分析の有限HTTP入力を定義する。。未完成の候補草案と分けて、標本計画・明示開始・取消・再開・固定選択分析の有限HTTP入力を定義する。 | backend/app.py、backend/ensemble/service.py、frontend/src/ensembleApi.ts | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/ensemble/historical_planning.py` | active：共通機体と明示原日時窓を固定し、支持外・未登録の窓も欠損試行として残す。季節を代表する抽選は行わない。。共通機体と明示原日時窓を固定し、支持外・未登録の窓も欠損試行として残す。季節を代表する抽選は行わない。 | backend/ensemble/service.py | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `backend/ensemble/planning.py` | active：元量の共通実現値と全候補の解決済み入力を固定し、延期の同条件性・時間支持・配備上限と入力不成立を計画へ残す。。元量の共通実現値と全候補の解決済み入力を固定し、延期の同条件性・時間支持・配備上限と入力不成立を計画へ残す。 | backend/app.py、backend/ensemble/service.py | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/ensemble/service.py` | active：親ApplicationServiceのDB・lock・既存一飛行queueを使い、全試行/attempt・取消/再開・固定snapshot・選択分析と完成結果回収を管理する。別worker poolは作らない。。親ApplicationServiceのDB・lock・既存一飛行queueを使い、全試行/attempt・取消/再開・固定snapshot・選択分析と完成結果回収を管理する。別worker poolは作らない。 | backend/application.py、backend/tests/test_ensemble.py | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/ensemble/storage.py` | active：集合の計画/全試行/attempt/snapshot/操作/分析の台帳と、COMMITTED境界を持つ不変JSON文書の公開・読戻しを担う。。集合の計画/全試行/attempt/snapshot/操作/分析の台帳と、COMMITTED境界を持つ不変JSON文書の公開・読戻しを担う。 | backend/ensemble/service.py | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/ensemble/views.py` | active：全予定試行の状態別母数と元量・固定結果参照・有効終点をコンパクトな台帳表示へ写し、位置や原履歴の欠測を区別する。。全予定試行の状態別母数と元量・固定結果参照・有効終点をコンパクトな台帳表示へ写し、位置や原履歴の欠測を区別する。 | backend/ensemble/service.py | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/errors.py` | active：HTTPに依存しないserviceエラー型を定義し、applicationとweatherの循環依存を避ける。。HTTPに依存しないserviceエラー型を定義し、applicationとweatherの循環依存を避ける。 | backend/application.py、backend/weather/service.py | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/historical_catalog.py` | active：サービス起動時の明示ローカルカタログから、期待SHAと元UTCのJRA場を照合して登録する。HTTPで任意pathを受け付けない。。サービス起動時の明示ローカルカタログから、期待SHAと元UTCのJRA場を照合して登録する。HTTPで任意pathを受け付けない。 | backend/application.py、backend/tests/test_historical_ensemble.py | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `backend/pyproject.toml` | active：ローカルサービスのPython版と直接依存・試験依存を宣言する。。ローカルサービスのPython版と直接依存・試験依存を宣言する。。現役の画面・APIと既存核の接続を担当し、n=1の受入を分散/科学的精度へ広げない。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `backend/requirements.lock` | active：実行と試験に用いるPython依存集合の解決済み版を固定する。。実行と試験に用いるPython依存集合の解決済み版を固定する。。現役の画面・APIと既存核の接続を担当し、n=1の受入を分散/科学的精度へ広げない。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `backend/storage.py` | active：レジストリと固定出力の完成境界を管理し保存結果の整合を検査する。。既存レジストリと一飛行結果のCOMMITTED公開・照合を担い、rename後DB更新失敗の完成結果を固定spec/manifestから回収する。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `backend/tests/test_application.py` | active：保存GFS/JRAによる実計算・保存再閲覧・支持停止・受付拒否と固定結果由来の境界を有限反例で検証する。。保存GFSによる実計算・保存再閲覧・停止・受付と失敗境界を検証する。。現役の画面・APIと既存核の接続を担当し、n=1の受入を分散/科学的精度へ広げない。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `backend/tests/test_climate.py` | active：有限の人工DuckDBと独立した期待値でUTC母数・重み/定常度・欠測拒否・元資料指紋と支持検査を確かめる。。有限の人工DuckDBと独立した期待値でUTC母数・重み/定常度・欠測拒否・元資料指紋と支持検査を確かめる。 | backend/tests/test_climate_service.py、backend/tests/test_climate_api.py | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/tests/test_climate_api.py` | active：実HTTP handlerの固定集計・計画参照保存・原DB不在再読と、集約中の固定GET/計画読出しの独立性を有限反例で確かめる。。実HTTP handlerの固定集計・計画参照保存・原DB不在再読と、集約中の固定GET/計画読出しの独立性を有限反例で確かめる。 | backend/README.md | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/tests/test_climate_archive.py` | active：独立sourceの母集団・面積重み・静穏分母・支持拒否・複数資料保存と旧固定読出しを検査する。。原標本の取得・固定支持・統計図・保存をつなぐ0.57の実体。機能検証と科学的受入は分ける。 | role:独立気象資料回帰 | 固有の責務・来歴・利用先を後継へ引き継ぎ、対応検証を受け入れた後。 |
| `backend/tests/test_climate_archive_interaction.py` | active：原UTC標本の年間専用48区分の暦・重み・件数と、気圧面変更時の集計再利用、返却値の変異・母集団混同・途中失敗・原資料変更の有限反例を検査する。。0.58の原UTC年間区分と気圧面探索を支える有限回帰。実データ照合・実画面受入は別票へ戻る。 | role:backend原標本年間区分・面探索回帰 | 固有の責務・来歴・利用先を後継へ引き継ぎ、対応検証と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/tests/test_climate_periods.py` | active：不均等暦/時刻subset/一点経験度数/未対応支持/旧保存の有限反例を独立期待値と指定実DBで検査する。。既存集計を期間/時刻の比較へつなぐ0.56の現役実体。 | role:backend気象統計回帰 | 固有の責務/根拠を後継へ引き継ぎ、利用先と対応検証を受け入れた後。 |
| `backend/tests/test_climate_samples.py` | active：原標本の加重分位・暦支持・改変検出と旧DB併用を有限反例で検査する。。原標本の取得・固定支持・統計図・保存をつなぐ0.57の実体。機能検証と科学的受入は分ける。 | role:原標本統計回帰 | 固有の責務・来歴・利用先を後継へ引き継ぎ、対応検証を受け入れた後。 |
| `backend/tests/test_climate_service.py` | active：固定集計の要求同一性・再利用・改変検出・原DB不在読出し・並行処理/transactionの境界を人工DBで検証する。。固定集計の要求同一性・再利用・改変検出・原DB不在読出し・並行処理/transactionの境界を人工DBで検証する。 | backend/README.md | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/tests/test_ensemble.py` | active：共通実現値・全試行母数・既存queue・取消/再開・完成結果回収・旧snapshot・選択分析・履歴予算と場消失の反例を無通信で検査する。。共通実現値・全試行母数・既存queue・取消/再開・完成結果回収・旧snapshot・選択分析・履歴予算と場消失の反例を無通信で検査する。 | docs/COMMANDS.md、docs/BUILD.md | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/tests/test_historical_ensemble.py` | active：原日時窓の共通飛行核への接続、欠損行の保持、支持外・重複日時・破損カタログの拒否を検査する。。原日時窓の共通飛行核への接続、欠損行の保持、支持外・重複日時・破損カタログの拒否を検査する。 | backend/tests/test_recovery550.py | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `backend/tests/test_recovery550.py` | active：完成出力の回復、処理系故障、request ID照会、state UUIDと別保存先ガードを有限故障注入で検査する。。完成出力の回復、処理系故障、request ID照会、state UUIDと別保存先ガードを有限故障注入で検査する。 | docs/IMPLEMENTATION_INDEX.json | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `backend/tests/test_weather.py` | active：気象取得のjob・再利用・取消・再開・完了登録と既存飛行接続を注入した無通信条件で確認する。。offlineの有限な契約試験。実HTTP/実UIと科学的受入を代替しない。 | docs/PROGRAM_GUIDE.tex、role:取得から適用・再計算までを維持する開発担当 | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/tests/test_weather_ground.py` | active：地表APIが既存場と同じ値/識別を返し、支持外・内容変更・後着変更を拒否し入力を変えないことを検査する。。地表APIが既存場と同じ値/識別を返し、支持外・内容変更・後着変更を拒否し入力を変えないことを検査する。 | docs/IMPLEMENTATION_INDEX.json、role:地表API検査 | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `backend/tests/test_weather_inventory_partial.py` | active：run/day別一覧失敗の隔離と取消・保存/整合性失敗の伝播を、無通信の注入条件で検査する。。run/day別一覧失敗の隔離と取消・保存/整合性失敗の伝播を、無通信の注入条件で検査する。 | docs/IMPLEMENTATION_INDEX.json、role:部分一覧検査 | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `backend/tests/test_weather_raw_reuse.py` | active：登録済み完成assetだけをraw候補とし、窓拡張・破損・未登録・異条件と旧資産不変を無通信条件で検査する。。登録済み完成assetだけをraw候補とし、窓拡張・破損・未登録・異条件と旧資産不変を無通信条件で検査する。 | docs/PROGRAM_GUIDE.tex、docs/IMPLEMENTATION_NOTES.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `backend/tests/test_weather_region.py` | active：放球点と延期窓の包含、120/384時間端、固定planの再確認を検査し、領域を無言で動かさない。。放球点と延期窓の包含、120/384時間端、固定planの再確認を検査し、領域を無言で動かさない。 | docs/IMPLEMENTATION_INDEX.json | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `backend/weather/__init__.py` | active：気象取得のアプリケーション枝のパッケージ入口。数値気象場の実装はballoon_simに置く。。気象取得のアプリケーション枝のパッケージ入口。数値気象場の実装はballoon_simに置く。 | docs/PROGRAM_GUIDE.tex、role:取得から適用・再計算までを維持する開発担当 | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/weather/catalog.py` | active：固定NOMADS一覧からrun/leadを有限観測し、独立day/runの失敗を正常観測と分けて記録する。。固定NOMADS一覧からrun/leadを有限観測し、独立day/runの失敗を正常観測と分けて記録する。 | backend/tests/test_weather.py、backend/weather/service.py | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/weather/contracts.py` | active：配布確認・中心矩形・候補時間窓・取得開始をPydanticの有限HTTP入力として定義する。。配布確認・中心矩形・候補時間窓・取得開始をPydanticの有限HTTP入力として定義する。 | backend/app.py、backend/weather/service.py、frontend/src/WeatherPreparation.tsx、frontend/src/api.ts、frontend/src/weatherAcquisition.ts | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/weather/planning.py` | active：候補時間窓と中心矩形をGFS取得仕様へ変換し、配布不足・依存・メモリ予算を判定する。。候補時間窓と中心矩形をGFS取得仕様へ変換し、配布不足・依存・メモリ予算を判定する。 | backend/weather/service.py | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/weather/service.py` | active：固定計画/取得jobの永続化・単一取得thread・完成asset公開。登録済み完成assetの同一要求raw候補をgfsへ供給し、旧資産を変更しない。。固定計画/取得jobの永続化・単一取得thread・完成asset公開。登録済み完成assetの同一要求raw候補をgfsへ供給し、旧資産を変更しない。 | backend/application.py、backend/tests/test_weather.py | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `backend/worker.py` | active：固定入力と保存場を検証して既存核の一飛行計算と出力を別processで実行する。。固定入力と保存場を検証して同じ核の一飛行計算と出力を別processで実行する。実際に構築したweather.metadataを保存し、固定入力snapshotとの違いを隠さない。n=1の有限受入を分散/科学的精度へ広げない。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `balloon_sim/__init__.py` | active：軌道本体パッケージの識別と版。0.20の現役軌道本体候補。全国を目的とする入力契約を持ち、実データ二地点の成立と全日本/実飛行精度の受入は分ける。 | balloon_sim/__main__.py | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `balloon_sim/__main__.py` | active：python -m balloon_sim をCLIへ接続する入口。0.20の現役軌道本体候補。全国を目的とする入力契約を持ち、実データ二地点の成立と全日本/実飛行精度の受入は分ける。 | role:実行者 | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `balloon_sim/cli.py` | active：利用者操作と環境取得・単一飛行・成果保存を結ぶ入口。利用者操作と環境取得・単一飛行・成果保存を結ぶ入口 | balloon_sim/__main__.py、tests/test_flight_cli.py、role:実行者 | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `balloon_sim/dynamics.py` | active：旧dynamics公開APIの互換入口。設定/選択モデル/飛行制御へ委譲する。旧dynamics公開APIの互換入口。設定/選択モデル/飛行制御へ委譲する | balloon_sim/cli.py、tests/test_trajectory.py | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `balloon_sim/ensemble/__init__.py` | active：標本固定・元量解決・固定結果分析の純粋APIを公開する。取得・保存・job・画面の寿命は持たない。。標本固定・元量解決・固定結果分析の純粋APIを公開する。取得・保存・job・画面の寿命は持たない。 | tests/test_ensemble.py、docs/PROGRAM_GUIDE.tex | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `balloon_sim/ensemble/geography.py` | active：WGS84の有限領域表示用座標変換と描画可能域を定義する。軌道積分・試行母数・禁止領域所属とは分ける。。WGS84の有限領域表示用座標変換と描画可能域を定義する。軌道積分・試行母数・禁止領域所属とは分ける。 | balloon_sim/ensemble/landing.py、tests/test_ensemble.py | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `balloon_sim/ensemble/histories.py` | active：原記録を変えず、相別・共通経過時刻の平均/分位/有効数を計算する。相跨ぎ・終了後の外挿を行わない。。原記録を変えず、相別・共通経過時刻の平均/分位/有効数を計算する。相跨ぎ・終了後の外挿を行わない。 | balloon_sim/ensemble/statistics.py | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `balloon_sim/ensemble/landing.py` | active：有限標本の着地点から50/90/95%経験域と全点外周を求め、点/線への退化・同点・描画不能と着地母数を区別する。。有限標本の着地点から50/90/95%経験域と全点外周を求め、点/線への退化・同点・描画不能と着地母数を区別する。 | balloon_sim/ensemble/statistics.py | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `balloon_sim/ensemble/sampling.py` | active：理由付き一様仮分布の元量実現値を固定し、対応する有効モデルの物理入力一箇所へ解決する。不成立値を補正・再抽選しない。。理由付き一様仮分布の元量実現値を固定し、対応する有効モデルの物理入力一箇所へ解決する。不成立値を補正・再抽選しない。 | balloon_sim/ensemble/__init__.py、backend/ensemble/planning.py | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `balloon_sim/ensemble/statistics.py` | active：全台帳の固定ID選択を検証し、欠結果/空履歴を母数に残して着地点経験域と相別履歴分析を結合する純粋入口。。全台帳の固定ID選択を検証し、欠結果/空履歴を母数に残して着地点経験域と相別履歴分析を結合する純粋入口。 | balloon_sim/ensemble/__init__.py、backend/ensemble/service.py | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `balloon_sim/environment/__init__.py` | active：保存環境・場・製品アダプターの名前空間。D-162の修復で分離した実体。定義と公開経路はIMPLEMENTATION_INDEXへ接続する | role:本体開発と検証 | 責務と固有の挙動・試験を後継へ移し、使用先との互換を受け入れた後 |
| `balloon_sim/environment/bundle.py` | active：保存スキーマの成立と製品規則を結ぶ場の構成入口。D-162の修復で分離した実体。定義と公開経路はIMPLEMENTATION_INDEXへ接続する | role:本体開発と検証 | 責務と固有の挙動・試験を後継へ移し、使用先との互換を受け入れた後 |
| `balloon_sim/environment/fields.py` | active：無通信の圧力面列再構成・支持判定・時空間照会。D-162の修復で分離した実体。定義と公開経路はIMPLEMENTATION_INDEXへ接続する | role:本体開発と検証 | 責務と固有の挙動・試験を後継へ移し、使用先との互換を受け入れた後 |
| `balloon_sim/environment/gfs.py` | active：固定GFSの取得/原本再生・復号。登録管理から注入された一致raw候補を内容検算して独立コピーし、不足時刻だけ取得後に新全窓を復号する。backend DBを直接読まない。。固定GFSの取得/原本再生・復号。登録管理から注入された一致raw候補を内容検算して独立コピーし、不足時刻だけ取得後に新全窓を復号する。backend DBを直接読まない。 | role:本体開発と検証 | 責務と固有の挙動・試験を後継へ移し、使用先との互換を受け入れた後 |
| `balloon_sim/environment/gfs_contract.py` | active：GFS配信規則・製品固有の時刻軸の検証。D-162の修復で分離した実体。定義と公開経路はIMPLEMENTATION_INDEXへ接続する | role:本体開発と検証 | 責務と固有の挙動・試験を後継へ移し、使用先との互換を受け入れた後 |
| `balloon_sim/environment/jra3q.py` | active：保存JRAのUTC・既知半層係数・full圧力を検証し、strictモデル面と明示表層Bの別schemaをそれぞれの場へ束縛する。。Jra3qModelFieldの旧strict経路を保持し、Jra3qSurfaceFieldで別schema/product・固定reconstructionを検査する。任意過去取得UIや科学的精度受入とは分ける。 | balloon_sim/environment/storage.py、tools/prepare_jra3q_flight_fixture.py | 固有の入力・来歴・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `balloon_sim/environment/model_levels.py` | active：製品暦・I/Oから独立したモデル面列の検証、厳密な時空間/高さ支持と任意高度の要求量・モデル地形の照会。。JRAから渡る列を扱う現役照会実体。地表橋渡し・補外や欠測列の捨象を追加しない。 | balloon_sim/environment/jra3q.py、balloon_sim/environment/model_surface.py | 固有の入力・来歴・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `balloon_sim/environment/model_surface.py` | active：原UTCごとにnativeモデル面を水平合成し、明示した表層診断節点から固定joinへ接続して同絶対Hで照会する暫定B方式。。ModelSurfaceFieldがモデル地形・固定joinの幾何、要求値の局所欠測、仮想上端を検査する。旧strict場の意味は変えず、物理的精度優位や実地表の再現を保証しない。 | balloon_sim/environment/jra3q.py、tests/test_jra3q_surface_field.py | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `balloon_sim/environment/nomads.py` | active：NOMADSに限定した有界通信をCLIとserviceで共有し、利用者単位の通信間隔・取消・再試行しない境界を担う。。NOMADSに限定した有界通信をCLIとserviceで共有し、利用者単位の通信間隔・取消・再試行しない境界を担う。 | backend/tests/test_weather.py、backend/weather/service.py、balloon_sim/environment/gfs.py、tests/test_flight_weather.py、tests/test_gfs_acquisition.py | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `balloon_sim/environment/storage.py` | active：厳密JSON/gzip保存とschema別の場の読込境界。既存気圧面・strict JRAを維持し、明示表層JRAを製品adapterへ委譲する。。保存schemaを読み、気圧面・strict JRAモデル面・表層B JRAの各readerへ委譲する。気象取得や補間方針の自動選択は行わない。 | role:本体開発と検証 | 責務と固有の挙動・試験を後継へ移し、使用先との互換を受け入れた後 |
| `balloon_sim/flight/__init__.py` | active：単一飛行を構成する責務の名前空間。D-162の修復で分離した実体。定義と公開経路はIMPLEMENTATION_INDEXへ接続する | role:本体開発と検証 | 責務と固有の挙動・試験を後継へ移し、使用先との互換を受け入れた後 |
| `balloon_sim/flight/config.py` | active：入力設定と単位・既存構成の成立条件。D-162の修復で分離した実体。定義と公開経路はIMPLEMENTATION_INDEXへ接続する | role:本体開発と検証 | 責務と固有の挙動・試験を後継へ移し、使用先との互換を受け入れた後 |
| `balloon_sim/flight/events.py` | active：破裂条件とその診断・境界の意味。D-162の修復で分離した実体。定義と公開経路はIMPLEMENTATION_INDEXへ接続する | role:本体開発と検証 | 責務と固有の挙動・試験を後継へ移し、使用先との互換を受け入れた後 |
| `balloon_sim/flight/models.py` | active：選択済み鉛直モデル・必要量と独立した気体評価の構成。D-162の修復で分離した実体。定義と公開経路はIMPLEMENTATION_INDEXへ接続する | role:本体開発と検証 | 責務と固有の挙動・試験を後継へ移し、使用先との互換を受け入れた後 |
| `balloon_sim/flight/numerics.py` | active：物理と独立した積分・誤差と根探索の接続。D-162の修復で分離した実体。定義と公開経路はIMPLEMENTATION_INDEXへ接続する | role:本体開発と検証 | 責務と固有の挙動・試験を後継へ移し、使用先との互換を受け入れた後 |
| `balloon_sim/flight/trajectory.py` | active：保存場・選択済みモデル・イベントを接続する単一飛行制御。D-162の修復で分離した実体。定義と公開経路はIMPLEMENTATION_INDEXへ接続する | role:本体開発と検証 | 責務と固有の挙動・試験を後継へ移し、使用先との互換を受け入れた後 |
| `balloon_sim/results/__init__.py` | active：計算結果の保存・表示の名前空間。D-162の修復で分離した実体。定義と公開経路はIMPLEMENTATION_INDEXへ接続する | role:本体開発と検証 | 責務と固有の挙動・試験を後継へ移し、使用先との互換を受け入れた後 |
| `balloon_sim/results/export.py` | active：結果各形式と再帰コード来歴の保存。D-162の修復で分離した実体。定義と公開経路はIMPLEMENTATION_INDEXへ接続する | role:本体開発と検証 | 責務と固有の挙動・試験を後継へ移し、使用先との互換を受け入れた後 |
| `balloon_sim/results/report.py` | active：結果からHTML・SVGを生成する表示。D-162の修復で分離した実体。定義と公開経路はIMPLEMENTATION_INDEXへ接続する | role:本体開発と検証 | 責務と固有の挙動・試験を後継へ移し、使用先との互換を受け入れた後 |
| `balloon_sim/weather.py` | active：旧weather公開APIの互換入口。製品/場/保存の実体へ委譲する。旧weather公開APIの互換入口。製品/場/保存の実体へ委譲する | balloon_sim/dynamics.py、balloon_sim/cli.py、tests/test_flight_weather.py | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `docs/BACKLOG.csv` | active：タスク・前提・受入条件。長期計画を具体作業へ結びつける | PROJECT_CONTEXT.md | タスクIDと依存・証拠の移行を検査した後 |
| `docs/BUILD.md` | active：生成・検査・依存の実務説明。実行条件と未受入を混同させない | role:作業者 | 新しいビルド経路と既存説明を照合して移行後 |
| `docs/COMMANDS.md` | active：取得・再生・計算・検査・資料生成の入力/副作用/出力/失敗と再開を示すコマンド一覧。CLIと実画面C09について、入力・保存副作用・固定計画/実行・結果選択・失敗/取消/再開の利用者操作を案内する。 | role:実行者 | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `docs/CONTENT_HEALTH.json` | active：範囲・時点・確認証拠。指紋と期限の編集元。用途寿命は別契約 | tools/check_health.py | 後継に未確認/期限/証拠を引き継ぎ検査受入後 |
| `docs/CONTINUITY_CONTRACT.json` | active：必要性・寿命・論証設計・変更理由・共通入口契約。実体と内容の存続理由、共通開始文とコピー分類・互換性・外部観測を編集する | tools/check_contract.py | 同じ責務の後継と比較理由を受け入れた後 |
| `docs/DECISIONS.md` | active：現在に効く採否と理由。却下理由と再検討条件を残す | PROJECT_CONTEXT.md | 現在へ効く理由をすべて後継へ受入後 |
| `docs/DOCUMENT_CONTROL.md` | active：全作業の判断原則と改訂・論証・点検の契約。意図から設計・実施・自己評価へ戻る原則の単一正本と、その運用を支える管理契約を説明する | README.md | 規則と理由を移行し誤操作防止を受入後 |
| `docs/ENVIRONMENT_CONTRACT.md` | active：固定標本の数値契約と、モデル拡張・経路別実取得/能力/来歴・地形の入力境界。固定GFS/JRA標本のgpm契約と0.20の幾何高度・全飛行runtimeを区別する実装仕様。気象の運用根拠はWEATHER_DATA_GUIDE、数式導出はTHEORY_GUIDE、API構造はPROGRAM_GUIDEへ接続する。 | tools/normalize_gfs_fixture.py、tests/test_environment.py、docs/PROJECT_PLAN.md | 一般環境adapter受入時にAPI・単位/品質/必要能力・取得来歴・回帰へ接続。外側の小取得証拠は必要性を判断し保持/移管する。 |
| `docs/IMPLEMENTATION_INDEX.json` | active：本体の主要API署名・理論/構造・試験・導入/点検時点を結ぶ索引。公開APIの実署名/試験対応に加え、実ファイル/関数木/静的依存と手動で確認した実行時契約を区別して索引化する。 | docs/PROGRAM_GUIDE.tex、role:変更担当 | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `docs/IMPLEMENTATION_NOTES.md` | active：構造図から分離した処理・入出力・失敗・拡張の詳細。旧構造ガイドの固有情報を保持。構造図から分離した処理・入出力・失敗・拡張の詳細。旧構造ガイドの固有情報を保持。0.21/RPT038で受入。科学的結論の一括採用とは区別する。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装担当 | 後継へ固有情報・原本同定・再現と未検証を移し、担当Codexが保持/移管理由と次判定を記録してから判断する。無断削除しない。 |
| `docs/INTEGRATION_DESIGN.html` | active：既存の場・一飛行・分散契約を、入力経路・対照標本・ジョブ・保存・分析の寿命へ橋渡しする接続設計。一つの計画を長期選定から飛行後まで通し、入力切替・標本対応・完了順の偏り・固定結果と保存図・実行境界を具体例で比較する。研究課題への戻り先を持ち、科学式/実API/性能の採用済み仕様にしない。 | docs/PROJECT_PLAN.md、docs/SIMULATOR_VISION.html、role:UIと本体の接続担当 | 固有の原本・設計理由・再現証拠・未確認境界を後継へ保持/移管し、主担当が理由と次判定を記録した後。無断削除しない。 |
| `docs/LESSONS.md` | active：失敗と対策の理由。古い失敗を現在の制約と回帰へ結ぶ | role:作業者 | 制約が不要と根拠付きで判断するか後継へ移した後 |
| `docs/PROGRAM_GUIDE.pdf` | generated：構造ガイドの人向け表示。編集元TeXとの対を保持。0.20のTeX編集元から作る派生表示。独立編集せず同じ版の生成・表示証拠と対応させる。科学的精度の採用とは分ける。 | role:読者 | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `docs/PROGRAM_GUIDE.tex` | active：本体の責務・依存・主要API・失敗経路・拡張時の影響を説明する構造ガイド編集元。実在実装の全体→ファイル→class/function/helperの階層と横の依存を図から追う構造ガイド。式と処理詳細は別資料へ接続する。 | docs/PROGRAM_GUIDE.pdf、docs/COMMANDS.md、role:実装担当 | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `docs/PROGRAM_GUIDE.txt` | generated：構造PDFから抽出した検索・取得用派生テキスト。0.20のTeX編集元から作る派生表示。独立編集せず同じ版の生成・表示証拠と対応させる。科学的精度の採用とは分ける。 | role:資料取得担当 | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `docs/PROJECT_PLAN.md` | active：中長期の構想・設計理由。中長期の構想と実装順。完成像の編集元VISIONと役割を分け、提案・現行実装・科学採用を区別する | PROJECT_CONTEXT.md | 方向・要求と必要理由を後継へ保持して承認後 |
| `docs/PROJECT_PLAN.pdf` | generated：計画の人向け表示。編集可能なソースとの対を保持 | role:読者 | 読者向け後継とソースを受入れた後 |
| `docs/PROJECT_PLAN.tex` | generated：計画PDFの生成中間ソース。MDを編集元とする派生物。単独編集しない | docs/PROJECT_PLAN.pdf | 代替生成経路を受入れPDFとの対を維持した後 |
| `docs/SIMULATOR_VISION.html` | active：完成した分析ツールの利用体験から設計を議論する。三用途と旧模型/反証/採否を保持し、現在は入力・MC・保存・実行を結ぶ総合設計とChat研究へ案内する。模型の局所成功を本体/科学の完成へ広げず、今回実績はS35へ戻す。 | PROJECT_CONTEXT.md、docs/PROJECT_PLAN.md、BOOTSTRAP_RUNBOOK.html | 完成像と未確定の議論を後継設計へ理由付きで移管した後 |
| `docs/THEORY_GUIDE.pdf` | generated：理論ガイドの人向け表示。編集元TeXとの対を保持。0.20のTeX編集元から作る派生表示。独立編集せず同じ版の生成・表示証拠と対応させる。科学的精度の採用とは分ける。 | role:読者 | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `docs/THEORY_GUIDE.tex` | active：本体の座標・気象再構成・鉛直式・移流・イベントと、一元量仮感度・経験被覆・相別履歴統計を導出/定義と限界で結ぶ理論ガイド編集元。。物理式と集計の定義・母数・描画限界を区別し、生成したPDF/textと一組で保持する。校正済み予報確率を主張しない。 | docs/THEORY_GUIDE.pdf、docs/PROGRAM_GUIDE.tex、role:科学レビュー担当 | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `docs/THEORY_GUIDE.txt` | generated：理論PDFから抽出した検索・取得用派生テキスト。0.20のTeX編集元から作る派生表示。独立編集せず同じ版の生成・表示証拠と対応させる。科学的精度の採用とは分ける。 | role:資料取得担当 | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `docs/UNCERTAINTIES.csv` | active：未確認・未決・影響・判定ゲート。解消済みと未検証を区別 | PROJECT_CONTEXT.md | 未確定と理由を後継へ移行した後 |
| `docs/VERSION_HISTORY.json` | active：版とGitの時間軸。現在を説明する観測済み遷移 | README.md | 採否とGit遷移の同定機能を後継へ移行後 |
| `docs/WEATHER_DATA_GUIDE.md` | active：提供元別の気象API/時刻/層/高さ/取得経路の仕様と実測を、任意時刻の場の成立条件へ結ぶ専用ガイド。運用知識の編集元。ENVの実装契約、PLANの長期構想、HTMLの行動/判断と責務を分ける。 | docs/ENVIRONMENT_CONTRACT.md、docs/PROJECT_PLAN.md、BOOTSTRAP_RUNBOOK.html、role:取得器と環境adapterの実装者 | 同じ運用知識・一次根拠・実測/未確認・再実行入口を後継へ移し、既存リンクと契約を検査受入した後 |
| `docs/WORK_ORDER_TEMPLATE.md` | active：範囲・基準・受入の発行様式。未発行のテンプレート。現在作業を命令しない | role:依頼作成者 | 後継の依頼契約を受入後 |
| `docs/research/BRIEF.md` | active：研究担当が全体の用途・ニーズ・境界と設計仮説をつなぎ、問いを独立に組み直す文脈。研究の共通知識として要求の重要度と設計上の仮説を区別する。仕様の第二の正本や現案への追認依頼にしない。 | docs/research/README.md、docs/research/TASKS.md、role:独立した研究担当 | 固有の目的・根拠・版・採否と再生成/再読経路を後継に保持した後。履歴を無断削除しない。 |
| `docs/research/README.md` | active：全体文脈と操作の書面説明から初回研究へ入り、回答を設計へ戻す入口。局所課題の順番を作業目的に置き換えず、独立した視点を設計へ取り込む。実Chatへの発行・回答や科学採用とは区別する。 | CONTENT_MAP.md、role:Codexの設計担当とChat研究担当 | 固有の依頼・出典・版・採否と再生成手段を後継へ保持した後。原本は派生物だけで代替せず、無断削除しない。 |
| `docs/research/RESPONSE_TEMPLATE.md` | active：研究回答の基準・根拠・反例・限界・変更先を保存可能な形で受け取る。欄の充足や反例の形式的通過を、独立した研究の成立と混同しない。実Chatへの発行・回答や科学採用とは区別する。 | docs/research/README.md、role:Codexの設計担当とChat研究担当 | 固有の依頼・出典・版・採否と再生成手段を後継へ保持した後。原本は派生物だけで代替せず、無断削除しない。 |
| `docs/research/REVIEW_042.md` | active：旧依頼の初読失敗、改訂、再批評と限定受入の根拠をrepo内に保持する。検証記録。内容批評で何が変わったかを記録する。新しい設計正本、実Chatの成功証拠、定量性能評価にはしない。 | REFERENCE_LOG.md、docs/research/README.md、role:研究依頼の採否を再検討する担当 | 固有の目的・根拠・版・採否と再生成/再読経路を後継に保持した後。履歴を無断削除しない。 |
| `docs/research/TASKS.md` | active：全体設計研究Q420-00と旧5重点課題を結び、問いの組替えと具体的判断を依頼する。既存課題分割を保守するための研究へ閉じず、全体の進行に効く判断を得る。実Chatへの発行・回答や科学採用とは区別する。 | docs/research/README.md、role:Codexの設計担当とChat研究担当 | 固有の依頼・出典・版・採否と再生成手段を後継へ保持した後。原本は派生物だけで代替せず、無断削除しない。 |
| `docs/research/UI_WALKTHROUGH.md` | active：UIを操作できない研究担当が、画面間の関係と利用者の比較・掘下げ操作を読む。操作模型の書面説明。現在の操作、仮のUI案、未実装の計算能力を分け、画面分割を固定要件にしない。 | docs/research/README.md、docs/research/BRIEF.md、role:画面を操作できない研究担当 | 固有の目的・根拠・版・採否と再生成/再読経路を後継に保持した後。履歴を無断削除しない。 |
| `docs/research/packet_sources.json` | active：共通文脈と課題別の抽出範囲を指定し、6資料束を再生成する。RPT-067/D-180の研究委譲を現在の設計へ結ぶ。未発行/未受領を成功へ変えない。 | docs/research/README.md、role:Codexの設計担当とChat研究担当 | 固有の依頼・出典・版・採否と再生成手段を後継へ保持した後。原本は派生物だけで代替せず、無断削除しない。 |
| `docs/research/packets/Q410-01.md` | generated：Q410-01の依頼と必要本文をChatへ渡す派生資料束。編集元ではない。源範囲・生成器へ戻り、再生成の同一性を確認して配布する。実Chat回答や科学採用の成功証拠ではない。 | docs/research/README.md、role:Codexの設計担当とChat研究担当 | 固有の依頼・出典・版・採否と再生成手段を後継へ保持した後。原本は派生物だけで代替せず、無断削除しない。 |
| `docs/research/packets/Q410-02.md` | generated：Q410-02の依頼と必要本文をChatへ渡す派生資料束。編集元ではない。源範囲・生成器へ戻り、再生成の同一性を確認して配布する。実Chat回答や科学採用の成功証拠ではない。 | docs/research/README.md、role:Codexの設計担当とChat研究担当 | 固有の依頼・出典・版・採否と再生成手段を後継へ保持した後。原本は派生物だけで代替せず、無断削除しない。 |
| `docs/research/packets/Q410-03.md` | generated：Q410-03の依頼と必要本文をChatへ渡す派生資料束。編集元ではない。源範囲・生成器へ戻り、再生成の同一性を確認して配布する。実Chat回答や科学採用の成功証拠ではない。 | docs/research/README.md、role:Codexの設計担当とChat研究担当 | 固有の依頼・出典・版・採否と再生成手段を後継へ保持した後。原本は派生物だけで代替せず、無断削除しない。 |
| `docs/research/packets/Q410-04.md` | generated：Q410-04の依頼と必要本文をChatへ渡す派生資料束。編集元ではない。源範囲・生成器へ戻り、再生成の同一性を確認して配布する。実Chat回答や科学採用の成功証拠ではない。 | docs/research/README.md、role:Codexの設計担当とChat研究担当 | 固有の依頼・出典・版・採否と再生成手段を後継へ保持した後。原本は派生物だけで代替せず、無断削除しない。 |
| `docs/research/packets/Q410-05.md` | generated：Q410-05の依頼と必要本文をChatへ渡す派生資料束。編集元ではない。源範囲・生成器へ戻り、再生成の同一性を確認して配布する。実Chat回答や科学採用の成功証拠ではない。 | docs/research/README.md、role:Codexの設計担当とChat研究担当 | 固有の依頼・出典・版・採否と再生成手段を後継へ保持した後。原本は派生物だけで代替せず、無断削除しない。 |
| `docs/research/packets/Q420-00.md` | generated：Q420-00の全体理解と独立設計研究に必要な本文と来歴を渡す生成資料束。編集元ではない。源範囲と生成器へ戻って再生成し、配布直前にfreshnessを確認する。研究回答や科学採用は含まない。 | docs/research/README.md、role:Chat研究担当 | 固有の目的・根拠・版・採否と再生成/再読経路を後継に保持した後。履歴を無断削除しない。 |
| `docs/research/packets/manifest.json` | generated：6資料束と元範囲・内容を同一性照合するmanifest。編集元ではない。源範囲・生成器へ戻り、再生成の同一性を確認して配布する。実Chat回答や科学採用の成功証拠ではない。 | docs/research/README.md、role:Codexの設計担当とChat研究担当 | 固有の依頼・出典・版・採否と再生成手段を後継へ保持した後。原本は派生物だけで代替せず、無断削除しない。 |
| `examples/gfs-japan-request.json` | reference：単一GFS run・UTC窓・領域・取得量上限を明示する取得例。0.20の現役本体開発を支える資料・入力例・生成/検査実体。使用範囲と未検証を各担当本文へ戻す。 | docs/COMMANDS.md | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `examples/hokkaido-simple.json` | reference：北海道の簡易モデル受入例の明示入力。全国のデフォルトや実打上げ計画ではない。0.20の現役本体開発を支える資料・入力例・生成/検査実体。使用範囲と未検証を各担当本文へ戻す。 | docs/COMMANDS.md、tests/test_flight_cli.py | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `examples/jra3q-ground-flight.json` | reference：保存JRAの地上から30km破裂・降下・モデル地形への着地をCLIで読む固定再現条件。実打上げの推奨既定値ではない。。C-11と保存JRAのGUI候補作成で使う明示入力。UTC・場・機体条件を固定して単一飛行を比較し、任意過去場の取得UIや季節MCへ広げない。 | docs/COMMANDS.md、role:再現担当、backend/application.py | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `examples/jra3q-support-flight.json` | reference：固定JRA原本の支持内で上昇・破裂・降下を行い、地表接続前の支持不足停止を読む診断入力。実打上げ条件の既定値ではない。。CLI診断飛行の明示条件。空中開始・着地なしを隠さず、終了2と最後の有効点を読む。 | docs/COMMANDS.md | 固有の入力・来歴・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `examples/wakayama-isothermal.json` | reference：和歌山の内外等温浮力・抗力モデル受入例の明示入力。0.20の現役本体開発を支える資料・入力例・生成/検査実体。使用範囲と未検証を各担当本文へ戻す。 | docs/COMMANDS.md、tests/test_flight_cli.py | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `frontend/SCREEN_PROVENANCE.md` | active：原0.40.1 r2の具体画面と現役frontendの対応・所有境界・保持する旧実体を案内する。原GUIと現役source・旧部品保持を結び、0.47/0.48の実取得/集合追加接点と人工モードの区別を案内する。受入実績はS35/S36へ分ける。 | docs/PROGRAM_GUIDE.tex、CONTENT_MAP.md、role:原GUIと現役sourceの対応を確認する担当 | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/index.html` | active：日本語比較画面のHTML入口とReact起動先を指定する。。日本語比較画面のHTML入口とReact起動先を指定する。。現役の画面・APIと既存核の接続を担当し、n=1の受入を分散/科学的精度へ広げない。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `frontend/package-lock.json` | active：画面の開発・構築・試験に用いるnpm依存集合を固定する。。画面の開発・構築・試験に用いるnpm依存集合を固定する。。現役の画面・APIと既存核の接続を担当し、n=1の受入を分散/科学的精度へ広げない。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `frontend/package.json` | active：画面のNode要件・React/Leaflet/Plotly/Cesiumの依存と起動・構築・試験コマンドを宣言する。共通frontendと独立scene3d rendererに必要な依存を同じprojectで解決する。具体的解決版はpackage-lockへ戻る。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `frontend/scene3d/THIRD_PARTY_NOTICES.txt` | generated：固定npm依存のライセンス全文とCesiumの第三者告知を3D配信の参照先にまとめる。現配布のライセンス告知。依存解決版を変えたら元パッケージと照合して再生成する。ライセンス適合の法的審査を示す資料ではない。 | frontend/scene3d/index.html | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/data/README.md` | active：EGM96の表示規約・固定データの取得元/帰属・補間の境界と有限検証を説明する。。0.55追補の3D表示とその有限検査に使用。ASLの元結果・KML出力と描画時の高度変換を分ける。 | frontend/scene3d/src/vertical-datum.js、role:3D表示の開発者 | 担当する表示/入力/取消の契約と固有の来歴を後継へ移し、利用先と対応検査を受け入れた後。 |
| `frontend/scene3d/data/WW15MGH.DAC` | active：描画時のASLから楕円体高への換算に使うEGM96全球15分ジオイド高格子。。固定同梱の表示入力。飛行核・気象入力・DEM・衝突判定の根拠へ転用しない。 | frontend/scene3d/src/route-layer.js、frontend/src/scene3d-datum.test.ts | 高度表示規約・固定取得元・帰属・既存結果との対応を後継へ引き継ぎ、描画と検査を受け入れた後。 |
| `frontend/scene3d/fixtures/surface.glb` | active：外部写真接続なしで地表面への投影・名称読取りを調べる人工meshを保持する。人工データによる表示確認の入力。実気象・実フライトや科学的受入の根拠にしない。 | frontend/scene3d/fixtures/tileset.json | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/fixtures/tileset.json` | active：人工surface.glbを3D Tilesの位置・変換・境界付き入力として記述する。人工データによる表示確認の入力。実気象・実フライトや科学的受入の根拠にしない。 | frontend/scene3d/src/main.js | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/index.html` | active：写真3Dの地図・候補一覧・キー入力・表示/視点操作とrenderer起動を構成する。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screens/forecast/controller.js | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/src/band-readout.js` | active：3Dへ渡された経験輪郭の面内区分とクリック判定を持つ。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/scene3d/src/hover-labels.js、frontend/scene3d/src/main.js | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/src/camera-fit.js` | active：対象範囲を覆うカメラ距離と地域の中心を計算する。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/scene3d/src/main.js、frontend/scene3d/src/protocol.js | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/src/catalog.js` | active：対象候補・延期系列・分位帯の一覧と凡例を構成する。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/scene3d/src/main.js | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/src/colors.js` | active：受渡し色を正規化し3D描画へ供給する。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/scene3d/src/catalog.js、frontend/scene3d/src/main.js、frontend/scene3d/src/overlays.js | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/src/fixture.js` | active：単独の人工地表確認で使う輪郭・禁止領域・点と経路を供給する。人工データによる表示確認の入力。実気象・実フライトや科学的受入の根拠にしない。 | frontend/scene3d/src/main.js | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/src/hover-controller.js` | active：カーソル静止・再描画待機・失効を管理して面の名称読取りを進める。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/scene3d/src/main.js | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/src/hover-labels.js` | active：3D面・境界の重なりから名称と吹出し配置を決める。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/scene3d/src/hover-controller.js、frontend/scene3d/src/main.js、frontend/src/screen-contracts.test.ts | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/src/main.js` | active：独立rendererの接続・受渡し・描画・名称/クリック・視点・終了をまとめる。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/scene3d/index.html | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/src/overlay-store.js` | active：差し替える描画実体を保持し、更新や破棄をまとめる。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/scene3d/src/main.js | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/src/overlays.js` | active：受け取った点・輪郭・経路・領域をCesium entityへ変換する。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/scene3d/src/main.js | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/src/protocol.js` | active：受渡しsnapshotのschema・図形・座標・対象を検査し受領情報を作る。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/scene3d/src/main.js、frontend/src/screen-contracts.test.ts | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/src/provider.js` | active：入力欄から認証値を受け取り、明示接続と値を露出しない失敗表示へつなぐ。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/scene3d/src/main.js | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/src/receipt-status.js` | conditional：受渡しの拒否状態を、正常snapshot受領まで保持する旧補助を残す。旧素材として保持。現在のApp/rendererのmodule参照経路では呼出しを確認できないため、現役機能とは記述しない。 | role:旧GUI素材の対応と移行後の責務を点検する担当 | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/src/route-geometry.js` | active：元ASLを保って同じ上端節点の立体線と全経路幕を作り、表示下端・原節点fallback・人工AGL全体保留を区別する。。0.55追補の3D表示とその有限検査に使用。ASLの元結果・KML出力と描画時の高度変換を分ける。 | frontend/scene3d/src/route-layer.js、frontend/src/scene3d-geometry.test.ts | 担当する表示/入力/取消の契約と固有の来歴を後継へ移し、利用先と対応検査を受け入れた後。 |
| `frontend/scene3d/src/route-layer.js` | active：実ASLの立体線と連続幕の描画更新/取消/復帰を管理し、人工AGLだけを地物高取得へ依存させる。。0.55追補の3D表示とその有限検査に使用。ASLの元結果・KML出力と描画時の高度変換を分ける。 | frontend/scene3d/src/main.js、frontend/src/scene3d-geometry.test.ts | 担当する表示/入力/取消の契約と固有の来歴を後継へ移し、利用先と対応検査を受け入れた後。 |
| `frontend/scene3d/src/surface-pick.js` | active：地形へのpickと名称境界の識別を行う。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/scene3d/src/main.js | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/src/surface-session.js` | active：名称/クリック読取り前の描画待機を世代と中止条件付きで制御する。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/scene3d/src/main.js | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/src/vertical-datum.js` | active：固定EGM96格子を検査・補間し、表示座標用のジオイド高をメートルで返す。。0.55追補の3D表示とその有限検査に使用。ASLの元結果・KML出力と描画時の高度変換を分ける。 | frontend/scene3d/src/route-layer.js、frontend/src/scene3d-datum.test.ts | 担当する表示/入力/取消の契約と固有の来歴を後継へ移し、利用先と対応検査を受け入れた後。 |
| `frontend/scene3d/src/view-memory.js` | active：表示対象の集合に対応する利用者の視点を記憶・呼出しする。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/scene3d/src/main.js | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/src/view-stability.js` | active：受渡しや描画更新の前後で視点を保つため公開カメラ姿勢を扱う。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/scene3d/src/main.js | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/scene3d/style.css` | active：独立3D画面の地図・接続・一覧・名称吹出しの配置を定める。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/scene3d/index.html | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/App.tsx` | active：共通計画の候補・用途切替・保存を管理し、育てた予報/気象/季節画面へ接続する。現役の共通入口。0.45の二枚カードを後続UIの基準とせず、具体画面と実入力・固定run・保存の接点を同時に統合する。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `frontend/src/ClimateFlightHandoff.tsx` | active：固定した統計の関心期間・構成半月・気象有効時刻・地域・出典を原日時試算へ渡し、原放球時刻や瞬時場へ自動変換しない。。固定した気象統計から関心を持った半月・地域・出典を原日時の試算へ渡す。平均風を飛行場へ読み替えない。 | frontend/src/screens/WeatherScreen.tsx | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/ConfigEditor.tsx` | active：候補の物理入力・最大飛行時間を編集し、方式切替で非選択値をmodelDraftsへ退避する。。候補の物理入力・最大飛行時間を編集し、方式切替で非選択値をmodelDraftsへ退避する。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `frontend/src/GroundPreparation.tsx` | active：選択場・地点・時刻に束縛したモデル地表を照会し、現在ASLとの差と指定余裕の明示適用を入力へ返す。。選択場・地点・時刻に束縛したモデル地表を照会し、現在ASLとの差と指定余裕の明示適用を入力へ返す。 | frontend/src/ConfigEditor.tsx、docs/PROGRAM_GUIDE.tex | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/HistoricalEntry.tsx` | active：元UTCの登録場から比較候補を作る入口と、元の気象分析へ戻る文脈を提供する。診断用入力と科学的設定を区別する。。元UTCの登録場から比較候補を作る入口と、元の気象分析へ戻る文脈を提供する。診断用入力と科学的設定を区別する。 | frontend/src/App.tsx | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/HistoricalPreparation.tsx` | active：原日時窓と選択理由を編集・固定し、同じ要求の明示回復と既存集合監視へ接続する。。原日時窓と選択理由を編集・固定し、同じ要求の明示回復と既存集合監視へ接続する。 | frontend/src/screens/ForecastScreen.tsx | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/HistoryPanel.tsx` | conditional：固定結果の時系列と表示時刻を描画して実行情報付きの図を保存する。。0.45の簡略比較画面の部品として保持する。現在のApp/mainからの表示経路には含まれない。元の有限成果や既存処理との比較に使うが、現役画面の入口とは案内しない。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `frontend/src/MapPanel.tsx` | conditional：共有地図へ固定軌道・場の支持範囲と着地または停止点を描画する。。0.45の簡略比較画面の部品として保持する。現在のApp/mainからの表示経路には含まれない。元の有限成果や既存処理との比較に使うが、現役画面の入口とは案内しない。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `frontend/src/SamplingEditor.tsx` | active：既存条件棚で元量・仮幅・理由・N/seedと対応候補を編集し、固定計画の支持・母数を確認して明示実行/取消/再開/表示へ進む。。既存条件棚で元量・仮幅・理由・N/seedと対応候補を編集し、固定計画の支持・母数を確認して明示実行/取消/再開/表示へ進む。 | frontend/src/screens/ForecastScreen.tsx | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/WeatherPreparation.tsx` | active：保存例・配布一覧の部分観測・固定計画・取得job・完成場の明示適用を扱い、入力/選択を保持してGETを再確認する。。保存例・配布一覧の部分観測・固定計画・取得job・完成場の明示適用を扱い、入力/選択を保持してGETを再確認する。 | frontend/src/screens/ForecastScreen.tsx | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/acquisition.test.ts` | active：方式切替、取得時間窓・valid時刻、family適用とHTTP送信契約を無通信で確認する。。offlineの有限な契約試験。実HTTP/実UIと科学的受入を代替しない。 | docs/PROGRAM_GUIDE.tex、role:取得から適用・再計算までを維持する開発担当 | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/api.ts` | active：相対APIの期限付き読取り/明示送信と保存先UUIDガードを提供し、期限後もPOST/PUTを自動再送しない。。相対APIの期限付き読取り/明示送信と保存先UUIDガードを提供し、期限後もPOST/PUTを自動再送しない。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `frontend/src/climate-expansion.test.ts` | active：月/季節の正規化・図別表示/保存・時刻支持・経験風配・旧artifact・関心引渡し・図出力の有限反例を検査する。。既存集計を期間/時刻の比較へつなぐ0.56の現役実体。 | role:frontend統計表示回帰 | 固有の責務/根拠を後継へ引き継ぎ、利用先と対応検証を受け入れた後。 |
| `frontend/src/climate-quantiles.test.ts` | active：資料固有の年・UTC・面・重み、月分位のDTO、12か月共通軸と固定SVG条件の反例を検査する。。原標本の取得・固定支持・統計図・保存をつなぐ0.57の実体。機能検証と科学的受入は分ける。 | role:月分位表示回帰 | 固有の責務・来歴・利用先を後継へ引き継ぎ、対応検証を受け入れた後。 |
| `frontend/src/climate.test.ts` | active：実/人工adapterの意味境界・nativeID/null/母数・SVG出典と、実hookの草案/復元/遅延応答を有限stubで検証する。。実/人工adapterの意味境界・nativeID/null/母数・SVG出典と、実hookの草案/復元/遅延応答を有限stubで検証する。 | frontend/package.json | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/climateApi.ts` | active：実風資料一覧と明示した集計POST・固定GETを既存request経路へ接続し、応答包絡の一致を確かめる。。実風資料一覧と明示した集計POST・固定GETを既存request経路へ接続し、応答包絡の一致を確かめる。 | frontend/src/useClimateWorkspace.ts | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/climateDomain.ts` | active：資料固有の年・面・UTC・重み、任意native風配点と固定artifactの型・同一性・表示支持を定義し、原標本分位と静穏を含む一点風配を分ける。。実風統計のquery/descriptor/artifactと表示参照の型・同一性・対応条件・表示エラーを定義する。 | frontend/src/climateApi.ts、frontend/src/useClimateWorkspace.ts、frontend/src/screens/WeatherScreen.tsx、frontend/src/screens/weather/sources/climateSummary.ts | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/domain.test.ts` | active：日時変換・表示補間・条件差分と保存場表示の基本契約を検証する。。日時変換・表示補間・条件差分と保存場表示の基本契約を検証する。。現役の画面・APIと既存核の接続を担当し、n=1の受入を分散/科学的精度へ広げない。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `frontend/src/domain.ts` | active：共通候補・親子延期・表示状態・固定結果の型と、日時/差分/表示用内挿を定義する。共通計画と固定結果の型を画面・保存・描画変換へ渡す。UI状態を計算結果そのものへ混ぜない。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `frontend/src/ensemble.test.ts` | active：親子要求・固定選択・全母数と空間部分集合・退化経験域・共通時刻・対応draw・領域保存のキー順不変性と3D受渡しの反例を検査する。。親子要求・固定選択・全母数と空間部分集合・退化経験域・共通時刻・対応draw・領域保存のキー順不変性と3D受渡しの反例を検査する。 | frontend/package.json、docs/BUILD.md | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/ensembleApi.ts` | active：集合APIを固定要求の永続保持と期限付き読取りへ接続し、不明受付の自動再送をしない。。集合APIを固定要求の永続保持と期限付き読取りへ接続し、不明受付の自動再送をしない。 | frontend/src/useEnsembleWorkspace.ts | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/ensembleDomain.ts` | active：仮分布・集合/試行/分析・固定結果参照の型と、候補family要求・支持説明・固定選択の同一性を定義する。。仮分布・集合/試行/分析・固定結果参照の型と、候補family要求・支持説明・固定選択の同一性を定義する。 | frontend/src/SamplingEditor.tsx、frontend/src/ensembleApi.ts、frontend/src/useEnsembleWorkspace.ts、frontend/src/useWorkspace.ts、frontend/src/workspaceState.ts、frontend/src/screens/ForecastScreen.tsx、frontend/src/screens/forecast/controller.js、frontend/src/screens/forecast/ensembleProjection.ts | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/fixedResultRead.ts` | active：保存参照の読取り状態・表示名・詳細待機を共有する。計算状態や保存結果を所有せずHTTPも行わない。。保存参照の読取り状態・表示名・詳細待機を共有する。計算状態や保存結果を所有せずHTTPも行わない。 | docs/PROGRAM_GUIDE.tex、docs/IMPLEMENTATION_NOTES.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `frontend/src/ground-preparation.test.tsx` | active：モデル地表の明示照会/適用と、別地点へ変わった後の後着応答の拒否を有限hook条件で検査する。。モデル地表の明示照会/適用と、別地点へ変わった後の後着応答の拒否を有限hook条件で検査する。 | docs/IMPLEMENTATION_INDEX.json、role:地表入力検査 | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/historical.test.ts` | active：原日時の時間所有、予報/過去の表示分離、固定結果と変更草案の照合を有限条件で検査する。。原日時の時間所有、予報/過去の表示分離、固定結果と変更草案の照合を有限条件で検査する。 | docs/IMPLEMENTATION_INDEX.json | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/historicalDomain.ts` | active：共通機体と元UTC窓の入力契約、支持診断、固定結果との意味照合を保持する。。共通機体と元UTC窓の入力契約、支持診断、固定結果との意味照合を保持する。 | frontend/src/HistoricalPreparation.tsx、frontend/src/ensembleDomain.ts、frontend/src/historical.test.ts、frontend/src/screens/ForecastScreen.tsx、frontend/src/screens/forecast/ensembleProjection.ts | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/historicalTypes.ts` | active：原日時窓とその等重み標本の純型を共有する。集合型と原日時入力規則の相互importを避け、動作や採用判断を持たない。。原日時窓とその等重み標本の純型を共有する。集合型と原日時入力規則の相互importを避け、動作や採用判断を持たない。 | frontend/src/historicalDomain.ts、frontend/src/ensembleDomain.ts | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/historicalWorkspace.ts` | active：共有projectを用途別に射影し、気象関心の来歴を詳細標本選択と分離して保持する。識別できる旧来歴だけを読み替える。。共有projectを用途別に射影し、気象関心の来歴を詳細標本選択と分離して保持する。識別できる旧来歴だけを読み替える。 | frontend/src/App.tsx、frontend/src/historical.test.ts、frontend/src/screens/ForecastScreen.tsx | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/jobObservation.ts` | active：GET観測の同時読取・期限後の間隔・最終確定状態・破棄を共有し、通信失敗と処理状態を分ける。。読取callbackを注入される共通監視。HTTPやPOSTの再送、物理failedの決定を所有しない。 | frontend/src/useWorkspace.ts、frontend/src/WeatherPreparation.tsx、docs/PROGRAM_GUIDE.tex | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/jra-weather.test.ts` | active：保存JRAの時刻秒・製品識別・由来の四状態と固定結果の分離を、既存入力/投影の有限反例で検査する。。実helper、SSRと保持controller断片を読み、秒・内容hash・旧snapshot・支持表示を検査する。実マウス・全DOM・科学精度の試験ではない。 | docs/IMPLEMENTATION_INDEX.json、role:画面接点検査 | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/main.tsx` | active：React AppとLeafletのCSSを読み、共通画面のrootを起動する。現役起動入口。旧src/style.cssはimportせず、Appがplatform.cssと各画面のCSSを使う。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `frontend/src/modelDrafts.ts` | active：方式別の非選択入力を退避・復元し、指定familyへ気象だけを適用する純粋な更新。。方式別の非選択入力を退避・復元し、指定familyへ気象だけを適用する純粋な更新。 | frontend/src/App.tsx、frontend/src/ConfigEditor.tsx、frontend/src/acquisition.test.ts | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/operational-observation.test.tsx` | active：GET期限・応答欠落・古い応答・全active復旧・初期取得の独立失敗を、草案/固定結果/POST再送との分離で検査する。。GET期限・応答欠落・古い応答・全active復旧・初期取得の独立失敗を、草案/固定結果/POST再送との分離で検査する。 | docs/IMPLEMENTATION_INDEX.json、role:観測回復検査 | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/platform.css` | active：共通ヘッダー・用途選択・保存入口と各画面hostの配置を定める。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/App.tsx | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/recordedMutation.ts` | active：集合POSTの正確な本文とIDを送信前に保持し、不明受付を明示回復へ残す。。集合POSTの正確な本文とIDを送信前に保持し、不明受付を明示回復へ残す。 | frontend/src/ensembleApi.ts、frontend/src/service-identity.test.ts、frontend/src/submission-recovery.test.ts、frontend/src/useEnsembleWorkspace.ts | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/restoration.test.ts` | active：保存結果GETの待機・404・失敗・再読、後着応答と草案/選択/画面寿命の境界を有限なhook/投影反例で検査する。。保存結果GETの待機・404・失敗・再読、後着応答と草案/選択/画面寿命の境界を有限なhook/投影反例で検査する。 | docs/PROGRAM_GUIDE.tex、docs/IMPLEMENTATION_NOTES.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `frontend/src/scene3d-datum.test.ts` | active：固定EGM96データの同一性・参照値・周期/極/符号・不正入力拒否と元高度不変を通信なしで検査する。。0.55追補の3D表示とその有限検査に使用。ASLの元結果・KML出力と描画時の高度変換を分ける。 | frontend/package.json、frontend/scene3d/src/vertical-datum.js | 担当する表示/入力/取消の契約と固有の来歴を後継へ移し、利用先と対応検査を受け入れた後。 |
| `frontend/src/scene3d-geometry.test.ts` | active：地形照会不要の実ASL連続幕、曲率/長経路fallback、人工AGL全体保留と表示更新の取消/復帰を有限条件で検査する。。0.55追補の3D表示とその有限検査に使用。ASLの元結果・KML出力と描画時の高度変換を分ける。 | frontend/package.json、frontend/scene3d/src/route-layer.js | 担当する表示/入力/取消の契約と固有の来歴を後継へ移し、利用先と対応検査を受け入れた後。 |
| `frontend/src/scene3d-routes.test.ts` | active：可視/注目/詳細対象の同じ経路と相・高度規約を地表線/空中線/幕の一組として送受信する契約を検査する。。0.55追補の3D表示とその有限検査に使用。ASLの元結果・KML出力と描画時の高度変換を分ける。 | frontend/package.json、frontend/scene3d/src/protocol.js | 担当する表示/入力/取消の契約と固有の来歴を後継へ移し、利用先と対応検査を受け入れた後。 |
| `frontend/src/screen-contracts.test.ts` | active：実recordの不等間隔・停止・欠測、草案比較、後着結果、3D/KML受渡し、季節adapterを有限な反例で検査する。固定した標本・入力・停止例による境界試験。試験ソースの所在と内容を記録し、実行結果や実UI受入を示す印にはしない。 | role:画面と固定結果の受渡しを検査する担当 | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/ForecastScreen.tsx` | active：成熟した予報画面へ実入力/固定結果と原日時窓を接続し、共有projectを用途別に表示する。。成熟した予報画面へ実入力/固定結果と原日時窓を接続し、共有projectを用途別に表示する。 | frontend/src/App.tsx | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/WeatherScreen.tsx` | active：実/人工の気象画面入口を保ち、資料別支持で草案と固定図を接続し、実統計の関心も原日時比較へ渡す。。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/App.tsx | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/forecast/analysisLoadState.test.ts` | active：全件/部分群の識別、原履歴の独立GET、blocked/failedとowner取得/明示retryの有限反例を検査する。。0.55の詳細閲覧と明示的な送信担当切替を支える現役実体。 | role:frontend回帰検査 | 固有の責務と根拠を後継へ引き継ぎ、利用先と対応検査を受け入れた後。 |
| `frontend/src/screens/forecast/analysisLoadState.ts` | active：固定case全件分析の再利用と群分析の読取/未送信保留/失敗/明示再試行を分け、画面破棄後の採用を止める。。0.55の詳細閲覧と明示的な送信担当切替を支える現役実体。 | frontend/src/screens/forecast/controller.js | 固有の責務と根拠を後継へ引き継ぎ、利用先と対応検査を受け入れた後。 |
| `frontend/src/screens/forecast/appearance390.js` | active：候補・延期系列・領域の色や表示段階を選ぶ操作を構成する。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screens/forecast/controller.js、frontend/src/screens/forecast/runtime.ts | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/forecast/controller.js` | active：予報の候補・延期系列・群・地図・詳細図と3D受渡しを操作につなぐ。既存候補/延期/群の操作を保ち、全台帳・空間点・履歴・固定選択分析を区別して2D/3D/詳細へ渡す。所属判定は既存mathを使用する。 | frontend/src/screens/forecast/runtime.ts | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/forecast/core340.js` | conditional：旧予報処理の抽出断片を保持し、controllerへ含まれた処理との比較先を残す。旧素材として保持。現在のApp/rendererのmodule参照経路では呼出しを確認できないため、現役機能とは記述しない。 | role:旧GUI素材の対応と移行後の責務を点検する担当 | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/forecast/data.js` | active：既存の人工候補・標本・履歴を画面確認用データとして供給する。人工データによる表示確認の入力。実気象・実フライトや科学的受入の根拠にしない。 | frontend/src/screens/forecast/controller.js、frontend/src/screens/forecast/runtime.ts | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/forecast/ensembleProjection.ts` | active：固定全台帳・共通分析・必要時に読んだ原履歴を既存画面へ写し、点/線/面・相別帯・draw ID対応比較を表示形式へ変換する。。固定全台帳・共通分析・必要時に読んだ原履歴を既存画面へ写し、点/線/面・相別帯・draw ID対応比較を表示形式へ変換する。 | frontend/src/screens/ForecastScreen.tsx、frontend/src/screens/forecast/controller.js | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/screens/forecast/export-context.test.ts` | active：未読履歴を除いた完成図を装わず、固定条件・過去窓の限界を図とKMLへ持ち出すことを検査する。。未読履歴を除いた完成図を装わず、固定条件・過去窓の限界を図とKMLへ持ち出すことを検査する。 | docs/IMPLEMENTATION_INDEX.json | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/screens/forecast/export390.js` | active：現在の地図上の対象を、図形・色・名称を含むGeoJSON/KML等へ変換する。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screen-contracts.test.ts、frontend/src/screens/forecast/controller.js、frontend/src/screens/forecast/runtime.ts | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/forecast/exportContext.ts` | active：固定結果の主要条件と図の読取完了条件を組み立て、表示中の草案と持出し結果を混同しない。。固定結果の主要条件と図の読取完了条件を組み立て、表示中の草案と持出し結果を混同しない。 | frontend/src/screens/forecast/controller.js、frontend/src/screens/forecast/export-context.test.ts | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/screens/forecast/historyLoadQueue.test.ts` | active：選択trialの独立GET、同時数/重複抑制、選択変更・失敗再試行・dispose時の原履歴queueを無通信の有限反例で検証する。。集計待ち・上限・選択変更・失敗再試行・dispose時の原履歴queueを無通信の有限反例で検証する。 | frontend/package.json | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/screens/forecast/historyLoadQueue.ts` | active：現在選択した固定trialの原履歴GETを群分析から独立した有限queueで読み、旧未発行要求を捨て失敗だけ明示再試行する。。現選択に対応した確定分析からだけ原履歴を読む画面寿命の有限queueを持ち、旧未発行要求を捨て失敗だけ明示再試行する。 | frontend/src/screens/forecast/controller.js | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/screens/forecast/hover-geometry400.mjs` | active：輪郭への距離から名称表示の候補を絞る幾何処理を持つ。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screens/forecast/hover400.mjs | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/forecast/hover400.mjs` | active：2D地図の静止カーソル位置と表示対象から名称吹出しを更新する。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screens/forecast/runtime.ts | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/forecast/map-style-guard401.js` | active：2D地図の必要CSSと配置状態を点検し、復帰・再試行を制御する。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screens/forecast/controller.js、frontend/src/screens/forecast/runtime.ts | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/forecast/markup.html` | active：候補タブ・注目帯・共有地図・条件棚・詳細・各対話の具体DOMを保持する。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screens/forecast/runtime.ts | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/forecast/math.js` | active：領域形状・包含・交差・標本の分類と表示用集約を提供する。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screens/forecast/controller.js、frontend/src/screens/forecast/runtime.ts | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/forecast/projection.ts` | active：共通候補と固定runを、既存画面のタブ・標本・履歴の描画形式へ写す。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screen-contracts.test.ts、frontend/src/screens/ForecastScreen.tsx | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/forecast/runtime.ts` | active：予報画面のDOM・CSS・補助moduleを読み込み、描画controllerを起動・終了する。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screens/ForecastScreen.tsx | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/forecast/scene-document.js` | active：現在の対象・輪郭・領域・経路を独立3D rendererへ渡すsnapshotへ組み立てる。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screen-contracts.test.ts、frontend/src/screens/forecast/controller.js、frontend/src/screens/forecast/runtime.ts | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/forecast/screen.css` | active：予報・詳細・季節計画の画面配置と見た目を画面scope内に定める。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screens/forecast/runtime.ts | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/forecast/season-adapter.js` | active：気象画面の季節条件を、人工の季節計画データへ受け渡す。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screen-contracts.test.ts、frontend/src/screens/forecast/controller.js、frontend/src/screens/forecast/runtime.ts | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/lifecycle.ts` | active：画面hostへ渡すdocument/windowとイベント・timer・observerの寿命をまとめる。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screens/forecast/runtime.ts、frontend/src/screens/weather/runtime.ts | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/shared/band-readout.mjs` | active：経験輪郭の面内区分とクリック読取りの共有判定を持つ。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screens/shared/hover-labels.mjs | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/shared/hover-labels.mjs` | active：重なりを含む面・境界の名称と吹出しの配置を共通に決める。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screen-contracts.test.ts、frontend/src/screens/forecast/hover400.mjs | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/shared/scene-style.js` | active：候補・輪郭帯・禁止領域の色・濃さ・名称の表現規則を共有する。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screen-contracts.test.ts、frontend/src/screens/forecast/controller.js、frontend/src/screens/forecast/runtime.ts、frontend/src/screens/forecast/scene-document.js | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/vendor.d.ts` | active：Plotlyの画面利用に必要なTypeScriptの外部module宣言を置く。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/tsconfig.json | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/weather/climateController.js` | active：固定実集計の図別表示と出力を所有し、元標本分位・補助平均・選択native点の風配を分ける。元格子点の操作を接続し、生成時の条件を保つ図出力の寿命を管理する。。既存集計を期間/時刻の比較へつなぐ0.56の現役実体。 | frontend/src/screens/weather/controller.js | 固有の責務/根拠を後継へ引き継ぎ、利用先と対応検証を受け入れた後。 |
| `frontend/src/screens/weather/climateDistributions.ts` | active：選択native点の風配の階級と静穏を含む選択UTC全標本の分母を照合・描画し、元格子点の選択図と補助の平均風速profileを担う。。既存集計を期間/時刻の比較へつなぐ0.56の現役実体。 | frontend/src/screens/weather/climateController.js | 固有の責務/根拠を後継へ引き継ぎ、利用先と対応検証を受け入れた後。 |
| `frontend/src/screens/weather/controller.js` | active：既存人工気象画面を維持し、実気象は専用controllerへ接続する。固定図の未読/失敗を人工値や空データへ読み替えない。。既存人工画面と実年間/地域図のDOM・描画・保存寿命を担当。固定図のGET未読/失敗を空データや人工値へ読み替えず表示する。 | frontend/src/screens/weather/runtime.ts | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/weather/direction-key.js` | active：風向矢印・配色とその凡例を画面の読み方へ結び付ける。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screens/weather/controller.js、frontend/src/screens/weather/runtime.ts | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/weather/export.ts` | active：保存開始時の図・固定集計/母数/尺度/出典を捕捉してSVGへ保存し、背景の欠落を成功として隠さない。。保存開始時の図・固定集計/母数/尺度/出典を捕捉してSVGへ保存し、背景の欠落を成功として隠さない。 | frontend/src/screens/weather/controller.js | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/screens/weather/fixture.js` | active：人工の気象系列・期間選択・集約と季節計画用標本を供給する。人工データによる表示確認の入力。実気象・実フライトや科学的受入の根拠にしない。 | frontend/src/screen-contracts.test.ts、frontend/src/screens/forecast/runtime.ts、frontend/src/screens/forecast/season-adapter.js、frontend/src/screens/weather/controller.js、frontend/src/screens/weather/runtime.ts | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/weather/impact-map.js` | active：既に求めた気象試算を代表地点・経路・分布として地図へ描き地点選択につなぐ。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screens/weather/controller.js、frontend/src/screens/weather/runtime.ts | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/weather/markup.html` | active：気象分析の4用途・期間/時刻/高度選択・図表・地点提案の具体DOMを保持する。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screens/weather/runtime.ts | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/weather/monthlyProfiles.ts` | active：固定summaryと月分位DTOの母集団を照合し、前後半中央値と月p10/p90を全12か月共通軸へ描く。平均を分位の代用品にしない。。原標本の取得・固定支持・統計図・保存をつなぐ0.57の実体。機能検証と科学的受入は分ける。 | frontend/src/screens/weather/sources/climateSummary.ts、frontend/src/screens/weather/climateController.js | 固有の責務・来歴・利用先を後継へ引き継ぎ、対応検証を受け入れた後。 |
| `frontend/src/screens/weather/plots.ts` | active：年間4図と地域の複数地図・同じ尺度/凡例を共通描画値から生成し、表示上のセルと矢印密度を母集団から分ける。。年間4図と地域の複数地図・同じ尺度/凡例を共通描画値から生成し、表示上のセルと矢印密度を母集団から分ける。 | frontend/src/screens/weather/controller.js、frontend/src/screens/weather/export.ts | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/screens/weather/runtime.ts` | active：気象画面のDOM・CSS・補助moduleを読み込み、controllerと引渡し操作を起動・終了する。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screens/WeatherScreen.tsx | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/weather/screen.css` | active：気象分析の4用途と地図/グラフの配置を画面scope内に定める。0.46の用途別画面統合で使用する現役候補。機能受入・写真3Dの再確認はS35の有限観察と分ける。 | frontend/src/screens/weather/runtime.ts | 固有の挙動・入力・来歴を後継へ移し、利用先の受入と残す理由を記録した後。無断削除しない。 |
| `frontend/src/screens/weather/sources/climateSummary.ts` | active：資料固有の固定summaryを表示modelへ投影し、年・native面・面積重み・高度支持・元標本分位の母集団を保持する。。固定analysisをraw標本へ捏造せず、UTC母数・native面/格子・pool/local R・null・出典付き表示値へ投影する。 | frontend/src/screens/WeatherScreen.tsx | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/screens/weather/sources/fixtureSummary.ts` | active：既存人工標本の集約とJST暦・元9格子/16面を保ち、人工と明示した共通描画値を供給する。。既存人工標本の集約とJST暦・元9格子/16面を保ち、人工と明示した共通描画値を供給する。 | frontend/src/screens/weather/controller.js | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/screens/weather/viewModel.ts` | active：人工と実集計を混ぜず同じ年間/地域図へ渡す表示値・母数・native識別・高さ/地理区画の契約を定義する。。人工と実集計を混ぜず同じ年間/地域図へ渡す表示値・母数・native識別・高さ/地理区画の契約を定義する。 | frontend/src/screens/weather/sources/climateSummary.ts、frontend/src/screens/weather/sources/fixtureSummary.ts、frontend/src/screens/weather/plots.ts、frontend/src/screens/weather/export.ts | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/service-identity.test.ts` | active：別state・未束縛要求の保留、読取り継続、instance不一致後の要求保持を検査する。。別state・未束縛要求の保留、読取り継続、instance不一致後の要求保持を検査する。 | docs/IMPLEMENTATION_INDEX.json | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/serviceIdentity.ts` | active：確認済みサービスの永続state UUIDを保持し、未確認の保存先へ新要求を送らない。。確認済みサービスの永続state UUIDを保持し、未確認の保存先へ新要求を送らない。 | frontend/src/acquisition.test.ts、frontend/src/api.ts、frontend/src/ensemble.test.ts、frontend/src/operational-observation.test.tsx、frontend/src/service-identity.test.ts、frontend/src/submission-recovery.test.ts、frontend/src/submissionLedger.ts、frontend/src/useWorkspace.ts、frontend/src/workspace-recovery.test.tsx、frontend/src/write-lease.test.ts | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/singleSubmission.ts` | active：固定した単便/延期家族を一件ずつ投入し、受付GETと明示再送・未送信取消を既存結果と分ける。。固定した単便/延期家族を一件ずつ投入し、受付GETと明示再送・未送信取消を既存結果と分ける。 | frontend/src/submission-recovery.test.ts、frontend/src/useWorkspace.ts | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/style.css` | conditional：条件比較・地図・履歴と状態表示の画面レイアウトを定義する。。0.45の簡略比較画面の部品として保持する。現在のApp/mainからの表示経路には含まれない。元の有限成果や既存処理との比較に使うが、現役画面の入口とは案内しない。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `frontend/src/submission-recovery.test.ts` | active：7候補の逐次投入、固定ID/本文、応答欠落・404後の明示再送・保存失敗を検査する。。7候補の逐次投入、固定ID/本文、応答欠落・404後の明示再送・保存失敗を検査する。 | docs/IMPLEMENTATION_INDEX.json | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/submissionLedger.ts` | active：kind別の固定要求をstate UUIDへ束縛してブラウザへ保存し、不正・別保存先・旧未識別の内容を無言で移行しない。。kind別の固定要求をstate UUIDへ束縛してブラウザへ保存し、不正・別保存先・旧未識別の内容を無言で移行しない。 | frontend/src/HistoricalPreparation.tsx、frontend/src/WeatherPreparation.tsx、frontend/src/operational-observation.test.tsx、frontend/src/recordedMutation.ts、frontend/src/service-identity.test.ts、frontend/src/singleSubmission.ts、frontend/src/submission-recovery.test.ts、frontend/src/useEnsembleWorkspace.ts、frontend/src/useWorkspace.ts、frontend/src/workspace-recovery.test.tsx、frontend/src/write-lease.test.ts | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/useClimateWorkspace.ts` | active：草案と固定集計を分け、気圧面・風配点・明示集計を最新要求列で直列化する。地点を含む6面cacheと地点変更時失効、再送ID・後着応答・固定GET復帰を管理し、地点のみの適用では地域・UTC・面の未適用草案を保持する。。草案条件・固定集計・復元と要求世代の正本を持ち、旧図を保持した再集計・要求ID再送・計画参照保存を管理する。 | frontend/src/screens/WeatherScreen.tsx | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/useEnsembleWorkspace.ts` | active：固定した集合の計画/受付・結果選択・群集計を管理し、不明要求と独立したGET監視を保持する。。固定した集合の計画/受付・結果選択・群集計を管理し、不明要求と独立したGET監視を保持する。 | frontend/src/App.tsx、frontend/src/SamplingEditor.tsx | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/useWorkspace.ts` | active：草案・固定結果・保存・単便家族・healthを所有し、固定要求の明示回復と通信観測を物理stateから分ける。。草案・固定結果・保存・単便家族・healthを所有し、固定要求の明示回復と通信観測を物理stateから分ける。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `frontend/src/weather-observation.test.tsx` | active：現在source一覧だけの変化が既存ForecastScreenのeffectを通じ、n=1/集合の由来表示へ届き旧結果/支持を保持する接点を検査する。。実ForecastScreenを有限hook harnessで呼び、catalog-only変更と欠落を検査する。runtimeはstubでありブラウザ・StrictMode全挙動を再現したとは扱わない。 | docs/IMPLEMENTATION_INDEX.json、role:表示更新検査 | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/weatherAcquisition.ts` | active：気象取得APIの型、候補familyの時間窓と取得要求、適用前の時間・地点の必要条件を扱う。。気象取得APIの型、候補familyの時間窓と取得要求、適用前の時間・地点の必要条件を扱う。 | frontend/src/WeatherPreparation.tsx、frontend/src/acquisition.test.ts、frontend/src/api.ts | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `frontend/src/workspace-recovery.test.tsx` | active：保存PUT不明と草案保持、独立GETの失敗、health故障、壊れた台帳、未完成草案の保存を有限hook条件で検査する。。保存PUT不明と草案保持、独立GETの失敗、health故障、壊れた台帳、未完成草案の保存を有限hook条件で検査する。 | docs/IMPLEMENTATION_INDEX.json | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/workspaceState.test.ts` | active：後着完了・明示選択・保存中編集と送信意図の状態遷移を検証する。。後着完了・明示選択・保存中編集と送信意図の状態遷移を検証する。。現役の画面・APIと既存核の接続を担当し、n=1の受入を分散/科学的精度へ広げない。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `frontend/src/workspaceState.ts` | active：草案・固定結果・比較選択と送信意図の状態遷移を管理する。。草案・n=1固定結果と集合固定参照の比較選択を保存し、共有する選択世代で遅い応答の上書きを防ぐ。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `frontend/src/write-lease.test.ts` | active：タブ間の送信権排他、明示移譲、破棄後の遅いgrant、readerのPOST/台帳更新拒否を検査する。。タブ間の送信権排他、明示移譲、破棄後の遅いgrant、readerのPOST/台帳更新拒否を検査する。 | docs/IMPLEMENTATION_INDEX.json | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/src/write-operation-guard.test.tsx` | active：受付から台帳後処理までの送信operationと取得時のintent更新を、mock境界内の正常/失敗/破棄反例で検査する。。0.55の詳細閲覧と明示的な送信担当切替を支える現役実体。 | role:frontend回帰検査 | 固有の責務と根拠を後継へ引き継ぎ、利用先と対応検査を受け入れた後。 |
| `frontend/src/writeLease.ts` | active：同originの要求送信と台帳更新を一タブへ限定し、別タブの閲覧と明示的な送信権取得を保つ。。同originの要求送信と台帳更新を一タブへ限定し、別タブの閲覧と明示的な送信権取得を保つ。 | frontend/src/acquisition.test.ts、frontend/src/api.ts、frontend/src/ensemble.test.ts、frontend/src/operational-observation.test.tsx、frontend/src/service-identity.test.ts、frontend/src/singleSubmission.ts、frontend/src/submission-recovery.test.ts、frontend/src/submissionLedger.ts、frontend/src/useWorkspace.ts、frontend/src/workspace-recovery.test.tsx、frontend/src/write-lease.test.ts | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `frontend/tsconfig.json` | active：画面と構築設定のTypeScript型検査範囲と出力方針を定義する。。画面と構築設定のTypeScript型検査範囲と出力方針を定義する。。現役の画面・APIと既存核の接続を担当し、n=1の受入を分散/科学的精度へ広げない。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `frontend/vite.config.ts` | active：React/TypeScript/ViteとローカルAPIを接続し、scene3d依存配布物を通常buildのresolved outDirにだけ生成する。。devのCesium配信を維持し、Vitest/dev終了では配布物をコピーしない。 | docs/PROGRAM_GUIDE.tex、docs/COMMANDS.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `references/EXCEL_ANALYSIS_REVIEW.md` | reference：Excel分析原資料の同一性・保存依存・既存原本との対応と未検証を保持し、入力/導出/モデル接続へ使う知見を案内する。提供6HTMLと同梱170ファイルの読取、A/B原本照合、飛行入力の有限差分、旧解析の条件付き結論と現在設計への接続を記す。科学計算/Excel再計算の再受入ではない。 | docs/INTEGRATION_DESIGN.html、role:物理入力と不確かさの設計担当 | 固有の原本・設計理由・再現証拠・未確認境界を後継へ保持/移管し、主担当が理由と次判定を記録した後。無断削除しない。 |
| `references/Program_Guide_FractalJP_Settings.pdf` | reference：構造説明形式の参考原資料。気球実装でなく説明パターンの例 | docs/DOCUMENT_CONTROL.md | 参照理由がなくなるか同等の例と原資料保全を確認後 |
| `references/Program_Guide_FractalJP_Settings.tex` | reference：参考ガイドの編集元原資料。内容の転用・公開許諾や再ビルドは別途確認 | references/Program_Guide_FractalJP_Settings.pdf | PDFを引き続き置く間は対のソースを保持 |
| `references/SOURCES.json` | reference：外部根拠の所在・確認日。外部調査の範囲と提供原本の来歴、一時Project資料の探索索引。現在条件や科学の全面確認ではない | docs/PROJECT_PLAN.md | 現在引用を代替し必要根拠を引継いだ後 |
| `references/WIND_REPORT_REVIEW.md` | reference：提供風解析の原本同定・独立検算・不一致・実装へ受け入れる教訓。提供原PDF/統計DBの数値監査、季節・場所選定/予報着地分散の判断用途を保持。指定9図の定義と年間比較軸を再読し、既集計DBで可能な表示と任意年/時刻maskに原標本を要する再集計を区別して設計へ渡す。 | docs/THEORY_GUIDE.tex、docs/PROGRAM_GUIDE.tex、role:モデル評価担当 | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `references/climate_demo_057/README.md` | reference：小規模機能デモの出典・native支持・展開手順と全地域統計/飛行用気象場との用途差を案内する。。原標本の取得・固定支持・統計図・保存をつなぐ0.57の実体。機能検証と科学的受入は分ける。 | docs/COMMANDS.md、REFERENCE_LOG.md | 固有の責務・来歴・利用先を後継へ引き継ぎ、対応検証を受け入れた後。 |
| `references/climate_demo_057/archive.json` | reference：固定デモZIPと全memberのpath/bytes/SHAを列挙し、オフライン展開前の完全一致を確認する。。原標本の取得・固定支持・統計図・保存をつなぐ0.57の実体。機能検証と科学的受入は分ける。 | tools/prepare_climate_demo.py | 固有の責務・来歴・利用先を後継へ引き継ぎ、対応検証を受け入れた後。 |
| `references/climate_demo_057/jra3q-native-basis.json` | reference：提供JRA資料由来のnative格子・圧力面・Gaussian重みを保持し、DB無しの取得条件照合へ使う。気象標本自体は含まない。。原標本の取得・固定支持・統計図・保存をつなぐ0.57の実体。機能検証と科学的受入は分ける。 | tools/acquire_jra3q_climate_samples.py | 固有の責務・来歴・利用先を後継へ引き継ぎ、対応検証を受け入れた後。 |
| `references/climate_demo_057/wind-samples.zip` | reference：独立したJRA/ERA各四元格子の全2024 UTC・native圧力面・元u/vと来歴を保全する機能デモ。全北海道の統計母集団ではない。。原標本の取得・固定支持・統計図・保存をつなぐ0.57の実体。機能検証と科学的受入は分ける。 | tools/prepare_climate_demo.py、references/climate_demo_057/archive.json | 固有の責務・来歴・利用先を後継へ引き継ぎ、対応検証を受け入れた後。 |
| `references/design_trials/framework_assessment_043.zip` | reference：固定参考FE/BEと現projectの用途を比較し、器の借用・現役ソース・二結果比較・正本分担の根拠へ戻る。参考main94887cbbの全188実体、担当FE/BE/継続性レビュー、有限試験と反例、固定照合を保存する。実装移行・科学採用・実サービス成功の証拠ではない。 | docs/INTEGRATION_DESIGN.html、docs/DECISIONS.md、role:正式開発への構成比較と後続実装担当 | 固有の固定参考・出典・批評・反例・未確認境界を後継へ保持し、理由と受入先を記録した後。無断削除しない。 |
| `references/design_trials/framework_integration_045.zip` | reference：0.45の実装移行・独立批評・実UI・保存再開・ソース境界の有限証拠を保持する。。0.45実装の有限検証・失敗と修復・独立批評・実UI観察の固定証拠。現役ソースはfrontend/backendに別置する。 | BOOTSTRAP_RUNBOOK.html#S35、REFERENCE_LOG.md、role:0.45移行の根拠 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `references/design_trials/gui_integration_046.zip` | reference：0.40.1 r2の具体GUI統合について批評・有限な実UI/API検査・文書生成の証拠と途中失敗を保持する。0.46の段階証拠。記録した入力・観察・失敗と未確認の範囲へ戻る。Git保存・全操作・科学精度・写真3Dの受入をZIP存在だけから推定しない。 | BOOTSTRAP_RUNBOOK.html、REFERENCE_LOG.md、docs/INTEGRATION_DESIGN.html | 固有の原入力・観察・批評・失敗を後継へ保持し、移管先と理由を記録した後。無断削除しない。 |
| `references/design_trials/hover_and_backend_design_040.zip` | reference：名称hoverの操作模型と、模型から実入力・場・保存へ接続する設計の原要求/批評/有限観察へ戻る。0.40の模型/source・原要求・独立批評・接続設計材料を保管する候補ZIP。最終packageと観察範囲は確定後にS34へ記録し、Googleキーや背景tileを保管しない。 | docs/SIMULATOR_VISION.html、docs/INTEGRATION_DESIGN.html、role:操作模型の設計レビュー担当 | 固有の原本・設計理由・再現証拠・未確認境界を後継へ保持/移管し、主担当が理由と次判定を記録した後。無断削除しない。 |
| `references/design_trials/hover_surface_pick_correction_0401.zip` | reference：面内名称と2D復帰の反例、限定修復・用途に沿う再評価、再現sourceと旧r1内容復旧へ戻る。0.40.1 r2の具体画面・source・批評・有限観察と旧r1復旧を保持する。0.46では用途別の具体画面の移植素材として参照する。原本と現役frontendを同一実体と扱わず、改修点/出典へ戻れるようにする。 | docs/SIMULATOR_VISION.html、role:地物確認から俯瞰比較へ戻る操作と公開SDK接続のレビュー担当 | 固有の旧反例・設計理由・再現証拠を後継へ移管し、理由を記録した後。無断削除しない。 |
| `references/design_trials/interaction_and_burst.zip` | reference：利用者が何を比較し判断できる必要があるかを有限模型で具体化し、実操作・視認・原資料との対応で評価する。旧案と科学反例は比較根拠として保持する。。0.35 workflow-ui-035の予報/気象模型と担当QA、短い現行レビュー。旧340 member中README/manifestを更新し残り338実体のbyteを保持。主担当検証と独立批評はinteraction_and_burst_review_035.zip、比較代案はinteraction_and_burst_alternatives_035.zipを同所展開して読む。人工模型で本体・科学採用ではない。 | docs/SIMULATOR_VISION.html、role:設計レビュー担当 | 本体の連動集計と破裂分布接続を受け入れる時に、この有限例の固有証拠と再現源を移すか保持するかを理由付きで判断。無断削除しない。 |
| `references/design_trials/interaction_and_burst_alternatives_035.zip` | reference：同じ場面と標本で比較した配置・表示の代案とその批評を保存し、採用案が失った効用と棄却理由へ戻る。。0.35のalternatives全体を保持する比較案ZIP。他の二ZIPと同じフォルダーへ展開する。 | docs/SIMULATOR_VISION.html、role:設計レビュー担当 | 本体の操作と科学受入へ接続する時に、各巡の固有証拠と再現源の移設/保持を理由付きで判断する。無断削除しない。 |
| `references/design_trials/interaction_and_burst_review_035.zip` | reference：各巡の要求・批評・反例・根拠訂正・比較案・主担当検証へ戻り、現行受入と固定sourceの対応を点検する。。0.35のreview/critiqueを保持する検証批評ZIP。模型ZIP・比較代案ZIPと同じフォルダーへ展開する。短い現行レビューと画像の一部は実行側にも同一byteで含む。 | docs/SIMULATOR_VISION.html、role:設計レビュー担当 | 本体の操作と科学受入へ接続する時に、各巡の固有証拠と再現源の移設/保持を理由付きで判断する。無断削除しない。 |
| `references/design_trials/interaction_workflow_037.zip` | reference：0.37の操作模型・再現source・原意見と利用入口。人工模型の操作評価と本体/科学採用を区別する。workflow-ui-037の操作模型、再現source/lock/license、原意見、3D技術検証と失敗/修復証拠。第二ZIPと同所へ展開して批評と代案へ戻る。人工模型の有限受入であり本体/科学/Google接続ではない。 | docs/SIMULATOR_VISION.html、role:設計レビュー担当 | 後続の設計または本体接続で固有の模型・原意見・批評・証拠を移設/保持する判断を理由付きで記録した後。無断削除しない。 |
| `references/design_trials/interaction_workflow_review_037.zip` | reference：0.37各巡の批評・代案・失敗・操作/表示証拠へ戻り、判断の変更理由と未確認を追う。独立批評、反対案、2D/季節の失敗と修復/操作/表示証拠。第一ZIPと同所へ展開し3D技術証拠を含む一つの証拠木へ復元する。人工模型の有限受入と未確認の根拠。 | docs/SIMULATOR_VISION.html、role:設計レビュー担当 | 後続の設計または本体接続で固有の模型・原意見・批評・証拠を移設/保持する判断を理由付きで記録した後。無断削除しない。 |
| `references/design_trials/needs_review_036.zip` | reference：0.36のneeds再調査の根拠・担当批評・最新フィードバック・有限観察と主担当総合判断に戻る。。RPT058/059/060に対する調査証拠ZIP。既存三模型ZIPの実体は変更せず、調査・観察・解釈と未実装を区別して保存する。 | docs/SIMULATOR_VISION.html、role:設計レビュー担当 | 後続設計で調査の固有証拠と原フィードバックの移設/保持を理由付きで判断した後。無断削除しない。 |
| `references/design_trials/photoreal_connection_038.zip` | reference：同じ落下結果を写真3Dで詳しく確認する接続模型・再現source・原要求・批評証拠へ戻り、実接続と未確認を区別する。自己完結のworkflow-ui-038操作模型、写真3Dの再現source/固定依存/license、原要求と批評/失敗/修復/実物観察を収録。展開してlocalhost HTTPから試す。キーとGoogleタイルは含めず、実接続と人工試験の範囲を区別する。 | docs/SIMULATOR_VISION.html、role:設計レビュー担当 | 後続の設計または本体接続で固有の模型・原要求・批評・証拠を移設/保持する判断を理由付きで記録した後。無断削除しない。 |
| `references/design_trials/scene_context_and_export_039.zip` | reference：同じ分析対象を2D・3D・保存先で読み比べる操作模型、再現source・原要求・批評証拠へ戻り、表示仮定と確認範囲を区別する。0.39操作模型と固定依存の再現source、RPT065原PDF、各巡の批評・失敗・修復・人工/実Googleの観察記録、実保存KML/JSON/SVGと独立reader。背景キー・取得tileを含まない。名称hoverは設計案のみ。旧タブ保存未到達の原因と全地物/科学の受入は未確認。 | docs/SIMULATOR_VISION.html、role:設計レビュー担当 | 後続の設計または本体接続で固有の模型・原要求・批評・証拠を移設/保持する判断を理由付きで記録した後。無断削除しない。 |
| `references/design_trials/weather_acquisition_047.zip` | active：0.47の実取得・明示適用・入力保持と画面批評/修正、有限検査と固定source照合の証拠を保存する。。有限実行・実UI・原HTTPと保存照合の証拠。科学的完成や全地域の支持保証とは分ける。 | docs/PROGRAM_GUIDE.tex、role:取得から適用・再計算までを維持する開発担当 | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `references/development_evidence/climate_expansion_0560_evidence.zip` | reference：提供統計の独立読解/SQL照合、各実装版の有限回帰、実UIと状態保全、ガイド/索引の原票を保全する。。原資料読解・独立数値照合・実UI・回帰・出版を有限な範囲で保全する証拠。 | BOOTSTRAP_RUNBOOK.html、REFERENCE_LOG.md | 固有の責務/根拠を後継へ引き継ぎ、利用先と対応検証を受け入れた後。 |
| `references/development_evidence/climate_interaction_0580_evidence.zip` | reference：0.58の年間専用48区分・気圧面探索について、原資料の支持確認、数値互換・費用比較、表示と保存、資料・索引の有限検査と訂正の根拠を保全する。各票の実施範囲・未確認を区別し、科学的受入やmain統合の証明には広げない。。0.58の有限実績・訂正・未確認を辿る証拠束。収録内容と最終指紋は主担当が確定する。 | BOOTSTRAP_RUNBOOK.html、REFERENCE_LOG.md | 固有の責務・来歴・利用先を後継へ引き継ぎ、対応検証と継続または退役の理由を記録した後。無断削除しない。 |
| `references/development_evidence/climate_quantiles_0570_evidence.zip` | reference：0.57の原標本取得・独立照合・統計図/フィルター・保存図・有限回帰・ガイド出版の実施範囲と未確認を保全する証拠束。。原標本の取得・固定支持・統計図・保存をつなぐ0.57の実体。機能検証と科学的受入は分ける。 | BOOTSTRAP_RUNBOOK.html、REFERENCE_LOG.md | 固有の責務・来歴・利用先を後継へ引き継ぎ、対応検証を受け入れた後。 |
| `references/development_evidence/detail_lease_0550_evidence.zip` | reference：詳細閲覧/明示引継ぎ修復の再現・有限反例・実UI観察・批評と出版の証拠を保全する。。有限試験・実UI観察・批評・出版の開発証拠。科学精度や全環境での受入証明ではない。 | BOOTSTRAP_RUNBOOK.html、REFERENCE_LOG.md | 固有の責務と根拠を後継へ引き継ぎ、利用先と対応検査を受け入れた後。 |
| `references/development_evidence/document_role_audit_0590_evidence.zip` | reference：0.59文書監査の独立批評・旧本文対応・生成/表示確認を保持する。管理検査やGit保存より前の有限証拠で、科学全体や実画面の再受入へ広げない。。文書の問い・責務・現在案内を点検した証拠束。原票の範囲と後続の保存記録を区別する。 | BOOTSTRAP_RUNBOOK.html、REFERENCE_LOG.md | 固有の役割と来歴を後継へ引き継ぎ、理由と対応検証を記録した後。無断削除しない。 |
| `references/development_evidence/ensemble_connection480.zip` | active：0.48の元量共有・全試行保存・対応候補/延期・選択群の接続について、設計・反例批評・有限試験/実UI・固定source照合の証拠を保存する。。作成・全member照合済みの有限証拠束。全機能・全データ・校正された確率・科学的精度の完成と区別する。 | BOOTSTRAP_RUNBOOK.html、REFERENCE_LOG.md、role:集合接続の設計・有限受入を再確認する開発担当 | 固有の判断・原入力・検証証拠を保持した移管を記録した後。過去版の証拠を無断削除しない。 |
| `references/development_evidence/historical_field510.zip` | reference：0.51の固定JRA原本から保存場・既存飛行核へ至る有限実行、支持停止、独立批評と資料生成の証拠を保全する。。生成・全154 memberの検算済みの固定証拠束。5例すべて停止の数値実績・失敗と再試験を保持し、後続のガイド出版・管理検査・Git保存・科学的受入とは分ける。 | BOOTSTRAP_RUNBOOK.html、REFERENCE_LOG.md、docs/DECISIONS.md | 固有の入力・来歴・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `references/development_evidence/historical_surface520.zip` | reference：0.52のJRA取得・失敗を含む明示再開、配列正規化、地上接続方式比較と有限CLI実行の由来を保全する証拠束。。原応答・変換と比較の出典へ戻るための固定資料。生成・全member検算は主担当の出版票に従い、登録案自体は完了を主張しない。 | references/flight_fixture/jra3q-weather.json.gz、BOOTSTRAP_RUNBOOK.html、REFERENCE_LOG.md、docs/DECISIONS.md | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `references/development_evidence/operational_continuity500.zip` | reference：0.50の保存結果読取り・GFS窓拡張raw再利用と、過去場への次接続設計の入力・来歴・有限批評/受入を保全する。。保存済み固定結果の復元失敗/再読と条件付きraw共有の固有観測を保存する143-member証拠束。過去JRA4D場は次接続設計であり、運用や科学精度の完成を表さない。 | BOOTSTRAP_RUNBOOK.html、REFERENCE_LOG.md、docs/DECISIONS.md | 固有の入力・原結果・失敗・来歴と採否を後継へ保持し、受入先と移行理由を記録した後。無断削除しない。 |
| `references/development_evidence/operational_weather490.zip` | reference：0.49の実GFS行程費用、実風統計接続、既存GUIとの比較・反例と有限受入の証拠を保持する。。実GFSの240原試行・取得・処理費用と、実JRA集計/画面/保存・有限検証の証拠を保全する。派生表示の再生成と既存0.48証拠へのhash参照、外部JRA原DB依存を明示する。 | BOOTSTRAP_RUNBOOK.html、REFERENCE_LOG.md、docs/DECISIONS.md | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `references/development_evidence/practical_forecast550.zip` | reference：0.55の予報反復行程・応答不明回復・原日時試算と実取得/画面/失敗/未確認を保全する有限証拠束。。出版済みの有限証拠。実取得・固定入力/結果・操作・故障・ガイドの有限証拠を保持する。科学精度・季節代表性・main統合を意味しない。 | BOOTSTRAP_RUNBOOK.html、REFERENCE_LOG.md、docs/DECISIONS.md | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `references/development_evidence/practical_weather540.zip` | reference：0.54の現在予報の準備・地表入力・観測回復・比較/保存・実負荷と失敗/未確認を保全する有限証拠束。。現在予報の原応答・完成場、単便/集合の固定入力と公開結果、UI/失敗/修復/再現/ガイドの有限証拠を保持する。科学精度・全画面/SQLite復元・後続保存票を代替しない。 | BOOTSTRAP_RUNBOOK.html、REFERENCE_LOG.md、docs/DECISIONS.md、role:実用行程の有限再読 | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `references/development_evidence/route3d_0550_evidence.zip` | reference：0.55追補の立体軌道/カーテンについて設計是正・有限検査・実画面観察と未確認を保全する。。失敗・利用者批評・是正後の観察を区別する開発証拠。科学精度や全地形での受入証明ではない。 | BOOTSTRAP_RUNBOOK.html、REFERENCE_LOG.md | 固有の判断理由と再検査に必要な証拠を後継へ受け入れ、原票の保持要否を明示した後。 |
| `references/development_evidence/saved_jra_gui530.zip` | reference：0.53の保存JRA登録・同一核数値対照・秒/延期・固定結果由来と保存再読の有限検討/観測を保全する証拠束。。失敗・修正・未確認を含む実票の出典へ戻る固定資料。原場/原11変数は固定0.52資料を参照し、ここへの登録だけでUI・科学・保存成功を主張しない。 | BOOTSTRAP_RUNBOOK.html、REFERENCE_LOG.md、docs/DECISIONS.md、role:接続の有限受入再読 | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `references/excel_analysis_manifest.json` | reference：提供Excel分析ZIP・member・依存閉包と既存Excel原本の照合証拠を、原著者本文と分けて保存する。原ZIPと170実体、6入口、43HTML依存、原飛行表の有限相違を結ぶ保管照合票。byte同一性と科学再現/表示検証を区別する。 | references/EXCEL_ANALYSIS_REVIEW.md、references/SOURCES.json、role:資料保管担当 | 固有の原本・設計理由・再現証拠・未確認境界を後継へ保持/移管し、主担当が理由と次判定を記録した後。無断削除しない。 |
| `references/flight_fixture/hokkaido-weather.json.gz` | reference：全飛行をオフラインで再現する北海道の取得済み正規化小標本。0.20の固定した再現入力。実データ由来の限定回帰で、最新予報・全国入力・精度の保証ではない。 | examples/hokkaido-simple.json、tests/test_flight_cli.py | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `references/flight_fixture/jra3q-weather.json.gz` | reference：同一JRA製品の取得11変数から作った、明示B方針と入力来歴を持つ固定3UTC・100モデル面の保存飛行場。。C-11と既存GUIのオフライン再現入力。schema/reconstructionと原配列由来を固定し、履歴絶対パスの存在をruntimeの必要条件にしない。元時刻一窓であり半月DBの仮想場ではない。 | examples/jra3q-ground-flight.json、docs/COMMANDS.md、role:有限再現担当、backend/application.py | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `references/flight_fixture/manifest.json` | active：二地点標本の出所・run/valid・抽出条件・hashと再現限界。0.20の固定した再現入力。実データ由来の限定回帰で、最新予報・全国入力・精度の保証ではない。 | docs/COMMANDS.md、tests/test_flight_cli.py | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `references/flight_fixture/wakayama-weather.json.gz` | reference：全飛行をオフラインで再現する和歌山の取得済み正規化小標本。0.20の固定した再現入力。実データ由来の限定回帰で、最新予報・全国入力・精度の保証ではない。 | examples/wakayama-isothermal.json、tests/test_flight_cli.py | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `references/gfs_p1_fixture/f000.grib2` | reference：GFS仮領域の固定f000入力。取得原バイトの再検査用。。P1/T-005の入力受入。補間・飛行モデル・科学的精度の受入ではない。 | docs/PROJECT_PLAN.md、role:P1作業者 | T-005正規化受入時に後継の入力契約・回帰への統合を判断。原データ/来歴/検査の行先と理由を残す。 |
| `references/gfs_p1_fixture/f001.grib2` | reference：GFS仮領域の固定f001入力。取得原バイトの再検査用。。P1/T-005の入力受入。補間・飛行モデル・科学的精度の受入ではない。 | docs/PROJECT_PLAN.md、role:P1作業者 | T-005正規化受入時に後継の入力契約・回帰への統合を判断。原データ/来歴/検査の行先と理由を残す。 |
| `references/gfs_p1_fixture/f002.grib2` | reference：GFS仮領域の固定f002入力。取得原バイトの再検査用。。P1/T-005の入力受入。補間・飛行モデル・科学的精度の受入ではない。 | docs/PROJECT_PLAN.md、role:P1作業者 | T-005正規化受入時に後継の入力契約・回帰への統合を判断。原データ/来歴/検査の行先と理由を残す。 |
| `references/gfs_p1_fixture/manifest.json` | active：固定GFS小標本の取得来歴・期待構造・限界の編集元。P1/T-005の入力受入。補間・飛行モデル・科学的精度の受入ではない。 | docs/PROJECT_PLAN.md、role:P1作業者 | T-005正規化受入時に後継の入力契約・回帰への統合を判断。原データ/来歴/検査の行先と理由を残す。 |
| `references/jra3q_model_fixture/source_bundle.json` | reference：JRAモデル面の小固定入力。原ASCII/属性/係数とURL・取得時刻・hashの保存正本。旧取得原本を保持し、旧試作検証と0.51の固定bundle変換に用いる。任意日時の取得や地上完飛行・科学精度の採用へ広げない。 | tools/normalize_jra3q_model_fixture.py | T-005一般adapterとT-008初回flightの受入時に、担当CodexがAPI/来歴/拒否条件/回帰の後継統合または継続理由を判定。固有根拠の行先を残し無断削除しない。 |
| `references/research_returns/Q420-00/2026-09-29-r7/CODEX_EVIDENCE.zip` | reference：独立批評・再計算・不一致を含む再現証拠を保つ。独立批評・再計算・不一致を含む再現証拠を保つ。研究提案とCodex採否を区別し、科学採用・実装済みと扱わない。 | docs/INTEGRATION_DESIGN.html、docs/research/README.md、role:研究返却の読解・再現・採否 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `references/research_returns/Q420-00/2026-09-29-r7/CODEX_RESEARCH_REPORT.md` | reference：Chat第7巡の原研究本文を直接読む。Chat第7巡の原研究本文を直接読む。研究提案とCodex採否を区別し、科学採用・実装済みと扱わない。 | docs/INTEGRATION_DESIGN.html、docs/research/README.md、role:研究返却の読解・再現・採否 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `references/research_returns/Q420-00/2026-09-29-r7/CODEX_REVIEW.md` | reference：現在の設計に対する採否・批評・再現限界へ戻る。現在の設計に対する採否・批評・再現限界へ戻る。研究提案とCodex採否を区別し、科学採用・実装済みと扱わない。 | docs/INTEGRATION_DESIGN.html、docs/research/README.md、role:研究返却の読解・再現・採否 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `references/research_returns/Q420-00/2026-09-29-r7/Q420_R7_20260929_package.zip` | reference：Chat第7巡の416実体を原本として保つ。Chat第7巡の416実体を原本として保つ。研究提案とCodex採否を区別し、科学採用・実装済みと扱わない。 | docs/INTEGRATION_DESIGN.html、docs/research/README.md、role:研究返却の読解・再現・採否 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `references/research_returns/Q420-00/2026-09-29-r7/READING_AND_EVIDENCE_LOG.md` | reference：著者の実読・失敗・訂正と証拠の範囲を保つ。著者の実読・失敗・訂正と証拠の範囲を保つ。研究提案とCodex採否を区別し、科学採用・実装済みと扱わない。 | docs/INTEGRATION_DESIGN.html、docs/research/README.md、role:研究返却の読解・再現・採否 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `references/user_supplied/ascent_burst_gas_a.xlsx` | reference：上昇・破裂・ガス量計算書Aの提供原本。既存式と入力の比較元。原入力と既存計算の根拠として参照。採用済みモデルや正解入力ではない | docs/PROJECT_PLAN.md | 比較・判断の根拠としての役割終了または代替を受入れ、固有情報と来歴の行先を確認後。削除は明示許可の範囲のみ |
| `references/user_supplied/ascent_burst_gas_b.xlsx` | reference：上昇・破裂・ガス量計算書Bの提供原本。Aの完全な後継とは未認定。原入力と既存計算の根拠として参照。採用済みモデルや正解入力ではない | docs/PROJECT_PLAN.md | 比較・判断の根拠としての役割終了または代替を受入れ、固有情報と来歴の行先を確認後。削除は明示許可の範囲のみ |
| `references/user_supplied/excel_analysis_20260920.zip` | reference：ユーザー提供のExcel分析原ZIPをbyte不変で保持し、本文・図・再現材料と著者の未確認範囲へ戻る。revised_01a0b429配下170ファイルを収めた11,177,282 bytesの原ZIP。6HTMLのみでなく相対依存を保管し、旧計画や改訂Excelを現在の命令/採用済み計算器に変換しない。 | references/EXCEL_ANALYSIS_REVIEW.md、references/excel_analysis_manifest.json、role:分析資料の参照担当 | 固有の原本・設計理由・再現証拠・未確認境界を後継へ保持/移管し、主担当が理由と次判定を記録した後。無断削除しない。 |
| `references/user_supplied/feedback_v_0_40_1.pdf` | reference：利用者の接続設計・入力/MC・保存の指摘を図付き原本へ戻って確認する。原資料の記述を現在の採用/命令と区別する。 | docs/research/README.md、role:Codexの設計担当とChat研究担当 | 固有の依頼・出典・版・採否と再生成手段を後継へ保持した後。原本は派生物だけで代替せず、無断削除しない。 |
| `references/user_supplied/feedback_v_0_40_1.txt` | generated：同feedbackの本文を探索する抽出補助。図と細部はPDFへ戻る。編集元ではない。源範囲・生成器へ戻り、再生成の同一性を確認して配布する。実Chat回答や科学採用の成功証拠ではない。 | docs/research/README.md、role:Codexの設計担当とChat研究担当 | 固有の依頼・出典・版・採否と再生成手段を後継へ保持した後。原本は派生物だけで代替せず、無断削除しない。 |
| `references/user_supplied/flight_records.xlsx` | reference：提供された15便の打上げ記録表。完全な生計測ログとは区別する。原入力と既存計算の根拠として参照。採用済みモデルや正解入力ではない | docs/PROJECT_PLAN.md | 比較・判断の根拠としての役割終了または代替を受入れ、固有情報と来歴の行先を確認後。削除は明示許可の範囲のみ |
| `references/user_supplied/wind_analysis_report.pdf` | reference：提供風分析報告の原PDF。気候分析と着地分散の判断用途の参考原本。提供風分析報告の原PDF。気候分析と着地分散の判断用途の参考原本。0.21/RPT038で受入。科学的結論の一括採用とは区別する。 | references/WIND_REPORT_REVIEW.md、role:分析担当 | 後継へ固有情報・原本同定・再現と未検証を移し、担当Codexが保持/移管理由と次判定を記録してから判断する。無断削除しない。 |
| `references/user_supplied/wind_analysis_report.txt` | generated：提供風PDFから出所とページを保持して抽出した検索用本文。表示/式の原本はPDF。提供風PDFから出所とページを保持して抽出した検索用本文。表示/式の原本はPDF。0.21/RPT038で受入。科学的結論の一括採用とは区別する。 | references/WIND_REPORT_REVIEW.md、role:資料取得担当 | 後継へ固有情報・原本同定・再現と未検証を移し、担当Codexが保持/移管理由と次判定を記録してから判断する。無断削除しない。 |
| `tests/test_acquire_era5_climate_samples.py` | active：ERA5のDODS/NCSS復号、元値・格子/面/UTC照合、通信上限・失敗保持・累積試行枠と既存原物/checkpoint再利用を通信なしの反例で検査する。。原標本の取得・固定支持・統計図・保存をつなぐ0.57の実体。機能検証と科学的受入は分ける。 | role:ERA5取得CLI回帰 | 固有の責務・来歴・利用先を後継へ引き継ぎ、対応検証を受け入れた後。 |
| `tests/test_acquire_jra3q_climate_samples.py` | active：JRAの元値・格子/面/UTC照合、native basis、通信上限・失敗保持・明示再開の反例を検査する。。原標本の取得・固定支持・統計図・保存をつなぐ0.57の実体。機能検証と科学的受入は分ける。 | role:JRA取得CLI回帰 | 固有の責務・来歴・利用先を後継へ引き継ぎ、対応検証を受け入れた後。 |
| `tests/test_check_run.py` | active：失敗時postと生ログ保全の回帰試験。問題解消後も守る契約が有効な間は保持 | role:テスト実行者 | 守る契約を廃止/置換し、検出能力と理由を後継へ受入後 |
| `tests/test_contract.py` | active：必要性/論証/変更理由の構造の回帰試験。用途/論証/遷移/ガード/入口を隔離試験する。偽ready反例は初期状態に依存せず証拠を明示的に除去する。候補の完了状態を理由に反例を失わない。 | role:テスト実行者 | 守る契約を廃止/置換し、検出能力と理由を後継へ受入後 |
| `tests/test_ensemble.py` | active：抽選固定と元量解決、欠結果/空履歴、退化/曲線/多峰/描画域外、相端点/同時刻/終了と選択IDの有限反例を検査する。。抽選固定と元量解決、欠結果/空履歴、退化/曲線/多峰/描画域外、相端点/同時刻/終了と選択IDの有限反例を検査する。 | docs/BUILD.md、docs/THEORY_GUIDE.tex | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `tests/test_environment.py` | active：環境入力・線形補間・端点・欠測・地下・支持範囲・実標本の契約試験。固定3時刻gpm/地下mask/原GRIB照合の独立回帰。新runtimeはtest_flight_weather/trajectoryで別に検査する。 | role:検査担当 | T-005の一般環境adapter受入時にAPI・来歴・品質と回帰を後継へ移すか判断。原標本と固有根拠は保持。 |
| `tests/test_flight_cli.py` | active：実コマンド・保存成果物・来歴・出力保全と二地点全飛行の回帰。0.20の現役本体開発を支える資料・入力例・生成/検査実体。使用範囲と未検証を各担当本文へ戻す。 | role:検査担当 | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `tests/test_flight_numerics.py` | active：数値adapterの解析式/誤差/根と、製品規則・選択モデルの責務分離を検証する。D-162の修復で分離した実体。定義と公開経路はIMPLEMENTATION_INDEXへ接続する | role:本体開発と検証 | 責務と固有の挙動・試験を後継へ移し、使用先との互換を受け入れた後 |
| `tests/test_flight_weather.py` | active：列別再構成と時空間補間・支持/品質・取得上限・原入力再生の回帰。0.20の現役本体開発を支える資料・入力例・生成/検査実体。使用範囲と未検証を各担当本文へ戻す。 | role:検査担当 | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `tests/test_gfs_acquisition.py` | active：NOMADS通信の有界性と利用者共通間隔、取得取消・raw再利用の契約を無通信で確認する。。offlineの有限な契約試験。実HTTP/実UIと科学的受入を代替しない。 | docs/PROGRAM_GUIDE.tex、role:取得から適用・再計算までを維持する開発担当 | 固有の契約・入力・来歴と検証を後継へ移し、利用先の受入と継続または退役の理由を記録した後。無断削除しない。 |
| `tests/test_gfs_forecast_plan.py` | active：GFS予定時刻の端点・内部欠落・未配布・明示fallbackと入力誤りの回帰。観測inventoryの時刻計画と明示fallbackの回帰。0.20取得/再生の検査と証明範囲を分ける。 | role:検査担当 | 一般取得器との接続受入時にCodexがAPI/来歴/拒否条件/回帰の後継統合または継続理由を判定。固有根拠の移管先を残し無断削除しない。 |
| `tests/test_gfs_raw_reuse.py` | active：一致する保存rawの検算・独立コピー・不足時刻通信・曖昧bytes拒否・容量/取消/保存障害を注入して検査する。。一致する保存rawの検算・独立コピー・不足時刻通信・曖昧bytes拒否・容量/取消/保存障害を注入して検査する。 | docs/PROGRAM_GUIDE.tex、docs/IMPLEMENTATION_NOTES.md、role:実装と開発環境 | 固有の原本・来歴・採否・失敗を後継へ保持し、移動理由と受入先を記録した後。無断削除しない。 |
| `tests/test_health.py` | active：時点/範囲の欠落・誤登録の回帰試験。問題解消後も守る契約が有効な間は保持 | role:テスト実行者 | 守る契約を廃止/置換し、検出能力と理由を後継へ受入後 |
| `tests/test_jra3q_flight_field.py` | active：解析式・Decimal・固定原行との独立照合、JRA製品/保存dispatch・支持外拒否と既存飛行の相別停止を検査する。。有界なoffline回帰。全期間取得、地上完飛行、実機精度、統計確率の検証へ拡張しない。 | role:検査担当 | 固有の入力・来歴・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `tests/test_jra3q_model_environment.py` | active：原入力再読と独立期待値、時空間/鉛直端点・予定時刻欠落・必要量・欠測/地表gapの回帰。JRAモデル面の列別圧力/高さ/予定時刻の回帰を保持。GFS軌道成功をこの経路の全飛行成功へ転用しない。 | role:検査担当 | T-005一般adapterとT-008初回flightの受入時に、担当CodexがAPI/来歴/拒否条件/回帰の後継統合または継続理由を判定。固有根拠の行先を残し無断削除しない。 |
| `tests/test_jra3q_surface_field.py` | active：表層B方式の再構成順序、固定join、局所欠測・支持、schema dispatchと旧strict維持を無通信の有限反例で検査する。。解析配列と旧固定原本を検査入力とし、runtimeが旧toolへ依存しないことも検査する。取得器・実打上げ精度・UIの試験とは分ける。 | role:検査担当 | 固有の入力・由来・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `tests/test_model_composition.py` | active：構成依存の正常/反例とJRA能力の照合。実力学と全飛行成功は対象外。静的な構成依存の正常/反例。実力学・全飛行検査はtest_trajectoryと役割を分けて保持する。 | role:検査担当 | T-005一般adapterとT-008初回flightの受入時に、担当CodexがAPI/来歴/拒否条件/回帰の後継統合または継続理由を判定。固有根拠の行先を残し無断削除しない。 |
| `tests/test_state.py` | active：表示と現行ファイルの検査の回帰試験。問題解消後も守る契約が有効な間は保持 | role:テスト実行者 | 守る契約を廃止/置換し、検出能力と理由を後継へ受入後 |
| `tests/test_trajectory.py` | active：解析解・別の力釣合い・刻み幅収束・支持境界・地形イベントの軌道回帰。0.20の現役本体開発を支える資料・入力例・生成/検査実体。使用範囲と未検証を各担当本文へ戻す。 | role:検査担当 | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `tests/test_workspace.py` | active：同期保全・LFとHTML呼出の回帰試験。問題解消後も守る契約が有効な間は保持 | role:テスト実行者 | 守る契約を廃止/置換し、検出能力と理由を後継へ受入後 |
| `tools/acquire_era5_climate_samples.py` | active：ERA5の元格子・圧力面・UTCを保持し、明示DODS/NCSS選択と上限・失敗原票付きの有限取得・再開で原標本束を保存する。照合済みDODSと完成月checkpointを再利用し、自動fallbackを行わない。。原標本の取得・固定支持・統計図・保存をつなぐ0.57の実体。機能検証と科学的受入は分ける。 | docs/COMMANDS.md、role:ERA5原風取得 | 固有の責務・来歴・利用先を後継へ引き継ぎ、対応検証を受け入れた後。 |
| `tools/acquire_jra3q_climate_samples.py` | active：提供DBまたは固定native basisを配布metadataへ照合し、JRA-3Qの元UTC u/vを有限取得・明示再開して原標本束へ保存する。。原標本の取得・固定支持・統計図・保存をつなぐ0.57の実体。機能検証と科学的受入は分ける。 | docs/COMMANDS.md、role:JRA原風取得 | 固有の責務・来歴・利用先を後継へ引き継ぎ、対応検証を受け入れた後。 |
| `tools/build_docs.py` | conditional：計画MDからTeX/PDF生成。専用Windows環境で文書生成を受入。失敗時の対不一致を避け別作業コピーでのみ使用 | docs/BUILD.md | 後継生成器と原文/表示再現を受入後 |
| `tools/build_guides.py` | active：理論/構造TeXからPDFと検索テキストを一組として再生成。既存TeX環境で選択したガイドをPDF/検索txtへ生成。省略時は両冊、選択時は選択冊だけ成功後にpublishする。 | docs/COMMANDS.md、docs/BUILD.md | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `tools/build_research_packet.py` | active：登録された源範囲から課題別資料束と内容manifestを再現生成・検査する。RPT-067/D-180の研究委譲を現在の設計へ結ぶ。未発行/未受領を成功へ変えない。 | docs/research/README.md、role:Codexの設計担当とChat研究担当 | 固有の依頼・出典・版・採否と再生成手段を後継へ保持した後。原本は派生物だけで代替せず、無断削除しない。 |
| `tools/check_contract.py` | active：必要性・論証・変更理由の構造検査。現在の用途/論証と、前後の構造/依存/保管/ガード差分・理由を読み取り検査。葉の自身の変更と祖先影響を分離する。 共通入口とコピー/READMEの対応、外部観測の限界、実在する完全基準での比較成立を検査する。。契約本文版とファイル版登録の一致も検査する | tools/check_state.py | 同等の目的/寿命/変更理由検査を後継で受入後 |
| `tools/check_health.py` | active：確認後変更・依存・期限の検査。確認印や意味の自動承認はしない。比較指定時は完全な前状態を必須とし、表示専用モードとの併用を拒否する | tools/run_checks.py | 時点/依存/未確認を後継へ移し異常試験受入後 |
| `tools/check_state.py` | active：ファイル・状態・参照の検査。新しい構造契約も呼ぶ通常入口 | tools/run_checks.py | 同等以上の欠落/状態/参照検査を後継で受入後 |
| `tools/compose_model.py` | active：段階別モデル構成から必要能力・状態移行を合成し、不足・重複・未使用入力を拒否する静的候補。将来の組合せ・必要能力を議論する静的候補。0.20実行可能な構成はdynamics.validate_configで限定され、未実装の慣性/Re/熱経路を選択しても実行済みとはしない。 | tests/test_model_composition.py、role:モデルと環境の接続担当 | T-005一般adapterとT-008初回flightの受入時に、担当CodexがAPI/来歴/拒否条件/回帰の後継統合または継続理由を判定。固有根拠の行先を残し無断削除しない。 |
| `tools/inspect_gfs_fixture.py` | active：固定GFS小標本のオフライン復号・単位・格子・UTC・欠測と保全を検査。P1/T-005の入力受入。補間・飛行モデル・科学的精度の受入ではない。 | docs/PROJECT_PLAN.md、role:P1作業者 | T-005正規化受入時に後継の入力契約・回帰への統合を判断。原データ/来歴/検査の行先と理由を残す。 |
| `tools/make_flight_fixture.py` | active：保存済み気象から全飛行回帰用の限定標本を来歴付きで作る。0.20の現役本体開発を支える資料・入力例・生成/検査実体。使用範囲と未検証を各担当本文へ戻す。 | references/flight_fixture/manifest.json、docs/COMMANDS.md | 対応する本体/説明/再現の後継へ固有の式・API・証拠・受入条件を移し、Codexが継続または退役理由と次判定を記録した後。無断削除しない。 |
| `tools/normalize_gfs_fixture.py` | active：固定GFSの正規化・地下/欠測maskとgeopotential height限定の問い合わせ候補。0.14固定3時刻のgpm専用adapterとして現役回帰を保持。0.20の幾何高度・地表橋渡し・全飛行runtimeとはAPIを混同しない。 | tests/test_environment.py、role:S14比較担当 | T-005の一般環境adapter受入時にAPI・来歴・品質と回帰を後継へ移すか判断。原標本と固有根拠は保持。 |
| `tools/normalize_jra3q_model_fixture.py` | active：JRA100層の列別圧力・高さを正規化し、必要fieldと共通gpm/UTCの支持付き問い合わせを返す限定候補。既存の限定研究adapterと回帰を保持し、0.51変換toolの原本検証にも再利用する。現役load_weather/飛行はこのtoolsへ依存しない。 | tests/test_jra3q_model_environment.py、tests/test_model_composition.py | T-005一般adapterとT-008初回flightの受入時に、担当CodexがAPI/来歴/拒否条件/回帰の後継統合または継続理由を判定。固有根拠の行先を残し無断削除しない。 |
| `tools/plan_gfs_forecast.py` | active：観測inventoryから単一GFS runと飛行時間窓を覆う予定validを選ぶオフライン候補。観測inventoryからrunを比較するオフライン候補。0.20取得器は利用者が明示した単一runを取得し、run自動選択へ暗黙接続していない。 | tests/test_gfs_forecast_plan.py、role:取得器と環境接続担当 | 一般取得器との接続受入時にCodexがAPI/来歴/拒否条件/回帰の後継統合または継続理由を判定。固有根拠の移管先を残し無断削除しない。 |
| `tools/prepare_climate_demo.py` | active：固定デモ束の全memberを照合して展開するか、完成した原束から四つの元格子を値・全UTC・全圧力面を変えず抽出する。通信しない。。原標本の取得・固定支持・統計図・保存をつなぐ0.57の実体。機能検証と科学的受入は分ける。 | docs/COMMANDS.md、references/climate_demo_057/README.md | 固有の責務・来歴・利用先を後継へ引き継ぎ、対応検証を受け入れた後。 |
| `tools/prepare_jra3q_flight_fixture.py` | active：固定JRA原本を旧検証器で再読し、新保存schemaを新規出力先へ生成・読戻しして変換来歴を残す無通信CLI。。研究用固定原本から現役bundleへの境界。runtime/飛行から旧toolsをimportする経路にはしない。 | docs/COMMANDS.md | 固有の入力・来歴・失敗条件・受入範囲を後継へ保持し、担当が移行理由と次判定を記録した後。無断削除しない。 |
| `tools/prepare_workspace.py` | active：保全的なclone検査・FF同期・LF整合。読取・同期・改行整合を明示分離。原本をreset/cleanで削除しない。同期時はGit無視対象を含めユーザーファイルと衝突すれば保全して停止する | BOOTSTRAP_RUNBOOK.html | 原本保全ガードと代替同期を受入後 |
| `tools/run_checks.py` | active：専用環境の段階検査とログ保存。成否にかかわらずpost照合を試みる | BOOTSTRAP_RUNBOOK.html | 生ログと実環境/前後検査を保つ代替を受入後 |
| `tools/template.tex` | conditional：計画表示のレイアウト原文。編集元の版/日付から柱・脚を生成する表示入力。外部フォントとTeX依存を必要とする | tools/build_docs.py | 代替テンプレートで可読性と生成を受入後 |
<!-- ASSET_VIEW_END -->

### 検査器が読むパス一覧

このブロックだけを機械の現行パス契約にする。役割が本当に増減するとき、上の表と一緒に更新する。通常の版更新だけでは変更しない。

<!-- CURRENT_PATHS_BEGIN -->
```text
.gitattributes
.gitignore
ACCESS_PROBE.md
AGENTS.md
BOOTSTRAP_RUNBOOK.html
CONTENT_MAP.md
PROJECT_CONTEXT.md
README.md
REFERENCE_LOG.md
backend/README.md
backend/__init__.py
backend/app.py
backend/application.py
backend/climate/__init__.py
backend/climate/aggregation.py
backend/climate/archive.py
backend/climate/contracts.py
backend/climate/extensions.py
backend/climate/periods.py
backend/climate/samples.py
backend/climate/service.py
backend/climate/source.py
backend/climate/statistics.py
backend/contracts.py
backend/ensemble/__init__.py
backend/ensemble/contracts.py
backend/ensemble/historical_planning.py
backend/ensemble/planning.py
backend/ensemble/service.py
backend/ensemble/storage.py
backend/ensemble/views.py
backend/errors.py
backend/historical_catalog.py
backend/pyproject.toml
backend/requirements.lock
backend/storage.py
backend/tests/test_application.py
backend/tests/test_climate.py
backend/tests/test_climate_api.py
backend/tests/test_climate_archive.py
backend/tests/test_climate_archive_interaction.py
backend/tests/test_climate_periods.py
backend/tests/test_climate_samples.py
backend/tests/test_climate_service.py
backend/tests/test_ensemble.py
backend/tests/test_historical_ensemble.py
backend/tests/test_recovery550.py
backend/tests/test_weather.py
backend/tests/test_weather_ground.py
backend/tests/test_weather_inventory_partial.py
backend/tests/test_weather_raw_reuse.py
backend/tests/test_weather_region.py
backend/weather/__init__.py
backend/weather/catalog.py
backend/weather/contracts.py
backend/weather/planning.py
backend/weather/service.py
backend/worker.py
balloon_sim/__init__.py
balloon_sim/__main__.py
balloon_sim/cli.py
balloon_sim/dynamics.py
balloon_sim/ensemble/__init__.py
balloon_sim/ensemble/geography.py
balloon_sim/ensemble/histories.py
balloon_sim/ensemble/landing.py
balloon_sim/ensemble/sampling.py
balloon_sim/ensemble/statistics.py
balloon_sim/environment/__init__.py
balloon_sim/environment/bundle.py
balloon_sim/environment/fields.py
balloon_sim/environment/gfs.py
balloon_sim/environment/gfs_contract.py
balloon_sim/environment/jra3q.py
balloon_sim/environment/model_levels.py
balloon_sim/environment/model_surface.py
balloon_sim/environment/nomads.py
balloon_sim/environment/storage.py
balloon_sim/flight/__init__.py
balloon_sim/flight/config.py
balloon_sim/flight/events.py
balloon_sim/flight/models.py
balloon_sim/flight/numerics.py
balloon_sim/flight/trajectory.py
balloon_sim/results/__init__.py
balloon_sim/results/export.py
balloon_sim/results/report.py
balloon_sim/weather.py
docs/BACKLOG.csv
docs/BUILD.md
docs/COMMANDS.md
docs/CONTENT_HEALTH.json
docs/CONTINUITY_CONTRACT.json
docs/DECISIONS.md
docs/DOCUMENT_CONTROL.md
docs/ENVIRONMENT_CONTRACT.md
docs/IMPLEMENTATION_INDEX.json
docs/IMPLEMENTATION_NOTES.md
docs/INTEGRATION_DESIGN.html
docs/LESSONS.md
docs/PROGRAM_GUIDE.pdf
docs/PROGRAM_GUIDE.tex
docs/PROGRAM_GUIDE.txt
docs/PROJECT_PLAN.md
docs/PROJECT_PLAN.pdf
docs/PROJECT_PLAN.tex
docs/SIMULATOR_VISION.html
docs/THEORY_GUIDE.pdf
docs/THEORY_GUIDE.tex
docs/THEORY_GUIDE.txt
docs/UNCERTAINTIES.csv
docs/VERSION_HISTORY.json
docs/WEATHER_DATA_GUIDE.md
docs/WORK_ORDER_TEMPLATE.md
docs/research/BRIEF.md
docs/research/README.md
docs/research/RESPONSE_TEMPLATE.md
docs/research/REVIEW_042.md
docs/research/TASKS.md
docs/research/UI_WALKTHROUGH.md
docs/research/packet_sources.json
docs/research/packets/Q410-01.md
docs/research/packets/Q410-02.md
docs/research/packets/Q410-03.md
docs/research/packets/Q410-04.md
docs/research/packets/Q410-05.md
docs/research/packets/Q420-00.md
docs/research/packets/manifest.json
examples/gfs-japan-request.json
examples/hokkaido-simple.json
examples/jra3q-ground-flight.json
examples/jra3q-support-flight.json
examples/wakayama-isothermal.json
frontend/SCREEN_PROVENANCE.md
frontend/index.html
frontend/package-lock.json
frontend/package.json
frontend/scene3d/THIRD_PARTY_NOTICES.txt
frontend/scene3d/data/README.md
frontend/scene3d/data/WW15MGH.DAC
frontend/scene3d/fixtures/surface.glb
frontend/scene3d/fixtures/tileset.json
frontend/scene3d/index.html
frontend/scene3d/src/band-readout.js
frontend/scene3d/src/camera-fit.js
frontend/scene3d/src/catalog.js
frontend/scene3d/src/colors.js
frontend/scene3d/src/fixture.js
frontend/scene3d/src/hover-controller.js
frontend/scene3d/src/hover-labels.js
frontend/scene3d/src/main.js
frontend/scene3d/src/overlay-store.js
frontend/scene3d/src/overlays.js
frontend/scene3d/src/protocol.js
frontend/scene3d/src/provider.js
frontend/scene3d/src/receipt-status.js
frontend/scene3d/src/route-geometry.js
frontend/scene3d/src/route-layer.js
frontend/scene3d/src/surface-pick.js
frontend/scene3d/src/surface-session.js
frontend/scene3d/src/vertical-datum.js
frontend/scene3d/src/view-memory.js
frontend/scene3d/src/view-stability.js
frontend/scene3d/style.css
frontend/src/App.tsx
frontend/src/ClimateFlightHandoff.tsx
frontend/src/ConfigEditor.tsx
frontend/src/GroundPreparation.tsx
frontend/src/HistoricalEntry.tsx
frontend/src/HistoricalPreparation.tsx
frontend/src/HistoryPanel.tsx
frontend/src/MapPanel.tsx
frontend/src/SamplingEditor.tsx
frontend/src/WeatherPreparation.tsx
frontend/src/acquisition.test.ts
frontend/src/api.ts
frontend/src/climate-expansion.test.ts
frontend/src/climate-quantiles.test.ts
frontend/src/climate.test.ts
frontend/src/climateApi.ts
frontend/src/climateDomain.ts
frontend/src/domain.test.ts
frontend/src/domain.ts
frontend/src/ensemble.test.ts
frontend/src/ensembleApi.ts
frontend/src/ensembleDomain.ts
frontend/src/fixedResultRead.ts
frontend/src/ground-preparation.test.tsx
frontend/src/historical.test.ts
frontend/src/historicalDomain.ts
frontend/src/historicalTypes.ts
frontend/src/historicalWorkspace.ts
frontend/src/jobObservation.ts
frontend/src/jra-weather.test.ts
frontend/src/main.tsx
frontend/src/modelDrafts.ts
frontend/src/operational-observation.test.tsx
frontend/src/platform.css
frontend/src/recordedMutation.ts
frontend/src/restoration.test.ts
frontend/src/scene3d-datum.test.ts
frontend/src/scene3d-geometry.test.ts
frontend/src/scene3d-routes.test.ts
frontend/src/screen-contracts.test.ts
frontend/src/screens/ForecastScreen.tsx
frontend/src/screens/WeatherScreen.tsx
frontend/src/screens/forecast/analysisLoadState.test.ts
frontend/src/screens/forecast/analysisLoadState.ts
frontend/src/screens/forecast/appearance390.js
frontend/src/screens/forecast/controller.js
frontend/src/screens/forecast/core340.js
frontend/src/screens/forecast/data.js
frontend/src/screens/forecast/ensembleProjection.ts
frontend/src/screens/forecast/export-context.test.ts
frontend/src/screens/forecast/export390.js
frontend/src/screens/forecast/exportContext.ts
frontend/src/screens/forecast/historyLoadQueue.test.ts
frontend/src/screens/forecast/historyLoadQueue.ts
frontend/src/screens/forecast/hover-geometry400.mjs
frontend/src/screens/forecast/hover400.mjs
frontend/src/screens/forecast/map-style-guard401.js
frontend/src/screens/forecast/markup.html
frontend/src/screens/forecast/math.js
frontend/src/screens/forecast/projection.ts
frontend/src/screens/forecast/runtime.ts
frontend/src/screens/forecast/scene-document.js
frontend/src/screens/forecast/screen.css
frontend/src/screens/forecast/season-adapter.js
frontend/src/screens/lifecycle.ts
frontend/src/screens/shared/band-readout.mjs
frontend/src/screens/shared/hover-labels.mjs
frontend/src/screens/shared/scene-style.js
frontend/src/screens/vendor.d.ts
frontend/src/screens/weather/climateController.js
frontend/src/screens/weather/climateDistributions.ts
frontend/src/screens/weather/controller.js
frontend/src/screens/weather/direction-key.js
frontend/src/screens/weather/export.ts
frontend/src/screens/weather/fixture.js
frontend/src/screens/weather/impact-map.js
frontend/src/screens/weather/markup.html
frontend/src/screens/weather/monthlyProfiles.ts
frontend/src/screens/weather/plots.ts
frontend/src/screens/weather/runtime.ts
frontend/src/screens/weather/screen.css
frontend/src/screens/weather/sources/climateSummary.ts
frontend/src/screens/weather/sources/fixtureSummary.ts
frontend/src/screens/weather/viewModel.ts
frontend/src/service-identity.test.ts
frontend/src/serviceIdentity.ts
frontend/src/singleSubmission.ts
frontend/src/style.css
frontend/src/submission-recovery.test.ts
frontend/src/submissionLedger.ts
frontend/src/useClimateWorkspace.ts
frontend/src/useEnsembleWorkspace.ts
frontend/src/useWorkspace.ts
frontend/src/weather-observation.test.tsx
frontend/src/weatherAcquisition.ts
frontend/src/workspace-recovery.test.tsx
frontend/src/workspaceState.test.ts
frontend/src/workspaceState.ts
frontend/src/write-lease.test.ts
frontend/src/write-operation-guard.test.tsx
frontend/src/writeLease.ts
frontend/tsconfig.json
frontend/vite.config.ts
references/EXCEL_ANALYSIS_REVIEW.md
references/Program_Guide_FractalJP_Settings.pdf
references/Program_Guide_FractalJP_Settings.tex
references/SOURCES.json
references/WIND_REPORT_REVIEW.md
references/climate_demo_057/README.md
references/climate_demo_057/archive.json
references/climate_demo_057/jra3q-native-basis.json
references/climate_demo_057/wind-samples.zip
references/design_trials/framework_assessment_043.zip
references/design_trials/framework_integration_045.zip
references/design_trials/gui_integration_046.zip
references/design_trials/hover_and_backend_design_040.zip
references/design_trials/hover_surface_pick_correction_0401.zip
references/design_trials/interaction_and_burst.zip
references/design_trials/interaction_and_burst_alternatives_035.zip
references/design_trials/interaction_and_burst_review_035.zip
references/design_trials/interaction_workflow_037.zip
references/design_trials/interaction_workflow_review_037.zip
references/design_trials/needs_review_036.zip
references/design_trials/photoreal_connection_038.zip
references/design_trials/scene_context_and_export_039.zip
references/design_trials/weather_acquisition_047.zip
references/development_evidence/climate_expansion_0560_evidence.zip
references/development_evidence/climate_interaction_0580_evidence.zip
references/development_evidence/climate_quantiles_0570_evidence.zip
references/development_evidence/detail_lease_0550_evidence.zip
references/development_evidence/document_role_audit_0590_evidence.zip
references/development_evidence/ensemble_connection480.zip
references/development_evidence/historical_field510.zip
references/development_evidence/historical_surface520.zip
references/development_evidence/operational_continuity500.zip
references/development_evidence/operational_weather490.zip
references/development_evidence/practical_forecast550.zip
references/development_evidence/practical_weather540.zip
references/development_evidence/route3d_0550_evidence.zip
references/development_evidence/saved_jra_gui530.zip
references/excel_analysis_manifest.json
references/flight_fixture/hokkaido-weather.json.gz
references/flight_fixture/jra3q-weather.json.gz
references/flight_fixture/manifest.json
references/flight_fixture/wakayama-weather.json.gz
references/gfs_p1_fixture/f000.grib2
references/gfs_p1_fixture/f001.grib2
references/gfs_p1_fixture/f002.grib2
references/gfs_p1_fixture/manifest.json
references/jra3q_model_fixture/source_bundle.json
references/research_returns/Q420-00/2026-09-29-r7/CODEX_EVIDENCE.zip
references/research_returns/Q420-00/2026-09-29-r7/CODEX_RESEARCH_REPORT.md
references/research_returns/Q420-00/2026-09-29-r7/CODEX_REVIEW.md
references/research_returns/Q420-00/2026-09-29-r7/Q420_R7_20260929_package.zip
references/research_returns/Q420-00/2026-09-29-r7/READING_AND_EVIDENCE_LOG.md
references/user_supplied/ascent_burst_gas_a.xlsx
references/user_supplied/ascent_burst_gas_b.xlsx
references/user_supplied/excel_analysis_20260920.zip
references/user_supplied/feedback_v_0_40_1.pdf
references/user_supplied/feedback_v_0_40_1.txt
references/user_supplied/flight_records.xlsx
references/user_supplied/wind_analysis_report.pdf
references/user_supplied/wind_analysis_report.txt
tests/test_acquire_era5_climate_samples.py
tests/test_acquire_jra3q_climate_samples.py
tests/test_check_run.py
tests/test_contract.py
tests/test_ensemble.py
tests/test_environment.py
tests/test_flight_cli.py
tests/test_flight_numerics.py
tests/test_flight_weather.py
tests/test_gfs_acquisition.py
tests/test_gfs_forecast_plan.py
tests/test_gfs_raw_reuse.py
tests/test_health.py
tests/test_jra3q_flight_field.py
tests/test_jra3q_model_environment.py
tests/test_jra3q_surface_field.py
tests/test_model_composition.py
tests/test_state.py
tests/test_trajectory.py
tests/test_workspace.py
tools/acquire_era5_climate_samples.py
tools/acquire_jra3q_climate_samples.py
tools/build_docs.py
tools/build_guides.py
tools/build_research_packet.py
tools/check_contract.py
tools/check_health.py
tools/check_state.py
tools/compose_model.py
tools/inspect_gfs_fixture.py
tools/make_flight_fixture.py
tools/normalize_gfs_fixture.py
tools/normalize_jra3q_model_fixture.py
tools/plan_gfs_forecast.py
tools/prepare_climate_demo.py
tools/prepare_jra3q_flight_fixture.py
tools/prepare_workspace.py
tools/run_checks.py
tools/template.tex
```
<!-- CURRENT_PATHS_END -->

### 原本と一時資料を使う判断

0.10.0候補で追加した3冊は、ユーザー提供の原本を同一バイトで保存する参照資料である。編集済みのモデルや正解データではない。原本名と保存名の対応、ハッシュ、用途、確認範囲は`references/SOURCES.json`で管理する。保存・固定読戻しの実績は内容検証と区別し、HTML S10-5で確認する。元のセル・注記・数式・保存値を残し、抽出・解釈・仮定を別に扱う。

| リポジトリ内のパス | 現在の用途 | 次に使う作業 |
|---|---|---|
| `references/user_supplied/flight_records.xlsx` | 提供された15便の打上げ記録表。完全な生時系列ログとは別 | T-006の対象理解、T-011の評価可能範囲・原セルの対応 |
| `references/user_supplied/ascent_burst_gas_a.xlsx` | 気球の上昇・破裂・ガス量に関する計算書A。係数と式は未検証 | T-006/011の入力理解、T-010の比較候補の根拠探索 |
| `references/user_supplied/ascent_burst_gas_b.xlsx` | 同分野の計算書B。Aの正しい完全後継とは未認定 | 同上。異なる入力や仮定の違いを比較 |

3冊は過去版の一式を置く倉庫ではなく、現在の検討が依存する原資料である。同じ責務を持つ参照原本を`references/user_supplied/`でまとめる。元の長い名前はSOURCESに保持し、コピー元を特定できるようにする。この保存名整理は、Project側の元ファイルの改名ではない。

### Projectの一時探索資料と、Gitへ受け入れた後継

0.10.0作成時に確認したProject資料は、気象データ候補のPDF4冊と、Excel・物理等に関するAI生成HTML7件である。これらは探索用であり、正式な採否や未実装機能を定める文書ではない。Project側の現在の掲載状態を再取得済みとはしない。名前・目的・原典への経路をSOURCESで案内し、採用する主張は原典等に戻って確認する。

Projectの`README.html`は参考パッケージの案内であり、リポジトリルートのREADME.mdではない。参照される一部のコード・修正版Excel等は0.10時点のProject集合になかった。この当時の不足を、後続で資料を受領した現在の未提供へ読み替えない。必要なものだけを取得し、全てを集めることを通常の計画相談の前提にしない。参考本文に書かれた「確認済み」は、その資料の作成者の記述であり、本プロジェクトの今回の検査成功ではない。

0.40では、そのうち既知6 HTMLと同じ内容を含む完全なExcel分析原ZIP（170ファイル）を`references/user_supplied/excel_analysis_20260920.zip`へ保管した。現在の入口は[EXCEL_ANALYSIS_REVIEW](references/EXCEL_ANALYSIS_REVIEW.md)、同一性・収録範囲は[excel_analysis_manifest.json](references/excel_analysis_manifest.json)。レビュー§4で必要な問いから原ZIPのHandbook章、原セル、再現資料へ辿る。分析に使った飛行表とrepo原本はbyte同一ではないが、有限のセル比較で実質入力差は検出されなかった。原A/Bはrepo既存2冊を使い、原ZIPにない著者builderや当時環境まで完全再現できるとはしない。旧AI-PROJECT-LEADSは受領履歴、後継のAI-EXCEL-ANALYSIS-001は現在の保管先という役割を分ける。

| 研究で必要な根拠 | Gitコピーから読めるもの | 別に確認するもの |
|---|---|---|
| 風分析の問い・図・推定法 | 原PDF/検索txt、WIND_REPORT_REVIEW | 外側保管の気象DBや当時の全実行。PDFの結論を科学的受入へ移さない |
| Excel入力・補助式・既存便 | 原xlsx、分析原ZIP、レビュー§4とmanifest | 未収録の著者生成環境、Microsoft Excel再計算、係数/母数の科学採用 |
| 気象製品・時刻・支持 | WEATHER_DATA_GUIDE、ENV、SOURCES、repo内の固定fixture | 外側の取得原票、現在の配布可用性/条件。取得URLとhashだけでは原bytesを復旧できない |
| 現在のUIと過去案 | VISIONのmodel-archive、保存された模型ZIPと批評 | Google実行時キー、写真タイル、現在hostの接続状態。Chatに操作確認を代行したことにさせない |
| 研究課題の最小入力 | docs/researchの課題・抽出範囲と生成した根拠束 | 未読節は未読、未受領資料は不足として返す。根拠束は指定版の派生物である |

一時保管の再判定は、最初のP1の情報源・比較条件のレビュー時、および該当論点を正式採用するときに行う。必要な主張と根拠を担当文書へ取り込み、参照が不要なら退役・Projectからの削除を利用者が判断する。必要なら理由と次の開発節目を残す。一時資料の所在・原典リンクを現在状態に保持することと、その全文をGitへ複写することは別である。

### 0.40.1模型の保管・限定評価を辿る（当時の索引）

以下は0.40.1の保存前後の参照案内を保持したもので、「現在」「次」は当時を指す。今回の行動はS35へ戻り、UI訂正の局所受入を本体接続や科学の受入へ拡張しない。

<details><summary>0.40.1で固定した模型と復旧・回帰の境界</summary>

完成した分析ツールを議論する場合は [SIMULATOR_VISION](docs/SIMULATOR_VISION.html) を読む。三用途の操作・モデル/分布・MC・図表・技術候補を持つ将来案の編集元で、実装説明とは別。工程はPLAN10.6、議論/実績はS34、採否はD-165/166へ戻る。0.40.1の現在案は[workflow401](docs/SIMULATOR_VISION.html#workflow401)、名称識別の修復と2D復帰の反証による完成判定撤回の理由はD179追記、r2の限定再評価と保存前手順は[S34末尾](BOOTSTRAP_RUNBOOK.html#s34-401-r2-review)。0.40の横断する接続案[INTEGRATION_DESIGN](docs/INTEGRATION_DESIGN.html)は維持する。旧9模型と当時の限定確認は[model-archive](docs/SIMULATOR_VISION.html#model-archive)へ。[hover_surface_pick_correction_0401.zip](references/design_trials/hover_surface_pick_correction_0401.zip) はr2の858ファイル、SHA256 `8356df3cc8f2184d5418fe3d84d1e1d274b7646f3b81be6210c07094b3d7a214` を照合済み。workflow-ui-0401/index.htmlが操作入口、review/hover-repair401.htmlが失敗・再修復・有限観察の入口である。r1の832内容はreview/previous-401-r1から826共通＋6旧byteを使って復旧・全照合した。反証前の未受入状態を消さず、元ZIPbyteの再現とは区別する。回帰時点の114実体へ標準430が成功した。結果と追記後の検査・保存先はS34末尾の実績へ結び、最終文書へ430再実行済みとは扱わない。本体20モジュールと現実装ガイドの対象は今回のUI訂正で変えない。PLAN/ENV/WGの0.40で修復した案内とExcel原ZIP・[内容と来歴のレビュー](references/EXCEL_ANALYSIS_REVIEW.md)を保持する。

</details>

## 3. 完了した0.3.0配置是正の受入先（監査用）

[更新:0.4.0] [確認:0.4.0]

S06はRPT-002とCHK-002で完了。以下の「退役」「消す前」等は当時の移行設計の記録であり、今回削除する指示ではない。通常の復旧は現行パスを読む。この対応表は情報の受入監査にまだ必要なため保持する。「PCのみ」は当時の配置先であって永久保管の命令ではない。現在の保存・整理条件はHTML retentionを優先し、固有の証拠と重複を分ける。

以下は旧版の読込を要求するリンク集ではなく、内容をどこへ引き継いだかの対応記録。0.3移行の受入監査と再発防止に必要な間だけ残し、以後の版別目録を追加しない。移行後の通常参照は第1〜2節。
旧物をGitHub上で別名へ丸ごと置くのではなく、必要な意味を現在の担当文書へ統合する。消す前にユーザーがC1固定ZIPをPCへ保全する。入力33件＋probe1件の基準34ファイルから、ルート6件更新・16新パス・27旧パス退役・probe保持で現在23ファイルになる。Gitのrename表示はこの概念上の分類と異なり得る。

| 退役する旧パス | 現在へ引き継ぐ情報／原物の扱い |
|---|---|
| `INITIAL_IMPORT_MANIFEST.json` | 初期配布だけの固定証拠はPCのみ。現行の検査に使用しない |
| `legacy/access-assessment-2026-09-16.md` | 読取実績/未検証条件はCONTEXT/REF_LOG、役割/費用の再確認条件はPLAN/UNCERTAINTIES。全文はPC |
| `legacy/bootstrap-draft-0.1/00_START_HERE.md` | README.md・HTMLの復旧手順へ統合 |
| `legacy/bootstrap-draft-0.1/01_PROJECT_STATE.json` | 要求9件/保存先/前提はPROJECT_CONTEXT、操作はHTMLへ統合。古いSTATEは退役 |
| `legacy/bootstrap-draft-0.1/02_FILE_REGISTRY.csv` | CONTENT_MAPの現在契約へ置換 |
| `legacy/bootstrap-draft-0.1/03_PROJECT_PLAN.md` | docs/PROJECT_PLAN.mdへ移し、現在方針へ更新 |
| `legacy/bootstrap-draft-0.1/03_PROJECT_PLAN.pdf` | docs/PROJECT_PLAN.pdfとして現在MD/TeXから再生成 |
| `legacy/bootstrap-draft-0.1/03_PROJECT_PLAN.tex` | docs/PROJECT_PLAN.texとして現在MDから再生成 |
| `legacy/bootstrap-draft-0.1/04_BACKLOG.csv` | docs/BACKLOG.csvへ移行。13件を保ち、実績と保留を更新 |
| `legacy/bootstrap-draft-0.1/05_UNCERTAINTIES.csv` | docs/UNCERTAINTIES.csvへ移行。12件を保ち、解決済み/部分確認を修正 |
| `legacy/bootstrap-draft-0.1/06_DECISIONS.md` | docs/DECISIONS.mdで6案の現時点の採否と理由へ更新 |
| `legacy/bootstrap-draft-0.1/07_LESSONS.md` | docs/LESSONS.mdへ統合。新しい配置/管理UIの教訓を追加 |
| `legacy/bootstrap-draft-0.1/08_SOURCES.json` | references/SOURCES.jsonへ移行。元の確認日を保持 |
| `legacy/bootstrap-draft-0.1/09_WORK_ORDER_TEMPLATE.md` | docs/WORK_ORDER_TEMPLATE.mdへ移行・基準SHA方式へ更新 |
| `legacy/bootstrap-draft-0.1/10_PROJECT_INSTRUCTIONS.md` | HTML S07の現行入口へ統合 |
| `legacy/bootstrap-draft-0.1/AGENTS.md` | ルートAGENTS.mdの短い入口へ統合。旧指示は残さない |
| `legacy/bootstrap-draft-0.1/BUILD.md` | docs/BUILD.mdに現行生成/検査手順を更新 |
| `legacy/bootstrap-draft-0.1/manifest.json` | 旧配布固有の証拠。PCのC1 ZIPだけへ保持。現在目録は本書/現行tree |
| `legacy/bootstrap-draft-0.1/manifest.sha256` | 旧配布固有のハッシュ。PCのC1 ZIPのみ |
| `legacy/bootstrap-draft-0.1/references/Program_Guide_FractalJP_Settings.pdf` | references/の同名ファイルへ未改変移動（使用目的は上の契約） |
| `legacy/bootstrap-draft-0.1/references/Program_Guide_FractalJP_Settings.tex` | references/の同名ファイルへ未改変移動 |
| `legacy/bootstrap-draft-0.1/reports/local_checks.json` | 旧版検査の全ログはPCのみ。今に効く限界はLESSONS/REFERENCE_LOGへ受入 |
| `legacy/bootstrap-draft-0.1/tests/test_bundle.py` | 旧スナップショット専用実装はPCのみ。現行契約の試験をtests/test_state.pyへ実装 |
| `legacy/bootstrap-draft-0.1/tools/build_docs.py` | tools/build_docs.pyへ移してパス/生成先を現行化 |
| `legacy/bootstrap-draft-0.1/tools/template.tex` | tools/template.texへ移して表紙/版/正本表示を更新 |
| `legacy/bootstrap-draft-0.1/tools/verify_bundle.py` | 旧固定manifest専用検査はPCのみ。現行検査をtools/check_state.pyへ実装 |
| `legacy/delivery-checks-0.1.json` | 旧配布の個別証拠はPCのみ。受領確認と混同しない規則をLESSONSへ |

## 4. ファイル追加と終了時の更新

新しいファイルは、既存の役割へ収まらない理由・目的・編集元・更新契機・検査・保持方針をまず定義してから追加する。目的のない過去のコピー・版別副本は追加しない。文書の配置を変えたら開始案内・リンク・生成器・検査を同じ変更で整合する。

毎回、現行重点や判断が変わったらPROJECT_CONTEXTと担当文書を更新し、参照した範囲・理由・不足をREFERENCE_LOGへ戻す。現行ファイルに反映された記録を維持し、「詳細は消えた会話を参照」としない。

## 5. 内容の構造・焦点・版の登録

ファイル一覧は所在の地図であり、内容の論理構造は各資料の目次/役割索引、点検範囲はCONTENT_HEALTHが担う。HTMLは大項目/小項目をIDで登録し、親を既定、必要な子を上書きする。他文書は初回は文書単位で始め、具体的な論理枝の追加時に範囲を細分化する。どの程度の粒度が適切かも点検対象である。

最終更新は内容を変えた時点、最終確認は役割と依存への整合を実際にレビューした時点。両者が同じとは限らない。既存の未改変資料は0.3等の基準印を保持し、今回の科学的再確認済みとはしない。レジストリの初回未確認と期限を参照する。

現在の焦点はCONTEXT第1節、点検範囲はCONTENT_HEALTHで確認し、本マップに一時的な停止位置を重複記入しない。依頼が変わったら具体的な対象を追加し、期限切れは焦点外でも選ぶ。既存・後続の構造/理論/コマンド文書にはDOCUMENT_CONTROLのDC-FRACTALに従い、役割と依存を理解できる索引を持たせる。

### 資料の要求と情報の移管先（準備時から継承する契約）

RPT-036では、検討・テスト中のガイド本文執筆ではなく、本実装時の執筆に備えて要求と材料の所在を整理するよう求められた。以下は当時の準備索引を保持する。0.20ではD-154の本体着手に伴い、ここに定めた初回範囲を三資料・API索引へ具体化した。将来の未実装モデルまで確定するものではない。進捗はHTML、採否はDECISIONS、必要作業はBACKLOGへ戻す。PLAN第3章の方針どおり空の将来文書は作らず、最初の本体機能を実装する作業依頼で必要な資料範囲を同じ変更単位に含める。D-127の「生まれた時から管理」を適用し、完成後にまとめて説明を付ける運用にしない。

| 担当資料 | 執筆・改訂に必要な内容と根拠 | 着手・受入で閉じる範囲 |
|---|---|---|
| 理論ガイド | モデル目的/ID、変数と単位、座標/高さ/時間、支配式と導出、閉じる関係式、仮定/無視する効果、パラメータ出典、適用域/極限、必要入力、数値解法、実装/試験対応。要件はPLAN 5.3とDC-NARRATIVE-BASE。材料はENVの補間・JRA圧力・モデル構成、WEATHERの場の再構成、D-139/148/151、各adapterと試験 | 最初の力/速度評価や数値処理の実装から該当範囲を書き、式とコードと独立期待値を照合する。内外等温・比較可能な単純経路を保ち、未採用係数や未検証精度を事実にしない |
| プログラム構造ガイド | 全体の流れと公開境界から、枝の役割/存在理由・入出力・内部構造・横の連携・依存/影響・目的別逆引きへ進む。モジュール/主要機能/API/設定/変換/試験のID・所在・理論/単位/仮定・導入/変更/確認時点・現役性を結ぶ。要件はDC-ASSET、PLAN 5.2/10.1。材料はENVのAPI/ライフサイクル、CONTINUITY assets、現コードと対応試験 | 最初の本体モジュール導入と同時にT-007の具体索引を実装する。実在パス/公開symbol/署名の照合と、責務の重複・欠落・依存方向のレビューを分ける。全小関数へ均一な長文台帳を作らない |
| コマンド一覧・操作説明 | CMD-ID、目的、前提/環境/実行場所、入力/副作用、原文、出力/期待、停止/失敗/再開、確認版、代表フロー。要件はD-117、DC-ENV、DC-PROCEDURE。材料はBUILDの通常検査・生成・固定fixture操作とHTMLの該当CMD-ID/実施記録 | 本体CLIの採用時から成功と失敗/再開を実測する。現在コマンドと過去操作を区別し、BUILDの環境仕様やHTMLの実績を二重管理しない。構成器の宣言表示を軌道計算CLIと呼ばない |
| 契約・入力・再現情報 | 設定/出力schema、気象run/valid/取得時刻/範囲/量/hash、地形版、コード/依存、solver/許容差、警告/終了理由。要件はPLAN 3/4.2/11。編集元はENV、WEATHER、SOURCES、fixture manifest/原bundle、CODE/TEST | 一般adapter・入出力・solverの実装時に要求→判断/モデル→symbol→test→run/dataを結ぶ。幾何高度とgpm、モデル地表とDEM、取得成功と全飛行支持を混同しない |

各ガイドはDC-FRACTALに従い、問い・前提・根拠を結ぶ説明・結論/限界を適切な大きさで繰り返し、子の結論を上位の問いへ戻す。本文執筆開始時からCONTINUITYの `document_designs` / `narrative_units` に主張・必要内容・寄与・順序の理由・未説明範囲を登録する。役割索引は短い参照であり本文の複写にしない。レビューでは設計図にあるのに本文にない内容と、本文にあるのに意図不明な内容を双方点検する。

理論/構造ガイドの編集元はPLAN 3.2/5.4に従うTeXとし、PDF・検索用テキスト・図の編集元/生成スクリプト・参考文献・パッケージ/フォント名/入手方法・ビルドコマンドを結ぶ。PDFの目次/しおり/リンク/安定ID・対象コード版・ビルドIDを確認し、再生成後に数式・図表・改ページを視認する。既存Windows環境とPLAN用生成器の説明はBUILDへあるが、0.20で新ガイドの直接TeX生成経路と主要APIの実在署名索引を導入した。CI/別環境の再現と将来拡張はT-007/T-012に残す。参考Program_Guideは説明形式の例であり、その実装や科学内容を採用済みとしない。

この準備で本文の科学審査、参考PDF/TeXの表示確認、親PLAN残部の未確認が解消したとは扱わない。資料の追加時には必要な役割・移管元・更新契機を定め、DC-CLOSEに従ってコード/索引/理論対応/説明/試験/生成物と確認範囲を同じ変更で受け入れる。

## 6. 情報の依存関係（復旧の必読範囲）

この節は現在の依存の読み方を示し、文書全体MAPの点検範囲に属する。

**矢印は一律の「先に全部実行」を意味しない。** 入口の探索順と、意味の根拠、派生物の生成、操作の前提、内容点検の依存は別である。親子の分類も前提条件とは異なる。

| 種類 | 関係・方向 | なぜ必要か / 変更時の扱い |
|---|---|---|
| 読取経路 | 外部の安定指示 → README R0〜R5 → CONTEXT/HISTORY → 本マップ/点検範囲 → 必要本文 | どこを読むかの案内。リンクが循環すること自体を科学モデルの循環依存と解釈しない |
| 意味の根拠 | CONTEXTの要求/採用判断 → PLANの将来構想 → BACKLOGの作業 → HTMLの実施/結果 | 作業の方向と理由を復元する。新しい本文やコードというだけで要求を上書きしない |
| 判断・制約 | UNCERTAINTIES + DECISIONS + LESSONS → 採用・実装の判断 | 未決/提案/観測事実を区別する。参照例や旧公開repoの存在は実装受入ではない |
| 作業前提 | T-003 → T-006 → T-005、およびT-006 → T-011 → T-010 | 体制確立、必要範囲の決定、データ受入、観測設計、高度化選定の関係。個別の前提集合はBACKLOGが正本 |
| 初回運用の前提 | U02の手順保存 + S07の入口設定 → S08の新値作成/復旧 → S09の結果保存/退避 | Project設定の保存だけでは復旧の実証にならない。U01は過去のv0.4適用であり再マージしない |
| 生成関係 | PROJECT_PLAN.md + template.tex + build_docs.py → PROJECT_PLAN.tex → PROJECT_PLAN.pdf | PDFを独立編集しない。現行の一組と直近の生成/表示の実績はREFERENCE_LOGの現行欄から確認する。生成条件・再実行はBUILD、0.15時点の生成はACT-150、環境受入はGEN-120の履歴。気象仕様はWEATHER_DATA_GUIDE、未来の分析構想はSIMULATOR_VISIONとPLAN10.6へ結び、科学本文の未確認とT-012の残件を保持する |
| 点検依存 | CONTENT_HEALTH.units.depends_on の参照先 → 依存する範囲の再点検 | 内容変更時の確認を伝播するための関係。全データ/生成関係を網羅する依存グラフではない |
| 階層・部分更新 | parent → 子の論理範囲 | 親は子の本文を除く指紋、子は自身の範囲を管理する。兄弟や無関係な科学資料の確認まで拡張しない |

復旧で最低限読む計画の範囲は、既存MDの「この資料の位置づけ」、第9章、第10章。CONTENT_HEALTHはこれをPLAN-POSITION / PLAN-ROLES / PLAN-ROADMAPとして段落境界で管理する。PLAN残部・参考資料等の未確認と初回期限は保持する。**計画の方向を読んだことを、未読の科学・出典・生成系の再検証済みという扱いにしない。**

復旧で必ず説明する観点はCONTENT_HEALTHのrecovery_contract.required_outcomesに登録し、README R4とHTML S08-3に同じIDを示す。表示は短い説明、詳細な手順と評価は担当本文が編集元。検査器は観点ID・参照先・本文見出し・操作欄の欠落を拒否するが、説明の意味的妥当性を自動判定しない。

## 7. 現在の環境操作の依存と境界

RPT-007→ENV-P01承認と実測値→E02の具体化案。共有LF契約は.gitattributes、実装はprepare_workspace.py、初回の呼出しはHTML E02、試験はtest_workspace.py。E02-1の統合M080→E02-2でlocalを同じSHAへFF→作業バイトをHEADへ一致→E02-3専用環境→E02-4検査、という環境構築時点の依存である。訂正後の最小実行はF01/RPT-010で受理済み。これを現在の再実行指示やモデル・気象源の採用前提と取り違えない。旧スレッドのT-006保留は解除されており、現在の目的と前提はCONTEXT第1節とBACKLOGを参照する。

<!-- LOGIC:TOOLS-LOGIC:BEGIN -->


## 8. 管理ツールの構造 — なぜ別の道具として残すのか

検査を通すこと自体ではなく、「次の判断の根拠を失わず、ユーザーの作業を壊さない」ことが上位目的である。同期・検査・証拠保存・文書生成を別にするのは、副作用と保証範囲が違うためである。

<!-- LOGIC:TOOL-WORKTREE:BEGIN -->
### 8.1 まず、何を検査する作業ツリーなのか

`prepare_workspace.py`は環境を作る道具でも文書内容の審査でもない。inspectは版と編集状態を読む。syncは明示したリモートSHAに限り取得し、cleanなmainが祖先ならfast-forwardする。normalizeは全体がHEADに対するCRLF差だけかを事前検査し、明示承認後の対象だけを置換する。verifyはHEADとの全バイト一致を要求する。

この細分化により、同期成功でも改行差が残る場合を表せる。非fast-forward・編集・未追跡・属性異常で止まるのは失敗ではなく保全条件である。`test_workspace.py`は一時Git repoでこの保全とHTMLの呼出引数を試す。問題が直っても削除しない理由は、将来の呼出変更で同じ事故が起こり得るためである。
<!-- LOGIC:TOOL-WORKTREE:END -->
<!-- LOGIC:TOOL-CHECKS:BEGIN -->
### 8.2 その内容について、何を検査できるのか

`check_state.py`は現行パス、本文状態、リンク、PDFとTeXの同伴、課題参照を調べる。新しい`check_contract.py`をここから呼び、全実体の必要性・寿命、タスクDAG、論証単位、役割表の一致も調べる。`check_health.py`は時点・範囲・更新/確認・依存指紋・期限を調べる。意味を削った編集を単に指紋再登録で受け入れないため、基準との内容変更はcheck_contract --baseの理由記録も見る。

各testsファイルは対応する検査器の正常・異常ケースを持つ。`test_state.py`は表示/所在、`test_health.py`は時点/範囲、`test_contract.py`は必要性/論証/変更理由を守る。検査の穴を塞いでも、その検査を退役させる理由にはならない。一方、守る要件を正式に廃止したときは、期待値だけ温存せず退役理由を残す。
共通入口ENTRY-01とHTMLの現行コピー、README/AGENTSの互換性記録をcheck_contractで照合する。ただし外部Project設定は自動取得せず、原文と実際の適用は別観測である。S08の固定試験文は歴史として残す。明示した--transitionでは空/不在/不完全な基準を拒否し、比較成立までを成功条件にする。prepare_workspace/run_checks/build_docsもコード変更監視の対象であり、保全条件の変更を見逃さない。
<!-- LOGIC:TOOL-CHECKS:END -->
<!-- LOGIC:TOOL-EVIDENCE:BEGIN -->
### 8.3 結果を後から判断できるようにするには

`run_checks.py`は専用prefixを確認してpre/state/health/tests/postを実行し、repo外の毎回新しいフォルダーへ環境JSON、stdout/stderr、summaryを保存する。途中失敗で通常の後続を止めてもpostを試みる。`test_check_run.py`は失敗時post・原出力・repo外保存・skipの扱いを守る。

保存先のログは証拠であり現在ソースではない。実行条件を満たさない生ログも原因調査用に保持する。再生成には同じSHAと環境が必要で、過去の実測という事実は再試験で置換できない。RPT-010/CHK-010はM081・91件全成功を受理した記録で、新しい検査器を実測済みにはしない。後続の実行は対象SHA・環境・結果を別の観測として記録する。

P1では同じ「後から入力と出力を検証できる」目的に`inspect_gfs_fixture.py`を加える。固定したNOMADSの3 GRIB2と取得manifestを読み、SHA/単位/層/走査/時刻/欠測をecCodesで検査し、repo外へmetadata CSVと検査JSONを保存する。管理文書の検査とは依存も対象も異なるため、run_checksの成功へ合算しない。この固定GFS経路では3 GRIB2が数値入力、manifestは取得来歴と期待構造の編集元、検査器はその整合の実行手段であり、役割が既存の原Excelや文書生成器では満たせないため5パスを追加した（D-134）。

以下は0.13/0.14に追加した道具の役割と当時の受入範囲である。現在の本体の高さ/地表/全飛行仕様はENVの現行節へ戻り、この旧時点の未受入表示を現在へ再適用しない。

処理の順はGRIB受入→地下気圧面の除外・高さ基準を明示した正規化→補間契約→モデルとソルバ→比較評価。0.13で受け入れたのは先頭の復号検査までであり、有限値を科学的に正しい入力と認定しない。0.14候補では地下mask・品質・支持範囲・geopotential height限定の問い合わせを実装と合成試験へ結ぶ。幾何高度と地表の対応は未受入で、S14-3を部分完了としてS14-4の比較へ渡す条件を限定する。検査器とfixtureはT-005受入時に後継の回帰との関係を見直し、参照根拠を失う削除や版別コピーを増やさない。再実行はBUILD、取得の限界はmanifest、実績はACT-130に戻す。
<!-- LOGIC:TOOL-EVIDENCE:END -->
<!-- LOGIC:TOOL-BUILD:BEGIN -->
環境候補の説明原本は[ENVIRONMENT_CONTRACT](docs/ENVIRONMENT_CONTRACT.md)。0.14で追加したGFS正規化器は既存inspect_gfs_fixtureの入力検査と固定標本に依存し、値・品質・来歴を問い合わせへ渡す。test_environmentは既知合成場と実標本で契約を検査する。主要機能・式・単位・使用先・導入0.14.0・現役性と一般adapter受入時の次判定は同契約へ集約し、索引を第二の仕様にしない。

0.18では保存JRAモデル面のqueryとモデル構成の依存検査を加えた。両API、入力の役割/寿命、共通高さや力学などの未受入範囲はENVIRONMENT_CONTRACTの0.18節、再現はBUILDとACT-180へ戻す。

### 8.4 読む文書をどう再生成するのか

`build_docs.py`と`template.tex`は計画MDから人向けのTeX/PDFを作る。提供参考PDF/TeXはこのビルドの対象ではない。Pandoc/XeLaTeX/フォント/TeX依存が必要で、0.12.0では専用Windows環境での生成と全17ページの表示を確認した。取得元・版・依存の観測と再生成手順はBUILD、証拠はGEN-120に残す。WindowsでもLFを出力するためPandocに`--eol=lf`を指定する。別OS・全依存の固定・CIの受入はT-012に残る。

現行生成器はTeXを先に書き、後のPDF生成で失敗すると対が不一致になり得る。したがって現状は作業コピーだけで使用する条件付きの道具である。無用な残骸として消さず、生成経路を受け入れた後に改善/代替を判断する。詳しい環境と実行手順はBUILD、出力を公開する判断はDC-CLOSEへ渡す。
<!-- LOGIC:TOOL-BUILD:END -->

**全体へ戻る結論：** この道具群は版・契約・証拠・表示を結ぶ管理基盤と、P1の気象入力受入を担う。0.20ではballoon_simが実気象の連続場と飛行モデル/幾何高度/粗い地表をつなぐ。旧道具は固有の入力回帰/設計根拠として保持し、本体と同じ機能を二重の現役入口として案内しない。必要な部分だけを使い、寿命と未確認を知ったうえで変更する。
<!-- LOGIC:TOOLS-LOGIC:END -->

## 版を経た安定性の点検先

以下は各版での構造変更の経緯であり、現在の比較基準はHTML start/REFERENCE_LOGに従う。M130は当時44パス/28論証単位。0.14候補はD-135に基づく環境契約・実装・試験の3パスを追加して47パスとし、28論証IDを維持する。0.13.0で再検査可能な気象入力3件・取得manifest・検査器の5パスをD-134の理由で追加した。0.9.2の36パスから、0.10.0候補で原本3冊を用途とともに加えた。通常の進捗更新はこの構造を作り直す理由にしない。前後比較の編集元はCONTINUITY_CONTRACTのstructural_changes、規則はDC-STABILITY、実行は既存check_contract.py。自身の本文変更と祖先への影響を分けて出力する。過去の合格件数を将来コードへ転用せず、比較元の全宣言パス/バイト指紋と実Gitの同定を組にする。
