import ChecklistItem from '@/components/ChecklistItem';
import { render, screen } from '@testing-library/react';

describe('ChecklistItem', () => {
  it('checked item', async () => {
    render(<ChecklistItem active={true}>Item 1</ChecklistItem>);

    expect(screen.getByTestId('complete-icon')).toBeInTheDocument();
    expect(screen.getByText('Item 1')).toBeInTheDocument();
  });

  it('unchecked item', async () => {
    render(<ChecklistItem active={false}>Item 1</ChecklistItem>);

    expect(screen.getByTestId('incomplete-icon')).toBeInTheDocument();
    expect(screen.getByText('Item 1')).toBeInTheDocument();
  });
});
