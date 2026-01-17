import { test, expect } from '@playwright/test';

test.describe('Search Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    const emailInput = page.getByLabel(/email|username/i).or(page.getByPlaceholder(/email|username/i));
    const passwordInput = page.locator('input[name="password"]').first();
    
    await emailInput.fill('admin@test.com');
    await passwordInput.fill('Admin123!');
    
    const submitButton = page.getByRole('button', { name: /login|войти/i });
    await submitButton.click();
    
    // Wait for navigation - try URL first, then wait a bit
    try {
      await page.waitForURL(/\/(dashboard|search)/, { timeout: 10000 });
    } catch {
      // If URL doesn't change, wait a bit for page to load
      await page.waitForTimeout(2000);
    }
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
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Use more specific selectors
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
    
    // Use more specific selector: button with type="submit" or text "Начать поиск"
    const submitButton = page.locator('button[type="submit"]').or(
      page.getByRole('button', { name: /начать поиск|поиск/i })
    ).first();
    
    // Wait for button to be enabled (not disabled)
    await submitButton.waitFor({ state: 'visible', timeout: 10000 });
    
    // Get current URL before submission
    const currentUrl = page.url();
    
    // Click submit button and wait for navigation
    await Promise.all([
      page.waitForURL(/\/results\/[^/]+/, { timeout: 20000 }), // ID can be string (MongoDB ObjectId)
      submitButton.click(),
    ]);
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Check for error message (if creation failed)
    const errorAlert = page.locator('[role="alert"]').filter({ hasText: /ошибка|error/i });
    const hasError = await errorAlert.isVisible().catch(() => false);
    
    if (hasError) {
      const errorText = await errorAlert.textContent();
      throw new Error(`Search creation failed with error: ${errorText}`);
    }
    
    // Verify we're on the results page by checking for the main heading
    await expect(
      page.getByRole('heading', { name: /результаты поиска/i })
    ).toBeVisible({ timeout: 10000 });
    
    // Verify URL changed to results page
    expect(page.url()).toMatch(/\/results\/[^/]+/);
  });

  test('should validate required fields', async ({ page }) => {
    await page.goto('/search');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Clear the query field to make it empty
    const queryInput = page.getByLabel(/поисковый запрос|query/i).or(
      page.getByPlaceholder(/python разработчик/i)
    ).or(page.locator('input[type="text"]').first());
    
    await queryInput.waitFor({ state: 'visible', timeout: 10000 });
    await queryInput.clear();
    
    // Use more specific selector: button with type="submit" or text "Начать поиск"
    const submitButton = page.locator('button[type="submit"]').or(
      page.getByRole('button', { name: /начать поиск|поиск/i })
    ).first();
    
    await submitButton.waitFor({ state: 'visible', timeout: 10000 });
    
    // Get current URL before submission attempt
    const currentUrl = page.url();
    
    // Try to submit the form
    await submitButton.click();
    
    // Wait a bit to see if navigation occurs
    await page.waitForTimeout(1000);
    
    // Form should not submit (URL should not change) when required fields are empty
    // This validates that HTML5 validation is working
    expect(page.url()).toBe(currentUrl);
    
    // Additionally, check that the query input has required attribute
    const isRequired = await queryInput.evaluate((el) => el.hasAttribute('required'));
    expect(isRequired).toBe(true);
  });
});
