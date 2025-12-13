# 🛠️ Guia de Setup do Ambiente de Desenvolvimento

Este guia detalha como configurar o ambiente de desenvolvimento do backend do Notion Clone.

---

## 📋 Pré-requisitos

- **Python**: 3.11 ou superior
- **PostgreSQL**: 15+ (para produção) ou SQLite (para desenvolvimento)
- **Redis**: 5+ (opcional - para token blacklist)
- **Git**: Para controle de versão

### Verificar versões instaladas:

```bash
python --version    # Python 3.11.0 ou superior
git --version       # Git 2.x.x
```

---

## 🚀 Setup Inicial

### 1. Clonar o Repositório

```bash
git clone https://github.com/brusodev/notion-clone.git
cd notion-clone/backend
```

### 2. Criar Ambiente Virtual

**Windows (PowerShell):**
```powershell
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1

# Se der erro de execução de scripts, execute:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Windows (CMD):**
```cmd
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate
```

**Verificar se o ambiente está ativo:**
```bash
# Você deve ver (venv) no início do prompt
(venv) PS C:\...\backend>
```

### 3. Atualizar pip

```bash
python -m pip install --upgrade pip
```

### 4. Instalar Dependências

```bash
pip install -r requirements.txt
```

**Dependências principais:**
- FastAPI 0.115.5
- SQLAlchemy 2.0.36
- Alembic 1.14.0
- Pydantic 2.10.3
- python-jose 3.3.0
- passlib 4.2.1
- uvicorn 0.32.1
- E mais...

### 5. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env com suas configurações
# No Windows você pode usar: notepad .env
```

**Arquivo `.env` mínimo para desenvolvimento:**
```env
# App
PROJECT_NAME=Notion Clone API
VERSION=1.0.0
API_V1_STR=/api/v1

# Database (SQLite para desenvolvimento local)
DATABASE_URL=sqlite:///./notion_clone.db

# OU PostgreSQL (Railway/produção)
# DATABASE_URL=postgresql://user:password@host:port/database

# JWT (gerar com: openssl rand -hex 32)
SECRET_KEY=ylWDqWuJq8mRmn7LwR0LMxTXkKnF7GVu2lMveSfDnC8
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]

# Frontend URL
FRONTEND_URL=http://localhost:3000

# Redis (opcional - deixe comentado se não tiver)
# REDIS_URL=redis://localhost:6379

# Cloudinary (opcional - deixe comentado se não tiver)
# CLOUDINARY_CLOUD_NAME=seu-cloud-name
# CLOUDINARY_API_KEY=sua-api-key
# CLOUDINARY_API_SECRET=seu-api-secret
```

**Gerar SECRET_KEY:**
```bash
# Windows PowerShell
python -c "import secrets; print(secrets.token_hex(32))"

# Linux/Mac
openssl rand -hex 32
```

### 6. Executar Migrações do Banco

```bash
# Ver migração atual
alembic current

# Executar todas as migrações pendentes
alembic upgrade head

# Ver histórico de migrações
alembic history
```

**Nota**: Se estiver usando SQLite, as tabelas serão criadas automaticamente no arquivo `notion_clone.db`.

### 7. Iniciar o Servidor

```bash
# Modo desenvolvimento (com reload automático)
uvicorn app.main:app --reload

# OU especificar host e porta
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Servidor rodando em:**
- API: http://localhost:8000
- Documentação: http://localhost:8000/docs
- Health check: http://localhost:8000/

---

## 🧪 Executar Testes

### Testes Completos (40 testes)
```bash
python test_all_apis.py
```

### Testes Principais (14 testes)
```bash
python test_core.py
```

**Resultado esperado:**
```
Total de testes: 40
✅ Testes passaram: 40
Taxa de sucesso: 100%
```

---

## 📁 Estrutura do Projeto

```
backend/
├── venv/                    # ⚠️ Ambiente virtual (não commitar)
├── alembic/                 # Migrações do banco
├── app/
│   ├── api/v1/             # Endpoints da API
│   ├── core/               # Configurações e segurança
│   ├── crud/               # Operações no banco
│   ├── models/             # SQLAlchemy models
│   ├── schemas/            # Pydantic schemas
│   └── main.py             # App FastAPI
├── tests/                   # Testes (pytest)
├── .env                     # ⚠️ Variáveis de ambiente (não commitar)
├── .env.example            # Template de .env
├── requirements.txt        # Dependências Python
├── alembic.ini             # Configuração Alembic
├── test_all_apis.py        # Suite de testes completa
└── README.md               # Documentação
```

---

## 🔄 Workflow Diário

### Iniciar o dia:
```bash
cd notion-clone/backend

# Ativar ambiente virtual
# Windows
.\venv\Scripts\Activate.ps1
# Linux/Mac
source venv/bin/activate

# Atualizar dependências (se houve mudanças)
pip install -r requirements.txt

# Executar migrações (se houver novas)
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

### Finalizar o dia:
```bash
# Desativar ambiente virtual
deactivate
```

---

## 🐛 Troubleshooting

### Problema: "venv não reconhecido"
**Solução:**
```bash
# Certifique-se de estar na pasta backend/
cd backend

# Recrie o ambiente virtual
python -m venv venv
```

### Problema: "ModuleNotFoundError"
**Solução:**
```bash
# Verifique se o ambiente está ativo (deve ter (venv) no prompt)
# Se não estiver, ative:
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Reinstale as dependências
pip install -r requirements.txt
```

### Problema: "Erro ao executar scripts PowerShell"
**Solução:**
```powershell
# Execute como administrador
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# OU use o CMD ao invés do PowerShell
venv\Scripts\activate.bat
```

### Problema: "Database não conecta"
**Solução:**
```bash
# Para desenvolvimento local, use SQLite:
DATABASE_URL=sqlite:///./notion_clone.db

# Para Railway/produção, verifique a URL:
# 1. Entre no Railway Dashboard
# 2. Copie a DATABASE_URL do PostgreSQL
# 3. Cole no .env
```

### Problema: "Migrations não aplicam"
**Solução:**
```bash
# Ver status das migrations
alembic current

# Forçar recriação das tabelas (CUIDADO: apaga dados)
# Deletar arquivo notion_clone.db (SQLite)
# E executar:
alembic upgrade head

# OU criar novas tabelas diretamente (sem migrations)
python -c "from app.core.database import engine, Base; from app.models import *; Base.metadata.create_all(engine)"
```

### Problema: "Porta 8000 já em uso"
**Solução:**
```bash
# Use outra porta
uvicorn app.main:app --reload --port 8001

# OU mate o processo na porta 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:8000 | xargs kill -9
```

---

## 🔧 Comandos Úteis

### Alembic (Migrações)
```bash
# Ver migração atual
alembic current

# Ver histórico
alembic history

# Criar nova migração
alembic revision --autogenerate -m "Descrição da mudança"

# Aplicar próxima migração
alembic upgrade +1

# Reverter última migração
alembic downgrade -1

# Aplicar todas as migrações
alembic upgrade head

# Reverter todas as migrações
alembic downgrade base
```

### Pip (Dependências)
```bash
# Listar pacotes instalados
pip list

# Ver pacotes desatualizados
pip list --outdated

# Congelar dependências atuais
pip freeze > requirements.txt

# Instalar pacote específico
pip install nome-do-pacote

# Desinstalar pacote
pip uninstall nome-do-pacote
```

### Python
```bash
# Abrir console interativo
python

# Executar script Python
python nome_do_script.py

# Ver versão do Python
python --version

# Ver path do Python sendo usado
python -c "import sys; print(sys.executable)"
```

---

## 📦 Adicionar Nova Dependência

### Processo:
1. Ativar ambiente virtual
2. Instalar o pacote
3. Atualizar requirements.txt
4. Commitar mudanças

```bash
# 1. Ativar venv
.\venv\Scripts\Activate.ps1

# 2. Instalar pacote
pip install nome-do-pacote

# 3. Atualizar requirements.txt
pip freeze > requirements.txt

# 4. Commitar
git add requirements.txt
git commit -m "feat: adiciona pacote X"
```

---

## 🚀 Deploy (Railway)

### Setup no Railway:
```bash
# 1. Instalar CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Link ao projeto
railway link

# 4. Deploy
git push
```

**Variáveis de ambiente no Railway:**
- `DATABASE_URL` - Automático (PostgreSQL)
- `SECRET_KEY` - Gerar com `openssl rand -hex 32`
- `ALLOWED_ORIGINS` - URL do frontend
- `CLOUDINARY_*` - Credenciais (opcional)

---

## ✅ Checklist de Verificação

Antes de começar a desenvolver, verifique:

- [ ] Python 3.11+ instalado
- [ ] Ambiente virtual criado (`venv/`)
- [ ] Ambiente virtual ativado (`(venv)` no prompt)
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` configurado
- [ ] Banco de dados funcionando (SQLite ou PostgreSQL)
- [ ] Migrações aplicadas (`alembic upgrade head`)
- [ ] Servidor rodando (`uvicorn app.main:app --reload`)
- [ ] API respondendo em http://localhost:8000
- [ ] Documentação acessível em http://localhost:8000/docs
- [ ] Testes passando (`python test_all_apis.py`)

---

## 📚 Recursos Adicionais

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)

---

**Pronto! Seu ambiente está configurado e você pode começar a desenvolver! 🚀**
