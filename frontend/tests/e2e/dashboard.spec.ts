import { test, expect } from '@playwright/test';

// Helper para criar usuário e fazer login
async function loginTestUser(page: any) {
  const testUser = {
    email: `test${Date.now()}@example.com`,
    password: 'Test123456',
    name: 'Test User Dashboard'
  };

  // Limpar localStorage
  await page.goto('/');
  await page.evaluate(() => localStorage.clear());

  // Criar conta
  await page.goto('/auth/register');
  await page.getByPlaceholder('Seu nome').fill(testUser.name);
  await page.getByPlaceholder('seu@email.com').fill(testUser.email);

  const senhas = await page.getByPlaceholder('••••••••').all();
  await senhas[0].fill(testUser.password);
  await senhas[1].fill(testUser.password);
  await page.getByRole('button', { name: 'Criar conta' }).click();

  await page.waitForURL('/dashboard');

  return testUser;
}

test.describe('Dashboard', () => {
  test('deve exibir dashboard após login', async ({ page }) => {
    const user = await loginTestUser(page);

    // Verificar elementos do dashboard
    await expect(page.getByText('Notion Clone')).toBeVisible();
    await expect(page.getByText(`Olá, ${user.name}`)).toBeVisible();
    await expect(page.getByRole('button', { name: 'Sair' })).toBeVisible();
  });

  test('deve exibir mensagem de boas-vindas', async ({ page }) => {
    await loginTestUser(page);

    await expect(page.getByText('Bem-vindo ao Dashboard!')).toBeVisible();
    await expect(page.getByText('O frontend foi configurado com sucesso!')).toBeVisible();
  });

  test('deve exibir lista de features completas', async ({ page }) => {
    await loginTestUser(page);

    // Verificar features implementadas
    await expect(page.getByText('Setup completo')).toBeVisible();
    await expect(page.getByText('Next.js 14 com TypeScript')).toBeVisible();
    await expect(page.getByText('Tailwind CSS configurado')).toBeVisible();
    await expect(page.getByText('Zustand para state management')).toBeVisible();
    await expect(page.getByText('React Query configurado')).toBeVisible();
    await expect(page.getByText('API client com Axios')).toBeVisible();
    await expect(page.getByText('Autenticação funcionando')).toBeVisible();
  });

  test('deve exibir próximos passos', async ({ page }) => {
    await loginTestUser(page);

    await expect(page.getByText('Próximos passos')).toBeVisible();
    await expect(page.getByText('Implementar sidebar com workspaces')).toBeVisible();
    await expect(page.getByText('Criar sistema de páginas')).toBeVisible();
    await expect(page.getByText('Adicionar editor de blocos')).toBeVisible();
  });

  test('deve ter header fixo', async ({ page }) => {
    await loginTestUser(page);

    const header = page.locator('header');
    await expect(header).toBeVisible();
    await expect(header).toHaveClass(/border-b/);
  });

  test('deve proteger rota do dashboard', async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());

    // Tentar acessar dashboard sem autenticação
    await page.goto('/dashboard');

    // Deve redirecionar para login
    await expect(page).toHaveURL('/auth/login');
  });

  test('deve fazer logout e limpar sessão', async ({ page }) => {
    const user = await loginTestUser(page);

    // Verificar que está autenticado
    await expect(page.getByText(`Olá, ${user.name}`)).toBeVisible();

    // Fazer logout
    await page.getByRole('button', { name: 'Sair' }).click();

    // Verificar redirect
    await expect(page).toHaveURL('/auth/login');

    // Tentar voltar ao dashboard
    await page.goto('/dashboard');

    // Deve redirecionar para login novamente
    await expect(page).toHaveURL('/auth/login');
  });

  test('deve exibir nome do usuário corretamente', async ({ page }) => {
    const user = await loginTestUser(page);

    const userGreeting = page.getByText(`Olá, ${user.name}`);
    await expect(userGreeting).toBeVisible();
    await expect(userGreeting).toHaveClass(/text-sm text-muted-foreground/);
  });

  test('deve manter autenticação após navegação', async ({ page }) => {
    const user = await loginTestUser(page);

    // Navegar para outras rotas
    await page.goto('/');
    await expect(page).toHaveURL('/auth/login'); // Home redireciona

    await page.goto('/dashboard');
    await expect(page).toHaveURL('/dashboard'); // Deve permanecer autenticado

    await expect(page.getByText(`Olá, ${user.name}`)).toBeVisible();
  });

  test('deve persistir autenticação após reload da página', async ({ page }) => {
    const user = await loginTestUser(page);

    // Recarregar página
    await page.reload();

    // Verificar que ainda está autenticado
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText(`Olá, ${user.name}`)).toBeVisible();
  });

  test('deve ter responsividade no header', async ({ page }) => {
    await loginTestUser(page);

    const header = page.locator('header');
    const container = header.locator('.container');

    await expect(container).toHaveClass(/flex/);
    await expect(container).toHaveClass(/items-center/);
    await expect(container).toHaveClass(/justify-between/);
  });
});
