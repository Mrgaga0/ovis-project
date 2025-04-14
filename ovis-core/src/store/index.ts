import { configureStore } from '@reduxjs/toolkit';

// 슬라이스 임포트
import systemReducer from './slices/systemSlice';
import agentsReducer from './slices/agentsSlice';
import logsReducer from './slices/logsSlice';
import nasReducer from './slices/nasSlice';

// 스토어 설정
export const store = configureStore({
  reducer: {
    system: systemReducer,
    agents: agentsReducer,
    logs: logsReducer,
    nas: nasReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // 직렬화 불가능한 값을 무시할 경로 지정
        ignoredActions: ['logs/setLogs'],
        ignoredPaths: ['logs.items'],
      },
    }),
});

// 타입 내보내기
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch; 