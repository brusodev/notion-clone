# PROMPT PARA DESENVOLVIMENTO DO BACKEND - CLONE NOTION

---

## 🎯 CONTEXTO DO PROJETO

Preciso desenvolver o backend completo de um clone do Notion usando **FastAPI** e **PostgreSQL**. O projeto será hospedado no **Railway** e deve suportar criação de páginas hierárquicas, edição de blocos de conteúdo, autenticação JWT e, futuramente, colaboração em tempo real via WebSocket.

---

## 📋 REQUISITOS TÉCNICOS

### Stack Obrigatória
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Banco de Dados**: PostgreSQL 15+
- **Cache**: Redis
- **Autenticação**: JWT (python-jose)
- **Passwords**: bcrypt (passlib)
- **Validação**: Pydantic V2
- **Hospedagem**: Railway

### Estrutura de Diretórios
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py            # Dependências (get_db, get_current_user)
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py        # Endpoints de autenticação
│   │       ├── workspaces.py  # CRUD de workspaces
│   │       ├── pages.py       # CRUD de páginas
│   │       └── blocks.py      # CRUD de blocos
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Settings (variáveis de ambiente)
│   │   ├── security.py        # JWT, hash de senha
│   │   └── database.py        # Conexão com DB
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── workspace.py
│   │   ├── workspace_member.py
│   │   ├── page.py
│   │   └── block.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py            # Pydantic schemas
│   │   ├── workspace.py
│   │   ├── page.py
│   │   ├── block.py
│   │   └── token.py
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── user.py            # Operações CRUD
│   │   ├── workspace.py
│   │   ├── page.py
│   │   └── block.py
│   └── utils/
│       ├── __init__.py
│       └── email.py           # Envio de emails (recuperação de senha)
├── alembic/
│   ├── versions/
│   └── env.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_auth.py
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
├── Procfile                   # Para Railway
└── README.md
```

---

## 🗄️ MODELO DE DADOS

### 1. User
```python
- id: UUID (PK, default=uuid4)
- email: String(255) (unique, index)
- password_hash: String(255)
- name: String(100)
- avatar_url: String(500) (nullable)
- is_active: Boolean (default=True)
- created_at: DateTime (default=now)
- updated_at: DateTime (onupdate=now)

# Relationships
- workspaces_owned: relationship -> Workspace
- workspace_memberships: relationship -> WorkspaceMember
- pages_created: relationship -> Page
```

### 2. Workspace
```python
- id: UUID (PK)
- name: String(100)
- icon: String(100) (nullable, emoji)
- owner_id: UUID (FK -> User.id, index)
- created_at: DateTime
- updated_at: DateTime

# Relationships
- owner: relationship -> User
- members: relationship -> WorkspaceMember
- pages: relationship -> Page
```

### 3. WorkspaceMember
```python
- id: UUID (PK)
- workspace_id: UUID (FK -> Workspace.id, index)
- user_id: UUID (FK -> User.id, index)
- role: Enum('owner', 'editor', 'viewer')
- joined_at: DateTime (default=now)

# Constraints
- unique_together: (workspace_id, user_id)

# Relationships
- workspace: relationship -> Workspace
- user: relationship -> User
```

### 4. Page
```python
- id: UUID (PK)
- workspace_id: UUID (FK -> Workspace.id, index)
- parent_id: UUID (FK -> Page.id, nullable, index)
- title: String(500) (default='Untitled')
- icon: String(100) (nullable, emoji)
- cover_image: String(500) (nullable, URL)
- is_archived: Boolean (default=False, index)
- is_public: Boolean (default=False)
- public_slug: String(100) (unique, nullable, index)
- order: Integer (default=0, para ordenação)
- created_by: UUID (FK -> User.id, index)
- created_at: DateTime
- updated_at: DateTime

# Relationships
- workspace: relationship -> Workspace
- parent: relationship -> Page (self-referential)
- children: relationship -> Page (back_populates='parent')
- creator: relationship -> User
- blocks: relationship -> Block (cascade delete)
```

### 5. Block
```python
- id: UUID (PK)
- page_id: UUID (FK -> Page.id, index, cascade delete)
- parent_block_id: UUID (FK -> Block.id, nullable, index)
- type: String(50) (ex: 'paragraph', 'heading1', 'image', 'code')
- content: JSONB (conteúdo flexível)
- order: Integer (posição na página)
- created_at: DateTime
- updated_at: DateTime

# Relationships
- page: relationship -> Page
- parent_block: relationship -> Block (self-referential)
- child_blocks: relationship -> Block
```

**Exemplo de content JSONB para diferentes tipos:**
```json
// Paragraph
{
  "text": "Meu texto com **negrito** e *itálico*",
  "marks": [
    {"type": "bold", "start": 13, "end": 21},
    {"type": "italic", "start": 24, "end": 31}
  ]
}

// Heading
{
  "text": "Título Principal",
  "level": 1
}

// Image
{
  "url": "https://cdn.example.com/image.jpg",
  "caption": "Legenda da imagem",
  "width": 800,
  "height": 600
}

// Code
{
  "code": "print('Hello World')",
  "language": "python"
}

// Checkbox (to-do)
{
  "text": "Tarefa a fazer",
  "checked": false
}
```

---

## 🔐 AUTENTICAÇÃO E SEGURANÇA

### Fluxo de Autenticação
1. **Registro**: POST /api/v1/auth/register
   - Input: email, password, name
   - Validação: email único, senha >= 8 caracteres
   - Hash senha com bcrypt (12 rounds)
   - Criar workspace pessoal automaticamente
   - Retornar: user data + access_token + refresh_token

2. **Login**: POST /api/v1/auth/login
   - Input: email, password
   - Verificar credenciais
   - Retornar: access_token (15min) + refresh_token (7 dias)

3. **Refresh**: POST /api/v1/auth/refresh
   - Input: refresh_token
   - Validar token
   - Retornar: novo access_token

4. **Logout**: POST /api/v1/auth/logout
   - Invalidar refresh_token (blacklist no Redis)

### JWT Payload
```json
{
  "sub": "user_id_uuid",
  "email": "user@example.com",
  "exp": 1234567890,
  "type": "access" // ou "refresh"
}
```

### Dependências de Autenticação
```python
# deps.py
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    # Decodificar JWT
    # Buscar usuário no DB
    # Validar is_active
    # Retornar User ou raise HTTPException(401)

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(403, "Inactive user")
    return current_user
```

---

## 📡 ENDPOINTS PRIORITÁRIOS (MVP)

### Auth (`/api/v1/auth`)
```python
POST   /register          # Criar conta
POST   /login             # Autenticar
POST   /refresh           # Renovar token
POST   /logout            # Invalidar token
GET    /me                # Dados do usuário logado
PATCH  /me                # Atualizar perfil
```

### Workspaces (`/api/v1/workspaces`)
```python
GET    /                  # Listar workspaces do usuário
POST   /                  # Criar workspace
GET    /{workspace_id}    # Detalhes do workspace
PATCH  /{workspace_id}    # Atualizar nome/ícone
DELETE /{workspace_id}    # Deletar (apenas owner)
```

### Pages (`/api/v1/pages`)
```python
GET    /                               # Listar páginas do workspace (query: workspace_id)
POST   /                               # Criar página
GET    /{page_id}                      # Detalhes da página + blocos
PATCH  /{page_id}                      # Atualizar metadados (título, ícone, etc)
DELETE /{page_id}                      # Arquivar página
GET    /workspace/{workspace_id}/tree  # Árvore hierárquica de páginas
PATCH  /{page_id}/move                 # Mover página (body: new_parent_id, new_order)
```

### Blocks (`/api/v1/blocks`)
```python
POST   /                  # Criar bloco
GET    /page/{page_id}    # Listar blocos da página (ordenados)
PATCH  /{block_id}        # Atualizar conteúdo ou tipo
DELETE /{block_id}        # Deletar bloco
PATCH  /{block_id}/move   # Reordenar (body: new_order, new_parent_block_id)
```

---

## ⚙️ CONFIGURAÇÕES (core/config.py)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Notion Clone API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # Email (futuro)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

## 🚀 CONFIGURAÇÃO RAILWAY

### 1. Variáveis de Ambiente (.env.example)
```bash
# Database (Railway fornece automaticamente)
DATABASE_URL=postgresql://user:password@host:port/database

# Redis (adicionar Redis service no Railway)
REDIS_URL=redis://host:port

# JWT (gerar com: openssl rand -hex 32)
SECRET_KEY=sua-chave-secreta-super-segura-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS (adicionar URL do frontend quando deployar)
ALLOWED_ORIGINS=["http://localhost:3000","https://seu-frontend.railway.app"]
```

### 2. Procfile
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
release: alembic upgrade head
```

### 3. requirements.txt
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9
redis==5.0.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0
```

### 4. Comandos Railway CLI (após setup)
```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Criar projeto
railway init

# Adicionar PostgreSQL
railway add --database postgresql

# Adicionar Redis
railway add --database redis

# Deploy
railway up
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### Fase 1 - Setup Inicial
- [ ] Criar estrutura de diretórios
- [ ] Configurar requirements.txt e instalar dependências
- [ ] Configurar core/config.py com variáveis de ambiente
- [ ] Configurar core/database.py (engine, SessionLocal, Base)
- [ ] Configurar Alembic para migrations

### Fase 2 - Models
- [ ] Implementar models/user.py
- [ ] Implementar models/workspace.py
- [ ] Implementar models/workspace_member.py
- [ ] Implementar models/page.py
- [ ] Implementar models/block.py
- [ ] Gerar primeira migration: `alembic revision --autogenerate -m "Initial tables"`
- [ ] Aplicar migration: `alembic upgrade head`

### Fase 3 - Schemas (Pydantic)
- [ ] schemas/user.py (UserCreate, UserUpdate, UserResponse)
- [ ] schemas/workspace.py (WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse)
- [ ] schemas/page.py (PageCreate, PageUpdate, PageResponse, PageWithBlocks)
- [ ] schemas/block.py (BlockCreate, BlockUpdate, BlockResponse)
- [ ] schemas/token.py (Token, TokenPayload)

### Fase 4 - CRUD
- [ ] crud/user.py (create, get_by_email, update, authenticate)
- [ ] crud/workspace.py (create, get_by_user, update, delete)
- [ ] crud/page.py (create, get_by_workspace, get_tree, update, archive)
- [ ] crud/block.py (create, get_by_page, update, delete, reorder)

### Fase 5 - Security
- [ ] core/security.py (hash_password, verify_password, create_access_token, decode_token)
- [ ] api/deps.py (get_db, get_current_user, get_current_active_user)

### Fase 6 - Endpoints
- [ ] api/v1/auth.py (register, login, refresh, logout, me)
- [ ] api/v1/workspaces.py (CRUD completo)
- [ ] api/v1/pages.py (CRUD + tree + move)
- [ ] api/v1/blocks.py (CRUD + reorder)

### Fase 7 - Main App
- [ ] main.py (criar app, incluir routers, configurar CORS, middleware)
- [ ] Health check endpoint: GET /health

### Fase 8 - Deploy Railway
- [ ] Criar .env.example
- [ ] Criar Procfile
- [ ] Testar localmente: `uvicorn app.main:app --reload`
- [ ] Push para GitHub
- [ ] Conectar Railway ao repositório
- [ ] Configurar variáveis de ambiente no Railway
- [ ] Deploy e verificar logs

### Fase 9 - Testes (Opcional MVP)
- [ ] tests/conftest.py (fixtures de DB e client)
- [ ] tests/test_auth.py (registro, login, tokens)
- [ ] tests/test_pages.py (CRUD, hierarquia)

---

## 🎯 TAREFAS IMEDIATAS

**Por favor, implemente os seguintes itens na ordem:**

1. **Criar estrutura completa do projeto** com todos os diretórios e arquivos base (__init__.py vazios)

2. **Implementar core/config.py** com todas as settings usando pydantic-settings

3. **Implementar core/database.py** com configuração do SQLAlchemy 2.0

4. **Criar todos os models** (user, workspace, workspace_member, page, block) com:
   - UUIDs como primary keys
   - Relationships corretas
   - Indexes apropriados
   - JSONB para Block.content

5. **Configurar Alembic** e gerar primeira migration

6. **Implementar core/security.py** com funções de JWT e hashing

7. **Criar schemas Pydantic** para todas as entidades (Create, Update, Response)

8. **Implementar CRUD operations** para User, Workspace, Page, Block

9. **Criar api/deps.py** com dependências de autenticação

10. **Implementar endpoints de Auth** (register, login, refresh, me)

11. **Implementar endpoints de Workspaces** (CRUD básico)

12. **Implementar endpoints de Pages** (CRUD + tree hierarchy)

13. **Implementar endpoints de Blocks** (CRUD + ordering)

14. **Configurar main.py** com routers, CORS, middleware de erros

15. **Preparar para Railway** (Procfile, .env.example, requirements.txt)

---

## 📝 OBSERVAÇÕES IMPORTANTES

1. **UUIDs**: Usar UUID4 para todos os IDs (mais seguro que auto-increment)

2. **Soft Delete**: Pages usam `is_archived` ao invés de deletar permanentemente

3. **Ordering**: Pages e Blocks têm campo `order` (Integer) para manter ordenação customizada pelo usuário

4. **JSONB**: O campo `content` de Block é JSONB para flexibilidade nos diferentes tipos de blocos

5. **Hierarchical Queries**: Para buscar árvore de páginas, usar recursive CTE ou queries aninhadas

6. **Permissions**: Por enquanto MVP, validar apenas que usuário é membro do workspace. Sistema completo de permissões vem depois.

7. **Error Handling**: Usar HTTPException do FastAPI com status codes apropriados

8. **Validation**: Pydantic cuida de validação de inputs automaticamente

9. **Logging**: Adicionar logging básico com Python logging module

10. **CORS**: Configurar corretamente para aceitar requests do frontend

---

## 🔍 EXEMPLO DE RESPONSE ESPERADO

### GET /api/v1/pages/{page_id}
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "workspace_id": "123e4567-e89b-12d3-a456-426614174001",
  "parent_id": null,
  "title": "Minha Primeira Página",
  "icon": "📝",
  "cover_image": null,
  "is_archived": false,
  "is_public": false,
  "created_by": "123e4567-e89b-12d3-a456-426614174002",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T14:20:00Z",
  "blocks": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174003",
      "type": "heading1",
      "content": {"text": "Introdução", "level": 1},
      "order": 0
    },
    {
      "id": "123e4567-e89b-12d3-a456-426614174004",
      "type": "paragraph",
      "content": {"text": "Este é um parágrafo de exemplo."},
      "order": 1
    }
  ]
}
```

---

## ❓ DÚVIDAS FREQUENTES

**Q: Como lidar com updates concorrentes em blocos?**
A: Por enquanto, last-write-wins. WebSocket virá na Fase 3 com operational transforms.

**Q: Preciso implementar upload de arquivos agora?**
A: Não no MVP. Por ora, aceitar URLs externas. Cloudinary/S3 virá depois.

**Q: E o sistema de permissões granulares?**
A: MVP usa apenas owner/editor/viewer no workspace. Permissões por página vêm depois.

**Q: Rate limiting?**
A: Não é crítico para MVP, mas pode adicionar com slowapi se tiver tempo.

---

## 🚀 PRONTO PARA COMEÇAR!

Com este prompt, você tem todas as informações necessárias para implementar o backend completo. Comece pela estrutura base, depois models, schemas, CRUD, endpoints e por fim o deploy no Railway.

Boa sorte! 🎉
