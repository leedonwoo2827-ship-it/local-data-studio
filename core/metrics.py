"""
core/metrics.py — KPI 달성도 / Green·Red 신호 계산.

참조 사진의 "달성도 현황판" + "Green/Red 도넛" 을 재현하는 핵심 로직.
방향(higher_better/lower_better) 무관하게 achievement_ratio 로 통일:
    higher_better : actual / target
    lower_better  : target / actual
=> 두 경우 모두 ratio >= green_threshold 이면 Green.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

import pandas as pd

from .config import KpiDef, TeamConfig


@dataclass
class KpiResult:
    name: str
    unit: str
    actual: float
    target: float
    achievement: float   # 0~1+ (1.0 = 목표 100% 달성)
    signal: str          # "Green" | "Red"
    direction: str

    def as_dict(self) -> dict:
        return asdict(self)


def _aggregate(series: pd.Series, agg: str) -> float:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return 0.0
    if agg == "sum":
        return float(s.sum())
    if agg == "mean":
        return float(s.mean())
    if agg == "last":
        return float(s.iloc[-1])
    if agg == "max":
        return float(s.max())
    if agg == "min":
        return float(s.min())
    return float(s.sum())


def compute_kpi(df: pd.DataFrame, kpi: KpiDef) -> KpiResult:
    if kpi.column not in df.columns:
        actual = 0.0
    else:
        actual = _aggregate(df[kpi.column], kpi.agg)

    target = float(kpi.target)
    if kpi.direction == "higher_better":
        achievement = (actual / target) if target else 0.0
    else:  # lower_better
        achievement = (target / actual) if actual else 0.0

    signal = "Green" if achievement >= kpi.green_threshold else "Red"
    return KpiResult(
        name=kpi.name,
        unit=kpi.unit,
        actual=round(actual, 4),
        target=target,
        achievement=round(achievement, 4),
        signal=signal,
        direction=kpi.direction,
    )


def compute_kpis(df: pd.DataFrame, cfg: TeamConfig) -> list[KpiResult]:
    return [compute_kpi(df, k) for k in cfg.kpis]


def green_red_counts(results: list[KpiResult]) -> tuple[int, int]:
    green = sum(1 for r in results if r.signal == "Green")
    return green, len(results) - green


def results_to_frame(results: list[KpiResult]) -> pd.DataFrame:
    """달성도 현황판 테이블용 DataFrame."""
    rows = []
    for r in results:
        rows.append({
            "성과지표": r.name,
            "실적": r.actual,
            "목표": r.target,
            "달성률(%)": round(r.achievement * 100, 1),
            "단위": r.unit,
            "신호": r.signal,
        })
    return pd.DataFrame(rows)
