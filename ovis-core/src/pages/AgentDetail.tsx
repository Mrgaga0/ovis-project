import React from 'react';
import { Typography, Card } from 'antd';
import { useParams } from 'react-router-dom';

const { Title, Paragraph } = Typography;

const AgentDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <div>
      <Title level={2}>에이전트 상세 정보</Title>
      <Paragraph>에이전트 ID: {id}</Paragraph>
      <Card title="에이전트 정보" style={{ marginBottom: 16 }}>
        <p>상세 정보는 이 곳에 표시됩니다.</p>
      </Card>
    </div>
  );
};

export default AgentDetail; 