# 📦 Guia de Instalação - Frontend

Este guia detalha como instalar e configurar o frontend do Notion Clone.

---

## 📋 Pré-requisitos

- **Node.js**: 18.0.0 ou superior
- **npm**: 9.0.0 ou superior (vem com Node.js)
- **Backend**: API rodando em http://localhost:8000

### Verificar versões instaladas:

```bash
node --version    # v18.0.0 ou superior
npm --version     # 9.0.0 ou superior
```

---

## 🚀 Instalação Passo a Passo

### 1. Navegar para a pasta frontend

```bash
cd notion-clone/frontend
```

### 2. Instalar dependências

```bash
npm install
```

**Isso vai instalar todas as dependências do `package.json`:**

#### Core (5 pacotes)
- next@^14.2.18
- react@^18.3.1
- react-dom@^18.3.1
- typescript@^5
- eslint-config-next@^14.2.18

#### State & Data (3 pacotes)
- zustand@^5.0.2
- @tanstack/react-query@^5.62.11
- axios@^1.7.2

#### UI & Styling (15+ pacotes)
- tailwindcss@^3.4.1
- tailwindcss-animate@^1.0.7
- next-themes@^0.4.4
- lucide-react@^0.469.0
- framer-motion@^11.15.0
- clsx@^2.1.1
- tailwind-merge@^2.5.5
- class-variance-authority@^0.7.1

#### Radix UI Components (9 pacotes)
- @radix-ui/react-slot
- @radix-ui/react-dialog
- @radix-ui/react-dropdown-menu
- @radix-ui/react-avatar
- @radix-ui/react-label
- @radix-ui/react-popover
- @radix-ui/react-select
- @radix-ui/react-separator
- @radix-ui/react-tabs
- @radix-ui/react-toast
- @radix-ui/react-tooltip

#### Forms & Validation (3 pacotes)
- react-hook-form@^7.54.0
- @hookform/resolvers@^3.9.1
- zod@^3.24.1

#### Editor (3 pacotes)
- @tiptap/react@^2.10.3
- @tiptap/starter-kit@^2.10.3
- @tiptap/extension-placeholder@^2.10.3

#### Utils (2 pacotes)
- date-fns@^4.1.0

---

### 3. Configurar variáveis de ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env.local

# Editar .env.local (pode usar notepad ou seu editor preferido)
notepad .env.local  # Windows
nano .env.local     # Linux/Mac
```

**Conteúdo do `.env.local`:**

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_V1=/api/v1

# App Configuration
NEXT_PUBLIC_APP_NAME=Notion Clone
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**⚠️ Importante**:
- O backend deve estar rodando em `http://localhost:8000`
- Se o backend estiver em outra porta, atualize `NEXT_PUBLIC_API_URL`

---

### 4. Iniciar servidor de desenvolvimento

```bash
npm run dev
```

**Servidor rodando em:**
- Frontend: http://localhost:3000
- Auto-reload: Habilitado

---

## ✅ Verificar Instalação

### 1. Abrir navegador

Acesse: http://localhost:3000

**Você deve ver:**
- Redirect automático para `/auth/login`
- Página de login funcionando

### 2. Criar conta

- Clique em "Criar conta"
- Preencha: nome, email, senha
- Após registro → redirect para `/dashboard`

### 3. Dashboard

**Você deve ver:**
- Header com "Olá, [seu nome]"
- Botão de "Sair"
- Mensagem de setup completo

---

## 🔧 Comandos Úteis

### Desenvolvimento

```bash
# Rodar em modo dev (hot reload)
npm run dev

# Rodar em porta diferente
npm run dev -- -p 3001
```

### Build & Produção

```bash
# Build para produção
npm run build

# Rodar build de produção
npm start

# Preview do build
npm run build && npm start
```

### Qualidade de Código

```bash
# Lint (ESLint)
npm run lint

# Type check (TypeScript)
npm run type-check

# Formatar código (se tiver Prettier configurado)
npm run format
```

### Limpeza

```bash
# Limpar cache do Next.js
rm -rf .next

# Reinstalar dependências
rm -rf node_modules
rm package-lock.json
npm install

# Limpar tudo (Windows)
rmdir /s /q .next node_modules
del package-lock.json
npm install
```

---

## 📁 Estrutura Após Instalação

```
frontend/
├── node_modules/           # ✅ Dependências instaladas
├── .next/                  # ✅ Build do Next.js (após npm run dev)
├── src/                    # Código fonte
├── public/                 # Assets estáticos
├── .env.local             # ✅ Variáveis de ambiente (criado por você)
├── package.json
├── package-lock.json      # ✅ Lock de versões
├── next.config.js
├── tsconfig.json
└── tailwind.config.ts
```

---

## 🐛 Troubleshooting

### Problema: `npm install` falha

**Erro comum:**
```
npm ERR! code ERESOLVE
npm ERR! ERESOLVE could not resolve
```

**Solução 1 - Forçar instalação:**
```bash
npm install --legacy-peer-deps
```

**Solução 2 - Limpar cache:**
```bash
npm cache clean --force
npm install
```

**Solução 3 - Usar versões exatas:**
```bash
rm package-lock.json
npm install
```

---

### Problema: Porta 3000 já em uso

**Erro:**
```
Port 3000 is already in use
```

**Solução 1 - Usar outra porta:**
```bash
npm run dev -- -p 3001
```

**Solução 2 - Matar processo (Windows):**
```bash
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**Solução 3 - Matar processo (Linux/Mac):**
```bash
lsof -ti:3000 | xargs kill -9
```

---

### Problema: Backend não conecta

**Erro no console:**
```
Network Error
AxiosError: connect ECONNREFUSED 127.0.0.1:8000
```

**Verificações:**

1. **Backend está rodando?**
```bash
cd backend
uvicorn app.main:app --reload
```

2. **URL correta no .env.local?**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000  # ✅ Correto
# NEXT_PUBLIC_API_URL=http://localhost:3000  # ❌ Errado
```

3. **CORS configurado no backend?**
Backend `.env` deve ter:
```env
ALLOWED_ORIGINS=["http://localhost:3000"]
```

---

### Problema: TypeScript errors

**Erro:**
```
Type error: Cannot find module '@/components/ui/button'
```

**Solução:**
```bash
# Verificar se paths estão corretos no tsconfig.json
# Deve ter:
"paths": {
  "@/*": ["./src/*"]
}

# Reiniciar TypeScript server (VSCode)
Ctrl+Shift+P > TypeScript: Restart TS Server
```

---

### Problema: Tema dark não funciona

**Solução:**
1. Verificar se `next-themes` está instalado:
```bash
npm list next-themes
```

2. Verificar se `ThemeProvider` está no `layout.tsx`

3. Limpar localStorage:
```javascript
localStorage.clear()
```

---

## 🔄 Atualizar Dependências

### Verificar atualizações disponíveis

```bash
npm outdated
```

### Atualizar todas para latest minor

```bash
npm update
```

### Atualizar para latest major (cuidado!)

```bash
npm install <pacote>@latest
```

**Exemplo:**
```bash
npm install next@latest
npm install react@latest react-dom@latest
```

---

## 📦 Adicionar Novas Dependências

### Processo

1. Instalar o pacote
2. Usar no código
3. Commitar `package.json` e `package-lock.json`

**Exemplo - Adicionar biblioteca de datas:**

```bash
# Instalar
npm install date-fns

# Usar no código
import { format } from 'date-fns'

# Commitar
git add package.json package-lock.json
git commit -m "feat: add date-fns"
```

---

## ✅ Checklist de Verificação

Antes de começar a desenvolver:

- [ ] Node.js 18+ instalado
- [ ] npm 9+ instalado
- [ ] Backend rodando em http://localhost:8000
- [ ] Dependências instaladas (`node_modules/` existe)
- [ ] Arquivo `.env.local` configurado
- [ ] Servidor dev rodando (`npm run dev`)
- [ ] Frontend acessível em http://localhost:3000
- [ ] Login funcionando
- [ ] Dashboard acessível após login

---

## 📚 Próximos Passos

Após instalação bem-sucedida:

1. **Explorar o código** - Veja a estrutura em `src/`
2. **Testar autenticação** - Login, register, logout
3. **Ler FRONTEND_PLAN.md** - Plano de desenvolvimento completo
4. **Começar desenvolvimento** - Implementar próximas features

---

**Pronto! Seu ambiente frontend está configurado! 🚀**

Para dúvidas ou problemas, consulte:
- [README.md](README.md) - Documentação geral
- [FRONTEND_PLAN.md](../FRONTEND_PLAN.md) - Plano de desenvolvimento
