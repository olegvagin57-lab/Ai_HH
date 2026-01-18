import { test, expect } from '@playwright/test';

test.describe('Search Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.waitForLoadState('networkidle');
    
    const emailInput = page.getByLabel(/email|username/i).or(page.getByPlaceholder(/email|username/i));
    const passwordInput = page.locator('input[name="password"]').first();
    
    await emailInput.waitFor({ state: 'visible', timeout: 10000 });
    await passwordInput.waitFor({ state: 'visible', timeout: 10000 });
    
    await emailInput.fill('admin@test.com');
    await passwordInput.fill('Admin123!');
    
    // Wait for login response (check both success and error)
    const loginResponsePromise = page.waitForResponse(response => 
      response.url().includes('/api/v1/auth/login') && 
      response.request().method() === 'POST'
    , { timeout: 10000 });
    
    const submitButton = page.getByRole('button', { name: /login|войти/i });
    await submitButton.click();
    
    // Wait for login response
    const loginResponse = await loginResponsePromise;
    
    // Check if login was successful
    if (loginResponse.status() !== 200) {
      const errorData = await loginResponse.json().catch(() => ({}));
      throw new Error(`Login failed with status ${loginResponse.status()}: ${JSON.stringify(errorData)}`);
    }
    
    const loginData = await loginResponse.json();
    if (!loginData.access_token) {
      throw new Error(`Login response missing access_token: ${JSON.stringify(loginData)}`);
    }
    
    // Verify token is stored in localStorage
    const token = await page.evaluate(() => localStorage.getItem('access_token'));
    if (!token) {
      throw new Error('Access token was not stored in localStorage after login');
    }
    
    // Wait for navigation after successful login
    await page.waitForURL(/\/(dashboard|search)/, { timeout: 10000 });
    await page.waitForLoadState('networkidle');
  });

  test('should display search page', async ({ page }) => {
    await page.goto('/search');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Check for search form elements - use more specific selectors
    const queryInput = page.getByLabel(/поисковый запрос|query/i).or(
      page.getByPlaceholder(/python разработчик/i)
    ).or(page.locator('input[type="text"]').first());
    const cityInput = page.getByLabel(/город|city/i).or(
      page.getByPlaceholder(/москва/i)
    ).or(page.locator('input[type="text"]').nth(1));
    
    await expect(queryInput).toBeVisible({ timeout: 10000 });
    await expect(cityInput).toBeVisible({ timeout: 10000 });
  });

  test('should create a search', async ({ page }) => {
    await page.goto('/search');
    await page.waitForLoadState('networkidle');
    
    const queryInput = page.getByLabel(/поисковый запрос|query/i).or(
      page.getByPlaceholder(/python разработчик/i)
    ).or(page.locator('input[type="text"]').first());
    const cityInput = page.getByLabel(/город|city/i).or(
      page.getByPlaceholder(/москва/i)
    ).or(page.locator('input[type="text"]').nth(1));
    
    await queryInput.waitFor({ state: 'visible', timeout: 10000 });
    await cityInput.waitFor({ state: 'visible', timeout: 10000 });
    
    await queryInput.fill('Python developer');
    await cityInput.fill('Москва');
    
    // Verify token exists in localStorage (should be from beforeEach)
    const token = await page.evaluate(() => localStorage.getItem('access_token'));
    if (!token) {
      throw new Error('Access token not found in localStorage. Login may have failed.');
    }
    
    const submitButton = page.locator('button[type="submit"]').or(
      page.getByRole('button', { name: /начать поиск|поиск/i })
    ).first();
    
    await submitButton.waitFor({ state: 'visible', timeout: 10000 });
    
    // Check that button is not disabled
    const isDisabled = await submitButton.isDisabled();
    if (isDisabled) {
      throw new Error('Submit button is disabled. Form may be invalid.');
    }
    
    // Set up response listener before clicking
    const responsePromise = page.waitForResponse(response => 
      response.url().includes('/api/v1/search') && 
      response.request().method() === 'POST'
    , { timeout: 15000 });
    
    // Click the button
    await submitButton.click();
    
    // Wait for API response
    const response = await responsePromise;
    
    // Check if response was successful
    if (response.status() !== 201) {
      const errorData = await response.json().catch(() => ({}));
      // Check for error message on page
      const errorAlert = page.locator('[role="alert"]').filter({ hasText: /ошибка|error/i });
      const hasError = await errorAlert.isVisible().catch(() => false);
      if (hasError) {
        const errorText = await errorAlert.textContent();
        throw new Error(`Search creation failed with status ${response.status()}. Error on page: ${errorText}`);
      }
      throw new Error(`Search creation failed with status ${response.status()}: ${JSON.stringify(errorData)}`);
    }
    
    // Verify response has id
    const responseData = await response.json();
    expect(responseData).toHaveProperty('id');
    
    // Wait for navigation to results page
    await page.waitForURL(/\/results\/[^/]+/, { timeout: 20000 });
    await page.waitForLoadState('networkidle');
    
    // Verify we're on the results page
    await expect(
      page.getByRole('heading', { name: /результаты поиска/i })
    ).toBeVisible({ timeout: 10000 });
  });

  test('should validate required fields', async ({ page }) => {
    await page.goto('/search');
    await page.waitForLoadState('networkidle');
    
    const queryInput = page.getByLabel(/поисковый запрос|query/i).or(
      page.getByPlaceholder(/python разработчик/i)
    ).or(page.locator('input[type="text"]').first());
    
    await queryInput.waitFor({ state: 'visible', timeout: 10000 });
    await queryInput.clear();
    
    const submitButton = page.locator('button[type="submit"]').or(
      page.getByRole('button', { name: /начать поиск|поиск/i })
    ).first();
    
    await submitButton.waitFor({ state: 'visible', timeout: 10000 });
    
    const currentUrl = page.url();
    
    // Try to submit the form
    await submitButton.click();
    
    // Wait a bit to see if navigation occurs
    await page.waitForTimeout(1000);
    
    // Form should not submit (URL should not change) when required fields are empty
    expect(page.url()).toBe(currentUrl);
    
    // Check that the query input has required attribute
    const isRequired = await queryInput.evaluate((el) => el.hasAttribute('required'));
    expect(isRequired).toBe(true);
  });
});
