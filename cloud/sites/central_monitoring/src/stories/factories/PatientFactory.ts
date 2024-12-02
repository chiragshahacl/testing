import { PatientType } from '@/types/patient';
import { faker } from '@faker-js/faker';

const createPatient = (override: Partial<PatientType> = {}): PatientType => ({
  id: faker.string.uuid(),
  primaryIdentifier: faker.string.uuid(),
  givenName: faker.person.firstName(),
  familyName: faker.person.lastName(),
  gender: faker.person.gender(),
  birthDate: faker.date.birthdate().toISOString(),
  ...override,
});

export { createPatient };
