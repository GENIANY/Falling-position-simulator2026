"""Original UTC wind archives projected into the shared climate analysis contract.

Acquisition is a separate CLI responsibility. No HTTP request from this adapter
downloads or interpolates a weather field. JRA and ERA archives retain their own
native coordinates, pressure levels and period; neither relabels the older DB.
"""
from collections import OrderedDict
from copy import deepcopy
import hashlib
import math
from threading import RLock

import numpy as np

from .aggregation import scales
from .contracts import Bounds, ClimateError, ClimateQuery
from .periods import QUARTER_CALENDAR, annual_quarters, periods
from .samples import MonthlySamples
from .source import _canonical, adapter_source_snapshot
from .statistics import combine_cells, vector_summary

VERSION = 'original-utc-wind/2'


def isa_height(pressure_hpa):
    """Dry standard-atmosphere geopotential altitude for a display axis only."""
    gas, gravity = 287.05287, 9.80665
    h, t, p = 0., 288.15, 101325.
    target = pressure_hpa * 100
    for top, lapse in ((11000.,-.0065),(20000.,0.),(32000.,.001),(47000.,.0028),(51000.,0.)):
        top_t = t + lapse*(top-h)
        top_p = p * (math.exp(-gravity*(top-h)/(gas*t)) if not lapse else (top_t/t)**(-gravity/(gas*lapse)))
        if target >= top_p:
            return h - gas*t/gravity*math.log(target/p) if not lapse else h+t/lapse*((target/p)**(-gas*lapse/gravity)-1)
        h,t,p = top,top_t,top_p
    raise ClimateError('CLIMATE_SUPPORT', '参考高度軸の対応範囲外です。')


class WindArchiveSource:
    def __init__(self, path):
        self._lock = RLock()
        self._samples = MonthlySamples(path)
        if self._samples.schema != 'balloon.wind-samples/1' or set(self._samples.months) != set(range(1,13)):
            raise ClimateError('CLIMATE_COUNTS', '年間分析には指定年の12か月すべての原標本が必要です。')
        self._snapshot = adapter_source_snapshot()
        self.dataset_sha256 = self._samples.bundle_sha256
        self.source_id = 'climate-' + hashlib.sha256(_canonical([VERSION,self.dataset_sha256])).hexdigest()
        self._grid = self._samples.grid
        self._levels = [{**r, 'isa_alt_m': isa_height(r['level_hpa']),
                         'alt_geom_mean_m': None, 'alt_geom_min_m': None, 'alt_geom_max_m': None}
                        for r in self._samples.levels]
        self._bounds = Bounds(min(r['lon'] for r in self._grid),max(r['lon'] for r in self._grid),
                              min(r['lat'] for r in self._grid),max(r['lat'] for r in self._grid))
        centre = ((self._bounds.north+self._bounds.south)/2,(self._bounds.east+self._bounds.west)/2)
        self._point = min(self._grid, key=lambda c:(c['lat']-centre[0])**2+(c['lon']-centre[1])**2)
        self._cache = OrderedDict()

    def _assert_current(self):
        self._samples.assert_current()
        if adapter_source_snapshot() != self._snapshot:
            raise ClimateError('CLIMATE_ADAPTER_CHANGED', '原標本の分析コードが変更されました。再起動が必要です。')

    def descriptor(self):
        self._assert_current()
        m = self._samples.manifest
        return deepcopy({'source_id':self.source_id,'dataset_sha256':self.dataset_sha256,
            'dataset_bytes':sum(p.stat().st_size for p in self._samples._files),
            'adapter_version':VERSION,'statistics_version':VERSION,'profile':'original-utc-wind',
            'provider':m['provider'],'label':m['label'],'source_code':self._snapshot,'duckdb_version':'not-used',
            'numerical_dependencies':{'numpy':np.__version__},
            'units':{'wind':'m/s','pressure':'hPa','altitude':'m','direction':'degree'},
            'capabilities':{'annual':True,'spatial':True,'years_fixed':self._samples.years,
                'date_convention':'UTC','native_hours_utc':[0,6,12,18],'grain':'half',
                'raw_observations':True,'year_filter':False,'display_grains':['half','month','season'],
                'annual_grains':['quarter','half','month','season'],
                'hour_filter':True,'hour_level_ids':[l['level_id'] for l in self._levels],
                'wind_rose':True,'wind_rose_hours_utc':[0,6,12,18],'wind_rose_hour_filter':True,
                'wind_rose_point_select':True,
                'quantile_reconstruction':False,'empirical_monthly_profiles':True,'flight_weather_field':False,
                'missing_policy':'reject_incomplete_or_unequal_support'},
            'weighting':self._samples.weighting,
            'bounds':self._bounds.as_dict(),'native_grid_count':len(self._grid),'native_grid':self._grid,
            'levels':self._levels,'timebins':periods('half',years=self._samples.years),
            'wind_rose_point':{k:self._point[k] for k in ('cell_id','lat','lon')},
            'height_definition':'ISA reference display altitude only; no observed/geopotential height acquired',
            'attribution':{'status':'original wind subset; acquisition receipts retained',
                'metadata':{'provider':m['provider'],'label':m['label'],
                    'dataset_url':m.get('provenance',{}).get('dataset_url'),
                    **{key:deepcopy(m['provenance'][key]) for key in
                       ('citation','dataset_doi','license','attribution','conversion','derived_subset')
                       if key in m.get('provenance',{})}}},
            'raw_samples':{'schema':self._samples.schema,'bundle_sha256':self.dataset_sha256,
                'complete_months':list(range(1,13)),'years_fixed':self._samples.years}})

    def verify_full(self):
        self._assert_current()
        return {'source_id':self.source_id,'dataset_sha256':self.dataset_sha256,'raw_samples':self._samples.verify_full()}

    def _moments(self, grid, hours):
        indices = [self._grid.index(c) for c in grid]
        values, quarter_rows = {}, {}
        quarters = annual_quarters(len(hours), self._samples.years)
        for month, item in self._samples.months.items():
            take = np.array([i for i,t in enumerate(item['times']) if int(t[11:13]) in hours])
            days = np.array([int(item['times'][i][8:10]) for i in take])
            halves = days <= 15
            u = np.load(item['files']['u'],mmap_mode='r',allow_pickle=False)
            v = np.load(item['files']['v'],mmap_mode='r',allow_pickle=False)
            for li,l in enumerate(self._levels):
                a = u[take,li,:][:,indices].astype(float)
                b = v[take,li,:][:,indices].astype(float)
                s = np.hypot(a,b)
                for half,mask in enumerate((halves,~halves)):
                    values[((month-1)*2+half,l['level_id'])] = (int(mask.sum()),np.stack([a[mask].mean(0),b[mask].mean(0),s[mask].mean(0)]))
                # Quarter means come from original UTC samples, never interpolated
                # half means. Retain only regional annual rows, not 48 spatial grids.
                for period in quarters[(month-1)*4:month*4]:
                    mask = (days >= period['start_day']) & (days <= period['end_day_max'])
                    n = int(mask.sum())
                    means = np.stack([a[mask].mean(0), b[mask].mean(0), s[mask].mean(0)])
                    quarter_rows[(period['timebin_id'],l['level_id'])] = self._annual_row(
                        self._cell_rows(means,n,grid),n,period['timebin_id'],l['level_id'])
            del u,v
        return values, [quarter_rows[(p['timebin_id'],l['level_id'])] for p in quarters for l in self._levels]

    @staticmethod
    def _cell_rows(means, n, grid):
        return [{'mean_u':float(means[0,i]),'mean_v':float(means[1,i]),'mean_speed':float(means[2,i]),
                 'weight':c['gauss_weight'],'time_count':n} for i,c in enumerate(grid)]

    @staticmethod
    def _period_means(values, period, level_id):
        # Preserve the pre-cache count weighting and addition order exactly.
        rows = [values[(i,level_id)] for i in period['member_timebin_ids']]
        n = sum(row[0] for row in rows)
        return n, sum(count*mean for count,mean in rows)/n

    @staticmethod
    def _annual_row(cell_rows, n, timebin_id, level_id):
        row = combine_cells(cell_rows)
        row.update(timebin_id=timebin_id,level_id=level_id,
                   max_cell_mean_speed=max(r['mean_speed'] for r in cell_rows),valid_time_count=n,missing_time_count=0)
        return row

    def _annual(self, values, grid, bins):
        annual = []
        for period in bins:
            for l in self._levels:
                n, means = self._period_means(values,period,l['level_id'])
                annual.append(self._annual_row(self._cell_rows(means,n,grid),n,period['timebin_id'],l['level_id']))
        return annual

    def _spatial(self, values, grid, bins, level_id):
        spatial = []
        for period in bins:
            n, means = self._period_means(values,period,level_id)
            for cell,row in zip(grid,self._cell_rows(means,n,grid)):
                spatial.append({**vector_summary(row['mean_u'],row['mean_v'],row['mean_speed']),
                    'timebin_id':period['timebin_id'],'cell_id':cell['cell_id'],
                    'time_count':n,'valid_time_count':n,'missing_time_count':0})
        return spatial

    def _rose_counts(self, level_id, hours, point):
        """Read the selected native column once for all three display grains."""
        li = next(i for i,l in enumerate(self._levels) if l['level_id']==level_id)
        ci = self._grid.index(point)
        counts = {}
        for month,item in self._samples.months.items():
            take = np.array([i for i,t in enumerate(item['times']) if int(t[11:13]) in hours])
            first = np.array([int(item['times'][i][8:10])<=15 for i in take])
            u = np.load(item['files']['u'],mmap_mode='r',allow_pickle=False)[take,li,ci].astype(float)
            v = np.load(item['files']['v'],mmap_mode='r',allow_pickle=False)[take,li,ci].astype(float)
            speed = np.hypot(u,v)
            direction = (np.degrees(np.arctan2(-u,-v))+360)%360
            sector = np.floor((direction+11.25)/22.5).astype(int)%16
            speed_class = np.searchsorted([5,10,20,30,50],speed,side='right')
            for half,mask in enumerate((first,~first)):
                moving = mask & (speed>0)
                counts[(month-1)*2+half] = (int(mask.sum()),np.bincount(sector[moving]*6+speed_class[moving],minlength=96),int((mask & (speed==0)).sum()))
        return counts

    def _rose(self, counts, level_id, hours, bounds, grain, point):
        labels = 'N NNE NE ENE E ESE SE SSE S SSW SW WSW W WNW NW NNW'.split()
        rows,calms = [],[]
        for p in periods(grain,len(hours),self._samples.years):
            n = sum(counts[i][0] for i in p['member_timebin_ids'])
            summed = sum(counts[i][1] for i in p['member_timebin_ids'])
            calm = sum(counts[i][2] for i in p['member_timebin_ids'])
            rows.extend({'timebin_id':p['timebin_id'],'sector':i//6,'speed_class':i%6,
                         'count':int(c),'frequency':float(c/n),'time_count':n} for i,c in enumerate(summed))
            calms.append({'timebin_id':p['timebin_id'],'count':calm,'frequency':calm/n,'time_count':n})
        return {'available':True,'level_id':level_id,'native_hours_utc':list(hours),
            'date_convention':'UTC','definition':'FROM; calm has no direction and remains in the total denominator',
            'point':{k:point[k] for k in ('cell_id','lat','lon')},
            'point_in_selected_region':bounds.west<=point['lon']<=bounds.east and bounds.south<=point['lat']<=bounds.north,
            'sectors':[{'sector':i,'centre_deg':i*22.5,'compass_16':label} for i,label in enumerate(labels)],
            'speed_classes':[{'speed_class':i,'lo_ms':lo,'hi_ms':hi,'label':label} for i,(lo,hi,label) in enumerate(
                zip([0,5,10,20,30,50],[5,10,20,30,50,None],['0–5','5–10','10–20','20–30','30–50','50+']))],
            'rows':rows,'calm_counts':calms}

    def query(self, query):
        try:
            with self._lock:
                return self._query(query)
        except ClimateError:
            raise
        except (OSError,ValueError,EOFError) as exc:
            self._assert_current()
            raise ClimateError('CLIMATE_SAMPLES','原標本の再集計に失敗しました。部分的な結果は保存しません。') from exc

    def _query(self, query):
        query = query if isinstance(query,ClimateQuery) else ClimateQuery.from_mapping(query)
        self._assert_current()
        if query.source_id!=self.source_id:
            raise ClimateError('CLIMATE_SOURCE_CHANGED','選択資料が一致しません。')
        if query.level_id not in {l['level_id'] for l in self._levels}:
            raise ClimateError('CLIMATE_SUPPORT','この原標本束に気圧面がありません。')
        point = self._point if query.rose_cell_id is None else next(
            (c for c in self._grid if c['cell_id'] == query.rose_cell_id), None)
        if point is None:
            raise ClimateError('CLIMATE_SUPPORT','この原標本束に指定した風配の元格子IDがありません。')
        b = query.bounds or self._bounds
        if b.west<self._bounds.west or b.east>self._bounds.east or b.south<self._bounds.south or b.north>self._bounds.north:
            raise ClimateError('CLIMATE_BOUNDS','指定範囲は元格子の支持外です。')
        grid = [c for c in self._grid if b.west<=c['lon']<=b.east and b.south<=c['lat']<=b.north]
        if not grid:
            raise ClimateError('CLIMATE_EMPTY_REGION','元格子を含まない範囲です。')
        hours = tuple(query.hours_utc or (0,6,12,18)); key = (*b.as_dict().values(),hours)
        if key not in self._cache:
            moments, quarters = self._moments(grid,hours)
            groups = {}
            for grain in ('half','month','season'):
                bins = periods(grain,len(hours),self._samples.years)
                groups[grain] = {'timebins':bins,'annual':self._annual(moments,grid,bins)}
            self._cache[key] = {'moments':moments,'groups':groups,'quarters':quarters,
                                'profiles':self._samples.profiles(grid,self._levels,hours)}
            if len(self._cache)>4:self._cache.popitem(last=False)
        self._cache.move_to_end(key)
        cached = self._cache[key]
        counts = self._rose_counts(query.level_id,hours,point)
        # Cache owns only pressure/point-invariant values. A new envelope below
        # keeps selected-level rows and scales out of those reusable dictionaries.
        groups = {grain:{**group,
            'spatial_rows':self._spatial(cached['moments'],grid,group['timebins'],query.level_id),
            'display_scales':scales(group['annual'],query.level_id),
            'wind_rose':self._rose(counts,query.level_id,hours,b,grain,point)}
            for grain,group in cached['groups'].items()}
        half = groups.pop('half')
        resolved = {**query.as_dict(),'bounds':b.as_dict()}
        qhash = hashlib.sha256(_canonical({'query':resolved,'code':self._snapshot,'numpy':np.__version__,'version':VERSION})).hexdigest()
        result = {'schema':'climate-summary/1','source':self.descriptor(),'query':resolved,
            'population':{'years_fixed':self._samples.years,'date_convention':'UTC','native_hours_utc':list(hours),
                'timebins':half['timebins'],'selected_cell_ids':[c['cell_id'] for c in grid],
                'native_grid_count':len(self._grid),'selected_cell_count':len(grid),
                'spatial_weighting':self._samples.weighting,'missing_policy':'reject_incomplete_or_unequal_support',
                'missing_cell_count':0,'effective_independent_time_count':None,
                'count_definition':'UTC times per grid; space-time values are not independent weather samples'},
            'levels':self._levels,'annual':half['annual'],'spatial':{'level_id':query.level_id,'grid':grid,'rows':half['spatial_rows']},
            'display_scales':half['display_scales'],'wind_rose':half['wind_rose'],
            'summaries_by_grain':groups,'monthly_profiles':cached['profiles'],
            'annual_quarters':{'schema':'climate-annual-quarters/1','date_convention':'UTC',
                'calendar_definition':QUARTER_CALENDAR,'timebins':annual_quarters(len(hours),self._samples.years),
                'annual':cached['quarters'],'display_scales':scales(cached['quarters'],query.level_id)},
            'provenance':{'query_hash':qhash,'adapter_version':VERSION,'statistics_version':VERSION,
                'numpy_version':np.__version__,'definitions':{'quantiles':'weighted inverse empirical CDF of grid-time scalar speeds',
                    'periods':'UTC calendar half-months 1–15 and 16–end; month and season means pooled by actual counts',
                    'height':'standard-atmosphere reference axis only; geometric height not acquired'}}}
        self._assert_current()
        result=deepcopy(result)
        result['provenance']['result_hash']=hashlib.sha256(_canonical(result)).hexdigest()
        return result
