import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiClient } from '../../utils/api';

// 에이전트 상태 타입
export type AgentStatus = 'idle' | 'loading' | 'running' | 'error' | 'inactive';

// 에이전트 타입
export interface Agent {
  id: string;
  name: string;
  type: string;
  description: string;
  status: AgentStatus;
  config: any;
  created_at: string;
  updated_at: string;
  last_active: string | null;
  metrics: Record<string, any>;
}

// 상태 인터페이스
interface AgentsState {
  items: Agent[];
  selectedAgent: Agent | null;
  loading: boolean;
  error: string | null;
}

// 초기 상태
const initialState: AgentsState = {
  items: [],
  selectedAgent: null,
  loading: false,
  error: null,
};

// 비동기 액션: 에이전트 목록 로드
export const fetchAgents = createAsyncThunk('agents/fetchAgents', async (_, { rejectWithValue }) => {
  try {
    const response = await apiClient.get('/api/v1/agents');
    return response.data.agents;
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || '에이전트 목록을 가져오지 못했습니다.');
  }
});

// 비동기 액션: 특정 에이전트 로드
export const fetchAgentById = createAsyncThunk(
  'agents/fetchAgentById',
  async (agentId: string, { rejectWithValue }) => {
    try {
      const response = await apiClient.get(`/api/v1/agents/${agentId}`);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '에이전트 정보를 가져오지 못했습니다.');
    }
  }
);

// 비동기 액션: 에이전트 시작
export const startAgent = createAsyncThunk(
  'agents/startAgent',
  async (agentId: string, { rejectWithValue }) => {
    try {
      const response = await apiClient.post(`/api/v1/agents/${agentId}/start`);
      return { agentId, status: 'running' as AgentStatus };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '에이전트를 시작하지 못했습니다.');
    }
  }
);

// 비동기 액션: 에이전트 중지
export const stopAgent = createAsyncThunk(
  'agents/stopAgent',
  async (agentId: string, { rejectWithValue }) => {
    try {
      const response = await apiClient.post(`/api/v1/agents/${agentId}/stop`);
      return { agentId, status: 'idle' as AgentStatus };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '에이전트를 중지하지 못했습니다.');
    }
  }
);

// 슬라이스 생성
const agentsSlice = createSlice({
  name: 'agents',
  initialState,
  reducers: {
    // 선택된 에이전트 설정
    setSelectedAgent: (state, action: PayloadAction<Agent | null>) => {
      state.selectedAgent = action.payload;
    },
    
    // 에이전트 상태 업데이트
    updateAgentStatus: (state, action: PayloadAction<{ agentId: string; status: AgentStatus }>) => {
      const index = state.items.findIndex((agent) => agent.id === action.payload.agentId);
      if (index !== -1) {
        state.items[index].status = action.payload.status;
      }
      
      if (state.selectedAgent?.id === action.payload.agentId) {
        state.selectedAgent.status = action.payload.status;
      }
    },
    
    // 에러 초기화
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // 에이전트 목록 로드
    builder
      .addCase(fetchAgents.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAgents.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchAgents.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
    // 특정 에이전트 로드
    builder
      .addCase(fetchAgentById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAgentById.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedAgent = action.payload;
        
        // 목록에 있는 에이전트도 업데이트
        const index = state.items.findIndex((agent) => agent.id === action.payload.id);
        if (index !== -1) {
          state.items[index] = action.payload;
        }
      })
      .addCase(fetchAgentById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
    // 에이전트 시작
    builder
      .addCase(startAgent.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(startAgent.fulfilled, (state, action) => {
        state.loading = false;
        const { agentId, status } = action.payload;
        
        // 에이전트 상태 업데이트
        const index = state.items.findIndex((agent) => agent.id === agentId);
        if (index !== -1) {
          state.items[index].status = status;
        }
        
        if (state.selectedAgent?.id === agentId) {
          state.selectedAgent.status = status;
        }
      })
      .addCase(startAgent.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
    // 에이전트 중지
    builder
      .addCase(stopAgent.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(stopAgent.fulfilled, (state, action) => {
        state.loading = false;
        const { agentId, status } = action.payload;
        
        // 에이전트 상태 업데이트
        const index = state.items.findIndex((agent) => agent.id === agentId);
        if (index !== -1) {
          state.items[index].status = status;
        }
        
        if (state.selectedAgent?.id === agentId) {
          state.selectedAgent.status = status;
        }
      })
      .addCase(stopAgent.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

// 액션 생성자 내보내기
export const { setSelectedAgent, updateAgentStatus, clearError } = agentsSlice.actions;

// 리듀서 내보내기
export default agentsSlice.reducer; 