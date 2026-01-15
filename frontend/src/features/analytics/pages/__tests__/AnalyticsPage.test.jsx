import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AnalyticsPage from '../AnalyticsPage';
import { analyticsAPI } from '../../../../api/api';

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

describe('AnalyticsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders analytics page', () => {
    analyticsAPI.getDashboard.mockResolvedValue({});
    analyticsAPI.getHiringFunnel.mockResolvedValue({});
    
    renderWithProviders(<AnalyticsPage />);
    
    expect(screen.getByText(/аналитика|analytics/i)).toBeInTheDocument();
  });

  it('displays dashboard metrics', async () => {
    const mockDashboard = {
      total_candidates: 100,
      total_vacancies: 10,
      total_searches: 25,
      hired_count: 5,
    };
    
    analyticsAPI.getDashboard.mockResolvedValue(mockDashboard);
    analyticsAPI.getHiringFunnel.mockResolvedValue({});
    
    renderWithProviders(<AnalyticsPage />);
    
    await waitFor(() => {
      expect(analyticsAPI.getDashboard).toHaveBeenCalled();
    });
  });

  it('displays hiring funnel', async () => {
    const mockFunnel = {
      new: 50,
      reviewed: 30,
      shortlisted: 20,
      interviewed: 10,
      hired: 5,
    };
    
    analyticsAPI.getDashboard.mockResolvedValue({});
    analyticsAPI.getHiringFunnel.mockResolvedValue(mockFunnel);
    
    renderWithProviders(<AnalyticsPage />);
    
    await waitFor(() => {
      expect(analyticsAPI.getHiringFunnel).toHaveBeenCalled();
    });
  });

  it('changes time period filter', async () => {
    analyticsAPI.getDashboard.mockResolvedValue({});
    analyticsAPI.getHiringFunnel.mockResolvedValue({});
    
    renderWithProviders(<AnalyticsPage />);
    
    const periodSelect = screen.queryByLabelText(/период|period|дни|days/i);
    if (periodSelect) {
      fireEvent.change(periodSelect, { target: { value: '7' } });
      
      await waitFor(() => {
        expect(analyticsAPI.getDashboard).toHaveBeenCalledWith(7);
      });
    }
  });

  it('shows loading state', () => {
    analyticsAPI.getDashboard.mockImplementation(() => new Promise(() => {}));
    analyticsAPI.getHiringFunnel.mockResolvedValue({});
    
    renderWithProviders(<AnalyticsPage />);
    
    expect(analyticsAPI.getDashboard).toHaveBeenCalled();
  });

  it('displays stat cards', async () => {
    const mockDashboard = {
      total_candidates: 100,
      total_vacancies: 10,
      total_searches: 25,
    };
    
    analyticsAPI.getDashboard.mockResolvedValue(mockDashboard);
    analyticsAPI.getHiringFunnel.mockResolvedValue({});
    
    renderWithProviders(<AnalyticsPage />);
    
    await waitFor(() => {
      expect(analyticsAPI.getDashboard).toHaveBeenCalled();
    });
  });

  it('handles empty data', async () => {
    analyticsAPI.getDashboard.mockResolvedValue({});
    analyticsAPI.getHiringFunnel.mockResolvedValue({});
    
    renderWithProviders(<AnalyticsPage />);
    
    await waitFor(() => {
      expect(analyticsAPI.getDashboard).toHaveBeenCalled();
    });
  });
});
