@echo off
setlocal

REM OVIS 프론트엔드 실행 스크립트
echo OVIS 프론트엔드를 시작합니다...

REM 환경 변수 설정
set REACT_APP_API_URL=http://localhost:3002/api/v1
set NODE_ENV=development
set PORT=3000
set WDS_SOCKET_PORT=0
set DANGEROUSLY_DISABLE_HOST_CHECK=true
set FAST_REFRESH=false
set BROWSER=none

REM 프론트엔드 디렉토리로 이동
cd ovis-core

REM Node.js 버전 확인
echo Node.js 버전:
node -v
echo NPM 버전:
npm -v

REM 패키지 설치
echo 의존성 패키지를 설치합니다...
call npm install --legacy-peer-deps

REM 프론트엔드 서버 실행
echo 프론트엔드 개발 서버를 시작합니다...
call npm start

echo OVIS 프론트엔드가 종료되었습니다.
endlocal 