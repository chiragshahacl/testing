import { ServerGroup } from '@/types/group';
import { faker } from '@faker-js/faker';

const createServerSideGroup = (override = {}): ServerGroup => ({
  id: faker.string.uuid(),
  name: faker.lorem.slug(),
  beds: [],
  ...override,
});

export { createServerSideGroup };
