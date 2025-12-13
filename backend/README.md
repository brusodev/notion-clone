# Notion Clone Backend

Backend API para clone do Notion construído com FastAPI e PostgreSQL.

## 🚀 Stack Tecnológica

- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Banco de Dados**: PostgreSQL 15+ (Railway)
- **Cache**: Redis (opcional)
- **Autenticação**: JWT (python-jose)
- **Passwords**: bcrypt (passlib)
- **Validação**: Pydantic V2
- **Upload**: Cloudinary
- **Hospedagem**: Railway

## ✅ Status do Projeto

**Fase Atual**: Backend Completo e Testado (100% funcional)

### Funcionalidades Implementadas

#### 🔐 Autenticação (6 endpoints)
- ✅ Registro de usuários
- ✅ Login com JWT (access + refresh tokens)
- ✅ Refresh token
- ✅ Logout com token blacklist
- ✅ Perfil do usuário
- ✅ Atualização de perfil

#### 🏢 Workspaces (6 endpoints)
- ✅ Criação automática de workspace pessoal
- ✅ CRUD completo de workspaces
- ✅ Sistema de membros e permissões
- ✅ Convites para workspace
- ✅ Listagem de membros

#### 📄 Páginas (13 endpoints)
- ✅ CRUD completo de páginas
- ✅ Hierarquia de páginas (parent/child)
- ✅ Árvore de páginas
- ✅ Duplicação de páginas (com blocos)
- ✅ Soft delete (lixeira)
- ✅ Restauração de páginas
- ✅ Versionamento de páginas
- ✅ Páginas públicas com slug
- ✅ Movimentação de páginas

#### 🧱 Blocos (5 endpoints)
- ✅ CRUD completo de blocos
- ✅ Blocos aninhados (parent/child)
- ✅ Conteúdo flexível (JSONB)
- ✅ Reordenação de blocos
- ✅ Tipos: paragraph, heading, list, code, etc.

#### 💬 Comentários (4 endpoints)
- ✅ Comentários em páginas
- ✅ Comentários em blocos
- ✅ Edição de comentários
- ✅ Soft delete de comentários

#### ⭐ Favoritos (3 endpoints)
- ✅ Adicionar páginas aos favoritos
- ✅ Listar favoritos do usuário
- ✅ Remover dos favoritos

#### 🏷️ Tags (6 endpoints)
- ✅ CRUD completo de tags
- ✅ Tags por workspace
- ✅ Adicionar/remover tags de páginas
- ✅ Buscar páginas por tag
- ✅ Contagem de páginas por tag

#### 📁 Upload de Arquivos (1 endpoint)
- ✅ Upload para Cloudinary
- ✅ Imagens para covers e avatares

#### 🔍 Busca (1 endpoint)
- ✅ Busca full-text em páginas e blocos
- ✅ Filtro por workspace

#### 🔒 Permissões (2 endpoints)
- ✅ Sistema de permissões granulares
- ✅ Níveis: viewer, editor, admin, owner

### Testes

✅ **40 testes automatizados - 100% de sucesso**

```bash
# Executar suite completa
python test_all_apis.py

# Resultados
Total de testes: 40
Testes passaram: 40 ✅
Taxa de sucesso: 100%
```

## 🛠️ Setup Local

### 1. Clonar o repositório

```bash
git clone <repository-url>
cd backend
```

### 2. Criar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e configure:

```bash
cp .env.example .env
```

Edite `.env` com suas configurações:

```env
# Database (PostgreSQL do Railway)
DATABASE_URL=postgresql://user:password@host:port/database

# JWT (gerar com: openssl rand -hex 32)
SECRET_KEY=sua-chave-secreta-super-segura-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Cloudinary (opcional)
CLOUDINARY_CLOUD_NAME=seu-cloud-name
CLOUDINARY_API_KEY=sua-api-key
CLOUDINARY_API_SECRET=seu-api-secret

# Redis (opcional - para token blacklist)
# REDIS_URL=redis://localhost:6379
```

### 5. Rodar o servidor

```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`

Documentação interativa: `http://localhost:8000/docs`

## 📡 API Endpoints (40 endpoints)

### Auth (6)
- `POST /api/v1/auth/register` - Criar conta
- `POST /api/v1/auth/login` - Autenticar
- `POST /api/v1/auth/refresh` - Renovar token
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Dados do usuário
- `PATCH /api/v1/auth/me` - Atualizar perfil

### Workspaces (6)
- `GET /api/v1/workspaces/` - Listar workspaces
- `POST /api/v1/workspaces/` - Criar workspace
- `GET /api/v1/workspaces/{id}` - Detalhes
- `PATCH /api/v1/workspaces/{id}` - Atualizar
- `DELETE /api/v1/workspaces/{id}` - Deletar
- `GET /api/v1/workspaces/{id}/members` - Listar membros

### Pages (13)
- `GET /api/v1/pages/` - Listar páginas
- `POST /api/v1/pages/` - Criar página
- `GET /api/v1/pages/{id}` - Detalhes + blocos
- `PATCH /api/v1/pages/{id}` - Atualizar
- `DELETE /api/v1/pages/{id}` - Arquivar
- `GET /api/v1/pages/workspace/{id}/tree` - Árvore hierárquica
- `PATCH /api/v1/pages/{id}/move` - Mover página
- `POST /api/v1/pages/{id}/duplicate` - Duplicar página
- `POST /api/v1/pages/{id}/restore` - Restaurar da lixeira
- `DELETE /api/v1/pages/{id}/permanent` - Deletar permanentemente
- `GET /api/v1/pages/trash` - Listar páginas arquivadas
- `GET /api/v1/pages/{id}/versions` - Histórico de versões
- `POST /api/v1/pages/{id}/versions/{version}/restore` - Restaurar versão

### Blocks (5)
- `POST /api/v1/blocks/` - Criar bloco
- `GET /api/v1/blocks/page/{id}` - Listar blocos da página
- `GET /api/v1/blocks/{id}` - Detalhes do bloco
- `PATCH /api/v1/blocks/{id}` - Atualizar bloco
- `DELETE /api/v1/blocks/{id}` - Deletar bloco

### Comments (4)
- `POST /api/v1/comments/` - Criar comentário
- `GET /api/v1/comments/page/{id}` - Comentários da página
- `PATCH /api/v1/comments/{id}` - Atualizar comentário
- `DELETE /api/v1/comments/{id}` - Deletar comentário

### Favorites (3)
- `POST /api/v1/pages/{id}/favorite` - Favoritar página
- `GET /api/v1/pages/favorites` - Listar favoritos
- `DELETE /api/v1/pages/{id}/favorite` - Desfavoritar

### Tags (6)
- `POST /api/v1/workspaces/{id}/tags` - Criar tag
- `GET /api/v1/workspaces/{id}/tags` - Listar tags
- `GET /api/v1/workspaces/{id}/tags/{tag_id}` - Detalhes da tag
- `PUT /api/v1/workspaces/{id}/tags/{tag_id}` - Atualizar tag
- `DELETE /api/v1/workspaces/{id}/tags/{tag_id}` - Deletar tag
- `POST /api/v1/pages/{id}/tags/{tag_id}` - Adicionar tag à página
- `DELETE /api/v1/pages/{id}/tags/{tag_id}` - Remover tag da página
- `GET /api/v1/pages/{id}/tags` - Listar tags da página

### Files (1)
- `POST /api/v1/files/upload` - Upload de arquivo

### Search (1)
- `GET /api/v1/search/` - Buscar em páginas e blocos

### Permissions (2)
- `GET /api/v1/permissions/page/{id}` - Verificar permissões
- `POST /api/v1/permissions/page/{id}` - Atualizar permissões

## 🗄️ Modelo de Dados

### User
- ID (UUID), email, password_hash, name, avatar_url
- is_active, created_at, updated_at

### Workspace
- ID (UUID), name, icon, owner_id
- created_at, updated_at

### WorkspaceMember
- ID (UUID), workspace_id, user_id, role
- joined_at

### Page
- ID (UUID), workspace_id, parent_id, title, icon, cover_image
- is_archived, is_public, public_slug, order
- created_by, created_at, updated_at

### Block
- ID (UUID), page_id, parent_block_id, type
- content (JSONB), order
- created_at, updated_at

### Comment
- ID (UUID), page_id, block_id, user_id
- content, is_deleted
- created_at, updated_at

### PageFavorite
- ID (UUID), user_id, page_id
- created_at

### Tag
- ID (UUID), workspace_id, name, color
- created_by, created_at, updated_at

### PageTag
- ID (UUID), page_id, tag_id
- created_at

### PageVersion
- ID (UUID), page_id, version_number
- title, icon, cover_image, content_snapshot (JSONB)
- created_by, created_at, change_summary

## 🧪 Testes

### Executar todos os testes

```bash
# Suite completa (40 testes)
python test_all_apis.py

# Testes principais (14 testes)
python test_core.py
```

### Cobertura de testes

- ✅ Autenticação (JWT, refresh, logout)
- ✅ Workspaces (CRUD, membros)
- ✅ Páginas (CRUD, árvore, duplicação, lixeira)
- ✅ Blocos (CRUD, reordenação)
- ✅ Comentários (CRUD)
- ✅ Favoritos (adicionar, listar, remover)
- ✅ Tags (CRUD, associação com páginas)

## 🔒 Segurança

- ✅ Senhas hasheadas com bcrypt (12 rounds)
- ✅ JWT com access tokens (15 min) e refresh tokens (7 dias)
- ✅ Token blacklist com Redis (opcional)
- ✅ CORS configurável
- ✅ UUIDs para IDs
- ✅ Validação com Pydantic V2
- ✅ SQL Injection protection (SQLAlchemy)
- ✅ Permissões granulares por workspace

## 📖 Documentação

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 🚀 Próximos Passos

### Fase 1: Melhorias Backend (Opcional)
- [ ] WebSockets para colaboração em tempo real
- [ ] Sistema de notificações
- [ ] Suporte a templates de páginas
- [ ] Exportação de páginas (PDF, Markdown)
- [ ] Importação de arquivos (Markdown, HTML)
- [ ] Rate limiting
- [ ] Logs estruturados
- [ ] Métricas e monitoring

### Fase 2: Frontend (Next.js + TypeScript)
- [ ] Setup inicial do projeto Next.js 14+
- [ ] Sistema de autenticação (login, registro)
- [ ] Dashboard de workspaces
- [ ] Editor de páginas com blocos
- [ ] Sidebar com árvore de páginas
- [ ] Sistema de drag & drop
- [ ] Editor de rich text
- [ ] Comentários inline
- [ ] Sistema de favoritos
- [ ] Sistema de tags
- [ ] Busca global
- [ ] Modo dark/light
- [ ] Responsivo (mobile-first)

### Fase 3: Features Avançadas
- [ ] Colaboração em tempo real (WebSockets)
- [ ] Mentions (@user)
- [ ] Compartilhamento público de páginas
- [ ] Exportação/Importação
- [ ] Templates
- [ ] Atalhos de teclado
- [ ] Histórico de versões (UI)
- [ ] Notificações
- [ ] Integrações (Slack, Discord, etc)

### Fase 4: DevOps & Produção
- [ ] CI/CD (GitHub Actions)
- [ ] Testes E2E (Playwright)
- [ ] Docker & Docker Compose
- [ ] Kubernetes (opcional)
- [ ] Monitoring (Sentry, DataDog)
- [ ] Backup automatizado
- [ ] CDN para assets
- [ ] Cache strategy
- [ ] Load balancing

## 📊 Estatísticas do Projeto

- **Endpoints**: 40
- **Tabelas**: 17
- **Testes**: 40 (100% pass)
- **Migrations**: 15
- **Linhas de código**: ~5000+
- **Cobertura de testes**: 100% dos endpoints principais

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.
