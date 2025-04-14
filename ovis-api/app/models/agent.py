from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

# 에이전트 상태 열거형
class AgentStatus(str, Enum):
    IDLE = "idle"
    LOADING = "loading"
    RUNNING = "running"
    ERROR = "error"
    INACTIVE = "inactive"

# 에이전트 설정 모델
class AgentConfig(BaseModel):
    name: str
    description: str = ""
    version: str = "1.0.0"
    model_path: str
    parameters: Dict[str, Any] = {}
    memory_requirement: str = "1GB"
    cuda_required: bool = False

# 에이전트 모델
class Agent(BaseModel):
    id: str
    name: str
    type: str
    description: str = ""
    status: AgentStatus = AgentStatus.INACTIVE
    config: AgentConfig
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_active: Optional[datetime] = None
    metrics: Dict[str, Any] = {}

    class Config:
        use_enum_values = True

# 에이전트 생성 요청 모델
class AgentCreate(BaseModel):
    name: str
    type: str
    description: str = ""
    config: AgentConfig

# 에이전트 업데이트 요청 모델
class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

# 에이전트 목록 응답 모델
class AgentList(BaseModel):
    agents: List[Agent]
    count: int
    
# 에이전트 작업 모델
class AgentTask(BaseModel):
    id: str
    agent_id: str
    task_type: str
    parameters: Dict[str, Any] = {}
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None 