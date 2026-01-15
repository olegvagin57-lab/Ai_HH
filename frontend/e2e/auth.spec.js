import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('should display login page', async ({ page }) => {
    await page.goto('/login');
    
    // Check for login form elements
    await expect(page.getByLabel(/email|username/i).or(page.getByPlaceholderText(/email|username/i))).toBeVisible();
    await expect(page.getByLabel(/password/i).or(page.getByPlaceholderText(/password/i))).toBeVisible();
    await expect(page.getByRole('button', { name: /login|войти/i })).toBeVisible();
  });

  test('should show validation errors for empty form', async ({ page }) => {
    await page.goto('/login');
    
    const submitButton = page.getByRole('button', { name: /login|войти/i });
    await submitButton.click();
    
    // Should show validation errors
    await expect(page.getByText(/required|обязательно/i).first()).toBeVisible();
  });

  test('should login with valid credentials', async ({ page }) => {
    await page.goto('/login');
    
    // Fill login form
    const emailInput = page.getByLabel(/email|username/i).or(page.getByPlaceholderText(/email|username/i));
    const passwordInput = page.getByLabel(/password/i).or(page.getByPlaceholderText(/password/i));
    
    await emailInput.fill('admin@test.com');
    await passwordInput.fill('Admin123!');
    
    const submitButton = page.getByRole('button', { name: /login|войти/i });
    await submitButton.click();
    
    // Should redirect after successful login
    await page.waitForURL(/\/(dashboard|search)/, { timeout: 5000 });
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');
    
    const emailInput = page.getByLabel(/email|username/i).or(page.getByPlaceholderText(/email|username/i));
    const passwordInput = page.getByLabel(/password/i).or(page.getByPlaceholderText(/password/i));
    
    await emailInput.fill('invalid@example.com');
    await passwordInput.fill('WrongPassword123');
    
    const submitButton = page.getByRole('button', { name: /login|войти/i });
    await submitButton.click();
    
    // Should show error message
    await expect(page.getByText(/invalid|неверный|error/i).first()).toBeVisible({ timeout: 5000 });
  });

  test('should navigate to register page', async ({ page }) => {
    await page.goto('/login');
    
    const registerLink = page.getByRole('link', { name: /register|регистрация/i });
    if (await registerLink.isVisible()) {
      await registerLink.click();
      await expect(page).toHaveURL(/\/register/);
    }
  });
});
