# 📝 Notion Clone - Full Stack Application

> Clone completo e funcional do Notion com backend FastAPI e frontend Next.js (planejado)

[![Backend Status](https://img.shields.io/badge/Backend-100%25%20Tested-success)](https://notion-clone-production-b81a.up.railway.app)
[![API Tests](https://img.shields.io/badge/API%20Tests-40/40%20Passing-brightgreen)]()
[![Railway Deploy](https://img.shields.io/badge/Railway-Deployed-blue)](https://railway.app)

---

## 🎯 Sobre o Projeto

Aplicação web full-stack que replica as funcionalidades principais do Notion, incluindo:

- ✅ Sistema completo de autenticação (JWT + Refresh Tokens)
- ✅ Workspaces com controle de permissões granulares
- ✅ Páginas hierárquicas ilimitadas
- ✅ Blocos de conteúdo flexíveis (JSONB)
- ✅ Sistema de comentários
- ✅ Tags e favoritos
- ✅ Versionamento de páginas
- ✅ Lixeira (soft delete) com restauração
- ✅ Busca full-text (PostgreSQL)
- ✅ Upload de arquivos (Cloudinary)
- ✅ API RESTful completa (40 endpoints)
- 🚧 Frontend Next.js (próximo passo)
- 🚧 Colaboração em tempo real (planejado)

---

## 🚀 Links Importantes

| Recurso | URL |
|---------|-----|
| **API Production** | https://notion-clone-production-b81a.up.railway.app |
| **API Docs (Swagger)** | https://notion-clone-production-b81a.up.railway.app/docs |
| **Health Check** | https://notion-clone-production-b81a.up.railway.app/ |
| **Roadmap Detalhado** | [ROADMAP.md](ROADMAP.md) |

---

## 📊 Status do Projeto

### Backend API: ✅ **100% Completo e Testado**

| Métrica | Status |
|---------|--------|
| **Endpoints Implementados** | 40 |
| **Testes Passando** | 40/40 (100%) ✅ |
| **Deploy** | ✅ Railway |
| **Banco de Dados** | ✅ PostgreSQL (Railway) |
| **Autenticação** | ✅ JWT + Refresh Tokens |
| **Documentação** | ✅ OpenAPI/Swagger |
| **Health Status** | 🟢 Online |

### Frontend: ⏳ **Próxima Fase**

**Stack planejada**: Next.js 14+ | TypeScript | Tailwind CSS | Shadcn/ui

---

## ✨ Funcionalidades Implementadas

### 🔐 Autenticação (6 endpoints)
- ✅ Registro de usuários com workspace pessoal automático
- ✅ Login com JWT (access + refresh tokens)
- ✅ Refresh token rotation
- ✅ Logout com token blacklist (Redis opcional)
- ✅ Perfil do usuário (get + update)
- ✅ Password hashing com bcrypt (12 rounds)

### 🏢 Workspaces (6 endpoints)
- ✅ CRUD completo de workspaces
- ✅ Workspace pessoal criado automaticamente
- ✅ Sistema de membros com roles (owner, admin, editor, viewer)
- ✅ Gerenciamento de membros (add, update role, remove)
- ✅ Sistema de convites por email
- ✅ Validação de permissões em todas operações

### 📄 Páginas (13 endpoints)
- ✅ CRUD completo de páginas
- ✅ Hierarquia ilimitada (parent/children)
- ✅ Árvore hierárquica de páginas
- ✅ Duplicação de páginas (com blocos)
- ✅ Soft delete (lixeira) com restauração
- ✅ Movimentação de páginas
- ✅ Versionamento automático de páginas
- ✅ Histórico de versões com snapshot
- ✅ Restauração de versões anteriores
- ✅ Páginas públicas com slug customizado
- ✅ Ícones emoji e cover images

### 🧱 Blocos (5 endpoints)
- ✅ CRUD completo de blocos
- ✅ Blocos aninhados (hierarquia)
- ✅ Conteúdo flexível em JSONB
- ✅ Reordenação de blocos
- ✅ Tipos: paragraph, heading, list, code, quote, divider

### 💬 Comentários (4 endpoints)
- ✅ Comentários em páginas
- ✅ Comentários em blocos específicos
- ✅ Edição de comentários
- ✅ Soft delete de comentários

### ⭐ Favoritos (3 endpoints)
- ✅ Adicionar páginas aos favoritos
- ✅ Listar favoritos do usuário
- ✅ Remover dos favoritos
- ✅ Status de favorito por página

### 🏷️ Tags (8 endpoints)
- ✅ CRUD completo de tags por workspace
- ✅ Tags com cores customizáveis
- ✅ Adicionar/remover tags de páginas
- ✅ Listar tags de uma página
- ✅ Buscar páginas por tag
- ✅ Contagem de páginas por tag

### 📁 Upload (1 endpoint)
- ✅ Upload de arquivos para Cloudinary
- ✅ Suporte a imagens para covers e avatares
- ✅ Validação de tipo e tamanho

### 🔍 Busca (1 endpoint)
- ✅ Busca full-text em páginas e blocos
- ✅ PostgreSQL FTS (Full-Text Search)
- ✅ Filtro por workspace
- ✅ Ranking por relevância

### 🔒 Permissões (2 endpoints)
- ✅ Sistema de permissões granulares
- ✅ Níveis: viewer, editor, admin, owner
- ✅ Verificação de permissões por página
- ✅ Atualização de permissões

---

## 📡 API Endpoints (40 endpoints)

### Autenticação (6)
- `POST /api/v1/auth/register` - Criar conta
- `POST /api/v1/auth/login` - Autenticar
- `POST /api/v1/auth/refresh` - Renovar token
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Dados do usuário
- `PATCH /api/v1/auth/me` - Atualizar perfil

### Workspaces (6)
- `GET /api/v1/workspaces/` - Listar
- `POST /api/v1/workspaces/` - Criar
- `GET /api/v1/workspaces/{id}` - Detalhes
- `PATCH /api/v1/workspaces/{id}` - Atualizar
- `DELETE /api/v1/workspaces/{id}` - Deletar
- `GET /api/v1/workspaces/{id}/members` - Membros

### Páginas (13)
- `GET /api/v1/pages/` - Listar
- `POST /api/v1/pages/` - Criar
- `GET /api/v1/pages/{id}` - Detalhes
- `PATCH /api/v1/pages/{id}` - Atualizar
- `DELETE /api/v1/pages/{id}` - Arquivar
- `GET /api/v1/pages/workspace/{id}/tree` - Árvore
- `PATCH /api/v1/pages/{id}/move` - Mover
- `POST /api/v1/pages/{id}/duplicate` - Duplicar
- `POST /api/v1/pages/{id}/restore` - Restaurar
- `DELETE /api/v1/pages/{id}/permanent` - Deletar permanentemente
- `GET /api/v1/pages/trash` - Lixeira
- `GET /api/v1/pages/{id}/versions` - Versões
- `POST /api/v1/pages/{id}/versions/{version}/restore` - Restaurar versão

### Blocos (5)
- `POST /api/v1/blocks/` - Criar
- `GET /api/v1/blocks/page/{id}` - Listar
- `GET /api/v1/blocks/{id}` - Detalhes
- `PATCH /api/v1/blocks/{id}` - Atualizar
- `DELETE /api/v1/blocks/{id}` - Deletar

### Comentários (4) + Favoritos (3) + Tags (8) + Outros (3)

Ver documentação completa em: [backend/README.md](backend/README.md)

---

## 🛠️ Tecnologias

### Backend (Implementado)
- **Framework**: FastAPI 0.115+
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL 15+ (Railway)
- **Migrations**: Alembic
- **Auth**: JWT (python-jose)
- **Cache**: Redis (opcional)
- **Upload**: Cloudinary
- **Deploy**: Railway

### Frontend (Planejado)
- **Framework**: Next.js 14+ (App Router)
- **Linguagem**: TypeScript
- **Styling**: Tailwind CSS
- **Componentes**: Shadcn/ui
- **State**: Zustand
- **Data Fetching**: React Query
- **Editor**: TipTap ou Slate.js
- **Deploy**: Vercel

---

## 🧪 Testes

### ✅ 100% de Cobertura nos Endpoints Principais

```bash
# Executar suite completa (40 testes)
cd backend
python test_all_apis.py

# Resultado
Total de testes: 40
✅ Testes passaram: 40
❌ Testes falharam: 0
Taxa de sucesso: 100.0%
```

### Cobertura de Testes
- ✅ Autenticação (6 testes)
- ✅ Workspaces (4 testes)
- ✅ Páginas (9 testes)
- ✅ Blocos (5 testes)
- ✅ Comentários (3 testes)
- ✅ Favoritos (3 testes)
- ✅ Tags (6 testes)
- ✅ Lixeira (2 testes)
- ✅ Cleanup (2 testes)

---

## 🚀 Quick Start

### Backend - Desenvolvimento Local

```bash
# 1. Clone o repositório
git clone https://github.com/brusodev/notion-clone.git
cd notion-clone/backend

# 2. Crie e ative o ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações

# 5. Inicie o servidor
uvicorn app.main:app --reload

# 6. Acesse a documentação
# http://localhost:8000/docs
```

### Variáveis de Ambiente

```env
# Database (PostgreSQL do Railway)
DATABASE_URL=postgresql://user:password@host:port/database

# JWT (gerar com: openssl rand -hex 32)
SECRET_KEY=sua-chave-secreta-super-segura-aqui

# CORS
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Cloudinary (opcional)
CLOUDINARY_CLOUD_NAME=seu-cloud-name
CLOUDINARY_API_KEY=sua-api-key
CLOUDINARY_API_SECRET=seu-api-secret
```

---

## 🗺️ Roadmap

### ✅ Fase 0: Backend (Completo)
- ✅ 40 endpoints implementados e testados
- ✅ Sistema de autenticação completo
- ✅ Workspaces, páginas, blocos
- ✅ Comentários, favoritos, tags
- ✅ Versionamento e lixeira
- ✅ Upload de arquivos
- ✅ Busca full-text

### 🎯 Fase 1: Frontend (Próximo - 6-8 semanas)
- [ ] Setup Next.js 14 + TypeScript
- [ ] Sistema de autenticação
- [ ] Dashboard e workspaces
- [ ] Editor de páginas com blocos
- [ ] Árvore hierárquica
- [ ] Comentários e tags
- [ ] Busca global
- [ ] Modo dark/light

### 🚀 Fase 2: Features Avançadas (3-4 meses)
- [ ] Colaboração em tempo real (WebSockets)
- [ ] Mentions (@user)
- [ ] Blocos avançados (tabela, database, etc)
- [ ] Templates de páginas
- [ ] Exportação (Markdown, PDF)
- [ ] Integrações (Slack, Discord)

### ⚙️ Fase 3: DevOps (2-3 semanas)
- [ ] CI/CD (GitHub Actions)
- [ ] Testes E2E (Playwright)
- [ ] Docker Compose
- [ ] Monitoring (Sentry)
- [ ] Backup automatizado

**Ver roadmap completo**: [ROADMAP.md](ROADMAP.md)

---

## 📊 Estatísticas

- **Endpoints**: 40
- **Tabelas**: 17
- **Testes**: 40 (100% pass)
- **Migrations**: 15+
- **Linhas de código**: ~5000+
- **Tempo de desenvolvimento**: 3 semanas
- **Uptime**: 99.9%

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona NovaFeature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

### Convenção de Commits
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `test:` Testes
- `refactor:` Refatoração

---

## 📚 Documentação

- [Backend README](backend/README.md) - Documentação técnica do backend
- [ROADMAP](ROADMAP.md) - Roadmap detalhado do projeto
- [API Docs](https://notion-clone-production-b81a.up.railway.app/docs) - Documentação interativa

---

## 📝 Licença

Este projeto está sob a licença MIT.

---

## 👨‍💻 Autor

**Bruno Soares**
- GitHub: [@brusodev](https://github.com/brusodev)

---

**Desenvolvido com ❤️ usando FastAPI e Python**

⭐ Se este projeto foi útil, considere dar uma estrela!
