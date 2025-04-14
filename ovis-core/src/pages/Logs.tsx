import React from 'react';
import { Typography, Table, Select, DatePicker, Card, Input, Space } from 'antd';
import { SearchOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;
const { Option } = Select;
const { RangePicker } = DatePicker;

const Logs: React.FC = () => {
  // 로그 데이터 샘플
  const logData = [
    {
      key: '1',
      timestamp: '2023-04-14 10:32:45',
      level: 'INFO',
      module: 'system',
      message: '시스템 시작됨',
    },
    {
      key: '2',
      timestamp: '2023-04-14 10:33:12',
      level: 'INFO',
      module: 'agents',
      message: '에이전트 alpha 실행됨',
    },
    {
      key: '3',
      timestamp: '2023-04-14 10:35:58',
      level: 'WARNING',
      module: 'nas',
      message: 'NAS 저장 공간 70% 사용 중',
    },
  ];

  // 테이블 컬럼 정의
  const columns = [
    {
      title: '시간',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
    },
    {
      title: '레벨',
      dataIndex: 'level',
      key: 'level',
      width: 100,
      render: (text: string) => {
        const color =
          text === 'ERROR' ? 'red' :
          text === 'WARNING' ? 'orange' :
          text === 'INFO' ? 'green' : 'default';
        return <span style={{ color }}>{text}</span>;
      },
    },
    {
      title: '모듈',
      dataIndex: 'module',
      key: 'module',
      width: 120,
    },
    {
      title: '메시지',
      dataIndex: 'message',
      key: 'message',
    },
  ];

  return (
    <div>
      <Title level={2}>로그</Title>
      <Paragraph>시스템 로그를 확인할 수 있습니다.</Paragraph>
      
      <Card style={{ marginBottom: 16 }}>
        <Space style={{ marginBottom: 16 }}>
          <Select defaultValue="all" style={{ width: 120 }}>
            <Option value="all">모든 레벨</Option>
            <Option value="info">INFO</Option>
            <Option value="warning">WARNING</Option>
            <Option value="error">ERROR</Option>
            <Option value="debug">DEBUG</Option>
          </Select>
          
          <Select defaultValue="all" style={{ width: 150 }}>
            <Option value="all">모든 모듈</Option>
            <Option value="system">시스템</Option>
            <Option value="agents">에이전트</Option>
            <Option value="nas">NAS</Option>
          </Select>
          
          <RangePicker />
          
          <Input 
            placeholder="검색어" 
            prefix={<SearchOutlined />} 
            style={{ width: 200 }} 
          />
        </Space>
        
        <Table 
          dataSource={logData} 
          columns={columns} 
          pagination={{ defaultPageSize: 10 }}
          size="middle"
        />
      </Card>
    </div>
  );
};

export default Logs; 