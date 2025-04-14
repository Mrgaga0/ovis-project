import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiClient } from '../../utils/api';

// 파일 타입 인터페이스
export interface FileItem {
  name: string;
  path: string;
  type: string;
  size?: number;
  agent_type?: string;
  full_path?: string;
}

// 모델 파일 인터페이스
export interface ModelFile extends FileItem {
  agent_type: string;
  full_path: string;
}

// NAS 상태 인터페이스
interface NasState {
  status: {
    connected: boolean;
    path: string;
    available_space: string;
  };
  currentPath: string;
  files: FileItem[];
  models: ModelFile[];
  selectedFile: FileItem | null;
  loading: boolean;
  error: string | null;
}

// 초기 상태
const initialState: NasState = {
  status: {
    connected: false,
    path: '',
    available_space: '',
  },
  currentPath: '',
  files: [],
  models: [],
  selectedFile: null,
  loading: false,
  error: null,
};

// 비동기 액션: NAS 상태 로드
export const fetchNasStatus = createAsyncThunk('nas/fetchStatus', async (_, { rejectWithValue }) => {
  try {
    const response = await apiClient.get('/api/v1/nas/status');
    return response.data;
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || 'NAS 상태를 가져오지 못했습니다.');
  }
});

// 비동기 액션: 파일 목록 로드
export const fetchFiles = createAsyncThunk(
  'nas/fetchFiles',
  async (path: string = '', { rejectWithValue }) => {
    try {
      const response = await apiClient.get('/api/v1/nas/files', { params: { path } });
      return {
        files: response.data,
        path,
      };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '파일 목록을 가져오지 못했습니다.');
    }
  }
);

// 비동기 액션: 모델 파일 목록 로드
export const fetchModels = createAsyncThunk('nas/fetchModels', async (_, { rejectWithValue }) => {
  try {
    const response = await apiClient.get('/api/v1/nas/models');
    return response.data;
  } catch (error: any) {
    return rejectWithValue(error.response?.data?.detail || '모델 목록을 가져오지 못했습니다.');
  }
});

// 비동기 액션: 파일 생성/업로드
export const uploadFile = createAsyncThunk(
  'nas/uploadFile',
  async ({ path, file }: { path: string; file: File }, { rejectWithValue, dispatch }) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiClient.post('/api/v1/nas/file', formData, {
        params: { path },
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      // 파일 목록 갱신
      dispatch(fetchFiles(path));
      
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '파일 업로드에 실패했습니다.');
    }
  }
);

// 비동기 액션: 디렉토리 생성
export const createDirectory = createAsyncThunk(
  'nas/createDirectory',
  async ({ path, name }: { path: string; name: string }, { rejectWithValue, dispatch }) => {
    try {
      const fullPath = path ? `${path}/${name}` : name;
      
      const response = await apiClient.post('/api/v1/nas/directory', null, {
        params: { path: fullPath },
      });
      
      // 파일 목록 갱신
      dispatch(fetchFiles(path));
      
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '디렉토리 생성에 실패했습니다.');
    }
  }
);

// 비동기 액션: 파일 삭제
export const deleteFile = createAsyncThunk(
  'nas/deleteFile',
  async ({ path, isDirectory }: { path: string; isDirectory?: boolean }, { rejectWithValue, dispatch }) => {
    try {
      const response = await apiClient.delete('/api/v1/nas/file', {
        params: { path },
      });
      
      // 상위 경로 계산
      const parentPath = path.includes('/')
        ? path.substring(0, path.lastIndexOf('/'))
        : '';
      
      // 파일 목록 갱신
      dispatch(fetchFiles(parentPath));
      
      return {
        ...response.data,
        deletedPath: path,
      };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || '파일 삭제에 실패했습니다.');
    }
  }
);

// 슬라이스 생성
const nasSlice = createSlice({
  name: 'nas',
  initialState,
  reducers: {
    // 현재 경로 설정
    setCurrentPath: (state, action: PayloadAction<string>) => {
      state.currentPath = action.payload;
    },
    
    // 선택된 파일 설정
    setSelectedFile: (state, action: PayloadAction<FileItem | null>) => {
      state.selectedFile = action.payload;
    },
    
    // 에러 초기화
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // NAS 상태 로드
    builder
      .addCase(fetchNasStatus.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchNasStatus.fulfilled, (state, action) => {
        state.loading = false;
        state.status = action.payload;
      })
      .addCase(fetchNasStatus.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
    
    // 파일 목록 로드
    builder
      .addCase(fetchFiles.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchFiles.fulfilled, (state, action) => {
        state.loading = false;
        state.files = action.payload.files;
        state.currentPath = action.payload.path;
      })
      .addCase(fetchFiles.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
    
    // 모델 파일 목록 로드
    builder
      .addCase(fetchModels.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchModels.fulfilled, (state, action) => {
        state.loading = false;
        state.models = action.payload;
      })
      .addCase(fetchModels.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
    
    // 파일 업로드
    builder
      .addCase(uploadFile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(uploadFile.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(uploadFile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
    
    // 디렉토리 생성
    builder
      .addCase(createDirectory.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createDirectory.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(createDirectory.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
    
    // 파일 삭제
    builder
      .addCase(deleteFile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteFile.fulfilled, (state, action) => {
        state.loading = false;
        
        // 만약 선택된 파일이 삭제된 파일이었다면 선택 해제
        if (state.selectedFile && state.selectedFile.path === action.payload.deletedPath) {
          state.selectedFile = null;
        }
      })
      .addCase(deleteFile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
  },
});

// 액션 생성자 내보내기
export const { setCurrentPath, setSelectedFile, clearError } = nasSlice.actions;

// 리듀서 내보내기
export default nasSlice.reducer; 