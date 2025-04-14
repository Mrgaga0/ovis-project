# 오비스 프로젝트 (OVIS Project) v0.19

오비스는 AI 기반 에이전트를 통해 뉴스 수집, 분석 및 콘텐츠 생성을 자동화하는 시스템입니다.

## 버전 정보

**현재 버전: v0.19**
- 알파 에이전트 핵심 기능 구현
- Docker 환경 최적화
- NAS 연결 지원
- Gemini 2.0 API 통합
- CLI 기반 워크플로우 관리자 추가

## 주요 기능

- 다양한 소스에서 뉴스 자동 수집
- AI 기반 주제 분석 및 클러스터링
- 다양한 형식의 콘텐츠 생성 (기사, MZ 콘텐츠, 유튜브 스크립트)
- 사용자 친화적인 대시보드 및 편집 인터페이스
- 통합 워크플로우 관리자로 전체 프로세스 실행 및 관리

## 시스템 요구사항

- Node.js 16.x 이상
- Python 3.9 이상
- Docker (선택 사항)

## 워크플로우 관리자 사용하기

### Windows에서 실행

```
# 프로젝트 루트 디렉토리에서 다음 파일 실행
run-ovis.bat
```

### Linux/macOS에서 실행

```
# 프로젝트 루트 디렉토리에서 다음 명령 실행
chmod +x run-ovis.sh
./run-ovis.sh
```

워크플로우 관리자에 대한 자세한 내용은 [워크플로우 가이드](docs/workflow-guide.md)를 참조하세요.

## Docker로 실행하기

### 사전 준비

Docker와 Docker Compose가 설치되어 있어야 합니다.

### 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가합니다:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

### 간편 실행 (PowerShell)

```powershell
# 프로젝트 디렉토리로 이동
cd ovis-project

# 자동 설정 및 실행 스크립트 실행
.\scripts\docker-start.ps1
```

### 수동 실행

1. 프로젝트 루트 디렉토리에서 다음 명령을 실행합니다:

```bash
docker-compose up -d
```

2. 브라우저에서 `http://localhost:8080`로 접속합니다.

### 컨테이너 상태 확인

```bash
docker-compose ps
```

### 로그 확인

```bash
docker-compose logs -f
```

### 컨테이너 중지

```bash
docker-compose down
```

## 로컬에서 직접 실행하기

### 백엔드 설치 및 실행

1. 필요한 패키지 설치:
```bash
cd ovis-api
pip install -r requirements.txt
```

2. 서버 실행:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 528 --reload
```

### 프론트엔드 설치 및 실행

1. 필요한 패키지 설치:
```bash
cd ovis-core
npm install
```

2. 개발 서버 실행:
```bash
npm run dev
```

3. 브라우저에서 `http://localhost:3000`으로 접속

## API 문서

API 문서는 서버 실행 후 `http://localhost:528/docs`에서 확인할 수 있습니다.

## 주요 기능

- 다양한 특화된 AI 에이전트 관리 및 실행 (알파, 베타, 세타 등)
- NAS 기반 데이터 저장 및 모델 관리
- 상세한 로깅 및 모니터링 시스템
- AI 에이전트 맞춤 파인튜닝 시스템
- Docker 기반 모듈식 아키텍처

## 시스템 아키텍처

OVIS는 다음 주요 모듈로 구성됩니다:
```
OVIS 시스템
├── 메인 인터페이스 (AI 선택 허브)
├── 개별 AI 에이전트 모듈 (알파, 베타, 세타 등)
├── AI 관리 & 파인튜닝 모듈
├── 로깅 & 모니터링 시스템
└── 데이터 저장 & 동기화 모듈 (NAS 연결)
```

## 기술 스택

- **프론트엔드**: React, TypeScript, Redux, Ant Design, Electron
- **백엔드**: FastAPI, SQLAlchemy, Python
- **컨테이너화**: Docker, Docker Compose
- **데이터 관리**: NAS/파일 시스템 연동

## 라이센스

이 프로젝트는 비공개 소프트웨어로, 저작권자의 명시적 허가 없이 사용, 복제, 수정이 금지됩니다. 