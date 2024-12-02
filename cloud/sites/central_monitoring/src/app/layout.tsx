'use client';

import AudioManagerContext from '@/context/AudioManagerContext';
import RuntimeConfigProvider from '@/context/RuntimeContext';
import SessionContext from '@/context/SessionContext';
import { setupMoment } from '@/utils/moment';
import { CacheProvider } from '@emotion/react';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider } from '@mui/material/styles';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import createEmotionCache from '../createEmotionCache';
import theme from '../theme/theme';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterMoment } from '@mui/x-date-pickers/AdapterMoment';
import './i18n';

setupMoment();

const clientSideEmotionCache = createEmotionCache();

interface RootLayoutProps {
  children: React.ReactNode;
}
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 0,
      refetchOnWindowFocus: false,
      staleTime: 0,
    },
  },
});

/**
 * Creates the Root Layout, with Providers and Contexts to be used throughout CMS
 */
const RootLayout = ({ children }: RootLayoutProps) => {
  return (
    <html lang='en'>
      <body>
        <CacheProvider value={clientSideEmotionCache}>
          <QueryClientProvider client={queryClient}>
            <ThemeProvider theme={theme}>
              <RuntimeConfigProvider>
                <LocalizationProvider dateAdapter={AdapterMoment}>
                  <SessionContext>
                    <AudioManagerContext>
                      <CssBaseline />
                      {children}
                    </AudioManagerContext>
                  </SessionContext>
                </LocalizationProvider>
              </RuntimeConfigProvider>
            </ThemeProvider>
          </QueryClientProvider>
        </CacheProvider>
      </body>
    </html>
  );
};

export default RootLayout;
