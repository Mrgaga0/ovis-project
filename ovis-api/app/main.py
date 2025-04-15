import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 라우터 임포트 - 하나씩 추가
from app.routers import agents
from app.routers import workflows
from app.routers import models
from app.routers import nas
from app.routers import logs

# API 프리픽스 설정
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")

# FastAPI 앱 초기화
app = FastAPI(
    title="OVIS API",
    description="오비스 AI 에이전트 시스템 API",
    version="0.1.0",
)

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)
logger.info("OVIS API 서버 시작 중...")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록 - 한 번에 하나씩 추가
app.include_router(agents.router, prefix=f"{API_PREFIX}/agents", tags=["agents"])
app.include_router(workflows.router, prefix=f"{API_PREFIX}/workflows", tags=["workflows"])
app.include_router(models.router, prefix=f"{API_PREFIX}/models", tags=["models"])
app.include_router(nas.router, prefix=f"{API_PREFIX}/nas", tags=["nas"])
app.include_router(logs.router, prefix=f"{API_PREFIX}/logs", tags=["logs"])

# 헬스체크 엔드포인트
@app.get("/health")
async def health_check():
    logger.info("헬스체크 호출됨")
    return {"status": "ok"}

# 기본 경로 설정
@app.get("/")
async def read_root():
    logger.info("루트 경로 호출됨")
    return {"message": "OVIS API 서버가 실행 중입니다"}

# API 기본 경로 정보
@app.get(f"{API_PREFIX}")
async def api_root():
    logger.info("API 루트 경로 호출됨")
    return {
        "service": "OVIS API",
        "version": "0.1.0",
        "status": "online",
        "api_prefix": API_PREFIX,
    }

# 상태 정보 엔드포인트
@app.get(f"{API_PREFIX}/status")
async def status():
    logger.info("상태 엔드포인트 호출됨")
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
        content={"detail": "서버 내부 오류가 발생했습니다"},
    )