import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from ...models.agent import AgentStatus, AgentConfig
from .modules.data_collector import NewsCollector
from .modules.topic_analyzer import TopicAnalyzer
from .modules.content_generator import ContentGenerator
from ...core.nas_manager import NASManager
from ...config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class AlphaAgent:
    """
    오비스 알파 에이전트 - 국제/국내 정치 및 이슈 관련 언론 콘텐츠 제작을 지원하는 시스템
    
    주요 기능:
    - 다양한 뉴스 소스에서 데이터 수집
    - 주제 분석 및 정치 성향 평가
    - 다양한 형식의 콘텐츠 생성 (일반 기사, MZ 타겟 기사, 유튜브 대본)
    """
    
    def __init__(self, agent_id: str, config: AgentConfig):
        self.id = agent_id
        self.config = config
        self.status = AgentStatus.INACTIVE
        self.last_active = None
        self.metrics = {"processed_news": 0, "generated_content": 0}
        self._running = False
        
        # NAS 경로 설정
        self.nas_manager = NASManager(settings.nas.path, settings.nas.directory_structure)
        self.data_path = self.nas_manager.get_data_path("alpha")
        self.model_path = self.nas_manager.get_model_path("alpha")
        
        # 하위 모듈 초기화
        self.data_collector = None
        self.topic_analyzer = None
        self.content_generator = None
        
    async def initialize(self):
        """에이전트 초기화 및 필요한 리소스 로드"""
        try:
            logger.info(f"알파 에이전트 초기화 중: {self.id}")
            self.status = AgentStatus.LOADING
            
            # 필요한 디렉토리 확인 및 생성
            await self._initialize_directories()
            
            # 하위 모듈 초기화
            gemini_api_key = self.config.parameters.get("gemini_api_key", "")
            if not gemini_api_key:
                raise ValueError("Gemini API 키가 설정되지 않았습니다.")
            
            # 데이터 수집 모듈 초기화
            self.data_collector = NewsCollector(
                config={
                    "rss_sources": self.config.parameters.get("rss_sources", []),
                    "api_keys": self.config.parameters.get("api_keys", {}),
                    "enable_js_rendering": self.config.parameters.get("enable_js_rendering", False),
                    "enable_anti_bot": self.config.parameters.get("enable_anti_bot", True)
                }
            )
            
            # 주제 분석기 초기화
            self.topic_analyzer = TopicAnalyzer(
                gemini_api_key=gemini_api_key,
                config={
                    "political_analyzer_enabled": self.config.parameters.get("political_analyzer_enabled", True),
                    "mz_analyzer_enabled": self.config.parameters.get("mz_analyzer_enabled", True),
                    "trend_sources": self.config.parameters.get("trend_sources", ["twitter", "instagram"])
                }
            )
            
            # 콘텐츠 생성기 초기화
            self.content_generator = ContentGenerator(
                gemini_api_key=gemini_api_key,
                config={
                    "enable_fact_checking": self.config.parameters.get("enable_fact_checking", True),
                    "formats": self.config.parameters.get("formats", ["standard", "mz", "youtube"])
                }
            )
            
            self.status = AgentStatus.IDLE
            logger.info(f"알파 에이전트 초기화 완료: {self.id}")
            return True
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"알파 에이전트 초기화 실패: {str(e)}")
            return False
    
    async def start(self):
        """에이전트 실행"""
        if self.status == AgentStatus.RUNNING:
            logger.warning(f"에이전트가 이미 실행 중입니다: {self.id}")
            return False
            
        try:
            logger.info(f"알파 에이전트 시작 중: {self.id}")
            if self.status == AgentStatus.INACTIVE:
                await self.initialize()
                
            self.status = AgentStatus.RUNNING
            self.last_active = datetime.now()
            self._running = True
            
            return True
        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"알파 에이전트 시작 실패: {str(e)}")
            return False
    
    async def stop(self):
        """에이전트 중지"""
        logger.info(f"알파 에이전트 중지 중: {self.id}")
        self._running = False
        self.status = AgentStatus.IDLE
        return True
        
    async def collect_news(self, parameters: Dict[str, Any]):
        """뉴스 데이터 수집"""
        if self.status != AgentStatus.RUNNING:
            raise RuntimeError("에이전트가 실행 중이 아닙니다.")
            
        logger.info(f"뉴스 수집 시작: {parameters}")
        try:
            collected_news = await self.data_collector.collect_news(parameters)
            self.metrics["processed_news"] += len(collected_news)
            return collected_news
        except Exception as e:
            logger.error(f"뉴스 수집 중 오류 발생: {str(e)}")
            raise
            
    async def analyze_topics(self, news_items: List[Dict[str, Any]], analysis_type: str = "default"):
        """수집된 뉴스에서 주제 분석"""
        if self.status != AgentStatus.RUNNING:
            raise RuntimeError("에이전트가 실행 중이 아닙니다.")
            
        logger.info(f"주제 분석 시작: {analysis_type}, 항목 수: {len(news_items)}")
        try:
            analysis_result = await self.topic_analyzer.analyze_topic(news_items, analysis_type)
            return analysis_result
        except Exception as e:
            logger.error(f"주제 분석 중 오류 발생: {str(e)}")
            raise
            
    async def generate_content(self, topic: Dict[str, Any], format_type: str, parameters: Optional[Dict[str, Any]] = None):
        """콘텐츠 생성"""
        if self.status != AgentStatus.RUNNING:
            raise RuntimeError("에이전트가 실행 중이 아닙니다.")
            
        logger.info(f"콘텐츠 생성 시작: {format_type}")
        try:
            content = await self.content_generator.generate_content(topic, format_type, parameters)
            self.metrics["generated_content"] += 1
            
            # 결과 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            content_path = self.data_path / "generated_content" / f"{format_type}_{timestamp}.json"
            content_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(content_path, "w", encoding="utf-8") as f:
                import json
                json.dump(content, f, ensure_ascii=False, indent=2)
                
            return content
        except Exception as e:
            logger.error(f"콘텐츠 생성 중 오류 발생: {str(e)}")
            raise
            
    async def _initialize_directories(self):
        """필요한 디렉토리 초기화"""
        required_dirs = [
            self.data_path / "collected_news",
            self.data_path / "analyzed_topics",
            self.data_path / "generated_content"
        ]
        
        for directory in required_dirs:
            directory.mkdir(parents=True, exist_ok=True)
            
    def get_status(self):
        """현재 에이전트 상태 반환"""
        return {
            "id": self.id,
            "status": self.status,
            "last_active": self.last_active,
            "metrics": self.metrics
        } 