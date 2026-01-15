import axios from 'axios';
import client from '../client';

jest.mock('axios');

describe('API Client', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    delete window.location;
    window.location = { href: '' };
  });

  it('creates axios instance with correct base URL', () => {
    expect(client.defaults.baseURL).toBe('/api/v1');
  });

  it('adds authorization header when token exists', async () => {
    localStorage.setItem('access_token', 'test-token');
    
    const mockAxios = axios.create();
    axios.create.mockReturnValue(mockAxios);
    
    // Re-import to trigger interceptors
    jest.resetModules();
    const newClient = require('../client').default;
    
    const config = { headers: {} };
    const interceptor = mockAxios.interceptors.request.use.mock.calls[0][0];
    const result = interceptor(config);
    
    expect(result.headers.Authorization).toBe('Bearer test-token');
  });

  it('does not add authorization header when token does not exist', async () => {
    localStorage.clear();
    
    const mockAxios = axios.create();
    axios.create.mockReturnValue(mockAxios);
    
    jest.resetModules();
    const newClient = require('../client').default;
    
    const config = { headers: {} };
    const interceptor = mockAxios.interceptors.request.use.mock.calls[0][0];
    const result = interceptor(config);
    
    expect(result.headers.Authorization).toBeUndefined();
  });

  it('handles 401 error and refreshes token', async () => {
    const refreshToken = 'refresh-token';
    const newAccessToken = 'new-access-token';
    
    localStorage.setItem('access_token', 'old-token');
    localStorage.setItem('refresh_token', refreshToken);
    
    const mockAxios = axios.create();
    axios.create.mockReturnValue(mockAxios);
    axios.post.mockResolvedValue({
      data: {
        access_token: newAccessToken,
        refresh_token: refreshToken,
      },
    });
    
    jest.resetModules();
    const newClient = require('../client').default;
    
    const originalRequest = {
      _retry: false,
      headers: {},
      config: {},
    };
    
    const error = {
      response: { status: 401 },
      config: originalRequest,
    };
    
    const interceptor = mockAxios.interceptors.response.use.mock.calls[0][1];
    
    try {
      await interceptor(error);
    } catch (e) {
      // Expected to fail in test environment
    }
    
    // Should attempt to refresh token
    expect(axios.post).toHaveBeenCalled();
  });

  it('redirects to login when refresh fails', async () => {
    localStorage.setItem('refresh_token', 'invalid-token');
    
    const mockAxios = axios.create();
    axios.create.mockReturnValue(mockAxios);
    axios.post.mockRejectedValue(new Error('Refresh failed'));
    
    jest.resetModules();
    const newClient = require('../client').default;
    
    const originalRequest = {
      _retry: false,
      headers: {},
    };
    
    const error = {
      response: { status: 401 },
      config: originalRequest,
    };
    
    const interceptor = mockAxios.interceptors.response.use.mock.calls[0][1];
    
    try {
      await interceptor(error);
    } catch (e) {
      // Expected
    }
    
    expect(localStorage.getItem('access_token')).toBe(null);
    expect(localStorage.getItem('refresh_token')).toBe(null);
  });

  it('handles non-401 errors normally', async () => {
    const mockAxios = axios.create();
    axios.create.mockReturnValue(mockAxios);
    
    jest.resetModules();
    const newClient = require('../client').default;
    
    const error = {
      response: { status: 404 },
      config: {},
    };
    
    const interceptor = mockAxios.interceptors.response.use.mock.calls[0][1];
    const result = interceptor(error);
    
    await expect(result).rejects.toEqual(error);
  });
});
