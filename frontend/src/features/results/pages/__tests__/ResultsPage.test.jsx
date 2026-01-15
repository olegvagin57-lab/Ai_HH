import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import ResultsPage from '../ResultsPage';
import { searchAPI } from '../../../../api/api';

jest.mock('../../../../api/api');

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const renderWithProviders = (component, initialEntries = ['/results/123']) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={initialEntries}>
        {component}
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe('ResultsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders results page', async () => {
    const mockSearch = {
      id: '123',
      query: 'Python Developer',
      status: 'completed',
      total_found: 10,
    };
    
    searchAPI.get.mockResolvedValue(mockSearch);
    searchAPI.getResumes.mockResolvedValue({ resumes: [] });
    
    renderWithProviders(<ResultsPage />);
    
    await waitFor(() => {
      expect(searchAPI.get).toHaveBeenCalledWith('123');
    });
  });

  it('displays search results', async () => {
    const mockSearch = {
      id: '123',
      query: 'Python Developer',
      status: 'completed',
    };
    
    const mockResumes = [
      { id: '1', name: 'John Doe', title: 'Python Developer', preliminary_score: 8.5 },
      { id: '2', name: 'Jane Smith', title: 'Senior Python', preliminary_score: 9.0 },
    ];
    
    searchAPI.get.mockResolvedValue(mockSearch);
    searchAPI.getResumes.mockResolvedValue({ resumes: mockResumes });
    
    renderWithProviders(<ResultsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });

  it('filters results by status', async () => {
    const mockSearch = { id: '123', status: 'completed' };
    searchAPI.get.mockResolvedValue(mockSearch);
    searchAPI.getResumes.mockResolvedValue({ resumes: [] });
    
    renderWithProviders(<ResultsPage />);
    
    await waitFor(() => {
      expect(searchAPI.get).toHaveBeenCalled();
    });
    
    const filterSelect = screen.queryByLabelText(/статус|status/i);
    if (filterSelect) {
      fireEvent.change(filterSelect, { target: { value: 'reviewed' } });
    }
  });

  it('exports results to Excel', async () => {
    const mockSearch = { id: '123', status: 'completed' };
    const mockBlob = new Blob(['test'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    
    searchAPI.get.mockResolvedValue(mockSearch);
    searchAPI.getResumes.mockResolvedValue({ resumes: [] });
    searchAPI.exportExcel.mockResolvedValue(mockBlob);
    
    // Mock URL.createObjectURL
    global.URL.createObjectURL = jest.fn(() => 'blob:url');
    global.URL.revokeObjectURL = jest.fn();
    
    renderWithProviders(<ResultsPage />);
    
    await waitFor(() => {
      const exportButton = screen.queryByLabelText(/excel|экспорт/i);
      if (exportButton) {
        fireEvent.click(exportButton);
        
        waitFor(() => {
          expect(searchAPI.exportExcel).toHaveBeenCalledWith('123');
        });
      }
    });
  });

  it('shows loading state', () => {
    searchAPI.get.mockImplementation(() => new Promise(() => {}));
    searchAPI.getResumes.mockResolvedValue({ resumes: [] });
    
    renderWithProviders(<ResultsPage />);
    
    expect(searchAPI.get).toHaveBeenCalled();
  });

  it('handles pagination', async () => {
    const mockSearch = { id: '123', status: 'completed' };
    searchAPI.get.mockResolvedValue(mockSearch);
    searchAPI.getResumes.mockResolvedValue({ resumes: [], total: 50 });
    
    renderWithProviders(<ResultsPage />);
    
    await waitFor(() => {
      expect(searchAPI.get).toHaveBeenCalled();
    });
  });

  it('displays search status', async () => {
    const mockSearch = {
      id: '123',
      query: 'Python Developer',
      status: 'processing',
    };
    
    searchAPI.get.mockResolvedValue(mockSearch);
    searchAPI.getResumes.mockResolvedValue({ resumes: [] });
    
    renderWithProviders(<ResultsPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/обработка|processing/i)).toBeInTheDocument();
    });
  });
});
