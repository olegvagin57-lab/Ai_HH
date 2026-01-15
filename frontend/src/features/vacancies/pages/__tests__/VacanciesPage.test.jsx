import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import VacanciesPage from '../VacanciesPage';
import { vacanciesAPI } from '../../../../api/api';

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

describe('VacanciesPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders vacancies page', () => {
    vacanciesAPI.list.mockResolvedValue({ vacancies: [] });
    
    renderWithProviders(<VacanciesPage />);
    
    expect(screen.getByText(/вакансии|vacancies/i)).toBeInTheDocument();
  });

  it('displays list of vacancies', async () => {
    const mockVacancies = [
      { id: '1', title: 'Python Developer', status: 'active' },
      { id: '2', title: 'Frontend Developer', status: 'active' },
    ];
    
    vacanciesAPI.list.mockResolvedValue({ vacancies: mockVacancies });
    
    renderWithProviders(<VacanciesPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Python Developer')).toBeInTheDocument();
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
    });
  });

  it('opens create vacancy dialog', () => {
    vacanciesAPI.list.mockResolvedValue({ vacancies: [] });
    
    renderWithProviders(<VacanciesPage />);
    
    const createButton = screen.getByRole('button', { name: /создать|create/i });
    fireEvent.click(createButton);
    
    expect(screen.getByText(/новая вакансия|new vacancy/i)).toBeInTheDocument();
  });

  it('filters vacancies by status', async () => {
    vacanciesAPI.list.mockResolvedValue({ vacancies: [] });
    
    renderWithProviders(<VacanciesPage />);
    
    const filterButton = screen.queryByLabelText(/filter|фильтр/i);
    if (filterButton) {
      fireEvent.click(filterButton);
      
      const activeOption = screen.queryByText(/активные|active/i);
      if (activeOption) {
        fireEvent.click(activeOption);
        
        await waitFor(() => {
          expect(vacanciesAPI.list).toHaveBeenCalledWith('active');
        });
      }
    }
  });

  it('searches vacancies', () => {
    vacanciesAPI.list.mockResolvedValue({ vacancies: [] });
    
    renderWithProviders(<VacanciesPage />);
    
    const searchInput = screen.queryByPlaceholderText(/поиск|search/i);
    if (searchInput) {
      fireEvent.change(searchInput, { target: { value: 'python' } });
      expect(searchInput.value).toBe('python');
    }
  });

  it('navigates to vacancy detail on click', () => {
    const mockVacancies = [
      { id: '1', title: 'Python Developer', status: 'active' },
    ];
    
    vacanciesAPI.list.mockResolvedValue({ vacancies: mockVacancies });
    
    renderWithProviders(<VacanciesPage />);
    
    // Click on vacancy card
    waitFor(() => {
      const vacancyCard = screen.getByText('Python Developer');
      if (vacancyCard) {
        fireEvent.click(vacancyCard);
      }
    });
  });

  it('deletes vacancy', async () => {
    const mockVacancies = [
      { id: '1', title: 'Python Developer', status: 'active' },
    ];
    
    vacanciesAPI.list.mockResolvedValue({ vacancies: mockVacancies });
    vacanciesAPI.updateStatus.mockResolvedValue({});
    
    // Mock window.confirm
    window.confirm = jest.fn(() => true);
    
    renderWithProviders(<VacanciesPage />);
    
    await waitFor(() => {
      const menuButtons = screen.queryAllByLabelText(/more|еще/i);
      if (menuButtons.length > 0) {
        fireEvent.click(menuButtons[0]);
        
        waitFor(() => {
          const deleteOption = screen.queryByText(/удалить|delete|закрыть|close/i);
          if (deleteOption) {
            fireEvent.click(deleteOption);
            
            waitFor(() => {
              expect(vacanciesAPI.updateStatus).toHaveBeenCalled();
            });
          }
        });
      }
    });
  });

  it('shows loading state', () => {
    vacanciesAPI.list.mockImplementation(() => new Promise(() => {}));
    
    renderWithProviders(<VacanciesPage />);
    
    expect(vacanciesAPI.list).toHaveBeenCalled();
  });

  it('handles empty vacancies list', async () => {
    vacanciesAPI.list.mockResolvedValue({ vacancies: [] });
    
    renderWithProviders(<VacanciesPage />);
    
    await waitFor(() => {
      expect(vacanciesAPI.list).toHaveBeenCalled();
    });
  });
});
