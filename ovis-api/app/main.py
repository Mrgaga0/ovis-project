from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os
from pathlib import Path
from typing import List, Dict, Any

# 로깅 설정
from .utils.logger import setup_logger
logger = setup_logger()

# 내부 모듈 임포트
from .config import get_settings
from .routers import agents, nas, logs
from .core.nas_manager import NASManager
from .models.agent import AgentStatus

# 환경 설정 로드
settings = get_settings()

# API 경로 확인 및 표준화
API_PREFIX = "/api/v1"  # 명시적으로 설정

# FastAPI 앱 초기화
app = FastAPI(
    title="OVIS API",
    description="개인화 AI 에이전트 시스템 API",
    version="0.1.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 오리진 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록 - 명시적 경로 사용
app.include_router(agents.router, prefix=f"{API_PREFIX}/agents", tags=["agents"])
app.include_router(nas.router, prefix=f"{API_PREFIX}/nas", tags=["nas"])
app.include_router(logs.router, prefix=f"{API_PREFIX}/logs", tags=["logs"])

# NAS 관리자 초기화
nas_manager = NASManager(settings.nas.path, settings.nas.directory_structure)

@app.on_event("startup")
async def startup_event():
    """앱 시작 시 실행되는 이벤트 핸들러"""
    logger.info("OVIS API 서버 시작 중...")
    
    # NAS 연결 확인
    if await nas_manager.check_connection():
        logger.info(f"NAS 연결 성공: {settings.nas.path}")
    else:
        logger.warning(f"NAS 연결 실패: {settings.nas.path}. 경로가 올바른지 확인하세요.")
    
    # 시스템 초기화
    try:
        await nas_manager.init_directories()
        logger.info("시스템 초기화 완료")
    except Exception as e:
        logger.error(f"시스템 초기화 중 오류 발생: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """앱 종료 시 실행되는 이벤트 핸들러"""
    logger.info("OVIS API 서버 종료 중...")
    # 리소스 정리

@app.get("/")
async def root():
    """API 루트 경로 - 명확한 응답 제공"""
    return {
        "message": "OVIS API 서버가 실행 중입니다",
        "version": settings.app.version,
        "docs_url": "/docs",
        "api_prefix": API_PREFIX
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트 - 컨테이너 상태 확인용"""
    return {"status": "ok"}

@app.get(f"{API_PREFIX}")
async def api_root():
    """API 기본 경로"""
    return {
        "message": "OVIS API가 실행 중입니다",
        "endpoints": [
            f"{API_PREFIX}/agents",
            f"{API_PREFIX}/nas",
            f"{API_PREFIX}/logs",
            f"{API_PREFIX}/status",
            f"{API_PREFIX}/system/info"
        ]
    }

@app.get(f"{API_PREFIX}/status")
async def get_status():
    """시스템 상태 정보 반환"""
    return {
        "status": "running",
        "version": settings.app.version,
        "environment": settings.app.environment,
        "nas_connected": await nas_manager.check_connection(),
        "available_agents": settings.agents.available
    }

@app.get(f"{API_PREFIX}/system/info")
async def get_system_info():
    """시스템 정보 반환"""
    return {
        "app_info": {
            "name": settings.app.name,
            "version": settings.app.version,
            "environment": settings.app.environment
        },
        "nas_info": {
            "path": settings.nas.path,
            "connected": await nas_manager.check_connection(),
            "available_space": await nas_manager.get_available_space()
        },
        "agent_info": {
            "available": settings.agents.available,
            "default": settings.agents.default
        }
    }

# 기본 Alpha 에이전트 테스트 엔드포인트 추가
@app.get(f"{API_PREFIX}/agents/alpha")
async def alpha_agent_info():
    """Alpha 에이전트 정보 반환 - 테스트용"""
    return {
        "id": "alpha-default",
        "name": "Alpha Agent",
        "type": "alpha",
        "status": "active",
        "description": "기본 알파 에이전트",
        "version": "0.19"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=3002, reload=True) 