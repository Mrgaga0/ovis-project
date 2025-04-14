# OVIS Core

OVIS 시스템의 핵심 UI 및 Electron 데스크톱 애플리케이션입니다.

## 주요 기능

- 다양한 AI 에이전트 관리 및 실행
- NAS 기반 데이터 저장 및 모델 관리
- 상세한 로깅 및 모니터링 시스템
- 직관적인 사용자 인터페이스

## 기술 스택

- React + TypeScript
- Redux (Redux Toolkit)
- Ant Design
- Electron
- 백엔드 연결: FastAPI

## 시작하기

### 개발 환경 설정

1. 저장소 클론 및 의존성 설치:
```bash
git clone https://github.com/yourusername/ovis-project.git
cd ovis-project/ovis-core
npm install
```

2. 개발 모드 실행 (React):
```bash
npm start
```

3. 개발 모드 실행 (Electron + React):
```bash
npm run electron-dev
```

### 배포용 빌드 생성

```bash
npm run build
npm run package
```

## 프로젝트 구조

```
ovis-core/
  ├── public/             # 정적 파일
  │   ├── electron.js     # Electron 메인 프로세스
  │   └── preload.js      # Electron 프리로드 스크립트
  ├── src/
  │   ├── components/     # 재사용 가능한 컴포넌트
  │   ├── pages/          # 페이지 컴포넌트
  │   ├── store/          # Redux 스토어 및 슬라이스
  │   ├── utils/          # 유틸리티 함수
  │   ├── App.tsx         # 메인 앱 컴포넌트
  │   └── index.tsx       # 앱 진입점
  ├── package.json        # 의존성 및 스크립트
  └── tsconfig.json       # TypeScript 설정
```

## 백엔드 연결

OVIS Core는 FastAPI 백엔드와 통신합니다. 기본적으로 `http://localhost:8000`에 연결됩니다. API URL은 애플리케이션 설정에서 변경할 수 있습니다.

## NAS 연결

NAS 경로는 설정에서 지정할 수 있습니다. NAS는 모델, 데이터 및 로그 파일을 저장하는 데 사용됩니다.

## 에이전트 관리

다양한 AI 에이전트를 관리하고 실행할 수 있습니다. 각 에이전트는 고유한 기능과 구성을 가질 수 있습니다. 