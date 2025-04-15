import os
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from app.routers import agents, workflows, models, nas, logs

# API 프리픽스 설정
API_PREFIX = os.getenv("API_PREFIX", "api/v1")

# FastAPI 앱 초기화
app = FastAPI(
    title="OVIS API",
    description="오비스 AI 에이전트 시스템 API",
    version="0.1.0",
)

# CORS 설정 개선
origins_str = os.getenv("CORS_ORIGINS", "http://localhost:8080,http://localhost:8001,http://localhost:3000,*")
origins = origins_str.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/api.log")
    ]
)
logger = logging.getLogger(__name__)

# 요청 로깅 미들웨어
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url}")
        try:
            response = await call_next(request)
            logger.info(f"Response: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            raise

app.add_middleware(RequestLoggingMiddleware)

# 라우터 등록 - API 프리픽스 없이 등록 (Nginx에서 처리)
app.include_router(agents.router, prefix="/agents", tags=["에이전트"])
app.include_router(workflows.router, prefix="/workflows", tags=["워크플로우"])
app.include_router(models.router, prefix="/models", tags=["모델"])
app.include_router(nas.router, prefix="/nas", tags=["저장소"])
app.include_router(logs.router, prefix="/logs", tags=["로그"])

# 정적 파일 서비스 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# 헬스체크 엔드포인트
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# 기본 경로 설정
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <html>
        <head>
            <title>OVIS API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                a { color: #0066cc; }
            </style>
        </head>
        <body>
            <h1>OVIS API 서비스</h1>
            <p>이 서비스는 오비스 AI 에이전트 시스템의 백엔드 API입니다.</p>
            <p><a href="/docs">API 문서 보기</a></p>
        </body>
    </html>
    """

# 상태 정보 엔드포인트
@app.get("/status")
async def status():
    return {
        "service": "OVIS API",
        "version": "0.1.0",
        "status": "online",
        "api_prefix": API_PREFIX,
    }

# 예외 핸들러
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "서버 내부 오류가 발생했습니다."},
    )