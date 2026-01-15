// API configuration that works in both Vite and Jest
// In Vite, process.env will be replaced with import.meta.env during build
// In Jest, we use process.env directly

// Get API URL from environment or use default
const getApiUrl = () => {
  // In Jest/Node environment
  if (typeof process !== 'undefined' && process.env && process.env.VITE_API_URL) {
    return process.env.VITE_API_URL;
  }
  // Default fallback
  return '/api/v1';
};

const API_BASE_URL = getApiUrl();

export default API_BASE_URL;
