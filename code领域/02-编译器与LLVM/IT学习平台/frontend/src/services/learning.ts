import api from './api';

export interface Course {
  id: number;
  title: string;
  description?: string;
  modules: any[];
  total_hours?: number;
  difficulty: string;
  created_at: string;
  updated_at: string;
}

export interface Skill {
  id: number;
  name: string;
  description?: string;
  level: string;
  category?: string;
  estimated_hours?: number;
  created_at: string;
}

export interface LearningPlan {
  id: number;
  title: string;
  goals: string[];
  timeline: any;
  status: string;
  start_date: string;
  end_date?: string;
  created_at: string;
  updated_at: string;
}

export const learningApi = {
  courses: {
    getAll: async (params?: any) => {
      const response = await api.get('/learning/courses/', { params });
      return response.data;
    },

    getById: async (id: number) => {
      const response = await api.get(`/learning/courses/${id}`);
      return response.data;
    },

    create: async (data: Partial<Course>) => {
      const response = await api.post('/learning/courses/', data);
      return response.data;
    },

    update: async (id: number, data: Partial<Course>) => {
      const response = await api.put(`/learning/courses/${id}`, data);
      return response.data;
    },

    delete: async (id: number) => {
      const response = await api.delete(`/learning/courses/${id}`);
      return response.data;
    },
  },

  skills: {
    getAll: async (params?: any) => {
      const response = await api.get('/learning/skills/', { params });
      return response.data;
    },

    getById: async (id: number) => {
      const response = await api.get(`/learning/skills/${id}`);
      return response.data;
    },

    getTree: async (id: number) => {
      const response = await api.get(`/learning/skills/${id}/tree`);
      return response.data;
    },

    create: async (data: Partial<Skill>) => {
      const response = await api.post('/learning/skills/', data);
      return response.data;
    },

    update: async (id: number, data: Partial<Skill>) => {
      const response = await api.put(`/learning/skills/${id}`, data);
      return response.data;
    },
  },

  plans: {
    getAll: async (params?: any) => {
      const response = await api.get('/learning/plans/', { params });
      return response.data;
    },

    getById: async (id: number) => {
      const response = await api.get(`/learning/plans/${id}`);
      return response.data;
    },

    create: async (data: Partial<LearningPlan>) => {
      const response = await api.post('/learning/plans/', data);
      return response.data;
    },

    update: async (id: number, data: Partial<LearningPlan>) => {
      const response = await api.put(`/learning/plans/${id}`, data);
      return response.data;
    },
  },
};
