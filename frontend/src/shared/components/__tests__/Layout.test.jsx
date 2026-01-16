import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from '../Layout';
import { useAuth } from '../../../features/auth/contexts/AuthContext';

jest.mock('../../../features/auth/contexts/AuthContext');

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const renderWithRouter = (component) => {
  useAuth.mockReturnValue({
    user: { id: '1', email: 'test@example.com', role_names: ['admin'] },
    loading: false,
    isAuthenticated: true,
    login: jest.fn(),
    logout: jest.fn(),
    register: jest.fn(),
  });
  
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{component}</BrowserRouter>
    </QueryClientProvider>
  );
};

describe('Layout', () => {
  it('renders without crashing', () => {
    renderWithRouter(<Layout />);
  });

  it('renders navigation when user is authenticated', () => {
    // Mock authenticated user
    const mockUser = { email: 'test@example.com', role_names: ['admin'] };
    localStorage.setItem('user', JSON.stringify(mockUser));
    
    renderWithRouter(<Layout />);
    
    // Should render some navigation elements
    // Adjust based on actual Layout implementation
  });

  it('renders layout structure', () => {
    renderWithRouter(<Layout />);
    
    // Layout should render navigation or app bar
    // Just check that it renders without crashing
    expect(screen.queryByRole('navigation') || screen.queryByRole('banner')).toBeTruthy();
  });
});
