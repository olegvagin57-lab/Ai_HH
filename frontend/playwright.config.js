import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: [
    // Start MongoDB and Redis only locally (in CI they're provided by services)
    ...(process.env.CI ? [] : [{
      command: 'cd .. && docker-compose up -d mongodb redis && sleep 5',
      url: 'http://localhost:8000/api/v1/health',
      reuseExistingServer: true,
      timeout: 60 * 1000,
      stdout: 'pipe',
      stderr: 'pipe',
    }]),
    {
      command: 'cd ../backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000',
      url: 'http://localhost:8000/api/v1/health/ready',
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000,
      stdout: 'pipe',
      stderr: 'pipe',
      env: {
        MONGODB_URL: process.env.MONGODB_URL || 'mongodb://localhost:27017',
        MONGODB_DATABASE: process.env.MONGODB_DATABASE || 'hh_analyzer_test',
        REDIS_URL: process.env.REDIS_URL || 'redis://localhost:6379',
        SECRET_KEY: process.env.SECRET_KEY || 'test-secret-key-for-ci-min-32-chars-required-12345678901234567890',
        ENVIRONMENT: 'test',
        RATE_LIMIT_ENABLED: 'false',
        CLOUDFLARE_WORKER_URL: process.env.CLOUDFLARE_WORKER_URL || '',
        CORS_ORIGINS: 'http://localhost:3000',
      },
    },
    {
      command: 'npm run dev',
      url: 'http://localhost:3000',
      reuseExistingServer: !process.env.CI,
      timeout: 60 * 1000,
    },
  ],
});
