import { renderHook, act, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from '../AuthContext';
import { authAPI } from '../../../../api/api';

jest.mock('../../../../api/api');

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const wrapper = ({ children }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  it('provides auth context', () => {
    authAPI.me.mockRejectedValue(new Error('Not authenticated'));
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    expect(result.current).toBeDefined();
    expect(result.current).toHaveProperty('user');
    expect(result.current).toHaveProperty('loading');
    expect(result.current).toHaveProperty('login');
    expect(result.current).toHaveProperty('logout');
    expect(result.current).toHaveProperty('register');
    expect(result.current).toHaveProperty('isAuthenticated');
  });

  it('loads user from token on mount', async () => {
    const mockUser = { id: '1', email: 'test@example.com', username: 'testuser' };
    localStorage.setItem('access_token', 'test-token');
    authAPI.me.mockResolvedValue(mockUser);
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    expect(authAPI.me).toHaveBeenCalled();
    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
  });

  it('handles failed user load', async () => {
    localStorage.setItem('access_token', 'invalid-token');
    authAPI.me.mockRejectedValue(new Error('Unauthorized'));
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    expect(result.current.user).toBe(null);
    expect(result.current.isAuthenticated).toBe(false);
    expect(localStorage.getItem('access_token')).toBe(null);
  });

  it('login function works correctly', async () => {
    const mockUser = { id: '1', email: 'test@example.com' };
    const mockTokens = {
      access_token: 'access-token',
      refresh_token: 'refresh-token',
      user: mockUser,
    };
    
    authAPI.login.mockResolvedValue(mockTokens);
    authAPI.me.mockRejectedValue(new Error('Not authenticated'));
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await act(async () => {
      await result.current.login('test@example.com', 'password123');
    });
    
    expect(authAPI.login).toHaveBeenCalledWith('test@example.com', 'password123');
    expect(localStorage.getItem('access_token')).toBe('access-token');
    expect(localStorage.getItem('refresh_token')).toBe('refresh-token');
    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
  });

  it('register function works correctly', async () => {
    const mockData = { id: '1', email: 'test@example.com' };
    authAPI.register.mockResolvedValue(mockData);
    authAPI.me.mockRejectedValue(new Error('Not authenticated'));
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    const userData = {
      email: 'test@example.com',
      username: 'testuser',
      password: 'TestPassword123',
    };
    
    await act(async () => {
      const data = await result.current.register(userData);
      expect(data).toEqual(mockData);
    });
    
    expect(authAPI.register).toHaveBeenCalledWith(userData);
  });

  it('logout function works correctly', async () => {
    localStorage.setItem('access_token', 'test-token');
    localStorage.setItem('refresh_token', 'refresh-token');
    authAPI.logout.mockResolvedValue({});
    authAPI.me.mockRejectedValue(new Error('Not authenticated'));
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await act(async () => {
      await result.current.logout();
    });
    
    expect(authAPI.logout).toHaveBeenCalled();
    expect(localStorage.getItem('access_token')).toBe(null);
    expect(localStorage.getItem('refresh_token')).toBe(null);
    expect(result.current.user).toBe(null);
    expect(result.current.isAuthenticated).toBe(false);
  });

  it('handles logout error gracefully', async () => {
    localStorage.setItem('access_token', 'test-token');
    authAPI.logout.mockRejectedValue(new Error('Network error'));
    authAPI.me.mockRejectedValue(new Error('Not authenticated'));
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await act(async () => {
      await result.current.logout();
    });
    
    // Should still clear local storage and user even if API call fails
    expect(localStorage.getItem('access_token')).toBe(null);
    expect(result.current.user).toBe(null);
  });

  it('throws error when used outside provider', () => {
    // Suppress console.error for this test
    const originalError = console.error;
    console.error = jest.fn();
    
    expect(() => {
      renderHook(() => useAuth());
    }).toThrow('useAuth must be used within AuthProvider');
    
    console.error = originalError;
  });
});
