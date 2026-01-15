import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter, Routes, Route, MemoryRouter } from 'react-router-dom';
import ProtectedRoute from '../ProtectedRoute';
import { useAuth } from '../../contexts/AuthContext';

jest.mock('../../contexts/AuthContext');

const TestComponent = () => <div>Protected Content</div>;

describe('ProtectedRoute', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('redirects to login when not authenticated', () => {
    useAuth.mockReturnValue({
      isAuthenticated: false,
      loading: false,
    });

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route path="/protected" element={
            <ProtectedRoute>
              <TestComponent />
            </ProtectedRoute>
          } />
          <Route path="/login" element={<div>Login Page</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Login Page')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('shows loading spinner when checking authentication', () => {
    useAuth.mockReturnValue({
      isAuthenticated: false,
      loading: true,
    });

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route path="/protected" element={
            <ProtectedRoute>
              <TestComponent />
            </ProtectedRoute>
          } />
        </Routes>
      </MemoryRouter>
    );

    // Should show loading indicator (CircularProgress)
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('renders children when authenticated', () => {
    useAuth.mockReturnValue({
      isAuthenticated: true,
      loading: false,
    });

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route path="/protected" element={
            <ProtectedRoute>
              <TestComponent />
            </ProtectedRoute>
          } />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('renders Outlet when no children provided', () => {
    useAuth.mockReturnValue({
      isAuthenticated: true,
      loading: false,
    });

    const NestedComponent = () => <div>Nested Content</div>;

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route path="/protected" element={<ProtectedRoute />}>
            <Route index element={<NestedComponent />} />
          </Route>
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Nested Content')).toBeInTheDocument();
  });
});
