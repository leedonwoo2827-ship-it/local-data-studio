"""
core/store.py — SQLite 누적 데이터 저장소.

"엑셀을 계속 추가하며 데이터를 쌓는" 시나리오를 위한 로컬 단일파일 DB.
- 팀별로 테이블 1개 (data_<team_key>).
- 업로드 파일을 append 하거나, 기간(period) 기준으로 upsert(중복 기간 교체).
- 서버/설치 불필요. db/lds.sqlite 파일 하나로 백업·이동 용이.

자세한 설계 근거: docs/DATA_STORE.md
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_DIR = PROJECT_ROOT / "db"
DB_PATH = DB_DIR / "lds.sqlite"

# 적재 시 출처/시각 메타 컬럼
SOURCE_COL = "_source_file"
INGESTED_COL = "_ingested_at"


def _table(team_key: str) -> str:
    safe = re.sub(r"[^0-9a-zA-Z_]", "_", team_key)
    return f"data_{safe}"


def _connect() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def table_exists(team_key: str) -> bool:
    with _connect() as con:
        cur = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (_table(team_key),),
        )
        return cur.fetchone() is not None


def row_count(team_key: str) -> int:
    if not table_exists(team_key):
        return 0
    with _connect() as con:
        return int(con.execute(f'SELECT COUNT(*) FROM "{_table(team_key)}"').fetchone()[0])


def read_team_data(team_key: str, drop_meta: bool = True) -> pd.DataFrame | None:
    if not table_exists(team_key):
        return None
    with _connect() as con:
        df = pd.read_sql(f'SELECT * FROM "{_table(team_key)}"', con)
    if drop_meta:
        df = df.drop(columns=[c for c in (SOURCE_COL, INGESTED_COL) if c in df.columns])
    return df


def ingest_dataframe(team_key: str, df: pd.DataFrame, *,
                     period_column: str | None = None,
                     mode: str = "upsert",
                     source_file: str = "") -> int:
    """
    df 를 팀 테이블에 적재.
      mode="append": 무조건 행 추가
      mode="upsert": period_column 값이 같은 기존 행을 지우고 새로 넣음(재업로드 idempotent)
      mode="replace": 테이블 전체 교체
    반환: 적재된 행 수
    """
    df = df.copy()
    df[SOURCE_COL] = source_file or "upload"
    df[INGESTED_COL] = pd.Timestamp.now().isoformat(timespec="seconds")
    table = _table(team_key)

    with _connect() as con:
        exists = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
        ).fetchone() is not None

        if mode == "replace" or not exists:
            df.to_sql(table, con, if_exists="replace", index=False)
            return len(df)

        if mode == "upsert" and period_column and period_column in df.columns:
            periods = [str(p) for p in df[period_column].unique()]
            placeholders = ",".join("?" for _ in periods)
            # 기존 동일 기간 삭제 (문자열 비교로 통일)
            con.execute(
                f'DELETE FROM "{table}" WHERE CAST("{period_column}" AS TEXT) IN ({placeholders})',
                periods,
            )
        df.to_sql(table, con, if_exists="append", index=False)
        return len(df)


def clear_team(team_key: str) -> None:
    with _connect() as con:
        con.execute(f'DROP TABLE IF EXISTS "{_table(team_key)}"')


def list_tables() -> list[tuple[str, int]]:
    """(team_key, row_count) 목록."""
    if not DB_PATH.exists():
        return []
    out = []
    with _connect() as con:
        names = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'data_%'"
        ).fetchall()]
        for n in names:
            cnt = int(con.execute(f'SELECT COUNT(*) FROM "{n}"').fetchone()[0])
            out.append((n[len("data_"):], cnt))
    return out
