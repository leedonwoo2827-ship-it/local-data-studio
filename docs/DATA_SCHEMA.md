# 데이터 파일 컬럼 규약

## 기본 형태 (집계형 — 대시보드 기본)
- **1행 = 1기간** (예: 한 달). 행이 기간 순서대로 정렬.
- 반드시 **기간 컬럼**(config `period_column`) 1개 + **KPI 컬럼**들.
- 컬럼명은 config의 `column` 값과 **정확히 일치**(앞뒤 공백 자동 제거됨).

예) `data/samples/education_2025.csv`
```
월,수강신청수,랜딩전환율,광고비,CAC,SNS도달수,ROAS
1,93,3.45,7210000,32100,38120,331
2,96,3.51,7430000,32480,39050,334
...
```

## 원시 로그형 (적재/누적용)
`_rawdata/*.csv` 처럼 **1행 = 일자 × 차원(채널/지역/캠페인 등)** 인 세밀한 데이터도 OK.
이 경우:
- 사이드바 **📥 데이터 적재**로 SQLite에 `append` 또는 `upsert`.
- 단, 대시보드 KPI는 config의 `column`/`agg` 로 집계되므로, **KPI 컬럼이 존재**해야 계산된다.
- 일자 단위를 월 KPI로 보고 싶으면, 미리 월 집계 후 올리거나(권장), 차원 컬럼을 무시하고
  `agg: sum/mean` 으로 전체 합/평균을 보는 방식이 가능하다.

## 포맷
- CSV (UTF-8 권장, CP949 자동 호환) 또는 Excel(.xlsx/.xls).
- 숫자 컬럼에 쉼표/통화기호가 없어야 정확히 합산됨(가능하면 순수 숫자).
- 결측치는 빈 칸으로 두면 집계 시 제외된다.

## 제공 샘플/원시 데이터
| 팀(config) | 샘플(월별) | 원시(_rawdata, 일자×차원) |
|------------|-----------|---------------------------|
| 운영팀 | operations_2025.csv | operations_raw.csv (채널) |
| 교육사업팀 | education_2025.csv | education_raw.csv (과정군×광고채널) |
| 글로벌사업팀 | global_biz_2025.csv | global_biz_raw.csv (지역) |
| 마케팅팀 | marketing_2025.csv | marketing_raw.csv (캠페인×채널) |
| 투자팀 | investment_2025.csv | investment_raw.csv (전략) |
