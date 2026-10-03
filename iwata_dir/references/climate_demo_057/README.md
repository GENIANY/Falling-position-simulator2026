# 元時刻の風データによる分析デモ

この資料は、人工例で設計した月別の中央値・分布の幅・UTC時刻フィルターを、公開元の実データで確認するためのものです。取得画面の完成を待たず、取得CLIと固定した標本から再現できるようにします。

**保存・照合済みの範囲。** 2024年の全12か月、UTC 00/06/12/18時を各製品の4元格子で収録しました。両商品の全地域束からの全878,400風値のbit一致、50収録実体のhash、通信なしの展開と再読を確認しています。ZIPは2,994,432 bytes、SHA256 `83b9a8c68b73938acd2163fd9e3c6ba11a756470083143e6129a70c8449d9f32`。原応答から全地域束への照合、取得の失敗・再開と画面確認は[S36](../../BOOTSTRAP_RUNBOOK.html#s36-climate-final570)へ戻ります。

## 何を保存するか

| 実体 | 内容と用途 |
|---|---|
| `jra3q-native-basis.json` | JRA-3Qの取得格子・気圧面・Gaussian面積重みの基準。提供された2016–2025年DBから得た座標基準であり、2024年の風値は含まない。取得値は公開元から別に取得する。 |
| `wind-samples.zip` | 両商品それぞれの指定点周辺2×2元格子、全年の元UTC時刻、全取得気圧面のu/v配列。補間・量子化・人工的な穴埋めをせず、地域全体から元格子を選び出す。 |
| `archive.json` | ZIP全体と各収録実体のbytes/SHA256、元資料との関係。 |
| ローカルの全地域取得束 | JRA-3Qの570格子、ERA5の1,188格子。原応答と取得失敗・再開の票を含む。Git内の4格子デモと混同しない。 |

両商品は別sourceです。提供済みの2016–2025年JRA-3Q期間集計DBも別sourceのまま保持します。新しい2024年の原標本を、その10年DBの原標本だと解釈してはいけません。

## 統計の意味

- 原標本のu/v（m/s）から各格子・元UTC時刻の速さを求めます。格子面積重みと等時間重みを用いた経験CDF逆関数で、月全体のp10/p90と前半・後半の中央値を求めます。
- 一月の前半はUTC 1–15日、後半は16–月末です。JSTの表示は時刻の読み替えであり、月・半月の所属日はUTCを保ちます。2024年2月は29日を含みます。
- 月の灰色帯は格子×時刻の風速分布です。地域平均風の時系列の幅、独立な標本数、将来の飛行の予測区間ではありません。
- JRA-3Qは3–1000 hPaの38面、ERA5は1–1000 hPaの37面です。高さの表示はISA参考高度で、実気象の幾何高度や地形の高さではありません。地下に相当する気圧面の値を地表からの飛行場として用いません。
- この束は風統計の機能確認用です。気温・湿度・地表場を含む瞬時4次元の飛行用気象束ではなく、一年の結果だけで多年の季節特性や予測精度を受け入れません。

## 再現する操作

リポジトリルートで次を実行します。既存の出力先を上書きしません。処理にネットワークは使いません。

```powershell
$taskPython = 'backend/.venv/Scripts/python.exe'
$taskDemo = Join-Path $env:LOCALAPPDATA ('SpaceBalloonSimulator\climate-demo-' + [guid]::NewGuid().ToString('N'))
& $taskPython -B -m tools.prepare_climate_demo --output $taskDemo
if ($LASTEXITCODE -ne 0) { throw '実標本デモの検査/展開に失敗しました。部分出力を保持して確認してください。' }
$env:BALLOON_CLIMATE_ARCHIVES = ConvertTo-Json -Compress -InputObject @(
    (Join-Path $taskDemo 'jra3q\manifest.json'),
    (Join-Path $taskDemo 'era5\manifest.json')
)
```

この環境設定を行った端末からローカルserviceを起動し、「気象を分析」→「保存した実気象集計」で資料を選びます。全地域の再取得は[コマンド一覧](../../docs/COMMANDS.md#C-CLIMATE-RAW)、API・支持と取得費用は[気象データガイド](../../docs/WEATHER_DATA_GUIDE.md)、式と可視化は理論ガイドに分担します。

## 出典・利用条件・変更

**JRA-3Q。** JMA JRA-3Q、NSF NCAR GDEX [d640000](https://gdex.ucar.edu/datasets/d640000/)、データDOI [10.5065/AVTZ-1H78](https://doi.org/10.5065/AVTZ-1H78)。Kosaka et al. (2024), DOI [10.2151/jmsj.2024-004](https://doi.org/10.2151/jmsj.2024-004)。配布元の2026-10-02確認時の利用条件は[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)です。JRA派生データについて同条件・帰属を保持します。プログラムの利用条件とデータの条件を一括りにしません。

**ERA5。** ECMWF / Copernicus Climate Change Service、NSF NCAR GDEX [d633000](https://gdex.ucar.edu/datasets/d633000/)、データDOI [10.5065/BH6N-5N20](https://doi.org/10.5065/BH6N-5N20)。配布元の2026-10-02確認時の利用条件は[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)です。Contains modified Copernicus Climate Change Service information. 含まれるCopernicus情報・データの利用について欧州委員会およびECMWFは責任を負いません。

変更は、日付・UTC時刻・気圧面・元格子の部分選択、DAP2またはNCSS NetCDF3の元Float32からNPY float32への保存形式変更、および原u/vからの集計です。デモの4格子選択はmanifestの元格子ID・元束SHA256・選択点と作成器SHA256に残します。提供者がこのデモやシミュレーターの精度を承認したことを意味しません。
