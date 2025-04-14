import axios, { AxiosRequestConfig, AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios';

// 환경 타입 정의를 위한 전역 인터페이스 확장
declare global {
  interface Window {
    process?: any;
    electron?: any;
  }
}

// API 기본 URL 설정 (환경에 따라 다름)
export const getApiBaseUrl = () => {
  // 개발 환경에서는 localhost:3002를 사용
  // 프로덕션 환경(Docker)에서는 상대 경로 사용
  
  // 환경 변수가 설정되어 있으면 그것을 사용
  if (typeof window !== 'undefined' && window.process && window.process.env && window.process.env.REACT_APP_API_URL) {
    return window.process.env.REACT_APP_API_URL;
  }
  
  // NODE_ENV가 production인 경우 상대 경로 사용
  if (typeof window !== 'undefined' && window.process && window.process.env && window.process.env.NODE_ENV === 'production') {
    // Docker 환경에서는 상대 경로를 사용 (Nginx가 프록시)
    return '/api';
  }
  
  // 로컬 스토리지에서 저장된 URL 가져오기 또는 기본값 사용
  const savedUrl = localStorage.getItem('apiUrl');
  if (savedUrl) {
    return savedUrl;
  }
  
  // 기본값: localhost:3002
  return 'http://localhost:3002';
};

// API 클라이언트 설정
export const apiClient = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
    // API 기본 URL 업데이트 (설정이 변경된 경우)
    config.baseURL = getApiBaseUrl();
    
    // JWT 토큰이 있으면 헤더에 추가
    const token = localStorage.getItem('auth_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error: AxiosError) => {
    // 요청 에러 처리
    return Promise.reject(error);
  }
);

// 응답 인터셉터
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // 응답 데이터 처리
    return response;
  },
  (error: AxiosError) => {
    // 응답 에러 처리
    if (error.response) {
      // 서버가 응답을 반환한 경우 (4xx, 5xx)
      console.error('API 에러:', error.response.data);
      
      // 401 Unauthorized - 인증 토큰 만료 또는 유효하지 않음
      if (error.response.status === 401) {
        localStorage.removeItem('auth_token');
        // 로그인 페이지로 리디렉션 또는 다른 처리
      }
    } else if (error.request) {
      // 요청이 전송되었으나 응답이 없는 경우
      console.error('API 요청 에러: 응답 없음');
    } else {
      // 요청 설정 중 에러 발생
      console.error('API 설정 에러:', error.message);
    }
    return Promise.reject(error);
  }
);

// 유틸리티 함수

// API 요청 타입
export interface ApiResponse<T> {
  data: T;
  status: number;
  statusText: string;
}

// 기본 API 함수
export const api = {
  // 에이전트 관련 API
  agents: {
    getAll: async () => {
      return await apiClient.get('/api/v1/agents');
    },
    
    getById: async (id: string) => {
      return await apiClient.get(`/api/v1/agents/${id}`);
    },
    
    create: async (data: any) => {
      return await apiClient.post('/api/v1/agents', data);
    },
    
    update: async (id: string, data: any) => {
      return await apiClient.put(`/api/v1/agents/${id}`, data);
    },
    
    delete: async (id: string) => {
      return await apiClient.delete(`/api/v1/agents/${id}`);
    },
    
    start: async (id: string) => {
      return await apiClient.post(`/api/v1/agents/${id}/start`);
    },
    
    stop: async (id: string) => {
      return await apiClient.post(`/api/v1/agents/${id}/stop`);
    },
    
    status: async (id: string) => {
      return await apiClient.get(`/api/v1/agents/${id}/status`);
    },
    
    execute: async (id: string, task: any) => {
      return await apiClient.post(`/api/v1/agents/${id}/execute`, task);
    },
    
    quickSetupAlpha: async () => {
      return await apiClient.post('/api/v1/agents/alpha/quick-setup');
    },
    
    getAlphaTemplates: async () => {
      return await apiClient.get('/api/v1/agents/types/alpha/templates');
    },
  },
  
  // NAS 관련 API
  nas: {
    getStatus: async () => {
      return await apiClient.get('/api/v1/nas/status');
    },
    
    listFiles: async (path?: string) => {
      return await apiClient.get('/api/v1/nas/files', { params: { path } });
    },
    
    readFile: async (path: string) => {
      return await apiClient.get('/api/v1/nas/file', { params: { path } });
    },
    
    uploadFile: async (path: string, file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return await apiClient.post('/api/v1/nas/file', formData, {
        params: { path },
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    },
    
    deleteFile: async (path: string) => {
      return await apiClient.delete('/api/v1/nas/file', { params: { path } });
    },
    
    createDirectory: async (path: string) => {
      return await apiClient.post('/api/v1/nas/directory', null, { params: { path } });
    },
    
    listModels: async () => {
      return await apiClient.get('/api/v1/nas/models');
    },
  },
  
  // 로그 관련 API
  logs: {
    getLogs: async (params?: any) => {
      return await apiClient.get('/api/v1/logs', { params });
    },
    
    getLogFiles: async () => {
      return await apiClient.get('/api/v1/logs/files');
    },
    
    readLogFile: async (path: string) => {
      return await apiClient.get('/api/v1/logs/file', { params: { path } });
    },
    
    deleteLogFile: async (path: string) => {
      return await apiClient.delete('/api/v1/logs/file', { params: { path } });
    },
  },
  
  // 시스템 관련 API
  system: {
    getStatus: async () => {
      return await apiClient.get('/api/v1/status');
    },
    
    getSystemInfo: async () => {
      return await apiClient.get('/api/v1/system/info');
    },
  },
}; 