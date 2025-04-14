import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Union, Any
from functools import lru_cache
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# 설정 모델
class ApiSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    prefix: str = "/api/v1"
    cors_origins: List[str] = ["*"]

class NasDirectoryStructure(BaseModel):
    models: str = "models"
    data: str = "data"
    logs: str = "logs"
    
    def items(self):
        """딕셔너리 형태로 항목 반환"""
        return self.dict().items()

class NasSettings(BaseModel):
    path: str = "./data"  # 기본값을 Docker 볼륨 경로로 변경
    cache_size: str = "1GB"
    timeout: int = 5000
    retry_attempts: int = 3
    directory_structure: NasDirectoryStructure = NasDirectoryStructure()

class AgentSettings(BaseModel):
    available: List[str] = ["alpha", "beta", "theta"]
    default: str = "alpha"
    auto_start: bool = False

class LoggingFileSettings(BaseModel):
    enabled: bool = True
    path: str = "/app/logs/ovis.log"
    max_size: str = "10MB"
    max_files: int = 5

class LoggingNasSettings(BaseModel):
    enabled: bool = True
    path: str = "logs/system"

class LoggingConsoleSettings(BaseModel):
    enabled: bool = True
    level: str = "debug"

class LoggingMetricsSettings(BaseModel):
    enabled: bool = True
    interval: int = 60

class LoggingSettings(BaseModel):
    file: LoggingFileSettings = LoggingFileSettings()
    nas: LoggingNasSettings = LoggingNasSettings()
    console: LoggingConsoleSettings = LoggingConsoleSettings()
    metrics: LoggingMetricsSettings = LoggingMetricsSettings()

class SecuritySettings(BaseModel):
    encryption_key: str = ""
    require_authentication: bool = False

class SystemResourceLimits(BaseModel):
    memory: str = "4GB"
    cpu_percent: int = 80

class SystemSettings(BaseModel):
    resource_limits: SystemResourceLimits = SystemResourceLimits()
    check_updates: bool = True
    auto_update: bool = False
    temp_directory: str = "/tmp/ovis"

class AppSettings(BaseModel):
    name: str = "OVIS - 개인화 AI 에이전트 시스템"
    version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "info"

class Settings(BaseModel):
    app: AppSettings = AppSettings()
    api: ApiSettings = ApiSettings()
    ui: dict = {"port": 3000, "dev_server": True}
    nas: NasSettings = NasSettings()
    agents: AgentSettings = AgentSettings()
    logging: LoggingSettings = LoggingSettings()
    security: SecuritySettings = SecuritySettings()
    system: SystemSettings = SystemSettings()

def load_config_from_file() -> Dict[str, Any]:
    """설정 파일에서 구성을 로드합니다."""
    config_path = os.environ.get("OVIS_CONFIG", "/app/config/local.json")
    default_config_path = os.path.join(os.path.dirname(config_path), "default.json")
    
    # 기본 설정 로드
    default_config = {}
    if os.path.exists(default_config_path):
        with open(default_config_path, 'r', encoding='utf-8') as f:
            default_config = json.load(f)
    
    # 로컬 설정 로드 및 통합
    config = default_config.copy()
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            local_config = json.load(f)
            
        # 로컬 설정과 기본 설정 병합
        _deep_update(config, local_config)
    
    return config

def _deep_update(target: dict, source: dict) -> None:
    """두 딕셔너리를 재귀적으로 병합합니다."""
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_update(target[key], value)
        else:
            target[key] = value

@lru_cache()
def get_settings() -> Settings:
    """설정을 가져오고 캐시합니다."""
    config_dict = load_config_from_file()
    return Settings(**config_dict) 