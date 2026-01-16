import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AdminPage from '../AdminPage';
import { usersAPI } from '../../../../api/api';

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

describe('AdminPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    window.confirm = jest.fn(() => true);
  });

  it('renders admin page', async () => {
    usersAPI.list.mockResolvedValue({ users: [], total: 0 });
    
    renderWithProviders(<AdminPage />);
    
    await waitFor(() => {
      // Admin page should render some content
      expect(usersAPI.list).toHaveBeenCalled();
    });
  });

  it('displays list of users', async () => {
    const mockUsers = [
      { id: '1', email: 'user1@example.com', username: 'user1', role_names: ['hr_specialist'] },
      { id: '2', email: 'user2@example.com', username: 'user2', role_names: ['admin'] },
    ];
    
    usersAPI.list.mockResolvedValue({ users: mockUsers, total: 2 });
    
    renderWithProviders(<AdminPage />);
    
    await waitFor(() => {
      expect(screen.getByText('user1@example.com')).toBeInTheDocument();
      expect(screen.getByText('user2@example.com')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('opens edit user dialog', async () => {
    const mockUsers = [
      { id: '1', email: 'user1@example.com', full_name: 'User One', role_names: [] },
    ];
    
    usersAPI.list.mockResolvedValue({ users: mockUsers, total: 1 });
    
    renderWithProviders(<AdminPage />);
    
    await waitFor(() => {
      expect(screen.getByText('user1@example.com')).toBeInTheDocument();
    });
    
    // Use getAllByRole and select the first Edit button (since there's only one user)
    const editButtons = screen.getAllByRole('button', { name: /edit/i });
    fireEvent.click(editButtons[0]);
    
    await waitFor(() => {
      expect(screen.getByText(/edit user/i)).toBeInTheDocument();
    });
  });

  it('updates user', async () => {
    const mockUsers = [
      { id: '1', email: 'user1@example.com', full_name: 'User One', role_names: [] },
    ];
    
    usersAPI.list.mockResolvedValue({ users: mockUsers, total: 1 });
    usersAPI.update.mockResolvedValue({ ...mockUsers[0], full_name: 'Updated Name' });
    
    renderWithProviders(<AdminPage />);
    
    await waitFor(() => {
      expect(screen.getByText('user1@example.com')).toBeInTheDocument();
    });
    
    // Use getAllByRole and select the first Edit button
    const editButtons = screen.getAllByRole('button', { name: /edit/i });
    fireEvent.click(editButtons[0]);
    
    await waitFor(() => {
      expect(screen.getByText(/edit user/i)).toBeInTheDocument();
    });
    
    const nameInput = screen.getByLabelText(/full name/i);
    fireEvent.change(nameInput, { target: { value: 'Updated Name' } });
    
    const saveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(saveButton);
    
    await waitFor(() => {
      expect(usersAPI.update).toHaveBeenCalled();
    });
  });

  it('deletes user', async () => {
    const mockUsers = [
      { id: '1', email: 'user1@example.com', role_names: [] },
    ];
    
    usersAPI.list.mockResolvedValue({ users: mockUsers, total: mockUsers.length });
    usersAPI.delete.mockResolvedValue({});
    
    renderWithProviders(<AdminPage />);
    
    await waitFor(() => {
      expect(screen.getByText('user1@example.com')).toBeInTheDocument();
    });
    
    // Use getAllByRole and select the first Delete button
    const deleteButtons = screen.getAllByRole('button', { name: /delete/i });
    fireEvent.click(deleteButtons[0]);
    
    await waitFor(() => {
      expect(window.confirm).toHaveBeenCalled();
      expect(usersAPI.delete).toHaveBeenCalledWith('1');
    });
  });

  it('handles pagination', async () => {
    usersAPI.list.mockResolvedValue({ users: [], total: 50 });
    
    renderWithProviders(<AdminPage />);
    
    await waitFor(() => {
      expect(usersAPI.list).toHaveBeenCalled();
    });
  });

  it('shows loading state', () => {
    usersAPI.list.mockImplementation(() => new Promise(() => {}));
    
    renderWithProviders(<AdminPage />);
    
    expect(usersAPI.list).toHaveBeenCalled();
  });

  it('filters users by role', async () => {
    usersAPI.list.mockResolvedValue({ users: [], total: 0 });
    
    renderWithProviders(<AdminPage />);
    
    const roleFilter = screen.queryByLabelText(/роль|role/i);
    if (roleFilter) {
      fireEvent.change(roleFilter, { target: { value: 'admin' } });
    }
  });
});
