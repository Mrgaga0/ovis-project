@echo off
:: GitHub main 브랜치 백업 배치 파일 (향상된 버전)
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

:: 이전 버전 폴더 생성
set OLD_VERSION_FOLDER=archive\ovis-%CURRENT_VERSION%
echo [1/7] 이전 버전(%CURRENT_VERSION%) 파일을 '%OLD_VERSION_FOLDER%' 폴더로 이동...
if not exist archive mkdir archive
if not exist %OLD_VERSION_FOLDER% mkdir %OLD_VERSION_FOLDER%

:: 변경된 파일 목록 저장
git diff --name-only HEAD > changed_files.txt

:: 이전 파일 백업 (변경되지 않은 파일)
for /f "tokens=*" %%f in ('git ls-files') do (
    set "FILE=%%f"
    findstr /C:"%%f" changed_files.txt >nul 2>&1
    if errorlevel 1 (
        :: 파일이 변경 목록에 없으면
        if not "%%f"=="%VERSION_FILE%" (
            if not "%%f"=="gitup.bat" (
                if not exist "%OLD_VERSION_FOLDER%\%%~dpf" mkdir "%OLD_VERSION_FOLDER%\%%~dpf"
                copy "%%f" "%OLD_VERSION_FOLDER%\%%f" >nul
            )
        )
    )
)

:: 임시 파일 삭제
del changed_files.txt

:: 커밋 메시지 입력
echo 커밋 메시지를 입력하세요:
set /p COMMIT_MSG="> "

:: Git 명령어 실행
echo.
echo [2/7] 변경사항 스테이징...
git add .

echo [3/7] 아카이브 폴더 커밋...
git add archive/
git commit -m "아카이브: 버전 ovis-%CURRENT_VERSION% 백업" --quiet

echo [4/7] 현재 버전 변경사항 커밋...
git commit -m "%COMMIT_MSG% [ovis-%NEW_VERSION%]"

echo [5/7] 버전 태그 생성...
git tag -a ovis-%NEW_VERSION% -m "Version ovis-%NEW_VERSION%"

echo [6/7] main 브랜치에 병합하기...
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

echo [7/7] GitHub에 푸시...
git push -f origin main
git push origin ovis-%NEW_VERSION%

:: 원래 브랜치로 돌아가기
git checkout %CURRENT_BRANCH%

echo.
echo 작업이 완료되었습니다!
echo GitHub 저장소: https://github.com/Mrgaga0/ovis-project
echo 현재 버전: ovis-%NEW_VERSION%
echo 이전 버전은 '%OLD_VERSION_FOLDER%' 폴더에 보관되었습니다.
echo.
pause