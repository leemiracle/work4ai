import api from './api';

export interface Note {
  id: number;
  title: string;
  content: string;
  category?: string;
  is_public: boolean;
  author_id: number;
  created_at: string;
  updated_at: string;
  tags?: Tag[];
}

export interface Tag {
  id: number;
  name: string;
  color?: string;
}

export const notesApi = {
  getAll: async (params?: any) => {
    const response = await api.get('/notes/', { params });
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get(`/notes/${id}`);
    return response.data;
  },

  create: async (data: Partial<Note>) => {
    const response = await api.post('/notes/', data);
    return response.data;
  },

  update: async (id: number, data: Partial<Note>) => {
    const response = await api.put(`/notes/${id}`, data);
    return response.data;
  },

  delete: async (id: number) => {
    const response = await api.delete(`/notes/${id}`);
    return response.data;
  },

  search: async (query: string) => {
    const response = await api.post('/notes/search', null, { params: { query } });
    return response.data;
  },
};
