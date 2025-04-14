import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiClient } from '../../utils/api';

// 로그 항목 인터페이스
export interface LogItem {
  timestamp: string;
  level: string;
  message: string;
  name?: string;
  module?: string;
  function?: string;
  line?: number;
  exception?: {
    type: string;
    message: string;
    traceback: string[];
  };
  data?: any;
  raw?: string;
}

// 로그 파일 인터페이스
export interface LogFile {
  name: string;
  path: string;
  type: string;
  size?: number;
  log_type?: string;
  full_path?: string;
}

// 로그 상태 인터페이스
interface LogsState {
  items: LogItem[];
  files: LogFile[];
  selectedFile: string | null;
  loading: boolean;
  error: string | null;
  filters: {
    level: string | null;
    startDate: string | null;
    endDate: string | null;
    logType: string;
    search: string;
  };
}

// 초기 상태
const initialState: LogsState = {
  items: [],
  files: [],
  selectedFile: null,
  loading: false,
  error: null,
  filters: {
    level: null,
    startDate: null,
    endDate: null,
    logType: 'system',
    search: '',
  },
};

// 비동기 액션: 로그 목록 로드
export const fetchLogs = createAsyncThunk(
  'logs/fetchLogs',
  async (params: {
    log_type?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
    level?: string;
  }, { rejectWithValue }) => {
    try {
      const response = await apiClient.get('/api/v1/logs', { params });
      return response.data.logs;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '로그 데이터를 가져오지 못했습니다.');
    }
  }
);

// 비동기 액션: 로그 파일 목록 로드
export const fetchLogFiles = createAsyncThunk(
  'logs/fetchLogFiles',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get('/api/v1/logs/files');
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '로그 파일 목록을 가져오지 못했습니다.');
    }
  }
);

// 비동기 액션: 특정 로그 파일 내용 로드
export const fetchLogFile = createAsyncThunk(
  'logs/fetchLogFile',
  async (path: string, { rejectWithValue }) => {
    try {
      const response = await apiClient.get('/api/v1/logs/file', { params: { path } });
      return {
        logs: response.data.logs,
        path,
      };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '로그 파일 내용을 가져오지 못했습니다.');
    }
  }
);

// 슬라이스 생성
const logsSlice = createSlice({
  name: 'logs',
  initialState,
  reducers: {
    // 로그 필터 설정
    setLogFilters: (state, action: PayloadAction<Partial<LogsState['filters']>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    
    // 선택된 로그 파일 설정
    setSelectedLogFile: (state, action: PayloadAction<string | null>) => {
      state.selectedFile = action.payload;
    },
    
    // 수동으로 로그 항목 설정 (예: 실시간 로그)
    setLogs: (state, action: PayloadAction<LogItem[]>) => {
      state.items = action.payload;
    },
    
    // 로그 항목 추가 (실시간 로그)
    addLogItem: (state, action: PayloadAction<LogItem>) => {
      state.items.unshift(action.payload); // 가장 최근 로그를 앞에 추가
      
      // 로그 항목이 너무 많으면 오래된 것부터 제거
      if (state.items.length > 1000) {
        state.items = state.items.slice(0, 1000);
      }
    },
    
    // 로그 초기화
    clearLogs: (state) => {
      state.items = [];
    },
    
    // 에러 초기화
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // 로그 목록 로드
    builder
      .addCase(fetchLogs.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchLogs.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchLogs.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
    
    // 로그 파일 목록 로드
    builder
      .addCase(fetchLogFiles.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchLogFiles.fulfilled, (state, action) => {
        state.loading = false;
        state.files = action.payload;
      })
      .addCase(fetchLogFiles.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
    
    // 특정 로그 파일 내용 로드
    builder
      .addCase(fetchLogFile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchLogFile.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload.logs;
        state.selectedFile = action.payload.path;
      })
      .addCase(fetchLogFile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
  },
});

// 액션 생성자 내보내기
export const {
  setLogFilters,
  setSelectedLogFile,
  setLogs,
  addLogItem,
  clearLogs,
  clearError,
} = logsSlice.actions;

// 리듀서 내보내기
export default logsSlice.reducer; 