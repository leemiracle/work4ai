import React, { useState } from 'react';
import { Card, Tabs, Button, Modal, Form, Input, InputNumber, Select, message, Space, Tag, Row, Col } from 'antd';
import { ThunderboltOutlined, RobotOutlined, BulbOutlined, ProjectOutlined, CodeOutlined } from '@ant-design/icons';
import AIChat from '../components/AIChat';
import api from '../services/api';

const { TabPane } = Tabs;
const { TextArea } = Input;

const AIAssistant: React.FC = () => {
  const [activeTab, setActiveTab] = useState('chat');
  const [pathModalVisible, setPathModalVisible] = useState(false);
  const [pathForm] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [learningPath, setLearningPath] = useState<any>(null);

  const handleGeneratePath = async () => {
    try {
      const values = await pathForm.validateFields();
      setLoading(true);

      const response = await api.post('/ai/learning/path', values);
      setLearningPath(response.data);
      message.success('学习路径生成成功！');
      setPathModalVisible(false);
      pathForm.resetFields();
    } catch (error) {
      message.error('生成学习路径失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async (content: string) => {
    try {
      const response = await api.post('/ai/knowledge/summarize', {
        content,
        max_length: 500,
      });
      return response.data.summary;
    } catch (error) {
      message.error('总结失败');
      return '';
    }
  };

  const handleGenerateQuiz = async (topic: string) => {
    try {
      const response = await api.post('/ai/knowledge/quiz', {
        topic,
        difficulty: 'medium',
        count: 5,
      });
      return response.data;
    } catch (error) {
      message.error('生成测验失败');
      return [];
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <ThunderboltOutlined style={{ color: '#52c41a', fontSize: '32px' }} />
          AI 助手
        </h1>
        <p style={{ color: '#666', marginTop: '8px' }}>
          利用AI技术提升学习效率和项目管理水平
        </p>
      </div>

      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane
          tab={
            <span>
              <RobotOutlined />
              AI 对话
            </span>
          }
          key="chat"
        >
          <AIChat />
        </TabPane>

        <TabPane
          tab={
            <span>
              <BulbOutlined />
              学习助手
            </span>
          }
          key="learning"
        >
          <div style={{ display: 'grid', gap: '16px', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))' }}>
            <Card
              title="个性化学习路径"
              extra={<Button type="primary" onClick={() => setPathModalVisible(true)}>生成</Button>}
            >
              <p style={{ color: '#666' }}>
                根据你的学习目标和当前水平，AI将为你制定详细的学习路径。
              </p>

              {learningPath && (
                <div style={{ marginTop: '16px' }}>
                  <h4>{learningPath.title || '学习路径'}</h4>
                  {learningPath.stages && learningPath.stages.map((stage: any, index: number) => (
                    <Card
                      key={index}
                      size="small"
                      style={{ marginTop: '8px' }}
                      title={`阶段 ${index + 1}: ${stage.title}`}
                    >
                      <p><strong>周期:</strong> {stage.duration_weeks || stage.week} 周</p>
                      <p><strong>目标:</strong></p>
                      <ul>
                        {(stage.goals || []).map((goal: string, i: number) => (
                          <li key={i}>{goal}</li>
                        ))}
                      </ul>
                    </Card>
                  ))}
                </div>
              )}
            </Card>

            <Card
              title="学习进度分析"
            >
              <p style={{ color: '#666' }}>
                AI将分析你的学习进度，识别薄弱环节，并提供改进建议。
              </p>
              <Button>开始分析</Button>
            </Card>

            <Card
              title="智能练习题"
            >
              <p style={{ color: '#666' }}>
                根据你的学习进度，AI生成针对性的练习题。
              </p>
              <Button>生成练习</Button>
            </Card>

            <Card
              title="概念解释"
            >
              <Space.Compact style={{ width: '100%' }}>
                <Input placeholder="输入概念名称" />
                <Button type="primary">解释</Button>
              </Space.Compact>
            </Card>
          </div>
        </TabPane>

        <TabPane
          tab={
            <span>
              <ProjectOutlined />
              项目助手
            </span>
          }
          key="project"
        >
          <Row gutter={[16, 16]}>
            <Col span={12}>
              <Card title="项目风险分析">
                <p style={{ color: '#666', marginBottom: '16px' }}>
                  AI分析项目可能面临的风险，并提供缓解策略。
                </p>
                <Button type="primary">分析风险</Button>
              </Card>
            </Col>
            <Col span={12}>
              <Card title="任务优化建议">
                <p style={{ color: '#666', marginBottom: '16px' }}>
                  根据团队技能和任务要求，AI提供最优的任务分配方案。
                </p>
                <Button type="primary">优化任务</Button>
              </Card>
            </Col>
            <Col span={12}>
              <Card title="项目报告生成">
                <p style={{ color: '#666', marginBottom: '16px' }}>
                  AI自动生成项目进度报告，包含关键指标和建议。
                </p>
                <Button type="primary">生成报告</Button>
              </Card>
            </Col>
            <Col span={12}>
              <Card title="团队效率优化">
                <p style={{ color: '#666', marginBottom: '16px' }}>
                  AI分析团队协作模式，提供效率提升建议。
                </p>
                <Button type="primary">分析团队</Button>
              </Card>
            </Col>
          </Row>
        </TabPane>

        <TabPane
          tab={
            <span>
              <CodeOutlined />
              代码助手
            </span>
          }
          key="code"
        >
          <Card title="代码生成">
            <Form layout="vertical">
              <Form.Item label="编程语言">
                <Select defaultValue="python">
                  <Select.Option value="python">Python</Select.Option>
                  <Select.Option value="javascript">JavaScript</Select.Option>
                  <Select.Option value="java">Java</Select.Option>
                  <Select.Option value="cpp">C++</Select.Option>
                  <Select.Option value="go">Go</Select.Option>
                </Select>
              </Form.Item>
              <Form.Item label="功能描述">
                <TextArea rows={4} placeholder="描述你想要实现的功能..." />
              </Form.Item>
              <Form.Item>
                <Button type="primary" loading={loading}>生成代码</Button>
              </Form.Item>
            </Form>
          </Card>

          <Card title="代码优化" style={{ marginTop: '16px' }}>
            <Form layout="vertical">
              <Form.Item label="编程语言">
                <Select defaultValue="python">
                  <Select.Option value="python">Python</Select.Option>
                  <Select.Option value="javascript">JavaScript</Select.Option>
                </Select>
              </Form.Item>
              <Form.Item label="代码">
                <TextArea rows={10} placeholder="粘贴你的代码..." />
              </Form.Item>
              <Form.Item label="优化重点">
                <Select mode="tags" placeholder="选择优化方向">
                  <Select.Option value="readability">可读性</Select.Option>
                  <Select.Option value="performance">性能</Select.Option>
                  <Select.Option value="best_practices">最佳实践</Select.Option>
                  <Select.Option value="security">安全性</Select.Option>
                </Select>
              </Form.Item>
              <Form.Item>
                <Button type="primary" loading={loading}>优化代码</Button>
              </Form.Item>
            </Form>
          </Card>
        </TabPane>
      </Tabs>

      <Modal
        title="生成个性化学习路径"
        open={pathModalVisible}
        onOk={handleGeneratePath}
        onCancel={() => {
          setPathModalVisible(false);
          pathForm.resetFields();
        }}
        okText="生成"
        cancelText="取消"
        confirmLoading={loading}
      >
        <Form form={pathForm} layout="vertical">
          <Form.Item
            name="learning_goal"
            label="学习目标"
            rules={[{ required: true, message: '请输入学习目标' }]}
          >
            <Input placeholder="例如：学习LLVM编译器技术" />
          </Form.Item>
          <Form.Item
            name="current_level"
            label="当前水平"
            rules={[{ required: true, message: '请选择当前水平' }]}
          >
            <Select defaultValue="beginner">
              <Select.Option value="beginner">初学者</Select.Option>
              <Select.Option value="intermediate">中级</Select.Option>
              <Select.Option value="advanced">高级</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="available_time_week"
            label="每周可用时间（小时）"
            rules={[{ required: true, message: '请输入可用时间' }]}
          >
            <InputNumber min={1} max={100} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default AIAssistant;
