import { createSlice, PayloadAction } from '@reduxjs/toolkit';

// 시스템 상태 인터페이스
interface SystemState {
  apiStatus: {
    connected: boolean;
    version: string;
    error: string | null;
  };
  appInfo: {
    version: string;
    platform: string;
    nodeVersion: string;
    electronVersion: string;
  } | null;
  isInitialized: boolean;
  darkMode: boolean;
  settings: {
    nasPath: string;
    apiUrl: string;
  };
}

// 초기 상태
const initialState: SystemState = {
  apiStatus: {
    connected: false,
    version: '',
    error: null,
  },
  appInfo: null,
  isInitialized: false,
  darkMode: false,
  settings: {
    nasPath: '',
    apiUrl: 'http://localhost:8000',
  },
};

// 슬라이스 생성
const systemSlice = createSlice({
  name: 'system',
  initialState,
  reducers: {
    // API 상태 설정
    setApiStatus: (state, action: PayloadAction<{ connected: boolean; version?: string; error?: string }>) => {
      state.apiStatus.connected = action.payload.connected;
      if (action.payload.version) state.apiStatus.version = action.payload.version;
      state.apiStatus.error = action.payload.error || null;
    },
    
    // 앱 정보 설정
    setAppInfo: (state, action: PayloadAction<SystemState['appInfo']>) => {
      state.appInfo = action.payload;
    },
    
    // 초기화 상태 변경
    setInitialized: (state, action: PayloadAction<boolean>) => {
      state.isInitialized = action.payload;
    },
    
    // 다크 모드 전환
    toggleDarkMode: (state) => {
      state.darkMode = !state.darkMode;
    },
    
    // NAS 경로 설정
    setNasPath: (state, action: PayloadAction<string>) => {
      state.settings.nasPath = action.payload;
    },
    
    // API URL 설정
    setApiUrl: (state, action: PayloadAction<string>) => {
      state.settings.apiUrl = action.payload;
    },
  },
});

// 액션 생성자 내보내기
export const {
  setApiStatus,
  setAppInfo,
  setInitialized,
  toggleDarkMode,
  setNasPath,
  setApiUrl,
} = systemSlice.actions;

// 리듀서 내보내기
export default systemSlice.reducer; 