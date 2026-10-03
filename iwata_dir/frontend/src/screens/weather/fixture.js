// Derived from the archived 0.40.1 r2 screen; see frontend/SCREEN_PROVENANCE.md.
export function install(scope) {
const {window,document}=scope;
/* Synthetic dated meteorology for interaction design. No observed wind or scientific adoption. */
'use strict';
window.WindFixture=(()=>{
 const pressures=[1000,925,850,700,500,400,300,250,200,150,100,70,50,30,20,10], heights=pressures.map(p=>7.2*Math.log(1000/p));
 const center={lat:43.05,lon:141.35},kmLat=111.2,kmLon=111.2*Math.cos(center.lat*Math.PI/180);
 const geo=(x,y)=>({lat:center.lat+y/kmLat,lon:center.lon+x/kmLon}),xy=(lat,lon)=>[(lon-center.lon)*kmLon,(lat-center.lat)*kmLat];
 const points=Array.from({length:9},(_,i)=>({id:i,x:(i%3-1)*40,y:(Math.floor(i/3)-1)*40,...geo((i%3-1)*40,(Math.floor(i/3)-1)*40)}));
 const hours=[3,9,15,21],years=[2020,2021,2022,2023,2024,2025],records=[];
 const calendarDefinition={version:'calendar-month-hierarchical-v1',description:'JST暦月を2分割し各半分を2分割。端数側は2000年基点の暦年/月で循環し、閏2月には閏年の通算順を使用。選択年・欠測では変えず、半月は四分割2個の和。'};
 const mod=(n,m)=>((n%m)+m)%m;
 function calendarRanges(year,month){
  const days=new Date(Date.UTC(year,month+1,0)).getUTCDate(),leapsBefore=y=>Math.floor((y-1)/4)-Math.floor((y-1)/100)+Math.floor((y-1)/400);
  // Gregorian leap years need their own ordinal: a year % 4 rotation would
  // always assign February's extra day to the same quarter.
  const cycle=month===1&&days===29?leapsBefore(year)-leapsBefore(2000):year-2000,halfDays=[Math.floor(days/2),Math.floor(days/2)];
  if(days%2)halfDays[mod(cycle+month,2)]++;
  let start=1;const half=[],quarter=[];
  halfDays.forEach((n,h)=>{half.push({from:start,to:start+n-1});const lengths=[Math.floor(n/2),Math.floor(n/2)];if(n%2)lengths[mod((days%2?Math.floor(cycle/2):cycle)+month+h,2)]++;for(const length of lengths){quarter.push({from:start,to:start+length-1});start+=length;}});
  return {year,month,days,half,quarter};
 }
 function periodRanges(grain,index,selectedYears=years){const parts=grain==='quarter'?4:grain==='half'?2:1,month=Math.floor(index/parts),part=index%parts;return selectedYears.map(year=>{const c=calendarRanges(year,month),r=parts===1?{from:1,to:c.days}:c[grain][part];return{year,month,...r,days:r.to-r.from+1};});}

 function normal(seed){let x=(seed*1664525+1013904223)>>>0;const a=(x+1)/4294967297;x=(x*1664525+1013904223)>>>0;return Math.sqrt(-2*Math.log(a))*Math.cos(2*Math.PI*(x+1)/4294967297);}
 function isoWeek(date){const d=new Date(date);d.setUTCHours(0,0,0,0);d.setUTCDate(d.getUTCDate()+4-(d.getUTCDay()||7));const y=d.getUTCFullYear();return {isoYear:y,week:Math.ceil((((d-new Date(Date.UTC(y,0,1)))/86400000)+1)/7)};}
 for(const year of years){for(let stamp=Date.UTC(year,0,1);stamp<Date.UTC(year+1,0,1);stamp+=86400000){const d=new Date(stamp),month=d.getUTCMonth(),day=d.getUTCDate(),doy=(stamp-Date.UTC(year,0,1))/86400000+1,calendar=calendarRanges(year,month),bin=month*2+calendar.half.findIndex(p=>day>=p.from&&day<=p.to),quarter=month*4+calendar.quarter.findIndex(p=>day>=p.from&&day<=p.to),wk=isoWeek(d);for(const hour of hours){
  const id=records.length,uv=new Float32Array(points.length*pressures.length*2),phase=2*Math.PI*(doy-.5)/(new Date(Date.UTC(year,1,29)).getUTCMonth()===1?366:365),a=normal((id+1)*7919),b=normal((id+9)*3571),sun=Math.sin((hour-3)/24*2*Math.PI),yr=(year-2022.5)*.45;
  for(const pt of points)for(let l=0;l<pressures.length;l++){const z=heights[l],jet=(7+23*(1+Math.cos(phase))*.5)*Math.exp(-(((z-11)/4)**2)),upper=12*Math.cos(phase)/(1+Math.exp(-(z-17)/2)),twoPeak=(month>=6&&month<=7?1:0)*Math.exp(-(((z-18)/5)**2))*(day%2?24:-24),variance=(month>=6&&month<=7?3:5)+(pt.x+40)/20,shear=pt.x/40*(2.5+4*Math.sin(phase))*Math.exp(-(((z-7)/7)**2));
   const u=5+jet+upper+twoPeak+shear+variance*a*(.4+.6*Math.sin(z/12+.3))+yr+2.5*sun*Math.exp(-z/3),v=4*Math.sin(phase)+pt.y/40*(2+3*Math.cos(phase))+b*variance*(.5+.5*Math.cos(z/17))+3*Math.sin(z/6+phase)+sun,k=(pt.id*pressures.length+l)*2;uv[k]=u;uv[k+1]=v;}
  records.push({id,year,month,day,doy,bin,quarter,hour,...wk,date:d.toISOString().slice(0,10),validUTC:new Date(stamp+(hour-9)*3600000).toISOString(),uv});
 }}}
 function value(record,point,level){const i=(point*pressures.length+level)*2;return [record.uv[i],record.uv[i+1]];}
 function quantile(a,p){if(!a.length)return NaN;const s=[...a].sort((x,y)=>x-y),t=(s.length-1)*p,i=Math.floor(t);return s[i]+(s[Math.min(i+1,s.length-1)]-s[i])*(t-i);}
 function summary(vectors){let u=0,v=0,s=0;const speeds=[];for(const q of vectors){u+=q[0];v+=q[1];const n=Math.hypot(...q);s+=n;speeds.push(n);}const n=vectors.length;if(!n)return null;u/=n;v/=n;s/=n;const resultant=Math.hypot(u,v);return {u,v,s,R:s?resultant/s:null,dir:resultant===0?null:((Math.atan2(-u,-v)*180/Math.PI)+360)%360,p10:quantile(speeds,.1),median:quantile(speeds,.5),p90:quantile(speeds,.9),n};}
 function domain(){return {xmin:-40,xmax:40,ymin:-40,ymax:40};}
 function supported(x,y){return Number.isFinite(x)&&Number.isFinite(y)&&x>=-40-1e-8&&x<=40+1e-8&&y>=-40-1e-8&&y<=40+1e-8;}
 function weights(x,y){if(!supported(x,y))throw new RangeError('人工場の取得範囲外です。外挿しません。');x=Math.max(-40,Math.min(40,x));y=Math.max(-40,Math.min(40,y));const ix=x<0?0:1,iy=y<0?0:1,tx=(x-(-40+40*ix))/40,ty=(y-(-40+40*iy))/40;return [{point:iy*3+ix,weight:(1-tx)*(1-ty)},{point:iy*3+ix+1,weight:tx*(1-ty)},{point:(iy+1)*3+ix,weight:(1-tx)*ty},{point:(iy+1)*3+ix+1,weight:tx*ty}].filter(q=>q.weight>0);}
 function valueAt(record,x,y,level){const out=[0,0];for(const w of weights(x,y)){const q=value(record,w.point,level);out[0]+=q[0]*w.weight;out[1]+=q[1]*w.weight;}return out;}
 function verticalWeights(h){let lo=0;while(lo<heights.length-2&&heights[lo+1]<h)lo++;const f=(h-heights[lo])/(heights[lo+1]-heights[lo]);return [lo,Math.max(0,Math.min(1,f))];}
 const minuteWeights=Array.from({length:120},(_,m)=>verticalWeights((m<60?m+.5:119.5-m)*.5));
 const layerSeconds=Array(16).fill(0);minuteWeights.forEach(([l,f])=>{layerSeconds[l]+=60*(1-f);layerSeconds[l+1]+=60*f;});
 function profileAt(record,x,y){const w=weights(x,y);return heights.map((_,l)=>{const v=[0,0];for(const q of w){const uv=value(record,q.point,l);v[0]+=uv[0]*q.weight;v[1]+=uv[1]*q.weight;}return v;});}
 function displacementAt(record,x,y){const prof=profileAt(record,x,y);return [x+prof.reduce((s,q,l)=>s+q[0]*layerSeconds[l]/1000,0),y+prof.reduce((s,q,l)=>s+q[1]*layerSeconds[l]/1000,0)];}
 function select({years:range=[2020,2025],hours:hh=hours,period}={}){return records.filter(r=>r.year>=range[0]&&r.year<=range[1]&&hh.includes(r.hour)&&(!period||(period.grain==='quarter'?r.quarter===period.index:period.grain==='half'?r.bin===period.index:period.grain==='season'?Math.floor(((r.month+1)%12)/3)===period.index:r.month===period.index)));}
 const definition='日付付き人工u/v場。2020–2025年の全暦日×03/09/15/21 JST。元格子9点×16圧力面。実観測・再解析・予報ではない。';
 function generateSeason({lat=center.lat,lon=center.lon,years:range=[2020,2025],hours:hh=hours,period={grain:'month',index:6},idPrefix='S',calendar=calendarDefinition.version}={}){
  const [x,y]=xy(lat,lon);if(!supported(x,y))throw new RangeError('指定地点は人工気象の取得範囲外です');
  if(![calendarDefinition.version,'legacy-fixed15-v1'].includes(calendar))throw new RangeError('未対応の暦区切り版です');
  const legacy=calendar==='legacy-fixed15-v1',effectiveCalendar=legacy?{version:calendar,description:'0.34/0.35保存候補の再現用：毎月1–15日/16日–月末で固定'}:calendarDefinition;
  const chosen=legacy?select({years:range,hours:hh}).filter(r=>period.grain==='half'?r.month===Math.floor(period.index/2)&&(r.day>15?1:0)===period.index%2:r.month===period.index):select({years:range,hours:hh,period});if(!chosen.length)throw new RangeError('対象気象標本がありません');
  const samples=chosen.map(r=>{const profile=profileAt(r,x,y),history=[];let e=0,n=0,distance=0;
   for(let t=0;t<=120;t++){const h=(t<=60?t:120-t)*.5,[l,f]=verticalWeights(h),u=profile[l][0]*(1-f)+profile[l+1][0]*f,v=profile[l][1]*(1-f)+profile[l+1][1]*f;history.push({t,phase:t<60?'up':'down',h,e,n,distance,speed:Math.hypot(u,v),vertical:t<60?500/60:t<120?-500/60:0,u,v});if(t<120){const [ml,mf]=minuteWeights[t],mu=profile[ml][0]*(1-mf)+profile[ml+1][0]*mf,mv=profile[ml][1]*(1-mf)+profile[ml+1][1]*mf;e+=mu*.06;n+=mv*.06;distance+=Math.hypot(mu,mv)*.06;}}
   const end=geo(x+e,y+n);return {id:`${idPrefix}-${r.id}`,sourceRecordId:r.id,weatherValidUTC:r.validUTC,duration:120,burst:60,status:'landed',...end,history};});
  const sw=geo(-40,-40),ne=geo(40,40);return {samples,calendarDefinition:effectiveCalendar,periodRanges:periodRanges(period.grain,period.index,years.filter(y=>y>=range[0]&&y<=range[1])).map(r=>legacy&&period.grain==='half'?{...r,from:period.index%2?16:1,to:period.index%2?new Date(Date.UTC(r.year,r.month+1,0)).getUTCDate():15,days:period.index%2?new Date(Date.UTC(r.year,r.month+1,0)).getUTCDate()-15:15}:r),sourceCount:chosen.length,sourceIds:chosen.map(r=>r.id),origin:[lat,lon],bounds:[[sw.lat,sw.lon],[ne.lat,ne.lon]],definition:definition+' 季節試算は放球点の気柱を時空間固定し、上昇60分/下降60分・最高30kmという処方高度に沿ってu/vを加算した操作用模型。1分中点積算。熱・抗力・破裂・地形着地・予報誤差を解かない。放球時計はこの凍結場計算へ影響しない。'};
 }
 return {calendarDefinition,calendarRanges,periodRanges,pressures,heights,points,hours,years,records,center,geo,xy,isoWeek,value,quantile,summary,domain,supported,weights,valueAt,profileAt,displacementAt,displacement:(r,p)=>displacementAt(r,points[p].x,points[p].y),select,generateSeason,layerSeconds,definition};
})();

}
