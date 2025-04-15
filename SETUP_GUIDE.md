# OVIS 로컬 환경 설정 가이드

이 가이드는 OVIS 시스템을 Windows 환경에서 로컬로 설치하고 실행하기 위한 단계별 지침입니다.

## 필수 요구사항

1. **Python 3.9+** 
   - 다운로드: [Python 공식 웹사이트](https://www.python.org/downloads/)
   - 설치 시 "Add Python to PATH" 옵션을 체크해야 합니다.

2. **Node.js 16+** 
   - 다운로드: [Node.js 공식 웹사이트](https://nodejs.org/)
   - LTS 버전 권장

## 1단계: Python 설치 확인

명령 프롬프트(cmd)나 PowerShell에서 다음 명령을 실행하여 Python이 올바르게 설치되었는지 확인합니다:

```
python --version
```

버전이 3.9 이상이어야 합니다. Python이 설치되지 않은 경우 위의 링크에서 다운로드하여 설치하세요.

## 2단계: Node.js 설치 확인

다음 명령을 실행하여 Node.js가 올바르게 설치되었는지 확인합니다:

```
node --version
npm --version
```

Node.js는 16 이상, npm은 7 이상이 권장됩니다.

## 3단계: Python 가상환경 설정 (권장)

가상환경을 사용하면 프로젝트별로 독립된 Python 환경을 유지할 수 있습니다.

1. 프로젝트 루트 디렉토리로 이동합니다:
   ```
   cd ovis-project
   ```

2. 가상환경을 생성합니다:
   ```
   python -m venv venv
   ```

3. 가상환경을 활성화합니다:
   - Windows Command Prompt:
     ```
     venv\Scripts\activate
     ```
   - Windows PowerShell:
     ```
     .\venv\Scripts\Activate.ps1
     ```
     
   - 활성화된 경우 명령 프롬프트 앞에 (venv)가 표시됩니다.

## 4단계: 필수 Python 패키지 설치

백엔드에 필요한 모든 패키지를 설치합니다:

```
pip install -r ovis-api/requirements.txt
```

## 5단계: 프론트엔드 의존성 설치

프론트엔드 디렉토리로 이동하여 필요한 패키지를 설치합니다:

```
cd ovis-core
npm install --legacy-peer-deps
cd ..
```

## 6단계: 환경 변수 확인

`.env` 파일이 올바르게 설정되어 있는지 확인합니다. 최소한 다음 항목들이 포함되어야 합니다:

```
GEMINI_API_KEY=AIzaSyAfPLmxWaXYeIlgHzqIez3ly2xSpt79xo8
ENVIRONMENT=development
DATABASE_URL=sqlite:///data/ovis.db
PORT=3002
HOST=0.0.0.0
API_PREFIX=/api/v1
CORS_ORIGINS=*
```

## 7단계: 시스템 실행

이제 시스템을 실행할 수 있습니다:

### Windows에서 실행

1. 통합 실행 스크립트 사용 (백엔드와 프론트엔드를 함께 실행):
   ```
   .\run-ovis.bat
   ```

2. 또는 별도로 실행:
   - 백엔드 실행:
     ```
     .\run-backend.bat
     ```
   - 프론트엔드 실행:
     ```
     .\run-frontend.bat
     ```

## 실행 문제 해결

다음은 일반적인 문제와 해결책입니다:

### 1. Python이 설치되지 않았거나 PATH에 없는 경우

오류 메시지: "python은 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는 배치 파일이 아닙니다."

해결책:
- Python을 설치하고 PATH에 추가했는지 확인합니다.
- 설치 후 새 명령 프롬프트를 열어 다시 시도합니다.

### 2. 패키지 설치 오류

오류 메시지: "pip is not recognized..." 또는 "ERROR: Could not install packages..."

해결책:
- pip가 최신 버전인지 확인: `python -m pip install --upgrade pip`
- 관리자 권한으로 명령 프롬프트를 실행하여 다시 시도합니다.

### 3. 포트 충돌

오류 메시지: "Address already in use" 또는 "Port 3000 is already in use"

해결책:
- 다른 프로세스가 해당 포트를 사용 중인지 확인합니다:
  ```
  netstat -ano | findstr :3000   (프론트엔드 포트)
  netstat -ano | findstr :3002   (백엔드 포트)
  ```
- 해당 프로세스를 종료하거나 `.env` 파일에서 포트 번호를 변경합니다.

### 4. Node.js 관련 오류

오류 메시지: "npm WARN..." 또는 "Error: Cannot find module..."

해결책:
- Node.js가 올바르게 설치되어 있는지 확인합니다.
- `npm cache clean --force` 실행 후 다시 시도합니다.
- 프론트엔드 의존성을 다시 설치합니다: `npm install --legacy-peer-deps`

## 추가 지원

문제가 계속되면 개발팀에 문의하거나 이슈를 보고해 주세요. 