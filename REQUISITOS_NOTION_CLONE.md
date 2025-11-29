# Requisitos do Projeto - Clone do Notion

## 1. Visão Geral do Projeto

### 1.1 Objetivo
Desenvolver um clone funcional do Notion com funcionalidades essenciais de gerenciamento de documentos, editor de blocos e colaboração.

### 1.2 Stack Tecnológica
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React 18
- **Banco de Dados**: PostgreSQL
- **Cache**: Redis
- **Hospedagem**: Railway
- **Autenticação**: JWT

---

## 2. Requisitos Funcionais

### 2.1 Autenticação e Usuários
- [ ] RF001: Sistema de registro de usuários com email e senha
- [ ] RF002: Login com JWT (access token e refresh token)
- [ ] RF003: Logout e invalidação de tokens
- [ ] RF004: Recuperação de senha via email
- [ ] RF005: Perfil de usuário com avatar e informações básicas

### 2.2 Workspaces (Espaços de Trabalho)
- [ ] RF006: Criar workspace pessoal automaticamente no registro
- [ ] RF007: Usuário pode criar múltiplos workspaces
- [ ] RF008: Convidar membros para workspace (via email)
- [ ] RF009: Gerenciar permissões (owner, editor, viewer)
- [ ] RF010: Listar todos os workspaces do usuário

### 2.3 Páginas
- [ ] RF011: Criar página em branco
- [ ] RF012: Criar página com template
- [ ] RF013: Editar título da página
- [ ] RF014: Adicionar ícone emoji à página
- [ ] RF015: Adicionar imagem de capa à página
- [ ] RF016: Criar hierarquia de páginas (páginas filhas)
- [ ] RF017: Mover páginas (drag & drop na sidebar)
- [ ] RF018: Duplicar página
- [ ] RF019: Arquivar página
- [ ] RF020: Deletar página permanentemente
- [ ] RF021: Restaurar página arquivada
- [ ] RF022: Buscar páginas por título/conteúdo
- [ ] RF023: Favoritar páginas
- [ ] RF024: Histórico de versões da página

### 2.4 Blocos de Conteúdo
- [ ] RF025: **Texto**
  - Parágrafo simples
  - Heading 1, 2, 3
  - Lista com marcadores
  - Lista numerada
  - Lista de tarefas (checkbox)
  - Quote (citação)
- [ ] RF026: **Mídia**
  - Upload de imagens
  - Embed de vídeos (YouTube, Vimeo)
  - Upload de arquivos
- [ ] RF027: **Estrutura**
  - Divider (linha divisória)
  - Callout (caixa de destaque)
  - Toggle list (bloco retrátil)
  - Colunas (layout em 2-3 colunas)
- [ ] RF028: **Avançado**
  - Bloco de código com syntax highlight
  - Tabela simples
  - Embed de links (preview)
  - Banco de dados inline (futuro)

### 2.5 Edição de Blocos
- [ ] RF029: Adicionar novo bloco com "/" (slash commands)
- [ ] RF030: Deletar bloco
- [ ] RF031: Duplicar bloco
- [ ] RF032: Mover bloco (drag & drop)
- [ ] RF033: Converter tipo de bloco
- [ ] RF034: Indentar bloco (criar hierarquia)
- [ ] RF035: Formatar texto (negrito, itálico, sublinhado, código inline)
- [ ] RF036: Adicionar links no texto
- [ ] RF037: Mencionar usuários (@mention)

### 2.6 Colaboração em Tempo Real
- [ ] RF038: Sincronização de edições em tempo real via WebSocket
- [ ] RF039: Indicador de presença (quem está visualizando a página)
- [ ] RF040: Cursor colaborativo (ver onde outros estão editando)
- [ ] RF041: Sistema de comentários em blocos
- [ ] RF042: Notificações de @menções

### 2.7 Compartilhamento
- [ ] RF043: Compartilhar página via link público
- [ ] RF044: Controlar permissões de compartilhamento (view, comment, edit)
- [ ] RF045: Desabilitar compartilhamento público
- [ ] RF046: Exportar página (Markdown, PDF, HTML)

---

## 3. Requisitos Não Funcionais

### 3.1 Performance
- RNF001: Tempo de resposta da API < 200ms para operações comuns
- RNF002: Carregar página com até 100 blocos em < 1 segundo
- RNF003: Sincronização WebSocket com latência < 100ms
- RNF004: Suportar até 10 usuários simultâneos editando a mesma página

### 3.2 Segurança
- RNF005: Senhas hasheadas com bcrypt (salt rounds >= 12)
- RNF006: Tokens JWT com expiração (access: 15min, refresh: 7 dias)
- RNF007: Rate limiting em endpoints de autenticação
- RNF008: Validação de permissões em todas as rotas
- RNF009: CORS configurado apenas para domínios permitidos
- RNF010: Sanitização de inputs para prevenir XSS

### 3.3 Escalabilidade
- RNF011: Arquitetura preparada para horizontal scaling
- RNF012: Cache Redis para queries frequentes
- RNF013: Pagination em listagens (máximo 50 itens por página)
- RNF014: Lazy loading de blocos em páginas grandes

### 3.4 Disponibilidade
- RNF015: Sistema deve ter 99% de uptime
- RNF016: Backup automático do banco de dados (diário)
- RNF017: Health check endpoint para monitoramento

### 3.5 Usabilidade
- RNF018: Interface responsiva (mobile, tablet, desktop)
- RNF019: Suporte a atalhos de teclado
- RNF020: Feedback visual para todas as ações
- RNF021: Sistema de undo/redo

### 3.6 Manutenibilidade
- RNF022: Código com type hints (Python) e TypeScript (React)
- RNF023: Cobertura de testes >= 80%
- RNF024: Documentação automática da API (OpenAPI/Swagger)
- RNF025: Logs estruturados para debugging

---

## 4. Modelo de Dados

### 4.1 Entidades Principais

#### User
```
- id: UUID (PK)
- email: String (unique)
- password_hash: String
- name: String
- avatar_url: String (nullable)
- created_at: DateTime
- updated_at: DateTime
```

#### Workspace
```
- id: UUID (PK)
- name: String
- icon: String (nullable)
- owner_id: UUID (FK -> User)
- created_at: DateTime
- updated_at: DateTime
```

#### WorkspaceMember
```
- id: UUID (PK)
- workspace_id: UUID (FK -> Workspace)
- user_id: UUID (FK -> User)
- role: Enum (owner, editor, viewer)
- joined_at: DateTime
```

#### Page
```
- id: UUID (PK)
- workspace_id: UUID (FK -> Workspace)
- parent_id: UUID (FK -> Page, nullable)
- title: String
- icon: String (nullable)
- cover_image: String (nullable)
- is_archived: Boolean
- is_public: Boolean
- public_slug: String (unique, nullable)
- created_by: UUID (FK -> User)
- created_at: DateTime
- updated_at: DateTime
- order: Integer (para ordenação na sidebar)
```

#### Block
```
- id: UUID (PK)
- page_id: UUID (FK -> Page)
- parent_block_id: UUID (FK -> Block, nullable)
- type: String (paragraph, heading1, image, etc)
- content: JSONB (conteúdo flexível por tipo)
- order: Integer (posição na página)
- created_at: DateTime
- updated_at: DateTime
```

#### Comment
```
- id: UUID (PK)
- block_id: UUID (FK -> Block)
- user_id: UUID (FK -> User)
- content: Text
- is_resolved: Boolean
- created_at: DateTime
- updated_at: DateTime
```

### 4.2 Índices Importantes
- User: email (unique)
- Page: workspace_id, parent_id, public_slug
- Block: page_id, order
- WorkspaceMember: workspace_id + user_id (composite unique)

---

## 5. APIs e Endpoints

### 5.1 Autenticação (`/api/auth`)
```
POST   /register          - Registrar novo usuário
POST   /login             - Login (retorna JWT)
POST   /logout            - Logout
POST   /refresh           - Renovar access token
POST   /forgot-password   - Solicitar recuperação de senha
POST   /reset-password    - Resetar senha com token
GET    /me                - Dados do usuário atual
PATCH  /me                - Atualizar perfil
```

### 5.2 Workspaces (`/api/workspaces`)
```
GET    /                  - Listar workspaces do usuário
POST   /                  - Criar workspace
GET    /{id}              - Detalhes do workspace
PATCH  /{id}              - Atualizar workspace
DELETE /{id}              - Deletar workspace
GET    /{id}/members      - Listar membros
POST   /{id}/members      - Adicionar membro
PATCH  /{id}/members/{user_id} - Atualizar role do membro
DELETE /{id}/members/{user_id} - Remover membro
```

### 5.3 Páginas (`/api/pages`)
```
GET    /                  - Listar páginas do workspace
POST   /                  - Criar página
GET    /{id}              - Detalhes da página + blocos
PATCH  /{id}              - Atualizar metadados da página
DELETE /{id}              - Arquivar página
POST   /{id}/duplicate    - Duplicar página
PATCH  /{id}/move         - Mover página (mudar parent)
PATCH  /{id}/restore      - Restaurar página arquivada
GET    /{id}/children     - Listar páginas filhas
GET    /public/{slug}     - Acessar página pública
```

### 5.4 Blocos (`/api/blocks`)
```
POST   /                  - Criar bloco
GET    /{id}              - Detalhes do bloco
PATCH  /{id}              - Atualizar conteúdo do bloco
DELETE /{id}              - Deletar bloco
POST   /{id}/duplicate    - Duplicar bloco
PATCH  /{id}/move         - Mover bloco (reordenar)
```

### 5.5 WebSocket (`/ws`)
```
WS     /pages/{page_id}   - Conexão para colaboração em tempo real
```

---

## 6. Configuração Railway

### 6.1 Serviços Necessários
- **Backend API**: FastAPI + Uvicorn
- **PostgreSQL**: Banco de dados principal
- **Redis**: Cache e pub/sub para WebSocket

### 6.2 Variáveis de Ambiente
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Redis
REDIS_URL=redis://host:port

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://seu-frontend.railway.app

# Email (para recuperação de senha)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app

# Upload (S3 ou Cloudinary)
UPLOAD_PROVIDER=cloudinary
CLOUDINARY_CLOUD_NAME=seu-cloud
CLOUDINARY_API_KEY=sua-key
CLOUDINARY_API_SECRET=seu-secret
```

### 6.3 Arquivos Railway
```
railway.json (configuração do projeto)
Procfile ou railway.toml (comandos de start)
```

---

## 7. Fases de Desenvolvimento

### Fase 1 - MVP Backend (2-3 semanas)
- Estrutura do projeto FastAPI
- Autenticação completa (JWT)
- CRUD de Workspaces
- CRUD de Páginas
- CRUD de Blocos básicos (texto)
- Deploy no Railway

### Fase 2 - Frontend Básico (2-3 semanas)
- Setup React + Tailwind
- Páginas de login/registro
- Sidebar com árvore de páginas
- Editor básico de blocos
- Integração com API

### Fase 3 - Recursos Avançados (3-4 semanas)
- WebSocket para colaboração
- Tipos de blocos avançados
- Sistema de permissões
- Upload de arquivos
- Comentários

### Fase 4 - Polimento (1-2 semanas)
- Testes automatizados
- Otimizações de performance
- Melhorias de UX
- Documentação

---

## 8. Critérios de Aceitação

### MVP Mínimo Viável
- [ ] Usuário pode se registrar e fazer login
- [ ] Usuário pode criar workspace pessoal
- [ ] Usuário pode criar e editar páginas
- [ ] Usuário pode adicionar blocos de texto (parágrafo, heading, lista)
- [ ] Páginas têm hierarquia (páginas filhas)
- [ ] Sistema salva automaticamente
- [ ] Interface responsiva básica

### Versão Completa
- [ ] Todos os tipos de blocos implementados
- [ ] Colaboração em tempo real funcionando
- [ ] Sistema de permissões robusto
- [ ] Compartilhamento público
- [ ] Performance otimizada
- [ ] Testes automatizados com 80%+ cobertura

---

## 9. Riscos e Mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Complexidade do editor de blocos | Alto | Média | Usar biblioteca pronta (Slate.js/TipTap) |
| Performance com muitos blocos | Alto | Média | Pagination, lazy loading, virtualization |
| Sincronização WebSocket | Médio | Alta | Usar operational transforms ou CRDT |
| Custos de hospedagem | Médio | Baixa | Monitorar uso, otimizar queries |
| Segurança de dados | Alto | Baixa | Auditorias, testes de penetração |

---

## 10. Referências e Recursos

### Documentação
- FastAPI: https://fastapi.tiangolo.com/
- Railway: https://docs.railway.app/
- PostgreSQL: https://www.postgresql.org/docs/

### Bibliotecas Recomendadas
- **Backend**: SQLAlchemy, Alembic, python-jose, passlib, python-multipart
- **Frontend**: Slate.js/TipTap, React Query, Zustand, Tailwind CSS

### Inspirações
- Notion.so (referência principal)
- Coda.io (alternativas de funcionalidades)
- Craft.do (UX de editor)
