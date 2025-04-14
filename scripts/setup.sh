#!/bin/bash

# OVIS 초기 설정 스크립트
# 시스템을 설정하고 필요한 디렉토리 및 파일을 준비합니다.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
NAS_MOCK_DIR="$PROJECT_ROOT/nas-mock"
CONFIG_DIR="$PROJECT_ROOT/config"
LOGS_DIR="$PROJECT_ROOT/logs"

echo "OVIS 설정을 시작합니다..."

# 필요한 디렉토리 생성
echo "기본 디렉토리를 생성합니다..."
mkdir -p "$LOGS_DIR"

# NAS 가상 디렉토리 설정 (실제 NAS가 없을 때)
if [ ! -d "$NAS_MOCK_DIR" ]; then
  echo "NAS 가상 디렉토리를 생성합니다..."
  mkdir -p "$NAS_MOCK_DIR/models/alpha"
  mkdir -p "$NAS_MOCK_DIR/models/beta"
  mkdir -p "$NAS_MOCK_DIR/models/theta"
  mkdir -p "$NAS_MOCK_DIR/data/shared"
  mkdir -p "$NAS_MOCK_DIR/data/agent-specific"
  mkdir -p "$NAS_MOCK_DIR/logs"
  
  # 빈 모델 파일 생성 (실제 모델 없이 구조만)
  touch "$NAS_MOCK_DIR/models/alpha/model.placeholder"
  touch "$NAS_MOCK_DIR/models/beta/model.placeholder"
  touch "$NAS_MOCK_DIR/models/theta/model.placeholder"
  
  echo "NAS 가상 디렉토리가 설정되었습니다: $NAS_MOCK_DIR"
fi

# 로컬 설정 파일 생성 (없을 경우)
if [ ! -f "$CONFIG_DIR/local.json" ]; then
  echo "로컬 설정 파일을 생성합니다..."
  cp "$CONFIG_DIR/local.json.example" "$CONFIG_DIR/local.json"
  
  # NAS 경로 설정 (자동)
  sed -i "s|/path/to/your/nas/mount|$NAS_MOCK_DIR|g" "$CONFIG_DIR/local.json"
  
  echo "로컬 설정 파일이 생성되었습니다: $CONFIG_DIR/local.json"
fi

# 환경 변수 파일 생성
if [ ! -f "$PROJECT_ROOT/.env" ]; then
  echo "환경 변수 파일을 생성합니다..."
  cat > "$PROJECT_ROOT/.env" << EOF
# OVIS 환경 변수
NODE_ENV=development
NAS_PATH=$NAS_MOCK_DIR
EOF
  echo "환경 변수 파일이 생성되었습니다: $PROJECT_ROOT/.env"
fi

echo "설정이 완료되었습니다!"
echo "다음 명령으로 시스템을 실행할 수 있습니다: docker-compose up -d" 