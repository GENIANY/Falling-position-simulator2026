"""Bounded SQL aggregation: time within each cell, then Gaussian region means."""
from .contracts import ClimateError
from .periods import periods
from .statistics import vector_summary

GRID_WHERE = "g.lon BETWEEN ? AND ? AND g.lat BETWEEN ? AND ?"


def rows(con, sql, params=()):
    cursor = con.execute(sql, params)
    keys = [item[0] for item in cursor.description]
    return [dict(zip(keys, row)) for row in cursor.fetchall()]


def cell_query(grain, hours):
    # Identifiers and VALUES come only from the fixed calendar, never user SQL.
    mapping = ",".join(f"({member},{p['timebin_id']})" for p in periods(grain) for member in p['member_timebin_ids'])
    table = "fact_wind_diurnal" if hours else "fact_wind"
    hour_filter = " AND w.hour_utc IN (" + ",".join("?" for _ in hours) + ")" if hours else ""
    return f"""WITH cells AS (
        SELECT p.period_id AS timebin_id,w.level_id,w.cell_id,
          sum(cast(w.u_mean AS DOUBLE)*w.n)/sum(w.n) AS mean_u,
          sum(cast(w.v_mean AS DOUBLE)*w.n)/sum(w.n) AS mean_v,
          sum(cast(w.speed_mean AS DOUBLE)*w.n)/sum(w.n) AS mean_speed,
          cast(sum(w.n) AS BIGINT) AS time_count
        FROM main.{table} w JOIN (VALUES {mapping}) p(native_id,period_id) ON w.timebin_id=p.native_id
        JOIN main.dim_grid g USING(cell_id)
        WHERE {GRID_WHERE}{hour_filter} GROUP BY p.period_id,w.level_id,w.cell_id)
    """


def annual(con, bounds, grain, hours, cell_count, level_count):
    values = rows(con, cell_query(grain, hours) + """SELECT c.timebin_id,c.level_id,
       sum(c.mean_u*g.gauss_weight)/sum(g.gauss_weight) AS mean_u,
       sum(c.mean_v*g.gauss_weight)/sum(g.gauss_weight) AS mean_v,
       sum(c.mean_speed*g.gauss_weight)/sum(g.gauss_weight) AS mean_speed,
       min(c.time_count) AS time_count,max(c.time_count) AS max_time_count,count(*) AS cell_count,
       max(c.mean_speed)-min(c.mean_speed) AS spatial_mean_speed_range,
       max(c.mean_speed) AS max_cell_mean_speed
       FROM cells c JOIN main.dim_grid g USING(cell_id)
       GROUP BY c.timebin_id,c.level_id ORDER BY c.timebin_id,c.level_id""", bounds + list(hours or ()))
    expected = {p['timebin_id']: p['n_analyses_expected'] for p in periods(grain, len(hours) if hours else 4)}
    if len(values) != len(expected) * level_count:
        raise ClimateError("CLIMATE_COUNTS", "Grouped annual summaries are incomplete.")
    for row in values:
        if row.pop('max_time_count') != row['time_count'] or row['time_count'] != expected[row['timebin_id']] or row['cell_count'] != cell_count:
            raise ClimateError("CLIMATE_COUNTS", "Grouped time or grid support differs from the selected population.")
        vector = vector_summary(row['mean_u'], row['mean_v'], row['mean_speed'])
        vector['pooled_constancy'] = vector.pop('constancy')
        row.update(vector, valid_time_count=row['time_count'], missing_time_count=0)
    return values


def spatial(con, bounds, grain, hours, level_id, cell_count):
    values = rows(con, cell_query(grain, hours) + """SELECT timebin_id,cell_id,mean_u,mean_v,mean_speed,time_count
                  FROM cells WHERE level_id=? ORDER BY timebin_id,cell_id""", bounds + list(hours or ()) + [level_id])
    expected = {p['timebin_id']: p['n_analyses_expected'] for p in periods(grain, len(hours) if hours else 4)}
    if len(values) != len(expected) * cell_count:
        raise ClimateError("CLIMATE_COUNTS", "Grouped spatial summaries are incomplete.")
    for row in values:
        if row['time_count'] != expected[row['timebin_id']]:
            raise ClimateError("CLIMATE_COUNTS", "Grouped spatial time support is incomplete.")
        row.update(vector_summary(row['mean_u'], row['mean_v'], row['mean_speed']),
                   valid_time_count=row['time_count'], missing_time_count=0)
    return values


def scales(values, level_id):
    return {"all_level_cell_mean_speed_max": max(r['max_cell_mean_speed'] for r in values),
            "selected_level_cell_mean_speed_max": max(r['max_cell_mean_speed'] for r in values if r['level_id'] == level_id),
            "annual_mean_speed_max": max(r['mean_speed'] for r in values), "constancy": [0, 1], "from_deg": [0, 360],
            "spatial_mean_speed_range_max": max(r['spatial_mean_speed_range'] for r in values),
            "population": "selected native grid centers and hours; maxima of period cell means, not instantaneous maxima"}
