"""Display periods made from disjoint UTC half-month supports.

These IDs describe grouping, never synthetic timestamps or connected winters.
"""
import calendar

from .statistics import utc_half_months


QUARTER_CALENDAR = {
    'version': 'utc-half-nested-quarters/1',
    'description': 'UTC 1–7 / 8–15 / 16–22 / 23–末日。既存の各半月を二分し、各年の暦日を等しく数える年間図専用の48区分。',
}


def annual_quarters(hour_count=4, years=(2016, 2025)):
    """Annual-only bins nested in halves; not a query or flight-interest grain.

    IDs belong to this separate 48-bin namespace, not to the half-month IDs.
    No member_timebin_ids: a quarter cannot be reconstructed from half means.
    """
    result = []
    for month in range(1, 13):
        last_days = [calendar.monthrange(year, month)[1] for year in range(years[0], years[1] + 1)]
        for quarter, (start, end) in enumerate(((1, 7), (8, 15), (16, 22), (23, None))):
            ends = last_days if end is None else [end] * len(last_days)
            days = sum(stop - start + 1 for stop in ends)
            result.append({'timebin_id': (month - 1) * 4 + quarter, 'month': month,
                           'quarter': quarter + 1, 'parent_timebin_id': (month - 1) * 2 + quarter // 2,
                           'start_day': start, 'end_day_min': min(ends), 'end_day_max': max(ends),
                           'label': f'{month}月{start}–{end if end is not None else "末"}日',
                           'n_days_total': days, 'n_analyses_expected': days * hour_count})
    return result


def periods(grain, hour_count=4, years=(2016, 2025)):
    halves = utc_half_months(*years)
    if grain == "half":
        return [{**r, "n_analyses_expected": r["n_days_total"] * hour_count,
                 "member_timebin_ids": [r["timebin_id"]],
                 "label": f'{r["month"]}月{"前半" if r["bin"] == 1 else "後半"}'} for r in halves]
    if grain == "month":
        groups = [(m - 1, f"{m}月", [m]) for m in range(1, 13)]
    elif grain == "season":
        groups = [(0, "冬（12–2月）", [12, 1, 2]), (1, "春（3–5月）", [3, 4, 5]),
                  (2, "夏（6–8月）", [6, 7, 8]), (3, "秋（9–11月）", [9, 10, 11])]
    else:
        raise ValueError("Unknown period grain")
    return [{"timebin_id": i, "label": label, "months": months,
             "member_timebin_ids": [r["timebin_id"] for r in halves if r["month"] in months],
             "n_days_total": sum(r["n_days_total"] for r in halves if r["month"] in months),
             "n_analyses_expected": sum(r["n_days_total"] for r in halves if r["month"] in months) * hour_count}
            for i, label, months in groups]
