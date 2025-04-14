#!/bin/bash

# 환경 설정
echo "오비스 알파 에이전트 시스템 구동 시작..."

# 필요한 디렉토리 생성
mkdir -p data logs nas-mount

# .env 파일 확인
if [ ! -f .env ]; then
    echo "GEMINI_API_KEY=" > .env
    echo ".env 파일을 생성했습니다. GEMINI_API_KEY 값을 설정해주세요."
    echo "예시: GEMINI_API_KEY=your-api-key-here"
    exit 1
fi

# GEMINI_API_KEY 확인
if grep -q "GEMINI_API_KEY=$" .env; then
    echo "GEMINI_API_KEY가 설정되지 않았습니다. .env 파일에 API 키를 입력해주세요."
    exit 1
fi

# 도커 컨테이너 빌드 및 실행
echo "Docker 컨테이너 빌드 및 시작..."
docker-compose up -d

# 상태 확인
echo "컨테이너 상태 확인..."
docker-compose ps

echo "시스템이 시작되었습니다."
echo "웹 인터페이스: http://localhost:8080"
echo "API 엔드포인트: http://localhost:528"
echo "로그 확인: docker-compose logs -f" 