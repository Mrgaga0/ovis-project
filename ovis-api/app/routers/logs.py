from fastapi import APIRouter, HTTPException, Query, Path, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import os
from pathlib import Path
import json

from ..config import get_settings
from ..core.nas_manager import NASManager

router = APIRouter()
settings = get_settings()

# NAS 관리자 초기화
nas_manager = NASManager(settings.nas.path, settings.nas.directory_structure)

@router.get("/")
async def get_logs(
    log_type: str = Query("system", description="로그 유형 (system, agent, ui 등)"),
    start_date: Optional[datetime] = Query(None, description="로그 시작일"),
    end_date: Optional[datetime] = Query(None, description="로그 종료일"),
    limit: int = Query(100, description="최대 로그 항목 수", ge=1, le=1000),
    level: Optional[str] = Query(None, description="로그 레벨 (debug, info, warning, error)")
):
    """로그 항목 조회"""
    try:
        # 기본 로그 디렉토리 경로
        logs_dir = nas_manager.get_log_path(log_type)
        
        # 날짜가 지정되지 않은 경우 기본값 설정
        if end_date is None:
            end_date = datetime.now()
        if start_date is None:
            start_date = end_date - timedelta(days=1)
        
        # 날짜 범위 내의 로그 파일 찾기
        log_files = []
        try:
            for item in await nas_manager.list_files(str(logs_dir.relative_to(nas_manager.base_path))):
                if item["type"] == "file" and item["name"].endswith(".log"):
                    log_files.append(item["path"])
        except:
            # 로그 디렉토리가 없는 경우 빈 결과 반환
            return {"logs": [], "count": 0}
        
        # 로그 항목 수집
        logs = []
        for log_file in log_files:
            try:
                content = await nas_manager.read_file(log_file)
                if content:
                    # 텍스트로 변환
                    text_content = content.decode('utf-8')
                    
                    # 각 줄을 파싱
                    for line in text_content.splitlines():
                        try:
                            # JSON 형식의 로그라고 가정
                            log_entry = json.loads(line)
                            
                            # 타임스탬프 파싱
                            if "timestamp" in log_entry:
                                log_time = datetime.fromisoformat(log_entry["timestamp"].replace('Z', '+00:00'))
                                
                                # 날짜 필터링
                                if start_date <= log_time <= end_date:
                                    # 레벨 필터링
                                    if level is None or log_entry.get("level", "").lower() == level.lower():
                                        logs.append(log_entry)
                        except:
                            # JSON 파싱 실패 시 다음 줄로 계속
                            continue
            except:
                # 파일 읽기 실패 시 다음 파일로 계속
                continue
        
        # 시간순 정렬 및 제한
        logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        logs = logs[:limit]
        
        return {"logs": logs, "count": len(logs)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files")
async def get_log_files():
    """사용 가능한 로그 파일 목록 조회"""
    try:
        logs_dir = str(nas_manager.directory_structure["logs"])
        log_files = []
        
        # 로그 디렉토리 탐색
        try:
            # 로그 디렉토리 내 모든 항목 조회
            items = await nas_manager.list_files(logs_dir)
            
            # 디렉토리 목록 (로그 유형)
            log_types = [item for item in items if item["type"] == "directory"]
            
            # 각 로그 유형별 파일 조회
            for log_type in log_types:
                type_path = f"{logs_dir}/{log_type['name']}"
                type_files = await nas_manager.list_files(type_path)
                
                # 각 파일에 로그 유형 정보 추가
                for file in type_files:
                    if file["type"] == "file" and file["name"].endswith(".log"):
                        file["log_type"] = log_type["name"]
                        file["full_path"] = f"{type_path}/{file['name']}"
                        log_files.append(file)
        except:
            # 로그 디렉토리 탐색 실패
            pass
            
        # 메인 로그 디렉토리에서 직접 로그 파일 조회
        try:
            main_log_files = [item for item in items if item["type"] == "file" and item["name"].endswith(".log")]
            for file in main_log_files:
                file["log_type"] = "main"
                file["full_path"] = f"{logs_dir}/{file['name']}"
                log_files.append(file)
        except:
            pass
        
        return log_files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/file")
async def read_log_file(path: str = Query(..., description="로그 파일의 상대 경로")):
    """특정 로그 파일 내용 읽기"""
    try:
        content = await nas_manager.read_file(path)
        if content is None:
            raise HTTPException(status_code=404, detail="로그 파일을 찾을 수 없습니다")
        
        # 텍스트로 변환
        text_content = content.decode('utf-8')
        
        # 각 줄을 JSON 객체로 파싱 시도
        logs = []
        for line in text_content.splitlines():
            try:
                # JSON 형식의 로그라고 가정
                log_entry = json.loads(line)
                logs.append(log_entry)
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 원시 텍스트로 추가
                logs.append({"raw": line})
        
        return {"logs": logs, "count": len(logs), "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/file")
async def delete_log_file(path: str = Query(..., description="삭제할 로그 파일의 상대 경로")):
    """로그 파일 삭제"""
    try:
        # 경로가 로그 디렉토리 내에 있는지 확인
        logs_dir = nas_manager.directory_structure["logs"]
        if not path.startswith(logs_dir):
            raise HTTPException(status_code=400, detail="로그 디렉토리 외부의 파일은 삭제할 수 없습니다")
        
        success = await nas_manager.delete_file(path)
        
        if not success:
            raise HTTPException(status_code=404, detail="로그 파일을 찾을 수 없거나 삭제할 수 없습니다")
        
        return {"message": "로그 파일이 성공적으로 삭제되었습니다", "path": path}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 