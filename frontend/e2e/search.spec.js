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
    
    // Wait for navigation (increase timeout for slow redirects)
    await page.waitForURL(/\/(dashboard|search)/, { timeout: 10000 });
  });

  test('should display search page', async ({ page }) => {
    await page.goto('/search');
    
    // Check for search form elements
    const queryInput = page.getByLabel(/query|описание/i).or(page.getByPlaceholder(/query|описание/i));
    const cityInput = page.getByLabel(/city|город/i).or(page.getByPlaceholder(/city|город/i));
    await expect(queryInput).toBeVisible();
    await expect(cityInput).toBeVisible();
  });

  test('should create a search', async ({ page }) => {
    await page.goto('/search');
    
    const queryInput = page.getByLabel(/query|описание/i).or(page.getByPlaceholder(/query|описание/i));
    const cityInput = page.getByLabel(/city|город/i).or(page.getByPlaceholder(/city|город/i));
    
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
    
    // Use more specific selector: button with type="submit" or text "Начать поиск"
    const submitButton = page.locator('button[type="submit"]').or(
      page.getByRole('button', { name: /начать поиск|поиск/i })
    ).first();
    await submitButton.click();
    
    // Should show validation errors
    await expect(page.getByText(/required|обязательно/i).first()).toBeVisible();
  });
});
