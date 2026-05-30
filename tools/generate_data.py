"""
tools/generate_data.py — 샘플/원시 데이터 생성기 (재현 가능, seed 고정).

생성물:
  1) data/samples/*.csv      — 월별(2025) 집계. config 의 KPI 컬럼과 1:1 매칭. 대시보드 기본 로드용.
  2) <repo_parent>/_rawdata/*.csv — 일자 단위 + 차원(채널/지역/캠페인 등) 원시 데이터.
                                    "엑셀을 계속 쌓는" 적재(ingest) 테스트/시연용.

실행:  python tools/generate_data.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SAMPLES_DIR = PROJECT_ROOT / "data" / "samples"
RAWDATA_DIR = PROJECT_ROOT / "_rawdata"

RNG = np.random.default_rng(20260530)
MONTHS = list(range(1, 13))
DAYS = pd.date_range("2024-01-01", "2025-12-31", freq="D")


def _noise(n: int, scale: float) -> np.ndarray:
    return RNG.normal(0, scale, n)


# ---------------------------------------------------------------------------
# 1) 월별 샘플 (config KPI 컬럼과 정확히 일치, Green/Red 혼재되도록 의도적 설계)
# ---------------------------------------------------------------------------
def gen_operations_sample() -> pd.DataFrame:
    t = np.array(MONTHS)
    return pd.DataFrame({
        "월": MONTHS,
        "브랜드인지도지수": np.round(66 + 0.4 * t + _noise(12, 1.2), 1),       # mean~69  (목표70) Green
        "공식채널유입수": np.round(4000 + 60 * t + _noise(12, 300)).astype(int),  # sum~52k (목표50k) Green
        "콘텐츠발행건수": np.round(17 + _noise(12, 1.5)).astype(int),            # sum~205 (목표240) Red
        "보도자료노출수": np.round(8500 + 50 * t + _noise(12, 600)).astype(int),  # sum~105k(목표120k) Red
        "리드확보수": np.round(140 + 2 * t + _noise(12, 12)).astype(int),        # sum~1750(목표1800) Green경계
    })


def gen_education_sample() -> pd.DataFrame:
    t = np.array(MONTHS)
    ad = np.round(7_000_000 + 200_000 * t + _noise(12, 400_000)).astype(int)
    return pd.DataFrame({
        "월": MONTHS,
        "수강신청수": np.round(90 + 3 * t + _noise(12, 8)).astype(int),          # sum~1300 (목표1200) Green
        "랜딩전환율": np.round(3.4 + 0.05 * t + _noise(12, 0.3), 2),             # mean~3.7 (목표4.5) Red
        "광고비": ad,
        "CAC": np.round(32000 + 400 * t + _noise(12, 1500)).astype(int),        # mean~34.6k(목표35k,낮을수록↑) Green
        "SNS도달수": np.round(37000 + 800 * t + _noise(12, 4000)).astype(int),   # sum~507k (목표600k) Red
        "ROAS": np.round(330 + 4 * t + _noise(12, 25), 0),                      # mean~356 (목표350) Green
    })


def gen_global_sample() -> pd.DataFrame:
    t = np.array(MONTHS)
    return pd.DataFrame({
        "월": MONTHS,
        "해외방문자수": np.round(6000 + 120 * t + _noise(12, 500)).astype(int),     # sum~81k (목표80k) Green
        "다국어콘텐츠조회수": np.round(12500 + 300 * t + _noise(12, 1500)).astype(int),  # sum~173k(목표200k) Red
        "해외문의수": np.round(42 + 1.5 * t + _noise(12, 6)).astype(int),          # sum~620 (목표600) Green
        "지역별전환율": np.round(1.85 + 0.05 * t + _noise(12, 0.2), 2),           # mean~2.2 (목표2.5) Red
        "파트너십문의": np.round(8 + 0.4 * t + _noise(12, 2)).astype(int),         # sum~125 (목표120) Green
    })


def gen_marketing_sample() -> pd.DataFrame:
    t = np.array(MONTHS)
    return pd.DataFrame({
        "월": MONTHS,
        "총ROAS": np.round(370 + 6 * t + _noise(12, 30), 0),                     # mean~409 (목표400) Green
        "전체유입수": np.round(22000 + 500 * t + _noise(12, 1800)).astype(int),    # sum~303k(목표300k) Green
        "전환수": np.round(680 + 18 * t + _noise(12, 60)).astype(int),           # sum~9560(목표9000) Green
        "참여율": np.round(3.9 + 0.05 * t + _noise(12, 0.25), 2),                # mean~4.2 (목표5.0) Red
        "광고비집행": np.round(10_700_000 + 250_000 * t + _noise(12, 600_000)).astype(int),  # sum~145M(목표120M,낮을수록↑) Red
    })


def gen_investment_sample() -> pd.DataFrame:
    t = np.array(MONTHS)
    monthly_ret = np.round(0.8 + 0.15 * np.sin(t / 2) + _noise(12, 1.4), 2)     # 월수익률 %
    cum = np.round(np.cumsum(monthly_ret), 2)                                   # 누적수익률 (last~목표12 부근)
    return pd.DataFrame({
        "월": MONTHS,
        "월수익률": monthly_ret,
        "누적수익률": cum,                                                       # last 값으로 평가
        "승률": np.round(53 + _noise(12, 4), 1),                                # mean~53 (목표60) Red
        "MDD": np.round(np.abs(7 + _noise(12, 2.5)), 1),                        # max~ (목표10이하)
        "샤프지수": np.round(1.05 + _noise(12, 0.18), 2),                        # mean~1.05 (목표1.0) Green
        "알파": np.round(np.cumsum(0.25 + _noise(12, 0.5)), 2),                  # last (목표3)
    })


SAMPLE_BUILDERS = {
    "operations_2025": gen_operations_sample,
    "education_2025": gen_education_sample,
    "global_biz_2025": gen_global_sample,
    "marketing_2025": gen_marketing_sample,
    "investment_2025": gen_investment_sample,
}


# ---------------------------------------------------------------------------
# 2) 원시(raw) 데이터 — 일자 × 차원 (적재 시연용, 대용량)
# ---------------------------------------------------------------------------
def _daily_dim_frame(dims: dict[str, list[str]], col_fn) -> pd.DataFrame:
    """일자 × (차원 곱집합) 행을 만들고 col_fn(date, combo)->dict 로 수치 생성."""
    import itertools
    dim_names = list(dims.keys())
    combos = list(itertools.product(*dims.values()))
    rows = []
    for d in DAYS:
        for combo in combos:
            base = {"일자": d.date().isoformat()}
            base.update(dict(zip(dim_names, combo)))
            base.update(col_fn(d, dict(zip(dim_names, combo))))
            rows.append(base)
    return pd.DataFrame(rows)


def gen_operations_raw() -> pd.DataFrame:
    weight = {"홈페이지": 1.0, "블로그": 0.6, "유튜브": 0.5, "뉴스레터": 0.3, "SNS": 0.8}
    def fn(d, c):
        w = weight[c["채널"]]
        imp = max(0, int(RNG.normal(4000 * w, 800)))
        sess = int(imp * RNG.uniform(0.18, 0.35))
        return {
            "노출수": imp,
            "유입수": sess,
            "평균체류초": round(RNG.uniform(40, 240), 1),
            "콘텐츠발행": int(RNG.random() < 0.12 * w),
            "보도자료노출": max(0, int(RNG.normal(300 * w, 120))),
            "리드수": max(0, int(sess * RNG.uniform(0.01, 0.04))),
            "브랜드언급수": max(0, int(RNG.normal(60 * w, 25))),
        }
    return _daily_dim_frame({"채널": list(weight)}, fn)


def gen_education_raw() -> pd.DataFrame:
    courses = ["어학", "IT", "자격증", "취미교양", "직무역량"]
    channels = ["검색광고", "SNS", "디스플레이"]
    def fn(d, c):
        imp = max(0, int(RNG.normal(3000, 700)))
        clk = int(imp * RNG.uniform(0.02, 0.06))
        land = int(clk * RNG.uniform(0.5, 0.8))
        enr = int(land * RNG.uniform(0.03, 0.09))
        cost = int(clk * RNG.uniform(300, 700))
        return {
            "노출수": imp, "클릭수": clk, "랜딩방문": land,
            "수강신청": enr, "광고비": cost,
            "결제금액": enr * int(RNG.uniform(150000, 450000)),
        }
    return _daily_dim_frame({"과정군": courses, "광고채널": channels}, fn)


def gen_global_raw() -> pd.DataFrame:
    regions = {"북미": "en", "유럽": "en", "동남아": "en", "중동": "ar", "중국": "zh", "일본": "ja"}
    def fn(d, c):
        vis = max(0, int(RNG.normal(1200, 400)))
        views = int(vis * RNG.uniform(1.2, 2.5))
        inq = max(0, int(vis * RNG.uniform(0.005, 0.02)))
        return {
            "언어": regions[c["지역"]],
            "방문자수": vis, "콘텐츠조회수": views,
            "문의수": inq,
            "파트너십문의": int(RNG.random() < 0.15),
            "광고비": int(vis * RNG.uniform(200, 600)),
        }
    return _daily_dim_frame({"지역": list(regions)}, fn)


def gen_marketing_raw() -> pd.DataFrame:
    campaigns = ["브랜딩", "퍼포먼스", "리텐션"]
    channels = ["검색", "디스플레이", "SNS", "이메일", "제휴"]
    def fn(d, c):
        imp = max(0, int(RNG.normal(8000, 2000)))
        clk = int(imp * RNG.uniform(0.01, 0.05))
        conv = int(clk * RNG.uniform(0.02, 0.08))
        cost = int(clk * RNG.uniform(400, 900))
        return {
            "노출수": imp, "클릭수": clk, "전환수": conv,
            "광고비": cost, "매출": conv * int(RNG.uniform(30000, 120000)),
        }
    return _daily_dim_frame({"캠페인": campaigns, "채널": channels}, fn)


def gen_investment_raw() -> pd.DataFrame:
    strategies = ["모멘텀", "가치", "배당", "성장"]
    tickers = {"모멘텀": "MOM01", "가치": "VAL01", "배당": "DIV01", "성장": "GRW01"}
    def fn(d, c):
        ret = round(RNG.normal(0.04, 1.3), 3)
        bench = round(RNG.normal(0.03, 1.0), 3)
        return {
            "종목코드": tickers[c["전략"]],
            "일수익률": ret,
            "벤치마크수익률": bench,
            "포지션비중": round(RNG.uniform(0.05, 0.35), 3),
            "거래횟수": int(RNG.poisson(1.2)),
            "평가금액": int(RNG.uniform(8_000_000, 25_000_000)),
        }
    return _daily_dim_frame({"전략": strategies}, fn)


RAW_BUILDERS = {
    "operations_raw": gen_operations_raw,
    "education_raw": gen_education_raw,
    "global_biz_raw": gen_global_raw,
    "marketing_raw": gen_marketing_raw,
    "investment_raw": gen_investment_raw,
}


def main() -> None:
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    RAWDATA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[samples] -> {SAMPLES_DIR}")
    for name, fn in SAMPLE_BUILDERS.items():
        df = fn()
        out = SAMPLES_DIR / f"{name}.csv"
        df.to_csv(out, index=False, encoding="utf-8-sig")
        print(f"  {out.name}: {len(df)} rows, {len(df.columns)} cols")

    print(f"[rawdata] -> {RAWDATA_DIR}")
    for name, fn in RAW_BUILDERS.items():
        df = fn()
        out = RAWDATA_DIR / f"{name}.csv"
        df.to_csv(out, index=False, encoding="utf-8-sig")
        print(f"  {out.name}: {len(df):,} rows, {len(df.columns)} cols")

    print("done.")


if __name__ == "__main__":
    main()
