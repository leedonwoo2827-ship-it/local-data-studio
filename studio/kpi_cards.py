"""studio/kpi_cards.py — Green/Red KPI 카드 렌더."""
from __future__ import annotations

import streamlit as st

from core.metrics import KpiResult

GREEN = "#2ecc71"
RED = "#e74c3c"


def _fmt(value: float, unit: str) -> str:
    if abs(value) >= 1000:
        s = f"{value:,.0f}"
    elif value == int(value):
        s = f"{int(value)}"
    else:
        s = f"{value:,.2f}"
    return f"{s}{unit}" if unit and unit != "%" else (f"{s}%" if unit == "%" else s)


def render_kpi_cards(results: list[KpiResult], per_row: int = 4) -> None:
    for i in range(0, len(results), per_row):
        cols = st.columns(per_row)
        for col, r in zip(cols, results[i:i + per_row]):
            color = GREEN if r.signal == "Green" else RED
            pct = round(r.achievement * 100, 1)
            arrow = "▲" if r.direction == "higher_better" else "▼"
            with col:
                st.markdown(
                    f"""
<div style="border-left:6px solid {color};padding:10px 14px;border-radius:6px;
            background:#fafafa;margin-bottom:8px;">
  <div style="font-size:0.85rem;color:#666;">{r.name} {arrow}</div>
  <div style="font-size:1.5rem;font-weight:700;">{_fmt(r.actual, r.unit)}</div>
  <div style="font-size:0.8rem;color:{color};font-weight:600;">
    {r.signal} · 달성률 {pct}% (목표 {_fmt(r.target, r.unit)})
  </div>
</div>
""",
                    unsafe_allow_html=True,
                )
