"""
core/data_loader.py — CSV/Excel 로드 + 기본 검증.
"""
from __future__ import annotations

from pathlib import Path
from typing import IO

import pandas as pd


def load_data(source: str | Path | IO, *, filename: str | None = None) -> pd.DataFrame:
    """
    경로 또는 업로드 버퍼에서 DataFrame 로드.
    filename: 업로드 버퍼일 때 확장자 판별용.
    """
    name = filename or (str(source) if isinstance(source, (str, Path)) else "")
    suffix = Path(name).suffix.lower()

    if suffix in (".xlsx", ".xls"):
        df = pd.read_excel(source)
    else:
        # CSV — 한글 인코딩 대비 (utf-8 → cp949 fallback)
        try:
            df = pd.read_csv(source)
        except UnicodeDecodeError:
            if hasattr(source, "seek"):
                source.seek(0)
            df = pd.read_csv(source, encoding="cp949")

    df.columns = [str(c).strip() for c in df.columns]
    return df


def load_team_data(data_path: str | Path) -> pd.DataFrame:
    data_path = Path(data_path)
    if not data_path.exists():
        raise FileNotFoundError(f"데이터 파일을 찾을 수 없습니다: {data_path}")
    return load_data(data_path)


def validate_columns(df: pd.DataFrame, required: list[str]) -> list[str]:
    """누락된 컬럼 목록 반환 (빈 리스트면 OK)."""
    cols = set(df.columns)
    return [c for c in required if c not in cols]
