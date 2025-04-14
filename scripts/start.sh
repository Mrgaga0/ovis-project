#!/bin/bash

# OVIS 시작 스크립트
# 백엔드 및 프론트엔드 서비스를 모두 시작합니다.

set -e

# 환경 변수 설정
export PYTHONPATH=/app
export OVIS_CONFIG=${OVIS_CONFIG:-/app/config/local.json}

echo "OVIS 시스템을 시작합니다..."

# NAS 마운트 확인
if [ ! -d "/nas-mount" ]; then
  echo "경고: NAS 마운트 디렉토리가 없습니다. Docker 볼륨이 올바르게 설정되었는지 확인하세요."
  mkdir -p /nas-mount
fi

# NAS 접근 가능 여부 테스트
echo "NAS 접근 테스트 중..."
if touch /nas-mount/test_access && rm /nas-mount/test_access; then
  echo "NAS 접근 성공!"
else
  echo "경고: NAS에 쓰기 권한이 없습니다. 읽기 전용으로 계속합니다."
fi

# 백그라운드에서 API 서버 시작
echo "백엔드 API 서버 시작 중..."
cd /app/api && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 &
API_PID=$!

# 프론트엔드 앱 시작 (개발 모드 또는 프로덕션 모드)
if [ "$NODE_ENV" = "development" ]; then
  echo "프론트엔드 개발 서버 시작 중..."
  cd /app/frontend && npm run dev &
  FRONTEND_PID=$!
else
  echo "프론트엔드 프로덕션 서버 시작 중..."
  cd /app/frontend && npm run start &
  FRONTEND_PID=$!
fi

# 서비스 상태 모니터링
echo "모든 서비스가 시작되었습니다."
echo "API 서버: PID $API_PID - 포트 8000"
echo "프론트엔드: PID $FRONTEND_PID - 포트 3000"

# 종료 핸들러
function handle_exit {
  echo "종료 신호를 수신했습니다. 서비스를 정상 종료합니다..."
  kill -SIGTERM $API_PID 2>/dev/null || true
  kill -SIGTERM $FRONTEND_PID 2>/dev/null || true
  wait
  echo "모든 서비스가 종료되었습니다."
  exit 0
}

# 종료 신호 처리
trap handle_exit SIGINT SIGTERM

# 메인 프로세스 유지
wait 