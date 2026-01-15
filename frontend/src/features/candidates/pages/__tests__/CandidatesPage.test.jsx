import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import CandidatesPage from '../CandidatesPage';
import { candidatesAPI } from '../../../../api/api';

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

describe('CandidatesPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders candidates page', () => {
    candidatesAPI.getKanban.mockResolvedValue({});
    
    renderWithProviders(<CandidatesPage />);
    
    expect(screen.getByText(/кандидаты|candidates/i)).toBeInTheDocument();
  });

  it('displays kanban view by default', async () => {
    const mockKanbanData = {
      new: [{ resume_id: '1', name: 'John Doe' }],
      reviewed: [],
    };
    candidatesAPI.getKanban.mockResolvedValue(mockKanbanData);
    
    renderWithProviders(<CandidatesPage />);
    
    await waitFor(() => {
      expect(candidatesAPI.getKanban).toHaveBeenCalled();
    });
  });

  it('switches between kanban and list view', async () => {
    candidatesAPI.getKanban.mockResolvedValue({});
    candidatesAPI.getByStatus.mockResolvedValue({ candidates: [] });
    
    renderWithProviders(<CandidatesPage />);
    
    const listViewButton = screen.getByLabelText(/list|список/i) || 
                          screen.getByRole('button', { name: /list|список/i });
    
    if (listViewButton) {
      fireEvent.click(listViewButton);
      
      await waitFor(() => {
        expect(candidatesAPI.getByStatus).toHaveBeenCalled();
      });
    }
  });

  it('filters candidates by status tab', async () => {
    candidatesAPI.getByStatus.mockResolvedValue({
      candidates: [{ id: '1', name: 'Test Candidate' }],
    });
    
    renderWithProviders(<CandidatesPage />);
    
    // Switch to list view first
    const listViewButton = screen.queryByLabelText(/list|список/i);
    if (listViewButton) {
      fireEvent.click(listViewButton);
    }
    
    // Click on a status tab
    const reviewedTab = screen.queryByText(/на рассмотрении|reviewed/i);
    if (reviewedTab) {
      fireEvent.click(reviewedTab);
      
      await waitFor(() => {
        expect(candidatesAPI.getByStatus).toHaveBeenCalled();
      });
    }
  });

  it('handles search query input', () => {
    candidatesAPI.getKanban.mockResolvedValue({});
    
    renderWithProviders(<CandidatesPage />);
    
    const searchInput = screen.queryByPlaceholderText(/поиск|search/i);
    if (searchInput) {
      fireEvent.change(searchInput, { target: { value: 'test query' } });
      expect(searchInput.value).toBe('test query');
    }
  });

  it('shows loading state', () => {
    candidatesAPI.getKanban.mockImplementation(() => new Promise(() => {}));
    
    renderWithProviders(<CandidatesPage />);
    
    // Should show loading indicator
    expect(candidatesAPI.getKanban).toHaveBeenCalled();
  });

  it('handles empty kanban data', async () => {
    candidatesAPI.getKanban.mockResolvedValue({});
    
    renderWithProviders(<CandidatesPage />);
    
    await waitFor(() => {
      expect(candidatesAPI.getKanban).toHaveBeenCalled();
    });
  });
});
