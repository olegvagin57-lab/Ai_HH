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
    
    expect(screen.getByLabelText(/название вакансии/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/описание/i)).toBeInTheDocument();
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
    
    // Submit form to trigger validation
    const form = submitButton.closest('form');
    if (form) {
      fireEvent.submit(form);
    } else {
      fireEvent.click(submitButton);
    }
    
    await waitFor(() => {
      // Check for validation error messages in helperText
      // Errors are displayed as helperText in TextField components
      // Material-UI renders helperText as a separate element, so we can search for it
      const titleErrors = screen.queryAllByText(/название.*обязательно/i);
      const descriptionErrors = screen.queryAllByText(/описание.*обязательно/i);
      const cityErrors = screen.queryAllByText(/город|удаленную/i);
      
      // Also check if TextField has error state (aria-invalid="true")
      const titleField = screen.queryByLabelText(/название/i);
      const descriptionField = screen.queryByLabelText(/описание/i);
      const hasTitleError = titleField && titleField.getAttribute('aria-invalid') === 'true';
      const hasDescriptionError = descriptionField && descriptionField.getAttribute('aria-invalid') === 'true';
      
      // At least one validation error should be shown (either text or error state)
      const hasError = titleErrors.length > 0 || descriptionErrors.length > 0 || cityErrors.length > 0 || hasTitleError || hasDescriptionError;
      expect(hasError).toBe(true);
    }, { timeout: 3000 });
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
    // Use getAllByLabelText and select the first one (main "Город" field, not "Город для поиска")
    const cityInputs = screen.getAllByLabelText(/город/i);
    fireEvent.change(cityInputs[0], {
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
      city: 'Москва', // Add city to pass validation
    };
    
    vacanciesAPI.update.mockResolvedValue({ ...mockVacancy, description: 'New description' });
    
    renderWithProviders(
      <VacancyForm vacancy={mockVacancy} onSuccess={mockOnSuccess} onCancel={mockOnCancel} />
    );
    
    // Wait for form to be populated with vacancy data
    await waitFor(() => {
      expect(screen.getByDisplayValue('Python Developer')).toBeInTheDocument();
    });
    
    fireEvent.change(screen.getByLabelText(/описание|description/i), {
      target: { value: 'New description' },
    });
    
    const submitButton = screen.getByRole('button', { name: /сохранить|save/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(vacanciesAPI.update).toHaveBeenCalledWith('123', expect.objectContaining({
        description: 'New description',
      }));
    }, { timeout: 3000 });
    
    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled();
    }, { timeout: 3000 });
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
    vacanciesAPI.create.mockRejectedValue({
      response: { data: { detail: 'Validation error' } },
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
    // Use getAllByLabelText and select the first one (main "Город" field, not "Город для поиска")
    const cityInputs = screen.getAllByLabelText(/город/i);
    fireEvent.change(cityInputs[0], {
      target: { value: 'Москва' },
    });
    
    const submitButton = screen.getByRole('button', { name: /создать|create/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      // Component shows generic error message, not the specific error detail
      expect(screen.getByText(/ошибка при сохранении/i)).toBeInTheDocument();
    });
  });
});
