import RuntimeConfigContext from '@/context/RuntimeContext';
import SessionContext from '@/context/SessionContext';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, waitFor } from '@testing-library/react';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { setCachedRuntimeConfig } from '../src/utils/runtime';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 0,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
    },
  },
});

const server = setupServer(
  rest.get('/api/user', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        config: 'new-config',
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

jest.mock('../src/utils/runtime', () => ({
  getCachedRuntimeConfig: () => ({ APP_URL: '' }),
  setCachedRuntimeConfig: jest.fn(),
}));

describe('RuntimeContext', () => {
  it('renders all components', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <SessionContext>
          <RuntimeConfigContext />
        </SessionContext>
      </QueryClientProvider>
    );

    await waitFor(() => {
      expect(setCachedRuntimeConfig).toHaveBeenCalledWith({ config: 'new-config' });
    });
  });
});
