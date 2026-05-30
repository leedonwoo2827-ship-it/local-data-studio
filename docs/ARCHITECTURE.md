# 아키텍처 — 코드 구조와 데이터 흐름

## 한 장 요약
```
                         ┌──────────────────────────────────────┐
   데이터 소스            │              app.py (Streamlit)        │
  ┌──────────────┐       │  studio/sidebar → dashboard → ai_panel │
  │ 샘플 CSV       │──┐   └───────┬───────────────┬────────────────┘
  │ 누적 DB(SQLite)│──┼─► df ─►   │ compute_kpis  │  AI 4종
  │ 일회성 업로드   │──┘           │ (core/metrics)│  (core/ai/*)
  └──────────────┘               ▼               ▼
                         Green/Red 신호·표·차트    DeepSeek(core/llm)
                         (core/charts)            via LiteLLM 프록시
```

## 레이어
| 레이어 | 위치 | 책임 |
|--------|------|------|
| 진입점 | `app.py` | .env 로드 → 사이드바 → 대시보드 → AI 패널 조립 |
| UI | `studio/` | sidebar(소스/적재/필터), dashboard(도넛·카드·표·차트), kpi_cards, ai_panel(탭) |
| 도메인 로직 | `core/` | config(YAML), data_loader, metrics(신호계산), charts(plotly), store(SQLite) |
| AI | `core/ai/` | insights · chat · recommend · report (모두 `core/llm` 경유) |
| 내보내기 | `core/export.py` | 보고서 마크다운 → Excel·Word·PDF·PPTX 변환 |
| LLM | `core/llm.py`, `core/ubion_llm.py` | DeepSeek 단일 진입점(lazy), 키트 래퍼 |
| 설정/데이터 | `config/teams/`, `data/samples/`, `_rawdata/`, `db/` | 팀 정의·샘플·원시·누적DB |
| 지식/문서 | `knowledge/`, `docs/`, `prompts/` | 도메인 지식·사용설명·프롬프트 |

## 핵심 흐름
1. **사이드바**가 팀 config를 고르고, 데이터 소스(샘플/DB/업로드)에서 `df` 를 만든다. 기간 필터 적용.
2. **metrics.compute_kpis(df, cfg)** 가 KPI별 실적/목표/달성률/신호(Green·Red)를 계산.
3. **dashboard** 가 도넛(Green/Red 비율)·KPI 카드·달성도 표·추이 차트를 렌더.
4. **ai_panel** 이 같은 `df`+KPI 결과를 DeepSeek에 보내 인사이트/Q&A/보고서/차트추천 생성.

## 설계 원칙
- **팀 차이는 전부 config YAML 에 격리** → 코드는 팀 무관, 새 팀은 파일 추가만.
- **신호 로직 통일**: higher/lower_better 를 달성비율로 통합(`metrics.py`).
- **LLM은 lazy**: 키 없어도 앱은 뜨고, AI 호출 시점에만 클라이언트 생성(`core/llm.py`).
- **누적은 SQLite**: 단일 파일·서버리스·upsert. 근거는 [DATA_STORE.md](DATA_STORE.md).
