import React, { useEffect, useState } from 'react';
import { Layout, Card, Button, Table, Tag, Space, Modal, message, Spin, Input, Form, Tooltip } from 'antd';
import { PlusOutlined, PlayCircleOutlined, PauseCircleOutlined, DeleteOutlined, ThunderboltOutlined, SettingOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { api as API, getApiBaseUrl } from '../utils/api';

const { Content } = Layout;

const Agents = () => {
  const [agents, setAgents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [alphaSetupModalVisible, setAlphaSetupModalVisible] = useState(false);
  const [apiSettingsModalVisible, setApiSettingsModalVisible] = useState(false);
  const [dockerHelpModalVisible, setDockerHelpModalVisible] = useState(false);
  const [apiUrl, setApiUrl] = useState(getApiBaseUrl());
  const navigate = useNavigate();

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      setLoading(true);
      const response = await API.agents.getAll();
      setAgents(response.data || []);
    } catch (error) {
      console.error('Error loading agents:', error);
      message.error('Failed to load agents');
    } finally {
      setLoading(false);
    }
  };

  const handleStartAgent = async (id: string) => {
    try {
      setActionLoading(true);
      await API.agents.start(id);
      message.success('Agent started successfully');
      loadAgents();
    } catch (error) {
      console.error('Error starting agent:', error);
      message.error('Failed to start agent');
    } finally {
      setActionLoading(false);
    }
  };

  const handleStopAgent = async (id: string) => {
    try {
      setActionLoading(true);
      await API.agents.stop(id);
      message.success('Agent stopped successfully');
      loadAgents();
    } catch (error) {
      console.error('Error stopping agent:', error);
      message.error('Failed to stop agent');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteAgent = async (id: string) => {
    try {
      setActionLoading(true);
      await API.agents.delete(id);
      message.success('Agent deleted successfully');
      loadAgents();
    } catch (error) {
      console.error('Error deleting agent:', error);
      message.error('Failed to delete agent');
    } finally {
      setActionLoading(false);
    }
  };

  const handleQuickSetupAlpha = async () => {
    try {
      setActionLoading(true);
      setAlphaSetupModalVisible(false);
      const response = await API.agents.quickSetupAlpha();
      message.success('Alpha Agent setup completed successfully');
      loadAgents();
    } catch (error) {
      console.error('Error setting up Alpha Agent:', error);
      message.error('Failed to set up Alpha Agent');
    } finally {
      setActionLoading(false);
    }
  };

  const handleSaveApiUrl = () => {
    localStorage.setItem('apiUrl', apiUrl);
    message.success('API URL이 저장되었습니다. 페이지를 새로고침하세요.');
    setApiSettingsModalVisible(false);
  };

  const getAgentTypeDisplay = (type: string) => {
    switch (type) {
      case 'alpha':
        return <Tag color="blue">Alpha</Tag>;
      case 'assistant':
        return <Tag color="green">Assistant</Tag>;
      case 'researcher':
        return <Tag color="purple">Researcher</Tag>;
      default:
        return <Tag>{type}</Tag>;
    }
  };

  const getStatusDisplay = (status: string) => {
    switch (status) {
      case 'running':
        return <Tag color="green">Running</Tag>;
      case 'stopped':
        return <Tag color="red">Stopped</Tag>;
      case 'error':
        return <Tag color="orange">Error</Tag>;
      default:
        return <Tag color="default">Unknown</Tag>;
    }
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: any) => (
        <a onClick={() => navigate(`/agents/${record.id}`)}>{text}</a>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => getAgentTypeDisplay(type),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => getStatusDisplay(status),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (text: string, record: any) => (
        <Space size="small">
          {record.status === 'stopped' ? (
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              size="small"
              onClick={() => handleStartAgent(record.id)}
              disabled={actionLoading}
            >
              Start
            </Button>
          ) : (
            <Button
              danger
              icon={<PauseCircleOutlined />}
              size="small"
              onClick={() => handleStopAgent(record.id)}
              disabled={actionLoading}
            >
              Stop
            </Button>
          )}
          <Button
            danger
            icon={<DeleteOutlined />}
            size="small"
            onClick={() => handleDeleteAgent(record.id)}
            disabled={actionLoading}
          >
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <Content style={{ padding: '24px' }}>
      <Card
        title="Agents"
        extra={
          <Space>
            <Tooltip title="API 설정">
              <Button 
                icon={<SettingOutlined />} 
                onClick={() => setApiSettingsModalVisible(true)}
              />
            </Tooltip>
            <Tooltip title="Docker 실행 안내">
              <Button 
                icon={<InfoCircleOutlined />} 
                onClick={() => setDockerHelpModalVisible(true)}
              />
            </Tooltip>
            <Button
              type="primary"
              icon={<ThunderboltOutlined />}
              onClick={() => setAlphaSetupModalVisible(true)}
            >
              Quick Setup Alpha
            </Button>
            <Button 
              type="primary" 
              icon={<PlusOutlined />} 
              onClick={() => navigate('/agents/new')}
            >
              Add Agent
            </Button>
          </Space>
        }
      >
        {loading ? (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <Spin size="large" />
          </div>
        ) : (
          <Table 
            columns={columns} 
            dataSource={agents.map(agent => ({ ...agent, key: agent.id }))} 
            pagination={false} 
          />
        )}
      </Card>

      <Modal
        title="Quick Setup Alpha Agent"
        open={alphaSetupModalVisible}
        onOk={handleQuickSetupAlpha}
        onCancel={() => setAlphaSetupModalVisible(false)}
        confirmLoading={actionLoading}
      >
        <p>This will quickly set up an Alpha Agent with default settings:</p>
        <ul>
          <li>News collection from pre-configured sources</li>
          <li>Topic analysis capabilities</li>
          <li>Content generation based on analyzed topics</li>
        </ul>
        <p>Do you want to proceed?</p>
      </Modal>

      <Modal
        title="API 설정"
        open={apiSettingsModalVisible}
        onOk={handleSaveApiUrl}
        onCancel={() => setApiSettingsModalVisible(false)}
      >
        <Form layout="vertical">
          <Form.Item 
            label="API URL" 
            tooltip="API 서버의 URL을 입력하세요. Docker 환경에서는 자동으로 '/api'로 설정됩니다."
          >
            <Input 
              value={apiUrl} 
              onChange={(e) => setApiUrl(e.target.value)} 
              placeholder="예: http://localhost:528" 
            />
          </Form.Item>
          <p>참고: 변경 후 페이지를 새로고침해야 적용됩니다.</p>
        </Form>
      </Modal>

      <Modal
        title="Docker 실행 안내"
        open={dockerHelpModalVisible}
        onOk={() => setDockerHelpModalVisible(false)}
        onCancel={() => setDockerHelpModalVisible(false)}
        width={700}
      >
        <h3>Docker로 실행하기</h3>
        <p>Docker Compose를 사용하여 오비스 시스템을 간편하게 실행할 수 있습니다:</p>
        <pre style={{ background: '#f6f8fa', padding: '12px', borderRadius: '4px' }}>
          {`# 프로젝트 루트 디렉토리에서
docker-compose up -d`}
        </pre>
        
        <h3>컨테이너 상태 확인</h3>
        <pre style={{ background: '#f6f8fa', padding: '12px', borderRadius: '4px' }}>
          {`docker-compose ps`}
        </pre>
        
        <h3>로그 확인</h3>
        <pre style={{ background: '#f6f8fa', padding: '12px', borderRadius: '4px' }}>
          {`docker-compose logs -f`}
        </pre>
        
        <h3>API 서버 접속</h3>
        <p>Docker 환경에서는 API URL이 자동으로 설정됩니다. 별도의 설정이 필요하지 않습니다.</p>
        <p>로컬 개발 환경에서 접속하는 경우, API URL을 설정해야 합니다:</p>
        <ul>
          <li>API 설정 버튼을 클릭하여 API URL 설정</li>
          <li>기본값: http://localhost:528</li>
        </ul>
      </Modal>
    </Content>
  );
};

export default Agents; 