"""
core/llm.py — DeepSeek(LiteLLM) 단일 진입점.

UbionClient 를 lazy 하게 생성해, 키가 없어도 앱 자체는 뜨도록 한다.
AI 기능을 실제로 호출하는 순간에만 클라이언트를 만든다.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

DEFAULT_MODEL = "deepseek-v4-flash"


class LLMNotConfigured(RuntimeError):
    """UBION_LITELLM_KEY 미설정 등으로 LLM 호출이 불가능할 때."""


def get_model() -> str:
    return os.environ.get("LDS_MODEL", DEFAULT_MODEL)


@lru_cache(maxsize=1)
def _client():
    if not os.environ.get("UBION_LITELLM_KEY"):
        raise LLMNotConfigured(
            "API 키가 설정되지 않았습니다. 앱 상단의 ⚙️ API 설정에서 "
            "주소(URL)와 키를 입력하고 저장하세요."
        )
    from .ubion_llm import UbionClient
    return UbionClient()


def reset_client() -> None:
    """설정(주소/키) 변경 후 캐시된 클라이언트를 무효화."""
    _client.cache_clear()


def is_configured() -> bool:
    return bool(os.environ.get("UBION_LITELLM_KEY"))


def load_prompt(name: str) -> str:
    """prompts/<name>.md 로드."""
    path = PROMPTS_DIR / f"{name}.md"
    return path.read_text(encoding="utf-8")


def complete(prompt: str, *, system: str | None = None,
             max_tokens: int = 1500, model: str | None = None, **kwargs) -> str:
    """
    텍스트 한 번 호출 후 .text 반환.
    system 메시지가 있으면 messages 형태로 구성.
    """
    client = _client()
    if system:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]
        return client.chat(model or get_model(), messages,
                           max_tokens=max_tokens, **kwargs).text
    return client.chat(model or get_model(), prompt,
                       max_tokens=max_tokens, **kwargs).text
