import React from 'react';
import { Layout, Typography, Button, Space, Dropdown, Avatar, Badge } from 'antd';
import { UserOutlined, BellOutlined, QuestionCircleOutlined, DownOutlined } from '@ant-design/icons';
import { useSelector } from 'react-redux';
import { RootState } from '../../store';
import type { MenuProps } from 'antd';

const { Header: AntHeader } = Layout;
const { Text } = Typography;

const Header: React.FC = () => {
  const { apiStatus } = useSelector((state: RootState) => state.system);

  // 사용자 메뉴 항목
  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      label: '프로필',
    },
    {
      key: 'settings',
      label: '사용자 설정',
    },
    {
      key: 'divider',
      type: 'divider',
    },
    {
      key: 'logout',
      label: '로그아웃',
    },
  ];

  // 알림 메뉴 항목
  const notificationMenuItems: MenuProps['items'] = [
    {
      key: 'notification1',
      label: '새 에이전트 업데이트가 있습니다',
    },
    {
      key: 'notification2',
      label: '시스템 로그 확인 필요',
    },
    {
      key: 'view-all',
      type: 'divider',
    },
    {
      key: 'view-all',
      label: '모든 알림 보기',
    },
  ];

  return (
    <AntHeader style={{ background: '#fff', padding: '0 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <div>
        <Badge 
          status={apiStatus.connected ? "success" : "error"} 
          text={apiStatus.connected ? "API 연결됨" : "API 연결 끊김"} 
        />
        {apiStatus.connected && (
          <Text style={{ marginLeft: 10 }} type="secondary">
            버전: {apiStatus.version}
          </Text>
        )}
      </div>

      <Space size="large">
        <Button type="text" icon={<QuestionCircleOutlined />}>
          도움말
        </Button>

        <Dropdown menu={{ items: notificationMenuItems }} placement="bottomRight" arrow>
          <Badge count={2} size="small">
            <Button type="text" icon={<BellOutlined />} />
          </Badge>
        </Dropdown>

        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight" arrow>
          <Space>
            <Avatar icon={<UserOutlined />} />
            <Text>관리자</Text>
            <DownOutlined />
          </Space>
        </Dropdown>
      </Space>
    </AntHeader>
  );
};

export default Header; 