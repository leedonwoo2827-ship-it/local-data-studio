# 설치 · 환경변수 · 실행

## 요구사항
- Python 3.10+ (개발/검증은 3.12)
- 사내망에서 Ubion LiteLLM 프록시(`http://192.168.50.119:4000`) 접근 가능해야 AI 기능 사용 가능.
  (AI 없이 대시보드/보고서 표/차트만 볼 거면 키 없이도 동작)

## 1) 설치
### Windows
```powershell
.\setup.bat
```
### macOS / Linux
```bash
chmod +x setup.sh run.sh
./setup.sh
```
`setup` 은 `.venv` 가상환경을 만들고 `requirements.txt` 를 설치한다.

## 2) 환경변수 (AI 키)
두 가지 방법 중 하나:

**A. .env 파일** (가장 간단)
```powershell
copy .env.example .env   # (mac/linux: cp .env.example .env)
```
`.env` 를 열어 `UBION_LITELLM_KEY` 를 본인 키로 채운다.
개발/테스트 키는 `_context/Ubion_liteLLM_Migration_Kit/test_dev_api_key.txt` 참고.

**B. 키트 bootstrap** (시스템 환경변수로 등록)
```powershell
..\_context\Ubion_liteLLM_Migration_Kit\bootstrap.ps1
```

> 연결 확인:
> ```powershell
> curl http://192.168.50.119:4000/health/liveliness
> ```

## 3) 실행
```powershell
.\run.bat        # mac/linux: ./run.sh
```
브라우저가 자동으로 열린다(기본 http://localhost:8501).

## 4) 샘플/원시 데이터 재생성 (선택)
```powershell
.\.venv\Scripts\python.exe tools\generate_data.py
```
- `data/samples/*.csv` (월별 집계, 대시보드 기본 로드)
- `_rawdata/*.csv` (일자 단위 원시, 적재 시연용)

## 문제 해결
| 증상 | 원인/해결 |
|------|-----------|
| AI 기능 클릭 시 "키 미설정" | `.env` 의 `UBION_LITELLM_KEY` 확인, 앱 재시작 |
| AI 호출 실패/타임아웃 | 사내망(VPN) 연결, 프록시 health 확인 |
| 한글 CSV 깨짐 | UTF-8 또는 CP949 자동 처리됨. 그래도 깨지면 UTF-8(BOM)로 저장 |
| 대시보드 KPI가 0 | 업로드 데이터 컬럼명이 config의 `column` 과 다름 → CONFIG_GUIDE 참고 |
