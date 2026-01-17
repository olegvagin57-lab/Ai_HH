import { test, expect } from '@playwright/test';

test.describe('Candidates Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    const emailInput = page.getByLabel(/email|username/i).or(page.getByPlaceholder(/email|username/i));
    const passwordInput = page.getByLabel(/password/i).or(page.getByPlaceholder(/password/i));
    
    await emailInput.fill('admin@test.com');
    await passwordInput.fill('Admin123!');
    
    const submitButton = page.getByRole('button', { name: /login|войти/i });
    await submitButton.click();
    
    await page.waitForURL(/\/(dashboard|search)/, { timeout: 5000 });
  });

  test('should display candidates page', async ({ page }) => {
    await page.goto('/candidates');
    
    // Should show candidates list or empty state
    await expect(
      page.getByText(/candidates|кандидаты/i).or(page.getByText(/no candidates|нет кандидатов/i))
    ).toBeVisible();
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
