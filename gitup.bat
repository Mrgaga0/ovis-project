@echo off
:: GitHub 자동 업로드 배치 파일 (자동 버전 관리 포함)
:: 사용법: github-upload.bat "커밋 메시지"

:: 한글 인코딩 설정 (인코딩 문제 해결)
chcp 65001 > nul
setlocal EnableDelayedExpansion

:: 색상 설정
color 0A

echo ===================================
echo    GitHub 자동 업로드 및 버전 관리 도구
echo ===================================
echo.

:: 커밋 메시지 확인
if "%~1"=="" (
    echo 커밋 메시지를 입력하세요:
    set /p COMMIT_MSG="> "
) else (
    set "COMMIT_MSG=%~1"
)

:: Git이 설치되어 있는지 확인
git --version > nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [오류] Git이 설치되어 있지 않습니다. https://git-scm.com/downloads 에서 설치해주세요.
    goto :error
)

:: 현재 폴더가 Git 저장소인지 확인
if not exist .git (
    echo [알림] 현재 폴더는 Git 저장소가 아닙니다. 초기화합니다...
    
    :: 저장소 초기화
    git init
    if %ERRORLEVEL% neq 0 goto :error
    
    :: 원격 저장소 연결
    echo [알림] GitHub 저장소와 연결합니다...
    
    :: HTTPS 주소에 인증 정보 포함 (사용자명, 토큰)
    set /p GIT_USERNAME="GitHub 사용자명을 입력하세요: "
    set /p GIT_TOKEN="GitHub 개인 액세스 토큰을 입력하세요: "
    
    git remote add origin https://%GIT_USERNAME%:%GIT_TOKEN%@github.com/Mrgaga0/ovis-project.git
    if %ERRORLEVEL% neq 0 goto :error
    
    echo [성공] Git 저장소가 초기화되었습니다.
) else (
    echo [알림] 기존 Git 저장소를 사용합니다.
)

:: 변경사항이 있는지 확인
git status --porcelain > nul 2>&1
if %ERRORLEVEL% neq 0 goto :error

:: 변경된 모든 파일 스테이징
echo [진행] 변경된 파일을 스테이징 중...
git add .
if %ERRORLEVEL% neq 0 goto :error

:: 버전 파일 확인 및 업데이트
set "VERSION_FILE=version.txt"
set NEW_VERSION=0.19

if exist %VERSION_FILE% (
    :: 기존 버전 파일 읽기
    set /p CURRENT_VERSION=<%VERSION_FILE%
    
    :: 버전 증가 (소수점 이후 숫자만 증가)
    for /f "tokens=1,2 delims=." %%a in ("!CURRENT_VERSION!") do (
        set MAJOR=%%a
        set MINOR=%%b
    )
    
    set /a MINOR=MINOR+1
    set NEW_VERSION=!MAJOR!.!MINOR!
) 

:: 새 버전 저장
echo !NEW_VERSION! > %VERSION_FILE%
echo [진행] 버전 업데이트: ovis-!NEW_VERSION!

:: 변경사항 커밋 (버전 포함)
echo [진행] 변경사항을 커밋 중...
git add %VERSION_FILE%
git commit -m "%COMMIT_MSG% [ovis-!NEW_VERSION!]"
if %ERRORLEVEL% neq 0 goto :error

:: 버전 태그 생성
echo [진행] 버전 태그 생성 중...
git tag -a ovis-!NEW_VERSION! -m "Version ovis-!NEW_VERSION!"
if %ERRORLEVEL% neq 0 goto :error

:: 브랜치 확인 및 GitHub에 푸시
echo [진행] 현재 브랜치를 확인 중...
for /f "tokens=*" %%a in ('git branch --show-current') do set CURRENT_BRANCH=%%a

if "%CURRENT_BRANCH%"=="" (
    set CURRENT_BRANCH=main
)

:: 브랜치 확인 및 GitHub에 푸시
echo [진행] GitHub에 푸시 중 (main 브랜치)...
echo git push -u origin main
git push -u origin main 2>&1
if %ERRORLEVEL% neq 0 (
    echo [오류] 푸시 과정에서 문제가 발생했습니다. 오류 코드: %ERRORLEVEL%
    goto :error
)

:: 태그 푸시
echo [진행] 버전 태그 푸시 중...
echo git push origin ovis-!NEW_VERSION!
git push origin ovis-!NEW_VERSION! 2>&1
if %ERRORLEVEL% neq 0 (
    echo [오류] 태그 푸시 과정에서 문제가 발생했습니다. 오류 코드: %ERRORLEVEL%
    goto :error
)

echo.
echo [성공] 모든 작업이 완료되었습니다!
echo 저장소 URL: https://github.com/Mrgaga0/ovis-project
echo 현재 버전: ovis-!NEW_VERSION!
echo.
goto :end

:error
echo.
echo [오류] 작업 중 문제가 발생했습니다.
echo 다음 단계를 확인해보세요:
echo 1. GitHub 사용자명과 개인 액세스 토큰이 올바른지 확인
echo 2. 인터넷 연결 상태 확인
echo 3. 저장소 URL이 올바른지 확인 (https://github.com/Mrgaga0/ovis-project)
echo.
echo 직접 명령어 실행해보기:
echo git remote -v
echo git status
echo.
exit /b 1

:end
endlocal
pause