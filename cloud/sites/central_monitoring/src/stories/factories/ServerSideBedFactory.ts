import { ServerBed } from '@/types/bed';
import { faker } from '@faker-js/faker';

const createServerSideBed = (override = {}): ServerBed => ({
  id: faker.string.uuid(),
  name: faker.lorem.slug(),
  ...override,
});

export { createServerSideBed };
