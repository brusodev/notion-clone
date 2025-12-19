# 🧪 Testes Automatizados - Notion Clone

## Testes Backend (API)

### Executar Teste de Registro

O teste automatizado `test_registration.py` valida todo o fluxo de autenticação:

1. **Health Check** - Verifica se a API está rodando
2. **Registro** - Cria um novo usuário com workspace pessoal
3. **Login** - Autentica o usuário criado
4. **Get Current User** - Valida o token e recupera dados do usuário

#### Como Executar

```bash
# Certifique-se que o backend está rodando
cd backend
uvicorn app.main:app --reload

# Em outro terminal, execute o teste
python test_registration.py
```

#### Saída Esperada

```
============================================================
NOTION CLONE API - REGISTRATION TEST SUITE
============================================================

ℹ Timestamp: 2025-12-15 12:00:00
ℹ API URL: http://localhost:8000/api/v1

============================================================
1. Testing API Health Check
============================================================

✓ API is running: {'status': 'healthy', 'version': '1.0.0', ...}

============================================================
2. Testing User Registration
============================================================

✓ Registration successful!
  - Access Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  - Refresh Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  - User ID: 550e8400-e29b-41d4-a716-446655440000

============================================================
3. Testing User Login
============================================================

✓ Login successful!

============================================================
4. Testing Get Current User
============================================================

✓ Current user retrieved successfully!

============================================================
TEST SUMMARY
============================================================

✓ All tests passed! ✓
```

---

## Testes Frontend (UI)

### Executar Testes Playwright

Os testes `tests/auth.spec.ts` validam:

- Exibição correta do formulário
- Validações de cliente (senha curta, senhas não coincidem)
- Registro bem-sucedido
- Detecção de email duplicado
- Navegação entre páginas

#### Como Executar

```bash
# Certifique-se que frontend e backend estão rodando
cd frontend
npm run dev

# Em outro terminal, execute os testes
npm run test

# Ou use o modo UI interativo
npm run test:ui
```

#### Opções Úteis

```bash
# Rodar apenas testes de autenticação
npm run test -- auth.spec.ts

# Rodar com navegador visível
npm run test:headed

# Modo debug (pausável)
npm run test:debug

# Gerar relatório em HTML
npm run test && npx playwright show-report
```

---

## Problemas Comuns

### Erro: "Cannot connect to API"
- Certifique-se que o backend está rodando em `http://localhost:8000`
- Execute: `uvicorn app.main:app --reload` no diretório `backend`

### Erro: "Connection refused" no teste do frontend
- Certifique-se que o frontend está rodando em `http://localhost:3000`
- Execute: `npm run dev` no diretório `frontend`

### Erro: "Email already registered"
- O teste gera emails únicos com timestamp
- Se receber erro de email duplicado, espere alguns segundos e tente novamente
- Ou mude manualmente o email no teste

### Erro 422 (Unprocessable Entity)
- Verifique se a senha tem **pelo menos 8 caracteres**
- Valide o formato do email
- Verifique se todos os campos obrigatórios estão preenchidos

---

## Validações Implementadas

| Campo | Validação | Mensagem |
|-------|-----------|----------|
| **Email** | Formato válido | `Invalid email format` |
| **Nome** | 1-100 caracteres | `Ensure this value has at least 1 characters` |
| **Senha** | Mínimo 8 caracteres | `Ensure this value has at least 8 characters` |
| **Confirmação** | Deve coincidir | `As senhas não coincidem` |
| **Email Duplicado** | Único no banco | `Email already registered` |

---

## Fluxo de Registro Completo

```
┌─────────────────────────────┐
│  Preencher Formulário       │
│  - Nome                     │
│  - Email                    │
│  - Senha (8+ caracteres)    │
│  - Confirmar Senha          │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Validações do Cliente      │
│  ✓ Senhas coincidem?        │
│  ✓ Senha tem 8+ chars?      │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  POST /auth/register        │
│  (enviar ao backend)        │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Validações do Backend      │
│  ✓ Email válido?            │
│  ✓ Email não existe?        │
│  ✓ Criar usuário            │
│  ✓ Criar workspace pessoal  │
│  ✓ Gerar tokens JWT         │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Armazenar Tokens (Zustand) │
│  - access_token             │
│  - refresh_token            │
│  - user data                │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Redirecionar para          │
│  /dashboard                 │
└─────────────────────────────┘
```

---

## Resumo das Correções

✅ **Validação de Senha**: Aumentada de 6 para 8 caracteres (conforme backend)
✅ **CORS Configurado**: Requests do frontend agora são aceitas
✅ **Error Handling**: Mensagens de erro claras no frontend e backend
✅ **Logging**: Backend loga todas as etapas do processo
✅ **Timeouts**: Request timeouts configurados para 30s

---

## Próximos Passos

Após validar que o registro está funcionando:

1. **Login** - Testar autenticação com email/senha
2. **Dashboard** - Implementar a navegação principal
3. **Editor** - Começar a trabalhar no editor de blocos
4. **Sidebar** - Integrar a sidebar com dados reais do banco

