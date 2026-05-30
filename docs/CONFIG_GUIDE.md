# 새 팀 / KPI / 목표 추가 가이드

이 스튜디오의 핵심은 **config 기반 일반화**다. 코드는 손대지 않고,
`config/teams/<팀>.yaml` 한 개와 데이터만 추가하면 새 대시보드가 생긴다.

## 1) 가장 빠른 길: AI 차트 추천 사용
1. 사이드바 **데이터 소스 → 일회성 업로드**로 새 데이터(CSV/Excel)를 올린다.
2. **✨ 차트 추천** 탭 → "차트 구성 추천" → 제안된 **config YAML**을 복사.
3. `config/teams/우리팀.yaml` 로 저장하고 `target` 값만 손본다. 끝.

## 2) 직접 작성

```yaml
team: 우리팀이름            # 사이드바 드롭다운에 표시
description: >             # AI 인사이트/보고서에 들어가는 도메인 맥락(선택)
  이 팀이 무엇을 추적하는지 1~2문장.
period_column: 월          # 기간 축 컬럼명 (월/주차/일자 등)
data_file: data/samples/우리팀_2025.csv   # 기본 로드할 샘플 경로

kpis:
  - name: 표시이름          # 카드/표에 보일 이름
    column: 데이터컬럼명     # CSV 의 실제 컬럼명과 일치해야 함
    unit: "%"              # 표시 단위 (명/건/원/% 등, 없으면 "")
    target: 1200           # 목표값
    direction: higher_better   # higher_better | lower_better
    green_threshold: 0.9   # 달성비율 >= 이 값이면 Green
    agg: sum               # 기간 집계: sum | mean | last | max | min

charts:
  - {type: line, x: 월, y: 수강신청수, title: 월별 추이}
  - {type: bar,  x: 월, y: 광고비,     title: 월별 광고비}
```

## 3) 필드 정하는 법

### direction (방향)
- `higher_better`: 클수록 좋음 (매출, 전환수, 수익률, 방문자 …)
- `lower_better`: 작을수록 좋음 (CAC, 광고비/예산, 이탈률, MDD 최대낙폭 …)

### agg (기간 집계) — 여러 기간을 하나의 "실적"으로 합치는 방식
| 지표 유형 | 권장 agg | 예 |
|-----------|----------|----|
| 건수/금액 누계 | `sum` | 수강신청수, 전환수, 광고비 |
| 비율/지수(평균이 의미) | `mean` | 전환율, ROAS, 참여율, 브랜드지수 |
| 누적/잔액(마지막 값) | `last` | 누적수익률, 누적가입자 |
| 최악값(낙폭 등) | `max` | MDD |

### green_threshold (신호 기준)
- 달성비율 계산: higher_better = `실적/목표`, lower_better = `목표/실적`.
- 두 경우 모두 **달성비율 ≥ green_threshold → Green**, 아니면 Red.
- 보수적으로 보려면 `1.0`(목표 100% 달성해야 Green), 관대하게는 `0.9`.

## 4) 데이터 누적해서 쓰기
샘플 대신 실제 데이터를 계속 쌓으려면 → 사이드바 **📥 데이터 적재**로 SQLite에 누적.
자세히: [DATA_STORE.md](DATA_STORE.md)

## 체크리스트
- [ ] CSV 컬럼명 == config의 `column` (정확히 일치, 공백 주의)
- [ ] `period_column` 이 실제 데이터에 존재
- [ ] `target` 단위가 데이터 단위와 동일 (원 vs 만원 혼동 금지)
- [ ] 저장 후 앱 새로고침 → 드롭다운에 새 팀 표시 확인
