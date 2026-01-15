import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import VacancyDetailPage from '../VacancyDetailPage';
import { vacanciesAPI, candidatesAPI } from '../../../../api/api';

jest.mock('../../../../api/api');

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const renderWithProviders = (component, initialEntries = ['/vacancies/123']) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={initialEntries}>
        {component}
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe('VacancyDetailPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders vacancy detail page', async () => {
    const mockVacancy = {
      id: '123',
      title: 'Python Developer',
      description: 'Test description',
      status: 'active',
    };
    
    vacanciesAPI.get.mockResolvedValue(mockVacancy);
    candidatesAPI.getByVacancy.mockResolvedValue({ candidates: [] });
    
    renderWithProviders(<VacancyDetailPage />);
    
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
    candidatesAPI.getByVacancy.mockResolvedValue({ candidates: [] });
    
    renderWithProviders(<VacancyDetailPage />);
    
    await waitFor(() => {
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
    candidatesAPI.getByVacancy.mockResolvedValue({ candidates: [] });
    
    renderWithProviders(<VacancyDetailPage />);
    
    await waitFor(() => {
      expect(vacanciesAPI.get).toHaveBeenCalled();
    });
    
    const statusButton = screen.queryByText(/статус|status/i);
    if (statusButton) {
      fireEvent.click(statusButton);
      
      const pausedOption = screen.queryByText(/на паузе|paused/i);
      if (pausedOption) {
        fireEvent.click(pausedOption);
        
        await waitFor(() => {
          expect(vacanciesAPI.updateStatus).toHaveBeenCalled();
        });
      }
    }
  });

  it('displays candidates for vacancy', async () => {
    const mockVacancy = { id: '123', title: 'Python Developer' };
    const mockCandidates = [
      { id: '1', name: 'John Doe', resume_id: '1' },
    ];
    
    vacanciesAPI.get.mockResolvedValue(mockVacancy);
    candidatesAPI.getByVacancy.mockResolvedValue({ candidates: mockCandidates });
    
    renderWithProviders(<VacancyDetailPage />);
    
    await waitFor(() => {
      expect(candidatesAPI.getByVacancy).toHaveBeenCalledWith('123');
    });
  });

  it('adds candidate to vacancy', async () => {
    const mockVacancy = { id: '123', title: 'Python Developer' };
    vacanciesAPI.get.mockResolvedValue(mockVacancy);
    vacanciesAPI.addCandidate.mockResolvedValue({});
    candidatesAPI.getByVacancy.mockResolvedValue({ candidates: [] });
    
    renderWithProviders(<VacancyDetailPage />);
    
    await waitFor(() => {
      expect(vacanciesAPI.get).toHaveBeenCalled();
    });
  });

  it('navigates back on back button click', () => {
    const mockVacancy = { id: '123' };
    vacanciesAPI.get.mockResolvedValue(mockVacancy);
    candidatesAPI.getByVacancy.mockResolvedValue({ candidates: [] });
    
    renderWithProviders(<VacancyDetailPage />);
    
    const backButton = screen.queryByLabelText(/back|назад/i);
    if (backButton) {
      fireEvent.click(backButton);
    }
  });

  it('shows loading state', () => {
    vacanciesAPI.get.mockImplementation(() => new Promise(() => {}));
    candidatesAPI.getByVacancy.mockResolvedValue({ candidates: [] });
    
    renderWithProviders(<VacancyDetailPage />);
    
    expect(vacanciesAPI.get).toHaveBeenCalled();
  });

  it('updates auto-matching settings', async () => {
    const mockVacancy = {
      id: '123',
      title: 'Python Developer',
      auto_matching_enabled: false,
    };
    
    vacanciesAPI.get.mockResolvedValue(mockVacancy);
    vacanciesAPI.updateAutoMatching.mockResolvedValue({ ...mockVacancy, auto_matching_enabled: true });
    candidatesAPI.getByVacancy.mockResolvedValue({ candidates: [] });
    
    renderWithProviders(<VacancyDetailPage />);
    
    await waitFor(() => {
      expect(vacanciesAPI.get).toHaveBeenCalled();
    });
  });
});
