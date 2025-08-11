import { test, expect } from '@playwright/test';

test('page loads without JS errors', async ({ page }) => {
  const errors = [];
  
  page.on('pageerror', (error) => {
    errors.push(error);
  });

  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      errors.push(new Error(`Console error: ${msg.text()}`));
    }
  });

  await page.goto('/');
  
  await expect(page).toHaveTitle(/Brands|Open Filament Database|web-ui/);
  
  await page.waitForTimeout(2000);
  
  expect(errors).toHaveLength(0);
});