import { test, expect } from '@playwright/test';

test.describe('Candidates Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test with retry logic for parallel execution
    const maxRetries = 5;
    let lastError = null;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        // Clear localStorage before each attempt
        await page.goto('/login');
        await page.evaluate(() => localStorage.clear());
        await page.reload();
        await page.waitForLoadState('networkidle');
        
        // Wait a bit to ensure backend is ready (exponential backoff before attempt)
        if (attempt > 1) {
          await page.waitForTimeout(500 * attempt);
        }
        
        const emailInput = page.getByLabel(/email|username/i).or(page.getByPlaceholder(/email|username/i));
        const passwordInput = page.locator('input[name="password"]').first();
        
        await emailInput.waitFor({ state: 'visible', timeout: 10000 });
        await passwordInput.waitFor({ state: 'visible', timeout: 10000 });
        
        // Clear inputs before filling
        await emailInput.clear();
        await passwordInput.clear();
        
        await emailInput.fill('admin@test.com');
        await passwordInput.fill('Admin123!');
        
        // Wait for login response
        const loginResponsePromise = page.waitForResponse(response => 
          response.url().includes('/api/v1/auth/login') && 
          response.request().method() === 'POST'
        , { timeout: 20000 });
        
        const submitButton = page.getByRole('button', { name: /login|войти/i });
        await submitButton.click();
        
        // Wait for login response
        const loginResponse = await loginResponsePromise;
        
        // Check if login was successful
        if (loginResponse.status() === 200) {
          const loginData = await loginResponse.json().catch(() => null);
          if (loginData && loginData.access_token) {
            // Verify token is stored in localStorage
            await page.waitForTimeout(500); // Wait for localStorage update
            const token = await page.evaluate(() => localStorage.getItem('access_token'));
            if (token) {
              // Wait for navigation after successful login
              await page.waitForURL(/\/(dashboard|search)/, { timeout: 10000 });
              await page.waitForLoadState('networkidle');
              return; // Success, exit retry loop
            }
          }
        }
        
        // If we get here, login failed
        if (attempt < maxRetries) {
          await page.waitForTimeout(1000 * attempt);
          continue;
        }
        
        // Last attempt failed, throw error
        const status = loginResponse.status();
        const errorData = await loginResponse.json().catch(() => ({}));
        throw new Error(`Login failed with status ${status}: ${JSON.stringify(errorData)}`);
      } catch (error) {
        lastError = error;
        if (attempt < maxRetries) {
          await page.waitForTimeout(1000 * attempt);
          continue;
        }
        throw lastError;
      }
    }
  });

  test('should display candidates page', async ({ page }) => {
    await page.goto('/candidates');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Should show candidates page heading (more specific locator to avoid strict mode violation)
    const heading = page.getByRole('heading', { name: /кандидаты/i });
    await expect(heading).toBeVisible({ timeout: 10000 });
  });

  test('should filter candidates by status', async ({ page }) => {
    await page.goto('/candidates');
    
    // Look for status filter
    const statusFilter = page.getByRole('button', { name: /status|статус/i }).or(
      page.getByLabel(/status|статус/i)
    );
    
    if (await statusFilter.isVisible()) {
      await statusFilter.click();
      await page.getByText(/new|новый/i).click();
      
      // Should filter candidates
      await expect(page.getByText(/new|новый/i)).toBeVisible();
    }
  });

  test('should view candidate details', async ({ page }) => {
    await page.goto('/candidates');
    
    // Click on first candidate if available
    const firstCandidate = page.locator('[data-testid="candidate-card"]').first().or(
      page.getByRole('link', { name: /view|просмотр/i }).first()
    );
    
    if (await firstCandidate.isVisible()) {
      await firstCandidate.click();
      
      // Should show candidate details
      await expect(page.getByText(/details|детали|information|информация/i)).toBeVisible({ timeout: 5000 });
    }
  });
});
