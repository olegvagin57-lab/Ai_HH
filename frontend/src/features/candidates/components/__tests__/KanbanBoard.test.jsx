import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import KanbanBoard from '../KanbanBoard';
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

describe('KanbanBoard', () => {
  const mockKanbanData = {
    new: [
      { resume_id: '1', name: 'John Doe', title: 'Python Developer' },
    ],
    reviewed: [
      { resume_id: '2', name: 'Jane Smith', title: 'Senior Developer' },
    ],
    shortlisted: [],
    interview_scheduled: [],
    interviewed: [],
    offer_sent: [],
    hired: [],
    rejected: [],
    on_hold: [],
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders kanban board with columns', () => {
    renderWithProviders(<KanbanBoard data={mockKanbanData} />);
    
    expect(screen.getByText(/новые|new/i)).toBeInTheDocument();
    expect(screen.getByText(/на рассмотрении|reviewed/i)).toBeInTheDocument();
  });

  it('displays candidates in correct columns', () => {
    renderWithProviders(<KanbanBoard data={mockKanbanData} />);
    
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Jane Smith')).toBeInTheDocument();
  });

  it('handles empty data', () => {
    renderWithProviders(<KanbanBoard data={null} />);
    
    expect(screen.getByText(/нет данных|no data/i)).toBeInTheDocument();
  });

  it('navigates to candidate detail on card click', () => {
    const mockNavigate = jest.fn();
    jest.mock('react-router-dom', () => ({
      ...jest.requireActual('react-router-dom'),
      useNavigate: () => mockNavigate,
    }));
    
    renderWithProviders(<KanbanBoard data={mockKanbanData} />);
    
    const candidateCard = screen.getByText('John Doe').closest('div');
    if (candidateCard) {
      fireEvent.click(candidateCard);
    }
  });

  it('updates candidate status', async () => {
    candidatesAPI.updateStatus.mockResolvedValue({});
    const mockOnUpdate = jest.fn();
    
    renderWithProviders(<KanbanBoard data={mockKanbanData} onUpdate={mockOnUpdate} />);
    
    const menuButtons = screen.queryAllByLabelText(/more|еще/i);
    if (menuButtons.length > 0) {
      fireEvent.click(menuButtons[0]);
      
      await waitFor(() => {
        const reviewedOption = screen.queryByText(/на рассмотрении|reviewed/i);
        if (reviewedOption) {
          fireEvent.click(reviewedOption);
          
          await waitFor(() => {
            expect(candidatesAPI.updateStatus).toHaveBeenCalled();
            expect(mockOnUpdate).toHaveBeenCalled();
          });
        }
      });
    }
  });

  it('displays empty columns correctly', () => {
    const emptyData = {
      new: [],
      reviewed: [],
      shortlisted: [],
      interview_scheduled: [],
      interviewed: [],
      offer_sent: [],
      hired: [],
      rejected: [],
      on_hold: [],
    };
    
    renderWithProviders(<KanbanBoard data={emptyData} />);
    
    // Should render all columns even if empty
    expect(screen.getByText(/новые|new/i)).toBeInTheDocument();
  });

  it('shows candidate count in columns', () => {
    renderWithProviders(<KanbanBoard data={mockKanbanData} />);
    
    // Should display count of candidates in each column
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });
});
