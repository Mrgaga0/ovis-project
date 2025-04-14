import asyncio
import logging
import uuid
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import feedparser
import aiohttp
from bs4 import BeautifulSoup
import re
from pathlib import Path

logger = logging.getLogger(__name__)

class RSSCrawler:
    """RSS 피드에서 뉴스 수집"""
    
    def __init__(self, sources: List[str]):
        self.sources = sources
        
    async def fetch_latest(self, parameters: Dict[str, Any]):
        """최신 뉴스 가져오기"""
        results = []
        time_range = parameters.get("time_range", 24)  # 기본 24시간
        
        for source in self.sources:
            try:
                feed = feedparser.parse(source)
                
                for entry in feed.entries:
                    # 시간 필터링
                    pub_date = entry.get('published_parsed')
                    if pub_date:
                        pub_datetime = datetime(*pub_date[:6])
                        if datetime.now() - pub_datetime > timedelta(hours=time_range):
                            continue
                    
                    # 항목 추가
                    results.append({
                        "title": entry.get('title', ''),
                        "link": entry.get('link', ''),
                        "summary": entry.get('summary', ''),
                        "published": entry.get('published', ''),
                        "source": source,
                        "source_type": "rss"
                    })
            
            except Exception as e:
                logger.error(f"RSS 피드 처리 중 오류 발생 ({source}): {str(e)}")
                
        return results


class WebScraper:
    """웹 페이지 스크래핑"""
    
    def __init__(self, javascript_support: bool = False, anti_bot_measures: bool = True):
        self.javascript_support = javascript_support
        self.anti_bot_measures = anti_bot_measures
        self.session = None
        
    async def _get_session(self):
        """aiohttp 세션 얻기"""
        if self.session is None or self.session.closed:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
        
    async def scrape_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """URL 목록 스크래핑"""
        results = []
        session = await self._get_session()
        
        for url in urls:
            try:
                # 요청 간 지연 (안티봇 대응)
                if self.anti_bot_measures:
                    await asyncio.sleep(1)  # 1초 지연
                
                async with session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # BeautifulSoup으로 파싱
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # 기본 메타데이터 추출
                        title = soup.title.string if soup.title else ""
                        
                        # 메타 태그에서 설명 추출
                        description = ""
                        meta_desc = soup.find('meta', attrs={'name': 'description'})
                        if meta_desc:
                            description = meta_desc.get('content', '')
                        
                        # 본문 추출 (간단한 휴리스틱)
                        main_content = ""
                        article_tag = soup.find(['article', 'main', 'div'], class_=re.compile(r'article|content|main'))
                        if article_tag:
                            # 불필요한 태그 제거
                            for tag in article_tag.find_all(['script', 'style', 'nav', 'footer', 'aside']):
                                tag.decompose()
                            main_content = article_tag.get_text(strip=True)
                        
                        results.append({
                            "title": title,
                            "link": url,
                            "summary": description,
                            "content": main_content[:1000] + "..." if len(main_content) > 1000 else main_content,
                            "source": url,
                            "source_type": "web",
                            "scraped_at": datetime.now().isoformat()
                        })
                    else:
                        logger.warning(f"스크래핑 실패 ({url}): 상태 코드 {response.status}")
                        
            except Exception as e:
                logger.error(f"스크래핑 중 오류 발생 ({url}): {str(e)}")
                
        return results


class NewsAPIConnector:
    """뉴스 API 연결"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = None
        
    async def _get_session(self):
        """aiohttp 세션 얻기"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
        
    async def fetch_news(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """뉴스 API에서 뉴스 가져오기"""
        results = []
        session = await self._get_session()
        
        # 파라미터 준비
        query = parameters.get("query", "")
        time_range = parameters.get("time_range", 24)  # 시간 단위
        
        # API 요청 URL 및 파라미터
        url = "https://newsapi.org/v2/everything"
        from_date = (datetime.now() - timedelta(hours=time_range)).strftime("%Y-%m-%d")
        
        params = {
            "q": query,
            "from": from_date,
            "sortBy": "publishedAt",
            "apiKey": self.api_key,
            "language": parameters.get("language", "ko")
        }
        
        try:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("status") == "ok":
                        articles = data.get("articles", [])
                        
                        for article in articles:
                            results.append({
                                "title": article.get("title", ""),
                                "link": article.get("url", ""),
                                "summary": article.get("description", ""),
                                "content": article.get("content", ""),
                                "published": article.get("publishedAt", ""),
                                "source": article.get("source", {}).get("name", "NewsAPI"),
                                "source_type": "api",
                                "author": article.get("author", "")
                            })
                    else:
                        logger.error(f"NewsAPI 오류: {data.get('message', '알 수 없는 오류')}")
                else:
                    logger.error(f"NewsAPI 요청 실패: 상태 코드 {response.status}")
                    
        except Exception as e:
            logger.error(f"NewsAPI 사용 중 오류 발생: {str(e)}")
            
        return results


class CopyrightFilter:
    """저작권 준수 필터"""
    
    def process(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """저작권 필터링"""
        filtered_items = []
        
        for item in items:
            # 메타데이터에 출처 정보 추가
            item["copyright_info"] = {
                "original_source": item.get("source", "Unknown"),
                "license": "unknown",  # 실제로는 라이선스 감지 로직 필요
                "usage_rights": "인용 목적으로만 사용 가능",
                "attribution_required": True
            }
            
            # 라이선스 탐지 로직 (실제 구현 필요)
            # 여기서는 간단한 예시로 모든 항목이 인용 가능하다고 가정
            filtered_items.append(item)
            
        return filtered_items


class SourceRotationManager:
    """소스 로테이션 관리"""
    
    def __init__(self, sources: List[str], priority_weights: List[float]):
        self.sources = sources
        self.weights = priority_weights
        self.failure_counts = {source: 0 for source in sources}
        
    def get_current_priorities(self) -> List[str]:
        """현재 우선순위에 따른 소스 목록 반환"""
        # 실패 횟수에 따라 가중치 조정
        adjusted_weights = []
        for source, weight in zip(self.sources, self.weights):
            failure_penalty = self.failure_counts[source] * 0.1
            adjusted_weight = max(0.1, weight - failure_penalty)
            adjusted_weights.append((source, adjusted_weight))
            
        # 가중치에 따라 정렬
        sorted_sources = [source for source, _ in sorted(adjusted_weights, key=lambda x: x[1], reverse=True)]
        return sorted_sources
        
    def report_failure(self, source: str):
        """소스 실패 보고"""
        if source in self.failure_counts:
            self.failure_counts[source] += 1
            
    def report_success(self, source: str):
        """소스 성공 보고"""
        if source in self.failure_counts:
            self.failure_counts[source] = max(0, self.failure_counts[source] - 1)


class NewsCollector:
    """통합 뉴스 수집기"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rss_crawler = RSSCrawler(config.get("rss_sources", []))
        self.web_scraper = WebScraper(
            javascript_support=config.get("enable_js_rendering", False),
            anti_bot_measures=config.get("enable_anti_bot", True)
        )
        
        # API 커넥터 초기화
        api_keys = config.get("api_keys", {})
        self.api_connectors = {}
        
        if "newsapi" in api_keys:
            self.api_connectors["newsapi"] = NewsAPIConnector(api_keys["newsapi"])
        
        # 기타 API 커넥터 추가 가능
        
        self.copyright_filter = CopyrightFilter()
        self.source_rotation = SourceRotationManager(
            sources=["rss", "web", "api"],
            priority_weights=[0.4, 0.3, 0.3]
        )
        
    async def collect_news(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """다양한 소스에서 뉴스 수집"""
        collected_items = []
        source_priorities = self.source_rotation.get_current_priorities()
        
        for source_type in source_priorities:
            try:
                if source_type == "rss":
                    items = await self.rss_crawler.fetch_latest(parameters)
                elif source_type == "web":
                    urls = self._generate_scrape_targets(parameters)
                    items = await self.web_scraper.scrape_urls(urls)
                elif source_type == "api" and self.api_connectors:
                    # API 중에서 하나 선택
                    api_name = next(iter(self.api_connectors.keys()))
                    connector = self.api_connectors[api_name]
                    items = await connector.fetch_news(parameters)
                else:
                    continue
                
                # 저작권 필터 적용
                filtered_items = self.copyright_filter.process(items)
                collected_items.extend(filtered_items)
                
                # 소스 성공 보고
                self.source_rotation.report_success(source_type)
                
                # 충분한 결과를 얻었으면 중단
                if len(collected_items) >= parameters.get("target_count", 50):
                    break
                    
            except Exception as e:
                logger.warning(f"Source {source_type} failed: {str(e)}")
                self.source_rotation.report_failure(source_type)
                continue
        
        # 결과 처리
        final_results = self._normalize_and_deduplicate(collected_items)
        
        return final_results
        
    def _generate_scrape_targets(self, parameters: Dict[str, Any]) -> List[str]:
        """웹 스크래핑 대상 URL 생성"""
        # 실제 구현에서는 키워드를 기반으로 검색 결과 URL을 생성하거나
        # 미리 정의된 주요 뉴스 사이트 URL을 사용할 수 있습니다.
        
        # 간단한 예시로 고정 URL 반환
        return [
            "https://news.naver.com/",
            "https://news.daum.net/",
            "https://www.khan.co.kr/"
        ]
    
    def _normalize_and_deduplicate(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """수집 데이터 정규화 및 중복 제거"""
        normalized = []
        seen_urls = set()
        seen_titles = set()
        
        for item in items:
            # 필수 필드 확인
            if not item.get("title"):
                continue
                
            # URL 기반 중복 제거
            url = item.get("link", "")
            if url and url in seen_urls:
                continue
            if url:
                seen_urls.add(url)
                
            # 제목 기반 중복 제거 (유사 제목 처리를 위해 간단한 정규화)
            title = re.sub(r'\s+', ' ', item.get("title", "").strip().lower())
            if title in seen_titles:
                continue
            seen_titles.add(title)
            
            # 고유 ID 추가
            item["id"] = str(uuid.uuid4())
            
            # 수집 시간 추가
            if "collected_at" not in item:
                item["collected_at"] = datetime.now().isoformat()
                
            normalized.append(item)
            
        return normalized 