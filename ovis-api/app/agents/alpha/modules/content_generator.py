import asyncio
import logging
import json
import uuid
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
import aiohttp
from pathlib import Path

from .topic_analyzer import GeminiConnector

logger = logging.getLogger(__name__)

class StandardArticleGenerator:
    """표준 뉴스 기사 생성기"""
    
    def __init__(self, gemini_pipeline):
        self.gemini = gemini_pipeline
        self.template = """
당신은 중도적 관점을 가진 저널리스트입니다. 주어진 주제와 관련 정보를 바탕으로 균형 잡힌 기사를 작성해주세요.
결과는 JSON 형식으로 제공해주세요.

# 주제 정보
{topic_info}

# 작성 가이드라인
- 객관적이고 중립적인 톤 유지
- 주요 사실과 배경 정보 포함
- 다양한 관점 균형있게 제시
- 명확하고 간결한 문체 사용
- 제목은 주제를 잘 반영하며 자극적이지 않게 작성
- 적절한 인용구 포함
- 주요 주장에 대한 근거 제시

# 기사 구조
1. 헤드라인: 10-15단어 이내의 명확한 제목
2. 부제목: 주요 내용을 한 문장으로 요약
3. 리드(도입부): 기사의 핵심 내용을 간결하게 요약
4. 본문: 배경, 주요 사실, 다양한 관점, 영향 등 포함
5. 결론: 주제에 대한 전망이나 함의 제시

# 반환 형식
JSON 형식으로 다음 필드를 포함하여 응답해주세요:
- headline: 헤드라인
- subheading: 부제목
- lead: 리드 문단
- body: 본문 내용 (여러 단락으로 구성)
- conclusion: 결론 문단
- sources: 참고할만한 출처 목록
- related_topics: 관련 주제 목록
"""
    
    async def generate(self, topic: Dict[str, Any], parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """표준 기사 생성"""
        # 주제 정보 포맷팅
        topic_info = self._format_topic_info(topic)
        
        # 템플릿 채우기
        prompt = self.template.format(topic_info=topic_info)
        
        # Gemini API 호출
        result = await self.gemini.generate_content(prompt)
        
        # 결과 파싱
        try:
            parsed_result = self._parse_result(result.get("text", ""))
            parsed_result["format"] = "standard"
            parsed_result["id"] = str(uuid.uuid4())
            parsed_result["created_at"] = datetime.now().isoformat()
            return parsed_result
        except Exception as e:
            logger.error(f"표준 기사 생성 실패: {str(e)}")
            return {
                "error": f"기사 생성 실패: {str(e)}",
                "raw_text": result.get("text", ""),
                "format": "standard",
                "id": str(uuid.uuid4()),
                "created_at": datetime.now().isoformat()
            }
    
    def _format_topic_info(self, topic: Dict[str, Any]) -> str:
        """주제 정보 포맷팅"""
        sections = []
        
        # 주요 주제 정보
        if "title" in topic:
            sections.append(f"주제: {topic['title']}")
        
        # 요약 정보
        if "summary" in topic:
            sections.append(f"요약: {topic['summary']}")
            
        # 키워드 및 엔티티
        keywords = topic.get("keywords", {}).get("keywords", [])
        if keywords:
            sections.append(f"키워드: {', '.join(keywords)}")
            
        entities = topic.get("keywords", {}).get("entities", [])
        if entities:
            sections.append(f"주요 개체: {', '.join(entities)}")
            
        # 정치 성향 분석
        political_analysis = topic.get("political_analysis", {})
        if political_analysis:
            center_index = political_analysis.get("center_index", 0.5)
            sections.append(f"중도성 지수: {center_index:.2f} (0: 극단적, 1: 중도적)")
            
        # MZ 세대 관련성
        mz_analysis = topic.get("mz_analysis", {})
        if mz_analysis:
            mz_score = mz_analysis.get("combined_score", 0)
            sections.append(f"MZ 세대 관련성: {mz_score:.2f} (0: 낮음, 1: 높음)")
            
        # 클러스터 정보
        if "clusters" in topic and "clusters" in topic["clusters"]:
            for cluster in topic["clusters"]["clusters"]:
                sections.append(f"관련 주제: {cluster.get('topic', '')}\n  요약: {cluster.get('summary', '')}")
                
        return "\n\n".join(sections)
    
    def _parse_result(self, text: str) -> Dict[str, Any]:
        """Gemini 응답 파싱"""
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
            return json.loads(json_str)
        else:
            try:
                # JSON 블록 없이 직접 JSON 문자열인 경우
                return json.loads(text)
            except:
                # 텍스트 응답을 구조화된 형태로 변환 시도
                lines = text.strip().split('\n')
                
                # 제목 추출 시도
                headline = lines[0] if lines else "제목 없음"
                subheading = lines[1] if len(lines) > 1 else ""
                
                # 본문 추출
                body = "\n".join(lines[2:]) if len(lines) > 2 else ""
                
                return {
                    "headline": headline,
                    "subheading": subheading,
                    "lead": "",
                    "body": body,
                    "conclusion": "",
                    "sources": [],
                    "related_topics": []
                }


class MZArticleGenerator:
    """MZ 세대 타겟 기사 생성기"""
    
    def __init__(self, gemini_pipeline):
        self.gemini = gemini_pipeline
        self.template = """
당신은 MZ세대(밀레니얼+Z세대)를 위한 콘텐츠를 제작하는 미디어 전문가입니다.
주어진 주제와 관련 정보를 바탕으로 MZ세대가 관심을 가질만한 기사를 작성해주세요.
결과는 JSON 형식으로 제공해주세요.

# 주제 정보
{topic_info}

# MZ세대 콘텐츠 가이드라인
- 간결하고 쉬운 용어 사용
- 시각적 요소 적극 활용 (인포그래픽, 차트 등)
- 대화체와 친근한 톤 유지
- 핵심을 빠르게 전달하는 형식
- 호기심을 자극하는 제목과 소제목
- 인터랙티브 요소 제안 (퀴즈, 투표 등)
- 모바일 친화적 형식 (짧은 단락, 굵은 텍스트 활용)
- 사회적 가치와 연결 (ESG, 다양성 등)

# 기사 구조
1. 캐치프레이즈: 호기심을 자극하는 짧은 제목
2. 메인 포인트: 핵심 내용을 3-5개 요점으로 정리
3. 본문: 짧은 단락과 시각적 요소로 구성
4. 인터랙티브 요소: 독자 참여를 위한 요소 제안
5. 액션 포인트: 기사 이후 독자가 할 수 있는 행동 제안

# 반환 형식
JSON 형식으로 다음 필드를 포함하여 응답해주세요:
- catchphrase: 캐치프레이즈 제목
- tldr: 너무 길어서 읽기 힘든 경우를 위한 초간단 요약 (50자 이내)
- main_points: 메인 포인트 목록 (3-5개)
- body: 본문 내용 (짧은 단락들로 구성)
- interactive_elements: 인터랙티브 요소 제안 (퀴즈, 투표 등)
- infographic_suggestions: 인포그래픽 구성 제안
- action_points: 독자가 취할 수 있는 액션 포인트 목록
- social_sharing_text: 소셜 미디어 공유용 짧은 텍스트 (150자 이내)
- hashtags: 관련 해시태그 목록
"""
    
    async def generate(self, topic: Dict[str, Any], parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """MZ 타겟 기사 생성"""
        # 주제 정보 포맷팅
        topic_info = self._format_topic_info(topic)
        
        # 템플릿 채우기
        prompt = self.template.format(topic_info=topic_info)
        
        # Gemini API 호출
        result = await self.gemini.generate_content(prompt)
        
        # 결과 파싱
        try:
            parsed_result = self._parse_result(result.get("text", ""))
            parsed_result["format"] = "mz"
            parsed_result["id"] = str(uuid.uuid4())
            parsed_result["created_at"] = datetime.now().isoformat()
            return parsed_result
        except Exception as e:
            logger.error(f"MZ 기사 생성 실패: {str(e)}")
            return {
                "error": f"기사 생성 실패: {str(e)}",
                "raw_text": result.get("text", ""),
                "format": "mz",
                "id": str(uuid.uuid4()),
                "created_at": datetime.now().isoformat()
            }
    
    def _format_topic_info(self, topic: Dict[str, Any]) -> str:
        """주제 정보 포맷팅"""
        sections = []
        
        # 주요 주제 정보
        if "title" in topic:
            sections.append(f"주제: {topic['title']}")
        
        # 요약 정보
        if "summary" in topic:
            sections.append(f"요약: {topic['summary']}")
            
        # MZ 세대 관심사 정보를 우선적으로 포함
        mz_analysis = topic.get("mz_analysis", {})
        if mz_analysis:
            mz_score = mz_analysis.get("combined_score", 0)
            sections.append(f"MZ 세대 관련성 점수: {mz_score:.2f}")
            
            trending_keywords = mz_analysis.get("trending_keywords", [])
            if trending_keywords:
                sections.append(f"트렌딩 키워드: {', '.join(trending_keywords)}")
                
            interests = mz_analysis.get("interests", [])
            if interests:
                sections.append(f"관심 분야: {', '.join(interests)}")
                
            suggested_angles = mz_analysis.get("suggested_angles", [])
            if suggested_angles:
                angle_text = "\n- " + "\n- ".join(suggested_angles)
                sections.append(f"추천 접근 방식: {angle_text}")
            
        # 키워드 및 엔티티
        keywords = topic.get("keywords", {}).get("keywords", [])
        if keywords:
            sections.append(f"키워드: {', '.join(keywords)}")
            
        # 정치 성향 정보는 중도적 관점 강조
        political_analysis = topic.get("political_analysis", {})
        if political_analysis:
            center_index = political_analysis.get("center_index", 0.5)
            sections.append(f"중도성 지수: {center_index:.2f} (0: 극단적, 1: 중도적)")
                
        return "\n\n".join(sections)
    
    def _parse_result(self, text: str) -> Dict[str, Any]:
        """Gemini 응답 파싱"""
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
            return json.loads(json_str)
        else:
            try:
                # JSON 블록 없이 직접 JSON 문자열인 경우
                return json.loads(text)
            except:
                # 텍스트 응답을 구조화된 형태로 변환 시도
                return {
                    "catchphrase": "제목 없음",
                    "tldr": "요약 없음",
                    "main_points": [],
                    "body": text,
                    "interactive_elements": [],
                    "infographic_suggestions": [],
                    "action_points": [],
                    "social_sharing_text": "",
                    "hashtags": []
                }


class YouTubeScriptGenerator:
    """유튜브 스크립트 생성기"""
    
    def __init__(self, gemini_pipeline):
        self.gemini = gemini_pipeline
        self.template = """
당신은 국제/국내 정치 및 시사 이슈를 다루는, 인기 있는 유튜브 채널의 콘텐츠 제작자입니다.
주어진 주제와 관련 정보를 바탕으로 매력적이고 정보가 풍부한 유튜브 스크립트를 작성해주세요.
결과는 JSON 형식으로 제공해주세요.

# 주제 정보
{topic_info}

# 스크립트 형식
{format_guidelines}

# 유튜브 콘텐츠 가이드라인
- 시청자의 관심을 빠르게 사로잡는 도입부
- 명확하고 간결한 메시지 전달
- 시각 자료에 대한 설명 포함 (그래픽, 차트, 영상 클립 등)
- 다양한 관점을 균형 있게 제시
- 전문성과 신뢰성 유지
- 짧은 문장과 대화체 사용
- 중요한 정보는 반복하여 강조
- 몰입도를 높이는 질문이나 호기심 유발 요소 포함
- 적절한 길이 유지 (형식에 따라 다름)
- 명확한 콜투액션 포함 (구독, 알림 설정, 댓글 등)

# 반환 형식
JSON 형식으로 다음 필드를 포함하여 응답해주세요:
- title: 영상 제목 (매력적이면서도 SEO 최적화)
- hook: 시청자의 관심을 사로잡는 짧은 도입부 (15-30초 분량)
- sections: 스크립트 섹션 배열 (각 섹션은 title과 content 포함)
- visual_cues: 시각 자료 제안 배열 (각 큐는 timecode, description 포함)
- outro: 영상 마무리 및 콜투액션
- description: 유튜브 설명란용 텍스트
- tags: 관련 태그 목록
- estimated_duration: 예상 영상 길이 (분)
"""
    
    async def generate(self, topic: Dict[str, Any], parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """유튜브 스크립트 생성"""
        # 파라미터 확인
        params = parameters or {}
        format_type = params.get("format_type", "standard")
        
        # 포맷 가이드라인 선택
        format_guidelines = self._get_format_guidelines(format_type)
        
        # 주제 정보 포맷팅
        topic_info = self._format_topic_info(topic)
        
        # 템플릿 채우기
        prompt = self.template.format(
            topic_info=topic_info,
            format_guidelines=format_guidelines
        )
        
        # Gemini API 호출
        result = await self.gemini.generate_content(prompt)
        
        # 결과 파싱
        try:
            parsed_result = self._parse_result(result.get("text", ""))
            parsed_result["format"] = "youtube"
            parsed_result["format_type"] = format_type
            parsed_result["id"] = str(uuid.uuid4())
            parsed_result["created_at"] = datetime.now().isoformat()
            return parsed_result
        except Exception as e:
            logger.error(f"유튜브 스크립트 생성 실패: {str(e)}")
            return {
                "error": f"스크립트 생성 실패: {str(e)}",
                "raw_text": result.get("text", ""),
                "format": "youtube",
                "format_type": format_type,
                "id": str(uuid.uuid4()),
                "created_at": datetime.now().isoformat()
            }
    
    def _get_format_guidelines(self, format_type: str) -> str:
        """스크립트 포맷 가이드라인 가져오기"""
        formats = {
            "shortform": """
# 숏폼(1-3분) 가이드라인
- 핵심 메시지 하나에 집중
- 처음 3초 내에 시청자 관심 사로잡기
- 강렬한 시각적 요소 활용
- 간결하고 직관적인 내용 구성
- 배경음악 및 효과음 적극 활용
- 빠른 템포와 에너지 있는 전달
- 특정 플랫폼(틱톡, 릴스, 쇼츠)에 최적화된 세로 형식 고려
            """,
            
            "standard": """
# 표준 영상(8-15분) 가이드라인
- 명확한 주제 및 구조 설정
- 효과적인 도입부와 마무리
- 주제를 3-5개 핵심 포인트로 분류
- 각 섹션 간 자연스러운 전환
- 시청자 참여 유도 요소 포함
- 균형 잡힌 정보 제공
- 적절한 사례와 설명 활용
            """,
            
            "indepth": """
# 심층 분석(20-40분) 가이드라인
- 주제에 대한 포괄적이고 깊이 있는 분석
- 배경 정보와 역사적 맥락 포함
- 다양한 관점과 해석 제시
- 데이터와 연구 결과 인용
- 심층적인 논의와 분석
- 복잡한 개념을 이해하기 쉽게 설명
- 주요 섹션별 요약 및 통합 결론
- 시청자가 휴식할 수 있는 자연스러운 휴지점 제공
            """
        }
        
        return formats.get(format_type, formats["standard"])
    
    def _format_topic_info(self, topic: Dict[str, Any]) -> str:
        """주제 정보 포맷팅"""
        sections = []
        
        # 주요 주제 정보
        if "title" in topic:
            sections.append(f"주제: {topic['title']}")
        
        # 요약 정보
        if "summary" in topic:
            sections.append(f"요약: {topic['summary']}")
            
        # 키워드 및 엔티티
        keywords = topic.get("keywords", {}).get("keywords", [])
        if keywords:
            sections.append(f"키워드: {', '.join(keywords)}")
            
        entities = topic.get("keywords", {}).get("entities", [])
        if entities:
            sections.append(f"주요 개체: {', '.join(entities)}")
            
        # 정치 성향 분석
        political_analysis = topic.get("political_analysis", {})
        if political_analysis:
            center_index = political_analysis.get("center_index", 0.5)
            sections.append(f"중도성 지수: {center_index:.2f} (0: 극단적, 1: 중도적)")
            
        # MZ 세대 관련성
        mz_analysis = topic.get("mz_analysis", {})
        if mz_analysis:
            mz_score = mz_analysis.get("combined_score", 0)
            sections.append(f"MZ 세대 관련성: {mz_score:.2f} (0: 낮음, 1: 높음)")
            
            trending_keywords = mz_analysis.get("trending_keywords", [])
            if trending_keywords:
                sections.append(f"트렌딩 키워드: {', '.join(trending_keywords)}")
            
        # 클러스터 정보
        if "clusters" in topic and "clusters" in topic["clusters"]:
            for cluster in topic["clusters"]["clusters"]:
                sections.append(f"관련 주제: {cluster.get('topic', '')}\n  요약: {cluster.get('summary', '')}")
                
        return "\n\n".join(sections)
    
    def _parse_result(self, text: str) -> Dict[str, Any]:
        """Gemini 응답 파싱"""
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
            return json.loads(json_str)
        else:
            try:
                # JSON 블록 없이 직접 JSON 문자열인 경우
                return json.loads(text)
            except:
                # 텍스트 응답을 구조화된 형태로 변환 시도
                return {
                    "title": "제목 없음",
                    "hook": "",
                    "sections": [{"title": "본문", "content": text}],
                    "visual_cues": [],
                    "outro": "",
                    "description": "",
                    "tags": [],
                    "estimated_duration": 0
                }


class InfographicGenerator:
    """인포그래픽 생성기"""
    
    def __init__(self, gemini_pipeline):
        self.gemini = gemini_pipeline
        self.template = """
당신은 복잡한 정보를 시각적으로 명확하게 전달하는 인포그래픽 전문가입니다.
주어진 주제와 관련 정보를 바탕으로 효과적인 인포그래픽 디자인 안을 작성해주세요.
결과는 JSON 형식으로 제공해주세요.

# 주제 정보
{topic_info}

# 인포그래픽 유형
{infographic_type}

# 디자인 가이드라인
- 핵심 정보를 명확하게 전달
- 시각적 계층 구조 활용
- 데이터 시각화를 통한 직관적 이해 지원
- 색상과 아이콘을 효과적으로 활용
- 텍스트는 최소화하고 핵심만 포함
- 일관된 시각적 스타일 유지
- 쉬운 내용 흐름과 명확한 방향성
- 출처 정보 포함

# 반환 형식
JSON 형식으로 다음 필드를 포함하여 응답해주세요:
- title: 인포그래픽 제목
- summary: 인포그래픽 핵심 메시지 요약
- sections: 인포그래픽 섹션 배열 (각 섹션은 title, content, visual_type 포함)
- data_points: 주요 데이터 포인트 배열 (숫자, 비율, 통계 등)
- color_scheme: 추천 색상 팔레트 (3-5개 색상 코드)
- icons: 필요한 아이콘 설명 목록
- layout: 전체 레이아웃 설명
- dimensions: 권장 크기 (pixels)
- sources: 데이터 출처 목록
"""
    
    async def generate(self, topic: Dict[str, Any], infographic_type: str = "chart") -> Dict[str, Any]:
        """인포그래픽 디자인 안 생성"""
        # 인포그래픽 유형 가이드라인 선택
        type_guidelines = self._get_type_guidelines(infographic_type)
        
        # 주제 정보 포맷팅
        topic_info = self._format_topic_info(topic)
        
        # 템플릿 채우기
        prompt = self.template.format(
            topic_info=topic_info,
            infographic_type=type_guidelines
        )
        
        # Gemini API 호출
        result = await self.gemini.generate_content(prompt)
        
        # 결과 파싱
        try:
            parsed_result = self._parse_result(result.get("text", ""))
            parsed_result["infographic_type"] = infographic_type
            parsed_result["id"] = str(uuid.uuid4())
            parsed_result["created_at"] = datetime.now().isoformat()
            return parsed_result
        except Exception as e:
            logger.error(f"인포그래픽 생성 실패: {str(e)}")
            return {
                "error": f"인포그래픽 생성 실패: {str(e)}",
                "raw_text": result.get("text", ""),
                "infographic_type": infographic_type,
                "id": str(uuid.uuid4()),
                "created_at": datetime.now().isoformat()
            }
    
    def _get_type_guidelines(self, infographic_type: str) -> str:
        """인포그래픽 유형 가이드라인 가져오기"""
        types = {
            "chart": """
# 차트/그래프 중심 인포그래픽
- 데이터 시각화에 중점
- 막대 그래프, 원형 차트, 선 그래프 등 활용
- 주요 수치와 추세를 명확히 표현
- 복잡한 데이터를 직관적으로 전달
- 색상 대비를 통한 중요 데이터 강조
- 명확한 범례와 축 라벨 제공
            """,
            
            "timeline": """
# 타임라인 인포그래픽
- 시간 순서에 따른 사건/발전 과정 시각화
- 명확한 시간 지표 사용
- 주요 이벤트 강조
- 각 시점별 간결한 설명 제공
- 시간의 흐름을 직관적으로 표현
- 기간에 따른 변화/발전 표현
            """,
            
            "comparison": """
# 비교형 인포그래픽
- 두 가지 이상의 주제/관점 비교
- 대칭적 레이아웃 활용
- 공통점과 차이점 명확히 구분
- 시각적 대조를 통한 비교 강화
- 중립적 관점 유지
- 균형 잡힌 정보량 제공
            """,
            
            "process": """
# 프로세스/단계 인포그래픽
- 절차나 과정을 단계별로 시각화
- 명확한 순서와 흐름 제시
- 각 단계별 아이콘/이미지 활용
- 단계 간 연결성 강조
- 진행 방향 명확히 표시
- 각 단계별 핵심 정보 간결하게 제공
            """
        }
        
        return types.get(infographic_type, types["chart"])
    
    def _format_topic_info(self, topic: Dict[str, Any]) -> str:
        """주제 정보 포맷팅"""
        sections = []
        
        # 주요 주제 정보
        if "title" in topic:
            sections.append(f"주제: {topic['title']}")
        
        # 요약 정보
        if "summary" in topic:
            sections.append(f"요약: {topic['summary']}")
            
        # 키워드 및 엔티티
        keywords = topic.get("keywords", {}).get("keywords", [])
        if keywords:
            sections.append(f"키워드: {', '.join(keywords)}")
            
        # MZ 세대 관련성 (인포그래픽 색감/스타일에 영향)
        mz_analysis = topic.get("mz_analysis", {})
        if mz_analysis:
            mz_score = mz_analysis.get("combined_score", 0)
            sections.append(f"MZ 세대 관련성: {mz_score:.2f} (0: 낮음, 1: 높음)")
            
        # 주요 데이터 포인트 (수치 정보)
        if "data_points" in topic:
            data_points = topic.get("data_points", [])
            data_text = "\n- " + "\n- ".join(data_points)
            sections.append(f"주요 데이터 포인트: {data_text}")
            
        # 클러스터 정보 (비교형 인포그래픽에 유용)
        if "clusters" in topic and "clusters" in topic["clusters"]:
            for cluster in topic["clusters"]["clusters"]:
                sections.append(f"관련 주제: {cluster.get('topic', '')}\n  요약: {cluster.get('summary', '')}")
                
        return "\n\n".join(sections)
    
    def _parse_result(self, text: str) -> Dict[str, Any]:
        """Gemini 응답 파싱"""
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(1)
            return json.loads(json_str)
        else:
            try:
                # JSON 블록 없이 직접 JSON 문자열인 경우
                return json.loads(text)
            except:
                # 텍스트 응답을 구조화된 형태로 변환 시도
                return {
                    "title": "인포그래픽 제목",
                    "summary": text[:200] + "..." if len(text) > 200 else text,
                    "sections": [],
                    "data_points": [],
                    "color_scheme": [],
                    "icons": [],
                    "layout": "",
                    "dimensions": "",
                    "sources": []
                }


class FactChecker:
    """팩트체크 시스템"""
    
    async def verify(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """콘텐츠 팩트체크 수행"""
        # 이 클래스에서는 실제 팩트체크 기능 구현은 생략하고
        # 간단한 메타데이터만 추가합니다.
        # 실제 구현에서는 외부 팩트체크 API 호출이나 진위 검증 로직 필요
        
        content["fact_check"] = {
            "verified": True,
            "verified_at": datetime.now().isoformat(),
            "verification_level": "basic",
            "accuracy_score": 0.85,  # 임의의 점수
            "warnings": []
        }
        
        return content


class ContentGenerator:
    """통합 콘텐츠 생성 시스템"""
    
    def __init__(self, gemini_api_key: str, config: Dict[str, Any]):
        self.config = config
        self.gemini_connector = GeminiConnector(gemini_api_key)
        
        # 콘텐츠 생성기 초기화
        self.generators = {
            "standard": StandardArticleGenerator(self.gemini_connector),
            "mz": MZArticleGenerator(self.gemini_connector),
            "youtube": YouTubeScriptGenerator(self.gemini_connector),
            "infographic": InfographicGenerator(self.gemini_connector)
        }
        
        # 팩트체크 시스템 초기화
        self.fact_checker = FactChecker()
        
    async def generate_content(self, topic: Dict[str, Any], format_type: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """특정 포맷의 콘텐츠 생성"""
        if format_type not in self.generators:
            raise ValueError(f"지원하지 않는 포맷 유형: {format_type}")
            
        logger.info(f"콘텐츠 생성 시작: {format_type}")
        
        # 해당 포맷 생성기 호출
        generator = self.generators[format_type]
        
        if format_type == "infographic":
            infographic_type = parameters.get("infographic_type", "chart") if parameters else "chart"
            content = await generator.generate(topic, infographic_type)
        else:
            content = await generator.generate(topic, parameters)
            
        # 팩트 체크 적용
        if self.config.get("enable_fact_checking", True):
            content = await self.fact_checker.verify(content)
            
        # 메타데이터 추가
        content["generated_from"] = {
            "topic_id": topic.get("id", "unknown"),
            "topic_title": topic.get("title", "")
        }
        
        return content 