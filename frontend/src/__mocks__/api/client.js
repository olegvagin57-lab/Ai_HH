// Mock for axios client in tests
import axios from 'axios';

const client = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
client.interceptors.request.use(
  (config) => {
    const token = typeof window !== 'undefined' ? window.localStorage?.getItem('access_token') : null;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for token refresh
client.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = typeof window !== 'undefined' ? window.localStorage?.getItem('refresh_token') : null;
      if (refreshToken) {
        try {
          const response = await axios.post('/api/v1/auth/refresh', {
            refresh_token: refreshToken,
          }, {
            baseURL: '',
          });

          const { access_token, refresh_token: new_refresh_token } = response.data;
          if (typeof window !== 'undefined') {
            window.localStorage.setItem('access_token', access_token);
            if (new_refresh_token) {
              window.localStorage.setItem('refresh_token', new_refresh_token);
            }
          }

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return client(originalRequest);
        } catch (refreshError) {
          if (typeof window !== 'undefined') {
            window.localStorage.removeItem('access_token');
            window.localStorage.removeItem('refresh_token');
            window.location.href = '/login';
          }
          return Promise.reject(refreshError);
        }
      } else {
        if (typeof window !== 'undefined') {
          window.localStorage.removeItem('access_token');
          window.localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }

    return Promise.reject(error);
  }
);

export default client;
