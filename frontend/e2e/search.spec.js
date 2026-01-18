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
    
    // Fill inputs - select all text first, then type new value to replace it
    // This ensures React state updates properly for Material-UI TextFields
    await queryInput.click({ clickCount: 3 }); // Triple click to select all
    await queryInput.type('Python developer', { delay: 50 });
    
    // For city input, select all first, then type
    await cityInput.click({ clickCount: 3 }); // Triple click to select all
    await cityInput.type('Москва', { delay: 50 });
    
    // Wait for React state to update (Material-UI state updates are async)
    // The delay in type() helps, but we also need to wait for React to process the changes
    await page.waitForTimeout(500);
    
    // Verify token exists in localStorage (should be from beforeEach)
    const token = await page.evaluate(() => localStorage.getItem('access_token'));
    if (!token) {
      throw new Error('Access token not found in localStorage. Login may have failed.');
    }
    
    const submitButton = page.locator('button[type="submit"]').or(
      page.getByRole('button', { name: /начать поиск|поиск/i })
    ).first();
    
    await submitButton.waitFor({ state: 'visible', timeout: 10000 });
    
    // Wait for button to become enabled (React state updates after typing)
    await expect(submitButton).toBeEnabled({ timeout: 5000 });
    
    // Verify button is actually enabled and inputs have values
    const isEnabled = await submitButton.isEnabled();
    const queryValue = await queryInput.inputValue();
    const cityValue2 = await cityInput.inputValue();
    
    if (!isEnabled) {
      throw new Error(`Button is disabled. Query: "${queryValue}", City: "${cityValue2}"`);
    }
    
    // Set up response and navigation listeners before submitting
    const responsePromise = page.waitForResponse(response => 
      response.url().includes('/api/v1/search') && 
      response.request().method() === 'POST'
    , { timeout: 20000 });
    
    const navigationPromise = page.waitForURL(/\/results\/[^/]+/, { timeout: 25000 });
    
    // Submit the form instead of clicking button (more reliable for Material-UI forms)
    const form = page.locator('form').first();
    await form.evaluate((form) => form.requestSubmit());
    
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
    
    // Wait for navigation to results page (already started waiting above)
    await navigationPromise;
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
    
    // Get the form first to scope the button search
    const form = page.locator('form').first();
    
    // Find submit button inside the form only (not in navigation)
    const submitButton = form.locator('button[type="submit"]');
    
    await submitButton.waitFor({ state: 'visible', timeout: 10000 });
    
    // Clear query input - use triple click to select all, then delete
    await queryInput.click({ clickCount: 3 });
    await page.keyboard.press('Delete');
    await page.waitForTimeout(300);
    
    // Button should be disabled when query is empty
    // (city has default value "Москва", so only query needs to be empty)
    // But to be safe, let's also check with both fields empty
    const cityInput = page.getByLabel(/город|city/i).or(
      page.getByPlaceholder(/москва/i)
    ).or(page.locator('input[type="text"]').nth(1));
    
    // Clear city as well to make sure button is disabled
    await cityInput.click({ clickCount: 3 });
    await page.keyboard.press('Delete');
    await page.waitForTimeout(500); // Wait for React state update
    
    // Button should be disabled when required fields are empty
    await expect(submitButton).toBeDisabled({ timeout: 5000 });
    
    // Check that the query input has required attribute
    const isRequired = await queryInput.evaluate((el) => el.hasAttribute('required'));
    expect(isRequired).toBe(true);
  });
});
