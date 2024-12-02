/* eslint-disable @typescript-eslint/no-empty-interface */
/* eslint-disable @typescript-eslint/no-namespace */
// This module is used to validate the environment variables

import moment from 'moment';
import { z } from 'zod';

const envSchema = z.object({
  APP_URL: z.string(),
  WSS_URL: z.string(),
  EMULATOR_URL: z.string().optional(),
  HOSPITAL_TITLE: z.string().optional().default(''),
  HOSPITAL_TZ: z
    .string()
    .optional()
    .default('UTC')
    .refine((val) => {
      return moment.tz.zone(val);
    }),
  MAX_NUMBER_BEDS: z.string(),
  HEALTHCHECK_INTERVAL: z.string().optional().default('30000'),
  IGNORE_BUTTERWORTH_FILTERS: z.string().optional().default('0'),
});

export const ENV = envSchema.safeParse(process.env);

if (!ENV.success) {
  throw new Error('There is an error with the server environment variables');
}

// Makes the environment variables typed available globally
type EnvSchemaType = z.infer<typeof envSchema>;
declare global {
  namespace NodeJS {
    interface ProcessEnv extends EnvSchemaType {}
  }
}
