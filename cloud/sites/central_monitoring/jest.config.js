module.exports = {
  moduleNameMapper: {
    '^.+\\.(png|jpg|jpeg|gif|webp|avif|ico|bmp|svg)$': '<rootDir>/__mocks__/fileMock.js',
    'next/font/(.*)': require.resolve('next/dist/build/jest/__mocks__/nextFontMock.js'),

    '^@/types/(.*)$': '<rootDir>/src/types/$1',
    '^@/constants': '<rootDir>/src/constants',

    '^@/styles/(.*)$': '<rootDir>/src/styles/$1',

    '^@/utils/(.*)$': '<rootDir>/src/utils/$1',

    '^@/components/(.*)$': '<rootDir>/src/components/$1',
    '^@/stories/(.*)$': '<rootDir>/src/stories/$1',

    '^@/pages/(.*)$': '<rootDir>/src/pages/$1',

    '^@/context/(.*)$': '<rootDir>/src/context/$1',

    '^@/hooks/(.*)$': '<rootDir>/src/hooks/$1',

    '^@/api/(.*)$': '<rootDir>/src/api/$1',

    '^@/theme/(.*)$': '<rootDir>/src/theme/$1',

    '^@/app/(.*)$': '<rootDir>/src/app/$1',

    '^@/schemas/(.*)$': '<rootDir>/src/schemas/$1',
  },
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testPathIgnorePatterns: ['<rootDir>/node_modules/', '<rootDir>/.next/'],
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': [
      'babel-jest',
      { presets: ['next/babel'], plugins: ['babel-plugin-transform-import-meta'] },
    ],
  },
  transformIgnorePatterns: ['node_modules/(?!(jest-)?.*)'],
  testEnvironment: 'jest-environment-jsdom',
};
