/* eslint-disable @typescript-eslint/no-empty-interface */
/* eslint-disable @typescript-eslint/no-namespace */
// This module is used to validate the environment variables

import { z } from 'zod';

const envSchema = z.object({
  NEXT_PUBLIC_SCICHART_KEY: z.string(),
  SCI_CHART_SERVER_KEY: z.string(),
  NEXT_PUBLIC_ENVIRONMENT: z.string(),
  NEXT_PUBLIC_SIBEL_UDI: z.string(),
});

export const ENV = envSchema.parse({
  NEXT_PUBLIC_SCICHART_KEY: process.env.NEXT_PUBLIC_SCICHART_KEY,
  SCI_CHART_SERVER_KEY: process.env.SCI_CHART_SERVER_KEY,
  NEXT_PUBLIC_ENVIRONMENT: process.env.NEXT_PUBLIC_ENVIRONMENT,
  NEXT_PUBLIC_SIBEL_UDI: process.env.NEXT_PUBLIC_SIBEL_UDI,
});

// Makes the environment variables typed available globally
type EnvSchemaType = z.infer<typeof envSchema>;
declare global {
  namespace NodeJS {
    interface ProcessEnv extends EnvSchemaType {}
  }
}
