import { ThemeProvider } from '@mui/material';
import { fireEvent, render, screen } from '@testing-library/react';

import theme from '@/theme/theme';

import HorizontalList from '@/components/lists/HorizontalList';
import SessionContext from '@/context/SessionContext';

const listItems = [
  {
    id: 'item_1',
    name: 'Item 1',
  },
  {
    id: 'item_2',
    name: 'Item 2',
  },
  {
    id: 'item_3',
    name: 'Item 3',
  },
];

describe('HorizontalList', () => {
  it('renders all components', async () => {
    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <HorizontalList items={listItems} activeItem='item_1' setActiveItem={jest.fn()} />
        </SessionContext>
      </ThemeProvider>
    );

    expect(screen.getByRole('button', { name: 'Item 1' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Item 1' })).not.toHaveClass('unselected');

    expect(screen.getByRole('button', { name: 'Item 2' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Item 2' })).toHaveClass('unselected');

    expect(screen.getByRole('button', { name: 'Item 3' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Item 3' })).toHaveClass('unselected');

    expect(screen.queryByTestId('left-arrow')).not.toBeInTheDocument();
    expect(screen.queryByTestId('right-arrow')).not.toBeInTheDocument();
  });

  it('shows scroll buttons if content overflows', async () => {
    Object.defineProperty(HTMLElement.prototype, 'scrollWidth', { configurable: true, value: 500 });
    Object.defineProperty(HTMLElement.prototype, 'clientWidth', { configurable: true, value: 10 });

    render(
      <ThemeProvider theme={theme}>
        <SessionContext>
          <HorizontalList items={listItems} activeItem='item_1' setActiveItem={jest.fn()} />
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
          <HorizontalList items={listItems} activeItem='item_1' setActiveItem={jest.fn()} />
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
          <HorizontalList items={listItems} activeItem='item_1' setActiveItem={jest.fn()} />
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
          <HorizontalList items={listItems} activeItem='item_1' setActiveItem={jest.fn()} />
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
          <HorizontalList items={listItems} activeItem='item_1' setActiveItem={jest.fn()} />
        </SessionContext>
      </ThemeProvider>
    );

    fireEvent.click(screen.getByTestId('left-arrow'));
    expect(scrollToMock).not.toHaveBeenCalled();
  });
});
