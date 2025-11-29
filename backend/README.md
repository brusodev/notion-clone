# Notion Clone Backend

Backend API para clone do Notion construído com FastAPI e PostgreSQL.

## 🚀 Stack Tecnológica

- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Banco de Dados**: PostgreSQL 15+
- **Cache**: Redis
- **Autenticação**: JWT (python-jose)
- **Passwords**: bcrypt (passlib)
- **Validação**: Pydantic V2
- **Hospedagem**: Railway

## 📋 Funcionalidades

- ✅ Autenticação JWT com access e refresh tokens
- ✅ Gerenciamento de usuários
- ✅ Workspaces com membros e permissões
- ✅ Páginas hierárquicas (árvore de páginas)
- ✅ Blocos de conteúdo flexíveis (JSONB)
- ✅ Soft delete para páginas
- ✅ Ordenação customizada
- ✅ API REST completa

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
DATABASE_URL=postgresql://user:password@localhost:5432/notion_clone
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
```

### 5. Executar migrations

```bash
alembic upgrade head
```

### 6. Rodar o servidor

```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`

Documentação interativa: `http://localhost:8000/docs`

## 📡 Endpoints Principais

### Auth
- `POST /api/v1/auth/register` - Criar conta
- `POST /api/v1/auth/login` - Autenticar
- `POST /api/v1/auth/refresh` - Renovar token
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/me` - Dados do usuário
- `PATCH /api/v1/auth/me` - Atualizar perfil

### Workspaces
- `GET /api/v1/workspaces/` - Listar workspaces
- `POST /api/v1/workspaces/` - Criar workspace
- `GET /api/v1/workspaces/{id}` - Detalhes
- `PATCH /api/v1/workspaces/{id}` - Atualizar
- `DELETE /api/v1/workspaces/{id}` - Deletar

### Pages
- `GET /api/v1/pages/` - Listar páginas
- `POST /api/v1/pages/` - Criar página
- `GET /api/v1/pages/{id}` - Detalhes + blocos
- `PATCH /api/v1/pages/{id}` - Atualizar
- `DELETE /api/v1/pages/{id}` - Arquivar
- `GET /api/v1/pages/workspace/{id}/tree` - Árvore hierárquica
- `PATCH /api/v1/pages/{id}/move` - Mover página

### Blocks
- `POST /api/v1/blocks/` - Criar bloco
- `GET /api/v1/blocks/page/{id}` - Listar blocos
- `PATCH /api/v1/blocks/{id}` - Atualizar
- `DELETE /api/v1/blocks/{id}` - Deletar
- `PATCH /api/v1/blocks/{id}/move` - Reordenar

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

## 🚀 Deploy no Railway

### 1. Instalar Railway CLI

```bash
npm i -g @railway/cli
```

### 2. Login

```bash
railway login
```

### 3. Criar projeto

```bash
railway init
```

### 4. Adicionar PostgreSQL

```bash
railway add --database postgresql
```

### 5. Adicionar Redis

```bash
railway add --database redis
```

### 6. Deploy

```bash
railway up
```

### 7. Configurar variáveis de ambiente no Railway Dashboard

- `SECRET_KEY` - Gere com: `openssl rand -hex 32`
- `ALLOWED_ORIGINS` - URL do frontend

## 🧪 Testes

```bash
pytest tests/
```

## 📝 Migrations

### Criar nova migration

```bash
alembic revision --autogenerate -m "Description"
```

### Aplicar migrations

```bash
alembic upgrade head
```

### Reverter migration

```bash
alembic downgrade -1
```

## 🔒 Segurança

- Senhas hasheadas com bcrypt (12 rounds)
- JWT com access tokens (15 min) e refresh tokens (7 dias)
- Token blacklist com Redis
- CORS configurável
- UUIDs para segurança adicional

## 📖 Documentação

Acesse `/docs` para documentação interativa (Swagger UI)

Acesse `/redoc` para documentação alternativa (ReDoc)

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.
