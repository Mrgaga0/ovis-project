from fastapi import APIRouter, HTTPException, Depends, Path, Query
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime

from ..config import get_settings
from ..models.agent import Agent, AgentCreate, AgentUpdate, AgentList, AgentStatus, AgentTask
from ..core.nas_manager import NASManager
from ..agents.alpha import AlphaAgent

router = APIRouter()
settings = get_settings()

# 가상 데이터 저장소 (실제 구현에서는 데이터베이스 사용)
agents_db = {}
agent_instances = {}

# NAS 경로와 디렉토리 구조로 NAS 관리자 초기화
nas_manager = NASManager(settings.nas.path, settings.nas.directory_structure)

@router.get("/", response_model=AgentList)
async def get_agents():
    """사용 가능한 모든 에이전트 목록 조회"""
    return {
        "agents": list(agents_db.values()),
        "count": len(agents_db)
    }

@router.post("/", response_model=Agent)
async def create_agent(agent_data: AgentCreate):
    """새 에이전트 생성"""
    agent_id = str(uuid.uuid4())
    
    # 모델 경로 확인
    model_path = nas_manager.get_model_path(agent_data.type) / agent_data.config.model_path
    
    # 새 에이전트 생성
    new_agent = Agent(
        id=agent_id,
        name=agent_data.name,
        type=agent_data.type,
        description=agent_data.description,
        status=AgentStatus.INACTIVE,
        config=agent_data.config,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    
    # 저장
    agents_db[agent_id] = new_agent
    return new_agent

@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str = Path(..., description="에이전트 ID")):
    """특정 에이전트 정보 조회"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="에이전트를 찾을 수 없습니다")
    
    return agents_db[agent_id]

@router.put("/{agent_id}", response_model=Agent)
async def update_agent(
    update_data: AgentUpdate, 
    agent_id: str = Path(..., description="에이전트 ID")
):
    """에이전트 정보 업데이트"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="에이전트를 찾을 수 없습니다")
    
    agent = agents_db[agent_id]
    
    # 업데이트 적용
    if update_data.name is not None:
        agent.name = update_data.name
    
    if update_data.description is not None:
        agent.description = update_data.description
    
    if update_data.config is not None:
        # 설정 업데이트 (실제 구현에서는 더 복잡한 병합 필요)
        for key, value in update_data.config.items():
            setattr(agent.config, key, value)
    
    agent.updated_at = datetime.now()
    return agent

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str = Path(..., description="에이전트 ID")):
    """에이전트 삭제"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="에이전트를 찾을 수 없습니다")
    
    # 삭제 전 실행 중지 확인
    agent = agents_db[agent_id]
    if agent.status in [AgentStatus.RUNNING, AgentStatus.LOADING]:
        raise HTTPException(status_code=400, detail="실행 중인 에이전트는 삭제할 수 없습니다")
    
    # 인스턴스가 있다면 제거
    if agent_id in agent_instances:
        del agent_instances[agent_id]
    
    # 데이터베이스에서 삭제
    del agents_db[agent_id]
    return {"message": "에이전트가 삭제되었습니다", "agent_id": agent_id}

@router.post("/{agent_id}/start")
async def start_agent(agent_id: str = Path(..., description="에이전트 ID")):
    """에이전트 시작"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="에이전트를 찾을 수 없습니다")
    
    agent = agents_db[agent_id]
    
    # 이미 실행 중인 경우
    if agent.status in [AgentStatus.RUNNING, AgentStatus.LOADING]:
        return {"message": "에이전트가 이미 실행 중입니다", "agent_id": agent_id}
    
    try:
        # 에이전트 유형에 따라 적절한 인스턴스 생성 및 시작
        if agent.type == "alpha":
            if agent_id not in agent_instances:
                # 새 인스턴스 생성
                agent_instances[agent_id] = AlphaAgent(agent_id, agent.config)
                
            # 에이전트 시작
            alpha_agent = agent_instances[agent_id]
            success = await alpha_agent.start()
            
            if success:
                # 상태 업데이트
                agent.status = alpha_agent.status
                agent.last_active = datetime.now()
                return {"message": "알파 에이전트가 시작되었습니다", "agent_id": agent_id}
            else:
                raise HTTPException(status_code=500, detail="알파 에이전트 시작 실패")
        else:
            # 지원하지 않는 에이전트 유형
            raise HTTPException(status_code=400, detail=f"지원하지 않는 에이전트 유형: {agent.type}")
            
    except Exception as e:
        # 오류 발생 시 에러 상태로 업데이트
        agent.status = AgentStatus.ERROR
        raise HTTPException(status_code=500, detail=f"에이전트 시작 중 오류 발생: {str(e)}")

@router.post("/{agent_id}/stop")
async def stop_agent(agent_id: str = Path(..., description="에이전트 ID")):
    """에이전트 중지"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="에이전트를 찾을 수 없습니다")
    
    agent = agents_db[agent_id]
    
    # 실행 중이 아닌 경우
    if agent.status not in [AgentStatus.RUNNING, AgentStatus.LOADING]:
        return {"message": "에이전트가 이미 중지되었습니다", "agent_id": agent_id}
    
    try:
        # 인스턴스가 있는 경우 중지
        if agent_id in agent_instances:
            instance = agent_instances[agent_id]
            await instance.stop()
            
            # 상태 업데이트
            agent.status = instance.status
            return {"message": "에이전트가 중지되었습니다", "agent_id": agent_id}
        else:
            # 인스턴스가 없는 경우 - 상태만 업데이트
            agent.status = AgentStatus.IDLE
            return {"message": "에이전트가 중지되었습니다 (인스턴스 없음)", "agent_id": agent_id}
            
    except Exception as e:
        # 오류 발생 시 에러 상태로 업데이트
        agent.status = AgentStatus.ERROR
        raise HTTPException(status_code=500, detail=f"에이전트 중지 중 오류 발생: {str(e)}")

@router.post("/{agent_id}/execute", response_model=AgentTask)
async def execute_agent_task(
    task_data: Dict[str, Any],
    agent_id: str = Path(..., description="에이전트 ID")
):
    """에이전트 작업 실행"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="에이전트를 찾을 수 없습니다")
    
    agent = agents_db[agent_id]
    
    # 에이전트가 실행 중이 아닌 경우
    if agent.status != AgentStatus.RUNNING:
        raise HTTPException(status_code=400, detail="에이전트가 실행 중이 아닙니다")
    
    # 인스턴스 확인
    if agent_id not in agent_instances:
        raise HTTPException(status_code=500, detail="에이전트 인스턴스를 찾을 수 없습니다")
    
    # 작업 생성
    task_id = str(uuid.uuid4())
    task_type = task_data.get("type", "default")
    parameters = task_data.get("parameters", {})
    
    # 샘플 작업 생성
    task = AgentTask(
        id=task_id,
        agent_id=agent_id,
        task_type=task_type,
        parameters=parameters,
        status="pending",
        created_at=datetime.now()
    )
    
    try:
        # 알파 에이전트 작업 실행
        instance = agent_instances[agent_id]
        
        if agent.type == "alpha":
            # 작업 유형에 따라 적절한 메서드 호출
            if task_type == "collect_news":
                # 작업 상태 업데이트
                task.status = "processing"
                task.started_at = datetime.now()
                
                # 뉴스 수집 작업 실행
                result = await instance.collect_news(parameters)
                
                # 작업 완료 업데이트
                task.status = "completed"
                task.completed_at = datetime.now()
                task.result = {"collected_count": len(result), "first_items": result[:5]}
                
            elif task_type == "analyze_topics":
                # 분석할 뉴스 데이터 필요
                if "news_items" not in parameters:
                    raise HTTPException(status_code=400, detail="news_items 파라미터가 필요합니다")
                    
                # 작업 상태 업데이트
                task.status = "processing"
                task.started_at = datetime.now()
                
                # 주제 분석 작업 실행
                analysis_type = parameters.get("analysis_type", "default")
                result = await instance.analyze_topics(parameters["news_items"], analysis_type)
                
                # 작업 완료 업데이트
                task.status = "completed"
                task.completed_at = datetime.now()
                task.result = {"analysis_result": result}
                
            elif task_type == "generate_content":
                # 주제 및 포맷 정보 필요
                if "topic" not in parameters or "format_type" not in parameters:
                    raise HTTPException(status_code=400, detail="topic 및 format_type 파라미터가 필요합니다")
                    
                # 작업 상태 업데이트
                task.status = "processing"
                task.started_at = datetime.now()
                
                # 콘텐츠 생성 작업 실행
                topic = parameters["topic"]
                format_type = parameters["format_type"]
                format_params = parameters.get("format_parameters", {})
                
                content = await instance.generate_content(topic, format_type, format_params)
                
                # 작업 완료 업데이트
                task.status = "completed"
                task.completed_at = datetime.now()
                task.result = {"content_id": content.get("id"), "format": format_type}
                
            else:
                # 지원하지 않는 작업 유형
                raise HTTPException(status_code=400, detail=f"지원하지 않는 작업 유형: {task_type}")
                
        else:
            # 지원하지 않는 에이전트 유형
            raise HTTPException(status_code=400, detail=f"지원하지 않는 에이전트 유형: {agent.type}")
            
    except Exception as e:
        # 작업 실패 처리
        task.status = "failed"
        task.error = str(e)
        raise HTTPException(status_code=500, detail=f"작업 실행 중 오류 발생: {str(e)}")
    
    return task

@router.get("/{agent_id}/status")
async def get_agent_status(agent_id: str = Path(..., description="에이전트 ID")):
    """에이전트 상태 조회"""
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="에이전트를 찾을 수 없습니다")
    
    agent = agents_db[agent_id]
    
    # 실제 인스턴스에서 최신 상태 가져오기
    if agent_id in agent_instances:
        instance = agent_instances[agent_id]
        status_info = instance.get_status()
        
        # DB에 저장된 에이전트 정보 업데이트
        agent.status = status_info["status"]
        agent.last_active = status_info["last_active"]
        agent.metrics = status_info["metrics"]
    
    return {
        "agent_id": agent_id,
        "name": agent.name,
        "type": agent.type,
        "status": agent.status,
        "last_active": agent.last_active,
        "metrics": agent.metrics
    }

# 알파 에이전트 특화 엔드포인트
@router.get("/types/alpha/templates")
async def get_alpha_templates():
    """알파 에이전트 생성 템플릿 목록"""
    return {
        "templates": [
            {
                "name": "기본 알파 에이전트",
                "description": "국제/국내 정치 및 이슈 관련 언론 콘텐츠 제작 지원",
                "config": {
                    "name": "알파 에이전트 설정",
                    "description": "기본 설정",
                    "version": "1.0.0",
                    "model_path": "default",
                    "parameters": {
                        "gemini_api_key": "",
                        "rss_sources": [
                            "http://rss.donga.com/total.xml",
                            "https://rss.hankyung.com/feed/headline.xml",
                            "https://www.hani.co.kr/rss/",
                            "https://rss.joins.com/joins_news_list.xml"
                        ],
                        "api_keys": {
                            "newsapi": ""
                        },
                        "enable_js_rendering": False,
                        "enable_anti_bot": True,
                        "political_analyzer_enabled": True,
                        "mz_analyzer_enabled": True,
                        "enable_fact_checking": True,
                        "formats": ["standard", "mz", "youtube"]
                    },
                    "memory_requirement": "2GB",
                    "cuda_required": False
                }
            }
        ]
    }

@router.post("/alpha/quick-setup", response_model=Agent)
async def quick_setup_alpha():
    """알파 에이전트 빠른 설정"""
    # 기본 설정으로 알파 에이전트 생성
    agent_id = str(uuid.uuid4())
    
    # 기본 설정
    config = {
        "name": "알파 에이전트 설정",
        "description": "기본 설정",
        "version": "1.0.0",
        "model_path": "default",
        "parameters": {
            "gemini_api_key": "YOUR_API_KEY_HERE",  # 실제 구현에서는 환경 변수 등에서 가져와야 함
            "rss_sources": [
                "http://rss.donga.com/total.xml",
                "https://rss.hankyung.com/feed/headline.xml",
                "https://www.hani.co.kr/rss/",
                "https://rss.joins.com/joins_news_list.xml"
            ],
            "api_keys": {},
            "enable_js_rendering": False,
            "enable_anti_bot": True,
            "political_analyzer_enabled": True,
            "mz_analyzer_enabled": True,
            "enable_fact_checking": True,
            "formats": ["standard", "mz", "youtube"]
        },
        "memory_requirement": "2GB",
        "cuda_required": False
    }
    
    # 새 에이전트 생성
    new_agent = Agent(
        id=agent_id,
        name="알파 에이전트",
        type="alpha",
        description="국제/국내 정치 및 이슈 관련 언론 콘텐츠 제작 지원 에이전트",
        status=AgentStatus.INACTIVE,
        config=config,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    
    # 저장
    agents_db[agent_id] = new_agent
    return new_agent 