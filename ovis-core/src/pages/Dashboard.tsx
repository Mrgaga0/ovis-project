import React, { useEffect, useState } from 'react';
import { Typography, Card, Row, Col, Statistic, Space, Empty } from 'antd';
import { ApiOutlined, RobotOutlined, DatabaseOutlined, SyncOutlined } from '@ant-design/icons';
import { useSelector } from 'react-redux';
import { RootState } from '../store';

const { Title, Paragraph } = Typography;

const Dashboard: React.FC = () => {
  const { apiStatus } = useSelector((state: RootState) => state.system);
  const { items: agents, loading: agentsLoading } = useSelector((state: RootState) => state.agents);

  const [stats, setStats] = useState({
    activeAgents: 0,
    totalAgents: 0,
    nasUsage: '0%',
    lastSync: '없음',
  });

  useEffect(() => {
    // 실제 API 데이터로 대체할 수 있는 예시 데이터
    setStats({
      activeAgents: agents.filter(agent => agent.status === 'running').length,
      totalAgents: agents.length,
      nasUsage: '45%',
      lastSync: new Date().toLocaleString(),
    });
  }, [agents]);

  return (
    <div>
      <Title level={2}>대시보드</Title>
      <Paragraph>OVIS 시스템 상태 및 통계를 확인할 수 있습니다.</Paragraph>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="API 상태"
              value={apiStatus.connected ? '연결됨' : '연결 끊김'}
              valueStyle={{ color: apiStatus.connected ? '#3f8600' : '#cf1322' }}
              prefix={<ApiOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="실행 중인 에이전트"
              value={stats.activeAgents}
              suffix={`/ ${stats.totalAgents}`}
              valueStyle={{ color: '#3f8600' }}
              prefix={<RobotOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="NAS 사용량"
              value={stats.nasUsage}
              prefix={<DatabaseOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="마지막 동기화"
              value={stats.lastSync}
              prefix={<SyncOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} md={12}>
          <Card title="최근 활동 에이전트" style={{ height: 300 }}>
            {agents.length > 0 ? (
              <p>여기에 에이전트 목록 표시</p>
            ) : (
              <Empty description="실행 중인 에이전트가 없습니다" />
            )}
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="시스템 로그" style={{ height: 300 }}>
            <Empty description="최근 로그 항목이 없습니다" />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24}>
          <Card title="시스템 정보">
            <Row gutter={16}>
              <Col xs={24} sm={8}>
                <Statistic title="운영체제" value={window.navigator.platform} />
              </Col>
              <Col xs={24} sm={8}>
                <Statistic title="앱 버전" value="0.1.0" />
              </Col>
              <Col xs={24} sm={8}>
                <Statistic title="API 버전" value={apiStatus.version || 'N/A'} />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard; 