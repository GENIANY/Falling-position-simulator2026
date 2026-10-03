---
document_id: BJP-REFERENCE-LOG
revision: 0.59.0
as_of: 2026-10-02
role: 今回の根拠・実読範囲と次の開始位置
---
# 現在の参照・引継ぎ記録

[更新:0.59.0] [確認:0.59.0] — REFS / REV-590-CONTENT-REFS

## 現在の参照先：0.59文書監査（実装・稼働は0.58）

対象は固定0.58記録C2 `95f09d2fc0ae076def05eb76df996b9f2c3b0ef4` / tree `2f07e4dc21ea87614ac632e781953480af4c0931`（全365実体）。`P590` は `C:/Users/genia/AppData/Local/Temp/balloon-document-audit590`。`recovery590.json` の固定指紋から選定本文を取得し、入口・資料の役割・現在と履歴・研究発行の境界を読んだ。今回の操作・適用状態・次の判断は[指示書start](BOOTSTRAP_RUNBOOK.html#start)と[S36の文書監査](BOOTSTRAP_RUNBOOK.html#s36-document-audit-plan590)が持つ。

独立読解は `P590/navigation-audit590.md`。README/AGENTS、MAP/参照、start/S36、規範/依頼様式と3管理JSONの役割、研究入口/束の版、参考レビューの来歴・採否境界を選び、21入力の固定SHA一致を確認した。旧進捗の現在形、S36の古い着地点、用途別逆引きと研究コピー文の版指定を修正候補とした。原PDF/Excel/研究原本の全科学再審査、実装・実画面・稼働・GitHubの再検証ではない。文書候補の適用・生成・検査の完了はこの読解から先取りしない。

### ACT-590：担当する問い・現在案内・実装への対応を有限に読む

`planning-audit590.md` はCONTEXT/PLAN/VISION/INTEGRATION、採否/残件/未決、ENV/WEATHER/LESSONSの役割と選定本文を読む。旧PLANの現在表、CONTEXT第4節、VISIONの現在導線、JRA接続を未了とするENV/課題行を照合した。CONTEXT第1節の縮約は `context-retention-map.md` と `requirements-preservation.json` でRPT-038/072/073の受領原文と既存S36/Dへの対応を確認する。古い版数だけを理由に全面改訂していない。

`guide-audit590.md` は構造/理論/操作/契約/生成の分担と選択した実装を照合した。構造索引の245入力指紋を確認し、weather図のexportと関心handoffの担当・monthlyProfilesの所在、理論の後述節案内、取得実績の時点、backendの現行案内を訂正対象とした。全科学式・全API・全外部仕様を新たに認定したものではない。

主担当の採否は `root-review590/root-dispositions.json`、管理補助の独立批評は `metadata-helper-review590.json`。固定比較元配下へ外側出力を作り得る反例を実行前に検出し、出力先の拒否条件を追加した。これはrepoの規範/checker変更ではない。選定原票・前後差分・生成/表示票の可搬入口は[0.59文書監査証拠束](references/development_evidence/document_role_audit_0590_evidence.zip)の `README.md` / `MANIFEST.json`。管理検査・Git保存の後続原票はP590とS36/VERSION_HISTORYへ分け、ZIPに未収録の後続完了を含めて読まない。

PLAN生成は `plan-build590/evidence/visual-build-receipt.json`、構造/理論は `pdf-build590/review02-receipt.json` に最終source/生成hashと視認範囲を持つ。31＋32＋27頁の配置、変更頁の実読を区別した。構造/理論のbuild01→02は確認印の同期で、PROGRAM全32頁とTHEORY本文26頁のRGB/textは一致、理論表紙の確認数字だけを再視認した。PLANの通常sandbox失敗と権限付き同一手順の再生成を混ぜず、既存Pandoc非推奨1件を残す。

内容C1の入口・役割表・S36は `P590/final-closure-critique590.md`（SHA256 `a57fcbca504051ac3ce34521d78a631289ed739f9a172554b253789c44123be6`）でも再批評し、新たな阻害点はなかった。対象4文書の指紋、h4訂正/一意IDと検査器不変を照合した範囲に限り、後続C2記録やPDF再視認の受入へ広げない。この票は凍結ZIPの後の外側記録である。

### ACT-590の閉鎖範囲

内容C1 `3c0b0a213a1a2288fec51b1b1987df92874f1167` / tree `297a30529ba22ab784a1085d4bd312a71af1921b` の全366実体を固定読戻しした。原票は `P590/content-c1/checks02/receipt.json`（管理6検査、全実体不変）、`save-receipt.json`（同private branch、main不変、元Git操作前後の限定一致）。初回見出し検査とGit起動の失敗票も保持する。本文の採否/保持対応とPDF表示、管理整合、Git保存は別の証拠として読む。

指示書HTMLのfile URLをブラウザで開く試みはURL制限で拒否され、回避していない。HTML描画は今回未確認で、静的構造/リンク検査と3冊PDFの90頁視認を混同しない。記録C2の保存は本稿編集時点で未了であり、[S36](BOOTSTRAP_RUNBOOK.html#s36-document-save590)と最終PR/外側受領票へ戻る。

以下は各版の参照記録である。「現在・次・未了」はその編集時点に属する。保存遷移は[VERSION_HISTORY](docs/VERSION_HISTORY.json)、実施の順序と後続の判断は各S36節へ戻る。

## 0.58時点の参照先：S36 / D-199（年間48区分と気圧面探索）

### ACT-580：元時刻の支持と、初回/反復の費用を分ける

参照の入口は[0.58証拠束](references/development_evidence/climate_interaction_0580_evidence.zip)。展開後の `README.md` が数値/費用/互換性/隔離UI/資料の有限範囲を示し、`SELECTION.json` から元票、`MANIFEST.json` からmember指紋へ辿れる。64 memberの固定束は編集時点のstaging表記と未了を保持し、常設反映・管理閉鎖・Git保存の後続票まで収録したものではない。後続実績は[S36の0.58保存記録](BOOTSTRAP_RUNBOOK.html#s36-climate-save580)と版履歴、PC内原票は下記P580へ戻る。`HASH_ONLY.json` の省略実体はhashから復元できず、全原配列・私的state・SQLite・秘密はこのZIPに含めない。

基準は0.57記録C2 `b1b66dbff8b84bb6bb0332ec98043cc8990071b3` / tree `8121dcdb0f8e1be23fd1209c9771b2b0e76314ea`（全363実体）。`P570/record-c2/save-receipt.json`で内容C1 e766b58を親とする保存・読戻しを確認した。旧0.57本文のC2未保存は当時の時点として保持する。main M550 `06936856ee0deab2fe0b3f3b04220d60652ffba6` と同private Draft PR31の分担を維持する。P580は `C:/Users/genia/AppData/Local/Temp/balloon-climate-interaction580`。

再提供tar内のDBと現runtime DBの同一SHA256は `1af26d91500252c285f89e2cc50eb32fd325f6df9905ad0c5162282791d5137a`。独立担当はtar memberをstream hash照合したうえで既存DBをread_onlyで確認した。実table18/view10・24半月、原有効日時のu/v表なしを確認し、fit/分位/共分散/時刻別平均から半月内の日付所属を復元できないと判断した。原票は `metadata-candidate580/ten-year-archive-inspection580.json/md`。再提供された資料に新しい原日時支持が増えたとは扱わない。

`backend-comparison580.json`はERA5 2024全域・UTC00・37面の年間48区分1,776行を別計算と比較し、記録した指標の最大差0を確認した。同じ票の300/250/200 hPa比較では既存数値/母集団fieldのfloat bit一致を確認したが、新annual_quarters・descriptor/来歴・query.source_idは対照から区別している。`backend-compatibility580.json`は旧artifactの通信なしGET、受理済みID再試行、新sourceの別artifactを隔離保存先で確認した。全条件や実ブラウザの成功ではない。

ERA5 2024全1,188格子・37面・UTC00の同PC逐次観測では、母集団cache未生成の初回が旧7.048秒→新13.240秒、同じ母集団の面変更8回の中央値が旧5.244秒→新0.806秒だった。初回は遅くなっており、一律高速化とはしない。これはoffline adapterのwall-clockで、HTTP・描画時間や全端末SLAではなく、OSのfile cacheを厳密にcoldへ制御した比較でもない。

4資料の差分/既存C2一致/保持した定義と限界は `docs580-impact.md/json`。PROGRAM/THEORYを生成し変更頁を視認、INDEX245入力と公開34項目の保持を照合した。隔離UIで原2資料48区分・JRA固定保存の再訪・十年24区分と48非対応、広幅/狭幅の操作枠を確認した。原票は `pdf-doc-review580.json`、`ui-review580.json`、`index02/publication.json`。常設8551への反映と保存内容の照合、管理6検査を終え、内容C1 `cbe211eaee15076fd271ce35d4e407e864a31eab` / tree `c83fc010d45eafdf8202257fc9fdf71bbde13368` を同private PR31へ保存し全365実体を固定読戻しした。実績を記すC2は本文編集時点では未保存で、最終自己SHAはPR本文/外側受領票へ置く。数値・性能・操作・管理・Gitの証拠を一つの成功へ束ねず、後続実績はS36へ戻す。

常設反映は845保存GET/2,841固定実体/3DBの照合で閉じ、UI後も共通projectは未変更。内容C1の48差分と全365読戻し、管理6検査は <code>P580/content-c1/</code>、次のC2は実績8pathに限定する。原票は <code>P580/live-ui-review580.json</code>。自己SHAと統合は先取りしない。

## 0.57時点の参照先：S36 / D-198（原標本の分布と分析機能）

### ACT-570：取得UIの延期と分析図の修正を混同しない

直前はprivate PR31の0.56記録C2 `98b6dad115e4ac30c03f06ff3366fc6468022b8a` / tree `a6f0002550a9538a141c03ccf4b12f01271a4042`、全347。保存票の成功・親・全実体hashを確認した。採用main M550 `06936856ee0deab2fe0b3f3b04220d60652ffba6` と候補を分け、元local.gitを切り替えない。原票は `P570=C:/Users/genia/AppData/Local/Temp/balloon-climate-quantiles570`。先のC2未保存という本文は当時の編集時点の記録である。

今回の直接訂正はRPT-076。主担当が「仕上げなくてよい」の対象を分析図まで広げた誤読を訂正し、公開元からの取得UIだけを後続にした。中央値・月p10/p90、月/半月/季節、UTC選択、気圧面自動更新と固定図保存の目的を維持する。2024年の原標本を独立sourceとして扱い、旧10年期間集計へ未取得の原標本が加わったと説明しない。

JRA/ERAの公開元catalog、DAP2 DDS/DASと原応答、u/v単位・UTC・native格子/圧力の契約を取得担当が読み、主担当と別担当が配列/数値/保存の接点を照合した。JRAのGaussian面積重みとERAの緯度帯面積、等UTCの経験逆CDF、静穏を含む一点風配、参考ISA高度をTHEORY/WEATHERへ分担する。公式出典は [NCAR JRA-3Q](https://gdex.ucar.edu/datasets/d640000/) と [NCAR ERA5](https://gdex.ucar.edu/datasets/d633000/)（2026-10-02確認）、計算法は [NumPy quantile](https://numpy.org/doc/stable/reference/generated/numpy.quantile.html)。実行版NumPy2.4.4とmetadataでの固定を、常に同じlatest仕様という意味に広げない。

独立批評から未知資料IDのfallback、設定済み不良資料のエラー隠れ、NumPy版とcache同一性、ERA帰属の受渡し、デモの固定地域名、旧DBに偏ったコマンド表を修正した。8570新状態の初回集計では、要求の全域nullと返却の明示全域を画面が誤判定する失敗を観測し、実API形状とmockの差を独立に切り分けた。数値試験が通ることを一巡の実UI成功へ読み替えない。詳細な行動・失敗・修復後の判定はS36に置く。

PROGRAM/THEORYは構造/式の更新・TeX生成とPDF視認、NOTESは保存契約、COMMANDSは操作、INDEXは実sourceと責務を担う。今回の有限読取・依存点検・実UI・取得状態を最終票で固定してから確認印と管理検査を閉じる。両商品2024年全12月の取得・原値照合・常設保存、両商品4格子デモの生成再読、8570/8551の実操作と既存保存物保全を有限確認した。全文献再監査、科学的妥当性、今回Git保存はこの本文編集時点では主張しない。

内容C1 `e766b58d053e2410144d0da1ad275b8052fb149e` / tree `f53b5ded242338b28da70499f96b10b0dcdb00fb`（親 `98b6dad115e4ac30c03f06ff3366fc6468022b8a`）を同private branch / Draft PR31へ保存し全363実体を固定読戻しした。管理6検査は全成功（state 2951、health 7470、fixed-health 7470、contract 8328、fixed-contract 8328、research 7生成物一致）、検査中363実体は不変。元local.gitは今回C1操作前後の1721ファイル一致。証拠束は168 member / 2,541,008 bytes / SHA256 `37a843b3b4482c06fda735a1205e8243b969ccdf3bfdc58cb9ed7da094dcc610`、全member読戻し済み。管理/Gitの後続票は固定ZIP外の `P570/content-c1/`。科学精度・多年代表性とmain統合は未採用。この実績のC2は本文編集時点では未保存で自己SHAを外側票/PR本文へ置く。

## 前段の参照先：S36 / D-197（0.56 季節・月・時刻の実気象分析）

### ACT-560：資料にある分析能力と、現在APIの不足を分ける

比較元はprivate PR31の保存済み記録C2 `cbc197276d14c5753cc112643e449abaeb3bb29f` / tree `1c85bfd90cc38c0dee15d558f85b0237e31eeb46`、全339実体。前回 `P550/detail-lease-repair550/record-c2/save-receipt.json` の成功・親 `57d2680faa07a360c56efe7fe98544e16e03ecc3`・339読戻しを実読し、主担当が `P550/climate-expansion550/basis.json` で開始作業実体との一致とmain M550を固定した。下記の0.55記録にあるC2未保存は当該本文編集時の状態であり、今回の比較元は保存済みである。今回の原票・比較・数値検査・画面観察は `P550/climate-expansion550/` へ集める。

利用者の目的は季節の分布と月区切り・時間帯の選択による比較である。データ担当から原tarのdiurnal、代表1格子のwind_rose、共分散/経験分位の存在報告を受けているが、この入口編集時点では実DBとの対応・支持範囲の独立照合は進行中。現APIが半月meanだけであることを原資料全体の限界として説明した接続不足を是正する。具体的な数値・行数・成功件数は確認後の原票に結び、まだ記さない。

管理担当はREADME R0〜R5、DC-JUDGMENT/CHANGE/CLOSE、DC-TIME/INDEX/STABILITY、現在入口/S36、比較元の保存票とVERSIONの接点を有限に読んだ。DC-INDEXの「配布済みの基準版から意味ある変更」に従い、新しい分析能力と選択/保存契約へ進む0.56候補を採用。従来の0.55修復記録は保持し、更新印と未完の確認を分ける。PROGRAM/THEORY/INDEX、操作/契約本文、HEALTHと最終検査は実装契約の確定後に照合する。原資料の存在を新科学モデル・多年代表性・精度の受入へ広げない。

backend契約の追認では、`contracts/periods/aggregation/extensions/source`とserviceの保存境界、FEのClimateView/ClimateFlightHandoffと表示controllerの追加接点を読んだ。提供資料の独立票は `independent-climate-data-review.md` / `climate-data-review-evidence.json`。原tar 97 memberと既存DBのhash、diurnal/風配の支持、n=14,612と原説明14,610の差を担当票から区別する。今回新たな外部取得や原PDF全頁の再視認を行ったとはしない。

`summary-full.json` / `summary-hours.json`は `independent-backend-sql-result.json` の入力hashと一致し、保存応答を別SQLで比較したfailure 0を読んだ。これは全域・指定1面（level_id 18）と全時刻/00・18UTC subsetの半月/月/季節結果の対照であり、全query/UIの再検証ではない。`independent-backend-boundary-result.json` のsource snapshot afterは現8 moduleと一致した。応答例のsource_codeとはextensions.pyが異なるため、異なる時点の票を同一最終sourceの一度の検査にまとめない。4資料の契約差分は `contracts560-diff.txt`、確認印/HEALTHと最終閉鎖はFE確定後に照合する。

最終backendの追加票は `final-numerics/binding.json` と `independent-backend-sql-result.json`。管理担当は現8 moduleおよび2応答hashが票と一致することを確認し、6組のfailure 0を読んだ。先票の差替えではない。backend26件とHTTP/application25件、frontend round04の通常307成功/2 opt-in省略と同2件の別実行成功を区別する。後続round05は別の検証を要し、先の全体結果をそのまま最終sourceへ付け替えない。

主担当の `ui-review.md`、`live-update.json`、`project-preservation.json` を実読した。同state再起動前後の応答byte/instance一致と、その後の意図したproject20→21の保存を分けた。候補/入力/結果参照は保持し、forecastのrouteDisplay既定値の明示保存はweather操作に伴う保存差分として記録する。詳細な再起動計画のS36本文への転記は実施後であり、操作前本文保存を捏造しない。dist03の実SVG読戻しと、dist04で新ファイルを確認できなかった事象は別観測として保持し、原因をブラウザ制約と断定しない。後続では利用者実マウスの保存返答と、主担当の実ファイル読戻し（export-final-receipt.json、641,772 bytes、XML/metadata/12月見出し各1回）を受領した。ツール単独はtimeout/未受領のままであり、原因特定や全ブラウザ保証へ広げない。round06は生成リンクに固定の生成時条件を表示する。round05全体311成功とround06対象42成功は別版の記録で、続く面自動更新は最終票を待つ。

ガイド出版票 `guide-review/published.json` の4出力hashを照合。PROGRAM31頁/THEORY26頁・警告0、視認は担当の変更7頁と主担当の修正後p7に限定する。INDEXはindex03まで233 source/API34/HTTP40とPython抽出100 bytes不変の担当票であり、後続修復後の現hash確認は最終票へ戻す。独立source批評は `final-independent-review.md/json` の22pathと数値/支持/保存接点の有限読解で、全科学/全ブラウザ監査ではない。

主担当の `ui-purpose-review.md` と独立の `analysis-question-review.md` を読んだ。人工の全9格子×選択時刻poolの中央値/月帯と、実Gaussian平均線の問いが異なる点を受け、平均は補助、元分位図は未接続へ訂正する。旧技術票の正当な数値/保存範囲を保持し、目的達成の証拠へ広げない。次の原cache/必要標本から同じ図へ進む採否はD-197/WEATHER、操作はCOMMANDS/NOTESへ分担した。

最終round08の主担当票 `pressure-ui-final.json` と `ui-review.md` の追記を読んだ。新規2面のPOST4→6、350/300再訪cache、未適用の無効地域/UTC草案保持、地域図/風配同期、保存300 hPaのGET再訪を有限に確認した観測である。frontend全体319件はround07であり、最終round08は対象52件・型/build成功を別票として扱う。最終出版票のTeX/PDF/txt全6実体hashとindex07（233 source/API34/HTTP40）を照合した。証拠束 `references/development_evidence/climate_expansion_0560_evidence.zip` は77 member / 3,127,883 bytes、SHA256 `6b48a51b71a0a43f0ae3085552369e2f9cba9469707e00fb0d386fcb91f78494`。管理担当がCRC、manifest内76 memberと外側原票、現143 sourceを全照合した。元中央値/月幅の未接続、原DB精度/季節飛行/全ブラウザ未受入は保持する。管理6検査と内容C1のGit保存は、この本文の編集時点では未実施である。

内容C1 `b6744d06c8f7ba8ed94e9990f92a6bbe3793156a` / tree `668fd0d8cd8ed0f93f589677f77aa8c6b4f59d57`（親 `cbc197276d14c5753cc112643e449abaeb3bb29f`）を同private branch / Draft PR31へ保存し、全347実体を固定読戻しした。管理6検査はすべて成功（state 2883、health 7251、fixed-health 7251、contract 7715、fixed-contract 7715、research 7生成物一致）、検査中347実体は不変。元local.gitは今回C1操作前後の1633ファイル一致に限定し、長期不変は主張しない。根拠は `P550/climate-expansion550/content-c1/save-receipt.json` / `checks01/receipt.json`。管理同期の初回はPROJECT_CONTEXTへの直接書込みでOSError22となった。部分変更2pathを外側へ保全し、承認前347実体へ復旧した後、同じ承認票を隔離コピーで再実行して24許可pathだけ原子反映、最終347hash一致を確認した。原因は断定せず、検査器の失敗や自動承認拒否とは扱わない。根拠は metadata-write-recovery.json。Git保存の最初のsandbox実行はls-remote前段のMSYS signal pipe作成がWin32 error 5で停止し、commit/push前だった。同じ固定候補・保存helperを権限付きで再実行し、認証経路や保存先を変更していない。初回6検査はHTML末尾の旧0.55表記と、検査呼出し側がhealthの変更前比較に旧basis540を指定した誤りでstate/healthが失敗した。元票/候補をcontent-c1-attempt01へ保全し、末尾0.56とRUNBOOK指紋だけを訂正した。healthは既存BUILDの定義どおり直前cbc197完全候補へ、contractは宣言したbasis540へ分け、checker/要件を変えず再検査した。source/PDF/INDEX/証拠ZIPと有限受入の境界を変えず、この実績の記録C2へ進める。C2はこの本文の編集時点では未保存で、自己SHAはPR31本文/外側票へ。main M550と人間による統合の分担は不変。ZIP固定後のlive tab19の明示writer取得はS36の主担当追加観察へ分け、新規集計や保存の実績とはしない。

## 前段の参照先：S36 / D-196（0.55 詳細閲覧と送信担当切替の修復）

### ACT-550-DETAIL-LEASE：固定結果の詳細と明示的な送信担当切替

比較元は保存済みPR31 C2 `ee051f506a94e2178c697b97684eba700da1769a` / tree `e03a9ccac43264960caa8487d91baff192788302`（全335）。前回保存票は `P550/route3d-implementation550/record-c2/save-receipt.json`。main M550と候補を分け、元local.gitを切り替えない。今回証拠先は `P550/detail-lease-repair550/`。

主担当が現8551の取得クリックで表示が変わらないこと、候補2の16/16という表示に対し原履歴0・空グラフであることを再現した。前回の検査用タブが送信担当を保持していたことも一因で、保存計画の候補9と、既存3D接続を持つ現タブの未保存候補13を区別した。復旧のために保存9を現13へ無言で読み込まない。これらは主担当の現タブ観測であり、修正後の成功ではない。

管理担当はREADME R0〜R5、DC-JUDGMENT/CHANGE/CLOSE、S36末尾、既存COMMANDS/NOTESの送信担当と固定結果読取、PROGRAMの責務箱、writeLeaseとprepare済みscope依存を有限読解した。起動時の空き権取得と明示協調引継ぎ、API受付＋台帳更新までのbusy、保存case分析と原履歴GET/部分群集計を分ける契約をD-196へ戻す。未確認の数値や実UIの成功を埋めず、source最終化後に担当実装/反例/実画面と照合して指紋を同期する。科学式・原気象・原結果・前回3D証拠を再受入しない。

主担当の最終実UI記録は `ui-review.md`、4応答の保全は `runtime-preservation.json`。新14はサーバー保存計画から開始し、readerで全16履歴・平均帯/風/時刻、部分2標本の保留理由と原履歴を確認。旧9の8秒無応答後は保存済み旧9だけを閉じ、14で再クリックして取得し、未送信だった部分群の集計へ進んだ。同版14/15の協調引継ぎは両方向成功し、選択/時刻を保持。報告対象候補2も16履歴・高度図・衛星地図・15.15分の連動を確認した。旧13は未reloadで未保存草案/接続iframeを保持し、その草案を新14へ移していない。隠れたiframeの受領票照会はtimeoutのため、現Google描画/新root接続を受入しない。管理担当は原票を読み、busy完了後に再クリックする実装へ操作説明を精密化した。

最終source 96ファイルを `frontend-final.json` と全照合し、全23 suite / 296試験成功、TypeScript exit 0、Vite build01成功を主担当の実行票へ結んだ。既存の500 kB超bundle警告は残る。guard担当の63関連件と現在10 guard件は別々の実行であり、一度の73件実行とはしない。独立最終批評の担当・有限範囲を区別し、追加の重大阻害点なしとの結論を採用した。PROGRAMは30頁・警告0、全頁概観と変更p9/p12の視認を出版担当票で確認。構造索引は226 source / frontend129、API34 / HTTP40を維持する。証拠ZIP `references/development_evidence/detail_lease_0550_evidence.zip` は315,587 bytes / 40 members、SHA256 `3efb3b7a2c9086212752f62fc8c3acba6ec8b4432ed04ff9e13d10698b56d280`。管理担当がCRCとmanifest内39memberの全hash、出版3実体と索引hashを読戻し照合した。管理検査と今回Git保存は次の実績票へ戻る。

内容C1 `57d2680faa07a360c56efe7fe98544e16e03ecc3` / tree `d917300b3addb274d069954d68f2152e86d85203`（親 `ee051f506a94e2178c697b97684eba700da1769a`）を同private branch / Draft PR31へ保存し、全339を固定読戻し。最終6検査はstate2849、現/固定health各7211、現/固定contract各7392、研究7一致で、検査中339不変。初回contractの既存2asset理由列挙漏れと、独立再読が検出した現行操作/契約2段落の旧集計前提は訂正し、原失敗/訂正前成功候補を保持して再検査した。source/PDF/証拠ZIPを変えず、独立docs回答受領後に固定した。根拠は `P550/detail-lease-repair550/content-c1/`。main M550不変、元local.gitは今回C1操作前後1623ファイル一致。前回1611から今回操作前への追加12はobjects配下だけで既存変更/削除0だが、追加主体/時刻は不明（`original-git-prior-comparison.json`）。長期不変とはしない。保存初回のMSYS起動失敗はls-remoteでcommit/push前に止まった事象で、自動承認拒否ではない。この実績の記録C2は、この本文の編集時点では未保存で、最終自己SHAはPR31本文と外側票に置く。

### ACT-550-ROUTE3D：KMLと3D画面の軌道表示に関する検討

2026-10-02 JST、main 06936856/PR31 head 30f61bfのまま全326作業実体を照合。scene-document.js:25–34、export390.js:10–18、controller.js:310–320、scene3d/srcのprotocol/overlays/main/catalog/camera-fit/surface-pick/overlay-store/providerを読み、立体経路はKMLのみへ発行されていることを確認した。主担当と独立批評でallObjectsの意味、深度読取り、地表接続、ASL/楕円体高、選択群と平均経路の意味を整理し、S36 s36-route3d-discussion550へ提案と受入論点を記録。新表示は未実装、8551とAPI接続は不変。

公式仕様の参照（2026-10-01 UTCに閲覧）：[Cesium WallGraphics](https://cesium.com/learn/cesiumjs/ref-doc/WallGraphics.html) の上下端とmaterial、[Scene.sampleHeight](https://cesium.com/learn/cesiumjs/ref-doc/Scene.html#sampleHeight) の現在描画範囲とundefined、[Cartesian3.fromDegrees](https://cesium.com/learn/cesiumjs/ref-doc/Cartesian3.html#fromDegrees) の楕円体高、[KML LineString](https://developers.google.com/kml/documentation/kmlreference#linestring) のextrude/altitudeMode。実装はlocal lockのCesium 1.145.0が基準で、latest公式文書の閲覧を写真meshの実物試験へ読み替えない。外側検査/保存票はP550/route3d-discussion550/。


### ACT-550-ROUTE3D-IMPLEMENTATION：原経路の表示と、部分幕案の撤回

2026-10-02、直接の追加指示を受けM550とPR31 b9d960/全326を固定した。scene-documentのallObjectsを3Dへ転用せず可視経路だけを足し、protocolで候補/結果/相/点列/高度基準を照合した。独立読取りはfrontend430（受渡し/構造索引/操作契約）、weather540_auditとrecovery530_review（EGM96/独立補間）、map_refresh_review（複数巡の反例と修復後の再批評）。主担当が全体用途・実写真・最終保存を担う。

初稿の部分カーテンについて、利用者の反論を受け表示目的の誤読を認めた。実ASLは地形照会から分離して全幕へ変更した。旧案は261試験・初回写真接続等の有限実績を持つが、それだけで用途を受け入れない。新旧のsource・途中生成物と失敗もP550/route3d-implementation550へ保持。最終案の試験・写真確認・資料・保存はS36の実装記録へ戻す。

同梱Cesium1.145.0のPolylineGeometry/WallGeometryLibrary/KmlDataSourceと、[WallGraphics](https://cesium.com/learn/cesiumjs/ref-doc/WallGraphics.html)、[KML LineString](https://developers.google.com/kml/documentation/kmlreference#linestring)を比較。線と幕の曲率補間、表示下端と地形の区別を確認した。EGM96原格子・形式・出典・利用条件はfrontend/scene3d/data/README.md、科学量との区別はTHEORYが編集元。原資料の提供命令を現行許可にしない。

永続する有限根拠は `references/development_evidence/route3d_0550_evidence.zip`。Google画像・APIキー・browser profileを含めず、検査票、独立批評の処置、非秘密のUI観測、出版票と再実行の入口を収める。Git実績追記そのものは証拠束の再帰的な自己hashへ含めない。

内容C1 `62d93e0afb5c2f6b4e91f5ef5fda3c8d409671fb`（tree `ac19fc26e85fb671a46afe5edb279ca259262e97`）を保存し全335実体を固定読戻し。全frontend270試験、TypeScript/Vite、6管理検査、PROGRAM30/THEORY25頁の出版と目視を実施した。原local.git 1611実体不変・main M550不変。検査/保存票は `P550/route3d-implementation550/content-c1/`。この保存結果と、固定DACのbinary属性明示を記録C2へ追記し、最終SHAはPR31と外側票に残す。旧属性も改行保護済みであり、原格子を変えずPRのtext diff/merge扱いを是正した。旧/新のautocrlf=trueで同一blob、属性の有限検査は `P550/route3d-implementation550/grid-attributes-receipt.json`。

### ACT-550-HIT-FIX：点表示の是正と最新資料の整合点検

2026-10-01、a448f87（全326実体）を固定し、人間の修正/資料点検依頼をS36 s36-hit-fix550へ操作前に記録した。D-174と現source/資料を読み、2Dだけでなく3D/KMLの干渉外周も撤去、点・件数・群詳細を保持。着地0件の0.0%表記も未定義へ是正した。独立批評の初回指摘と修正後probe/再批評はP550/repair-hit550/critic/。

型/build・frontend182試験、独立source probe、8551の2/16・14/16干渉、14履歴と詳細往復・点表示切替を確認。保存版18で14候補を退避し、backend再起動なしのasset追加/index交換で4応答bytes一致、検証後も候補/結果/healthを保持した。Google再接続・気象取得・飛行再計算なし。THEORY/IM/COMMANDS/入口を訂正、PROGRAM/VISIONの変更不要の根拠と確認範囲、構造索引、理論23頁の出版/視認をS36へ記録。検査・固定保存の票は同じ外側フォルダーへ置く。保存直前にPR30の人間による統合を確認した。現在main 06936856ee0deab2fe0b3f3b04220d60652ffba6のtreeは比較元a448f87と同一。旧branchは削除済みのため、旧Git/mainを変更せず codex/restore-interference-points-055 の新Draft PRへ保存する。PR metadataのbase_shaは過去の基準であり現在mainの観測ではなかったため、ls-remoteと固定fetchで訂正した。観測票はP550/repair-hit550/main-merge-observation.json。

保存実績：内容C1 `b9a1973dca187b18756182a84b8351c2124de2c3` / tree `f34d2b9c2f05e8d13440451c6eeab0c6a6393b26` を [Draft PR31](https://github.com/GENIANY/space-balloon-simulator-jp/pull/31) へ保存し、全326実体の固定読戻しと元local.git 1,588ファイル不変を確認した。8551へ修正反映済み。実績追記と元の改行形式へ戻す最終記録を同PRへ保存し、最終自己SHAは外側票/PR本文に置く。mainのマージは人間が行う。 原票はP550/repair-hit550/save-receipt.json、最終票は同record-final/save-receipt.json。最終独立批評はcritic/final-doc-review.json。

### ACT-550-HIT-DISPLAY：実計算の干渉外周と模型の点表示を照合

2026-10-01 JSTの問いを受け、controller.jsのdrawMap/classification/点半径・透明度、ensembleProjection.tsのcompact着地点、landing.pyのextent、実装ノートの分母/輪郭契約、PROJECT_CONTEXT RPT-051/052、DECISIONS D-171/172、現在の8551画面を読んだ。private branch e86aafa1cafb8e16ef25aa1d2a6946fc84e5c96d、main M420不変。source・計算・入力・表示選択を変更しない読取調査。

集合結果には干渉全点の凸包（退化時は点/線）を意図的に追加しているが、個別点も描画している。他候補の点は1.5px/0.5で、外周の方が目立ちやすい。現在の注目候補9は干渉0で、別の可視候補の干渉も表示中だった。外周は点群の要約であり、禁止域との交差面/予測100%域ではなく、干渉数は個々の着地点から算定する。

D-171の囲い案の後にRPT-052/D-172で点と数へ整理した経緯を確認した。現行実装ノートにextentが書かれていることだけでは、模型からの表示差や「干渉した点」のUI名との不整合を正当化できない。既定は点と件数、外周は必要時の補助とする方向を次の設計案として記録した。今回は採用/実装変更なし。理由・未確認・次の実物評価はS36 s36-hit-display550、検査/保存の固定票はP550/inspect-hit-display550/へ戻る。

**同ターンの訂正：** 70485a8保存後、D-174の第四巡・二配置比較後の採否まで再照合すると、包絡復活と描画形式の常設選択UIは既に不採用だった。D-172で読解を止めて任意外周を推した照合不足を認め、上の推奨を撤回する。修正方向は、干渉点・件数・群詳細への導線を実計算でも守ること。外周を再導入する新しい根拠は今回得ていない。source/利用者画面は変更なし。S36同節とP550/inspect-hit-display550-correction/へ戻る。

### ACT-550-BACKGROUND：背景写真切替による地図停止を修正

2026-10-01 JST、人間から背景を衛星写真にできないとの報告。比較元はprivate branch / Draft PR30の 4384c567e4492843c14a8e8e4c74be20f5385042、main M420不変。Leaflet 1.9.4のTileLayerに対して、地図から外す前のoff()がremove時の地図イベント解除まで消すことを独立した通信なしの再現で確認した。controller.jsの解除順序だけを変更した。旧処理は同じgetCenter例外、修正処理は25回の交換・viewresetを通過した。

利用中8551で写真タイル16/16読込、地図との切替、拡大/縮小/移動、共有地図へ戻る操作を実画面で確認。利用者の14候補と既存計算結果を保存・全文照合してから適用した。初回再起動でCodexが保存先環境変数名を誤り別instanceの空stateが起動したが、再読込前の照合で検出し停止。BALLOON_DATA_DIRをsourceと照合し、元instance・保存版14を復元してから再読込した。元stateの上書き・版巻戻しは行わず、誤起動stateも削除しない。

型検査、Vite build、screen-contracts 12件成功。最初のsandboxでのspawn EPERMと再実行成功を区別する。実装索引はcontroller一件の指紋更新のみで構文宣言・階層・34科学API・40 HTTP経路を変更していない。S36「背景写真切替」に原因・操作・保全・検査限界・次判断を記録。外側証拠はP550/repair-background550/ のsource前後、通信なし再現、build/test、索引照合、前後project/health、候補検査・Git読戻し。追加報告の白画面は通常更新の強制viewresetが直接原因。4箇所だけ強制指定を外し、CSS復旧専用の1箇所を保持した。通信なしの25回更新で旧処理は300タイル破棄、新処理は0枚破棄・既存12枚保持。批評役は旧CSS復旧との独立性を確認し、自身viewのecho省略は受領視点や結果更新を落とす懸念から見送った。最終適用では保存版15・同instanceのproject/health/runs/ensembles生JSON全文一致、実画面の連続時刻入力・移動・詳細往復・地図高さ調整を確認。全再描画負荷や写真3D・科学精度の新しい受入ではない。

### ACT-550-WRITER：見えていない検査ページの送信権と停止サービスの復旧

2026-10-01 JST、人間から「一つのタブしかないのに取得を押しても再計算できない」と報告された。比較元は同private branch / Draft PR30の `e0ff4a98ccb014265cb0572179b90de9ea6fb467`、main M420不変を再確認した。古いCodex検査ページが同originのWeb Lockを保持しており、利用者の画面はreaderだった。取得ボタンは空きlockへの再試行で、協調した移譲ではない。8551 proxyは稼働していたが8550 backendが停止していることも別に確認した。停止の元原因は未確定。

同じruntime01・dist-review550-07・state-review550でbackendを隠しプロセスとして再開し、instance `a01d2deb-6082-4a3c-a749-59bbc0bbb02b` と計算可能healthを確認した。旧検査ページの閉鎖は未保存状態の保全不足を理由に自動承認レビューが一度拒否した。通常UIで旧計画を保存し、全project応答を外側へ退避してから旧ページを閉じ、現在の比較案を保持したまま送信権を取得できた。

旧ページの保全保存により版11→12の競合を生じさせた点も今回の不手際として記録する。現行の通常409経路は未保存草案を保持するが、再読込で草案を置換する案内しか出なかった。サービス停止中にDB全体をbackupし、instance・版12全文一致・active job 0を条件にCodexが追加した保存だけを版11へ戻した。その後同じサービスを再開し、現在の9候補を通常UIから版12へ保存した。利用画面は再読込せず、キーを読出していない。この限定復旧を汎用的な保存競合解決手段とはしない。

実計算・3D保持・最終保存の結果はS36の同名記録へ戻る。根拠はP550/`repair-writer550/` の前後project/health、旧検査project退避、SQLite backupと限定復旧票、起動ログ、検査・Git受領票。製品source/buildは変更しておらず、協調した送信権移譲・草案の退避/競合解消UI・通常起動の簡便化は未実装。人間へ渡す前に、実際に使う画面で編集→計算→保存まで通すことを優先し、古い検査ページを無条件に保持しない。

### ACT-550-3D：通常確認画面へ検査用の通信制限を残した不具合

2026-09-30、ユーザーの指摘と修正依頼を受けた。記録C2 `51c9b95a5ccab56274ade81e27384f73e5378346` / tree `cda8e4aee3c97441085b88df023d78e7b69cd388` は同private branch / Draft PR30へ保存済みで、今回もGitHubのhead/private/draft/unmergedとmain M420不変を確認した。下の「記録C2未保存」は過去の追記時点の記述である。

原因はP550の `review_proxy550.py` が付ける `connect-src 'self'`。3Dの削除やAPIキー失効と推測せず、配信ヘッダーと画面受領を照合した。実装済みCesiumの接続先 `https://tile.googleapis.com` とGoogle出典画像 `https://assets.ion.cesium.com/google-credit.png` だけを既存制限へ追加し、8551のproxyのみを再起動した。backend instance `a01d2deb-6082-4a3c-a749-59bbc0bbb02b` は不変。5経路の200・配信制限更新・3D HTML同一bytesを確認した。製品ソースとbuildは変更していないため、0.55の実行環境修復記録として追記する。

人間が新しい8551タブへキーを入力して接続。主担当はGoogle写真mesh・軌道・落下結果・合成禁止領域・Google出典表示を視認し、2Dへの復帰と拡大/縮小、3D再表示を操作した。7/7候補・71表示要素を保持し、明示接続試行表示は1のまま。これは課金確定数や全tile要求数の意味ではない。実マウスの面内ホバー、全地域、科学精度は今回再受入していない。旧タブの未保存状態を残し、接続済み新タブを維持する。

根拠はP550/`repair-preview3d550/` のplan、HTTP前後票、元proxyと修正版、およびS36の実績。旧proxy SHA256 `7cbaf93b02f7bdd83d55513dee93b1270762481ef38e6792d1a154486c65e626`、修正後 `feeffb36b91c5852623a87ba4ec97ffc5d2306840ae29bf8ba0d0c6e4990539a`。一般の起動経路はCOMMANDSの直接uvicorn配信であり、この検査用proxyを必須にしない。今後はUIを引き渡す前に、配信制限が案内する操作と矛盾しないかを確認する。次はこの修復記録の検査・同PRへの保存で、main統合は人間が行う。

固定比較は0.54記録C2 `cc7b0fd0463a69ad495debb7f03f1b3eb734e0e6`、tree `46ad5ea17e9173b8f201bba59c1e44f07f0a2fd4`、全302実体。P550は `C:/Users/genia/AppData/Local/Temp/balloon-seasonal-550`、基準はその `basis540`。main M420と既存private branch / Draft PR30を維持する。0.55の証拠束は出版済み。内容C1を保存し、全326実体を固定読戻しした。記録C2はこの追記時点で未保存であり、その最終SHA・完了は外側受領票とPR本文へ置く。

### ACT-550：現在予報の継続操作と、過去原日時の有限接続

| P550内の根拠 | 確認したこと | 今回の限界 |
|---|---|---|
| ui-observations550.md / ui-after-restart550/weather-acquisitions.json | 09-30 00UTCのGFS、lead9–17の9時刻。北海道の任意秒本命と6延期を支える範囲を明示取得。新規1,437,320 bytes、取得状態の開始→終了125.940秒 | 一環境の経過時間であり、純転送/積分/画面時間と混同しない |
| gfs-boundary120-550-01/receipt.json / gfs-endpoint384-550-01/receipt.json / gfs-offline-readback550.json | 同じ09-30 00UTC予報の119:17:13–123:17:13と379:17:13–383:17:13の窓を取得し、各窓で地上→30km→着地まで計算。新規619,441/486,264 bytes、取得53.127/35.934秒。通信なしの再読でも全結果値・全入力不変 | 120h付近の時刻間隔変更と384h手前を含む有限の核/CLI検査。全予報期間のGUI操作・予報精度の保証へ広げない |
| 同UI票 / ui-after-restart550/runs.json・ensembles.json | 本命+30分刻み6延期の7単便と、共通16機体標本×7条件の112試行。集合は112/112着地、単便7件は完了・結果読取可能。単便着地は主担当のUI観測 | 仮の破裂高度28–32km一様幅。校正済み落下確率ではない。合成2領域（穴・重複）による干渉は本命2/16、+30分14/16、+60分12/16、後続4条件0/16。該当2件の履歴・東北軸・風分布とSVG保存を確認 |
| ui-observations550.md / proxy記録（主担当が最終根拠を追記） | 受付後の応答503を作り、再読込後も固定要求を保持。単便はGET照合後に未送信の6便を明示続行、集合は同じIDの明示再送で受付を確認。別タブreaderは保存を拒否 | 自動再送/別IDの新規集合へ読み替えない。全クラッシュ点や全送信権移譲の受入ではない |
| ui-before-restart550 / ui-after-restart550 / restart-readback550.json | project / runs / ensembles / weather-acquisitions / health の5応答は正常再起動前後でbyte一致 | 全APIの一致ではない。weather-sourcesはJRA2窓追加により変化している |
| jra-two-window550/normalization/receipt.json / jra-offline-readback550.json | 北海道の冬・夏2原日時窓の全量検査、原Float32値を保った保存、既存Bで地上→30km→着地。別processで通信なしに全result値を再現 | 過去UIでは明示3窓の2着地・1未取得、地図と履歴の対象数区別を確認。別exportの全bytes再生成・代表季節MC・精度を認定しない |
| frontend-regression550-06/receipt.json / review-build550-06.json | 06時点の18file・180試験と型検査が成功。保存HTTP既定値の限定照合、気象関心と標本選択の分離も反例へ追加 | 先行169/175/176件等を加算しない。backend試験や実UIとは別 |
| frontend-regression550-07b/receipt.json / review-build550-07.json / ui-write-boundary550.md / index550-v3 | 共通requestの全非読取要求を送信権と保存先へ束縛。最終18file182試験・型/build成功。readerの再集計POST増分0とownerのPOST201/固定集計受領を主担当が実操作。2sourceを索引へ再反映 | 06/07を合算しない。風統計の既存Abort/同画面IDは永続要求台帳ではない。全送信権移譲は未確認。DBの実hashは確認済みだが、起動時に使用したDB_SHA256名は非対応で、環境pinの検査実績とはしない |
| backend-recovery550-all02/receipt.json / backend-climate-optin550-01/receipt.json / 先行各範囲票と独立レビュー | 最終backend回帰は143成功・実DB指定を要する1件skip。その1件を同じ固定sourceと提供DBで別途実行して成功し、DBとsourceの不変を確認。完成結果回復・pool異常・同ID照会・原日時・台帳識別は各範囲票へ戻る | 143成功/1skipの元票を全成功へ書き換えず、追加1件を区別する。先行52/23/選択5等を合算しない。実DB試験は集計値・形の有限照合で科学精度の受入ではない。初回Temp権限失敗を保持 |
| technical-publication550/final-receipt550.json / guides550-final01 / index550-v2 | 4技術本文と構造29頁/理論23頁のPDF・検索txt、構造索引の既存9scopeを出版・読戻し。全52頁概観と改訂6頁、新構造2頁の独立視認。215索引入力と34旧APIを照合、新経路名の誤記を独立批評で訂正し既存API索引1試験成功 | 管理閉鎖/Git保存とは別。Overfull/Missing character0だが既存Underfull/字体代替警告あり。旧科学式/全UIの再受入ではない |

証拠束 `references/development_evidence/practical_forecast550.zip` を65,454,340 bytes・2,267 memberで保存し、全member読戻しとSHA256 `422dcc2c11b4d3dcdbd62b7ba5df2d8fe49c7f23a08ae3c396a9f7c9f194e07b` を確認した。初回出版分（2,213 member、SHA256 2035b7e1c3a519da2bab6f54677fc419ed6e605cd0ac5398f0696e36a150ee27）は外側に保持し、全旧収録内容を保ったままFE07・索引v3・送信権の実画面確認54入力を加えた。採用した固定stateは完成資産1,377件とSQLite backup 3件。直接DBコピーを含んだ初稿は不採用として経緯を残す。最終批評で構造ガイド7頁の旧「季節試算は人工のみ」という総称を原日時の実計算経路へ訂正し、PROGRAMのみ再生成した（29頁、抽出差7頁のみ、同頁を視覚確認）。NOTESの共通送信権・instance照合説明も修正し、束後の実績は `guide-contact-final550/publication.json` へ保持する。トップ15試験ファイルの最終回帰は310成功（`top-level-science550-02/receipt.json`、固定117入力不変）。これらはGit保存/管理閉鎖とは別である。

主担当の追加観測では、PUT受領200の応答だけ503化し、照合GET503の後のGET200で別版へ誤判定せず受付確認し、後続の高度軸を保持した。気象分析の1月前半という関心も詳細・保存再訪を通じて保持した。初回の別版誤判定と来歴/標本欄の衝突は、修正前の失敗として残す。詳細な操作順と最新の根拠追記、証拠の固定先、Git保存の実状態は[S36](BOOTSTRAP_RUNBOOK.html#s36-result550)へ戻る。初期表示修正の実故障後UI再実行、全送信権移譲、全クラッシュ条件は未確認、Googleは今回未接続である。以下の0.54以前にある「現在・次・未保存」は、記載当時の履歴である。

### ACT-550-C1：内容保存と固定読戻し

内容C1 `59ea0d6765f76c13e6708c1fd7cf734401882b94`、tree `8be26248eff105153d53df086d81afe4b04c2cd4`、親0.54 C2 `cc7b0fd0463a69ad495debb7f03f1b3eb734e0e6` を `2026-09-30T11:15:43.910892+00:00` に確認した。根拠はP550内の `freeze550.json` / `git-receipt550.json`（SHA256 `f278250f3e5827841f8c8bb26b7ab556c2c323d14ab7724afe653c68b7b31df5`）と、最終保全観測 `execution550-initial-publish-c87de24ef0464d17b707d5c3cf658def/005-preservation-verified.json`。全326のpath・mode・size・blob・SHA256を固定照合し、private branch / Draft PR30とmain M420の境界を確認した。

管理6検査は `management-checks550-02/receipt.json` による `6検査すべて成功（同一326実体の作業フォルダーでも6検査成功）`。管理3試験fileは `management-regression550-02/receipt.json` による `指定3fileのcollect/JUnit一致183件成功、失敗0・エラー0・skip0、試験前後の326/基準302不変`。実行対象と失敗・再試験を分け、既存FE182件・backend143成功/1skipと追加実DB1件・科学/CLI310件へ加算しない。管理閉鎖時の研究REVラベル正規化の不一致は、旧ラベルを保持し確認55だけを更新する是正を行い、六冊bytesを保ったmanifest再生成へ戻した。C1固定前に見つかったHTML現在版表示と先行管理検査については `初回management-checks550-01は2成功/4失敗。MAP frontmatter、HTMLのhead/現在表示/末尾、S36の最終見出し状態、0.55履歴行を修復した。INTEGRATION/EXCELの確認印を先に確定し、research-closure550-r5でmanifestの21+3参照指紋だけを更新、六冊と抽出は不変。metadata-close550-root03を反映後、management-checks550-02とmanagement-current550-01の各6検査が成功した。`。後続管理・保存票は既存証拠ZIPの外側に保持する。

保存の経過・失敗票・次操作は[S36](BOOTSTRAP_RUNBOOK.html#s36-save550)へ集約する。この追記を記録C2として保存する前であり、C2自身のSHAや完了を本文へ先取りしない。

## 0.54時点の参照先と実績（履歴）

## 現在の参照先：RPT-074 / S36（0.54安定化候補）

比較元は0.53記録C2 `f2a3fa6fa0621076452001177ce3556ef189acd5`、tree `ed8d1ded2ec3ce82e7ec3a4d2531c79e874101e9`。P530/record-git-receipt530.jsonの2026-09-30T03:21:28.926227+00:00・readback_verifiedを新たに確認し、全295の固定byteをP540/basis530へ保全した。P540は `C:/Users/genia/AppData/Local/Temp/balloon-practical-540`。旧8530のproject/runsは中断前とbyte一致。旧8531の未保存編集と接続を保持し、8540/8541の別stateで検査した。

### ACT-540：現在予報・反復比較・観測回復・保存再開

証拠束は [practical_weather540.zip](references/development_evidence/practical_weather540.zip)（790 member、39,717,459 bytes、SHA256 `dcba3f1ea29c77180fbeff6b7f1f306bfbf1aea2fccf14575531a008af5c46c1`）。全member読戻し後に保存。後続の索引CLI7試験・管理閉鎖・Git保存票は束外で、S36へ戻す。

| P540内の根拠 | 実際に確認したこと | 限界 |
|---|---|---|
| inventory-live540.json / plan-live540.json / acquisition-final540.json | 09-29 18UTC、北海道周辺6有効時刻を明示取得。947,279新規bytes、77.554秒。配布一覧観測42.328秒と分離 | 09-30 00UTCは一覧lead0件。前周期を無言採用していない。単回通信費用 |
| single-result540.json / single-cli-comparison540/receipt.json | 43N/141.5E・06:17:13UTC、地表68.86m+明示5m、30kmを経て着地。API/CLIの873記録・10,733数値一致。worker2.954秒、独立CLI3.716秒 | CLI値一致は同一核の再現。精度と純積分時間ではない |
| ensemble-final540.json / project-live540.json / ui-review540.md | 本命/30分延期・破裂高度28–32km一様仮幅・16共通標本ずつ32着地。合成領域12/16と5/16、該当12履歴・図・風の表示 | 人工領域は規制情報ではなく、機体仮幅は校正済み分布ではない |
| proxy540.jsonl / UI票 / restart-comparison540.json | GET25秒遅延/503後に再送なしで復帰。保存視点維持、正常再起動後6応答のJSON意味値一致（5はbyte一致、sourcesはキー順差のみ） | 強制終了/電源断/POST応答停止の全域を受入しない |
| restart-before-climate-analysis540.json / UI票 | 2016–2025・全UTC帯/570格子の固定半月統計を1回作成。年間4図の凡例、地域300hPaの図と再読を確認。応答約3.75MB/1.094秒 | loopback応答経過はDB/描画単独時間ではない。年/時刻mask・季節分位/MC未接続 |
| backend-review / frontend-final-tests.json / root-code-review-final.md / frontend-cross-review540.md | 新backend19と既存23を別実行で成功、frontend130/36suite成功、型/build成功、視域VM7例。批評による修正と再確認 | 初回権限エラー等を保持。全科学/全UIではない |
| reproducibility540.md / runtime01-complete-manifest540.json | 最初74path runtimeの分類来歴3点不足を修復。新77path複製は全byte一致、4反例拒否 | 旧analysis500を成功へ書き換えない。環境依存の自動導入ではない |
| git-diagnosis/report540.md / git-guard540 | 旧1448内容は不変、新12は固定C2完全blob、19mtime差。生成者不明。保全連鎖と物理分離の読取検査を改訂 | 原.gitを同期/修復しない。人工反例と実保存は別票 |

GSI背景は許可された合成北海道例で確認後、JRA回帰と地域図では検査CSPで外部画像を遮断した。背景欠落の通知と気象値保持を確認し、地図品質の受入には数えない。Google再接続・キー読出しは行っていない。確認した画面はCUA表示観測で、スクリーンショットファイルは保存していない。

構造・操作・契約を更新し、PROGRAM27頁/THEORY22頁を警告0で生成した。全49頁の配置概観と変更頁を視認し、最終renderは訂正したPROGRAM7頁以外が初回と同pixel。guide-publication540.jsonで2TeX/2PDF/2txtの一致を固定した。内容C1を同じprivate branch / Draft PR30へ保存し、全302実体を固定読戻しした。管理6検査と管理回帰224件は成功・skip0。記録C2はこの追記時点で未保存。 C1 `bd4a659cd9b80b94d884528f0ad2c788234521a8`、tree `f3c7feaf1c7e2f932806e690ba95306266d134cd`、記録時刻 `2026-09-30T06:38:45.394761+00:00`。原票は `P540/freeze540.json・git-receipt540.json、management-checks540-02/receipt.json・management-regression540-01/receipt.json、S36#s36-save540。` C1とC2の保全観測は別に扱う。次の対象は風統計で候補季節/高さを絞った後の元日時窓の小集合であり、半月周辺量から瞬時共同場を作らない。以下の0.53以前の『現在/未保存』は当時の記録である。

## 0.53時点の参照先と実績（履歴）

## 現在の参照先：RPT-073 / S36（0.53候補、内容C1読戻し済み・記録C2追記中）

比較元は0.52記録C2 `3057db449af449d024dac2ce88bb32bd454483a0`、tree `ea2b6c1f3aec77d05959a22003163a6cbeff7b05`、全292実体。P520/record-git-receipt520.jsonは2026-09-30T00:41:37.916439+00:00にreadback_verifiedを記録する。P530は `C:/Users/genia/AppData/Local/Temp/balloon-jra-gui-530`、固定比較はbasis530.jsonとbasis520（292実体）へ戻る。既存private branch / Draft PR30を継続し、main統合・元local.git M101の同期は行わない。旧1305・前回診断13・追加診断65を分けた1383実体の保全を継承する。

### ACT-530：実過去場を、秒・延期・詳細・保存へつなぐ

| 根拠（P530内） | 確認した内容 | 境界 |
|---|---|---|
| gui-cli-comparison01/receipt.json と3例の原入出力 | GUIの02:17:13/04:17:13/04:47:13 UTCの全result/provenanceが各独立CLIと一致。848/849/849記録、全て30kmを経て着地 | 同じ固定窓・機体のn=1。季節確率やモデル精度の検証ではない |
| 同票とproxy530.jsonl | workerは8.010/6.602/6.516秒、別CLI wallは7.034/7.356/7.279秒。延期は約6.6秒待機。結果GET約817KB | wallの内訳/包含を区別。loopback転送をブラウザ描画時間へ読み替えない |
| root-review530.md、project-before/after-restart530.json、runs-before/after-restart530.json | 既存候補/延期/履歴比較、人工矩形の本命1/1・子0/1、該当群詳細、保存再読と再起動前後のAPI同一を確認 | 実地域背景をCSPで遮断。Google未再接続、スクリーンショットファイルは未保存 |
| crash-recovery01/receipt.json・observation.json とproject.json/runs.json | アプリ終了後、採用済み23source不変、41stateファイルを保全して再開。API応答bytesは再起動前と一致。新しい8531タブでも同じ本命・時刻・領域・該当群・図・選択時刻を復元 | 稼働SQLiteの将来bytes不変を保証しない。再計算なし、画像は観察のみ |
| backend/frontendの試験票・差分・索引レビュー | backend34成功/5期待失敗の後、訂正/追加を含む7成功。FE110成功と後続1成功・型/build成功。四状態の照合を有限試験で評価 | Temp拒否・spawn EPERM・syntax失敗を保持。40/111件一括成功、全ブラウザ行程成功とはしない |
| guide-review530・guides-build-final530/build.json・docs-publication530.json | PROGRAM p8の固定case/現在source分離を訂正し、PROGRAM27頁/THEORY22頁、警告0で生成。全頁配置概観・変更頁とroot有限視認を区別。担当資料9点・ガイド6点を正本へ反映 | 旧科学式全体・全source動作・印刷の再受入ではない |

気象SHAは `17acf33d243843ce91b3c1f8e8266355bf5a4dfccba652796d0b69d2216aea91`。保存project SHAは `245cc5b55dfc04db76984a461b79aead910981741e9ec5c3de0172aeddd319ec`、runs SHAは `38a6e7ba2bd1e9fe199ee71c7331ab7a0cfcaa5d09ad137f67fc8feb7a976dba`。前後応答bytesの独立照合を、この候補作成時にも行った。現在sourceの内容照合・入力の未計算・GET読取状態を分けた設計はD-192/IMPLEMENTATION_NOTES、操作はCOMMANDS、階層と接点はPROGRAM/INDEXへ戻る。

初期地図の東海自動fit不足、n=1風配の0/1反復目盛、位置だけを変えてもASL高度は自動補正しない点を残す。単便の数値一致はUIや科学精度の全面合格ではない。次は北海道内の少数原日時窓を事前固定し、期間統計→条件比較→保存の行程と費用を評価する。窓IDと機体標本ID、取得失敗/支持不足と有効標本を分け、期間統計から瞬時の共同場を作らない。

証拠ZIP `references/development_evidence/saved_jra_gui530.zip` は347 member・23,989,555 bytes、SHA256 `b7468cf793e0c5a6fcc0c317112cb4b79b11c5e3a8edd65bc08f4fb22e9ed188`。全CRC/SHAを読戻し、研究7生成物も現本文と一致した。**内容C1全295の固定読戻し済み。** 管理6検査/回帰の実結果と残る記録C2は[S36の保存実績](BOOTSTRAP_RUNBOOK.html#s36-save530)を参照する。C2はこの追記時点で未保存。

### ACT-530-C1：実保存後の管理・Git参照

内容C1 `566fa1214eb4d8908d3d1560031f74a39b3aabe2`、tree `59d45f664c4d7947fe4afcbc9dae52e1eaf012a9`、親 `3057db449af449d024dac2ce88bb32bd454483a0`、全295。P530/git-receipt530.json の `2026-09-30T03:08:58.066744+00:00` の `readback_verified` とfreeze530.jsonを対応させた。管理6検査は `management-checks530-c1-final/receipt.json`、管理回帰は `management-regression530-c1/receipt.json` → `management-regression530-c1-retry/receipt.json` の順に読む。3パス修正票 `entry-reference-fix530/proposal.json` と主担当意味票 `entry-reference-publication530.json` の後、同1件の再試験 `management-entry-recheck530-c1/receipt.json` を読む。224件一括成功とはしない。初回はWindows Temp権限で実行/終了処理が失敗した（JUnit447 entryは224試験と223終了処理errorであり447独立試験ではない）。通常権限で同じ224試験を再実行し223成功/1失敗。失敗原因はREADMEの根拠IDが旧版のままで現行IDの故障注入が成立しなかったこと。判定器を弱めず参照を訂正し、同1件を再試験した。各時点のsource hashと失敗ログを残した。

元local.git：元local.gitの旧1383は内容/HEAD/ref/indexに変更・欠落なし。新65を別診断し、63完全blob（固定0.52 C2一致38、現候補一致23、既知JSONのCRLF→LFのみ1、途中RUNBOOKの実績hash一致1）と未完成圧縮prefix2を区別した。追加生成者は不明。原物を採用/修復/削除せず、固定1448のbytes・mtimeを保全条件として専用Git保存先との物理分離も検査し、C1保存前後の一致を確認した。中間RUNBOOKは独立保管bytesでなく実績hashとの照合であり、未完成2件は完全objectではない。過去から全Gitが不変だったという主張ではない。 先行freezeは未記録65を検出して保存前に停止し、診断後の制限環境Git照会もexit128で停止した。freeze/push票がないこととremote親を確認し、通常環境で同じ固定照合を実行してから保存した。認証値や診断stderrは記録していない。 根拠：`git-drift530/diagnosis.json`、`git-drift530/supplement.json`、`history-scope-review530/original-git-preservation-review530.json`、`history-scope-review530/recovery-helper-implementation-review530.json`、`original-recovery-guard530.json`、`recovery-helper-adoption530.json`、`git-receipt530.json`。

この追記は実績の候補本文で、CONTINUITYの理由event・metadata意味レビュー・C2保存は別工程。最終headは外側受領票とDraft PR30本文に置き、main統合は人間が判断する。科学精度・季節代表性・校正済み落下確率は未受入。

## 0.52時点の参照先と実績（以下は履歴）

## 現在の参照先：RPT-073 / S36（0.52候補）

基準は0.51記録C2 `f94027cec2ff56b732af7bd11b2df26bdd9513a5` / tree `b7a696394584671ab5d11ed41dfd34d4b829561f`、全287実体。P520は `C:/Users/genia/AppData/Local/Temp/balloon-surface-520`。basis520.json / basis-copy520.json / basis-repoが固定比較の根拠で、前の不完全shadowを基準にしない。main M420、同private branch/Draft PR30を維持。元Gitの旧1318不変と追加65の分類を分け、全1383を保全する。

### ACT-520：実窓・近似・全飛行・費用を結ぶ

| 読解/実行根拠（P520内） | 今回確認したこと | 限界 |
|---|---|---|
| acquisition/combined-receipt520.json、三つのrunと原応答 | 全11変数・3UTC・100層・20×46格子。503/接続失敗と成功原物再利用を分別。保全応答約5.88MB | 任意期間の安定取得サービスではない。通信と待機を混ぜて速度と呼ばない |
| normalization/run520/receipt.json、join-diagnostics.json | 1,394,720 Float32原値を照合、GP/g0以外の値を変更せず緯度を整列。全窓固定join支持 | 約7.81秒は読戻し/検査込み。モデル地形は細密DEMではない |
| flights、analysis-review/decision-review520.md、independent-values520.json | strict/A/BとB刻み半減、独立同地点式。A/B約32.35m、B10/5約0.0057m | 一条件の数値比較。科学精度や多数年性能の証明ではない |
| runtime-fixture520、runtime-flight520、runtime-cross06-flight520 | 新明示schema/policy、配列一致、CLI地上完飛行、本体と試作の数値一致、06UTC跨ぎ | 任意過去取得UI/季節MCは未接続 |
| surface-research、runtime-implementation520.json、pytest-root*.xml | JMA公式TL479診断高度とfull p式、局所反例、対象169回帰成功。先行sandbox失敗は全てWinError5、元XML保持 | 原実行と再試験を区別。全画面・予測精度の合格ではない |

取得仕様はWEATHER、schema/責務はIMPLEMENTATION_NOTES、再実行はCOMMANDS、式/構造はTHEORY/PROGRAMへ追補する。原データ/比較/失敗/批評はhistorical_surface520.zipへ236 member・14,273,956 bytes、SHA256 bed4ff61a5916784ac7cb97f6b2a692aa1ce3c9c07fbd291d72164653c82dc4cとして固定し全memberを読戻した。ガイド出版票はP520/guides-publication520.json、PROGRAM27頁/THEORY22頁。管理/Git保存の後発結果は別に記録する。実績と人間に評価してほしい方向は[S36](BOOTSTRAP_RUNBOOK.html#s36-result520)。以下は0.51以前の当時の記録として保持する。

### ACT-520の後続：管理・再開・保存と次の設計

内容C1 `664a37f8978f63a8f0504a62b68cda054d98105f`、tree `08ab5cb8a407e47cd1f5aff41284ba31ce5f1faa` を保存し全292を固定読戻し。`freeze520.json` / `git-receipt520.json` が原票。記録C2はこの追記時点では未保存で、自己SHAを本文へ再追記せずPR本文と外側受領票へ置く。

管理5検査は `checks-final520/summary.json` で成功。初回のHTML末尾版番号とinline evidence ID不足は `checks-initial520` / `management-fix-adoption520.json` に保持。初回管理回帰は不整合を直す前に中断したため合否集計に使わない。修復後の全224件は222成功/2失敗、文字コードを明示した同2件の再試験2成功を `checks-management-final520` / `management-encoding-retry520/receipt.json` / `management-encoding-review520.json` で分ける。親の `-X utf8` は子へ伝播せず、継承環境 `PYTHONUTF8=1` / `PYTHONIOENCODING=utf-8` を用いた。判定条件や正本sourceは変更していない。全224一括成功とは記さない。

研究4原本の限定確認印と7生成束を `research-prestamp520.json` / `research-final-publication520.json` で整合させた。原本文・採否・旧更新印は保持。新しい研究依頼は発行していない。

元Gitは旧1318変更/削除0、追加65は完全blobで64が固定C2原bytes一致、1が既知JSONの41CRLF→LFのみ。`git-diagnosis520.json` / `git-extension-independent520.json` を別束縛し、旧票を置換しない。HEAD M101、生成者不明。初回freeze停止を消さず、有限な追加集合を検証して再開した。

8500の再開は `runtime-refresh520/readonly-review520.json`。固定source53・停止時backup3018・稼働immutable3010を照合、保存済み5 GET応答は前後同値。稼働SQLite7とlock1のbytes同一は主張しない。初回active判定のstatus/state誤りと、停止後訂正・graceful終了未観察を保持する。新規取得・再計算・Google接続はしていない。

次の設計批評は `wind-to-window-next-review520.md` / 同JSON。北海道DBには300–1000hPa・20面・00/06/12/18UTC別平均もあり、時刻情報が皆無ではない。一方、現APIはその限定切替に未対応で、任意年/日や瞬時4D共同場は集計から復元できない。今回C11は東海窓（北端38.397°N）、北海道DB南端39.896°Nと非重複。まず同じ保存場のGUI/CLI一致、次に北海道内の事前固定した少数日時窓による統計→条件比較→保存の用途評価を分ける。二半月各一日・本命と30分延期という二窓四飛行は導線/費用試験の候補で、季節代表性や確率の根拠ではない。

## 0.51時点の参照先と実績（以下は履歴）

## 現在の参照先：RPT-073 / S36（0.51、内容C1読戻し済み・記録C2追記中）

比較元は保存済み0.50記録C2 `2cefd08dfd039645b85d184a7089a7aa002ab775`、tree `e06a65986898e0cf6c5e1000ffa396012a6417a2`。全281読戻しはP500/record-git-receipt500.json、今回の固定保全はP510/basis510.jsonとbasis-repoを根拠とする。P510は `C:/Users/genia/AppData/Local/Temp/balloon-historical-510`。採用mainはM420のままで本候補は未統合。同private branch / Draft PR30を継続する。

元local.gitは旧1305実体の変更/削除0と、今回診断した追加13の完全loose blobを区別する。追加は固定0.50 C2の既知bytesへ一致したが生成主体は不明であり、元Git全体が過去から不変だったとはしない。`git-extra-review510.json` と `basis510.json` で1318実体を区別して保全した。内容C1保存時の1318実体の前後保持は固定受領票に記録した。記録C2段階の照合は別に閉じる。

### ACT-510：元UTCのモデル面から、支持内の飛行と停止へ

D-190/S36-plan510を起点に、旧JRA原本/decoder、現飛行核、モデル面の圧力・高度・時刻、保存/レポート接点を読んだ。独立批評は60秒定速だけではp/T/qと相遷移を使わないこと、格子点の約8 gpmだけでは起伏のある補間支持を説明できないことを指摘した。主担当は物理上昇・破裂・下降と地表/時刻/水平の拒否を別の実行として確認した。実結果と後続の地表量/地形stencilの判断は[S36](BOOTSTRAP_RUNBOOK.html#s36-plan510)に戻る。

| 根拠（P510内） | 確認した内容 | 限界 |
|---|---|---|
| `prepared-02/receipt.json` | 固定原本から27,609 bytesのbundleを無通信で新規生成・全payload読戻し。bundle SHA256 `cabe925a3b1fe39ffc17959e10d1b0fc586e1b0f9bbadbe965d9a2d651a3c558` | 元資料は2024-01-01 00/06 UTC・2×2格子。任意過去日時の取得ではない。 |
| `real-runs-02/receipt.json` と各原結果/manifest | 5例すべて停止・CLI終了2、直接計算とCLIのresult一致、保存manifest読戻し。物理例は301.372秒で破裂、552.201秒で下端不足、64記録・着地なし | 上空開始の診断条件。地表全飛行・実測軌道との精度照合ではない。 |
| 同実行票の時間/量 | 物理例のsimulate呼出し約0.098秒、別CLI process全体約0.978秒、保存7ファイル計272,001 bytes | 2×2の一例・一台の観察。純積分、ブラウザ表示、転送量、通常規模や季節MCの性能とは別。 |
| `regression-01.xml` | 既存GFS/飛行/CLI/旧JRA/新JRAの対象139成功・失敗0・skip0 | 有限の回帰。最終管理検査・全UI・科学的予測精度を証明しない。 |
| `adapter-implementation-review510-round2.json` / `theory-candidate-review510.json` / `theory-formula-check510.json` | 旧値/支持と保存結果の独立読解、公式TL479 §8.1の式、800層のDecimal照合、旧本文保持 | 前者の実行照合はreal-runs-01を対象。最終prepared-02実行票と測定時点を混同しない。PDFの生成/視認は別。 |
| `docs-adopt510.json` / `root-adopt-guides-index510.json` | C-10と実装ノート、理論・構造の編集元と索引の接点を主担当が読み採用 | 後続でPROGRAM26頁/THEORY19頁の出版・有限視認を完了。最終管理・Git保存は別。 |

この経路の原JRAモデル面と、既存北海道の半月統計DBは地域・期間・表す量が異なる。実装はCLIに限定し、GFS取得UIへJRAを偽装登録していない。幾何30 kmの一点照会成功は、その高さまでの全軌道と着地を支える証拠ではない。次は時刻窓/領域/地表量と起伏をまたぐ列の扱いを揃え、一つの実過去窓で地上から着地までを支える。その後に既存GUI/保存比較と季節・時間帯の標本へ接続する。

PROGRAM26頁・THEORY19頁を生成し、全頁の配置概観、変更箇所の個別画像、独立批評の反例修正と最終差分を確認した。TeX/PDF/txtは固定出版票で一致を検査した。証拠ZIPは154実体・1,014,078 bytes、SHA256 27752039ec2109a3cdd7959a335d3e9a107ac2d124e52f9ebd41dba6ce5648a7として保存した。内容C1の保存・全287固定読戻しを確認した。実SHA・tree、管理検査/回帰の実結果と原票は[S36の保存実績](BOOTSTRAP_RUNBOOK.html#s36-save510)へ集約する。`git-receipt510.json` と `freeze510.json` がC1の固定受領票であり、記録C2はこの追記時点では未保存である。 PROGRAMの呼出順1文は最終consumer批評で訂正し、build06の15頁を再視認・再出版した（他25頁画像一致）。`program-call-order-root-reading510.json`で先の出版と区別する。 `historical-field510-archive-receipt.json`、`program-publication510.json`、`theory-publication510.json` がそれぞれの読戻し票である。HTMLレポートのfile URLはブラウザ方針により拒否され、迂回せず目視未了を残した。139回帰は図注訂正前、訂正後5実行の数値JSONは前回と一致する。C10例はlabel/purposeだけ別で物理結果は同じ。科学的精度、任意過去場取得UI、地上完飛行と季節MCは未了。以下の0.50以前の記録は、その時点の表現と意味を保持する。

## 0.50時点の参照先と実績（以下は履歴）

## 現在の参照先：RPT-073 / S36（0.50、内容C1読戻し済み・記録C2追記中）

基準は0.49記録C2 `22799fe2c20627321e9c60367e974b92e16497cf`、tree `9d782987601b25252f170f5e31c009727ad6e6b0`。全276実体をP500/basis-repoへ固定照合した。P500は `C:/Users/genia/AppData/Local/Temp/balloon-operational-500`。採用main M420、同private branch/PR30、元local.git M101は維持する。旧1193実体の不変と追加112（固定C2一致blob110・改行差1・旧原本の不完全prefix1）を別に診断し、全1305を開始点として独立照合・保全した。追加の生成主体は未特定であり、過去からGit全体が不変だったとはしない。内容C1保存時の全1305の前後照合は後記の固定受領票へ戻る。記録C2の照合は別に閉じる。

### ACT-500：有限な修復・実用審査と根拠

| 根拠 | 今回読める内容 | 境界 |
|---|---|---|
| `real-raw500/receipt.json` | 完成assetの6 raw、374,827 bytesを独立コピー。不足f027、62,584 bytesだけ取得関数へ渡し、新7時刻のaxes/fields/surfaceが対照と一致。旧asset/入力不変 | 不足応答も保存実GRIBを用いた無通信再生。NOAAの現在配布やネット速度の試験ではない |
| `profile-run500/receipt.json` | 固定一飛行の原844 records/JSON一致。通常wall1.48秒、simulate1.10秒、場読込0.146秒、出力0.203秒、source_snapshot0.028秒 | 内訳は包含関係を持つ。cProfile3.16秒は上乗せあり、同process/未消去cache。一例を旧48/192試行82.6/359.6秒や原JSON41.0/164.5 MBへ外挿しない |
| `ui-review500.json` / `proxy500-final.jsonl` | 最終review06の503→A再読→64履歴/145.05分/3図→1.45分の風図→B/C再読。最後の68要求はGET200、POST0。先行実風404→固定300 hPa/草案500 hPa復元も記録 | 保存し直し、外部地域背景、新Google/全3Dは今回未確認。必要な新規選択群のPOSTは別。旧票の包括的「POSTなし」は後続反例・訂正票と併読する |
| `backend-tests500-02.xml` / `frontend-validation500-review06.json` / `frontend-tests500-review06.json` | backend98成功・1明示opt-in skip、frontend100成功・型/build成功 | Windows Temp/子process拒否の元ログと、同範囲の許可環境再実行を区別。機能失敗を削除せず、全科学/全UIの合格とはしない |
| `program-publication500.json` / `program-visual-independent500-02.json` | PROGRAM25頁生成。変更7頁をroot/独立担当が視認し、TeX/PDF/txtを固定 | この先行票は変更7頁。後続の全頁レイアウト視認は次段。THEORY/PLANは保持 |

その後、主担当は残18頁も直接視認し、全25頁の文字/図の収まりと階層の可読性を確認した。`program-root-final-visual500.json`（SHA256 `2b7ac132d33a1bf6f8dc1aad660837c9250454fc1bfd9395280ac376f6acfa0d`）と更新したpublication票が根拠である。科学本文全体/全source動作の再証明ではない。次のZIPは先行7頁時点で固定済みなので改変せず、この後続視認は本文へ別記する。

上の先行根拠と批評履歴を[0.50証拠ZIP](references/development_evidence/operational_continuity500.zip)へ保存した。3,795,156 bytes、143 member（137証拠＋6つのmanifest・案内等）、SHA256 `2ce8cab4b09450cab2961157a66278b3c69bf9b64df855600a715285297853a9`。外側全member読戻しと、repoへ置いたZIPの同一性を確認した。旧0.48/0.49 ZIPにある28入力は `external-inputs.json` にmember/hashを固定して参照し、大容量原本を再収録していない。0.49 ZIPだけでも今回束だけでも再生入力は完結しない。縮小したprofile出力は完全COMMITTEDのAPI結果directoryではなく、原結果JSONと来歴を保持した診断証拠である。

内容C1 `3b9c55c02bc336138e91082390c4ae104f2bbac9` の全281固定読戻しを確認した。管理結果と再試験の時点は[S36の保存実績](BOOTSTRAP_RUNBOOK.html#s36-save500)へ戻る。記録C2はこの追記時点では未保存。次は[S36の現在手順](BOOTSTRAP_RUNBOOK.html#s36-close500)へ戻る。条件反復の費用比較と、既存の元UTCを持つJRAモデル面を単一飛行へつなぐ有限工程を進める。半月統計から共同4D場を生成したことや、季節実MC/確率校正/科学精度の完成は主張しない。

### 内容C1の保存と、限定実績C2への引継ぎ

内容C1 `3b9c55c02bc336138e91082390c4ae104f2bbac9`（tree `40618569572bcee5885b84d37c0f929b87bc7106`）の全281登録実体を固定読戻しした。固定根拠はP500/freeze500.json・git-receipt500.json。管理5検査、先行194成功・30失敗と最終metadata後の対象30成功の区別、元local.git1305保持は[S36の保存実績](BOOTSTRAP_RUNBOOK.html#s36-save500)へ集約する。元ログと後続成功を区別し、証拠ZIPへ後発票を循環収録しない。記録C2は追記時点で未保存で、最終SHAと全数読戻しはPR本文・外側record-git-receipt500.jsonへ置く。

## 0.49時点の参照先と実績（以下は履歴）

## 現在の参照先：RPT-073 / S36（0.49候補）

基準は0.48記録C2 `57c852b010544a938bca0cca02795fa33bfd79be`、tree `32eb43efffaf9711386d6c0b55d8e88a51eadbc1`。256実体の固定照合と外側比較保全は P490/basis-repo490.json、C2保存はP480/record-git-receipt480.json。P490は `C:/Users/genia/AppData/Local/Temp/balloon-operational-490`。採用main M420、旧元Gitの診断/保全は下の0.48記録を継承し、無断同期しない。

今回の有限読解は、実GFSでの48/192試行と取得窓拡張、MC GET/履歴待機、提供JRA-3Q DBの意味/実装/既存図接続。計測はmeasurement-48/192/acquisition-03とmeasurement-independent-review490.json、保存再起動はresults-lifecycle490.json/climate-live490.json、DB有限照合と独立批評はclimate-service-independent-review490.json、図/状態境界はclimate-ui-independent-review490.json、端点/SVG修復はfinal-ui-fixes-review490.json。実UIと未確認はS36へ戻す。出力図・画面・失敗ログと240原試行を[0.49証拠ZIP](references/development_evidence/operational_weather490.zip)へ保全した。全3,835 member照合と、既存0.48証拠を併用した新240/旧25試行の別場所への実復元はP490/evidence-handoff490.json・evidence-restoration490.json。元stateは不変で、原JRA tar/DBは外部依存として明記し重複追加しない。

THEORYには期間統計の母集団・pooled R・FROM/TO・ISA・共同場の限界、PROGRAMには現役climateのFE/BE階層を追加し、COMMANDS/IMPLEMENTATION_NOTES/BUILDの3MD候補は実sourceと限定独立読解で照合し適用した。THEORY/PROGRAMのTeX/PDF/txt各3実体は別環境で生成・全頁の有限視認と限定独立批評を経て公開し、theory-publication490.json/program-publication490.jsonへ生成/公開の指紋を固定した。本文の有限読解、機械検査、実UI、科学的採用を区別する。内容C1の全276固定読戻しと最終管理検査を確認し、次の実績へ記した。実績C2はこの追記時点では未保存である。

### 0.49内容保存・最終検査・次の判断

保存票の開始時刻は2026-09-29T17:25:44.166003+00:00。0.49内容C1 bd613efe6edf5a496f846ae88042d1cf65e06d53（親57c852b010544a938bca0cca02795fa33bfd79be、tree 6cabd0c0f157b0e50f5cd36a1d9f88851d863605）をprivate branch codex/framework430-assessment / Draft PR30へ保存し、全276実体のpath/mode/blob/size/SHA256を固定読戻しした。main M420は不変。元local.gitは旧1122と開始時に診断した71追加を区別した1193実体を今回保存前後で保持した。追加物の生成主体は不明であり、過去からの全面不変とはしない。

C1と同じ276実体について、最終管理state/health/現contract/固定0.48 C2 contract/研究束一致の5検査を成功確認した。初回healthはUTC基準日2026-09-29に対してJSTで記録した2026-09-30の確認日を未来と判定した151件で、本文を変更せず--as-of 2026-09-30を明示して解消した。文書管理の5群224試験は、初回にWindows Temp下の作成・片付けでアクセス拒否を含む447 ERRORとなった。同じ5群・同じコマンドを許可された実行環境で再実行し224成功・skip0、前後の276実体不変を確認した。元ログと再実行ログはP490のmanagement490-final/management490-jst、regression490-final/regression490-permittedへ分けて保持する。検査器/schema/policyを緩めた成功ではない。既存のbackend 73試験とfrontend 87試験・型検査/buildの成功は、それぞれbackend-tests490.xml、frontend-tests490-restored.json、frontend-validation490-restored.jsonへ戻り、C2本文追記後に再実行したとの主張にはしない。

運用証拠ZIPの全3,835 memberの照合と、新240・旧25のCOMMITTEDの別ディレクトリへの実復元を確認した。原stateを保持し飛行を再計算していない。提供JRA原tar/DBは外部依存のためGitだけからの再集計を保証しない。保存済み集計の再閲覧と原DBを使う新集計を区別する。根拠はevidence-handoff490.json/evidence-restoration490.jsonと固定証拠ZIPであり、復元したサーバを新たに起動して全UIを審査したことにはしない。

実GFSの48/192試行の費用と実JRA年間/地域集計の代表行程を有限受入とし、科学的精度や通常規模全般の快適性の完成とはしない。実地域背景と背景入りSVG、今回のGoogle再接続/全3D操作の再受入は未実施。期間統計を瞬時共同場へ転用せず、元時刻を持つ過去4D場・年/時間帯mask・季節飛行は別の後続工程である。保存復元中の「未計算」表示を読込み中/失敗と区別する修復も残る。人間にはs36-next490に沿って実GFSの応答と分析行程、実年間風統計が判断に役立つかを評価してほしい。全窓cache keyと同directory内の再開に限る現構成では、窓拡張時に既存6枚を再取得した。次は完成資産に結び付く周期/lead/全selector/正規化矩形・URLとbytes/hashを照合したrawだけを独立copyし、新全窓を復号・公開検査する小修復案を比較する（未実装、速度改善は未確認。外側票raw-cache-next-design490.json、SHA256 a96a9c89abdb86cc5f18d4a2b6cbfc0a4abe52dbcc35c1b5f43c3388241cbab5）。

このC1保存実績と現在入口の訂正は明示9管理パス以内のC2へ渡す。実装・ガイド・研究束・原資料/証拠ZIPはC1 bytesを保持し、C2の本文差と依存影響を改めて読んで管理検査を行う。この追記時点でC2は未保存である。C2自身のSHAと最終全276読戻しはPR本文とP490/record-git-receipt490.jsonへ置き、自己SHAだけの第三commitは作らない。mainマージとpublic参考先への選別反映は人間が行う。

## 0.48時点の参照先と実績（以下は履歴）

## 現在の参照先：RPT-073 / S36（0.48候補）

局所基準は0.47記録C2 `42adf4fe5293824ec98e9b0fc8cd68965f71106a`、tree `dbd6506c5dbd680adc3a456e9c5973954ce3cd28`。main M420とprivate/open Draft PR30を再取得し、全235登録実体を固定blob・bytesで照合した。P480=`C:/Users/genia/AppData/Local/Temp/balloon-ensemble-480` の recovery480.json（SHA256 `faaf282736bd8bf80a414122e04e9d93e1ed201c417bb6f918f84b81f59449da`）と baseline-copy が局所比較根拠。0.47 C2未保存と書かれた下の段落は当時の記録で、今回保存済みと確認した。

### 保全と根拠を区別した開始

元local.gitは旧1122実体を保持し、71追加・旧変更0・旧欠落0。追加66はC2固定blob、4は既存sourceの改行正規化byte、1は既知ZIPの未完成prefixと照合した。一次診断 original-git-diagnosis480.json（`aa59738c276b557a9fdb2274ebd96b4c75bc2384d57863c95cf02943c1d198fa`）、独立票 git-diagnosis-review480.json（`fceab62bf67fc778a52dd8e3bc44d912b8b4ddbd369d477cc44ee3a1369f63ec`）。追加物の生成主体は不明であり、修復・削除・同期や旧履歴全体の不変宣言はしない。1193実体指紋 `e7016115c2ae535afa315cc074bb054d2222312361d42e6374b8af5a2bf74d79` を旧集合と追加診断の対応を保って保存前後に照合する。

S36/INTEGRATION7.3、研究第7巡の元量/対応標本/母数/保存の採否、既存数値核・API・具体画面を結び、取得済みGFSから実集合へ進めた。予報・当時予報と再解析・長期計画の三用途は保持する。元量の一様仮分布を予報誤差や製品の既定分布とはしない。NumPy Generator/eigh/quantile、GeographicLibのWGS84測地線の距離・方位による局所方位距離座標、SciPy ConvexHullの一次仕様を読み、適用式と実環境版をTHEORYへ置いた。参照先の最新stable文書と使用環境NumPy2.4.4/SciPy1.17.1/GeographicLib2.1の版は区別する。

### ACT-480：実標本から判断へ戻る有限受入

8481の別環境で、保存済み実GFSの等温ガス質量0.48–0.56 kg・8標本と+30分延期（計16試行）をUIから実行した。元値・全config・draw IDの対応を独立に確認した。+60分を含む初回planは場の時刻支持外として実行不可。理由の英文だけではどの候補を直すか読みにくかったため、固定planの候補別必要窓と場の支持窓を日本語で示すよう修復した。

人工の穴あき/重複GeoJSONをUIから追加し、親3/8、延期5/8の着地干渉を独立点判定と照合。重複の二重計数と穴への誤包含はなかった。同じ3標本の入力表・相別履歴を読み、保存して再開した。初回は領域JSONの項目順だけで群が解除される反例があり、元保存を保全して修復。同版で保存→再読後も3/8・保存済みを確認し、座標/ID/頂点順/snapshot/標本集合の実変更は拒否する独立反例10件と区別した。比較候補の2応答が次render前に届く場合のlost updateも、実hook反例で発見し同じ反例で修復確認した。

独立の分析照合は acceptance-api-independent480.json（`41b2bbe97040674bd19e160e8840728562f3f1165cffec2b3d66dcfb5818aaeb`）。平均着地の差0、経験閾値の最大差2.22e-14、時刻別高度の平均/分位最大差7.28e-12 m。破裂左右の相と着地終端・終了後除外を原履歴から確認した。別API受入では、共通破裂高度29500–30500 mの4標本を等温/定速上昇へ渡した。取消時2着地＋6取消、明示再試行後8着地。旧snapshot/固定plan不変、同一request IDの再送は同じ応答で、試行数を増やさなかった。これはAPI操作であり同じモデル比較全操作をUIから行ったという証拠ではない。

独立批評は母数脱落、最初の試行を平均と呼ぶ誤表示、破裂の同時刻相別点、計算しない履歴の欠落、領域版の保存、反例による点/線退化、64 MiB履歴集計上限、worker再開/完成書込中断を検討し、実装と資料へ戻した。上限は256試行/計画・4稼働集合。原履歴JSON合計64 MiB超では理由付きで履歴集計不可とし、全N台帳と着地集計を保持する。RSS保証や長期大量処理の性能受入ではない。

PROGRAM23頁とTHEORY14頁を編集元・PDF・検索本文の組で生成し全頁を作成担当が視認、主担当もPROGRAM代表頁の階層/依存を確認した。PLAN3実体は固定C2のまま。実UI・独立数値照合・機械検査・文書生成を別の証拠として保存する。新しいGoogle接続やキー読出し、NOMADS再取得は行っていない。8481はコピーした試験状態であり、旧8461/8471の利用状態を保持した。この欄の時点では最終管理検査・Git保存は未完了で、結果は追記する。

証拠ZIP `references/development_evidence/ensemble_connection480.zip` は708 member、26712272 bytes、SHA256 `551d3b1c59c0f660589a40dec8beae9f725829f1f2329347111b9dda889c8412`。全memberを照合した。管理最終結果とGit保存は後続のS36/受領票へ戻る。

### 0.48内容保存・最終検査・実用審査の再開点

保存票の開始時刻2026-09-29T15:13:21.596041+00:00。0.48内容C1 5ec82de219ee5a5add7614d782db35e2bcd4d884（親42adf4fe5293824ec98e9b0fc8cd68965f71106a、tree a90f392318d89e9b283f14da938526e2248797eb）をprivate branch codex/framework430-assessment / Draft PR30へ保存した。全256実体のpath/mode/blob/size/SHA256を固定読戻しし一致。main M420は不変、元local.gitは旧1122＋開始時に診断した71追加の1193実体を今回保存前後で保持した。追加物の生成主体は不明のままで、過去からの全面不変とはしない。

backend50試験、frontend47試験と型検査/build、数値核・気象・CLIの対象回帰を成功確認した。初回のWindows Temp権限拒否は原ログを保持し、該当する同じ5群を昇格再実行して解消した。文書管理5群224試験も初回はTemp権限拒否（447 ERROR）で、同じ5群の再実行は224成功・skip0。最終管理state/health/現contract/固定C2 contract/研究束一致は全成功、検査前後256実体不変。初回stateのHTML末尾版番号1件を訂正した。検査器・schema・policyは変更していない。完全ログはP480のcore-regression480とretry-permissions、management480-finalとfinal02、management-regression480とretry。有限UI/API・独立数値・PDF表示の証拠は直前の受入と別に扱う。

既存原JSON122件を前後指紋照合して費用を復元した。0.47の実GFS6時刻374827 bytesは取得job開始から完了まで77.072992秒で、うち要求間待機が50.016023秒。0.48の16試行は受付からsnapshot一覧登録まで35.847471秒、結果JSON計13859175 bytesだった。取消/再試行を含む別8試行の17.009885秒を連続計算の速度とはしない。CPU/RSS・純積分・実画面表示までの時間は未測定。再利用jobの同一timestampを0秒性能と解釈しない。根拠はexisting-operational-observations480.json（SHA256 fe6346aa72236b4cd7ee2445a1baebed05815af00f9b7ebe0b1f0add563ffe5e）。

実用審査の事前批評で、MC状況取得が全件一過性失敗すると次のpollが予約されないsource上の経路と、集計返答待ちに原履歴取得が先行し得る経路を見つけた。少数成功で長時間運用を受入れず、次の性能試験に先立ち再取得/待機の制御と反例試験を修復する。風DBの半月はUTCの1–15日/16日–末日で、現模型のJST暦へ無条件置換しない。2016–2025固定の対象、集計重み・有効数・実高度を明示した実DB図を既存画面へ接続する。新旧の図を見比べる目的を保ち、任意の年/時間帯や瞬時共同場を集計DBから作ったことにしない。次担当はCodex、人間には実データ画面で判断のしやすさと待ち時間を評価してもらう。

本保存実績を明示9管理パス以内へ追記し、実装・ガイド・研究束・原資料ZIPはC1 bytesを保持して再検査し記録C2へ保存する。C2自身のSHAと最終256読戻しはPR本文とP480/record-git-receipt480.jsonへ置き、自己SHAだけの第三commitは作らない。mainマージとpublicへの選別反映は人間の操作であり、この保存に含めない。

## 0.47時点の参照先：RPT-073 / S36


0.46記録C2 `2436152f815a20573e6eca7badedc958c18efe48` は作業再開時にprivate APIで固定し、main M420とopen Draft PR30を再確認した。全221登録実体はこのC2と一致し、P470=`C:/Users/genia/AppData/Local/Temp/balloon-implementation-470` の `baseline-copy` / `basis-receipt470.json` へ保存した。今回の依頼は、成熟した具体GUIを基盤として、実気象の取得と模型ゆえの非現実的接点を解消し、判断に役立つシミュレーターへ接続する継続である。採否D-186、操作・反例・結果・再開先S36へ戻る。以下の0.46の記録C2未保存という記述は、その文書を作成した時点の履歴である。

### 着手時の根拠と保全の診断

原feedback_v_0_40_1の検索本文全4頁、既存接続設計の入力/気象/標本/保存、Q420-00第7巡CODEX_REVIEW、気象取得と実UIのsourceを読んだ。独立担当は原PDF図と本文、取得器とfrontend接点を別に確認した。README/CONTEXTの現在方向・DOCUMENT_CONTROLの判断/変更/終了、MAP依存、PLANの用途・責務・費用・実装接続を選択読取した。資料全体の科学的再採用や未読箇所の通読済みへの変更は行わない。

元local.gitは、旧受領票の1011実体に対して111追加が見つかった。旧実体の変更・削除は0、HEAD M101は不変。103件はC2の既知blob、7件はC2登録sourceのCRLF→LF変換後の全bytes、1件は既知の旧ZIPの未完成prefixと照合された。独立担当は7件の変換hashとzlib/header/blob名、読取前後1122実体不変を再確認した。生成主体は特定しておらず、元Gitを削除・同期・再基準化していない。一次票 `original-git-delta470.json`、独立票 `independent-git-delta470.json/.md` の対象・帰属を区別する。

### 取得設計の反例と実装への接続

「取得できたn=1」だけで完了とせず、取得範囲・親/延期の飛行時間・予報更新・入力保持・固定結果の比較という用途から構成を決めた。批評はP470 `critique-weather470-round1.md`、`round3.md/.json` に反例を残す。取得jobと完成asset、必要飛行窓と実valid、選択中の入力と後着した取得結果を分ける。方式切替で入力が初期値へ戻る点、遅い復元応答による新計画の上書き、途中転送量の非表示、完了marker書込み中断、旧失敗jobの再試行で既存完成場を再利用しない点を個別に是正中である。実UIの受入とは分ける。

一次資料は2026-09-29にNOMADS Grib Filterの10秒待機、NCO GFS製品表、GeographicLib 2.1のWGS84 Direct、ECMWF ecCodes Python配布元を確認した。URLと意味はWEATHER_DATA_GUIDEの0.47節へ置いた。新P470専用Python3.12環境へ固定依存を導入し、ecCodes Python/native2.48.0のselfcheckは成功。旧450/460実行環境と8461の接続済み3Dを変更しない。復号・HTTPのオフライン反例検査と実HTTPの観測はS36で別に記録する。

### ACT-470：有限の実受入と資料の固定

実配布6時刻374827 bytes→資産登録→明示適用→n=1着地→保存/service再起動後の再読を確認した。結果原bytesのSHA256は前後とも `58986462a37d5d8df3d7975aa70884ea52af22272a24d87b84e7fd459985e6aa`。同条件の再取得は0新規bytes、延期+60分で延びた窓へ旧資産を適用する操作は拒否した。観察値と限界はS36、仕様は担当ガイドへ戻る。人間による面内/重なり名称の0.46確認はS35の当時記録として保持し、今回新接続したとはしない。

独立批評8巡、実画面の前後、配布原応答/GRIB/固定結果、source指紋、試験と生成票を `references/design_trials/weather_acquisition_047.zip` へ保存した。201member、3152013 bytes、SHA256 `3467c9114480198319f57d425e6e0ff9bcbb08e0fadb60569f7540cf2b9e2b6f`。全member長さ/hash照合済み。これは最終管理検査/Git保存前の有限証拠で、それらの成功を内包しない。日時が自動変換された派生JSONを原応答証拠へ混ぜていない。backend30件の旧実行は成功を観測したが完全ログ未保存で、その遡及票を当時固定hashの証明へ使わない。

PROGRAMのTeX/PDF/検索本文を生成した。19頁を作成担当が視認し、主担当は2/3/6/8/11頁の階層と依存・表示を独立確認した。最終04の確認印訂正で全頁画像が03と一致。PDF SHA256 `39ddecc7e4d0d17c7a19d001462e4d3a0646b8a77be85e7acd961bf21a6ebf09`。PLAN/THEORY6実体はC2のまま保持する。source監査が見つけたVitest由来419配布物とpytest cache4件は外側へhash照合保全し、通常buildだけで配布コピーする修正後、35試験/型検査/build成功と再発なしを確認した。監査の除外範囲は増やしていない。GFS取得/既存気象51試験は成功。全repo回帰・管理遷移・Git保存の結果は実施後に追記する。

2026-09-29T12:11:06〜12:11:28 UTC、同じ最終backend sourceで30試験を再実行し、30成功・exit0・既存依存の非推奨警告1件を完全ログへ保存した。実行前後37実体のhashは不変（P470/backend-tests470-final.*）。旧遡及票をこの時点の証拠に差し替えず、別実行として保持する。研究入口4文書の「現在0.46」「統合作業中」という陳腐化も独立批評で検出し、受領当時S35と現行S36/未発行0.47候補を分離した。問い・科学・原模型観察日は保持する。

HTML指示書の直接ブラウザ表示はfile URL policyで拒否され、この版の新しいブラウザ目視は未実施とした。別経路で回避せず、静的構造/参照検査と実アプリ8471の操作観察、PROGRAMのPDF目視を区別する。S36内の小見出しはh4へ整理し、stepの見出しを一つに保った。検査器を弱めて通したものではない。

最初の管理検査はstate・現/固定C2 contract・研究束一致が成功し、healthはS36の操作計画が表だけで手順リストを持たないため失敗した。続く全445回帰は434成功・11不合格（すべてtest_health）・skip0、前後235 source不変。10件は同一のRB-S36エラーを明示し、残る初回期限の正常基準検査はsourceから同根と推定した。表の3行全セルを保持して順序付き3工程へ組み直し、検査器は変更していない。初回原ログをP470/management470-01・regression470-01に保全し、修正後のhealth全体と管理を再実行する。

### 内容保存・修復後の有限検査と再開先

保存票の開始時刻2026-09-29T12:53:39.117904+00:00。内容C1 3b08f3e4037b655e01e0b40437dff37048ee8e3d（親2436152f815a20573e6eca7badedc958c18efe48、tree e5cd6c52713642d55fe3fd8f1b5962d24bb39fb7）を既存private branch codex/framework430-assessment / Draft PR30へ保存した。全235のpath/mode/blob/size/SHA256を固定読戻しして一致。main M420は不変。元local.gitは旧1011保持＋開始時に診断した111追加の1122実体が今回保存前後で一致し、過去から全面不変という意味にはしない。

初回全445回帰の11不合格はS36の操作リスト不足に関係する文書管理の正常系だった。修復後のhealth全65件はskip0で成功し、当初の11件も解消した。その他380件は初回成功を保持し、変更のない数値核/取得/保存試験を再実行したとはしない。初回445と修復後65という二つの実行を合わせて評価する。最終管理state/health/現contract/固定C2 contract/研究束一致は全成功、各実行前後235実体不変。版齢助言176範囲は本文の一括再認定へ変えず残した。完全ログはP470/regression470-01・health-regression470-02・management470-02、原因の独立票はregression-failure-review470.json。

本実績と現在入口を明示9管理パス以内へ戻し、実装・ガイド・研究束・原資料ZIPはC1のbytesを保持したまま再検査して記録C2へ保存する。C2自身のSHAと最終235読戻しはPR本文とP470/record-git-receipt470.jsonへ置き、自己SHAだけの第三commitを作らない。人間には8471で取得窓・延期・物理編集・旧結果との比較を評価してほしい。Codexは次に、利用者が明示する一変量の感度仮説と対応標本による実MC・延期比較、経験範囲・母数・干渉群から入力/履歴へ戻る一体の接続を実装する。次設計の境界はINTEGRATION7.3。main統合・public反映・科学的採用は今回の保存に含まない。

## 0.46時点の参照先：RPT-072 / S35

0.46は、0.40.1 r2の用途別の具体画面を同一platformへ統合し、入力・保存・実計算との接点を並行して改修した。管理検査と全437回帰（skip 0）は成功し、内容C1 `9f3819ee5cb9ddb5bac80ebd12d923aed6aef084`（tree `4b08faaa0863e0a3e51f1588a8744b68928047a8`）の全221実体を固定読戻しした。記録C2はこの案内の更新時点では未保存で、最終SHA/読戻しはPR本文・外側受領票へ置く。main統合と実MC/過去場/科学採用は完了に含めない。方針訂正はD-185、接点と受入はINTEGRATION7.3、行動と再開先はS35。0.45の計算/保存の有限成果を活用し、その簡略画面を後続製品UIの基準にはしない。以下の旧版の現在/次/未実施は当時の履歴として保持する。

## RPT-072 / ACT-460：具体画面の統合・有限受入と保存

採用main M420 `4e3e4db0d047af9479bcd68bfc2553eeb71efcc9`、比較元PR30/0.45記録C2 `ce6a29accfad6865beca0b2dfe4f414e2bafb81a`、tree `5c2dd058e23efb4792f924dfe2a2d4534104e2bc`。主担当は全166登録実体を固定Git blobと照合した。P460は `C:/Users/genia/AppData/Local/Temp/balloon-gui-460`、basis-C2とbasis-receipt460.jsonが比較コピー/票である。元local.git M101へ書き込まない。

主担当は原GUIのr2 ZIP（858実体、SHA256 `8356df3cc8f2184d5418fe3d84d1e1d274b7646f3b81be6210c07094b3d7a214`）を照合し、workflow-ui-0401の入口/forecast/weather、原フィードバック4頁の検索本文を再読した。独立批評は原HTML/JS、UI_WALKTHROUGHと接続設計を読み、予報の候補と広い地図、延期親子、干渉群の詳細、気象4画面、季節への引渡し、2D/3Dの対象共有を具体的な移行比較点として整理した。これは新画面を実操作した実績ではない。

継続性担当はDC-CLOSE/CHANGE/STABILITY、現0.45管理構造、metadata/明示review/文書finalizeと保存helperの固定条件を読んだ。旧137＋新29、当時のguard4変更、PROGRAM16頁、元.gitの追加object特例をそのまま0.46へ流用しない。更新と実review、本文変更と依存だけの再点検を分ける。P460/continuity-plan460.mdへ文書/登録/生成と長期作業の再開計画を置き、現在方針を既存担当資料へ戻した。

その後、用途別の画面host/controllerと共通projectの接点を実装し、現役frontend54実体と段階証拠ZIP1実体を追加登録した。全候補221実体、source/依存/runtimeを区別する。独立批評と主担当の実UIでは、原形との画面比較、実入力/固定結果、候補複製と親子延期、比較群、停止結果、保存・再読・再起動の有限行程を確認した。途中の空画面、CSS guard、重複入力、不等間隔履歴、保存後の選択ラベル、群と支持の混同等は反例と修正を残した。気象と季節の人工fixtureを実過去場/実MCへ昇格させていない。主担当の原票はroot-review460.md、実装/批評票は段階証拠ZIPへ集め、機械検査の成功と実UI・科学採用を分ける。この段階では管理検査・最終確認指紋・Git保存/固定読戻しは未了だった。後段の「0.46の検査・保存と固定読戻し」に、その後の実績を記す。

PLAN10.6/12に残る0.42の現在形は、当時の接続前検討と現在の統合作業を分ける最小訂正を行った。目的と工程表を保持し、現在の再開先をD-185/S35へ結ぶ。主担当はPLAN build03の30頁、PROGRAM build04の17頁を全頁視認し、source対応の独立批評後にTeX/PDFを一組として配置した（plan-publication460.json等）。THEORYと物理核は保持した。API索引は24 Python APIと26 Python source、frontendは20 TS/TSX・35 JS/MJS・16補助実体を再抽出し、物理階層・実module参照と注入/受渡しを区別した。published APIの署名/試験所在を照合する既存試験1件は成功。これはfrontend実UIや科学精度の検証ではない。


### 接続済み写真3Dの有限観察と、残る受入

ユーザーが現0.46へMap Tiles APIキーを入力した後、主担当はbundle index-DJXESdH7.jsで写真mesh、実n=1軌道と終了点、wheel拡大、左ドラッグ移動、保存視点復元を実UIで確認した。+30分を注目・+60分を非表示にした状態を2Dへ引き継ぎ、地理院タイル/軌道の位置とzoom操作が正常で、旧タイル分断が現れないことを確認。再び3Dへ戻って接続が維持され、停止候補から2Dへ戻っても着地0/1・停止1が継続した。接続試行表示は全過程1であり、Google課金数の計測ではない。キー値の読出し・不要な再接続は行っていない。写真証拠はphoto3d-connected460.png / photo3d-return2d460.png。

この実n=1例に分散面/禁止領域はなく、この段階ではその写真上ホバーは再確認していなかった。後段の人工分散を使った最新Ti修正版とユーザー実マウスの観察で、代表面内/重なりの名称表示を別に確認した。右ドラッグ回転、任意画面寸法、全export描画、実MC/過去気象/科学精度は今回の受入外。ボタンをcheckboxとして取得してtimeoutした後に役割を読み直した試行や、意図以上に拡大した後に保存視点へ戻した試行を、初回から全成功だった記録へ替えない。この観察時点では写真接続を保ち、管理検査・source凍結とGit保存は別工程として後続へ置いた。

継続性担当は、変更本文と依存だけの再点検を分けた。歴史S13〜S33等のown本文、S34の現在接続部分、管理/PLAN/ENV/研究入口、未変更消費側sourceを読み、旧手順を再実行しない境界を確認した。WEATHERの全文や過去科学を新規通読/再採用した印は付けず、SOURCES既存entry不変と現在案内への限定影響を記録する。研究資料束は現在源文へ再生成し、変更抜粋・版・manifestを確認してから候補へ戻す。段階証拠は references/design_trials/gui_integration_046.zip に置き、保存時点の実績/未確認は同梱READMEとS35で区別する。

### 原GUIの機能対応を再点検した補修

旧r2と現sourceの対応を機能ごとに照合し、人工候補JSONの読込入口と、外部CSS故障時に地図paneを封じ込めるinline CSSの移植漏れ2件を修復した。実候補の即時取消が未接続であるのに取消可能と読める文言も訂正した。機能照合表は段階証拠ZIPの gui-feature-matrix460.md / .json、現役sourceの対応は frontend/SCREEN_PROVENANCE.md へ戻る。表はsource上の移植、意図的な実データ未接続、今版の実UI未確認を分け、関数/DOM数の一致を受入の代替にしていない。

最終修復sourceは index-TiNcwLt2.js、frontend71実体で新規source追加はない。画面契約試験は5件から7件へ増え、既存17件と合わせ24件成功。追加2件は分位帯と2D/3D共通名称判定の有限試験で、写真表面のpickや実マウスの検証ではない。主担当は直前Bvh修正版で人工JSON書出し→読込→C3追加、同条件r1/60着地・64総数/同着地点を実UI確認した。Ti修正版ではJSON入口の配置だけを最終調整しており、その差を同一bundleで全操作済みとは扱わない。最新Tiの人工分散/禁止領域と写真3Dは、次の別接続による代表行程で確認した。今回完了と未確認はS35へ戻る。

### 最新Ti修正版の人工面と、実マウス名称表示

主担当はユーザーが接続した最新 index-TiNcwLt2.js の人工写真3Dで、A/Bの50/90/95%面と禁止領域の重畳、点OFF・分散面/禁止面のON/OFF、A→Bの注目と凡例の更新、クリックによるA50–90%区分を確認した。Bのまま2Dへ戻り、干渉3/60から3標本詳細へ進み、共有地図へ戻って3Dを再表示する連続操作でも接続試行1を保持した。photo-fixture-b460.pngはこの観察の写真証拠。実n=1と人工分散は別々に許可された二つの接続タブであり、各タブの接続試行1を全作業の合計要求1と数えない。接続試行表示はGoogleの実請求数ではない。

その後、ユーザーは実マウスでAの面内、禁止領域の面内、重なりで両名称が同じ吹出しに出ること、同名が反復しないことを全て確認したと報告した。これは主担当の合成入力やクリック検査とは別の、人間の実カーソル観察である。旧GUIのsource照合で検出した2漏れを修復し、代表的な画面行程を有限に受け入れる。旧GUI全機能の全状態/全端末の完全保証、任意の斜視での地表pick精度、実MC/過去場/科学精度まで拡張しない。最終管理検査・Git保存/読戻しはこの時点では未了。

最終段階証拠ZIPは `references/design_trials/gui_integration_046.zip`、123実体、2,569,829 bytes、SHA256 `369f75beb83fa17279c99a065f0854c84bec40df77e05f501747c573519d858d`。CRC・member数・READMEを照合し、root-review460.mdの写真観察、実マウス報告、JSON復元と独立CSS検査の追記を読んだ。最終sourceはrepoのfrontend/backend、原GUI ZIPは不変。CSS検査は現在CSSと最小DOM/guardの実ブラウザ確認であり、通信/linkイベントは模擬されている。最終Git結果はこのZIPから推定せずS35と固定読戻し票へ分ける。

### 0.46の検査・保存と固定読戻し

2026-09-29T10:19:50.919515+00:00、内容C1 9f3819ee5cb9ddb5bac80ebd12d923aed6aef084（親0.45 C2 ce6a29accfad6865beca0b2dfe4f414e2bafb81a、tree 4b08faaa0863e0a3e51f1588a8744b68928047a8）を既存private branch codex/framework430-assessment / Draft PR30へ保存した。全221のpath/mode/blob/size/SHA256を固定読戻しし一致。main M420は不変。元local.gitは別途診断したM101/1011実体の今回snapshotと保存後が一致した。旧938に対する73追加は前欄の通り保全し、過去から全面不変とはしない。

保存前のstate/health/contractと固定C2 checkerは成功。全437回帰はskip0で成功し、前後221 source不変。初回S35前提欄重複は旧欄を履歴属性へ修復、sandboxで一時領域へのアクセスを拒否された試験は同内容を権限付き再実行した。失敗ログもP460へ保全。backend13件・frontend24件・型検査/build、PROGRAM17頁/PLAN30頁と研究7生成物、実UI/利用者hoverは各記録の範囲に限定する。healthの版齢助言175件は自動確認印で消さず保持した。 Gitの初回freezeはsandbox内の資格情報ヘルパーがWin32 error 5で停止した。freeze/prepush/receipt未作成を確かめ、同じ処理を権限付きで再実行した。ユーザー担当の旧制限による再承認ではない。

保存前の状態を現行入口に残さないため、当初の管理6パスにREADME/CONTEXT/AGENTSの状態訂正を明示追加し、記録範囲を9パスへ限定する。実装・研究本文・生成研究束・PLAN・証拠ZIPを変えず、管理検査と研究束一致を再確認して記録C2へ保存する。C2自身のSHAと最終読戻しはPR本文とP460/record-git-receipt460.jsonへ置き、自己SHAの追記だけの第三commitを作らない。人間は用途別画面の連続性と実/人工の区別を確認し、mainを統合する。実MC・過去場・科学採用・public反映は今回の完了に含まない。

## RPT-071 / ACT-450：現役sourceと比較・再閲覧の接続

採用main M420、未統合PR30/0.44記録C2 `346e9484d3fc3444fd7a12c9e85710e479685666`（tree `7e090262c5da55a089b9f4a9292f06fa14a53c96`）を固定取得し、全137登録実体を照合した。P450は `C:/Users/genia/AppData/Local/Temp/balloon-implementation-450`、basis-C2が比較コピー。元local.gitは操作しない。添付ZIP30,725,666 bytesは保存済み原本とSHA256 `40ec3fc281680a970be56b65604a30f1bd9bc3bf618bb749a23bb659ddefcaf8` が一致し、416ファイルとCRCを再照合した。再提供を新しい研究版と扱わない。

主担当はREADME R0〜R5、CONTEXT第1〜3節、PLANの位置づけ/9章/10章の現行方向、DC-JUDGMENT/ASSET/FRACTAL/CHANGE/CLOSEと現在設計の入力/変更/寿命/保存/器の範囲を取得し、S35へ実装前手順を置いた。実装担当は既存核と固定参考FE/BE、継続性担当は実構造とガイドを分担して読む。過去全文を新たに実読・再検証したとは扱わない。

source監査の変更は依存導入との衝突を解く有限改訂である。独立担当が初稿の.pyc名directoryとos.walk分類失敗の二つの見逃しを反例で示し、主担当が修正した。最終独立15ケース、旧新版のclean137、runtime追加、未登録sourceの対照をP450/runtime-review450.mdへ残す。通常sandboxでのTemporaryDirectory準備失敗と、同じ検査を実行権限付きで再試行した成功を分ける。実NTFS junctionや全ての同時改変に対する保証ではない。

画面/API/実階層の有限受入はS35の0.45欄、一次実操作は `framework_integration_045.zip` のroot-ui-review450.md、再起動hashはui-restart450.json。backend7件・frontend17件・既存核206件を確認。PROGRAM16頁を生成し担当全頁/主担当2〜5頁を視認、24 API/35コード指紋を照合した。依存導入・型・非同期・所有lockの失敗と修復を含む。地理院背景の初回拒否はユーザーの本検査例への送信許可後に同経路で再試行し、標準/写真/復帰を確認した。管理検査・Git保存の実績は後段に追記する。

0.45保存前の照合は、0.44保存時の元.git全体との違いを検出して停止した。旧905実体の変更/削除は0、追加33実体は正常な32 loose blobと未完tmp object一つで、正常分は全て固定C2に一致し、未完分も既存のinteraction_and_burst.zipの先頭56,022,270 bytesと一致した。HEAD M101・既存refs/index/config/reflogは不変、追加の実行主体は未特定である。旧snapshotを保持し、追加33件のpath/hashだけを明示審査して現938実体を今回保存期間の基準にする。新たな差は再停止し、元.gitへ書込みや削除は行わない。調査原票と逸脱票はP450へ残す。これは自動承認拒否ではない。

### 0.45の検証・保存と固定読戻し

2026-09-29T06:41:17.393968+00:00、内容C1 `d00a2ccfdbb1ec70de21dfed227e025682eafe30`（親0.44記録C2 `346e9484d3fc3444fd7a12c9e85710e479685666`、tree `04ba4300574eab8716b30dd1d95e5a0805dc3ea8`）を既存 `codex/framework430-assessment` / Draft PR30へ保存した。C2から69差分（40更新・29追加・削除0）、全166のpath/mode/size/Git blobと凍結SHA256を固定読戻しした。main M420は不変。元local.gitは明示審査したM101/938実体の今回snapshot（SHA256 `dc1d7bad8218dcff2ae946aaec93855f8f1a8b9746136642ebf17c88e223f701`）と保存後が一致した。旧905からの追加33は前欄の調査で分離し、過去から全面不変とはしない。

保存前管理03はstate 2228 / health 4871 / contract 4263 / fixed_contract 4263 / 研究7生成物一致が成功し、前後166実体不変。既存核206件と追加のCLI/実行環境/検査runner48件に続き、state/health/contractの初回183回帰は179成功・2失敗・2エラー（exit 1）だった。確認欄の旧根拠IDと現preconditionの旧mainを修復し、子PythonへUTF-8を継承する実行条件を明示した後、該当4件と近接3件の計7件は成功した。全183件を修復後に再実行したという意味ではない。原票とrepair-regression450へ結果を分けて固定。追加48件を実行したコマンドには存在しないtest_flight_coreの指定も含めてしまい、48件自体は成功したがコマンド全体はloader errorでexit 1だった。これを全体成功に数えず原ログを保持する。新backend7件・frontend17件・build・実UIの結果とは別の実績である。

本実績を6管理パス以内へ戻し、残る実体を内容C1と比較して管理5検査を再実行する。記録C2自身のSHAと全166の最終読戻しはPR本文とP450/record-git-receipt450.jsonへ置き、自己SHAのためだけに第三commitを作らない。main統合・public反映・MC/三用途全体・科学採用は未完である。

## RPT-070 / ACT-440：研究返却の来歴と採否を設計へ戻す

固定mainはM420 `4e3e4db0d047af9479bcd68bfc2553eeb71efcc9`。比較元は未統合PR30 C2 `bea3f98a39b3827006c644743bc195804e27188b`（tree `af3a61131c6c7dc915ec30f8d8fd92003ac1fbd1`、親C1 `253f31ce5ba1b58d452d9a46d93340cff397e433`）で、主担当が現在132実体との全一致を確認した。P440は `C:/Users/genia/AppData/Local/Temp/balloon-research-440`、比較コピーはbasis-C2。元local.git M101を操作しない。

先行する研究本文・読取ログと、続いて提供された完全ZIPを同じQ420-00 rev7の返却として受領した。原ZIPは30,725,666 bytes、SHA256 `40ec3fc281680a970be56b65604a30f1bd9bc3bf618bb749a23bb659ddefcaf8`。パス・CRC・全416実体（manifest対象415＋自身）と先行2MDの同一性は主担当が確認し、receipt440.jsonへ記録した。原本を `references/research_returns/Q420-00/2026-09-29-r7/` に保持する。報告は依頼0.42・固定M420を明記するが、原依頼束の比較元M401や配布時の添付集合全体の独立確認とは区別する。

継続性担当は読取ログ全文・報告第13〜16章、付属README/REPRODUCE/verify_current/verify_package、来歴の対象と境界、E03保存手順全文、現INTEGRATION5/5.1/7/7.1/7.2と研究入口/抽出・生成処理を読んだ。source_audit_r7の全44行のbytes/SHA256/Git blobと固定M420が一致し、同梱する核9モジュール・2 example・2 weather fixtureも全13実体がバイト一致。旧成果移転票307個のcurrent_path/hashも実体と一致した。source-audit440.json、package-provenance440.json、provenance-review.mdへ記録した。著者のraw連携応答はなく観測要約であり、旧R1〜R6全ZIPとの再比較、全研究の意味的受入、全科学再現を主張しない。

採否と各担当の有限検証はCODEX_REVIEWとCODEX_EVIDENCEへ統合する。報告の12処理・197 assertion・39 JSON等を、そのままCodexの今回実績へ転記しない。verify_currentのnewは保存軌道再解析と局所式の検算で、飛行再積分は別入口。E03のhard linkとdirectory fsyncはLinux研究手順で、Windowsの製品保存・電断・真の同時競合の受入ではない。SQLiteは候補のまま、最初の比較接続に全DB/workerの完成を要求しない。

今回確認した公式仕様はSQLite WALの修正版・同一ホスト・DB/WAL保持、Python3.13 Future.cancel、FastAPIの応答後処理と重い計算の区別に限定する。資料の原文とURLは担当レビューへ置き、外部気象仕様や全ライブラリを現在版で再監査したとはしない。現在の稼働DB・サービス・実装は作成していない。

現在案内から旧「回答未受領」を除き、0.42/0.43時点の履歴は保持する。研究の問いを全面再編集せず、実受領・採否と次の担当を既存入口へ戻す。研究束は未発行候補として必要な生成差分を主担当が再生成し、最終管理・保存・読戻しの実績は実行後のS35と本欄へ記録する。この時点で今回0.44のGit保存・main統合を先取りしない。

### 0.44の保存と固定読戻し

2026-09-29T04:35:22.126768+00:00、内容C1 `87a02529f6a0609f5c47212513c8393707223bd1`（親0.43/C2 `bea3f98a39b3827006c644743bc195804e27188b`、tree `86512ceb88c315a951103fefc6c65c82bbb03fa1`）を既存 `codex/framework430-assessment` / Draft PR #30へ保存した。C2から35差分（30更新・研究返却5追加・削除0）、全137のpath/mode/size/Git blobと凍結時SHA256を固定照合した。現在PRはopen/draft/未mergeで、main M420は不変。元local.gitは今回保存前のM101/905実体、snapshot SHA256 `dbe054bb1103df45b22d74ddd39f385369362275ad1567bb4a35794a06eaba90` と保存後が一致した。0.43保存後からの不変という意味ではない。

通常sandboxのfreezeはls-remote終了128で停止し、freeze/prepush/Git受領票が未作成と確認後、同じ限定操作をrequire_escalatedで再試行して成功した。自動承認拒否ではない。保存前の管理02はstate 1,999 / health 4,451 / 現行・固定C2 contract各3,268 / 研究7生成物一致が成功し、前後137実体不変。P440/freeze440.json・git-receipt440.json・validation440_02/receipt.jsonが対応する。原ZIPの受領票receipt440.jsonは別に保持する。

この実績を6管理パス以内へ戻し、他の実体を内容C1とbyte比較して管理5検査を行い、子の実績記録C2を同Draft PRへ保存する。最終検査票はP440/validation440_03/receipt.json、C2自身のSHAと固定読戻しはPR本文とP440/record-git-receipt440.jsonへ置く。自己SHAの再追記を反復しない。main統合・実装移行・public反映・科学的採用は別に残す。

## RPT-069 / ACT-430：参考の器と、現模型から正式開発へ進む境界

Chat研究を始めたとのユーザー申告を受け取り、返答待ちに参考public repoの構成を批評する。発行した課題ID・束/版・Git基準は未確認、回答は未受領。その後ユーザーは、現private repoを実装正本とし、参考構成を取り入れる。public参考先の許可branchへの反映は人間が手動commitする。参考先の本人にだけ編集権がある特定branchで開発する事情から、private側を作業先として自由に開発し、準備できた差分を人間が反映する分担を選んだ。連携アカウントの事情はユーザー申告であり一般的な製品制約とは断定しない。今回実装移行は未着手。主担当が目的と統合評価を担い、別担当が固定FE/BEと現projectの継続性を並行して読む。

主担当の固定取得は現main M420 `4e3e4db0d047af9479bcd68bfc2553eeb71efcc9`、tree `61f6853081aea968222f341e2b62dbada642dabc`、全131実体、PR29統合済み。参考repoは `ddd3h/Falling-position-simulator2026` main `94887cbb97a8b8ba98d84ef7662e2df200f000d7`、全188実体。P430は `C:/Users/genia/AppData/Local/Temp/balloon-framework-430`。原票はfixed-bases.json、ourcommit/ourtree、templatemain/templatetreeと担当レビュー。元local.git M101を別に保持する。

継続性担当はREADME R0〜R5、CONTEXT第1〜6節、DC-JUDGMENT/CHANGE/CLOSE、PLAN位置づけ/9章/10章の現行設計、S35、INTEGRATION、D167/180/181、研究入口と抽出指定、関連課題/未知/依存を読んだ。既存の第一候補はJS画面＋Python HTTPサービスであり、今回の焦点はフレームワーク名より、現役ソース、再現できる起動/開発、条件と固定結果の意味であると評価した。全131の現役ファイルには展開FEがなく、0.40.1 ZIPの858 memberにはsource/ビルド用資料が存在した。ソース喪失や全再ビルド成功とは解釈しない。

具体比較と採否候補はD182/INTEGRATIONへ集約する。固定参考・担当レビュー・反例・照合を `references/design_trials/framework_assessment_043.zip` へ固定した（25 member、983,086 bytes、SHA-256 `e40e53d318f6d919e373507db4674781bf7c57496d4b97ff34d6fc59d0ada625`）。全memberの読戻し一致はP430/archive430.jsonへ記録。生成/検査/候補保存は実施後にS35と本欄へ戻す。PLAN・現実装ガイド本文は今回の方針を変えない範囲で維持し、依存への影響を実読して管理証拠へ結ぶ。今回の比較を科学精度、全ブラウザ性能、本体接続の受入へ広げない。

今回のINTEGRATION資料表示はブラウザのfile URLポリシーで拒否されたため、別経路で迂回せず本文とHTML構造の確認に限定した。資料の描画品質は未確認。参考アプリの独立した実UI観察は別の結果であり、資料表示成功へ読み替えない。これは保存や管理操作の自動承認拒否ではない。

全6研究束とmanifestを0.43候補として未使用出力先へ生成し、共通の現在案内/時制とQ410-05の7.2追加を差分で確認して適用した。7生成物の再生成一致を確認済み。実Chatへ新たに配布したという記録ではない。M420から本体・tools・tests・examples・固定気象入力の56パスがbyte不変（P430/code-input430-unchanged.json）で、旧430回帰を今回再実行済みとは数えない。管理と保存の最終実績は後続で記す。

0.43管理01ではstate 1,963・現行/固定M420 contract各3,121・7生成一致が成功したが、healthはM420の親C4が遷移台帳に未登録として停止した。主担当がC4を固定取得して親/treeを照合し、観測した遷移だけを補う。初回metadata書込みのOSError [Errno 22]は対象JSONの完全性を確認し、同じ操作の再試行で成功した。原因は未特定で、自動承認拒否とは記さない。また主担当の実文レビューでHTML start/s35-nextに残った旧現在案内を検出し、0.43と既進行Chatの返却へ修正した。検査成功だけで現在案内の意味を受入としない。

修復後の管理02はstate 1,965・health 4,373・現行/固定M420 contract各3,121項目と7生成物一致が成功し、前後132登録実体は不変だった。新規は固定評価ZIP1実体で、PLANのMD/TeX/PDFと本体コードは維持した。点検範囲は82 scopeで、旧scopeの依存確認を本文変更や科学の新受入に数えない。本実績追記後の最終管理結果と固定hashはP430/validation430_03/receipt.jsonへ置き、保存実績は実行後に記録する。現在は保存前の評価候補である。

### 0.43の保存と固定読戻し

2026-09-29T03:06:58.802587+00:00、内容候補C1 `253f31ce5ba1b58d452d9a46d93340cff397e433`（親M420、tree `abcf65c76070b0805e083f470607fedd76714f4f`）を `codex/framework430-assessment` へ保存し、[Draft PR #30](https://github.com/GENIANY/space-balloon-simulator-jp/pull/30) を作成した。M420から30差分（29更新・固定評価ZIP追加1、削除0）、全132のpath/mode/size/Git blobとfreeze時のSHA-256を固定照合。main M420は不変で、PRはopen/draft/未mergeである。元local.gitは明示固定した今回のM101/893実体、snapshot SHA-256 `8c3e269b39dcd947ed7c4443a76f0e109d47506183e820ba44b1192b091523e5` を保存前後で照合した。過去時点からの全面不変という主張ではない。

初回の通常sandboxではls-remoteが終了128となりfreeze前に停止し、freeze/prepush/receiptが未作成であることを確認した。require_escalated指定で同じ限定したread/freezeを再試行して成功。これは自動承認拒否ではない。保存前の最終管理03はstate 1,965・health 4,373・現行/固定M420 contract各3,121と7生成一致が成功、前後132不変だった。

本C1/PR実績を6管理パス以内へ戻し、他の126実体をC1のfreezeとbyte照合して管理5検査を行う。その記録差分をC1の子として同Draft PR #30へ保存する。C2自身のSHAと最終固定読戻しはPR本文とP430/record-receipt430.jsonへ置き、本文へ自己SHAを追記する反復をしない。人間のmain統合、実装移行、public参考先への反映、研究回答の受領は未実施である。

## RPT-068 / AUD-420：形式的な引継ぎから、独立した設計研究の入力へ

ユーザーは、UIが見えないChatに状況・目的・ニュアンスを十分共有できず、5課題へ狭く誘導していることを指摘した。ニーズと問題意識の推測を支える材料を渡し、白黒の検査とは別に内容の自己批評を循環させ、Chatから最大の設計成果を得る入力へ直す要求として受理した。D-181を本文編集前に記録した。

main M401と未統合PR29/C2を再取得し、全127ローカル登録実体がC2に一致することを照合してP420/basis-C2-410へ固定した。P420は `C:/Users/genia/AppData/Local/Temp/balloon-design-420`。元local.git M101、既存API接続/模型を変更しない。提供feedback_v_0_40_1.pdfは0.41保存済み原本のまま参照する。

初読者は旧研究入口/課題/返却/Q01束だけで仮回答を作り、その後にCONTEXT/VISIONを読んだ。元量の所有は理解できたが、同地点モデル比較・禁止域干渉の重要度と既存の製品径対膜厚換算の対立材料が薄く、3入力経路を完成させる回答へ寄った。別の要求側批評も、技術的誤読防止に比べ、ニーズ推測の材料・過去の失敗理由・問題分割への異論が弱いと指摘した。形式検査が合格したことを反証にせず、BRIEF/UI_WALKTHROUGHと全体研究Q420-00へ改める。批評による変更・残る限界はREVIEW_042とS35へ集約する。

主担当は既存8402模型で予報概要/条件編集/延期ダイアログ/詳細と風分布、気象4画面と季節計画への遷移を再読した。写真3Dへ再接続せず、そちらはS34の以前の観察と本文を使用。12か月の同尺度比較、気象時刻と放球時刻の引継ぎ区別、詳細の選択群と時刻の関係、人工模型に残る「実計算」表記と未実装入力診断を、研究側が誤読しないよう書面化した。これは模型の新しい全回帰受入ではない。

## ACT-420：仮提案を作る批評から内容を改める

BRIEFとUI_WALKTHROUGHの改訂後、批評担当が実際に三つの仮提案を作った。干渉群の交絡例、相関で裾が変わる季節例、着地点が同じでも時刻が異なる過去照合例を用い、何を判断し次に何を変えられるかを評価した。そこから入口別の選択継承、操作入力/導出量の区別、季節の同視点比較と閲覧/計算の境界を補った。Q420-00は全体から焦点を選んで具体設計へ進めるものとし、旧五課題を直列に固定しない。

配布物で発見したsup/subの意味欠落を生成器で修復し、VISIONの番号引用に対応する出典一覧を加えた。破裂への材料偏重を改め、粗い原記録の実例と風図の比較軸を渡す。初回の添付はQ420-00、風原PDF、0.40.1フィードバック原PDF（Gitコピーから読めれば重複不要）。管理手順を束の前半から外し、研究判断へ読み進められるようにした。原要求の短い引用と、原図を必要とする結論への案内も加えた。

第3巡は現物の季節操作ソースと原風図29へ戻り、大枠の新たな重大欠落は見つからなかった。これは本文を増殖させる根拠にはせず、上記の限定修正で内容レビューを閉じる判断に使った。担当は本文執筆にも関与しており、盲検・実Chat・科学検証ではない。原票はP420、永続的な判断と三つの具体例・限界はdocs/research/REVIEW_042.md。PDFの全画面視認や模型全操作回帰をこの内容評価へ含めない。

### 0.42の生成・表示確認

全6資料束とmanifestを再生成した。別担当の生成器検証は213項目を通過し、43抽出範囲を別に走査して照合した。Markdownのコードフェンス内の見出しを節境界として誤認する問題も修正した。最後の生成で変わったのは研究README全体のhashで、6束の本文は直前の内容確認版と同一。生成検査は内容の有用性・科学的妥当性の証拠とは分ける。

PLANの原稿MDを固定し、独立コピーでTeX/PDFを再生成。担当は30頁を110 dpiで全頁視認し、主担当も物理頁1〜3・26〜29の表紙/目次/位置づけ/研究方針/再開手順を確認した。文字欠け・表のはみ出しは見つからなかった。TeXとPDFを対で採用し、MDは前後同hash。初回のsandbox生成はログ書込み・一時ファイル後処理で失敗し、同じ許可範囲を生成コピーで再試行して成功。原出典の科学的再検証、実機印刷は含まない。詳細はP420/plan-build-02/logs/qa.json・receipt.json。

0.41で成功した430回帰について、対象コード/検査/原資料/fixture等54パスが当時・C2・現在で同hashであることを再照合した。430を今回実行済みとは数えない。管理5検査とGit保存は、この生成確認の後に実行して結果を追記する。

管理01ではhealth・現行/固定旧contract・生成一致が成功、stateは初読批評の一時ファイルの配置とHTML末尾の旧版表示を検出した。初読原票を同hashのままP420/reader-first.mdへ移し、末尾を0.42へ訂正した。state再検査は1,949項目で成功。検査器・登録範囲を緩めず、最終管理5検査を再実行して保存票に結ぶ。

管理02はstate・health・現行/固定旧contract・生成一致の5件が成功し、前後131実体は不変だった。

初回の保存freezeは元local.gitの全体指紋がP410当時と異なるため、manifest作成・Git書込み・push前に停止した。現在878ファイルを複数回・別列挙で読み、指紋 `42ad1942588036f9ffda1e02b4db3edf48d5eba6b28a2201ee069fc868c4af8c` が一致した。HEAD/mainはM101、refs/index/reflogの更新時刻は本ターンより前。前回保存後のmtimeを持つ現101ファイルは全てobjects/で、本作業開始直後の19:52:25〜27 UTCに集中するが、書込主体は特定していない。旧時点のpath別指紋がなく、過去からの全体不変や「追加だけ」とは断定しない。

これは元.gitを修復・削除・巻戻す理由にしない。主担当は上記の現物を明示的に固定し、外部bareからの保存の前後で全878実体とM101が同一であることを要求する限定継続を決めた。次の不一致を自動で基準更新する処理は入れない。旧不一致の観測・元全path指紋・採否はP420/original-git-observed.json、original-git-reconciliation.jsonへ保持し、本段落にも未説明範囲を残す。元Gitの変更とGitHub作業branchへの保存を混同しない。

### 0.42の保存と固定読戻し

2026-09-27 UTC、C2を親に内容C3 `f0a589ea94beb0e804920a5ffe73dc7937138b3c`、tree `e32ee02d4bd77e201ebaae09052d13e762fb2079` を同branch/Draft PR29へ保存した。GitHub固定commit/treeと全131のpath・mode・size・Git blobを照合し、保持した全131のローカルSHA-256も一致。main M401不変、PR29 open/draft/未mergeを確認。M401から40差分（23更新・17追加、削除0）、C2から34差分。管理03はstate 1,950・health 4,355・現行/固定旧contract各3,632項目と7生成物一致が成功し、前後131不変だった。

保存時のsandbox内Gitはls-remoteで終了128となり、書込み前に停止。同じ限定操作を通常権限で再試行して成功した。元.gitは上段で明示固定した現878実体が保存前後に同一だった。P410当時からの全面不変という主張はしていない。固定照合の証拠はP420/save-receipt420.json・C3-fixed-readback.json・C3-remote-commit/tree/main/pr.json。PRの題名/本文を0.42の全体文脈・批評・研究依頼と限界へ更新した。

Codexはこの実績を本書/S35/VERSION_HISTORYへ戻し、記録差分だけをC3の子として同PRへ保存し、管理5検査と全131照合を行う。記録commit自身のSHAはPR本文と外側のreceipt/readbackへ置き、自己SHA追記の無限循環を作らない。人間は研究入口とQ420-00の内容をレビューし、受入/統合後にGitコピーと指定原資料をChatへ渡す。研究回答はまだ0件。回答を受けた後、Codexが出典・現行差・具体的な効果を検討して設計と採否へ戻す。

## RPT-067：全体の設計判断とChatへの研究依頼を継続可能にする

2026-09-28受領。ユーザーは模型中心の作業から、プロジェクトの文書可用性、入力/モデル/MC/設定とproject保存/画面間接続/FE-BEを横断する設計へ重心を移すよう求めた。Chatへ調査・議論の課題と必要資料を渡し、人間が今回PR統合後のGitコピーを受け渡す。Codexは主担当として設計・実装・統合を進め、自己批評と別視点の批評を継続する。モデル名・利用枠はユーザーの申告であり、無制限利用を技術前提として保証しない。

提供PDFは[feedback_v_0_40_1.pdf](references/user_supplied/feedback_v_0_40_1.pdf)、検索補助は同名txt。4頁を本文抽出とページ描画で読んだ。中心＋東西/南北距離の範囲、モデルごとの最小入力と製品/補助計算の経路、元量の分布と従属量、分布診断、projectと画面連携、ERA/JRA選択と過去予報比較、二台での計算分担が設計論点である。製品表の±を標準偏差と解釈せず、Excel画像を科学的正解として採用しない。資料内の案は議論材料であり、現在の直接指示とは分ける。

## AUD-410：既知の情報を、未決の設計へ結び直す

GitHubからmain M401 `55100867df2bef615c3131228c7c75adf31c9833`、tree `99291719395a1e1517e0676dc96bd14dd8f3f246`を固定取得。PR28のmerged=trueと両親M390/C401を確認し、ローカル全114のblob/sizeを照合して不一致0。比較用一式をrepo外の `Temp/balloon-design-410/basis-M401` に保全した。元local.gitはM101であり作業本文の版とは別。

独立監査は、接続設計の入力三経路、元量標本、階層重み、結果と分析版、jobの境界を有効な足場と認めた。一方、現在入口がhover修復で占有され、VISIONの旧Dash/実装待ち、CONTEXTのworkflow390、U-007/008等のS32案内、Excel付属物未提供という旧Project索引が後継を示さず残っていた。単に資料がないと判断して再発明せず、現在案内と当時の根拠を分けて修復する。未決が変える入力・標本・保存・分析の境界へ既存情報を集める。独立批評は全科学文献や全旧実験の再実行ではない。

OpenAI公式の[Projects and chats](https://learn.chatgpt.com/docs/projects)を2026-09-28に取得。ChatGPT Projectへは必要なsourceをアップロード/接続するという説明を、課題別抜粋を渡す設計の根拠にした。今回のChatの具体的モデル、ファイル処理、検索能力、料金枠は実行して確認していない。Chat側には読めた本文と不足を最初に返してもらい、画面操作やローカル実測を成功と推定させない。

## ACT-410：利用の行程から反例を作り、研究の受渡しを具体化する

0.41候補を、入力・保存の設計、情報の可用性、Chat研究の3担当で独立に読み、主担当が相互に批評を依頼した。重要だったのは欄の充足ではなく、同じ計画を冬の季節選定→予報→run更新→充填済み延期→飛行後まで動かす想定である。良いように見える局所設計が、次の操作で意味を失わないかを問うことで、次を修正した。

| 反例・不足 | 設計と運用に戻した変更 | 未確認の範囲 |
|---|---|---|
| 先に終了したMCだけの雲は、長い飛行を選別し得る | 標本ID・重みを先に決めた小バッチ完了単位を検証候補にし、全体待ちの代案も保持 | 実装・遅延費用・統計手法の採用は後続 |
| 同seed、新旧runの同member番号では、同じ実量の比較にならない | 実量固定・共通分位・対応不能を区別し、共有量と変更軸を保存する | 較正・結合方式は研究課題 |
| 直接率のCVを、製品導出や非線形なCdA換算へコピーすると別の分布になる | 不活性の控え、結合標本からの変換、代表値だけの換算と分布再指定を区別 | 補助式と母数の科学採用は未了 |
| 親編集を延期子へ黙って反映すると、時刻だけの比較が崩れる | 系列を明示更新し、変更対象・未反映・独立案化を既存VISIONと整合 | 実入力画面の評価は後続 |
| 保存図が最新の候補・製品・禁止領域へ付け替わる | 草案、固定実行、標本結果、判定/集計、保存図を別の参照として追えるようにする | 最終schema/DB/API・別PC実行は未実装 |
| 現在案内に旧計画が残り、次の担当が過去の順序へ戻る | CONTEXT/VISION/PLAN/課題索引を修復。手順はS35をS34の後へ追加。共通履歴注の現在先を恒常的なstartへ変更 | 過去の全科学的主張を再受入したものではない |

研究課題Q410-01〜05は、答えで変える設計、初回範囲、比較候補、実読箇所、成果と停止目安を持つ。5資料束とmanifestを生成し、元パス・選択範囲・本文hashを結ぶ。単なるGitパス一覧にせず必要本文を含め、未同梱の原資料を区別した。共通入口のQ410-01例が他課題を上書きしないよう汎用開始文と担当ID表示へ修正した。返却原文の保管、基準差の照合、採否と担当本文への戻し先を指定した。全課題は未発行・回答0件で、実Chatの読取・返却成功はU-022として残す。

生成器の反例試験10件で、節の切出し、欠落/重複見出しの拒否、repo外参照の拒否、SVG代替説明/後続本文/表セル、同一生成、課題識別/追加資料、元変更への追従、既存出力への上書き拒否、古い束の不合格を確認した。初回fixtureはWindowsの一時ディレクトリへの書込制約で失敗し、削除せず保持。repo外の用途を固定した新規fixtureで再実行した。これはChatの実受渡し検査ではない。配布前の `tools/build_research_packet.py --check` を研究入口へ明記する。

PLANは同じMDからTeX/PDFを独立生成。初回はXeLaTeX書込/cleanup失敗、2回目は出力cp932復号例外でログ不完全のため受入から除外。3回目はプロセス内だけPYTHONUTF8を設定してexit 0。全30頁を担当が110dpiで視認し、旧M401の変更部と比較、主担当も物理14/27〜30頁を確認した。文字欠け・表の見切れ・内容構造の欠落は見当たらない。PDF SHA256は `3d0e9a54c33ca7eced3b7d2272502466ed472f60a022594af4221f33308ca9b7`。科学再検証・実印刷の受入ではない。

外側の検査原票は `Temp/balloon-design-410/` の固定基準、packet-behavior-result.json、plan-build-01〜03と成功回のlogs/qa.jsonへ保持する。接続設計HTMLのfile URL表示はブラウザのURLポリシーで拒否されたため迂回せず、今回の実ブラウザ表示は未確認。本文・HTML構造の独立読取とPDFの視認を、ブラウザ上の操作確認へ読み替えない。既存Google接続に追加要求は行っていない。下記に今回の管理検査・標準回帰の結果を追記し、Git保存はS35の手順に従って固定読戻しまで続ける。

**主担当の自己評価：** 今回は、見えている画面の修正だけでなく、利用者の同じ検討が条件更新と保存を越えて続くことを軸に、情報・入力・実行・分析の境界を設計した。別担当の反例で、最初の案が見落とした分布切替と明示更新を改めており、批評を確認印のための工程にしなかった。依頼準備は研究の質や本体の成立をまだ証明しない。次は返却根拠と現入力の具体例を照合し、保存GFSの一経路で、今分けた責務が使い手の操作を支えるかを確かめる。

初見の資料束レビューで、Q410-01に当時の次作業を含むENVの旧節が抜かれていたことを検出した。元の正本に時点区別があっても、抜粋で親見出しが落ちれば誤読するため、現ENV-CURRENT内のモデル境界と一標本入力の2節へ差し替えて再生成した。模擬受領では、旧基準でも有効な指摘は現行差分と照合、保存方式の衝突は同じ利用例で代案比較、原典未読で平均径からSDを断定する回答は科学採用せず仮の感度条件と区別する手順を確認した。本物のChat回答は受け取っていない。

管理範囲の点検では、WG-DISPERSION-NEXTの開始位置が可変の確認版文字列そのものへ依存していた。固定コメント境界へ移し、既存のschema/検査器・期限を変えずに本文と限定確認の意味を保持した。過去の実験や旧管理合格を今回再実施した記録へ変更しない。

Q410-02〜04も別担当が資料束だけで読み、Q02のVISION抜粋に残る「現在は保留」を0.29/0.31当時の順序として明示し直した。管理初回は127実体不変のまま不合格を返し、S35内の見出しの役割、資料束の相対リンク、提供PDFの原本宣言、既存lifecycle列挙と確認日のUTC/JST区別を修正した。相対リンクは注記で原パスへ戻らせるだけではGit内でクリックできず、生成器が資料束の位置へ変換する方式へ改めた。節内リンクと外部URLを含む3反例を加えた13件は合格。本文日付はJST9月28日、確認票の日付は実時刻のUTC9月27日として記録する。検査器を改変して失敗を免除していない。

### 0.41保存前の検査結果

management-02ではstate/health/現行と固定M401のcontract（transition/base指定）、5資料束の生成一致が全て成功し、127登録実体は検査前後不変。version-ageの158助言を残し、未読の一括確認や検査器/期限の緩和は行っていない。全430回帰は534.209秒、失敗/エラー/skip 0で成功し、前後127実体が不変だった（regression-01/receipt.json・hashes.json・原stdout/stderr）。追加した生成器は別の13反例で評価した。

最終独立読者はREADME→研究入口→Q410-01/課題/返却形式を読み、最初の具体行動・目的・提出物・M401と未来統合SHA・本体と構想・未発行と未採用を区別できた。主要導線と抜粋の一致を確認し、初回を妨げる重大残件は見つからなかった（final-reader-entry-q01.md）。実Chatでの添付・読取・研究・返却は未実施である。

この後の追記はS35/REFSと管理/版履歴の記録範囲に限定し、試験済み本体・生成器・研究本文/束・PDFを変えない。全127指紋を回帰時点と比較し、管理検査を再実行してから保存する。Gitへの保存成功は次の実績欄へ事実取得後に記録する。

### 0.41の保存・固定読戻し

管理03は全5成功・前後127不変。回帰以降の差分はRB/REFS/HEALTHの記録3パスだけで、本体・試験ソース・生成器・研究本文/束・PLAN/PDFは回帰時のまま。初回Git操作はls-remote時にsandboxで認証helperのsignal pipe作成がWin32 error 5となり、外側bare・commit・remote更新の前に停止した。同じ限定保存を通常権限で再実行し、新branchへのC1保存が成功。既存branchの置換やmainへの書込みを許可へ含めていない。

2026-09-27 19:29:52 UTCにDraft PR #29（https://github.com/GENIANY/space-balloon-simulator-jp/pull/29）を作成。C1 `6156f88454c0f7362a3f99e1390463cc0e7fcb87`、親M401 `55100867df2bef615c3131228c7c75adf31c9833`、tree `a4c01943c56670cca2b4f194b470f8f0a6003bdc`。23既存更新・13追加、削除/改名0。GitHub固定GETの全127 blob/mode/size、commitの親/tree、PR head/base/Draft、main不変を独立照合した（C1-fixed-readback.json）。元local.gitはM101・全内部ファイル指紋不変。継続許可内の保存であり、人間のmain統合は未実施。

この実績を含む記録差分を同PRのC2へ保存し、同じ全127固定読戻しを行う。最終head自身・最終検査と照合結果はPR本文と外側record-receipt.json / C2-fixed-readback.jsonへ置く。研究資料/コード等が変わらなければ全430を反復せず、回帰以後の差分が6記録パス以内であることと管理検査を確認する。実Chat研究は未発行/未受領で、S35の依頼準備と保存は完了したが、統合後の人間の開始操作とCodexの受領点検へ継続する。管理04は子手順のないS35へのpartial指定を不合格としたため、子手順を水増しせずdoingのまま本文で完了範囲を示した。元の不合格と判定規則を保持する。

## 0.40.1時点の参照先：RPT-066続報 / ACT-401-R2

現在は0.40.1訂正候補r2の限定再評価後。2D復帰の反証と当時の完成判定撤回を保持し、地図へ戻って比較を続ける行程の再確認を根拠に管理検査・同PR保存の準備へ進む。現在案VISION workflow401、採否D179追記、行動・適用host・次担当はS34#s34-401-r2-reviewと後続の保存前手順。比較元はPR28のC2、main/PR baseはM390。P400はTemp/balloon-design-400、追加証拠はそのphoto-followup400。旧9模型ZIPと原Excel資料を保持する。

## AUD-401：固定C2から名称識別の訂正を評価する

局所比較はPR28/C2 `f6dbf6d54de252d63b586beeecc1962926aa6dd4`、main/PR baseはM390 `7622593e0d4dacb101f9ed86990f2832845494ed`。固定113実体と0.40 ZIPの照合はphoto-followup400/base401-receipt.jsonとmanifest-C2へ結ぶ。旧0.40の人工検査・回帰・Git保存の事実を保持し、それを新修復版の成功へ移さない。今回の限定読取と批評、変更source、未検証範囲を新archive832memberへ収録し、全memberを照合した。ZIPのSHA256は `944d664adbd8a8a91fb6cb81095f48fee00b189e12a62fa36ffa79720b3ef8da`。

## ACT-401：実写真の反例から描画と位置読取りを分離する

ユーザーの実マウス報告と主担当の同一位置診断をS34へ記録した。公開APIによる再描画の有無を比較する診断と、描画完了までの競合を制御する恒久案を区別する。恒久401 hostの実写真で、利用者が青/赤の面を交互に指して継続表示と同名反復の解消を確認した。主担当は57表示要素、クリック50%内、2D往復後の接続試行表示1回を確認した。独立生成は400条件成功、scene3d417member差分0。実写真の穴・非表示・全機器を網羅した結果ではない。記録はphoto-followup400/verified-host401.json、独立生成票、naming-proposal/review-naming401.mdへ結ぶ。局所診断を終了して元API/配信overlayを復元した。生成ZIP・管理検査・回帰・保存の実値は実行後にS34へ戻す。以下の0.40の未確認や保存時点は、その当時の記録として保持する。

## ACT-401-RETURN：2D復帰の反証と保存停止

面内名称の継続表示、同名反復の解消、3D再開後の57要素/接続試行1という先の観察は保持する。ただしそれは2D背景の連続性・縮尺・輪郭との位置整合・pan/zoomを確認した票ではなかった。利用者の追報と主担当の同じ接続タブの観察で、2D復帰時のタイル分断を確認した。tile画像は256pxで取得済みだが、Leaflet pane/tileはposition:static、mapはoverflow:visible。同版の新規未接続タブではabsolute/hiddenで地図が連続した。必須CSS未適用の状態を根拠に調査するが、発生時点・原因、3D closeとの因果は未確定である。

根拠はphoto-followup400/2d-failure401.jsonとroundtrip-release-critique401.md、行動はS34#s34-401-2d-failure。直前の832member/SHA256 `944d664adbd8a8a91fb6cb81095f48fee00b189e12a62fa36ffa79720b3ef8da` は反証前の未受入候補として保持し、全member照合を受入成功へ読み替えない。superseded401-r1へのbyte不変保全を確認済みで、登録パスを後続訂正候補へ置換する計画とし、新候補の件数/hash/最終QAは未確定。code/ZIPを変える修復なので、回帰後の記録だけを追記する経路では閉じない。確定した修復source/ZIPへ必要な検証を結び直す。

## ACT-401-R2：戻った地図で比較と分析を続ける有限確認

主担当は別host `http://127.0.0.1:8402/forecast/` の接続tab14で、3D→2Dを3回確認した。AからBへの候補変更、2D写真への背景切替、地図領域の高さ883→763、3D側でのA非表示が2Dへ反映される場面を含む。復帰した2Dの地物は連続し、pan/zoomが正常だった。Bの詳細で60着地から干渉3本の図を表示し、共有地図へ戻るところまで継続できた。接続試行表示は1を保持した。表示の回数をGoogle側の課金・無料残量へ読み替えない。ブラウザviewport操作は実寸1641×1270を変えず解除したため、地図領域の高さ変更と「3D中のウィンドウサイズ変更」を区別し、後者は未確認とする。

別の人工labではCSSをdisabledにした故障を自動1回の再取得で復旧し、center/zoomを保持した。実paneだけのstatic、実mapだけのoverflow異常をそれぞれ検出して地図を隔離し、その後に自動再取得を増やさなかった。再取得計3回（自動1回＋手動2回）でも競合中は失敗を保持し、故障解除後には復帰した。これらは人工故障の実画面観察であり、元のCSS異常の発生原因・時点を解明したものではない。担当の17ケース・104 assertionはDOM/computed等をmockにしたunit試験の結果で、人工lab視認、接続hostの地理表示、標準回帰430とは別の証拠である。

局所名称の成功と3D接続維持だけを全体へ拡張した反省から、今回の採否は「戻った後に利用者の比較・分析が続くか」を軸にした。原観察・失敗票・旧832候補は保持する。この有限再評価で管理検査と同PR保存の準備へ進むが、全端末/全地形、未達の窓寸法変更、科学的干渉の受入へ広げない。r2 ZIPは858ファイル、19,220,587 bytes、SHA256 `8356df3cc8f2184d5418fe3d84d1e1d274b7646f3b81be6210c07094b3d7a214` で、全memberのCRC/size/SHAを照合した。旧9ZIPとscene3dの417実体は不変。旧r1の832内容は826共通＋6旧ファイル（161,746 bytes）から復旧し、全path/size/SHAが一致した。元ZIPbyteを再現した保証ではなく、その原ZIPの外部保全は保持する。このr2評価時点では標準回帰・最終管理検査・Git保存は未実施であった。後続の実績は直後の回帰記録とS34へ戻す。行程・採否・実行前手順はS34#s34-401-r2-review、s34-401-r2-save-planへ戻る。根拠はphoto-followup400のverified-return402.json、package401.json、r1-restoration402.json、map-return-proposalの限定試験票、map-return-independent-critique401.mdに方法別に結ぶ。8402で新たに物理マウスhoverを確認したとは記さず、8401の利用者報告とscene3dのbyte不変を分けて保持する。

### r2回帰の失敗・現在参照の訂正

r2凍結候補の標準回帰attempt-01は一時フォルダーのWinError 5等で450 error・終了1。入力114を変えず通常権限で行ったattempt-02は430件616.281秒、失敗1・error/skip 0、114全hash不変。残る1件はENTRYの今回の点検根拠REV-401-WORKFLOWに対し、README表示が旧REV-400-WORKFLOWのままなので、存在しない根拠番号へ置換する異常系が対象を変えられないものだった。AGENTS/CONTEXT/REFSの現在先頭にも同じ旧参照が残っていた。主担当の更新漏れとして、実読済みの今回の根拠へ現在4参照を揃える。旧期間の根拠や検査器・試験・模型ZIPは変更せず、metadataを整合して凍結し直した候補へ同じ430をattempt-03として実行する。成功は実行後に別記する。原票はphoto-followup400/save401/regression-C401-01,02に保持。

### r2凍結候補の標準回帰と記録を閉じる位置

現在4文書の点検根拠参照を訂正して凍結し直した標準回帰attempt-03は430件を596.159秒で実行し、失敗・error・skip 0、終了0。実行中の114登録実体は全hash不変。初回attempt-01の一時領域アクセス拒否450 errorと、同じ入力で行ったattempt-02の根拠ID不一致1失敗は原ログを保持する。03は検査器・試験・模型ZIPを変えず、記録の参照を直した新入力での全体再実行であり、過去の成功部分の合算ではない。

これは回帰時点の114実体についての結果である。後続はS34の事前手順どおり6記録以内の実績・来歴と対応する派生指紋だけを更新し、残る108の完全不変と実diffの意味を照合する。最終114の管理4検査・C2直子の同PR28保存・固定読戻しは後続で実行し、最終結果と自己SHAは外側受領票およびPR本文へ記す。最終文書で430を再実行したとは称さず、UIの有限確認や科学的採用の境界も広げない。

原票はphoto-followup400/save401/regression-C401-01,02,03のreceipt.json・stdout.txt・stderr.txt・tested-hashes.jsonとrecord-snapshot。参照不一致の独立批評はregression-failure401-review.md、失敗1件の訂正後確認はsave401/inline-evidence-recheck.stderr。最終管理票はsave401/validation-C401-02、保存はsave401/C401-git-receipt.json、固定照合はsave401/readback-C401-01を参照する。これら後続票の成功を本追記時点で先取りしない。

## AUD-400：固定基準と文書責務の再点検

PR27は2026-09-27T02:16:09Zに人間が統合。M390 `7622593e0d4dacb101f9ed86990f2832845494ed`、tree `090a1620d46bb05e4fffdb933d6d64cd93ff8186`、親M380/C2-390を取得し、全108登録パスのmode/size/Git blob/SHA256をbase-0.39.0へ照合。元local.git M101は切り替えない。新branch codex/ui400-hover-backend-designを使う。

README R0–R5/適用AGENTS、CONTEXT1–3/方向、MAP依存、DC-JUDGMENTとSTART/READ/INDEX/RECOVERY/NARRATIVE/FRACTAL/CLOSE/CHANGE、PLANの位置づけ/工程、ENVの現行/分散/モデル、気象ガイドの用途/時刻/後続案を担当別に読んだ。独立文書監査は本体20モジュールの索引指紋全一致と17 API照合の既存試験1件成功を確認。PROGRAM/THEORY/COMMANDS等の現実装内容を新機能へ改版する必要はないが、PLAN/ENV/WGの古い次案内、VISIONの保存予定表示は漏れだった。新規の科学式全面検証や旧全PDFの再描画とは区別する。詳細読取範囲と反証は新模型ZIP review/evidence/doc-audit400.md。

## ACT-400：実物・反例・原資料をつなぐ

feedback_v_0_39_0.pdfは全4頁を抽出・描画して読み、元量/分布・領域と支持・三用途・保存/実行の違いへ整理。Excel分析6HTMLと完全原ZIPは別担当が原本・170ファイル・相対依存・既知資料hashを照合。原ZIPはreferences/user_supplied/excel_analysis_20260920.zip、来歴と科学的未確認はEXCEL_ANALYSIS_REVIEW/manifestへ置く。係数や文献の再採用ではない。

名称hoverは表示中の少数対象だけを候補/領域ごとに識別し、画面入力の所有側で静止・移動・更新を制御する。主担当2Dと独立3D実装に対して担当を替えて反例批評を行い、2D移動/ズーム重複、既存tooltipとの衝突、境界だけ表示、長名の末尾切落しを修復。人工試験と実Google観察の範囲はS34末尾へ記録する。ユーザーが接続したGoogleタブを維持し、値を読出し/保存しない。

接続設計の初稿には元量を独立量と呼ぶ曖昧さ、同一IDだけの対照、分析版と履歴保持の不足があり、独立批評から具体入力3経路・遅延充填の反例・長期重み例・保存参照図へ修正する。根拠は既存ENV/D167/168と実config/models/records。FastAPI公式BackgroundTasks/deployment、Python concurrent.futures公式を参照し、重いCPU計算・workerメモリ・取消の限界を案へ反映する。フレームワーク選択は試作案で性能実証ではない。

PLANは専用の既存Pandoc/XeLaTeXから独立copyで生成。最初はsandbox一時dirのアクセス拒否、同じ生成器を通常権限で再実行して成功した。初版28頁で見出しと表の分離が見つかり、既存titlesecの見出し下の確保量だけを調整して29頁へ修復。新依存・固定ページ改行なし。担当が全29頁を視認、rootが新工程表等の該当頁を再読した。元科学本文を改訂した判断ではない。生成src/失敗/成功/画像の有限証拠はP400/plan-build、要約は新ZIP review/evidence/docs-repair400.mdへ。

hover r3は340条件と独立再生成418ファイルのbyte一致を確認。人工WebGLの旧gate失敗→world姿勢の累積有意差への修正後、候補/領域2名、穴、drag退避を実描画で観察。2D最終forecastの合成入力でもA標準案の名前を地図上に視認。CUAに物理mousemove操作がないため、合成入力と実mesh/表示の有限検査であり物理マウス全操作ではない。ユーザーが接続したGoogleタブはr2を維持し、配布r3の写真上hoverは次の正規host起動で確認する。接続維持と新版の実観察を混同しない。

管理検査とGit保存の実績は実行後に追記する。以下の0.39以前は当時の観察であり、当時の次を現在へ移さない。

模型収録実績：新ZIPは17,844,971 bytes / 804 member / SHA256 d253aa5d5857671dd0793ea04d9715c697526bd0cad55cfd1ef2ac72d0ab7f30。CRC・各member size/SHA256照合、旧8ZIP不変を確認。P400/metadata/package400.json。限定パターンの秘密検査は一致なしだが全秘密の検出保証ではなく、そもそもGoogleキー/通信/タイルを採取していない。後続の批評読戻し・最終管理/Git実績はS34と本節へ戻す。

初回の管理検査C1-preflightはhealth成功（4054）だったが、state/現・固定旧contractは新5実体がCURRENT_PATHSにないと拒否した。登録JSON/派生asset表だけを追加し正本パス列挙を更新し忘れた主担当の仕上げ漏れである。CONTENT_MAPの宣言へ新5pathを加えて113とし、検査器は変更しない。失敗原票はP400/validation-C1-preflightに保持し、修復後の別票へつなぐ。

### 凍結候補の回帰と新Draft PR保存

標準回帰attempt-02は430件594.734秒、失敗/error/skip 0、113登録ファイルを含む検査対象は前後不変。初回attempt-01は試験用TempへのWinError 5を含む450 errorで失敗し、同じ試験を通常権限で再実行した。state1295/health4054/現・固定旧contract各2813成功。初回のCURRENT_PATHS新5path漏れも修復し失敗票を保持。確認印の更新は85scopeに限定し、非選択169scopeの版差注意は旧科学・原本・実装不変の責務と未確認を理由付きで据え置く。期限/版差は全体査読済みへ自動変換しない。

C1 `329c98f8cb7219751de5db92d30cf974b5f01d13`（唯一の親M390 `7622593e0d4dacb101f9ed86990f2832845494ed`、tree `b724f56d6c629ce1527348ba605ede0ad05ecb4f`）をcodex/ui400-hover-backend-designへ保存し、[Draft PR #28](https://github.com/GENIANY/space-balloon-simulator-jp/pull/28)を作成した。2026-09-27T10:58:59.787477+00:00に113全pathのmode/size/Git blob、commitの親/tree、PR head/base、privateの同一repo、Draft/open/unmergedとmain M390不変を照合。元local.gitはC1保存の直前直後で全file指紋が一致しHEAD M101を保持。mainへの直接書込・mergeは行わない。

Gitの初回ls-remoteも制限環境のWin32 error 5で停止した。同じ保存処理を通常権限で再実行し、既存認証で保存した。認証値の取得・別経路への変更はしていない。この結果をC2で同じPRへ追記する。C2は記録/管理6path以内とし、標準回帰で確認した本体・模型・生成PDFを変えない。最終自己SHAを入れるためだけの再帰commitは作らず、最終SHA/固定照合はPR本文と外側受領票へ置く。原票はP400/metadata/regression400/attempt-01,02、validation-C1-preflight,C1-final、C1-git-receipt.json/C1-fixed-readback.json。外側票が失われたとき、固定Gitからの再検査は過去の原実行票の復元とは区別する。

## AUD-390：統合済みmainから開始する

PR26は2026-09-26T13:04:11Zに人間が統合済み。main M380 `19bf0cc5cd32509a44ca8e246f4294ab0972d61e`、tree `c6cf7f6e6a0b2b0deff1b368a3b136cee069445f`、親M350/C2-380を実取得。固定107実体をmode/size/Git blob/SHA256で照合しP390/base-0.38.0へ保存した。元local.git HEAD=M101を保持。0.39はcodex/ui390-context-exportを新規作成する計画で、統合済みPR26を再利用しない。P390はTemp/balloon-design-390。

## ACT-390：同じ対象を読む・比べる・保存する

原PDF feedback_v_0_38_0.pdfは4ページ870248 bytes、SHA256 `af8228f0ce1fa57bb312081fe56137e80c4e501d1a3faaff07895c887531ee1a`。主担当と独立担当が全頁・本文を読んだ。資料内の具体案は設計材料として扱い、一括命令/許可にしない。長い批評循環・一接続の十分な利用は直接要求として別に受理した。

三担当の初期案、担当交換の反例、主担当CUAの人工3D・KML reader・風SVG実読から、表示対象と結果identityを分けた。全目録KML、排他帯、候補/領域の色、来向円環を改訂。失敗時の図形と説明の不一致、入力未反映の欠落、平均風が0の時の偽北、保存SVGの初期縮小等を修復した。新ZIPのreview/evidenceに各巡を保持する。source検査は予報32、3D最終r8 179、局所入力の独立21、風33。各対象だけを表し、GUI/科学の証明ではない。

同じGoogle接続で屋根上のA 50%内/B 95%外、視点を保つ候補比較、干渉28/60の2D往復を確認した。詳細の無効checkboxは選択数を示す静的カードへ修復し、表示だけの更新でも同じ接続を保った。 同コードの新しい無キーIABタブでは実UIからJSON 747 bytes、KML 133470/381012 bytesが保存され、実ファイルの複製一致と別readerの55要素/可視43、209要素/可視120を確認した。後者は非表示A親・表示+30/+60子・B・二つの領域を保持する。旧タブで未到達だった内部原因は未特定であり、全環境の保存保証にはしない。 風SVGは実保存と単独表示を確認済み。最終r8 sourceからruntime411件+inventoryがbyte一致した（scene-rebuild390-r8.json）。初回167条件の記録も保持する。詳細はroot-design390.mdと担当票へ。Google Earth、全マウス操作、実気象MC、本体/科学の受入は残る。管理検査とGit保存は実施後に追記する。

名称hoverは初期設計案を置いたが、今回模型では未実装。まず表示中の分位面と禁止領域の面に絞り、候補名一つ・領域名一つと追加件数を短く示す。静止後に表示し、移動・拡大・ドラッグ中は消し、クリックの地点読取・選択・判定を変えない。輪郭のみの別候補を識別できない反例と重複優先の妥当性は次の実物批評へ残す。入力は背景を所有する側で管理し、現在の接続へ表示部品から継ぎ足す実装は避ける。次の正規のhost更新で組み込む。

### 保存前の確認と残す境界

新ZIPは15,487,079 bytes、643メンバーのCRC/byte/hash照合済み。管理検査review2はstate1280/health3908/現・固定旧contract各2573成功、108実体は検査中不変。版差だけの注意182範囲は残し、変更/依存の実読63範囲以外へ確認印を広げない。旧理論・原本・科学的採用の再査読を今回行ったとはしない。

標準回帰attempt-01は一時フォルダー権限、attempt-02は編集中の不確定候補が混入して失敗した。凍結後のattempt-03は430件491.956秒、失敗1・error/skip 0、108実体不変。残存1件はREADMEの確認根拠が旧IDのままなので異常系テストが対象を置換できないことが原因だった。実読済み0.39の根拠へ入口4文書の参照を整合し、テスト/検査器を変えず再確認する。各原ログはP390/metadata/regression390へ保持する。最終回帰と保存の成功は実際の終了後に記録する。

配布review/index.htmlは1264×712で視認した。repoのSIMULATOR_VISION.htmlをfile URLで開く操作はブラウザURL方針に拒否され、同HTMLの今回レンダリングは未確認とする。本文/アンカー照合を表示品質の保証にしない。

### 最終候補の検査と新Draft PR保存

2026-09-26 15:15:22〜15:24:19 UTC、凍結した候補の標準回帰attempt-04は430件534.650秒、失敗/error/skip 0。108ファイル前後不変で、validation-C1-finalの検査時指紋と一致。固定M380の本体・試験・検査等47パスと旧7ZIPは同一。最終管理検査はstate1280/health3908/現・固定旧contract各2573成功。追加実績の見出しh3が手順見出しとして誤認される初回不整合も、既存記録と同じh4へ訂正し、失敗票を保持した。最終標準回帰はこの修復後の一runであり、以前の成功部分の合算ではない。

C1 `87a9afc836961a0a943c6434cb77a0b9e76d4c4a`（唯一の親M380 `19bf0cc5cd32509a44ca8e246f4294ab0972d61e`、tree `1a092b1670a802b67a99ff214c2d5e89ec016314`）をcodex/ui390-context-exportへ新規保存し、[Draft PR #27](https://github.com/GENIANY/space-balloon-simulator-jp/pull/27)を作成。2026-09-26T15:36:48.051634+00:00に固定commit/treeの108パスmode/size/Git blob、PR head、main、Draft/open/unmergedを読戻した。元.gitはC1保存操作の直前・直後で807ファイル/252097525 bytes、集約SHA256 98094b078594fdb9b218df45b44d444fcb47ba9a299e74b85f21fe9429f70bf6が一致し、HEADはM101。ただし0.38終了時の793ファイル/171198111 bytesとは異なる。変化は0.39保存補助準備前に既に存在し、主体・原因・個別差分は旧票から確定できないため、全期間の.git不変は主張しない。Git認証プロセスが制限内ではWin32 error 5となったため、継続許可内の同じ保護付きコマンドを通常権限で再実施した。別branchの上書き・main更新・認証値抽出は行っていない。PR作成の最初の呼出しは必須repository_full_name不足で未実行、構造化引数を訂正して一件だけ作成した。

この結果と次判断をC2へ追記し、同じPRの固定読戻しを行う。C2自身のSHAだけで再帰commitは作らず、最終SHAはPR本文と外側受領票へ置く。C2は記録・管理6パス以内とし、標準回帰で試験したコード/模型ZIPを変えない。原ログはP390/metadata/regression390/、管理票はvalidation-C1-final/、保存票はC1-git-receipt.json/C1-fixed-readback.json。外側原票が失われた場合は固定Git内容から再検査できるが、過去の実行票を復元したことにはしない。

以下の0.38以前は当時の観察であり、当時の「次」を現在へ移さない。

## AUD-380：保存済み0.37を比較元に固定する

0.37はC2-370 `2aa9ec781818c0a9b2dfe0f53309b4abf1711f60`、tree `053edc39850bd33e6dfd72733bddd451496c1ae4`、親C1-370 `5999774c23beabd53ea18d56ba7ceb8afd918d86`。2026-09-26T08:06:20.109439+00:00の全106パスmode/size/blob固定読戻し、PR26 Draft/open/unmerged、main M350不変を外側受領票から確認し、P380/base-0.37.0へ106実体を保全した。0.37の旧「次はC2保存」は当時の計画で、今回の開始位置へ戻さない。P380はTemp/balloon-design-380。元local.gitはM101のまま。

## ACT-380：実接続と費用の検査を分けて記録する

主担当はNavaraの地形drapeとGoogle meshの違い、公式Map Tiles/JS3D/Demo Keyの前提を調べ、独立批評の3利用場面へ戻った。既存APIを使うCesiumJS候補と薄いsnapshot境界を用い、独自shader・多engine製品化を先取りしない。独立批評/接続調査の全文と、sourceモック18条件の対象・結果・修復を読んだ。主担当のCUA実操作は新ZIP内root-live-observation380に記録する。

人間のローカルキー入力後、Google背景に2候補21地物、詳細60/60着地68地物、海上多角形選択0/60の6参照地物を表示し、接続試行1のまま2Dへ帰還した。Google/Airbus帰属と近接地理を視認した。請求件数、無料枠残量、屋根/樹冠への線・面の全面追従、右ドラッグと全端末の用途受入は別。実Googleセッションと保存版gate/header/footerの無キー検査を区別する。APIキー・Googleタイル・HARを成果物へ含めない。

この段階は接続できる開発候補。キーのアプリ内参照解放とGoogle Cloud側無効化は別で、人間の無効化確認は未取得。保存と固定読戻しは後続実績を参照する。科学モデル・本体・ガイド・検査器は変更しない。

### 目的の再評価と終了処理

独立批評を受け、人工禁止領域2つを実Googleへ追加してA28/B3干渉、2候補55表示要素を確認。道路/林縁/畑/建物に対する赤境界の内外、面OFFによる写真の見直しは有用だった。細い輪郭の背景埋没と局所復帰の不便を修復へ戻し、視点identityが同じ地上群を過剰に分ける反例も再修正する。実キー試用は接続試行1のまま解除し、背景消失/未接続案内を視認。Cloud側の無効化は人間の完了報告待ち。

人工fixtureは黒表示の原因（最上位geometricError=0によるCesium選択省略）を修復し、主担当が屋根/段差・3輪郭・経路・穴つき面・5点を視認した。実写真meshの細部評価と分ける。検査準備でrootの保存がRUNBOOK等をCRLFへ変え歴史scopeに偽差分を生んだことを独立inspectが検出し、基準LFへ戻した。古い範囲の確認印を上げて隠していない。

### 最終修復の観察範囲

輪郭縁取り・意味的な視点記憶/復帰・地図外の工具帯を最終人工試験1280×720で視認。独立配置批評16状態で接続増加抑止と失敗時の回復を確認した。通常タブ再読込後の再観察ではGoogle接続1の状態であったため、開始主体を推測せず同じ接続で最終配置の記憶→zoom→復帰（1656×1270、2候補21要素、禁止領域なし）だけを追加確認し解除した。各画面内1は累積利用数や請求数でない。初回旧moduleの領域/詳細観察、最終人工地形、最終Google概要の帰属をroot-live-observation380.mdで区別する。Cloud側失効は未確認。

### 封入した実体（Git保存前）

`references/design_trials/photoreal_connection_038.zip`：510 members / 11,279,467 bytes / SHA256 `10b0c1ac4aa83eafb90ce8c625dba766f7b98d58ac5f466d764923b6df5d6134`。CRC・全memberのbytes/SHA256一致、旧6ZIP不変、模型5HTMLの相対18リンク欠損0。sourceと別ディレクトリ再生成runtime409ファイルも一致。P380/packagingのmember-manifest380.json・package-receipt380.json・link-preservation380.jsonと、ZIP内のcesium-rebuild380.jsonを参照。キー/Google取得タイルを封入していない。模型のGoogle利用実績とGit保存は別の段階として記録する。

### 管理検査の初回成功

管理検査はstate 1279件、health 3877件、contract-new/固定旧contract各2559件で終了0・error0。比較基準は未統合C2-370、観測main M350別。検査中107登録パスのSHA256不変を確認した。版齢注意180scopeは未読の印を上げて消していない。現在入口/設計/実績と依存旧本文の実読63scopeについて、root/forecast/extraの担当と限界を分けて確認記録を更新した。検査器・科学核・ガイドは変更せず、検査成功を用途や科学的受入の代用にしない。 P380/validation-C1-initial、metadata/metadata-review-receipt380.json・dependency-review380.md・final-record-critique380.mdを参照。本文へ実績を戻した後に保存対象と同じ107指紋で最終検査する。

### 0.38 C1保存と固定読戻し

2026-09-26T09:30:03.182765+00:00、0.38候補を既存branch codex/ui-needs-036 / Draft PR26へ追記保存した。C1-380 c2236ab210e4ae52e1d2684b7222c2996d446ab3、親C2-370 2aa9ec781818c0a9b2dfe0f53309b4abf1711f60、tree 5fd9f564b09217ce58578e95bfe0727e16df34f0。固定tree全107パスのmode/size/Git blobがmanifest-C1と一致し、PR head/Draft/open/unmerged、main M350 9b2feeb09626184caad07df89dc027a1afee6958 不変を確認した。

P380/git-saveの独立bareを使い、元local.git HEAD=M101および全.gitファイル指紋を前後比較して保持を確認した。既存106登録パスと旧6ZIPを保持し、写真3D接続模型/source/原要求/批評の1ZIPを追加した。科学核・ガイド・検査器はbyte不変。実接続・表示・科学的受入の結果は担当本文に記録し、Git保存から成功を推論しない。

この保存実績を同じbranch/PRへのC2で追記し、107パスを再照合する。C2自身のSHAはPR本文と外側受領票へ記録し、自己SHAだけの再帰commitは行わない。main統合は人間の判断とする。

初回のsandbox実行は既存認証補助のWin32 error 5でls-remote時点に停止した。自動承認レビューの拒否ではない。同じsave_git.py C1 --executeをrequire_escalatedで再試行し、既存認証と同じ保存先で成功した。資格情報の抽出/認証方式変更は行っていない。元.gitは793ファイル/171,198,111 bytes、全指紋1195a5fa4705d1f2026a1b6375f5e5bb998499cfef64da29e9732c7b09bbca5eを前後保持。 保存対象は14差分。P380/validation-C1-final/receipt.json、manifest-C1.json、C1-git-receipt.json、C1-fixed-readback.jsonを参照。最終C2の自己SHAと107パス照合はPR本文/外側票へ置く。

## AUD-370：未統合候補と目的を固定する

2026-09-26、PR26 open/Draft/unmerged、C2-360 `30c5126f6a44345f5d71fbc5b26af7caa2c293aa`、tree `68a81a8d594e2775b3f5a684c8aa27893dfc7b1c` を固定。main M350 `9b2feeb09626184caad07df89dc027a1afee6958` とは別。全104登録パスのblob/size一致をP370/base-0.36.0へ保存。P370=`C:/Users/genia/AppData/Local/Temp/balloon-design-370`。元local.gitはM101のまま。適用表示AGENTS0.35と作業C2-360の0.36を区別し、継続許可/規範に矛盾しないことを読んだ。

README R0–R5/AGENTS、DC-JUDGMENT/CHANGE/CLOSE、CONTEXT方向、PLAN位置づけ/9/10、VISION現在案/旧案/保存/三用途を読んだ。主担当はfeedback_v_0_35_0.pdf全4頁を本文と画像で確認。原本SHA256 `86c925b64e682e9b744bfed9f892bf21dcd1032c6f18b8d2be5783e2a72c6288`。文書内意見を実ユーザーの操作許可へ転用しない。風原資料の既存読取は後継記録へ戻り、今回主担当が全図を新規再検証したとはしない。

## ACT-370：独立批評と実物修復の循環

主担当は設計案と反対案をP370/design-round1、予報/気象/3D担当の自己評価、担当交換の独立批評、rootの暦/連続操作/3D実入力と文書批評を統合した。各巡全文と選定画像を読んだ範囲はroot-final370、依存点検はmetadata/dependency-review370へ記録。旧版・失敗・修復前画像を保持する。

原8768日時/風値の保持、400年4800月の暦包含、既知旧保存/未知規則拒否、気象→季節計画の14/15標本引継ぎ、写真上の停止×と線種/凡例、単独図保存を確認。3Dは概要2候補55地物、詳細3ID/0ID、実wheel/右drag、同じ2D状態への復帰を主担当が実行/視認。閉環、エラー上書き、出口色、候補色、地下突抜けと遠方喪失の反例を修復後に再確認した。全端末、科学モデル、Google建物/樹木mesh、高さ/衝突判定の受入ではない。

<!-- ACT370-CHECKS-BEGIN -->
管理検査（P370/validation-initial/receipt.json）はstate 1272件、health 3854件、contract-new 2564件、contract-old 2564件が終了0・error0。現行/固定C2-360検査器を変更せず、同じ固定baseに対するtransitionを検査。検査中の登録106パス不変を照合した。版齢注意は実読していない印の繰上げで消さず、科学/人間の採用へ拡張しない。比較基準C2-360は未統合で、観測main M350とは別。

実読・依存レビューは64 scopeについてA/B/rootの実読範囲を区別して統合した。RB-S14〜S33の24 scopeとS34の0.37以前48,360文字を固定原文へ照合。S34案内修復時に範囲指定を誤り一時削った歴史指示は固定原文から復元し、別担当が旧本文全体の完全一致を確認した。CSV担当列、旧現在案内、discussion310の欠落、冒頭の旧版/PR表示も修復。読んだscopeだけに確認を置き、45論証ID/旧104パス/四ZIP/本体/ガイド/検査器を保持した。

二資料のworkflow370/model-archive/start/受入節を1440×900と390×844で描画し、主担当が広幅の表と本文、狭幅の本文を視認。文書横はみ出しなし、狭幅の表は内部scroll。現行headerも修正後に視認した。模型5 HTMLの内部47リンク、RUNBOOK/VISION内部277リンクはfile/fragment欠損0。全頁印刷・外部リンク到達性・全端末を検査したとはしない。

最終ZIPはinteraction_workflow_037.zip: 166 members / 92,073,041 bytes / SHA256 f4e93e6e3fc8c7bc4dc1c7492a1250b1fd35fe9e7bd9ef0f0a17c3e564609c55；interaction_workflow_review_037.zip: 242 members / 100,527,680 bytes / SHA256 87bc7d2df10ec69afec5642e6e3080786d6997a979469aff1bf93a72a88668f8。両方のCRCと全member SHA256/bytesが一致し、同所展開で一つの証拠木へ復元する。初回封入後に文書依存レビューと表示証拠を追補した。ZIP内の初回指紋は当時のもの、最終指紋はこの記録と外側受領票を使う。二ZIPは100MiB未満、旧四ZIPは不変。再現source/lock/license、原意見、反対案、失敗と修復を保持し、人工模型の有限受入とGoogle/実気象MC/科学/人間採用を区別する。
<!-- ACT370-CHECKS-END -->
<!-- ACT370-SAVE-BEGIN -->
2026-09-26T07:55:28.396867+00:00、0.37候補を既存branch codex/ui-needs-036 / Draft PR26へ追記保存した。C1-370 5999774c23beabd53ea18d56ba7ceb8afd918d86、親C2-360 30c5126f6a44345f5d71fbc5b26af7caa2c293aa、tree 835def13a264b5d0c62c0ba0fe8248290bd13dbc。固定tree全106パスのmode/size/Git blobがmanifest-C1と一致し、PR head/Draft/open/unmerged、main M350 9b2feeb09626184caad07df89dc027a1afee6958 不変を確認した。

P370/git-saveの独立bareを使い、元local.git HEAD=M101および全.gitファイル指紋を前後比較して保持を確認した。既存104登録パスと旧4ZIPを保持し、新しい操作模型と批評の2ZIPを追加した。人工データの用途試験であり、科学核・ガイド・検査器はbyte不変、Google 3Dは未接続である。

この保存実績を同じbranch/PRへのC2で追記し、106パスを再照合する。C2自身のSHAはPR本文と外側受領票へ記録し、自己SHAだけの再帰commitは行わない。main統合は人間の判断とする。

初回はsandbox内のgit ls-remoteで認証補助のWin32 error 5によりcommit前に停止した。同じ認証・同じ操作をrequire_escalatedで再試行して成功し、自動承認の拒否や新しい人間承認待ちではない。通常ブランチの親C2-360へ追記するcommitのみを作り、expected-oldの照合で他のheadを上書きしない。元.gitは793ファイル/171,198,111 bytes、全指紋1195a5fa4705d1f2026a1b6375f5e5bb998499cfef64da29e9732c7b09bbca5eを前後で保持。

保存対象はC2-360から文書13件と新ZIP2件の15差分。C1直前の検査はvalidation-C1-finalに記録し、検査時106指紋と保存manifestを完全一致させた。PR26の題名/本文を0.37の比較と地理探索へ更新し、Draft/open/unmergedを応答で確認した。本文の旧計画を保存済み事実へ書換えず、この段に実績を追記した。
<!-- ACT370-SAVE-END -->

## AUD-360：main統合と設計資料を固定して読み直す

2026-09-26、PR25 merged、main M350 `9b2feeb09626184caad07df89dc027a1afee6958`、tree `80a0ef750694ea1830e526ad6799d148021ee005`、親M320/C2-350を実取得。全103登録パスのGit blob/sizeを照合してP360=`C:/Users/genia/AppData/Local/Temp/balloon-needs-360` のbase-0.35.0に固定した。元local.gitはM101不変。RPT-059への回答時にもmain/PRを再取得し同じ統合を確認した。

主担当の実読はREADME/AGENTSとDC-JUDGMENT/CHANGE/CLOSE、CONTEXTの方向、PLAN位置づけ/9/10、VISIONの現在案/比較/気象/過去/保存/構造。過去意見、長期用途/現コード、風原図は独立担当が範囲を記録して再読した。原PDFの実頁確認はreference担当であり主担当の全頁再読としない。各担当の未読・未検証をZIP内報告に残し、最新外部製品仕様や科学的採用を新規確認したとは扱わない。

## ACT-360：解釈を反証し、次の比較場面へ戻す

複数モデルの運用判断を狭めないという第一巡の仮説へ、現共有地図/件数で足りる第二巡の反証を戻した。機能欠落の断定を採らず、多数条件時の関係復元を後続場面にした。風原資料にも速さ幅0/地点R1/全域R0の反例を当てた。意見1は原PNGを無編集保存し、コードの480px上限と三指定viewportの初期画面を観察。実装は変更していない。画像からユーザーの画面全体を推定せず、背景を意図的に遮断した観察を地理表示の試験と混同しない。

<!-- ACT360-CHECKS-BEGIN -->
管理検査（P360/validation-initial-ready/receipt.json）はstate 1267、health 3819、現行contract 2525、固定0.35contract 2525が終了0・error0。検査器を変更せず、旧103登録と45論証IDを保持し、新しい調査ZIPだけを追加した104パスを点検した。版齢注意や未検証の科学範囲を、未読印の繰上げで消していない。依存点検は過去手順を再実行した意味ではない。

初回validation-initialではhealthが履歴DAGで停止した。M350の実親C2-350が旧VERSION_HISTORYへ未登録だったためで、GitHubから14f83fa5b2aa0585aff716c9e5afc19ee5e5bb4aと親C1-350/treeを固定GETして観測遷移を追加した。次の検査で判明した履歴表示行の40桁SHA省略も、編集元に合わせて訂正した。親関係を省略したり検査器を緩めたりせず、失敗した試行も保持する。未来の0.36保存を先取りした補完ではない。

三担当の読取と相互反証を主担当が統合し、主担当への再批評で指摘された過去飛行の弱まりと意見1の次作業の曖昧さを訂正して再確認した。全原資料/全実装の網羅監査ではなく、各報告に実読/未確認を持つ。原PDF指定9図と§3.1の実頁はreference担当が確認。高さ観察は3指定viewportで各480px、外部地図を遮断した配置試験。ユーザーの画面全体寸法や地理画像品質を推定しない。

VISIONの新規2節を1440/390pxで描画し、主担当が広幅の表と狭幅の本文を視認した。document横はみ出しなし、狭幅の表は内部スクロール。過去模型索引の内部24ファイル/7参照を存在照合したが全旧版の実操作再現ではない。原意見のPNGは無編集保存。調査ZIPは43実体・2734498 bytes、SHA256 3f0d87ba50aca175a1fbeafd116ba577a76d58676449b08c80d46002ff7bfc21、CRCと全member指紋を照合。旧三模型ZIP・本体・ガイド・検査器は固定M350とbyte不変。管理検査やファイル存在をUI修復・科学採用・人間の採用の証拠にはしない。
<!-- ACT360-CHECKS-END -->
<!-- ACT360-SAVE-BEGIN -->
2026-09-26T04:50:31.490552+00:00、0.36候補15差分をmain M350から新規branch codex/ui-needs-036 / Draft PR26へ保存した。C1-360 c87d9c29ad7b4d5c7c1101881a84e4dc5ca702ae、親 9b2feeb09626184caad07df89dc027a1afee6958、tree dad7603e3ee5fcd16908ed0e7673d682cf196495。GitHub固定treeの全104パスのmode/size/Git blobがmanifest-C1と一致。PR head/Draft/open/unmerged、main M350不変を確認した。mainへの書込み/マージは行っていない。

P360/git-saveの独立bare領域を用い、元local.git HEAD=M101とcheckoutを変更していない。初回はGit認証補助プロセスのsignal pipe作成がWin32 error 5で失敗し、ls-remote時点で停止した。同じ保存操作をrequire_escalatedで再試行して成功した。旧103パスを保持し調査ZIP一件を追加。旧三模型ZIP・科学核・ガイド・検査器はbyte不変。調査結果、過去模型索引、原意見/画像と次の比較操作を保存した段階で、地図高の修復・科学採用の完了ではない。文書の管理検査はvalidation-C1-final、固定照合はC1-fixed-readbackと各remote JSONに保存。

この実績をC2として同じbranch/PRへ追記保存し、全104パスを再照合する。最終C2自身のSHAはPR本文と外側受領票へ置き、自己SHAだけのcommitを繰り返さない。次のCodex担当はS34末尾の意見1の配置比較。人間は散発的な意見を自由に返し、mainへの統合を判断する。
<!-- ACT360-SAVE-END -->

## AUD-350：0.34候補を固定し、用途への不適合を確認する

2026-09-25、main M320 `f33165b2ccd6456d57efc92f7aaf2c2a83f4aab6`、PR25 open/Draft/unmerged、head C2-340 `371797547671beee06c57ba6d16ab68a7647912e` を主担当が実取得。候補tree `6b39572a6250ddb8cd085009119da59e57607ad6` と作業全101パスの同一性を確認し、P350=`C:/Users/genia/AppData/Local/Temp/balloon-design-350` のbase-0.34.0へ固定。元local.gitのHEAD M101は切り替えない。

README/AGENTS/CONTEXTとDC-JUDGMENT/CHANGE/CLOSEから、検査の充足と意図の理解を分ける規範を再確認。0.34のD-173/workflow340には、小画面で比較面数を減らす判断が明記されていたため、単なる寸法不具合でなく設計判断から改める。主担当が原風資料の§3.1/p10と該当図を再読し、月内前後半24区間と旧「週」表記の関係をWIND_REPORT_REVIEW第12節へ戻す。詳細な読取・依存範囲と未確認は有限レビュー証拠へ記録する。

## ACT-350：判断を進める条件を先に置き、実物を修正する

操作前のS34-350-planを根拠に、予報/詳細と気象の担当へ固定C2-340と独立パスを渡す。主担当が原資料の読み直しと跨る用途を評価する。記録担当は現在入口・採否・実績・有限な依存確認を結び、古い検査成功を今回の成功へ流用しない。

改訂対象は、親から遅延列を作る発見可能な入口と意図のある離散範囲、通常地図/写真の連続取得と詳細切替、月内固定24区間と月の軸表示、12面単位での一覧比較である。原模型と証拠を保持してworkflow-ui-035へ追加し、変更結果を人工データの範囲で評価する。 実装の再点検から、旧09–23時の人工制限では翌日へ延びる遅延を表せないことも修正対象にした。親日時と従属する時差の継承、独立化後の分離、新人工変換toy-jst-time-035-v1と旧式の識別を評価する。これは実気象の時刻支持の実証ではない。

RPT-055の追加指示を同候補へ受領。主担当は実装とは独立した批評役へ元目的・根拠・実物を渡し、検査成功に依存しない全体評価と反証を行う。具体案を一律採用せず代替案を比較し、批評への採否理由と修正後の観察をS34へ残す。批評で判明した用途不適合を解消するまでは受入・PR保存を完了扱いにしない。

RPT-056はこの批評・設計改善の循環をさらに繰り返す指示。初回反例の解消だけで止めず、別の利用場面へ問いを移し、修復案自体の代償も再評価する。担当間の評価と主担当の採否を分け、S34に順に実績を戻す。

独立した用途批評と状態・保存批評は初回0.35を受入不可とした。記録担当はcritique/critique.mdとalternatives/lifecycle-review.mdを全文読取し、親未更新時の質量混在、子復元での継承破断、風図の60分集計/90分注記、クリック一回目喪失の数値証拠を照合した。風配850 hPa、六遅延、旧条件の群詳細の保存画像も視認した。修復後の画像・操作の評価ではない。D-174/workflow350/S34へ反証→代案→採否を同じ0.35の記録として戻した。初回に成功した検査件数を修復後の受入証拠へ流用しない。根拠は試験ZIP workflow-ui-035のcritique/alternatives/reviewへ同梱する。

RPT-057を第四巡へ受領。三縦区画と異なる配置模型を比較し、必要な同時視認と縦スクロールの関係を再検討する。現在のruntimeを固定し、全赤点の常時表示と干渉全標本の保持も区別して評価する。実施前計画はS34-350-layout-plan、反例と案は試験ZIP内の第四巡。

<!-- ACT350-CHECKS-BEGIN -->
2026-09-25T10:23:55.167271+00:00の管理検査はstate 1264、health 3790、現行contract 2547、固定旧contract 2547が終了0・error0。全103登録パスは検査中不変。未選択範囲の版齢注意を全科学の再受入印で消さない。証拠P350/validation-ready/receipt.json。管理検査器自体は変更していない。

人工模型の初回操作検査だけでは受入せず、独立批評・代案比較・修復・再評価を繰り返した。第1巡の親子条件混在/保存時刻ずれ/高度軸・風配の読みにくさ、第2巡の多数候補比較/密度変更による地点移動/自動fit/微小標的/通信復帰、第3巡の丸めた共通条件誤記/系列列と累積塗りによる地理の遮蔽を記録して修復。第4巡では三縦区画と常設入力の面積を問い直し、縦積み/地図主体の代案、全点/包絡を同じ結果で比較。第5巡へ向けた修復でも、440px地図が件数と対象を離す反例を主担当が返して再設計した。第五巡で棚の重なり・古い群名・更新後の干渉入口・詳細の初期視点も修復して独立再確認した。自然高の群履歴上下図を時間照合の目的から選び、独立再批評と主担当の現物評価を経て有限受入とした。後続の点表示希望を読み落とした批評自身の訂正も残す。原反例と失敗した試行はその指紋で保持し、現在像VISION workflow350、採否D-174、review/root-review.mdから各巡へ戻れる。

主担当の最終sourceでの用途23・気象から計画への往復14、原日時と人工気柱の独立14、入口/review/VISION今回節の1440/390px描画6を確認。地図/写真は実タイルを限定取得し、通信障害の試験を地理表示の成功と混ぜない。予報/気象の各担当検査と独立批評はそれぞれ対象sourceを記録している。気象18/15/67/21は609a時点で、最終112633の非同期保存名修復は主担当の取得遅延＋画面切替で独立確認した。古い試験の成功を最終source全体の再実行と記述せず、件数を合算して品質の証明としない。

三つの通常ZIPへ梱包した。references/design_trials/interaction_and_burst.zip: 718実体 / 87767595 bytes / SHA256 ac76a8d34d77454c07ae5aa8eaf30a649b4a496a74fe59a6bce38fa506e29a15; references/design_trials/interaction_and_burst_review_035.zip: 353実体 / 80478008 bytes / SHA256 c509eb87085ac6fa25db8025e001c40c8e07571338581044a6bf1662df15e414; references/design_trials/interaction_and_burst_alternatives_035.zip: 195実体 / 40034775 bytes / SHA256 3b0a4a5d5ac3eb970b4b7da527e1682fcfae6eb0626e8ae6385e0ce92f1e31d1。合計の重複除外1261実体。旧340実体中README/manifest以外338実体のバイトを保持し、改訂模型と担当QA、全体批評/主担当検証/代案を役割に分けた。三つを同じフォルダーへ展開すれば現行HTMLの参照が揃う。各100MiB未満、CRC/member指紋、三ZIP間の重複同一性と結合後の現行/実験HTML参照を照合。初回57参照のうち、保存専用の部分ソース6件/56参照は固定path・hashと再構成説明で区別し、実験入口の案内欠落1件は固定sourceを変えず中継先を追加した。旧sourceを全て直接開けると主張しない。原フィードバック・失敗/反例・再現源・画像を削らず同梱した。

VISION旧104→105 ID、RUNBOOK旧386→407 IDで欠落なし。旧101パスを包含し新資産2件を追加した103登録パス・既存45論証IDを保持。生成済みガイド・科学核・取得器はバイト不変。今回の境界は人工模型の意味と操作・表示の適合であり、実気象MC・物理精度・予測確率・現実の安全性・本番性能・3D・人間の使用感の採用は未受入。原PDF全頁や全履歴文書の印刷品質を再監査したものでもない。保存と固定照合の実数は後続保存欄へ戻す。
<!-- ACT350-CHECKS-END -->
<!-- ACT350-SAVE-BEGIN -->
2026-09-25T10:27:02.500772+00:00までに、検査済みの0.35候補17差分を既存branch codex/design-feedback-032 / Draft PR25へ保存。C1-350 3df1824b7266d651dae77a425a91c10a13be10f4、親は未統合C2-340 371797547671beee06c57ba6d16ab68a7647912e、tree 69fe3e01f0458304f9eebe81feb160b40f557191。GitHub固定treeで全103パスのmode/size/Git blobをmanifest-C1.jsonと照合。PR head一致、Draft/open/unmerged、main M320 f33165b2ccd6456d57efc92f7aaf2c2a83f4aab6不変を再確認した。mainの書込み/マージは行っていない。

P350/git-saveの独立bare領域に固定C2-340からcommitを作り、通常pushで作業branchを更新した。許可リスト17パスと全103パスmanifestを照合し、直前/直後のmain/branchを確認。元作業フォルダーlocal.gitのHEAD M101とcheckoutは不変。既存runtime ZIPを保持し、review/critique用とalternatives用の新規ZIP二件を追加登録した。三ZIPは同じ空フォルダーへ展開する。保存前の管理検査はvalidation-C1-final、模型/文書表示の確認はACT350と試験ZIP、固定読戻しはC1-fixed-readback.json / C1-remote-tree.jsonを参照。

この実績をC2-350として同じbranch/PR25へ追記保存し、再度全103パスを固定照合する。C2自身のSHAと最終照合はPR本文と外側受領票へ置き、自己SHAだけの再commitを繰り返さない。操作模型と設計案の改訂であり、本体接続・科学採用・人間の使用感の採用は別。次の依頼はS34末尾、mainマージは人間。

C1の初回通常実行はGit認証補助shのsignal pipe作成がWin32 error 5で失敗し、remote照会前に停止した。同一save_git.py C1を昇格実行し、既存の継続許可と同じ17差分・作業branchの範囲で成功した。自動承認の旧規範による拒否ではなく、main/元local.git保護を解除していない。GitHub応答の保存は一度Windowsコマンド長上限206で失敗したため、取得済み応答をfile patchで保存し直し、固定照合した。いずれもGitの重複pushや別commitを作らず処理した。
<!-- ACT350-SAVE-END -->

## AUD-340：未統合候補を固定し、改善する実物を選ぶ

2026-09-25、main M320 `f33165b2ccd6456d57efc92f7aaf2c2a83f4aab6` 不変、PR25 open/Draft/unmerged、head C2-330 `617afabaf1f4566435923ee7f249499e02cefcc6` を実取得。候補tree `ab869cd8eaad69f48250fc0541c3ee5c1a987d45` と作業全101パスの同一性を確認し、P340=`C:/Users/genia/AppData/Local/Temp/balloon-design-340` のbase-0.33.0へ固定。元local.gitのHEADはM101のまま切り替えない。

実読はREADME R0–R5、適用AGENTSとの互換性、CONTEXT現在/RPT052、CONTROL判断/変更/終了、VISION feedback330の診断と全具体案、D172、S34の計画/現在/前回実績、今回依存の工程/課題/不確実性。RPT052添付全文を再読し、前回確認したコード/保存画像と現在の模型を照合した。科学核や原風資料全ページの再評価を今回のUI改訂へ含めない。

## ACT-340：二つの模型とその接続を改善する

操作前にS34-340-planへ担当/入力/操作/期待/停止/記録先を置いた。独立パスの予報/詳細担当と気象担当へ固定比較元を渡し、主担当が全体の適合を担う。metadata担当は登録101パス/45narrative IDsを保って依存を点検する。完成像・判断・実績の役割を維持し、一般原則の別台帳は増やさない。

共通準備の折畳み、複数施設、対象行の操作、遅延集合/結果再利用、位置/風と履歴の同時視認、全取得域と図別期間、日付からの週集計、地理背景と原格子、任意点季節計画への実データ受渡しを人工模型で具体化する。再現源・操作検査・観察を既存ZIPのworkflow-uiへ保存する。

<!-- ACT340-CHECKS-BEGIN -->
2026-09-25、予報の連続操作42/42、実入力・参照付き除去・一点/SVG等11/11、背景4/4が成功。写真は12/12タイル取得後に視認。気象の主検査23/23と最終の凡例透明度修正に対する限定6/6、主担当の日付/条件/人工履歴の独立14項目、気象→任意点計画→詳細→元の気象状態への往復13/13が成功した。通常の人工模型操作は通信要求0・JavaScript例外0。主担当は予報初期/写真、気象12風配/場所差、季節の全域表示、1366×768詳細を視認。入口/review/VISION今回節の1440/390px表示6件は横溢れ・画像欠落・JS例外・通信要求0。証拠は試験ZIP workflow-ui 内の各qa340とreview。

実操作と視認で、地図上の文字が地点クリックを奪うこと、気象へ戻ると探索状態が失われること、季節分散の見切れ、場所差での時期バーの離れを発見し修正へ戻した。旧人工変換の2時間制限が12時間の遅延比較を塞ぐ問題も訂正し、変換IDを分けた。準備・比較・掘下げの役割と条件/結果/表示の寿命が連続操作で追えるようになったことを今回の効用とする。小画面の同時視認、ユーザーの使用感、実気象/科学核/確率/本番性能の受入は別である。

新試験ZIPは340実体、29306709bytes、SHA256 9a29c520fe793ba1ba30debf0c97b87cf307dc358c8e773f4727f993e0da2885。旧243実体のうちREADME/manifest以外241実体をバイト保持し、97実体を追加。原フィードバック、再現源、現行QA/画像/担当と主担当の評価を同梱し、旧0.32QAを新成功として流用しない。本文/旧版の比較はC2-330固定全101パスが基準。state 1262、health 3750、現行/固定旧contract各 2481 が終了0・error0、検査中101パス不変。未選択範囲の版齢注意は全科学を再受入した印で消さない。証拠P340/validation-ready/receipt.json。

VISIONは旧103→104 ID、RUNBOOKは旧381→385 IDで旧IDの欠落なし。登録101パス/既存45論証IDは保持、変更は14パスで他87パス不変。生成済みガイド・科学核・取得器・検査器は変更していない。原風全PDF再監査、現実の気象再集計、物理・科学の受入、全履歴文書の印刷確認は今回未実施。
<!-- ACT340-CHECKS-END -->
<!-- ACT340-SAVE-BEGIN -->
2026-09-25 06:13:08 UTCまでに、検査済みの0.34候補14差分を既存branch codex/design-feedback-032 / Draft PR25へ保存。C1-340 5e3c8eddf78b45d6d8eede653fec33361a2e4c54、親は未統合C2-330 617afabaf1f4566435923ee7f249499e02cefcc6、tree 03d4901f45395535e395183c2bf801bc240f4e8c。GitHub固定treeで全101パスのmode/size/Git blobをmanifest-C1.jsonと照合。PR head一致、Draft/open/unmerged、main M320 f33165b2ccd6456d57efc92f7aaf2c2a83f4aab6不変を再確認した。mainの書込み/マージは行っていない。

P340/git-saveの独立bare領域に固定C2-330からcommitを作り、通常pushで作業branchを更新した。許可リストと全101パスmanifestを照合し、直前/直後のmain/branchを確認。元作業フォルダーlocal.gitのHEAD M101とcheckoutは不変。保存前の管理検査はvalidation-C1-final、模型/文書表示の確認はACT340と試験ZIP、固定読戻しはC1-fixed-readback.json / C1-remote-tree.jsonを参照。

この実績をC2-340として同じbranch/PR25へ追記保存し、再度全101パスを固定照合する。C2自身のSHAと最終照合はPR本文と外側受領票へ置き、自己SHAだけの再commitを繰り返さない。操作模型と設計案の改訂であり、本体接続・科学採用・人間の使用感の採用は別。次の依頼はS34末尾、mainマージは人間。
<!-- ACT340-SAVE-END -->

## AUD-330：統合後0.32を固定し、原因と代案を比較する

2026-09-25 UTC、GitHub連携でPrivate repo1373721672、main `f33165b2ccd6456d57efc92f7aaf2c2a83f4aab6`、PR24 closed/mergedを確認。親はM280 `f4b6bb317499bb2ac4676ecd5567485e21bc4921` とC2-320 `9c8e1080ae343b58e64d507da57de25e05d448c3`、tree `14ee62545480cbc4b87c95248ee8be47758ff6de`。全101パスのGit blob/sizeを照合、modeは全100644。P330=`C:/Users/genia/AppData/Local/Temp/balloon-design-330` のbase-0.32.0へコピーし、snapshot SHA256 `c71d6d6713ce7dc86a6a6b5b64cddd5612bf8e7e35df523f2b9122acd6a777ca`。適用AGENTSと作業基準0.32が一致。local.gitの旧HEADを切り替えない。

今回の実読は添付全文、README R0–R5、CONTEXTの現在/要求/方針とRPT、CONTROLの判断/変更/終了、VISIONの対象設計、D-171、S34現在と0.32実績、PLAN9/10の今回依存、MAPの情報依存、TASKS/UNKNOWNSの対象。原風の再読は既存WIND_REPORT_REVIEW第10–11節と既存テキストに限定し、PDF全114頁の再監査とはしない。0.32試験ZIPと同一のreleaseにあるforecastのreview/app/保存画像、weatherのapp/fixture/index/保存画像を読取。主担当は詳細画面と風配一覧を視認。実装上の意図と利用適合の区別を二担当の批評で問い直した。

## ACT-330：修正要求へ短絡せず、議論に返す

S34へ担当/入力/操作/期待/停止/記録を置いてから文書を改訂。根拠と具体案を既存VISIONへ集約し、原則の別台帳は追加しない。現在の気象maskは人工hourによる気象時刻層別、profileは初期9点等重みの中央値/p10–p90、年間は週でなく半月、任意点は凍結気柱と確認した。用途・対象を定めず人工データの構造へUIを従属させた点を診断した。記録中のT-016で旧実績がowner列へ入っていた誤りはevidenceへ戻し、履歴表示の0.32/0.31の並びは編集元の版順から訂正する。旧実績を削除しない。

<!-- ACT330-CHECKS-BEGIN -->
2026-09-25 UTC、固定M320との文書比較を実施。state1262、health3736、現行/固定旧contract各2464が終了0・error0。全101パスは検査中不変。healthの警告1件は未選択177範囲の版齢注意で、全科学を再受入した印は付けない。検査器/通常import/CLIと試験ZIPはバイト不変。候補差分13パス、他88パス不変。VISION旧98 IDとRUNBOOK旧376 IDを保持し、それぞれ103/380 ID。既存45論証IDと101パスを保持した。証拠P330/validation-ready/receipt.json、manifest-C1.json。

新設計本文は予報/気象の二担当が独立読取。半月ページの意味、期間切替の作用範囲、遅延除去と比較参照、概要での同時視認の4点を訂正した。主担当は原0.32の詳細/風配画像と、新文書の配置図/気象表を視認。文書の1440/390px描画でページ横溢れ/JSエラー/HTTP要求0を確認した。これは配置図の表示確認であり、改修UIの操作や全頁印刷の検証ではない。読取に用いたreleaseの70実体は固定ZIPと全バイト一致した。

初回はフッター旧版と派生履歴の統合SHA短記を既存検査が拒否し、訂正した。一時的OSError22によりmetadata書込が中断した試行は失敗として保持、同一内容の再書込後にrefresh/再検査で解消。原検査器は変更しない。非表示Edgeの初回spawn EPERMは同じ通信遮断描画の昇格実行で解消。原風全PDF再監査、実気象再集計、改修模型操作、本番性能、科学採用、人間の使用感は未確認。
<!-- ACT330-CHECKS-END -->
<!-- ACT330-SAVE-BEGIN -->
2026-09-25T05:24:35Zまでに、検査済みの設計/記録13差分を新branch codex/design-feedback-032へ保存し、Draft PR25 https://github.com/GENIANY/space-balloon-simulator-jp/pull/25 を作成。C1 ae9c90cc94979fd2c3c0bf731282bd55f1c82f15、親M320 f33165b2ccd6456d57efc92f7aaf2c2a83f4aab6、tree 96328a55a3b695177d5cacc97403a1d8624df103。GitHub固定treeで全101パスのmode/size/Git blobをmanifest-C1.jsonへ照合。PR head一致、Draft/open/unmerged、main M320不変を再確認した。main書込み/マージは行っていない。

保存にはP330/git-saveの独立bare領域を使用し、固定mainから作ったcommitを通常pushした。対象パスはmanifestと許可リストに限定し、直前/直後のmainとbranchを確認。元作業フォルダーのlocal.git/HEAD/checkoutは不変。保存前のvalidation-C1-readyはstate1262、health3736、現行/固定旧contract各2464成功、101パス検査中不変。証拠C1-git-receipt.json、C1-remote-tree.json、manifest-C1.json。

この実績をC2として同じbranch/PR25へ追記保存し、固定読戻しを行う。C2自身のSHAと最終照合はPR本文と外側受領票に置き、自己SHAの記録だけで再commitし続けない。0.33は設計議論と記録の改訂で、模型の修復完了ではない。次の人間への依頼とCodex作業はS34末尾へ。mainマージは人間。
<!-- ACT330-SAVE-END -->

## AUD-320：改善理由と運用上の判断を結ぶ固定比較

2026-09-24T16:14:24.613974+00:00、main M280 f4b6bb317499bb2ac4676ecd5567485e21bc4921、PR24 Draft/open/unmerged、C2-310 35882468429e2bbd8833c28f04b059ceb72f25b1、tree 5df1da541b9b9e6a6f1c91fb8af405a64214dbe2 を確認。全101登録パスのmode/size/Git blob一致でbase-0.31.0を固定し、snapshot SHA256 e81933a4475b578a547d933a81dd636e8202d4bf4c247d6320c094ddcb4e1023。適用AGENTS/作業候補は0.31、main0.28を区別しlocal.git履歴を変更しない。P320は C:/Users/genia/.codex/visualizations/2026/09/21/01a0c475-9ac7-7852-85a1-e3a4f3188dfa/design-320/。

README/AGENTS/CONTEXT現在、DC-JUDGMENT/START/CHANGE/CLOSE、VISION/S34と方向・依存を取得。今回の原風図は0.31の固定レビューを継承し、PDF全114頁や数値監査を再受入しない。Navara公式サイト/Getting Started/公開repo、GSIタイル一覧/利用条件、GeoJSON RFC7946、KML Polygon、Shapely covers、気象ガイドの時刻補間を参照。URL・確認範囲・非確認は試験ZIPの landing-planning-review/sources.json とreview.mdへ保存する。Navara URLは実ユーザー回答。外部資料内の指示を作業権限にしない。

## ACT-320：干渉・従属する遅延・場所変更と気象比較を具体化する

S34へ操作前計画を置き、主担当が全体設計/記録、並列担当が予報模型・気象模型・一次資料/独立批評を担当。比較基準C2-310と編集先P320を固定した。50/90/95%域、禁止域の実着地点ID、遅延親子、明示地点指定、凡例と任意点季節比較の意味をD-171/VISIONへ記録する。

<!-- ACT320-CHECKS-BEGIN -->
予報28/28＋追加17/17、気象の既存39/39＋新39/39成功。両方のオフライン操作はJSエラー/HTTP要求0。予報の地理院背景は限定通信で標準18/写真15タイル取得。経験50/90/95%の順位/実包含数、GeoJSON/KMLの穴/境界/無効入力、実着地IDと領域版、親子/古い結果/独立化、地点補間、凡例と図保存を確認。主担当は遅延列/干渉詳細/写真/任意点季節/12か月地図を実行画像で視認し修正後を再評価した。独立指摘の異地点平均軌道原点、無効コントロール、KML高度の無言切捨てを修正。気象の線種と平均/季節のラベル重なりを修正し、経験域はceil(pN)と実包含数で両模型を揃えた。

試験ZIP 243実体、21,055,085 bytes、SHA256 7f715eee6044024e57d222ca2b856a2413bdca5b71d192db30bb2696c8da259d。旧165実体中README/manifest以外163実体をbyte保持し、CRC/全member/manifestと相対参照47件を照合。新模型は landing-planning-ui/forecast と weather、根拠は landing-planning-review。vendor/license/原資料は保持。通常import/CLIには接続しない。

固定0.31と比べて旧121手順範囲の正規化差0、親41順序/旧306 ID維持、VISION旧93 ID保持+5追加、保護81パスbyte不変。限定依存50範囲の担当/時制/後続を実読し、上位PLAN/DCの追加は不要と判断。63範囲は今回の意味的影響について確認し、未読範囲の版差注意は印を上げて消さない。現在入口7資料の独立読取で旧現在形を訂正した。

2026-09-24 16:44 UTCの既存検査はstate 1262、health 3716、現行/固定比較元contract各2481が成功し、全101パスは検査前後不変。初回healthは編集後のS34指紋が未更新で失敗。metadata適応時に証拠IDの辞書参照を壊した不具合も既存healthが検出し、補助scriptを修正して同じ検査を通した。検査器は変更していない。healthの残警告1件は非選択範囲の版差注意。実行内容はP320/validation-corrected/receipt.json。

独立担当のIABによるローカルUI閲覧はBrowser URL policyに拒否され、迂回せず画像/ソース/実行担当の結果読取に限定した。文書235件はID/順序/リンク等の静的検査で、新文書全体のブラウザ/印刷表示を再受入した意味ではない。人工操作と設計の有限評価であり、実気象MC・物理再計算/境界停止再判定・予測確率/精度・本番性能・人間使用感・3D導入は未確認。保存検査/固定読戻しの実数は次の保存欄へ戻す。
<!-- ACT320-CHECKS-END -->
<!-- ACT320-SAVE-BEGIN -->
2026-09-24T17:08:34.740Z、0.32の14差分をC1 9efd486cf97494e26b36418bf0e7dd54c1e5ce6b（親C2-310 35882468429e2bbd8833c28f04b059ceb72f25b1、tree 96ff901620f4ee9a4f0b374e48b9dcfba3d24c37）として既存branch codex/climate-planning-rpt048へ保存し、Draft PR24 https://github.com/GENIANY/space-balloon-simulator-jp/pull/24 のhead一致を確認した。GitHub固定commit/treeで全101登録パスのmode/size/Git blobが保存manifestと一致。Draft/open/unmerged、main M280不変を再確認した。

当初の接続ツールによる13文書blob作成は成功したが、大容量ZIPの分割読み出しが未完返却と停滞を生じた。対象/権限を変えず、既存Git認証の読み取りを確認してP320/git-saveに独立したbare保存領域を用意した。同じ14ファイルをmanifestへ照合し、固定親からtree/commitを作成、直前main/branch照合後にforceなしの通常pushを行った。元作業フォルダーのlocal.git/HEAD/checkoutは変更していない。これは処理経路の変更であり、自動承認拒否の回避ではない。

保存前検査はP320/validation-C1-ready/receipt.json：state1262、health3716、現行/固定比較元contract各2481、全てerror0、全101パス検査前後不変。記録更新の途中にファイルopenの一時エラーでmetadata更新が中断した試行（validation-C1-final）は失敗として保持し、同じ更新を再実行後にC1-readyを通した。証拠はsave-C1/manifest.json、C1-git-prepush.json、C1-receipt.json。

このC1実績をC2として保存・再照合する。C2自身のSHAと最終受領はPR本文と外側P320/C2-receipt.jsonへ置き、自己SHA記載だけを目的とするC3は作らない。次に人間へ求める評価はS34末尾、Codexの次設計は二基盤から過去予報/再解析と季節計画への共用。mainのマージは人間。
<!-- ACT320-SAVE-END -->

## AUD-310：0.30差戻しの固定比較と原図再読

2026-09-24T13:05:23 UTC、main M280 f4b6bb317499bb2ac4676ecd5567485e21bc4921 不変、PR24 Draft/open/unmerged、C2-300 80731433f2feb68ae965246f7912657e60f6f182、tree e51b1e46ba81de9661480ae0be3418bbcfe644f0 を取得。全101パスのmode/size/Git blob一致を確認しbase-0.30.0を固定。本会話で提示された適用AGENTS0.29、復旧時の作業ファイルAGENTSを含む候補0.30、main0.28を区別し、local.git HEADは変更しない。

外側P310は C:/Users/genia/.codex/visualizations/2026/09/21/01a0c475-9ac7-7852-85a1-e3a4f3188dfa/design-310/。復旧票、旧実体、旧案/原図の独立レビュー、新模型の再現源と操作/描画/保存証拠を置く。結論と通常再開に必要な根拠はrepoと既存試験ZIPへ戻す。README R0〜R5/AGENTS、DC-JUDGMENT/START/CHANGE/CLOSE、CONTEXT現在、PLAN/VISION/S34と依存を用途に沿って確認した。原風PDF9図を主担当・独立担当が視認し、DB支持は読み取り専用SQLで照合。初期healthは成功3546検査で、比較元未指定と版差注意はまだ別に評価する。

## ACT-310：予報と気象の二基盤を再設計する

S34に操作前計画を置き、予報/原風/旧設計批評を分担し、主担当が二基盤の関係を評価した。データ境界とUIタブ、群と確率混合、情報削減と簡潔さを混同した原因をVISION/D-170へ戻す。検査と保存の実績は実行後に追記する。

<!-- ACT310-CHECKS-BEGIN -->
予報39/39、独立反例10/10、気象39/39、再配置/相互リンク8/8、文書表示30/30成功。実物の意味と旧案比較はroot-review310.md、独立forecast/critique/windレビューへ記録。気象は実マウス保持中の更新、全12か月保持、maskと表示の区別、SVG7種と画面全ノード一致を確認。数値定義R/地点平均の幅/風配countsを原人工標本と照合。予報の対象すり替え/結果ID衝突は独立反例の再実行で解消。実データ・科学採用・人間の使用感は別。

試験ZIP 165実体、12,559,099 bytes、SHA256 4c767357b76a085d43118594f382198d3b40d11df321af28b213a7f3c892555f。旧95実体のREADME/manifest以外93実体を保持、相対参照41件とCRC/全member一致。原資料/製品表/vendorライセンス保持。新二基盤は別フォルダーへ再配置し、リンク先を別タブで開くことで元画面の作業状態を保持する有限経路を検査した。全ワークスペースの永続化や両モード間の条件共用を実装した意味ではない。

文書の旧91IDを保持し93へ。最終横断点検でS34冒頭の旧PR23指示とVISION8.1の旧prototype案内が現在形に見える残件を発見し、当時の記録と現在の入口を明示した。README末尾版表示も訂正した。現行推奨と矛盾する旧「次に本体接続」「群の配分」記述を保留/別操作へ修正し、図17の出典事実と新提案を区別。現在の入口とS34の時系列は変更理由へ接続。既存検査（2026-09-24 13:58 UTC）はstate 1256、health 3706、現行/比較元contract各2506、全てerror 0。healthの残警告は非選択範囲の確認版差であり、未読範囲の印を上げて解消しない。初回healthは確認日の記録形式を日時にしたため失敗し、既存契約どおり日付に訂正して同じ検査を通した。入力101パスは検査前後不変。文書表示は最終本文/印更新後に30/30を再確認。限定依存は50登録範囲の担当/時制/後続の実読、旧121範囲の正規化差0、41親順序/旧306 ID維持、科学核等81パスのbyte不変を確認。CONTROL/ENVは指定部分のみ実読で全面確認に広げない。
<!-- ACT310-CHECKS-END -->
<!-- ACT310-SAVE-BEGIN -->
2026-09-24T14:09:13.582Z、0.31の15差分をC1 4eb178624b9ee4f77c9bead2a621168502453c0a（親C2-300 80731433f2feb68ae965246f7912657e60f6f182、tree 857e4df695bada3ae61315b6af6094a3730cb3cb）として既存branch codex/climate-planning-rpt048へ保存し、Draft PR24 https://github.com/GENIANY/space-balloon-simulator-jp/pull/24 のhead更新を確認した。全101パスのmode/size/Git blobを保存manifestへ固定照合し、親・PR head一致・Draft/open/unmergedとmain M280不変を確認した。mainへの書込み/マージはしていない。この実績を次のC2へ追記保存する。C2自身のSHAと最終読戻しはPR本文と外側受領票へ置き、自己SHAの追記だけを目的とするC3は作らない。

証拠はP310/save-C1/manifest.json、validation-C1-final/receipt.json、C1-receipt.json。保存前検査はstate 1262、health 3706、新旧contract各2506が成功し、検査前後の全101パスはバイト不変。実績追記後の検査とC2保存/読戻しはこの記述時点では未実施であり、続いて実行する。これらは記録と保存の整合確認であり、人工模型の科学的妥当性や本体完成の受入ではない。

独立読直しP310/critique/final-doc-consistency.mdは、C1に含む7資料の固定hashを示し、S34の旧計画とVISIONの旧模型記述を過去記録として区別する訂正、README現版表示、風統計と飛行条件を必要とする軌道解析の区別を確認した。判定範囲は現行の順序・人間への依頼・旧時制・人工/科学境界の意味整合であり、科学的採用、製品品質、同報告後のGit保存実績の受入ではない。
<!-- ACT310-SAVE-END -->

## AUD-300：目的から画面を組み直すための固定比較と読取

2026-09-24 UTC、private repo id1373721672、main M280 f4b6bb317499bb2ac4676ecd5567485e21bc4921 不変、PR24 open/Draft/unmerged、head C2-290 a5f3ce04372ceaec7ff8b2fc6abe0d75d3b26d6d、tree cdba0bc055387f2bd5e070ea1e537a6b8fa014c4 を実取得。101全パスのmode/size/Git blobをローカルへ照合しbase-0.29.0を固定。local.git HEAD M101は変更しない。適用AGENTS0.29と作業候補0.29、main0.28を区別した。

外側P300は C:/Users/genia/.codex/visualizations/2026/09/21/01a0c475-9ac7-7852-85a1-e3a4f3188dfa/design-300/。復旧受領票、旧全実体、独立needs/critique、限定依存レビュー、操作/文書表示/保存ログを保持する。現在の結論はrepoへ、再現用の模型とレビューは既存試験ZIPへ戻し、外側だけを通常再開の前提にしない。

README R0〜R5/AGENTS、DC-JUDGMENT/START/CHANGE/CLOSE、CTX現在とRPT043〜049、VISION旧案・関連D165〜168、PLAN10.6、S34、依存索引を読んだ。独立担当はVISIONを枠にせず先に8使用状況を導出し、別担当は旧画面コードと6使用状況から評価した。固定同一版の既読科学根拠は維持し、今回新しい文献調査や製品CVの受入は行わない。初期healthは成功、必須期限切れなし。版差注意は用途への影響から選び、未選定範囲の印を上げない。

## ACT-300：用途から解析と画面を再設計する

RPT-049をS34の実施前計画へ置き、共通比較/独立気象/専用観測入口、任意接続、初期不採用と失う便益をVISIONへ具体化した。旧0.27操作模型は過去の検討例へ畳み、模型/科学根拠のIDを保持する。操作評価・文書遷移・保存実績は実行後に追記する。予定を実行成功にしない。

<!-- ACT300-CHECKS-BEGIN -->
操作模型は43/43、文書表示は29/29成功。Edge 153.0.4234.48、file URL・通信遮断、1280/390px。主担当と独立担当が表示を読んで入力草案/固定結果の分離、事後破裂/場差替えの分離を修正した。UI検査は操作意味と図の保存、文書検査は旧ID/入れ子リンク/狭幅/印刷時状態を対象にし、科学計算・人間採用・物理的な全頁印刷品質は含まない。

試験ZIP95実体、6,588,591bytes、SHA256 a7cfe040fcb7156e31b27768e7a9ff2843cb077c9e914d1a7beda1c341039a00。既存68のREADME/manifest以外66実体を保持。新模型21実体＋個別manifest、設計レビュー5実体を追加。CRC/全member bytes/hash/相対参照31件を確認。元の製品表・数値例・vendor/ライセンスは不変。P300/package300-receipt.jsonが証拠。

旧51依存範囲の実読と121範囲/41親順序/旧40親内306IDの比較はhelper/dependency-reviewとdependency-snapshot。旧本文の当時の操作や科学を再実行/認定しない。PLAN10.5/10.6は独立気象とVISIONの役割を既に許容し生成対は不変。版差注意を一括解消しない。文書検査04はstate1256、health3692、新/固定旧contract各2481成功、101実体は検査前後不変。初回は派生した版履歴行の確認範囲不足で停止し実読を追加。続いて末尾版表示の残留を訂正した。追記時の改行変換による旧範囲差は元のLFへ戻し解消し、検査器は変更していない。無関係なCONTROL/PLANの4確認印は元へ戻し、限定読取を全体再認定にしない。最終記録監査で表紙/現在問いの旧0.29文もRPT049の方針へ訂正した。版差注意は保持。結果追記後は同じ検査を再実行し、最終実数は保存受領票へ置く。
<!-- ACT300-CHECKS-END -->
<!-- ACT300-SAVE-BEGIN -->
2026-09-24T12:11:08.936Z、0.30の14差分をC1 a86cc86fae47d7ff70bf0d86dccd8b2b0380eed9（親C2-290 a5f3ce04372ceaec7ff8b2fc6abe0d75d3b26d6d、tree a3fd4716747b655fa4d203e5b3647fcf4cdc4e1b）として既存branch codex/climate-planning-rpt048へforce=falseで保存し、Draft PR24 https://github.com/GENIANY/space-balloon-simulator-jp/pull/24 を更新した。全101パスのmode/size/Git blobを保存manifestへ固定照合、親・PR head一致・Draft/open/unmergedとmain M280不変を確認した。main書込み/マージはしていない。続いてこの実績をC2へ追記保存し、C2自身のSHA/最終読戻しはPR本文と外側受領票へ置く。自己SHAのみの反復commitは行わない。

P300/save-C1/manifest.json、validation-C1/receipt.json、C1-receipt.jsonに証拠。保存前検査はstate1256/health3692/新旧contract各2481成功。実績追記後も同じ検査で整合を確認する。
<!-- ACT300-SAVE-END -->

## AUD-290：気候条件の探索を、モデル比較と打上げ判断へ結ぶ

2026-09-24 UTC、private repo id1373721672、main M280 f4b6bb317499bb2ac4676ecd5567485e21bc4921 を実取得。PR23はmerged/closed、mergeの親はM250とC2-280 8e0e4d520f413d58bf4d418b46afa3dc2a30cb15、tree e747381d8a29aaf7d6eadca501be4c749ae1ad7d。全101パスのmode/size/Git blobを照合し、完全base-0.28.0を保持。local.git M101は切替しない。適用AGENTS0.28と固定mainの本文は一致し、継続保存許可は有効。

P290は C:/Users/genia/.codex/visualizations/2026/09/21/01a0c475-9ac7-7852-85a1-e3a4f3188dfa/interaction-290/。復旧受領票、固定base、気象/破裂/操作模型の独立調査、表示・文書検査、保存受領票を保持。判断に必要な本文はVISIONへ、再現例は既存試験ZIPへ戻し、この外側だけを引継ぎの前提にしない。

README R0〜R5、DC-JUDGMENT/START/CHANGE/CLOSE、CTX現在、PLAN10.6、MAP依存、D165〜167、VISION三用途/モデル/分布/気象/破裂/操作、S34を比較した。通常継続として前ターン実読した同一treeの本文は再利用する。今回の期限検査は成功、必須期限切れはなく版差注意160範囲を保持。原本/本体/検査器/現行ガイドの科学的再受入は今回の範囲外。

## ACT-290：比較と季節打上げの設計を実物へする

<!-- ACT290-CHECKS-BEGIN -->
気象操作模型はEdge 153.0.4234.48、1280/390px、file URL・HTTP遮断で31項目成功。条件引継ぎ、09:30等の独立放球時刻、空mask/未実行、未検証生成器の停止、条件JSONの実保存を確認。図と件数は人工例。主担当は季節/打上げの画面と相関図を視認し、狭幅の縦移動量を製品設計課題へ残した。

二層相関例は解析式と20万標本×3条件の13検査成功。両層の周辺平均10 m/s・SD5 m/sが同じでも、相関−0.8/0/+0.8で東変位SDは5.69/12.73/17.08 km。実気象検証ではない。破裂診断は製品表の平均径と検査時径を分け、仮定した径CV10%と厚み換算CV20%のGammaモーメントをSciPy1.17.1で逆照合。分布幅の科学的根拠は推定していない。

改訂VISION/RUNBOOKは影響する27表示検査成功。旧ID保持、入れ子詳細への旧リンク、1280/390幅、print展開/復帰、通信/JS例外0を確認した。初稿のQ1〜3アンカー消失とdetails祖先の展開不足を修正。検査側headerが2要素に一致する失敗を対象IDへ修正。Edgeの初回EPERMは同じ通信遮断ローカル検査を昇格実行し解消した。承認レビュー拒否ではない。

参考ZIPは68実体・4,965,743 bytes、SHA256 251a2e74464be1acc97279a2b0d9958322ae524ef9100222073c7f9dd8877a70。旧42実体を保持し、README/manifest以外40実体は同一。26実体を追加し全読戻しhash/CRC/安全相対path/相対参照21件を確認。提供画像の原hashと公式表との比較をburst-optionsへ保存した。

文書検査02はstate1256、health3680、新/固定旧contract各2464成功、検査前後101パス不変。01ではS34内補足見出しの階層と、統合履歴表示のSHA欠落を検出し訂正。検査器/ガードは変更していない。版差注意は基準160から177へ増えたが、追加17は旧手順/PLAN表示等が版差に達したもの。今回本文不変・科学/生成の全再受入を要しないため警告を保持し、確認印で一括解消しない。意味の依存51範囲は限定実読し、旧121操作/41親手順の順を保存。PLAN三点と本体/原本/現行ガイドの実装内容は変更していない。

証拠はP290のroot-review290、dependency-review290、final-design-review290、climate-ui/qa、climate/correlation_counterexample、burst、document-ui、package290-receipt、validation-02。最終記録追記後の同じ既存検査とGit読戻しは保存受領票へ残す。操作成立・数式診断・設計採用・実気球の科学受入を区別する。
<!-- ACT290-CHECKS-END -->

<!-- ACT290-SAVE-BEGIN -->
2026-09-24 10:39:48 UTC、0.29の14差分をC1 abb39fbb9b2ee8a5b017b99ff567b02d70b8679b（親main M280 f4b6bb317499bb2ac4676ecd5567485e21bc4921、tree 5259045e760a220a47ca1a77855d8ea9c604341f）として新branch codex/climate-planning-rpt048へ保存し、Draft PR24 https://github.com/GENIANY/space-balloon-simulator-jp/pull/24 を作成した。全101パスのmode/size/Git blobを保存manifestと固定照合し、PR head一致・Draft/open/unmerged、main M280不変を確認。mainへ書込み/マージしていない。

新branchにupdate_refを呼んだ初回は422 Reference does not exist（作成APIではなかった）。同じ固定commitからcreate_branchで新branchを作り解消した。認可拒否や履歴のforce更新ではない。続いてこの実績をC2へ保存し、C2自身の最終SHA/読戻しはPR本文と外側受領票へ置く。自己SHAだけを追記する反復commitはしない。P290/save-C1/manifest.json、C1-receipt.jsonが証拠。
<!-- ACT290-SAVE-END -->

## AUD-280：使う行為と、実装の負担を具体的に調べる

2026-09-24 UTC、private repo id1373721672、main M250 `eb53fe37954f58b26771cc2f5437d46ee3f32fcd`、Draft/open/unmerged PR23 head C2-270 `ddf8550ac303111786979f03435988b8a0a6d50e` を実取得。固定treeの100パスをsize/Git blob照合し、完全base-0.27.0を保持した。local.git M101の履歴は変更しない。

P280は `C:/Users/genia/.codex/visualizations/2026/09/21/01a0c475-9ac7-7852-85a1-e3a4f3188dfa/interaction-280/`。固定base、復旧受領票、map/burst/prototype各担当の原調査、表示/検査/保存ログを保持。再現に必要な有限試作と式診断はrepo内の試験資料ZIPにも収録した。ZIPは実装済み製品の入口ではなく設計を確かめる参考物である。

README/DC-JUDGMENT/DC-CHANGE/DC-CLOSE、CONTEXT、VISION6〜9、S34、PLAN10.6/T016/U020/U021を比較元の本文から復元。旧推薦のPlotly/Dash中心案と旧H-Weibull例を、新しい利用行為と径分布案へ照らして問い直す。公式ライブラリ調査、原Excelセルの式/単位、操作試作の独立担当を主担当が統合し、科学採用と技術的動作を区別する。

## ACT-280：地図から選び、同じ標本を図で追う試作

<!-- ACT280-CHECKS-BEGIN -->
径分布は基準幾何→平均径、誘導厚みCV→径Weibullという入力案に具体化。原Excel①/⑤の幾何差、基準厚と平均厚の違い、幅ゼロ/裾を式と数値で照合した。地図方式は公式仕様を比較し、Leaflet/Plotlyの人工128標本で20操作、別の固定データ監査15項目を確認。JS集計は操作試験に限定し、本体はPython一元集計へ接続する案。風/高度履歴は人工で実気象MCではない。VISION/RUNBOOKは1440/390 px・印刷/無JS/キーボードと旧履歴を含む66項目を確認し、新節を視認した。有限試験ZIPは30実体、再展開後に監査15項目と式診断を再実行し数値JSONの同一を確認。文書整合とGit保存は後段の実績へ追記する。

主担当の目的適合評価はP280/root-review280.md、依存51範囲の限定レビューはdependency-review280.md。原本/本体/PLAN/現行ガイドの式・実装は不変。操作試作初版の着地/境界矛盾、全体と部分要約、平均形状/線種、時刻操作の画面遷移競合を独立レビューから訂正した。ZIPの独立監査器配置も再展開試験で確認した。

試作の性能は当該PC/128本/1回の観測に限定する。式診断は分布のパラメータ化で、Excelの大気表再計算・分布適合・科学的母数推定ではない。操作選択は群の関連を調べる入口で、因果効果の保証ではない。次はPythonの同一集計への接続、起動/容量/更新費用、基準幾何と径イベント入力の具体化。RPT-047で配布先の任意再集計は不要、グラフ保存が必要と回答を得た。D-167とVISIONへ受理し、C1後の追加試験としてPNG/SVG出力を進める。

<!-- ACT280-DOC-CHECK -->文書検査03はstate1255、health3659、新/固定旧contract各2482が成功し、前後101パス不変。01は追加ZIPの現行パス一覧・新設理由と現行フッタを検出。登録訂正の補助器に構文エラーがあり02では反映されず、補助器を直して03で再確認した。検査器/ガードは変更していない。版数注意160範囲は残し、無関係な確認印を上げない。原本/本体/ツール/試験/PLAN三点/現行ガイドを含む61パスは固定C2-270からbyte不変。
<!-- ACT280-CHECKS-END -->

<!-- EXPORT280-ACTUAL-BEGIN -->
RPT-047による追加実績：追加出力試験はEdge 153.0.4234.48・通信なしのfile URLで15項目成功。実ダウンロード5件（個別履歴PNG/SVG、風速PNG、風向SVG、グループ履歴PNG）を保存し、ファイル形式・対象/定義・空集合/飛行中0件・390pxの操作欄を確認した。個別/群の履歴には時刻・相別対象数n(t)、風図には放球後時刻と飛行中数、単一選択にはIDを残す。履歴は1200×960、風図は1200×800。初稿で注記切れ、履歴対象数の脱落、風配図の重複整数目盛り、風速軸題と注記の重なりを発見し訂正した。主担当と独立担当がPNG視認とSVG内容確認を行い、画像ボタンの動作だけを受入にしない。

これは人工標本の有限出力試験であり、実気象の図、全図種・全形式・全端末、印刷先/編集アプリの最終品質、製品の保存済み対話HTML出力は未確認。任意再集計は本体側に残す方針を保持する。

再梱包は42実体、2,581,259 bytes、ZIP SHA256 f1659c16dfab8a45bd6a45e5531680bd9e42f976255a45b2666544454f568438。CRCと全memberのSHA256を照合。追加コード/検査器/出力結果JSONと独立レビューを同梱する。C1の30実体版は当時の記録として上に保持。出力検査はP280/prototype/qa/export-results.json、画像はqa/exports、図単体の評価はexport-statistics-review、文書受理はexport-document-review。前の20操作/15データ監査/66文書表示は当時の実績であり、追加試験を同じ件数へ混ぜない。
追加出力を含む文書最終検査01はstate1255、health3663、新/固定旧contract各2482が成功し、前後101パス不変。42実体ZIPを別フォルダーへ展開して全manifest hash、最新試作/レビューとのbyte一致を確認。数値処理/人工入力はC1時の再実行済みコピーと同一なので、数値の再試行はせず追加出力15項目の結果を用いた。実績追記後も同じ既存検査を保存前に行う。
<!-- EXPORT280-ACTUAL-END -->

<!-- ACT280-SAVE-BEGIN -->
0.28の14差分（新設1参考ZIP）をC1 b16e851bd58736a4c42ad8ec89e8bdebeb4f9531、tree d1ace76ab5f8bc1c93c33edfaa9d6204598e98a0として既存branchへ保存した。2026-09-24 08:40:46 UTC、全101パスmode/size/Git blobと保存manifestの一致、PR23 Draft/open/unmergedとhead一致を固定読戻しで確認。直前のmain M250/C2-270を再取得しnon-force更新した。main書込み/マージなし。この実績追記もC2へ検査・保存し、その最終SHAはPR本文と外側受領票へ置く。
保存manifest/受領票はP280/save-C1、C1-receipt.json。保存対象は0.28の設計・要求/判断/手順/管理13ファイルと再現用ZIP1件。全101パスの基準照合で、原本や本体の未変更も区別する。
<!-- ACT280-SAVE-END -->

## AUD-270：図の問いと、情報・費用の段階を具体化する

2026-09-24 UTC、private repo id1373721672、main M250 `eb53fe37954f58b26771cc2f5437d46ee3f32fcd`、Draft/open/unmerged PR23 head C2-260 `a1720411c3e4701c56397b43ab7597ccc2588d4f` を実取得。固定treeとローカル全100パスのsize/Git blob一致を確認した。完全base-0.26.0を保持し、この候補を前後比較の基準とする。local.git M101の履歴は変更しない。

外部証拠P270は `C:/Users/genia/.codex/visualizations/2026/09/21/01a0c475-9ac7-7852-85a1-e3a4f3188dfa/interaction-270/`。recovery-receipt.json、base-0.26.0、wind-review.md、statistics-review.md、interaction-review.mdと指定9頁PNG、編集/表示/検査/保存の受領票を置く。ここは生ログの補助保管で、Gitへ残る要求・判断・原本hash・頁/式・再現手順の代わりにしない。失われた場合は固定候補と原本から新たに検査し、当時のログを再現したとはしない。

README R0〜R5、CONTEXT要求と長期方向、DC-JUDGMENT/DC-CHANGE/DC-CLOSE、VISION全体、PLAN10.6/T016/U020/U021/D165、S34の担当/事前手順と過去実績から今回の意図を復元。原風図担当、統計担当、操作/費用担当の独立レビューを統合し、元のユーザー案へ戻って判断した。依存点検でS29の後継注記に旧PR22 Draftの現在形が残る点を発見し、当時の引継ぎとその後のM250統合へ時制を限定した。旧指示/実績本文とコピー欄は保持。PLANの工程とモデル/分布の既決境界は変えず、詳細は既存VISION内へ置く。

原PDFの指定9図（印刷＝物理35/36/37/38/40/41/43/45/48）を120 dpiで描画・視認。本文方法と付録Dを限定再読した。半月ビン、中央値/分位幅、地域間max−min、全4解析時刻、DB再集計の制約を確認。初期読取りで付録Dの機体摂動条件を見落としたが、統合原稿再レビューで第5条件の存在を確認し訂正した。原本/供給コードの変更や全数値再計算はない。

統計レビューで、グループ配分を全試行へ掛けるか着地分布へ掛けるかの曖昧さを発見。前者に定義し、合成後に着地集合へ条件付ける。時刻/位相・停止集合、平均形状、風向来向/移動方向も明確化した。HDR原著、SciPy KDEの多峰/退化制約、ECMWFの風向/有効時刻を公式資料で確認。太陽相対の4時間帯を標準化する研究照合は未了で、規格として採用しない。

期限選定：基準healthは成功、初稿0.27検査で必須期限切れ/初回未確認は0。3版差の注意信号158範囲は、今回使う本文/依存を優先して再点検。変更していない本体/試験/原気象/既存科学・生成物の再受入は不要と判断し、版差だけを理由に確認印を上げない。PLAN生成三点と本体/検査器/試験の50パスは基準とバイト同一。

## ACT-270：必要な情報へ降りる画面案

比較元VISIONは主画面から点群と他候補連動を出す案だった。RPT-045に合わせ、概要を平均点/分布領域/少数数値へ絞り、個別詳細の選択は当該タブ内、グループ詳細は全着地標本比較へ変えた。気候図は図番号の羅列から、問い・統計定義・操作・次の判断の対応表へ具体化。入力変更時の旧結果、表示と追加計算の分離も模型へ含めた。感度/校正/停止の旧論旨は補助索引/専門節に保持した。

<!-- ACT270-CHECKS-BEGIN -->
主担当/操作担当が1440px・390px・JavaScript無効・印刷表示を確認。候補/合成/詳細/選択/風時刻/旧結果状態の操作検査は62項目成功（P270/ui-02）。狭画面は図内スクロールで文字を保持し、ページ全体のはみ出しなし。外部HTTP要求とconsole/page errorなし。模型は説明用で、全種類のグラフや気候UIを実装済みとはしない。旧履歴40節は順と操作本文を保持し、S29の後継注記だけ時制を是正した。

文書検査03はstate1253、health3638、候補/固定旧contract各2441成功、検査前後100パス不変。初稿のHTML metadata/footer版不一致は既存検査で検出して修正。ガード変更なし。17自身範囲を変更し、依存先は限定実読。資料/意図の自己評価はP270/root-review270.md、依存47範囲はdependency-review270.md。PLAN生成三点と本体/検査器/試験50パスは不変。
<!-- ACT270-CHECKS-END -->

<!-- ACT270-SAVE-BEGIN -->
C1-270 486d6d67d8beee35a9378c1ad8ab2262ef56a075 をPR23の既存branchへ保存。2026-09-24 07:31:26 UTC、固定commitの全100パスmode/size/Git blobとローカルが一致、Draft/open/unmergedを読戻した。保存直前main M250とbranch C2-260を再確認し、non-force更新した。mainへの書込み/マージなし。この実績追記もC2へ保存し、最終SHAはPR本文と外側受領票へ置く。
<!-- ACT270-SAVE-END -->

## AUD-260：完成した分析ツールの姿から設計を問い直す

### 中断後の復旧確認 CHK-028

2026-09-23 UTC、GitHub APIでprivate repo（id1373721672）とmainを再取得した。PR22は2026-09-23T14:50:16Zに統合済み。固定main M250 `eb53fe37954f58b26771cc2f5437d46ee3f32fcd`、tree `451d292912bc2d29e3333465111cacab68646feb`、親M200 `6d86fa7149fa8d2d0879a20fc3fe18241bc690e1` とC2-250 `5cf2c511a9486c4b605dee0ac971d3ab09786b87`を読戻した。全登録99パスのmode/size/Git blobはローカルと一致し、SHA256付きmanifestと完全base-0.25.0を保持した。復元・上書きは不要。local.gitのHEAD M101 `ad3494d700068d873a22ed2fbbf6f0a760a41735`を変更しない。Gitの多数差分だけで破損と判断しない。未登録pycacheは触っていない。

P260は `C:/Users/genia/AppData/Local/Temp/balloon-vision-260-20260923/`。recovery-receipt.json、observed-transitions.json、base-0.25.0が基準証拠。TEMPの生ログは永続保全を保証しない。判断・SHA・読取範囲・再現条件は本節とS34に残し、生ログが失われた場合は固定Git版と現環境から再検査し、過去の実行ログを再現したとはしない。

### 読取と設計への反映

README R0〜R5、CONTEXTの要求とRPT-043/044、DC-JUDGMENTと変更/終了規範、PLAN位置づけ/9/10/12、T-016/U-020/U-021、D-164を読み、三用途の完成行為から不足を問い直した。主担当は『利用者が候補を選べる一連の道具』を受入の戻り先とし、用途担当・数理担当・表現担当を分けてから統合物を通読した。原風資料の地域・季節区分・結論は要件にしない。原図の読取はAUD-250とWIND_REPORT_REVIEWの範囲を継承し、今回全文を再計算・再監査したとはしない。

三用途は、狭い予定時刻/機体条件を選ぶ予報比較、当時可能だった予測の評価と場の差だけを見る過去比較、数年の気象事例×機体反復による長期企画。条件・母集団・気象実現・機体実現・モデルを識別し、MCの回数と気象事例数、予報の条件付き幅と過去年の変動を分ける。モデル改良/分布/相関/MC/図を別機能の羅列にせず、候補選択→理由へ戻る→結果と判断を保存する流れへ結んだ。

### 破裂の具体案と原本の確認範囲

原Excel B `references/user_supplied/ascent_burst_gas_b.xlsx` のSHA256は `adb79c4fe2cf08ff4aa389f6bcbe39c20af723e1487c6bc1f331ef199079662b`。『破裂高度計算・統合（変更不可）』C20=5.0 µmは固定閾値、H20:I25/C21は平均径表と参照、O3:AD4は膨張から面積/膜厚/閾値、E29:E34は六つの決定論的近似結果である。標本平均・σ・Weibull適合を立証する情報とはしない。数式と保存値の読取りのみで、原本保存やExcel再計算は行っていない。元シートの『変更不可』は資料中の記述であり、現在の権限源にはしない。

膜厚閾値Hの平均μ/CVからWeibull形状kと尺度λを求める候補、薄い一様球殻H=m/(ρπD²)から径・体積・破裂イベントへつなぐ案を検討した。平均変換の非可換性、kによる逆数モーメントの存在条件、切断後の再較正、初期不成立と二重摂動を確認。SciPy1.17.1でCV=.20の正規化した演算例k≈5.7974、λ/μ≈1.0800を平均/σへ逆照合したが、実機の推定・推奨値ではない。証拠はexcel-burst-evidence.json、weibull_math_diagnostic.py/.json、uncertainty-design-review.mdとuncertainty-vision-review.md。

技術候補はPlotlyの対話HTML→Dash連動画面、固定図は同じ集計からPlotly/Kaleido、必要ならMatplotlib。Streamlit/独立地図を代替候補とし、初期に重複導入しない。公式仕様は2026-09-23 UTCに閲覧し、VISIONの出典欄へURLと支持する用途を置く。GEFS/ERA5 EDAとNumPyの仕様も候補の根拠として区別した。新環境導入、実MC、取得性能、校正、地図利用条件の全面受入は行っていない。

## ACT-260：議論できる完成像と、実装順への接続

新しいSIMULATOR_VISIONは将来の利用体験と設計案の編集元とする。PLANは工程へ短く接続し、現行構造/式のガイドへ未来のモジュールや未採用分布を混ぜない。独立用途レビューで文章・表だけでは完成画面を議論しにくい不足を認め、候補別落下集合→比較表→選択群の理由の模式図を追加する方針へ戻した。図は配置・操作を議論する説明用で、架空の科学成果を作らない。

<!-- ACT260-CHECKS-BEGIN -->
完成像全文を三用途から主担当が読み返し、用途/数理の独立レビューを反映した。模式図は同一実現値の候補対応と診断への連動を示し、実計算結果とはしない。最終の数式/原値の解釈/分母・単位の修正を本文と表示へ戻した。

既存専用環境の02でPLANを同じMDからTeX/PDFへ生成、全28頁を表示確認。欠字/はみ出し警告なし。初回通常実行はTEMPログへの書込拒否で失敗し、生ログを保持した。同じ生成処理の権限実行で成功した。Pandocの既存非推奨警告は保持。HTMLは既存Edge headlessで1440/390幅、三用途/2群切替、JS無効/印刷時の全表示、S34現在1/履歴40の順序と旧deep linkを確認。外部HTTP要求0、pageerror0。通常起動のspawn EPERMは同じ確認の権限実行で解消。実プリンタや全ブラウザの受入ではない。

validation-firstはstate1251、health3668、新/固定旧contract各2553が成功。検査前後100パス不変。版差だけの108注意範囲は一覧を点検し、今回変更/利用/依存する範囲以外の確認印は上げず保持。旧99パス/44論証IDを残し、新VISION1件で100パス/45論証。原本・本体・tests/tools・既存構造/理論ガイドなどの保護パスはbyte同一。全430回帰は前回の証拠で今回は再実行していない。

表示・数理の確認と文書整合を、科学採用/実MC/校正/新取得/性能や完成UIの受入へ拡張しない。実績の最終追記も同じ検査で確かめ、固定保存受領票と対応させる。
<!-- ACT260-CHECKS-END -->

<!-- ACT260-SAVE-BEGIN -->
2026-09-23 15:42:08 UTCの読戻しで、新branch `codex/simulator-vision-rpt043`、Draft PR23（https://github.com/GENIANY/space-balloon-simulator-jp/pull/23）のC1-260 `161aa2615ab68b9e428649de12c05dfbdc63f25e`、tree `43a5d0b6da317830247514bb7cf307abd063bd6c`、親M250を確認した。16差分（新VISION1件）、削除なし。全100パスのmode/size/Git blobが候補manifestと一致。PRはDraft/open/unmerged、mainはM250不変、local.git M101も変更していない。受領票はP260/C1-receipt.json。

最終同期でPLAN-PDF点検目的に残っていた『ACT-150時点』の古い限定を一般化し、実際の描画範囲を各ACTへ戻す記述へ修正した。旧依存の追加7範囲と17構造差分も再読し、独立担当の未解消指摘はない。validation-presaveはstate1251、health3668、新/固定旧contract各2561成功、検査前後100ファイル不変。実績追記の初回state検査では、子を持たないS34にpartialを付けた形式不整合を検出した。議論が継続する意味に合わせdoingへ戻し、検査器を変えず再確認する。この実績追記をC2として検査・保存し、最終SHAと固定読戻しはPR本文/外側受領票へ残す。

S34の完成像提示・候補保存は完了した。未回答のS34-Q1〜3とT-016は継続で、モデル/分布の科学採用、実MC、入力製品支持、完成UIの実装/評価は未完。次は模式図で候補選択に足りない判断材料を議論し、Codexが元入力→実現値→結果集合の具体例と取得支持の不足を整える。人間へは利用目的/優先と大きな代償への意見を求め、既知事項の再承認や技術調査の宿題にしない。mainのマージは人間が行う。
<!-- ACT260-SAVE-END -->

## AUD-250：風資料の問いから将来の分析システムを考える

RPT-042の原文はCONTEXT第44節。固定main M200 `6d86fa7149fa8d2d0879a20fc3fe18241bc690e1`、未統合PR22 C2-240 `da3d01931f9f0beb6a3f1329b4f8272ebfcc2615`、実tree `2ad961af35bdad1783169530cf4998725e4499a4`をGitHub連携で再取得した。全99パスのmode/size/Git blobと作業コピーのSHA256を照合し、完全base-0.24.0をP250へ保存。P250は `C:/Users/genia/.codex/visualizations/2026/09/21/01a0c475-9ac7-7852-85a1-e3a4f3188dfa/vision-250/`。local.git M101は変更しない。注入AGENTS0.20、保存候補0.24、最新の直接要求と継続許可を別に照合した。

原風PDFは114物理頁、SHA256 `d2430f5399311c767198cfa4197985b7108b4d909eff24e44e77ecf3194168d4`で不変。主担当は目的/第4章を中心にp5–6、19–28、31–32、98–99、103–104、107の本文を読み、p23/24/28/32/103/107を描画して表示した。独立担当はp1–6、15–17、33、45–53、65–99の関連本文と、p33/45/48/49/65/68/74/76/77/86/87/88/90/91/96の15原図頁を表示。全文の数値再監査や元時系列の再計算ではない。原資料内の旧別実装への指示や製品仕様は現在の操作許可・最新仕様にはしない。

| 原資料で問うこと | 比較と表示の理由 | 今の設計へ渡す判断 |
|---|---|---|
| 候補日をどこまで細かく区別する価値があるか（第4章、p19–24） | 別年検証と同じ年の候補差、全域と拡大図、区別できない粒度の表、同等なら粗くする判断を組にする | 集計の粒度を固定機能とせず、対象集合・比較設計・弱い結論へ戻る規則を分析側へ置く |
| 季節/場所をどう絞るか（図25/45、29/49） | 同じ尺度で候補を俯瞰し、選んだ地点の分布と海岸、判断用の少数値へ降りる | 単一軌道の描画から候補選択は生まれない。標本計画・地理・停止を含む集合・段階的表示が必要 |
| 取得できない上層がどれほど効くか（表16、p76） | 地域/季節/滞在時間で寄与を比べる。相殺があるので比率が100%を超えることを説明する | API上端の仕様だけで選ばず、用途での影響を測る。符号付き寄与/絶対量/分母を保持する |
| 延期で何が変わるか（図64/65、表20） | 同条件の時刻差を中央値/分位帯で比較し、予報誤差と分ける | 打上げUTC・run・valid・取得時点を分離し、基準と変更の対応を結果へ残す |
| 時間/位置の近似のどちらを直す価値があるか（表21、図66/67） | 2×2条件を同じ鉛直条件で比較し、kmと%を分け、相互作用を見る | 実行の直積を回す前に比較を設計する。二つの差を独立な正の誤差として加算しない |
| 分散の原因をどこまで表現できているか（図73、p107） | 要素を加えた落下集合を地理と重ねる。層独立の雲の狭さを比較できる | 相関や分布の意味を標本生成と結び、モデル/機体/気象の差を分けて見せる。原図の「観測」は実プロファイルからの計算で実飛行観測と区別 |

WIND_REPORT_REVIEW第8/9節には用途認識が既にあった。今回の不足は同じ教訓の欠落ではなく、それを現在の比較単位・保存単位・実装順へ使えていなかったことにある。PLAN10.5では分析計画/標本、取得保管、連続場/地表、実行/単一飛行、診断/評価、表示を必要責務として導き、実在パッケージと混同しない。風場だけを分析する経路、当時予報・再解析・観測・集計済み気候値の違いも保持する。

実コードの根拠は `environment/storage.py:load_weather` のGFS固定、`fields.py:PressureLevelField`の全量保持、`results/export.py:export_result` の毎飛行7成果物と指紋再読、`trajectory.py` の気象地形と終端/固定3状態である。10年間14,612起点×3地点×2モデル＝87,672飛行/613,704ファイルという机上算術は、保存と表示の寿命を分ける理由になる。処理時間やRAMの実測、特定保管技術の採用を行ったものではない。独立のコード読取はP250/future-structure-review.md、原図の比較設計はwind-analysis-reading.mdに保持する。原本・現コード・本体ガイドは今回変更しない。

## ACT-250：設計の具体化・表示・保存

今回の作業と次担当はHTML S33に集約する。PLAN5.2/10.5は、将来の問い→比較条件と標本→責務→現構造の壁→最初の一体成果を説明する。最小案は北海道/和歌山×冬/夏×異なる年の2起点×簡易/等温の16飛行。これは設計確認の提案で、実取得済み・季節優劣・運用確率を意味しない。予報更新/延期の別例で共通境界を問い直し、実測で次の保存方式を選ぶ。

<!-- ACT250-CHECKS-BEGIN -->
統合独立レビューで、16飛行を「8気象ケース×2モデル」と明確化し、地点間の機体条件とモデル固有値の対応を追記した。主担当は問い→比較→図→責務→次担当を読み返し、設計仮説として受け入れた。実用上の有効性は次の小比較で検証する。P250/root-review.md、integrated-design-review.mdと修正後PLANへ根拠を保持する。

PLAN最終04は既存専用環境で同一MDからTeX/PDFを生成した。全27頁を確認（03の27頁と04で画像不変の25頁、変更26/27頁の単頁表示）。欠字/はみ出し警告なし、Pandoc既存非推奨警告は保持。最初の通常TEMP書込拒否を生ログへ残し、同じ処理を通常権限で実行した。HTMLは1440/390幅、現在1/履歴39、時系列、旧アンカー、印刷/JS無効を確認。最終の実績更新後も表示と参照を再確認する。

validation-acceptedはstate1238、health3609、新/固定旧contract各2448が成功、検査前後99ファイル不変。初回のメタデータ同期中のOneDrive書込エラーと、新S33の記録h3が手順見出しを上書きする既存解析への不適合は原出力を保持し、印をファイルごとに一度で同期、記録見出しを本文の強調に直して解消した。検査器のコードは変更しない。版差だけの99注意範囲は、今回変更/利用/依存する範囲以外の印を繰り上げず保持する。

原99パスと本体/tools/tests/reference/example/既存PROGRAM/THEORYの73保護パスは不変。全430回帰は前回の証拠で今回再実行していない。新規の過去場取得/16飛行/科学精度/性能は未実施。保存後の実績追記は同じ検査と固定照合で確認し、最終受領票へ結果を置く。
<!-- ACT250-CHECKS-END -->

<!-- ACT250-SAVE-BEGIN -->
2026-09-23 12:18:47 UTC、作業branch `codex/structure-guide-rpt038`へC1-250 `61806ed807557b9c81b42bee3d10d70020c62f42`（tree `5210c0e85c35bdef6a7703be513c971fdba2f3c7`、親C2-240 `da3d01931f9f0beb6a3f1329b4f8272ebfcc2615`）をforce:falseで保存した。0.24.0から15差分、追加/削除パスなし。固定commit/treeと候補manifestの全99パスのmode/size/Git blobを照合して一致し、PR22 headも同じC1だった。Draft PR22の題名/本文を0.25.0の累積成果・検証範囲へ更新した。main M200は不変、PRはDraft/open/unmergedで、local.git M101は変更していない。受領票はP250/C1-receipt.json。

S33の読取・設計再検討・候補保存を完了とし、T-016の小比較と共有境界の実証は未実施として引き継ぐ。この実績追記をC2として検査・保存し、最終headと固定読戻しはPR本文および外側C2-receipt.jsonに記録する。自己SHAを埋めるための追記は繰り返さない。人間は提示した用途の不足や実際に選びたい条件を指摘でき、Codexは回答を必須条件にせず次の取得計画と比較設計を進める。mainの採用/マージは人間が行う。
<!-- ACT250-SAVE-END -->

## AUD-240：RPT-041の成果物判定と修復（実施前の基準）

直接依頼の全文：「現段階の成果物を，今回確認した規範に合っているかを判定し，修正の必要性の根拠とその方向性を置き，それから修正作業を始めましょう．それらが済んだことを確認したら本来の作業に戻りますが，今は病に侵されたプロジェクトを治療するのが先決です。」採否と順序はD-162、操作と実施状態はS32へ結ぶ。本節の初期判定を置いてから実体の修正を開始する。

Private repo ID1373721672、main `6d86fa7149fa8d2d0879a20fc3fe18241bc690e1`、PR22 Draft/open/未マージ、作業branch head `c1623997d4d8142f9e34ebf496e4be5d9c442bf6` をGitHub連携で再取得。全83パスのmode/size/Git blobをローカル候補へ照合し、完全比較元を外側 `repair-240/base-0.23.0` に保存した。ローカル.gitはM101のまま。会話に適用された旧0.20のAGENTSと手元0.23を区別し、直接依頼と継続許可に従う。ENTRY-01の原文は不変で、Project設定UIは今回の作業入口に使っていない。

評価の意図は、日本の任意時刻/領域で予報・過去場と厳選モデルを比較し、落下分散等から判断できる長期用途へ進むため、現在の計算・説明・運用を変更可能な一組にすること。DC-JUDGMENT、PLANの用途/第5・9・10章、CONTEXTの要求/D-156、風資料の用途、参考構造ガイドを、現実装と担当資料へ結び付けて読む。全83バイトの同一性確認を全83実体の科学的検証とはしない。

| 対象と、支えるべき行為 | 実施前の判定と根拠 | 修正方向・保持するもの |
|---|---|---|
| 本体・対応試験：局所的にモデル/環境/表示を変更する | 修正必要。dynamics.simulateに物理mode・RHS・RK4・根探索・相遷移・記録が集中。weatherの汎用照会がGFS配布軸を知り、cliがHTML/保存まで所有する。試験に通ることだけでは主要依存が階層へ反映されない | 責務に沿う下位実体へ移し、公開入口を維持。現在の固定気象/解析解/拒否条件を前後比較の基準にする。数値解法変更の受入は別に行う |
| 構造・理論・操作資料：変更対象と根拠へ到達する | 構造ガイドは色・リンクが改善したが、simulateの多数の内部関数を平面に並べ、責務を実コードの階層として読めない。実装忠実性と構造の良さは別。理論/操作は移行後の接続と現行挙動を照合する必要 | コード境界を先に設計し、全体→枝→実体を反復する図と横依存へ描き直す。式の導出・処理詳細・操作をそれぞれの担当資料へ残す |
| ENV/WEATHER：今使えるデータと照会契約を選ぶ | 修正必要。前半のgpm/圧力線形/地表橋渡しなしの試作と、後半の幾何高度/現本体契約が併存し、読者に現行規則の再構成を要求する | 現行本体・限定試作・調査/将来案の読順と適用先を明示。原取得の数値/時刻/根拠は保持。異なる製品を名前だけで互換としない |
| PLAN/課題/未知：長期用途と今の判断を結ぶ | 修正必要。PLANは「軌道本体未実装」「実装言語未決定」、第12章はM140を現在比較元とする。BACKLOG等は更新文の積上げで現在と過去の「次」が混在 | 現在の到達点と残件を先に書き、過去の検証条件は時点を明記。P0〜P6、評価の早期着手、追加実験なし、等温の拡張条件と科学未確認を保持 |
| 指示書・入口：次の判断/操作と過去の経緯をたどる | 修正必要。S番号が逆転し、本文と目次も異順。現在案内が複数文書へ長文で重複。過去手順のdoingが現在の実施待ちと混ざる | 現在の短い入口と、安定した履歴の順序を分ける。過去本文/コピー原文は保持し、残る要求の引継ぎ先を置く。担当と人間に求める判断を現在手順へ明示 |
| 原資料・固定入力・取得/モデル試作：根拠を追う | 原物の改変理由はない。固定入力と原報告は再現/判断の証拠として有用。一方、限定試作が本体と別に残る位置づけは明確にする必要 | 原bytesを保持。試作の目的/高度基準/本体未接続/移管条件を説明し、科学採用や一般運用の受入へ広げない |
| 管理規範・検査・登録簿：意味のある変更を支える | 原則と機械検査は維持する。合格は読解/責務の適合を認定しない。構造変更に伴う実在/主要API/再帰コード来歴と登録の対応が必要 | 記録・索引を新しい実体へ結ぶ。検査閾値を下げて合格にせず、従来想定の平坦なコード配置があれば理由と反例を伴って修正する |

総合判定：現成果物は有用な動作・再現の証拠を持つが、そのまま機能を追加できる構造/説明の適合には届いていない。原則の再掲だけ、機械的な分割だけ、全確認印の更新だけを治療の成果にしない。根拠の詳細と修正前の観察は外側 `C:/Users/genia/.codex/visualizations/2026/09/21/01a0c475-9ac7-7852-85a1-e3a4f3188dfa/repair-240/` のcore-audit.md、documents-audit.md、workflow-audit.mdへ保持する。これらの読取/実表示/未確認範囲は各原記録で区別し、統合後の再評価を本節へ追記する。

## ACT-240：判定に基づく修復と、成果物全体の再評価

### 比較元と作業の境界

RPT-041に従い、AUD-240/D-162と領域別の修正前監査を置いてから実施した。比較元は未統合PR22 C2-230 `c1623997d4d8142f9e34ebf496e4be5d9c442bf6`、実tree `b26ccb0517461f83490d03ae59fe46f511b7c896`。main M200、local.git M101と区別し、83原パスのmode/size/blobを固定読戻しした。今回の外側証拠をP240=`C:/Users/genia/.codex/visualizations/2026/09/21/01a0c475-9ac7-7852-85a1-e3a4f3188dfa/repair-240/`へ保存する。原資料・固定入力・既存履歴は保持し、原本の科学的な再認定、外部APIの再取得、追加の物理/アンサンブル/一般JRA・DEM実装はしていない。

### 修正案を実物で問い直した結果

| 修復前に不足した行為 | 実施した修正と、再検討 | 修正後に辿れること |
|---|---|---|
| 物理・取得・表示のどこを変更するか判断する | environment / flight / resultsへ分けた。一度目の切出しではtrajectoryに物理mode判定が残ったため、同値試験の成功後も設計へ戻った。選択済みのPhaseModel/FlightModelsと独立したBurstEventを構成し、飛行制御が個別のmodeや気体設定辞書を知らない接点へ修正 | PROGRAM全体地図→実パッケージ→担当ファイル/主要機能→横の契約を読み、法則の追加、製品規則、数値法、表示の各変更を分けて考えられる。任意状態のプラグイン完成とはしない |
| 一般的な数値算法の保守を本体から外す | D-163でSciPy RK45の適応刻み/dense outputとbrentqを採用。支持不足時の最後の採用点、破裂での再初期化、地形の有限な接触判定は本体に残す | THEORYで式と数値誤差、PROGRAMで委譲先、COMMANDSで依存版/設定、結果来歴で実行条件へ戻れる。性能改善を測定済みとしない |
| 実際の停止を正しく説明する | 独立レビューで、放球時の根0を後の丘との接触と誤認する例、記録検証前に時刻/歩数を更新する例、破裂後の必要量欠測で到達済み点が失われる例を検出。方向付きの根区間と採用の一括更新、破裂前後の同時刻2状態へ修正 | 終端時刻・採用歩数・最終記録・イベントが対応する。等温上昇の破裂と気象上端が一致する場合の試行支持不足は旧版でも再現し、上端余裕と契約の制限として明記。外挿で成功へ変えない |
| 今使える仕様と長期用途を取り違えず読む | ENV/WEATHERは現本体→用途/拡張→旧試作の順へ再配置。PLANの言語未決/本体未実装/M140を現在値とする案内を修正し、課題/未知を到達点と残件で読む形へ整えた | 地上〜上空/任意時刻の場、予報更新と過去場の別用途、比較・落下分散へ至る順序を保持する。旧gpm試作や半月風DBを現行の瞬時場と混同しない |
| 現在の依頼を読み、過去の経緯を上から追う | 短い現在入口とS00からの履歴を分け、目次/本文の順序を一致。旧原文・状態を変えず、8つの未完了旧手順から現在の引継ぎ先を付した | README→現在目的→S32で次担当/入力/操作/期待/停止/実績を見つけられる。過去のdoingやマージ指示を現在の依頼として再実行しない |

ここでの適合判断は、名前や検査数だけから行っていない。rootは最終コードの飛行制御とモデル/環境/結果の接点、ガイドの全体地図と枝、次変更の案内、数値の式と入力契約、現在入口と履歴を実読・視認した。担当者の6つの利用/変更場面による読解とも突き合わせた。構造ガイドは実体の階層と主要依存を辿る資料へ戻り、計算手順の長文は実装ノート/理論へ分けられた。これはユーザビリティの被験者試験や、将来拡張の無修正保証ではない。

### 証拠と受入の限界

- 本体担当の最終回帰96件は失敗/skip0、対象24ソースは実行前後同一。5つの旧基準との数値移行では終端/停止理由を維持し、完走4例の記録は破裂前後2相により各1点増えた。許容差、実差、入力/依存版は`core-test-results.json`・`scipy-transition-results.json`へ保存した。
- 構造だけの中間段階では固定5例・1,804記録点のresult全体一致を観測した。ただし第二段構造修正時のソース一式を退避しておらず、この中間段階だけを完全に再実行できるとはしない。最終24ソースは`core-final-source/`とhashへ保存。最終版の再現と、中間観察の証拠強度を区別する。
- 独立読取・反例は`numerics-independent-review.md`と再確認3例。独立した等温場の閉形式による全飛行時間も5条件で照合し、最大刻み73/17/3秒で誤差約0.00699/0.000226/0.00000109秒を観測した。初回の過度に厳しい診断閾値で失敗した出力も保持する。これを実気象の精度や全条件の誤差保証へ拡張しない。
- PROGRAM14頁、THEORY11頁、PLAN23頁を専用環境で再生成した。元TeXまたはMDとPDF/txtの対応・内部リンクを照合し、rootも最終の全頁をコンタクトシートで視認、PROGRAM3/9は単頁で再確認した。図中ラベルの重なりを修正した最終版に欠け/重なりは見つからない。PLANには既存Pandocの非推奨オプション警告が残るが、3PDFともOverfull/欠字警告は0。 PLAN保存直前06では進捗をS32へ集約する表現に改め、全23頁を再確認した。05の通常TEMP権限による失敗、06の同じ既存環境での成功も生ログへ残す。
- 指示書はPC/狭い画面、履歴アンカー、印刷/JS無効時の全履歴を確認。旧ID345・コピー原文128・旧状態119、歴史38手順と81子範囲の固有本文を照合した。検査印と今回追加した履歴案内を除き、旧手順本文は保持した。表示の証拠は`workflow-repaired-observations.json`、意味保存は`workflow-source-verification.json`等。
- PLAN親の実際の残部（第5/8/11章、末尾出典、子の境界）をrootが読んで、構造/理論の分担、検証と再現の計画として評価した。新PLAN-INFORMATIONと各既存子は自身の範囲で別に確認する。親確認を、参考原本の全面監査や外部仕様の最新性・科学精度の認定へ広げない。

<!-- ACT240-VALIDATION-BEGIN -->
全回帰02は430件・失敗0・skip0で成功し、実行前後99パスのhashは不変だった。初回01の426件・失敗8・skip0のログも保持する。初回失敗は、PLANが常に未確認という実資料への固定、親子確認版が偶然同じというfixtureの前提、完全SHAをheaderだけへ要求する表示試験に分類した。独立診断を先に置き、未確認/期限/親子/継承を隔離fixtureへ移し、main照合は現在の手順入力を対象にした。旧receiptや過去欄だけに正しいSHAが残る反例も拒否する。限定17件も成功し、両試験・両検査器の実行前後hashは一致した。検査器本体・期限閾値・拒否保護は変更していない。

state/health/新旧固定contractの遷移検査も成功。validation-02はstate1220、health3667、新旧contract各3033項目で、新旧結果は一致した。限定修正と最終検査の生ログ・受領票はP240のmanagement-selected-01、regression-01/02、validation-02へ保存。以後の実績追記に対しては管理・遷移・表示の必要な検査を再実行し、コードが不変なら全回帰を繰り返して成功数だけを増やさない。

独立横断レビューでは、別製品追加、物理拡張、数値/イベント、固定例と途中停止、長期用途の5場面を図→契約→実体→試験/判断で照合した。全飛行の試験入口が誤った「同上」を指す1件を修正し、再確認済み。依存コードレビューでは、気象試験2箇所のpatch先を実lookupへ直してdecoder不呼出しを明示し、43件成功を別受領票へ保存した。これらから未解消の修復依頼は残っていない。

版数による点検候補93範囲は、過去の子手順/付録、不変の管理・生成/試作、原資料/固定入力/外部出典に分けて選定した。意味に影響した依存は再読し、旧科学・旧操作の再実行や外部再取得は今回の修復には不要とした。検査上の期限超過と初回未確認は0。科学的な全面受入をした意味ではなく、版数だけで残る確認印を更新しない。判断の観察は`root-reassessment.md`へ記録する。
<!-- ACT240-VALIDATION-END -->

### 全体評価と次への境界

必要とされた修復は、役割分担と説明、現在/履歴、数値処理と結果の整合を一組で扱うことである。上の実物読解と独立横断確認、全回帰から、今回検出した不一致に対する修復は完了したと判断する。実装の変更理由が実階層に現れ、説明・入力/停止契約・履歴と次判断が対応したことが判断の根拠である。将来機能や科学精度は別の残件として保持する。作業branchへの保存と固定読戻しが済むまではS32を閉じず、その照合後に本来の設計・調査へ復帰できる。

再開後のCodexは、長期目的から環境経路と比較・落下分散の設計を組み立てる。現在の限定GFS本体を拡張する入力/高度/時刻契約、過去場・モデル面・地形の不足と導入順を、風資料の用途へ結び直す。取得/実装上の技術調査を人間の宿題にはしない。目的や大きな代償の選択が必要になった時点で具体材料を示して議論する。

<!-- ACT240-SAVE-BEGIN -->
2026-09-23 11:14:01 UTC、作業branch `codex/structure-guide-rpt038`へC1 `e844c24aeb7d6fcc71dc6980c658391b9ca8a345`（tree `ec5c037c4c3d7e9d41015bf761a9797b6aee30af`、親C2-230）を保存し、Draft PR22を更新した。宣言全99パスのmode/size/Git blobを候補manifestと固定treeで照合し、一致した。mainはM200不変、PRはDraft/open/unmerged。受領票はP240/C1-receipt.json。local.git M101は変更していない。

この技術・意味・表示・保存の証拠に基づき、T-015/S32の有限な修復を完了と判定する。実績追記は別commit C2として同じbranchへ保存し、その固定読戻しと最終headをPR本文/外側C2-receipt.jsonへ置く。未来の自己SHAを本文へ埋めるために無限追記しない。人間は修復結果の有用性と採用をレビューしmain統合を判断する。Codexの次成果はCONTEXT第1節/HTML startへ記録した設計表と小規模実取得・再実行例であり、新しい物理モデルや全経路を今回完成したとは扱わない。
<!-- ACT240-SAVE-END -->

## ACT-190：S23統合と本実装準備・予報時刻計画

RPT-036の報告全文304bytes/SHA256 768b99ed4991cd7cf8ca847940b6222e66c7dbeb35d7bf474daa9bb2648d552dを読取。原文は外側evidence/report-S23-original.txt。直接依頼は議論/作業継続と資料準備であり、ガイド本文の今の執筆ではない。RPT-022/028/029のCodex保存・人間mainマージを維持する。

CHK-025：Private repo ID1373721672、main M180 7367b5ad86e536e6ef2a4c53c3b62b80fea5845d、tree 309de08c7e39937d6945bcb81dd70843b3904a96、2親M170/C2 1925e793e3e6002fd6674b682dba99b2f20a33f3、PR19 merged at2026-09-23T02:26:59Z、branches=mainのみ。全53パスのmode/size/Git blobと手元bytes一致。local.git HEAD=M101は同期しない。外側P190は C:/Users/genia/.codex/visualizations/2026/09/21/01a0c475-9ac7-7852-85a1-e3a4f3188dfa/p1-forecast-plan-0.19.0/ 。base-0.18.0を完全保存し、原GET/照合はevidence/M180-remote.json・M180-local-hashes.jsonへ保持。

### 判断・準備・限定実装

<!-- ACT190-RESULTS-BEGIN -->
D-152：理論/構造/コマンドの必要内容、根拠、既存材料、不足、着手/受入をCONTENT_MAP第5節へ整理した。詳細出典はdoc-readiness/readiness-review.md・source-receipt.json（固定19資料）。最初の本体機能の作業依頼に該当説明を同時に含める。ガイド本文/直接TeX生成/本体索引/科学受入は未着手。

D-153：tools/plan_gfs_forecast.pyとtests/test_gfs_forecast_plan.pyを追加。全飛行時間窓を同一runの予定validへ対応づけ、毎時/3h刻み・端点・内部欠落・未配布・将来情報・明示fallbackを検査。最新は入力inventory内のみで、run/snapshot ageを返す。D-151の運用側ではallow_older_run=trueを明示設定して古い完全runも利用する案とし、毎回承認は求めない。required_fieldsは宣言で、データ能力の確認ではない。ENV/BUILD/WEATHERへ現在の候補契約と残件を記録。

forecast-plan-evidenceに35限定試験成功（skip0）、通信禁止の実JSON CLIを2回実行したstdout一致・欠時刻exit2・不正期間exit1、新2ソースとcompose依存の前後hash一致を保存。audit-evidence/planner-independent-review.mdに独立384時間窓・必要lead欠落5例・型変異280例の期待一致を保持。提供予定軸はEMC/NCO一次ページで再確認したが、新規気象データを取得した結果ではない。

期限9 scopeの全本文/コードをaudit-evidence/expiry-and-time-contract-review.mdへ意味レビュー。既存ecCodes環境・通信禁止で保存GFS3ファイルを全復号し、417メッセージ/33777値、地下値144/142/142と原hashを確認。runner/test_contractは静的読取を全回帰へ接続。歴史出典の外部確認日を新規調査日に置き換えない。現在案内の旧手順・S25追記先の残存を独立レビューで訂正し、旧コピー/操作原文を保持。
<!-- ACT190-RESULTS-END -->

### 読取と継続性

README R0–R5、CONTEXT1–3/方向、PLAN位置づけ/9/10章、台帳、MAP情報依存、CONTINUITYの実体/説明/入口、DC開始/終了と説明規範を読取。日本向け・無償/特別資格不要・厳選モデルの目標とP0〜P6、P1からの評価、T003→T006→T005/011の前提を維持する。PLAN3/5章からの文書要件抽出は管理要件の棚卸しで、親PLANの科学全文受入ではない。PLAN MD/TeX/PDFと原Excel、初回未確認3範囲/2026-10-01期限を保持。新たな生成・PDF視認・外部UI確認なし。期限9範囲はaudit-evidenceへ実読根拠を残す。

### 検査・保存

<!-- ACT190-CHECKS-BEGIN -->
Windows/Python3.12.12の全回帰318件成功、失敗0・skip0、wrapper 318.766秒。宣言55ファイルの実行前後hash一致。state 890 / health 2937 / 新旧contract各 1809 とdiff checkに合格。旧125コピー原文/既存コードと試験/PLAN三点を保持。初回管理検査はHTML footer版とBUILD末尾空行を検出し訂正、原失敗はevidence/initial-check-failureへ保持。検査器変更なし。既知のWindows一時dir制限に対して許可済み回帰をrepo外tempで通常権限実行し、ACL/Git/依存環境は変更しない。初回未確認3範囲と期限を保持。結果記録/C1追記後は管理検査と試験済みコード/入力のhashを再照合し、最終実数は受領票へ保存する。
<!-- ACT190-CHECKS-END -->
<!-- ACT190-SAVE-BEGIN -->
2026-09-23T03:06:13ZにDraft PR #20（https://github.com/GENIANY/space-balloon-simulator-jp/pull/20）を作成。C1 42ad6e379dc68de1cdbd01104161530e40226159、親M180 7367b5ad86e536e6ef2a4c53c3b62b80fea5845d、tree b7ca002d2e3644c75e717768f1378ecc91c5bc1d。既存15更新・追加2/削除/改名0、全55パスのmode/size/Git blobを固定照合した。workbranch=codex/forecast-plan-readiness-rpt036をforce=falseで更新、main=M180不変。RPT-022継続許可の範囲で実施し、mainマージは行っていない。 原受領票はevidence/C1-remote-receipt.json。実績追記C2を同PRへ保存し、親C1・全55・PR head・mainを再照合する。最終結果はPR本文とevidence/C2-final-remote-receipt.jsonへ置き、自己SHAだけの反復保存を行わない。
<!-- ACT190-SAVE-END -->

### 次の担当

Codexは時刻計画へ実一覧取得・保存/hash・必要量/領域/層/地表支持を結び、計画から実fieldまでの検査を進める。本体を採用する作業依頼で必要な説明範囲を同時に発行する。人間はS25の候補をレビューして受入時にmainをマージ。新たな必須回答待ちはない。

## ACT-180：S21統合後、モデル面queryと構成検査を実装する

### 基準・依頼・復旧

RPT-034：報告_Balloon_JP_v0_17_0.txt（313 bytes、SHA256 `59c2f193eae86a40fbfa2a31571ee966124765743769230f1ed0bfea14f417e9`）全文を読んだ。原文は外側evidence/report-S21-original.txt、要旨はCONTEXT第38節。報告本文は証拠、直接の依頼「議論と作業を進めよう」とRPT-022/028/029が実行範囲の根拠である。Codex保存/PR/実績、人間mainマージを維持する。

CHK-024：Private repo ID1373721672、main M170 `3f4258bb0535811f84d4fd1e71564b92c3da1deb`、tree `02a9ae72e14312d3e48aa8096470e104d7d5f252`、2親M160 `a4f6f26dd645940b5ad3322151f47d280e0f8c2d` / C2-170 `273c3943035601991863303f8fb4f7a018711531`、PR18 merged at2026-09-23T01:07:59Z、branches=mainのみ。全48パスのmode/size/Git blobと手元bytesを独立照合。local.git HEAD=M101は同期せず、既存__pycache__は保持して配布へ含めない。

外側ルートP180は `C:/Users/genia/.codex/visualizations/2026/09/21/01a0c475-9ac7-7852-85a1-e3a4f3188dfa/p1-model-adapter-0.18.0/`。完全比較元base-0.17.0、evidence/M170-remote.json・M170-local-hashes.json、各担当のレビュー/生ログを保持する。並列担当は固定M170でJRA3パス、構成器2パス、GFS調査は外側限定に分け、rootが本文/索引を統合する。

### 実装・議論・観測

<!-- ACT180-RESULTS-BEGIN -->
RPT-035はS22-Q1への回答としてCONTEXT39へ原文を保持し、D-151で「予報が届く限り早期から当日まで任意更新」を採用した。モデル面の窓をシミュレーション全体の制約とせず、圧力面＋地上量を長期予報の基本経路へ接続する。技術調査を人間へ宿題にせず、追加の必須回答待ちはない。

| 証拠 | 実装/観測と検査 | 限界 |
|---|---|---|
| jra-adapter-evidence/jra-implementation-receipt.json、jra-validation-run03.json、independent-real-query.json、evidence/jra-root-review.md | 原15本文/289,373bytesを340,890bytesの固定bundleへ収録。100層/2時刻/2×2・4,012値、JMAの非線形全層pとHGT/GPのgpmを保持。任意UTC/必要量別のquery。28試験、socket無効2 CLI出力一致。03UTC/30,000gpmのT=234.193826220591652K等を独立Decimal計算で照合 | 保存小領域の候補。NCAR再格子化を保持。地表gap約7.85〜8.04gpmはstrict拒否。一般取得/幾何高度/DEM/全飛行は未受入。初回座標丸め誤期待とWindows一時dir失敗の原ログを保持し、期待値/実行境界を訂正して再実測 |
| composition-evidence/report.md、run-01、review/composition-review.md | 速度指定/準定常/慣性を段階別に共有部品と合成し、必要field/状態/parameterと評価順を導出。24試験、独立15例と576変異（560理由付き拒否/16有効、未処理例外0）。簡易u/vのみと湿潤/Re/径破裂を区別。実JRAの02:17:13UTC queryにも接続 | 静的構成と実queryの能力照合。力学評価/solver/イベント実行/全飛行/科学採用は別。固定径で径破裂の体積依存を回避する経路は拒否するよう限定試験中に訂正 |
| gfsmode-research/gfs-model-report.md、http-ledger.json、verify-saved.json | 既存balloonwx/netCDF4の人工Range成功。実nativeのNOMADS256KiB後に接続失敗、公式S3で320KiB後に負Range。原範囲だけで失敗再現。通常0〜12hと別NACC0〜24hを区別。80mAGLの5量/45有限値を追加確認。controlled22 HTTP（200×12/206×9/接続失敗1）、保存body1,111,425bytes。NOMADS最小完了後10.091778s | 完全native metadata/1列未復号。Windows long32bit/castとの整合は原因仮説。NACC同一raw/層/処理は未検証。80mは地表連続/DEMから80mの受入ではない。追加導入/全球取得なし |
| forecast-horizon-research/forecast-report.md、claims-and-sources.json、http-ledger.json、offline-inspection/replay.json | 固定20260922/00 f381/f384をidx確認後、10hPaのHGT/TMP/q/u/v・3×3を取得。validは10/07 21UTCと10/08 00UTC。各932bytes、計10message/90有限/欠測0。controlled6 HTTP200/119,761bytes、NOMADS最小完了後10.101026s。ネット無効2独立復号JSONは同SHA256 1201dac62ce3d182e1c1aa4c87c8e473bce129803bcadae873680a38d12a9289 | 1層では30,000gpmの上下を挟めない。384hはinitからの上限で、飛行終端と時間余白が範囲内で全支持が必要。全209validの取得/全層/地表/一般cache/16日精度は未受入 |

JRA候補は既存GFSの数値/時刻/支持helperを使用し、構成器は独立した標準lib静的検査として依存を明記。今回の追加は計5パス（新tool2/test2/input1）で、旧48パス/39論証は保持する。外側診断は成果の根拠であってrepoの現役一般取得器ではない。各reportに原bytes・版・実行入口・寿命/次判定を残す。
<!-- ACT180-RESULTS-END -->

### 継続性と期限点検

README R0–R5、CONTEXT/台帳、PLAN位置づけ/第9/10章、CONTINUITYの実体/説明/入口、DCの開始終了規則を読み、M170の現本文と今回依頼を照合。期限20範囲はevidence/expiry-review-scopes.jsonへ役割/現在依存/履歴/生成関係の読取根拠を残す。PLANのMD/TeX/PDFは0.15の一組と同じbytesを保持し、生成・全頁表示はACT-150時点の実績。今回の再生成/新表示確認とはしない。初回未確認のPLAN残部・参考PDF/TEXと2026-10-01/利用前期限を維持する。共通ENTRY本文と既存コピー原文は保持し、旧注入AGENTSを現ファイル更新で消せたとは扱わない。

### 検査と保存

<!-- ACT180-CHECKS-BEGIN -->
Windows/Python3.12.12の全回帰283件成功、失敗0・skip0、wrapper 331.829秒。実行前後の宣言53ファイルはhash一致。state 854 / health 2847 / 新旧contract各 1842 とdiff checkに合格。旧121コピー原文/既存コードと試験/PLAN三点を保持。独立レビューで現在案内の旧S20/S21残存を修正した。初回管理検査ではHTML版/CONTROLとRB-E02の表示印不一致、子を持たないS20のpartial指定を検出し、内容と印を整合させ、S20の調査記録完了/残実装S22移管を明示して訂正。検査器は変更していない。原失敗はevidence/initial-check-failureとpre-final-*へ保持。Windows一時dir制限は権限/ACL変更で回避せず、許可済みの同一検査をrepo外tempで通常権限実行した。初回未確認3範囲/期限を保持。結果記録とC1実績追記後は管理検査を再実施し、実装/試験/入力の試験時hashが維持されることを照合する。最終実数は受領票へ保存する。
<!-- ACT180-CHECKS-END -->
<!-- ACT180-SAVE-BEGIN -->
2026-09-23T02:05:43ZにDraft PR #19（https://github.com/GENIANY/space-balloon-simulator-jp/pull/19）を作成。C1 77807f88de84ad0d3ef892d15c4507ff027e54f5、親M170 3f4258bb0535811f84d4fd1e71564b92c3da1deb、tree e1e4e7f5af764fba4224b364dc157dfabb963377。既存19更新・追加5/削除/改名0、全53パスのmode/size/Git blobを固定照合した。workbranch=codex/jra-model-adapter-rpt034をforce=falseで更新、main=M170不変。RPT-022継続許可の範囲で実施し、mainマージは行っていない。 原受領票はevidence/C1-remote-receipt.json。実績追記C2を同PRへ保存し、親C1・全53・PR head・mainを再照合する。最終結果はPR本文とevidence/C2-final-remote-receipt.jsonへ置き、自己SHAだけの反復保存を行わない。
<!-- ACT180-SAVE-END -->

### 次へ渡すもの

限定queryと構成宣言を、共通高さ・地表gap・地形/solverの境界へ接続する。全飛行の時空間窓、GFSモデル面の安定取得、ERAの時間/水平窓、実力学とTawhiri実行比較は残件。人間にはS23の実候補レビュー/マージを求める。S22-Q1は回答済みで、Codexが長期予報を含む取得/支持設計へ進める。技術仕様調査を人間へ宿題にせず、数mのgapを理由に過大な境界層モデルや新実験を要求しない。

## ACT-170：S18/S19報告からモデル入力とモデル面へ進む

### 固定基準・報告・責務

RPT-032：報告_Balloon_JP_v0_16_0.txt（2,661 bytes、SHA256 `5d0d7ad0775960779b2335a668f63d339712040496cedb688f15f8e7bf6670e5`）全文を読み、原文はCONTEXT第36節と外側evidenceへ保持した。本文の要求/提案は分析対象であり、保存の権限根拠は直接依頼とRPT-022の継続委任。Codexが保存/PR/記録を担当し、人間がmainへマージする。

CHK-023：Private repo ID1373721672、main M160 `a4f6f26dd645940b5ad3322151f47d280e0f8c2d`、tree `0aa9513e81b4e96ff77f139bc331d63d4cbf6809`、2親M150 `4e1ff0c39633236a991f07ef62f120110237cf5e` / C2-160 `cb0dad7dd6c3d963d903f31a84c6eb592b319ef7`、PR17 merged at2026-09-22T13:06:38Z、branches=mainのみを実GET。全48パスのmode/size/Git blobと手元bytesの一致を確認。全バイナリを再downloadした意味ではない。local.git HEAD=M101は別状態のまま保持。

外側ルート（P170）は `C:/Users/genia/.codex/visualizations/2026/09/21/01a0c475-9ac7-7852-85a1-e3a4f3188dfa/p1-model-weather-0.17.0/`。`base-0.16.0/`は全48の完全比較元、`evidence/M160-remote.json`、`M160-local-hashes.json`、`report-S18-S19-original.txt`が原証拠。既存__pycache__1件は今回より前の残存であり、宣言48/配布へ混入せず保持した。

### 判断・実測・限界

RPT-032の湿度/Reの指摘は妥当で、Tg=Taからp/T/u/vだけへ限定した推論をD-144で訂正。モデル面を優先して取り込みの実際を確認し、8〜10gpm程度の残りを単純近似として扱う可能性とDEM差を分けた。Open-Meteoの低優先化、SciPy接地イベントの内部trialをD-145〜147へ記録。人間への依頼はS20-Q1の比較軸への意見として提示し、RPT-033で組合せ設計/簡易経路/レビュー要求を受領した。D-148とENVへ回答・漏れ/重複のレビューを戻した。根拠は固定Tawhiri原文とevidence/design-composition-review.md。科学採用と方針受理を分け、同じ問いを再提示しない。

| 証拠 | 実施と費用 | 限界 |
|---|---|---|
| model-input-research/model-input-report.md、sources-and-claims.json、http-ledger.json | GFS 2026-09-22/00 f003、136–138E/34–36N/9×9、5気圧面のq/RH/omega/wと2m湿度。6,350 bytes/22message/1,782有限値/欠測0。一次資料込み933,730 bytes、7応答HTTP200。保存済み同run/valid/格子のT等と対応 | 1000hPaの湿潤/乾燥密度差−0.589%は1地点の例。気球精度/球相関適用は未受入。omegaとwの符号相違を単純変換で消さない |
| model-level-research/model-level-report.md、claims-and-sources.json、http-ledger.json | NCAR JRA100層2時刻2×2/4,012値、ERA137層1列/550値。45要求993,229 bytes、HTTP200だが完全44/部分timeout1。JRA全層圧の非線形式・配布HGTとERA湿潤高さを別処理 | ERA当初2時刻2×2は60秒timeout、原部分を保持し1列へ縮小。一般取得器/時間水平4D場/幾何30km/全飛行は未受入。モデル地表gapをDEM差にしない |
| solver-research/gfs-model-range.json、gfs-atmf003-first64k.bin | native GFS atmf003.ncをRange0–65535で65,536 bytes取得、HTTP206/総7,085,209,987 bytes/HDF5署名。公式一覧のモデル出力毎時0〜12hを照合 | 変数未復号。h5py/h5netcdf/netCDF4/fsspecは未導入。全体download/依存導入なし。可否は限定読取と時間窓の次検証へ |
| solver-research/solver-report.md、source-ledger.json、solver-diagnostic-0p3.json | installed SciPy1.17.1、固定公式ソースと実装の改行正規化本文一致。平地z0=10m、下降10m/s、u=5+0.1z、step0.3sの6人工ケース | 初回2s/延長幅15mは不足で失敗し原スクリプト保持。0.25sでは丸め程度の地下しか通らず、0.3sへ変更。最終有限延長3.1mでt=1s,x≈5.5m。実地形/初期vz0の浮力離床/全飛行/着地精度は未受入 |

### オフライン再読・規範点検

GFS入力診断はsocket禁止2プロセスのJSON完全一致（SHA256 `336bcb56629a8bf818834ad3e13190556b7f50d547141440edcc093399e2235a`）。旧T等の依存はP160/forecast-research/native-subset-f003.bodyで、配布証拠ZIPへその1入力と来歴を相対配置込みで含める。JRA/ERAは全13fieldの保存raw/軸/係数をsocket無効で再読一致。SciPy6ケースもJSON完全一致（SHA256 `8acd986abf0cb2e41c23eb720605577cf1815d2a4e01690f3bbbff720fc7e59f`）。再読の絶対パス/時計の扱いは各診断器と受領票で区別し、移設後のJSON完全一致を無条件保証しない。

README R0–R5、現入口/CONTEXT、PLAN位置づけ/9/10章と依存、DC/台帳/対象本文を読み、基準M160と局所差分を比較。独立担当はHTML75 own範囲と管理コード/試験6全文を期限点検し、rootはExcel3原本のbyte同一性/用途/未再計算を確認。84範囲の期限点検を意味の読取と結び、過去外部操作を再実行した扱いにしない。旧コピー原文117件を固定。最終独立レビューでS10/S10-3/S11/S12/S14/S14-3/S15/S17の明示的な現在案内がS18/S19へ残っていたためS20/S21へ訂正し、歴史本文とコピー値は保持した。初回未確認3範囲と2026-10-01期限、PLAN0.15のMD/TeX/PDF一組、製品/試験/原本を保持する。PLAN中の入力最小案は歴史的案で、現在の詳細設計をD-144/ENVへ明示した。

### 候補検査・保存

<!-- ACT170-CHECKS-BEGIN -->
Windows/Python3.12.12の全回帰231件成功、失敗0・skip0、wrapper 280.766秒。実行前後の宣言48ファイルはhash一致。state 834 / health 2727 / 新旧contract各 1678 とdiff checkに合格。初回は原文引用の空行3箇所の行末空白をdiff checkが検出し、引用の内容を変えず整形して再検査した。原失敗はevidence/initial-validationに保持。初回未確認3範囲/期限を維持し、全48パス/39論証IDを保持。検査器/試験を変更せず実行した。結果記録と保存実績追記後も管理検査と完全M160比較を再実施し、最終実数は各受領票へ保存する。
<!-- ACT170-CHECKS-END -->
<!-- ACT170-SAVE-BEGIN -->
2026-09-22T14:24:25ZにDraft PR #18（https://github.com/GENIANY/space-balloon-simulator-jp/pull/18）を作成。C1 755287bf82892b5cc98ad2a192cee2e16382bdbf、親M160 a4f6f26dd645940b5ad3322151f47d280e0f8c2d、tree d81c1f17e9613bfb8004e656e4b3d56e6766521e。既存16更新・追加/削除/改名0、全48パスのmode/size/Git blobを固定照合した。workbranch=codex/model-weather-requirements-rpt032をforce=falseで更新、main=M160不変。RPT-022継続許可の範囲で実施し、mainマージは行っていない。 原受領票はevidence/C1-remote-receipt.json。実績追記C2を同PRへ保存し、親C1・全48・PR head・mainを再照合する。最終結果はPR本文とevidence/C2-final-remote-receipt.jsonへ置き、自己SHAだけの反復保存を行わない。
<!-- ACT170-SAVE-END -->

### 次の担当

S20はRPT-033回答済み。Codexは構成表/能力合成と衝突検査に加え、モデル面adapter・任意時刻/支持検査・GFS限定読取と窓・モデル係数の出典/原本対応を進める。少数取得の成功を全飛行の完成へ繰り上げず、取得調査だけを無期限に続けない。人間にはCodexのレビューへの修正意見があれば求め、S21の実PRのレビュー/main統合を担当していただく。新たな必須回答待ちはない。

## ACT-160：任意時刻の気象場に向けた運用仕様の確認

### 固定基準・要求・復旧

RPT-030のS17報告（報告_Balloon_JP_v0_15_0.txt、299 bytes、SHA256 `be0fab076aad76dddf0a004c3ecf97525ec3a3c242c9a3141a4e87a9dac4e679`）を読取。CHK-022でPrivate repo ID1373721672、main M150 `4e1ff0c39633236a991f07ef62f120110237cf5e`、tree `19ab40334aad1d0abb6d637b21a191e5285474ef`、PR16 merged at2026-09-22T11:06:32Z、2親M140/C2、branches=mainのみを独立GET。最終C2 `5e0c6bd216e06a172ff25b723ea74fbcd89a427e` とM150のtree、および開始時全47パスのsize/mode/Git blobを照合した。local.git HEAD=M101は保持。

完全比較元と証拠のルートは `C:/Users/genia/.codex/visualizations/2026/09/21/01a0c475-9ac7-7852-85a1-e3a4f3188dfa/p1-weather-field-0.16.0/`。`base-0.15.0/`が全47パス、`evidence/M150-remote.json`/`M150-local-hashes.json`/`report-S17-original.txt`が照合証拠。これをM101のGit差分と混同しない。

RPT-031の直接依頼をD-141/142に受け入れた。任意放球時刻・地表〜約30kmの連続場を近い目標とし、API/運用仕様は専用WEATHER_DATA_GUIDE、実装契約はENV、行動/判断はS18へ分ける。README R0–R5、CONTEXT1–3、PLAN位置づけ/9/10章、MAP依存、BACKLOG/UNCERTAINTIES/DECISIONS、DCの説明/変更/終了規則を読んだ。PLANの長期境界を専用ガイドで具体化し、既存MD/TeX/PDFは0.15.0の一組のまま保持。科学未確認の親/参考2点を再確認済みにしない。

### 調査と実測の範囲

予報、過去場、再構成を独立に担当させ、基準M150とrepo無編集・原証拠の外側保存を固定した。主担当が以下の原報告と根拠・値を読んで本書とガイドへ統合した。診断日/領域は実打上げ計画ではない。

| 証拠群 | 実施したこと | 未受入 |
|---|---|---|
| forecast-research/forecast-report.md、http-ledger.json、offline-final-validation.json | fixed GFS 00UTC/f003/004/120/123・9×9・41圧力層と地表等を復号。700message/56,700値。OM4種のendpoint差、44要求層、null/400、返却時刻/座標と派生処理を照合。03:27の上空問い合わせを原値16点から再現 | 一般adapter、地表橋渡し、幾何高度、全飛行、科学精度。Single Runsの今回の10hPaは全null |
| historical-research/historical-report.md、offline-inspection.json、claims-and-sources.json | ERA37層×00/01UTC×2×2と地表等1220値、JRA45層×00/06UTC×2×2と地表等1476値。時刻units/calendar、地下2/2・7/7、地表gapと上端支持を検査 | CDS認証job、model-level実値、月境界、NRT実値、地形/高さの統合、気象精度 |
| reconstruction-research/reconstruction-report.md、diagnostic-result.json、source-inventory.json | 固定Tawhiri5原文の読取。現候補の各列再構成と原版の順序差を人工21ケースと独立有理数で診断。時刻欠落をcoreだけで判定できない境界も実行確認 | Tawhiriコンパイル/実行、solver、地表からの全飛行。数値の差を精度順位にしない |

予報の新規26応答は200×23/400×3、971,542 bytes（GRIB4subset186,949）。NOMADSは逐次、応答完了後待機の最小10.100311秒。要求上限20MiB・timeout60秒・自動retry0。複数地点のnan個数不一致、Single start_hour拒否、Previous圧力量拒否の3原400を保持し、別の訂正要求と区別した。風向の固定公式コード追補19,358 bytesは別のguide-review-hashes.jsonに保持する。

過去場は64原応答（HTTP200×63、TCP timeout×1）、2,742,379 bytes。jra3q-v-dasは約21.047秒で失敗してbatch停止、理由付きの一回followupで回復し原失敗を保持した。公式PDFの追加描画は旧Popplerパス不存在で生成前停止し、新規導入せず本文/表情報と原PDFの確認に限定した。PDF全頁の視認を主張しない。今回要求の実測は全60秒未満だが、通信全段階の絶対deadline受入とは別。

### オフライン再読と意味レビュー

forecast-research/replay-receipt.jsonでsocket無効の3回の数値/支持/来歴一致（検査時刻除外）、historical-research/offline-replay-receipt.jsonで独立2プロセスの一致（検査時刻除外）を確認。人工診断21件は結果JSONも完全一致、SHA256 `358e6f5cbc24eecfc01af45c2f2f44b261ae714543d3231a8ec351d18f3a92b4`。具体の再読入口と出力副作用はガイド第7節。これらは外側調査器であり製品依存へ追加しない。

独立レビューは各研究dirのguide-review.md、reconstruction-research/guide-common-review.md/governance-review.md。Forecast実測endpointを/v1/forecast?models=gfs_globalへ訂正、Previous量を2m温度へ明記、風向の角度単位/符号/固定コード根拠を補完。THREDDS入口/全層JSON位置/不変地表/予定valid/期限を追加した。鉛直節点一致を1点支持と明記。S18の抽象的な近似許容質問は、任意の用途上追加制約だけを今受け、具体比較後に採否を問う形へ修正した。

期限到来のRB-sourcesは当時の一次資料/実行の区別を全文点検し、旧外部確認日を維持。tests/test_check_run.pyとinspect_gfs_fixture.pyは責務/副作用/失敗停止を読取。GFS原3入力/manifestは同一性を保持して現検査を再実行し、417message/33,777値・81列/時刻の30,000gpm支持を確認（evidence/fixed-gfs-reinspection）。現役コードを再読したことを再取得や科学検証へ昇格しない。MAPの現在PLAN案内が0.14に残っていた箇所も0.15の実績ACT-150へ修正した。

### 候補検査と保存

初回回帰は231件中230成功/1失敗、skip0、267.687秒（wrapper268.000秒）、全48パスの実行前後hash一致。固定28IDの期待値が11ID追加後の計39IDに不適合だったためD-143で比較元ID集合の保持へ訂正した。原出力はevidence/first-regression。修正後の全回帰231成功/skip0、wrapper 266.187秒、実行前後48パスhash一致（evidence/candidate_tests.json/.stderrとcandidate-tested-hashes.json）。検査器は不変。初回静的検査でfooter/状態見出し/式のリンク誤検出を本文側で訂正し、外側wrapperの子UTF-8明示も修正した。検査器は不変で、失敗を合格へ読み替えない。

全48パス（ガイド1追加）、旧47パスの存続と既存28論証IDを保持し、ガイド11IDを追加。構造変更理由はD-142/CONTINUITYへ記録。保存前のstate815/health2671/新旧contract各1787成功、diff check成功。修正後の全回帰成功は上記。候補固定と保存実績の後にも静的検査を行い、実数は各受領票へ残す。2026-09-22T12:23:56ZにDraft PR #17（https://github.com/GENIANY/space-balloon-simulator-jp/pull/17）を作成。C1 c3d4a929d28f92bfadaaef1372b7bd96c8ee565d、親M150 4e1ff0c39633236a991f07ef62f120110237cf5e、tree 428fdf1542e7f1eb54505a13213960c722ffdd97。既存16更新・ガイド1追加、削除/改名0、全48パスのpath/mode/size/Git blobを固定照合した。workbranchはforce=falseで更新し、main=M150不変。 原受領票はevidence/C1-remote-receipt.json。実績追記C2も同PRへ保存して全48パス・親C1・PR head/mainを再照合する。最終head自身と検査数はPR本文とevidence/C2-final-remote-receipt.jsonへ記録し、自己SHAだけの追記commitを繰り返さない。人間マージは未実施。

独立の最終範囲レビューはevidence/independent-governance-review.md（更新64範囲の根拠・旧コピー113個/旧出典33件/PLAN三点保持）、test-count-review.md（固定比較元の集合保持を維持）、final-user-goal-review.md（仕様から次担当への接続）に保持。Git保存では今回、自動承認による拒否や追加許可待ちは生じていない。外側payload読取の過剰並列と点検用一行コードの引用構文はそれぞれ分割読取・固定スクリプトへ訂正し、Git mutation前後の内容hash照合を維持した。これらは提供元APIの失敗ではない。

### 次の担当と成果

Codexは固定native GFSの予定valid/必要量/単位/来歴を持つmanifestと、地表→最下有効層の不足区間/変数/地形差を数値化する。限定した地表橋渡しとモデル層の具体案・追加入力/検証費用を示してから方法の採否を議論する。人間は用途上の追加制約があれば任意で知らせ、候補PRをレビューして受入時にmainへマージする。追加実験・温度差感度・Tawhiri完全実行を着手条件へ戻さない。

## ACT-150：S15統合受入と、取得経路・等温初期モデルの拡張設計

### 固定基準と実読範囲

RPT-025のS15原報告300 bytes、SHA256 `090444d98b128401e856ecc1e462e993416af9dab86d59341e830027a8684f3f`。ユーザーのレビュー/マージ/branch削除報告と、CHK-021のGitHub連携GETを区別した。Private repo ID1373721672、PR15 merged at 2026-09-22T09:11:12Z、main M140 `f8dee6cc46e772a3e38b0fbe426371fcfaf4ba93`、親M130とC2 `1c0898759fe5455eca9e4860f67c81b02952b3b5`、tree `dc3d24da74f8c4673dc1cb923285e8a67e0df809`。branch一覧mainのみ。全47パスのmode/size/Git blob SHAをローカルバイトと照合し、完全base-0.14.0を退避した。バイナリの全直接ダウンロードとは称しない。local.git HEAD=M101で、同期/履歴書換えなし。

外側証拠の基点は `C:/Users/genia/.codex/visualizations/2026/09/21/01a0c475-9ac7-7852-85a1-e3a4f3188dfa/p1-weather-access-0.15.0/`。evidence/M140-remote.json、M140-local-hashes.json、base-0.14.0が固定元。README R0–R5、現在CONTEXT、PLANの位置づけ/第9/10章、担当台帳/規範、ENV、HTML start/S14/S15/S16と今回変更箇所を読んだ。期限5範囲のコード/設定と歴史2節はevidence/expiry-review-150.mdへ記録し、S10-1の現入口と生成履歴の混同、S10-3の比較元再選択を促す古い文を局所修正した。PLAN親残部・参考PDF/TeXの科学未確認3範囲と利用前/2026-10-01期限を保持する。

### 議論の実施と採否

RPT-026は人間への依頼の曖昧さ、予報/過去データの実用経路、将来モデルと必要量/費用、地形選定を具体化する要求。D-138に戻し、S16に回答済み/現在人間へ求めること/Codexの次成果を分けた。Q6では当初、内外等温と温度差感度試験の先行を提案した。RPT-027は後からモデル追加できる設計で初期等温を正当化し、今の感度試験は不要と回答。D-139で受理し、感度先行案を取り下げた。回答前の合成計算はphysics-reviewに探索履歴として保持するが、現在の受入条件ではない。PLAN/ENVは能力宣言・状態スキーマ・熱と内圧/形状/イベントの分離を設計として示し、物理本体の実装完了とはしない。

### 実取得：予報の併設候補

Open-Meteo GFSへ35N/137E、2026-09-22 12/13/14UTCを指定し2GET。10hPa T/風/ghと地上4量はHTTP200/804 bytes、8量×3時刻が有限。gh10は31,304.35–31,318.84 API m。応答点は34.969086/136.99219。5hPa T/gh要求はHTTP200/433 bytesでも全null・単位undefinedで、必要能力を満たさなかった。UIの概算26km表記だけで10hPaを除外せず、成功HTTPだけで5hPaを採用もしない。原run初期時刻のmetadataなし。上端/全層/全飛行支持の認定ではない。

forecast-access/request-plan.json、2原本文/HTTP記録、offline-review.jsonに保存。原SHA256は10hPa `a1aa65d07cef25ad8caa6f11c19c967747cf1b964ade2dbcb709d05612eb1f2e`、5hPa `b934b9ebb4371b4242e1604d2c6d8151dca79d2cb25ba08f90ad7c95c79b68f2`。初回検査器は5hPa要求を10hPa要求の量リストで検査してKeyErrorとなった。実要求の量を読むoffline検査器へ修正し、原bytes不変・追加GETなしでnullを確認。失敗は削除しない。

### 実取得：過去条件と当時予報

historical-access/REPORT.md、verification.json、http-ledger.json、artifact-hashes.jsonと28要求/応答原本を保管。2024-01-01は診断日で実飛行日ではない。各経路3MiB/合計8MiB上限、timeout60秒、retry0、逐次取得を先に設定し、実本文合計2,841,743 bytes、HTTP200×23/206×4/404×1。説明文閲覧はこの集計外。保存28原本文のhashと数値をsocket生成無効で再検査し成功した。

| 経路 | 実取得・検査 | 本文累計と不足 |
|---|---|---|
| ERA5 / NCAR公開THREDDS | 35N137E、00/01/02UTC、37層1–1000hPa、T/Z/u/v=444値全有限 | 233,247 bytes。Z=m²/s²でgh[gpm]ではない。地表量・地下mask・領域query未受入 |
| JRA-3Q / NCAR公開THREDDS | 35N137.5E、00/06/12UTC、45層0.01–1000hPa、T/gh/u/v=540値全有限 | 113,349 bytes。gh=gpm。地表量/地下mask未受入。NC-SA条件を保持 |
| NOAA GFS / AWS固定過去予報 | init00UTC/lead3h/valid03UTC、10hPa HGT/TMP/u/vの4全球GRIBメッセージ、各1,038,240値全有限 | 2,492,981 bytes（index等込み）、4Rangeの実GRIBは2,451,735 bytes/HTTP206。元全体529,882,452 bytesは取得していない。全層/全地域/全期間の受入ではない |
| Open-Meteo GFS履歴 | 8量×24h=192値全有限、10hPa gh=31,130.44–31,173.92 API m | 成功2,131 bytes、初回40435 bytesを含む計2,166。/v1/gfsは404、公式履歴/v1/forecast?models=gfs_globalで成功。初期時刻なし・複数runの先頭を接続した系列、単一runの代用不可 |

ERA5/NCARを過去条件の最初のadapter候補、JRAを独立比較、native GFSを固定当時予報、Open-Meteoを併設候補として設計する。NCARの公開ファイル取得とログインを要するcustom jobは別。CDSの本人登録/規約同意/token設定はその別経路を追加する場合の操作で、今の開発開始の条件にはしない。NCEIにAWS30日という記載があっても2024keyが実在した事実を消さず、その逆に全期間の永久保存保証へ広げない。一次根拠と個別制約はENV/SOURCESに受入。経路が確保できたことと再解析間の科学的優劣を区別する。

### 実取得：国内地形

terrain-access/terrain-access-report.md、manifest.json、raw/、offline-inspection/、offline-replay/、replay-receipt.jsonへ保管。GSI DEM10B PNG z14の陸地/海岸/沖合3要求、合計96,019 bytes。陸地76,474 bytes、海岸19,225 bytesはHTTP200、沖合は404 XML320 bytes。256×256 RGB/PNG CRCを検査し、欠測と整数cmへ復号して2回の保存入力再読で結果一致。NoDataはRGB(128,0,0)、有効0mと区別した。海岸は有効41,329/欠測24,207、有効0m67画素。PNG埋込metadataなし。格納0.01mは精度でなく、診断点値は地上真値でない。

国内の初期adapter候補を単一DEM10Bへ絞る案は実行可能。気象ghと地形標高/軌道高さの対応、海陸湖分類/水面、終端交差はまだ必要。欠測/0mを海としない。Copernicus DSM/EGM2008を無条件の穴埋めにしない。今回の3要求に山岳/湖/全タイル境界の受入は含まない。原入力保管と小検査器の役割/再実行/後続への移管判定は調査報告とBUILDへ記録した。

### 検査・生成・保存結果

PLANのMD/TeX/PDFを既存専用Windows環境の独立コピーで再生成し、最終22頁を1頁ずつ表示確認した。MD SHA256 849386247d238a29752826221c3e5a7614043fe7b310f8d27cf81231ec18373f、TeX 2acd5812b5237fd0e511d0932ee5e881b598d23865aaa2b3aadb43afd134dc49、PDF ca02978462b8fdf35bd179810d724be11df826556afda906812152b0169fbead。初回は一時log書込権限で失敗し同じ生成を適切な境界の新規stageで再試行、stage02後にGOALSの未採用表現をD-139と整合させstage03を最終受入。補助文字抽出のU+2011差による検索失敗と限定正規化後の成功も保持。evidence/pdf-150-acceptance.json、plan-edit-final.json。生成器/テンプレートは不変、追加導入なし。

初回管理検査はhealthがHTML時系列の0.14統合SHA不足/0.15行不足を検出した。VERSION_HISTORY正本から表示を訂正し、検査器を弱めず再検査して成功。初回出力をevidence/initial-check-failureへ保管。独立意味レビューの旧S15/M130への現在案内、T-005の既済を次作業とする文、READMEの旧候補時制、S10の冒頭担当案内、U-002の登録境界を局所修正。evidence/governance-review-150.md、dependency-impact-150.md。これらは過去操作の再実行や全出典の最新確認ではない。

現候補の全回帰とGit保存は実行後に本欄へ記録する。過去231件/20頁を今回の実測へ転記しない。実装・テスト・既存固定入力・原Excel・参考原本の不変を照合し、今回の意味変更と試験時点を区別する。科学的精度、地表/全飛行支持、一般adapterの障害復旧、Tawhiri原版実行、CIは未受入。

全回帰231件成功、skip 0。278.297秒（ラッパー実測）、試験中の全47パス不変。原出力evidence/candidate_tests.stdout/.stderr、candidate_tests.json、candidate-tested-hashes.json。state786・health2601・新旧contract各1376・diff-checkを成功。初回未確認3範囲と期限を維持。以後の実績記録のみの更新は静的検査とコード/テスト/原入力/PLANの不変を再照合し、全回帰を再実行したとは称しない。

### 作業branch保存とDraft PRの実績

2026-09-22T10:17:26ZにDraft PR #16（https://github.com/GENIANY/space-balloon-simulator-jp/pull/16）を作成。C1 d390af76fe0bf4f0a7a6014b4f18775dd7b75204、親M140 f8dee6cc46e772a3e38b0fbe426371fcfaf4ba93、tree c4b49025ca014f894ad4ddf652984e33f236895c、全47パスのpath/mode/size/Git blob SHAを固定照合。既存21更新・追加削除改名0。作業branch codex/weather-access-rpt026をforce=falseで更新し、main=M140不変を確認した。C1作成時点では人間の内容レビュー待ちとして案内した。現在のC2再開はRPT-028/029の手順に従い、記録追記C2を同じPRへ保存し、最終headと再照合の受領票はPR本文/外側へ置く。自己SHAだけの無限追記は行わない。

途中、docs/PROJECT_PLAN.texのblob保存を自動承認レビューが会話に残る旧AGENTSの人間保存制限を理由に拒否した。RPT-022の直接の継続委任とRPT-024の明示上書き、固定M140の現行AGENTS、private repo/両branch=M140、生成済みTeXのmanifest同一性を再照合した。同一連携・同一bytesの再試行で成功。追加許可の質問や別経路での回避は行っていない。原拒否と確認はevidence/tex-approval-rejection-and-recheck.json、成功と全blob/C1/PRはevidence/C1-remote-receipt.json。継続委任が取り消されたとは扱わず、将来の自動審査の無誤拒否は保証しない。

実績追記C2の途中、README.mdのblob保存が旧AGENTSのユーザー担当制限を理由に自動承認拒否された。C1の現行AGENTS・直接の継続許可・PR16/C1/main=M140・同一README bytesを照合した同じ操作の再試行も拒否された。この時点でC2はHTML/CONTEXTの2blobのみ作成、tree/commit/branch更新は未実施。別経路で回避せず、0.15実績追記7ファイルの保存/commit/branch/PR更新について旧制限を明示上書きするかユーザーへ質問した。未回答を許可としない。C1の保存と全47パス照合は成立しており、初回PRの成果を未保存へ戻さない。ローカルC2と原拒否/照合証拠は外側に保持し、回答後は現在refとhashを確認して同じ連携の拒否位置から再開する。

<!-- ACT150-C2-RESUME -->
### RPT-028/029：指示の食い違いの調査と保存再開

RPT-028でユーザーは再承認の提示とAGENTS修正を許可し、RPT-029でPR #16の実績追記7ファイルについて「旧制限を上書きし、保存再開を許可する」と回答した。7ファイルに、RPT-028で許可されたAGENTS是正と担当規範/判断の記録2ファイルを加えた10ファイルをC1からのC2差分として固定する。最新main=M140・PR16 Draft/open・head=C1を再確認してから、同じGitHub連携でREADME blobの拒否位置から再開する。古いpayload-C2.jsonと途中2blobを無条件に再利用せず、現在bytesのhashで照合する。実行後のC2 SHA/全47パス照合/PR更新結果はPR本文と外側C2-final-remote-receipt.jsonへ記録し、自己SHAだけの追加commitは作らない。mainマージは人間が担当する。

現行AGENTS0.15.0とmain M140の担当規定を確認した。repoからドライブrootの12階層とrepo子ツリーには別のAGENTS/overrideがなく、global AGENTSは0 bytes、global overrideなし、確認したconfigに指示ファイル/代替名/最大読込量の設定なし。会話に注入された0.10.1の旧担当制限と原拒否の対応は観測できるが、local Git HEADの旧blobが注入元だという因果は未確認。限定調査の証拠はevidence/instruction-chain-audit-rpt028.md。秘密・認証値・無関係な設定は収集していない。

OpenAI Docs https://learn.chatgpt.com/docs/agent-configuration/agents-md を2026-09-22に読み、起動時の指示チェーンと古い指示の再読込み確認を照合した。AGENTSの現在分担を冒頭へ移し、README/DC-ENTRYで明示許可済みの旧担当差を一律停止しないよう是正。D-140へ選択肢・根拠・代償・残る読込み確認を記録した。ファイル変更だけで会話注入文や自動審査内部が更新されたとはしていない。共通ENTRY-01原文と歴史の保存操作値は変更しない。


RPT-028/029の指示是正後、全回帰231件成功・skip0、275.379秒（ラッパー275.688秒）、試験中の全47パス不変。初回はsandbox内の隔離tempへの書込/後片付けでWinError 5となり、231件実行表記・403 errors・終了1だった。原失敗出力をsandbox-failed-*へ保持し、同じ231試験を審査済みの実行境界で再実行して成功した。実repoのGit履歴・権限は変更していない。evidence/rpt028-029/candidate_tests.json/.stdout/.stderrとcandidate-tested-hashes.json、independent-review.mdを参照。以後はこの実績とC1段落の時制を記録し、state/health/新旧contract・diff-checkと実装/試験/原入力/PLAN不変を再照合する。

## ACT-140：S13統合の受入とP1環境契約候補

[更新:0.14.0] [確認:0.14.0]

### 固定基準・報告・実観測

RPT-021原報告301 bytes、SHA256 `4ad53a551edf451b3fec3fb54d7006fa1e969ef015fd9d2d83841f439d05ee15`。ユーザーの内容レビュー・マージ・branch削除報告と、CHK-020のGitHub連携による独立取得を区別した。main M130 `9ae8e7b5c7cdb74c15fdf937fd14896df51d641d`、PR14 merged at 2026-09-22T06:29:57Z、親M101とC2 `b89d0eac81cd3f626149c617b9e38f9f81b3bff8`、tree `81f417629fba09dd38e70fae1374a928cb84e998`。branch一覧はmainのみ。

固定treeの全44パス・mode・size・Git blob SHAを手元のバイト列と照合し、完全な0.13.0比較元を退避した。バイナリをすべて直接ダウンロードしたという意味ではない。原Excel3冊と参考PDF/TeXを変更していない。ローカル.git HEADはM101、開始時の作業ファイルはM130と全一致。ローカル同期・reset/clean・権限変更は行わない。

外側の実証拠は `C:/Users/genia/.codex/visualizations/2026/09/21/01a0c475-9ac7-7852-85a1-e3a4f3188dfa/p1-environment-0.14.0/`。evidence/m130-remote.jsonが取得PR/ref/commit/tree、evidence/base-hashes.jsonが44パス、base-0.13.0が完全比較元。これらを通常の開始文の代わりにしない。

### 何を判断して前進するか

S13/S11/T-014の有限受入を閉じ、既存のS14-3指示へ追加3パスと高さの未受入を具体化してから候補実装を進める。D-135は限定APIを選ぶ理由・代償・再検討点、ENVIRONMENT_CONTRACTは式・単位・品質・主要機能、PLANは中長期への位置、HTMLは操作と実績を担当する。

NCEP一次表P1-HEIGHTとOpenAI公式AGENTS S12を2026-09-22に再取得。前者はgh/gpmと幾何高度の区別、後者は起動時の指示読込を確認した。自動審査の内部原因や誤拒否なし、未知の高さ変換の採用まで結論しない。

### 点検と実行の境界

期限到達86範囲（歴史HTML75・コード/試験8・原本3）を固定M130で意味レビューし、現役性・過去の証拠・現在への接続を確認した。記録はevidence/review-expiry.json。原本同一性や歴史の読取を、科学的認定・Excel再計算・過去操作の再実行へ読み替えない。未確認のPLAN親残部・参考PDF/TeXの3範囲は保持する。BUILDに残ったM081固定CMDを現在の標準入口と読める記述は当時の入口と明記して是正する。

今回の実測は以下の結果欄。0.13の201件/19頁と実行時点を分ける。

### RPT-021時点の0.14.0候補の実測結果（後続RPT-023より前）

- 新規環境試験30件（合成26・実標本4）は全成功、skip 0。最初のsandboxではTemporaryDirectoryのmkdir/cleanupがWinError 5となり、同じ試験を根拠付きの別実行境界で実施して成功した。試験コードや安全検査を弱めていない。証拠：environment-reviewed-tests/receipt.jsonとstderr.txt。
- 独立レビューの反例で、返却dictと内部fieldの共有参照、有限入力の差/重み/結果の非有限化、巨大整数の例外分類の3群を検出し修正した。修正後の独立した合成34ケースは期待通り。environment-independent-review.jsonに前後の実測と限界を保持する。30件と34件は別の集合として示す。
- 固定GRIBの地下maskは144/142/142セル。元500hPa格子との一致と30,000gpm内挿、地下・2時間窓外の拒否を検査。CLIは通常sandboxで成功し、environment-normalized-reviewed/environment.jsonは1,239,534 bytes、SHA256 `2c448bbe8e766067433183c5c89f3be398f02e5b820dc9b289c7986f588f45d6`。無変更の原入力と来歴を保持する。
- 初回全回帰は231件中1件失敗。README本文に旧証拠IDが残り、登録された現行証拠IDを置換する異常系試験が空振りした。本文と点検台帳の証拠参照を揃え、検査器や試験を弱めず同じ全回帰を再実行した。初回原出力はevidence/regression-initial-failureへ保持する。
- 全回帰 **231件成功、skip 0**（unittest 249.800秒、ラッパー 250.078秒）。今回は0.14候補で実行した結果であり、過去の201件を流用していない。実行中の全47パス不変を照合した。原出力はevidence/candidate_tests.stdout/.stderr、環境境界/前後確認はcandidate_tests.jsonとcandidate-tested-hashes.json。実測追記後は変更した記録のstate/health/新旧contractを再検査し、コード・入力・PLAN不変を別に照合する。
- PLANは既存専用Windows環境で生成し、全19頁を110dpiで描画・1頁ずつ実視認した。日本語・表・柱脚・出典・新P1節の欠け/重なり/はみ出しなし。MD `383f88a96081789adb869583f31caad7534eee7d9c716e81f92f82bd6548e70f`、TeX `2bc66309af1a9fbceb029f163821e47773ec6657dbdb101c0228939efa507d01`、PDF `40f2d5cb20db42a436282f737a00239617a4b0c5de5121a5c46f11323c6de43a`。初回Temp権限と後続wrapper文字コード表示の失敗もevidence/pdf-acceptance.jsonに残す。生成本体は再実行で終了0、追加依存なし。
- 意味レビューで現在案内のS13残存、C1観測時刻と統合観測の混同、過去検査を現入口に見せる文を是正。HTML編集時の進捗filter部品欠落・footer・手順内見出しと履歴SHA短縮はstate/healthが検出し、部品・全文SHA・正しい見出しを復旧した。検査を弱めて通さない。台帳更新中の一時的ファイル書込み失敗は同じファイルへの再試行で成功し、最終検査で整合を確認する。

実測追記後の管理検査はstate 753、health 2543、新contract 1439、M130の旧contract 1439を全成功、diff-checkも成功。期限超過0、初回未確認3範囲と2026-10-01/利用前の期限は保持した。最終固定時に同じ管理検査とコード・入力・PLANの試験時点からの不変を確認し、外側のcandidate-receipt.jsonにZIP・全47パスの指紋とともに保存する。科学的精度・幾何高度/地表対応・Tawhiri原版実行・全飛行・GitHub CIは未受入である。

### RPT-022：保存の継続許可と議論手順への接続

2026-09-22の直接指示で保存・PRをCodexの継続責務、人間マージとする分担を受領した。0.13限定のRPT-020と区別し、AGENTS/README/CONTEXT/D-136/S15/U-008へ戻した。0.14の承認待ちは解消。main=M130/private/id1373721672とbranch一覧mainのみを連携GETで再確認し、前回の全47パス候補と受領票の同一性を検査して外側publish-rpt022/base-local-0.14.0へ固定した。実repoの.git HEAD=M101と候補作業ファイルを分離したまま保存する。

S16では議題4件を提案として記録する。Q1の主成果/優先順位は今問える。Q2の実ケース選定は原セル表、Q4の保存容量はCodexの実測後に最終判断する。Q3の未調整比較/校正方針は提案段階で、科学的採用を先書きしない。回答・採否・理由・保留・後続を同じ手順へ追記する。

前回全231試験/独立34ケース/PLAN19頁の実測は上欄へ保持。今回はRPT-022とS16による文書・構造変更を検査し、その実結果、Git保存・PRの実値と全47パス読戻しを本節/S15/外側publish-rpt022へ追記する。RPT-022検査時点ではPLAN/実装/テスト/原入力が前回候補から不変であった。後続RPT-023ではPLANを改訂・再生成し、科学的な受入を追加しない。

### RPT-023：実際の議論と優先案の修正

S16-Q1を相談パネルで提示し、ユーザーから長期設計・モデル改良幅からの逆算、気象環境の実取得試験と地形選定を優先すべきとの反論を受けた。原回答はCONTEXT第28節と外側evidence/rpt023-user-answer.txt。原版比較先行案を未採用とし、PLAN10.1/10.2に既にある責務境界と非直列工程に照合してD-137/S16/PLAN10.4/12/ENV末尾を修正した。具体的な製品・モデル・成功閾値は未採用。前の提案と不採用理由を手順内に保持する。

RPT-022反映後の全回帰231件は成功・skip0（280.692秒、wrapper281.063秒）、実行中の全47パス不変。以後のRPT-023は仕様の説明/優先と生成文書・実績の変更であり、数値実装/テスト/原入力は不変を照合して管理検査とPLAN再生成/全頁表示を行う。初回手順検査の状態ラベル・履歴表示の不一致は本文を是正、検査器は変更なし。TeX blobの自動承認拒否は旧AGENTSのユーザー担当を理由とした。固定M130の現行担当、実ユーザー継続許可、同一TeXを照合した後、同じ連携・同じ操作の再試行が成功した。別経路への迂回はしていない。保存/PRの実値は後続記録へ戻す。

RPT-023のPLAN最終生成は既存環境で成功し、全20頁を描画して1頁ずつ実視認した。日本語・表・改頁に欠け/重なり/はみ出しを認めず、旧S13固定参照を現在入口の保存手順へ是正した。MD `708ad5249f24dac32b52aecedba7332f8d974b9ecbe6606cc45f64e91b79dc22`、TeX `6bebf9f0c2a884630472af2f0def349b8572785f0235bc0960cee140ee58769c`、PDF `5213b6e58ca20a36850238f750b86519ce8c756aa0669999ff489663af4e1fe4`。証拠 `publish-rpt022/evidence/pdf-rpt023-acceptance.json`。追加依存なし、原本8実体・生成器・テンプレート不変。表示確認は科学の真偽・実印刷・別環境の受入ではない。

ENVへ将来モデル別の必要入力・単位/高度/時間支持・来歴の対応案を追加した。SOURCESのNCEP鉛直運動量表・GFS時間支持とNOMADS条件を実読。地形候補は国土地理院とCopernicus DEMの一次仕様を調べ、地表/建物植生を含む表面の違い、鉛直基準、更新/欠測、登録条件、水面判定の別責務を比較した。具体製品や物理モデルの採用、DEM取得は未実施。公開仕様の確認は実取得品質の実証と区別する。

### RPT-023・試験Aの実取得と再読

新run 2026-09-22 00UTCのf000/001/002をNOMADS公式可用一覧で確認後、旧標本と同じ診断領域136–138E/34–36N・0.25度9×9・33気圧面/量（旧manifestのschema参照）を新取得した。具体URL/量/上限は実行前の publish-rpt022/live-acquisition-rpt023/request-plan.json と attempt-02 のHTTP記録へ固定。上限2MiB/応答・6MiB合計・timeout60秒・retry0・逐次3GET。新取得を旧runの再現と呼ばない。

| ファイル | HTTP | bytes | SHA256 |
|---|---|---:|---|
| f000.grib2 | 200 | 37852 | ba0167d6925203fde737d4facbcff601ab5d6cb029876bc5a0be60499190e892 |
| f001.grib2 | 200 | 37592 | 2880605a2ebb3b99a023ce289bf067d94cfae236c1443f51ec83a33ad242797a |
| f002.grib2 | 200 | 37440 | 157455931193b70bbd2becc553d152c5cf07471a0e5c05c3e282ea896cbe2029 |

合計112,884 bytes。前応答完了から開始の実測10.109/10.093/10.094秒、全て10秒以上。別Pythonプロセス2回で接続入口を禁止して保存バイトだけを検査し、各417message/33,777値、地下132/131/131、入力/正規化出力hash一致、接続試行0。正規化SHA256 dadf16d3b61a71edbde0769bdb4a56a3aa37129637b8ce1d2f721d5722fdde9a。旧標本・実装・原本の保護9パス不変。初回は条件HTML受信後の外側器のEOF処理不具合で停止しデータGET0回。初回ログを保持し、器修正と受信HTMLの長さ/hash/本文照合後に未着手データ取得へ進んだ。

最低利用可能ghの格子範囲は各時刻56.409–1998.916 / 61.135–2004.907 / 62.894–2006.278gpm。0gpmの人工問い合わせは3時刻×81点でHEIGHT_OUT_OF_RANGE。これは地表との幾何的な距離をmで測った結果ではない。放球/地表近傍をどの層・高さ変換・地形基準で支えるかが次の具体設計課題である。30,000gpmの1内挿は成功したが、全飛行/幾何高度/地形/科学精度/一般取得器/cache障害復旧の受入ではない。

元データはrepoに追加せず、上記外側ディレクトリの fixture/ と attempt-02/ に保全した。集約は summary.json、再取得しない再検査入口は README.md と verify_offline.py。外側器は一回用の実験で、T-005の一般取得器を実装するときに必要な証拠/回帰を移管するか保持理由を再判定する。repoの再開にはここで固定した条件・結果・保存先・限界を用い、外側ログを通常の開始文の代わりにしない。

RPT-023反映後の管理検査はstate 778、health 2565、新contract 1481、M130旧contract 1481、diff-checkを全成功。初回未確認3範囲は期限2026-10-01/利用前を維持する。全回帰時点からtools/tests/referencesと生成テンプレートの対象24パス不変を照合。実取得再検査入口も追加のネット取得なしで確認した。最終固定tree照合と保存結果はS15/後続受領票へ記録する。

### RPT-023候補の保存試行・一時停止とRPT-024での再開

RPT-022の継続許可に基づく保存を実行。作業branch codex/p1-environment-rpt-021をM130に作成し、RPT-022時点21blob、RPT-023最終候補へ更新した14blobを作成した。最終候補は全47パス・差分21（既存18/新規3）。方針修正前のblobがあることを最新候補保存完了としない。

自動承認レビューがdocs/UNCERTAINTIES.csvのcreate_blobを「trusted AGENTSが保存を人間へ割り当てる」として拒否。固定M130の現行AGENTS、ユーザーの継続許可・旧制限上書き指示、ローカル/snapshot/manifestの完全同一性を確認し、同一連携・同一bytesの同操作を再試行したが再拒否。外側evidence/uncertainties-approval-rejection.json、uncertainties-retry-rejection.jsonへ原文と成功blob集合を保持。迂回なし。これは未承認の科学判断やユーザー回答待ちとは区別する。

その後の連携GETでmainと作業branchは双方M130、Open PRは0件を確認（evidence/remote-blocked-state.json）。tree/commit/PRは未作成、main未変更。snapshot-C1という外側名は当初の提出予定スナップショットであり、実在するC1コミットを意味しない。ローカル最終候補・PR本文・47パスmanifest・原ログをpublish-rpt022へ保持し、現在ref/bytesの再照合後、同じ操作の拒否位置から再開する。根拠を失う部分保存や別経路への迂回は行わない。

RPT-024でユーザーがこのターンの旧AGENTS保存担当制限の明示上書きと拒否位置からの再試行を許可した。同じ連携・同一bytesのCSV blob、続くVERSION_HISTORY/SOURCESのblob作成に成功し、拒否を解消。権限/公開/担当の拡張や代替経路による迂回はない。成功証拠はevidence/permission-rpt024.json。以降のtree/commit/PRと固定読戻しは実行後にS15/本節へ追記する。

### RPT-024後のC1保存・PR15の実績

RPT-024後の保存実績：C1 ca96c585437331a0ad7b176b9391de4ba06ba678（親M130）、tree 83ff29a5edf96a1f62024e0b66d50f7fdf85bde1を作成し、作業branchをforce=falseで更新。固定treeの全47パスについてpath/mode/size/Git blob SHAをローカル候補と照合した。2026-09-22T08:55:55ZにDraft PR #15（https://github.com/GENIANY/space-balloon-simulator-jp/pull/15）を作成、既存18更新・新規3追加。保存・PR作成の停止は解消。現在は人間による内容レビューとmainマージ待ちで、main=M130を保持する。今回の実績追記を同じPRへ保存する。追記コミット自身のSHAはPRと外側受領票へ記録し、そのSHAだけを埋めるための改訂ループは行わない。

証拠はpublish-rpt022/evidence/C1-remote-receipt.json（Git commit/tree独立GET、全47パス比較、PR応答）。作業branchの候補保存と承認済みmainの統合を分ける。上記「branch=M130、PR0件」は拒否時の歴史観測で、現在のPR状態はこの後続記録を採る。

### 次の作業

RPT-023/D-137に基づき長期到達像・モデル要求から気象/地形の環境設計と狙い付き実取得を具体化する。高さの意味・支持範囲と原版への入力対応を解消し、S14-4で固定原版実行と15便の原セル/単位/使用目的表を進める。今回の候補保存手順はHTML S15へ具体化し、過去S13の値を上書きして再利用しない。科学的採用・精度主張・main統合はそれぞれ別判定。

## ACT-130：指示から行動記録への復帰とP1の最初の実行

RPT-018をCONTEXT第23節、判断過程をD-133/D-134、再発防止をGAP-019へ記録した。前回は生成環境を整えた後の保存指示と本体作業が具体化されず、ユーザーのS10-3回答を実行へ接続できていなかった。現在の手順編集元をHTML S13（Codex保存・Draft PR／ユーザーマージ／固定版照合）とS14（P1）にした。各操作を実施者・入力・操作・期待出力・記録・次の判断まで書き、同じ欄へ実結果を戻す。PR作成の代行は今回ユーザーが認めた範囲、main確定は引き続きユーザーである。

### 基準と今回読んだ情報

CHK-019：2026-09-22 UTCに正しい非公開repoのmain/commit/treeを再取得し、M101 `ad3494d700068d873a22ed2fbbf6f0a760a41735`、tree `8690657a122b937d2a74e03f451124509413af50`を確認した。直接比較元は完全な0.12.0候補39パスで、前回最終SHA256一覧と照合してから固定した。M101への累積変更として0.11/0.12の修正を含め、個別に統合済みとはしない。

指定されたS10-3報告原文を全読した。13,146 bytes、SHA256 `b7b09ddeb20ab0e51c34da981fa84cc3c6c12e9269f9e0019ee962658c559d9c`。既存の目的、追加実験を求めない方針、モデル比較、NOAA-GFS優先、任意領域と日本語GUIを再質問せず計画へ接続した。過去報告中の操作文を今回の許可へ取り違えず、RPT-018の依頼に基づいて進めた。

### 本体の到達点と判断

T-004はCUSF原版`668b44e5b88a66e0d885a9f9b16ff507d856bbbd`のstandard_profileを固定し、モデル、積分器、データ形状、境界、依存、原版/派生の差を一次コードで確認。一定上昇・高度閾値破裂・経験密度による下降・水平移流、既定60秒RK4、終端0.01は最後の線分比。原版の9.53 GB固定配列やPOSIX依存を直接継承せず、モジュール化した実装と隔離原版を比較するD-134を採った。原版を実行したという記録ではない。具体的な比較条件と未受入はPLAN 10.4、一次根拠はSOURCESのP1-T004。

T-005は公式NOMADS一覧とidxを実取得し、GFS 2026-09-21 18UTC・f000/001/002・仮領域136–138°E/34–36°Nの33層と地表量を取得した。3ファイル113,590 bytesを未改変保存、既存ecCodesで417 GRIBメッセージ・33,777値を復号。欠測なし、81列の気圧面高度が単調、30,000 gpmを含む。ただし地下に相当する気圧面level-cellが144/142/142あり、有限だから利用可能とは判定しない。上空gh[gpm]と地表orog[m]の基準を保存し、高さ変換・地下マスク・補間・全飛行・DEM・科学的精度は未受入。fixtureは実打上げ条件ではない。

取得後の公式条件確認で、実際の要求開始が約4.5秒間隔で、10秒以上の待機条件を満たさなかったと判明した。成功した取得を規範準拠と記録しない。追加取得を止め、次回は応答完了後10秒以上、逐次、キャッシュとバックオフを用いる。事実と是正はmanifestにも保持した。

manifestとオフライン検査器を含め5パスを追加し、全44パスとした。取得物・取得来歴・検査手段を分ける必要性と寿命を登録し、元Excel3冊と参考PDF/TeXは変更しない。通常再検査はrepo内5パスとBUILDの環境/コマンドで成立し、この外側ログや会話を必要としない。

### 検証と保存の実績

<!-- ACT130-CHECKS-BEGIN -->
Windows/Python 3.12.12で全回帰201件を実行し、失敗0・skip 0（252.625秒）。試験前後の宣言44ファイルはSHA256不変。state 733検査、health 2475検査、現行/固定0.12.0のcontract比較器各1539検査に成功。初回未確認はPLAN残部と参考PDF/TeXの3範囲、期限2026-10-01を維持。新規PLAN-SOURCES範囲で旧出典と今回の一次確認を分離し、親の未読科学を確認済みにしなかった。各大項目の5欄は本文にも保持するが、機械契約はS13/S14の実行小項目を登録し、親子で同じ操作欄を二重計数しない。既存の必須範囲は削除していない。

正式GFS検査器は正常1・異常12の13ケースで期待どおり。13は管理回帰201へ合算しない。気圧層一覧の欠落/不整合、非UTC・timezone欠落・秒付きrun、既存出力、入力改変、単位/field不正、repo内出力を拒否。入力4ファイルの不変、既存出力の保全も確認。来歴の復号受入であり、地下マスクや高度変換の実装済みを意味しない。

専用Windows環境でPLAN 0.13.0のMD/TeX/PDFを独立コピーから生成、終了0、19ページ。全19ページを1600px PNGに描画して日本語・表・URL・柱/脚・改ページを実見した。最終冒頭修正後は18頁の画像が受入済み画像とバイト一致、変更した物理3頁も再目視して不具合なし。入力MD/template/buildのコピー元一致、TeXのCRLF 0を確認した。今回のPDF版と科学的妥当性は別判定である。

初回の制限環境ではWindows一時領域へのログ出力が拒否され、生成は終了1、tlmgrもHKCU書込み用openのエラーを返した。失敗ログをevidence-build-restrictedへ保持し、許可された専用環境を実行する権限で再実行して正常生成した。成功だけへ書き換えず、制限環境での可用性を保証しない。既存の--no-highlight非推奨警告は保持した。

期限RB-S10/RB-sources/CHECK-RUNNER-TESTと、CONTROL/DECISIONS等から波及する旧手順・PLAN/作業依頼書を意味レビューした。旧手順の実行者・SHA・コピー原文91欄は保持。9件の管理検査/試験コードは0.12から不変を確認し、今回の科学結果として過去の検査を流用しない。現在の34パス変更は既存29更新と新規5追加、削除・改名なし、論証28IDを維持。最後の実績記入後に同じ管理検査/完全比較/diffを再実行し、コードが全回帰から不変であることを証拠一覧へ記録する。
<!-- ACT130-CHECKS-END -->

<!-- ACT130-GIT-BEGIN -->
S13-1の最初の試行でCodexが作業ブランチをM101から作成した後、最初のblob作成は自動承認レビューに拒否された。理由は旧AGENTSの保存・PR担当制限であり、内容不備や検査失敗ではなかった。回避せず明示許可を質問した。当時は内容commit・PR作成・マージが未実施で、拒否後の再GETでは作業ブランチとmainの双方がM101だった。拒否原文と停止位置はevidence/publication-review-block.jsonへ保持した。

その後RPT-019で検査済み34パスの保存とDraft PR作成について明示許可を受領した。既存ブランチとmainのM101一致、同headのOpen PR不存在、前回候補44パスの一致を再確認して再開した。

RPT-019後にもUNCERTAINTIESとCONTINUITYのblob保存が一時拒否され、対象34パスと許可の再照合後、同一操作の再試行で成功した。最後のtools/inspect_gfs_fixture.pyは再試行でも拒否され、33 blobのみ保存・commit/PR未作成の位置で停止した。その後、旧AGENTSの制限を今回の34パス保存・commit・branch更新・Draft PR・実績追記について上書きするかを明示して質問し、RPT-020でユーザーが『旧制限を上書きして、記載した操作を許可する』と回答した。この追加回答後、残るblob・tree・commit・branch更新・Draft PR作成を同じ連携で実行した。mainマージや回避経路は用いていない。

<!-- ACT130-C2-RECEIPT-BEGIN -->
2026-09-22T03:34:55Zの受領票：Codexが既存29更新・新規5追加の34パスを保存し、初回提出C1（W130）`afbc2417d94fe9ec5e40eabb66547a079291904d`、親M101 `ad3494d700068d873a22ed2fbbf6f0a760a41735`、tree `7282c1a1abcbc11ff982acc371227c41a6fa1a3f`を取得した。Draft [PR #14](https://github.com/GENIANY/space-balloon-simulator-jp/pull/14)、base=main、head=`codex/p1-action-rpt-018`。固定C1のcommit/親/treeと全44パス・mode・size・Git blob SHAをローカル候補のバイトから計算した値へ照合した。バイナリもGit同一性による比較で、GitHubから全バイナリを直接ダウンロードしたという意味ではない。実値と原出力への入口はevidence/C1-remote-receipt.jsonへ保存した。C1は候補提出であり、この実績を戻す記録追記C2の自己SHAや検査成功を先書きしない。C2保存後の最終headと全44パスの読戻し結果はPR本文と外側の最終受領票で示す。ユーザーのレビュー対象は、その照合済み最新headである。mainのマージとS13-3の統合版照合は未実施。ユーザーへ別PRの作成を求めない。
<!-- ACT130-C2-RECEIPT-END -->
<!-- ACT130-GIT-END -->

証拠の外側保管先は`C:/Users/genia/.codex/visualizations/2026/09/21/01a0c475-9ac7-7852-85a1-e3a4f3188dfa/p1-action-0.13.0/`。base-0.12.0は完全比較元、researchは一次読取・NOMADS取得時刻/idx/原出力・正常/異常実行、evidenceは最終管理検査と回帰、generation-lf/evidence-lf/renders-lfは文書生成・ログ・描画である。外側の原出力が失われた場合に再実行で過去事実を置換できるとはしない。

### 次に実行すること

CodexはS14-3で、既存fixtureから地下面を除外し高さの種類・UTC・単位・範囲外を明示する最小環境契約と正規化処理を実装する。必要な理論/入力/API/依存の説明と合成場の境界試験を作成時から同じ変更へ入れ、その後S14-4で隔離原版との比較と15便の入力意味表を進める。追加実験をユーザーへ要求しない。RPT-019/020に基づく保存とDraft PR作成は完了し、ユーザーの次の操作は[PR #14](https://github.com/GENIANY/space-balloon-simulator-jp/pull/14)をS13-2の詳細手順でレビューし、マージを判断することである。C1と記録追記C2を区別し、PR本文に記された最終headの照合結果を確認してから操作する。P1の解析・候補実装をこのマージ待ちで停止しない。

## GEN-120：専用Windows環境による計画書の継続生成（0.12.0の履歴）

以下の「今回」「現在」「次」は0.12.0作成時の記録。現行の作業順・権限・成果はACT-130/S13/S14。

RPT-017をCONTEXT第22節へ、採用・不採用の理由と再検討条件をD-132へ記録した。ユーザーは文書生成環境の整備を明示的に依頼しており、必要な依存をrepo外の専用領域へ導入した。HTMLの指示書兼開発記録は直接改訂し、PLANは既存のMD→TeX→PDF経路を維持する。現在の入口はHTML S12、課題はT-012。0.11.0の未統合是正は今回の0.12.0へ継承した。

### 固定基準・直接比較元・実行環境

CHK-018：2026-09-22 UTCにGitHub main refをGETし、M101 `ad3494d700068d873a22ed2fbbf6f0a760a41735` の継続を確認した。PR13/tree/全39パスの照合はCHK-017を継承し、新しい統合の観測と混同しない。直接比較元は変更前の0.11.0完全39パスを前回の最終SHA256一覧と照合したコピー。M101→0.11.0と0.11.0→0.12.0を二段で比較し、0.11.0単独のGit統合を記録しない。

専用配置は `C:/Users/genia/.local/share/balloon-docs/`。Pandoc 3.11、TinyTeX-1 Windows v2026.09 / TeX Live 2026、XeTeX 3.141592653-2.6-0.999998、Noto Sans CJK JP/Noto Sans Mono CJK JPを使用した。Pythonは既存のMiniforge 3.12.12で、文書生成器に必要な標準ライブラリだけを利用。追加Pythonパッケージ、永続PATH、OSフォント登録、実repoのGit書込みは行っていない。コマンドごとにPATHとFONTCONFIG_FILEを指定する。版固定URL・SHA256・フォントcommit・再実行手順はBUILDへ集約した。

PandocとTinyTeX本体は公式GitHub release APIのdigestと配布物SHA256を照合。フォントは固定commitから取得したSHA256を記録した。追加TeXパッケージはCTAN HTTPS経由の今回の状態であり、tlmgrが `not verified: gpg unavailable` と報告したためGPG署名検証済みとはしない。取得・導入ログとtexlive.tlpdbを保存し、別クリーン環境への完全な依存固定はT-012に残す。

### 生成・表示・失敗時の境界

PLANの位置づけ、表紙、第1/6/7/9/12章を現在のCodex中心・repo記録・ユーザー保存の分担へ整合した。第2/10章は方向と未確認境界を読み戻し、科学・出典の妥当性を新たに認定していない。残部と参考PDF/TeXの初回未確認3範囲、利用前または2026-10-01の期限を保持する。元Excel3冊と参考PDF/TeXは生成対象外。

独立作業コピーでの初回生成は終了0、17ページ。再生成も終了0でTeX全バイト・PDFページ本文が一致した。PDFバイトは生成日時を含むため同一性の基準にしない。全17ページをpdftoppm 26.07.0で1600pxのPNGへ描画して目視し、表紙版、日本語、数式、表、長いURL、柱・脚と改ページを確認した。欠字・はみ出しは検出しなかった。リンク文字とPDF内リンク領域は確認対象だが、全出典サイトの再取得や印刷機での実測ではない。

WindowsのPandoc既定出力は全743改行がCRLFだった。既存LF規範への逸脱を出力後の手修正で吸収せず、生成器へ `--eol=lf` を追加して再生成した。最終生成は終了0、TeXはLF 743/CRLF 0。最終PDFも17ページで、全ページの描画PNGが先に目視した版とバイト一致した。編集元MD・テンプレート・生成器のコピー元とのハッシュ一致を確認して最終TeX/PDFを候補へ戻した。`Overfull`/`Missing character`警告はなく、既存 `--no-highlight` の非推奨警告だけを旧版互換のため保持した。

隔離した失敗試験ではテンプレートへ無効な命令を入れ、終了1を確認。旧PDFは保持されたがTeXは更新され、現生成器には対の不一致が起き得る。この既知の制約を隠さず、独立作業コピーで生成・全頁確認後に一組を戻す制限を維持した。失敗側生成物は候補に混入させていない。これはLF修正前と同じ対更新方式の試験で、原子的な一括更新を実装した意味ではない。

最初のパッケージ一覧取得はWindowsのbatch引数処理で `--data name,localrev,cat-version` が誤解釈され、エラー文を出した。終了0だけで成功にせず、生tlpdbを保全して版を記録し、通常の `tlmgr info --only-installed` で再取得した。現在の一覧と初回失敗の双方を保存する。

### 点検・回帰と証拠の所在

期限に達したPLAN位置づけ/役割/工程/表紙、PLAN-TEX/PDF、BUILD-CODE、TEMPLATE、ATTRS、RB-S10-3を、現在の役割・生成条件・未確認境界の範囲で読み戻した。変更した本文と依存する入口・担当資料の整合をレビューした。科学本文の初回確認印や参考資料の確認印を一括更新しない。共通ENTRY-01と過去手順のコピー原文は維持し、使用していない外部設定UIを確認済みとしない。

<!-- GEN120-CHECKS-BEGIN -->
Windows/Python 3.12.12の全回帰201件が成功、失敗0・skip 0（250.469秒）。隔離一時領域で実行し、試験前後の宣言39ファイルのSHA256はすべて一致した。state 675検査、health 2229検査、現行contractと固定0.11.0比較器はそれぞれ1277検査に合格。期限超過0、初回未確認3範囲を保持、パス追加/削除0、論証28IDを保持した。検査コードとテストは全回帰時から保持し、この結果記入と表示案内の更新後に同じ管理検査・完全比較・diff検査を再実施する。最終結果と試験時からの文書差分はfinal_checks.jsonへ保存する。元Excel3冊・参考PDF/TeXは変更前と同一、最終PLAN一組は表示受入時から同一である。
<!-- GEN120-CHECKS-END -->

今回の証拠はrepo外の `C:/Users/genia/.codex/visualizations/2026/09/21/01a0c475-9ac7-7852-85a1-e3a4f3188dfa/doc-build-0.12.0/`。`base-0.11.0/`は完全比較元、`evidence/`は取得・初回生成・再生成/失敗・パッケージ観測、`evidence-lf/`は最終生成の実行と版/フォント/依存一覧・`pdf-acceptance.json`、`renders/`と`renders-lf/`は全17頁の画像。最終比較・回帰は`evidence/final_checks.json`、`final_*.stdout/.stderr`、`candidate_tests.json`と標準出力・標準エラーへ保存する。実行スクリプトもこの外側に保持し、通常再生成の入口はrepo内BUILDを用いる。

生ログが失われた場合も本書とBUILDから版・根拠・結果・限界を復元できるが、再実行は過去の原出力を代替しない。生成日時・追加TeX依存の将来取得状態・別OSまで同一になる保証はしない。管理検査に使う比較元はGit M101そのものではなく、この版のCONTINUITYが指す完全0.11.0コピーである。

### 次の開始位置

README→CONTEXT第1/22節→HTML start/S12→GEN-120/BUILD。0.12.0候補のレビューとユーザーによる保存後に、報告された固定SHAと一組を照合する。PLAN更新保留のU-011/U-016は今回のWindows文書生成の範囲で解消し、追加依存の固定・別環境・CI・対更新改善の要否はT-012へ残す。既存科学方針は再質問せず、受入後S10-3/P1の具体化へ戻る。


## AUD-110：0.11.0作成時の規範是正（継承する履歴）

以下の「今回」「現在」と環境未導入・PLAN保持は0.11.0作成時の記録。現在の追加許可と生成結果はGEN-120に従う。

RPT-016の依頼をCONTEXT第21節に保存し、採用理由と境界をDECISIONSのD-130/131へ記録した。会話は依頼の入口とし、次回の判断に必要な採用・理由・前提・棄却案・変更条件は各担当文書へ戻す。進捗の編集元はHTML S11、作業依存はT-014、未確定はUNCERTAINTIESである。

### 固定基準と権限

CHK-017：GitHub連携で非公開repoのmainを取得し、M101 `ad3494d700068d873a22ed2fbbf6f0a760a41735`、tree `8690657a122b937d2a74e03f451124509413af50`、PR13の統合と2親を確認。変更前のローカルHEADと全39パスのGit blobが固定treeに一致した。3原本ExcelはSOURCESのサイズ/SHA256と一致。完全な作業前コピーを固定し、比較元として使用した。

今回許可されたローカルの規範是正と検査を実施。実リポジトリのGit書込み、依存導入、Project削除・権限変更は行わない。Git保存・PR・マージはユーザーが担当し、その後Codexが固定SHAを読戻す。隔離テスト内の一時Gitリポジトリ操作は実repoの操作と区別する。

### 検出した逸脱と判断

| 対象 | 観測した問題 | 修正・判断 |
|---|---|---|
| 現在の入口・履歴・課題 | PR13後も未統合、H01の旧停止、36ファイルなどが現在案内へ残る | M101/39パス/原本統合を記録し、現在をS11/T-014へ。旧操作のコマンドは保持して時点を明示 |
| 開発規範と判断 | Chat中心の旧役割、会話や存在しないSTATEへの参照、判断の戻し先が混在 | Codex中心をD-130へ採用。CONTEXT/DECISIONS/HTML/課題/不確実性/根拠を責務別に更新する様式を明示 |
| `prepare_workspace.py` | Git無視対象のローカルファイルが新追跡ファイルと衝突すると上書きされる | mergeへ`--no-overwrite-ignore`を追加。衝突時停止と非衝突時の継続を試験 |
| `check_health.py` | HEALTH欠落の比較元や、表示モードと比較の併用でも成功する | 宣言された全パス・登録対応が揃う前状態を必須化。表示と比較オプションの併用は明示拒否 |
| `check_state.py` | 通常起動で動的importのキャッシュを生成し、読取り専用の説明と異なる | bytecodeを保存しない読込みへ変更。`-B`なしの子プロセス実行前後で全ファイル一致を試験 |
| `check_contract.py` | CONTINUITY本文版とファイル版登録が違っても成功する | 登録版との一致を検査。他の未変更ファイルに最新プロジェクト版を強制しない |
| 計画書の役割・再開記述 | PLANは0.10.0の役割案を含み、現在の生成環境を確認できない | MD/TeX/PDFを一組で保持。現行D-130を優先し、同時更新・再生成をT-012/U-016へ残す |

初期検査の成功だけでは上の意味の古さや反例を検出できなかった。反例を固定M101で再現し、検査器を緩めず保全条件と失敗検出を追加した。共通ENTRY-01の6行、歴史S08、既存G2/M081受入、39パス/28論証IDと3版/30日・初回期限を保持する。

### 実読・確認の範囲

README R0〜R5、CONTEXT全節、MAP、CONTROL A〜E、HISTORY/HEALTH/CONTINUITY、DECISIONS/LESSONS/BUILD/様式、課題・不確実性・出典台帳、HTMLの現在入口と全登録手順を役割・時点・依存・記録先の観点で確認。管理コードと関連テストを読み、保全・比較・版管理の反例を実行した。PLAN全文と生成経路を読んだが科学的妥当性の審査は行っていない。期限に達した歴史範囲は現行への影響を確認したもので、過去操作を再実行したという意味ではない。

PLAN残部・参考PDF/TEXの初回未確認3範囲は保持し、利用前または2026-10-01の期限を延ばしていない。既存PLAN/PDFの再生成・今回の表示審査は未実施。原本Excelのハッシュ一致は内容や計算の正しさを保証しない。外部製品・科学モデル・気象データの最新仕様の検証は今回の是正に含めない。

### 実行証拠と結果

実行環境：Windows、Python 3.12.12。確認日UTC 2026-09-21（作業日JST 2026-09-22）。M101基準はstate 656検査、health 2046検査に合格し、回帰190件成功・skip 0。最初のsandbox内回帰は一時ディレクトリのアクセス拒否で失敗した。同じ基準コードを自動承認済みの隔離テスト領域で再実行した結果であり、OS側の拒否をコードの欠陥や成功として扱わない。

5反例は旧基準で再現済み。修正後の新規10件と関連3件の局所試験は13件成功・skip 0。stateの通常起動に関する追加1件を含むstate関連14件も成功・skip 0。候補全体の回帰は201件成功・失敗0・skip 0（240.892秒）。試験の前後で対象39ファイルのハッシュはすべて一致した。

生ログ・比較元・反例スクリプトはrepo外の `C:/Users/genia/.codex/visualizations/2026/09/21/01a0c475-9ac7-7852-85a1-e3a4f3188dfa/norms-audit/` に保全する。`evidence/baseline_identity.json`、`baseline_state.stdout`、`baseline_health.stdout`、`baseline_tests.stderr`（初回拒否）、`baseline_tests_unsandboxed.stderr`（成功）、`checker-baseline-counterexamples.json`、`checker-targeted-tests.txt`、`state-readonly-counterexample.json`、`state-targeted-tests.txt` が原出力。再実行には固定M101の完全取得、候補全39パス、BUILDの検査コマンドが必要。生ログが失われても本書から範囲・結果・限界は復元できるが、旧実行の原出力を再実行で代替しない。

固定M101との候補比較は、旧M101 contract 1395検査、現行contract 1396検査、health 2205検査、state 665検査に合格。過去の検査器を変更せずに新候補の遷移を検査した。初回未確認3範囲の警告は保持し、期限超過0、追加/削除パス0、論証ID追加/削除0。原本Excel3冊・PLAN一組の全バイト一致、`git diff --check`成功も確認した。

`evidence/candidate_tests.json`と`candidate_tests.stdout/.stderr`は全回帰、`candidate-tested-hashes.json`は試験時の39ファイル。結果記録後に行う最終の静的検査と完全比較は`final_checks.json`と`final_*.stdout/.stderr`へ保存する。結果記入に伴う文書・登録の変化を除き、試験した管理コードとテストは保持する。最終39ファイルのハッシュは`candidate-final-hashes.json`に保存し、試験時との差分も`final_checks.json`へ明示する。生ログの欠落を成功記録だけで補完しない。

再現用の入口（repoルート、`<M101完全基準>`は固定SHAと全39パスを照合した別フォルダー）：

```text
python -B tools/check_state.py .
python -B tools/check_health.py . --base <M101完全基準>
python -B tools/check_contract.py . --transition --base <M101完全基準>
python -B <M101完全基準>/tools/check_contract.py . --transition --base <M101完全基準>
python -B -m unittest discover -s tests -v
git diff --check
```

通常の読取り用コマンドに`-B`を必須化して逸脱を隠したわけではない。追加回帰で`-B`とbytecode抑止環境変数を外したstate CLIも前後不変を確認している。隔離Git試験ではtempの権限が必要であり、再実行時のOS拒否は個別に記録する。

### 次の開始位置

README→CONTEXT第1/21節→HTML start/S11→T-014。ローカル是正候補のレビューとユーザー保存後に固定SHAを照合し、S10-3/P1の具体化へ戻る。承認済みのHe・GFS開始・追加実験を要求しない方針を再質問しない。T-012/U-016の計画書一組の生成は条件付き残件であり、科学・全環境の検証済み宣言や本体作業全体の停止条件にはしない。

## 0.10.1作成時の記録（PR13統合前の歴史）

以下の「今回」「現在」「未統合」は当該版作成時の記録であり、AUD-110の現在案内を上書きしない。

CHK-016 / FB-S105-CONSISTENCY。現在はユーザーが承認済み候補をS10-5から保存する段階。0.10.1では基準SHA・対象一覧・ブランチ・コミット/PR文・報告のコピー欄と操作粒度を、H01-3/H01-4・S10-4に合わせた。科学計画・原本・全Pythonコードは0.10.0から保持。過去手順は原文を保持し、必要な確認印だけを更新する。

### 当時の取得・比較・点検

GitHub連携のmainとcommit/treeを取得し、main=M092、tree=807997ba4d6b208e9089b18b5a590de811671c4bを確認。既存添付ZIPの36原本からtreeを再計算して一致を確認した。0.10.0完全候補も配布時の39パス/tree=74c073e4cf4d8f289e790ec7703f4ae8013942d0と一致した。全バイナリのGitHub新規ダウンロードやcloneとしての取得を意味しない。

今回の変更前は配布済み0.10.0候補である。M092→0.10.0と0.10.0→0.10.1を二段の完全実体比較として実行し、Gitへの累積変更一覧はM092と最終候補の全バイトから別に生成する。0.10.0をGit統合済みとして扱わず、自己SHAや仮コミットは作らない。CONTINUITYのcomparison_base_sha256は直前の0.10.0全実体を指す。

S10-5と比較対象の保存手順、既存DC-PROCEDURE、取得引継ぎメモ、前候補の承認受領記録を読んだ。追加コピー欄の文字列・改行・対象一覧の一致、コミット/PR欄の使い分け、Merge方式と停止、報告/読戻しを一連の操作として確認する。確認印の更新は実際の局所差分/依存影響と版期限に対応した範囲だけ。期限に達したS10-1/2a/4、E02-2、出典一覧、ログ回帰テストは現在への影響と歴史記録/検査責務として読み直し、過去操作の再実行や出典の最新外部仕様確認とはしない。科学本文・PDFの全審査は行わない。

初回回帰で入口の反例2件が失敗した。今回確認した入口の証拠IDと本文の表示が不一致であり、READMEに最新操作の説明を反映していないことも明らかになったため、README/AGENTSのS10-5案内・根拠IDと更新印を是正した。テストや検査器は変更しない。初回失敗と訂正前入口・登録を配布証跡に保持する。

実検査のコマンド・原出力と表示/コピーの範囲は配布外枠CHECKS.jsonへ保存する。GitHub書込み・Project削除・ユーザーPC操作は未実施。既存G2/M081受入、未確認範囲、3版/30日および初回期限は維持する。共通ENTRY-01の6行と歴史S08は不変。

### 当時の次の開始点

S10-5のユーザー保存→PR/統合SHA報告→AIの固定読戻し。すでに旧0.10.0の保存を始めていれば二重実行せずその版と停止位置を確認する。Project Excel重複削除は同一性と読戻し後の別判断。承認済みの本体方針を再質問せず、保存確認後はP1の具体化へ戻る。

## 0.10.0の基礎作業記録（累積差分の根拠）

REF-20260921-P1 / RPT-015 / CHK-015。GitHub連携でmain=a5dd6c10377257a36b8be20a3950279a1e19d5fd、固定README、コミットの親/tree、再帰treeを実取得。提供固定ZIPの全36ファイルからGit blob/treeを計算し、tree=807997ba4d6b208e9089b18b5a590de811671c4bと一致した後にローカル本文を使用した。Gitから全バイナリを直接転送した実績ではない。

### 取得の失敗と回復

旧r1作成時はLibraryの過去ZIPの原バイト搬送が失敗した。今回はGitHubからの取得を先に再試行し、本文・ref・treeは取得できたが、作業領域のraw.githubusercontent.com名前解決はTemporary failure in name resolutionで失敗した。一時的障害かどうか、過去のmaterialize失敗と同じ原因かは未確定。ユーザー提供ZIPを同一性照合して基準を回復した。認証情報・期限付きURLは成果物に含めない。

### 今回の本文と比較範囲

README全R0〜R5、CONTEXTの要求/焦点/受入と原意、MAPとCONTROL全A〜E、HISTORY/HEALTH/CONTINUITYの規則・登録、台帳/採否/教訓/BUILD/AGENTS/作業様式、HTMLのstart/H01/S10/S07と歴史S08/保存・検査欄を読戻した。S10-3原報告全文、H01 Closeout、r1の12組の原稿と原セル受領情報を比較した。固定M092と候補の同じ境界から、自身の論旨変更と親への影響を分けて確認した。

PLANは位置づけ・第9/10章に加え、変更した表紙・第1/2/7/12章を局所レビューした。子範囲は旧版にもある一意な章境界から定め、親の残部が変わらないことを照合する。旧出典の科学・製品条件を現在検証済みにはせず、PLAN残部と参考PDF/TEXの未確認/利用前または2026-10-01期限を維持する。生成したPLANのTeX/PDFは編集元との対応・表示として確認し、科学的真偽と区別する。

原Excel3冊はバイト同一コピーで、シート/チャート構造・原記述・数式と保存値の位置を確認した。再計算・修正・係数の採用なし。SOURCESは原本と一時AI資料の所在・使用条件の索引として点検し、旧checked_onを維持した。AI資料に記載された過去実験・検査成功・精度値は本候補の受入ではない。

### 実行と意味のレビュー

実行対象は基準M092の隔離コピーと候補。現行検査、完全基準を渡すhealth/contract比較、固定旧比較器、回帰試験、生成と表示の実ログは配布外枠CHECKS.jsonに残す。これはユーザーWindows・CI/Work/Codexの実行ではない。既存検査器の規則と閾値は維持し、成功欄のために検査を弱めない。手動レビューではRPT-015の各論点、残る候補と採用方針の境界、原本の位置、ENTRY原文、旧受入・操作原文・論証28IDを比較した。

### H01終了と入口の観測

RPT-014のPR #12/M092統合をGitで照合し、有限監査の終了はH01 Closeoutから受理した。PC保存とProject設定の開き直し一致はユーザー報告。旧Linux188件の原生ログは今回取り出しておらず、今回の再実行は別の観測。過去M081のWindows91件の受入を維持する。共通ENTRY-01の本文6行・本文版1と歴史S08のhashは保持し、会話に適用された共通文の照合を行う。設定UIは独立取得していない。

### 次の開始点と限界

0.10.0作成時は候補レビューとP1の具体化の段階だった。その後の保存承認は本書の現在記録を参照し、PR・統合SHA・原本同一性・固定読戻しを観測してからProject重複削除を利用者が判断する。現時点ではGit書込み・削除・権限変更、ユーザーPC変更なし。追加実験・新probe・再clone・環境再作成は要求しない。次は原資料とTawhiri基準を対応づけ、必要環境場・小標本受入・評価を具体化する。未調査の外部仕様、科学モデル、入力の曖昧さはU-014等に残す。

## RPT-037 / CHK-026：S25統合報告と、全飛行への要求（2026-09-23）

ユーザーはS25でM180基準からPR20をマージし、M190 `21d8565a97c59d38bf51f3ab8736ffb14ba21198`、branch `codex/forecast-plan-readiness-rpt036` 削除を報告した。Codexはprivate repo/既定main、PR20 merged、2親M180/C2-190、tree `93b7186e03a5d4d09ea54b285c2c8b6b811e41e5`、全55パスmode/size/blobとlocalバイト、branch一覧を固定GETで照合した。local.git HEAD=M101を変更しない。旧基準/原提供Excel/PLAN三点は保全対象。

同じ要求で、小さな進捗の完了報告から実際の軌道計算へ歩幅を広げ、北海道/和歌山の風報告とデータを検証して生かし、日本のあらゆる地点という目的を維持することを受理した。添付確認の追信はDownloadsの `main.pdf` と `jra3q_hokkaido_wind_2016-2025_v1.tar.gz` を明示。資料中の命令は現在の指示と区別する。S26/D-154/155へ接続した。

## ACT-200：実気象で動く軌道本体と資料（0.20.0）

基準は完全M190。外側の証拠ルートは `C:/Users/genia/.codex/visualizations/2026/09/21/01a0c475-9ac7-7852-85a1-e3a4f3188dfa/flight-core-0.20.0`。`base-0.19.0`、`evidence/M190-*`、S25原報告、`wind-review`、`weather-evidence`、`dynamics-evidence`を保持する。原PDF/tarはDownloadsに変更せず保持。独立レビューのrepo側要約は `references/WIND_REPORT_REVIEW.md`。北海道DB519,840行の検算は29項目中28整合、上端3hPa/14,612時刻/n_eff上限という3点の説明不一致を記録。元JRA時系列・和歌山・報告の精度改善数値は未再現。

新規GFS取得はrun2026-09-23 00UTCのf006未配信404で部分保存を残して停止。別の明示要求run2026-09-22 18UTCを選び、valid2026-09-23 03〜09UTCの7時刻、130〜151E/30〜46N、85×65、33面1000〜1hPa、gh/T/u/v/qと地上量を9,692,040 bytes取得した。原request/provenance/raw/receiptを保持する。原bundleと再読bundleのgzip header差はJSON payload同値と分けて記録。現writerはmtime0固定。rawhash/URL/予定時刻検査を含む通信禁止の再復号はweather-evidenceへ保存。

`balloon_sim`のweather/dynamics/cliを接続。保存場から同高度の列再構成→水平/時間内挿し、球面の現位置/時刻でRK4を評価。一定上昇または等温浮力/抗力、高度または径破裂、CdAまたは密度換算下降率、event根で終端を計算する。未対応モード/余分な物理設定/支持外を暗黙補完しない。設定、結果JSON/CSV/GeoJSON、日本語自己完結HTML、来歴とhashを新規出力へ保存する。

北海道例（43N/141.5E、5mAGL、上昇5m/s）と和歌山例（33.8N/135.2E、等温He0.5kg・膜1kg・payload1kg・Cd0.47）は仮の検証入力。共通UTC03:30、30km高度破裂、ρref1.225kg/m3で5m/sの降下。10秒刻みの地形終端時刻は各8670.016184秒、8363.853149秒。これは気象入力を使う数値実行の実証で、実飛行の予測誤差ではない。小領域のexact slice2本とhash/元raw来歴、設定をrepoへ含め、通信なしで再現する。刻み20/10/5秒・反例・解析期待値・最終回帰と生成/表示/保存結果は続報を本節へ追記する。


### ACT-200：独立レビューと最終生成

気象43試験、軌道28試験、CLI7試験を作成。旧318試験も含む全回帰の実結果は下へ記録する。レビューでは気象の高さ再構成順序、正重みの支持、元値の比湿/T検査、JSON重複key/非有限値、初期地下/内部RK段階の地形処理、余分な物理設定の拒否を確認し、指摘を修正した。別担当による16解析全飛行は時刻誤差0.000464秒未満。これは解析条件下の数値検証で、GFSや実飛行の精度保証ではない。

理論ガイド10頁、プログラム構造ガイド8頁、コマンド一覧と17公開API索引を実装から作成。専用XeLaTeXで各3回生成し、検索本文をpypdfで抽出。全18頁を画像で確認し、欠字/はみ出し/重なりなし。PDFの見出し移動先が前頁末尾になる不具合を発見し、titlesecを外して標準見出しへ戻した。本文は修正前後で同一バイト、最終build06のしおり23/19件と内部リンク36/25件を照合し、ページ不一致/未解決0。確認済みPDFとtxtをhash照合して発行した。生成の失敗ログと改善前後も外側guide-build-01〜06/link-anchor-reviewへ残す。PLAN三点をこの生成で変更していない。

軌道HTMLは2例の埋込869/838レコード、12成果物のhashとリンク、外部参照なし/重複IDなし、JavaScript構文を確認した。ブラウザへのfile URL表示はBrowser URL security policyに拒否され、回避経路を使わなかった。従ってHTMLの実表示・スライダ操作は未確認として残す。PDFの全頁画像確認とは別の検証範囲である。証跡はevidence/html-display-limits.json等。

<!-- ACT200-FINAL-CHECKS-BEGIN -->
全回帰 396 件が合格（354.968秒）。実行前後の全80ファイルhashは不変。state 964、health 3320、候補/固定旧contract各2815検査が合格し、git diff --checkも合格した。初回のBUILD末尾空行を是正した経緯を含め原ログを保存。healthの初回未確認3範囲（PLAN本文と旧REFERENCE PDF/TeX）は警告と期限を保持し、科学確認済みへ変更していない。全回帰では専用一時領域を指定しWindows通常ユーザー権限で実行、ACL/local.git/旧原本を変更していない。実績追記後は実装と入力のhash不変を確認し、文書の構造/依存を再検査する。
<!-- ACT200-FINAL-CHECKS-END -->

<!-- ACT200-SAVE-BEGIN -->
2026-09-23T04:34:40ZにDraft PR #21（https://github.com/GENIANY/space-balloon-simulator-jp/pull/21）を作成。C1 fbc82de966dcc7cc567fec62179af266205bccac、親M190 21d8565a97c59d38bf51f3ab8736ffb14ba21198、tree c18bf1827a0fc18a51e3ce3b0907a28e4b70d389。既存16更新・追加25/削除/改名0、全80パスのmode/size/Git blobを固定照合した。workbranch=codex/flight-core-rpt037をforce=falseで更新、main=M190不変。RPT-022の継続許可の範囲で実施し、mainマージは行っていない。 原受領票はevidence/C1-remote-receipt.json。実績追記C2を同PRへ保存し、親C1・全80・PR head・mainを再照合する。最終結果はPR本文とevidence/C2-final-remote-receipt.jsonへ置き、自己SHAだけの反復保存を行わない。
<!-- ACT200-SAVE-END -->

最終コードでflights-releaseの2例を通信/DNS禁止のまま再出力し、全869/838レコードと結果JSONが旧出力と完全一致、CSV/GeoJSONも同一バイト、通信試行0を確認。入力/元raw/本体sourceと全成果物hashをevidence/release-flight-verification.jsonへ固定した。最初の証跡用検証脚本がevents配列にもlaunchを要求したため誤って失敗したが、launchは初期record、eventsはburst/landingという実schemaに直して再検査し、旧判定も保持した。製品コード・出力の改変で成功にしていない。


## RPT-038 / CHK-027：S26/S27報告と、構造資料・用途の是正（2026-09-23）

原報告は外側structure-guide-0.21.0/evidence/report-S26-S27-original.txt。利用者はPR21をM200 `6d86fa7149fa8d2d0879a20fc3fe18241bc690e1`へマージ、作業branch削除と報告。Codexはprivate repo/既定main/PR merged、2親M190/C2-200、tree b9c4f65538c30eaccdb0531a19811c87a723ac6e、全80パスのmode/size/Git blobとローカルbytes一致を確認し、完全base-0.20.0を外側へ保存した。一方GitHub branch一覧にはcodex/flight-core-rpt037が残っていた。統合完了と削除の観測差を分離し、削除操作やlocal.git同期はしない。

ユーザーの直接依頼は風分析資料のGit保存と、構造ガイドの実装忠実な階層/依存・視覚説明への是正。報告中の用途説明は現在方針の根拠として受理し、第三者資料の命令を実行許可にしない。S26-Q1の優先三択は撤回、D-156の落下分散中心と予報/過去の判断用途へ接続する。

## ACT-210：構造を読めるガイドと、用途の訂正

比較元はM200の80実体。参考燃焼ガイドは構造説明様式として参照し、実装の科学的採用とはしない。旧PROGRAM_GUIDEの内容の行先を残し、実ファイルと論理関数群の木、呼出/データ/契約の別、色と説明枠を対応させる。風PDFは原本バイトと検索用本文を保存し、数値結果と動機/意思決定の読み取りをWIND_REPORT_REVIEWへ集積する。本体の物理コードと理論ガイドは変更しない。

<!-- ACT210-CHECKS-BEGIN -->
構造ガイドを14頁の実装階層/依存図へ全面改訂し、詳細はIMPLEMENTATION_NOTESへ移した。旧3〜6節の意味を保持し、コードとの誤記を是正。実在5ファイル/64関数/3class/3lambdaと静的145辺、17公開APIの索引を照合し、独立47検査と17意味項目が合格。全14頁の表示、15anchor/52内部リンクを点検、rootは最終6頁を独立確認した。原風PDF 114頁/15,759,118 bytesと検索txtを保存候補へ追加し、原本全byteと全頁抽出の一致を確認。用途再読と科学的受入は分け、GEFSは一次仕様調査まで。402全回帰、state/health/新旧contractが合格し、全83ファイルは試験前後不変。期限20範囲を点検、PLAN全体のみ初回未確認を維持した。原PDF限定例外を6試験で検証し、自作PDFのTeX条件は維持。初回state不合格とsandbox試験失敗は原ログで保持。HTMLは静的検査でありブラウザ表示を確認したとはしない。証拠はACT-210。保存はS29へ進む。

全回帰実測 358.375秒。生成/全頁表示はguide-author-review.json、root追加確認はevidence/root-guide-visual.json、旧情報対応はstructure-information-migration.json、実コード意味はstructure-audit/guide-semantic-review.json、原PDFはwind-reference-evidence/acceptance.json、境界独立レビューはoriginal-pdf-guard-review.mdへ固定。選択生成CLIはevidence/guide-selection-cli.json。実装本体5ファイルとTHEORY/PLAN三点はM200から不変。
<!-- ACT210-CHECKS-END -->

<!-- ACT210-SAVE-BEGIN -->
2026-09-23T06:25:04ZにDraft PR #22（https://github.com/GENIANY/space-balloon-simulator-jp/pull/22）を作成。C1 7e7961d1267b22a2ffae5d61020b0af13bb3824f、親M200 6d86fa7149fa8d2d0879a20fc3fe18241bc690e1、tree cd62805dafc6ab350f6689a60fab06796f200fbb。既存28更新・追加3/削除/改名0、全83パスのmode/size/Git blobを固定照合。原風PDF 15,759,118 bytesも原本blobと一致。workbranch=codex/structure-guide-rpt038をforce=falseで更新しmain=M200不変。継続許可RPT-022に基づき実行、mainマージは人間担当。 実績追記C2を同PRへ保存し、親C1・全83・PR head/mainを再照合する。最終結果はPR本文とevidence/C2-final-remote-receipt.jsonへ置き、自己SHAだけの反復保存を行わない。
<!-- ACT210-SAVE-END -->

ACT-210の確認範囲補足：燃焼参考PDF（113頁）は構造説明形式の目的適合性をp2/3/14の図・色・注記とTeX描画/階層定義から確認した。原PDF/TeXはM200同値、更新版unknownを維持する。全頁の論証・燃焼実装との一致・科学的正しさ・再生成の受入ではない。初回未確認PLAN全体は維持する。初回stateの不合格（footer旧版、S26状態ラベル、原風PDFへのTeX要求）をchecks-first-failure.jsonへ保持し、表示補正とD-158の限定した原本契約/反例へ戻した。


## RPT-039 / ACT-220：目的から設計へ戻す振り返り（2026-09-23）

ユーザーはCodexの表面的な理解と注意不足を批判し、規範・参考資料・方向性を結び、必要な構造を推測して計画する過程そのものの見直しを求めた。今回は反省と方針修正へ集中する直接指示として受理した。指示書の順番やガイドの見た目だけを直す依頼とは扱わない。SciPy等の既存機能を使い、独自部分を固有の仕事へ絞る設計上の推奨も受け入れる。継続許可の範囲は変えない。

### 固定基準・読取と判断

repo ID1373721672/private/main、main M200 `6d86fa7149fa8d2d0879a20fc3fe18241bc690e1`を再取得。固定main README R0〜R5、作業ファイル0.21、注入AGENTS0.20と今回直接指示を区別した。PR22はopen/draft/未統合、先端C2-210 `7f06e1529d30f95f404ba7ab2e3cf887640ddace`、tree `9d34294d4e23e2083230a88029421b84bdf9ef9c`、83blob。既存公開manifestと作業83ファイルをSHA256で照合し、完全base-0.21.0を外側design-retrospectiveへ保存した。今回の比較元はC2-210、採用mainはM200であり同一視しない。local.git HEAD=M101は操作しない。

PLAN位置づけ/第5/9/10章、CONTROLの責務・説明設計・開始/終了、CONTEXTの用途と原回答、DECISIONS D-147〜159、LESSONS GAP-019/022/023、MAP、ENVのモデル構成/分散契約とballoon_simを照合した。燃焼参考TeXの全体責務、simulation/state/rhs/events/solver、physicsとfeed_system/injectorの説明を読み、PDF物理ページ36/41/43/60/69/103を表示した。原本を変更せず、燃焼コード自体との一致や科学的妥当性を保証しない。風資料はWIND_REPORT_REVIEW第5〜8節と保存原本の物理ページ5/13/76/105の用途記述を再読し、今回の全文/数値再監査とはしない。

手順DOM順序と目次/進捗表示、前回挿入スクリプト、設計台帳と検査器の判定範囲を突き合わせた。三変更例で本体境界を監査し、必要量の二重定義、位置3成分への固定、径破裂と上昇モードの結合、GFS製品条件と一般照会の混在、比較実行/結果の責務不足を把握した。SciPyは既存Miniforgeに1.17.1があり、D-147の既往調査と自前RK4採否の間の説明不足を確認。公式仕様と固定実装も参照した（https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.integrate.solve_ivp.html、https://github.com/scipy/scipy/blob/v1.17.1/scipy/integrate/_ivp/ivp.py）。速度比較やsolver移行の試験は今回行っていない。

採否はD-159、分析はGAP-024。次の設計作業はS30 A/B/Cへ戻した。旧成果・試験結果を消さず、PR22の構造受入とマージ依頼を保留する。今回コード/ガイド/PLAN本文は不変、手順順序の是正も未実施である。

### 点検と限界

<!-- ACT220-CHECKS-BEGIN -->
現3版周期で期限到来した9範囲を限定再点検した。RB-S10は全体37,933bytesを読み、過去の役割とstartへの案内を確認、partialは維持した。検査runner/契約/予報時刻計画の試験ソースを読取。予報planner35試験は成功、runner9試験は初回sandbox内の一時フォルダー権限失敗で開始できなかった。コードを変えず、通常権限で同じ9試験を再実行し0.153秒で成功した。初回失敗ログも保持する。保存GFS3ファイル/manifest/検査器は通信拒否下で417メッセージ・33,777値を復号し、前後hash不変。これは現行予報の取得可用性や科学精度の再受入ではない。外側design-retrospective/expiry-*-review.mdと原ログに証拠を保持する。候補の文書検査はstate1015、health3423、新/固定旧contract各2212が成功。初回はHTML meta版、続いてfooter版の旧表示を検出し、現在表示だけを訂正した。初回出力も保存した。healthの初回未確認PLANと元期限は保持する。これらは記録・参照・指紋の整合であり、指示書の順序や本体構造の良さを保証しない。reflection-review.mdでは反省/次作業/入口の接続を独立に読んだ。コード/ガイド/原本のbytesは固定C2と不変、全402回帰・新PDF生成/ブラウザ表示・科学的再受入は今回未実施。
<!-- ACT220-CHECKS-END -->

### 保存と引継ぎ

<!-- ACT220-SAVE-BEGIN -->
2026-09-23 08:11:00 UTCにC1 83848ce5f10a6f25e57eb1e12f3d4ceeae2e84fb（親C2-210 7f06e1529d30f95f404ba7ab2e3cf887640ddace、tree cd93eb25eabfc098335c37fe978565b3c4e0abc8）を既存作業branchへforce=falseで保存し、Draft PR22を反省・再設計の計画へ更新した。前候補から12記録ファイル更新、全83パスのmode/size/blobを固定照合。本体・試験ソース・全ガイド/原資料は不変。実績追記後の最終headはPR本文/外側受領票へ置く。main統合は未実施で、マージ依頼は保留。
<!-- ACT220-SAVE-END -->


## ACT-230：抽象原則を全作業へ適用する仕組み

### 固定基準と依頼の解釈

RPT-040はユーザーの直接指示。原則は個別教訓より上位にあり、情報を総合して暗黙のニーズを推測し、推測・設計・成果を問い直す判断を全作業で持続させる要求として受理。意図と仕組みの対応、今回の適用・自己評価・次の実施はHTML S31へ置き、ここへ進捗を二重入力しない。

Private GENIANY/space-balloon-simulator-jp ID1373721672/default mainを確認。main M200=6d86fa7149fa8d2d0879a20fc3fe18241bc690e1は不変。PR22はopen/Draft、C2-220=0b55b9d72b07d63209bb6fc132e1645b84cac8a3、tree ab03a1832b1ce89a48df869ef69f62ff603abb76。全83パスのmode/size/Git blobをローカル候補と照合してbase-0.22.0を保存した。local.git HEAD=M101は同期しない。注入AGENTS0.20、保存候補0.22、今回の直接要求を区別し、RPT-022/028/029の継続許可を維持する。

外側P230：C:/Users/genia/.codex/visualizations/2026/09/21/01a0c475-9ac7-7852-85a1-e3a4f3188dfa/design-principles/ 。remote-baseline.json、baseline-manifest.json、完全base-0.22.0を保持する。原則/入口/実施のroot、readonlyの目的/運用監査、health検査/試験、管理JSON3ファイルの担当を分離し、固定SHAと全体目的を渡した。外側証拠の分類は既存EXT-TEMP/EXT-CHECKPOINTを使い、版ごとに新しい管理台帳を設けない。これらが失われた場合、Git固定版から基準を再取得し必要な検査を再実行できるが、過去実行の原ログを再現したとはしない。通常再開に一時スクリプトを必須にしない。

### 読取と判断の接続

固定main README R0〜R5を取得し、同一性を確認した現候補の入口・CONTEXT1〜3/方向・MAP情報依存・規範・WORK_ORDER・GAP024・D159・S30・管理契約を読む。長期方向と既決の物理/気象方針は前回の固定読取から不変で、その科学的再評価は行わない。今回の根本原則はPLANの具体要件を置換せず、それらの解釈と適用の基礎になる。原資料の再取得・新PDFの生成/表示は本作業の成果に含めない。

audit-architecture.mdとaudit-history.mdは、継続ターン・小変更・分担・途中発見・引継ぎ・管理自身へ原則が抜ける経路を独立読取した。これをDC-JUDGMENTと既存の開始/設計/実施/終了へ接続。旧DC-READの「未読を推測しない」は未取得の事実を補わない意味とし、取得情報から暗黙ニーズを推測する責務と区別した。新しい総合判断台帳や全段階必須記入は追加しない。原則の案を読み返し、初期の誤読に固執しないよう「新情報だけでなく同じ情報の再検討でも理解を更新する」と補正し、恒久原則から個別の三例への依存を外した。

D-161の周期見直しは、原則をこの仕組み自体へ適用した結果。新しい版を想定した時点で101範囲が版数だけで期限になること、THEORYの印更新がTeX/PDFまで波及することを確認した。版差警告を保持し、内容/依存/実時間/利用の根拠へ戻す方針とした。旧規則の結果と新規則の結果は別に保存し、確認印をまとめて更新して解消しない。

版差候補のうち原本Excel・本体・理論・固定入力は今回その内容を科学/実装の判断に使わず、固定バイト不変なので新しい内容レビューへ広げない。管理検査の変更と依存する運用/歴史は別に選定し、旧HTMLとPLAN子の自己本文が同じことと新原則からの意味的影響を限定確認する。旧現在形・順序問題や親PLANの未確認、科学/構造の未受入は保持する。候補の見送りを確認済みへ変えない。

### 検証・限界・保存

<!-- ACT230-CHECKS-BEGIN -->
原則と適用経路はnorm-review.mdの修正後再読で照合。初稿の「当初意図」を初期誤読への固執にしない補正と、恒久原則から固有三例を外す補正を反映した。S31の自己評価と区別し、読取上の整合を長期遵守や本体設計の承認へ拡張しない。

version-age-fixture-results.json：固定0.22の独立fixture14件成功。通常sandboxの一時dir権限失敗2回を原ログに保持し、ACL/tempfileを変えず同じrunnerを審査済み通常権限で再実行。management-results.json：現候補のhealth63/contract89/state20/check_run9、計181件、失敗/エラー/skip0、191.828秒。変更2ソースのSHAを結果に固定した。全本体回帰ではなく管理検査の変更影響を対象とする。

initial-validation-summary.json：state1029/health3462/新旧contract各2288成功。旧healthは98件の版数期限だけで失敗し、原stdoutをinitial-old-health.jsonへ保持。新healthでは同じ98件をversion_age_advisories/warningsへ出す。age-receipt-preservation.jsonに、元101候補のうち98の確認記録を完全保持し、変更したhealth/その試験/document-healthの3件だけ更新したことを記録。これは未実施レビューの成功化ではない。初回未確認PLANと期限も保持する。

新旧contractは固定比較元83パス・44論証・policy/ガード変更の理由と前後を照合する。本文マーカーと派生MAPを同期後の検査であり、質の自動認定ではない。実績追記時にS31の完了ラベルが既存書式と異なることをstateが検出し、状態を変えずラベルを訂正した。原失敗はC2-initial-state-failure.jsonへ保持。結果追記後は整合検査と試験済み2ソース/本体・原資料・全PDF/TeXのバイトを再照合する。最終実数は外側受領票へ保持し、自己記録だけの反復改訂を要求しない。

本体計算・科学的妥当性・ガイドPDFの改善、手順全体の並替え、継続運用での効果は未実証。PLAN第12章等の古い現在形、旧手順の残件表示、focus累積の再設計は今回の原則追加で解決したことにせずS30へ残す。
<!-- ACT230-CHECKS-END -->

<!-- ACT230-SAVE-BEGIN -->
2026-09-23 09:14:23 UTCにC1 f5db6f33763019c0f587c51e33d6ec676ea21417（親C2-220 0b55b9d72b07d63209bb6fc132e1645b84cac8a3、tree f7bcda7bb5844ff0a0c42081dd267a1bfe932d80）を作業branch codex/structure-guide-rpt038へforce=falseで保存し、Draft PR22を0.23の根本原則と継続運用へ更新した。17差分・全83パスのmode/size/Git blob、親・PR headを固定照合。main M200は不変。実績追記後の最終headと読戻し結果はPR本文/外側受領票へ置き、自己SHAだけの反復保存はしない。
<!-- ACT230-SAVE-END -->
