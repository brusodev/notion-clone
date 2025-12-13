# 🧪 Testes - Notion Clone Frontend

Documentação completa dos testes E2E (End-to-End) usando Playwright.

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Instalação](#instalação)
- [Executando Testes](#executando-testes)
- [Estrutura dos Testes](#estrutura-dos-testes)
- [Testes Implementados](#testes-implementados)
- [Escrevendo Novos Testes](#escrevendo-novos-testes)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

### O que são Testes E2E?

Testes End-to-End (E2E) simulam o comportamento real do usuário, testando o aplicativo completo do início ao fim. Eles garantem que todas as partes do sistema funcionem juntas corretamente.

### Por que Playwright?

- ✅ Multi-browser (Chrome, Firefox, Safari)
- ✅ Rápido e confiável
- ✅ API moderna e fácil de usar
- ✅ Suporte a screenshots e vídeos
- ✅ Debug interativo
- ✅ TypeScript nativo

### Cobertura Atual

- ✅ **15 testes de Autenticação** (auth.spec.ts)
- ✅ **12 testes de Dashboard** (dashboard.spec.ts)
- ✅ **Total**: 27 testes E2E

---

## 📦 Instalação

### 1. Instalar Playwright

```bash
cd frontend

# Instalar Playwright
npm install -D @playwright/test

# Instalar browsers
npx playwright install
```

### 2. Verificar Instalação

```bash
npx playwright --version
```

Deve exibir: `Version 1.49.1` (ou superior)

---

## 🚀 Executando Testes

### Comandos Principais

```bash
# Executar todos os testes (headless)
npm test

# Executar com UI interativa (recomendado)
npm run test:ui

# Executar com browser visível
npm run test:headed

# Executar em modo debug
npm run test:debug

# Executar arquivo específico
npx playwright test tests/e2e/auth.spec.ts

# Executar teste específico
npx playwright test -g "deve criar conta com sucesso"
```

### Opções Avançadas

```bash
# Executar apenas em Chrome
npx playwright test --project=chromium

# Executar em modo paralelo
npx playwright test --workers=4

# Gerar relatório HTML
npx playwright show-report

# Executar com trace
npx playwright test --trace=on
```

---

## 📁 Estrutura dos Testes

```
frontend/tests/
├── e2e/
│   ├── auth.spec.ts         # Testes de autenticação (15 testes)
│   └── dashboard.spec.ts    # Testes de dashboard (12 testes)
└── README.md                # Este arquivo
```

### Convenções

- **Arquivos**: `*.spec.ts`
- **Nomes descritivos**: `deve [ação] [resultado esperado]`
- **Organização**: Por feature/módulo
- **Helpers**: Funções reutilizáveis no topo

---

## 🧪 Testes Implementados

### 1. Autenticação (auth.spec.ts)

**15 testes cobrindo:**

#### Navegação e UI
- ✅ Redirect para login quando não autenticado
- ✅ Exibir página de login corretamente
- ✅ Exibir página de registro corretamente
- ✅ Navegar entre login e registro

#### Validações
- ✅ Validar campos obrigatórios no login
- ✅ Validar formato de email no login
- ✅ Validar senhas coincidentes no registro
- ✅ Validar tamanho mínimo da senha

#### Fluxos Principais
- ✅ Criar conta com sucesso
- ✅ Fazer login com sucesso
- ✅ Exibir erro com credenciais inválidas
- ✅ Fazer logout com sucesso

#### Persistência
- ✅ Manter sessão após reload
- ✅ Exibir indicadores de loading

### 2. Dashboard (dashboard.spec.ts)

**12 testes cobrindo:**

#### Exibição
- ✅ Exibir dashboard após login
- ✅ Exibir mensagem de boas-vindas
- ✅ Exibir lista de features completas
- ✅ Exibir próximos passos
- ✅ Ter header fixo

#### Autenticação e Segurança
- ✅ Proteger rota do dashboard
- ✅ Fazer logout e limpar sessão
- ✅ Manter autenticação após navegação
- ✅ Persistir autenticação após reload

#### UI/UX
- ✅ Exibir nome do usuário corretamente
- ✅ Ter responsividade no header

---

## ✍️ Escrevendo Novos Testes

### Template Básico

```typescript
import { test, expect } from '@playwright/test';

test.describe('Nome da Feature', () => {
  test.beforeEach(async ({ page }) => {
    // Setup - executado antes de cada teste
    await page.goto('/');
  });

  test('deve fazer algo específico', async ({ page }) => {
    // Arrange - preparar
    await page.goto('/rota');

    // Act - executar ação
    await page.getByRole('button', { name: 'Botão' }).click();

    // Assert - verificar resultado
    await expect(page).toHaveURL('/nova-rota');
  });
});
```

### Boas Práticas

#### 1. Use Seletores Semânticos

```typescript
// ✅ BOM - Por role e texto
await page.getByRole('button', { name: 'Entrar' });
await page.getByRole('link', { name: 'Criar conta' });
await page.getByLabel('Email');

// ❌ RUIM - Por classe ou ID
await page.locator('.btn-primary');
await page.locator('#submit-button');
```

#### 2. Use Placeholders para Inputs

```typescript
// ✅ BOM
await page.getByPlaceholder('seu@email.com').fill('teste@test.com');

// ❌ RUIM
await page.locator('input[type="email"]').fill('teste@test.com');
```

#### 3. Aguarde Navegações

```typescript
// ✅ BOM
await page.getByRole('button', { name: 'Enviar' }).click();
await page.waitForURL('/success');
await expect(page).toHaveURL('/success');

// ❌ RUIM
await page.getByRole('button', { name: 'Enviar' }).click();
// Sem aguardar navegação
```

#### 4. Use Timeouts Adequados

```typescript
// ✅ BOM - Timeout explícito para operações lentas
await expect(page.getByText('Carregando...')).toBeVisible({ timeout: 10000 });

// ✅ BOM - Aguardar elemento aparecer
await page.getByText('Sucesso').waitFor({ state: 'visible' });
```

#### 5. Limpe Estado Entre Testes

```typescript
test.beforeEach(async ({ page }) => {
  // Limpar localStorage
  await page.goto('/');
  await page.evaluate(() => localStorage.clear());
});
```

### Helpers Úteis

```typescript
// Helper para login
async function loginUser(page: any, email: string, password: string) {
  await page.goto('/auth/login');
  await page.getByPlaceholder('seu@email.com').fill(email);
  await page.getByPlaceholder('••••••••').fill(password);
  await page.getByRole('button', { name: 'Entrar' }).click();
  await page.waitForURL('/dashboard');
}

// Helper para criar usuário de teste
function createTestUser() {
  return {
    email: `test${Date.now()}@example.com`,
    password: 'Test123456',
    fullName: 'Test User'
  };
}
```

---

## 🐛 Troubleshooting

### Problema: Testes falhando localmente

**Solução 1 - Backend não está rodando:**
```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev

# Terminal 3 - Testes
cd frontend
npm test
```

**Solução 2 - Limpar estado:**
```bash
# Limpar banco de dados de teste
cd backend
rm notion_clone.db
alembic upgrade head
```

### Problema: Timeouts

**Erro:**
```
Test timeout of 30000ms exceeded
```

**Solução:**
```typescript
// Aumentar timeout do teste
test('teste lento', async ({ page }) => {
  test.setTimeout(60000); // 60 segundos

  // ... resto do teste
});
```

### Problema: Seletores não encontrados

**Erro:**
```
locator.click: Target closed
```

**Solução:**
```typescript
// Aguardar elemento estar visível
await page.getByRole('button', { name: 'Botão' }).waitFor({ state: 'visible' });
await page.getByRole('button', { name: 'Botão' }).click();
```

### Problema: Screenshots não sendo capturados

**Solução:**
```bash
# Executar com screenshot sempre
npx playwright test --screenshot=on

# Executar com trace sempre
npx playwright test --trace=on
```

### Problema: Browsers não instalados

**Erro:**
```
browserType.launch: Executable doesn't exist
```

**Solução:**
```bash
npx playwright install
```

---

## 📊 Relatórios

### Gerar Relatório HTML

```bash
# Executar testes e gerar relatório
npm test

# Abrir relatório
npx playwright show-report
```

### Ver Screenshots e Traces

Após executar os testes, você pode ver:
- **Screenshots**: `test-results/*/test-failed-1.png`
- **Traces**: Abrir no Trace Viewer

```bash
# Abrir trace específico
npx playwright show-trace test-results/*/trace.zip
```

---

## 🔧 Configuração (playwright.config.ts)

```typescript
export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## 📚 Recursos

- [Playwright Docs](https://playwright.dev/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)
- [Selectors Guide](https://playwright.dev/docs/selectors)
- [Assertions Guide](https://playwright.dev/docs/test-assertions)

---

## ✅ Checklist para Novos Testes

Antes de commitar um novo teste, verifique:

- [ ] Teste tem nome descritivo
- [ ] Usa seletores semânticos (getByRole, getByPlaceholder)
- [ ] Limpa estado (localStorage, cookies) se necessário
- [ ] Aguarda navegações com waitForURL
- [ ] Usa timeouts adequados
- [ ] Não usa sleeps (await page.waitForTimeout)
- [ ] Testa happy path E edge cases
- [ ] Passa localmente em todos os browsers
- [ ] Documentado se for helper/utility

---

**Testes escritos, código confiável! 🚀**
