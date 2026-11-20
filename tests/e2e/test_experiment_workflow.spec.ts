import { test, expect } from '@playwright/test';

test.describe('ResearchLab E2E Tests', () => {
  test('should load the application', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await expect(page.locator('text=ResearchLab')).toBeVisible();
  });

  test('should navigate to experiments page', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.click('text=Experiments');
    await expect(page.locator('h1', { hasText: /experiments/i })).toBeVisible();
  });

  test('should display dashboard stats from backend', async ({ page }) => {
    await page.goto('http://localhost:5173');
    // Dashboard should show health status
    await expect(page.locator('text=System health')).toBeVisible();
  });
});
