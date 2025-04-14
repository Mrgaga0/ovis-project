import React from 'react';
import { Typography, Form, Input, Button, Card, Switch } from 'antd';

const { Title, Paragraph } = Typography;

const Settings: React.FC = () => {
  const [form] = Form.useForm();

  const handleSubmit = (values: any) => {
    console.log('설정 저장:', values);
    // 여기에 설정 저장 로직을 구현합니다
  };

  return (
    <div>
      <Title level={2}>설정</Title>
      <Paragraph>OVIS 시스템 설정을 관리할 수 있습니다.</Paragraph>
      
      <Card title="일반 설정" style={{ marginBottom: 16 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            apiUrl: 'http://localhost:528',
            nasPath: '/mnt/v/ovis_save',
            darkMode: false,
          }}
        >
          <Form.Item
            label="API URL"
            name="apiUrl"
            rules={[{ required: true, message: 'API URL을 입력하세요' }]}
          >
            <Input placeholder="http://localhost:528" />
          </Form.Item>
          
          <Form.Item
            label="NAS 경로"
            name="nasPath"
            rules={[{ required: true, message: 'NAS 경로를 입력하세요' }]}
          >
            <Input placeholder="/mnt/v/ovis_save" />
          </Form.Item>
          
          <Form.Item label="다크 모드" name="darkMode" valuePropName="checked">
            <Switch />
          </Form.Item>
          
          <Form.Item>
            <Button type="primary" htmlType="submit">
              설정 저장
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default Settings; 