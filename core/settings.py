"""
core/settings.py — 런타임 API 설정(주소/키/모델) 저장·로드·연결테스트.

비전문가 사용자가 .env 를 직접 편집하지 않고 **앱 화면에서** 값을 입력·저장하도록 한다.
- 저장 위치: 프로젝트 루트의 .lds_settings.json (gitignore, 평문 — 로컬 단일사용자 가정)
- 저장값은 os.environ 에 반영되어 기존 core/llm.py(환경변수 기반)가 그대로 동작.
- 우선순위: 저장된 설정 > .env > 미설정
"""
from __future__ import annotations

import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SETTINGS_PATH = PROJECT_ROOT / ".lds_settings.json"

DEFAULT_MODEL = "deepseek-v4-flash"
MODEL_CHOICES = [
    "deepseek-v4-flash",
    "deepseek-v4-flash-think",
    "deepseek-v4-pro",
    "claude-sonnet-4-6",
    "gpt-5.5",
    "gemini-3-flash-preview",
]


def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        try:
            return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def current() -> dict:
    """저장 설정 + 환경변수 폴백을 합친 현재 유효값."""
    s = load_settings()
    return {
        "url": s.get("url") or os.environ.get("UBION_LITELLM_URL", ""),
        "key": s.get("key") or os.environ.get("UBION_LITELLM_KEY", ""),
        "model": s.get("model") or os.environ.get("LDS_MODEL", DEFAULT_MODEL),
    }


def apply_to_env(data: dict | None = None) -> None:
    """설정값을 os.environ 에 반영 (llm.py 가 읽음)."""
    data = data or load_settings()
    if data.get("url"):
        os.environ["UBION_LITELLM_URL"] = data["url"]
    if data.get("key"):
        os.environ["UBION_LITELLM_KEY"] = data["key"]
    if data.get("model"):
        os.environ["LDS_MODEL"] = data["model"]


def save_settings(url: str, key: str, model: str) -> dict:
    data = {
        "url": (url or "").strip().rstrip("/"),
        "key": (key or "").strip(),
        "model": (model or DEFAULT_MODEL).strip(),
    }
    SETTINGS_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    apply_to_env(data)
    return data


def test_connection(url: str, key: str, timeout: float = 8.0) -> tuple[bool, str]:
    """프록시 /v1/models 호출로 주소+키 유효성 확인."""
    import requests

    if not url:
        return False, "API URL 을 입력하세요."
    if not key:
        return False, "API 키를 입력하세요."

    base = url.strip().rstrip("/")
    try:
        r = requests.get(
            f"{base}/v1/models",
            headers={"Authorization": f"Bearer {key.strip()}"},
            timeout=timeout,
        )
    except Exception as e:
        return False, f"연결 오류: {e}"

    if r.status_code == 200:
        try:
            n = len(r.json().get("data", []))
        except Exception:
            n = 0
        return True, f"연결 성공 · 모델 {n}개 확인"
    if r.status_code in (401, 403):
        return False, f"인증 실패 (HTTP {r.status_code}) — API 키를 확인하세요."
    return False, f"실패 (HTTP {r.status_code}): {r.text[:160]}"
