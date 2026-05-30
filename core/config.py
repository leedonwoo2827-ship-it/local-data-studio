"""
core/config.py — 팀별 대시보드 설정(YAML) 로드/검증.

config/teams/*.yaml 한 개 = 한 팀(또는 한 도메인)의 대시보드 정의.
코드는 팀에 무관하며, 모든 차이는 이 YAML 에 격리된다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config" / "teams"

VALID_DIRECTIONS = {"higher_better", "lower_better"}
VALID_AGG = {"sum", "mean", "last", "max", "min"}


@dataclass
class KpiDef:
    name: str
    column: str
    target: float
    unit: str = ""
    direction: str = "higher_better"   # higher_better | lower_better
    green_threshold: float = 0.9       # 달성비율 >= 이 값이면 Green
    agg: str = "sum"                   # 기간 집계 방식: sum|mean|last|max|min

    def __post_init__(self):
        if self.direction not in VALID_DIRECTIONS:
            raise ValueError(
                f"KPI '{self.name}': direction 은 {VALID_DIRECTIONS} 중 하나여야 합니다 (got {self.direction!r})"
            )
        if self.agg not in VALID_AGG:
            raise ValueError(
                f"KPI '{self.name}': agg 는 {VALID_AGG} 중 하나여야 합니다 (got {self.agg!r})"
            )


@dataclass
class ChartDef:
    type: str           # line | bar | area
    x: str
    y: str
    title: str = ""


@dataclass
class TeamConfig:
    team: str
    period_column: str
    data_file: str
    kpis: list[KpiDef] = field(default_factory=list)
    charts: list[ChartDef] = field(default_factory=list)
    description: str = ""
    source_path: Path | None = None

    @property
    def resolved_data_path(self) -> Path:
        p = Path(self.data_file)
        return p if p.is_absolute() else PROJECT_ROOT / p

    @property
    def key(self) -> str:
        """SQLite 테이블명 등에 쓰는 안정적 식별자 (yaml 파일명 기반)."""
        if self.source_path is not None:
            return self.source_path.stem
        return "".join(ch if ch.isalnum() else "_" for ch in self.team)


def load_team_config(path: str | Path) -> TeamConfig:
    path = Path(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path}: YAML 최상위는 매핑이어야 합니다.")

    for required in ("team", "period_column", "data_file", "kpis"):
        if required not in raw:
            raise ValueError(f"{path}: 필수 키 '{required}' 누락")

    kpis = [KpiDef(**k) for k in raw["kpis"]]
    charts = [ChartDef(**c) for c in raw.get("charts", [])]
    return TeamConfig(
        team=raw["team"],
        period_column=raw["period_column"],
        data_file=raw["data_file"],
        kpis=kpis,
        charts=charts,
        description=raw.get("description", ""),
        source_path=path,
    )


def list_team_configs(config_dir: str | Path = CONFIG_DIR) -> dict[str, Path]:
    """{팀이름: yaml경로} 매핑. 앱 사이드바 드롭다운용."""
    config_dir = Path(config_dir)
    out: dict[str, Path] = {}
    for yml in sorted(config_dir.glob("*.yaml")):
        try:
            cfg = load_team_config(yml)
            out[cfg.team] = yml
        except Exception:
            # 깨진 config 는 건너뛰되, 파일명으로라도 노출
            out[yml.stem] = yml
    return out
