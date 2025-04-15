@echo off
setlocal

REM OVIS 백엔드 서버 실행 스크립트
echo OVIS 백엔드 서버를 시작합니다...

REM 환경 변수 설정
set PYTHONPATH=%~dp0
set ENVIRONMENT=development
set DATABASE_URL=sqlite:///data/ovis.db
set LOG_LEVEL=debug
set PORT=3002
set HOST=0.0.0.0
set API_PREFIX=/api/v1
set CORS_ORIGINS=*

REM .env 파일에서 GEMINI_API_KEY 로드
for /f "tokens=1,* delims==" %%a in (.env) do (
    if "%%a"=="GEMINI_API_KEY" set GEMINI_API_KEY=%%b
)

echo API 키: %GEMINI_API_KEY%

REM 필요한 디렉토리 생성
if not exist data mkdir data
if not exist logs mkdir logs
if not exist ovis_save mkdir ovis_save

REM 가상환경 활성화 (존재한다면)
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo 가상환경이 없습니다. Python이 시스템 경로에 있어야 합니다.
)

REM 필요한 패키지 설치
pip install -r ovis-api/requirements.txt

REM 백엔드 서버 실행
cd ovis-api
python -m uvicorn app.main:app --host %HOST% --port %PORT% --reload --log-level %LOG_LEVEL%

REM 가상환경 비활성화
if exist venv\Scripts\activate.bat (
    deactivate
)

echo OVIS 백엔드 서버가 종료되었습니다.
endlocal 