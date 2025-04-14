#!/bin/bash

# OVIS 워크플로우 관리자 실행 스크립트 (Linux/macOS용)
echo "OVIS 워크플로우 관리자를 실행합니다..."

# 스크립트 위치로 디렉토리 변경
cd "$(dirname "$0")"

# 리눅스/macOS에서 워크플로우 매니저 실행
if [ -f "ovis-workflow.sh" ]; then
    # Linux/macOS 네이티브 스크립트가 있는 경우
    bash ./ovis-workflow.sh
elif command -v wine >/dev/null 2>&1; then
    # Wine이 설치되어 있는 경우 Windows 스크립트 실행
    wine cmd /c ovis-workflow.cmd
else
    # Docker 환경에서 실행 (fallback)
    echo "리눅스/macOS용 네이티브 스크립트가 없습니다."
    echo "Docker를 사용하여 실행합니다..."
    
    if command -v docker >/dev/null 2>&1; then
        docker-compose up -d
        echo "OVIS Docker 환경이 시작되었습니다."
        echo "웹 인터페이스: http://localhost:8080"
        echo "API 엔드포인트: http://localhost:528"
    else
        echo "오류: Docker가 설치되어 있지 않습니다."
        echo "Docker를 설치하거나 Windows 환경에서 실행해주세요."
        exit 1
    fi
fi 