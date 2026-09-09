import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic } from 'antd';
import {
  BookOutlined,
  ReadOutlined,
  ProjectOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState({
    notes: 0,
    courses: 0,
    skills: 0,
    projects: 0,
  });

  useEffect(() => {
    // TODO: Fetch stats from API
    setStats({
      notes: 0,
      courses: 0,
      skills: 0,
      projects: 0,
    });
  }, []);

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>Dashboard</h1>

      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="Knowledge Notes"
              value={stats.notes}
              prefix={<BookOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Courses"
              value={stats.courses}
              prefix={<ReadOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Skills"
              value={stats.skills}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="Projects"
              value={stats.projects}
              prefix={<ProjectOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      <Card title="Recent Activity">
        <p style={{ color: '#999' }}>No recent activity yet.</p>
      </Card>
    </div>
  );
};

export default Dashboard;
