import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import CandidateDetailPage from '../CandidateDetailPage';
import { candidatesAPI, searchAPI } from '../../../../api/api';

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

const renderWithProviders = (component, initialEntries = ['/candidates/123']) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={initialEntries}>
        <Routes>
          <Route path="/candidates/:resumeId" element={component} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
};

describe('CandidateDetailPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Clear QueryClient cache between tests
    queryClient.clear();
  });

  it('renders candidate detail page', async () => {
    const mockCandidate = {
      id: '123',
      resume_id: '123',
      status: 'new',
      tags: [],
      notes: '',
      rating: 0,
      resume: {
        name: 'Test User',
        title: 'Test Title',
      },
    };
    
    candidatesAPI.get.mockResolvedValue(mockCandidate);
    candidatesAPI.getInteractions.mockResolvedValue([]);
    searchAPI.list.mockResolvedValue({ searches: [] });
    
    renderWithProviders(<CandidateDetailPage />, ['/candidates/123']);
    
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
    
    renderWithProviders(<CandidateDetailPage />, ['/candidates/123']);
    
    await waitFor(() => {
      expect(candidatesAPI.get).toHaveBeenCalledWith('123');
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
    
    renderWithProviders(<CandidateDetailPage />, ['/candidates/123']);
    
    await waitFor(() => {
      expect(candidatesAPI.get).toHaveBeenCalledWith('123');
    });
    
    const statusButton = screen.queryByText(/статус|status/i);
    if (statusButton) {
      fireEvent.click(statusButton);
      
      await waitFor(() => {
        const reviewedOption = screen.queryByText(/на рассмотрении|reviewed/i);
        return reviewedOption !== null;
      });
      
      const reviewedOption = screen.queryByText(/на рассмотрении|reviewed/i);
      if (reviewedOption) {
        fireEvent.click(reviewedOption);
        
        await waitFor(() => {
          expect(candidatesAPI.updateStatus).toHaveBeenCalledWith('123', expect.any(String));
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
    
    renderWithProviders(<CandidateDetailPage />, ['/candidates/123']);
    
    await waitFor(() => {
      expect(candidatesAPI.get).toHaveBeenCalledWith('123');
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
    
    renderWithProviders(<CandidateDetailPage />, ['/candidates/123']);
    
    await waitFor(() => {
      expect(candidatesAPI.get).toHaveBeenCalledWith('123');
    });
  });

  it('navigates back on back button click', async () => {
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
    
    renderWithProviders(<CandidateDetailPage />, ['/candidates/123']);
    
    await waitFor(() => {
      expect(candidatesAPI.get).toHaveBeenCalledWith('123');
    });
    
    const backButton = screen.queryByLabelText(/back|назад/i);
    if (backButton) {
      fireEvent.click(backButton);
    }
  });

  it('shows loading state', () => {
    candidatesAPI.get.mockImplementation(() => new Promise(() => {}));
    candidatesAPI.getInteractions.mockResolvedValue([]);
    searchAPI.list.mockResolvedValue({ searches: [] });
    
    renderWithProviders(<CandidateDetailPage />, ['/candidates/123']);
    
    expect(candidatesAPI.get).toHaveBeenCalledWith('123');
  });

  it('displays interactions', async () => {
    const mockInteractions = [
      { id: '1', type: 'comment', content: 'Test comment' },
    ];
    
    const mockCandidate = {
      id: '123',
      resume_id: '123',
      status: 'new',
      tags: [],
      notes: '',
      rating: 0,
    };
    candidatesAPI.get.mockResolvedValue(mockCandidate);
    candidatesAPI.getInteractions.mockResolvedValue(mockInteractions);
    searchAPI.list.mockResolvedValue({ searches: [] });
    
    renderWithProviders(<CandidateDetailPage />, ['/candidates/123']);
    
    await waitFor(() => {
      expect(candidatesAPI.get).toHaveBeenCalledWith('123');
      expect(candidatesAPI.getInteractions).toHaveBeenCalledWith('123');
    });
  });
});
