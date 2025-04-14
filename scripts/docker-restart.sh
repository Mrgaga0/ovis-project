#!/bin/bash

# Docker 컨테이너 중지
echo "도커 컨테이너 중지 중..."
docker-compose down

# Docker 이미지 재빌드
echo "도커 이미지 재빌드 중..."
docker-compose build

# Docker 컨테이너 시작
echo "도커 컨테이너 시작 중..."
docker-compose up -d

# 로그 확인 (선택 사항)
echo "컨테이너 로그 확인 중..."
docker-compose logs -f 