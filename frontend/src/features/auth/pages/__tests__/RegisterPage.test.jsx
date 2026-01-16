import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import RegisterPage from '../RegisterPage';
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

describe('RegisterPage', () => {
  const mockRegister = jest.fn();
  const mockLogin = jest.fn();
  const mockNavigate = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    
    useAuth.mockReturnValue({
      register: mockRegister,
      login: mockLogin,
      user: null,
      loading: false,
      isAuthenticated: false,
    });

    // Mock useNavigate
    jest.mock('react-router-dom', () => ({
      ...jest.requireActual('react-router-dom'),
      useNavigate: () => mockNavigate,
    }));
  });

  it('renders registration form', () => {
    renderWithProviders(<RegisterPage />);
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/имя пользователя/i)).toBeInTheDocument();
    // There are two password fields - check that at least one exists
    expect(screen.getAllByLabelText(/пароль/i).length).toBeGreaterThan(0);
    expect(screen.getByLabelText(/подтвердите пароль/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /зарегистрироваться/i })).toBeInTheDocument();
  });

  it('validates email field', async () => {
    renderWithProviders(<RegisterPage />);
    
    const emailInput = screen.getByLabelText(/email/i);
    fireEvent.blur(emailInput);
    
    await waitFor(() => {
      expect(screen.getByText(/поле обязательно|required/i)).toBeInTheDocument();
    });

    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.blur(emailInput);
    
    await waitFor(() => {
      expect(screen.getByText(/корректный email/i)).toBeInTheDocument();
    });
  });

  it('validates username field', async () => {
    renderWithProviders(<RegisterPage />);
    
    const usernameInput = screen.getByLabelText(/имя пользователя|username/i);
    fireEvent.change(usernameInput, { target: { value: 'ab' } });
    fireEvent.blur(usernameInput);
    
    await waitFor(() => {
      expect(screen.getByText(/минимум 3 символа/i)).toBeInTheDocument();
    });
  });

  it('validates password field', async () => {
    renderWithProviders(<RegisterPage />);
    
    // There are two password fields - get the first one (password)
    const passwordInputs = screen.getAllByLabelText(/пароль/i);
    const passwordInput = passwordInputs[0];
    fireEvent.change(passwordInput, { target: { value: 'short' } });
    fireEvent.blur(passwordInput);
    
    await waitFor(() => {
      expect(screen.getByText(/минимум 8 символов/i)).toBeInTheDocument();
    });
  });

  it('validates password confirmation', async () => {
    renderWithProviders(<RegisterPage />);
    
    // There are two password fields - get the first one (password)
    const passwordInputs = screen.getAllByLabelText(/пароль/i);
    const passwordInput = passwordInputs[0];
    const confirmPasswordInput = screen.getByLabelText(/подтвердите пароль/i);
    
    fireEvent.change(passwordInput, { target: { value: 'TestPassword123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'DifferentPassword' } });
    fireEvent.blur(confirmPasswordInput);
    
    await waitFor(() => {
      expect(screen.getByText(/пароли не совпадают|passwords do not match/i)).toBeInTheDocument();
    });
  });

  it('shows password strength indicator', async () => {
    renderWithProviders(<RegisterPage />);
    
    // There are two password fields - get the first one (password)
    const passwordInputs = screen.getAllByLabelText(/пароль/i);
    const passwordInput = passwordInputs[0];
    fireEvent.change(passwordInput, { target: { value: 'TestPassword123' } });
    
    await waitFor(() => {
      expect(screen.getByText(/надёжность|strength/i)).toBeInTheDocument();
    });
  });

  it('submits form with valid data', async () => {
    mockRegister.mockResolvedValue({});
    mockLogin.mockResolvedValue({ user: { id: '1', email: 'test@example.com' } });
    
    renderWithProviders(<RegisterPage />);
    
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/имя пользователя|username/i), { target: { value: 'testuser' } });
    // There are two password fields - get both
    const passwordInputs = screen.getAllByLabelText(/пароль/i);
    fireEvent.change(passwordInputs[0], { target: { value: 'TestPassword123' } });
    fireEvent.change(screen.getByLabelText(/подтвердите пароль/i), { target: { value: 'TestPassword123' } });
    
    const submitButton = screen.getByRole('button', { name: /зарегистрироваться|register/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith({
        email: 'test@example.com',
        username: 'testuser',
        password: 'TestPassword123',
      });
    });
  });

  it('handles registration error', async () => {
    const errorMessage = 'Email already exists';
    mockRegister.mockRejectedValue({
      response: { data: { detail: errorMessage } },
    });
    
    renderWithProviders(<RegisterPage />);
    
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/имя пользователя|username/i), { target: { value: 'testuser' } });
    // There are two password fields - get both
    const passwordInputs = screen.getAllByLabelText(/пароль/i);
    fireEvent.change(passwordInputs[0], { target: { value: 'TestPassword123' } });
    fireEvent.change(screen.getByLabelText(/подтвердите пароль/i), { target: { value: 'TestPassword123' } });
    
    const submitButton = screen.getByRole('button', { name: /зарегистрироваться|register/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('toggles password visibility', () => {
    renderWithProviders(<RegisterPage />);
    
    // There are two password fields - get the first one (password)
    const passwordInputs = screen.getAllByLabelText(/пароль/i);
    const passwordInput = passwordInputs[0];
    expect(passwordInput).toHaveAttribute('type', 'password');
    
    const toggleButton = screen.getAllByLabelText(/toggle password visibility/i)[0];
    fireEvent.click(toggleButton);
    
    expect(passwordInput).toHaveAttribute('type', 'text');
  });
});
