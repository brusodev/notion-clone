# ⚡ Quick Start - Notion Clone Backend

Comandos rápidos para desenvolvimento do backend.

---

## 🚀 Iniciar Desenvolvimento

### 1. Ativar ambiente virtual
```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
.\venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

### 2. Instalar/atualizar dependências
```bash
pip install -r requirements.txt
```

### 3. Iniciar servidor
```bash
# Desenvolvimento (auto-reload)
uvicorn app.main:app --reload

# Produção
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Executar testes
```bash
python test_api.py
```

---

## 🗄️ Banco de Dados

### Criar/aplicar migrations
```bash
# Criar nova migration
alembic revision --autogenerate -m "descrição"

# Aplicar migrations
alembic upgrade head

# Reverter última migration
alembic downgrade -1

# Reverter todas
alembic downgrade base
```

### Resetar banco SQLite
```bash
# Windows PowerShell
Remove-Item notion_clone.db -ErrorAction SilentlyContinue
alembic upgrade head

# Linux/Mac
rm -f notion_clone.db
alembic upgrade head
```

---

## 🧪 Testes

### Teste completo
```bash
python test_api.py
```

### Testar endpoint específico
```bash
# Health check
curl http://localhost:8000/health

# Registrar usuário
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"teste@notion.com","password":"senha123","name":"Teste"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"teste@notion.com","password":"senha123"}'
```

---

## 📚 Documentação

### Swagger UI (Interativa)
```
http://localhost:8000/docs
```

### ReDoc
```
http://localhost:8000/redoc
```

### OpenAPI JSON
```
http://localhost:8000/openapi.json
```

---

## 🔧 Utilitários

### Gerar SECRET_KEY
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Ver rotas disponíveis
```python
from app.main import app
for route in app.routes:
    print(f"{route.methods} {route.path}")
```

### Conectar ao banco SQLite
```bash
# Windows (se tiver sqlite3.exe)
sqlite3 notion_clone.db

# Python
python -c "import sqlite3; conn = sqlite3.connect('notion_clone.db'); print(conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall())"
```

---

## 🐛 Debug

### Ver logs detalhados
```bash
uvicorn app.main:app --reload --log-level debug
```

### Testar imports
```python
python -c "from app.main import app; print('OK')"
```

### Ver versão Python
```bash
python --version
```

### Ver pacotes instalados
```bash
pip list
```

---

## 🚀 Deploy Railway

### Via CLI
```bash
# Instalar CLI
npm install -g @railway/cli

# Login
railway login

# Inicializar
railway init

# Deploy
railway up

# Ver logs
railway logs --tail

# Abrir dashboard
railway open
```

### Via Git
```bash
git add .
git commit -m "Deploy to Railway"
git push origin main
```

---

## 🔄 Git

### Commit padrão
```bash
git add .
git commit -m "feat: descrição da feature"
git push origin main
```

### Tipos de commit
- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Documentação
- `test:` - Testes
- `refactor:` - Refatoração
- `style:` - Formatação
- `chore:` - Manutenção

---

## 📊 Monitoramento

### Ver processos Python
```bash
# Windows PowerShell
Get-Process python

# Linux/Mac
ps aux | grep python
```

### Matar servidor
```bash
# Windows PowerShell
Get-Process | Where-Object {$_.ProcessName -like "*uvicorn*"} | Stop-Process -Force

# Linux/Mac
pkill -f uvicorn
```

---

## 🔐 Segurança

### Verificar variáveis de ambiente
```bash
# Windows PowerShell
Get-Content .env

# Linux/Mac
cat .env
```

### Exemplo .env
```env
DATABASE_URL=sqlite:///./notion_clone.db
SECRET_KEY=seu-secret-key-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

---

## 📦 Dependências

### Adicionar nova dependência
```bash
pip install nome-pacote
pip freeze > requirements.txt
```

### Atualizar todas
```bash
pip install --upgrade -r requirements.txt
```

### Verificar outdated
```bash
pip list --outdated
```

---

## 🎯 Atalhos Úteis

### Windows PowerShell
```powershell
# Alias para ativar venv
Set-Alias -Name venv -Value ".\venv\Scripts\Activate.ps1"

# Alias para iniciar servidor
function Start-Server { uvicorn app.main:app --reload }
Set-Alias -Name dev -Value Start-Server

# Alias para testes
function Run-Tests { python test_api.py }
Set-Alias -Name test -Value Run-Tests
```

### Linux/Mac (.bashrc ou .zshrc)
```bash
alias venv="source venv/bin/activate"
alias dev="uvicorn app.main:app --reload"
alias test="python test_api.py"
```

---

## 📋 Checklist Diário

Antes de começar a trabalhar:
- [ ] Ativar ambiente virtual
- [ ] `git pull origin main`
- [ ] Verificar se servidor inicia sem erros
- [ ] Rodar testes para validar funcionalidade

Antes de fazer commit:
- [ ] Executar `python test_api.py`
- [ ] Verificar se não há erros no código
- [ ] Atualizar documentação se necessário
- [ ] Commit com mensagem descritiva

---

## 🆘 Problemas Comuns

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Port 8000 already in use"
```bash
# Windows
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### "Database is locked" (SQLite)
```bash
# Fechar todas as conexões e reiniciar servidor
Get-Process python | Stop-Process -Force
uvicorn app.main:app --reload
```

### Migrations não aplicam
```bash
# Resetar Alembic
alembic downgrade base
alembic upgrade head
```

---

## 💡 Dicas

1. **Use o Swagger UI** (`/docs`) para testar endpoints rapidamente
2. **Mantenha o .env atualizado** mas nunca faça commit dele
3. **Execute testes regularmente** para detectar bugs cedo
4. **Use migrations** para qualquer mudança no banco
5. **Leia os logs** quando algo não funcionar

---

**Desenvolvido por Bruno Sousa**  
GitHub: [@brusodev](https://github.com/brusodev)
