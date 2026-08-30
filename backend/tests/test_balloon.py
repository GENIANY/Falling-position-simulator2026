"""calc.js黄金値パリティ + ラウンドトリップ性質テスト.

黄金値はlegacy js/calc/calc.jsのburst-altitudeパスをNodeで忠実実行して採取
(フロントエンド frontend/src/physics/balloon.test.ts と同一フィクスチャ)。
"""

import math

import pytest

from bfps.core.balloon import (
    BalloonPhysicsError,
    from_model,
    launch_radius_for_ascent_rate,
    launch_radius_for_burst_altitude,
    performance,
)

GOLDEN = [
    # (model, payload_g, gas, tba, expect)
    (
        "k1200", 1000, "he", 30000,
        dict(
            ascent_rate=7.600437042636673,
            burst_altitude=30000.0,
            time_to_burst=65.7856906379353,
            neck_lift=4274.724053407592,
            launch_volume=5.33390885951636,
        ),
    ),
    (
        "h500", 250, "h2", 25000,
        dict(
            ascent_rate=7.187463439286281,
            burst_altitude=25000.0,
            time_to_burst=57.97130937587655,
            neck_lift=1807.993610160845,
            launch_volume=2.0697637971131244,
        ),
    ),
    (
        "k1500", 2000, "he", 33000,
        dict(
            ascent_rate=4.89760340988275,
            burst_altitude=33000.0,
            time_to_burst=112.2998238056942,
            neck_lift=3234.2074864071365,
            launch_volume=4.612439094317163,
        ),
    ),
]


@pytest.mark.parametrize("model,payload_g,gas,tba,expect", GOLDEN)
def test_golden_parity(model, payload_g, gas, tba, expect):
    cfg = from_model(model, payload_g / 1000.0, gas)
    r = launch_radius_for_burst_altitude(cfg, tba)
    perf = performance(cfg, r)
    assert perf.ascent_rate_ms == pytest.approx(expect["ascent_rate"], abs=1e-6)
    assert perf.burst_altitude_m == pytest.approx(expect["burst_altitude"], abs=1e-3)
    assert perf.time_to_burst_min == pytest.approx(expect["time_to_burst"], abs=1e-4)
    assert perf.neck_lift_g == pytest.approx(expect["neck_lift"], abs=1e-3)
    assert perf.launch_volume_m3 == pytest.approx(expect["launch_volume"], abs=1e-6)


@pytest.mark.parametrize("tar", [2.0, 3.5, 5.0, 7.0])
def test_ascent_rate_round_trip(tar):
    """target ascent -> radius -> performance -> 同じascent rate.

    legacyの壊れたCardano実装ではこのテストは通らない。
    """
    cfg = from_model("k1200", 1.0, "he")
    r = launch_radius_for_ascent_rate(cfg, tar)
    perf = performance(cfg, r)
    assert perf.ascent_rate_ms == pytest.approx(tar, abs=1e-6)


def test_monotonicity_more_gas_faster_lower_burst():
    cfg = from_model("k1200", 1.0, "he")
    slow = performance(cfg, launch_radius_for_ascent_rate(cfg, 3.0))
    fast = performance(cfg, launch_radius_for_ascent_rate(cfg, 7.0))
    assert fast.launch_volume_m3 > slow.launch_volume_m3
    assert fast.burst_altitude_m < slow.burst_altitude_m


def test_unknown_model():
    with pytest.raises(BalloonPhysicsError):
        from_model("nope", 1.0)


def test_insufficient_buoyancy():
    cfg = from_model("k50", 50.0, "he")  # 50kgペイロードは無理
    r = launch_radius_for_burst_altitude(cfg, 30000)
    with pytest.raises(BalloonPhysicsError):
        performance(cfg, r)
