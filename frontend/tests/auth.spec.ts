#!/usr/bin/env node

/**
 * Automated test for Notion Clone frontend registration flow
 * Uses Playwright to test the UI
 */

const { test, expect } = require('@playwright/test');

const BASE_URL = 'http://localhost:3000';
const API_URL = 'http://localhost:8000/api/v1';
const TIMEOUT = 30000;

test.describe('Notion Clone - Registration Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to register page
    await page.goto(`${BASE_URL}/auth/register`, { waitUntil: 'networkidle' });
  });

  test('should display registration form', async ({ page }) => {
    // Check if form elements exist
    await expect(page.locator('text=Criar conta')).toBeVisible();
    await expect(page.locator('input[type="text"][placeholder*="Nome"]')).toBeVisible();
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toHaveCount(2);
  });

  test('should show validation error for short password', async ({ page }) => {
    const timestamp = Date.now();
    
    // Fill form with short password
    await page.fill('input[placeholder*="Nome"]', `Test User ${timestamp}`);
    await page.fill('input[type="email"]', `test${timestamp}@example.com`);
    await page.fill('input[type="password"]:nth-of-type(1)', 'short');
    await page.fill('input[type="password"]:nth-of-type(2)', 'short');
    
    // Click submit
    await page.click('button:has-text("Criar conta")');
    
    // Check for error message
    await expect(page.locator('text=A senha deve ter pelo menos 8 caracteres')).toBeVisible();
  });

  test('should show validation error for mismatched passwords', async ({ page }) => {
    const timestamp = Date.now();
    
    // Fill form with mismatched passwords
    await page.fill('input[placeholder*="Nome"]', `Test User ${timestamp}`);
    await page.fill('input[type="email"]', `test${timestamp}@example.com`);
    await page.fill('input[type="password"]:nth-of-type(1)', 'ValidPassword123');
    await page.fill('input[type="password"]:nth-of-type(2)', 'DifferentPassword123');
    
    // Click submit
    await page.click('button:has-text("Criar conta")');
    
    // Check for error message
    await expect(page.locator('text=As senhas não coincidem')).toBeVisible();
  });

  test('should successfully register new user', async ({ page }) => {
    const timestamp = Date.now();
    const testEmail = `test${timestamp}@example.com`;
    const testPassword = `ValidPassword${timestamp}!`;
    
    // Fill form
    await page.fill('input[placeholder*="Nome"]', `Test User ${timestamp}`);
    await page.fill('input[type="email"]', testEmail);
    await page.fill('input[type="password"]:nth-of-type(1)', testPassword);
    await page.fill('input[type="password"]:nth-of-type(2)', testPassword);
    
    // Click submit button
    const submitButton = page.locator('button:has-text("Criar conta")');
    await submitButton.click();
    
    // Wait for navigation to dashboard
    await page.waitForURL(`${BASE_URL}/dashboard*`, { timeout: TIMEOUT });
    
    // Verify we're on dashboard
    await expect(page).toHaveURL(new RegExp(`${BASE_URL}/dashboard`));
  });

  test('should show error for duplicate email', async ({ page }) => {
    const timestamp = Date.now();
    const testPassword = `ValidPassword${timestamp}!`;
    
    // First registration
    await page.fill('input[placeholder*="Nome"]', `Test User 1 ${timestamp}`);
    await page.fill('input[type="email"]', `duplicate${timestamp}@example.com`);
    await page.fill('input[type="password"]:nth-of-type(1)', testPassword);
    await page.fill('input[type="password"]:nth-of-type(2)', testPassword);
    await page.click('button:has-text("Criar conta")');
    
    // Wait for successful registration
    await page.waitForURL(`${BASE_URL}/dashboard*`, { timeout: TIMEOUT });
    
    // Logout (if needed, navigate back to register)
    await page.goto(`${BASE_URL}/auth/register`, { waitUntil: 'networkidle' });
    
    // Second registration with same email
    await page.fill('input[placeholder*="Nome"]', `Test User 2 ${timestamp}`);
    await page.fill('input[type="email"]', `duplicate${timestamp}@example.com`);
    await page.fill('input[type="password"]:nth-of-type(1)', testPassword);
    await page.fill('input[type="password"]:nth-of-type(2)', testPassword);
    await page.click('button:has-text("Criar conta")');
    
    // Check for error message
    await expect(page.locator('text=/Email already registered|Email já cadastrado/')).toBeVisible({ timeout: 5000 });
  });

  test('should navigate to login page from register', async ({ page }) => {
    // Click on login link
    await page.click('a:has-text("Entrar")');
    
    // Verify we're on login page
    await expect(page).toHaveURL(`${BASE_URL}/auth/login`);
    await expect(page.locator('text=Bem-vindo de volta')).toBeVisible();
  });
});
