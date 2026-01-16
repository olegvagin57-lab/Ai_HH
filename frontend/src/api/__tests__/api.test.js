import { authAPI, searchAPI, candidatesAPI, vacanciesAPI, usersAPI, analyticsAPI, notificationsAPI } from '../api';
import client from '../client';

jest.mock('../client');

describe('API Methods', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('authAPI', () => {
    it('login calls correct endpoint', async () => {
      client.post.mockResolvedValue({ data: { access_token: 'token', user: {} } });
      
      await authAPI.login('test@example.com', 'password');
      
      expect(client.post).toHaveBeenCalledWith('/auth/login', {
        email_or_username: 'test@example.com',
        password: 'password',
      });
    });

    it('register calls correct endpoint', async () => {
      client.post.mockResolvedValue({ data: { id: '1' } });
      
      const userData = { email: 'test@example.com', username: 'testuser', password: 'pass' };
      await authAPI.register(userData);
      
      expect(client.post).toHaveBeenCalledWith('/auth/register', userData);
    });

    it('refresh calls correct endpoint', async () => {
      client.post.mockResolvedValue({ data: { access_token: 'new-token' } });
      
      await authAPI.refresh('refresh-token');
      
      expect(client.post).toHaveBeenCalledWith('/auth/refresh', {
        refresh_token: 'refresh-token',
      });
    });

    it('logout calls correct endpoint', async () => {
      client.post.mockResolvedValue({});
      
      await authAPI.logout();
      
      expect(client.post).toHaveBeenCalledWith('/auth/logout');
    });

    it('me calls correct endpoint', async () => {
      client.get.mockResolvedValue({ data: { id: '1', email: 'test@example.com' } });
      
      await authAPI.me();
      
      expect(client.get).toHaveBeenCalledWith('/auth/me');
    });
  });

  describe('searchAPI', () => {
    it('create calls correct endpoint', async () => {
      client.post.mockResolvedValue({ data: { id: '1' } });
      
      await searchAPI.create('Python developer', 'Москва');
      
      expect(client.post).toHaveBeenCalledWith('/search', {
        query: 'Python developer',
        city: 'Москва',
      });
    });

    it('list calls correct endpoint with params', async () => {
      client.get.mockResolvedValue({ data: { searches: [] } });
      
      await searchAPI.list(1, 20);
      
      expect(client.get).toHaveBeenCalledWith('/search', {
        params: { page: 1, page_size: 20 },
      });
    });

    it('get calls correct endpoint', async () => {
      client.get.mockResolvedValue({ data: { id: '123' } });
      
      await searchAPI.get('123');
      
      expect(client.get).toHaveBeenCalledWith('/search/123');
    });

    it('exportExcel calls correct endpoint', async () => {
      const mockBlob = new Blob(['test'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      client.get.mockResolvedValue({ data: mockBlob, responseType: 'blob' });
      
      await searchAPI.exportExcel('123');
      
      expect(client.get).toHaveBeenCalledWith('/search/123/export/excel', {
        responseType: 'blob',
      });
    });
  });

  describe('candidatesAPI', () => {
    it('get calls correct endpoint', async () => {
      client.get.mockResolvedValue({ data: { id: '1' } });
      
      await candidatesAPI.get('resume-123');
      
      expect(client.get).toHaveBeenCalledWith('/candidates/resume/resume-123');
    });

    it('updateStatus calls correct endpoint', async () => {
      client.patch.mockResolvedValue({ data: {} });
      
      await candidatesAPI.updateStatus('resume-123', 'reviewed');
      
      expect(client.patch).toHaveBeenCalledWith('/candidates/resume/resume-123/status', {
        status: 'reviewed',
      });
    });

    it('addTag calls correct endpoint', async () => {
      client.post.mockResolvedValue({ data: {} });
      
      await candidatesAPI.addTag('resume-123', 'python');
      
      expect(client.post).toHaveBeenCalledWith('/candidates/resume/resume-123/tags', {
        tag: 'python',
      });
    });

    it('getKanban calls correct endpoint', async () => {
      client.get.mockResolvedValue({ data: {} });
      
      await candidatesAPI.getKanban();
      
      expect(client.get).toHaveBeenCalledWith('/candidates/kanban', {
        params: {},
      });
    });

    it('getByVacancy calls correct endpoint', async () => {
      client.get.mockResolvedValue({ data: { candidates: [] } });
      
      await candidatesAPI.getByVacancy('vacancy-123', 1, 20);
      
      expect(client.get).toHaveBeenCalledWith('/candidates/by-vacancy/vacancy-123', {
        params: { page: 1, page_size: 20 },
      });
    });
  });

  describe('vacanciesAPI', () => {
    it('list calls correct endpoint', async () => {
      client.get.mockResolvedValue({ data: { vacancies: [] } });
      
      await vacanciesAPI.list('active', 1, 20);
      
      expect(client.get).toHaveBeenCalledWith('/vacancies', {
        params: { status: 'active', page: 1, page_size: 20 },
      });
    });

    it('create calls correct endpoint', async () => {
      client.post.mockResolvedValue({ data: { id: '1' } });
      
      const vacancyData = { title: 'Test', description: 'Test desc' };
      await vacanciesAPI.create(vacancyData);
      
      expect(client.post).toHaveBeenCalledWith('/vacancies', vacancyData);
    });

    it('update calls correct endpoint', async () => {
      client.patch.mockResolvedValue({ data: {} });
      
      await vacanciesAPI.update('123', { title: 'Updated' });
      
      expect(client.patch).toHaveBeenCalledWith('/vacancies/123', { title: 'Updated' });
    });
  });

  describe('usersAPI', () => {
    it('list calls correct endpoint', async () => {
      client.get.mockResolvedValue({ data: { users: [] } });
      
      await usersAPI.list(1, 20);
      
      expect(client.get).toHaveBeenCalledWith('/users', {
        params: { page: 1, page_size: 20 },
      });
    });

    it('update calls correct endpoint', async () => {
      client.patch.mockResolvedValue({ data: {} });
      
      await usersAPI.update('123', { full_name: 'New Name' });
      
      expect(client.patch).toHaveBeenCalledWith('/users/123', { full_name: 'New Name' });
    });

    it('delete calls correct endpoint', async () => {
      client.delete.mockResolvedValue({});
      
      await usersAPI.delete('123');
      
      expect(client.delete).toHaveBeenCalledWith('/users/123');
    });
  });

  describe('analyticsAPI', () => {
    it('getDashboard calls correct endpoint', async () => {
      client.get.mockResolvedValue({ data: {} });
      
      await analyticsAPI.getDashboard(30);
      
      expect(client.get).toHaveBeenCalledWith('/analytics/dashboard', {
        params: { days: 30 },
      });
    });

    it('getHiringFunnel calls correct endpoint', async () => {
      client.get.mockResolvedValue({ data: {} });
      
      await analyticsAPI.getHiringFunnel(30);
      
      expect(client.get).toHaveBeenCalledWith('/analytics/funnel', {
        params: { days: 30 },
      });
    });
  });

  describe('notificationsAPI', () => {
    it('getNotifications calls correct endpoint', async () => {
      client.get.mockResolvedValue({ data: { notifications: [] } });
      
      await notificationsAPI.getNotifications(true, 1, 20);
      
      expect(client.get).toHaveBeenCalledWith('/notifications', {
        params: { unread_only: true, page: 1, limit: 20 },
      });
    });

    it('markAsRead calls correct endpoint', async () => {
      client.patch.mockResolvedValue({ data: {} });
      
      await notificationsAPI.markAsRead('123');
      
      expect(client.patch).toHaveBeenCalledWith('/notifications/123/read');
    });

    it('markAllAsRead calls correct endpoint', async () => {
      client.post.mockResolvedValue({ data: {} });
      
      await notificationsAPI.markAllAsRead();
      
      expect(client.post).toHaveBeenCalledWith('/notifications/read-all');
    });

    it('delete calls correct endpoint', async () => {
      client.delete.mockResolvedValue({});
      
      await notificationsAPI.delete('123');
      
      expect(client.delete).toHaveBeenCalledWith('/notifications/123');
    });
  });
});
