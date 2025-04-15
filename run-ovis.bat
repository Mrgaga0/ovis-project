@echo off
setlocal

REM OVIS 시스템 통합 실행 스크립트
echo OVIS 시스템을 시작합니다...

REM 백엔드와 프론트엔드를 병렬로 실행
echo 두 개의 명령 프롬프트 창이 열립니다.
echo 첫 번째 창에서는 백엔드가 실행됩니다.
echo 두 번째 창에서는 프론트엔드가 실행됩니다.
echo.
echo 시스템을 종료하려면 각 창을 닫으세요.
echo.
timeout /t 3

REM 백엔드 실행
start "OVIS 백엔드" cmd /k "run-backend.bat"

REM 잠시 대기 (백엔드가 시작할 시간을 줌)
timeout /t 5

REM 프론트엔드 실행
start "OVIS 프론트엔드" cmd /k "run-frontend.bat"

REM 브라우저 열기
timeout /t 10
echo 브라우저를 엽니다...
start http://localhost:3000

echo.
echo OVIS 시스템 시작 완료!
echo 백엔드 API: http://localhost:3002/api/v1
echo 프론트엔드: http://localhost:3000
echo.
echo 각 창을 닫아 종료하세요.

endlocal 