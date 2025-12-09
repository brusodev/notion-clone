# 🚀 Deploy no Railway - Notion Clone Backend

Guia completo para fazer deploy da API do Notion Clone no Railway.

---

## 📋 Pré-requisitos

- ✅ Conta no [Railway](https://railway.app)
- ✅ Código do backend funcionando localmente
- ✅ Git instalado e configurado
- ✅ Repositório no GitHub (opcional, mas recomendado)

---

## 🎯 Passo a Passo

### 1️⃣ Preparar o Projeto

Certifique-se de que os seguintes arquivos estão no diretório `backend/`:

#### `Procfile` ✅
```
web: alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### `requirements.txt` ✅
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
alembic==1.13.1
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.0.1
python-multipart==0.0.6
email-validator==2.1.0
redis==5.0.1
psycopg2-binary==2.9.9
```

#### `.env.example` (criar)
```env
DATABASE_URL=postgresql://user:password@host:5432/database
SECRET_KEY=seu-secret-key-super-seguro-aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

---

### 2️⃣ Criar Conta no Railway

1. Acesse [railway.app](https://railway.app)
2. Clique em **"Start a New Project"**
3. Faça login com GitHub (recomendado)

---

### 3️⃣ Criar Novo Projeto

#### Opção A: Deploy via GitHub (Recomendado)

1. Push seu código para o GitHub:
```bash
git add .
git commit -m "Preparar para deploy no Railway"
git push origin main
```

2. No Railway:
   - Clique em **"New Project"**
   - Selecione **"Deploy from GitHub repo"**
   - Escolha o repositório `notion-clone`
   - Selecione a pasta `backend` como root directory

#### Opção B: Deploy via Railway CLI

1. Instale o Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login no Railway:
```bash
railway login
```

3. Inicialize o projeto:
```bash
cd backend
railway init
```

4. Deploy:
```bash
railway up
```

---

### 4️⃣ Adicionar PostgreSQL

1. No dashboard do Railway, clique em **"New"**
2. Selecione **"Database"** → **"PostgreSQL"**
3. O Railway criará automaticamente:
   - ✅ Instância PostgreSQL
   - ✅ Variável `DATABASE_URL` configurada automaticamente

---

### 5️⃣ Configurar Variáveis de Ambiente

No Railway Dashboard, vá em **"Variables"** e adicione:

#### Variáveis Obrigatórias:

```env
SECRET_KEY=<gere-com-comando-abaixo>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
BACKEND_CORS_ORIGINS=["https://seu-frontend.vercel.app"]
```

#### Gerar SECRET_KEY:
```bash
# No terminal local:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Variáveis Automáticas (Railway configura):
- ✅ `DATABASE_URL` - URL do PostgreSQL
- ✅ `PORT` - Porta do servidor

---

### 6️⃣ Configurar Build e Deploy

1. No Railway, vá em **"Settings"**
2. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: *(deixe vazio, Railway detecta automaticamente)*
   - **Start Command**: `web: alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

### 7️⃣ Deploy Automático

1. O Railway iniciará o deploy automaticamente
2. Acompanhe os logs em **"Deployments"**
3. Aguarde a mensagem: **"Deployment successful"**

---

### 8️⃣ Obter URL da API

1. No Railway Dashboard, vá em **"Settings"**
2. Clique em **"Generate Domain"**
3. Sua API estará disponível em: `https://seu-projeto.up.railway.app`

---

## ✅ Verificar Deploy

### 1. Health Check
```bash
curl https://seu-projeto.up.railway.app/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "project": "Notion Clone API"
}
```

### 2. Documentação
Acesse: `https://seu-projeto.up.railway.app/docs`

### 3. Testar Registro
```bash
curl -X POST "https://seu-projeto.up.railway.app/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@exemplo.com",
    "password": "senha123",
    "name": "Usuário Teste"
  }'
```

---

## 🔧 Comandos Úteis Railway CLI

```bash
# Ver logs em tempo real
railway logs

# Abrir dashboard no navegador
railway open

# Ver variáveis de ambiente
railway variables

# Conectar ao PostgreSQL
railway connect postgres

# Executar comando no servidor
railway run <comando>

# Executar migrations manualmente
railway run alembic upgrade head
```

---

## 🐛 Troubleshooting

### Erro: "Module not found"
**Solução**: Verifique se todas as dependências estão em `requirements.txt`

### Erro: "Database connection failed"
**Solução**: Verifique se o PostgreSQL foi adicionado ao projeto

### Erro: "Port already in use"
**Solução**: Use `$PORT` em vez de porta fixa no código

### Migrations não executam
**Solução**: 
1. Verifique se `alembic upgrade head` está no `Procfile`
2. Execute manualmente: `railway run alembic upgrade head`

### CORS bloqueando frontend
**Solução**: Adicione a URL do frontend em `BACKEND_CORS_ORIGINS`:
```env
BACKEND_CORS_ORIGINS=["https://meu-frontend.vercel.app","http://localhost:3000"]
```

---

## 📊 Monitoramento

### Logs
```bash
railway logs --tail
```

### Métricas
- Acesse o dashboard do Railway
- Veja CPU, memória e requisições em tempo real

### Alertas
Configure notificações no Railway para:
- Deploy failed
- High memory usage
- Database errors

---

## 💰 Custos

- **Hobby Plan (Grátis)**:
  - $5 de crédito/mês
  - Suficiente para desenvolvimento
  - Até 500 horas/mês

- **Developer Plan ($5/mês)**:
  - $5 de crédito inicial + $5/mês adicionais
  - Sem limites de horas
  - Recomendado para produção

---

## 🔄 Atualizações

### Deploy Automático (GitHub)
Cada `git push` para a branch `main` fará deploy automático.

### Deploy Manual (CLI)
```bash
railway up
```

### Rollback
```bash
# Ver deployments anteriores
railway status

# Fazer rollback para deployment específico
railway rollback <deployment-id>
```

---

## 🔐 Segurança

### Recomendações:

1. ✅ Use `SECRET_KEY` forte e único
2. ✅ Configure CORS apenas para domínios confiáveis
3. ✅ Nunca commite `.env` para o Git
4. ✅ Use HTTPS sempre (Railway fornece automaticamente)
5. ✅ Rotacione `SECRET_KEY` periodicamente
6. ✅ Monitore logs para atividades suspeitas

---

## 📝 Checklist de Deploy

Antes do deploy em produção:

- [ ] Testes locais passando (22/22)
- [ ] `requirements.txt` atualizado
- [ ] `Procfile` configurado
- [ ] `.env` não está no Git
- [ ] `SECRET_KEY` gerado com segurança
- [ ] CORS configurado corretamente
- [ ] PostgreSQL adicionado ao Railway
- [ ] Variáveis de ambiente configuradas
- [ ] Migrations funcionando
- [ ] Health check respondendo
- [ ] Documentação `/docs` acessível

---

## 🎉 Pronto!

Sua API está no ar! 🚀

URL da API: `https://seu-projeto.up.railway.app`  
Documentação: `https://seu-projeto.up.railway.app/docs`

---

## 📞 Suporte

- **Railway Docs**: https://docs.railway.app
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Issues GitHub**: https://github.com/brusodev/notion-clone/issues

---

**Desenvolvido por Bruno Sousa** 👨‍💻  
GitHub: [@brusodev](https://github.com/brusodev)
