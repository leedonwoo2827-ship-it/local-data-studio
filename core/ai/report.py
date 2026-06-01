"""core/ai/report.py — 중간/최종 보고서 생성.

실시간 대시보드와 함께, 같은 데이터로 사람이 읽는 보고서를 생성한다.
report_type: "중간보고서" | "최종보고서"
"""
from __future__ import annotations

import pandas as pd

from .. import llm
from ..config import TeamConfig
from ..metrics import KpiResult, results_to_frame, green_red_counts
from ._shared import df_to_markdown, trend_summary

INTERIM = "중간보고서"
FINAL = "최종보고서"


def generate_report(cfg: TeamConfig, results: list[KpiResult],
                    df: pd.DataFrame, report_type: str = INTERIM,
                    context: str = "", period: str = "") -> str:
    green, red = green_red_counts(results)
    kpi_table = df_to_markdown(results_to_frame(results))
    value_cols = [k.column for k in cfg.kpis]
    trend = trend_summary(df, cfg.period_column, value_cols)

    template = llm.load_prompt("report")
    prompt = template.format(
        report_type=report_type,
        team=cfg.team,
        context=context or cfg.description or "(맥락 정보 없음)",
        period=period or "전체 기간",
        kpi_table=f"(Green {green} / Red {red})\n{kpi_table}",
        trend_summary=trend,
    )
    return llm.complete(prompt, max_tokens=6000)
