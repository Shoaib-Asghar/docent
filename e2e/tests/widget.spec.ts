import { test, expect } from '@playwright/test';

test.describe('Docent AI Widget E2E', () => {

  test('User can open widget, ask a question, and receive a response', async ({ page }) => {
    // 1. Navigate to the Docusaurus Homepage
    await page.goto('/');

    // 2. Wait for the widget to inject into the DOM and become visible
    // The widget container uses an ID for deterministic locating
    const widgetButton = page.locator('#docent-widget-root button').first();
    await expect(widgetButton).toBeVisible();

    // 3. Click to open the chat interface
    await widgetButton.click();

    // 4. Verify the chat window opened by checking for the input field
    // We target the input field directly to ensure the UI rendered
    const chatInput = page.locator('input[placeholder*="Ask"]');
    await expect(chatInput).toBeVisible();

    // 5. Type a query and submit
    await chatInput.fill('What is Docent?');
    await chatInput.press('Enter');

    // 6. Wait for the AI's response to appear
    // We wait for a new message bubble that is not from the user
    // Since network requests to the AI take time, we increase the timeout to 15s
    const aiResponse = page.locator('.docent-message.bot').last();
    await expect(aiResponse).toBeVisible({ timeout: 15000 });
    
    // Ensure the response contains some text
    const responseText = await aiResponse.textContent();
    expect(responseText?.length).toBeGreaterThan(10);
  });
});
