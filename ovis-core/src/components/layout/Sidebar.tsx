import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Layout, Menu, Typography } from 'antd';
import {
  DashboardOutlined,
  RobotOutlined,
  SettingOutlined,
  FileTextOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';

const { Sider } = Layout;
const { Title } = Typography;

const Sidebar: React.FC = () => {
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);

  // 현재 활성화된 메뉴 키 계산
  const getSelectedKey = () => {
    const path = location.pathname;
    if (path.includes('/dashboard')) return ['dashboard'];
    if (path.includes('/agents')) return ['agents'];
    if (path.includes('/settings')) return ['settings'];
    if (path.includes('/logs')) return ['logs'];
    return ['dashboard'];
  };

  // 메뉴 아이템 정의
  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: <Link to="/dashboard">대시보드</Link>,
    },
    {
      key: 'agents',
      icon: <RobotOutlined />,
      label: <Link to="/agents">에이전트</Link>,
    },
    {
      key: 'logs',
      icon: <FileTextOutlined />,
      label: <Link to="/logs">로그</Link>,
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: <Link to="/settings">설정</Link>,
    },
  ];

  return (
    <Sider
      collapsible
      collapsed={collapsed}
      onCollapse={setCollapsed}
      theme="dark"
      width={220}
      style={{ 
        overflow: 'auto', 
        height: '100vh', 
        position: 'sticky', 
        top: 0, 
        left: 0 
      }}
    >
      <div className="app-logo">
        {collapsed ? 'OVIS' : 'OVIS AI 시스템'}
      </div>
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={getSelectedKey()}
        items={menuItems}
      />
      
      {/* 사이드바 접기/펼치기 버튼 */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          width: '100%',
          padding: '10px',
          textAlign: 'center',
          background: '#001529',
          color: 'white',
          cursor: 'pointer',
        }}
        onClick={() => setCollapsed(!collapsed)}
      >
        {collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
      </div>
    </Sider>
  );
};

export default Sidebar; 