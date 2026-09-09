import React, { useEffect, useState } from 'react';
import { Card, Button, Input, Space, Tag, Modal, Form, message } from 'antd';
import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { Note } from '../services/notes';
import notesApi from '../services/notes';

const Notes: React.FC = () => {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchNotes();
  }, []);

  const fetchNotes = async () => {
    setLoading(true);
    try {
      const data = await notesApi.getAll();
      setNotes(data);
    } catch (error) {
      message.error('Failed to fetch notes');
    }
    setLoading(false);
  };

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      await notesApi.create(values);
      message.success('Note created successfully');
      setModalVisible(false);
      form.resetFields();
      fetchNotes();
    } catch (error) {
      message.error('Failed to create note');
    }
  };

  const handleSearch = async () => {
    if (!searchText) {
      fetchNotes();
      return;
    }
    try {
      const data = await notesApi.search(searchText);
      setNotes(data);
    } catch (error) {
      message.error('Failed to search notes');
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Knowledge Base</h1>
        <Space>
          <Input
            placeholder="Search notes..."
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            onPressEnter={handleSearch}
            style={{ width: 300 }}
          />
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setModalVisible(true)}
          >
            New Note
          </Button>
        </Space>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16 }}>
        {notes.map((note) => (
          <Card
            key={note.id}
            title={note.title}
            extra={
              note.category && <Tag color="blue">{note.category}</Tag>
            }
            hoverable
          >
            <p style={{ color: '#666', marginBottom: 8 }}>
              {note.content.substring(0, 100)}
              {note.content.length > 100 && '...'}
            </p>
            <small style={{ color: '#999' }}>
              Created: {new Date(note.created_at).toLocaleDateString()}
            </small>
          </Card>
        ))}
      </div>

      <Modal
        title="Create New Note"
        open={modalVisible}
        onOk={handleCreate}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="title"
            label="Title"
            rules={[{ required: true, message: 'Please enter title' }]}
          >
            <Input placeholder="Note title" />
          </Form.Item>
          <Form.Item
            name="content"
            label="Content"
            rules={[{ required: true, message: 'Please enter content' }]}
          >
            <Input.TextArea rows={10} placeholder="Note content (Markdown supported)" />
          </Form.Item>
          <Form.Item name="category" label="Category">
            <Input placeholder="Category" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Notes;
