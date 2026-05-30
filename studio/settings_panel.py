"""studio/settings_panel.py — 화면 내 API 설정 패널.

비전문가 사용자가 회사에서 받은 주소(URL)와 키를 화면에서 입력 → 연결 테스트 → 저장.
.env 편집이나 명령어 입력이 전혀 필요 없다.
"""
from __future__ import annotations

import streamlit as st

from core import settings, llm


def _status() -> tuple[str, str]:
    """(이모지, 문구) 현재 연결 상태."""
    cur = settings.current()
    tested = st.session_state.get("conn_tested")
    if not cur["key"] or not cur["url"]:
        return "🔴", "미설정 — 주소와 키를 입력하세요"
    if tested is True:
        return "🟢", "연결됨"
    if tested is False:
        return "🔴", "연결 실패 — 주소/키 확인"
    return "🟡", "저장됨 · 연결 미확인"


def render_settings_panel() -> None:
    cur = settings.current()
    # 세션 초기값 시드
    st.session_state.setdefault("set_url", cur["url"])
    st.session_state.setdefault("set_key", cur["key"])
    st.session_state.setdefault("set_model", cur["model"])

    emoji, status_text = _status()
    label = f"⚙️ API 설정 — {emoji} {status_text} · 모델 {cur['model']}"

    # 미설정이면 펼친 상태로 시작해 사용자를 유도
    expanded = not (cur["key"] and cur["url"]) or st.session_state.get("conn_tested") is False
    with st.expander(label, expanded=expanded):
        st.caption("회사에서 받은 **API 주소(URL)** 와 **키** 를 넣고 [연결 테스트] → [저장] 하세요. "
                   "주소가 바뀌면 여기서 다시 고치면 됩니다.")

        c1, c2 = st.columns(2)
        with c1:
            url = st.text_input("API URL", key="set_url",
                               placeholder="http://회사가-준-주소:4000")
        with c2:
            key = st.text_input("API 키", key="set_key", type="password",
                               placeholder="sk-...")

        with st.expander("고급 설정", expanded=False):
            model = st.selectbox(
                "모델", settings.MODEL_CHOICES,
                index=(settings.MODEL_CHOICES.index(cur["model"])
                       if cur["model"] in settings.MODEL_CHOICES else 0),
                key="set_model",
            )

        b1, b2, _ = st.columns([1, 1, 4])
        with b1:
            if st.button("🔌 연결 테스트", use_container_width=True):
                ok, msg = settings.test_connection(url, key)
                st.session_state["conn_tested"] = ok
                (st.success if ok else st.error)(msg)
        with b2:
            if st.button("💾 저장", type="primary", use_container_width=True):
                settings.save_settings(url, key, st.session_state["set_model"])
                llm.reset_client()
                st.session_state["conn_tested"] = None
                st.success("저장했습니다.")
                st.rerun()
