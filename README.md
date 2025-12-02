# 📝 Notion Clone

Clone completo do Notion com backend FastAPI e frontend React (em desenvolvimento).

---

## 🎯 Sobre o Projeto

Aplicação web que replica as funcionalidades principais do Notion:
- Sistema de workspaces
- Páginas hierárquicas
- Blocos de conteúdo flexíveis
- Edição em tempo real (planejado)
- Colaboração multi-usuário

---

## 🏗️ Estrutura do Repositório

```
notion-clone/
├── backend/          # API FastAPI + PostgreSQL ✅ CONCLUÍDO
│   ├── app/
│   ├── alembic/
│   ├── tests/
│   └── [docs]/
└── frontend/         # React + TypeScript (em desenvolvimento)
    └── [a definir]
```

---

## ✅ Backend - Concluído

### Status: **Production Ready** 🚀

- ✅ 22 endpoints REST implementados
- ✅ 21/22 testes passaram (95.5%)
- ✅ Autenticação JWT completa
- ✅ Sistema de workspaces
- ✅ Páginas hierárquicas
- ✅ Blocos de conteúdo JSONB
- ✅ Migrations Alembic
- ✅ SQLite (dev) + PostgreSQL (prod)
- ✅ Documentação Swagger/ReDoc
- ✅ Pronto para Railway

### 📚 Documentação Backend

Navegue para `backend/` e consulte:

| Arquivo | Descrição |
|---------|-----------|
| [README.md](backend/README.md) | Documentação principal |
| [QUICK_START.md](backend/QUICK_START.md) | Comandos rápidos |
| [API_ENDPOINTS.md](backend/API_ENDPOINTS.md) | Referência completa de endpoints |
| [DEPLOY_RAILWAY.md](backend/DEPLOY_RAILWAY.md) | Guia de deploy no Railway |
| [PROJETO_RESUMO.md](backend/PROJETO_RESUMO.md) | Resumo executivo do projeto |
| [TESTE_RESULTS_FINAL.md](backend/TESTE_RESULTS_FINAL.md) | Resultados dos testes |

### 🚀 Quick Start Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux/Mac

# Instalar dependências
pip install -r requirements.txt

# Aplicar migrations
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload

# Acessar documentação
# http://localhost:8000/docs
```

### 🧪 Testar API

```bash
# Executar todos os testes
python test_api.py

# Resultado esperado: 21/22 passando (95.5%)
```

---

## 🎨 Frontend - Em Desenvolvimento

### Status: **Aguardando Início** ⏳

Planejado para:
- React 18+ com TypeScript
- Vite como bundler
- TailwindCSS para estilização
- React Query para gerenciamento de estado
- Editor de blocos customizado

---

## 🛠️ Tecnologias

### Backend
- FastAPI 0.109.0
- SQLAlchemy 2.0.25
- PostgreSQL 15+ / SQLite
- Alembic 1.13.1
- JWT (python-jose)
- Bcrypt 4.0.1
- Pydantic V2
- Uvicorn

### Frontend (Planejado)
- React 18+
- TypeScript
- Vite
- TailwindCSS
- React Query
- Zustand

---

## 📡 API Endpoints

### Autenticação (6)
- POST `/api/v1/auth/register` - Registro
- POST `/api/v1/auth/login` - Login
- POST `/api/v1/auth/refresh` - Renovar token
- POST `/api/v1/auth/logout` - Logout
- GET `/api/v1/auth/me` - Perfil
- PATCH `/api/v1/auth/me` - Atualizar perfil

### Workspaces (5)
- GET `/api/v1/workspaces/` - Listar
- POST `/api/v1/workspaces/` - Criar
- GET `/api/v1/workspaces/{id}` - Detalhes
- PATCH `/api/v1/workspaces/{id}` - Atualizar
- DELETE `/api/v1/workspaces/{id}` - Deletar

### Páginas (7)
- GET `/api/v1/pages/` - Listar
- POST `/api/v1/pages/` - Criar
- GET `/api/v1/pages/{id}` - Detalhes
- PATCH `/api/v1/pages/{id}` - Atualizar
- DELETE `/api/v1/pages/{id}` - Arquivar
- GET `/api/v1/pages/tree` - Árvore hierárquica
- POST `/api/v1/pages/{id}/duplicate` - Duplicar

### Blocos (6)
- POST `/api/v1/blocks/` - Criar
- GET `/api/v1/blocks/page/{page_id}` - Listar
- GET `/api/v1/blocks/{id}` - Detalhes
- PATCH `/api/v1/blocks/{id}` - Atualizar
- PATCH `/api/v1/blocks/{id}/move` - Reordenar
- DELETE `/api/v1/blocks/{id}` - Deletar

**Total**: 22 endpoints + 2 health checks

---

## 🗄️ Modelo de Dados

```
User
├── id (UUID)
├── email (unique)
├── password_hash
├── name
└── workspaces[]

Workspace
├── id (UUID)
├── name
├── icon
├── owner → User
└── pages[]

Page
├── id (UUID)
├── workspace → Workspace
├── parent → Page (hierarquia)
├── title
├── icon
├── is_archived
└── blocks[]

Block
├── id (UUID)
├── page → Page
├── type (heading, paragraph, code...)
├── content (JSONB)
└── order
```

---

## 🚀 Deploy

### Backend (Railway)

```bash
# Via CLI
npm install -g @railway/cli
railway login
railway init
railway up

# Ou via GitHub
# Push para main → Deploy automático
```

Consulte [DEPLOY_RAILWAY.md](backend/DEPLOY_RAILWAY.md) para instruções detalhadas.

### Frontend (Vercel - Planejado)

Em desenvolvimento.

---

## 📊 Status do Projeto

| Componente | Status | Progresso |
|------------|--------|-----------|
| Backend API | ✅ Concluído | 100% |
| Banco de Dados | ✅ Pronto | 100% |
| Testes | ✅ Validado | 95.5% |
| Documentação | ✅ Completa | 100% |
| Deploy Backend | 🟡 Pronto | - |
| Frontend | ⏳ Aguardando | 0% |
| Deploy Frontend | ⏳ Aguardando | 0% |

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'Adiciona nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra um Pull Request

---

## 📝 Licença

Este projeto está sob a licença MIT.

---

## 👨‍💻 Autor

**Bruno Vargas**
- GitHub: [@brusodev](https://github.com/brusodev)

---

## 🙏 Agradecimentos

- [FastAPI](https://fastapi.tiangolo.com/) - Framework incrível
- [Railway](https://railway.app/) - Deploy simplificado
- [Notion](https://notion.so/) - Inspiração

---

**Desenvolvido com ❤️ por Bruno Vargas**
