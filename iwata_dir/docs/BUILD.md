# 編集元・生成・検査

[更新:0.55.0] [確認:0.58.0] — BUILD / REV-550-CURRENT-BUILD

## 役割

HTML指示書はBOOTSTRAP_RUNBOOK.htmlを直接編集する。JavaScriptは表示とコピーのみ、状態は静的本文。文書全体の別原本を作らない。

長期計画はdocs/PROJECT_PLAN.mdとtools/template.texが編集元、tools/build_docs.pyがPandoc→TeX→XeLaTeXでdocs/PROJECT_PLAN.tex/.pdfを生成する。生成TeXを独立に編集しない。参考用Program_Guideはユーザー提供の原PDF/TeXで、このビルドの対象ではない。

計算核は`balloon_sim`、0.45の画面とローカルサービスは`frontend/`・`backend/`、現在の操作の入口は[コマンド一覧](COMMANDS.md)。理論・構造ガイドは`docs/THEORY_GUIDE.tex`/`docs/PROGRAM_GUIDE.tex`を編集元とし、末尾の専用生成手順でPDF/検索用textを作る。旧Program_Guide原本やPLAN一組をこの生成へ取り替えない。保存気象場からの軌道計算と、新しいネット取得、原GRIB再読、資料生成は依存と副作用が違うため、目的に応じて実行する。

### 0.50：既存画面・予報取得・感度集合・保存風統計を起動する

`frontend/package.json` とpackage-lock.jsonがReact/TypeScript/Vite/Leaflet/Plotly/Cesiumと検査依存を指定する。`npm --prefix frontend ci`、`npm --prefix frontend run build`で、型検査後にdistを作る。用途別画面の具体的な出典と改修は`frontend/SCREEN_PROVENANCE.md`、第三者の告知は`frontend/scene3d/THIRD_PARTY_NOTICES.txt`へ戻る。3D rendererの現役ソースは`frontend/scene3d/`、Cesium配布物はnpm依存からbuild時に生成し、distの`scene3d/`と`cesium/`を同じoriginで配信する。Node下限はpackage.jsonへ、実際の使用版と成否はS36/REFERENCE_LOGへ戻す（0.46の統合実績はS35）。lockfileはソース、node_modules/distは再生成可能なruntimeである。

`backend/pyproject.toml` はPython3.12とFastAPI/uvicorn/数値・復号・測地依存、`requirements.lock` はその版と検査依存を固定する。backend/.venvへ導入し、repoルートから `backend.app:create_app` をuvicorn factoryとして起動する。rootへのeditable installや既存核の移動は不要。数値計算は既存核を呼ぶ。0.47の予報取得にはecCodes/NumPy、中心と片幅からの範囲設計にはGeographicLibを使うため、画面用lockへecCodes 2.48.0とGeographicLib 2.1を追加した。0.49の提供JRA-3Q集計DB読取はDuckDB 1.5.5を同じlockへ加える。DuckDBの拡張や外部DBを自動取得する構成ではない。保存場だけを読む既存CLIにまでecCodesを必須化しない。依存不足では画面に不足名を示し、サービスが自動導入しない。具体コマンドはCOMMANDS C-09、APIと保存形式はIMPLEMENTATION_NOTESを読む。

0.48の集合計算は同じ数値環境で動き、NumPyのPCG64/eigh/quantile、SciPyのConvexHull、GeographicLibのWGS84変換を使う。新たなブラウザ側科学計算環境や別worker poolを必要としない。原気象の再取得を伴わない感度検査には固定保存場を再利用する。計算用sourceは起動時に指紋を固定するため、変更したまま新計算を始めずserviceを正常終了・再起動する。0.49のworker指紋はPython版/実装・NumPy・SciPy・GeographicLibの版を照合する。全依存の完全固定ではなく、DuckDB版は風統計側の資料・集計identityへ別に記録する。

保存風統計を使うときは、起動前にrepo外の提供v1 DBを`BALLOON_CLIMATE_DB`、任意の期待SHAを`BALLOON_CLIMATE_SHA256`へ指定する。具体例はCOMMANDS C-09。元DBをruntime rootやGitへコピーせず、read-onlyで識別・支持を検査する。未設定/不一致でも保存済み集計を`BALLOON_DATA_DIR/climate.sqlite3`から読む経路は分ける。DBを交換したら、稼働中設定を書き換えるのではなく正常終了・明示再登録する。DuckDBの128 MB buffer/1 thread/temporary disk 0 Bはadapterの設定で、Pythonを含む実メモリの上限保証ではない。

`tools/run_checks.py` のunittest回帰には、純粋核の `tests/test_ensemble.py` を含める。frontendのVitestとbackendのpytestは含めないため、COMMANDS C-09の `npm --prefix frontend test` と専用Pythonでの `pytest backend/tests` を別に実行する。

通常画面は8451、Vite開発は8450、previewは8452でAPI8451へproxyする。frontendビルド済みならbackendが同一originで配信する。数値計算は保存場を使い外部通信しない。通常画面の地図表示は地理院背景を取得し、未接続を選ぶ項目は0.47で除いた。NOMADSの索引観測/取得は明示操作からだけ起動し、poll/計画/保存再読で外部予報を取得しない。同一の正規化要求・復号器に対応する完成bundleの再利用に加え、0.50のbackend取得は登録済み完成assetの共通rawを検算・独立コピーし、不足時刻だけを取得する。新全窓の復号/公開検査を省略しない。既存CLIは省略可能なraw_providerを渡さないため、backendの資産共有を自動利用するとは扱わない。実風統計はローカルDBを読み、年間図は地図要求を行わない。地域図とその背景入りSVG保存は地理院へ通信する。Google写真3Dは利用者の明示接続まで通信せず、キーをprojectやGitへ保存しない。pip/npmの依存導入時の通信とは区別する。

正本の列挙から外すruntimeは `frontend/node_modules`、`frontend/dist`、`backend/.venv` の3rootだけ。一般.gitignoreの全patternを検査除外へ転用しない。登録pathをその配下に置く、rootをfile/link/reparse pointにする、未登録sourceを他の場所へ置く場合はcheck_stateが拒否する。依存内の第三者src等は正本監査の対象外で、安全性確認済みという意味ではない。利用状態はrepo外のBALLOON_DATA_DIRへ置き、distへ保存しない。

構造ガイドを変えた場合はPROGRAM_GUIDEを `--guide PROGRAM_GUIDE` で独立コピーから生成し、全ページを表示点検してTeX/PDF/txtを揃える。0.48の標本・包含域・履歴集計に続き、0.49の風統計の定義をTHEORYへ加える場合も、THEORY_GUIDEを別の独立コピーから生成する。PLAN一組は変更しない。0.46のPLAN生成、0.47のPROGRAM生成とTHEORY維持は当時の記録として残る。現在の作業状態はS36、取得仕様はWEATHER/IMPLEMENTATION_NOTES、現階層はPROGRAMへ戻し、未読の資料の確認印を一括で上げない。生成・ビルド・試験・実UI・科学的受入は別の証拠である。下記0.24以下の実行版・頁数・成功記録は当時の観測として保持する。

### 0.55：固定要求の回復と原日時窓の有限接続

依存lockと科学核は維持し、現在の予報取得・単便・集合を同じサービスへ渡す。送信前の要求をブラウザへ保存する仕組み、保存台帳instanceの識別、同originの単一送信タブはそれぞれ異なる責務である。Web Locks非対応や台帳照合不能の状態を、書込可能へ無言で代替しない。具体的な再開操作と制約はCOMMANDS C-09、契約はIMPLEMENTATION_NOTESへ戻る。完成物の検算回復と壊れた計算poolの受付停止を、計算の自動再実行と混同しない。

過去窓は任意の原UTCと保存場の対応をカタログで明示する。`BALLOON_HISTORICAL_CATALOG` は起動時に読み、登録済みの窓を共通機体の固定計画へ渡す。気象分析用DBと原日時の場は別の入力であり、提供半月集計から瞬時の場を生成しない。選んだ3窓のうち2窓が着地し、未取得1窓を台帳に残す有限例はS36/ACT-550へ戻る。

独立runtimeは全sourceのmanifestへ束縛し、前節の分類来歴用FE3実体も含める。frontendの表示修正は既存計算のruntimeを無断で置換せず、buildごとの入力hashと出力を記録する。最終ビルド・回帰・正常再起動・実UIは異なる検査票である。今回の最終publicationと保存完了はS36へ戻り、以下の0.54以前の頁数や成功を0.55の証拠に転用しない。PDFは従来の専用生成器と視覚確認を使い、PLAN一組は変更しない。

### 0.54：現在予報を使う行程と状態確認の回復

依存lockと飛行核は継承する。GET観測は専用の期限付き読取と単便/取得の共通observerへ、モデル地表の読取は既存気象構築へ委譲し、明示applyを入力編集へ戻す。操作はCOMMANDS C-09、契約はIMPLEMENTATION_NOTES、構造はPROGRAMに記す。稼働中sourceの差替えをせず、変更版の独立runtimeと独立状態で受入してから正常終了/再起動する。

独立runtimeへ必要sourceだけを複製する場合は、Python核/backend/examples/fixtureに加え、集合の来歴が参照する `frontend/src/screens/forecast/math.js`、`controller.js`、`shared/scene-style.js` の実体も必要である。0.54の最初の74path複製はこれを欠き、analysis500となった。後の77path manifestと新しい複製手順/4反例をACT-540へ保存する。これは通常repoルート起動の必要pathを削ってよいという仕様ではない。

PROGRAM27頁の新しい監視/地表照会の階層と接点を編集し、THEORY22頁は現在位置の説明/表紙を更新した。旧数式・科学採否の全面改訂ではない。実際の生成hash・全頁配置確認・変更頁視認・最終出版はS36/ACT-540の票を読む。PLAN一組は変更しない。

### 0.53：保存実JRAを既存GUIで計算・比較・再開する

保存JRAの明示schema/policyを既存backendの気象一覧へ登録し、同じworker/load_weather/simulate/exportを用いる。新しいsolver・HTTP取得経路・実行依存は追加しない。JRAの支持を予報run/leadやpressure_pa軸へ読み替えず、既存GFSと製品別に表示する。保存入力の日時は秒まで保持する。起動・適用・保存の実コマンドはCOMMANDS C-09、sourceの内容照合と旧結果の扱いはIMPLEMENTATION_NOTESへ戻る。

今回のfrontend/packageとbackendサービスの表示版は0.53としたが、核の互換version表示や旧保存結果を一括置換しない。成果物は固定source hashで識別する。テスト用API8530/検査proxy8531と独立stateを使用し、proxyは外部背景をCSPで遮断する。これは製品の新しい背景選択肢ではなく有限検査の環境である。計算は保存場を使用し、Google接続と新しい気象取得は必要ない。稼働sourceを交換する場合は、保存stateを保全し正常再起動してから新計算を行う。

PROGRAM27頁/THEORY22頁を既存TinyTeX/XeLaTeX・FONTCONFIG_FILEで外側生成し、最終警告0。PROGRAMは保存source登録→固定case→現在sourceの別照合→既存画面の階層/接点を追補し、p8の変換引数の誤記を訂正した。THEORYは導入の接点と確認範囲を更新し、旧科学式の再認定は行っていない。`guides-build-final530/build.json` と `guide-review530/guides-final-review530.json` が生成/有限視認の根拠で、`docs-publication530.json` の前後hashでTeX/PDF/txtを正本へ反映した。最終修正は両表紙のみで、先行修復後の他47頁と画像が一致する。PLAN一組や生成器は変更しない。

機能検査ではbackendの34成功/5期待失敗と訂正/追加を含む7成功、frontendの110成功と後続1成功・型/build成功を区別する。Temp拒否・spawn EPERM・syntax失敗を消さず、対象sourceと実行票をS36/REFERENCE_LOGへ戻す。最終管理検査・Git保存はこれらの成功に含めない。GUIで作った3入力は各独立CLIと全result/provenanceが一致したが、有限な同一性の確認であり、任意過去取得・多数年MC・全UI/科学精度の受入ではない。

### 0.52：実過去窓の地上接続と実行例

保存された `references/flight_fixture/jra3q-weather.json.gz` を既存Python/SciPy/NumPyのCLIで読む。新しい実行依存は追加しない。原NCSS応答の有限取得・NetCDF3復号/正規化は外側実験であり、runtimeにdecoder/HTTPを持ち込まない。表層とモデル面の元配列を保持し、新schema/policyを明示する。操作はCOMMANDS、構造・近似の選択はPROGRAM/THEORY/S36へ戻る。

PROGRAM27頁/THEORY22頁を既存TinyTeX/XeLaTeX・FONTCONFIG_FILEで外側生成し、警告0、配置概観と変更図/式のPNG視認後にTeX/PDF/txtを一組で出版した。source/outputの指紋はP520/guides-build-04/build.jsonとguides-publication520.jsonへ固定し、範囲・改善過程・未確認はS36へ戻る。169対象回帰は通常権限で成功、先行一時領域アクセス拒否と区別した。backend/frontendの表示版は無関係に一括変更せず、原結果の全source指紋で実体を特定する。serviceのsourceを変更した後は、新計算前に既存保存状態を保持して正常再起動する。旧GUIやGoogle接続を新JRAの完了証拠にしない。

### 0.51：保存モデル面とガイド追補

固定JRA原本の変換とinspectは標準ライブラリだけで行い、simulateは既存SciPy/NumPyで動く。新しい取得依存は追加しない。COMMANDS C-10は同じrepoから新規出力へ作る。backend/画面の版0.50と既存核の互換version表示は変更せず、保存provenanceの全source hashで今回0.51の実体を識別する。UIのJRA取得/登録が完成した表示にしない。

PROGRAM26頁とTHEORY19頁を既存XeLaTeXで生成し、全頁配置概観と変更頁の個別画像を確認した。最初のフォント不足は既存FONTCONFIG_FILE設定の欠落、続く理論末尾の孤立行は新規参照説明の簡潔化で修復した。原source/PDF/txt一致と有限視認票はS36/REFERENCE_LOGへ戻る。PLAN/旧生成器は不変。139回帰と図注訂正後5再実行を区別し、全UI/科学精度の再受入とはしない。

### 既存CLIの実行依存と0.24の修復

| 行うこと | 必要な依存と境界 |
|---|---|
| 管理検査・保存気象のinspect | Pythonと標準ライブラリ。気象の取得は行わない |
| 保存気象からsimulate | Python、SciPy/NumPyとrepo本体。0.24/D-163でRK45/dense output/brentqへ移行し、計算中の通信はしない |
| GFS取得・原GRIBからの再生 | 既存ecCodes/NumPy。fetchだけがネット取得を行い、replayは保存原bytesを読む |
| PLAN/ガイド生成 | 既存の専用Pandoc/XeLaTeX環境。ガイドの検索本文にはpypdfも使用 |

この修復で使用した既存実行環境はPython3.12.12、SciPy1.17.1、NumPy2.4.4、ecCodes2.47.0。新規導入・global設定変更はしていない。これは当該Windowsでの実測で、全対応版の宣言や完全なlockではない。不足する環境では依存名と対象操作を確認する。モデル式、数値誤差、イベントの意味はTHEORY/ENVへ、APIと実体はPROGRAM/IMPLEMENTATION_INDEXへ戻る。

0.24のPLANは独立コピーで23頁を再生成した。両ガイドも同じ担当TeXから再生成し、生成ログと全頁表示をACT-240へ記録する。過去の版別節にある枚数・依存・成功範囲は当時の記録であり、現在へ読み替えない。コードの責務移行と数値法の移行は別に比較し、計算結果の数値同等性と表示の使いやすさを別に評価する。

## 通常の読取検査と、変更受入の検査

管理用のstate/health検査はPython 3.10以降、標準ライブラリのみ。リポジトリのルートで実行する。全試験は実GRIB検査と軌道計算を含むため、既存ecCodes/NumPy/SciPyを必要とする。気象inspectだけと本体simulateの依存を混同しない。

```text
python tools/check_state.py .
python tools/check_health.py .
python tools/check_health.py . --base /path/to/unchanged-before-state
python -m unittest discover -s tests -v
```

不足/余剰パス、旧版保管ディレクトリ、本文状態とデータ属性、主要な相対リンク、末尾等を調べる限定的検査。最新HEAD、ユーザーの承認、文章の意味的完全性、PDF見た目、物理モデルを保証しない。検査自身の有効性は意図的欠落等の試験で確認する。

## 計画PDFの生成

**使用制限：以下は固定版の独立した作業コピー内だけで試す。正本や通常のcloneを直接生成先にしない。** 現行生成器はTeXを書いた後でPDF生成に失敗し得る。`python tools/build_docs.py .`自体は作業コピーを作成しない。T-012で依存・成功/失敗時の対の更新を受け入れるまで、この制限を維持する。

Python 3.10以降、Pandoc、XeLaTeX、TeX Liveが必要。確認環境の版は配布検査記録へ記録する。使用フォント名はNoto Sans CJK JPとNoto Sans Mono CJK JP。フォント実体は配布しない。各OSのパッケージまたは公式配布から準備する。

必要なTeXパッケージはtemplate.texのusepackageを正本とし、geometry/fontspec/xeCJK/amsmath/amssymb/longtable/booktabs/array/calc/xcolor/graphicx/xurl/hyperref/bookmark/fancyhdr/titlesec/enumitem/fancyvrb/fvextra等。0.12.0で採用した専用Windows環境と再生成手順は次節に示す。今回の実行受入と、依存の完全固定・別環境での受入は区別し、残件はT-012へ保持する。

```text
python tools/build_docs.py .
```

生成補助ファイルは一時領域に置く。TeX/PDF更新後は全ページを描画し、図表・文字欠け・はみ出しを確認する。本文を変えたらMDだけではなくTeX/PDFも同時に更新する。バイト一致の再現と数値/表示の再現は別。

生成TeXの改行は`.gitattributes`に従ってLFとする。0.12.0のWindows初回生成では全743改行がCRLFとなったため、生成器のPandoc引数へ`--eol=lf`を追加して再生成し、最終候補TeXのCRLFが0件であることを確認した。生成後の手直しやGit全体設定の変更で吸収せず、生成元の出力指定で契約を満たす。既存の`--no-highlight`はPandoc 3.11で非推奨警告を出すが、旧環境との互換性を保つため今回は維持する。警告をビルド失敗や日本語欠字として数えず、生ログへ残す。

## 専用Windows生成環境と再生成（0.12.0）

ユーザーの今回の環境整備依頼に基づき、D-132でrepo外の専用環境を採用した。HTML指示書は引き続き直接編集する。以下はPLANの生成経路であり、HTMLをTeXへ変換する手順ではない。導入・生成・表示確認の到達点はHTMLとREFERENCE_LOG、未受入の条件はT-012/U-016を参照する。

以下のPowerShell欄は再利用するための手順表現である。今回の実行には外側のPython補助も用いており、欄の存在や構文解析を、そのPowerShell原文を一括実行した証拠とはしない。実行したコマンド、環境、出力、終了コードは外側ログと担当記録で確認する。

| 用途 | 配置・版・確認条件 |
|---|---|
| 専用root | `C:/Users/genia/.local/share/balloon-docs`。repo、既存Miniforge baseと別に置く |
| Pandoc | `pandoc-3.11/pandoc.exe`、3.11、Windows x86_64公式ZIP |
| XeLaTeX / tlmgr | `TinyTeX/bin/windows`、TinyTeX-1 v2026.09（TeX Live）。追加パッケージは下記 |
| Python | 今回は`C:/Miniforge3/python.exe`の3.12.12。標準ライブラリのみ、baseへのパッケージ追加なし。他環境はPython>=3.10を実測する |
| フォント | `fonts`へNoto Sans CJK JP / Noto Sans Mono CJK JPのRegular/Bold。`fonts.conf`で明示する。OS全体のフォント登録は要求しない |
| 実行時設定 | process内だけPATH、FONTCONFIG_FILEを設定。ユーザー/マシンの永続PATHは変更しない |

### 導入元と固定入力

PandocとTinyTeXの取得バイトは配布元が公開するSHA-256と照合した。フォントはnotofonts/noto-cjkの固定commitから取得し、下表は今回の取得バイトのSHA-256である。フォントのハッシュを配布元の独立署名として扱わない。

| 固定取得元 | SHA-256 |
|---|---|
| [pandoc-3.11-windows-x86_64.zip](https://github.com/jgm/pandoc/releases/download/3.11/pandoc-3.11-windows-x86_64.zip) | `2ab72baf2399450e148ddf7a2a8689806c42e1bba71862b57e220fd9b8456d3d` |
| [TinyTeX-1-windows-v2026.09.exe](https://github.com/rstudio/tinytex-releases/releases/download/v2026.09/TinyTeX-1-windows-v2026.09.exe) | `eea6a6e5f97d44416ca9ea974385af1ffd3fa119be19d34cdaf2abc85775d374` |
| `Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf` | `68a3fc98800b2a27b371f2fb79991daf3633bd89309d4ffaa6946fd587f375b5` |
| `Sans/OTF/Japanese/NotoSansCJKjp-Bold.otf` | `e53dcb0dcb2922e45d01aae1ebd2f382bb81d4229b18b6b883bd170678af1f76` |
| `Sans/Mono/NotoSansMonoCJKjp-Regular.otf` | `4d01725be822d144cf9a56ade981e6fb920cd7a610b8fc24cc601a920beea5b9` |
| `Sans/Mono/NotoSansMonoCJKjp-Bold.otf` | `dfdffe149bc6cbf52860dabd8b8dadbca40ae87a4fbe143b55c0258db2dadfb8` |
| `Sans/LICENSE` | `6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2` |

フォント取得URLは`https://raw.githubusercontent.com/notofonts/noto-cjk/f8d157532fbfaeda587e826d4cd5b21a49186f7c/`に表のパスを続ける。4フォントとLICENSEを専用rootの`fonts`へ保存する。取得記録は専用rootの`downloads.json`に保持し、repo内の新しい管理原本にはしない。

初回導入は、新しい専用rootを対象とする。既存環境がある場合は上書き展開せず、次項の再利用検査へ進む。PowerShellで`$taskRuntime`を上表のroot、`$taskDownloads`をその`downloads`子フォルダーに設定し、上記URLから`Invoke-WebRequest -Uri <固定URL> -OutFile <保存先>`で取得する。各ファイルの`(Get-FileHash -LiteralPath <保存先> -Algorithm SHA256).Hash`を表と照合し、不一致・取得失敗なら展開しない。照合済みアーカイブは次のように展開する。

```powershell
$taskRuntime = 'C:\Users\genia\.local\share\balloon-docs'
$taskDownloads = Join-Path $taskRuntime 'downloads'
Expand-Archive -LiteralPath (Join-Path $taskDownloads 'pandoc-3.11-windows-x86_64.zip') -DestinationPath $taskRuntime
$taskExtract = Start-Process -FilePath (Join-Path $taskDownloads 'TinyTeX-1-windows-v2026.09.exe') -ArgumentList '-y', ('-o' + $taskRuntime) -Wait -PassThru -WindowStyle Hidden
if ($taskExtract.ExitCode -ne 0) { throw 'TinyTeX展開が失敗したため停止する。' }
```

展開先を変更する場合は、新しい絶対パスを確認し、後述のフォント設定と実行時PATHも同じ配置へ合わせる。フォント用設定は`fonts.conf`へUTF-8で保存する。`fonts`はフォント実体、`font-cache`は生成キャッシュである。

```xml
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig>
  <dir>C:/Users/genia/.local/share/balloon-docs/fonts</dir>
  <cachedir>C:/Users/genia/.local/share/balloon-docs/font-cache</cachedir>
</fontconfig>
```

必要パッケージの追加は次の一回の導入操作で行う。既存のTinyTeX全体を無条件に更新するコマンドには置き換えない。

```powershell
$taskTlmgr = Join-Path $taskRuntime 'TinyTeX\bin\windows\tlmgr.bat'
& $taskTlmgr --repository https://mirror.ctan.org/systems/texlive/tlnet install xecjk titlesec enumitem fancyhdr fvextra xurl bookmark booktabs tools fontspec geometry amsmath amsfonts graphics xcolor fancyvrb
if ($LASTEXITCODE -ne 0) { throw 'TeXパッケージ導入が失敗したため停止する。' }
```

この追加経路は更新されるCTAN repositoryを使う。今回のmirror選択は`ftp.jaist.ac.jp`で、GPGが利用できず署名検証していないというtlmgr表示があった。HTTPSでの取得と、GPG署名の検証済みを混同しない。バンドルの固定ハッシュだけでは追加分の版は固定できないため、専用rootの`TinyTeX/tlpkg/texlive.tlpdb`を実行時点で外側の証拠へコピーし、導入ログと共に保持する。必要な索引はこの原記録の`name`/`revision`/`catalogue-version`から抽出する。今回の`packages-installed.json`は180レコードであり、全依存の将来取得を保証するlockではない。将来取得時の版差は別環境として再受入する。

初回の台帳出力試行では、`tlmgr info --only-installed --data name,localrev,cat-version`がWindowsのバッチ引数処理により`localrev`/`cat-version`をパッケージとして扱い、エラー文を出した一方で終了0だった。この出力は台帳として採用せず、上記の原tlpdb保存へ変更した。終了0だけを成功判定にしない。

### 既存専用環境の再利用と、独立コピーでの生成

実行場所は対象候補のrepo rootとする。最初に現在の基準SHA、候補の変更集合、作業フォルダーの実体を確認する。別の候補を編集しているプロセスがないことを確認し、以下で全宣言パスを新しい一意な作業コピーへ複写する。コピーとログはrepo外に置き、`.git`を持ち込まない。元の候補をGit checkout/resetで切り替えない。

```powershell
$taskRepo = (Get-Location).Path
$taskRuntime = 'C:\Users\genia\.local\share\balloon-docs'
$taskPython = 'C:\Miniforge3\python.exe'
$taskBuild = Join-Path $taskRuntime ('builds\' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '-' + [guid]::NewGuid().ToString('N'))
& $taskPython -B -c "import json,pathlib,shutil,sys; src=pathlib.Path(sys.argv[1]); dst=pathlib.Path(sys.argv[2]); paths=json.loads((src/'docs/CONTENT_HEALTH.json').read_text(encoding='utf-8'))['files']; dst.mkdir(parents=True,exist_ok=False); [( (dst/p).parent.mkdir(parents=True,exist_ok=True), shutil.copy2(src/p,dst/p) ) for p in paths]" $taskRepo $taskBuild
if ($LASTEXITCODE -ne 0) { throw '作業コピー作成が失敗したため停止する。' }
```

まずPATHとフォント設定を一時的に揃え、実際に見つかったコマンド・版・フォントを照会する。次の診断欄の終了後、出力を下記の期待結果と照合する。

```powershell
$taskOldPath = $env:PATH
$taskOldFc = $env:FONTCONFIG_FILE
try {
    $env:PATH = (Join-Path $taskRuntime 'pandoc-3.11') + ';' + (Join-Path $taskRuntime 'TinyTeX\bin\windows') + ';' + $taskOldPath
    $env:FONTCONFIG_FILE = Join-Path $taskRuntime 'fonts.conf'
    Get-Command pandoc, xelatex -ErrorAction Stop | Select-Object Name, Source
    & $taskPython --version
    if ($LASTEXITCODE -ne 0) { throw 'Pythonの照会が失敗したため停止する。' }
    & pandoc --version
    if ($LASTEXITCODE -ne 0) { throw 'Pandocの照会が失敗したため停止する。' }
    & xelatex --version
    if ($LASTEXITCODE -ne 0) { throw 'XeLaTeXの照会が失敗したため停止する。' }
    & fc-match 'Noto Sans CJK JP'
    if ($LASTEXITCODE -ne 0) { throw '本文フォントの照会が失敗したため停止する。' }
    & fc-match 'Noto Sans Mono CJK JP'
    if ($LASTEXITCODE -ne 0) { throw '等幅フォントの照会が失敗したため停止する。' }
} finally {
    $env:PATH = $taskOldPath
    $env:FONTCONFIG_FILE = $taskOldFc
}
```

ここで出力を読む。期待結果は、`Get-Command`のSourceが専用root内の`pandoc-3.11/pandoc.exe`と`TinyTeX/bin/windows/xelatex.exe`であること、Python/Pandoc/TeXの版が今回使う環境の記録と一致すること、`fc-match`が`NotoSansCJKjp-Regular.otf` / `Noto Sans CJK JP`と`NotoSansMonoCJKjp-Regular.otf` / `Noto Sans Mono CJK JP`をそれぞれ返すことである。別配置や代替フォント、未説明の版差、照会失敗があれば、次の生成欄を実行せず配置・設定を直して再診断する。照会コマンドの終了0だけで一致にしない。

診断の一致を確認した後、次の生成欄を実行する。既存生成器の呼出しは`python -B tools/build_docs.py .`であり、Pythonラッパーは同じ呼出しのstdout/stderrを生バイトで作業コピーの外へ保存するためだけに使う。失敗は例外として停止し、環境変数と現在フォルダーはfinallyで戻す。

```powershell
$taskOldPath = $env:PATH
$taskOldFc = $env:FONTCONFIG_FILE
$taskLog = $taskBuild + '-logs'
try {
    $env:PATH = (Join-Path $taskRuntime 'pandoc-3.11') + ';' + (Join-Path $taskRuntime 'TinyTeX\bin\windows') + ';' + $taskOldPath
    $env:FONTCONFIG_FILE = Join-Path $taskRuntime 'fonts.conf'
    New-Item -ItemType Directory -Path $taskLog -ErrorAction Stop | Out-Null
    Set-Location -LiteralPath $taskBuild
    & $taskPython -B -c "import pathlib,subprocess,sys; logs=pathlib.Path(sys.argv[1]); result=subprocess.run([sys.executable,'-B','tools/build_docs.py','.'],stdout=(logs/'build.stdout').open('wb'),stderr=(logs/'build.stderr').open('wb')); sys.exit(result.returncode)" $taskLog
    if ($LASTEXITCODE -ne 0) { throw ('生成が失敗した。作業コピーとログを保持する: ' + $taskLog) }
} finally {
    Set-Location -LiteralPath $taskRepo
    $env:PATH = $taskOldPath
    $env:FONTCONFIG_FILE = $taskOldFc
}
```

Perlのlocale警告が出る場合は、実行プロセスだけ`LC_ALL=C`、`LC_CTYPE=C`、`LANG=C`へ設定し、終了後に元へ戻す。日本語原稿の保存をASCIIへ変更する対策ではない。

生成後は非空のTeX/PDF、TeXのCRLFが0件であること、終了コード、`build.stdout`の`REVIEW:`、`build.stderr`を確認する。PDFを全ページ画像へ描画し、表紙版・柱/脚・日本語・数式・表・はみ出し・リンクを確認する。描画ツールの版・ページ数・確認対象・問題と修正を外側ログとREFERENCE_LOGへ記録する。抽出テキストが読めることだけで表示確認を代替しない。

受入後に、レビュー済みの`docs/PROJECT_PLAN.md`と生成した`.tex`/`.pdf`を同じ候補へ適用し、差分・前後ハッシュ・DC-CLOSEの管理検査を行う。TeX/PDFの片方だけを適用しない。途中失敗したコピーは状態とログを保管し、原因の修正後に新しいコピーでやり直す。生成器自体の対更新・全依存固定・別OS受入は、この一回の生成成功で解消したことにしない。

## 配布と記録

配布ZIP/チェックJSONはローカル退避用で、GitHubの現行ファイル一覧へ追加しない。GitHub側の現行パスはCONTENT_MAP、現行版はGitのコミットを参照する。配布ハッシュはZIPの外側の検査記録に保持する。自分自身の将来コミットSHAを本文に埋める必要はない。

## 時間・範囲の検査

この検査を使う目的と確認対象の選定にも[DC-JUDGMENT](DOCUMENT_CONTROL.md#DC-JUDGMENT)を適用する。D-161により現policyはversion_age_mode=advisoryで、3版差はversion_age_advisoriesとwarningsへ出す候補情報である。版数だけでは失敗にせず、主担当が用途・意味的影響を見て選定する。30日・初回期限/利用前・本文/依存不一致の保護は維持する。mode省略時は従来のrequired、未知値は拒否。0.22以前の検査器はadvisoryを知らず版数期限で失敗するため、0.23移行時はその結果を残し、旧contractによる変更理由照合と新しい反例試験を併せて確認する。警告を消すために確認印を上げない。

check_healthはPython 3.10以降の標準ライブラリのみ。readonlyでGitHubへ接続せず、正しい内容であることを認定するツールではない。文書の未確認・期限切れ・確認後変更・依存後変更・更新印忘れと時系列/範囲登録の整合を判定する。`--base`は基準コミットと変更集合、全宣言パスのバイトを同定した変更前の固定一式を指定する。未統合候補を直接比較元にする場合は、元のGitコミットSHAと候補一式のsnapshot hashを区別し、その候補をGitへ統合済みとは扱わない。既存ZIPの展開でも、Gitから取り出した一式でもよく、毎版ZIPの永久保管は不要。0.12.0作成時の直接比較元は完全な0.11.0未統合候補であり、M101からの累積比較との対応はREFERENCE_LOGのGEN-120に記録する。未指定なら基準差分検査を省いたことを結果へ明記する。

既定の評価日はUTCの当日。再現用に`--as-of 2026-09-17`を使えるが、古い日付を指定して現在の期限切れを隠してはならない。期限到達時は再確認まで失敗することが正しい挙動である。本文指紋と依存指紋は実際のレビュー後に登録する。自動で確認印を全件更新する機能は設けない。

0.4導入時にはPLANのMD/TeX/PDFを0.3表示版のまま保持した。その後0.10.0で一組を再生成した（末尾の生成記録）。0.11.0候補では生成環境を確保できなかったため、PLAN一式を0.10.0の同一バイトで保持し、第9/12章の旧役割・再開案をCONTEXT第1節とD-130/131の現行方針へ接続した。0.12.0ではD-132に従って環境整備と一組の改訂・再生成へ進む。前回の保持は履歴であり、今回の改訂を免除する条件ではない。参考PDF/TeXと原Excelはこの生成の対象外である。

探索索引の再計算：`python tools/check_health.py . --index`。指紋の計算：`python tools/check_health.py . --fingerprints`。出力は計算値でありレビュー証拠ではない。元文書を確認せず、その値を全件登録して確認完了にしない。probeについてはlive_checks_requiredを別に実施する。

## 復旧契約の検査（v0.5）

check_healthは焦点とは独立したrecovery_contractを読み、方向・依存の必読範囲とRC結果欄、U02/S08の操作5欄を点検する。PLANの既存章は一意なtext_range境界で抽出し、親の未確認領域を残す。これらは内容理解の自動判定でも、GitHub画面の実操作試験でもない。回帰試験は契約欠落・省略指示・見出しの不在/重複/逆転も与えて検出を確認する。

## v0.6の点検と保管

S08の完了記録には8観点の合格とRPT-004/RC-004の照合根拠を要する。S09操作5欄、RET規則の欠落もcheck_healthが点検する。テストは特定の最新番号を文字列に固定せず、レジストリの版と証拠から改変対象を選ぶ。PC退避の可読性と削除対象の固有情報は利用者が確認する。完全履歴mirror/bundleの導入は後続であり、現段階の新しい実行コマンドにしない。

## Windows既存cloneのLF整合と検査（v0.8）

RPT-007でPython3.12.12/64 bit、Git2.44.0.windows.1、conda25.11.1、cloneのM060、サンプル3件のLF/CRLF差を受理。現行指紋はCRLFを無視しない。`.gitattributes`は既知テキストをLF、未知/バイナリを変換対象外にする。現在の原文と副作用説明は[HTML E02](../BOOTSTRAP_RUNBOOK.html#E02)に集約する。

`tools/prepare_workspace.py`はinspect/sync/normalize/verifyを提供する。inspect/preview/verifyは読取、syncはローカルGitのfetchとfast-forward、normalize --applyはHEADとCRLF差だけの検証済みパスの置換とそのindex情報更新。GitHub書込・global設定・reset/clean・再clone・自動stashは行わない。複数ファイルの一括トランザクションではないので並行する編集や同期を止め、失敗時は状態を保持して報告する。

condaの専用prefixはrepo外。作成仕様はPython3.12系列・conda-forgeのみ・既定追加パッケージなし。condaの取得キャッシュや環境一覧等の管理情報は変わるが、baseのパッケージを追加/更新する手順ではない。科学依存とTeXは導入しない。実行はconda run -p経由とし、DLL検索を含む環境を揃える。

初回ユーザー試験ではstate/healthとunittestを実行する。healthの評価日は当日のままで--baseは省略を明記する。過去日を指定して期限を隠さない。全科学/PDF/CIの受入ではない。検査前後にHEADとの全追跡バイト一致を確認し、検査出力・環境をrepo内へ勝手に増やさない。

Windowsでのテストコード読込はUTF-8を明示する。新しいGit fixture試験はtemp内でのみリポジトリを作り、ネットワークを使わない。Git未発見でskipした場合は成功件数と分けて報告する。

## Windows回帰修正と端末非依存の記録（0.8.1）

BUG-008-LF: tests/test_health.pyのPath.write_textでnewline未指定だったため、一時コピーの計画本文がWindowsでCRLF化した。tests/test_health.py/test_state.pyの意図的な本文変更はUTF-8・newline="\n"で保存する。実CRLFを与えて拒否される異常系は別に保持する。tools/check_health.pyの境界/指紋は弱めず、.gitattributesや計画の保存バイトも変更しない。

当時のM081実行入口はHTML F01のCMD-CHECK-02。現在の候補検査は本書の通常検査・版間受入コマンドと当該REFERENCE_LOGを用い、過去の固定SHAや91件へ戻さない。`tools/run_checks.py`は専用prefixの実体を確認し、pre verify→state→health→regression→post verifyを実行する。失敗時は通常の後続検査を省くが、post verifyをfinallyで試みる。結果はrepo/環境の外の新しいlogs子フォルダーへ段階別stdout/stderr（生バイト）、環境JSON、summary.jsonとして保存する。既存ログを上書きしない。失敗やskipを成功に変更しない。強制終了/電源断/容量不足で最終記録が揃わない場合は途中状態を保持する。

この入口はGit fetch/push、改行変換、環境作成/更新をしない。試験は一時領域を使う。JSONのokだけで科学的妥当性や未読PDFを確認済みにせず、既存の期限とlive inputの限界を残す。端末表示の過去の欠落原因は未確定であり、ログ経路の追加を原因特定済みと呼ばない。

## 実環境の受入と、以後の境界（0.8.2）

RPT-010/CHK-010はM081の利用者Windows/PowerShell/既存conda prefixに対する受入。Python3.12.14/64 bit、91件全成功・skip0、検査前後33追跡バイト一致。テストIO修正が実環境で通ることを確認した。--base比較未実行・初回8範囲未確認・live probe未実施の警告/限界は解消扱いにしない。

HTML F01-2の原文にER-081-01を取り込み、tests/test_workspace.pyで呼出契約を検査する。F01-2/3はM081で実行した過去手順として保持し、新しい版へ進めた後にM081固定コマンドを再実行しない。0.8.2候補の追加試験は過去の91件へ加算しない。本体のPython依存固定・TeX生成・CIの受入は後続である。

## 0.9の監査・改訂用入口

`check_state.py`はcheck_contractも呼ぶ。単独では `python tools/check_contract.py .`、変更前との理由照合は `python tools/check_contract.py . --base <変更前一式>`。出力は構造上の判定であり、意味の承認ではない。

CONTINUITY_CONTRACTのassetsを編集した後、`python tools/check_contract.py . --views`の出力をCONTENT_MAPのASSET_VIEW_BEGIN/END間へ入れる。次にDC-CLOSEに沿ってレビューした範囲だけを登録し、既存のcheck_health --fingerprints / --indexの計算値を対応範囲へ入れる。これらのコマンド自体は書込み・自動承認をしない。目的が分からない範囲に確認印を付けて検査を通さない。

**生成器の使用境界：** 現行build_docsはTeX更新後にPDF生成が失敗し得る。T-012で対の更新方式と依存を受け入れるまで、既存cloneを直接更新せず、固定版の別作業コピーでのみ試す。失敗したTeX/PDFを配布しない。0.9監査時は再生成せず、0.10.0の生成記録は下記、0.11.0も一組を保持した。

## 版間の受入（DC-STABILITY）

通常の状態検査は前後比較の代替ではない。変更前一式を固定SHA/treeと照合し、候補へ `python tools/check_contract.py <候補root> --transition --base <固定変更前root>` と `python tools/check_health.py <候補root> --base <固定変更前root>` を実行する。比較器の新旧互換がある場合は、固定変更前rootのtools/check_contract.pyを実行元にして候補を比較する。schema非互換なら無理に現行で通さず、移行のレビューを別に行う。--transitionに--baseがなければ明示停止する。

出力のstructural changes、自身の内容変更、祖先影響は異なる。全パス/バイト集合の比較指紋は基準の取り違えを検出するが、GitHub取得を代替しない。外側の適用一覧に基準SHA・tree・前後ハッシュを残し、保存後の再GETも行う。ユーザーWindows/PowerShellの新規受入は別で、既存の91件実測へ合算しない。

## 入口と比較成立の確認（0.9.2）

共通入口の表示は `python tools/check_contract.py . --entry-text`。提供された控えの照合は `python tools/check_contract.py . --entry-copy <repo外のUTF-8本文.txt>`。いずれも外部UIへのアクセスや書込みをしない。通常stateからは原文とHTMLコピー・README/AGENTSの互換性記録を検査する。外部Projectの現在設定は別途観測し、未観測ならそのまま記録する。

--transitionを付けたときは、存在する完全な基準と旧contractを要する。空/不在のパスを初回棚卸しとして通さない。--views/--entry-textの表示と--transition/--base/--entry-copyを混ぜない。失敗を無視せず、終了コードとtransition.status=checkedの両方を確認する。保全/ログ/生成用コードはGUARD_PATHSにも含めて旧比較器と候補の両方で点検する。

## S10-3：本体計画と提供原本の受入境界

原本xlsxは計算・ビルド入力ではなく参照実体として追加する。バイト同一性の照合で受け入れ、ビルド時に自動再計算・リンク更新・再保存しない。本文の科学的利用は別作業とする。PLANのMDを改訂した場合は、既存の生成器・テンプレートと対応するTeX/PDFを同じ作業コピーで再生成して確認する。

比較用の変更前一式は、対象SHAに対応する全宣言パスを揃えて同定する。不完全な一式を本番cloneへ上書きして補完しない。`--transition`は完全基準の検査が成立したときだけ成功を意味する。旧r1レビュー原稿をrepo rootへ適用しない。今回は固定M092の完全なtreeを同定し、同名文書へ組み込んだ候補に対して検査する。

上段のM092は0.10.0作成時の基準である。0.11.0の比較元はPR #13のM101、全39パス。`check_health --base`も必須メタデータと全宣言ファイルが不足する基準を拒否する。`--index`/`--fingerprints`は表示専用で、`--base`/`--scope`/`--as-of`と混用しない。CONTINUITY自身の版はHEALTHの当該ファイル登録と照合し、無変更の他文書まで最新版へ揃えない。


## 0.10.0の生成確認（作業用Linuxのみ）

固定M092のbuild_docs.pyを変更せず、独立した生成コピーでpandoc→XeLaTeX3回を実行した。PLANのMarkdownからTeX/PDFを再生成した。テンプレートの柱・脚に固定されていた0.3.0と2026-09-17を、編集元のrevision/build_dateへ対応させる修正を行った。値がない旧ソースは従来表示へ戻るため、別版を現在版と誤表示しない。テンプレート以外の生成ロジック・同期・検査器コードは変更しない。

0.10.0のTeX/PDF生成はユーザーWindowsへのTeX導入・実行ではなく、当時のU-011の未確認を解消しなかった。0.12.0のWindows専用環境は上記の別の実行記録として扱う。生ログと表示の確認範囲は配布外枠に保持し、過去の成功へ合算しない。参考ガイドPDF/TeXと元Excelはビルド対象にしない。


## P1 GFS固定入力の再検査（0.13.0）

`tools/inspect_gfs_fixture.py`はネットワークを使わず、保存した3 GRIB2のSHA256とmanifest、変数・層・単位・格子走査・run/valid時刻・欠測・有限値を検査する。気象補間や飛行モデルではない。入力は`references/gfs_p1_fixture/`の4ファイル、出力はrepo外の未使用先に置くJSONと3 metadata CSV。入力を再保存しない。

今回の実行は既存`C:/Miniforge3/python.exe` 3.12.12、ecCodes Python/native 2.47.0、NumPy 2.4.4。追加導入なし。通常の管理検査（標準ライブラリのみ）とは依存が違い、専用文書生成環境の存在からGRIB復号可否を推定しない。別環境ではecCodesのnative libraryも必要で、依存固定と専用実行環境は次のT-005で決める。

repoルートで、`<repo外の未使用出力先>`を実在する外部親の新しい子へ置換して実行する。

```text
python -B tools/inspect_gfs_fixture.py --output-dir <repo外の未使用出力先>
```

正常は終了0、3入力・417メッセージ・33,777値のPASSと地下気圧面の警告を表示する。SHA不一致、未知/欠落field、単位/時刻/格子不一致、既存出力・repo内出力は終了1。失敗時は原出力を残し、入力を推測修正しない。f000/001/002の地下level-cell数144/142/142は欠測ではなく、有限でも補間に使ってはいけない値である。現在の検査器は検出までで、マスクはS14-3の実装対象。

入力の取得runは2026-09-21 18UTC、時刻は18/19/20UTC、仮領域136–138°E・34–36°N、33層1000–1hPa。実打上げ条件や全飛行を覆う窓ではない。上空HGTのgpmと地表HGTのmを同じ幾何高度として扱わない。原URL/取得時刻/HTTP/ハッシュ、取得間隔違反と次回の是正、未受入項目はmanifestに保持する。再ダウンロードを通常の検査条件にしない。新規取得時は公式NOMADS条件に従い応答完了後10秒以上待つ逐次処理とキャッシュを用いる。

T-005の正規化受入時に本検査器とfixtureの役割を再評価する。一般adapterの代わりにこの小標本専用コードを拡張し続けず、後継の入力契約・回帰へ移す際は根拠と原バイトの行先を記録する。実施結果と次の判断はACT-130/S14、理論・データの接続はPLAN 10.4とCONTENT_MAP 8.3。

0.13.0作成時の直接比較元は完全な0.12.0候補39パスだった。ACT-130の固定コピーとCONTINUITYのcomparison_base_sha256を用いる。古い生成欄の比較元を現在の値として実行しない。


## 0.14.0環境候補の検査と現在の比較元

基準はPR14統合M130の全44パス。新候補はENVIRONMENT_CONTRACTに従う固定小標本の正規化器・試験・説明を3パス追加する。既存ecCodes/NumPyを利用し、追加導入も標本の再取得もしない。一般adapterや科学モデルを採用する検査ではない。

repoルートで `python -B -m unittest discover -s tests -p test_environment.py -v` を実行する。正常/境界/欠測と実標本の試験を含む。具体的なCLIの入力・出力・停止はENVIRONMENT_CONTRACTへ置く。通常の管理回帰は `python -B -m unittest discover -s tests -v`、state/health/contractは上記の完全M130を--baseへ指定する。試験時のtemp作成で環境の権限エラーが出た場合、製品の数値結果と分けて原ログを残し、許可された同じ試験を適切な実行境界で再実施する。テストや検査条件を弱めない。

今回の実測件数・生成ページ・前後不変はACT-140へ記録する。以前の201件や19頁を今回の新規実行結果へ転用しない。

## 0.15.0の比較元と取得証拠の再読

0.15.0作成時の比較元はPR15統合M140 `f8dee6cc46e772a3e38b0fbe426371fcfaf4ba93` の全47パス（CHK-021）。0.14節のM130は当時の履歴。現候補も47パスを維持し、実装/テスト/GFS原入力を変更せず、取得経路・拡張設計・意思決定と手順を改訂する。state/health/新旧contractにはACT-150の完全base-0.14.0を指定する。PLANは上の既存Windows経路で独立生成コピーからMD/TeX/PDF一組を作り、表示確認後に取り込む。

一回の取得調査はACT-150の外側forecast-access/historical-access/terrain-accessへ原bytes・manifest・小検査器を保持する。再読は保存入力を使い、現行URLからの再取得を再現と呼ばない。通常のrepo検査にネットワークやCDSアカウントを追加しない。一般adapterへ移す小fixture/検査/依存は後続の意味ある実装で選び、外側スクリプトを無説明の必須運用にしない。

## 0.16.0の比較元・調査証拠・再実行

0.16.0作成時の比較元はPR16統合M150 `4e1ff0c39633236a991f07ef62f120110237cf5e` の全47パス（CHK-022）。ACT-160の完全base-0.15.0をstate/health/新旧contractの比較に用いる。候補はWEATHER_DATA_GUIDEだけを追加した48パスで、製品コード/固定入力/PLAN三点は変更しない。既存契約試験の固定28個という期待値だけはD-143に従い比較元の全ID集合へ一般化する。Markdownガイドは直接編集し、数式・APIパラメータ・来歴表を意味レビューする。PDFを新規生成した実績はない。

ACT-160の外側 `p1-weather-field-0.16.0/` にforecast-research、historical-research、reconstruction-researchの保存bytes・要求/応答metadata・hash・診断器を置く。ガイド第7節の再読入口はネットワーク無しを基本とする。再取得は別run/別改訂を持つ新たな観測であり、同じURLから同じ入力を再現できるとは限らない。調査器を通常repo検査の必須依存へ追加しない。具体的コマンドと再実行結果はACT-160へ記録する。

## 0.17.0の比較元と外側研究の再読

0.17.0作成時の比較元はPR17統合M160 `a4f6f26dd645940b5ad3322151f47d280e0f8c2d` の全48パス（ACT-170/CHK-023）。state/health/新旧contractはP170の完全base-0.16.0へ比較する。全48パス/39論証IDを維持し、製品コード/試験/固定GFS/PLAN三点/原Excelは不変。ガイドとENVは担当本文を更新し、取得仕様・式・行動記録を重複する正本にしない。

外側model-input-researchの `python -B calculate_saved.py replay-new.json` は保存GFSをecCodesで再読しsocketを禁止する。旧T等の依存 `p1-weather-field-0.16.0/forecast-research/native-subset-f003.body` をP170の兄弟位置に置く。model-level-researchの再読入口はガイド第7節と同dirの報告、solver-researchは `python -B diagnostic.py replay-new.json`（SciPy1.17.1）を使う。いずれも既存出力名を上書きせず、新しい出力を指定する。これらは一回の調査再現用で、通常repo検査の必須依存ではない。ネット再取得は別観測であり、原bytesの再読を代替しない。今回追加依存の導入、PDF生成/視認は行わない。

## 0.18.0：固定JRA queryとモデル構成検査

現在の比較元はPR18統合M170 `3f4258bb0535811f84d4fd1e71564b92c3da1deb`、P180/base-0.17.0の全48パス。候補は新規5を加えた53パス。既存GFS入力/実装/試験とPLAN一組・原Excelは保持する。新候補は標準ライブラリで動き、追加依存・ネット取得は不要。既存全回帰の実GRIB検査だけ従来ecCodes/NumPyを要する。

repo rootのPythonから以下を実行する。`<repo外の未使用出力先>`は新しい外部ディレクトリへ置換する。既存出力（空でも）とrepo内出力は拒否し、失敗は入力を変更せず理由を報告する。JSONは診断出力で、一般adapterの保存交換形式ではない。

```text
python -B tools/normalize_jra3q_model_fixture.py --output-dir <repo外の未使用出力先>
python -B -m unittest discover -s tests -p test_jra3q_model_environment.py -v
python -B -m unittest discover -s tests -p test_model_composition.py -v
```

任意時刻queryと構成の呼出例はENVの0.18節へ置く。標準ライブラリだけの限定試験と、全回帰の外部GRIB依存を混同しない。今回のWindows sandboxではTemporaryDirectoryの再アクセスに失敗したため原失敗を保持し、同一の許可済み試験を適切な実行境界で再検査した。ACLや製品のガードを弱めていない。全回帰の実環境/件数/前後保全はACT-180が正本。

GFSの有限Range診断は製品の通常CLIへ入れない。P180/gfsmode-research/gfs-model-report.mdが既存balloonwxの子プロセス環境・転送上限・原失敗・再生条件を持つ。新たなネット取得や別reader導入を、保存済みfixtureの再検査に混ぜない。

### 構成宣言だけを表示する

repoルート・既存専用Pythonから実行する。構成器自身にファイル出力CLIは設けていない。

```text
python -B -m unittest discover -s tests -p test_model_composition.py -v
python -B -c "from tools.compose_model import compose_model,tawhiri_like_spec; p=compose_model(tawhiri_like_spec(5,5,30000)); print(p['required_fields']); print(p['required_terrain_fields']); print(p['unresolved_contracts'])"
```

最初のコマンドは保存JRA標本との接続試験も含む。JRA標本/APIが欠けた環境ではskip成功に変えず失敗する。二つ目は標準ライブラリだけで構成依存を表示する。力学計算・気象再取得・DEM照合は行わない。数値queryの再実行は上のENV例を用いる。今回の生ログと前後hashは外側 `composition-evidence` の実行受領票へ保存する。

### GFSの予報時刻窓をofflineで計画する（0.19.0候補）

repoルートから、既存Pythonで実行する。標準libとrepo内 `compose_model.FIELD_UNITS` だけに依存し、ネット接続・新規導入は不要。以下の三つの入力JSONはENV「0.19.0」の形式に従って利用者側の保存場所へ用意する。試験で保存した完全な人工例はACT-190の外側 `forecast-plan-evidence/cli-01/{request,inventory,required-fields}.json` であり、実予報の提供一覧ではない。

```text
python -B tools/plan_gfs_forecast.py <request.jsonの実パス> <inventory.jsonの実パス> --required-fields <required-fields.jsonの実パス>
python -B -m unittest discover -s tests -p test_gfs_forecast_plan.py -v
```

`--required-fields` は省略可能。付ける場合は `compose_model(...)["required_fields"]` だけをJSON化した辞書を指定し、モデル全体や構成結果全体を渡さない。日時JSONは末尾 `+00:00` まで明記し、期間は整数秒とする。CLIは入力を読みstdoutへ計画JSONを出すだけで、入力の上書きやcache作成はしない。呼出側がstdoutを保存する場合は新しい証拠名を用い、元入力と一緒に保持する。

正常な入力でも時間支持が足りなければ終了2、`status=unavailable` と各runの不足理由をstdoutへ返す。時間計画が成立すれば終了0/`temporal_plan_ready`。不正JSON、重複key、UTC/期間/単位等の不正宣言、読込失敗は終了1でstderrへ理由JSONを返す。引数そのものの誤りはargparseの通常のusage/終了2なので、時刻不足と区別して出力も確認する。終了0を実GRIB取得成功や軌道計算成功と扱わない。

Python APIの最小接続例（`request`/`inventory`の全形式はENV、日時・機体値は検証用）：

```python
from tools.compose_model import compose_model, tawhiri_like_spec
from tools.plan_gfs_forecast import plan_gfs_forecast

model = compose_model(tawhiri_like_spec(5, 5, 30000))
result = plan_gfs_forecast(request, inventory, model["required_fields"])
print(result["status"], result["selection"]["reason"])
```

再実行用の外側 `run_checks.py` と `run_examples.py` は各々未使用の結果ディレクトリ名を引数に取り、元証拠を上書きしない。前者は35限定試験と新2ファイル/内部依存1ファイルの前後hash、後者はsocketを禁止したCLIの成功2回・欠落・不正入力の終了理由とstdout一致を記録する。全repo回帰とは別の限定結果として読む。

## 0.20.0：気象取得・軌道本体・理論/構造ガイドの生成

この節の基準SHA・初回実績・依存表は0.20時点の記録。現在も使う生成経路は維持するが、現在のsimulate依存と適応積分の仕様は冒頭およびCOMMANDS/理論ガイドに従う。標準ライブラリだけで積分していた当時の条件を再利用しない。

### 実行を選ぶ前に依存を分ける

固定比較元はPR20統合M190 `21d8565a97c59d38bf51f3ab8736ffb14ba21198`。外側`flight-core-0.20.0/base-0.19.0`に全55パスの比較元を保持する。本体の入出力契約は[ENVの0.20節](ENVIRONMENT_CONTRACT.md)、全引数・例・終了理由は[COMMANDS](COMMANDS.md)、気象の原仕様と取得費用は[WEATHER第8節](WEATHER_DATA_GUIDE.md)を読む。古いfixture正規化器、JRA query、構成器、0.19時刻plannerは回帰と設計根拠として保持する。

| 操作 | 依存と副作用 | 成立を示すもの |
|---|---|---|
| 保存JSON gzipのinspect/simulate | Python標準libとrepo本体。ネット不要。simulateは新しい出力先を作成 | 元設定/場/codehash、結果JSON/CSV/GeoJSON/HTML/manifest。終了0と着地の有無を照合 |
| GFS fetch | 既存Python3.12.12/ecCodes2.47.0/NumPy2.4.4とHTTP。新規取得先へ最大50MBのrawと場を保存 | URL・取得時刻・bytes/hashと復号結果。404/timeout等も失敗原本として保持 |
| 原GRIB replay | 同じecCodes/NumPy。ネット不要、新規正規化ファイルのみ | 要求/原URL/bytes/hash再照合と復号。異なるrunの新規取得は再読ではない |
| 理論/構造ガイド生成 | 既存XeLaTeX、フォント、Codex文書Python/pypdf。新規build先。指定時だけdocsの生成物を更新 | 生成log、source/outputhash、PDF/text、全ページの表示点検 |

この環境では追加ライブラリやTeXパッケージの導入を行っていない。別環境で必要依存がない場合に勝手に導入せず、欠けた実行能力を特定する。試験でのWindows TemporaryDirectory ACLエラーと機能失敗を混同しない。0.20の気象試験は初回4件がそのACLで止まり、同じ許可範囲の通常権限で実行して成功した。ACL自体を変更していない。

### ネットを使わず最初の全飛行を再現する

repoには元正規化場から格子indexだけで切り出した小領域2標本を保持する。`references/flight_fixture/manifest.json`が原run/原raw/元bundlehashと小標本を結び、`tools/make_flight_fixture.py`が抽出を再現する。全領域取得要求のboundsと小標本のmetadata.subset.boundsは異なる意味なので区別する。

repoルートで下記の`<...>`を未使用の外部ディレクトリへ置換する。既存出力は拒否する。機体値・日時は候補の再現例であり、実機の値へ採用したものではない。

```text
python -B -m balloon_sim inspect references/flight_fixture/hokkaido-weather.json.gz
python -B -m balloon_sim simulate examples/hokkaido-simple.json --weather references/flight_fixture/hokkaido-weather.json.gz --output <未使用の北海道結果ディレクトリ>
python -B -m balloon_sim simulate examples/wakayama-isothermal.json --weather references/flight_fixture/wakayama-weather.json.gz --output <未使用の和歌山結果ディレクトリ>
python -B -m unittest discover -s tests -p "test_flight*.py" -v
```

途中停止でも受理済みの軌道点と理由を保存する。生成reportを開いて軌道と高度を確認し、`complete`, `stop_reason`, run/valid/入力hashを読む。HTMLが生成できたことだけを着地成功にしない。全飛行成功も予報誤差や地形精度の認証ではない。再現用原設定を実飛行値へ変更した場合は、別の結果ディレクトリへ出力して比較する。

新しい予報は`examples/gfs-japan-request.json`の内容を用途に合わせて明示的に設定し、COMMANDSのfetchを使う。日時を古い例から無言で現在へ変換しない。00UTC runが配信途中なら、取得器のfailure.jsonと来歴を残し、別run/別出力で再実行する。0.20では自動fallback・cache再開・恒久的な取得遅延保証は実装していない。

原rawの再読は外側`weather-evidence/gfs-japan-expanded`を入力に`weather.replay_gfs`またはCOMMANDSに示すCLIを使い、新しい出力名を渡す。原場と2回再読のJSON payloadは同一、現writerのgzip2本も同一となった。原acquire開始時のgzipには生成時刻headerがあったため原gziphashは異なる。`replay-verification.json`はpayloadとbytesの比較を別々に残す。新しいwriterはmtime0を明示し、同一decoder/入力でbytesを再現する。

### 理論・構造ガイドをTeXから生成する

`THEORY_GUIDE.tex`と`PROGRAM_GUIDE.tex`が編集元である。PDFだけを手で直さず、式・仮定・API・主要機能の対応をTeXへ戻す。今回使うXeLaTeXは既存専用Windows環境`C:/Users/genia/.local/share/balloon-docs/TinyTeX/bin/windows`、フォントとfontconfigは同じ専用環境を使う。検索用textは既存Codex文書Python `C:/Users/genia/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe` のpypdf 6.10.0で抽出する。Miniforge baseにはpypdfがなく、同梱Popplerにもpdftotextがないため、存在を仮定して呼び出さない。同梱Popplerのpdftoppm/pdfinfoは描画・PDF情報点検に使える。新規導入せず、実行プロセスだけで既存の実行ファイルとフォントを解決し、OS全体のPATHやフォント登録は変更しない。

```text
C:/Users/genia/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -B tools/build_guides.py . --output-dir <repo外の未使用buildディレクトリ>
C:/Users/genia/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -B tools/build_guides.py . --output-dir <別の未使用buildディレクトリ> --publish
```

初回の確認だけなら`--publish`を付けない。採用する生成実行では`--publish`を付けると、**両ガイド**のXeLaTeX3回・pypdfによるtext抽出・Overfull/Missing-character点検に成功した後、PDFと検索用textをdocsへ複写する。TeXは編集元なのでこの複写で上書きしない。未成功の片方だけをpublishしない。出力先は既存なら拒否し、XeLaTeX/pypdfの依存とTeX原本を確認してから新しいbuild先を作る。shell-escapeを無効化し、入力・出力hashと各passのstdout/stderrを新しいbuild先に残す。

この成功判定は構文・文字抽出・特定警告を対象とする。生成PDFの全ページを画像化し、数式、表の行、改ページ、文字欠け、リンク/参照を目視点検してから表示受入を記録する。ビルド成功をPDF見た目の確認へ置換しない。PDFの時刻metadata等があるため、必ずしも全bytes一致を文書再現の条件にせず、固定source・環境・生成logと抽出内容・表示点検の範囲を記録する。旧PLANの生成・採用範囲は前節までの契約を維持する。

## 0.21.0：構造ガイドだけの再生成と参考PDF原本

固定比較元はPR21統合M200 `6d86fa7149fa8d2d0879a20fc3fe18241bc690e1`、外側`structure-guide-0.21.0/base-0.20.0`の全80パス。構造ガイドは実在実装の親子階層と依存図を編集元TeXに記す。詳細な処理説明はIMPLEMENTATION_NOTESへ移し、旧版の情報対応とコード/表示の確認を外側証拠へ残す。

`tools/build_guides.py`に`--guide PROGRAM_GUIDE`（または`THEORY_GUIDE`、繰返し可）を付けると選択した冊子だけを生成する。省略時は従来通り両冊。`--publish`は選択した全冊が成功した後にそのPDF/txtだけを複写する。新規出力先・既存依存・3回コンパイル・警告と全ページ表示確認の条件は変えない。COMMANDS C-07の同じ専用環境を使い、`build.json`に選択名・原TeX・出力hashを記録する。今回THEORYとPLANは再生成しない。

提供風資料は `references/user_supplied/wind_analysis_report.pdf` に元の `Downloads/main.pdf` のバイトをそのまま保存する。TeX原本は未提供なので生成資料の対を捏造しない。検索用 `.txt` は既存文書Pythonのpypdfでページごとに抽出し、先頭に出所/抽出方法/表示の限界を付ける。再抽出の記録と受入hashはWIND_REPORT_REVIEW、外側`accept_wind_reference.py`/`wind-reference-evidence`を参照する。PDFのレイアウトと式の解釈は原PDFへ戻る。tar/統計DBの大容量配布・更新設計はT-011/U-009へ残し、この参考PDF保存と同一視しない。

提供PDF例外はCONTINUITYの当該reference資産の`provided_pdf`で宣言し、SOURCES参照と原本SHA256をstateで検査する。自作PDFのTeX/PDF対は従来通り必須。原本変更や出典不一致を例外へ丸めない（D-158）。

## 0.50：保存結果の復元・raw窓共有の生成/検査記録

比較元は0.49 C2 `22799fe2c20627321e9c60367e974b92e16497cf`。既存の専用Python/Node/TeX環境を使い、生成/試験/診断はrepo外のP500へ分けた。新依存の導入や科学式の改定による性能改善を記録したものではない。

- backend最終 `backend-tests500-02.xml` は99件中98成功・1明示skip、失敗/エラー0。提供DBのopt-in検査は未実行のまま。初回のTemp操作拒否と許可された再実行を区別した。
- frontend最終 `frontend-validation500-review06.json` / `frontend-tests500-review06.json` は100成功・skip0、型検査/build成功。直前review05の子process起動拒否を成功扱いせず、review06の実行票を最終根拠とする。出力先はP500/dist-review06。
- PROGRAMは担当TeXから別作業コピーで25頁を生成した。変更7頁（1/4/6/8/11/15/24）を主担当と独立担当が視認し、初回の1/8頁を訂正して再確認した。`program-publication500.json` が生成入力と正本TeX/PDF/txtの一致を固定する。この先行票は変更7頁の視認で、後続の全頁レイアウト確認は次段へ分ける。THEORY/PLANは再生成していない。
- 実UIは `ui-review500.json` のローカルQA行程へ分ける。CSPで外部画像/通信を遮断した503/404再読、群/時刻/図の復元を確認したが、全ブラウザ・地域背景・新Google接続を受け入れたものではない。型/build成功だけを画面受入の証拠にしない。

後続で主担当は残18頁も直接視認し、全25頁の文字/図の収まり、欠けの有無、階層と横依存の可読性を確認した。追加問題は検出されず、`program-root-final-visual500.json`（SHA256 `2b7ac132d33a1bf6f8dc1aad660837c9250454fc1bfd9395280ac376f6acfa0d`）が対象PDF/全頁PNGを固定する。publication票はこの後続票を参照する。科学本文全体や全source動作の再証明には広げない。次のZIPは変更7頁確認時点を保持し、後続視認票を含むよう無言で置き換えない。

[0.50証拠ZIP](../references/development_evidence/operational_continuity500.zip) は143 member、3,795,156 bytes、SHA256 `2ce8cab4b09450cab2961157a66278b3c69bf9b64df855600a715285297853a9`。旧0.48/0.49 ZIP内の28入力をhash付きで参照し、原実GRIB再生は外部通信0、一飛行profileは上乗せ/包含関係/未消去cacheを含む限定診断として残す。旧原本・runtime state全体をこの小束へ複製したものではない。

元Gitは旧1193＋診断112追加の1305を保全する。0.50の最終管理検査・Git保存・保存後照合はこの記録時点で未実施。次の場照会/積分の費用比較、元UTCの過去JRA場の有限接続はS36の指示へ戻り、生成成功や今回のraw再利用をその先行実績にしない。


### 0.55 3D表示用格子の配布

通常のfrontendビルドは `frontend/scene3d/data/WW15MGH.DAC`（2,076,480 bytes）をscene3d/dataへ複写する。実ASLの3D表示は同originからこれを読み、追加の外部APIへジオイド高を照会しない。固定SHA・出典と破損検査は同data/README.md、単体検査はscene3d-datum.test.tsへ戻る。Googleの写真meshやキーをビルドへ含めない。
