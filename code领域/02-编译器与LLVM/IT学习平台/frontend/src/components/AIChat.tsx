import { useState, useRef, useEffect } from 'react';
import { Card, Input, Button, List, Avatar, Space, Spin, message, Tag } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined, BulbOutlined } from '@ant-design/icons';
import api from '../services/api';

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

const AIChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await api.post('/ai/learning/chat', {
        question: input,
        conversation_history: messages.map(m => ({
          role: m.role,
          content: m.content,
        })),
      });

      const aiMessage: Message = {
        role: 'assistant',
        content: response.data.answer,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, aiMessage]);

      // Update suggestions
      if (response.data.suggested_followup) {
        setSuggestions(response.data.suggested_followup);
      }
    } catch (error) {
      message.error('发送消息失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Card
        title={
          <Space>
            <RobotOutlined style={{ color: '#1890ff' }} />
            <span>AI 学习助手</span>
          </Space>
        }
        style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}
        bodyStyle={{ flex: 1, padding: 0, display: 'flex', flexDirection: 'column' }}
      >
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '16px',
            backgroundColor: '#fafafa',
          }}
        >
          {messages.length === 0 && (
            <div style={{ textAlign: 'center', marginTop: '50px', color: '#999' }}>
              <BulbOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
              <p>你好！我是你的AI学习助手。</p>
              <p>有什么可以帮助你的？</p>
            </div>
          )}

          <List
            dataSource={messages}
            renderItem={(msg) => (
              <List.Item
                style={{
                  border: 'none',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                }}
              >
                <Space direction={msg.role === 'user' ? 'row-reverse' : 'row'}>
                  <Avatar
                    icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                    style={{ backgroundColor: msg.role === 'user' ? '#1890ff' : '#52c41a' }}
                  />
                  <div
                    style={{
                      maxWidth: '70%',
                      padding: '12px 16px',
                      borderRadius: '8px',
                      backgroundColor: msg.role === 'user' ? '#1890ff' : '#fff',
                      color: msg.role === 'user' ? '#fff' : '#333',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                    }}
                  >
                    {msg.content}
                  </div>
                </Space>
              </List.Item>
            )}
          />

          {loading && (
            <div style={{ textAlign: 'center', padding: '16px' }}>
              <Spin tip="AI正在思考..." />
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {suggestions.length > 0 && (
          <div style={{ padding: '12px 16px', borderTop: '1px solid #f0f0f0' }}>
            <div style={{ fontSize: '12px', color: '#999', marginBottom: '8px' }}>
              建议问题:
            </div>
            <Space wrap>
              {suggestions.map((suggestion, index) => (
                <Tag
                  key={index}
                  color="blue"
                  style={{ cursor: 'pointer' }}
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion}
                </Tag>
              ))}
            </Space>
          </div>
        )}

        <div style={{ padding: '16px', borderTop: '1px solid #f0f0f0' }}>
          <Space.Compact style={{ width: '100%' }}>
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onPressEnter={handleSend}
              placeholder="输入你的问题..."
              disabled={loading}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSend}
              loading={loading}
            >
              发送
            </Button>
          </Space.Compact>
        </div>
      </Card>
    </div>
  );
};

export default AIChat;
