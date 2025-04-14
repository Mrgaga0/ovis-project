#!/bin/bash

# 스크립트 시작 메시지
echo "오비스 프로젝트를 GitHub에 v0.19 버전으로 백업합니다..."

# 비공개 API 키 제거
echo "민감한 정보 제거 중..."
sed -i 's/GEMINI_API_KEY="[^"]*"/GEMINI_API_KEY=""/' Dockerfile

# Git 저장소 초기화 (필요한 경우)
if [ ! -d .git ]; then
    echo "Git 저장소 초기화 중..."
    git init
    
    # .gitignore 파일 생성
    if [ ! -f .gitignore ]; then
        echo "기본 .gitignore 파일 생성 중..."
        cat > .gitignore << EOF
# 환경 변수 및 비밀 정보
.env

# 데이터 및 로그 파일
/data/
/logs/
/nas-mount/

# 시스템 및 임시 파일
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.DS_Store
node_modules/
npm-debug.log
yarn-debug.log
yarn-error.log
.npm/
.eslintcache
EOF
    fi
fi

# GitHub 원격 저장소 확인 및 추가
if ! git remote | grep -q origin; then
    echo "GitHub 원격 저장소 URL을 입력하세요 (예: https://github.com/username/ovis-project.git):"
    read github_url
    
    if [ -z "$github_url" ]; then
        echo "유효한 URL이 입력되지 않았습니다. 스크립트를 종료합니다."
        exit 1
    fi
    
    echo "GitHub 원격 저장소 추가 중..."
    git remote add origin $github_url
fi

# 변경사항 스테이징 및 커밋
echo "변경사항 스테이징 중..."
git add .

echo "변경사항 커밋 중..."
git commit -m "OVIS Project v0.19 - Docker 환경 최적화 및 알파 에이전트 기능 구현"

# 태그 생성
echo "v0.19 태그 생성 중..."
git tag -a v0.19 -m "OVIS Project 버전 0.19 - 알파 에이전트 Docker 환경 구현"

# GitHub에 푸시
echo "GitHub에 변경사항 푸시 중..."
git push -u origin master

# 태그 푸시
echo "태그 푸시 중..."
git push origin v0.19

echo "백업이 완료되었습니다!"
echo "OVIS 프로젝트 v0.19이 GitHub에 성공적으로 백업되었습니다." 