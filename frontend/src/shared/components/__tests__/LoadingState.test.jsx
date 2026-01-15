import React from 'react';
import { render, screen } from '@testing-library/react';
import LoadingState from '../LoadingState';

describe('LoadingState', () => {
  it('renders without crashing', () => {
    render(<LoadingState />);
    // Check for loading indicator
    expect(screen.getByRole('progressbar') || screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('displays custom message', () => {
    render(<LoadingState message="Loading data..." />);
    expect(screen.getByText(/loading data/i)).toBeInTheDocument();
  });
});
