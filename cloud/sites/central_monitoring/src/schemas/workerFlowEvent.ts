import { WORKER_FLOWS } from '@/utils/websocket/flows';
import { z } from 'zod';

const connectEventSchema = z.object({
  flow: z.literal(WORKER_FLOWS.CONNECT),
  token: z.string(),
  socketUrl: z.string(),
  allPatients: z.array(z.string()),
  allPatientFilters: z.array(z.string()).optional(),
  selectedPatientId: z.string().optional(),
  // TODO: Remove property when ECG Scale Indicator has been tested
  ignoreEcgFilter: z.boolean().optional(),
});

const updateSelectedPatientEventSchema = z.object({
  flow: z.literal(WORKER_FLOWS.UPDATE_SELECTED_PATIENT),
  patientPrimaryIdentifier: z.string().optional(),
});

const updateSelectedGroupEventSchema = z.object({
  flow: z.literal(WORKER_FLOWS.UPDATE_SELECTED_GROUP),
  patientsPrimaryIdentifiers: z.array(z.string()),
});

const disconnectEventSchema = z.object({
  flow: z.literal(WORKER_FLOWS.DISCONNECT),
});

const testDisconnectionEventSchema = z.object({
  flow: z.literal(WORKER_FLOWS.TEST_DISCONNECTION),
});

export const workerFlowEventSchema = z.discriminatedUnion('flow', [
  connectEventSchema,
  updateSelectedPatientEventSchema,
  updateSelectedGroupEventSchema,
  disconnectEventSchema,
  testDisconnectionEventSchema,
]);
