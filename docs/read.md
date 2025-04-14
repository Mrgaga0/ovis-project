아래 요청 프롬프트를 전체적으로 확인하고 확실하게 이해한 뒤
단계별로 요청사항을 진행해

# 오비스 알파 에이전트 개발 요청

## 프로젝트 개요
알파 에이전트는 오비스 시스템의 첫 번째 특화 AI로, 국제/국내 정치 및 이슈 관련 언론 콘텐츠 제작을 지원하는 시스템입니다. 이 에이전트는 뉴스 수집부터 주제 선정, 다양한 형식(일반 기사, MZ세대용 기사, 유튜브 대본)의 콘텐츠 생성까지 담당합니다. 타겟 독자는 중도 성향 독자와 MZ세대입니다.

## 기술 스택
- 백엔드: Python (FastAPI)
- 프론트엔드: React (Electron 내부)
- AI 모델: Google Gemini 2.0 API
- 데이터 저장: SQLite(로컬 캐시), NAS(영구 저장)
- 기타: Docker, 데이터 수집 라이브러리(feedparser, requests, BeautifulSoup, Scrapy 등)

## 시스템 아키텍처
알파 에이전트는 다음 주요 모듈로 구성됩니다:

알파 에이전트
├── 데이터 수집 모듈
│   ├── 멀티소스 크롤러 (RSS/웹 스크래핑/API 통합)
│   ├── 동적 날짜 필터
│   ├── API 백업 시스템
│   └── 저작권 준수 필터
│
├── 분석 & 주제 선정 모듈
│   ├── 통합 AI 파이프라인
│   ├── 정치 성향 분석기 (좌/우 스코어링)
│   ├── MZ 트렌드 분석기
│   └── 주제 클러스터링 엔진
│
├── 콘텐츠 생성 모듈
│   ├── 표준 기사 작성기
│   ├── MZ 기사 생성기 (인포그래픽/인터랙티브 포함)
│   ├── 다양한 유튜브 포맷 스크립트 생성기
│   └── 팩트체크 검증 레이어
│
└── 사용자 인터페이스
├── 대시보드 (주제 개요 및 트렌드 분석)
├── 주제 탐색기 (성향 분석 포함)
├── 고급 콘텐츠 편집기
└── 출판 관리자

## 개발 로드맵

### 1단계: 강화된 데이터 수집 시스템 (1-2주)

#### 멀티소스 크롤러 구축
개발 목표: 다양한 뉴스 소스에서 안정적으로 데이터를 수집하는 통합 시스템

- **RSS 크롤러 구현**:
  - 주요 언론사 RSS 피드 연결
  - 피드 데이터 정규화 및 중복 제거
  
- **웹 스크래핑 시스템**:
  - BeautifulSoup/Scrapy 기반 스크래퍼
  - JavaScript 렌더링 지원 (필요 시 Selenium/Playwright)
  - 반봇 감지 우회 메커니즘 (요청 타이밍, 헤더 변경)
  
- **뉴스 API 통합**:
  - Google News API, NewsAPI, GDELT 연결
  - API 키 관리 및 요청 할당량 모니터링
  - API 실패 시 자동 백업 소스 전환
  
- **저작권 준수 필터**:
  - CCL 라이선스 자동 감지
  - 원본 출처 메타데이터 보존
  - 인용 규칙 준수 확인

```python
# 멀티소스 크롤러 핵심 구조
class NewsCollector:
    def __init__(self, config):
        self.rss_crawler = RSSCrawler(config.rss_sources)
        self.web_scraper = WebScraper(
            javascript_support=config.enable_js_rendering,
            anti_bot_measures=config.enable_anti_bot
        )
        self.api_connectors = {
            "google": GoogleNewsAPI(config.api_keys.google),
            "newsapi": NewsAPI(config.api_keys.newsapi),
            "gdelt": GDELTConnector()
        }
        self.copyright_filter = CopyrightFilter()
        self.source_rotation = SourceRotationManager(
            sources=["rss", "web", "api"],
            priority_weights=[0.4, 0.3, 0.3]
        )
        
    async def collect_news(self, parameters):
        """
        다양한 소스에서 뉴스 수집 - 동적 소스 선택 및 오류 복구 메커니즘 포함
        """
        collected_items = []
        source_priorities = self.source_rotation.get_current_priorities()
        
        for source_type in source_priorities:
            try:
                if source_type == "rss":
                    items = await self.rss_crawler.fetch_latest(parameters)
                elif source_type == "web":
                    urls = self._generate_scrape_targets(parameters)
                    items = await self.web_scraper.scrape_urls(urls)
                elif source_type == "api":
                    api_name = self.source_rotation.select_best_api()
                    connector = self.api_connectors[api_name]
                    items = await connector.fetch_news(parameters)
                
                # 저작권 필터 적용
                filtered_items = self.copyright_filter.process(items)
                collected_items.extend(filtered_items)
                
                # 충분한 결과를 얻었으면 중단
                if len(collected_items) >= parameters.get("target_count", 50):
                    break
                    
            except Exception as e:
                logger.warning(f"Source {source_type} failed: {str(e)}")
                continue
        
        # 수집 결과 메타데이터 기록
        self._log_collection_results(collected_items)
        return self._normalize_and_deduplicate(collected_items)
        
    # 내부 메서드: 웹 스크래핑 대상 URL 생성
    def _generate_scrape_targets(self, parameters):
        # 구현 내용
        pass
    
    # 내부 메서드: 수집 데이터 정규화 및 중복 제거
    def _normalize_and_deduplicate(self, items):
        # 구현 내용
        pass

동적 날짜 및 컨텍스트 필터
개발 목표: 유연한 시간 범위 및 컨텍스트 기반 필터링 구현

스마트 날짜 필터:

최신 뉴스 우선 수집 (기본 24시간)
주제별 특성에 따른 동적 확장 (장기 이슈는 자동으로 더 넓은 범위)
중요도 기반 시간 가중치 (핵심 키워드에 더 넓은 시간 범위 적용)


컨텍스트 인지 필터:

주제 연관성 스코어링
의미론적 필터링 (단순 키워드 매칭 넘어서기)
최신/장기 이슈 분류 시스템



2단계: 통합 주제 분석 시스템 (2-3주)
단일 AI 파이프라인 구현
개발 목표: 하나의 Gemini 2.0 인스턴스를 효율적으로 활용하는 통합 파이프라인

통합 분석 프로세스:

단일 Gemini 인스턴스로 다양한 분석 작업 수행
작업 큐 및 우선순위 관리 시스템
프롬프트 템플릿으로 태스크 전환


스마트 키워드 추출:

주요 엔티티 및 키워드 식별
관련 검색어 자동 확장
정치적 맥락 인식 (국제/국내, 핵심 인물/단체)

# 통합 AI 파이프라인 핵심 구조
class GeminiPipeline:
    def __init__(self, api_key, config):
        self.gemini = GeminiConnector(api_key)  # 단일 Gemini 인스턴스
        self.prompt_templates = self._load_templates("templates/")
        self.task_queue = PriorityTaskQueue(max_size=100)
        self.processing_thread = None
        self.is_running = False
        
    def start(self):
        """파이프라인 처리 시작"""
        self.is_running = True
        self.processing_thread = threading.Thread(
            target=self._process_queue,
            daemon=True
        )
        self.processing_thread.start()
        
    def stop(self):
        """파이프라인 처리 중지"""
        self.is_running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=30)
        
    async def analyze_topic(self, news_items, analysis_type, callback=None):
        """주제 분석 작업 큐에 추가"""
        task_id = str(uuid.uuid4())
        
        # 작업 메타데이터 준비
        task = {
            "id": task_id,
            "type": analysis_type,  # "keyword_extraction", "topic_clustering", "bias_analysis" 등
            "data": {
                "news_items": self._prepare_items_for_analysis(news_items),
                "parameters": {"target": "중도층 및 MZ세대"}
            },
            "priority": self._calculate_priority(analysis_type, news_items),
            "callback": callback,
            "created_at": datetime.now()
        }
        
        # 큐에 작업 추가
        await self.task_queue.put(task)
        return task_id
        
    def _process_queue(self):
        """백그라운드에서 작업 큐 처리"""
        while self.is_running:
            try:
                task = self.task_queue.get(block=True, timeout=1)
                result = self._execute_task(task)
                
                # 결과 처리 및 콜백 호출
                if task["callback"]:
                    asyncio.create_task(task["callback"](result))
                    
            except queue.Empty:
                # 큐가 비어있으면 잠시 대기
                time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error processing task: {str(e)}")
                
    def _execute_task(self, task):
        """Gemini API를 사용해 작업 실행"""
        template = self.prompt_templates[task["type"]]
        prompt = template.format(**task["data"])
        
        # Gemini API 호출
        response = self.gemini.generate_content(prompt)
        
        # 응답 파싱 및 후처리
        return self._parse_gemini_response(response, task["type"])

정치 성향 및 MZ 관심도 분석
개발 목표: 중도적 관점과 MZ세대 관심도를 정량화하는 분석 시스템

정치 성향 스코어링:

좌/우 정치 성향 스펙트럼 분석
기사 문구, 관점 및 논조 평가
중도 지수 계산 및 시각화


MZ 관심도 분석:

소셜 미디어 트렌드 연동 (TikTok, Instagram 해시태그)
MZ 세대 키워드 및 관심사 데이터베이스
주제별 MZ 참여도 예측 점수

# 정치 성향 및 MZ 관심도 분석 모듈
class ContentAnalyzer:
    def __init__(self, gemini_pipeline):
        self.gemini = gemini_pipeline
        self.political_scale = PoliticalScaleAnalyzer()
        self.mz_trend_analyzer = MZTrendAnalyzer(
            refresh_interval=24,  # 트렌드 DB 갱신 주기(시간)
            trend_sources=["twitter", "tiktok", "instagram"]
        )
        
    async def analyze_content_bias(self, content):
        """콘텐츠의 정치적 성향 분석"""
        # 기본 키워드 및 구문 분석
        base_score = self.political_scale.calculate_base_score(content)
        
        # Gemini를 통한 고급 분석
        gemini_result = await self.gemini.analyze_topic(
            [content], 
            "political_bias_analysis"
        )
        
        # 결과 통합 및 정규화
        final_score = self._combine_scores(base_score, gemini_result)
        
        return {
            "left_right_score": final_score,  # -1.0(좌) ~ 1.0(우)
            "center_index": self._calculate_center_index(final_score),  # 0(극단) ~ 1.0(중도)
            "key_indicators": gemini_result.get("indicators", [])
        }
    
    async def analyze_mz_relevance(self, topic):
        """MZ세대 관심도 및 관련성 분석"""
        # 현재 트렌드와 키워드 매칭
        trend_score = self.mz_trend_analyzer.match_with_trends(topic)
        
        # Gemini를 통한 MZ 관심도 예측
        gemini_result = await self.gemini.analyze_topic(
            [topic],
            "mz_relevance_analysis"
        )
        
        # 결과 통합
        return {
            "mz_relevance_score": (trend_score + gemini_result.get("score", 0)) / 2,  # 0 ~ 1.0
            "trending_keywords": gemini_result.get("trending_keywords", []),
            "suggested_angles": gemini_result.get("suggested_angles", [])
        }

3단계: 고급 콘텐츠 생성 시스템 (3-4주)
다양한 콘텐츠 형식 생성기
개발 목표: 표준 기사, MZ 기사, 다양한 유튜브 포맷 스크립트 자동 생성

표준 기사 생성기:

저널리즘 원칙 준수 프롬프트
다양한 관점 통합 메커니즘
내부 구조화 (표제, 요약, 본문, 인용구 등)


MZ 세대 타겟 콘텐츠:

인포그래픽 생성 연동 (표/차트/그래픽 자동 생성)
인터랙티브 요소 통합 (퀴즈, 투표, 타임라인)
쉬운 용어와 시각적 스타일 가이드 적용


유튜브 포맷 다각화:

다양한 포맷 템플릿 (숏폼/롱폼/심층 분석)
시각 자료 지시사항 포함
시나리오 및 B-roll 가이드

# 콘텐츠 생성 모듈 핵심 구조
class ContentGenerator:
    def __init__(self, gemini_pipeline, config):
        self.gemini = gemini_pipeline
        self.config = config
        self.formats = {
            "standard_article": StandardArticleGenerator(gemini_pipeline),
            "mz_article": MZArticleGenerator(gemini_pipeline),
            "youtube_script": YouTubeScriptGenerator(gemini_pipeline),
            "infographic": InfographicGenerator(gemini_pipeline)
        }
        self.fact_checker = FactChecker()
        
    async def generate_content(self, topic, format_type, parameters=None):
        """특정 포맷의 콘텐츠 생성"""
        if format_type not in self.formats:
            raise ValueError(f"Unknown format type: {format_type}")
            
        # 해당 포맷 생성기 호출
        generator = self.formats[format_type]
        content = await generator.generate(topic, parameters)
        
        # 팩트 체크 적용
        if self.config.enable_fact_checking:
            content = await self.fact_checker.verify(content)
            
        return content

# MZ 타겟 콘텐츠 생성기 예시
class MZArticleGenerator:
    def __init__(self, gemini_pipeline):
        self.gemini = gemini_pipeline
        self.interactive_elements = InteractiveElementsGenerator()
        self.infographic_generator = InfographicGenerator()
        
    async def generate(self, topic, parameters=None):
        """MZ 타겟 기사 생성"""
        params = parameters or {}
        
        # 기본 기사 내용 생성
        content = await self.gemini.analyze_topic(
            topic,
            "generate_mz_article"
        )
        
        # 인터랙티브 요소 추가
        if params.get("add_interactive", True):
            interactive = await self.interactive_elements.generate(
                topic, 
                params.get("interactive_types", ["quiz", "poll"])
            )
            content["interactive_elements"] = interactive
            
        # 인포그래픽 추가
        if params.get("add_infographic", True):
            infographic = await self.infographic_generator.generate(
                topic,
                params.get("infographic_type", "chart")
            )
            content["infographics"] = infographic
            
        return content

팩트체크 및 품질 검증 시스템
개발 목표: AI 콘텐츠의 정확성과 품질을 보장하는 검증 레이어

자동 팩트체크 시스템:

주요 주장 추출 및 검증
외부 팩트체크 API 연동
인용구 및 출처 확인


품질 검증 레이어:

콘텐츠 타겟 준수 검증 (중도성/MZ 친화성)
가독성 및 톤 검사
문법 및 스타일 교정

# 팩트체크 시스템 예시
class FactChecker:
    def __init__(self):
        self.claim_extractor = ClaimExtractor()
        self.external_checkers = {
            "mediabias": MediaBiasFactCheckAPI(),
            "google": GoogleFactCheckAPI()
        }
        
    async def verify(self, content):
        """콘텐츠 팩트체크 수행"""
        # 주요 주장 추출
        claims = self.claim_extractor.extract(content["body"])
        
        # 각 주장 검증
        verification_results = []
        for claim in claims:
            result = await self._verify_claim(claim)
            verification_results.append(result)
            
        # 팩트체크 결과 콘텐츠에 추가
        content["fact_check"] = {
            "verified_claims": len(verification_results),
            "accuracy_score": self._calculate_accuracy(verification_results),
            "warnings": self._extract_warnings(verification_results),
            "detailed_results": verification_results
        }
        
        return content
        
    async def _verify_claim(self, claim):
        """개별 주장 검증"""
        results = {}
        
        # 여러 외부 팩트체크 서비스 사용
        for name, checker in self.external_checkers.items():
            try:
                results[name] = await checker.check_claim(claim)
            except Exception as e:
                logger.warning(f"Fact checker {name} failed: {str(e)}")
                
        # 결과 통합 및 신뢰도 점수 계산
        return self._combine_check_results(claim, results)

4단계: 통합 사용자 인터페이스 (2-3주)
탭 기반 통합 UI
개발 목표: 직관적이고 효율적인 워크플로우를 지원하는 UI 설계

대시보드:

실시간 뉴스 트렌드 및 주제 제안
정치 성향 및 MZ 관심도 시각화
콘텐츠 성과 통계


주제 탐색 및 분석:

관련 주제 클러스터 시각화
좌/우 성향 및 MZ 관심도 필터
소스 및 관련 뉴스 탐색


콘텐츠 에디터:

기사/MZ 버전/유튜브 스크립트 통합 편집
인포그래픽 및 인터랙티브 요소 편집기
팩트체크 결과 표시 및 수정 제안

// 메인 인터페이스 컴포넌트 (React)
import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import { 
  AppBar, Tabs, Tab, Box, Typography, Drawer, List,
  ListItem, ListItemIcon, ListItemText, IconButton
} from '@material-ui/core';
import {
  Dashboard as DashboardIcon,
  Search as SearchIcon,
  Edit as EditIcon,
  Publish as PublishIcon,
  Settings as SettingsIcon,
  Menu as MenuIcon
} from '@material-ui/icons';

// 탭 컴포넌트 임포트
import Dashboard from './components/Dashboard';
import TopicExplorer from './components/TopicExplorer';
import ContentEditor from './components/ContentEditor';
import PublishManager from './components/PublishManager';
import SettingsPanel from './components/SettingsPanel';

// 테마 설정
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
});

const MainInterface = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [currentContent, setCurrentContent] = useState(null);
  
  // 탭 변경 핸들러
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  // 사이드 드로어 토글
  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };
  
  // 주제 선택 핸들러
  const handleTopicSelect = (topic) => {
    setSelectedTopic(topic);
    setActiveTab(1); // 주제 탐색 탭으로 이동
  };
  
  // 콘텐츠 생성 핸들러
  const handleContentCreate = (topic, contentType) => {
    // API 호출해서 콘텐츠 생성 요청
    fetch('/api/alpha/content/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        topicId: topic.id,
        contentType: contentType,
      }),
    })
    .then(response => response.json())
    .then(data => {
      setCurrentContent(data);
      setActiveTab(2); // 콘텐츠 편집 탭으로 이동
    })
    .catch(error => {
      console.error('Error creating content:', error);
    });
  };
  
  // 탭 내용 렌더링
  const renderTabContent = () => {
    switch (activeTab) {
      case 0:
        return <Dashboard onTopicSelect={handleTopicSelect} />;
      case 1:
        return (
          <TopicExplorer 
            selectedTopic={selectedTopic}
            onContentCreate={handleContentCreate}
          />
        );
      case 2:
        return (
          <ContentEditor 
            content={currentContent}
            onContentUpdate={setCurrentContent}
            onPublish={() => setActiveTab(3)}
          />
        );
      case 3:
        return <PublishManager />;
      case 4:
        return <SettingsPanel />;
      default:
        return <div>Tab content not found</div>;
    }
  };
  
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className="alpha-agent-interface">
        <AppBar position="static">
          <Tabs 
            value={activeTab} 
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab label="대시보드" icon={<DashboardIcon />} />
            <Tab label="주제 탐색" icon={<SearchIcon />} />
            <Tab label="콘텐츠 편집" icon={<EditIcon />} />
            <Tab label="출판 관리" icon={<PublishIcon />} />
            <Tab label="설정" icon={<SettingsIcon />} />
          </Tabs>
        </AppBar>
        
        <Box p={3}>
          {renderTabContent()}
        </Box>
      </div>
    </ThemeProvider>
  );
};

export default MainInterface;

저작권 및 오류 대응 시스템
저작권 준수 시스템
개발 목표: 법적 문제 없는 콘텐츠 재가공 및 원본 출처 관리

자동 인용 시스템:

원본 출처 추적 및 메타데이터 보존
인용 형식 자동 적용
저작권 라이선스 확인 및 준수


트래픽 환원 시스템:

원본 링크 자동 추가
원본 출처 강조 표시
인용량 모니터링 및 공정 이용 준수



오류 방지 및 복구 시스템
개발 목표: AI 오류 누적 방지 및 신속한 문제 복구

다단계 검증 절차:

각 처리 단계별 사용자 검토 포인트
자동 오류 감지 알고리즘
이전 단계로 롤백 기능


안정성 보장 장치:

자동 백업 및 버전 관리
장애 복구 프로토콜
로그 기반 문제 진단 시스템



구현 우선순위 및 개발 전략

핵심 데이터 파이프라인 구축 (최우선)

멀티소스 크롤러 → 주제 분석 → 콘텐츠 생성 파이프라인


사용자 인터페이스 프레임워크

기본 탭 구조 및 워크플로우 설계 → 세부 기능 점진적 추가


주요 알고리즘 구현

주제 클러스터링 → 정치 성향 분석 → MZ 관심도 평가


콘텐츠 생성 시스템

표준 기사 → MZ 기사 → 유튜브 스크립트 (순차적 개발)


검증 및 안전 시스템

팩트체크 → 저작권 관리 → 오류 복구 메커니즘



개발 시 주의사항

모듈식 설계 유지: 기능별 독립 모듈로 개발하여 확장성 보장
프롬프트 엔지니어링 중요성: Gemini API 활용 효율 극대화를 위한 최적화
NAS 연결 최적화: 대용량 데이터 처리 시 성능 고려
점진적 기능 추가: 핵심 기능부터 구현 후 고급 기능 단계적 확장
사용자 검토 포인트: 완전 자동화보다 사용자 개입 지점 적절히 배치

프로젝트를 단계적으로 구현하면서 각 모듈의 성능과 신뢰성을 지속적으로 평가하고 개선해 나가야 합니다.