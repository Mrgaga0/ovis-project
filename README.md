# OVIS (Open Visual Intelligence System)

OVIS는 오픈 비주얼 인텔리전스 시스템으로, 다양한 AI 에이전트를 활용하여 시각적인 작업을 수행할 수 있는 플랫폼입니다.

## 시스템 요구사항

### 백엔드
- Python 3.9 이상
- pip 패키지 관리자
- 필요한 Python 라이브러리 (requirements.txt 참조)

### 프론트엔드
- Node.js 16 이상
- npm 패키지 관리자
- React 애플리케이션 실행에 필요한 패키지

## 설치 및 실행 방법

### Windows에서 실행하기

1. 레포지토리 복제:
   ```
   git clone https://github.com/yourusername/ovis.git
   cd ovis
   ```

2. 간편 실행 (통합 스크립트 사용):
   ```
   run-ovis.bat
   ```
   이 스크립트는 자동으로 백엔드와 프론트엔드 서버를 시작합니다.

3. 개별 실행:
   - 백엔드 서버 실행:
     ```
     run-backend.bat
     ```
   - 프론트엔드 서버 실행:
     ```
     run-frontend.bat
     ```

### Linux/macOS에서 실행하기

1. 레포지토리 복제:
   ```
   git clone https://github.com/yourusername/ovis.git
   cd ovis
   ```

2. 간편 실행 (통합 스크립트 사용):
   ```
   chmod +x run-ovis.sh
   ./run-ovis.sh
   ```

3. 개별 실행:
   - 실행 권한 부여:
     ```
     chmod +x run-backend.sh run-frontend.sh
     ```
   - 백엔드 서버 실행:
     ```
     ./run-backend.sh
     ```
   - 프론트엔드 서버 실행:
     ```
     ./run-frontend.sh
     ```

## 수동 설정 및 실행

### 백엔드 서버 (FastAPI)

1. 가상환경 생성 및 활성화 (선택사항):
   ```
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

2. 필요한 패키지 설치:
   ```
   pip install -r ovis-api/requirements.txt
   ```

3. 백엔드 서버 실행:
   ```
   cd ovis-api
   python -m uvicorn app.main:app --host 0.0.0.0 --port 3002 --reload
   ```

### 프론트엔드 서버 (React)

1. 필요한 패키지 설치:
   ```
   cd ovis-core
   npm install --legacy-peer-deps
   ```

2. 프론트엔드 개발 서버 실행:
   ```
   npm start
   ```

## 접속 방법

- 프론트엔드 웹 인터페이스: http://localhost:3000
- 백엔드 API: http://localhost:3002/api/v1
- API 문서: http://localhost:3002/docs

## 환경 변수 설정

.env 파일에 다음 환경 변수를 설정할 수 있습니다:

```
GEMINI_API_KEY=your-api-key  # Google Gemini API 키
ENVIRONMENT=development       # 개발 환경 설정
DATABASE_URL=sqlite:///data/ovis.db  # 데이터베이스 URL
LOG_LEVEL=debug              # 로깅 레벨
PORT=3002                    # 백엔드 서버 포트
HOST=0.0.0.0                 # 백엔드 서버 호스트
API_PREFIX=/api/v1           # API 경로 프리픽스
CORS_ORIGINS=*               # CORS 허용 오리진
```

## 프로젝트 구조

```
ovis-project/
├── ovis-api/            # 백엔드 API 서버 (FastAPI)
│   ├── app/
│   │   ├── routers/     # API 엔드포인트
│   │   ├── models/      # 데이터 모델
│   │   ├── core/        # 핵심 기능
│   │   └── main.py      # 메인 애플리케이션
│   └── requirements.txt # 백엔드 의존성
├── ovis-core/           # 프론트엔드 (React)
│   ├── public/          # 정적 파일
│   ├── src/             # 소스 코드
│   │   ├── components/  # React 컴포넌트
│   │   ├── pages/       # 페이지 컴포넌트
│   │   ├── utils/       # 유틸리티 함수
│   │   └── App.tsx      # 메인 앱 컴포넌트
│   └── package.json     # 프론트엔드 의존성
├── data/                # 데이터 저장소
├── logs/                # 로그 파일
├── config/              # 설정 파일
├── ovis_save/           # NAS 마운트 지점
├── .env                 # 환경 변수
├── run-ovis.bat         # Windows 통합 실행 스크립트
├── run-backend.bat      # Windows 백엔드 실행 스크립트
├── run-frontend.bat     # Windows 프론트엔드 실행 스크립트
├── run-ovis.sh          # Linux/macOS 통합 실행 스크립트
└── README.md            # 이 파일
```

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