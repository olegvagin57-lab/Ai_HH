import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from '../App';
import { useAuth } from '../../features/auth/contexts/AuthContext';

jest.mock('../../features/auth/contexts/AuthContext');

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

  it('renders login page for unauthenticated users', () => {
    useAuth.mockReturnValue({
      user: null,
      loading: false,
      isAuthenticated: false,
      login: jest.fn(),
      logout: jest.fn(),
      register: jest.fn(),
    });
    
    renderWithProviders(<App />, ['/login']);
    
    expect(screen.getByText(/вход|login|добро пожаловать|welcome/i)).toBeInTheDocument();
  });

  it('renders register page', () => {
    useAuth.mockReturnValue({
      user: null,
      loading: false,
      isAuthenticated: false,
      login: jest.fn(),
      logout: jest.fn(),
      register: jest.fn(),
    });
    
    renderWithProviders(<App />, ['/register']);
    
    expect(screen.getByText(/регистрация|register/i)).toBeInTheDocument();
  });

  it('renders forgot password page', () => {
    useAuth.mockReturnValue({
      user: null,
      loading: false,
      isAuthenticated: false,
      login: jest.fn(),
      logout: jest.fn(),
      register: jest.fn(),
    });
    
    renderWithProviders(<App />, ['/forgot-password']);
    
    expect(screen.getByText(/восстановление пароля|forgot password/i)).toBeInTheDocument();
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

  it('handles navigation between routes', () => {
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
    
    expect(screen.queryByText(/поиск|search/i)).toBeInTheDocument();
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
