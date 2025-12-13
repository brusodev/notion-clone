# 🎨 Plano de Implementação do Frontend - Notion Clone

**Data de início**: 13/12/2024
**Stack**: Next.js 14 + TypeScript + Tailwind CSS + Shadcn/ui
**Duração estimada**: 6-8 semanas

---

## 📋 Visão Geral

Criar um frontend moderno e responsivo que replique a experiência do Notion, incluindo:
- Editor de blocos intuitivo
- Navegação hierárquica de páginas
- Sistema de workspaces
- Colaboração (comentários, tags, favoritos)
- Interface limpa e minimalista

---

## 🏗️ Arquitetura do Projeto

### Estrutura de Diretórios

```
frontend/
├── app/                          # Next.js 14 App Router
│   ├── (auth)/                   # Rotas de autenticação
│   │   ├── login/
│   │   └── register/
│   ├── (dashboard)/              # Rotas protegidas
│   │   ├── layout.tsx           # Layout com sidebar
│   │   ├── page.tsx             # Dashboard home
│   │   └── [workspaceId]/
│   │       ├── page.tsx         # Workspace home
│   │       └── [pageId]/
│   │           └── page.tsx     # Editor de página
│   ├── layout.tsx               # Root layout
│   └── globals.css
├── components/
│   ├── ui/                      # Shadcn/ui components
│   ├── editor/                  # Editor de blocos
│   │   ├── BlockEditor.tsx
│   │   ├── blocks/
│   │   │   ├── ParagraphBlock.tsx
│   │   │   ├── HeadingBlock.tsx
│   │   │   ├── ListBlock.tsx
│   │   │   └── CodeBlock.tsx
│   │   └── BlockMenu.tsx
│   ├── sidebar/
│   │   ├── Sidebar.tsx
│   │   ├── PageTree.tsx
│   │   ├── WorkspaceSwitcher.tsx
│   │   └── FavoritesList.tsx
│   ├── page/
│   │   ├── PageHeader.tsx
│   │   ├── PageCover.tsx
│   │   └── PageIcon.tsx
│   └── shared/
│       ├── CommandPalette.tsx
│       ├── SearchBar.tsx
│       └── ThemeToggle.tsx
├── lib/
│   ├── api/                     # API client
│   │   ├── client.ts
│   │   ├── auth.ts
│   │   ├── workspaces.ts
│   │   ├── pages.ts
│   │   └── blocks.ts
│   ├── hooks/                   # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useWorkspace.ts
│   │   └── usePage.ts
│   ├── store/                   # Zustand stores
│   │   ├── authStore.ts
│   │   ├── workspaceStore.ts
│   │   └── editorStore.ts
│   └── utils/
│       ├── cn.ts
│       └── formatters.ts
├── types/
│   ├── api.ts
│   ├── workspace.ts
│   ├── page.ts
│   └── block.ts
└── public/
```

---

## 🎯 Fases de Implementação

## Fase 1: Setup e Fundação (Semana 1)

### 1.1 Setup Inicial
- [ ] Criar projeto Next.js 14 com App Router
- [ ] Configurar TypeScript (strict mode)
- [ ] Setup Tailwind CSS
- [ ] Instalar e configurar Shadcn/ui
- [ ] Configurar ESLint + Prettier
- [ ] Setup de variáveis de ambiente

**Comandos:**
```bash
# Criar projeto
npx create-next-app@latest frontend --typescript --tailwind --app --eslint

# Instalar dependências
npm install zustand @tanstack/react-query axios
npm install lucide-react date-fns clsx tailwind-merge
npm install @radix-ui/react-dropdown-menu
npm install @radix-ui/react-dialog
npm install @radix-ui/react-popover

# Shadcn/ui
npx shadcn-ui@latest init
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add toast
```

### 1.2 Configuração da API Client
- [ ] Criar axios client configurado
- [ ] Interceptors para JWT tokens
- [ ] Refresh token automático
- [ ] Error handling global
- [ ] Types para responses da API

**Arquivo: `lib/api/client.ts`**
```typescript
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor para adicionar token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor para refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Implementar refresh token logic
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 1.3 State Management
- [ ] Setup Zustand stores
- [ ] Auth store (user, tokens)
- [ ] Workspace store
- [ ] Editor store (current page, blocks)

**Arquivo: `lib/store/authStore.ts`**
```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  name: string;
  avatar_url?: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  setAuth: (user: User, accessToken: string, refreshToken: string) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      setAuth: (user, accessToken, refreshToken) =>
        set({ user, accessToken, refreshToken }),
      logout: () => set({ user: null, accessToken: null, refreshToken: null }),
      isAuthenticated: () => !!get().accessToken,
    }),
    {
      name: 'auth-storage',
    }
  )
);
```

---

## Fase 2: Autenticação e Layout (Semana 1-2)

### 2.1 Páginas de Autenticação
- [ ] Página de Login (`app/(auth)/login/page.tsx`)
- [ ] Página de Registro (`app/(auth)/register/page.tsx`)
- [ ] Formulários com validação
- [ ] Feedback de erros
- [ ] Loading states

**Features:**
- Email/senha
- Validação client-side
- Mensagens de erro claras
- Redirect após login

### 2.2 Proteção de Rotas
- [ ] Middleware para autenticação
- [ ] Higher-Order Component para rotas protegidas
- [ ] Redirect para login se não autenticado
- [ ] Persist de redirect destination

**Arquivo: `middleware.ts`**
```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token');

  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: '/dashboard/:path*',
};
```

### 2.3 Layout Principal
- [ ] Root layout com providers
- [ ] Dashboard layout com sidebar
- [ ] Header com user menu
- [ ] Sidebar colapsável
- [ ] Responsivo (mobile-first)

**Componentes:**
- `DashboardLayout` - Container principal
- `Sidebar` - Navegação lateral
- `Header` - Barra superior
- `UserMenu` - Dropdown do usuário

---

## Fase 3: Workspaces e Navegação (Semana 2)

### 3.1 Workspace Switcher
- [ ] Dropdown para trocar workspace
- [ ] Listar workspaces do usuário
- [ ] Criar novo workspace
- [ ] Ícone e nome do workspace

**Componente: `WorkspaceSwitcher.tsx`**
```typescript
'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ChevronDown, Plus } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export function WorkspaceSwitcher() {
  const { data: workspaces } = useQuery({
    queryKey: ['workspaces'],
    queryFn: fetchWorkspaces,
  });

  return (
    <DropdownMenu>
      <DropdownMenuTrigger>
        <div className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded">
          <span>My Workspace</span>
          <ChevronDown size={16} />
        </div>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        {workspaces?.map((ws) => (
          <DropdownMenuItem key={ws.id}>{ws.name}</DropdownMenuItem>
        ))}
        <DropdownMenuItem>
          <Plus size={16} /> New Workspace
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
```

### 3.2 Sidebar com Páginas
- [ ] Lista de páginas do workspace
- [ ] Estrutura hierárquica (tree view)
- [ ] Expand/collapse páginas
- [ ] Criar nova página (botão +)
- [ ] Favoritos no topo

**Funcionalidades:**
- Drag & drop para reorganizar (fase futura)
- Context menu (right-click)
- Ícones de página
- Indicador de página ativa

### 3.3 Command Palette (Cmd+K)
- [ ] Busca global
- [ ] Criar nova página
- [ ] Navegar entre páginas
- [ ] Ações rápidas
- [ ] Keyboard navigation

**Atalhos:**
- `Cmd/Ctrl + K` - Abrir command palette
- `/` - Comandos de bloco
- `Cmd/Ctrl + P` - Buscar páginas

---

## Fase 4: Editor de Páginas (Semana 3-4)

### 4.1 Estrutura do Editor
- [ ] Componente principal `BlockEditor`
- [ ] Sistema de blocos modular
- [ ] Renderização dinâmica por tipo
- [ ] Focus management
- [ ] Keyboard navigation

**Tecnologia do Editor:**

**Opção Recomendada: TipTap**
- Baseado em ProseMirror
- API simples e intuitiva
- Extensível
- TypeScript nativo
- Comunidade ativa

```bash
npm install @tiptap/react @tiptap/starter-kit
npm install @tiptap/extension-placeholder
npm install @tiptap/extension-typography
```

### 4.2 Tipos de Blocos Básicos

#### 4.2.1 Paragraph Block
- [ ] Texto simples
- [ ] Formatação inline (bold, italic, underline)
- [ ] Links
- [ ] Placeholder

#### 4.2.2 Heading Blocks (H1, H2, H3)
- [ ] Três níveis de headings
- [ ] Atalhos: `#`, `##`, `###`
- [ ] Auto-formatting

#### 4.2.3 List Blocks
- [ ] Bullet list (atalho: `-` ou `*`)
- [ ] Numbered list (atalho: `1.`)
- [ ] Checkbox list (atalho: `[]`)
- [ ] Indentação com Tab

#### 4.2.4 Code Block
- [ ] Syntax highlighting
- [ ] Seleção de linguagem
- [ ] Copy button
- [ ] Line numbers (opcional)

**Libs sugeridas:**
```bash
npm install @tiptap/extension-code-block-lowlight
npm install lowlight
```

#### 4.2.5 Quote Block
- [ ] Blockquote styling
- [ ] Atalho: `>`

#### 4.2.6 Divider
- [ ] Linha horizontal
- [ ] Atalho: `---`

### 4.3 Block Menu (Slash Commands)
- [ ] Trigger com `/`
- [ ] Filtrar por texto
- [ ] Keyboard navigation (arrows)
- [ ] Enter para selecionar
- [ ] Preview de blocos

**UI:**
```typescript
const blockTypes = [
  { id: 'paragraph', label: 'Text', icon: Type, shortcut: 'Just start typing' },
  { id: 'heading1', label: 'Heading 1', icon: Heading1, shortcut: '#' },
  { id: 'heading2', label: 'Heading 2', icon: Heading2, shortcut: '##' },
  { id: 'heading3', label: 'Heading 3', icon: Heading3, shortcut: '###' },
  { id: 'bulletList', label: 'Bullet List', icon: List, shortcut: '-' },
  { id: 'numberedList', label: 'Numbered List', icon: ListOrdered, shortcut: '1.' },
  { id: 'code', label: 'Code', icon: Code, shortcut: '```' },
  { id: 'quote', label: 'Quote', icon: Quote, shortcut: '>' },
  { id: 'divider', label: 'Divider', icon: Minus, shortcut: '---' },
];
```

### 4.4 Page Header
- [ ] Título da página (editable)
- [ ] Ícone da página (emoji picker)
- [ ] Cover image
- [ ] Breadcrumbs
- [ ] Ações (share, favorite, etc)

### 4.5 Salvamento Automático
- [ ] Debounce de 500ms
- [ ] Indicador de "Saving..." / "Saved"
- [ ] Retry em caso de erro
- [ ] Queue de mudanças

**Implementação:**
```typescript
const debouncedSave = useMemo(
  () => debounce(async (content) => {
    setSaving(true);
    try {
      await updatePage(pageId, { content });
      setSaved(true);
    } catch (error) {
      setError('Failed to save');
    } finally {
      setSaving(false);
    }
  }, 500),
  [pageId]
);
```

---

## Fase 5: Árvore de Páginas (Semana 4)

### 5.1 Page Tree Component
- [ ] Hierarquia visual com indentação
- [ ] Expand/collapse folders
- [ ] Lazy loading de children
- [ ] Skeleton loading

**Biblioteca recomendada:**
```bash
npm install react-arborist
# ou implementar manualmente com recursão
```

### 5.2 Interações
- [ ] Click para navegar
- [ ] Hover para mostrar actions
- [ ] Context menu (right-click)
- [ ] Drag & drop para reorganizar (fase futura)

### 5.3 Ações de Página
- [ ] Adicionar subpágina
- [ ] Duplicar página
- [ ] Mover para lixeira
- [ ] Restaurar da lixeira
- [ ] Deletar permanentemente
- [ ] Copiar link

---

## Fase 6: Comentários e Colaboração (Semana 5)

### 6.1 Sistema de Comentários
- [ ] Thread de comentários
- [ ] Comentar em bloco específico
- [ ] Reply to comments
- [ ] Editar/deletar comentário
- [ ] Resolve comment

### 6.2 Tags
- [ ] Adicionar tags à página
- [ ] Color picker
- [ ] Filtrar por tag
- [ ] Gerenciar tags do workspace

### 6.3 Favoritos
- [ ] Estrela para favoritar
- [ ] Lista de favoritos na sidebar
- [ ] Quick access

---

## Fase 7: Busca e Navegação (Semana 6)

### 7.1 Busca Global
- [ ] Command palette integrada
- [ ] Busca em tempo real
- [ ] Highlight de resultados
- [ ] Filtros (workspace, tag, data)
- [ ] Keyboard shortcuts

**Biblioteca:**
```bash
npm install cmdk
```

### 7.2 Busca em Página
- [ ] Ctrl+F para buscar
- [ ] Highlight de matches
- [ ] Navegação entre resultados
- [ ] Replace (opcional)

---

## Fase 8: Temas e Polish (Semana 7)

### 8.1 Dark Mode
- [ ] Toggle dark/light
- [ ] Persistir preferência
- [ ] Smooth transition
- [ ] Sistema de cores consistente

**Implementação com Next.js:**
```bash
npm install next-themes
```

### 8.2 Responsividade
- [ ] Mobile layout
- [ ] Tablet layout
- [ ] Sidebar colapsável
- [ ] Touch gestures
- [ ] Bottom navigation (mobile)

### 8.3 Atalhos de Teclado
- [ ] Documentação de atalhos
- [ ] Modal de ajuda (`?`)
- [ ] Vim mode (opcional)

### 8.4 Animações
- [ ] Framer Motion para transições
- [ ] Page transitions
- [ ] Loading skeletons
- [ ] Micro-interactions

```bash
npm install framer-motion
```

---

## Fase 9: Features Extras (Semana 8)

### 9.1 Cover e Ícones
- [ ] Upload de cover image
- [ ] Unsplash integration (opcional)
- [ ] Emoji picker para ícones
- [ ] Remove cover/icon

### 9.2 Export
- [ ] Export para Markdown
- [ ] Download como PDF
- [ ] Copy content

### 9.3 Share
- [ ] Link público
- [ ] Copy link
- [ ] QR code (opcional)

---

## 🎨 Design System

### Paleta de Cores

```css
/* Light Mode */
--background: 0 0% 100%;
--foreground: 0 0% 3.9%;
--card: 0 0% 100%;
--card-foreground: 0 0% 3.9%;
--primary: 0 0% 9%;
--primary-foreground: 0 0% 98%;
--muted: 0 0% 96.1%;
--muted-foreground: 0 0% 45.1%;

/* Dark Mode */
--background: 0 0% 3.9%;
--foreground: 0 0% 98%;
--card: 0 0% 3.9%;
--card-foreground: 0 0% 98%;
--primary: 0 0% 98%;
--primary-foreground: 0 0% 9%;
--muted: 0 0% 14.9%;
--muted-foreground: 0 0% 63.9%;
```

### Tipografia

```css
font-family:
  -apple-system, BlinkMacSystemFont, 'Segoe UI',
  'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell',
  'Fira Sans', 'Droid Sans', 'Helvetica Neue',
  sans-serif;
```

### Espaçamento

Usar escala de 4px: 4, 8, 12, 16, 24, 32, 48, 64

---

## 🧪 Testing Strategy

### Unit Tests
```bash
npm install -D vitest @testing-library/react @testing-library/jest-dom
```

- Testar componentes isolados
- Testar hooks
- Testar utils

### Integration Tests
- Fluxos completos (login → criar página → editar)
- Interações entre componentes

### E2E Tests (Playwright)
```bash
npm install -D @playwright/test
```

- Fluxos críticos
- Cross-browser testing

---

## 📦 Otimizações

### Performance
- [ ] Code splitting por rota
- [ ] Lazy loading de componentes pesados
- [ ] Image optimization (Next.js Image)
- [ ] Memoização (React.memo, useMemo)
- [ ] Virtual scrolling para listas grandes

### SEO
- [ ] Meta tags dinâmicas
- [ ] Open Graph tags
- [ ] Sitemap
- [ ] robots.txt

### Acessibilidade
- [ ] ARIA labels
- [ ] Keyboard navigation
- [ ] Screen reader support
- [ ] Focus indicators
- [ ] Color contrast

---

## 🚀 Deploy

### Vercel (Recomendado)
```bash
npm install -g vercel
vercel
```

**Configurações:**
- Auto deploy no push para main
- Preview deployments para PRs
- Environment variables
- Analytics

---

## 📊 Métricas de Sucesso

### Performance
- Lighthouse score > 90
- First Contentful Paint < 1.5s
- Time to Interactive < 3s
- Bundle size < 200KB (inicial)

### Funcionalidade
- ✅ Criar/editar/deletar páginas
- ✅ Editor com 7+ tipos de blocos
- ✅ Navegação hierárquica
- ✅ Busca funcional
- ✅ Comentários
- ✅ Tags e favoritos
- ✅ Mobile responsive

---

## 🔄 Processo de Desenvolvimento

### Dia a Dia
1. Escolher uma task do plano
2. Criar branch (`feature/nome-da-feature`)
3. Implementar + testar
4. Commit (Conventional Commits)
5. Push e abrir PR
6. Review (pode ser self-review no início)
7. Merge para main
8. Deploy automático

### Daily Checklist
- [ ] Código funciona localmente
- [ ] Tipos TypeScript corretos
- [ ] Sem warnings no console
- [ ] Responsivo testado
- [ ] Acessibilidade básica

---

## 📚 Recursos e Referências

### Documentação
- [Next.js Docs](https://nextjs.org/docs)
- [TipTap Docs](https://tiptap.dev/)
- [Shadcn/ui](https://ui.shadcn.com/)
- [TanStack Query](https://tanstack.com/query/latest)

### Inspiração
- [Notion.so](https://notion.so)
- [Coda.io](https://coda.io)
- [Obsidian](https://obsidian.md)

---

## ✅ Checklist de Conclusão

### Semana 1
- [ ] Setup projeto Next.js
- [ ] Configurar Tailwind + Shadcn
- [ ] API client configurado
- [ ] State management (Zustand)
- [ ] Login e registro funcionando

### Semana 2
- [ ] Layout com sidebar
- [ ] Workspace switcher
- [ ] Lista de páginas
- [ ] Criar nova página

### Semana 3-4
- [ ] Editor básico funcionando
- [ ] 7 tipos de blocos
- [ ] Slash commands
- [ ] Salvamento automático
- [ ] Page header

### Semana 5
- [ ] Árvore hierárquica
- [ ] Comentários
- [ ] Tags
- [ ] Favoritos

### Semana 6
- [ ] Busca global
- [ ] Command palette
- [ ] Filtros

### Semana 7
- [ ] Dark mode
- [ ] Responsivo
- [ ] Animações
- [ ] Polish

### Semana 8
- [ ] Features extras
- [ ] Testes
- [ ] Deploy
- [ ] Documentação

---

**Próximo passo**: Executar `npx create-next-app@latest frontend` e começar a implementação! 🚀
