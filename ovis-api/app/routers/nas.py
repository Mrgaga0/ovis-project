from fastapi import APIRouter, HTTPException, Depends, Path, Query, UploadFile, File
from fastapi.responses import Response
from typing import List, Dict, Any, Optional
import os
from pathlib import Path

from ..config import get_settings
from ..core.nas_manager import NASManager

router = APIRouter()
settings = get_settings()

# NAS 경로와 디렉토리 구조로 NAS 관리자 초기화
nas_manager = NASManager(settings.nas.path, settings.nas.directory_structure)

@router.get("/status")
async def get_nas_status():
    """NAS 연결 상태 확인"""
    is_connected = await nas_manager.check_connection()
    available_space = await nas_manager.get_available_space() if is_connected else "Unknown"
    
    return {
        "connected": is_connected,
        "path": str(nas_manager.base_path),
        "available_space": available_space
    }

@router.get("/files", response_model=List[Dict[str, Any]])
async def list_files(path: str = Query("", description="조회할 상대 경로")):
    """NAS 파일 목록 조회"""
    try:
        files = await nas_manager.list_files(path)
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/file")
async def read_file(path: str = Query(..., description="읽을 파일의 상대 경로")):
    """NAS 파일 내용 읽기"""
    try:
        content = await nas_manager.read_file(path)
        if content is None:
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
        
        # 파일 타입 추측
        file_ext = os.path.splitext(path)[1].lower()
        content_type = "application/octet-stream"  # 기본값
        
        if file_ext in ['.txt', '.log', '.json', '.md']:
            content_type = "text/plain"
        elif file_ext in ['.html', '.htm']:
            content_type = "text/html"
        elif file_ext in ['.jpg', '.jpeg']:
            content_type = "image/jpeg"
        elif file_ext == '.png':
            content_type = "image/png"
        
        return Response(content=content, media_type=content_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/file")
async def write_file(
    path: str = Query(..., description="쓸 파일의 상대 경로"),
    file: UploadFile = File(..., description="업로드할 파일")
):
    """NAS에 파일 쓰기 (업로드)"""
    try:
        content = await file.read()
        success = await nas_manager.write_file(path, content)
        
        if not success:
            raise HTTPException(status_code=500, detail="파일 쓰기에 실패했습니다")
        
        return {"message": "파일이 성공적으로 저장되었습니다", "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/file")
async def delete_file(path: str = Query(..., description="삭제할 파일의 상대 경로")):
    """NAS에서 파일 삭제"""
    try:
        success = await nas_manager.delete_file(path)
        
        if not success:
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없거나 삭제할 수 없습니다")
        
        return {"message": "파일이 성공적으로 삭제되었습니다", "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/directory")
async def create_directory(path: str = Query(..., description="생성할 디렉토리의 상대 경로")):
    """NAS에 디렉토리 생성"""
    try:
        full_path = nas_manager.base_path / path
        os.makedirs(full_path, exist_ok=True)
        return {"message": "디렉토리가 성공적으로 생성되었습니다", "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models", response_model=List[Dict[str, Any]])
async def list_models():
    """사용 가능한 모델 파일 목록 조회"""
    models_path = nas_manager.directory_structure["models"]
    results = []
    
    try:
        # 각 에이전트 유형별 모델 파일 리스트
        for agent_type in settings.agents.available:
            agent_path = f"{models_path}/{agent_type}"
            
            # 해당 에이전트 디렉토리의 파일 목록 가져오기
            files = await nas_manager.list_files(agent_path)
            
            # 각 파일에 에이전트 타입 정보 추가
            for file in files:
                file["agent_type"] = agent_type
                if file["type"] == "file":  # 파일인 경우에만 추가
                    file["full_path"] = f"{agent_path}/{file['name']}"
                    results.append(file)
                    
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 