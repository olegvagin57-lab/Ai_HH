/**
 * Mock for @/lib/query to avoid module resolution issues in CI
 * Jest automatically uses this file when @/lib/query is imported
 */
export const queryKeys = {
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
};
