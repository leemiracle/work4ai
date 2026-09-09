import api from './api';

export interface Project {
  id: number;
  name: string;
  description?: string;
  status: string;
  priority: string;
  start_date?: string;
  end_date?: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: number;
  title: string;
  description?: string;
  status: string;
  priority: string;
  project_id: number;
  assignee_id?: number;
  due_date?: string;
  estimated_hours?: number;
  created_at: string;
  updated_at: string;
}

export interface Milestone {
  id: number;
  title: string;
  description?: string;
  project_id: number;
  target_date: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export const projectsApi = {
  getAll: async (params?: any) => {
    const response = await api.get('/projects/', { params });
    return response.data;
  },

  getById: async (id: number) => {
    const response = await api.get(`/projects/${id}`);
    return response.data;
  },

  create: async (data: Partial<Project>) => {
    const response = await api.post('/projects/', data);
    return response.data;
  },

  update: async (id: number, data: Partial<Project>) => {
    const response = await api.put(`/projects/${id}`, data);
    return response.data;
  },

  delete: async (id: number) => {
    const response = await api.delete(`/projects/${id}`);
    return response.data;
  },

  tasks: {
    getAll: async (projectId: number, params?: any) => {
      const response = await api.get(`/projects/${projectId}/tasks`, { params });
      return response.data;
    },

    create: async (data: Partial<Task>) => {
      const response = await api.post('/projects/tasks/', data);
      return response.data;
    },

    update: async (id: number, data: Partial<Task>) => {
      const response = await api.put(`/projects/tasks/${id}`, data);
      return response.data;
    },

    delete: async (id: number) => {
      const response = await api.delete(`/projects/tasks/${id}`);
      return response.data;
    },
  },

  milestones: {
    getAll: async (params?: any) => {
      const response = await api.get('/projects/milestones/', { params });
      return response.data;
    },

    create: async (data: Partial<Milestone>) => {
      const response = await api.post('/projects/milestones/', data);
      return response.data;
    },

    update: async (id: number, data: Partial<Milestone>) => {
      const response = await api.put(`/projects/milestones/${id}`, data);
      return response.data;
    },

    delete: async (id: number) => {
      const response = await api.delete(`/projects/milestones/${id}`);
      return response.data;
    },
  },
};
