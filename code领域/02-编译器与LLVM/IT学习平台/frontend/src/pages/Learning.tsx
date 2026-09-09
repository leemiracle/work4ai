import React, { useEffect, useState } from 'react';
import { Card, Tabs, Tag, Button, Modal, Form, Input, InputNumber, Select, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { Course, Skill } from '../services/learning';
import learningApi from '../services/learning';

const { TabPane } = Tabs;

const Learning: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(false);
  const [courseModalVisible, setCourseModalVisible] = useState(false);
  const [skillModalVisible, setSkillModalVisible] = useState(false);
  const [courseForm] = Form.useForm();
  const [skillForm] = Form.useForm();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [coursesData, skillsData] = await Promise.all([
        learningApi.courses.getAll(),
        learningApi.skills.getAll(),
      ]);
      setCourses(coursesData);
      setSkills(skillsData);
    } catch (error) {
      message.error('Failed to fetch learning data');
    }
    setLoading(false);
  };

  const handleCreateCourse = async () => {
    try {
      const values = await courseForm.validateFields();
      await learningApi.courses.create(values);
      message.success('Course created successfully');
      setCourseModalVisible(false);
      courseForm.resetFields();
      fetchData();
    } catch (error) {
      message.error('Failed to create course');
    }
  };

  const handleCreateSkill = async () => {
    try {
      const values = await skillForm.validateFields();
      await learningApi.skills.create(values);
      message.success('Skill created successfully');
      setSkillModalVisible(false);
      skillForm.resetFields();
      fetchData();
    } catch (error) {
      message.error('Failed to create skill');
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'green';
      case 'intermediate':
        return 'blue';
      case 'advanced':
        return 'orange';
      default:
        return 'default';
    }
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'beginner':
        return 'green';
      case 'intermediate':
        return 'blue';
      case 'advanced':
        return 'purple';
      case 'expert':
        return 'red';
      default:
        return 'default';
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Learning Management</h1>
      </div>

      <Tabs defaultActiveKey="courses">
        <TabPane tab="Courses" key="courses">
          <div style={{ marginBottom: 16 }}>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setCourseModalVisible(true)}
            >
              New Course
            </Button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: 16 }}>
            {courses.map((course) => (
              <Card
                key={course.id}
                title={course.title}
                extra={
                  <Tag color={getDifficultyColor(course.difficulty)}>
                    {course.difficulty}
                  </Tag>
                }
              >
                <p style={{ color: '#666', marginBottom: 16 }}>
                  {course.description || 'No description'}
                </p>
                <div>
                  <Tag icon={<span>⏱️</span>} color="blue">
                    {course.total_hours || 0} hours
                  </Tag>
                  <Tag icon={<span>📚</span>} color="green">
                    {course.modules?.length || 0} modules
                  </Tag>
                </div>
              </Card>
            ))}
          </div>
        </TabPane>

        <TabPane tab="Skills" key="skills">
          <div style={{ marginBottom: 16 }}>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setSkillModalVisible(true)}
            >
              New Skill
            </Button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16 }}>
            {skills.map((skill) => (
              <Card
                key={skill.id}
                title={skill.name}
                extra={
                  <Tag color={getLevelColor(skill.level)}>
                    {skill.level}
                  </Tag>
                }
              >
                {skill.category && <Tag style={{ marginBottom: 8 }}>{skill.category}</Tag>}
                <p style={{ color: '#666', marginBottom: 8 }}>
                  {skill.description || 'No description'}
                </p>
                {skill.estimated_hours && (
                  <small style={{ color: '#999' }}>
                    Estimated: {skill.estimated_hours} hours
                  </small>
                )}
              </Card>
            ))}
          </div>
        </TabPane>

        <TabPane tab="Learning Plans" key="plans">
          <Card>
            <p style={{ color: '#999' }}>Learning plans feature coming soon.</p>
          </Card>
        </TabPane>
      </Tabs>

      <Modal
        title="Create New Course"
        open={courseModalVisible}
        onOk={handleCreateCourse}
        onCancel={() => {
          setCourseModalVisible(false);
          courseForm.resetFields();
        }}
      >
        <Form form={courseForm} layout="vertical">
          <Form.Item
            name="title"
            label="Title"
            rules={[{ required: true, message: 'Please enter title' }]}
          >
            <Input placeholder="Course title" />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <Input.TextArea rows={4} placeholder="Course description" />
          </Form.Item>
          <Form.Item
            name="difficulty"
            label="Difficulty"
            rules={[{ required: true }]}
          >
            <Select defaultValue="beginner">
              <Select.Option value="beginner">Beginner</Select.Option>
              <Select.Option value="intermediate">Intermediate</Select.Option>
              <Select.Option value="advanced">Advanced</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="total_hours" label="Total Hours">
            <InputNumber min={0} placeholder="Total hours" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="Create New Skill"
        open={skillModalVisible}
        onOk={handleCreateSkill}
        onCancel={() => {
          setSkillModalVisible(false);
          skillForm.resetFields();
        }}
      >
        <Form form={skillForm} layout="vertical">
          <Form.Item
            name="name"
            label="Name"
            rules={[{ required: true, message: 'Please enter name' }]}
          >
            <Input placeholder="Skill name" />
          </Form.Item>
          <Form.Item name="description" label="Description">
            <Input.TextArea rows={4} placeholder="Skill description" />
          </Form.Item>
          <Form.Item
            name="level"
            label="Level"
            rules={[{ required: true }]}
          >
            <Select defaultValue="beginner">
              <Select.Option value="beginner">Beginner</Select.Option>
              <Select.Option value="intermediate">Intermediate</Select.Option>
              <Select.Option value="advanced">Advanced</Select.Option>
              <Select.Option value="expert">Expert</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="category" label="Category">
            <Input placeholder="Category" />
          </Form.Item>
          <Form.Item name="estimated_hours" label="Estimated Hours">
            <InputNumber min={0} placeholder="Estimated hours" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Learning;
