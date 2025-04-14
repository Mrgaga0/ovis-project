import os
import shutil
import aiofiles
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Union, BinaryIO
import logging

class NASManager:
    """NAS 연결 및 파일 관리를 위한 클래스"""
    
    def __init__(self, base_path: str, directory_structure: Dict[str, str]):
        """
        NAS 관리자 초기화
        
        Args:
            base_path: NAS 마운트 경로
            directory_structure: NAS 디렉토리 구조 (models, data, logs 등)
        """
        self.base_path = Path(base_path)
        self.directory_structure = directory_structure
        self.logger = logging.getLogger("ovis.nas_manager")
    
    async def check_connection(self) -> bool:
        """NAS 연결 상태 확인"""
        try:
            # 임시 파일 생성하여 쓰기 권한 확인
            test_file = self.base_path / ".connection_test"
            async with aiofiles.open(test_file, 'w') as f:
                await f.write("CONNECTION TEST")
            
            # 임시 파일 제거
            os.remove(test_file)
            return True
        except (IOError, PermissionError):
            return False
    
    async def init_directories(self) -> None:
        """필요한 디렉토리 구조 초기화"""
        for dir_type, dir_name in self.directory_structure.items():
            dir_path = self.base_path / dir_name
            os.makedirs(dir_path, exist_ok=True)
            
            # 에이전트별 디렉토리 생성 (모델 디렉토리)
            if dir_type == "models":
                for agent_type in ["alpha", "beta", "theta"]:
                    agent_dir = dir_path / agent_type
                    os.makedirs(agent_dir, exist_ok=True)
            
            # 데이터 디렉토리 하위 폴더 생성
            if dir_type == "data":
                os.makedirs(dir_path / "shared", exist_ok=True)
                os.makedirs(dir_path / "agent-specific", exist_ok=True)
    
    async def get_available_space(self) -> str:
        """NAS의 사용 가능한 공간 반환"""
        try:
            total, used, free = shutil.disk_usage(self.base_path)
            return f"{free // (2**30)} GB"
        except Exception:
            return "Unknown"
    
    async def list_files(self, relative_path: str = "") -> List[Dict[str, Union[str, int]]]:
        """지정된 경로의 파일 목록 반환"""
        full_path = self.base_path / relative_path
        result = []
        
        try:
            for item in os.listdir(full_path):
                item_path = full_path / item
                is_dir = os.path.isdir(item_path)
                
                file_info = {
                    "name": item,
                    "path": str(Path(relative_path) / item),
                    "type": "directory" if is_dir else "file",
                }
                
                if not is_dir:
                    file_info["size"] = os.path.getsize(item_path)
                
                result.append(file_info)
                
            return result
        except (FileNotFoundError, PermissionError) as e:
            self.logger.error(f"파일 목록 조회 중 오류: {str(e)}")
            return []
    
    async def read_file(self, relative_path: str) -> Optional[bytes]:
        """파일 내용 읽기"""
        full_path = self.base_path / relative_path
        
        try:
            async with aiofiles.open(full_path, 'rb') as f:
                return await f.read()
        except Exception as e:
            self.logger.error(f"파일 읽기 중 오류: {str(e)}")
            return None
    
    async def write_file(self, relative_path: str, content: Union[bytes, str]) -> bool:
        """파일 내용 쓰기"""
        full_path = self.base_path / relative_path
        
        # 디렉토리 생성
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        try:
            mode = 'wb' if isinstance(content, bytes) else 'w'
            async with aiofiles.open(full_path, mode) as f:
                await f.write(content)
            return True
        except Exception as e:
            self.logger.error(f"파일 쓰기 중 오류: {str(e)}")
            return False
    
    async def delete_file(self, relative_path: str) -> bool:
        """파일 삭제"""
        full_path = self.base_path / relative_path
        
        try:
            if os.path.isfile(full_path):
                os.remove(full_path)
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                return False
            return True
        except Exception as e:
            self.logger.error(f"파일 삭제 중 오류: {str(e)}")
            return False
    
    def get_model_path(self, agent_type: str) -> Path:
        """지정된 에이전트 타입의 모델 경로 반환"""
        return self.base_path / self.directory_structure["models"] / agent_type
    
    def get_data_path(self, shared: bool = True, agent_type: Optional[str] = None) -> Path:
        """데이터 경로 반환"""
        if shared:
            return self.base_path / self.directory_structure["data"] / "shared"
        else:
            return self.base_path / self.directory_structure["data"] / "agent-specific" / (agent_type or "")
    
    def get_log_path(self, log_type: str = "system") -> Path:
        """로그 경로 반환"""
        return self.base_path / self.directory_structure["logs"] / log_type 