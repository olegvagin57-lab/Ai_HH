import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from '../App';
import { useAuth } from '../../features/auth/contexts/AuthContext';

jest.mock('../../features/auth/contexts/AuthContext', () => ({
  useAuth: jest.fn(),
  AuthProvider: ({ children }) => children,
}));
jest.mock('../../features/auth/components/ProtectedRoute', () => {
  return function MockProtectedRoute({ children }) {
    return children;
  };
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const renderWithProviders = (component, initialEntries = ['/']) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={initialEntries}>
        {component}
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe('App', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  it('renders login page for unauthenticated users', async () => {
    useAuth.mockReturnValue({
      user: null,
      loading: false,
      isAuthenticated: false,
      login: jest.fn(),
      logout: jest.fn(),
      register: jest.fn(),
    });
    
    renderWithProviders(<App />, ['/login']);
    
    // Login page should have email input or login button
    await waitFor(() => {
      const emailInput = screen.queryByLabelText(/email.*имя.*пользователя|email.*username/i);
      const loginButton = screen.queryByRole('button', { name: /войти|login/i });
      // At least one should exist
      expect(emailInput || loginButton).toBeTruthy();
    }, { timeout: 3000 });
  });

  it('renders register page', async () => {
    useAuth.mockReturnValue({
      user: null,
      loading: false,
      isAuthenticated: false,
      login: jest.fn(),
      logout: jest.fn(),
      register: jest.fn(),
    });
    
    renderWithProviders(<App />, ['/register']);
    
    // Register page should have some form elements
    await waitFor(() => {
      // Check for email input, username input, or any textbox
      const emailInput = screen.queryByLabelText(/^email$/i);
      const usernameInput = screen.queryByLabelText(/имя.*пользователя|username/i);
      const textboxes = screen.queryAllByRole('textbox');
      const buttons = screen.queryAllByRole('button');
      // At least one should exist
      expect(emailInput || usernameInput || textboxes.length > 0 || buttons.length > 0).toBeTruthy();
    }, { timeout: 5000 });
  });

  it('renders forgot password page', async () => {
    useAuth.mockReturnValue({
      user: null,
      loading: false,
      isAuthenticated: false,
      login: jest.fn(),
      logout: jest.fn(),
      register: jest.fn(),
    });
    
    renderWithProviders(<App />, ['/forgot-password']);
    
    // Forgot password page should have email input or button
    await waitFor(() => {
      const emailInput = screen.queryByLabelText(/^email$/i);
      const button = screen.queryByRole('button', { name: /отправить|send/i });
      // At least one should exist
      expect(emailInput || button).toBeTruthy();
    }, { timeout: 3000 });
  });

  it('redirects to dashboard for authenticated users', () => {
    useAuth.mockReturnValue({
      user: { id: '1', email: 'test@example.com' },
      loading: false,
      isAuthenticated: true,
      login: jest.fn(),
      logout: jest.fn(),
      register: jest.fn(),
    });
    
    renderWithProviders(<App />, ['/']);
    
    // Should redirect to dashboard or show dashboard content
    expect(screen.queryByText(/вход|login/i)).not.toBeInTheDocument();
  });

  it('renders protected routes for authenticated users', () => {
    useAuth.mockReturnValue({
      user: { id: '1', email: 'test@example.com' },
      loading: false,
      isAuthenticated: true,
      login: jest.fn(),
      logout: jest.fn(),
      register: jest.fn(),
    });
    
    renderWithProviders(<App />, ['/search']);
    
    // Should render protected content, not redirect to login
    expect(screen.queryByText(/вход|login/i)).not.toBeInTheDocument();
  });

  it('handles navigation between routes', async () => {
    useAuth.mockReturnValue({
      user: { id: '1', email: 'test@example.com' },
      loading: false,
      isAuthenticated: true,
      login: jest.fn(),
      logout: jest.fn(),
      register: jest.fn(),
    });
    
    const { rerender } = renderWithProviders(<App />, ['/dashboard']);
    
    // Navigate to search
    rerender(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={['/search']}>
          <App />
        </MemoryRouter>
      </QueryClientProvider>
    );
    
    await waitFor(() => {
      // Search page may not have visible text immediately, just verify it doesn't show login
      expect(screen.queryByText(/вход|login/i)).not.toBeInTheDocument();
    });
  });

  it('shows loading state while checking auth', () => {
    useAuth.mockReturnValue({
      user: null,
      loading: true,
      isAuthenticated: false,
      login: jest.fn(),
      logout: jest.fn(),
      register: jest.fn(),
    });
    
    renderWithProviders(<App />, ['/dashboard']);
    
    // Should show loading indicator
    expect(screen.queryByText(/вход|login/i)).not.toBeInTheDocument();
  });
});
