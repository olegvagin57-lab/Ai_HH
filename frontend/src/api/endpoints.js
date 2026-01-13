// API endpoints
// Note: baseURL is set in client.js, so endpoints should be relative paths
export const endpoints = {
  auth: {
    login: '/auth/login',
    register: '/auth/register',
    refresh: '/auth/refresh',
    logout: '/auth/logout',
    me: '/auth/me',
  },
  search: {
    create: '/search',
    list: '/search',
    detail: (id) => `/search/${id}`,
    status: (id) => `/search/${id}/status`,
    resumes: (id) => `/search/${id}/resumes`,
    exportExcel: (id) => `/search/${id}/export/excel`,
    exportCsv: (id) => `/search/${id}/export/csv`,
  },
  users: {
    list: '/users',
    detail: (id) => `/users/${id}`,
    update: (id) => `/users/${id}`,
    delete: (id) => `/users/${id}`,
  },
};
