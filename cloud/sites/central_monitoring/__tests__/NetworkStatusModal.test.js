import { fireEvent, render, screen, waitFor } from '@testing-library/react';

import NetworkStatusModal from '@/components/modals/NetworkStatusModal';

describe('Network status modal', () => {
  it('renders all components', async () => {
    render(
      <NetworkStatusModal
        isOnline={false}
        onLostConnection={jest.fn()}
        onConfirm={jest.fn()}
        title='Network disconnected'
        description='Unable to detect a network connection. Please check your network settings. If the problem persists, contact support.'
      />
    );

    expect(screen.getByText('Network disconnected')).toBeInTheDocument();
    expect(
      screen.getByText(
        'Unable to detect a network connection. Please check your network settings. If the problem persists, contact support.'
      )
    ).toBeInTheDocument();

    expect(screen.getByRole('button', { name: 'Ok' })).toBeInTheDocument();
  });

  it('Clicking ok wont do anything while the connection is not restored', async () => {
    const onConfirm = jest.fn();

    const { rerender } = render(
      <NetworkStatusModal
        isOnline={false}
        onLostConnection={jest.fn()}
        onConfirm={onConfirm}
        title='Network disconnected'
      />
    );

    const button = screen.getByRole('button', { name: 'Ok' });
    fireEvent.click(button);
    expect(onConfirm).not.toHaveBeenCalled();

    rerender(
      <NetworkStatusModal
        isOnline
        onLostConnection={jest.fn()}
        onConfirm={onConfirm}
        title='Network disconnected'
      />
    );

    fireEvent.click(button);
    expect(onConfirm).toHaveBeenCalled();
  });

  it('It can be closed when back online', async () => {
    render(
      <NetworkStatusModal
        isOnline={false}
        onLostConnection={jest.fn()}
        onConfirm={jest.fn()}
        title='Network disconnected'
      />
    );

    expect(screen.getByText('Network disconnected')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Ok' }));

    waitFor(() => {
      expect(screen.getByText('Network disconnected')).not.toBeInTheDocument();
    });
  });

  it('calls onConfirm when connection is restored and user clicks button', () => {
    const onConfirm = jest.fn();
    const { rerender } = render(
      <NetworkStatusModal isOnline={false} onConfirm={onConfirm} onLostConnection={jest.fn()} />
    );

    expect(onConfirm).not.toHaveBeenCalled();

    rerender(<NetworkStatusModal isOnline onConfirm={onConfirm} onLostConnection={jest.fn()} />);

    const okButton = screen.getByRole('button', { name: 'Ok' });
    fireEvent.click(okButton);
    expect(onConfirm).toHaveBeenCalled();
  });

  it('calls onLostConnection when connection is lost', () => {
    const onLostConnection = jest.fn();
    const { rerender } = render(
      <NetworkStatusModal isOnline onConfirm={jest.fn} onLostConnection={onLostConnection} />
    );
    expect(onLostConnection).not.toHaveBeenCalled();

    rerender(
      <NetworkStatusModal
        isOnline={false}
        onConfirm={jest.fn}
        onLostConnection={onLostConnection}
      />
    );

    expect(onLostConnection).toHaveBeenCalled();
  });
});
