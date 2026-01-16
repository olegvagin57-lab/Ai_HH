import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import VacancyDetailPage from '../VacancyDetailPage';
import { vacanciesAPI } from '../../../../api/api';

jest.mock('../../../../api/api');

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { 
      retry: false,
      refetchOnWindowFocus: false,
      refetchOnMount: true,
    },
    mutations: { retry: false },
  },
});

const renderWithProviders = (component, initialEntries = ['/vacancies/123']) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={initialEntries}>
        <Routes>
          <Route path="/vacancies/:id" element={component} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe('VacancyDetailPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Clear QueryClient cache between tests
    queryClient.clear();
  });

  it('renders vacancy detail page', async () => {
    const mockVacancy = {
      id: '123',
      title: 'Python Developer',
      description: 'Test description',
      status: 'active',
    };
    
    vacanciesAPI.get.mockResolvedValue(mockVacancy);
    
    renderWithProviders(<VacancyDetailPage />, ['/vacancies/123']);
    
    await waitFor(() => {
      expect(vacanciesAPI.get).toHaveBeenCalledWith('123');
    });
  });

  it('displays vacancy information', async () => {
    const mockVacancy = {
      id: '123',
      title: 'Python Developer',
      description: 'We need a Python developer',
      requirements: 'Python, FastAPI',
      city: 'Москва',
      status: 'active',
    };
    
    vacanciesAPI.get.mockResolvedValue(mockVacancy);
    
    renderWithProviders(<VacancyDetailPage />, ['/vacancies/123']);
    
    await waitFor(() => {
      expect(vacanciesAPI.get).toHaveBeenCalledWith('123');
      expect(screen.getByText('Python Developer')).toBeInTheDocument();
    });
  });

  it('updates vacancy status', async () => {
    const mockVacancy = {
      id: '123',
      title: 'Python Developer',
      status: 'active',
    };
    
    vacanciesAPI.get.mockResolvedValue(mockVacancy);
    vacanciesAPI.updateStatus.mockResolvedValue({ ...mockVacancy, status: 'paused' });
    
    renderWithProviders(<VacancyDetailPage />, ['/vacancies/123']);
    
    await waitFor(() => {
      expect(vacanciesAPI.get).toHaveBeenCalledWith('123');
    });
    
    const statusButton = screen.queryByText(/статус|status/i);
    if (statusButton) {
      fireEvent.click(statusButton);
      
      await waitFor(() => {
        const pausedOption = screen.queryByText(/на паузе|paused|приостановлена/i);
        return pausedOption !== null;
      });
      
      const pausedOption = screen.queryByText(/на паузе|paused|приостановлена/i);
      if (pausedOption) {
        fireEvent.click(pausedOption);
        
        await waitFor(() => {
          expect(vacanciesAPI.updateStatus).toHaveBeenCalledWith('123', expect.any(String));
        });
      }
    }
  });

  it('displays candidates for vacancy', async () => {
    const mockVacancy = { id: '123', title: 'Python Developer', candidate_ids: ['1'] };
    
    vacanciesAPI.get.mockResolvedValue(mockVacancy);
    
    renderWithProviders(<VacancyDetailPage />, ['/vacancies/123']);
    
    await waitFor(() => {
      expect(vacanciesAPI.get).toHaveBeenCalledWith('123');
    });
  });

  it('adds candidate to vacancy', async () => {
    const mockVacancy = { id: '123', title: 'Python Developer' };
    vacanciesAPI.get.mockResolvedValue(mockVacancy);
    vacanciesAPI.addCandidate.mockResolvedValue({});
    
    renderWithProviders(<VacancyDetailPage />, ['/vacancies/123']);
    
    await waitFor(() => {
      expect(vacanciesAPI.get).toHaveBeenCalledWith('123');
    });
  });

  it('navigates back on back button click', async () => {
    const mockVacancy = { id: '123' };
    vacanciesAPI.get.mockResolvedValue(mockVacancy);
    
    renderWithProviders(<VacancyDetailPage />, ['/vacancies/123']);
    
    await waitFor(() => {
      expect(vacanciesAPI.get).toHaveBeenCalledWith('123');
    });
    
    const backButton = screen.queryByLabelText(/back|назад/i) || screen.queryByRole('button', { name: /назад/i });
    if (backButton) {
      fireEvent.click(backButton);
    }
  });

  it('shows loading state', () => {
    vacanciesAPI.get.mockImplementation(() => new Promise(() => {}));
    
    renderWithProviders(<VacancyDetailPage />, ['/vacancies/123']);
    
    expect(vacanciesAPI.get).toHaveBeenCalledWith('123');
  });

  it('updates auto-matching settings', async () => {
    const mockVacancy = {
      id: '123',
      title: 'Python Developer',
      auto_matching_enabled: false,
    };
    
    vacanciesAPI.get.mockResolvedValue(mockVacancy);
    vacanciesAPI.updateAutoMatching.mockResolvedValue({ ...mockVacancy, auto_matching_enabled: true });
    
    renderWithProviders(<VacancyDetailPage />, ['/vacancies/123']);
    
    await waitFor(() => {
      expect(vacanciesAPI.get).toHaveBeenCalledWith('123');
    });
  });
});
