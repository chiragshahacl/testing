/* eslint-disable camelcase */
import { ServerSidePatientMonitor } from '@/types/patientMonitor';
import { faker } from '@faker-js/faker';

const createServerSidePatientMonitor = (
  override: Partial<ServerSidePatientMonitor> = {}
): ServerSidePatientMonitor => ({
  id: faker.string.uuid(),
  primary_identifier: faker.string.uuid(),
  name: `Patient Monitor ${faker.number.int({ min: 1, max: 10000 })}`,
  location_id: null,
  gateway_id: null,
  device_code: 'Patient Monitor',
  vital_ranges: [],
  ...override,
});

export { createServerSidePatientMonitor };
