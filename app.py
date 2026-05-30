"""
app.py — Local Data Studio (Streamlit 진입점)

흐름: 팀/예제 선택 → 데이터 로드 → 실시간 대시보드 → AI(인사이트/챗봇/보고서/차트추천)
실행: streamlit run app.py
"""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

# .env 를 import 단계에서 먼저 로드 (LLM 키 인식)
load_dotenv(Path(__file__).resolve().parent / ".env")

import streamlit as st

from core.metrics import compute_kpis
from studio.sidebar import render_sidebar
from studio.dashboard import render_dashboard
from studio.ai_panel import render_ai_panel

st.set_page_config(page_title="Local Data Studio", page_icon="📊", layout="wide")


def main() -> None:
    cfg, df, period_label = render_sidebar()

    if cfg is None:
        st.title("Local Data Studio")
        st.warning("config/teams 에 대시보드 설정(YAML)이 없습니다.")
        return
    if df is None:
        st.title(cfg.team)
        st.warning("데이터를 불러오지 못했습니다. 사이드바에서 파일을 업로드하거나 "
                   "샘플 데이터 경로를 확인하세요.")
        return

    results = compute_kpis(df, cfg)

    render_dashboard(cfg, df, results, period_label)
    st.markdown("---")
    render_ai_panel(cfg, df, results, period_label)


if __name__ == "__main__":
    main()
