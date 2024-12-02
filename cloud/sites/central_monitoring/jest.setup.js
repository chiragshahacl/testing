import '@testing-library/jest-dom/extend-expect';

class Worker {
  constructor(stringUrl) {
    this.url = stringUrl;
    // eslint-disable-next-line
    this.onmessage = () => {};
    // eslint-disable-next-line
    this.terminate = () => {};
  }

  // eslint-disable-next-line
  postMessage(msg) {}
}

window.Worker = Worker;
jest.mock('./src/utils/runtime', () => ({
  getCachedRuntimeConfig: () => ({ APP_URL: '' }),
  HOSPITAL_TZ: 'UTC',
  // eslint-disable-next-line
  HOSPITAL_TITLE: "Children's Hospital",
  MAX_NUMBER_BEDS: 64,
}));

process.env.NEXT_PUBLIC_ENVIRONMENT = 'Development';
