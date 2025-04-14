import React, { useEffect, useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout, Spin, Result, Button } from 'antd';
import { useDispatch, useSelector } from 'react-redux';
import { setApiStatus, setInitialized } from './store/slices/systemSlice';
import { RootState } from './store';
import { apiClient } from './utils/api';

// 레이아웃 컴포넌트
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';

// 페이지 컴포넌트
import Dashboard from './pages/Dashboard';
import Agents from './pages/Agents';
import AgentDetail from './pages/AgentDetail';
import Settings from './pages/Settings';
import Logs from './pages/Logs';
import NotFound from './pages/NotFound';

const { Content } = Layout;

const App: React.FC = () => {
  const dispatch = useDispatch();
  const { isInitialized, apiStatus } = useSelector((state: RootState) => state.system);
  const [initError, setInitError] = useState<string | null>(null);

  // 앱 초기화
  useEffect(() => {
    const initializeApp = async () => {
      try {
        // API 서버 상태 확인
        // utils/api.ts에서 BaseURL 설정이 자동으로 이루어짐
        const response = await apiClient.get('/api/v1/status');
        dispatch(setApiStatus({
          connected: true,
          version: response.data.version,
        }));
        
        // Electron 환경인지 확인하고 추가 초기화
        const isElectron = window.navigator.userAgent.toLowerCase().indexOf('electron') > -1;
        if (isElectron) {
          // Electron 특화 기능 초기화 (필요한 경우)
          console.log('Electron 환경에서 실행 중');
          
          // 여기에 Electron 전용 코드를 추가
          try {
            // @ts-ignore - Electron window 객체 확장
            if (window.electron) {
              // @ts-ignore
              const version = await window.electron.app.getVersion();
              console.log('Electron 버전:', version);
            }
          } catch (electronError) {
            console.warn('Electron API 접근 오류:', electronError);
          }
        } else {
          console.log('웹 브라우저 환경에서 실행 중');
        }
        
        // 초기화 완료
        dispatch(setInitialized(true));
      } catch (error) {
        console.error('초기화 실패:', error);
        setInitError('API 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.');
        dispatch(setApiStatus({
          connected: false,
          error: '연결 실패',
        }));
      }
    };

    if (!isInitialized) {
      initializeApp();
    }
  }, [dispatch, isInitialized]);

  // 로딩 화면
  if (!isInitialized && !initError) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" tip="애플리케이션 초기화 중..." />
      </div>
    );
  }

  // 초기화 오류 화면
  if (initError) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Result
          status="error"
          title="초기화 오류"
          subTitle={initError}
          extra={[
            <Button 
              key="retry" 
              type="primary" 
              onClick={() => {
                setInitError(null);
                dispatch(setInitialized(false));
              }}
            >
              다시 시도
            </Button>,
            <Button 
              key="settings" 
              onClick={() => {
                // 설정 화면으로 이동 (오류 상태에서도 설정 접근 가능)
                setInitError(null);
                dispatch(setInitialized(true));
              }}
            >
              설정 확인
            </Button>,
          ]}
        />
      </div>
    );
  }

  // 메인 앱 레이아웃
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sidebar />
      <Layout>
        <Header />
        <Content style={{ margin: '24px 16px', padding: 24, minHeight: 280 }}>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/agents" element={<Agents />} />
            <Route path="/agents/:id" element={<AgentDetail />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/logs" element={<Logs />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
};

export default App; 