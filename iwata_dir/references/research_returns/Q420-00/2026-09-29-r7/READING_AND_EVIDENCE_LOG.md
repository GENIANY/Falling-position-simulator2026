# 統合研究の参照・批評・実行記録

対応本文：`CODEX_RESEARCH_REPORT.md`、改訂7、依頼Q420-00／0.42.0、2026-09-29。本書は第七巡の実施と、第一〜第六巡から残す根拠・失敗・制約を収録する**現在の一冊**である。過去報告を別に入手する必要はない。研究の判断は統合本文を読む。ここは何を読み、どの範囲を再実行し、どこを未確認のまま残したかを点検するための記録である。

# A. 第七巡の判断と証拠

## A.1 基準・アクセス・自己完結の確認

第六巡一式 `Q420_R6_20260929_package.zip`（25,443,184 bytes）を読み、341 memberのパス・symlink・CRCを検査した。manifestの340実体は全件size/SHA-256一致。新しい独立フォルダへ展開し、`CODEX_RESEARCH_REPORT.md`と`READING_AND_EVIDENCE_LOG.md`を読み直した。第七巡の作業・結果は別の新規ディレクトリに作成し、第六巡一式や元資料を変更していない。

GitHub連携で実repo名 `GENIANY/space-balloon-simulator-jp`、ID1373721672、Private、既定mainを取得した。mainのHは `4e3e4db0d047af9479bcd68bfc2553eeb71efcc9` で前回と同じ。root tree `61f6853081aea968222f341e2b62dbada642dabc`、第一親／資料束の比較元M401 `55100867df2bef615c3131228c7c75adf31c9833`、第二親 `3f67124960063a20ede16ca38f8716402a802809` を区別する。root READMEの冒頭をH指定で取得し、同じblobの保持原本でR0〜R5全文を読んだ。`models.py`の物理式もH指定の原行40〜90を独立に取得した。原ファイル中の保存前PR状態を、ライブで得た統合後の状態へ無断訂正していない。

Drive指定rootとBRIEF本文も実取得できた。rootは `1Q9B9JAJf5f4XHbHvl0qGbQZ9UXIZ0JfV`、展開済みprojectは `12VweWIPpqDb3ppTZiMLTC_2HO6UlAkN3`、BRIEFは `16LQ4Yc-F1isTnf58jq0xMG7cspD6ko6K`。JSON表示が打ち切られた本文の残りは保持原本で読む。全Drive資料の再取得・全フォルダ同一性・約498MBの元main ZIPの読取りを行ったとはしない。Pythonの実行とファイル読取も成功し、開始条件の欠落はなかった。

`provenance/source_audit_r7.json`は44保持原本について、今回の全bytes、SHA-256、Git blob、期待値、所在を持つ。44/44一致。期待値の大半は固定Hの過去取得証拠を継承し、READMEとmodelsは第七巡の取得でも照合した。これは全44ファイルを新規取得・全文精読したという意味ではない。`provenance/live_reads_r7.json`は呼出先と観測の要約票であり、ツールの完全な生応答を装っていない。

第七巡でも最新版本文へ内容を統合した。第4章へ入力の等価性・変更後の分岐・同時分布、第11章へ較正の目的、第13章へ入力と運動キャッシュの別、第14〜16章へ変更先・証拠・不足を受け入れる。第六巡の有効な数式・数値・反例・代案・未決を削って差分報告にはしない。`INTEGRATION_R7_MAP.csv`は前回見出しから本版へ対応を点検する補助で、読む手順ではない。既存のE01〜E06のデータは今回の`studies/`に保持する。

## A.2 前回の何を批評し、焦点をどう変えたか

前版は、元量の一度だけの抽選、同条件比較、較正と検証の分離、対象窓と取得窓の区別、情報時点、診断用履歴を既に扱っていた。「前版が全係数の一意同定を推奨した」とは批評しない。

不足は、それらの注意を**現行の計算式が実際に区別できる入力と、利用者が次に変える条件**へ接続した証拠が薄かったことにある。入力を増やして全欄を埋めたり、過去履歴へ一組を合わせたりしても、同じ搭載変更を評価できるとは限らない。逆に手持ちの質量・ガス量で限定できる場合は、その情報を使えばよく、全ユーザーへ同定作業や相関行列を要求すべきではない。

現行式の等価変換を代数で導き、同じ原GFSと未変更の本体で履歴が一致する四入力を確かめた。次に同じ絶対量の搭載変更を施し、予測が分かれるかを調べた。また周辺分布だけを保存する代案へ、七つの周辺分布が完全に同じ直積群を反例として当てた。結果は、入力の同時標本と適用条件を保存し、変更後に同じ群へ戻る推奨を強めた。

元ニーズとの接続は、製品・既知情報から入力負担を減らすこと、同地点モデル比較、入力／派生量の分布診断、粗い観測の説明、条件変更と再訪である。物理量をr/c/b/dへ全面置換するUI、一つの最良適合点と独立CVへ潰す案、全解析へ較正を必須化する案は採らない。気象の新規取得や輪郭手法を不要としたわけでもない。第六巡までの別課題の知見と未決は現在本文に残した。

## A.3 今回の実読・再利用・未読を分ける

原行は各原ファイル自身の行番号である。記載の章・節と、実際に読んだ本文を区別する。検索、抽出、hash一致、描画だけを全文精読・視認と数えない。

| 資料 | 第七巡に行ったこと | 継承・未確認の境界 |
|---|---|---|
| 依頼文、前回統合報告・統合ログ | 新添付33行、報告1146行とログ393行を分割して読み、R6一式内の実体も参照 | 過去全コードの全行再監査ではない |
| README／AGENTS／CONTEXT | README全文、AGENTSとCONTEXT第1〜5節・関連する原要求を現在文脈と保持原本で照合 | 全744行の履歴を新規全件監査したものではない |
| BRIEF／UI_WALKTHROUGH／TASKS／REVIEW_042 | BRIEFはliveと保持原本、UIは前半の現在文脈と原行64〜160、Q420・五課題、既存の交絡・相関・観測例を確認 | 書面UIは実物操作ではない。過去の担当による内容確認を本巡の盲検としない |
| INTEGRATION_DESIGN／VISION | inputs、distribution、paired-meaning、diagnostics、lifetime、save-and-reopen、models、burst、過去照合等の選択本文をHTMLから抽出して読取。長い取得の一部は打切りがあり、保持原文・同じHの既読も併用 | 全HTMLと全旧模型の新規精読／ブラウザ操作とはしない |
| PLAN／DOCUMENT_CONTROL／CONTENT_MAP | PLAN位置づけ・第1章の現在状態、原行276〜366と573〜640、DC-JUDGMENT、CONTENT_MAP情報依存を読取 | PLAN10章中の未再読範囲や全科学出典は固定Hの既読として継承 |
| BACKLOG／UNCERTAINTIES／RUNBOOK／版・健康情報 | T-003/005/006/010/011/016/017とU-020〜022の現行行、RUNBOOK startとS35の関連本文、版遷移、全276 scan_indexの期限・版差 | 全HTML・全台帳の意味を点検していない。公式管理スクリプトは完全ツリーがなく未実行 |
| 現行config/models/events/numerics/trajectoryとenvironment使用部 | 入力・運動・相・停止・記録の対応を確認し、同一の9モジュールを新計算で使用。models原行40〜90はGitHubから再取得 | 新規物理実装や9モジュールの全行監査、全プロジェクト回帰ではない |
| ENV／WEATHER／IMPLEMENTATION_NOTES | 必要量・支持・入力契約・停止の関連節を現文脈／固定H本文で確認 | GFS/GEFS/ERA/JRAの全提供仕様は第七巡に再調査していない。第六巡確認の時点を保持 |
| 原フィードバックPDF | p.1〜4本文を抽出、p.3を画像として視認。既知製品・仮CV・診断・保存の関係を読取 | 本巡にメーカーの分布・全製品を科学採用したものではない |
| 原風PDF | p.17/35/53/54の本文を取得し関連箇所を読む。p.35・図14、p.53・図32を画像として視認 | 全114頁再読、全図の再視認、原気象DBの再集計ではない |
| 04_flight_physics_research.pdf | 物理p.10/11/12/16/17の本文を取得、主にp.11〜12の抗力・鉛直風・熱・入力識別の関連本文を読取 | 第3.4節の既存問題意識を使用。原論文の全文再読や四技術巻の全精読ではない |
| Excel原資料／Handbook／EXCEL_ANALYSIS_REVIEW | 原量・同定・条件付き評価の既存読取を継承し、現在のレビュー・索引へ戻る | 本巡にExcel全セル再監査、Microsoft Excel再計算、原15便再フィット、公開便再解析はしていない |

画像読取は既存のPDF画素を描画して行い、OCRは使用していない。風図の見せ方と、その著者の地域・係数・改善率を分けた。新しい数値図2点はmatplotlibで個別に生成し、実画像で読んだ。本体UIを操作した証拠ではない。

## A.4 実験の定義・来歴・再現

E07の基準はHe0.5 kg、膜1.0 kg、搭載物1.0 kg、Cd0.47、径8m、膜を全て失う仮の有効下降質量1.0 kg、基準密度1.225 kg/m³で5m/sとなるCdAである。ガス・膜・搭載物・下降質量・CdAをa倍、Cdと径をa^(1/3)倍する。四scale(0.75,1,1.25,1.5)と搭載追加0.5kgは、スクリプトで定義してから計算した。メーカーの四製品や原15便を同定した入力ではない。

和歌山／北海道の二つの保存fixture、元exampleの放球位置・高さ・03:30 UTCを使う。元exampleの定速または直接高度破裂を、そのコピー上で等温・径破裂へ替えた。原本を変更せず、研究configを保存した。本体は同じHのコードを無変更で使用し、積分中のネット取得・別run混合をしない。

| 群 | 実際の計算 | 数に含めないこと |
|---|---|---|
| family_w／family_h | 四つの等価入力を各保存場へ通す8飛行 | 異なる8実飛行観測や新規気象窓ではない |
| payload | 和歌山の四仮説へ同じ絶対量0.5kgを追加 | ガスの再充填、実施推奨、単独の物理係数だけの効果ではない |
| cross_0〜3 | ガスscaleと残りのscaleを直積化した非対角12飛行。対角はfamily_wを再使用 | 16を全て新規独立計算と数えない。七周辺分布は同一だが同時分布は異なる |
| refinement | a=1/1.5の基準／変更後を最大刻み5秒で4飛行 | 新しい機体・気象情報を得た標本ではない |

完了した主計算は計28関数呼出し（24構成条件＋4刻み確認）。主解析の結果・索引は36 JSON、summary／joint_distributions／pointwiseは3 JSONである。初回に中断した二件は`evidence/interrupted/`へ保全し、28回や解析に重ねて数えない。

二地点の等価群は丸め誤差水準で運動が一致し、搭載変更後の四着地点の最大相互距離は19.755 kmだった。直積16組中12組の着地位置の最大相互距離は48.185 km、二組は初期自由浮力不足、二組は経度支持外。**48.185 kmは12完了組の記述だけ**で、全16の領域・上限・95%ではない。主張の論拠は本文式(I1)〜(I4)と同梱データへ置き、ここで実飛行精度へ膨らませない。

197検査には、50桁Decimal別式と108局所評価、Fractionによる七周辺分布、raw保存値からの履歴比較、停止の母数、既知ガスによる四仮説の限定等を含む。検査側は飛行核・研究生成・集計関数をimportしていないが、同じ研究担当が書いた別ロジックであり盲検ではない。

移設した一式から全8群と後処理を再生成し、**39 JSONと図2点がバイト一致**した。`numerical_reproduction.json`と`figure_reproduction_process.json`に対応を保存する。入力・出力・物理閉じ方・数値条件が同じ環境での一致であり、別OS・別ライブラリ全面互換性は未確認である。

既存研究の検査も分けて実施した。`verify_current.py --section earlier`は9処理、`--section new`は3処理が成功し、E06/E05後処理の13 JSONとE07後処理3 JSONが一致した。`all`を一回で起動したとはしない。既存の全飛行・全図を再生成したわけではない。現行検査の記録は`evidence/revision7/`、E07独自の実施票は同研究の`evidence/`へ置く。

## A.5 失敗と警告を、結果から切り離して残す

**複数群を同じ外側時間枠に入れた。** 初回はcontainer.execの45秒枠へ複数群を直列に入れたため、`Command failed because it timed out.`となった。family_wは成功票を持ち、family_hは二つの結果ファイルだけがあり索引がなかった。後続のプロセス一覧にstudyは残っていなかった。不完全な群を完了とせず、研究出力内の`evidence/interrupted/family_h`へ保全し、一群ごとの呼出しで新しい主出力を作った。権限変更や承認回避ではない。経緯は`outer_timeout.json`、当時の補助起動コードは`initial_group_runner.py`に残す。

**子処理の成功後に外側ツールが時間切れを返した。** 初回refinementは子プロセスreturncode0、所要32.479秒、stdoutと五出力を保持した後、外側が同じtimeoutを返した。出力を読み戻して別式検査へ通し、子処理の成功とツール全体の時間切れを別に記録した。外側全体が超過した内部原因は未確定。後の再実行は障害を隠すための反復ではなく、別配置による全数値再現試験の一部である。

**再生成の外側に端末の警告が出た。** 複数のcontainer呼出しの末尾に制御文字`ESC[3J`と `TERM environment variable not set.` が表示された。各子の保存stderrは空、記録したexitは0だった。端末後処理のどの内部条件が原因かは特定していない。環境変数・起動設定は変更せず、数値・索引・再生成一致を別に点検した。

**一次論文PDFの取得が一回失敗した。** Galliceの公式PDFをWebで取得する一回の試行はタイムアウトだった。公式論文ページの要旨は取得できたので、その範囲を使用した。同じ失敗URLを繰り返し要求せず、全論文を再読したとは記録しない。保持していないエラー全文を創作しない。

旧巡のClientError、Spreadsheet warmup、PermissionError等は下段に当時の観測として保持する。第七巡にそれら全てが再発したという意味ではない。今回のmatplotlib生成はreturncode0で図とプロセス記録を保存した。

## A.6 外部一次資料と、新規性の範囲

第七巡で新たに本文へ結んだのは、GalliceらのAMT2011公式要旨（`https://amt.copernicus.org/articles/4/2235/2011/`）と、Brynjarsdóttir–O’Hagan2014の著者公開要旨（`https://www.tonyohagan.co.uk/academic/abs/simmach.html`）である。前者はLUAMIからの抗力曲線・熱拡散・夜間への限定、後者は予測と物理パラメータ推定、モデル不一致との交絡という問題を確認した。論文の全算法・全例を追試していない。

本稿の等価変換は、これらの論文から気球の式を転記したものではなく、固定Hの実式から導いた研究である。識別可能性やモデル不一致という一般概念を新発見としない。新規性は、この現行核のどの元量が運動へ同じ効果を持ち、その同じ履歴からの条件変更・同時分布・保存がどこで分岐するかを具体化した範囲にある。

GFS／GEFS／ERA5／JRA-3Q、製品平均径、SQLite等の外部運用仕様は、第六巡までの確認日・内容を保持した。第七巡に現行可用性を再検証したとはしない。非公開資料を一般Web検索へ送ったり、外部プレビューを使ったりしていない。

## A.7 READMEの継続、未確認と次の批評

| 復旧・継続の観点 | 第七巡の結果 |
|---|---|
| RC-IDENTITY | live H／Private／main、READMEとmodelsを固定取得。44保持原本の期待blob一致。全repo cloneではない |
| RC-GOALS | 三用途、同地点モデル比較、少入力と既知製品、独立した風図、分散・干渉・再訪を保持。30kmは代表規模 |
| RC-HORIZON | P0基盤→P1実現性・早期評価→P2一飛行→P3日本適合→P4必要な物理→P5不確かさ→P6利用・保守。評価を後回しにせず、今回の研究を全機能実装としない |
| RC-DEPENDENCIES | T-003の共有可能な要求からT-006の対象・必要量へ、そこからT-005の取得へ進む。T-006→T-011の使える観測が、T-010で追加する物理・未知量の判断を支える |
| RC-DECISIONS | 等温初期・追加実験なし・GFS方針と未採用母数を分離。本稿の等価性・同時仮説の提案は採用決定でない |
| RC-STATE | 単一飛行核を使用。実UI／実気象MC／過去場一般接続は未完。mainの統合確認と資料の保存前「未受領」を分ける |
| RC-LIMITS | 正式管理検査・全回帰・実UI・Windows二台・原Excel再計算・実飛行精度・実観測フィットは未実施。新probeは指定されていない |
| RC-NEXT | 本文第14章のA/C接続で、既知量→未確定な入力群→同じ変更→結果と保存後再訪を試す。季節窓・情報時点・領域法の未決は別に保持 |

CONTENT_HEALTHの全276 scan_indexへ2026-09-29・現policyを適用し、日付超過0、初期期限超過0、版差のadvisory159範囲だった。advisoryは全159本文の点検完了を意味しない。`provenance/start_selection_r7.json`に限定を記録する。完全ツリーでの`check_health.py`は未実行である。

次の批評で最も効く反証は、既存の機体情報を加えると今回の非一意性がどれだけ残るか、異なる閉じ方や有効量の入力へ替える方が人間に自然か、同時標本の表示・保存が比較を助けるかである。仮説四組を固定要件として増殖させる方向にはしない。実物に対する有用性を確認していないことを隠さず、式と数値の有限な結果は利用できる形で返す。

# B. 第一〜第六巡から保持する累積根拠

以下は第六巡時点で統合した根拠・実行・失敗の記録を本版内に保持したものである。この節内の「今回」「本巡」「現在版」は**第六巡時点**を指す。第七巡の実施・現行入口・追加判断は上のA節と統合報告本文が担当する。当時の数値・エラー・読取範囲を黙って第七巡の実績へ変換しない。旧報告ファイルを読む依存はない。


対応本文：`CODEX_RESEARCH_REPORT.md`、改訂6、依頼Q420-00／0.42.0。本記録は第一〜第五巡から残す証拠・制約も含む現在版である。旧報告を読む前提はない。過去の実行は実行時点を保持し、今回の成功へ足していない。

## B.1. 今回の是正と、確認できた入口

利用者は、最新版だけで既往研究の有効な情報を理解でき、過去報告・スレッドをたどらずCodexへ渡せることを要求した。従来は「以前の領域法を維持」「前回の入力方針を参照」としたため、次の読者に研究史を再構成させていた。修正を目次・旧ZIP同梱だけで済ませず、分野別に現在の結論・式・主要数値・反例・撤回理由・未決を本文へ統合した。

今回の添付 `Chat_研究依頼.zip` は163813 bytes、SHA256 `ef81afadacc3e6444986b1479179fa2d7fe944201aca2d2c87cd0d48529f9c78`。16entriesのうち通常ファイル10件は、第一〜第五巡それぞれの研究本文と参照ログである。パス・symlink・CRCを点検して、新しい作業場所へ展開した。10本文すべてが保持している各巡の配布ZIP内の同名本文とバイト一致した。これは10文書の主張がすべて正しいことの証明ではない。

| 入口 | この巡で行ったこと | 範囲 |
|---|---|---|
| 添付研究ZIPと依頼文 | 実ファイルを読み、ZIPの安全なパス・CRC・本文一致を確認 | 元mainの約498MB ZIPではない |
| 過去成果一式5ZIP | 存在・CRC・各本文と必要付属物を確認、新規領域へ展開 | 数値・コード・図の出所を保持し、過去本文への依存を取り除くために使用 |
| Google Drive指定root | connectorでフォルダの内容を取得 | `1Q9B9JAJf5f4XHbHvl0qGbQZ9UXIZ0JfV` |
| Drive BRIEF | connectorで本文を取得、保持する固定Hの本文と対応 | 巨大JSONの表示が打ち切られた部分は、保持している同一実体の本文で読む |
| GitHub main | connectorのGETでHEAD・親・treeを取得 | H=`4e3e4db0d047af9479bcd68bfc2553eeb71efcc9` |
| GitHub repo | connectorのGETで実名・ID・Private・既定branchを取得 | `GENIANY/space-balloon-simulator-jp`、1373721672、main |
| root README | H指定で冒頭を取得し、同じblobの保持原本を全文読む | 期待blob `4aa1757e8346824c0c7fc54ee2c1d0870faefdd2` |

展開済みrootはDrive `12VweWIPpqDb3ppTZiMLTC_2HO6UlAkN3`、researchは `1qPIkKpvydn2l9raSMxGiCxxAvHIe4M-t`。今回rootとBRIEFが読めたことを、全Driveファイルの一括取得成功と書かない。元main巨大ZIPは再取得・解凍していない。利用者は展開フォルダによる代用を認めている。

本文の基準はPR29統合後のHであり、資料束の比較元M401 `55100867df2bef615c3131228c7c75adf31c9833`と区別する。ファイル内の保存前「PR29未統合」「回答0件」を、ライブ状態の代わりに使っていない。main・Drive・元ファイル・既存成果物・権限は変更しない。

## B.2. 受入の方式と、何を失わないようにしたか

`INTEGRATION_MAP.csv` は旧10本文の節を現在の本文・本ログへ対応させる。旧節番号は来歴の識別にすぎず、旧本文を読む指示ではない。研究本文の内容は主に次のように移した。

| 旧研究で得たもの | 今の受入先 | 修正した扱い |
|---|---|---|
| 近似と禁止域の反例、有限2048点、補正／層化の比較 | 本文第7章 | 補正方式を標準にしない。推定対象と費用、標本の対応の効率を分離 |
| 領域スコア・含有率・順位較正・形の比較・格子の失敗 | 第8章 | 知識のある母分布Qを使う評価と製品運用を区別。未較正で通常分析を閉ざさない |
| 入力逆算、製品表、階層配分、GFS交互作用、支持・地表・公開手順 | 第3〜6・10〜11・13章 | 新規性を既出構想と限定検査へ分離。最終DB／物理モデルの採用ではない |
| 高度目的と着地条件の対立、診断標本、部分事象、比較保存 | 第3・9・12〜13章 | 順位を決めない用途へ合否を強制しない。元群と全体の再評価を保持 |
| 同上昇時間のモデル差、符号付き内訳、32飛行、風分布、間引き | 第10〜13章 | 内訳は原因割合ではない。表示用と解析用記録を分ける |
| 全巡で残った未読・未実行・環境失敗 | 本文第15〜16章と本ログ | 成功件数の合算や、過去実績の今回への付替えを避ける |
| 第六巡の対象窓・情報時点の二例 | 第5章、各入力・表示・保存の帰結 | 共通完了群でも母集団が変わり得る。実現後の最良選択を実施可能な予報方策としない |

過去の研究本文そのものは配布一式の必読付録にしていない。数値・コード・図等307実体を新しい `studies/` の分野別ディレクトリへバイト不変で収録した。過去本文と旧配布用README等19実体の指紋は `provenance/narrative_inputs.json` に残し、本文に必要な内容は統合した。`provenance/evidence_transfers.json` が付属物の旧位置→新位置・hashを保持する。旧コード内のR1等の説明ラベルや証跡の絶対パスは履歴であり、実行時の探索先ではない。

この対応表とリンク検査は、移行の欠落を見つける補助である。意味をすべて自動証明するものではない。全情報を無批評で現在の推奨へ昇格させず、既存案への重複、後に反証された主張、未採用の統計母数を区別した。

## B.3. 原資料の同一性と、実読範囲

### 3.1 同一性

保持原本44実体について、新たにSHA256とGit blobを計算し、固定Hの期待blobに一致した。一覧は `provenance/source_audit.json`。期待値の大部分は以前のGitHub固定取得の証拠を引き継いだもので、44件を全て今回再取得したわけではない。原PDF2件・原Excel3冊も同一性対象であるが、バイト一致は全文精読・科学採用・Microsoft Excel再計算の証拠ではない。

### 3.2 今回読んだもの／固定Hの既読を再利用したもの

| 対象 | 読み方と範囲 | 残る境界 |
|---|---|---|
| 第一〜第五巡の研究本文5件 | 添付ZIP内の実体を照合し、式・数値・推奨・反例・未決の節を分割読取。既に取得された同じ本文も併用 | 各過去コードの全行を盲検監査したわけではない |
| 第一〜第五巡の参照ログ5件 | 読取範囲・実行・環境失敗・未確認の節を確認し、現在のログへ統合 | 長いツール表示で一度打ち切られた取得を全文読了とせず、必要な範囲へ分割。過去の実績は新実行に数えない |
| 依頼文、BRIEF、UI_WALKTHROUGH、TASKS、REVIEW_042 | 目的と三用途・全五課題・具体行程・反例を読む。BRIEFはlive、その他は固定Hの保持本文／既取得本文を併用 | 書面UIは現物の全操作・視覚品質を代替しない |
| PROJECT_CONTEXT | 第1〜5節とRPT-043以後の関連要求を再確認、過去取得本文を併用 | 全744行の履歴を本巡に新たに意味監査したものではない |
| INTEGRATION_DESIGN | inputs/input-changes、distribution/paired-meaning、weather/long-samples、lifetime/save-and-reopen、technology/service-boundary/gatesの関連本文 | 実サービス起動・DB移行・画面接続の試験ではない |
| SIMULATOR_VISION | models/burst/distributions、比較・分析、年間／季節、段階計算、費用・保存、過去の設計批評。選択節をHTMLから抽出し読取 | 全旧模型ZIP・全ブラウザ動作は未読／未検査 |
| README/AGENTS、DOCUMENT_CONTROL、PLAN、DECISIONS | 復旧R0〜R5、現在の一組、DC-JUDGMENT、方向P0〜P6、旧案受入と採否の境界。固定Hの既読を継承 | 旧手順を現在の実行許可へ変換しない。全版履歴・全根拠の再監査ではない |
| ENVIRONMENT_CONTRACT、WEATHER_DATA_GUIDE、IMPLEMENTATION_NOTES | 現行の有限モデル／場／記録、長期の対象、支持・高さ・時刻、提供元と費用 | 一般のモデル面／全提供元の復号と本体接続は未実施 |
| 9モジュール・2fixture・2example | 現行の設定・物理・相・記録・支持を保持し、同梱検査から使う | 第六巡は旧全飛行の再積分ではなく、主に保存出力の再検査 |
| EXCEL_ANALYSIS_REVIEW、原分析Handbook・技術／監査／検証資料 | 元量の状態・順逆算・径と厚み・原記録・条件付き検証の必要段落、同じ資料の既読を使用 | 原分析ZIP全170ファイルの新規全member検算、全273数式の科学再監査、Excel本体再計算なし |
| WIND_REPORT_REVIEWと風PDF | 図の問いと原法・モデル／場／誤差の区別。今回画像読取は下記 | 原JRA時系列・風DBの再集計はなし |
| CONTENT_MAP、REFERENCE_LOG、VERSION_HISTORY、CONTINUITY、BACKLOG、UNCERTAINTIES | 現在の根拠／実績／タスク・未決へ戻る索引と関連範囲。固定Hの既読を継承 | 巨大JSONや全過去台帳を新たに意味監査したと数えない |
| CONTENT_HEALTH | policy・全276 scan_indexへ日付／版経過規則を適用 | 公式check_healthを完全作業ツリーで実行したわけではない |

### 3.3 原図の今回の確認と累積読取

今回PyMuPDFで、フィードバックp.1〜4、風PDFp.35/36/48/89/90を描画し、必要な本文を抽出した。画像として明示的に読んだのはフィードバックp.3、風p.35とp.90である。描画しただけの残りを目視済みへ数えない。p.35の年間×高度の共通軸、p.90の図66/67の距離と相対差、フィードバックp.3の入力経路・CV・分布診断・保存の関係を、現在の論旨へ戻した。OCRは使っていない。

累積した原図読取には、初回の風PDF指定9図（14/15/16/17/19/20/23/25/29）、原法と近似・延期の章、フィードバック全4頁がある。第二巡は統計・輪郭関連の原本文へ戻り、第三巡は風p.76/103–105の本文・図と原飛行表の280非空セル、第四巡は風p.32–35/48/97–99、第五巡はp.15–17/76–77の本文、p.16/17/76の画像を用いた。各時点の視認と本文抽出を区別する。**風PDF全114頁の新規全頁視認をしたわけではない。**

Projectの技術資料は `01_forecast_database_gfs.pdf`、`02_historical_database_gfs.pdf`、`03_implementation_reference.pdf`、`04_flight_physics_research.pdf` の関連検索・本文が参照に現れる。上記4ファイルの正確な表示名は保持実体の一覧で確認した。今回の主張は第04巻の観測／物理の関連本文と、現行repo資料で追えるようにした。四巻を全面改訂・全出典再確認したものではない。

## B.4. 第六巡の研究として、新しく確かめたこと

### 4.1 対象十窓と共通完了七窓

年と原日時を表す架空の十窓、各重み1/10を定義した。A/Bの事象を両方確認できる七窓ではA=1/7、B=3/7で、B−A=+2/7。隠した三窓を含む全十窓ではA=.4、B=.3、差−.1。これは実大気の観測でなく、**同条件比較と対象全体への代表性が別**であることの構成例である。

未知の三窓について構造的な制約を置かなければ、一窓の差は−1/0/1を取り得る。既知寄与+.2、未知重み.3から、全対象の差は[−.1,.5]。未知のA/B真偽の全64補完を別コードで列挙し、上下端の達成と一致を確認した。一窓ずつ確認する16/4/1補完も検査した。既知の機体標本だけを1/10/1000倍に分割しても、重みを保てば対象の未知は減らない。

確率抽出した七窓から対象を推定する場合には抽出設計の推論が使える。この例のような未取得／支持不足を黙って確率標本として扱わない、という限定であり、無作為な部分計算すべてに同じ最悪範囲を必須化する提案ではない。

### 4.2 四状態と利用情報

等重み四状態を二つの観測可能情報群に分け、各群に(A,B)=(0,1)/(1,0)の損失を置いた。許される情報だけを使う四つの決定的方策は全て平均損失.5。完全に実現した状態を見て選べる事後oracleは0。25通りのランダム化確率でも.5になることを別式で確認した。

この例により、再解析を見て良い日時を選んだ成績と、その時点の予報から日時を選んだ成績を区別する。現実の予報に価値がないという実験ではない。充填の逆算が未知Cdを使ってしまう問題と同じ情報制約を、長期・予報の比較へ広げた。

### 4.3 実装と検査の独立性

`frame_study.py` と `verify_frame.py` は別のロジックで、検査側は生成側をimportしない。Fractionと列挙で53項目を検査した。乱数で64補完を近似したものではない。ただし同じ研究担当が作成したコードであり、独立研究者の盲検ではない。厳密な有限例の検査を実気象の精度保証へ換算しない。

## B.5. 累積した実行証拠の境界

| 研究実体 | 以前行ったこと | 今回行ったこと |
|---|---|---|
| approximation | 2048点の線形風反例、有限分散比較、76内部項目、別実装照合、数値10と図2の再生成 | 同梱CSVに対する分類・分散の別実装検査。76を今回再実行数に足さない |
| coverage | 形・較正・希少成分・格子・行複製、147検査、44出力の再生成 | 147検査を今回配置から再実行。全オラクル積分を全て新規生成したものではない |
| input_weather_storage | 二地点基準、2×2と刻み、階層・入力・支持、63検査、27公開試験、数値論理17と図2再生成 | 63検査、新規DBで27公開試験。過去の費用中央値を再測定したわけではない |
| conditional_comparison | 55飛行関数呼出し、188検査、数値52と図1再生成 | 保存出力の188検査。探索的な65km境界／9.3mの選択を事前登録に変えない |
| trajectory_diagnostics | 三モデル、16入力組×二モデル、風感度・刻み・間引き、316検査、数値53と図4再生成 | 保存出力の316検査と後段の移設再解析。気象実現を増やしたわけではない |
| target_frame | 以前の実績はない | 有限定義2データ、53検査、再生成・図・移設検査は最終証跡へ |

件数の中には同じ対象への複数assertion、同一標本の刻み変更、同じ数値の再生成がある。全件を独立した科学実験へ数えない。上記の再検査は新しいローカル出力先で行い、元の数値・コード・過去成果は変えていない。

## B.6. 外部一次資料の読取水準

第六巡では、気球製作所規格表、GFS/GEFS公式inventory、CDS ERA5圧力面、NCAR JRA-3Q、SciPy1.17 gaussian_kde、FastAPI BackgroundTasks、Python3.13 Future、SQLite WAL、PNNL許容限界の公式説明を取得した。書誌確認としてPeherstorferほか2016、Hyndman1996、Inglebyほか2022の出版元／著者側情報も確認した。本文W1〜W16に識別子を収録する。

論文や以前の物理レビューから使う条件は、その確認水準を保つ。Galliceの夜間・機種・校正条件、Inglebyの下降品質、Munzner・Shneiderman・Lempertの設計の位置付けは、今回の実性能や全論文再読ではない。原典の性能改善率を本体へ転用していない。非公開repo本文を一般検索へ投げたり、外部プレビューに渡したりしていない。

今回のWeb openでSciPy1.17 RK45の固定URLは `Internal Error`／`Cache miss`、ECMWF ERA5の一つのlanding URLも `Internal Error`となった。同じURLを反復しない。SciPy gaussian_kdeの対象版、CDSの別の正式データカタログは取得成功した。失敗をライブラリ廃止・互換性欠如・実データ停止の証拠とはしない。

## B.7. 失敗・訂正を累積して保持する

以下は発生した巡を区別した歴史的な観測であり、今回再発したという意味ではない。取得・実行・表示・証跡保存のどこで失敗したかを分け、内部原因を確認していないものは未特定とする。

| 時点と事象 | 結果と対応 | 未確認・保持する境界 |
|---|---|---|
| 初回：元main ZIP取得上限 | 約498MBのZIPを直接取得できず、Drive展開済み資料とGit blob照合へ切替 | 展開全件の一括同一性を認定しない。利用者が代用を許可 |
| 初回：図生成が元の新規ディレクトリを読めない | `PermissionError: [Errno 13] Permission denied`。既存権限を変えず新規の共有可能な出力先へ研究物をコピーして生成成功 | 全ツール間の恒久的な共有保証ではない。完全な呼出しは現 `studies/approximation/data/plot_access_failure.txt` |
| 第二巡：格子較正の全平面を有限箱へ誤集計 | 真の集合は全平面である場合、面積無限・質量1として訂正 | 数値箱だけを統計集合の代用品にしない |
| 第二巡：名目較正順位の修正、再生成のタイムアウト | 実際の修正内容と再確認は次の抜粋に保持 | 旧ログにない例外全文・実測時間を創作しない |
| 第三巡：artifact_tool起動待ち | TimeoutError。Excelのインポート成功とせず、原値・式をXMLで読む別経路を使用 | Excel本体再計算とレンダリングは未確認。元のスタック全行は保管できていない |
| 第三巡：図再生成後の証跡JSON保存 | PermissionError。生成図の一致とログ書込み成功を分け、container側でパス・bytesを再確認し新規証跡を作成 | 権限変更なし。途中副作用を未確認のまま成功にしない |
| 第四巡：存在しない外側証跡パス、括弧SyntaxError | 正確なZIP内容から読み直す／括弧を一度修正 | 元資料の破損やPython全体不能ではない |
| 第四巡：最大刻みの10対10.0 | JSON表記だけの差を保持し既定表記を統一、既定／明示の両経路を照合 | 物理入力・軌道値・検査意味は変えない |
| 第五巡：container ClientError | `Encountered exception: <class 'caas.internal.errors.ClientError'>.`。別Python実行で2を得た後、正確な実体を独立読取 | 内部原因未特定。承認や権限を回避・変更したものではない |
| 第五巡：PDF画像がFilesで得られない | 原実体をPyMuPDFで描画し必要頁を見る | 本文取得と図視認の成功を別に記録 |
| 第五巡：Spreadsheet warmup警告 | 子プロセスreturncode0だがstderr警告を保持、数値・図の実体と再生成を別確認 | 原因未特定。研究コードのExcelインポート失敗ではなく起動フックの警告 |
| 第五巡：不完了結果の差が紛れる設計 | 完了フラグだけでなく全飛行比較の既定で不完了入力を拒否するよう研究処理を修正 | 接頭区間は読める。未到達帯を0として全飛行差へ使わない |
| 第六巡：Filesの複合タイトル検索0件 | canonical file IDでR5本文を取得し、添付ZIPの原実体も読んだ | 0件を過去資料の不在と判定しない |
| 第六巡：長いツール本文の表示打切り | 必要範囲の分割と保持実体を使用 | 列挙・描画だけを精読と数えない |
| 第六巡：Web二URLの取得失敗 | 前節の通り | 実気象取得の成否とは別 |

過去の正確なエラーコード・コードブロックを保存している範囲は、下の抜粋に移す。歴史的な絶対パスは観測の内容であって、本版を使うために作るべき場所ではない。元ログが全文スタックを保管していなかった箇所は、今回も補完しない。

### 第六巡の移設検査・図生成における追加記録

過去本文を置かない別の新規ディレクトリへ今回の研究一式をコピーし、作業ディレクトリとPYTHONPATHを旧場所へ依存させず、`verify_current.py`を実行した。9処理が成功し、E06のデータ2件とE05の後処理11件、計13 JSONがバイト一致した。研究スクリプトのPython本文に`/mnt/data`や旧絶対出力先への固定依存がないことも走査した。歴史的な証跡JSONのパス文字列をruntime依存には数えない。

新規図1点を `python_user_visible.exec` の子プロセスで生成し、移設したコード／再生成データからの再生成も成功、画像のバイトが一致した。軸・凡例・上下線が信頼区間でない注記を画像として確認した。ただし二回の子プロセス起動時にSpreadsheet warmup警告がstderrへ出た。returncode=0と実体・再生成一致を確認した一方、警告なしの実行とはしていない。研究用描画コードはartifact_toolをimportしていない。原因の追加診断・自動warmupの修復・権限変更は行っていない。

正確なstdout/stderrは `evidence/figure_generation_process.json` と `figure_reproduction_process.json` に保存した。返された最後の例外行は `artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.`。これは今回も観測した事象であり、第五巡の警告を今回へ単に転記したものではない。上記の数値検査の成功と図生成時の起動警告を分ける。

## B.8. README R0〜R5と今回の終了境界

| 観点 | 現在の内容 |
|---|---|
| RC-IDENTITY | main・Private・既定branch・Hをlive確認、44保持実体一致。全131登録実体の新照合ではない |
| RC-GOALS | 日本向けの使いやすい／検証・開発しやすい分析ツール、無償・特別資格不要、簡易と拡張モデル。三用途と独立風探索を維持 |
| RC-HORIZON | P0基盤→P1実現性と早期評価→P2最小全飛行→P3日本向け適合→P4必要物理→P5不確かさ・妥当性→P6利用・保守。研究は現接続を支え、全物理を先行要求しない |
| RC-DEPENDENCIES | 根拠・要求T-003が対象と評価T-006を支え、それが取得T-005の必要量を定める。T-006→T-011の検証可能性がT-010の物理追加を支える。読順・生成・実行・点検は別の依存 |
| RC-DECISIONS | GFS方針、等温初期、追加同定実験を要求しない方針を保持。径分布・気象較正・最終DB・全UIを採用しない |
| RC-STATE | 一飛行核、人工模型、接続設計、研究返却、Codex採否は別。今回の報告作成を本体のT-016/T-017完了へ変換しない |
| RC-LIMITS | 完全ツリーの公式管理・全回帰、実UI、実飛行精度、新気象取得・復号、Windows／二台／LANは未実施。新probe指定なし |
| RC-NEXT | 本文第14章の三行程を現行版へ照合し、採否と実装・受入を既存担当文書へ戻す |

CONTENT_HEALTHのpolicyと全276 scan_indexにセッション上の2026-09-29／UTC日付規則を適用し、日数・初期日付の期限超過0、版経過advisory159を得た。版経過はadvisoryで、全159の意味点検を済ませたという意味ではない。`provenance/start_selection.json`参照。実行環境の時計とセッション日付は別に記録し、過去に得た外部仕様の参照日を一律更新しない。

この研究一式には秘密・認証値・配布用フォントを含めない。実物の受領・ユーザーPCでの動作・Codexへの取込みは利用者側の確認であり、ローカル生成と同一ではない。

## 付録：訂正・エラーの保持本文（歴史的原記録からの必要範囲）

### 発生時点：第1巡（入力文書SHA256 `3ece7d7f353549d64928ab0655351d7935d7583417d0dd392617ad6918a8d420`）

以下は当時の失敗・訂正の保持である。内部の旧版名・絶対パスは当時の観測を表す。

#### 6.2 図生成時の環境エラーと、その扱い

図を生成する `python_user_visible.exec` が、root側で作成した新規作業ディレクトリを読む際に一度PermissionErrorとなった。数値計算側と図生成側の実行ユーザーが異なり、最初の新規ディレクトリは作成者だけが読めるモードだった。失敗した呼出しでは図は作られていない。

```text
PermissionError: [Errno 13] Permission denied: '/mnt/data/Q420_R1_20260928_l8u7o3ea/data/experiment/cases.csv'
```

会話で失敗を報告し、既存ディレクトリをchmod/chownせず、別の新規出力先 `/mnt/data/Q420_R1_20260928_delivery` を作った。今回生成した数値とプログラムだけをそこへコピーして、同じ図生成を一度実行し直したところ成功した。既存資料、Drive、GitHubのファイルや権限は変更していない。失敗したコードと返却エラーは `data/plot_access_failure.txt` に保存した。

この結果から、この環境で常にファイル生成・全ツール間共有が成功すると一般化しない。一方、今回の数値・図・文書の生成が全て失敗したとも扱わない。操作ごとの成否を分ける。


### 発生時点：第2巡（入力文書SHA256 `2d34c74e9fb4290dd7e174274ca49377653031fe8bf5afe191a84ff32920ea2e`）

以下は当時の失敗・訂正の保持である。内部の旧版名・絶対パスは当時の観測を表す。

#### 6. この巡の途中で修正したこと

**初案：非平滑格子を共通の基準にする。** 正の質量を直接保持でき、帯域を増やさない点が魅力だった。しかし少数点からの未観測セルが較正でゼロ密度の同順位となり、95%域が全平面になった。したがって有限Qの記述・索引用途は残すが、連続分布を囲む標準法からは下げた。

**最初の探索：較正経験分位点を `ceil(np)` として比較した。** 名目被覆の順位保証を述べる場合は `(n+1)` が必要なので、最終試験は `ceil((n+1)p)` へ修正した。探索結果と最終結果を混在させず、本文の名目順位は最終の123/128で統一した。

**コード内の不整合：oracle表でゼロ密度格子を有限な表示矩形にしていた。** 主指標では全平面と扱えていたが、既知Q参照表には同じ分岐がなかった。これを発見して、全平面・有限面積なしへ修正し、新しい出力ディレクトリで再実行した。修正前の2880 km²という表示矩形面積は本文・配布最終表に採用していない。全平面を有限の95%域に見せないという今回の主張自身に対する反例だった。

**検査名の修正：水準の順序だけではマスクの包含検査にならない。** 最終版は実しきい値の順序を検査し、別コードで実際の50/90/95%マスクを比較した。

**自案への追加反例：固定hは希少な狭い塊を平滑化して消す。** 同じQの含有率に較正しても、形の最適性は戻らない。固定KDEを普遍的な優勝方式とはせず、帯域の標準値・自動選択は未決として残した。

この巡で上記の局所コード誤りはあったが、入力原本やプロジェクトの式を修正したわけではない。失敗を隠すために指標・検査の定義を弱めていない。

#### 7. 表示・配布物の確認

`make_figures.py` を `python_user_visible.exec` から別プロセスで実行し、3点のPNGを新しい作成先へ出力した。原データは読み取りのみで、新しい図を配布用ディレクトリへ複写した。権限変更はしていない。

3図は実際に開き、軸、凡例、線種、例示領域、注記を確認した。図1は同じQ含有率に揃えた形の比較、図2は一つのスコアの50/90/95%入れ子、図3は行分割による帯域の変化を示す。図の英文ラベルは単位と合成条件を明示するためのもので、実UIの言語方針を変更するものではない。

本文はMarkdownであり、数式はLaTeX記法、図は相対パスで参照する。特定Markdownビューアの数式組版・印刷・Web UIの全操作は検証していない。配布ZIPには元のPDF・Excel・認証情報・フォントファイルを含めない。

再生成では、主試験37ファイル、細分化3ファイル、図3点、真の密度oracle1ファイルの**計44ファイルがバイト一致**した。再生成側の別計算検査も147/147項目成功した。元のプロジェクト21ファイルとその他の入力6件は、終了時にも全て同じSHA-256だった。結果は `evidence/delivery_checks.json`。主試験の内部manifest、配布物のmanifest、元資料の指紋は異なる責務の記録である。

再生成を複数コマンドでまとめた最初の `container.exec` は、短い `timeout=1000` の指定により `Command failed because it timed out.` で終了した。主試験の出力は完了していたため指紋で確認し、細分化の未完了先とプロセスの有無を調べた。同じ出力先への上書きや全処理の盲目的再実行はせず、細分化のみ新規出力先・`timeout=45000`で一度再実行して成功し、後続を実行した。ツール名・渡したコマンド全文・返却エラー全文・処置は `evidence/reproduction_timeout.json` に保存した。制限や権限を変更して回避したものではない。


### 発生時点：第3巡（入力文書SHA256 `63f0fffbe896e0e6692ac6afed215b9880566ad7473de87633efb68f651d97c7`）

以下は当時の失敗・訂正の保持である。内部の旧版名・絶対パスは当時の観測を表す。

#### 8. 実行環境の失敗

#### artifact_toolによる原Excelの読込

使用ツール：`python.exec`。渡したコード：

```python
from pathlib import Path
from artifact_tool import Blob, SpreadsheetFile
P = Path("/mnt/data/Q420_R3_20260928_g2z2ck_w")
records_wb = SpreadsheetFile.import_xlsx(Blob.load("/mnt/data/データ.xlsx"))
print(records_wb.inspect({"kind": "sheet", "include": "id,name"}).ndjson)
```

返された例外メッセージ：

```text
TimeoutError: Timed out waiting for artifact tool daemon socket. Set ARTIFACT_TOOL_RPC_DAEMON_STARTUP_TIMEOUT_S=<seconds> to increase the limit.
```

スタックは `SpreadsheetFile.import_xlsx` → `RemoteClassAttr.__call__` → `RemoteClass.call_static` → `_ensure_client` → `get_or_create_client` → `start_daemon` の起動待ちで止まった。元のスタック全文ファイルを別途保存できていないので、ここで行番号や残りを創作しない。

この呼出しでExcelのインポート・inspectが成功したとは扱わない。設定変更・デーモン再起動・同じ経路の反復再試行はしていない。必要なのは原値と式の読取だったため、その後はPython標準ライブラリのzipfile/XMLを使う**読取りだけ**へ切り替えた。Excel再計算、代替表計算ソフト、原本編集、作成した修正版ブックの配布は行っていない。失敗を「資料のZIPが壊れている」とは解釈しない。

数値核・独立検算・研究用保存試験・図の生成は、それとは別の実行経路で成功した。原Excelのレンダリング・Microsoft Excelでの再計算は未確認のまま残す。

#### 8.2 図再生成の証跡JSONを保存する際の権限エラー

`python_user_visible.exec` で配布スクリプトから図を再生成し、図の一致表示に続いて `delivery / "evidence/figure_reproduction.json"` を新規作成しようとしたところ、保存段階で失敗した。同呼出し全体が成功したとは扱わなかった。

渡したコード：

```python
from pathlib import Path
import hashlib
import json
import subprocess
import sys

delivery = Path("/mnt/data/Q420_R3_20260928_delivery")
regenerated = Path("/mnt/data/Q420_R3_20260928_figures_reproduced")

subprocess.run(
    [
        sys.executable, "-B", str(delivery / "make_figures.py"),
        "--data", str(delivery / "data/synthetic"),
        "--out", str(regenerated),
    ],
    check=True,
    capture_output=True,
    text=True,
    timeout=45,
)

checks = []
for original in sorted((delivery / "figures").glob("*.png")):
    repeated = regenerated / original.name
    matches = original.read_bytes() == repeated.read_bytes()
    assert matches, original.name
    checks.append({
        "file": original.name,
        "byte_identical": matches,
        "sha256": hashlib.sha256(original.read_bytes()).hexdigest(),
    })
    print(f"{original.name}: 再生成した図とのバイト一致 = {matches}")

with (delivery / "evidence/figure_reproduction.json").open(
    "x", encoding="utf-8"
) as f:
    json.dump({"count": len(checks), "checks": checks}, f, indent=2)
    f.write("\n")
```

返却されたスタック：

```text
PermissionError                           Traceback (most recent call last)
Cell In[3], line 34
     30         "sha256": hashlib.sha256(original.read_bytes()).hexdigest(),
     31     })
     32     print(f"{original.name}: 再生成した図とのバイト一致 = {matches}")
     33
---> 34 with (delivery / "evidence/figure_reproduction.json").open(
     35     "x", encoding="utf-8"
     36 ) as f:
     37     json.dump({"count": len(checks), "checks": checks}, f, indent=2)
     38     f.write("\n")

File /usr/lib/python3.13/pathlib/_local.py:539, in Path.open(self, mode, buffering, encoding, errors, newline)
    537 if "b" not in mode:
    538     encoding = io.text_encoding(encoding)
--> 539 return io.open(self, mode, buffering, encoding, errors, newline)

PermissionError: [Errno 13] Permission denied: '/mnt/data/Q420_R3_20260928_delivery/evidence/figure_reproduction.json'
```

既存ファイル・ディレクトリの権限は変更しなかった。同じ失敗経路を反復せず、研究用配布物を作成したcontainer側で、配布図と再生成図それぞれの正確なパスの存在を改めて確認し、バイトを再読して一致を検査したうえで、新しい証跡JSONを作成した。`figure_reproduction.json` にこの証拠の再確立を記録している。失敗した呼出しの途中の副作用を、確認せず成功と推測したわけではない。


### 発生時点：第4巡（入力文書SHA256 `facbdc12b008faaabfbd5b4d4a1cc10706c6ea2e8cc3de35fc44cf1bddc11cdf`）

以下は当時の失敗・訂正の保持である。内部の旧版名・絶対パスは当時の観測を表す。

#### 7. 実行中の失敗と対処

研究の前提であるR3資料・Driveアクセスの失敗はなかった。一方、ローカルの参照方法と読取スクリプトには次の失敗があった。元資料の破損、Python全体の不能、権限の不足とは解釈しない。

**R3の証跡を、2 Markdownだけが置かれたディレクトリから探した。** `container.exec`で`/mnt/data/Q420_R3_20260928_delivery/evidence/source_audit.json`を読む試みは、`FileNotFoundError: [Errno 2] No such file or directory: '/mnt/data/Q420_R3_20260928_delivery/evidence/source_audit.json'`となった。R3一式ZIPの実在を確認し、その中の実体を新しいscratchへ展開して解決した。存在しないファイルを記憶で再作成したのではない。この失敗時のコマンド全文／スタック全文を別ファイルとして保持していないため、ここで創作しない。

**本文読取のPython一行に括弧の誤りがあった。** `for i in range(572,min(641,len(p)))):print(f'{i+1}: {p[i]}')`という行は、`SyntaxError: unmatched ')'`（標準入力の5行目）で終了した。コードは実行開始前に構文で止まった。括弧を一つ除いた`range(572,min(641,len(p)))`へ一度修正して読取に成功した。元資料の変更はなく、数値計算の失敗でもない。

**再生成の最初のバイト比較で1ファイルが一致しなかった。** `container.exec`内の全件一致assertionが`AssertionError`で停止した。比較を分けて読むと、`data/focused10/metrics.json`の8か所の`max_step_s`だけが`10`と`10.0`という表記差で、JSON数値としての値も軌道ファイルも一致していた。原因は`argparse`の既定値を整数10とし、明示引数をfloatで解釈していたことだった。

初回要約を`evidence/initial_focused10_metrics.json`へ保持し、前後指紋と差を`reproduction_initial_difference.json`へ記録した。研究スクリプト`focused_checks.py`の既定値を10.0へ統一し、明示引数で再生成した要約をR4候補へ受け入れた。さらに新規出力先で既定値経路を一度実行し、明示引数経路と9ファイル一致を確認した。プロジェクト本体ソース、機体値、気象値、軌道数値、assertionの意味は変更していない。R4作成中の表記修正であり、R3や原資料の上書きではない。

上の失敗に対して、権限・ACL・セキュリティ設定・環境パッケージは変更していない。R3の過去のartifact_tool起動失敗や図証跡保存のPermissionErrorは、R3ログに属するもので、今回また発生したとは記録しない。


### 発生時点：第5巡（入力文書SHA256 `b119d1cada7414ef309bfa9d4e59899cd605b94d40eadaa8dbff768490cbf317`）

以下は当時の失敗・訂正の保持である。内部の旧版名・絶対パスは当時の観測を表す。

#### 8. 実行環境と取得の失敗・制約

#### 8.1 container.execのClientError

最初に既存ファイルの所在を確認するため、`container.exec` に以下を渡した。

```json
{
  "cmd": [
    "bash",
    "-lc",
    "ls -ld /mnt/data/Q420_R4*; ls -l /mnt/data/Q420_R4_20260928/Q420_R4*; python - <<'PY'\nfrom pathlib import Path\nfor p in [Path('/mnt/data/Q420_R4_20260928/Q420_R4_RESEARCH.md'),Path('/mnt/data/Q420_R4_20260928/Q420_R4_CRITIQUE_AND_READING_LOG.md')]:\n print(p, p.exists(), p.stat().st_size if p.exists() else None)\n if p.exists(): print(p.read_text()[:1400])\nPY"
  ],
  "timeout": 20000
}
```

ツールから返されたエラー全文は次のとおり。

```text
ClientError
Encountered exception: <class 'caas.internal.errors.ClientError'>.
```

この呼出しがファイル一覧を取得したとは扱わず、同じ経路を反復再試行しなかった。Pythonで `print("R5_PYTHON_PROBE",1+1)` を別に実行し、`R5_PYTHON_PROBE 2`を得た後、正確なパスの存在、本文、ZIPの一覧・CRCを独立に読み直した。権限変更・承認無効化・秘密の取得はしていない。ClientErrorの内部原因は未特定で、ZIP破損やユーザー側設定が原因とは断定しない。開始時にユーザーへ報告した。

#### 8.2 FilesのPDF画像が得られなかった範囲

Filesのページ読取は、風PDF15–17/76–77で画像なし、フィードバック4ページで画像なしと返した。本文抽出の成功と図表の視認は別にした。実体は `/mnt/data` に存在したため、PyMuPDFで風p16/17/76およびフィードバックp4を画像化して実際に表示した。フィードバックp3はFilesの画像を読んだ。OCRは使っていない。風のp15/77は本文読取で、全図の視認済みとはしない。

#### 8.3 SciPyの版固定Webページ

`https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.integrate.RK45.html` のWeb openはInternal Errorを返した。同じ失敗URLを反復せず、取得できた公式の現行ページを使い、ページ表示版1.18.0と実行環境1.17.0を区別した。失敗をライブラリ非互換・廃止の証拠にはしない。参照内容はRK45の一般的な方法説明だけである。

#### 8.4 Python子プロセス起動時のSpreadsheet warmup警告

数値検算や図生成の子プロセスはreturncode=0で成果物を返したが、stderrに次の起動警告が出た。研究スクリプトはartifact_toolをimportせず、Excelの読取やwarmupを要求していない。起動フックがどの状態に依存してこの警告になったかまでは診断していない。

```text
Spreadsheet runtime warmup failed during python startup
Traceback (most recent call last):
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/patches/warm_spreadsheet_runtime_on_startup.py", line 26, in warm_spreadsheet_runtime_on_startup
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/spreadsheet_warmup.py", line 785, in warm_spreadsheet_runtime
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/spreadsheet_warmup.py", line 720, in _warm_feature_flows
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/spreadsheet_warmup.py", line 704, in _warm_collaboration_flows
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/generated/interface/models.py", line 32317, in hydrate_crdt_from_proto
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/rpc/remote.py", line 749, in __call__
  File "/tmp/tmp.L2TH2Y5coc/artifact_tool_v2-2.8.22/artifact_tool/rpc/client.py", line 150, in call
artifact_tool.rpc.client.RemoteError: hydrateCrdtFromProto requires an empty collaborative document.
```

警告なしの成功と書かず、stdout/stderrとreturncodeを `evidence` に残した。数値成果物の存在・内容・別プロセス再生成の一致は、それぞれ別に確認した。自動warmupを修復・再試行する操作はしていない。研究再現のための子プロセス起動と、Spreadsheet障害を直すための反復再試行は別である。

