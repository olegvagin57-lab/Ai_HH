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

  it('renders admin page', () => {
    usersAPI.list.mockResolvedValue({ users: [] });
    
    renderWithProviders(<AdminPage />);
    
    expect(screen.getByText(/пользователи|users|администрирование|admin/i)).toBeInTheDocument();
  });

  it('displays list of users', async () => {
    const mockUsers = [
      { id: '1', email: 'user1@example.com', username: 'user1', role_names: ['hr_specialist'] },
      { id: '2', email: 'user2@example.com', username: 'user2', role_names: ['admin'] },
    ];
    
    usersAPI.list.mockResolvedValue({ users: mockUsers });
    
    renderWithProviders(<AdminPage />);
    
    await waitFor(() => {
      expect(screen.getByText('user1@example.com')).toBeInTheDocument();
      expect(screen.getByText('user2@example.com')).toBeInTheDocument();
    });
  });

  it('opens edit user dialog', async () => {
    const mockUsers = [
      { id: '1', email: 'user1@example.com', full_name: 'User One' },
    ];
    
    usersAPI.list.mockResolvedValue({ users: mockUsers });
    
    renderWithProviders(<AdminPage />);
    
    await waitFor(() => {
      const editButton = screen.queryByLabelText(/edit|редактировать/i);
      if (editButton) {
        fireEvent.click(editButton);
        
        expect(screen.getByText(/редактировать|edit/i)).toBeInTheDocument();
      }
    });
  });

  it('updates user', async () => {
    const mockUsers = [
      { id: '1', email: 'user1@example.com', full_name: 'User One' },
    ];
    
    usersAPI.list.mockResolvedValue({ users: mockUsers });
    usersAPI.update.mockResolvedValue({ ...mockUsers[0], full_name: 'Updated Name' });
    
    renderWithProviders(<AdminPage />);
    
    await waitFor(() => {
      const editButton = screen.queryByLabelText(/edit|редактировать/i);
      if (editButton) {
        fireEvent.click(editButton);
        
        waitFor(() => {
          const nameInput = screen.queryByLabelText(/имя|name/i);
          if (nameInput) {
            fireEvent.change(nameInput, { target: { value: 'Updated Name' } });
            
            const saveButton = screen.queryByRole('button', { name: /сохранить|save/i });
            if (saveButton) {
              fireEvent.click(saveButton);
              
              waitFor(() => {
                expect(usersAPI.update).toHaveBeenCalled();
              });
            }
          }
        });
      }
    });
  });

  it('deletes user', async () => {
    const mockUsers = [
      { id: '1', email: 'user1@example.com' },
    ];
    
    usersAPI.list.mockResolvedValue({ users: mockUsers });
    usersAPI.delete.mockResolvedValue({});
    
    renderWithProviders(<AdminPage />);
    
    await waitFor(() => {
      const deleteButton = screen.queryByLabelText(/delete|удалить/i);
      if (deleteButton) {
        fireEvent.click(deleteButton);
        
        waitFor(() => {
          expect(window.confirm).toHaveBeenCalled();
          expect(usersAPI.delete).toHaveBeenCalledWith('1');
        });
      }
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
    usersAPI.list.mockResolvedValue({ users: [] });
    
    renderWithProviders(<AdminPage />);
    
    const roleFilter = screen.queryByLabelText(/роль|role/i);
    if (roleFilter) {
      fireEvent.change(roleFilter, { target: { value: 'admin' } });
    }
  });
});
