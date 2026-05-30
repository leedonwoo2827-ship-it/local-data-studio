"""studio/ai_panel.py — AI 패널: 인사이트 / 챗봇 / 보고서 / 차트추천."""
from __future__ import annotations

import datetime as dt

import pandas as pd
import streamlit as st

from core import llm, export
from core.ai import insights, chat, recommend, report
from core.config import TeamConfig
from core.metrics import KpiResult, results_to_frame


def _guard() -> bool:
    if not llm.is_configured():
        st.info("AI 기능을 쓰려면 `.env` 에 `UBION_LITELLM_KEY` 를 설정하세요. "
                "(자세히: docs/LLM_GUIDE.md)")
        return False
    return True


def render_ai_panel(cfg: TeamConfig, df: pd.DataFrame,
                    results: list[KpiResult], period_label: str) -> None:
    st.markdown("## 🤖 AI 분석 (DeepSeek v4 Flash)")
    tab_insight, tab_chat, tab_report, tab_reco = st.tabs(
        ["🧠 자동 인사이트", "💬 데이터 챗봇", "📝 보고서 생성", "✨ 차트 추천"]
    )

    # --- 인사이트 ---
    with tab_insight:
        if st.button("인사이트 생성", key="btn_insight") and _guard():
            with st.spinner("DeepSeek 가 분석 중..."):
                try:
                    text = insights.generate_insight(
                        cfg, results, df, context=cfg.description,
                        period=period_label)
                    st.session_state["insight_text"] = text
                except Exception as e:
                    st.error(f"생성 실패: {e}")
        if st.session_state.get("insight_text"):
            st.markdown(st.session_state["insight_text"])

    # --- 챗봇 ---
    with tab_chat:
        st.caption("데이터에 근거해 답합니다. 예: \"목표를 미달한 지표는?\"")
        q = st.text_input("질문", key="chat_q",
                          placeholder="이 데이터에 대해 물어보세요")
        if st.button("질문하기", key="btn_chat") and _guard() and q:
            with st.spinner("답변 생성 중..."):
                try:
                    ans = chat.answer_question(q, cfg, df, results)
                    st.session_state.setdefault("chat_log", []).append((q, ans))
                except Exception as e:
                    st.error(f"답변 실패: {e}")
        for ques, ans in reversed(st.session_state.get("chat_log", [])):
            st.markdown(f"**Q. {ques}**")
            st.markdown(ans)
            st.markdown("---")

    # --- 보고서 ---
    with tab_report:
        st.caption("같은 데이터로 사람이 읽는 보고서를 생성합니다.")
        rtype = st.radio("보고서 유형", [report.INTERIM, report.FINAL],
                         horizontal=True, key="report_type")
        if st.button("보고서 생성", key="btn_report") and _guard():
            with st.spinner(f"{rtype} 작성 중..."):
                try:
                    text = report.generate_report(
                        cfg, results, df, report_type=rtype,
                        context=cfg.description, period=period_label)
                    st.session_state["report_text"] = text
                    st.session_state["report_meta"] = (cfg.team, rtype)
                    # 내보내기 포맷 사전 생성 (md/xlsx/docx/pdf/pptx)
                    kpi_df = results_to_frame(results)
                    exports = {"md": text.encode("utf-8")}
                    builders = {
                        "xlsx": lambda: export.to_excel(text, kpi_df, df),
                        "docx": lambda: export.to_docx(text),
                        "pdf":  lambda: export.to_pdf(text),
                        "pptx": lambda: export.to_pptx(
                            text, title=f"{cfg.team} {rtype}", subtitle=period_label),
                    }
                    for fmt, fn in builders.items():
                        try:
                            exports[fmt] = fn()
                        except Exception as ex:
                            exports[fmt] = None
                            st.warning(f"{fmt} 생성 실패: {ex}")
                    st.session_state["report_exports"] = exports
                except Exception as e:
                    st.error(f"생성 실패: {e}")
        if st.session_state.get("report_text"):
            st.markdown(st.session_state["report_text"])
            team, rtype_done = st.session_state.get("report_meta", (cfg.team, "보고서"))
            today = dt.date.today().isoformat()
            base = f"{team}_{rtype_done}_{today}"
            exports = st.session_state.get("report_exports", {})
            specs = [
                ("md",   "⬇️ Markdown", "text/markdown"),
                ("xlsx", "⬇️ Excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                ("docx", "⬇️ Word", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                ("pdf",  "⬇️ PDF", "application/pdf"),
                ("pptx", "⬇️ PPT", "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
            ]
            cols = st.columns(len(specs))
            for col, (fmt, label, mime) in zip(cols, specs):
                data = exports.get(fmt)
                if data:
                    col.download_button(label, data=data, file_name=f"{base}.{fmt}",
                                        mime=mime, key=f"dl_{fmt}")

    # --- 차트 추천 ---
    with tab_reco:
        st.caption("현재 로드된 데이터의 컬럼을 보고 차트/KPI config(YAML)를 제안합니다.")
        if st.button("차트 구성 추천", key="btn_reco") and _guard():
            with st.spinner("추천 생성 중..."):
                try:
                    st.session_state["reco_text"] = recommend.recommend_config(df)
                except Exception as e:
                    st.error(f"추천 실패: {e}")
        if st.session_state.get("reco_text"):
            st.markdown(st.session_state["reco_text"])
