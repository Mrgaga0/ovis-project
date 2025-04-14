@echo off
echo Ovis 프로그램 강제 업데이트 시작...

cd G:\#7_ovis\ovis-project

echo 이전 컨테이너 중지 및 볼륨 제거 중...
docker-compose down -v

echo Docker 이미지 캐시 초기화 중...
docker builder prune -f

echo 새 이미지 강제 빌드 중...
docker-compose build --no-cache

echo 새 컨테이너 시작 중...
docker-compose up -d

echo 업데이트 완료!
echo 로그 확인: docker-compose logs -f