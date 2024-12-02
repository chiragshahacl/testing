'use client';

import { SciChartSurface } from 'scichart';
import MetricsContext from '@/context/MetricsContext';
import PatientsContext from '@/context/PatientsContext';
import AuthenticatedRoot from './AuthenticatedRoot';

interface RootLayoutProps {
  children: React.ReactNode;
}

const RootLayout = ({ children }: RootLayoutProps) => {
  SciChartSurface.useWasmLocal();
  SciChartSurface.setRuntimeLicenseKey(process.env.NEXT_PUBLIC_SCICHART_KEY);
  SciChartSurface.configure({
    wasmUrl: 'scichart2d.wasm',
    dataUrl: 'scichart2d.data',
  });
  return (
    <>
      <title>CMS - Home</title>
      <PatientsContext>
        <MetricsContext>
          <AuthenticatedRoot>{children}</AuthenticatedRoot>
        </MetricsContext>
      </PatientsContext>
    </>
  );
};

export default RootLayout;
