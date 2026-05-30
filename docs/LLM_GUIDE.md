# LLM(DeepSeek) · LiteLLM 연결 가이드

## 무엇을 쓰나
- **모델**: `deepseek-v4-flash` (기본). 추론과정이 필요하면 `deepseek-v4-flash-think`.
- **경유**: 사내 LiteLLM 프록시 (OpenAI 호환).
- **래퍼**: 키트의 `ubion_llm.py` 를 [core/ubion_llm.py](../core/ubion_llm.py) 로 복사해 사용.
  단일 진입점은 [core/llm.py](../core/llm.py).

## 연결 설정
```
UBION_LITELLM_URL=http://your-litellm-host:4000
UBION_LITELLM_KEY=sk-...본인키...
LDS_MODEL=deepseek-v4-flash      # 모델 교체는 이 변수만 바꾸면 됨
```
`.env` 또는 키트 bootstrap 으로 등록. 자세히는 [SETUP.md](SETUP.md).

## AI 기능 4종 (모두 prompts/*.md 템플릿 기반)
| 기능 | 코드 | 프롬프트 | 입력 |
|------|------|----------|------|
| 자동 인사이트/요약 | core/ai/insights.py | prompts/insight_summary.md | KPI 표 + 도메인 맥락 |
| 데이터 챗봇(Q&A) | core/ai/chat.py | prompts/data_qa.md | df 요약/샘플 + KPI 표 + 질문 |
| 차트/구성 추천 | core/ai/recommend.py | prompts/chart_recommend.md | 업로드 데이터 스키마 |
| 중간/최종 보고서 | core/ai/report.py | prompts/report.md | KPI 표 + 추이 + 보고서유형 |

> 보고서는 생성 후 **Markdown · Excel(.xlsx) · Word(.docx) · PDF · PowerPoint(.pptx)** 로 내려받을 수 있다.
> 변환 로직은 [core/export.py](../core/export.py) (마크다운 파싱 → 포맷별 렌더러). PDF는 한글 폰트(맑은 고딕 등)를 자동 임베딩한다.

### 비용/성능 메모
- DeepSeek 계열은 **신 OpenAI 모델이 아니므로 `max_tokens` 그대로** 사용(자동 처리됨).
- 동일 프롬프트는 프록시의 **Redis 캐시(10분)** 로 무료 재응답될 수 있음(버그 아님).
- 챗봇은 **코드 실행 없이** df 요약/샘플을 컨텍스트로 주입하는 안전 방식.

## 프롬프트를 Skill 로 고도화하기 (로드맵)
현재는 `prompts/*.md` 텍스트 템플릿이다. 다음 단계로:
1. 각 프롬프트를 Claude Code **skill**(`SKILL.md` + 입력 스키마)로 승격.
2. 챗봇을 **tool-use / code-exec**(pandas 쿼리 실행)로 고도화해 정밀 집계 질의 지원.
3. 키트의 `skills/ubion-litellm/SKILL.md` 패턴을 참고해 `skills/local-data-studio/` 신설.

> 현재 코드는 `core/llm.py:load_prompt()` 로 템플릿을 읽으므로,
> 프롬프트 파일만 교체/개선해도 즉시 반영된다.
