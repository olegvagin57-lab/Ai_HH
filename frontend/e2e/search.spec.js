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
    await submitButton.click();
    
    // Should redirect to results page or show success message
    try {
      await page.waitForURL(/\/results\/\d+/, { timeout: 10000 });
    } catch {
      // If no redirect, check for success message
      await expect(
        page.getByText(/success|успешно|created|создан|processing|обработка/i).first()
      ).toBeVisible({ timeout: 5000 });
    }
  });

  test('should validate required fields', async ({ page }) => {
    await page.goto('/search');
    
    // Wait for page to load
    await page.waitForLoadState('networkidle');
    
    // Use more specific selector: button with type="submit" or text "Начать поиск"
    const submitButton = page.locator('button[type="submit"]').or(
      page.getByRole('button', { name: /начать поиск|поиск/i })
    ).first();
    
    await submitButton.waitFor({ state: 'visible', timeout: 10000 });
    await submitButton.click();
    
    // Should show validation errors (MUI shows "Поле обязательно для заполнения" or similar)
    await expect(
      page.getByText(/required|обязательно|заполнения/i).first()
    ).toBeVisible({ timeout: 5000 });
  });
});
