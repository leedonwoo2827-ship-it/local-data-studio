"""
core/charts.py — Plotly 차트 빌더 (도넛 / 막대 / 선 / 영역 / 게이지).
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from .config import ChartDef

GREEN = "#2ecc71"
RED = "#e74c3c"
ACCENT = "#3498db"


def donut_green_red(green: int, red: int) -> go.Figure:
    """전체 Green/Red 비율 도넛 (참조 사진의 좌측 도넛)."""
    fig = go.Figure(data=[go.Pie(
        labels=["Green", "Red"],
        values=[green, red],
        hole=0.6,
        marker=dict(colors=[GREEN, RED]),
        textinfo="label+percent",
        sort=False,
    )])
    fig.update_layout(
        showlegend=True,
        margin=dict(t=10, b=10, l=10, r=10),
        height=300,
        annotations=[dict(text=f"{green}/{green + red}", x=0.5, y=0.5,
                          font_size=22, showarrow=False)],
    )
    return fig


def gauge(value_pct: float, title: str = "") -> go.Figure:
    """달성률 게이지 (0~120%)."""
    color = GREEN if value_pct >= 90 else RED
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value_pct,
        number={"suffix": "%"},
        title={"text": title},
        gauge={
            "axis": {"range": [0, 120]},
            "bar": {"color": color},
            "threshold": {"line": {"color": "black", "width": 2},
                          "thickness": 0.75, "value": 100},
        },
    ))
    fig.update_layout(height=220, margin=dict(t=40, b=10, l=20, r=20))
    return fig


def build_chart(df: pd.DataFrame, chart: ChartDef) -> go.Figure:
    """config 의 ChartDef 로 시계열/막대 차트 생성."""
    title = chart.title or f"{chart.y} by {chart.x}"
    if chart.type == "line":
        fig = px.line(df, x=chart.x, y=chart.y, markers=True, title=title)
    elif chart.type == "area":
        fig = px.area(df, x=chart.x, y=chart.y, title=title)
    else:  # bar (default)
        fig = px.bar(df, x=chart.x, y=chart.y, title=title)
    fig.update_traces(marker_color=ACCENT) if chart.type == "bar" else None
    fig.update_layout(height=320, margin=dict(t=50, b=30, l=20, r=20))
    return fig
