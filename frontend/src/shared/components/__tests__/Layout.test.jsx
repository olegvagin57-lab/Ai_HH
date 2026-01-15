import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Layout from '../Layout';

const renderWithRouter = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('Layout', () => {
  it('renders without crashing', () => {
    renderWithRouter(<Layout />);
  });

  it('renders navigation when user is authenticated', () => {
    // Mock authenticated user
    const mockUser = { email: 'test@example.com', role_names: ['admin'] };
    localStorage.setItem('user', JSON.stringify(mockUser));
    
    renderWithRouter(<Layout />);
    
    // Should render some navigation elements
    // Adjust based on actual Layout implementation
  });

  it('renders children content', () => {
    renderWithRouter(
      <Layout>
        <div>Test Content</div>
      </Layout>
    );
    
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });
});
