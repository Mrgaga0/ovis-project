import asyncio
import logging
import json
import uuid
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
import aiohttp
from pathlib import Path

logger = logging.getLogger(__name__)

class GeminiConnector:
    """Google Gemini API 연결 클래스"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "gemini-1.5-pro"
        self.session = None
        
    async def _get_session(self):
        """aiohttp 세션 얻기"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
        
    async def generate_content(self, prompt: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Gemini API 호출"""
        session = await self._get_session()
        
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        
        # 기본 파라미터
        default_params = {
            "temperature": 0.2,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 8192
        }
        
        # 사용자 파라미터로 업데이트
        if parameters:
            default_params.update(parameters)
            
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": default_params
        }
        
        try:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # 응답에서 텍스트 추출
                    if "candidates" in result and result["candidates"] and "content" in result["candidates"][0]:
                        content = result["candidates"][0]["content"]
                        text = content["parts"][0]["text"] if "parts" in content and content["parts"] else ""
                        
                        return {
                            "text": text,
                            "raw_response": result
                        }
                    else:
                        logger.error(f"Gemini API 응답에서 텍스트를 찾을 수 없습니다: {result}")
                        return {
                            "text": "",
                            "error": "응답에서 텍스트를 찾을 수 없습니다",
                            "raw_response": result
                        }
                else:
                    error_text = await response.text()
                    logger.error(f"Gemini API 오류: {response.status} - {error_text}")
                    return {
                        "text": "",
                        "error": f"API 오류: {response.status}",
                        "error_details": error_text
                    }
        except Exception as e:
            logger.error(f"Gemini API 호출 중 오류 발생: {str(e)}")
            return {
                "text": "",
                "error": f"API 호출 오류: {str(e)}"
            }


class PriorityTaskQueue:
    """우선순위 작업 큐"""
    
    def __init__(self, max_size: int = 100):
        self.queue = asyncio.PriorityQueue(maxsize=max_size)
        
    async def put(self, task: Dict[str, Any]):
        """작업 추가"""
        # 우선순위, 시간, 작업 순으로 정렬
        priority = task.get("priority", 5)  # 기본 우선순위 5
        timestamp = datetime.now().timestamp()
        await self.queue.put((priority, timestamp, task))
        
    async def get(self):
        """작업 가져오기"""
        _, _, task = await self.queue.get()
        return task
        
    def empty(self):
        """큐가 비어있는지 확인"""
        return self.queue.empty()
        
    def size(self):
        """큐 크기 확인"""
        return self.queue.qsize()


class PoliticalScaleAnalyzer:
    """정치 성향 분석기"""
    
    def __init__(self):
        # 좌/우 성향 관련 키워드 사전 (간단한 예시)
        self.left_keywords = [
            "진보", "민주", "평등", "노동", "복지", "공공", "인권", "정의당", "민주당"
        ]
        self.right_keywords = [
            "보수", "국민의힘", "시장", "자유", "안보", "애국", "기업", "규제완화"
        ]
        
    def calculate_base_score(self, content: Dict[str, Any]) -> float:
        """키워드 기반 기본 점수 계산"""
        text = ""
        if "title" in content:
            text += content["title"] + " "
        if "summary" in content:
            text += content["summary"] + " "
        if "content" in content:
            text += content["content"]
            
        text = text.lower()
        
        # 좌/우 키워드 매칭 수 계산
        left_count = sum(1 for keyword in self.left_keywords if keyword in text)
        right_count = sum(1 for keyword in self.right_keywords if keyword in text)
        
        total = left_count + right_count
        if total == 0:
            return 0.0  # 중립
            
        # -1.0(좌) ~ 1.0(우) 점수 계산
        return (right_count - left_count) / total


class MZTrendAnalyzer:
    """MZ 세대 트렌드 분석기"""
    
    def __init__(self, refresh_interval: int = 24, trend_sources: List[str] = None):
        self.refresh_interval = refresh_interval
        self.trend_sources = trend_sources or ["twitter", "instagram"]
        self.last_refresh = None
        self.trending_keywords = []
        
    async def refresh_trends(self):
        """트렌드 갱신"""
        # 실제 구현에서는 소셜 미디어 API 호출 등을 통해 트렌드 갱신
        # 여기서는 간단한 예시로 고정 키워드 사용
        self.trending_keywords = [
            "MZ", "밀레니얼", "Z세대", "인스타", "틱톡", "ESG", "친환경", 
            "웰빙", "플렉스", "YOLO", "워라밸", "갓생", "취향존중", 
            "소확행", "욜로족", "뉴트로", "한달살기", "N잡러"
        ]
        self.last_refresh = datetime.now()
        
    def match_with_trends(self, topic: Dict[str, Any]) -> float:
        """주제와 트렌드 매칭 점수 계산"""
        # 트렌드 갱신 필요한지 확인
        if self.last_refresh is None or (datetime.now() - self.last_refresh).total_seconds() > self.refresh_interval * 3600:
            asyncio.create_task(self.refresh_trends())
            
        if not self.trending_keywords:
            return 0.5  # 기본값
            
        # 주제 텍스트 준비
        text = ""
        if "title" in topic:
            text += topic["title"] + " "
        if "summary" in topic:
            text += topic["summary"] + " "
        if "keywords" in topic and isinstance(topic["keywords"], list):
            text += " ".join(topic["keywords"]) + " "
            
        text = text.lower()
        
        # 키워드 매칭
        matches = sum(1 for keyword in self.trending_keywords if keyword.lower() in text)
        
        # 0 ~ 1.0 점수 계산
        score = min(1.0, matches / len(self.trending_keywords) * 5)  # 최대 20% 키워드 매칭시 만점
        return score


class GeminiPipeline:
    """Gemini API 통합 파이프라인"""
    
    def __init__(self, api_key: str):
        self.gemini = GeminiConnector(api_key)
        self.task_queue = PriorityTaskQueue(max_size=100)
        self.prompt_templates = self._load_templates()
        self.is_running = False
        self.processing_task = None
        
    def _load_templates(self) -> Dict[str, str]:
        """프롬프트 템플릿 로드"""
        return {
            "keyword_extraction": """
다음 뉴스 항목에서 중요 키워드와 엔티티를 추출해주세요. JSON 형식으로 응답해주세요.

뉴스 항목:
{news_items}

응답 형식:
- keywords: 중요 키워드 (최대 10개)
- entities: 주요 개체 (인물, 조직, 장소 등)
- main_topic: 주요 주제 (간략한 설명)
- subtopics: 부가 주제들 (최대 3개)
- language: 뉴스 본문 언어 (ko, en 등)
            """,
            
            "topic_clustering": """
다음 뉴스 항목들을 비슷한 주제끼리 클러스터링하고, 각 클러스터의 주요 주제를 요약해주세요. JSON 형식으로 응답해주세요.

뉴스 항목:
{news_items}

응답 형식:
- clusters: 클러스터 목록 (각 클러스터는 id, topic, article_ids, summary 포함)
- related_topics: 연관 주제 목록
- trending_score: 전체 트렌드 점수 (0~1)
            """,
            
            "political_bias_analysis": """
다음 뉴스 내용의 정치적 성향을 분석해주세요. 좌우 스펙트럼에서 어디에 위치하는지 평가하고, 증거가 되는 구문이나 표현을 제시해주세요. JSON 형식으로 응답해주세요.

뉴스 내용:
{news_content}

응답 형식:
- score: 정치적 성향 점수 (-1.0: 극좌, 0: 중도, 1.0: 극우)
- center_index: 중도 지수 (0: 극단, 1.0: 완전 중도)
- indicators: 성향 지표 (좌/우 성향을 나타내는 표현 목록)
- analysis: 간략한 성향 분석
            """,
            
            "mz_relevance_analysis": """
다음 주제가 MZ세대(밀레니얼+Z세대)에게 얼마나 관련성이 있고 흥미로울지 분석해주세요. JSON 형식으로 응답해주세요.

주제:
{topic}

응답 형식:
- score: MZ 관련성 점수 (0~1)
- trending_keywords: MZ세대 관련 트렌딩 키워드
- interests: 관심 분야 (소셜미디어, 라이프스타일, 기술 등)
- suggested_angles: MZ세대 타겟으로 접근 가능한 각도들
- engagement_prediction: 예상 참여도 (low, medium, high)
            """
        }
    
    async def analyze_topic(self, news_items, analysis_type: str) -> Dict[str, Any]:
        """주제 분석 수행"""
        if analysis_type not in self.prompt_templates:
            raise ValueError(f"지원하지 않는 분석 유형: {analysis_type}")
            
        # 템플릿 준비
        template = self.prompt_templates[analysis_type]
        
        # 입력 준비
        if isinstance(news_items, list):
            # 리스트인 경우 포맷팅
            formatted_items = []
            for idx, item in enumerate(news_items):
                if isinstance(item, dict):
                    title = item.get("title", "제목 없음")
                    summary = item.get("summary", "")
                    content = item.get("content", "")
                    formatted_items.append(f"항목 {idx+1}:\n제목: {title}\n요약: {summary}\n내용: {content[:500]}...")
                else:
                    formatted_items.append(f"항목 {idx+1}: {str(item)[:500]}...")
            input_text = "\n\n".join(formatted_items)
        elif isinstance(news_items, dict):
            # 단일 딕셔너리인 경우
            input_text = f"""
제목: {news_items.get('title', '제목 없음')}
요약: {news_items.get('summary', '')}
내용: {news_items.get('content', '')[:1000]}...
            """
        else:
            # 문자열 또는 기타 형식
            input_text = str(news_items)
            
        # 프롬프트 생성
        if analysis_type == "political_bias_analysis":
            prompt = template.format(news_content=input_text)
        elif analysis_type == "mz_relevance_analysis":
            prompt = template.format(topic=input_text)
        else:
            prompt = template.format(news_items=input_text)
        
        # Gemini API 호출
        result = await self.gemini.generate_content(prompt)
        
        # 결과 파싱
        try:
            # JSON 응답 파싱
            text = result.get("text", "")
            json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1)
                parsed_result = json.loads(json_str)
            else:
                # JSON 형식이 아닌 경우 텍스트에서 직접 파싱 시도
                try:
                    parsed_result = json.loads(text)
                except:
                    # JSON 직접 파싱도 실패한 경우 텍스트 응답 반환
                    parsed_result = {
                        "text_response": text,
                        "analysis_type": analysis_type
                    }
            
            # 분석 유형 및 ID 추가
            parsed_result["analysis_type"] = analysis_type
            parsed_result["id"] = str(uuid.uuid4())
            parsed_result["created_at"] = datetime.now().isoformat()
            
            return parsed_result
            
        except Exception as e:
            logger.error(f"Gemini 응답 파싱 오류: {str(e)}")
            return {
                "error": f"응답 파싱 오류: {str(e)}",
                "text_response": result.get("text", ""),
                "analysis_type": analysis_type,
                "id": str(uuid.uuid4()),
                "created_at": datetime.now().isoformat()
            }


class TopicAnalyzer:
    """통합 주제 분석 시스템"""
    
    def __init__(self, gemini_api_key: str, config: Dict[str, Any]):
        self.config = config
        self.gemini_pipeline = GeminiPipeline(gemini_api_key)
        self.political_analyzer = PoliticalScaleAnalyzer()
        self.mz_analyzer = MZTrendAnalyzer(
            refresh_interval=24,
            trend_sources=config.get("trend_sources", ["twitter", "instagram"])
        )
        
    async def analyze_topic(self, news_items: List[Dict[str, Any]], analysis_type: str = "default") -> Dict[str, Any]:
        """주제 분석 수행"""
        results = {}
        
        # 기본 분석 - 키워드 추출 및 주제 클러스터링
        if analysis_type == "default" or analysis_type == "comprehensive":
            results["keywords"] = await self.gemini_pipeline.analyze_topic(news_items, "keyword_extraction")
            
            if len(news_items) > 1:
                results["clusters"] = await self.gemini_pipeline.analyze_topic(news_items, "topic_clustering")
                
        # 정치 성향 분석
        if (analysis_type == "political" or analysis_type == "comprehensive") and self.config.get("political_analyzer_enabled", True):
            # Gemini를 통한 고급 분석
            political_results = await self.gemini_pipeline.analyze_topic(news_items, "political_bias_analysis")
            
            # 기본 키워드 분석과 통합
            if isinstance(news_items, list) and len(news_items) > 0:
                sample_item = news_items[0]  # 첫 번째 항목 샘플링
                base_score = self.political_analyzer.calculate_base_score(sample_item)
                
                # 가중 평균 계산
                gemini_score = political_results.get("score", 0)
                political_results["combined_score"] = (gemini_score * 0.7) + (base_score * 0.3)
                
            results["political_analysis"] = political_results
            
        # MZ 세대 관련성 분석
        if (analysis_type == "mz" or analysis_type == "comprehensive") and self.config.get("mz_analyzer_enabled", True):
            # 트렌드 기반 기본 분석
            if isinstance(news_items, list) and len(news_items) > 0:
                trend_score = self.mz_analyzer.match_with_trends(news_items[0])
            else:
                trend_score = self.mz_analyzer.match_with_trends(news_items)
                
            # Gemini를 통한 고급 분석
            mz_results = await self.gemini_pipeline.analyze_topic(news_items, "mz_relevance_analysis")
            
            # 결과 통합
            mz_results["trend_score"] = trend_score
            mz_results["combined_score"] = (mz_results.get("score", 0) * 0.7) + (trend_score * 0.3)
            
            results["mz_analysis"] = mz_results
            
        # 메타데이터 추가
        results["id"] = str(uuid.uuid4())
        results["analysis_type"] = analysis_type
        results["created_at"] = datetime.now().isoformat()
        results["item_count"] = len(news_items) if isinstance(news_items, list) else 1
        
        return results 