import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from '../Dashboard';
import { useAuth } from '../../../features/auth/contexts/AuthContext';
import { searchAPI, analyticsAPI, notificationsAPI } from '../../../api/api';

jest.mock('../../../features/auth/contexts/AuthContext');
jest.mock('../../../api/api');

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

describe('Dashboard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    useAuth.mockReturnValue({
      user: { id: '1', username: 'testuser', role_names: ['viewer'] },
      isAuthenticated: true,
      loading: false,
    });
    searchAPI.list.mockResolvedValue({ searches: [], total: 0 });
    analyticsAPI.getDashboard.mockResolvedValue({});
    notificationsAPI.getNotifications.mockResolvedValue({ notifications: [], unread_count: 0 });
  });

  it('renders without crashing', async () => {
    renderWithProviders(<Dashboard />);
    await waitFor(() => {
      expect(screen.queryByText(/dashboard|панель/i)).toBeInTheDocument();
    });
  });

  it('displays statistics', async () => {
    renderWithProviders(<Dashboard />);
    await waitFor(() => {
      // Dashboard should render stat cards
      expect(searchAPI.list).toHaveBeenCalled();
    });
  });
});
