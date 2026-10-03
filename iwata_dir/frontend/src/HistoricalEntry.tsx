import {useState} from 'react';
import type {WeatherSource} from './domain';
export function HistoricalEntry({sources,context,onCreate,onReturn}:{sources:WeatherSource[];context?:Record<string,unknown>;onCreate:(source:WeatherSource)=>void;onReturn:()=>void}){
 const available=sources.filter(s=>s.time_kind==='analysis_valid_utc'&&s.default_config),[chosen,setChosen]=useState('');
 const source=available.find(s=>s.id===chosen)??available[0];
 return <section className="historical-entry"><h2>原日時から、打上げへの影響を調べる</h2><p>気象分析で見つけた季節や地域の特徴を、原日時の場で飛行させて確かめます。下の地図・干渉群・詳細・図保存は予報と共通です。</p>{context&&<p>{String(context.label??'気象分析からの条件')} <button onClick={onReturn}>元の気象分析へ戻る</button></p>}<details open={!available.length}><summary>原日時の比較候補を追加</summary><p>保存場の診断用入力を出発点にし、候補ごとの共通機体・地点と原日時を編集します。取得済みの日時だけで多年の代表性が成立するわけではありません。</p><label>入力の出発点<select value={source?.id??''} onChange={e=>setChosen(e.target.value)}>{available.length?available.map(s=><option key={s.id} value={s.id}>{s.label}</option>):<option value="">元UTCの場を確認中、または未登録</option>}</select></label><button disabled={!source} onClick={()=>source&&onCreate(source)}>この保存場から比較候補を追加</button></details></section>;
}
