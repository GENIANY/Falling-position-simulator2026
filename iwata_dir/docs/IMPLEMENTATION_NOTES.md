---
document_id: BJP-IMPLEMENTATION-NOTES
revision: 0.58.0
as_of: 2026-10-02
role: 本体の実装仕様・設計上の注意
---

[更新:0.59.0] [確認:0.59.0] — IMPLEMENTATION-NOTES / REV-590-CONTENT-IMPLEMENTATION-NOTES

<!-- LOGIC:IMPLEMENTATION-NOTES:BEGIN -->
# 実装ノート

**0.58候補の改訂範囲。** 比較元は保存済み0.57 C2 `b1b66dbff8b84bb6bb0332ec98043cc8990071b3`。原標本の年間48区分、全高度の年間値の再利用、選択面の図と風配の再計算、面操作行の責務を該当節へ反映する。旧半月/月/季節、月の二つの中央値とp10–p90、固定要求と保存参照の意味は変更しない。この記述は差分の契約読解であり、速度・実UI・旧科学核の再受入を先取りしない。

**0.57候補の改訂範囲。** 元格子・元UTC時刻のu/vを保存した資料から、半月中央値と月全体の経験分位を同じ母集団で求める。提供10年DBとJRA-3Q/ERA5の原標本sourceを分け、資料ごとの年・面・重み・静穏・高度の支持を保持する。地点選択追補では、原標本の任意元格子風配、草案を保つ要求順序、旧保存とSVGの地点来歴を該当節のsourceへ照合した。今回の確認印は、比較元0.56 C2 `98b6dad115e4ac30c03f06ff3366fc6468022b8a`からのこの実装・画面契約の読解に限る。取得の完了、実データの数値照合、画面操作と図保存の実績はS36の対応工程で別に判定する。旧科学核や全UIを再受入れした印ではない。

**0.56候補の改訂範囲。** 既存の半月queryと保存artifactを保ち、月/季節の件数重み付き再集計・時刻subset・実風配を接続する。新規科学モデルや原日時共同場の復元ではない。以下の統計契約は現backendと応答例に照合し、画面/保存の有限受入と最終確認は[S36](../BOOTSTRAP_RUNBOOK.html#s36-climate-expansion-plan)へ集約する。

**0.55候補の改訂範囲。** 固定要求の永続化・保存先の同一性・完成結果の回復、原日時集合から共通計算/画面への接続を扱う。0.54のGET監視・地表照会・一覧観測と表示復元を継承する。既存GUI・保存JRA/GFS・飛行核・半月統計の責務を継承する。コードの有限反例と実画面の受入は分け、確認範囲・費用・未確認は[S36](../BOOTSTRAP_RUNBOOK.html#s36-plan550)へ集約する。

**0.55での確認の境界。** 比較元0.54 C2 `cc7b0fd0463a69ad495debb7f03f1b3eb734e0e6`に対する受付/保存寿命・原日時集合の変更接点を実装と照合し、旧一飛行・再構成・統計の記述を保持した。今回の確認印はこの読解に対応し、旧科学式、全API、Google写真3Dを一括して再受け入れする印ではない。

0.53では保存JRAの登録・実効来歴・秒入力・固定結果との照合、既存GUIの3便と同じ固定入力のCLI全結果・来歴一致、親子比較、合成領域の詳細、保存・再起動後の復元を限定確認した。その実績は全UIや科学精度の全面受入ではなく、今回の通信回復の確認とも区別する。

0.52の確認範囲は、保存schemaの選択、JRA地上再構成と品質/来歴、既存飛行・出力との接点、および今回の案内差分である。旧UI・GFS・科学モデル全体を再受け入れした印ではない。

この資料は、構造ガイドで実装の場所を見つけた後に読む詳細仕様である。構造把握は [PROGRAM_GUIDE.pdf](PROGRAM_GUIDE.pdf)、式の導出と仮定は [THEORY_GUIDE.pdf](THEORY_GUIDE.pdf)、具体的な操作は [COMMANDS.md](COMMANDS.md) を使う。取得元・製品・APIの外部仕様は [WEATHER_DATA_GUIDE.md](WEATHER_DATA_GUIDE.md)、将来の組合せと入力契約は [ENVIRONMENT_CONTRACT.md](ENVIRONMENT_CONTRACT.md) に戻る。

本体は0.20.0で導入し、0.24.0で責務を実パッケージへ分けた。比較元は固定C2-230 `c1623997d4d8142f9e34ebf496e4be5d9c442bf6`。`environment`が製品/保存/場、`flight`が設定/物理/イベント/数値/進行、`results`が表示と保存を担当する。旧`weather.py`・`dynamics.py`とCLIの既存公開名は再exportで維持し、以下の従来APIの呼び方を変えない。実定義の所在はIMPLEMENTATION_INDEXの`path/symbol`、互換経路は`public_path/public_symbol`へ分けた。

0.24の数値移行（D-163）ではSciPyのRK45とbrentqを実行依存にした。保存場の読取は標準ライブラリ、復号はecCodes/NumPy、飛行はSciPy/NumPyを必要とする。詳細な版確認はCOMMANDS/BUILDへ戻す。

取得を終えた保存物から場を構成し、その場で飛行し、最後に結果を保存する。積分の途中からネットワークへ出ないことは、異なる予報runの混入や通信障害と物理停止の混同を避ける設計上の境界である。地域は入力で指定し、北海道専用／和歌山専用の分岐を本体に置かない。

## 画面を統合し、草案・仕事・固定結果へ接続する

0.45で `frontend/` と `backend/` をprivate正本へ追加した。0.46は0.45 C2 `ce6a29accfad6865beca0b2dfe4f414e2bafb81a` を比較元に、0.40.1 r2で育てた用途別画面を現役ソースへ取り込み、共通基盤と入力・保存・実結果の接点を改修した。0.47の予報取得と各条件n=1を保ち、0.48では同じ固定場に対する一変量の仮定感度MCを加える。一飛行の式・設定・結果schemaを変えず、その周囲へ標本・集合実行・集計の責務を置く。画面確認用の人工分散・人工風と実計算を別の名前空間で扱う。0.49では提供されたJRA-3Q半月集計を既存の年間・地域図へ接続する。0.49時点では気象誤差分布の同定、過去瞬時場による飛行照合、実風に基づく長期計画は未了だった。0.55では明示した原日時の有限比較を接続するが、季節母集団の代表抽出や校正済み予測は未了である。実装仕様と試験・Windows実操作の受入は別であり、現在の到達点はS36、0.46の履歴はS35へ戻す。

### HTTPから核へ降りる境界

`backend.app.create_app(data_dir=None)` はFastAPIの経路・JSON要求・応答と、serviceの起動/終了を担当する。`contracts.py` は要求の外枠、`application.ApplicationService` は入力固定、仕事、草案と結果の保存を担う。物理条件は既存 `flight.config.validate_config` が検証し既定値を展開する。HTTPが式を複写したり、場の不足を標準大気へ埋めたりしない。

APIは `/api/v1` 以下で、POST/PUTは `application/json` を要求する。未定義APIは404のまま、画面HTMLへfallbackしない。loopbackで一人が使うローカルサービスであり、認証・公開マルチユーザーの配備契約ではない。

|HTTP|入力・出力と副作用|
|---|---|
|GET `/health`|service版、worker数、待機上限、台帳のinstance_id、飛行実行器のflight_execution。飛行や保存場の科学的受入を表さない。|
|GET `/weather-sources`|保存fixtureと完成取得資産のID、hash/size、schema/product、製品ごとの時刻・範囲・鉛直識別、入力例とsourceエラー。GFSのrun/validとJRAの解析有効UTCを区別する。取得資産はdefault_configを持たず、任意の利用者path/URLを受けない。|
|GET `/weather-sources/{id}/ground`|期待するsource SHA、UTC、緯度経度、放球ASLを受け、その保存場のモデル地表と高度差を返す。入力の変更やrun生成はしない。詳細は下のモデル地表照会へ。|
|POST `/runs`|client_request_id、candidate_id/revision、label、weather_source_id、configを固定し、202でrun_id/job_id/state/hashを返す。|
|GET `/runs`、`/runs/{id}`|仕事の一覧/詳細。後者は固定specと開始/終了時刻も返す。再送や再計算を起こさない。|
|GET `/run-requests?client_request_id=...`|固定要求IDからrun/specを照合する。404は今回の観測時点で未登録という意味で、再送・再計算しない。|
|GET `/runs/{id}/result`|指紋を照合した固定結果とrun/trial ID、n=1、weight=1、場/コード来歴。未公開結果は409。|
|POST `/runs/{id}/cancel`|空JSON `{}` を送る。待機中だけ取消し、実行中は409。|
|GET `/project`、PUT `/project`|草案と比較run参照。PUTはexpected_revisionを照合し、旧版からの保存は409。計算を起動しない。|

同じclient_request_idと同じ要求を再送したときは同じrunへ戻し、同じIDに違う入力なら409とする。serviceは1件を別processで実行し、最大4件を待機させる。queue満杯は429で新runを作らない。workerの `execute_run(spec, weather_path, config_path, staging_path)` は入力・コード・数値環境を前後で照合し、保存場をloadしてsimulate/export_resultを呼ぶ。計算中の新規取得はなく、大きい軌道配列をprocess queueで返さない。

job状態は queued/running/completed/failed/cancelled/interrupted。`completed` は照合済み結果を保存した意味で、物理的に `stopped` の結果も含む。着地はresultの `complete` と `summary.landing` で読み、`landing:null` の最終有効点を着地点へ変えない。記録点ゼロの停止もあり得る。正常終了は実行中workerを待つ。再起動では下記の完成物照合・回復を先に行い、なお未完了の仕事をinterruptedへ移す。ブラウザ再読は `/runs` から状態を復元してpollし、新規要求を自動再送しない。実行中の即時取消は実装していない。

### 受付不明を、別の計算へ変えずに回復する（0.55）

`submissionLedger.ts` は送信前のID・完全本文と接続先instanceをlocalStorageへ固定する。`singleSubmission.ts` が親/延期列の行ごとの未送信・不明・受付・終了を管理し、`useWorkspace` が一件ずつ進める。`recordedMutation.ts` は集合等の同一要求の再送、`api.writeRequest` は60秒deadlineを担う。HTTPの自動再POSTは行わない。草案・結果・outboxは別の寿命であり、ブラウザ再読後は読み取りと明示再開へ戻す。localStorageが書けなければ最初のPOSTも送らない。

`GET /run-requests?client_request_id=...` は未確定な単便の照合専用で、該当なしは404。再計算しない。`GET /runs/{id}` のspecには送信した完全入力も残る。PUT projectの不明応答は送信前revisionと固定本文を現在保存と照合し、同版/同内容・未適用・競合を区別する。後続の編集は勝手に捨てない。 `projectSaveSignature` はHTTP JSONで省略されるundefinedと、Project/Candidate/EnsembleResultRefの明示既定項目だけを揃える。物理config・原日時・固定結果参照・ui_state内部の実値やnull差を同一化せず、再送する固定要求本文も変更しない。

保存先の `registry.sqlite3` に永続する不透明なinstance UUIDを `GET /health` で返す。新UIの送信はこのIDに束縛され、header照合によってhealth観測後の接続先切替も拒否する。headerなしの既存API利用は互換を残すため、同じ保証を無条件に主張しない。別instance/未束縛/破損outboxは自動移植せず保持する。独立に初期化した台帳は別IDだが、同じregistryの複製は同IDを保つ。UUIDは認証やpath識別ではなく、複製・巻戻しの検出を保証しない。既存の識別行が欠落・破損していれば起動を拒否し、黙って新IDを生成しない。

`writeLease.ts` はWeb Locksの同origin exclusive lockで送信担当を一つにする。0.55修復の起動取得は `ifAvailable` に限り、明示した取得クリックだけが `BroadcastChannel` で既存担当へ協調引継ぎを要求する。協調メッセージは権利そのものではなく、実Web Lock取得までrequesterはreaderのままである。処理中の担当は中断・強奪せず、外側のAPI受付と要求台帳更新が終わるまでoperation scopeを保持する。busy返信で今回の取得を終了し、処理完了後の再クリックを求める。画面破棄時も進行中operationの解放を待ち、台帳更新の途中でlockを落とさない。通信の終了だけでbusyを解除して台帳更新を旧readerへ残さない。8秒無応答の旧版/休止タブ等には理由を返し、自動強制取得はしない。切替えで表示・草案・キー/既存接続を作り直さず、不明な要求の自動再送も行わない。

共通の `api.request` はGET/HEAD/OPTIONS以外で送信権と確認済みinstanceをfetch前に検査し、writeのinstance headerを呼出元より後に固定する。`submissionLedger` のput/removeも権利を確認し、readerからHTTP書込みや共有台帳更新を始めない。`writeRequest` の60秒期限と `climateApi.create` の既存Abort・同画面内IDは別の責務で、風統計へ永続outboxを追加したものではない。readerの固定結果GET・地図・接続済み3Dは保持し、family観測でも共有要求台帳を更新しない。Web Locks未対応時は送信を止める。別origin・別ブラウザ・CLIまでの排他制御ではない。実装・反例・実UIの適用状態はS36の今回修復へ戻し、契約の追記だけで成功としない。

worker異常でpoolを使えなくなった場合は投入を止め、未投入・待機中を保つ。healthの `flight_execution` が利用不可と再起動要求を返す。新受付は503、既に受理した同一要求の読戻しや固定結果GETは独立する。再起動後の未完了を自動再実行しない。完成directoryとCOMMITTEDがあるのにDBが未反映なら、固定spec、外側manifest、核のmanifestと全8成果物を照合して完成結果を再登録する。`run_recoveries` は旧state/errorと再計算なしを保存し、その終了時刻は回復記録時刻である。元の純計算所要時間へ読み替えない。

### 保存済み結果と、編集できる草案

保存先はrepo外で、Windowsの既定は `%LOCALAPPDATA%/BalloonSimulator/state`、他OSでは `~/.local/share/BalloonSimulator/state`。`BALLOON_DATA_DIR` またはservice引数で切り替える。一保存先を同時に二serviceが所有しないようlockし、稼働中のDB/ファイルを手で変更しない。

SQLiteには草案revision、固定run仕様、可変job状態と結果参照を置く。固定入力は `specs/<run_id>/run.json` とconfigにも保存する。workerが新規stagingへ作った核の7出力を `storage.publish_result` が名前/size/hashと固定configで照合し、run.jsonとCOMMITTED.jsonを加えてresultsへrenameした後、DBに参照を記録する。directoryがあるだけを完了にはしない。途中失敗のstagingは診断用に残し、再利用しない。

`storage.read_result` はDBに記録したCOMMITTEDのhash、run ID、内容ファイルのsize/hashを照合する。読む際に保存気象を再loadしないため、原場が失われても確定した結果を閲覧できる。ただし再計算可能なことや別PCへの移送完了を保証しない。電源断・全Windows障害・複数PCでの安全をこの構成だけで受入済みにしない。

projectは `balloon.project/1`、候補の草案と `compare_run_ids`、任意の `ui_state` を持つ。0.45の最大2候補/2結果は初回試験の制限だったため解除した。比較IDは重複を許さず、completedかつ固定結果を持つrunだけを受け入れる。未完了runの指定は409 COMPARISON_RESULT_NOT_READY、存在しないrunは404で拒否する。結果参照を変えても古いrunは変わらず、草案に不完全な入力を残すことと実行可能な入力の受理を分ける。科学的な比較条件が揃うかは入力差・場・モデルを読んで判断し、複数のIDがあるだけで統制比較としない。結果の削除APIやprojectの可搬import/exportは今回ない。

候補の任意の `parent_id` と `delay_minutes` は、親候補と延期差分の関係を記録する。両方を持つか両方を省き、親の実在・循環なし・有限の非負遅延をserviceが検査する。これだけでは物理入力が「時刻だけ異なる」と保証しない。画面が子の完全なconfigを具体化し、親と子の草案を一つのproject更新へまとめる。以前の固定runはそのときの入力を保持する。

`ui_state` は画面の文脈を保持する有限JSONで、旧projectでは空辞書として読める。画面側のschemaと `forecast_real` / `forecast_fixture` / `weather_real` / `weather_fixture` / `season_fixture` / `season_real` を区別し、選択・比較群・領域・視点を扱う。共通の打上げcontrollerでは `routeDisplay` に軌道と幕の表示選択も保持する。APIキーや固定結果の複製を格納する場所にはしない。保存操作は計算を起動せず、版競合・非有限JSON・不正な親関係があれば以前の保存を残す。

### 画面の選択と、描画だけの処理

`App.tsx` は用途の切替と候補操作を共通基盤へ結び、`ConfigEditor.tsx` は現在核の直接入力を編集する。`useWorkspace.ts` が初期取得/送信/poll/保存、`workspaceState.ts` のreducerが草案・固定run・結果参照を更新する。表示結果の明示選択にepochを持たせ、遅れて届いた完了や読込が新しい選択を上書きしない。通常の再読で復帰した仕事は観察して結果一覧へ足し、保存済みの比較選択を替えない。例外は受付不明の原要求を明示照合した単便で、`recoveryCandidate` と草案の完全一致、対象候補の比較選択が空、選択epoch一致の場合だけ初期表示へ入れる。集合や別runの選択、送信後の編集を上書きしない。保存開始時の草案を捕捉するので、保存待ちの追加編集を保存済みへ偽装しない。API呼出は `api.ts` に集約する。

`screens/ForecastScreen.tsx` と `WeatherScreen.tsx` は、旧画面の具体的なDOM/CSS/表示処理を使う。Reactは画面hostと専用入力portalを所有し、`forecast/`・`weather/` のcontrollerはhost配下の表示を所有する。実計算側は `forecast/projection.ts` が固定結果を表示用へ渡し、controllerの操作意図をAppへ返す。人工生成器が実結果の欠測や未接続を埋める経路にはしない。`lifecycle.ts` は画面のイベント・observer・timer等の寿命を管理する。これは既存画面の段階的統合であり、全controllerをReact部品に分割し終えた構造ではない。

0.55の単便送信は `singleSubmission.ts` と永続要求台帳を使う。受付確認後の新しい計算は新IDにし、応答不明なら完全入力と旧IDを保つ。INSTANCE_MISMATCHは4xxでも原要求を保留する。詳細は上の受付回復節へ戻る。旧SubmissionIntentsの画面内だけの記憶は現役経路ではない。非同期の完了は読込世代を照合し、run監視と表示選択の所有を分ける。

比較保存は草案と固定結果の参照を保存し、用途ごとの画面文脈を `ui_state` の各namespaceへ含める。人工気象から人工季節への新しい提案は `pendingProposal` として受け、既存候補に追加して消費する。単に用途へ戻る操作は既存の閲覧状態を復元する。季節候補ごとに出所と `source.returnState` を保ち、その候補を生んだ気象の条件へ戻る。これらの実操作の到達状態はS35へ記録し、項目がJSONにあるだけで画面の復元完了としない。

打上げ画面の地図・詳細履歴は、0.40.1 r2を素材とする `screens/forecast/` へ移す。0.45の `MapPanel.tsx` と `HistoryPanel.tsx` は移行比較用の旧部品で、現Appの主画面ではない。人工気象の四用途と実風統計の年間・地域図は `screens/weather/`、3Dの独立描画は `frontend/scene3d/` に置く。3D iframeは従来からのrenderer境界であり、用途別アプリ全体をiframeで囲ったものではない。Cesiumはnpm依存からbuild時に配布物を生成する。

移行でも守る表示契約は、元の不等間隔の経過時間、相の境界、固定した気象来歴、着地と支持停止の区別である。現主画面は `projection.ts` のsampleからcontrollerのhistoryAtへ原recordを渡し、表示カーソルを内挿する。東北変位・累積水平距離はそのrecordから局所平面換算で作る表示量であり、積分結果の再標本化やイベント再計算ではない。`domain.ts` のpointAtは保持した旧MapPanel/HistoryPanelの経路に残る。同時刻の上昇/下降2行を保持して相別に描き、不等間隔を行番号で揃えない。終了した結果は最後の有効点と表示し、まだ飛行中とは扱わない。時刻バーは経過時間の比較であり、異なる放球日時の同じUTC時刻を自動で揃える仕様ではない。n=1を50/90/95%の落下分散へ見せず、未接続の風統計を人工値で補わない。これらの接点はコード批評と実画面で個別に照合する。

### 3Dの地表投影と空中経路を同じ結果から描く（0.55）

`scene-document.js` の `includeElevatedRoutes` はKML向けの `allObjects` と独立した選択である。3Dへは概要の可視・注目候補、または詳細の選択群から既に作った相別経路だけを渡し、非表示候補やOFFにした分位帯を復活させない。`mean-route` は地表への投影、`flight-route` と `route-curtain` は同じ点列に高さmを持つ。核の記録や集計を再計算せず、経路の高さをkmからmへ戻す。集合の平均経路を、実在する一機の軌道に読み替えない。

受信契約は `bjp-scene3d-v2` のkind追加であり、地表線だけの旧payloadも受理する。`protocol.js` は立体点の有限値と経緯度範囲、実結果の `absolute`／人工結果の `relativeToGround`、同一candidate/result/phaseの地表線・空中線・幕の点数・順序・水平位置と空中線/幕の高さ一致を検査する。幕の `fillOpacity` は有限の0〜0.99に限り、静的描画で不透明alphaへ丸められる値を通さない。`routeDisplay` は `visible` と `curtain` のboolean二つで、旧payloadの省略時は両方trueとする。地表線と空中線は一つのスイッチに従い、幕は独立してOFFにできる。幕の幾何を削除して切り替える方式ではない。

親controllerが同じ `routeDisplay` を `snapshot`／`restore`、3D payload、KMLの初期visibilityへ接続する。KMLは従来どおり非表示候補も含む全対象を保持し、その初期表示に設定を反映する。`main.js` は通常の候補・表示更新で視点を保持し、「軌道全体を見る」は空中経路と地理的な範囲へ明示的に視点を移す。3Dの表示設定を保存することと、Googleのキー・接続や一時的に覚えた視点を保存することは別である。

実ASLの空中線は `route-geometry.js` で表示用楕円体高 `h = z_model_ASL + N_EGM96` にする。既存核の幾何ASLをEGM96基準として表示する規約であり、厳密な測量標高や地物との離隔精度を保証する変換ではない。`route-layer.js` がローカル同梱の約2 MBの格子を取得し、`vertical-datum.js` が符号を保って補間する。読込失敗時は0補正へ代替せず空中線の高度基準エラーを表示する。科学計算、固定結果、KMLのASL m／`absolute` は変更しない。人工の `relativeToGround` は取得した地物高に人工高さを加える模式AGLである。地物メッシュが返す高さは既に楕円体基準なので、人工上端へEGM96を二重加算しない。格子の来歴・形式・利用条件は [data/README](../frontend/scene3d/data/README.md) を編集元とする。

実ASLでは、地物高を取得できた区間だけ幕を作る方式から、全経路の上下関係を示す連続wallへ変更する。`routeSections` は相別経路の上端に対し、表示用下端の楕円体高mを `min(-12000, min(h_upper) - 1000)` とする。下端は地形の推定値ではなく、全上端より低い描画用の面である。不透明な写真メッシュの深度で地下の余長を隠し、下端線は描かない。地物が上端より高くても元の軌道を持ち上げたり、その区間だけ幕を削ったりしない。メッシュの穴・未読・非遮蔽部分では余長が見える場合があり、地表との正確な接合や衝突を保証しない。fit範囲は空中経路と地理的な範囲から作り、この地下下端を含めない。

`route-geometry.js` は上端線とwallに同じ表示節点を使う。空中polylineは `GEODESIC`、wallもgeodesic補間で、双方の `granularity` を揃える。分割が4096節点の上限を超えた実ASLでも、原節点の全経路へ戻して線と幕を残し、疎な原点間で上端の曲率が違う二方式を混在させない。`route-layer.js` は実ASLだけの経路ではGPU地物高照会を起動せず、旧「地物への接続」操作も実結果には出さない。これは経路描画の契約であり、hoverやクリックなど別用途の地物読取りまでゼロとする意味ではない。

人工AGLだけは、表示上端を求めるために現在の地物メッシュへ `sampleHeight` を照会する。全相の全分割節点に有限な地物高が揃うまでは空中線と幕を一括保留し、一部区間だけを完成した全経路として出さない。欠測を0で補わず、地表投影線は別に保持する。共有surface sessionで照会を直列化し、自作entityを除外する。一回は512照会またはGPU照会の累計1.2秒に達したところで区切り、cursorを保って次の更新を続きから行う。待ち時間を含む総所要時間の1.2秒保証や、単独GPU照会の途中取消ではない。視点移動中は照会を止め、静止・タイル更新・「人工AGLの高さを再確認」で調べ直す。長い経路では分割上限や未読メッシュにより全点が揃わず、空中線と幕の保留が続き得る。この人工AGLの制限と、実ASLの原節点fallbackを区別する。

経路描画は既存viewer／providerを使い、Google root接続を追加しない。通常の接続中タイル読込みまで「通信なし」とする契約ではない。元の気象モデル地形と写真地物との差を隠す補正は行わず、連続幕は全経路の上下関係を読むための表示として扱う。

追加の受信・選択契約は `scene3d-routes.test.ts`、表示用高度は `scene3d-datum.test.ts`、連続幕・原節点fallbackと人工AGLの待機は `scene3d-geometry.test.ts` の有限反例で確認する範囲である。連続幕版では全frontend試験と実写真上の全経路表示、切替、2D復帰、候補更新を確認した。観察対象と未確認の境界はS36の実装結果へ分けて記録した。旧方式の部分幕を実写真上で確認した記録はその版の観察として保持し、新方式の成功へ読み替えない。実績と未確認は[S36](../BOOTSTRAP_RUNBOOK.html#s36-plan550)へ戻す。

### 保存結果の読取り状態を、計算状態から分ける（0.50）

`fixedResultRead.ts`は`loading / missing / error / ready`、表示名、詳細待機の判定を共有する。`missing`はAPIの404応答、`error`はその他の読取り失敗であり、物理計算の失敗状態ではない。状態を持つのはn=1の`useWorkspace.resultReads`、集合の`useEnsembleWorkspace.caseReads`、風統計の`useClimateWorkspace.restoreRead`で、helper自身はHTTPや保存を行わない。

0.54の単便と気象取得は`jobObservation.ts`のGET監視を共有する。`api.ts`の`readRequest`はそのfacadeの各GETへ20秒の期限を設け、ヘッダーとJSON本文を含めて待ち、transportがabortを無視しても画面の待機を終了する。一般の`request`やPOST/PUTを自動再送する機能ではなく、集合/風統計の専用wrapperの期限は維持する。runの状態とresultを順に読む監視一巡は複数GETなので、一巡全体を20秒としない。

監視はIDごとに同時読取りを共有し、完了後に正常時0.9秒、失敗時1.8/3.6/7.2/14.4秒から最大15秒で次を予約する。最後に確定した状態と`lastConfirmedAt`、現在の観測不能を別に保持し、通信失敗をrunのfailedや物理停止へ上書きしない。計算終了後のresult読取失敗も別の未確認である。明示再確認も同じGETを使う。終端の失敗/取消/中断を計算再送で解消しない。読込世代の変更/画面終了は監視を破棄し、後着応答を採らない。復帰した全active runを観測することと、候補の最新run/表示結果を選ぶことは別であり、古い仕事の完了で新しいpendingや表示選択を取り消さない。

保存参照の再読は元IDをGETする。n=1の`reloadResult`は画面の生存/読込世代を照合し、reducerへ`intent:restore`で渡して表示対象を選び直さない。この経路に応答run/result IDの追加照合はない。集合の`loadCase`はsnapshot/case IDを照合し、風統計の`restoreSaved`は保存参照のanalysis/source/data/query/result識別を照合する。計画を読み直す/画面を終了する前の応答は世代で区別し、新しい選択や草案へ採用しない。風統計は草案queryの編集と固定artifactの採用世代を分け、編集中でも同じ保存図のGETを受け取れるが、新artifact採用後の旧GETは採用しない。読取り再試行はPOSTを再送しない。

`ForecastScreen`は固定結果が未読のタブへ読取り状態を渡す。草案が削除済みの保存結果は、結果本体が得られるまで候補への投影を待ち、初期画面を保存状態へ逆流させない。`forecast/controller`は未読詳細の選択ID・時刻を保持し、保存時刻を表示する。時間範囲が未読の間はsliderを隠して無効にし、結果到着後に元の範囲と時刻へ戻す。未読中の図保存も無効にする。草案差分のpendingと結果の読取状態は独立で、読取失敗を草案変更扱いにしない。`WeatherScreen`と`weather/controller`も未読の固定図を空の実データや人工値へ読み替えない。この保持は復元中の表示状態を守るもので、missingになった物理ファイルを修復する機構ではない。

地図視点は同じcontrollerが所有する。保存視点がない初回だけ固定結果の読取を待ってfitし、未確定の初期視点はsnapshotへ入れない。ユーザーのパン/ズーム/明示fitは初回fitを解除する。`restoreMapView`は同一の保存視点を繰り返し受信しても適用し直さず、表示状態の通知待ちに行われた新しいパンを巻き戻さない。新たに受信した保存視点は復元する。風速頻度と風配の本数軸は整数stepを共有し、零標本や着地後の母数の意味は変えない。

再読ボタン自身は固定結果GETを送るが、その後の表示で必要な未保存の選択群集計は別のPOSTになり得る。保存分析ID/keyが一致する選択群はgetAnalysisで再利用する。共有地図の干渉は保存済み着地点のIDと領域内判定から点として作り、概要・3D・KMLのためだけに干渉群の外周集計を要求しない。干渉群を詳細で選んだ場合の履歴・入力分布等は必要に応じて集計するため、全復元がGETだけになる保証ではない。

0.55修復では、全標本の選択に固定caseの分析を再利用する。 `screens/forecast/analysisLoadState.ts` が選択群の集計状態と明示retryを持ち、`controller.js` が表示要求を渡す。`historyLoadQueue.ts` は現在選択の原履歴GETを別の有限queueで扱う。個々の原履歴GETは派生集計の成否/送信権から独立させ、選択した履歴を追加集計待ちで空にしない。部分群の分析が未読/未作成でも全体分析へ置き換えず、対象群と読取/生成状態を保持する。待機・失敗・送信権待ちは持続する表示と明示retryへ接続する。owner取得で自動的に再開できるのはnever-sentのblocked派生分析だけであり、送信済みで受付不明のものは同じ要求の明示確認/再試行へ残す。表示のretry、派生分析の生成、飛行再計算は別の操作である。

<a id="IM-JRA-GUI"></a>
### 保存JRAを共通の候補・固定結果へ渡す接点（0.53候補）

0.51/0.52のCLI接続は下の各節へ残す。ここでは `references/flight_fixture/jra3q-weather.json.gz` と `examples/jra3q-ground-flight.json` の既存一窓を、`ApplicationService._load_sources` の明示定義へ追加する。新しい取得serviceや飛行workerを作らず、既存のsource一覧→入力固定→worker→`load_weather / simulate / export_result`を通す。任意日時のJRA取得UI、北海道の半月統計から原日時を選ぶ接続、多年の季節集合はこの候補に含めない。

| 登録される情報 | 意味 |
|---|---|
| ID / kind | `jra3q-surface-fixture` / `saved_jra3q`。IDは選択先を示し、同じbytesである証明ではない |
| schema / product | `balloon.weather.jra3q_surface/1` / `jra3q.ncar.regular_gaussian.model_surface_analysis` |
| 時刻 | `time_kind: analysis_valid_utc`、`run_utc: null`。00/06/12 UTCは解析の有効時刻で、予報run/leadを作らない |
| 範囲 | 共通のlat/lon範囲と `model_level:[1,100]`。固定pressure_pa軸を仮造せず、モデル面番号を高度支持の保証にしない |
| 来歴 | 登録時のbundle bytes/hashと、`load_weather`で検証した実効metadata。Bのpolicy・join・順序・モデル地形等を原取得来歴と区別して保持 |

登録時は読取前後のbundle hashを照合する。不適合・欠落はsource_errorsへ分け、他資料や保存結果の閲覧を止めない。新JRAとacquired_gfsのn=1受付では、放球から `integration.max_duration_s` までの全時間支持を調べる。従来GFS fixtureの支持停止診断は保持する。これは水平/高度の全軌道支持を保証せず、途中の支持不足は同じ核の停止結果になる。稼働後の登録済みpathが読めなければ409 `WEATHER_UNAVAILABLE`、bytesが変われば409 `WEATHER_CHANGED`で新受付を拒否する。起動時に登録されなかったIDは422 `UNKNOWN_WEATHER_SOURCE`である。

固定runは入力とweather snapshotを保ち、workerは実際に構築した場の `weather.metadata` をexportへ渡す。CLIとの比較は同じ固定入力・bundle・数値環境で行い、出力path/run IDによる来歴差と数値差を分ける。保存result GETは原場を読み直さない。現在の場が無くても旧結果の由来・軌道を表示でき、新しい計算の可否とは別になる。

画面では「保存例から候補を作る」と「既存候補へ気象だけを適用する」を分ける。前者は入力例を複写し、後者は現在の物理条件を保持して親と延期子のsourceを変更する。日時はJSTで秒を保持し、固定UTCへ変換する。延期は同じ物理入力へ時刻差だけを具体化する。親と子の計算受付は個別であり、一部の支持不足や拒否を全候補成功へまとめない。地点を地図で動かしても幾何ASL高度が自動で新地点のモデル地表になるとは扱わない。

**モデル地表照会（0.54）。** `GET /weather-sources/{id}/ground`はqueryに`expected_sha256`（64桁hex）、`time_utc`、`latitude_deg`、`longitude_deg`、`launch_altitude_m`を取る。schema `balloon.weather-ground/1`で、source ID/hash、正規化したUTCと要求座標/ASL、`ground_altitude_m`、`clearance_m`（要求ASL−地表）、`below_model_ground`、`ground_model`を返す。`height_reference: geometric_asl_m`、`is_fine_dem: false`、`scope: point_ground_only_not_full_flight_validation`を明示する。

`ApplicationService.weather_ground`は登録sourceを短くlock内で捕捉し、lock外で既存の`load_weather → field.ground_altitude`を呼ぶ。bundle hashを前後照合し、起動sourceの現状も確認する。未知IDは422 `UNKNOWN_WEATHER_SOURCE`、期待SHA/実bytes不一致は409 `WEATHER_CHANGED`、欠損/復号不能は409 `WEATHER_UNAVAILABLE`、時刻や空間支持のエラーは422で返す。workerと別の地表式を作らず、run/草案も作らない。地表値が返ることと、同じ高度の気象や全飛行の支持は別である。

`ConfigEditor → GroundPreparation`は候補、source ID/hash、UTC、緯度経度に束縛して応答を採る。後着応答のqueryは要求ASLも照合するが、同一点の地表値を利用中にASLを編集した場合の差は現在値から求める。地表照会だけでは入力を変えず、非負の指定余裕を明示適用したときだけ放球ASLを更新する。地点/時刻/場が変わった応答を別条件へ使わない。場の読込費用があるため、地図移動ごとの自動照会は行わない。粗いモデル地形と実DEM・建物/樹木を同一視しない。

気象の内容照合は、現在のsourceと、固定runのspec（旧票では読めたresult envelope）のweather snapshotとの比較である。入力差分、現在の気象の利用可否、保存結果の読取状態は独立に保持する。

| 由来の照合状態 | 表示と保持するもの |
|---|---|
| `same` | bytes hashと比較可能なschema/product/policy/joinが整合。科学精度や機体入力まで同一という意味ではない |
| `changed` | hashまたは比較可能な実効定義に差を確認した。表示中の旧結果を残し、現在資料による結果へ無言に貼り替えない |
| `unavailable` | 現在一覧に利用可能なsourceがなく、照合できない。保存結果の欠損とは別で、新実行と旧GETを分ける |
| `unverified` | 旧snapshotのhash欠落などで同一性を確認できない。変更を観測したとも一致したとも断言せず、現在値で過去の欄を埋めない |

この四状態と、固定結果GETの `loading / missing / error / ready` は別軸である。後者の`missing`は404であり、現在の気象が無い`unavailable`とは違う。旧workspaceに照合欄が無くても固定参照を読み、未確認を理由に未計算/0標本へ落とさない。source一覧の更新もn=1/集合の表示判定へ渡すが、草案revision、表示選択、固定結果、保存済み状態を勝手に変更しない。地図の支持境界と条件は固定結果のsnapshotに基づく。固定frontend候補では`weatherIdentity / weatherMatch / runWeatherSnapshot`を使い、入力差分は`draftInputsMatchRun`、集合では`collectionInputsMatch`へ分ける。`draftMatchesRun / collectionMatches`は入力一致に気象の`same`を加える。今回の実画面観察と未観察状態はS36へ分けて記録する。

### 説明と検査の戻り先

新serviceの契約は `backend/tests/test_application.py`、時間/相/入力差と状態更新は `frontend/src/domain.test.ts` と `workspaceState.test.ts`、現役画面への原record・停止3D・実出力の接点は `screen-contracts.test.ts` が担当する。実際の起動・地図操作・再起動後再閲覧は別の観察を必要とする。主要Python入口と実体の索引はIMPLEMENTATION_INDEX、使い方はCOMMANDS C-09、依存/lock/runtime集合はBUILDへ戻す。ここに試験数や将来の成功を固定しない。

## 予報を準備し、候補へ適用する接点（0.47）

`backend/weather`は外部配布の観測、固定計画、取得仕事、完成資産を分ける。`contracts.py`が外枠、`catalog.py`が配布索引の原応答と観測来歴、`planning.py`が候補群の必要時間窓・格子・取得可能性、`service.py`が永続状態と取得threadを所有する。飛行processとは別の同時1取得・最大4待機で、積分から取得処理を呼ばない。実階層はPROGRAMのWEB-WEATHERへ戻る。

| `/api/v1`以下の入口 | 入力・出力と副作用 |
|---|---|
| `POST /weather-inventories/refresh` | 任意の固定`run_utc`、`run_limit`既定2/最大4。NOMADSの索引を明示取得し、`inventory_id`と観測時点、部分観測の状態を返す。取得できた原HTML・URL・長さ・hashと、失敗したday/runの理由を分けて保存する |
| `GET /weather-inventories[/{id}]` | 保存一覧はDBの観測記録を返す。詳細読出しと計画作成では保存manifest・原応答を照合する。いずれも再通信しない |
| `POST /weather-plans` | `inventory_id`、固定`run_utc`、`region`、`candidate_windows`、時間余裕と上限から不変の`plan_id`を作る。`ready/unavailable`、不足lead、依存不足、必要窓・取得valid・範囲・概算を返す。通信しない |
| `GET /weather-plans/{id}` | 固定計画の読戻し。入力の変更でこの計画を上書きしない |
| `POST /weather-acquisitions` | `plan_id/client_request_id`。202で仕事を返す。同じID/同じ内容は同じ仕事、ID衝突は409。同じ取得・復号条件の完成資産はhash照合後再利用し、同じ実行中仕事も二重に取得しない |
| `GET /weather-acquisitions[/{id}]` | 保存履歴/進捗。pollは外部通信しない |
| `POST /weather-acquisitions/{id}/cancel` | 協調取消。`cancelling`から停止完了まで時間を要する場合がある |
| `POST /weather-acquisitions/{id}/retry` | 失敗/取消/中断だけを明示再試行。`attempt`と旧試行記録を残す。要求/復号器/rawを検査し、別runへ差し替えない |
| `GET /weather-status` | 復号・測地依存の利用可否と同時数。自動導入/通信しない |

0.54のinventoryは`observation_status: complete | partial | unavailable`と`observation_errors: [{stage: day|run, url, code, message, day?, run_utc?}]`を返す。成功したrunだけを`runs`へ入れ、失敗したrunを空の正常観測として混ぜない。root一覧の失敗、取消、local保存・整合性エラーは従来どおり操作を失敗させ、独立したday/runの外部観測失敗だけを部分結果にする。全対象runを読めなかった場合も200のunavailable観測を保存できるが、readyな取得計画にはならない。completeは今回の有限一覧観測についての値であり、各runの全leadの配布やGRIBの復号成功を保証しない。

`region`はWGS84の中心・東西/南北片幅、または緯度経度境界を受ける。中心指定はGeographicLibで東西南北への距離を求め、その外接矩形を0.25度格子へ外向きに丸める。全辺が一定距離の測地矩形という意味ではない。経度継ぎ目や極をまたぐ現行未対応要求は拒否する。`candidate_windows`はID、秒を含む放球UTC、最大飛行秒を持つ。親と延期子の最早放球から、最遅の（放球＋最大飛行秒＋時間余裕）までの包絡区間を`required_window`とし、それを挟む配布時刻を`normalized_request`へ固定する。配布名が揃うこと、復号した場が30 kmを支えること、各軌道の全行程を支えることはそれぞれ別に判定する。

保存先は`BALLOON_DATA_DIR/weather/registry.sqlite3`、`inventories/`、`acquisitions/`。仕事はqueued/running/cancelling/completed/failed/cancelled/interruptedを区別し、再起動で途中の仕事を勝手に再送しない。復号・支持検査後の`ASSET.json`は部分名からrenameして完成させ、登録した資産だけを既存の`weather-sources`へ接続する。起動後にPython/NumPy/SciPy/GeographicLibの実行版または対象Python sourceが変わった場合、新規操作、処理中の進捗、登録直前の照合で`SOURCE_CHANGED`を返す。計画時のecCodes等の復号器との不一致は`DECODER_CHANGED`で拒否し、再計画を必要とする。`SOURCE_CHANGED`の場合は再起動まで新規作業を止めるが、保存閲覧・取消・受付済み要求の読戻しは可能。変更検出は前後照合であり、瞬間的な変更と復元を原子的に監視する仕組みではない。

取得場は`kind: acquired_gfs`、固定SHA・bytes・run・valid・boundsと、全時刻/全格子の上端最小値を持つ。`default_config`はnullで、別地域の既定機体や放球高度を作らない。完成bundleは正規化要求全体と復号器の`cache_key`が一致するときに照合して再利用する。0.50では窓の異なる要求にも、登録済み完成資産の一致rawを独立コピーできる。全窓のcacheは別のままで、コピー/取得した全rawを現在の復号器で再検査し、新しいbundleとreceiptを作る。同じ失敗仕事の`retry`による保存prefixの再開、別完成資産からのrawコピー、完成bundle全体の再利用は別の経路である。完成資産再利用時の進捗は全ファイル完了・新規0 bytes・再利用raw bytesを示す。gzipのbytesは別値であり、転送量と取り違えない。飛行送信時にも現在の放球から`max_duration_s`までが選択場の時刻支持内かを検査し、外なら`WEATHER_WINDOW_UNSUPPORTED`で拒否する。

画面の`WeatherPreparation`が「条件→固定計画→取得・適用」を表示し、`weatherAcquisition`が親子窓・同一条件・不変planと草案の差を解釈する。取得範囲は橙の破線、固定結果が使った支持範囲は灰の破線で、地図確認から取得条件へ戻れる。取得条件や対象時間窓の変更後は旧計画を開始せず再計画する。ガス量等だけの物理編集では取得計画を無効にしない。取得完了は候補や表示runを自動で変えず、明示適用が現在の対象候補の`weather_source_id`を替えて`revision`を増やす。適用までの物理編集、元の固定結果は保持する。`modelDrafts`は候補・方式別の編集値を保ち、方式を戻したとき既定値で上書きしない。

一覧を更新しても選択中runを保持し、新観測から欠けた場合は「この観測で配布未確認」と表示する。今回観測した新しいrunは別に示し、明示選択まで差し替えない。初期のinventory・依存状態・取得履歴は独立に読み、成功分を一つの失敗で捨てず、失敗分は明示再確認できる。これを新しい配布一覧取得のPOSTと混同しない。取得jobの監視は前述の`jobObservation`へ渡し、受付/取消/明示retry後は、それより前に開始したGETの後着応答をepochで退ける。GET観測の回復でPOSTのエラーや未確認を消したり、草案/計画を作り直したりしない。

`ui_state.forecast_real.weatherPreparation`には選択した索引/計画/仕事と取得条件を保持し、原GRIB・巨大配列・キーは入れない。保存用の型は`WeatherPreparation.tsx`、取得のtransport型は`weatherAcquisition.ts`が定義し、`App`/`ForecastScreen`が接続する。配布観測/取得/再利用/保存後再読の有限観察はS36へ戻り、人工季節、保存半月統計、仮感度MCの各受入とは分ける。

## 元量を共有した感度計算と、その固定結果を読む（0.48）

### 一飛行、集合の進行、数値集計を分ける

`balloon_sim.ensemble` は抽選・物理入力への解決・着地図形・相別履歴の純粋な計算を担当する。HTTP・SQLite・workerを参照しない。`backend.ensemble` は計画、全試行の台帳、再試行、snapshot、選択分析の保存を担当し、既存の一飛行workerを共有する。`frontend` は利用者が比較する候補と標本を選び、同じ固定参照を地図・表・詳細へ渡す。ブラウザの再描画で抽選や飛行をやり直さない。

最初の実装は一つの固定気象場と、一つの物理量の一様分布である。`gas_mass_kg`（等温浮力上昇）、`burst_altitude_m`（高度破裂）、`reference_descent_speed_m_s`（定格速度下降）から、全比較候補で有効な量を選ぶ。量と単位・モデルの適合を核の定義から確認し、非対応モデルへ別の意味で渡さない。分布の理由、上下限、標本数、seedを入力へ残す。製品仕様や実測から校正済みの誤差と呼ばず、仮定した感度幅として表示する。ガス質量だけを替えても、破裂後の有効下降質量を連動変更する実装ではない。

`freeze_drawset` はNumPyのPCG64による物理値、等重み1、順序、版、理由を固定する。seedだけに再現性を依存させず、実現値そのものとhashを保存する。`resolve_config` は各候補の既存設定へ同じ物理値を適用し、既存の設定検査を通す。無効な実現値を切り詰めたり、成功するまで引き直したりしない。各試行の元値・解決config・エラーを台帳へ残す。

延期子では親から放球時刻だけが指定分ずれることをAPIで検査する。モデル変更は独立候補として扱う。共通drawは同じ物理値を割り当てる意味であり、異なるモデルでも同じ軌道を保証する意味ではない。候補別の結果を一つの確率混合分布へ自動統合しない。

### 固定計画と永続化の境界

| `/api/v1`以下の入口 | 入力・出力と副作用 |
|---|---|
| GET `/ensemble-capabilities` | 対応元量、仮定感度という解釈、運用上の上限を返す |
| POST `/ensemble-plans`、GET `/ensemble-plans[/{id}]` | 固定場、候補群、samplingを計画へ固定する。全実現入力・不足窓・拒否理由を確認でき、飛行は開始しない |
| POST `/ensembles` | `plan_id/plan_hash/client_request_id`を確認して集合を受け付ける。新規抽選しない |
| GET `/ensembles[/{id}]`、`/ensembles/{id}/trials` | 集合進捗と全試行台帳。試行一覧はcase/offset/limitで読む |
| POST `/ensembles/{id}/cancel` | client_request_idを伴う協調取消。実行中の一飛行は完了させ、未開始分を止める |
| POST `/ensembles/{id}/retry` | client_request_idと再試行するtrial_idsを明示する。実現値とtrial IDを保ち、attemptとrun IDを新しくする |
| GET `/ensemble-snapshots/{id}`、`/cases/{case_id}` | 固定時点の台帳と候補別集計。後の再試行で以前のsnapshotを置き換えない |
| GET `/ensemble-snapshots/{id}/trials/{trial_id}/result` | 明示選択した試行の原履歴・固定入力を読む |
| POST `/ensemble-analyses`、GET `/ensemble-analyses/{id}` | snapshot/case/選択trial IDsを固定し、その群の集計を保存する。領域からの選択では領域集合と判定器版も記録する |

実行票の数値環境指紋はPythonの版/実装、NumPy・SciPy・GeographicLibの版を対象とする。0.49ではGeographicLibもworkerの実行前後照合へ加えた。全依存環境の固定を保証するものではない。風統計側のDuckDB版は別に資料descriptor・集計同一性へ記録する。旧版の指紋から変更された計画を無条件に再実行せず、保存結果の閲覧と新計画の作成を分ける。

同一の要求IDで同一入力の再送は同じ保存物へ戻し、違う内容には衝突を返す。新計算のコード/数値環境/場のhashを検査する一方、既に受理した要求の読戻しを新計算として扱わない。原resultの公開後、DB登録前で中断した場合は、COMMITTEDと固定specを照合した結果だけを回復する。不完全なstagingの存在から完了を推測しない。

全予定試行は `unstarted/queued/running/landed/stopped/invalid_input/failed/cancelled/interrupted` を保持する。集合は既存processへ1件ずつ補充し、別の無制限worker poolを作らない。初期配備の制限は1計画256試行（候補数×標本数）、同時4集合で、科学的に適切な標本数を決める値ではない。再起動後の未完了集合と投入済みattemptはinterruptedとなり、未投入trialはunstartedのまま残る。勝手に再計算しない。取消の再送応答は受付時のcancellingを固定した受領記録であり、現在の終端状態はGETで読む。

画面の集合関連GETは応答本文のJSON読取までを30秒のdeadlineに含め、期限時/画面の再読世代変更時にAbortControllerで読取りを止める。これは計算取消POSTではない。進行中jobのGET監視は読取り完了後に通常0.9秒待機し、通信失敗後の待機を1.8/3.6/7.2/14.4秒と延ばし、以後15秒を上限とする。これはGET開始間の総時間ではなく、読取り時間に加わる待機である。一jobのGETを重複させず、利用者の「状況を確認」も同じ読取りへ接続する。回復時に解消するのはGETの観測エラーだけで、別のPOSTエラーを消さない。状態不明の間は最後に読めたstate/countsと最終確認時刻を残す。jobのepoch/state_revisionと画面世代を照合し、古い応答で再開後の状態を巻き戻さない。固定snapshotはこの監視から独立している。

`registry.sqlite3`がtrial/attemptと結果参照を持ち、`ensemble-artifacts/<UUID>/{document.json,COMMITTED.json}`へ計画・snapshot・分析を固定する。一飛行の原履歴は従来の`results/<runUUID>`にあり、集合文書へ全原履歴を複写しない。

projectの `compare_results` は一飛行run参照と集合snapshot/case参照を区別する。旧 `compare_run_ids` も読み、既存保存を壊さない。内部の集合trialを通常の一飛行結果一覧へ大量に混ぜず、`GET /runs?include_ensemble=true` を明示した場合だけ含める。草案更新・集合再試行・表示snapshot選択はそれぞれ別の操作である。

### 分母、輪郭、履歴の意味

全予定数N、着地数L、選択した禁止領域へ着地した数Hを区別する。未着地・失敗・入力不成立をLへ加えず、台帳からも消さない。H/Lは着地が得られた群に条件付けた割合であり、残る試行を安全と判定した全計画の確率ではない。停止地点は最後の有効位置として描き、着地点へ変えない。地域判定は50/90/95%輪郭や凸包の交差で代用せず、全着地点に対して行う。

着地集計はGeographicLibのWGS84局所平面で共分散を求め、観測Mahalanobis距離の順序統計で50/90/95%の経験的な包含域を作る。正規分布の理論確率域ではない。1標本等は点、一直線の群は線として退化を保持し、人工的な幅を足さない。閾値の同順位を含むため表示割合を超える場合があり、実際の包含数を返す。二峰性や曲がった分布では無標本の空間も包み得る。全選択点を囲むextentは集計APIの出力として保持するが、干渉群の外周表示には使わない。概要・3D・KMLは該当着地点を示し、件数から同じID群の詳細へつなぐ。極/経度継ぎ目/広すぎる局所投影は描画不能理由を返してLを保持する。

履歴は経過秒で相ごとに内挿し、上昇/下降の境界を横切って結ばない。相の始終点を共通時刻列へ含め、短い相も消さない。同じ破裂時刻の上昇左値と下降右値は別系列に入り、二系列のnを加算しない。着地/停止の端点は履歴曲線へ含め、それより後へ延長しない。瞬時風分布はその時刻に飛行中の群だけを対象とし、履歴端点の扱いとは異なる。各時刻の平均・10–90%帯・nを返し、平均軌道を一つの実在飛行とは扱わない。同一相・同一時刻の重複で全物理値が一致する場合だけ解析用に統合し、原記録は保存する。

履歴集計には選択した `result.json` の合計64 MiBという運用上限を設ける。これは実メモリ上限の保証ではない。超過時も着地・全N台帳を保持し、履歴は `HISTORY_ANALYSIS_BYTE_LIMIT` と省略数を返す。利用者が標本を絞って読み直せるようにし、空の図を飛翔履歴が存在しない意味へ読み替えない。

原履歴GETは、詳細の固定snapshot/case内で現在選択された既知のtrial IDのうち、result_availableがtrueの記録を対象とする。重複・未知IDは拒否し、集計の完了・履歴の未生成理由・送信権を開始条件にしない。領域操作で選ばれたIDも、領域集計を待たずに読める。`historyLoadQueue`は一画面instanceで最大4件を同時に読み、読込済み・送信中を重複させない。選択や画面が変わったら旧選択の未送信分を送らず、既に送ったGETが完了しても旧queueの続きを増やさない。失敗分は「表示データの読込を再試行」で明示再読する。64 MiBはサーバ側の選択集計の受入制限であり、4並列は画面側の要求数制限である。既に読んだ履歴cacheや複数画面を合わせたメモリ/総通信量の上限を保証しない。式・退化・集計量の定義はTHEORY第8章へ戻る。

### 同じ選択を地図、詳細、保存へ渡す

禁止領域内の判定は既存frontendの地理判定器を一か所で使う。APIは指定trial IDs、有限の領域JSON、判定器版と各hashを固定するが、サーバ側で独立に幾何判定を検証したとは扱わない（`classification_verified_by_server:false`）。再閲覧では保存した着地点と領域から選択を照合する。面の重なりを同名反復にせず、穴や境界、複数領域への所属を扱う責務は表示側の判定器に残る。

画面全体の選択世代でn=1/集合の読込を共有し、後着応答が新しい選択へ割り込まないようにする。全標本、空間的に位置を持つ標本、明示選択した試行を区別し、地図上で選べない試行を全Nから消さない。地図の選択・干渉群は同じtrial ID集合を詳細へ渡し、入力実現値の分布・台帳・相別履歴へつなぐ。これは原因候補を調べる入口であり、選択群と他群の差だけから因果を確定する手続きではない。

## 原日時集合から、同じ飛行・集計・画面へ渡す（0.55）

`ClimateFlightHandoff` は固定集計の出典・半月/月/季節・構成する元半月ID・気象有効時刻subset・地域を関心条件としてAppへ渡す。UTC暦とJST時刻ラベルを分け、有効時刻を原放球時刻へ自動置換しない。`HistoricalEntry` / `HistoricalPreparation` が共通機体と明示した原放球日時を編集し、`historicalDomain` が両者の役割と比較を扱う。共通のHistoricalWindow/HistoricalSamplingは純型の `historicalTypes.ts` に置き、`ensembleDomain` と `historicalDomain` がそこへ依存する。後者の互換re-exportを保ち、相互importを避ける。`historicalWorkspace.projectForAnalysis` は共通projectの画面投影だけを絞り、予報候補や旧結果を保存から削らない。`season_real` の表示状態は予報と独立し、固定結果は既存ForecastScreen/runtimeへ渡す。機体仮幅のparameter表示を原日時へ偽装しない。

関心の来歴は `ui_state.season_real.historicalInterest`、詳細で選んだ標本群は同namespaceの `selectionContext` へ分ける。`readHistoricalInterest` はschema・由来ID/hash・範囲・元半月支持を検査し、旧半月来歴と新しい月/季節・時刻subsetの来歴を読み、`mergeHistoricalView` が詳細更新前に別欄へ保全する。既に標本群の表示で上書きされた値から元の気象関心を推測復元しない。固定した `HistoricalDraft.selection_context` は別の実行入力として保持する。

`backend/historical_catalog.py` が起動時catalogの各path/hash/schemaを検査して原UTC場を登録する。`HistoricalPlanRequest` を `POST /ensemble-plans` へ渡すと、`historical_planning.build_historical_plan` が原日時×共通機体caseを展開する。元日時の重複を拒否し、各試行に実際のsource snapshotを固定する。集合に付く `historical_window_set` は選択集合の指紋であり、一つの気象場のIDではない。現在の登録場との照合・境界描画はmembersごとに行う。

同じ `EnsembleService` / ApplicationService / worker / flight核へ投入し、既存の状態台帳・snapshot・分析を使う。未登録・時刻不足・放球点の領域外は `invalid_input` として台帳へ残す。全不成立なら実行を受け付けず、一部成立なら予定数と実行可能数を別に返す。試行ごとに原UTCだけを置換し、他の機体/地点条件を保持する。延期の親子関係と原日時という二重の時刻所有はこの経路では拒否する。

`CaseResult.mode` は `historical_windows`、`parameter` はnull、原日時は `weather_window` に置く。等重み1の明示選択であり抽選seedはない。予定数・着地分母・経験域・相別履歴は共通定義を使う。原日時や選定理由を草案で変えた後も旧結果は不変で、変更を未反映として示す。単一テンプレートの日時を集合全体の実放球日時として表示しない。季節の母集団を網羅する取得・時間帯mask・共同場の抽選・校正済み予報確率はこの接続からは導かれない。

## 保存統計と元時刻標本を、年間・地域・月の比較へ渡す（0.49→0.58）

同じ分析画面へ、異なる由来と支持を持つ資料を接続する。GFSの時空間場、飛行worker、人工風の生成器とは別である。提供DBの集約値からは平均・件数を結合し、元時刻標本からは元値を直接まとめて平均・分位・風配を求める。少数の分位やfitから原標本、高度/時間の同時相関を作らない。具体階層はPROGRAM、式と分母はTHEORY、起動と操作はCOMMANDS C-09へ戻る。

| 資料・読取担当 | 固定する支持と用途 |
|---|---|
| 提供DB / `ClimateSource` | 2016–2025年、38面・570格子の平均とcount。時刻subsetの平均は下層20面。任意の同支持原標本がある場合だけ月分位を追加する |
| 元UTC束 / `WindArchiveSource` | `balloon.wind-samples/1`の年・格子・面を独立して登録。JRA-3QとERA5を同じ格子や10年DBの代替へ読み替えない |
| 人工操作模型 | 既存の操作説明用標本。実資料の不足を補完するfallbackにしない |

今回の取得対象は2024年の全12か月・00/06/12/18 UTC、JRA-3Qが38面/570格子、ERA5が37面/1188格子である。これは入力計画の範囲で、取得・検査の成功記録ではない。年filterはまだなく、選んだ資料の`years_fixed`が母集団を決める。単年の経験分布を多年の季節確率にしない。

### 登録資料と要求の境界

`BALLOON_CLIMATE_DB`と任意の`BALLOON_CLIMATE_SHA256`をservice起動時に読む。DB pathは信頼する起動設定であり、HTTPはpath・URL・SQLを受けない。`ClimateSource`は全ファイルSHAを固定し、提供profileのテーブル/量/元格子/面/半月の完全支持を検査する。DBはread-only、外部アクセス/拡張自動導入なし、DuckDB 1 thread、buffer manager 128 MB、temporary disk 0 Bで開く。これらはプロセスRSSの保証ではない。通常照会はfile statとadapter sourceを前後照合する。画面の資料状態GETは全ファイル再hashではなく、敵対的なstat復元への対策でもない。

元時刻束は`BALLOON_CLIMATE_ARCHIVES`のJSON path配列（最大8件）で別々に登録する。`BALLOON_CLIMATE_SAMPLES`は旧DBと同じ年/格子/面を束縛する任意の伴走資料であり、単年の別製品をここへ差し込まない。`MonthlySamples`は新`balloon.wind-samples/1`と旧`balloon.climate.raw-months/1`を区別する。新schemaはprovider/label、年の両端、元格子と正の面積重み、nativeの面、月ごとのUTC配列とu/vのpath/bytes/SHAを持つ。`.npy`のfloat32配列は `(元UTC時刻, 面, 格子)`、pickleは不可。月内の全指定年・毎日4 UTCの順序/件数、shape・有限値・支持を検査し、不足を補間しない。相対pathの束外逸脱、重複ID、非正の重みや破損を拒否する。年間の独立sourceは全12か月を要求する。旧DBの伴走資料では未取得月を`available:false/reason:month_not_acquired`として保持できる。

元束の`dataset_sha256`はmanifestのSHA、source IDはadapter版とmanifest SHAから得る。配列のhashはmanifestへ束縛し、起動時に実体を照合する。通常照会はmanifest/配列のstatと実装snapshotを前後照合し、`verify_full`は全SHAを明示再確認する。statを偽装して戻す敵対的な置換の検出を通常GETへ約束しない。`provider/label/weighting/capabilities/levels`はsourceごとに返す。互換の格子字段`gauss_weight`も、ERA5では球面面積重みを持つため、表示の重み名は`weighting`を読む。

取得toolsはHTTP rawと受領情報を保全し、単位/座標/UTC/圧力面を確かめて完成月だけをmanifestへ加える。解析serviceは取得toolを呼ばず、HTTP入力から外部取得を始めない。両製品ともu/vだけのこの束は、地表量・温度・高度を揃えた飛行用気象場ではない。 `prepare_climate_demo.py`は、完成束から指定点を挟む2×2の元格子を補間せず選ぶか、固定ZIPの全memberを検査して新規出力先へ展開する。元時刻と全圧力面を保つ小さな機能確認用資料であり、全域統計の代表性を意味しない。JRA取得のnative basisは、配布DBの代わりに元格子/面/重みだけの固定JSONも使える。再開の通信上限と段階操作はCOMMANDS、実際の取得履歴と停止理由はS36へ分ける。

0.57のERA取得追補は`acquire_era5_climate_samples.py`の明示`--transport dods|ncss`に限定する（既定はdods）。同じNCAR `e5.oper.an.pl`のNCSS原NetCDF3をSciPyで読み、Float32のU/V、native次元順、単位/calendar、時刻・37面・緯度経度の型と値、fill/有限値を照合する。補間・packed値の展開や不一致の補正はしない。NCSSは日別ファイルへ`time=all/timeStride=6`を要求し、返却が00/06/12/18 UTCであることを別に確かめる。自動fallbackはなく、`--resume`は同年・既公開月列を含む要求だけを受ける。成功済みDODSとNCSSのURL/bytes/SHAを再検証し、両方あれば復号値/UTCの不一致を拒否する。DODSの失敗枠をリセットせず、NCSS原bytesと試行票を別名で保全し、`canonical_request/canonical_sha256/prior_dods_attempts`とmanifestの`conversion/service_policy`で混在を説明する。完成月checkpointは内容一致を要求し、両成分の全UTC配列が揃った後だけmanifestを公開する。有限2probeの意味と、その後の取得状況・完了実績はWEATHER/S36、試行枠とworker数はCOMMANDSへ戻る。本段の確認はfreeze10の取得契約読解であり、全量取得・全U/Vのサービス間一致を認定した印ではない。

要求は`source_id`、nativeの`level_id`、任意の`bounds={west,east,south,north}`、`grain:half`を保ち、任意の`hours_utc`を加える。省略/nullは全4時刻、部分集合は整数00/06/12/18の非空・重複なしに限る。順序を昇順へ正規化し、全4指定は省略と同じqueryへ戻す。空・重複・bool・範囲外時刻を拒否し、`grain:month/season`をPOSTの別要求にしない。範囲内中心の元格子を選び、領域外・空集合・継ぎ目・不明字段を拒否する。年範囲はdescriptorの`years_fixed`で固定し、半月はUTC 1–15日/16–月末の24区分。JSTラベル09/15/21/翌03時はUTC暦を変更しない。

原標本の風配だけを切り替える任意の`rose_cell_id`は、そのsourceに存在する非負の整数native IDであり、配列indexではない。bool・負数・非整数は`CLIMATE_INPUT`、元束にないIDは`CLIMATE_SUPPORT`で拒否する。省略/nullはquery辞書へ出力せず、旧要求のcanonical bytesと受付IDの束縛を維持する。未指定を既定IDへ書き換えない。選択可能な元束だけが`wind_rose_point_select:true`を返し、旧DBへの非null指定は`CLIMATE_UNSUPPORTED`となる。領域外の元格子も明示指定でき、地域の標本集合は変更しない。

提供DBでは全時刻は`fact_wind`の38面（3–1000 hPa）、subsetは`fact_wind_diurnal`の20面（300–1000 hPa）に限定する。subset時の年間縦断もこの20面に絞り、非対応面は`CLIMATE_HOUR_SUPPORT`で拒否する。descriptorの`hour_filter/hour_level_ids`で支持を渡す。時刻別/風配の拡張表がない旧mean専用資料は基礎集計を利用できるが、存在する表の型・単位・母数・キー・支持が壊れていれば登録を拒否し、別母集団へ無言でfallbackしない。38面/570格子は提供profileの支持であり、製品の共通仕様ではない。独立元束はdescriptorの全native面で4 UTCの任意部分集合を使える。元束の資源上限は2000格子/45面/連続10年までで、全条件の性能保証ではない。

`climate-summary/1`の上位`annual/spatial/population.timebins/display_scales`は24半月の既存形を保つ。`summaries_by_grain.month/season`へ各12か月/4季節の`timebins/annual/spatial_rows/display_scales/wind_rose`を追加する。各図のgrainはこの保存応答内の表示選択であり、queryや受付IDを変更しない。元半月の同一cell/levelを実時刻数nで時間合成してから資料固有の面積重みで地域平均を求め、u/v/平均scalar speedから来向・定常度を再計算する。空間の最大最小も合成後のcell平均から求め、半月の極値を平均しない。冬は固定年に含まれる12/1/2月のpoolであり、連続する冬を年跨ぎで抽出したものではない。時刻数と格子数を別に保持し、支持の欠けた行を除外して異なる母集団を混ぜない。

原標本adapterだけが別枝`annual_quarters`を返す。`schema:climate-annual-quarters/1`、`date_convention:UTC`、`calendar_definition.version:utc-half-nested-quarters/1`と、48個の`timebins`・全高度の`annual`・`display_scales`を持つ。各月のUTC 1–7日/8–15日/16–22日/23–月末を元u/vから直接平均し、資料固有の格子重みで地域集計する。元半月の平均や分位を分割して値を作らない。月末・閏年と選択UTC数を実件数へ反映する。既存の`population.timebins`と`summary.annual`は24半月のままで、`summaries_by_grain`にもquarterを追加しない。`ClimateAnnualGrain`と`annual_grain`だけが`quarter`を許し、`query.grain`はhalf固定を維持し、共通`ClimateGrain`・地域図/風配・飛行関心の期間型は半月/月/季節を維持する。元日時別の標本を欠く旧10年集計DBや旧artifactには48区分を補完しない。

提供DBの`wind_rose`は固定cell 285（43.267398834228516°N、143.625°E）・選択面・全4 UTC時刻の16方向×6速度階級だけを返す。月/季節はcountを足して合算nで割る。`point_in_selected_region`がfalseでも同じ固定点の資料を返すため、選択地域の代表性へ読み替えない。subset時は`available:false/reason:hour_subset_not_available`、表なしは`source_has_no_wind_rose`を返す。来向はFROM北0°時計回り、0–5 m/sは無風専用ではなく、50+は上端なし。分位/fitパラメータを合成してはいない。

独立元束の風配は、未指定時には元格子矩形の中心に最も近い既定1点、`rose_cell_id`指定時にはその元格子の選択UTC標本から求める。descriptorの`wind_rose_point`は既定点のまま保持し、各半月/月/季節応答の`wind_rose.point`に実効点を残す。局所選択をsourceの共有既定点へ書き戻さない。`point_in_selected_region`は実効点と選択boundsから判定する。領域変更だけで点を移動せず、地域の中央値・幅と一点の風配を別の母集団として読む。`wind_rose_hour_filter:true`と`native_hours_utc`で部分時刻への対応を区別し、旧DBの非対応文を流用しない。速度0の標本は風向なしとして方向行に入れず、`calm_counts`へ分ける。方向階級のcount合計＋calm countが全採用時刻数Nであり、各frequencyの分母もNである。FEはこの整合を検査し、静穏n/Nを表示する。旧DBに`calm_counts`がない場合だけ従来のcount契約を保つ。

気圧native IDを保持し、縦軸はISA補助高度で並べる。提供DBの幾何高度の補足は元DB全域・全期間で、選択範囲の高度ではない。元束では実高度を取得しておらず、`alt_geom_mean/min/max_m`はnull、標準大気からの参考高度だけを示す。平均ベクトル0の来向、全無風時の定常度はnullで、ゼロ度/ゼロ定常度へ補わない。平均/領域集計/定常度の式はTHEORYへ戻る。

### 固定集計の保存と、草案の編集

| `/api/v1`以下の入口 | 入力・出力と副作用 |
|---|---|
| GET `/climate-sources` | 登録descriptorと利用不可理由。資料を再登録・再集計しない |
| POST `/climate-analyses` | `client_request_id`と`query`を受け、固定analysis artifactを返す。同一内容の照合済み保存物があれば再利用する |
| GET `/climate-analyses/{id}` | 保存artifactを照合して返す。元のDB/原標本束がなくても読み、再集計しない |

`BALLOON_DATA_DIR/climate.sqlite3`へartifact本体、要求ID、query対応を保存する。artifactは`analysis_id/query/query_hash/result_hash/created_at/summary`を持ち、summaryにも資料hash/実装/統計版/母数と使用数値ライブラリを残す。旧DBはDuckDB版、原標本がある資料はNumPy版を含む。同じ要求ID・同じqueryの再送は現資料を調べる前に保存受付へ戻り、違うqueryなら409。同じqueryでも新しい要求IDの場合は、現在の資料/adapter/統計版/DuckDB版と、ある場合の`numerical_dependencies.numpy`の同一性を確かめて保存集計を再利用する。同一query identityで異なる結果が得られれば上書きせず拒否する。集計用lockは飛行管理とは独立し、保存GETは集計用lockを取らない。原標本adapter内には範囲＋採用UTCをkeyとする4母集団のLRUがあり、全高度のmoment/月分位に加え、半月/月/季節の年間値と年間48区分を再利用する。面変更では選択面のspatial/表示尺度と選択地点の風配を組み直す。風配は選択面・選択点の元標本を一巡して24半月のcount/静穏数を作り、同じcountを半月/月/季節へ合算する。3粒度ごとに元標本を読み直さず、分母の採用UTC件数は維持する。地点だけを変える場合も範囲＋UTCのcacheを再利用し、地域のmoment/分位/年間値を変えない。応答はcacheの値から独立させ、要求ごとのspatialや来歴の追加で共有値を書き換えない。明示pointは永続query identityへ含める。これは永続artifactの照合cacheやFEの6面cacheとは別の寿命である。資料/実装変更は409。現在資料が一つでも登録されている時の未知sourceは409、登録資料を一つも利用できない場合は503で、別資料へfallbackしない。その他の支持・標本不整合は原則422として返し、部分集計を保存しない。

`ui_state.weather_real`は草案queryと、表示中artifactのanalysis/source/data/query/result識別、図ごとのgrainを含むviewを持つ。`annual_grain/spatial_grain/monthly_grain`、`monthly_mode`（quantiles/profile/rose）・`monthly_page`、関心受渡し用`interest_grain/interest_period_id`を保存し、旧値の不足は既定表示へ補うが統計値は補わない。時刻subsetはquery、粒度はviewへ分ける。入力編集中も旧固定集計を保持する。共通適用は草案query、地域図/実風配の面探索はartifact.queryのlevel_idだけを変える。面探索は最初の入力から300msの開始予定を後続入力で延ばさないmax-waitとし、一度に1要求と最新1待機へ直列化し、古い応答を表示へ採用しない。二つの面スライダーは選択中の要求面を共有し、図/表示面は新artifactが受領されるまで固定する。未適用の地域/UTC等を送信・消去せず、同じsourceの草案面も後の明示編集を上書きしない。同じ母集団とdata hashで受領済みのartifactを画面内最大6面のLRUに保持し、hitはPOSTなしで表示する。共通適用・資料変更・復元・画面破棄は古い探索とcacheを無効にし、資料一覧再取得はcache世代だけを破棄する。古い応答は現在の図へ採用しないが、同世代/同母集団の妥当なartifactはcacheへ保持でき、その面を後で明示選択した時にだけ表示できる。通信より速い全drag frameの描画を保証する契約ではない。reader/旧source/未対応面は送信せず、権利取得だけでblocked/不明要求を自動再送しない。近傍の明示retryと共通適用を区別する。保存/再訪は採用済みartifact参照と草案を保持し、自動POSTを開始しない。旧source_idが現在descriptor一覧にない場合、selectにその旧識別を持つ無効な案内選択肢を残し、現在資料を選択済みに見せない。新集計には現資料を明示選択し、固定artifactや草案を自動置換しない。保存済み旧artifactは元DBや新adapterなしでもhash照合してGETでき、月/季節/風配が欠けていれば未対応とし、新値を生成して補完しない。旧DBの現adapterは`jra3q-halfmonth-summary/3`・統計版`gaussian-pooled-wind/3`、独立元束は`original-utc-wind/2`を使い、それぞれのsource codeと数値依存版をidentityへ含める。旧保存値を再計算で上書きしない。年filterと実季節飛行をこの統計画面で実装済みにせず、資料が読めなくても人工画面へ自動切替しない。

実側の面操作行はスライダーと状況欄を独立した行にし、値表示の中は専用gridで固定枠へ分ける。選択中hPaと表示中hPaを固定枠へ置き、表示中の下段にISA参考高度を置く。retryボタン・待機/失敗/支持理由は別の状況行へ出し、文字幅の変化でスライダーを動かさない。これは要求のmax-wait/直列化と別の表示責務であり、通信より速い全frame追随や所要時間を保証するものではない。年間48区分がない結果では支持理由を示し、旧図を保って現資料の明示再集計へ案内する。

地点切替は共通適用と別の適用種別を使い、表示中artifact.queryの`rose_cell_id`だけを変える。点の候補は地図の最寄り元格子またはID一覧で選び、明示確定するまでPOSTしない。草案は点欄だけ更新し、受領時はapplied参照だけを替えるため、未適用の地域・UTC・気圧面と後続編集を保持する。面探索と共通の1実行＋最新1待機のqueueへ直列化し、地点待機/送信中は面スライダーを無効にする。先行する面要求は最新地点要求で表示採用を失効させ、後着応答を新地点の図や面cacheへ混ぜない。面cacheのkeyには点も含み、地点切替時にも世代を破棄する。失敗/readerは明示retryを待つ。地点選択前のraw保存結果でも、同じsource IDが現在catalogで選択対応かつ草案でも同じ資料を選択中なら新たな地点操作を許可し、保存artifactのcapabilityや数値を書き換えない。旧DBや現在利用不能の資料へは広げない。

草案編集で旧計算応答の採用を無効にしても、保存済みartifactのGET復元は新しい固定結果を採用するまで維持する。復元GETと新POSTのbusy/statusを分け、後着GETで進行中のPOSTを完了扱いにしない。資料/保存GETは20秒、新集計POSTは60秒でAbortControllerへ中断を要求する。POST取消APIはなく、server処理完了/未受付の証明ではない。同じ入力の明示再試行は同じ要求IDを使う。この再送情報は画面内で、reload後にPOSTを自動再送しない。

### 図だけの操作と出力

同じ固定view modelで入力や状態文だけが変わった場合はSVG群を再生成しない。年間図はsourceが示す全時刻/時刻subsetの面支持を保持し、地域図は色セルを選択格子全体へ描く。矢印/中心記号だけを共通の間引きIDで減らし、統計の母数を減らさない。元中心から作る色セルの境界は可視化上の区画であり、連続気象場の支持や地形精度ではない。


**月の分布図と平均図の責務：** `monthly_profiles`は`climate-month-profiles/1`で、元格子×選択UTC時刻の風速を面積重み付きでpoolした経験分位である。`method:inverted_cdf`と資料固有の`weighting`を固定し、各月・各面の前後半中央値2線、月全体p10–p90帯、時刻数/格子数/元値数を保持する。定義と式はTHEORYへ戻る。地域平均した風の時系列分布でも、半月分位の平均でもない。旧人工図は等重み・線形補間分位の模型として区別する。

`monthlyProfiles.ts`はsource/summary/DTOの固定年、格子ID、面、採用UTC、重み、月の暦件数、分位順序と有限値を照合する。`climateSummary.ts`が固定view modelへ渡し、controllerが`monthlyProfiles.ts`の描画関数で12か月固定の同じ軸へ結ぶ。月の未取得は空枠のまま、平均線で分位を代用しない。profileモードは平均風の補助図として残す。分位図は半月中央値と月帯という固定の問いであり、月/季節粒度の選択から季節分位を合成しない。全12か月のp90と両中央値を共通横軸へ含め、月ごとに尺度を変えない。保存SVGにも固定資料・年・UTC・地域/格子数・分位/重み定義を残す。

年間図には背景地図要求がなく、地域図を開くと地理院タイルを読む。背景失敗でも集計値と固定参照を保持する。実気象のSVG準備は押した時点の図・条件・凡例・来歴を捕捉し、実際に含む背景だけを埋込み対象・出典へ記録する。年間図へ地図背景の出典を付けない。保存途中の入力変更で別条件の図を混ぜず、背景取得に失敗したら出力成功としない。実気象は「SVGを準備」の生成成功後、明示ダウンロードリンクを公開する。生成したBlob URLは次の同図生成成功時に交換/旧URL解放、画面破棄時に解放する。風配のSVG metadata/凡例は捕捉した`wind_rose.point`とqueryを保持し、リンク直下の生成時母集団/面/元格子ID・座標の条件文も同じ成功時だけ確定する。表示条件の変更やクリックではhref/条件文を差し替えず、再生成失敗時は前回生成分の表示で旧リンクを保つ。クリックはブラウザへの保存要求であってファイル保存完了の証明ではない。図保存は再集計でもDB配布でもなく、別PCへ任意再集計を提供するものではない。人工profile/風配/飛行影響は資料を明示する旧人工経路に残る。一点の実風配を選べることを、地域全体の分布や季節飛行の科学的採用へ広げない。

## 気象層：保存物を場として受け入れる
### 取得と復号を分けて失敗から再開する
`acquire_gfs(request, output_dir, *, resume=False, progress=None, cancel=None, raw_provider=None)`は要求・復号依存・作業配列の概算を検証した後、新しい出力ディレクトリを作る。既存の二引数呼出を保ち、明示的な再開、進捗通知、協調取消、登録済みraw候補の提供をkeyword-only引数へ分ける。CLI既定は`raw_provider=None`で、backendの登録DBへ依存しない。
要求は固定run、利用する時刻範囲、緯度経度矩形、取得量上限を持つ。内部`_request`が0.25度格子へ外向きに丸め、範囲両端を挟む最小の配信時刻集合を作る。
`_url`はその集合から各ファイルのURLを作り、`_download`は残りバイト数を確認しながら一ファイルずつ保存する。
これは全地球を暗黙に取る入口ではなく、一run・一要求の有限な取得である。最大50 MBのraw入力上限には、新規通信、再利用、保全したpartialを含める。

取得・raw再生・復号の実定義は`environment/gfs.py`、NOMADSへの通信と間隔は`nomads.py`、GFS固有の層・配信時刻・GRIB短縮名は`gfs_contract.py`、JSON/gzip保存は`storage.py`にある。

完了したrawごとのURL、時刻、バイト数、SHA-256、HTTPメタデータは`provenance.json`へ残る。失敗部分について同じ完了メタデータが全て揃うとは保証しない。
復号に失敗しても取得済みrawを捨てず、`failure.json`で失敗を説明する。
既存ディレクトリへの再取得、配布先の変更、別runへの差替えは自動では行わない。既定のCLI呼出は従来どおり新規出力だけを許す。serviceからの明示再試行は`resume=True`で、保存要求とデコーダーの同一性、完了rawのURL・長さ・hash・GRIB識別を検査して接続する。不完全なrawを完成物として再利用せず、残った部分bytesも同じ要求のraw入力予算へ算入する。完成bundleとreceiptも揃っていればhash照合で再利用する。rawだけが揃っていて完成bundleがない場合は、通信せず再復号する。

0.50の`WeatherService._raw_donors`は登録済み完成assetの参照を短くlock下で写し、以後の照合をlock外で行う。同じrun・正規化矩形・不足leadについて、markerと圧縮bundleのhash、保存rawの正確なURLを確認して候補を返す。URLには量/層のselectorも含む。未登録directory、途中job、失敗jobを走査して採用しない。bundleの照合は圧縮ファイルのhash読取りであり、この段階では全配列を復号しない。

`acquire_gfs`は同じ仕事のprefixを先に照合し、不足leadがある場合だけ`raw_provider(specification, missing_leads)`を呼ぶ。`_verified_raw_candidates`でURL/lead/名前/bytes/SHA/GRIB識別と通常のfile変更を検査する。同じ要求キーに異なる正当なbytesが見つかれば`AMBIGUOUS_SAVED_RAW`で拒否する。一致候補の破損は黙って通信へfallbackせず、理由を残す。候補のあるleadでも完了を仮定せず、全て照合してから残り通信を始める。

`_copy_verified_raw`は別のpartialへstream copyし、flush/fsync後にコピー先を再読してbytes/SHAを照合してから完了rawへrenameする。hardlinkや元assetの更新は行わない。元のHTTP日時/headersを保ち、コピー元asset/acquisition・bundle/marker・原provenanceのhashとコピー日時を`reuse_history`へ加える。新しい全窓の`decode_gfs`、source guard、bundle/receiptとassetの公開検査は省略しない。数値配列が同じでも来歴が異なるためbundle全bytes一致を再利用の条件にしない。

既知のコピーbytesは先に予算へ予約し、HTTPへ渡す残量から除く。新規通信bytesと再利用bytesを分け、`.reuse.partial`のコピー残骸は新規通信へ加算しない。原本の由来が完成前の障害で不明になった診断partialにも完全なコピー履歴が揃うとは保証しない。進捗の`checking_saved_raw`/`reusing_raw`は照合/コピーで、ネットワーク転送ではない。照合する完成候補の数に応じてファイル読取りが増え、OSのhash読取り等を含む即時取消や実行時間の保証はない。

`NomadsGateway`は同じOSユーザーの共有lockと最終完了時刻を使い、索引取得とGRIB取得、別service/CLIの間にも10秒以上の間隔を設ける。HTTP失敗時にも間隔を保ち、`Retry-After`が長ければそれを使う。固定のHTTPSホスト・経路以外とredirectを拒否し、自動再試行しない。lock待機とstream読取の間に取消を調べ、socket timeoutと経過時間deadline、長さ/総byte上限を検査する。DNSやブロッキングI/Oを含む全操作時間の厳密な上限ではない。

作業メモリ見積りは64 MiB＋171量×格子数×時刻数×192 bytes。取得APIでは512 MiBを超える要求を通信前に拒否する。serviceでは利用者がそれ以下の上限を設定できる。Python配列等を含む受入前の概算であり、プロセスRSSの上限保証ではない。正規化したgzipは部分名へ書いてから完了名へ移し、部分結果を選択可能な場にしない。

`decode_gfs(paths, specification, provenance)`はrawを正規化する境界である。
ecCodesでメッセージを読み、run・有効時刻・格子・単位・風の向き・瞬時量・欠測・必要フィールドを検査してから`balloon.weather/1`を作る。
全33圧力面の高度・温度・東西風・南北風・比湿と、地表気圧・地形・2 m温度/比湿・10 m風が必要である。
フィルターで一緒に届いた不要な組合せは記録して除外し、要求した量の代用品へはしない。
GFSの地形高度はecCodesの短縮名だけで判断せず、GRIBの識別と製品仕様で扱う。

`replay_gfs(acquisition_dir, output_path)`は保存要求と来歴を読み、期待するlead集合・ファイル名・URL・バイト数・rawのSHA-256を照合した後、同じ復号入口を呼ぶ。
出力は新規ファイルだけで、通信を行わない。復号ライブラリの版が変われば新しい版をメタデータへ残す。
同じデコーダーと同じ版での再生では決定的JSONとgzipヘッダーを使うが、異なるライブラリまで無条件に同一バイトを約束しない。

### スキーマ検証が照会の前提になる
`environment.storage.load_weather(bundle_path)`はJSONまたは`.gz`を読み、schemaが`balloon.weather.jra3q_surface/1`なら`jra3q.Jra3qSurfaceField`、`balloon.weather.jra3q_model/1`なら旧`jra3q.Jra3qModelField`、それ以外は従来の`environment.bundle.WeatherField`へ渡して各形式を検証する。以下は従来のGFS圧力面形式の説明で、共通補間は`fields.PressureLevelField`が担う。WeatherFieldはGFS予定時刻のvalidatorと粗地形の品質ラベルを明示的に渡し、JRAの時刻/列支持へ自動適用しない。JRA保存場の違いは[元時刻場の接点](#IM-HISTORICAL-NEXT)へ分ける。
plain/gzipともUTF-8（BOM可）として読み、重複キー、NaN、Infinity、1e999のように有限値へ表現できない数を`INVALID_JSON`で拒否する。
スキーマ`balloon.weather/1`の上層配列は`(time, pressure, latitude, longitude)`、地上量は`(time, latitude, longitude)`の順である。
時刻と緯度経度は昇順、気圧面は下降順を要求し、配列寸法・有限値・各列の高度単調性・地上量・配信時刻の内部欠落を検証する。
呼出元の辞書をそのまま保有せず、計算用配列をtupleへ変換しメタデータをコピーするため、後から入力辞書を変更しても場は入れ替わらない。

`geometric_to_geopotential(z)`と`geopotential_to_geometric(h)`は、それぞれmからgpm、gpmからmへ球面近似で変換する。
変換式・半径・限界は理論ガイドの座標節に置く。高度の種類をファイル名や値の大きさから推測せず、保存スキーマとAPIの名前で区別する。

### 照会は一つの高さで列を作ってから混ぜる
主入口の署名は次のとおりである。緯度経度はdegree、高度はm、時刻はUTCオフセット0を持つ文字列またはdatetimeである。
```python
WeatherField.sample(self, time_utc, latitude_deg, longitude_deg,
                    altitude_m, fields=None)
WeatherField.ground_altitude(self, time_utc, latitude_deg, longitude_deg)
```
`sample`の`fields`は重複しない既知の名前のlistまたはtupleで、省略時は風二成分・気圧・温度・比湿の五量を求める。
空、未知名、重複、文字列単体などの指定は`UNKNOWN_FIELD`で拒否する。
上昇一定速度かつ指数降下という簡易経路なら、積分側は風だけを要求できる。
欠けている不要量のために風だけの照会まで止めず、要求量の正の重みを持つ寄与に欠測があれば止める。

内部`_support`が時刻・緯度・経度の非ゼロ重みの組を作り、各列を同じ照会高度へ鉛直再構成してから、水平・時間で混合する。
気圧面の高度が時刻ごとに動くため、先に気圧面同士を時刻補間して別の高度列を作る手順へは置き換えない。
気圧は列内でlog補間、他量は線形補間し、列から返る実値を重み付きで混ぜる。
端点にぴったり一致する軸は一つの寄与だけとなり、重み0の欠測を読まない。

返値は要求したSI量に加え、`ground_altitude_m`、`quality`、`surface_bridge_height_m`、`terrain_stencil_clamp_depth_m`を持つ辞書である。
最後の二量は地上アンカーから最初の有効圧力面までの最大橋渡し厚さと、寄与列の地形より照会点が低かった際の最大地表延長量である。
混合地形より低い照会は拒否するが、混合地形より高くても一部の寄与列の地面より低い場合は、その列を地表値で延長し品質に明示する。
この扱いの理由と限界は理論ガイドの`THEORY-WEATHER`に説明した。

`ground_altitude`は同じ支持から地形Hを混合し、mへ変換した一値を返す。
現在の地形は粗いGFS地形であり、メソッド名が同じでも細密DEMを導入すれば接地の意味・試験・品質記録を変更する必要がある。

### 例外は支持不足を見える形にする
`WeatherError`は`ValueError`を継承し、`code`と`detail`を持つ。
外挿しなければ得られない時刻・場所・高度、地下照会、必要量欠測、形式不整合を、既定の0や近傍の別runへ代替しない。
現在のsimulateがstoppedへ変換する例外はValueError / KeyError / OverflowError / ArithmeticErrorであり、任意の例外すべてではない。WeatherErrorはValueError派生である。独自アダプターはこの境界とcodeの扱いを満たす必要がある。
エラー文字列を解析して復旧するのではなく、結果に残るコード・要求・支持範囲を確認して次の取得要求を作る。

## 運動層：モデルを選び、相とイベントを積分する
### 設定の受入と物理関数
`flight.config.validate_config(config)`は元の辞書をコピーし、`launch`、`ascent`、`burst`、`descent`、`integration`を検証して既定値を補う。
有限な数値、UTC、正の係数、モデルと破裂条件の組合せをここで受け入れる。
未知のmodeを近い既存modeへ丸めず、launch / ascent / burst / descent / integration内の未知キーを拒否する。一方、トップレベルの追加metadataは保持する。元の利用者入力を後から書き換えない。
既定値を含む採用設定は結果へ返すため、同じ計算の再実行で暗黙条件を探し直す必要がない。

`moist_air_density(pressure_pa, temperature_k, specific_humidity_kg_kg)`は湿潤空気密度kg/m³を返す独立した関数である。
`vertical_state(config, phase, altitude_m, sample)`は検証済み設定とその場の気象値から鉛直速度と確認用物理量を返す。
`flight/models.py`の内部`_density`が密度に必要な量、`_gas_state`が等温・内外同圧の体積・直径・面積を作る。
これにより、積分器に入る前に密度、浮力、抗力、降下式を独立に調べられる。

上昇は`constant_speed`または`isothermal_buoyancy`、破裂は`altitude`または`diameter`である。
直径破裂は気球体積を持つ等温モデルでのみ使う。
降下の`constant_cda`と`rated_speed`は別選択で、後者の密度は保存気象の`weather`または高度だけの`exponential`を選ぶ。
質量・抗力面積の形と基準降下率の形が特定の条件で同じになる理由は理論ガイドに示し、二つを同時に加算しない。

### 一飛行で使う評価を組み立てる

`compile_models(validated_config)`は現在の有限な設定を一度解釈し、`FlightModels(ascent, descent, burst)`を返す。各`PhaseModel`は`evaluate(altitude, sample)`と`required_fields`を持ち、各相に必要な設定だけを閉じ込める。gasの二量も独立して取り出し、`BurstEvent`へ気体計算のcallableとして渡す。イベントは上昇設定の辞書配置や等温mode名を知らない。

`flight/events.py`の`BurstEvent`は、符号余裕`value`、破裂時の`diagnostics`、指定速度/高度の`exact_step`、高度しきい値へ丸める`project_altitude`を担当する。trajectoryは束縛済み評価を呼び、物理modeの名前を判定して別式へ切り替えない。必要量が増えたときも、モデルの要求から場の照会へ伝わる。

これは既存`flight.config/1`を保った構造修復である。任意のプラグイン登録、熱/慣性を含む任意次元状態の飛行が完成したとはしない。新しい状態を追加する際は、状態schema・初期化・相遷移・記録・数値制御を明示して拡張する。

### 外部から呼ぶ飛行入口
```python
from balloon_sim.weather import load_weather
from balloon_sim.dynamics import simulate

field = load_weather("references/flight_fixture/hokkaido-weather.json.gz")
# config は COMMANDS.md の JSON 例と同じ辞書。
result = simulate(config, field)
```
`simulate(config, weather)`は設定を検証してから計算し、`balloon.flight.result/1`の辞書を返す。
気象オブジェクトに必要なのは`sample(..., fields=...)`と`ground_altitude(...)`である。
この依存を満たす解析場を試験に使えるため、ネットワークやGRIB復号を成功させないと積分器を試せない構造にはなっていない。

設定エラーは計算前の`FlightError`等として外へ出る。
計算開始後の支持喪失や数値・物理の拒否は、可能な範囲の記録を保つ`stopped`結果になる。
呼出側は辞書が返ったことだけで成功にせず、`complete`、`status`、`stop_reason`を読む。

### 進行の局所状態と、外へ委譲する計算を分ける
`flight/trajectory.py`の`simulate`内の`stamp`は打上げからの秒をUTCへ変え、`ground`と`sample_at`は場の照会と返値の検証を行う。
`rhs`が現在位置での球面移流と相の評価をまとめ、数値試行は`flight/numerics.py`へ委譲する。
`burst_value`は束縛した破裂条件、`make_record`は候補点の検証と辞書生成、`accept`は成功した記録と時刻/状態/相/歩数/イベントの一括採用、`failure`は停止理由への変換を担う。`locate_crossing`はnumericsからimportする根探索である。
これらはクロージャ内で一飛行の設定を共有する内部実装であり、安定した外部APIとして個別にimportする対象ではない。

積分段ごとに気象を引き直す。破裂か地面の交差を見つけたら、そのイベント時間をdense補間とbrentqで求めて採用し、破裂では降下へ切り替えて積分器を再初期化する。指定速度/高度破裂の場合は、残り高度から計算した正確な破裂時間も使う。
降下中の地面到達だけが`landed`となる。上昇中の地形衝突、最大時間・歩数、場の支持不足は途中停止として保存する。
根を挟むRK段だけ地表で気象を照会する回数は`ground_clamped_stage_queries`へ記録する。
気象上端が破裂高度と同じだけでは、等温上昇の根を挟むための上側の試行が支持外になり、直前停止することがある。定速上昇の解析的な破裂刻みとは異なる。取得余白を用い、支持端を明示するadapter/イベント契約を受け入れるまでは上端外挿しない。
有限刻みで狭い障害物を完全に検出する仕様ではなく、熱・水平慣性・鉛直慣性を含む一般運動方程式もまだ提供しない。

### 数値adapterと飛行固有の受入

`numerics.AdaptiveRK45`は右辺と最終時刻、相対/成分別絶対許容誤差を受け、`trial(time, state, maximum_step)`でSciPyの一採用区間を返す。`IntegrationStep`は開始/終了時刻、終端state、`state_at(time)`によるdense補間を持つ。`locate_crossing(step, function, tolerance, *, start_time=None)`はその区間内の時間根をbrentqで探す。場・物理・相はimportしない。

`relative_tolerance`の既定は1e-9で、100×double epsilon未満を拒否する。`absolute_tolerance`は`latitude_deg`/`longitude_deg`各1e-9、`altitude_m`1e-3が既定で、正の有限値を要求する。`max_step_s`は固定刻みではなく上限であり、`event_tolerance_s`はbrentqの時間`xtol`である。単位と数値的意味は理論ガイドの積分節に示す。

SciPyの通常誤差制御と、本体による支持外試行の破棄を区別する。trajectoryは場の拒否や途中地形の検出で上限を縮め、最後の採用状態からやり直す。内部段に加えdense区間中点も地形照合するが、狭い障害物・多重交差の完全検出ではない。結果は採用点とイベント点を不等間隔で保存し、固定間隔の再標本化は行わない。

### 返値を読む順序
まず`status`と`complete`で終端を判断し、失敗なら`stop_reason`を読む。
次に`events`の破裂・着地・衝突、`summary`の飛行時間・最大高度・採用歩数・接地位置を確認する。
`records`は時刻、経緯度、高度、地形高度、地上高、相、風、鉛直速度、参照した物理量、気象品質を持つ。
地上高のキーは全層で`height_agl_m`で統一する。
`config`は実際に採用した設定、`model_assumptions`は結果解釈に必要な仮定である。`numerics`はbackend、event solver、SciPy/NumPy版、相対/成分別絶対許容誤差、時間根許容誤差、最大刻み、記録点の意味を保持する。
破裂では上昇側の到達記録とイベントを先に採用し、下降側の初期評価を別に受け入れる。下降必要量が欠ければ上昇の破裂点と最大高度を保って停止する。成功時は同時刻の上昇/下降2行が現れるため、時間が重複したことだけで不正と判定せず、相とイベントを読む。

## CLIと保存：利用者の一回の操作を再現可能にする
### 四つの操作を同じ入口で扱う
`main(argv=None)`が`fetch`、`inspect`、`replay`、`simulate`を選ぶ。
CLIは共通の`environment.storage.read_json(path)`を使い、UTF-8（BOM可）を読み、重複キーやNaN/Infinityを拒否する。
PowerShell等からの正しい引数、必要な環境、終了コード、再開例はコマンド一覧にまとめる。
CLIの責務はエラーを黙って消すことではなく、計算前の拒否と記録済みの途中停止を明確に返すことである。

`results.export.export_result(result, config_path, weather_path, output_dir, weather_metadata)`は新規ディレクトリを作る。
元の設定バイトを`input.json`、計算結果を`result.json`、入力とパッケージ配下を再帰列挙した全`.py`の相対パス・SHA-256を`provenance.json`へ保存する。
続いてCSV、GeoJSON、HTMLを生成し、最後に各成果物のバイト数とハッシュを`manifest.json`へ記す。
manifest自身は自分のハッシュ一覧に含まない。途中のI/O失敗ではディレクトリが残り得るため、存在だけを出力完了の根拠にしない。
元入力と既存出力は上書きしない。結果の`numerics`もprovenanceへ保存し、同じコードでも異なる数値依存版の結果を無条件に同一とは扱わない。

### 表示は計算結果の解釈を助ける
`make_geojson(result)`は`(longitude, latitude, altitude)`順のLineStringとイベントPointを作る。
`results.report.render_report(result, provenance)`は外部通信なしの単一HTMLを返し、軌道、高度と地形、時刻スライダー、採用モデル、来歴、成果物リンクを表示する。
内部`_trajectory_svg`と`_altitude_svg`は描画だけを担当する。
水平図の局所平面への射影に使う平均緯度は表示用であり、軌道式の現在緯度による地図因子とは別である。
背景地図や海岸線を載せていないため、着地地点の地物判定はこの図だけで行わない。

文字列はHTMLへエスケープし、JSONは埋込時に閉じタグを安全に扱う。
それでも保存された場が科学的に妥当であること、地点が安全であることまで表示層は保証しない。
HTMLの見た目の確認、JSON/CSVの照合、実際の物理的精度の評価は、別の受入項目として記録する。

## 新しいモデルや製品を足すときの順序
変更の入口は「追加関数を書くこと」より先に、何を比較したいか、既存選択とどう組み合うか、必要な入力と状態が何かを定めることにある。
たとえばRe依存抗力は抗力則の変更であり、鉛直慣性の導入は状態変数の追加である。
両者を一つの排他的modeへまとめると効果を分けて試せないため、契約の構成表で独立な軸と禁止組合せを明示してから実装する。

本版の有限なmode選択は初期モデルを実装するための形である。未実装の任意プラグイン登録APIや任意次元状態の積分器が既にあるわけではない。
熱モデルでは気体温度などの状態、エネルギー式、放射/伝熱量、初期条件が増える。
その変更時に設定スキーマ・照会量・状態・返値・説明・試験をまとめて拡張し、等温・慣性なしの極限へ戻る比較を残す。
初期実装の前に温度差の感度試験を必須化したり、追加飛行実験を要求したりしない。

別の気象製品はまず保存スキーマへの正規化を作り、時刻・座標・鉛直面・単位・欠測・地形の意味を保証する。
次に同じ`sample`契約を解析場の試験と実データ例に通す。JRAの気候統計DBを直接時刻指定の場として使うことは、この工程の代わりにならない。
全国用途では地域名を分岐条件にせず、取得範囲と入力地点を変えて同じ経路を通す。
将来の細密地形は気象場の地上近傍処理との整合が必要であり、地形ファイルだけ差し替えて接地の意味が維持されるとはしない。


<a id="IM-HISTORICAL-NEXT"></a>
### 元時刻のJRA場を同じ飛行核へ渡す接点（0.51・固定原本のCLI接続）

この小節は0.51のstrict経路と当時の不足を保持する。地上接続は後続の[0.52節](#IM-JRA-SURFACE)で明示的に選び、同じ保存schemaの意味を変更しない。

0.50の接点案を、保存済み2024-01-01 00/06 UTC・100層・2×2格子から飛行を計算する経路へ具体化した。旧`tools/normalize_jra3q_model_fixture.py`と原`references/jra3q_model_fixture/source_bundle.json`は、固定原応答の検査・復号と旧queryの対照として保持する。半月統計DBから原日時の共同場を復元する実装ではない。操作はCOMMANDS C-10、実行結果と採否はS36へ戻る。

| 実体 | 今回の責務 | ここで行わないこと |
|---|---|---|
| `environment/model_levels.py` | `ModelLevelField`が幾何ASL mを受ける`sample`で列ごとのH/gpmへ各要求量を再構成して水平・UTC内挿し、`ground_altitude`で地表の幾何ASL mを返す | 製品の暦・取得・保存I/O、地表gapの補完 |
| `environment/jra3q.py` | `Jra3qModelField`がschema/product、解析UTC、100層、固定半層係数を検証し、各時刻/列の地表圧からfull圧力を作る | GFS run/lead規則の流用、未知の係数版の自動受入 |
| `environment/storage.py` | 保存schemaから場を選び、従来の厳密JSON/gzip読取を共用する | 取得や不足原本の探索。JRAをGFS名で登録すること |
| `tools/prepare_jra3q_flight_fixture.py` | 旧loaderで固定原本を照合し、新bundleを検証・新規保存・読戻しして変換receiptを作る | 任意日時のJRA取得、稼働中の場の差替え。飛行packageからこのtoolsへの依存 |

保存schemaは`balloon.weather.jra3q_model/1`、productは`jra3q.ncar.regular_gaussian.model_analysis`である。`axes`に`time_utc / model_level / latitude_deg / longitude_deg`、`fields`にH/gpmとT/u/v/q等、`surface`に地表圧Paと地表H/gpm、`hybrid`に101個の`a_half_pa / b_half`、`metadata`に来歴を置く。上層は`(time, model_level, latitude, longitude)`、地表は`(time, latitude, longitude)`の順で、モデル番号は地表側から1〜100。pは保存された代表軸から読まず、各列のSPと半層係数からSimmons–Burridge式（最上層は下側half圧力の1/2）で再構成する。

半層係数はfloat正規化した[A,B]のSHA256を`COEFFICIENT_SHA256`へ固定している。端点・単調性・100層だけ合う別係数を受け入れず、変更は製品版の明示確認を要する。保存時刻は00/06/12/18 UTCで隣接差が6時間となることを検査する。ただし、これは**保存された列の内部連続性**であり、利用者が必要とした先頭/末尾時刻の存在を証明しない。単独の解析時刻も形式上は許容され、その瞬間以外の照会は支持外になる。現在のCLIに「放球＋最大飛行時間」の事前被覆計画はなく、要求窓と保存窓を別に照合し、照会時の窓外は`TIME_OUT_OF_RANGE`として読む。GFS取得APIの窓検査がJRAへ接続済みとは扱わない。

`ModelLevelField`は各正重み列の実H上でpを含む要求量を線形補間してから、水平/時間で混ぜる。旧JRAのp線形を保持し、従来GFSのlog(p)補間へ変更していない。高度APIは既存の球近似（R=6371000 m）で幾何ASL mからgpmへ一度変換する。幾何30000 mは約29859.397 gpmであり、30000 gpmの旧queryと同じ高度ではない。密度は内挿したp/T/qから既存の物理モデルが求める。ここで密度を直接内挿したり、静力学的整合の新しい保証を加えたりしない。

地表Hを内挿して返せても、その高度の気象が支持されるとは限らない。正重みの各列が要求高さを支える必要があり、地下は`BELOW_MODEL_SURFACE`、最下層までの空白は`HEIGHT_OUT_OF_RANGE`、必要値の欠測は対応する支持エラーで止める。近傍列を捨てて重みを再正規化せず、GFSのsurface bridgeやterrain clampも適用しない。今回の原列の地表–最下層差は約8 gpmだが、水平/時間内部点では周囲の高地列も必要なため共通下端までの差は約123 gpmになる。地表をそこへ引き上げて着地を作らない。返値`quality`に球近似・厳密列支持・p線形・粗いモデル地形を残し、細密DEMとの一致を意味しない。

入力配列はtupleへ変換しmetadataをcopyする。固定原本の変換では、元bundleと各ASCII応答のhash/完了状態・変数/単位/軸を旧loaderで照合し、`metadata.source`へprovider・URL・原応答票・係数・原本hashを保持する。静的GPの識別時刻1947-09-01は原来歴に残すが、2024年の気象有効窓へ混ぜない。変換toolのsource hashは`metadata.preparation.source_files`、飛行時のpackage sourceと場/設定hashは従来の`provenance.json`へ残す。通常の`load_weather`がraw原応答へ戻って再検算するわけではない。

変換toolは既存出力先を拒否し、gzipヘッダーを固定して`weather.json.gz`を新規作成する。JSON payload全体と読戻した場を照合した後、bundle hash/bytesと段階別時間を変換`receipt.json`へ保存する。I/O失敗で部分出力が残る可能性はあるので、directoryの存在を完成としない。これは非上書きの保存規約であり、OS側でファイル変更を禁止する仕組みではない。`inspect`は正規化bundleを検証してmetadataを返し、`simulate`は同じ飛行核・出力形式を使う。

今回の診断例は短い定速計算だけでなく、非native放球UTCで等温浮力上昇→指定高度破裂→気象密度による下降→下端支持不足という行程を扱う。支持不足では有効履歴と破裂を保持して`stopped / complete:false / landing:null`を保存し、CLI終了2を返す。地表開始・時刻窓外・水平外の停止と幾何30 kmでの照会は別の観察として扱い、30 kmまでの全軌道完走や着地精度の証拠へ広げない。0.51時点の接続はCLIに限定し、HTTPのweather-source登録、過去場取得UI、実飛行との照合、地上完飛行と季節MCは未実装であった。0.52の一窓で追加する範囲は次節へ分ける。

次の地上接続用取得は、飛行の開始〜最大時間を挟む全予定時刻、100層T/q/u/v/HGTと地表p・2mT/q・10m風、静的GP、水平の補間余白を一要求群として見積もる。float32の単純な配列量なら`4 × 時刻数 × 格子数 × (5 × 100 + 5) + 4 × 格子数` bytesだが、導出p・座標・欠測・原本・Python配列・復号時メモリは別に加わる。転送量やRSSの実測値ではない。製品経路・情報締切・長期のマスク/対応標本は[気象ガイド](WEATHER_DATA_GUIDE.md)へ戻し、この接点案から一般取得器や過去場MCの完成を主張しない。

<a id="IM-JRA-SURFACE"></a>
### 明示的なJRA地上再構成を保存し、同じ核へ渡す（0.52）

`environment/model_surface.py`の`ModelSurfaceField`は検証済み`ModelLevelField`を包み、B方式の`sample / ground_altitude`を提供する。取得・製品暦・保存I/Oは持たない。`jra3q.Jra3qSurfaceField`が新schemaと地上解析量を検証し、元の`Jra3qModelField`でUTC・係数・原列配列を検査してから包む。`storage.load_weather`がschemaを選び、CLIが得た場を既存flight核、既存resultsへ渡す。旧strictやGFSを自動でBへ替えない。

| 保存契約 | 固定するもの |
|---|---|
| schema / product | `balloon.weather.jra3q_surface/1` / `jra3q.ncar.regular_gaussian.model_surface_analysis` |
| 原モデル量 | strictと同じ`axes / fields / hybrid`。SPから各元列のfull pを生成し、既知係数SHAを照合する |
| `surface` | 既存`pressure_pa / geopotential_height_gpm`に`temperature_2m_k / specific_humidity_2m_kg_kg / eastward_wind_10m_m_s / northward_wind_10m_m_s`を加える。すべて`(time, latitude, longitude)` |
| `reconstruction` | `policy: native_horizontal_first_surface_v1`と`join_model_levels`だけを受ける。整数でp/T/qは1、u/vは2の五量を必須にする。未知policy・余分/不足キー・別joinは拒否 |

原UTCごとに正重みの水平支持を作り、native面ごとのH/Fと地表量を混合する。各仮想列の同じ絶対Hへpを含む要求量を線形内挿し、最後に時間重みを掛ける。pは原列のfull pを平均するB1であり、平均SPからfull pを作るB2ではない。全高度でstrictと値が異なり得る。上端も、原列すべてが同じHを支えるというstrictの共通上端から、各原UTCの仮想列上端へ変わる。保持したnative配列を延長する実装ではないが、元の全列共通支持と同一とも説明しない。

仮想地表の幾何高度から2m/10mを加えてHへ戻し、pはSPからlevel1、T/qは2mからlevel1、u/vは10mからlevel2へ結ぶ。診断高度以下は定値にする。native level1の風は置換対象で、他の量のlevel1は残す。`_validate_fixed_joins`は保存窓の全原UTC・全列の地形/指定join高さが存在し、各アンカーより上であることを構築時に検査する。照会ごとに都合のよいjoinを探して切り替えない。

欠測には二段階がある。構築には全窓の固定join幾何が必要で、照会時には正重み支持の全native高さが仮想列を作れる必要がある。要求する量の消費節点・必要な地上解析値は、平均前に有限性と物理範囲を検査する。不要量の地上診断欠測を無条件に照会しない一方、橋を使う場合はアンカーより下の定値区間でも固定joinの値を要求する。元の消費native節点が地中、p>SP、必要値欠測なら拒否し、列を落として再正規化しない。モデル地表より低い照会は拒否し、高さ変換の丸め許容以外の地形延長は行わない。

時刻・水平範囲・未知field・形式不正の拒否は既存の`WeatherError`に従い、支持外を標準大気へ埋めない。旧strictの保存schemaはそのまま読める。A案の各列地表値延長は比較実験として残り、今回の現役policyには登録しない。任意JRA窓の取得、HTTPのweather-source登録と選択UI、季節MCはこの変更に含めない。

`metadata`には元の資料/正規化来歴を保ち、新schema/product、`reconstruction_policy`、join、鉛直/圧力/時刻の順序、`native_wind_not_used_model_levels:[1]`、近似の範囲と検証境界を加える。sampleの`quality`にはpolicy・球近似・モデル地形を、橋を使った際には`surface_layer_bridge`や定値保持・風level1不使用を残す。`surface_bridge_height_m`は今回照会が使う橋の地表からの最大厚さ、`terrain_stencil_clamp_depth_m`はBで0である。これらは誤差推定でも橋内の滞在時間でもない。

同じ`results.export`が設定/場のbytes hash、package source、数値依存と`weather_bundle.metadata`を`provenance.json`へ、採用点の`weather_quality`を結果/CSVへ保存する。原応答・正規化・再構成の識別は区別する。通常loadやinspectが元raw11応答を再読して真正性を検証するわけではない。 固定例の`metadata.input_bindings`と`builder_sha256`は厳密場/地上診断/正規化票と結合作業を識別する。来歴中の取得時の絶対pathは履歴の所在であり、通常実行の依存ではない。保存場に含む配列を使い、原物の保全先は`metadata.evidence_archive`から辿る。保存済み例の再実行は[COMMANDS C-11](COMMANDS.md#C-11)、原本取得・正規化・A/B/刻み比較と未確認は[S36](../BOOTSTRAP_RUNBOOK.html#s36-plan520)へ戻る。モデル地形への着地は細密DEMや実着地誤差の保証ではなく、定値/H線形接続は境界層・静力学・保存則を再現しない。

0.52の上記説明は再構成とCLI接続の記録として保持する。後続の保存例登録・GUI選択・固定結果の扱いは[0.53候補の接点](#IM-JRA-GUI)へ戻る。新しい実行・画面受入の結果はS36へ記録し、旧科学説明へ成功実績を上乗せしない。

## 検証と現役性

主要Python APIの識別子、署名、所在、導入・意味変更・確認の時点、現役性、対応試験は [IMPLEMENTATION_INDEX.json](IMPLEMENTATION_INDEX.json) に置く。既存核の17公開APIは0.20.0導入。0.45のローカルservice入口を追加し、TypeScript/HTTPの手動読解をPython AST署名と分ける。0.24.0では実定義と旧公開経路を分け、署名とimport実体の両方を照合する。私有ヘルパーは親機能の説明へ属し、個別の安定した公開APIとはしない。別の利用先を持つ、または公開する変更時に入力・返値・例外・依存・寿命を受け入れる。

| 対象 | 検査が守るもの | 入口 |
|---|---|---|
| 場の読取と照会 | アフィン場、log気圧、動く高度列、端点、欠測、地上アンカー、地形延長、形式拒否 | `tests/test_flight_weather.py` |
| 保存JRAモデル面と飛行接続 | 旧query対照、独立列期待値/圧力、地表支持不足、任意時刻、相遷移、欠測/係数/保存形式の拒否 | `tests/test_jra3q_flight_field.py`。旧試作との対照は `tests/test_jra3q_model_environment.py` |
| 明示JRA地上再構成 | 原UTC別B1、変数別join、level1風置換、仮想上端、正重み欠測、schema/metadataと旧strict保存 | `tests/test_jra3q_surface_field.py`。実過去窓の全飛行・費用はS36へ分ける |
| 取得・復号・再生 | 時刻・領域計画、バイト上限、既存出力拒否、raw改変拒否。実製品は実取得の受入記録も参照 | 同上、BOOTSTRAP S26 |
| 設定・物理式 | 型、モデル組合せ、密度、浮力抗力、直径破裂、非正揚力、要求量の分離 | `tests/test_trajectory.py` |
| 数値adapter | 解析式、成分別誤差、dense補間、両方向の根、非有限/試行拒否の境界 | `tests/test_flight_numerics.py` |
| 全飛行 | 解析時間、球面積分、時間変化風、斜面接地、現在緯度、支持境界停止、刻み比較 | `tests/test_trajectory.py` |
| CLIと出力 | 実場2例、通信禁止反復、終了2の保存、JSON拒否、GeoJSON/CSV順、指紋、既存出力保持、API署名 | `tests/test_flight_cli.py` |

解析解との一致は特定の数値・物理処理の検証、実GFSの反復一致は保存入力からの再現経路の検証である。全国全期間の成功、実気球の着地誤差、配布先の将来稼働を証明しない。API索引のAST照合は署名と試験パスを検査し、説明の科学的正しさまでは判定しない。HTML表示、文書の構造検査、PDFのページ目視も、それぞれの範囲を区別する。実行条件・終了値・未実行理由は指示書の同じ手順へ戻す。

既存toolsのモデル面・他製品・構成・長期予報計画は、本体が自動で選べる機能ではない。正式アダプターへの昇格時に保存契約と全飛行試験を接続する。現在の比較・回帰・根拠として残し、置換時には固有証拠と使用先を確認して残存／統合／退役を判断する。正本はCONTINUITY_CONTRACTとCONTENT_MAPであり、古いことだけを理由に削除しない。

## 0.24の構造修復と、旧構造ガイドからの移送対応

0.24では0.21の実ファイル図とsimulate内部図を、environment/flight/resultsの実体に合わせて置き直した。旧weather→environment、旧dynamics→flight、旧cli内の結果生成→resultsであり、互換入口は別実装を持たない。下表は0.20→0.21時の情報移送を保存した履歴で、当時の「5実ファイル」は現在のファイル数ではない。今回の受入はD-162/D-163とS32へ残す。

比較した旧版はM200の `docs/PROGRAM_GUIDE.tex`（PDF 8ページ）。単に短くして詳細を失わないよう、次の受入先を定めた。旧PDFのページ番号は物理ページである。

| 旧版の内容 | 新しい受入先 | 維持した意味 |
|---|---|---|
| 表紙・目次、1節「全体を分けた理由」 | 構造ガイドの読方・物理配置・依存図、本ノート冒頭 | 取得→保存場→飛行→出力、ネットワーク境界、読む目的 |
| 2節「モジュールの境界と実行依存」 | 構造ガイド5実ファイルとimport/duck typing図、本ノート冒頭・現役性 | 実体と責務、Python/復号依存、tools未接続、残存判定 |
| 3節「気象層」 | 本ノート「気象層」全文、構造ガイドweatherの4階層 | 取得制約・raw保持・厳密読取・配列・照会順・品質・例外 |
| 4節「運動層」 | 本ノート「運動層」全文、構造ガイドdynamics/内部図 | 設定、モデル選択、場の契約、内部関数、イベント、返値 |
| 5節「CLIと保存」 | 本ノート「CLIと保存」全文、構造ガイドCLI2頁 | 出力責務・指紋・I/O失敗・GeoJSON順・表示投影・未検証範囲 |
| 6節「新しいモデルや製品」 | 本ノート同節、構造ガイド変更逆引き | 独立な比較軸、追加状態、未実装API、等温拡張、追加実験を要求しない境界 |
| 7節「変更と試験と説明」 | 本ノート「検証と現役性」、構造ガイドtests/逆引き、IMPLEMENTATION_INDEX | API時点・試験対応・内部公開基準・証拠の適用範囲 |
| ガイド生成と表示確認 | BUILD、構造ガイドTeX冒頭、S28実績 | TeX編集元→PDF/検索txt、単冊生成、全頁表示とリンク確認を分離 |

構造ガイドは上位から子へ降りる図と短い責務説明に集中させた。本ノートへ移した詳細を図の吹き出しへ全て詰め戻さない。実装が変われば、構造・ノート・理論・操作・API索引・試験のうち意味が変わる受入先を同じ変更で更新する。
<!-- LOGIC:IMPLEMENTATION-NOTES:END -->
