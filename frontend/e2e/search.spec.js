import { test, expect } from '@playwright/test';

test.describe('Search Functionality', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    const emailInput = page.getByLabel(/email|username/i).or(page.getByPlaceholder(/email|username/i));
    const passwordInput = page.getByLabel(/password/i).or(page.getByPlaceholder(/password/i));
    
    await emailInput.fill('admin@test.com');
    await passwordInput.fill('Admin123!');
    
    const submitButton = page.getByRole('button', { name: /login|войти/i });
    await submitButton.click();
    
    // Wait for navigation
    await page.waitForURL(/\/(dashboard|search)/, { timeout: 5000 });
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
    
    const submitButton = page.getByRole('button', { name: /search|поиск|create|создать/i });
    await submitButton.click();
    
    // Should show success message or redirect
    await expect(
      page.getByText(/success|успешно|created|создан/i).or(page.getByText(/processing|обработка/i))
    ).toBeVisible({ timeout: 10000 });
  });

  test('should validate required fields', async ({ page }) => {
    await page.goto('/search');
    
    const submitButton = page.getByRole('button', { name: /search|поиск|create|создать/i });
    await submitButton.click();
    
    // Should show validation errors
    await expect(page.getByText(/required|обязательно/i).first()).toBeVisible();
  });
});
