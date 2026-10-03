import {selectedClimateHours,climateYearsLabel,climateWeightLabel,type ClimateArtifact,type ClimateMonthlyProfiles} from '../../climateDomain';
import {niceSpeedMax,type WindViewModel} from './viewModel';
import {esc,fmt,text,line,svg} from './plots';

export const monthlyProfileDefinition='青緑＝前半中央値、橙＝後半中央値、灰帯＝月全体の10–90%幅。各高度で選択地域の格子×UTC時刻をまとめた風速分布です。12か月・全表示高度で共通軸を使います。';
export function monthlyProfileMethod(vm:WindViewModel):string {const p=vm.monthlyProfiles;return `${climateYearsLabel(p?.population.years_fixed??[])}、UTC暦の1–15日／16–月末。格子は${climateWeightLabel(p?.weighting)}、時刻は等重みの経験CDF逆関数（inverted_cdf）です。地域平均風の時系列分布ではありません。人工例の等重み・線形補間分位とは有限標本の計算法が異なります。この表示は平均図と共通の支持面を使い、未取得月を短い年期間で代用しません。`; }
const invalid=()=>{throw Error('保存された月分位の母集団・支持面・件数または値が一致しません。');};
function sameIds(a:unknown,b:number[]):boolean {return Array.isArray(a)&&a.length===b.length&&new Set(a).size===a.length&&a.every(x=>Number.isInteger(x)&&b.includes(x));}
function sameYears(a:unknown,b:unknown):a is [number,number] {return Array.isArray(a)&&Array.isArray(b)&&a.length===2&&b.length===2&&a.every((x,i)=>Number.isInteger(x)&&x===b[i])&&a[0]>=1940&&a[1]<=2100&&a[0]<=a[1]&&a[1]-a[0]<=9;}
function count(value:unknown):value is number{return Number.isSafeInteger(value)&&Number(value)>=0;}
function speed(value:unknown):value is number{return typeof value==='number'&&Number.isFinite(value)&&value>=0;}

/** Validate the supplied result, without reconstructing quantiles from mean or half-month summaries. */
export function checkedMonthlyProfiles(a:ClimateArtifact):ClimateMonthlyProfiles|undefined {
 const p=a.summary.monthly_profiles;if(p===undefined)return undefined;
 const s=a.summary,hours=selectedClimateHours(a.query),pop=p?.population,raw=p.provenance?.manifest_schema==='balloon.wind-samples/1';
 const weight=s.population.spatial_weighting,weightMatches=weight===p.weighting||(!raw&&p.weighting==='gaussian-area-equal-times'&&['gauss','provided_gaussian_grid_weights'].includes(weight));
 if(p?.schema!=='climate-month-profiles/1'||p.method!=='inverted_cdf'||!['gaussian-area-equal-times','spherical-area-equal-times'].includes(p.weighting)||p.date_convention!=='UTC'||
   !pop||!sameYears(pop.years_fixed,s.population.years_fixed)||!sameYears(pop.years_fixed,s.source.capabilities.years_fixed)||!sameIds(pop.hours_utc,hours)||!hours.length||hours.some(h=>!s.source.capabilities.native_hours_utc.includes(h))||
   !weightMatches||(raw?s.source.weighting!==p.weighting:s.source.weighting!==undefined&&s.source.weighting!==p.weighting)||
   !sameIds(pop.selected_cell_ids,s.population.selected_cell_ids)||!pop.selected_cell_ids.length||!sameIds(pop.level_ids,s.levels.map(l=>l.level_id))||!pop.level_ids.length||
   !/^[a-f0-9]{64}$/.test(p.provenance?.bundle_sha256??'')||!['balloon.climate.raw-months/1','balloon.wind-samples/1'].includes(p.provenance?.manifest_schema)||!p.provenance.numpy_version||
   !Array.isArray(p.months)||p.months.length!==12||new Set(p.months.map(m=>m.month)).size!==12)invalid();
 for(const id of pop.selected_cell_ids){const cell=s.source.native_grid.find(c=>c.cell_id===id);if(!cell||!speed(cell.gauss_weight)||cell.gauss_weight===0)invalid();}
 for(const m of p.months){
  if(!Number.isInteger(m.month)||m.month<1||m.month>12)invalid();
  let expected=0;for(let year=pop.years_fixed[0];year<=pop.years_fixed[1];year++)expected+=new Date(Date.UTC(year,m.month,0)).getUTCDate()*hours.length;
  if(m.expected_time_count!==expected)invalid();
  if(m.available===false){if(m.reason!=='month_not_acquired'||'rows' in m||'time_count' in m)invalid();continue;}
  if(m.available!==true||!count(m.time_count)||m.time_count!==expected||!Array.isArray(m.half_time_counts)||m.half_time_counts.length!==2||
    m.half_time_counts[0]!==(pop.years_fixed[1]-pop.years_fixed[0]+1)*15*hours.length||m.half_time_counts[1]!==expected-(pop.years_fixed[1]-pop.years_fixed[0]+1)*15*hours.length||
    m.cell_count!==pop.selected_cell_ids.length||!count(m.sample_count)||m.sample_count!==m.time_count*m.cell_count||
    !Array.isArray(m.rows)||!sameIds(m.rows.map(r=>r.level_id),pop.level_ids))invalid();
  for(const row of m.rows)if(!speed(row.p10)||!speed(row.p90)||row.p10>row.p90||!Array.isArray(row.half_medians)||row.half_medians.length!==2||!row.half_medians.every(speed))invalid();
 }
 return p;
}

export function monthlyProfileScale(vm:WindViewModel):number {
 const values=vm.monthlyProfiles?.months.flatMap(m=>m.available?m.rows.flatMap(r=>[r.p90,...r.half_medians]):[])??[];
 return niceSpeedMax(Math.max(0,...values)*1.05);
}

/** A separate twelve-month display; mean/rose grain selections remain untouched. */
export function monthlyProfileView(vm:WindViewModel):WindViewModel {
 const profiles=vm.monthlyProfiles;
 const months=Array.from({length:12},(_,i)=>profiles?.months.find(m=>m.month===i+1));
 const periods=months.map((m,i)=>({id:i,month:i+1,label:`${i+1}月`,description:`UTC 1–15日／16–月末 · ${climateYearsLabel(profiles?.population.years_fixed??[])}`,timeCount:m?.available?m.time_count:0}));
 return {...vm,annualPeriods:periods,annual:periods.map(()=>vm.levels.map(()=>null)),populationLabel:vm.populationLabel.replace(/(?:半月|月|季節)\d+区分/,'月12区分'),annualDefinition:monthlyProfileMethod(vm),annualSpeedMax:monthlyProfileScale(vm),metadata:{...vm.metadata,grain:'month',period_membership:months.map((m,i)=>({month:i+1,available:m?.available??false,expected_time_count:m?.expected_time_count})),monthly_profiles:profiles,profile_axis_max:monthlyProfileScale(vm)}};
}

export function monthlyProfileLegend():string {
 return svg(740,32,line(4,10,29,10,'#087f83',2)+text(34,14,'前半中央値（UTC 1–15日）',11)+line(239,10,264,10,'#d07032',2,'stroke-dasharray="5 2"')+text(269,14,'後半中央値（UTC 16–月末）',11)+'<rect x="499" y="4" width="25" height="12" fill="#ccd7d8"/>'+text(529,14,'月全体の10–90%幅',11)+text(4,30,'幅は各高度の経験分位。独立標本数や将来の予測区間を示すものではありません。',10),'月別中央値と10–90%幅の凡例');
}

export function monthlyProfilePlot(vm:WindViewModel,index:number):string {
 const m=vm.monthlyProfiles?.months.find(m=>m.month===index+1),W=190,H=212,x0=32,y0=30,pw=146,ph=126,max=monthlyProfileScale(vm),zMax=Math.max(...vm.levels.map(l=>l.height)),X=(s:number)=>x0+s/max*pw,Y=(h:number)=>y0+ph*(1-h/zMax);
 let b=text(W/2,12,`${index+1}月`,12,'text-anchor="middle" font-weight="650" data-period-label="true"');
 for(let k=0;k<=3;k++){const x=max*k/3;b+=line(X(x),y0,X(x),y0+ph)+text(X(x),y0+ph+14,fmt(x,0),10,'text-anchor="middle"');}
 for(let z=0;z<=zMax;z+=5)b+=line(x0,Y(z),x0+pw,Y(z))+text(x0-5,Y(z)+3,z,10,'text-anchor="end"');
 if(m?.available){
  const rows=vm.levels.map(l=>m.rows.find(r=>r.level_id===l.id)!);
  b+=`<polygon data-quantile-band="p10-p90" fill="#ccd7d8" points="${rows.map((r,i)=>`${X(r.p10)},${Y(vm.levels[i].height)}`).concat(rows.map((r,i)=>`${X(r.p90)},${Y(vm.levels[i].height)}`).reverse()).join(' ')}"/>`;
  for(const half of [0,1]){const color=half?'#d07032':'#087f83';b+=`<polyline data-half-median="${half+1}" points="${rows.map((r,i)=>`${X(r.half_medians[half])},${Y(vm.levels[i].height)}`).join(' ')}" fill="none" stroke="${color}" stroke-width="2" ${half?'stroke-dasharray="5 2"':''}/>`;
   rows.forEach((r,i)=>{const l=vm.levels[i];b+=`<circle cx="${X(r.half_medians[half])}" cy="${Y(l.height)}" r="1.5" fill="${color}"><title>${esc(`${index+1}月${half?'後半':'前半'} / ${l.pressure} hPa：中央値 ${fmt(r.half_medians[half])} m/s / 月p10 ${fmt(r.p10)}–p90 ${fmt(r.p90)} m/s / 半月${m.half_time_counts[half]}時刻×${m.cell_count}格子`)}</title></circle>`;});}
  b+=text(W/2,205,`${m.time_count}時刻 × ${m.cell_count}格子`,10,'text-anchor="middle"');
 }else{b+=text(108,83,'未取得',13,'text-anchor="middle"')+text(108,103,`${climateYearsLabel(vm.monthlyProfiles?.population.years_fixed??[])}の原標本なし`,10,'text-anchor="middle"')+text(W/2,205,'取得済みの月だけを描画',10,'text-anchor="middle"');}
 b+=text(1,25,'ISA km',10)+text(110,188,'風速 [m/s]',11,'text-anchor="middle"');
 return svg(W,H,b,`${index+1}月の前半・後半中央値と月10–90%幅`,`data-profile="quantiles" data-month="${index+1}" data-available="${m?.available??false}" data-axis-max="${max}" data-height-max="${zMax}"`);
}
