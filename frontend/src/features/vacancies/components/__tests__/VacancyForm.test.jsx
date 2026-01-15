import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import VacancyForm from '../VacancyForm';
import { vacanciesAPI } from '../../../../api/api';

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
      {component}
    </QueryClientProvider>
  );
};

describe('VacancyForm', () => {
  const mockOnSuccess = jest.fn();
  const mockOnCancel = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders vacancy form for new vacancy', () => {
    renderWithProviders(
      <VacancyForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />
    );
    
    expect(screen.getByLabelText(/название|title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/описание|description/i)).toBeInTheDocument();
  });

  it('renders vacancy form with existing vacancy data', () => {
    const mockVacancy = {
      id: '123',
      title: 'Python Developer',
      description: 'Test description',
      city: 'Москва',
    };
    
    renderWithProviders(
      <VacancyForm vacancy={mockVacancy} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />
    );
    
    expect(screen.getByDisplayValue('Python Developer')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Test description')).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    vacanciesAPI.create.mockResolvedValue({ id: '1' });
    
    renderWithProviders(
      <VacancyForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />
    );
    
    const submitButton = screen.getByRole('button', { name: /создать|create|сохранить|save/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/обязательно|required/i)).toBeInTheDocument();
    });
  });

  it('creates new vacancy', async () => {
    const mockVacancy = { id: '1', title: 'New Vacancy' };
    vacanciesAPI.create.mockResolvedValue(mockVacancy);
    
    renderWithProviders(
      <VacancyForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />
    );
    
    fireEvent.change(screen.getByLabelText(/название|title/i), {
      target: { value: 'New Vacancy' },
    });
    fireEvent.change(screen.getByLabelText(/описание|description/i), {
      target: { value: 'Test description' },
    });
    fireEvent.change(screen.getByLabelText(/город|city/i), {
      target: { value: 'Москва' },
    });
    
    const submitButton = screen.getByRole('button', { name: /создать|create/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(vacanciesAPI.create).toHaveBeenCalled();
      expect(mockOnSuccess).toHaveBeenCalled();
    });
  });

  it('updates existing vacancy', async () => {
    const mockVacancy = {
      id: '123',
      title: 'Python Developer',
      description: 'Old description',
    };
    
    vacanciesAPI.update.mockResolvedValue({ ...mockVacancy, description: 'New description' });
    
    renderWithProviders(
      <VacancyForm vacancy={mockVacancy} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />
    );
    
    fireEvent.change(screen.getByLabelText(/описание|description/i), {
      target: { value: 'New description' },
    });
    
    const submitButton = screen.getByRole('button', { name: /сохранить|save/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(vacanciesAPI.update).toHaveBeenCalledWith('123', expect.objectContaining({
        description: 'New description',
      }));
      expect(mockOnSuccess).toHaveBeenCalled();
    });
  });

  it('handles form cancellation', () => {
    renderWithProviders(
      <VacancyForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />
    );
    
    const cancelButton = screen.getByRole('button', { name: /отмена|cancel/i });
    fireEvent.click(cancelButton);
    
    expect(mockOnCancel).toHaveBeenCalled();
  });

  it('toggles remote work option', () => {
    renderWithProviders(
      <VacancyForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />
    );
    
    const remoteSwitch = screen.getByLabelText(/удаленная|remote/i);
    fireEvent.click(remoteSwitch);
    
    expect(remoteSwitch).toBeChecked();
  });

  it('handles salary fields', () => {
    renderWithProviders(
      <VacancyForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />
    );
    
    const minSalaryInput = screen.queryByLabelText(/мин.*зарплата|min.*salary/i);
    const maxSalaryInput = screen.queryByLabelText(/макс.*зарплата|max.*salary/i);
    
    if (minSalaryInput) {
      fireEvent.change(minSalaryInput, { target: { value: '100000' } });
      expect(minSalaryInput.value).toBe('100000');
    }
    
    if (maxSalaryInput) {
      fireEvent.change(maxSalaryInput, { target: { value: '200000' } });
      expect(maxSalaryInput.value).toBe('200000');
    }
  });

  it('handles form submission error', async () => {
    const errorMessage = 'Validation error';
    vacanciesAPI.create.mockRejectedValue({
      response: { data: { detail: errorMessage } },
    });
    
    renderWithProviders(
      <VacancyForm onSuccess={mockOnSuccess} onCancel={mockOnCancel} />
    );
    
    fireEvent.change(screen.getByLabelText(/название|title/i), {
      target: { value: 'Test' },
    });
    fireEvent.change(screen.getByLabelText(/описание|description/i), {
      target: { value: 'Test description' },
    });
    fireEvent.change(screen.getByLabelText(/город|city/i), {
      target: { value: 'Москва' },
    });
    
    const submitButton = screen.getByRole('button', { name: /создать|create/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });
});
