"""Optional supplied tables: supported hourly moments and one-point wind roses.

Absent tables leave the original means-only profile usable. Present but malformed
tables fail registration; they never silently fall back to a different population.
"""
from .aggregation import rows
from .contracts import ClimateError
from .periods import periods
from .statistics import ROUNDING_RELATIVE_TOLERANCE


def _check_table(con, table, columns):
    tables = dict(con.execute("SELECT table_name,table_type FROM information_schema.tables WHERE table_schema='main'").fetchall())
    if tables.get(table) != 'BASE TABLE':
        raise ClimateError('CLIMATE_SCHEMA', f'Required extension base table {table} is absent.')
    types = dict(con.execute("SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='main' AND table_name=?", [table]).fetchall())
    integers = {'TINYINT','SMALLINT','INTEGER','BIGINT','UTINYINT','USMALLINT','UINTEGER','UBIGINT'}
    for name, kind in columns.items():
        allowed = integers if kind == 'integer' else integers | {'FLOAT','DOUBLE'} if kind == 'number' else {kind}
        if types.get(name) not in allowed:
            raise ClimateError('CLIMATE_SCHEMA', f'Unsupported extension column {table}.{name}.')


def inspect_extensions(con, levels, grid):
    tables = {r[0] for r in con.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='main'").fetchall()}
    support = {'hour_level_ids': [], 'rose': None}
    if 'fact_wind_diurnal' in tables:
        columns = {k:'integer' for k in ('timebin_id','level_id','cell_id','hour_utc','n')}
        columns.update({k:'number' for k in ('u_mean','v_mean','speed_mean')})
        _check_table(con, 'fact_wind_diurnal', columns)
        units = con.execute("SELECT column_name,units FROM main.meta_column WHERE table_name='fact_wind_diurnal' AND column_name IN ('u_mean','v_mean','speed_mean')").fetchall()
        if len(units) != 3 or dict(units) != {k: 'm s-1' for k in ('u_mean','v_mean','speed_mean')}:
            raise ClimateError('CLIMATE_UNSUPPORTED', 'Hourly wind moments must declare supported m s-1 units.')
        ids = [r['level_id'] for r in levels if 300 <= r['level_hpa'] <= 1000]
        count = con.execute('SELECT count(*) FROM main.fact_wind_diurnal').fetchone()[0]
        if not ids or count != 24 * len(ids) * len(grid) * 4:
            raise ClimateError('CLIMATE_COUNTS', 'Hourly moments must cover the complete supported product.')
        duplicate = con.execute('SELECT 1 FROM main.fact_wind_diurnal GROUP BY timebin_id,level_id,cell_id,hour_utc HAVING count(*)<>1 LIMIT 1').fetchone()
        invalid = con.execute('''SELECT count(*) FROM main.fact_wind_diurnal w
           LEFT JOIN main.dim_timebin t USING(timebin_id) LEFT JOIN main.dim_level l USING(level_id)
           LEFT JOIN main.dim_grid g USING(cell_id)
           WHERE t.timebin_id IS NULL OR l.level_id IS NULL OR g.cell_id IS NULL OR l.level_hpa<300
             OR w.hour_utc IS NULL OR w.hour_utc NOT IN (0,6,12,18) OR w.n IS NULL OR w.n<>t.n_days_total
             OR w.u_mean IS NULL OR w.v_mean IS NULL OR w.speed_mean IS NULL
             OR NOT isfinite(w.u_mean) OR NOT isfinite(w.v_mean) OR NOT isfinite(w.speed_mean) OR w.speed_mean<0
             OR sqrt(pow(cast(w.u_mean AS DOUBLE),2)+pow(cast(w.v_mean AS DOUBLE),2))>
                cast(w.speed_mean AS DOUBLE)+?*greatest(1,cast(w.speed_mean AS DOUBLE))
             OR (w.speed_mean=0 AND (w.u_mean<>0 OR w.v_mean<>0))''', [ROUNDING_RELATIVE_TOLERANCE]).fetchone()[0]
        if duplicate or invalid:
            raise ClimateError('CLIMATE_COUNTS', 'Invalid hourly moments, keys or support.')
        support['hour_level_ids'] = ids
    rose_tables = {'fact_wind_rose','dim_sector','dim_speed_class'}
    if tables & rose_tables:
        _check_table(con, 'fact_wind_rose', {k:'integer' for k in ('timebin_id','level_id','cell_id','sector','speed_class','count')})
        _check_table(con, 'dim_sector', {'sector':'integer','centre_deg':'number','lo_deg':'number','hi_deg':'number','wraps_north':'BOOLEAN','compass_16':'VARCHAR'})
        _check_table(con, 'dim_speed_class', {'speed_class':'integer','lo_ms':'number','hi_ms':'number','label':'VARCHAR'})
        if con.execute('SELECT count(*) FROM main.dim_sector').fetchone()[0] != 16 or con.execute('SELECT count(*) FROM main.dim_speed_class').fetchone()[0] != 6:
            raise ClimateError('CLIMATE_SUPPORT', 'Unsupported wind-rose bin counts.')
        sectors = rows(con, 'SELECT sector,centre_deg,lo_deg,hi_deg,wraps_north,compass_16 FROM main.dim_sector ORDER BY sector')
        speeds = rows(con, 'SELECT speed_class,lo_ms,hi_ms,label FROM main.dim_speed_class ORDER BY speed_class')
        names = 'N NNE NE ENE E ESE SE SSE S SSW SW WSW W WNW NW NNW'.split()
        expected_sectors = [dict(sector=i,centre_deg=i*22.5,lo_deg=(i*22.5-11.25)%360,hi_deg=i*22.5+11.25,wraps_north=i==0,compass_16=n) for i,n in enumerate(names)]
        expected_speeds = [dict(speed_class=i,lo_ms=a,hi_ms=b,label=label) for i,(a,b,label) in enumerate(zip([0,5,10,20,30,50],[5,10,20,30,50,None],['0-5','5-10','10-20','20-30','30-50','50+']))]
        if sectors != expected_sectors or speeds != expected_speeds:
            raise ClimateError('CLIMATE_SUPPORT', 'Unsupported wind-rose bin definitions.')
        count = con.execute('SELECT count(*) FROM main.fact_wind_rose').fetchone()[0]
        if count != 24 * len(levels) * 16 * 6:
            raise ClimateError('CLIMATE_COUNTS', 'Wind rose must cover one native point and all periods/levels/bins.')
        cells = con.execute('SELECT DISTINCT cell_id FROM main.fact_wind_rose').fetchall()
        if len(cells) != 1 or cells[0][0] not in {r['cell_id'] for r in grid}:
            raise ClimateError('CLIMATE_SUPPORT', 'Wind rose must identify one native grid point.')
        duplicate = con.execute('SELECT 1 FROM main.fact_wind_rose GROUP BY timebin_id,level_id,cell_id,sector,speed_class HAVING count(*)<>1 LIMIT 1').fetchone()
        invalid = con.execute('''SELECT count(*) FROM main.fact_wind_rose r
           LEFT JOIN main.dim_timebin t USING(timebin_id) LEFT JOIN main.dim_level l USING(level_id)
           LEFT JOIN main.dim_sector s USING(sector) LEFT JOIN main.dim_speed_class c USING(speed_class)
           WHERE t.timebin_id IS NULL OR l.level_id IS NULL OR s.sector IS NULL OR c.speed_class IS NULL
             OR r.count IS NULL OR r.count<0''').fetchone()[0]
        wrong_total = con.execute('''SELECT 1 FROM main.fact_wind_rose r JOIN main.dim_timebin t USING(timebin_id)
           GROUP BY r.timebin_id,r.level_id,t.n_analyses_expected HAVING sum(r.count)<>t.n_analyses_expected LIMIT 1''').fetchone()
        if duplicate or invalid or wrong_total:
            raise ClimateError('CLIMATE_COUNTS', 'Wind-rose counts or population support are invalid.')
        support['rose'] = {'point': next(r for r in grid if r['cell_id'] == cells[0][0]), 'sectors': sectors, 'speed_classes': speeds}
    return support


def wind_rose(con, support, grain, hours, level_id, bounds):
    if hours:
        return {'available': False, 'reason': 'hour_subset_not_available'}
    if support['rose'] is None:
        return {'available': False, 'reason': 'source_has_no_wind_rose'}
    bins = periods(grain)
    mapping = ','.join(f"({member},{p['timebin_id']})" for p in bins for member in p['member_timebin_ids'])
    values = rows(con, f'''SELECT p.period_id AS timebin_id,r.sector,r.speed_class,cast(sum(r.count) AS BIGINT) AS count
        FROM main.fact_wind_rose r JOIN (VALUES {mapping}) p(native_id,period_id) ON r.timebin_id=p.native_id
        WHERE r.level_id=? GROUP BY p.period_id,r.sector,r.speed_class ORDER BY p.period_id,r.sector,r.speed_class''', [level_id])
    counts = {p['timebin_id']:p['n_analyses_expected'] for p in bins}
    for row in values:
        row.update(time_count=counts[row['timebin_id']], frequency=row['count']/counts[row['timebin_id']])
    point = support['rose']['point']
    return {'available': True, **support['rose'], 'level_id':level_id, 'rows':values,
            'point_in_selected_region': bounds.west<=point['lon']<=bounds.east and bounds.south<=point['lat']<=bounds.north,
            'native_hours_utc':[0,6,12,18], 'date_convention':'UTC',
            'definition':'empirical count / pooled per-point analyses; FROM north=0 clockwise; speed bins lower-inclusive upper-exclusive; no separate calm category'}
