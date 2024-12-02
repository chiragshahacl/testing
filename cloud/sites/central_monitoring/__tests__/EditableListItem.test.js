import { ThemeProvider } from '@mui/material';
import { fireEvent, render, screen } from '@testing-library/react';

import theme from '@/theme/theme';

import EditableListItem from '@/components/lists/EditableListItem';
import SessionContext from '@/context/SessionContext';

describe('EditableListItem', () => {
  it('renders all components', async () => {
    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <EditableListItem
            item={{ id: 'I-001', name: 'Item 1' }}
            isActive={true}
            isEditing={true}
            onNameChange={jest.fn()}
            onFinishEditing={jest.fn()}
            hasError={false}
          />
        </SessionContext>
      </ThemeProvider>
    );

    expect(screen.getByRole('textbox', { name: 'Item 1' })).toBeInTheDocument();
    expect(screen.getByRole('textbox', { name: 'Item 1' })).toHaveFocus();
    expect(screen.getByRole('textbox', { name: 'Item 1' })).not.toBeDisabled();
    expect(screen.getByRole('textbox', { name: 'Item 1' })).toHaveClass('active');
  });

  it('distinguishes active item', async () => {
    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <EditableListItem
            item={{ id: 'I-002', name: 'Item 2' }}
            isActive={false}
            isEditing={false}
            onNameChange={jest.fn()}
            onFinishEditing={jest.fn()}
            hasError={false}
          />
        </SessionContext>
      </ThemeProvider>
    );

    expect(screen.getByRole('textbox', { name: 'Item 2' })).toHaveClass('inactive');
  });

  it('distinguishes editing item', async () => {
    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <EditableListItem
            item={{ id: 'I-002', name: 'Item 2' }}
            isActive={false}
            isEditing={false}
            onNameChange={jest.fn()}
            onFinishEditing={jest.fn()}
            hasError={false}
          />
        </SessionContext>
      </ThemeProvider>
    );

    expect(screen.getByRole('textbox', { name: 'Item 2' })).not.toHaveFocus();
    expect(screen.getByRole('textbox', { name: 'Item 2' })).toBeDisabled();
  });

  it('handles change -> valid', async () => {
    const onNameChangeMock = jest.fn();

    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <EditableListItem
            item={{ id: 'I-001', name: 'Item 1' }}
            isActive={true}
            isEditing={true}
            onNameChange={onNameChangeMock}
            onFinishEditing={jest.fn()}
            hasError={false}
          />
        </SessionContext>
      </ThemeProvider>
    );

    fireEvent.change(screen.getByRole('textbox', { name: 'Item 1' }), {
      target: { value: 'Item 4' },
    });
    expect(onNameChangeMock).toHaveBeenCalledWith('I-001', 'Item 4');
  });

  it('handles blur -> valid', async () => {
    const onNameChangeMock = jest.fn();
    const onFinishEditing = jest.fn();

    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <EditableListItem
            item={{ id: 'I-001', name: 'Item 1' }}
            isActive={true}
            isEditing={true}
            onNameChange={onNameChangeMock}
            onFinishEditing={onFinishEditing}
            hasError={false}
          />
        </SessionContext>
      </ThemeProvider>
    );

    fireEvent.change(screen.getByRole('textbox', { name: 'Item 1' }), {
      target: { value: 'Item 4' },
    });
    fireEvent.blur(screen.getByRole('textbox', { name: 'Item 1' }));
    expect(onNameChangeMock).toHaveBeenCalledWith('I-001', 'Item 4');
    expect(onFinishEditing).toHaveBeenCalledWith('I-001', 'Item 4');
  });
});
