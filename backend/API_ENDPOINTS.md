# 📡 Endpoints da API - Notion Clone Backend

Referência completa de todos os endpoints disponíveis.

**Base URL**: `http://localhost:8000`  
**Docs**: `http://localhost:8000/docs`

---

## 🏥 Health & Status

### GET /health
Verificar saúde da API.

**Request:**
```bash
curl http://localhost:8000/health
```

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "project": "Notion Clone API"
}
```

### GET /
Informações básicas da API.

**Request:**
```bash
curl http://localhost:8000/
```

**Response:** `200 OK`
```json
{
  "message": "Welcome to Notion Clone API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

---

## 🔐 Autenticação

Base: `/api/v1/auth`

### POST /register
Registrar novo usuário e criar workspace pessoal.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@exemplo.com",
    "password": "senha123",
    "name": "Nome do Usuário"
  }'
```

**Response:** `201 Created`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### POST /login
Autenticar usuário existente.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=usuario@exemplo.com&password=senha123"
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### POST /refresh
Renovar access token usando refresh token.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJhbGciOiJIUzI1NiIs..."}'
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### POST /logout
Invalidar refresh token (blacklist).

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "eyJhbGciOiJIUzI1NiIs..."}'
```

**Response:** `200 OK`
```json
{
  "message": "Successfully logged out"
}
```

### GET /me
Obter dados do usuário logado.

**Request:**
```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "usuario@exemplo.com",
  "name": "Nome do Usuário",
  "avatar_url": null,
  "is_active": true,
  "created_at": "2025-11-29T10:00:00",
  "updated_at": "2025-11-29T10:00:00"
}
```

### PATCH /me
Atualizar perfil do usuário.

**Request:**
```bash
curl -X PATCH http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Novo Nome",
    "avatar_url": "https://exemplo.com/avatar.jpg"
  }'
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "usuario@exemplo.com",
  "name": "Novo Nome",
  "avatar_url": "https://exemplo.com/avatar.jpg",
  "is_active": true,
  "created_at": "2025-11-29T10:00:00",
  "updated_at": "2025-11-29T11:00:00"
}
```

---

## 🏢 Workspaces

Base: `/api/v1/workspaces`

### GET /
Listar workspaces do usuário.

**Request:**
```bash
curl http://localhost:8000/api/v1/workspaces/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "name": "Meu Workspace",
    "icon": "🏠",
    "owner_id": "uuid",
    "created_at": "2025-11-29T10:00:00",
    "updated_at": "2025-11-29T10:00:00"
  }
]
```

### POST /
Criar novo workspace.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/workspaces/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Novo Workspace",
    "icon": "🚀"
  }'
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "name": "Novo Workspace",
  "icon": "🚀",
  "owner_id": "uuid",
  "created_at": "2025-11-29T10:00:00",
  "updated_at": "2025-11-29T10:00:00"
}
```

### GET /{workspace_id}
Obter detalhes de um workspace.

**Request:**
```bash
curl http://localhost:8000/api/v1/workspaces/{workspace_id} \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "Meu Workspace",
  "icon": "🏠",
  "owner_id": "uuid",
  "created_at": "2025-11-29T10:00:00",
  "updated_at": "2025-11-29T10:00:00"
}
```

### PATCH /{workspace_id}
Atualizar workspace.

**Request:**
```bash
curl -X PATCH http://localhost:8000/api/v1/workspaces/{workspace_id} \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Workspace Atualizado",
    "icon": "🎯"
  }'
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "name": "Workspace Atualizado",
  "icon": "🎯",
  "owner_id": "uuid",
  "created_at": "2025-11-29T10:00:00",
  "updated_at": "2025-11-29T11:00:00"
}
```

### DELETE /{workspace_id}
Deletar workspace.

**Request:**
```bash
curl -X DELETE http://localhost:8000/api/v1/workspaces/{workspace_id} \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**Response:** `204 No Content`

---

## 📄 Páginas

Base: `/api/v1/pages`

### GET /
Listar páginas de um workspace.

**Query Params:**
- `workspace_id` (required): UUID do workspace
- `skip` (optional): Offset para paginação (default: 0)
- `limit` (optional): Limite de resultados (default: 100)

**Request:**
```bash
curl "http://localhost:8000/api/v1/pages/?workspace_id={workspace_id}" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "workspace_id": "uuid",
    "parent_id": null,
    "title": "Minha Página",
    "icon": "📝",
    "cover_image": null,
    "is_archived": false,
    "is_public": false,
    "public_slug": null,
    "order": 0,
    "created_by": "uuid",
    "created_at": "2025-11-29T10:00:00",
    "updated_at": "2025-11-29T10:00:00"
  }
]
```

### POST /
Criar nova página.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/pages/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "uuid",
    "title": "Nova Página",
    "icon": "📝",
    "parent_id": null
  }'
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "workspace_id": "uuid",
  "parent_id": null,
  "title": "Nova Página",
  "icon": "📝",
  "cover_image": null,
  "is_archived": false,
  "is_public": false,
  "public_slug": null,
  "order": 0,
  "created_by": "uuid",
  "created_at": "2025-11-29T10:00:00",
  "updated_at": "2025-11-29T10:00:00"
}
```

### GET /{page_id}
Obter detalhes da página com blocos.

**Request:**
```bash
curl http://localhost:8000/api/v1/pages/{page_id} \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "workspace_id": "uuid",
  "parent_id": null,
  "title": "Minha Página",
  "icon": "📝",
  "cover_image": null,
  "is_archived": false,
  "is_public": false,
  "public_slug": null,
  "order": 0,
  "created_by": "uuid",
  "created_at": "2025-11-29T10:00:00",
  "updated_at": "2025-11-29T10:00:00",
  "blocks": [
    {
      "id": "uuid",
      "page_id": "uuid",
      "type": "paragraph",
      "content": {"text": "Conteúdo"},
      "order": 0,
      "created_at": "2025-11-29T10:00:00",
      "updated_at": "2025-11-29T10:00:00"
    }
  ]
}
```

### PATCH /{page_id}
Atualizar página.

**Request:**
```bash
curl -X PATCH http://localhost:8000/api/v1/pages/{page_id} \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Título Atualizado",
    "icon": "✏️"
  }'
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "title": "Título Atualizado",
  "icon": "✏️",
  ...
}
```

### DELETE /{page_id}
Arquivar página (soft delete).

**Request:**
```bash
curl -X DELETE http://localhost:8000/api/v1/pages/{page_id} \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**Response:** `204 No Content`

### GET /tree
Obter árvore hierárquica de páginas.

**Query Params:**
- `workspace_id` (required): UUID do workspace

**Request:**
```bash
curl "http://localhost:8000/api/v1/pages/tree?workspace_id={workspace_id}" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "title": "Página Principal",
    "icon": "📝",
    "children": [
      {
        "id": "uuid",
        "title": "Subpágina",
        "icon": "📄",
        "children": []
      }
    ]
  }
]
```

### POST /{page_id}/duplicate
Duplicar página com blocos.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/pages/{page_id}/duplicate \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "title": "Minha Página (cópia)",
  ...
}
```

---

## 🧱 Blocos

Base: `/api/v1/blocks`

### POST /
Criar novo bloco.

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/blocks/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "page_id": "uuid",
    "type": "paragraph",
    "content": {
      "text": "Este é um parágrafo com **negrito**",
      "marks": [
        {"type": "bold", "start": 24, "end": 32}
      ]
    },
    "order": 0
  }'
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "page_id": "uuid",
  "parent_block_id": null,
  "type": "paragraph",
  "content": {
    "text": "Este é um parágrafo com **negrito**",
    "marks": [{"type": "bold", "start": 24, "end": 32}]
  },
  "order": 0,
  "created_at": "2025-11-29T10:00:00",
  "updated_at": "2025-11-29T10:00:00"
}
```

**Tipos de Blocos:**
- `heading1`: `{"text": "Título", "level": 1}`
- `heading2`: `{"text": "Título", "level": 2}`
- `heading3`: `{"text": "Título", "level": 3}`
- `paragraph`: `{"text": "...", "marks": [...]}`
- `code`: `{"text": "...", "language": "python"}`
- `quote`: `{"text": "..."}`
- `bullet_list`: `{"text": "..."}`
- `numbered_list`: `{"text": "..."}`
- `checkbox`: `{"text": "...", "checked": false}`

### GET /page/{page_id}
Listar blocos de uma página.

**Request:**
```bash
curl http://localhost:8000/api/v1/blocks/page/{page_id} \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "page_id": "uuid",
    "type": "heading1",
    "content": {"text": "Introdução", "level": 1},
    "order": 0,
    "created_at": "2025-11-29T10:00:00",
    "updated_at": "2025-11-29T10:00:00"
  },
  {
    "id": "uuid",
    "page_id": "uuid",
    "type": "paragraph",
    "content": {"text": "Parágrafo de exemplo"},
    "order": 1,
    "created_at": "2025-11-29T10:00:00",
    "updated_at": "2025-11-29T10:00:00"
  }
]
```

### GET /{block_id}
Obter detalhes de um bloco.

**Request:**
```bash
curl http://localhost:8000/api/v1/blocks/{block_id} \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "page_id": "uuid",
  "parent_block_id": null,
  "type": "paragraph",
  "content": {"text": "Conteúdo"},
  "order": 0,
  "created_at": "2025-11-29T10:00:00",
  "updated_at": "2025-11-29T10:00:00"
}
```

### PATCH /{block_id}
Atualizar conteúdo do bloco.

**Request:**
```bash
curl -X PATCH http://localhost:8000/api/v1/blocks/{block_id} \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "type": "heading1",
    "content": {
      "text": "Novo Título",
      "level": 1
    }
  }'
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "type": "heading1",
  "content": {"text": "Novo Título", "level": 1},
  "updated_at": "2025-11-29T11:00:00",
  ...
}
```

### PATCH /{block_id}/move
Reordenar bloco.

**Request:**
```bash
curl -X PATCH http://localhost:8000/api/v1/blocks/{block_id}/move \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{"new_order": 5}'
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "order": 5,
  ...
}
```

### DELETE /{block_id}
Deletar bloco.

**Request:**
```bash
curl -X DELETE http://localhost:8000/api/v1/blocks/{block_id} \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

**Response:** `204 No Content`

---

## 🔑 Autenticação

Todos os endpoints (exceto `/health`, `/`, `/register` e `/login`) requerem autenticação JWT.

### Header
```
Authorization: Bearer {access_token}
```

### Tokens
- **Access Token**: Expira em 15 minutos
- **Refresh Token**: Expira em 7 dias

### Fluxo
1. Registrar ou fazer login → Recebe tokens
2. Usar `access_token` em todas as requisições
3. Quando expirar, usar `/refresh` com `refresh_token`
4. Ao fazer logout, enviar `refresh_token` para blacklist

---

## 📊 Códigos de Status

| Código | Significado |
|--------|-------------|
| 200 | OK - Sucesso |
| 201 | Created - Recurso criado |
| 204 | No Content - Sucesso sem resposta |
| 400 | Bad Request - Dados inválidos |
| 401 | Unauthorized - Token inválido/expirado |
| 403 | Forbidden - Sem permissão |
| 404 | Not Found - Recurso não encontrado |
| 422 | Validation Error - Erro de validação Pydantic |
| 500 | Internal Server Error - Erro no servidor |

---

## 🧪 Testar no Swagger

Acesse `http://localhost:8000/docs` e:

1. Clique em **"Authorize"** no topo
2. Registre-se ou faça login
3. Copie o `access_token`
4. Cole no campo e clique em **"Authorize"**
5. Todos os endpoints estarão desbloqueados

---

**Desenvolvido por Bruno Sousa**  
GitHub: [@brusodev](https://github.com/brusodev)
