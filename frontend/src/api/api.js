import client from './client';
import { endpoints } from './endpoints';

// Auth API
export const authAPI = {
  login: async (emailOrUsername, password) => {
    const response = await client.post(endpoints.auth.login, {
      email_or_username: emailOrUsername,
      password,
    });
    return response.data;
  },
  register: async (userData) => {
    const response = await client.post(endpoints.auth.register, userData);
    return response.data;
  },
  refresh: async (refreshToken) => {
    const response = await client.post(endpoints.auth.refresh, {
      refresh_token: refreshToken,
    });
    return response.data;
  },
  logout: async () => {
    await client.post(endpoints.auth.logout);
  },
  me: async () => {
    const response = await client.get(endpoints.auth.me);
    return response.data;
  },
};

// Search API
export const searchAPI = {
  create: async (query, city) => {
    const response = await client.post(endpoints.search.create, { query, city });
    return response.data;
  },
  list: async (page = 1, pageSize = 20) => {
    const response = await client.get(endpoints.search.list, {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },
  get: async (id) => {
    const response = await client.get(endpoints.search.detail(id));
    return response.data;
  },
  getStatus: async (id) => {
    const response = await client.get(endpoints.search.status(id));
    return response.data;
  },
  getResumes: async (id, page = 1, pageSize = 20, sortBy = 'ai_score', sortOrder = 'desc') => {
    const response = await client.get(endpoints.search.resumes(id), {
      params: { page, page_size: pageSize, sort_by: sortBy, sort_order: sortOrder },
    });
    return response.data;
  },
  exportExcel: async (id) => {
    const response = await client.get(endpoints.search.exportExcel(id), {
      responseType: 'blob',
    });
    return response.data;
  },
  exportCsv: async (id) => {
    const response = await client.get(endpoints.search.exportCsv(id), {
      responseType: 'blob',
    });
    return response.data;
  },
};

// Users API
export const usersAPI = {
  list: async (page = 1, pageSize = 20) => {
    const response = await client.get(endpoints.users.list, {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },
  get: async (id) => {
    const response = await client.get(endpoints.users.detail(id));
    return response.data;
  },
  update: async (id, userData) => {
    const response = await client.patch(endpoints.users.update(id), userData);
    return response.data;
  },
  delete: async (id) => {
    await client.delete(endpoints.users.delete(id));
  },
};

// Analytics API
export const analyticsAPI = {
  getDashboard: async (days = 30) => {
    const response = await client.get('/analytics/dashboard', {
      params: { days },
    });
    return response.data;
  },
  getVacancyAnalytics: async (vacancyId) => {
    const response = await client.get(`/analytics/vacancy/${vacancyId}`);
    return response.data;
  },
  getHiringFunnel: async (days = 30) => {
    const response = await client.get('/analytics/funnel', {
      params: { days },
    });
    return response.data;
  },
};

// Notifications API
export const notificationsAPI = {
  getNotifications: async (unreadOnly = false, page = 1, limit = 50) => {
    const response = await client.get('/notifications', {
      params: { unread_only: unreadOnly, page, limit },
    });
    return response.data;
  },
  markAsRead: async (notificationId) => {
    const response = await client.patch(`/notifications/${notificationId}/read`);
    return response.data;
  },
  markAllAsRead: async () => {
    const response = await client.post('/notifications/read-all');
    return response.data;
  },
  delete: async (notificationId) => {
    await client.delete(`/notifications/${notificationId}`);
  },
};
