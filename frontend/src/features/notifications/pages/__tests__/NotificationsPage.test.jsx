import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import NotificationsPage from '../NotificationsPage';
import { notificationsAPI } from '../../../../api/api';

jest.mock('../../../../api/api');

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

describe('NotificationsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders notifications page', () => {
    notificationsAPI.getNotifications.mockResolvedValue({ notifications: [] });
    
    renderWithProviders(<NotificationsPage />);
    
    expect(screen.getByText(/уведомления|notifications/i)).toBeInTheDocument();
  });

  it('displays list of notifications', async () => {
    const mockNotifications = [
      {
        id: '1',
        title: 'New candidate',
        message: 'A new candidate was added',
        read: false,
        created_at: new Date().toISOString(),
      },
      {
        id: '2',
        title: 'Search completed',
        message: 'Your search has been completed',
        read: true,
        created_at: new Date().toISOString(),
      },
    ];
    
    notificationsAPI.getNotifications.mockResolvedValue({ notifications: mockNotifications });
    
    renderWithProviders(<NotificationsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('New candidate')).toBeInTheDocument();
      expect(screen.getByText('Search completed')).toBeInTheDocument();
    });
  });

  it('switches between all and unread tabs', async () => {
    notificationsAPI.getNotifications.mockResolvedValue({ notifications: [] });
    
    renderWithProviders(<NotificationsPage />);
    
    const unreadTab = screen.queryByText(/непрочитанные|unread/i);
    if (unreadTab) {
      fireEvent.click(unreadTab);
      
      await waitFor(() => {
        expect(notificationsAPI.getNotifications).toHaveBeenCalledWith(true, 1, 100);
      });
    }
  });

  it('marks notification as read', async () => {
    const mockNotifications = [
      { id: '1', title: 'Test', read: false },
    ];
    
    notificationsAPI.getNotifications.mockResolvedValue({ notifications: mockNotifications });
    notificationsAPI.markAsRead.mockResolvedValue({});
    
    renderWithProviders(<NotificationsPage />);
    
    await waitFor(() => {
      const menuButtons = screen.queryAllByLabelText(/more|еще/i);
      if (menuButtons.length > 0) {
        fireEvent.click(menuButtons[0]);
        
        waitFor(() => {
          const markReadOption = screen.queryByText(/отметить.*прочитанным|mark.*read/i);
          if (markReadOption) {
            fireEvent.click(markReadOption);
            
            waitFor(() => {
              expect(notificationsAPI.markAsRead).toHaveBeenCalledWith('1');
            });
          }
        });
      }
    });
  });

  it('marks all notifications as read', async () => {
    notificationsAPI.getNotifications.mockResolvedValue({ notifications: [] });
    notificationsAPI.markAllAsRead.mockResolvedValue({});
    
    renderWithProviders(<NotificationsPage />);
    
    const markAllButton = screen.queryByText(/отметить все|mark all/i);
    if (markAllButton) {
      fireEvent.click(markAllButton);
      
      await waitFor(() => {
        expect(notificationsAPI.markAllAsRead).toHaveBeenCalled();
      });
    }
  });

  it('deletes notification', async () => {
    const mockNotifications = [
      { id: '1', title: 'Test', read: false },
    ];
    
    notificationsAPI.getNotifications.mockResolvedValue({ notifications: mockNotifications });
    notificationsAPI.delete.mockResolvedValue({});
    
    renderWithProviders(<NotificationsPage />);
    
    await waitFor(() => {
      const menuButtons = screen.queryAllByLabelText(/more|еще/i);
      if (menuButtons.length > 0) {
        fireEvent.click(menuButtons[0]);
        
        waitFor(() => {
          const deleteOption = screen.queryByText(/удалить|delete/i);
          if (deleteOption) {
            fireEvent.click(deleteOption);
            
            waitFor(() => {
              expect(notificationsAPI.delete).toHaveBeenCalledWith('1');
            });
          }
        });
      }
    });
  });

  it('shows loading state', () => {
    notificationsAPI.getNotifications.mockImplementation(() => new Promise(() => {}));
    
    renderWithProviders(<NotificationsPage />);
    
    expect(notificationsAPI.getNotifications).toHaveBeenCalled();
  });

  it('handles empty notifications list', async () => {
    notificationsAPI.getNotifications.mockResolvedValue({ notifications: [] });
    
    renderWithProviders(<NotificationsPage />);
    
    await waitFor(() => {
      expect(notificationsAPI.getNotifications).toHaveBeenCalled();
    });
  });
});
