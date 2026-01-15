import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  define: {
    // Replace process.env with import.meta.env for Vite
    'process.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL || '/api/v1'),
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
