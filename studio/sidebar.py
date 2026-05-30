"""studio/sidebar.py — 팀 선택 · 데이터 소스(샘플/누적DB/일회성) · 적재 · 기간 필터."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from core import llm, store
from core.config import TeamConfig, load_team_config, list_team_configs
from core.data_loader import load_data, load_team_data


def _ingest_section(cfg: TeamConfig) -> None:
    """엑셀/CSV 를 SQLite 에 누적 적재하는 패널."""
    with st.sidebar.expander("📥 데이터 적재 (DB에 쌓기)", expanded=False):
        up = st.file_uploader("엑셀/CSV 업로드", type=["csv", "xlsx", "xls"],
                              key=f"ingest_{cfg.key}")
        mode_label = st.radio(
            "적재 방식",
            ["같은 기간 교체(upsert)", "무조건 추가(append)", "전체 교체(replace)"],
            key=f"mode_{cfg.key}",
        )
        mode = {"같은 기간 교체(upsert)": "upsert",
                "무조건 추가(append)": "append",
                "전체 교체(replace)": "replace"}[mode_label]

        if st.button("DB에 적재", key=f"do_ingest_{cfg.key}") and up is not None:
            df_new = load_data(up, filename=up.name)
            n = store.ingest_dataframe(
                cfg.key, df_new, period_column=cfg.period_column,
                mode=mode, source_file=up.name)
            st.success(f"{n}행 적재 완료 → 누적 {store.row_count(cfg.key)}행")
            st.rerun()

        cur = store.row_count(cfg.key)
        st.caption(f"현재 DB 누적: **{cur}행** (테이블 data_{cfg.key})")
        if cur and st.button("⚠️ 이 팀 DB 비우기", key=f"clear_{cfg.key}"):
            store.clear_team(cfg.key)
            st.rerun()


def render_sidebar() -> tuple[TeamConfig | None, pd.DataFrame | None, str]:
    """반환: (cfg, df, period_label)."""
    st.sidebar.title("📊 Local Data Studio")

    if llm.is_configured():
        st.sidebar.success(f"AI 연결됨 · 모델: {llm.get_model()}")
    else:
        st.sidebar.warning("AI 키 미설정 — 대시보드는 정상, AI 기능만 비활성")

    teams = list_team_configs()
    if not teams:
        st.sidebar.error("config/teams 에 YAML 이 없습니다.")
        return None, None, ""

    team_name = st.sidebar.selectbox("팀 / 예제 선택", list(teams.keys()))
    cfg = load_team_config(teams[team_name])

    st.sidebar.markdown("---")
    has_db = store.row_count(cfg.key) > 0
    source_options = ["샘플 파일", "누적 DB (SQLite)", "일회성 업로드"]
    default_idx = 1 if has_db else 0
    source = st.sidebar.radio("데이터 소스", source_options, index=default_idx)

    df: pd.DataFrame | None = None
    if source == "샘플 파일":
        try:
            df = load_team_data(cfg.resolved_data_path)
            st.sidebar.caption(f"샘플: {cfg.data_file}")
        except FileNotFoundError as e:
            st.sidebar.error(str(e))
    elif source == "누적 DB (SQLite)":
        df = store.read_team_data(cfg.key)
        if df is None or df.empty:
            st.sidebar.warning("누적 DB가 비어 있습니다. 아래 '데이터 적재'로 채우세요.")
            df = None
        else:
            st.sidebar.caption(f"DB 누적 {len(df)}행")
    else:  # 일회성 업로드
        up = st.sidebar.file_uploader("CSV/Excel 업로드(저장 안 함)",
                                      type=["csv", "xlsx", "xls"], key="oneoff")
        if up is not None:
            df = load_data(up, filename=up.name)
            st.sidebar.caption(f"미리보기: {up.name} (DB 저장 안 됨)")

    # 적재 패널 (항상 노출)
    _ingest_section(cfg)

    if df is None:
        return cfg, None, ""

    # 기간 필터
    period_label = "전체 기간"
    if cfg.period_column in df.columns:
        periods = list(df[cfg.period_column].astype(str).unique())
        sel = st.sidebar.multiselect(
            f"기간 필터 ({cfg.period_column})", periods, default=periods)
        if sel:
            df = df[df[cfg.period_column].astype(str).isin(sel)]
            period_label = f"{sel[0]} ~ {sel[-1]}"

    return cfg, df, period_label
