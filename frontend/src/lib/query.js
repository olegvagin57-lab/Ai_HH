/**
 * React Query keys for caching and invalidation
 */
export const queryKeys = {
  search: {
    all: ['searches'],
    detail: (id) => ['searches', id],
    resumes: (id) => ['searches', id, 'resumes'],
  },
  user: {
    all: ['users'],
    detail: (id) => ['users', id],
    current: ['users', 'current'],
  },
  users: {
    all: ['users'],
    detail: (id) => ['users', id],
    current: ['users', 'current'],
  },
};
