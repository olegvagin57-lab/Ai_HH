import React from 'react';
import { render, screen } from '@testing-library/react';
import EmptyState from '../EmptyState';

describe('EmptyState', () => {
  it('renders without crashing', () => {
    render(<EmptyState title="No data found" />);
    expect(screen.getByText(/no data found/i)).toBeInTheDocument();
  });

  it('displays custom title and description', () => {
    render(<EmptyState title="Custom title" description="Custom description" />);
    expect(screen.getByText(/custom title/i)).toBeInTheDocument();
    expect(screen.getByText(/custom description/i)).toBeInTheDocument();
  });

  it('displays action button when provided', () => {
    render(
      <EmptyState
        title="No data"
        actionLabel="Add Item"
        onAction={() => {}}
      />
    );
    expect(screen.getByText(/add item/i)).toBeInTheDocument();
  });
});
