# 🎨 Notion Clone - Frontend

> Interface moderna e responsiva construída com Next.js 14, TypeScript e Tailwind CSS

## 🚀 Status do Projeto

**Fase 1: Setup Inicial** ✅ **Completo**

- ✅ Next.js 14 com App Router e TypeScript
- ✅ Tailwind CSS configurado com tema dark/light
- ✅ Shadcn/ui components
- ✅ Zustand para state management
- ✅ React Query para data fetching
- ✅ Axios API client com interceptors
- ✅ Sistema de autenticação (login/register)
- ✅ Proteção de rotas
- ✅ Refresh token automático

## 📦 Stack Tecnológica

### Core
- **Next.js 14** - Framework React com App Router
- **TypeScript** - Tipagem estática
- **Tailwind CSS** - Estilização
- **Shadcn/ui** - Componentes UI

### State & Data
- **Zustand** - State management global
- **React Query** - Server state e caching
- **Axios** - HTTP client

### UI Components
- **Radix UI** - Componentes acessíveis
- **Lucide React** - Ícones
- **Framer Motion** - Animações (planejado)

### Editor (Próximo)
- **TipTap** - Editor de blocos rico
- **React Hook Form** - Formulários
- **Zod** - Validação de schemas

## 📁 Estrutura do Projeto

```
frontend/
├── src/
│   ├── app/                  # Next.js App Router
│   │   ├── auth/            # Páginas de autenticação
│   │   │   ├── login/       # Login page
│   │   │   └── register/    # Register page
│   │   ├── dashboard/       # Dashboard (protected)
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Home (redirect)
│   │   └── globals.css      # Estilos globais
│   │
│   ├── components/          # Componentes React
│   │   ├── ui/             # Componentes base (Shadcn)
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   └── label.tsx
│   │   └── providers.tsx   # React Query & Theme providers
│   │
│   ├── stores/             # Zustand stores
│   │   ├── auth-store.ts   # Auth state
│   │   └── workspace-store.ts # Workspace state
│   │
│   ├── services/           # API services
│   │   └── auth.service.ts # Auth endpoints
│   │
│   ├── lib/                # Utilities
│   │   ├── api-client.ts   # Axios instance
│   │   └── utils.ts        # Helper functions
│   │
│   ├── types/              # TypeScript types
│   │   └── index.ts        # Type definitions
│   │
│   └── hooks/              # Custom hooks (próximo)
│
├── public/                 # Assets estáticos
├── .env.local             # Environment variables
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## 🛠️ Setup & Instalação

### Pré-requisitos
- Node.js 18+
- npm ou yarn
- Backend rodando em http://localhost:8000

### Instalação

```bash
# Ir para pasta frontend
cd frontend

# Instalar dependências
npm install

# Copiar arquivo de ambiente
cp .env.example .env.local

# Editar .env.local se necessário
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Rodar em desenvolvimento
npm run dev
```

A aplicação estará rodando em **http://localhost:3000**

## 🔧 Scripts Disponíveis

```bash
# Desenvolvimento (com hot reload)
npm run dev

# Build para produção
npm run build

# Rodar build de produção
npm start

# Lint
npm run lint

# Type check
npm run type-check
```

## 🔐 Autenticação

### Fluxo de Auth

1. **Login/Register** - Usuário faz login ou cria conta
2. **Tokens** - API retorna `access_token` e `refresh_token`
3. **Storage** - Tokens salvos no localStorage via Zustand persist
4. **Auto-refresh** - Axios interceptor renova token automaticamente
5. **Logout** - Limpa tokens e redireciona para login

### Stores

**Auth Store** (`auth-store.ts`)
```typescript
{
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: () => boolean
  setAuth: (data: AuthResponse) => void
  setTokens: (access, refresh) => void
  updateUser: (user: Partial<User>) => void
  logout: () => void
}
```

**Workspace Store** (`workspace-store.ts`)
```typescript
{
  currentWorkspace: Workspace | null
  workspaces: Workspace[]
  setCurrentWorkspace: (workspace) => void
  setWorkspaces: (workspaces) => void
  addWorkspace: (workspace) => void
  updateWorkspace: (id, data) => void
  removeWorkspace: (id) => void
}
```

## 🎨 Temas (Dark/Light)

O projeto suporta temas dark e light usando `next-themes`:

```typescript
import { useTheme } from "next-themes"

// Em qualquer componente
const { theme, setTheme } = useTheme()

// Alternar tema
setTheme(theme === 'dark' ? 'light' : 'dark')
```

## 📡 API Client

O API client (`lib/api-client.ts`) tem:

- ✅ Base URL configurável via env
- ✅ Timeout de 30s
- ✅ Auto-inject de Bearer token
- ✅ Auto-refresh de token expirado
- ✅ Redirect para login se refresh falhar
- ✅ Tratamento de erros

### Exemplo de uso:

```typescript
import apiClient from "@/lib/api-client"

// GET
const pages = await apiClient.get("/pages")

// POST
const newPage = await apiClient.post("/pages", {
  title: "Nova Página",
  workspace_id: "123"
})

// PATCH
await apiClient.patch(`/pages/${id}`, { title: "Updated" })

// DELETE
await apiClient.delete(`/pages/${id}`)
```

## 🧩 Componentes UI (Shadcn)

Componentes já implementados:

- ✅ `Button` - Botão com variants
- ✅ `Input` - Input de texto
- ✅ `Label` - Label de formulário

**Próximos componentes a adicionar:**
- [ ] `Dialog` - Modal
- [ ] `DropdownMenu` - Menu dropdown
- [ ] `Avatar` - Avatar de usuário
- [ ] `Tooltip` - Tooltip
- [ ] `Select` - Select dropdown
- [ ] `Tabs` - Tabs
- [ ] `Toast` - Notificações

## 🗺️ Roadmap Frontend

### ✅ Fase 1: Setup (Completo)
- ✅ Configuração inicial
- ✅ Autenticação
- ✅ Dashboard básico

### 🔄 Fase 2: Core Features (Próximo)
- [ ] Sidebar com workspaces
- [ ] Lista de páginas
- [ ] Criação de páginas
- [ ] Árvore hierárquica
- [ ] Editor de blocos (TipTap)

### 🚀 Fase 3: Features Avançadas
- [ ] Comentários
- [ ] Tags e favoritos
- [ ] Busca global (Cmd+K)
- [ ] Drag & drop
- [ ] Upload de imagens

### 🎯 Fase 4: Polish
- [ ] Animações (Framer Motion)
- [ ] Modo offline
- [ ] PWA
- [ ] Testes (Vitest + Playwright)

## 🐛 Troubleshooting

### Problema: Erro de CORS
**Solução**: Verifique se o backend está rodando e se `ALLOWED_ORIGINS` no backend inclui `http://localhost:3000`

### Problema: "Module not found"
**Solução**:
```bash
rm -rf node_modules
rm package-lock.json
npm install
```

### Problema: Redirect loop no login
**Solução**: Limpe o localStorage:
```javascript
localStorage.clear()
```

### Problema: Token expirado
**Solução**: O sistema deve renovar automaticamente. Se não funcionar, faça logout e login novamente.

## 📚 Recursos

- [Next.js Docs](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Shadcn/ui](https://ui.shadcn.com/)
- [Zustand](https://docs.pmnd.rs/zustand)
- [React Query](https://tanstack.com/query/latest)

## 🤝 Contribuindo

1. Crie uma branch para sua feature
2. Faça commit das mudanças
3. Abra um Pull Request

## 📝 Convenções

### Commits
- `feat:` Nova feature
- `fix:` Correção de bug
- `style:` Mudanças de estilo
- `refactor:` Refatoração
- `docs:` Documentação

### Componentes
- Use `"use client"` para componentes com estado
- TypeScript estrito (sem `any`)
- Shadcn/ui para componentes base

---

**Desenvolvido com ❤️ usando Next.js 14 e TypeScript**
