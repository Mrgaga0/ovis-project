#!/bin/bash

# OVIS 시스템 통합 실행 스크립트 (Linux/macOS용)
echo "OVIS 시스템을 시작합니다..."

# 백엔드 실행 스크립트
cat > run-backend.sh << 'EOF'
#!/bin/bash

# OVIS 백엔드 서버 실행 스크립트
echo "OVIS 백엔드 서버를 시작합니다..."

# 환경 변수 설정
export PYTHONPATH=$(pwd)
export ENVIRONMENT=development
export DATABASE_URL=sqlite:///data/ovis.db
export LOG_LEVEL=debug
export PORT=3002
export HOST=0.0.0.0
export API_PREFIX=/api/v1
export CORS_ORIGINS=*

# .env 파일에서 GEMINI_API_KEY 로드
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "API 키: $GEMINI_API_KEY"

# 필요한 디렉토리 생성
mkdir -p data logs ovis_save

# 가상환경 활성화 (존재한다면)
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "가상환경이 없습니다. Python이 시스템 경로에 있어야 합니다."
fi

# 필요한 패키지 설치
pip install -r ovis-api/requirements.txt

# 백엔드 서버 실행
cd ovis-api
python -m uvicorn app.main:app --host $HOST --port $PORT --reload --log-level $LOG_LEVEL

# 가상환경 비활성화
if [ -d "venv" ]; then
    deactivate
fi

echo "OVIS 백엔드 서버가 종료되었습니다."
EOF

# 프론트엔드 실행 스크립트
cat > run-frontend.sh << 'EOF'
#!/bin/bash

# OVIS 프론트엔드 실행 스크립트
echo "OVIS 프론트엔드를 시작합니다..."

# 환경 변수 설정
export REACT_APP_API_URL=http://localhost:3002/api/v1
export NODE_ENV=development
export PORT=3000
export WDS_SOCKET_PORT=0
export DANGEROUSLY_DISABLE_HOST_CHECK=true
export FAST_REFRESH=false
export BROWSER=none

# 프론트엔드 디렉토리로 이동
cd ovis-core

# Node.js 버전 확인
echo "Node.js 버전:"
node -v
echo "NPM 버전:"
npm -v

# 패키지 설치
echo "의존성 패키지를 설치합니다..."
npm install --legacy-peer-deps

# 프론트엔드 서버 실행
echo "프론트엔드 개발 서버를 시작합니다..."
npm start

echo "OVIS 프론트엔드가 종료되었습니다."
EOF

# 스크립트 실행 권한 추가
chmod +x run-backend.sh
chmod +x run-frontend.sh

# 백엔드와 프론트엔드를 병렬로 실행
echo "두 개의 터미널 창이 열립니다."
echo "첫 번째 창에서는 백엔드가 실행됩니다."
echo "두 번째 창에서는 프론트엔드가 실행됩니다."
echo ""
echo "시스템을 종료하려면 각 창을 닫으세요."
echo ""
sleep 3

# 운영체제 확인 및 터미널 명령 선택
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open -a Terminal.app run-backend.sh
    sleep 5
    open -a Terminal.app run-frontend.sh
else
    # Linux
    gnome-terminal -- ./run-backend.sh || xterm -e ./run-backend.sh || konsole -e ./run-backend.sh || echo "백엔드 실행 실패: 터미널 프로그램을 찾을 수 없습니다."
    sleep 5
    gnome-terminal -- ./run-frontend.sh || xterm -e ./run-frontend.sh || konsole -e ./run-frontend.sh || echo "프론트엔드 실행 실패: 터미널 프로그램을 찾을 수 없습니다."
fi

# 브라우저 열기
sleep 10
echo "브라우저를 엽니다..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:3000
else
    xdg-open http://localhost:3000 || echo "브라우저를 열 수 없습니다. http://localhost:3000 으로 접속하세요."
fi

echo ""
echo "OVIS 시스템 시작 완료!"
echo "백엔드 API: http://localhost:3002/api/v1"
echo "프론트엔드: http://localhost:3000"
echo ""
echo "각 창을 닫아 종료하세요." 