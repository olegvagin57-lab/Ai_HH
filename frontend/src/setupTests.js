import '@testing-library/jest-dom';

// Mock @/lib/query to avoid module resolution issues in CI
// This is a workaround for Jest not finding the module in GitHub Actions
jest.mock('@/lib/query', () => ({
  queryKeys: {
    search: {
      all: ['searches'],
      detail: (id) => ['searches', id],
      resumes: (id) => ['searches', id, 'resumes'],
    },
    users: {
      all: ['users'],
      detail: (id) => ['users', id],
      current: ['users', 'current'],
    },
  },
}));

// Suppress React Router v7 deprecation warnings in tests
const originalError = console.error;
const originalWarn = console.warn;
beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('React Router Future Flag Warning') ||
       args[0].includes('validateDOMNesting') ||
       args[0].includes('An update to Transition'))
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
  
  console.warn = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('React Router Future Flag Warning')
    ) {
      return;
    }
    originalWarn.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
  console.warn = originalWarn;
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return [];
  }
  unobserve() {}
};
