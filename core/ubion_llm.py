"""
ubion_llm.py — Ubion LiteLLM 사내 thin wrapper (Python)

원본: _context/Ubion_liteLLM_Migration_Kit/ubion_llm.py 를 복사.
유일한 변경점: 맨 아래 모듈 로드시 자동 client 생성을 try/except 로 감싸서,
키(UBION_LITELLM_KEY)가 없어도 import 자체는 실패하지 않게 함 (대시보드는 키 없이도 조회 가능).

환경 변수:
    UBION_LITELLM_URL="http://192.168.50.119:4000"
    UBION_LITELLM_KEY="sk-...본인-virtual-key..."
"""
from __future__ import annotations

import base64
import os
import time
from pathlib import Path
from typing import Any

import requests
from openai import OpenAI


# ---------------------------------------------------------------------------
# 모델 상수 (자주 쓰는 것만)
# ---------------------------------------------------------------------------
class MODELS:
    # 텍스트 — Anthropic
    OPUS    = "claude-opus-4-7"
    SONNET  = "claude-sonnet-4-6"
    HAIKU   = "claude-haiku-4-5"
    # 텍스트 — OpenAI
    GPT_FLAGSHIP     = "gpt-5.5"
    GPT_FLAGSHIP_PRO = "gpt-5.5-pro"
    GPT_INSTANT      = "chat-latest"
    GPT_MINI         = "gpt-5.4-mini"
    GPT_NANO         = "gpt-5.4-nano"
    # 텍스트 — Gemini
    GEMINI_PRO        = "gemini-3.1-pro-preview"
    GEMINI_FLASH      = "gemini-3-flash-preview"
    GEMINI_FLASH_LITE = "gemini-3.1-flash-lite"
    # 텍스트 — DeepSeek
    DEEPSEEK_FLASH       = "deepseek-v4-flash"
    DEEPSEEK_FLASH_THINK = "deepseek-v4-flash-think"
    DEEPSEEK_PRO         = "deepseek-v4-pro"
    # 이미지
    NANO_BANANA     = "gemini-3.1-flash-image-preview"
    NANO_BANANA_PRO = "gemini-3-pro-image-preview"
    GPT_IMAGE_2     = "gpt-image-2"
    # TTS
    GPT_TTS               = "gpt-4o-mini-tts"
    GPT_TTS_BASIC         = "tts-1"
    GPT_TTS_HD            = "tts-1-hd"
    GEMINI_TTS            = "gemini-2.5-flash-preview-tts"
    GEMINI_TTS_PRO        = "gemini-2.5-pro-preview-tts"
    GEMINI_TTS_LATEST     = "gemini-3.1-flash-tts-preview"
    ELEVEN_V3             = "eleven_v3"
    ELEVEN_MULTILINGUAL   = "eleven_multilingual_v2"
    ELEVEN_TURBO          = "eleven_turbo_v2_5"
    ELEVEN_FLASH          = "eleven_flash_v2_5"
    # STT
    WHISPER                = "whisper-1"
    GPT_TRANSCRIBE         = "gpt-4o-transcribe"
    GPT_TRANSCRIBE_MINI    = "gpt-4o-mini-transcribe"
    GPT_TRANSCRIBE_DIARIZE = "gpt-4o-transcribe-diarize"
    ELEVEN_SCRIBE          = "scribe_v1"
    # 비디오
    SORA_2     = "sora-2"
    SORA_2_PRO = "sora-2-pro"
    VEO        = "veo-3.1-generate-preview"
    VEO_FAST   = "veo-3.1-fast-generate-preview"
    VEO_LITE   = "veo-3.1-lite-generate-preview"


# ElevenLabs voice_id + Gemini voice 이름
class VOICES:
    RACHEL = "21m00Tcm4TlvDq8ikWAM"
    ADAM   = "pNInz6obpgDQGcFmaJgB"
    BELLA  = "EXAVITQu4vr4xnSDxMaL"
    ANTONI = "ErXwobaYiN019PkySvjV"
    ALLOY   = "alloy"
    ECHO    = "echo"
    NOVA    = "nova"
    SHIMMER = "shimmer"
    KORE     = "Kore"
    PUCK     = "Puck"
    CHARON   = "Charon"
    SULAFAT  = "Sulafat"


# 신 OpenAI 모델 (max_tokens 안 받음, max_completion_tokens 필수)
_NEW_OPENAI = {
    "gpt-5.5", "gpt-5.5-pro", "chat-latest", "gpt-5.4-nano", "gpt-5.4-mini",
}

# Gemini TTS 모델 (chat/completions + modalities=["audio"] 로 라우팅)
_GEMINI_TTS = {
    "gemini-2.5-flash-preview-tts",
    "gemini-2.5-pro-preview-tts",
    "gemini-3.1-flash-tts-preview",
}


class _Response:
    """텍스트 응답을 .text 로 일관 노출."""
    def __init__(self, raw: Any, text: str, usage: Any = None):
        self.raw = raw
        self.text = text
        self.usage = usage


class UbionClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.base_url = base_url or os.environ.get(
            "UBION_LITELLM_URL", "http://localhost:4000"
        )
        self.api_key = api_key or os.environ["UBION_LITELLM_KEY"]
        self._oai = OpenAI(api_key=self.api_key, base_url=f"{self.base_url}/v1")

    # ---- 텍스트 ---------------------------------------------------------
    def chat(self, model: str, prompt: str | list, max_tokens: int = 1000,
             **kwargs) -> _Response:
        msgs = (
            [{"role": "user", "content": prompt}] if isinstance(prompt, str)
            else prompt
        )
        params = dict(model=model, messages=msgs, **kwargs)
        if model in _NEW_OPENAI:
            params["max_completion_tokens"] = max_tokens
        else:
            params["max_tokens"] = max_tokens

        resp = self._oai.chat.completions.create(**params)
        msg = resp.choices[0].message
        text = msg.content or ""
        return _Response(resp, text, resp.usage)

    # ---- 이미지 ---------------------------------------------------------
    def image(self, model: str, prompt: str, **kwargs) -> bytes:
        if model.startswith("gpt-image-"):
            resp = self._oai.images.generate(
                model=model, prompt=prompt,
                size=kwargs.get("size", "1024x1024"),
                quality=kwargs.get("quality", "low"),
                n=1,
            )
            return base64.b64decode(resp.data[0].b64_json)
        resp = self._oai.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            modalities=["image", "text"],
        )
        url = resp.choices[0].message.images[0].image_url.url
        b64 = url.split(",", 1)[1] if "," in url else url
        return base64.b64decode(b64)

    # ---- TTS ------------------------------------------------------------
    def tts(self, model: str, text: str, voice: str, **kwargs) -> bytes:
        if model in _GEMINI_TTS:
            fmt = kwargs.get("format", "pcm16")
            resp = self._oai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": text}],
                modalities=["audio"],
                extra_body={"audio": {"voice": voice, "format": fmt}},
            )
            return base64.b64decode(resp.choices[0].message.audio.data)
        resp = self._oai.audio.speech.create(
            model=model, voice=voice, input=text,
        )
        return resp.content

    # ---- STT ------------------------------------------------------------
    def stt(self, audio_path: str | Path, model: str = MODELS.GPT_TRANSCRIBE) -> str:
        with open(audio_path, "rb") as f:
            resp = self._oai.audio.transcriptions.create(model=model, file=f)
        return resp.text

    # ---- 비디오 (async → sync 헬퍼) -----------------------------------
    def video(self, model: str, prompt: str, seconds: int = 4,
              poll_interval: float = 10.0, max_wait: float = 600.0) -> bytes:
        headers = {"Authorization": f"Bearer {self.api_key}",
                   "Content-Type": "application/json"}
        sub = requests.post(
            f"{self.base_url}/v1/videos", headers=headers,
            json={"model": model, "prompt": prompt, "seconds": seconds},
            timeout=30,
        )
        sub.raise_for_status()
        job = sub.json()
        job_id = job.get("id") or job.get("video_id")

        start = time.monotonic()
        while time.monotonic() - start < max_wait:
            time.sleep(poll_interval)
            st = requests.get(
                f"{self.base_url}/v1/videos/{job_id}", headers=headers, timeout=30,
            ).json()
            status = st.get("status")
            if status in ("completed", "succeeded", "ready"):
                break
            if status in ("failed", "error", "canceled"):
                raise RuntimeError(f"video generation failed: {st}")
        else:
            raise TimeoutError(f"video generation exceeded {max_wait}s")

        dl = requests.get(
            f"{self.base_url}/v1/videos/{job_id}/content",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=120,
        )
        dl.raise_for_status()
        return dl.content

    @property
    def openai(self) -> OpenAI:
        return self._oai


# 모듈 로드 시 기본 client 자동 생성 (키 없으면 None — import 실패 방지)
try:
    client = UbionClient()
except Exception:
    client = None
