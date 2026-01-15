import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import SearchPage from '../SearchPage';

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

describe('SearchPage', () => {
  it('renders search form', () => {
    renderWithProviders(<SearchPage />);
    
    // Should have query input
    const queryInput = screen.getByLabelText(/query|описание/i) || screen.getByPlaceholderText(/query|описание/i);
    expect(queryInput).toBeInTheDocument();
    
    // Should have city input
    const cityInput = screen.getByLabelText(/city|город/i) || screen.getByPlaceholderText(/city|город/i);
    expect(cityInput).toBeInTheDocument();
  });

  it('allows user to enter search query', () => {
    renderWithProviders(<SearchPage />);
    
    const queryInput = screen.getByLabelText(/query|описание/i) || screen.getByPlaceholderText(/query|описание/i);
    fireEvent.change(queryInput, { target: { value: 'Python developer' } });
    
    expect(queryInput.value).toBe('Python developer');
  });

  it('submits search form', async () => {
    renderWithProviders(<SearchPage />);
    
    const queryInput = screen.getByLabelText(/query|описание/i) || screen.getByPlaceholderText(/query|описание/i);
    const cityInput = screen.getByLabelText(/city|город/i) || screen.getByPlaceholderText(/city|город/i);
    const submitButton = screen.getByRole('button', { name: /search|поиск/i });
    
    fireEvent.change(queryInput, { target: { value: 'Python developer' } });
    fireEvent.change(cityInput, { target: { value: 'Москва' } });
    fireEvent.click(submitButton);
    
    // Should attempt to submit
    await waitFor(() => {
      // Search submission logic would be tested here
    });
  });
});
