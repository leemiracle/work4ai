import React, { useEffect, useState } from 'react';
import { Card, Button, Tag, Modal, Form, Input, Select, InputNumber, message, List, Badge } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { Project, Task } from '../services/projects';
import projectsApi from '../services/projects';

const Projects: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [projectTasks, setProjectTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const data = await projectsApi.getAll();
      setProjects(data);
    } catch (error) {
      message.error('Failed to fetch projects');
    }
    setLoading(false);
  };

  const fetchProjectTasks = async (projectId: number) => {
    try {
      const data = await projectsApi.tasks.getAll(projectId);
      setProjectTasks(data);
    } catch (error) {
      message.error('Failed to fetch tasks');
    }
  };

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      await projectsApi.create(values);
      message.success('Project created successfully');
      setModalVisible(false);
      form.resetFields();
      fetchProjects();
    } catch (error) {
      message.error('Failed to create project');
    }
  };

  const handleProjectClick = async (project: Project) => {
    setSelectedProject(project);
    await fetchProjectTasks(project.id);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'green';
      case 'completed':
        return 'blue';
      case 'on_hold':
        return 'orange';
      default:
        return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'red';
      case 'medium':
        return 'orange';
      case 'low':
        return 'green';
      default:
        return 'default';
    }
  };

  const getTaskStatusColor = (status: string) => {
    switch (status) {
      case 'done':
        return 'success';
      case 'in_progress':
        return 'processing';
      case 'blocked':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Project Management</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setModalVisible(true)}
        >
          New Project
        </Button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: 16, marginBottom: 24 }}>
        {projects.map((project) => (
          <Card
            key={project.id}
            title={project.name}
            hoverable
            onClick={() => handleProjectClick(project)}
            style={{
              cursor: 'pointer',
              border: selectedProject?.id === project.id ? '2px solid #1890ff' : '1px solid #d9d9d9',
            }}
          >
            <p style={{ color: '#666', marginBottom: 12 }}>
              {project.description || 'No description'}
            </p>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <Tag color={getStatusColor(project.status)}>
                {project.status}
              </Tag>
              <Tag color={getPriorityColor(project.priority)}>
                {project.priority}
              </Tag>
            </div>
          </Card>
        ))}
      </div>

      {selectedProject && (
        <Card
          title={
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>{selectedProject.name} - Tasks</span>
              <Button size="small" onClick={() => setSelectedProject(null)}>
                Close
              </Button>
            </div>
          }
        >
          <List
            dataSource={projectTasks}
            renderItem={(task) => (
              <List.Item>
                <List.Item.Meta
                  title={
                    <span>
                      <Badge status={getTaskStatusColor(task.status)} text={task.title} />
                    </span>
                  }
                  description={
                    <div>
                      {task.description && <p style={{ marginBottom: 4 }}>{task.description}</p>}
                      <div style={{ display: 'flex', gap: 8 }}>
                        <Tag color={getPriorityColor(task.priority)}>{task.priority}</Tag>
                        {task.due_date && (
                          <Tag>Due: {new Date(task.due_date).toLocaleDateString()}</Tag>
                        )}
                      </div>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        </Card>
      )}

      <Modal
        title="Create New Project"
        open={modalVisible}
        onOk={handleCreate}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="Project Name"
            rules={[{ required: true, message: 'Please enter project name' }]}
          >
            <Input placeholder="Project name" />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <Input.TextArea rows={4} placeholder="Project description" />
          </Form.Item>
          <Form.Item
            name="priority"
            label="Priority"
            rules={[{ required: true }]}
          >
            <Select defaultValue="medium">
              <Select.Option value="low">Low</Select.Option>
              <Select.Option value="medium">Medium</Select.Option>
              <Select.Option value="high">High</Select.Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Projects;
