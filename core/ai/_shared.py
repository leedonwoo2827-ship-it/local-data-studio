"""core/ai/_shared.py — AI 프롬프트용 공통 포맷 헬퍼."""
from __future__ import annotations

import pandas as pd


def df_to_markdown(df: pd.DataFrame, max_rows: int = 50) -> str:
    """tabulate 없이 간단 마크다운 표 생성."""
    if df.empty:
        return "(데이터 없음)"
    df = df.head(max_rows)
    cols = list(df.columns)
    header = "| " + " | ".join(str(c) for c in cols) + " |"
    sep = "| " + " | ".join("---" for _ in cols) + " |"
    rows = []
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(row[c]) for c in cols) + " |")
    return "\n".join([header, sep, *rows])


def trend_summary(df: pd.DataFrame, period_col: str, value_cols: list[str],
                  max_points: int = 12) -> str:
    """기간별 추이를 사람이 읽을 수 있는 짧은 텍스트로."""
    if period_col not in df.columns:
        return "(기간 컬럼 없음)"
    keep = [period_col] + [c for c in value_cols if c in df.columns]
    sub = df[keep].tail(max_points)
    return df_to_markdown(sub, max_rows=max_points)
