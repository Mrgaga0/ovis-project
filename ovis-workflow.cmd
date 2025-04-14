@echo off
setlocal enabledelayedexpansion
color 0B
title OVIS - 워크플로우 관리자 v0.19

REM =================================================
REM OVIS 워크플로우 관리자
REM 모든 OVIS 프로세스를 단일 인터페이스에서 관리
REM =================================================

:check_env
IF NOT EXIST .env (
    echo GEMINI_API_KEY= > .env
    echo.
    echo [!] .env 파일이 없어 새로 생성했습니다.
    echo [!] GEMINI_API_KEY를 설정해주세요.
    echo.
    timeout /t 3 > nul
)

:set_variables
set "API_ENDPOINT=http://localhost:528"
set "WEB_ENDPOINT=http://localhost:8080"
for /f "tokens=1,2 delims==" %%a in (.env) do (
    if "%%a"=="GEMINI_API_KEY" set "API_KEY=%%b"
)

:main_menu
cls
echo ======================================================
echo               OVIS 워크플로우 관리자 v0.19             
echo ======================================================
echo.
echo  [시스템 관리]
echo  1. Docker 환경 시작 (전체 시스템)
echo  2. Docker 환경 중지
echo  3. 로그 확인
echo  4. 시스템 상태 확인
echo.
echo  [데이터 수집 워크플로우]
echo  5. 뉴스 데이터 수집 시작 (멀티소스)
echo  6. 수집된 데이터 확인
echo.
echo  [주제 분석 워크플로우]
echo  7. 주제 분석 및 클러스터링 시작
echo  8. 정치 성향 분석 실행
echo  9. MZ 세대 관심도 분석 실행
echo.
echo  [콘텐츠 생성 워크플로우]
echo  10. 표준 기사 생성
echo  11. MZ 세대 타겟 콘텐츠 생성
echo  12. 유튜브 스크립트 생성
echo.
echo  [팩트체크 및 검증]
echo  13. 팩트체크 실행
echo  14. 콘텐츠 품질 검증
echo.
echo  [유틸리티]
echo  15. API 키 설정
echo  16. 빠른 알파 에이전트 설정
echo  17. GitHub 백업 (v0.19)
echo.
echo  0. 종료
echo.
echo ======================================================
echo.

set /p choice="메뉴 선택: "

if "%choice%"=="0" goto :exit
if "%choice%"=="1" goto :start_docker
if "%choice%"=="2" goto :stop_docker
if "%choice%"=="3" goto :view_logs
if "%choice%"=="4" goto :check_status
if "%choice%"=="5" goto :start_news_collection
if "%choice%"=="6" goto :view_collected_data
if "%choice%"=="7" goto :start_topic_analysis
if "%choice%"=="8" goto :run_political_analysis
if "%choice%"=="9" goto :run_mz_analysis
if "%choice%"=="10" goto :generate_standard_article
if "%choice%"=="11" goto :generate_mz_content
if "%choice%"=="12" goto :generate_youtube_script
if "%choice%"=="13" goto :run_factcheck
if "%choice%"=="14" goto :verify_content
if "%choice%"=="15" goto :set_api_key
if "%choice%"=="16" goto :setup_alpha_agent
if "%choice%"=="17" goto :github_backup

echo 잘못된 선택입니다. 다시 선택해주세요.
timeout /t 2 > nul
goto :main_menu

REM =================================================
REM 시스템 관리 함수
REM =================================================

:start_docker
cls
echo [시작] Docker 환경 시작 중...
echo.
echo 모든 오비스 서비스를 시작합니다.
echo 이 작업은 약 30초 정도 소요될 수 있습니다.
echo.

REM Docker Compose 실행
docker-compose up -d

echo.
echo [완료] Docker 환경이 시작되었습니다.
echo.
echo 웹 인터페이스: %WEB_ENDPOINT%
echo API 엔드포인트: %API_ENDPOINT%
echo.
pause
goto :main_menu

:stop_docker
cls
echo [시작] Docker 환경 중지 중...
echo.
echo 모든 오비스 서비스를 중지합니다.
echo.

REM Docker Compose 중지
docker-compose down

echo.
echo [완료] Docker 환경이 중지되었습니다.
echo.
pause
goto :main_menu

:view_logs
cls
echo [시작] 로그 확인 중...
echo.
echo Docker 컨테이너 로그를 표시합니다.
echo 종료하려면 Ctrl+C를 누르세요.
echo.

REM Docker 로그 확인
docker-compose logs -f

echo.
pause
goto :main_menu

:check_status
cls
echo [시작] 시스템 상태 확인 중...
echo.

REM Docker 컨테이너 상태 확인
docker-compose ps

echo.
echo [완료] 시스템 상태 확인이 완료되었습니다.
echo.
pause
goto :main_menu

REM =================================================
REM 데이터 수집 워크플로우 함수
REM =================================================

:start_news_collection
cls
echo [시작] 뉴스 데이터 수집 중...
echo.
echo 다양한 소스에서 뉴스 데이터를 수집합니다.
echo.

set /p topic="수집할 주제 (예: 정치, 경제, 기술): "
set /p time_range="시간 범위 (시간 단위, 기본값: 24): "

if "%time_range%"=="" set "time_range=24"

REM API 호출하여 뉴스 수집 시작
echo.
echo [API 호출] 뉴스 수집 요청 중...
echo.
curl -X POST "%API_ENDPOINT%/api/agents/alpha/collect-news" ^
     -H "Content-Type: application/json" ^
     -d "{\"topic\":\"%topic%\",\"time_range\":%time_range%}"

echo.
echo [완료] 뉴스 데이터 수집 요청이 완료되었습니다.
echo 결과는 '수집된 데이터 확인' 메뉴에서 확인할 수 있습니다.
echo.
pause
goto :main_menu

:view_collected_data
cls
echo [시작] 수집된 데이터 확인 중...
echo.

REM API 호출하여 수집된 데이터 확인
echo [API 호출] 수집된 데이터 요청 중...
echo.
curl -X GET "%API_ENDPOINT%/api/agents/alpha/collected-news"

echo.
echo [완료] 수집된 데이터 확인이 완료되었습니다.
echo.
pause
goto :main_menu

REM =================================================
REM 주제 분석 워크플로우 함수
REM =================================================

:start_topic_analysis
cls
echo [시작] 주제 분석 및 클러스터링 중...
echo.

REM API 호출하여 주제 분석 시작
echo [API 호출] 주제 분석 요청 중...
echo.
curl -X POST "%API_ENDPOINT%/api/agents/alpha/analyze-topics" ^
     -H "Content-Type: application/json" ^
     -d "{\"analysis_type\":\"clustering\"}"

echo.
echo [완료] 주제 분석 요청이 완료되었습니다.
echo.
pause
goto :main_menu

:run_political_analysis
cls
echo [시작] 정치 성향 분석 중...
echo.

set /p topic_id="분석할 주제 ID: "

REM API 호출하여 정치 성향 분석 시작
echo [API 호출] 정치 성향 분석 요청 중...
echo.
curl -X POST "%API_ENDPOINT%/api/agents/alpha/analyze-topics" ^
     -H "Content-Type: application/json" ^
     -d "{\"topic_id\":\"%topic_id%\",\"analysis_type\":\"political_bias\"}"

echo.
echo [완료] 정치 성향 분석 요청이 완료되었습니다.
echo.
pause
goto :main_menu

:run_mz_analysis
cls
echo [시작] MZ 세대 관심도 분석 중...
echo.

set /p topic_id="분석할 주제 ID: "

REM API 호출하여 MZ 세대 관심도 분석 시작
echo [API 호출] MZ 세대 관심도 분석 요청 중...
echo.
curl -X POST "%API_ENDPOINT%/api/agents/alpha/analyze-topics" ^
     -H "Content-Type: application/json" ^
     -d "{\"topic_id\":\"%topic_id%\",\"analysis_type\":\"mz_relevance\"}"

echo.
echo [완료] MZ 세대 관심도 분석 요청이 완료되었습니다.
echo.
pause
goto :main_menu

REM =================================================
REM 콘텐츠 생성 워크플로우 함수
REM =================================================

:generate_standard_article
cls
echo [시작] 표준 기사 생성 중...
echo.

set /p topic_id="기사 생성할 주제 ID: "

REM API 호출하여 표준 기사 생성 시작
echo [API 호출] 표준 기사 생성 요청 중...
echo.
curl -X POST "%API_ENDPOINT%/api/agents/alpha/generate-content" ^
     -H "Content-Type: application/json" ^
     -d "{\"topic_id\":\"%topic_id%\",\"format_type\":\"standard\"}"

echo.
echo [완료] 표준 기사 생성 요청이 완료되었습니다.
echo.
pause
goto :main_menu

:generate_mz_content
cls
echo [시작] MZ 세대 타겟 콘텐츠 생성 중...
echo.

set /p topic_id="콘텐츠 생성할 주제 ID: "

REM API 호출하여 MZ 세대 타겟 콘텐츠 생성 시작
echo [API 호출] MZ 세대 타겟 콘텐츠 생성 요청 중...
echo.
curl -X POST "%API_ENDPOINT%/api/agents/alpha/generate-content" ^
     -H "Content-Type: application/json" ^
     -d "{\"topic_id\":\"%topic_id%\",\"format_type\":\"mz\"}"

echo.
echo [완료] MZ 세대 타겟 콘텐츠 생성 요청이 완료되었습니다.
echo.
pause
goto :main_menu

:generate_youtube_script
cls
echo [시작] 유튜브 스크립트 생성 중...
echo.

set /p topic_id="스크립트 생성할 주제 ID: "
set /p script_type="스크립트 유형 (short/long/deep): "

REM API 호출하여 유튜브 스크립트 생성 시작
echo [API 호출] 유튜브 스크립트 생성 요청 중...
echo.
curl -X POST "%API_ENDPOINT%/api/agents/alpha/generate-content" ^
     -H "Content-Type: application/json" ^
     -d "{\"topic_id\":\"%topic_id%\",\"format_type\":\"youtube\",\"parameters\":{\"script_type\":\"%script_type%\"}}"

echo.
echo [완료] 유튜브 스크립트 생성 요청이 완료되었습니다.
echo.
pause
goto :main_menu

REM =================================================
REM 팩트체크 및 검증 워크플로우 함수
REM =================================================

:run_factcheck
cls
echo [시작] 팩트체크 실행 중...
echo.

set /p content_id="팩트체크할 콘텐츠 ID: "

REM API 호출하여 팩트체크 시작
echo [API 호출] 팩트체크 요청 중...
echo.
curl -X POST "%API_ENDPOINT%/api/agents/alpha/factcheck" ^
     -H "Content-Type: application/json" ^
     -d "{\"content_id\":\"%content_id%\"}"

echo.
echo [완료] 팩트체크 요청이 완료되었습니다.
echo.
pause
goto :main_menu

:verify_content
cls
echo [시작] 콘텐츠 품질 검증 중...
echo.

set /p content_id="검증할 콘텐츠 ID: "

REM API 호출하여 콘텐츠 품질 검증 시작
echo [API 호출] 콘텐츠 품질 검증 요청 중...
echo.
curl -X POST "%API_ENDPOINT%/api/agents/alpha/verify-content" ^
     -H "Content-Type: application/json" ^
     -d "{\"content_id\":\"%content_id%\"}"

echo.
echo [완료] 콘텐츠 품질 검증 요청이 완료되었습니다.
echo.
pause
goto :main_menu

REM =================================================
REM 유틸리티 함수
REM =================================================

:set_api_key
cls
echo [시작] API 키 설정 중...
echo.
echo 현재 API 키: %API_KEY%
echo.

set /p new_api_key="새 API 키 입력 (변경하지 않으려면 그냥 Enter): "

if not "%new_api_key%"=="" (
    echo GEMINI_API_KEY=%new_api_key% > .env
    echo.
    echo [완료] API 키가 업데이트되었습니다.
) else (
    echo.
    echo [취소] API 키 변경이 취소되었습니다.
)
echo.
pause
goto :main_menu

:setup_alpha_agent
cls
echo [시작] 빠른 알파 에이전트 설정 중...
echo.
echo 알파 에이전트를 기본 설정으로 빠르게 구성합니다.
echo.

REM API 호출하여 알파 에이전트 빠른 설정 시작
echo [API 호출] 알파 에이전트 설정 요청 중...
echo.
curl -X POST "%API_ENDPOINT%/api/agents/quick-setup-alpha"

echo.
echo [완료] 알파 에이전트 설정 요청이 완료되었습니다.
echo.
pause
goto :main_menu

:github_backup
cls
echo [시작] GitHub 백업 (v0.19) 중...
echo.
echo 오비스 프로젝트를 GitHub에 v0.19 버전으로 백업합니다.
echo.

REM PowerShell 스크립트 실행
powershell -ExecutionPolicy Bypass -File .\scripts\github-backup.ps1

echo.
echo [완료] GitHub 백업 작업이 완료되었습니다.
echo.
pause
goto :main_menu

:exit
cls
echo 오비스 워크플로우 관리자를 종료합니다.
echo 감사합니다!
timeout /t 2 > nul
exit /b 0 