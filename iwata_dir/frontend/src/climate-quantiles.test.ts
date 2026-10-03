import {describe,it,expect} from 'vitest';
import {climateHourSupport,climateYearsLabel,queryIssue,type ClimateArtifact,type ClimateMonthlyProfiles,type ClimateWeighting} from './climateDomain';
import {climateViewModel} from './screens/weather/sources/climateSummary';
import {climateDisplayState} from './screens/weather/climateController';
import {checkedMonthlyProfiles,monthlyProfileView,monthlyProfileScale,monthlyProfilePlot,monthlyProfileLegend,monthlyProfileDefinition,monthlyProfileMethod} from './screens/weather/monthlyProfiles';
import {createWindExport,windDownloadConditions} from './screens/weather/export';

function sample(hours=[0,6,12,18]):ClimateArtifact {
 const cells=[{cell_id:11,lat:40,lon:140,gauss_weight:2},{cell_id:12,lat:40,lon:141,gauss_weight:2},{cell_id:21,lat:41,lon:140,gauss_weight:1},{cell_id:22,lat:41,lon:141,gauss_weight:1}];
 const levels=[{level_id:8,level_hpa:100,isa_alt_m:16000,alt_geom_mean_m:16200,alt_geom_min_m:15000,alt_geom_max_m:17000},{level_id:2,level_hpa:1000,isa_alt_m:100,alt_geom_mean_m:150,alt_geom_min_m:50,alt_geom_max_m:250}];
 const months:ClimateMonthlyProfiles['months']=Array.from({length:12},(_,i)=>{const month=i+1;let expected=0;for(let year=2016;year<=2025;year++)expected+=new Date(Date.UTC(year,month,0)).getUTCDate()*hours.length;return month===1||month===12?{month,available:true,expected_time_count:expected,time_count:expected,half_time_counts:[150*hours.length,expected-150*hours.length],cell_count:4,sample_count:expected*4,rows:levels.map((l,j)=>({level_id:l.level_id,p10:1+j,p90:10+j,half_medians:[4+j,month===12?27:6+j]}))}:{month,available:false,reason:'month_not_acquired',expected_time_count:expected};});
 const timebins=Array.from({length:24},(_,i)=>({timebin_id:i,month:Math.floor(i/2)+1,bin:i%2+1,start_day:i%2?16:1,end_day_min:i%2?28:15,end_day_max:i%2?31:15,n_days_total:150,n_analyses_expected:150*hours.length}));
 const bounds={west:140,east:141,south:40,north:41},query={source_id:'with-raw-manifest',level_id:2,bounds,grain:'half' as const,...(hours.length===4?{}:{hours_utc:hours})};
 const moment={mean_u:2,mean_v:0,mean_speed:3,from_deg:270,time_count:600,valid_time_count:600,missing_time_count:0};
 return {schema:'balloon.climate.analysis-artifact/1',analysis_id:'raw-fixed',query,query_hash:'q-fixed',result_hash:'r-fixed',created_at:'2026-10-02',summary:{schema:'climate-summary/1',source:{source_id:query.source_id,dataset_sha256:'d'.repeat(64),bounds,native_grid:cells,native_grid_count:4,levels,timebins,capabilities:{years_fixed:[2016,2025],date_convention:'UTC',native_hours_utc:[0,6,12,18],grain:'half',annual:true,spatial:true},attribution:{}},query,levels,population:{timebins,selected_cell_ids:cells.map(c=>c.cell_id),selected_cell_count:4,native_grid_count:4,years_fixed:[2016,2025],date_convention:'UTC',native_hours_utc:[0,6,12,18],spatial_weighting:'gauss',count_definition:'per cell'},annual:timebins.flatMap(t=>levels.map(l=>({...moment,timebin_id:t.timebin_id,level_id:l.level_id,pooled_constancy:2/3,spatial_mean_speed_range:1,cell_count:4}))),spatial:{level_id:2,grid:cells,rows:timebins.flatMap(t=>cells.map(c=>({...moment,timebin_id:t.timebin_id,cell_id:c.cell_id,constancy:2/3})))},display_scales:{all_level_cell_mean_speed_max:5,selected_level_cell_mean_speed_max:5,annual_mean_speed_max:5,spatial_mean_speed_range_max:1},provenance:{query_hash:'q-fixed',result_hash:'r-fixed'},monthly_profiles:{schema:'climate-month-profiles/1',method:'inverted_cdf',weighting:'gaussian-area-equal-times',date_convention:'UTC',population:{years_fixed:[2016,2025],hours_utc:hours,selected_cell_ids:cells.map(c=>c.cell_id),level_ids:levels.map(l=>l.level_id)},months,provenance:{bundle_sha256:'a'.repeat(64),manifest_schema:'balloon.climate.raw-months/1',numpy_version:'2.4.2'}}}};
}

describe('fixed monthly empirical quantiles',()=>{
 it('retains old artifacts and the saved mean/rose modes while defaulting new profiles to quantiles',()=>{
  const a=sample();delete a.summary.monthly_profiles;expect(checkedMonthlyProfiles(a)).toBeUndefined();expect(climateViewModel(a).monthlyProfiles).toBeUndefined();
  expect(climateDisplayState({}).monthly_mode).toBe('profile');expect(climateDisplayState({},true).monthly_mode).toBe('quantiles');
  for(const mode of ['profile','rose','quantiles']){const stored={monthly_mode:mode,monthly_grain:'season',monthly_page:1};expect(climateDisplayState(JSON.parse(JSON.stringify(stored)),true).monthly_mode).toBe(mode);}
 });
 it('uses supplied quantiles, all twelve month positions and a common axis including both median curves',()=>{
  const a=sample(),vm=monthlyProfileView(climateViewModel(a));expect(vm.levels.map(l=>l.id)).toEqual([2,8]);expect(vm.annualPeriods.map(p=>p.label)).toEqual(Array.from({length:12},(_,i)=>`${i+1}月`));expect(vm.metadata.grain).toBe('month');expect(vm.annual.flat().every(v=>v===null)).toBe(true);
  expect(monthlyProfileScale(vm)).toBe(30);const plots=Array.from({length:12},(_,i)=>monthlyProfilePlot(vm,i));
  for(let i=0;i<12;i++){expect(plots[i]).toContain(`data-month="${i+1}"`);expect(plots[i]).toContain('data-axis-max="30"');expect(plots[i]).toContain('data-height-max="16"');expect(plots[i]).toContain(`data-period-label="true">${i+1}月</text>`);}
  expect(plots[0]).toContain('data-half-median="1"');expect(plots[0]).toContain('data-half-median="2"');expect(plots[0]).toContain('data-quantile-band="p10-p90"');expect(plots[0]).toContain('1240時刻 × 4格子');expect(plots[1]).toContain('未取得');expect(plots[1]).not.toContain('<polygon');expect(plots[11]).toContain('中央値 27.0 m/s');
 });
 it('shows valid calm quantiles as zero, without confusing them with unacquired months',()=>{
  const a=sample(),m=a.summary.monthly_profiles!.months[0];if(!m.available)throw Error();m.rows.forEach(r=>{r.p10=r.p90=0;r.half_medians=[0,0];});const vm=monthlyProfileView(climateViewModel(a)),plot=monthlyProfilePlot(vm,0);expect(plot).toContain('data-available="true"');expect(plot).toContain('data-quantile-band="p10-p90"');expect(plot).not.toContain('未取得');
 });
 it('validates selected UTC hours and leap-day expected counts without silently reducing the year population',()=>{
  const a=sample([0,18]);expect(checkedMonthlyProfiles(a)!.months[1].expected_time_count).toBe(566);const vm=monthlyProfileView(climateViewModel(a));expect(vm.populationLabel).toContain('UTC 00/18時');expect(monthlyProfilePlot(vm,0)).toContain('620時刻 × 4格子');
  a.summary.monthly_profiles!.population.years_fixed=[2025,2025];expect(()=>checkedMonthlyProfiles(a)).toThrow();
 });
 it.each([
  ['missing month',(p:any)=>p.months.pop()],['duplicate month',(p:any)=>p.months[1]={...p.months[0]}],
  ['wrong hours',(p:any)=>p.population.hours_utc=[0]],['wrong cells',(p:any)=>p.population.selected_cell_ids=[11,12]],
  ['extra level',(p:any)=>p.population.level_ids.push(44)],['missing row',(p:any)=>p.months[0].rows.pop()],['duplicate row',(p:any)=>p.months[0].rows[1]={...p.months[0].rows[0]}],
  ['partial time population',(p:any)=>p.months[0].time_count--],['wrong half counts',(p:any)=>p.months[0].half_time_counts.reverse()],['wrong cell sample count',(p:any)=>p.months[0].sample_count--],
  ['NaN quantile',(p:any)=>p.months[0].rows[0].p10=NaN],['negative speed',(p:any)=>p.months[0].rows[0].half_medians[0]=-1],['reversed interval',(p:any)=>p.months[0].rows[0].p10=100],
  ['statistics on missing month',(p:any)=>p.months[1].rows=[]],['unknown method',(p:any)=>p.method='linear'],['missing bundle identity',(p:any)=>p.provenance.bundle_sha256=''],
 ])('rejects %s instead of painting a partial or different distribution',(_name,mutate)=>{const a=sample();mutate(a.summary.monthly_profiles);expect(()=>climateViewModel(a)).toThrow('月分位');});
 it('exports all twelve months once each, with methods, population, counts and independent provenance',()=>{
  const a=sample([0,18]),vm=monthlyProfileView(climateViewModel(a));const elements=Array.from({length:12},(_,i)=>({viewBox:{baseVal:{width:190,height:212}},closest:()=>({querySelector:()=>({textContent:`${i+1}月`})}),getAttribute:()=>`${i+1}月`,querySelector:()=>({}),innerHTML:monthlyProfilePlot(vm,i).replace(/^<svg[^>]*>|<\/svg>$/g,'')} as unknown as SVGSVGElement));
  const out=createWindExport(vm,'quantiles',elements,{mode:'wind',scale:'all',page:0,background:false,legend:monthlyProfileDefinition+' '+monthlyProfileMethod(vm),keySvg:monthlyProfileLegend()});
  a.query.hours_utc=[6];a.summary.monthly_profiles!.provenance.bundle_sha256='b'.repeat(64);
  expect(out.metadata.periods).toHaveLength(12);expect((out.metadata as any).query.hours_utc).toEqual([0,18]);expect((out.metadata as any).monthly_profiles.provenance.bundle_sha256).toBe('a'.repeat(64));expect(out.source).toContain('inverted_cdf');expect(out.source).toContain('Gaussian');expect(out.source).toContain('独立標本数');expect(out.source).toContain('線形補間分位');expect(out.source.match(/data-profile="quantiles"/g)).toBeNull();
  for(let month=1;month<=12;month++)expect([...out.source.matchAll(/<text\b[^>]*>([^<]*)<\/text>/g)].filter(m=>m[1]===`${month}月`)).toHaveLength(1);
  expect(windDownloadConditions(out.metadata)).toContain('UTC 00/18時');expect(windDownloadConditions(out.metadata)).not.toContain('1000 hPa');
 });
});

function rawSample(weighting:ClimateWeighting='spherical-area-equal-times'):ClimateArtifact {
 const a=sample([0,18]),s=a.summary,p=s.monthly_profiles!;
 s.source.label=weighting==='spherical-area-equal-times'?'ERA5 元時刻標本 2024':'JRA-3Q 元時刻標本 2024';
 s.source.provider=weighting==='spherical-area-equal-times'?'ERA5':'JRA-3Q';s.source.weighting=weighting;
 s.source.capabilities={...s.source.capabilities,years_fixed:[2024,2024],hour_filter:true,hour_level_ids:s.levels.map(l=>l.level_id),wind_rose_hour_filter:true};
 s.population.years_fixed=[2024,2024];s.population.spatial_weighting=weighting;
 s.levels.forEach(l=>{l.alt_geom_mean_m=null;l.alt_geom_min_m=null;l.alt_geom_max_m=null;});
 p.weighting=weighting;p.population.years_fixed=[2024,2024];p.provenance.manifest_schema='balloon.wind-samples/1';
 // 2024 is a leap year. Explicit month lengths are independent of the validator's UTC-calendar implementation.
 const days=[31,29,31,30,31,30,31,31,30,31,30,31];
 p.months=days.map((n,i)=>({month:i+1,available:true,expected_time_count:n*2,time_count:n*2,half_time_counts:[30,(n-15)*2],cell_count:4,sample_count:n*8,rows:s.levels.map(l=>({level_id:l.level_id,p10:0,p90:10,half_medians:[3,6]}))}));
 return a;
}

describe('source-bound raw profiles and filter meaning',()=>{
 it.each(['gaussian-area-equal-times','spherical-area-equal-times'] as const)('uses a single leap year and explicit %s without assuming the legacy ten-year source',weighting=>{
  const a=rawSample(weighting),vm=monthlyProfileView(climateViewModel(a)),feb=vm.monthlyProfiles!.months[1];
  expect(feb.available&&feb.time_count).toBe(58);expect(feb.available&&feb.half_time_counts).toEqual([30,28]);expect(feb.available&&feb.sample_count).toBe(232);
  expect(vm.annualPeriods).toHaveLength(12);expect(vm.annualPeriods[1].description).toContain('2024年');expect(vm.populationLabel).not.toContain('2016');expect(climateYearsLabel([2024,2024])).toBe('2024年');
  expect(monthlyProfileMethod(vm)).toContain(weighting==='spherical-area-equal-times'?'球面格子面積重み':'Gaussian面積重み');expect(vm.annualDefinition).not.toContain('2016');
  expect(vm.levels.every(l=>l.heightDescription.includes('参考高度のみ／実高度未取得'))).toBe(true);expect(vm.levels.some(l=>l.heightDescription.includes('平均0.00'))).toBe(false);
  const plot=monthlyProfilePlot(vm,1);expect(plot).toContain('58時刻 × 4格子');expect(plot).toContain('data-half-median="1"');expect(plot).toContain('data-quantile-band="p10-p90"');
 });
 it('keeps raw source upper levels available to hour filters while retaining the narrower legacy support',()=>{
  const a=rawSample(),d=a.summary.source,q={...a.query,level_id:8};expect(queryIssue(q,d)).toBeNull();expect(climateHourSupport(d)).toContain('1000–100 hPaの2面');expect(climateHourSupport(d)).toContain('風配も選択');
  d.capabilities.hour_level_ids=[2];delete d.capabilities.wind_rose_hour_filter;expect(queryIssue(q,d)).toContain('1000 hPaの1面');expect(queryIssue(q,d)).not.toContain('300');expect(climateHourSupport(d)).toContain('全4時刻のみ');expect(q.level_id).toBe(8);
 });
 it.each([
  ['source year',(a:ClimateArtifact)=>a.summary.source.capabilities.years_fixed=[2016,2025]],
  ['reversed year',(a:ClimateArtifact)=>a.summary.monthly_profiles!.population.years_fixed=[2025,2024]],
  ['absent source weight',(a:ClimateArtifact)=>delete a.summary.source.weighting],
  ['other source weight',(a:ClimateArtifact)=>a.summary.source.weighting='gaussian-area-equal-times'],
  ['other population weight',(a:ClimateArtifact)=>a.summary.population.spatial_weighting='gauss'],
  ['nonleap February',(a:ClimateArtifact)=>{const m=a.summary.monthly_profiles!.months[1];if(m.available){m.time_count=56;m.expected_time_count=56;m.half_time_counts=[30,26];m.sample_count=224;}}],
 ])('rejects %s rather than silently relabeling the raw distribution',(_name,mutate)=>{const a=rawSample();mutate(a);expect(()=>climateViewModel(a)).toThrow('月分位');});
 it('exports fixed ERA5 conditions and explicit missing months without taking the later draft source or Gaussian wording',()=>{
  const a=rawSample();a.summary.monthly_profiles!.months[11]={month:12,available:false,reason:'month_not_acquired',expected_time_count:62};
  const vm=monthlyProfileView(climateViewModel(a)),out=createWindExport(vm,'quantiles',[],{mode:'wind',scale:'all',page:0,background:false,legend:monthlyProfileMethod(vm)});
  a.summary.source.label='Later JRA draft';a.query.hours_utc=[6];
  expect(out.source).toContain('ERA5 元時刻標本 2024');expect(out.source).toContain('球面格子面積重み');expect(out.source).not.toContain('Gaussian');expect(windDownloadConditions(out.metadata)).toContain('ERA5 元時刻標本 2024');expect(windDownloadConditions(out.metadata)).toContain('UTC 00/18時');
  expect((out.metadata as any).monthly_profiles.provenance.manifest_schema).toBe('balloon.wind-samples/1');expect(monthlyProfilePlot(vm,11)).toContain('2024年の原標本なし');expect(monthlyProfilePlot(vm,11)).not.toContain('data-quantile-band');
 });
 it('keeps raw provider credit visible when the SVG metadata is not displayed',()=>{
  const a=rawSample();a.summary.source.profile='original-utc-wind';
  a.summary.source.attribution={metadata:{dataset_doi:'10.example/data',attribution:{license:'CC BY 4.0',license_url:'https://example.invalid/license',acknowledgement:'Original provider credit'}}};
  const vm=monthlyProfileView(climateViewModel(a)),out=createWindExport(vm,'quantiles',[],{mode:'wind',scale:'all',page:0,background:false,legend:monthlyProfileMethod(vm)});
  const visible=out.source.replace(/<metadata>[\s\S]*?<\/metadata>/,'');
  expect(visible).toContain('10.example/data');expect(visible).toContain('CC BY 4.0');expect(visible).toContain('Original provider credit');
  expect((out.metadata as any).source.attribution.metadata.dataset_doi).toBe('10.example/data');
 });
});
