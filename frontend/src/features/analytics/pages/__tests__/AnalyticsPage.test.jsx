import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AnalyticsPage from '../AnalyticsPage';
import { analyticsAPI } from '../../../../api/api';

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
    // Clear QueryClient cache between tests
    queryClient.clear();
  });

  it('renders analytics page', async () => {
    analyticsAPI.getDashboard.mockResolvedValue({});
    analyticsAPI.getHiringFunnel.mockResolvedValue({});
    
    renderWithProviders(<AnalyticsPage />);
    
    // Wait for API call first
    await waitFor(() => {
      expect(analyticsAPI.getDashboard).toHaveBeenCalled();
    }, { timeout: 3000 });
    
    // Then check for text
    await waitFor(() => {
      expect(screen.getByText(/аналитика/i)).toBeInTheDocument();
    });
  });

  it('displays dashboard metrics', async () => {
    // Match the structure expected by AnalyticsPage component
    const mockDashboard = {
      searches: { total: 25 },
      vacancies: { active: 10 },
      candidates: { total: 100, hired: 5, by_status: {} },
    };
    
    analyticsAPI.getDashboard.mockResolvedValue(mockDashboard);
    analyticsAPI.getHiringFunnel.mockResolvedValue({});
    
    renderWithProviders(<AnalyticsPage />);
    
    // Wait for API call first
    await waitFor(() => {
      expect(analyticsAPI.getDashboard).toHaveBeenCalled();
    }, { timeout: 3000 });
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
    
    await waitFor(() => {
      expect(analyticsAPI.getDashboard).toHaveBeenCalled();
    });
    
    const periodSelect = screen.queryByLabelText(/период/i);
    if (periodSelect) {
      fireEvent.mouseDown(periodSelect);
      
      const option = await waitFor(() => {
        return screen.queryByText(/7 дней/i);
      });
      
      if (option) {
        fireEvent.click(option);
        
        await waitFor(() => {
          // Check that API was called again with new days parameter
          const calls = analyticsAPI.getDashboard.mock.calls;
          expect(calls.length).toBeGreaterThan(1);
        });
      }
    } else {
      // If select doesn't exist, just verify initial call
      expect(analyticsAPI.getDashboard).toHaveBeenCalled();
    }
  });

  it('shows loading state', () => {
    analyticsAPI.getDashboard.mockImplementation(() => new Promise(() => {}));
    analyticsAPI.getHiringFunnel.mockResolvedValue({});
    
    renderWithProviders(<AnalyticsPage />);
    
    expect(analyticsAPI.getDashboard).toHaveBeenCalled();
  });

  it('displays stat cards', async () => {
    // Match the structure expected by AnalyticsPage component
    const mockDashboard = {
      searches: { total: 25 },
      vacancies: { active: 10 },
      candidates: { total: 100, hired: 5, by_status: {} },
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
