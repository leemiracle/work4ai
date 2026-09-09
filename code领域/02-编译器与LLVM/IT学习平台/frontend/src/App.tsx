import React from 'react';
import { Layout, Menu } from 'antd';
import {
  HomeOutlined,
  BookOutlined,
  ReadOutlined,
  ProjectOutlined,
  ThunderboltOutlined
} from '@ant-design/icons';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Notes from './pages/Notes';
import Learning from './pages/Learning';
import Projects from './pages/Projects';
import AIAssistant from './pages/AIAssistant';

const { Header, Content } = Layout;

const App: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/ai',
      icon: <ThunderboltOutlined />,
      label: 'AI Assistant',
    },
    {
      key: '/notes',
      icon: <BookOutlined />,
      label: 'Knowledge Base',
    },
    {
      key: '/learning',
      icon: <ReadOutlined />,
      label: 'Learning',
    },
    {
      key: '/projects',
      icon: <ProjectOutlined />,
      label: 'Projects',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <Layout className="app-layout">
      <Header className="app-header">
        <div style={{ color: 'white', fontSize: '20px', fontWeight: 'bold' }}>
          AI Learning Platform
        </div>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ lineHeight: '64px', minWidth: '400px' }}
        />
      </Header>
      <Content className="app-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/ai" element={<AIAssistant />} />
          <Route path="/notes" element={<Notes />} />
          <Route path="/learning" element={<Learning />} />
          <Route path="/projects" element={<Projects />} />
        </Routes>
      </Content>
    </Layout>
  );
};

export default App;
