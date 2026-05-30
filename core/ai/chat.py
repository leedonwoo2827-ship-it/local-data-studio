"""core/ai/chat.py — ② 자연어 질의응답 (데이터 챗봇).

안전성: 코드 실행 없이, df 의 요약/샘플/ KPI 표를 컨텍스트로 주입해 답변.
(추후 tool-use / code-exec 고도화 가능 — docs/LLM_GUIDE.md 참고)
"""
from __future__ import annotations

import pandas as pd

from .. import llm
from ..config import TeamConfig
from ..metrics import KpiResult, results_to_frame
from ._shared import df_to_markdown


def answer_question(question: str, cfg: TeamConfig, df: pd.DataFrame,
                    results: list[KpiResult]) -> str:
    describe = df.describe(include="all").transpose()
    describe = describe.reset_index().rename(columns={"index": "컬럼"})
    template = llm.load_prompt("data_qa")
    prompt = template.format(
        team=cfg.team,
        period_column=cfg.period_column,
        columns=", ".join(map(str, df.columns)),
        describe=df_to_markdown(describe, max_rows=40),
        kpi_table=df_to_markdown(results_to_frame(results)),
        sample_rows=df_to_markdown(df.tail(12)),
        question=question,
    )
    return llm.complete(prompt, max_tokens=1200)
