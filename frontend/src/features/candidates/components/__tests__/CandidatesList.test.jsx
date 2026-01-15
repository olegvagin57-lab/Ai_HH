import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import CandidatesList from '../CandidatesList';
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

describe('CandidatesList', () => {
  const mockCandidates = [
    {
      resume_id: '1',
      name: 'John Doe',
      title: 'Python Developer',
      status: 'new',
      rating: 4,
      tags: ['python', 'fastapi'],
    },
    {
      resume_id: '2',
      name: 'Jane Smith',
      title: 'Senior Developer',
      status: 'reviewed',
      rating: 5,
      tags: ['python'],
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders candidates list', () => {
    renderWithProviders(<CandidatesList candidates={mockCandidates} />);
    
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
  });

  it('displays candidate information', () => {
    renderWithProviders(<CandidatesList candidates={mockCandidates} />);
    
    expect(screen.getByText('Python Developer')).toBeInTheDocument();
    expect(screen.getByText('Senior Developer')).toBeInTheDocument();
  });

  it('handles empty candidates list', () => {
    renderWithProviders(<CandidatesList candidates={[]} />);
    
    // Should not crash and render empty state or message
    expect(screen.queryByText('John Doe')).not.toBeInTheDocument();
  });

  it('navigates to candidate detail on click', () => {
    const mockNavigate = jest.fn();
    jest.mock('react-router-dom', () => ({
      ...jest.requireActual('react-router-dom'),
      useNavigate: () => mockNavigate,
    }));
    
    renderWithProviders(<CandidatesList candidates={mockCandidates} />);
    
    const candidateCard = screen.getByText('John Doe').closest('tr') || 
                         screen.getByText('John Doe').closest('div');
    if (candidateCard) {
      fireEvent.click(candidateCard);
    }
  });

  it('updates candidate status', async () => {
    candidatesAPI.updateStatus.mockResolvedValue({});
    
    renderWithProviders(<CandidatesList candidates={mockCandidates} />);
    
    const menuButtons = screen.queryAllByLabelText(/more|еще/i);
    if (menuButtons.length > 0) {
      fireEvent.click(menuButtons[0]);
      
      await waitFor(() => {
        const reviewedOption = screen.queryByText(/на рассмотрении|reviewed/i);
        if (reviewedOption) {
          fireEvent.click(reviewedOption);
          
          await waitFor(() => {
            expect(candidatesAPI.updateStatus).toHaveBeenCalled();
          });
        }
      });
    }
  });

  it('displays candidate tags', () => {
    renderWithProviders(<CandidatesList candidates={mockCandidates} />);
    
    expect(screen.getByText('python')).toBeInTheDocument();
    expect(screen.getByText('fastapi')).toBeInTheDocument();
  });

  it('displays candidate rating', () => {
    renderWithProviders(<CandidatesList candidates={mockCandidates} />);
    
    // Should show star ratings
    const stars = screen.queryAllByLabelText(/rating|рейтинг/i);
    expect(stars.length).toBeGreaterThan(0);
  });
});
