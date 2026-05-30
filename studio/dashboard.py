"""studio/dashboard.py — 실시간 대시보드 메인 레이아웃."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from core import charts
from core.config import TeamConfig
from core.metrics import KpiResult, green_red_counts, results_to_frame
from .kpi_cards import render_kpi_cards

GREEN = "#2ecc71"
RED = "#e74c3c"


def _signal_style(val):
    if val == "Green":
        return f"background-color:{GREEN};color:white;font-weight:600;"
    if val == "Red":
        return f"background-color:{RED};color:white;font-weight:600;"
    return ""


def render_dashboard(cfg: TeamConfig, df: pd.DataFrame,
                     results: list[KpiResult], period_label: str) -> None:
    green, red = green_red_counts(results)

    st.markdown(f"## {cfg.team} · 성과지표 대시보드")
    st.caption(f"기간: {period_label} · 데이터 {len(df)}행")

    # 상단: 도넛 + 요약 메트릭
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("##### Green / Red 전체 비율")
        st.plotly_chart(charts.donut_green_red(green, red),
                        use_container_width=True)
    with c2:
        st.markdown("##### 달성도 요약")
        m1, m2, m3 = st.columns(3)
        m1.metric("전체 지표", f"{len(results)}개")
        m2.metric("🟢 Green (달성)", f"{green}개")
        m3.metric("🔴 Red (미달)", f"{red}개")
        st.markdown("###### KPI 카드")
        render_kpi_cards(results, per_row=3)

    # 달성도 현황판 테이블
    st.markdown("##### 📋 달성도 현황판")
    table = results_to_frame(results)
    styled = table.style.map(_signal_style, subset=["신호"])
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # 차트
    if cfg.charts:
        st.markdown("##### 📈 추이 차트")
        cols = st.columns(2)
        for idx, chart in enumerate(cfg.charts):
            if chart.x in df.columns and chart.y in df.columns:
                with cols[idx % 2]:
                    st.plotly_chart(charts.build_chart(df, chart),
                                    use_container_width=True)
