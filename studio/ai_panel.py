"""studio/ai_panel.py — AI 패널: 인사이트 / 챗봇 / 보고서 / 차트추천.

생성된 결과는 SQLite(ai_history)에 자동 저장되며, 사이드바 '내 분석 이력'과
마이페이지(render_history_view)에서 다시 열람·다운로드·삭제할 수 있다.
"""
from __future__ import annotations

import datetime as dt

import pandas as pd
import streamlit as st

from core import llm, export, store
from core.ai import insights, chat, recommend, report
from core.config import TeamConfig
from core.metrics import KpiResult, results_to_frame


# 다운로드 버튼 공통 사양 (포맷, 라벨, MIME)
_DL_SPECS = [
    ("md",   "⬇️ Markdown", "text/markdown"),
    ("xlsx", "⬇️ Excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    ("docx", "⬇️ Word", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
    ("pdf",  "⬇️ PDF", "application/pdf"),
    ("pptx", "⬇️ PPT", "application/vnd.openxmlformats-officedocument.presentationml.presentation"),
]


def _guard() -> bool:
    if not llm.is_configured():
        st.info("AI 기능을 쓰려면 `.env` 에 `UBION_LITELLM_KEY` 를 설정하세요. "
                "(자세히: docs/LLM_GUIDE.md)")
        return False
    return True


def _build_exports(text: str, *, title: str, subtitle: str = "",
                   kpi_df: pd.DataFrame | None = None,
                   df: pd.DataFrame | None = None, warn: bool = False) -> dict:
    """텍스트(+선택적 데이터)로 내보내기 포맷 사전 생성. 실패한 포맷은 None."""
    exports: dict = {"md": text.encode("utf-8")}
    builders = {
        "docx": lambda: export.to_docx(text),
        "pdf":  lambda: export.to_pdf(text),
        "pptx": lambda: export.to_pptx(text, title=title, subtitle=subtitle),
    }
    if kpi_df is not None:
        builders["xlsx"] = lambda: export.to_excel(text, kpi_df, df)
    for fmt, fn in builders.items():
        try:
            exports[fmt] = fn()
        except Exception as ex:  # 한 포맷 실패가 나머지를 막지 않도록
            exports[fmt] = None
            if warn:
                st.warning(f"{fmt} 생성 실패: {ex}")
    return exports


def _render_downloads(base: str, exports: dict, key_prefix: str, container=None) -> None:
    target = container or st
    cols = target.columns(len(_DL_SPECS))
    for col, (fmt, label, mime) in zip(cols, _DL_SPECS):
        data = exports.get(fmt)
        if data:
            col.download_button(label, data=data, file_name=f"{base}.{fmt}",
                                mime=mime, key=f"{key_prefix}_{fmt}")


# 이력 ref(고유 식별자)용 종류 영어명
_KIND_EN = {
    "인사이트": "insight",
    "중간보고서": "interim_report",
    "최종보고서": "final_report",
    "챗봇": "chat",
}


def _make_ref(cfg: TeamConfig, kind: str) -> str:
    """부서 간에도 겹치지 않는 고유 식별자: 일시분초_영어팀키_종류."""
    ts = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    return f"{ts}_{cfg.key}_{_KIND_EN.get(kind, 'ai')}"


def _save_history(cfg: TeamConfig, kind: str, content: str, *,
                  title: str = "", period: str = "") -> str:
    """AI 결과를 이력 DB에 자동 저장하고 ref 를 반환 (실패해도 화면은 유지)."""
    ref = _make_ref(cfg, kind)
    try:
        store.save_ai_output(cfg.key, cfg.team, kind, content, ref=ref,
                             title=title, period=period,
                             model=llm.get_model() if llm.is_configured() else "")
    except Exception as ex:
        st.caption(f"⚠️ 이력 저장 실패(결과는 정상): {ex}")
    return ref


def render_history_view() -> None:
    """마이페이지 — 사이드바에서 선택한 저장 분석을 본문 상단에 펼쳐 보여준다."""
    vid = st.session_state.get("view_history_id")
    if not vid:
        return
    rec = store.get_ai_output(int(vid))
    if not rec:
        st.session_state.pop("view_history_id", None)
        return

    box = st.container(border=True)
    box.markdown("### 📑 마이페이지 — 저장된 분석")
    meta = " · ".join(p for p in [
        rec.get("team"), rec.get("kind"), rec.get("period"),
        rec.get("created_at"), f"모델 {rec.get('model') or '-'}",
    ] if p)
    box.caption(meta)
    if (rec.get("title") or "").strip():
        box.markdown(f"**{rec['title']}**")
    box.markdown(rec.get("content") or "")

    base = f"{rec.get('team')}_{rec.get('kind')}_{str(rec.get('created_at'))[:10]}"
    exports = _build_exports(rec.get("content") or "",
                             title=f"{rec.get('team')} {rec.get('kind')}",
                             subtitle=rec.get("period") or "")
    _render_downloads(base, exports, key_prefix=f"hist_dl_{vid}", container=box)
    if box.button("✖ 닫기", key=f"hist_close_{vid}"):
        st.session_state.pop("view_history_id", None)
        st.rerun()
    st.markdown("---")


def render_ai_panel(cfg: TeamConfig, df: pd.DataFrame,
                    results: list[KpiResult], period_label: str) -> None:
    st.markdown("## 🤖 AI 분석 (DeepSeek v4 Flash)")

    # 화면에 보이는 AI 결과는 팀(폴더)별로 분리 보관 → 팀을 바꿔도 서로 섞이지 않음.
    # (예: 글로벌사업팀 화면에 교육사업팀 분석이 뜨지 않도록)
    tk = cfg.key

    def k(name: str) -> str:
        return f"{name}::{tk}"

    tab_insight, tab_chat, tab_report, tab_reco = st.tabs(
        ["🧠 자동 인사이트", "💬 데이터 챗봇", "📝 보고서 생성", "✨ 차트 추천"]
    )

    # --- 인사이트 ---
    with tab_insight:
        if st.button("인사이트 생성", key=f"btn_insight_{tk}") and _guard():
            with st.spinner("DeepSeek 가 분석 중..."):
                try:
                    text = insights.generate_insight(
                        cfg, results, df, context=cfg.description,
                        period=period_label)
                    st.session_state[k("insight_text")] = text
                    st.session_state[k("insight_exports")] = _build_exports(
                        text, title=f"{cfg.team} 인사이트", subtitle=period_label,
                        kpi_df=results_to_frame(results), df=df, warn=True)
                    st.session_state[k("insight_ref")] = _save_history(
                        cfg, "인사이트", text, period=period_label)
                except Exception as e:
                    st.error(f"생성 실패: {e}")
        if st.session_state.get(k("insight_text")):
            st.markdown(st.session_state[k("insight_text")])
            base = st.session_state.get(k("insight_ref")) or f"{tk}_insight"
            _render_downloads(base, st.session_state.get(k("insight_exports"), {}),
                              key_prefix=f"dl_insight_{tk}")
            st.caption(f"저장 ID: `{base}`")

    # --- 챗봇 ---
    with tab_chat:
        st.caption("데이터에 근거해 답합니다. 예: \"목표를 미달한 지표는?\"")
        q = st.text_input("질문", key=f"chat_q_{tk}",
                          placeholder="이 데이터에 대해 물어보세요")
        if st.button("질문하기", key=f"btn_chat_{tk}") and _guard() and q:
            with st.spinner("답변 생성 중..."):
                try:
                    ans = chat.answer_question(q, cfg, df, results)
                    st.session_state.setdefault(k("chat_log"), []).append((q, ans))
                    _save_history(cfg, "챗봇", ans, title=q, period=period_label)
                except Exception as e:
                    st.error(f"답변 실패: {e}")
        for ques, ans in reversed(st.session_state.get(k("chat_log"), [])):
            st.markdown(f"**Q. {ques}**")
            st.markdown(ans)
            st.markdown("---")

    # --- 보고서 ---
    with tab_report:
        st.caption("같은 데이터로 사람이 읽는 보고서를 생성합니다.")
        rtype = st.radio("보고서 유형", [report.INTERIM, report.FINAL],
                         horizontal=True, key=f"report_type_{tk}")
        if st.button("보고서 생성", key=f"btn_report_{tk}") and _guard():
            with st.spinner(f"{rtype} 작성 중..."):
                try:
                    text = report.generate_report(
                        cfg, results, df, report_type=rtype,
                        context=cfg.description, period=period_label)
                    st.session_state[k("report_text")] = text
                    st.session_state[k("report_meta")] = (cfg.team, rtype)
                    st.session_state[k("report_exports")] = _build_exports(
                        text, title=f"{cfg.team} {rtype}", subtitle=period_label,
                        kpi_df=results_to_frame(results), df=df, warn=True)
                    st.session_state[k("report_ref")] = _save_history(
                        cfg, rtype, text, period=period_label)
                except Exception as e:
                    st.error(f"생성 실패: {e}")
        if st.session_state.get(k("report_text")):
            st.markdown(st.session_state[k("report_text")])
            base = st.session_state.get(k("report_ref")) or f"{tk}_report"
            _render_downloads(base, st.session_state.get(k("report_exports"), {}),
                              key_prefix=f"dl_report_{tk}")
            st.caption(f"저장 ID: `{base}`")

    # --- 차트 추천 ---
    with tab_reco:
        st.caption("현재 로드된 데이터의 컬럼을 보고 차트/KPI config(YAML)를 제안합니다.")
        if st.button("차트 구성 추천", key=f"btn_reco_{tk}") and _guard():
            with st.spinner("추천 생성 중..."):
                try:
                    st.session_state[k("reco_text")] = recommend.recommend_config(df)
                except Exception as e:
                    st.error(f"추천 실패: {e}")
        if st.session_state.get(k("reco_text")):
            st.markdown(st.session_state[k("reco_text")])
