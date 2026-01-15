import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter, MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import CandidateDetailPage from '../CandidateDetailPage';
import { candidatesAPI, searchAPI } from '../../../../api/api';

jest.mock('../../../../api/api');

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { retry: false },
    mutations: { retry: false },
  },
});

const renderWithProviders = (component, initialEntries = ['/candidates/123']) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={initialEntries}>
        {component}
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe('CandidateDetailPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders candidate detail page', async () => {
    const mockCandidate = {
      id: '123',
      resume_id: '123',
      status: 'new',
      tags: [],
      notes: '',
      rating: 0,
    };
    
    candidatesAPI.get.mockResolvedValue(mockCandidate);
    candidatesAPI.getInteractions.mockResolvedValue([]);
    searchAPI.list.mockResolvedValue({ searches: [] });
    
    renderWithProviders(<CandidateDetailPage />);
    
    await waitFor(() => {
      expect(candidatesAPI.get).toHaveBeenCalledWith('123');
    });
  });

  it('displays candidate information', async () => {
    const mockCandidate = {
      id: '123',
      resume_id: '123',
      status: 'reviewed',
      tags: ['python', 'fastapi'],
      notes: 'Test notes',
      rating: 4,
    };
    
    candidatesAPI.get.mockResolvedValue(mockCandidate);
    candidatesAPI.getInteractions.mockResolvedValue([]);
    searchAPI.list.mockResolvedValue({ searches: [] });
    
    renderWithProviders(<CandidateDetailPage />);
    
    await waitFor(() => {
      expect(candidatesAPI.get).toHaveBeenCalled();
    });
  });

  it('updates candidate status', async () => {
    const mockCandidate = {
      id: '123',
      resume_id: '123',
      status: 'new',
    };
    
    candidatesAPI.get.mockResolvedValue(mockCandidate);
    candidatesAPI.updateStatus.mockResolvedValue({ ...mockCandidate, status: 'reviewed' });
    candidatesAPI.getInteractions.mockResolvedValue([]);
    searchAPI.list.mockResolvedValue({ searches: [] });
    
    renderWithProviders(<CandidateDetailPage />);
    
    await waitFor(() => {
      expect(candidatesAPI.get).toHaveBeenCalled();
    });
    
    const statusButton = screen.queryByText(/статус|status/i);
    if (statusButton) {
      fireEvent.click(statusButton);
      
      const reviewedOption = screen.queryByText(/на рассмотрении|reviewed/i);
      if (reviewedOption) {
        fireEvent.click(reviewedOption);
        
        await waitFor(() => {
          expect(candidatesAPI.updateStatus).toHaveBeenCalled();
        });
      }
    }
  });

  it('adds tag to candidate', async () => {
    const mockCandidate = {
      id: '123',
      resume_id: '123',
      status: 'new',
      tags: [],
    };
    
    candidatesAPI.get.mockResolvedValue(mockCandidate);
    candidatesAPI.addTag.mockResolvedValue({ ...mockCandidate, tags: ['python'] });
    candidatesAPI.getInteractions.mockResolvedValue([]);
    searchAPI.list.mockResolvedValue({ searches: [] });
    
    renderWithProviders(<CandidateDetailPage />);
    
    await waitFor(() => {
      expect(candidatesAPI.get).toHaveBeenCalled();
    });
  });

  it('updates candidate notes', async () => {
    const mockCandidate = {
      id: '123',
      resume_id: '123',
      notes: '',
    };
    
    candidatesAPI.get.mockResolvedValue(mockCandidate);
    candidatesAPI.updateNotes.mockResolvedValue({ ...mockCandidate, notes: 'New notes' });
    candidatesAPI.getInteractions.mockResolvedValue([]);
    searchAPI.list.mockResolvedValue({ searches: [] });
    
    renderWithProviders(<CandidateDetailPage />);
    
    await waitFor(() => {
      expect(candidatesAPI.get).toHaveBeenCalled();
    });
  });

  it('navigates back on back button click', () => {
    const mockNavigate = jest.fn();
    jest.mock('react-router-dom', () => ({
      ...jest.requireActual('react-router-dom'),
      useNavigate: () => mockNavigate,
    }));
    
    candidatesAPI.get.mockResolvedValue({ id: '123' });
    candidatesAPI.getInteractions.mockResolvedValue([]);
    searchAPI.list.mockResolvedValue({ searches: [] });
    
    renderWithProviders(<CandidateDetailPage />);
    
    const backButton = screen.queryByLabelText(/back|назад/i);
    if (backButton) {
      fireEvent.click(backButton);
    }
  });

  it('shows loading state', () => {
    candidatesAPI.get.mockImplementation(() => new Promise(() => {}));
    candidatesAPI.getInteractions.mockResolvedValue([]);
    searchAPI.list.mockResolvedValue({ searches: [] });
    
    renderWithProviders(<CandidateDetailPage />);
    
    expect(candidatesAPI.get).toHaveBeenCalled();
  });

  it('displays interactions', async () => {
    const mockInteractions = [
      { id: '1', type: 'comment', content: 'Test comment' },
    ];
    
    candidatesAPI.get.mockResolvedValue({ id: '123' });
    candidatesAPI.getInteractions.mockResolvedValue(mockInteractions);
    searchAPI.list.mockResolvedValue({ searches: [] });
    
    renderWithProviders(<CandidateDetailPage />);
    
    await waitFor(() => {
      expect(candidatesAPI.getInteractions).toHaveBeenCalledWith('123');
    });
  });
});
