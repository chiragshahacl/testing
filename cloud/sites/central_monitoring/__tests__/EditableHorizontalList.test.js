import { ThemeProvider } from '@mui/material';
import { fireEvent, render, screen } from '@testing-library/react';

import theme from '@/theme/theme';

import EditableHorizontalList from '@/components/lists/EditableHorizontalList';
import SessionContext from '@/context/SessionContext';

const listItems = [
  {
    id: 'I-001',
    name: 'Item 1',
    beds: [],
  },
  {
    id: 'I-002',
    name: 'Item 2',
    beds: [],
  },
  {
    id: 'I-003',
    name: 'Item 3',
    beds: [],
  },
];

describe('EditableHorizontalList', () => {
  it('renders all components', async () => {
    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <EditableHorizontalList
            items={listItems}
            activeItem='I-001'
            onItemPress={jest.fn()}
            editingActiveItem={false}
            onItemNameChange={jest.fn()}
            onFinishEditingItem={jest.fn()}
            hasError={{}}
          />
        </SessionContext>
      </ThemeProvider>
    );

    expect(screen.getByRole('textbox', { name: 'Item 1' })).toBeInTheDocument();
    expect(screen.getByRole('textbox', { name: 'Item 1' })).toHaveClass('active');
    expect(screen.getByRole('textbox', { name: 'Item 1' })).not.toHaveClass('inactive');

    expect(screen.getByRole('textbox', { name: 'Item 2' })).toBeInTheDocument();
    expect(screen.getByRole('textbox', { name: 'Item 2' })).toHaveClass('inactive');

    expect(screen.getByRole('textbox', { name: 'Item 3' })).toBeInTheDocument();
    expect(screen.getByRole('textbox', { name: 'Item 3' })).toHaveClass('inactive');

    expect(screen.queryByTestId('left-arrow')).not.toBeInTheDocument();
    expect(screen.queryByTestId('right-arrow')).not.toBeInTheDocument();
  });

  it('handles activate item', async () => {
    const onItemPressMock = jest.fn();

    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <EditableHorizontalList
            items={listItems}
            activeItem='I-001'
            onItemPress={onItemPressMock}
            editingActiveItem={false}
            onItemNameChange={jest.fn()}
            onFinishEditingItem={jest.fn()}
            hasError={{}}
          />
        </SessionContext>
      </ThemeProvider>
    );

    fireEvent.click(screen.getByRole('textbox', { name: 'Item 2' }));
    expect(onItemPressMock).toHaveBeenCalledWith('I-002');
  });

  it('shows scroll buttons if content overflows', async () => {
    Object.defineProperty(HTMLElement.prototype, 'scrollWidth', { configurable: true, value: 500 });
    Object.defineProperty(HTMLElement.prototype, 'clientWidth', { configurable: true, value: 10 });

    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <EditableHorizontalList
            items={listItems}
            activeItem={undefined}
            onItemPress={jest.fn()}
            editingActiveItem={false}
            onItemNameChange={jest.fn()}
            onFinishEditingItem={jest.fn()}
            hasError={{}}
          />
        </SessionContext>
      </ThemeProvider>
    );

    expect(screen.getByTestId('left-arrow')).toBeInTheDocument();
    expect(screen.getByTestId('right-arrow')).toBeInTheDocument();
  });

  it('handles scroll right', async () => {
    const scrollToMock = jest.fn();
    Object.defineProperty(HTMLElement.prototype, 'scrollWidth', { configurable: true, value: 500 });
    Object.defineProperty(HTMLElement.prototype, 'clientWidth', { configurable: true, value: 10 });
    Object.defineProperty(HTMLElement.prototype, 'scrollTo', {
      configurable: true,
      value: scrollToMock,
    });

    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <EditableHorizontalList
            items={listItems}
            activeItem={undefined}
            onItemPress={jest.fn()}
            editingActiveItem={false}
            onItemNameChange={jest.fn()}
            onFinishEditingItem={jest.fn()}
            hasError={{}}
          />
        </SessionContext>
      </ThemeProvider>
    );

    fireEvent.click(screen.getByTestId('right-arrow'));
    expect(scrollToMock).toHaveBeenCalledWith({ behavior: 'smooth', left: 100 });
  });

  it('handles scroll left', async () => {
    const scrollToMock = jest.fn();
    Object.defineProperty(HTMLElement.prototype, 'scrollWidth', { configurable: true, value: 500 });
    Object.defineProperty(HTMLElement.prototype, 'clientWidth', { configurable: true, value: 10 });
    Object.defineProperty(HTMLElement.prototype, 'scrollLeft', { configurable: true, value: 400 });
    Object.defineProperty(HTMLElement.prototype, 'scrollTo', {
      configurable: true,
      value: scrollToMock,
    });

    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <EditableHorizontalList
            items={listItems}
            activeItem={undefined}
            onItemPress={jest.fn()}
            editingActiveItem={false}
            onItemNameChange={jest.fn()}
            onFinishEditingItem={jest.fn()}
            hasError={{}}
          />
        </SessionContext>
      </ThemeProvider>
    );

    fireEvent.click(screen.getByTestId('left-arrow'));
    expect(scrollToMock).toHaveBeenCalledWith({ behavior: 'smooth', left: 300 });
  });

  it('stops when right end reached', async () => {
    const scrollToMock = jest.fn();
    Object.defineProperty(HTMLElement.prototype, 'scrollWidth', { configurable: true, value: 500 });
    Object.defineProperty(HTMLElement.prototype, 'clientWidth', { configurable: true, value: 10 });
    Object.defineProperty(HTMLElement.prototype, 'offsetWidth', { configurable: true, value: 100 });
    Object.defineProperty(HTMLElement.prototype, 'scrollLeft', { configurable: true, value: 400 });
    Object.defineProperty(HTMLElement.prototype, 'scrollTo', {
      configurable: true,
      value: scrollToMock,
    });

    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <EditableHorizontalList
            items={listItems}
            activeItem={undefined}
            onItemPress={jest.fn()}
            editingActiveItem={false}
            onItemNameChange={jest.fn()}
            onFinishEditingItem={jest.fn()}
            hasError={{}}
          />
        </SessionContext>
      </ThemeProvider>
    );

    fireEvent.click(screen.getByTestId('right-arrow'));
    expect(scrollToMock).not.toHaveBeenCalled();
  });

  it('stops when left end reached', async () => {
    const scrollToMock = jest.fn();
    Object.defineProperty(HTMLElement.prototype, 'scrollWidth', { configurable: true, value: 500 });
    Object.defineProperty(HTMLElement.prototype, 'clientWidth', { configurable: true, value: 10 });
    Object.defineProperty(HTMLElement.prototype, 'offsetWidth', { configurable: true, value: 100 });
    Object.defineProperty(HTMLElement.prototype, 'scrollLeft', { configurable: true, value: 0 });
    Object.defineProperty(HTMLElement.prototype, 'scrollTo', {
      configurable: true,
      value: scrollToMock,
    });

    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <EditableHorizontalList
            items={listItems}
            activeItem={undefined}
            onItemPress={jest.fn()}
            editingActiveItem={false}
            onItemNameChange={jest.fn()}
            onFinishEditingItem={jest.fn()}
            hasError={{}}
          />
        </SessionContext>
      </ThemeProvider>
    );

    fireEvent.click(screen.getByTestId('left-arrow'));
    expect(scrollToMock).not.toHaveBeenCalled();
  });
});
