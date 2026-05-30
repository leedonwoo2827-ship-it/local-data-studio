# Local Data Studio 📊

구글 Data Studio(구 Looker Studio)를 **사내 로컬로 대체**하는 팀별 성과 대시보드 스튜디오.
데이터(CSV/Excel)를 올리면 → **실시간 Green/Red 달성도 대시보드** + **중간/최종 보고서** + **AI 인사이트/챗봇/차트추천**을 즉시 생성합니다.

- **AI 엔진**: 딥시크 v4 플래시 (`deepseek-v4-flash`) — 사내 LiteLLM 프록시(OpenAI 호환) 경유
- **포함 예제 5종**: 운영팀 · 교육사업팀 · 글로벌사업팀 · 마케팅팀 (마케팅 도메인) + 투자팀 (비마케팅, 일반화 입증용)
- **config 기반**: 팀별 YAML 1개만 바꾸면 어느 팀/도메인이든 재사용
- **데이터 누적**: 엑셀을 계속 올려 SQLite에 쌓기(append/upsert) → [docs/DATA_STORE.md](docs/DATA_STORE.md)

## 시작하기 (Windows · 3단계, 명령어 필요 없음)

1. 탐색기에서 **`setup.bat` 더블클릭** → 설치(처음 한 번, 수 분 소요).
2. **`run.bat` 더블클릭** → 브라우저에 대시보드가 열립니다.
3. 화면 위 **⚙️ API 설정**에 **회사가 준 주소(URL)와 키**를 넣고 → **연결 테스트** → **저장**. 끝!
   - 주소가 바뀌면 이 패널에서 다시 고치면 됩니다 (파일 편집 불필요).

> macOS/Linux는 `./setup.sh` → `./run.sh`.  AI 키가 없어도 대시보드/표/차트는 동작합니다.

## 사용법

1. 사이드바에서 **팀(예제)** 선택 → 샘플 데이터 자동 로드.
2. **데이터 소스** 전환: `샘플 파일` / `누적 DB(SQLite)` / `일회성 업로드`.
   - 실데이터를 계속 쌓으려면 **📥 데이터 적재**로 엑셀/CSV를 DB에 누적.
3. 메인 화면에서 **Green/Red 도넛 · KPI 카드 · 달성도 표 · 추이 차트** 확인 (실시간 대시보드).
4. **🤖 AI 패널**:
   - 🧠 **자동 인사이트** — 달성/미달 원인·시사점 요약
   - 💬 **데이터 챗봇** — "목표를 미달한 지표는?" 같은 자연어 질문
   - 📝 **보고서 생성** — **중간보고서 / 최종보고서** 작성 후 **Markdown · Excel · Word · PDF · PPT** 내려받기
   - ✨ **차트 추천** — 업로드 데이터에 맞는 차트/KPI 구성을 YAML로 제안

## 새 팀 추가하기

`config/teams/<우리팀>.yaml` 하나 만들고 데이터만 넣으면 끝. (또는 **✨ 차트 추천**이 YAML을 만들어 줌)
→ 자세한 방법: [docs/CONFIG_GUIDE.md](docs/CONFIG_GUIDE.md)

## 더 알아보기 (docs / knowledge)

| 문서 | 내용 |
|------|------|
| [docs/SETUP.md](docs/SETUP.md) | 설치 · 환경변수 · 실행 상세 |
| [docs/CONFIG_GUIDE.md](docs/CONFIG_GUIDE.md) | 새 팀/KPI/목표 추가법 |
| [docs/DATA_SCHEMA.md](docs/DATA_SCHEMA.md) | 데이터 파일 컬럼 규약 |
| [docs/DATA_STORE.md](docs/DATA_STORE.md) | **데이터 누적 전략 (SQLite 리포트)** |
| [docs/LLM_GUIDE.md](docs/LLM_GUIDE.md) | DeepSeek/LiteLLM 연결 · 모델 · 비용 · skill 고도화 |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 코드 구조와 데이터 흐름 |
| [knowledge/](knowledge/) | KPI 정의 · 차트 선택 규칙 · 대시보드 설계 원칙 · 팀 맥락 |
