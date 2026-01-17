const path = require('path');

module.exports = {
  rootDir: path.resolve(__dirname),
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  moduleNameMapper: {
    '^@/lib/query$': path.resolve(__dirname, 'src/lib/__mocks__/query.js'),
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '^@/api/config$': '<rootDir>/src/api/__mocks__/config.js',
  },
  moduleDirectories: ['node_modules', '<rootDir>/src'],
  transform: {
    '^.+\\.(js|jsx)$': ['babel-jest', {
      configFile: './babel.config.cjs',
    }],
  },
  transformIgnorePatterns: [
    'node_modules/(?!(.*\\.mjs$))',
  ],
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/main.jsx',
    '!src/**/*.test.{js,jsx}',
    '!src/**/__tests__/**',
  ],
  coverageThreshold: {
    global: {
      branches: 40,
      functions: 35,
      lines: 50,
      statements: 50,
    },
  },
  testMatch: [
    '**/__tests__/**/*.{js,jsx}',
    '**/*.{spec,test}.{js,jsx}',
  ],
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
    '/build/',
    '/e2e/',
  ],
  moduleFileExtensions: ['js', 'jsx', 'json'],
};
