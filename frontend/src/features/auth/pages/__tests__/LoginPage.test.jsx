import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import LoginPage from '../LoginPage';
import { useAuth } from '../../contexts/AuthContext';

jest.mock('../../contexts/AuthContext');

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const renderWithProviders = (component) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{component}</BrowserRouter>
    </QueryClientProvider>
  );
};

describe('LoginPage', () => {
  beforeEach(() => {
    localStorage.clear();
    jest.clearAllMocks();
    useAuth.mockReturnValue({
      user: null,
      loading: false,
      isAuthenticated: false,
      login: jest.fn(),
      logout: jest.fn(),
      register: jest.fn(),
    });
  });

  it('renders login form', () => {
    renderWithProviders(<LoginPage />);
    
    // Should have email/username input - use label text in Russian
    const emailInput = screen.getByLabelText(/email или имя пользователя/i);
    expect(emailInput).toBeInTheDocument();
    
    // Should have password input - use label text in Russian
    const passwordInput = screen.getByLabelText(/пароль/i);
    expect(passwordInput).toBeInTheDocument();
    
    // Should have submit button - use text in Russian
    const submitButton = screen.getByRole('button', { name: /войти/i });
    expect(submitButton).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    renderWithProviders(<LoginPage />);
    
    const submitButton = screen.getByRole('button', { name: /войти/i });
    fireEvent.click(submitButton);
    
    // Should show validation errors in Russian
    await waitFor(() => {
      const errorMessages = screen.queryAllByText(/обязательно|заполнения/i);
      expect(errorMessages.length).toBeGreaterThan(0);
    }, { timeout: 2000 });
  });

  it('submits form with valid data', async () => {
    const mockLogin = jest.fn().mockResolvedValue({});
    useAuth.mockReturnValue({
      user: null,
      loading: false,
      isAuthenticated: false,
      login: mockLogin,
      logout: jest.fn(),
      register: jest.fn(),
    });
    
    renderWithProviders(<LoginPage />);
    
    const emailInput = screen.getByLabelText(/email или имя пользователя/i);
    const passwordInput = screen.getByLabelText(/пароль/i);
    const submitButton = screen.getByRole('button', { name: /войти/i });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'TestPassword123' } });
    fireEvent.click(submitButton);
    
    // Should attempt to submit
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'TestPassword123');
    }, { timeout: 2000 });
  });
});
