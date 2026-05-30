"""core/ai/recommend.py — ③ 차트/대시보드 자동 구성 추천.

임의 데이터(컬럼/타입/샘플)를 보고 적합한 차트 + KPI config(YAML) 제안.
"""
from __future__ import annotations

import pandas as pd

from .. import llm
from ._shared import df_to_markdown


def recommend_config(df: pd.DataFrame) -> str:
    schema_df = pd.DataFrame({
        "컬럼": df.columns,
        "타입": [str(t) for t in df.dtypes],
        "예시값": [str(df[c].dropna().iloc[0]) if df[c].dropna().size else ""
                   for c in df.columns],
    })
    template = llm.load_prompt("chart_recommend")
    prompt = template.format(
        schema=df_to_markdown(schema_df, max_rows=60),
        sample_rows=df_to_markdown(df.head(8)),
    )
    return llm.complete(prompt, max_tokens=1800)
