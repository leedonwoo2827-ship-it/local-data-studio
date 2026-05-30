# 설치 · 실행 · API 설정

## 요구사항
- Python 3.10+ (없으면 setup.bat 이 안내). 설치 시 "Add python.exe to PATH" 체크.
- LiteLLM 프록시 주소·키 (회사/관리자 지급). AI 없이 대시보드/표/차트만 볼 거면 없어도 동작.

## 가장 쉬운 방법 (Windows · 명령어 불필요)
1. 탐색기에서 **`setup.bat` 더블클릭** — 가상환경 + 패키지 설치 (처음 한 번).
2. **`run.bat` 더블클릭** — 브라우저에 대시보드가 열림 (기본 http://localhost:8501).
3. 화면 위 **⚙️ API 설정** 펼치기 → **API URL**(회사가 준 주소)과 **API 키** 입력
   → **🔌 연결 테스트** (초록색 "연결 성공") → **💾 저장**. 끝.
   - 주소가 바뀌면 이 패널에서 다시 입력 후 저장하면 된다 (파일 편집 불필요).
   - 저장값은 `.lds_settings.json`(로컬, git 제외)에 보관되어 다음 실행에도 유지된다.

> macOS/Linux: 터미널에서 `chmod +x setup.sh run.sh` 후 `./setup.sh` → `./run.sh`.

## (선택) 고급: .env 파일로 미리 지정
화면 입력 대신 파일로 넣고 싶다면 `.env.example` 을 `.env` 로 복사해 채운다.
화면에서 저장한 값이 있으면 그 값이 우선한다.
```
UBION_LITELLM_URL=http://회사가-준-주소:4000
UBION_LITELLM_KEY=sk-...본인키...
LDS_MODEL=deepseek-v4-flash
```

## (선택) 샘플/원시 데이터 재생성
```
.\.venv\Scripts\python.exe tools\generate_data.py
```
- `data/samples/*.csv` (월별 집계, 대시보드 기본 로드)
- `_rawdata/*.csv` (일자 단위 원시, 적재 시연용)

## 문제 해결
| 증상 | 원인/해결 |
|------|-----------|
| setup.bat 이 깜빡이고 닫힘 | Python 미설치 → 안내대로 설치(PATH 체크) 후 재실행 |
| AI 기능 클릭 시 "키 미설정" | ⚙️ API 설정에서 주소/키 입력 후 **저장** |
| 연결 테스트 인증 실패(401/403) | API 키 확인 |
| 연결 오류/타임아웃 | 사내망(VPN) 연결, 주소(host:port) 확인 |
| 한글 CSV 깨짐 | UTF-8/CP949 자동 처리. 안 되면 UTF-8(BOM)로 저장 |
| 대시보드 KPI가 0 | 데이터 컬럼명이 config의 `column` 과 다름 → CONFIG_GUIDE 참고 |
