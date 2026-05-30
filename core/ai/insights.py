"""core/ai/insights.py — ① 자동 인사이트/요약 생성."""
from __future__ import annotations

import pandas as pd

from .. import llm
from ..config import TeamConfig
from ..metrics import KpiResult, results_to_frame, green_red_counts
from ._shared import df_to_markdown


def generate_insight(cfg: TeamConfig, results: list[KpiResult],
                     df: pd.DataFrame, context: str = "",
                     period: str = "") -> str:
    """KPI 결과 + 도메인 맥락을 DeepSeek 로 보내 인사이트 요약 생성."""
    green, red = green_red_counts(results)
    kpi_table = df_to_markdown(results_to_frame(results))
    template = llm.load_prompt("insight_summary")
    prompt = template.format(
        team=cfg.team,
        context=context or cfg.description or "(맥락 정보 없음)",
        period=period or "전체 기간",
        kpi_table=f"(Green {green} / Red {red})\n{kpi_table}",
    )
    return llm.complete(prompt, max_tokens=1500)
