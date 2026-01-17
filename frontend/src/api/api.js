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

// Candidates API
export const candidatesAPI = {
  get: async (resumeId) => {
    const response = await client.get(endpoints.candidates.get(resumeId));
    return response.data;
  },
  updateStatus: async (resumeId, status) => {
    const response = await client.patch(endpoints.candidates.updateStatus(resumeId), { status });
    return response.data;
  },
  addTag: async (resumeId, tag) => {
    const response = await client.post(endpoints.candidates.addTag(resumeId), { tag });
    return response.data;
  },
  removeTag: async (resumeId, tag) => {
    const response = await client.delete(endpoints.candidates.removeTag(resumeId, tag));
    return response.data;
  },
  assign: async (resumeId, assignedToUserId) => {
    const response = await client.post(endpoints.candidates.assign(resumeId), {
      assigned_to_user_id: assignedToUserId,
    });
    return response.data;
  },
  addRating: async (resumeId, rating) => {
    const response = await client.post(endpoints.candidates.addRating(resumeId), { rating });
    return response.data;
  },
  updateNotes: async (resumeId, notes) => {
    const response = await client.patch(endpoints.candidates.updateNotes(resumeId), { notes });
    return response.data;
  },
  setFolder: async (resumeId, folder) => {
    const response = await client.patch(endpoints.candidates.setFolder(resumeId), { folder });
    return response.data;
  },
  getInteractions: async (resumeId, limit = 50) => {
    const response = await client.get(endpoints.candidates.getInteractions(resumeId), {
      params: { limit },
    });
    return response.data;
  },
  getAll: async (page = 1, pageSize = 20) => {
    const response = await client.get(endpoints.candidates.getAll, {
      params: { page, page_size: pageSize },
    });
    return response.data || { candidates: [], total: 0, page, page_size: pageSize };
  },
  getByStatus: async (status, page = 1, pageSize = 20) => {
    const response = await client.get(endpoints.candidates.getByStatus(status), {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },
  getByTags: async (tags, page = 1, pageSize = 20) => {
    const response = await client.get(endpoints.candidates.getByTags, {
      params: { tags: Array.isArray(tags) ? tags.join(',') : tags, page, page_size: pageSize },
    });
    return response.data;
  },
  getByVacancy: async (vacancyId, page = 1, pageSize = 20) => {
    const response = await client.get(endpoints.candidates.getByVacancy(vacancyId), {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },
  getKanban: async (vacancyId = null) => {
    const response = await client.get(endpoints.candidates.getKanban, {
      params: vacancyId ? { vacancy_id: vacancyId } : {},
    });
    return response.data;
  },
};

// Vacancies API
export const vacanciesAPI = {
  list: async (status = null, page = 1, pageSize = 20) => {
    const response = await client.get(endpoints.vacancies.list, {
      params: { status, page, page_size: pageSize },
    });
    return response.data;
  },
  create: async (vacancyData) => {
    const response = await client.post(endpoints.vacancies.create, vacancyData);
    return response.data;
  },
  get: async (id) => {
    const response = await client.get(endpoints.vacancies.get(id));
    return response.data;
  },
  update: async (id, vacancyData) => {
    const response = await client.patch(endpoints.vacancies.update(id), vacancyData);
    return response.data;
  },
  updateStatus: async (id, status) => {
    const response = await client.patch(endpoints.vacancies.updateStatus(id), null, {
      params: { status },
    });
    return response.data;
  },
  updateAutoMatching: async (id, settings) => {
    const response = await client.patch(endpoints.vacancies.updateAutoMatching(id), settings);
    return response.data;
  },
  addCandidate: async (id, resumeId) => {
    const response = await client.post(endpoints.vacancies.addCandidate(id, resumeId));
    return response.data;
  },
  removeCandidate: async (id, resumeId) => {
    const response = await client.delete(endpoints.vacancies.removeCandidate(id, resumeId));
    return response.data;
  },
};
