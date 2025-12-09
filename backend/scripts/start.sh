#!/bin/bash

# Script de inicialização para o Railway
# Executa migrations e inicia o servidor

set -e  # Parar se houver erro

echo "========================================="
echo "Iniciando Notion Clone API"
echo "========================================="

echo "1. Verificando conexão com o banco..."
python -c "from app.core.database import engine; engine.connect()" && echo "✓ Banco conectado com sucesso"

echo ""
echo "2. Executando migrations do Alembic..."
alembic upgrade head && echo "✓ Migrations executadas com sucesso"

echo ""
echo "3. Iniciando servidor Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
