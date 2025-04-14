@echo off
:: GitHub 간단 백업 배치 파일 (v12)
:: 한글 인코딩 설정
chcp 65001 > nul

echo ===================================
echo    GitHub 간단 백업 도구 (v12)
echo ===================================
echo.

:: 버전 관리 변수
set VERSION_FILE=version.txt
set DEFAULT_VERSION=0.19

:: 버전 읽기 또는 초기화
if exist %VERSION_FILE% (
    set /p CURRENT_VERSION=<%VERSION_FILE%
) else (
    set CURRENT_VERSION=%DEFAULT_VERSION%
)

:: 버전 표시
echo 현재 버전: ovis-%CURRENT_VERSION%
echo.

:: 버전 증가 (간단하게)
for /f "tokens=1,2 delims=." %%a in ("%CURRENT_VERSION%") do (
    set MAJOR=%%a
    set /a MINOR=%%b+1
)
set NEW_VERSION=%MAJOR%.%MINOR%

:: 새 버전 저장
echo %NEW_VERSION% > %VERSION_FILE%
echo 새 버전: ovis-%NEW_VERSION%
echo.

:: 커밋 메시지 입력
echo 커밋 메시지를 입력하세요:
set /p COMMIT_MSG="> "

:: Git 명령어 실행
echo.
echo [1/4] 변경사항 스테이징...
git add .

echo [2/4] 변경사항 커밋...
git commit -m "%COMMIT_MSG% [ovis-%NEW_VERSION%]"

echo [3/4] 버전 태그 생성...
git tag -a ovis-%NEW_VERSION% -m "Version ovis-%NEW_VERSION%"

echo [4/4] GitHub에 푸시...
:: master에서 main으로 변경하고 푸시
echo 클로드 연동을 위해 main 브랜치로 변경합니다...

:: 현재 브랜치 확인
for /f "tokens=*" %%a in ('git branch --show-current') do set CURRENT_BRANCH=%%a
echo 현재 브랜치: %CURRENT_BRANCH%

:: main 브랜치 생성 및 전환 (없는 경우)
git checkout -b main 2>nul
if %ERRORLEVEL% neq 0 (
    :: 이미 존재하면 전환만
    git checkout main
)

:: main 브랜치로 푸시
git push -u origin main
git push origin ovis-%NEW_VERSION%

echo.
echo 작업이 완료되었습니다!
echo GitHub 저장소: https://github.com/Mrgaga0/ovis-project
echo 현재 버전: ovis-%NEW_VERSION%
echo.

pause