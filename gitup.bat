@echo off
:: GitHub main 브랜치 백업 배치 파일 (최종)
:: 한글 인코딩 설정
chcp 65001 > nul

echo ===================================
echo    GitHub main 브랜치 백업 도구
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
echo [1/5] 변경사항 스테이징...
git add .

echo [2/5] 변경사항 커밋...
git commit -m "%COMMIT_MSG% [ovis-%NEW_VERSION%]"

echo [3/5] 버전 태그 생성...
git tag -a ovis-%NEW_VERSION% -m "Version ovis-%NEW_VERSION%"

echo [4/5] main 브랜치에 병합하기...
:: 현재 브랜치 저장
for /f "tokens=*" %%a in ('git branch --show-current') do set CURRENT_BRANCH=%%a
echo 현재 브랜치: %CURRENT_BRANCH%

:: main 브랜치가 있는지 확인
git show-ref --verify --quiet refs/heads/main
if %ERRORLEVEL% neq 0 (
    echo main 브랜치가 없습니다. 생성합니다...
    git branch main
)

:: main 브랜치로 전환하여 현재 브랜치 내용 가져오기
git checkout main
git merge %CURRENT_BRANCH% --no-edit

echo [5/5] GitHub에 푸시...
git push -f origin main
git push origin ovis-%NEW_VERSION%

:: 원래 브랜치로 돌아가기
git checkout %CURRENT_BRANCH%

echo.
echo 작업이 완료되었습니다!
echo GitHub 저장소: https://github.com/Mrgaga0/ovis-project
echo 현재 버전: ovis-%NEW_VERSION%
echo.

pause