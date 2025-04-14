import os
import sys
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from functools import wraps
import time
import traceback

from ..config import get_settings

class CustomJSONFormatter(logging.Formatter):
    """JSON 형식으로 로그 메시지를 포맷팅하는 클래스"""
    
    def format(self, record):
        """로그 레코드를 JSON 형식으로 포맷팅"""
        log_object = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # 예외 정보 추가
        if record.exc_info:
            log_object["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # 추가 데이터 있으면 포함
        if hasattr(record, "data") and record.data:
            log_object["data"] = record.data
        
        return json.dumps(log_object)

def setup_logger():
    """로거 설정 및 반환"""
    settings = get_settings()
    
    # 루트 로거 설정
    logger = logging.getLogger("ovis")
    level = getattr(logging, settings.app.log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # 이미 핸들러가 설정된 경우 중복 방지
    if logger.handlers:
        return logger
    
    # 콘솔 로깅 설정
    if settings.logging.console.enabled:
        console_handler = logging.StreamHandler(sys.stdout)
        console_level = getattr(logging, settings.logging.console.level.upper(), logging.DEBUG)
        console_handler.setLevel(console_level)
        console_handler.setFormatter(CustomJSONFormatter())
        logger.addHandler(console_handler)
    
    # 파일 로깅 설정
    if settings.logging.file.enabled:
        log_file = settings.logging.file.path
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=parse_size(settings.logging.file.max_size),
            backupCount=settings.logging.file.max_files
        )
        file_handler.setFormatter(CustomJSONFormatter())
        logger.addHandler(file_handler)
    
    # NAS 로깅 설정 (후속 구현)
    
    return logger

def parse_size(size_str):
    """문자열 크기 파싱 (예: "10MB")"""
    if not size_str:
        return 10 * 1024 * 1024  # 기본 10MB
    
    units = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 * 1024,
        "GB": 1024 * 1024 * 1024
    }
    
    size_str = size_str.upper()
    for unit, multiplier in units.items():
        if size_str.endswith(unit):
            try:
                size = float(size_str[:-len(unit)])
                return int(size * multiplier)
            except ValueError:
                return 10 * 1024 * 1024  # 파싱 실패 시 기본값
    
    # 단위 없는 경우 바이트로 간주
    try:
        return int(size_str)
    except ValueError:
        return 10 * 1024 * 1024  # 파싱 실패 시 기본값

def log_execution_time(logger=None, level=logging.INFO):
    """함수 실행 시간을 로깅하는 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            
            execution_time = end_time - start_time
            log_msg = f"{func.__name__} 실행 시간: {execution_time:.4f}초"
            
            # 로거 설정
            nonlocal logger
            if logger is None:
                logger = logging.getLogger("ovis.performance")
            
            # 로그 기록
            logger.log(level, log_msg, extra={"data": {"execution_time": execution_time}})
            
            return result
        return wrapper
    return decorator 