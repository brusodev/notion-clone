import { test, expect } from '@playwright/test';

// Configuração de teste - limpar localStorage antes de cada teste
test.beforeEach(async ({ page }) => {
  await page.goto('/');
  await page.evaluate(() => localStorage.clear());
});

test.describe('Autenticação', () => {
  const testUser = {
    email: `test${Date.now()}@example.com`,
    password: 'Test123456',
    name: 'Test User'
  };

  test('deve redirecionar para login quando não autenticado', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL('/auth/login');
  });

  test('deve exibir página de login corretamente', async ({ page }) => {
    await page.goto('/auth/login');

    // Verificar elementos da página
    await expect(page.getByRole('heading', { name: 'Bem-vindo de volta' })).toBeVisible();
    await expect(page.getByPlaceholder('seu@email.com')).toBeVisible();
    await expect(page.getByPlaceholder('••••••••')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Entrar' })).toBeVisible();
    await expect(page.getByText('Não tem uma conta?')).toBeVisible();
  });

  test('deve exibir página de registro corretamente', async ({ page }) => {
    await page.goto('/auth/register');

    // Verificar elementos da página
    await expect(page.getByRole('heading', { name: 'Criar conta' })).toBeVisible();
    await expect(page.getByPlaceholder('Seu nome')).toBeVisible();
    await expect(page.getByPlaceholder('seu@email.com')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Criar conta' })).toBeVisible();
    await expect(page.getByText('Já tem uma conta?')).toBeVisible();
  });

  test('deve navegar entre login e registro', async ({ page }) => {
    await page.goto('/auth/login');

    // Ir para registro
    await page.getByRole('link', { name: 'Criar conta' }).click();
    await expect(page).toHaveURL('/auth/register');

    // Voltar para login
    await page.getByRole('link', { name: 'Fazer login' }).click();
    await expect(page).toHaveURL('/auth/login');
  });

  test('deve validar campos obrigatórios no login', async ({ page }) => {
    await page.goto('/auth/login');

    // Tentar submeter sem preencher
    await page.getByRole('button', { name: 'Entrar' }).click();

    // Verificar validação HTML5 (campo email required)
    const emailInput = page.getByPlaceholder('seu@email.com');
    await expect(emailInput).toHaveAttribute('required');
  });

  test('deve validar formato de email no login', async ({ page }) => {
    await page.goto('/auth/login');

    // Preencher com email inválido
    await page.getByPlaceholder('seu@email.com').fill('email-invalido');
    await page.getByPlaceholder('••••••••').fill('senha123');
    await page.getByRole('button', { name: 'Entrar' }).click();

    // Verificar validação de email (HTML5)
    const emailInput = page.getByPlaceholder('seu@email.com');
    await expect(emailInput).toHaveAttribute('type', 'email');
  });

  test('deve validar senhas coincidentes no registro', async ({ page }) => {
    await page.goto('/auth/register');

    // Preencher formulário
    await page.getByPlaceholder('Seu nome').fill(testUser.name);
    await page.getByPlaceholder('seu@email.com').fill(testUser.email);

    // Preencher senhas diferentes
    const senhas = await page.getByPlaceholder('••••••••').all();
    await senhas[0].fill('senha123');
    await senhas[1].fill('senha456');

    await page.getByRole('button', { name: 'Criar conta' }).click();

    // Verificar mensagem de erro
    await expect(page.getByText('As senhas não coincidem')).toBeVisible();
  });

  test('deve validar tamanho mínimo da senha no registro', async ({ page }) => {
    await page.goto('/auth/register');

    // Preencher formulário
    await page.getByPlaceholder('Seu nome').fill(testUser.name);
    await page.getByPlaceholder('seu@email.com').fill(testUser.email);

    // Preencher senha curta
    const senhas = await page.getByPlaceholder('••••••••').all();
    await senhas[0].fill('123');
    await senhas[1].fill('123');

    await page.getByRole('button', { name: 'Criar conta' }).click();

    // Verificar mensagem de erro
    await expect(page.getByText('A senha deve ter pelo menos 6 caracteres')).toBeVisible();
  });

  test('deve criar conta com sucesso', async ({ page }) => {
    await page.goto('/auth/register');

    // Preencher formulário
    await page.getByPlaceholder('Seu nome').fill(testUser.name);
    await page.getByPlaceholder('seu@email.com').fill(testUser.email);

    const senhas = await page.getByPlaceholder('••••••••').all();
    await senhas[0].fill(testUser.password);
    await senhas[1].fill(testUser.password);

    // Submeter formulário
    await page.getByRole('button', { name: 'Criar conta' }).click();

    // Aguardar redirect para dashboard
    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });

    // Verificar elementos do dashboard
    await expect(page.getByText(`Olá, ${testUser.name}`)).toBeVisible();
  });

  test('deve fazer login com sucesso', async ({ page }) => {
    // Primeiro, criar conta
    await page.goto('/auth/register');
    await page.getByPlaceholder('Seu nome').fill(testUser.name);
    await page.getByPlaceholder('seu@email.com').fill(testUser.email);

    let senhas = await page.getByPlaceholder('••••••••').all();
    await senhas[0].fill(testUser.password);
    await senhas[1].fill(testUser.password);
    await page.getByRole('button', { name: 'Criar conta' }).click();

    // Aguardar dashboard e fazer logout
    await page.waitForURL('/dashboard');
    await page.getByRole('button', { name: 'Sair' }).click();

    // Fazer login
    await page.waitForURL('/auth/login');
    await page.getByPlaceholder('seu@email.com').fill(testUser.email);
    await page.getByPlaceholder('••••••••').fill(testUser.password);
    await page.getByRole('button', { name: 'Entrar' }).click();

    // Verificar redirect para dashboard
    await expect(page).toHaveURL('/dashboard', { timeout: 10000 });
    await expect(page.getByText(`Olá, ${testUser.name}`)).toBeVisible();
  });

  test('deve exibir erro com credenciais inválidas', async ({ page }) => {
    await page.goto('/auth/login');

    // Tentar login com credenciais inválidas
    await page.getByPlaceholder('seu@email.com').fill('usuario@inexistente.com');
    await page.getByPlaceholder('••••••••').fill('senhaErrada123');
    await page.getByRole('button', { name: 'Entrar' }).click();

    // Verificar mensagem de erro (aguardar aparecer)
    await expect(page.getByText(/Credenciais inválidas|Erro ao fazer login/i)).toBeVisible({ timeout: 5000 });
  });

  test('deve fazer logout com sucesso', async ({ page }) => {
    // Criar conta e fazer login
    await page.goto('/auth/register');
    await page.getByPlaceholder('Seu nome').fill(testUser.name);
    await page.getByPlaceholder('seu@email.com').fill(testUser.email);

    const senhas = await page.getByPlaceholder('••••••••').all();
    await senhas[0].fill(testUser.password);
    await senhas[1].fill(testUser.password);
    await page.getByRole('button', { name: 'Criar conta' }).click();

    await page.waitForURL('/dashboard');

    // Fazer logout
    await page.getByRole('button', { name: 'Sair' }).click();

    // Verificar redirect para login
    await expect(page).toHaveURL('/auth/login');

    // Verificar que não consegue acessar dashboard
    await page.goto('/dashboard');
    await expect(page).toHaveURL('/auth/login');
  });

  test('deve manter sessão após reload', async ({ page }) => {
    // Criar conta
    await page.goto('/auth/register');
    await page.getByPlaceholder('Seu nome').fill(testUser.name);
    await page.getByPlaceholder('seu@email.com').fill(testUser.email);

    const senhas = await page.getByPlaceholder('••••••••').all();
    await senhas[0].fill(testUser.password);
    await senhas[1].fill(testUser.password);
    await page.getByRole('button', { name: 'Criar conta' }).click();

    await page.waitForURL('/dashboard');

    // Recarregar página
    await page.reload();

    // Verificar que ainda está autenticado
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText(`Olá, ${testUser.name}`)).toBeVisible();
  });

  test('deve exibir indicadores de loading', async ({ page }) => {
    await page.goto('/auth/login');

    // Preencher formulário
    await page.getByPlaceholder('seu@email.com').fill('teste@example.com');
    await page.getByPlaceholder('••••••••').fill('senha123');

    // Clicar em entrar e verificar loading
    const submitButton = page.getByRole('button', { name: 'Entrar' });
    await submitButton.click();

    // Verificar que botão está desabilitado e texto mudou
    await expect(submitButton).toBeDisabled();
    await expect(submitButton).toHaveText('Entrando...');
  });
});
