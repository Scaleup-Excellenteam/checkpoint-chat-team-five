import { test, expect } from '@playwright/test';

test('happy path chat: load history and send message', async ({ page }) => {
  await page.goto('/');
  await page.goto('/general');
  await expect(page.getByText('General Chat')).toBeVisible();
  // Type and send
  const input = page.getByPlaceholder('Type your message');
  await input.fill('Hello E2E');
  await page.getByRole('button', { name: 'Send' }).click();
  // Expect it to appear (either via WS or REST fallback)
  await expect(page.getByText('Hello E2E')).toBeVisible();
});


