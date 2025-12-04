"""
Script para criar as tabelas do banco de dados manualmente
Execute: railway run python create_tables.py
"""

import sys
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import Base
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.models.page import Page
from app.models.block import Block

def create_tables():
    """Cria todas as tabelas no banco de dados"""
    print("=" * 60)
    print("CRIAÇÃO DE TABELAS - NOTION CLONE")
    print("=" * 60)
    print()

    # Criar engine
    print(f"1. Conectando ao banco de dados...")
    print(f"   Database URL: {settings.DATABASE_URL[:50]}...")

    try:
        engine = create_engine(settings.DATABASE_URL)

        # Testar conexão
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("   ✓ Conexão estabelecida com sucesso!")
    except Exception as e:
        print(f"   ✗ Erro ao conectar: {e}")
        sys.exit(1)

    print()
    print("2. Criando tabelas...")
    print(f"   Modelos encontrados: {len(Base.metadata.tables)} tabelas")

    for table_name in Base.metadata.tables.keys():
        print(f"   - {table_name}")

    try:
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        print()
        print("   ✓ Todas as tabelas foram criadas com sucesso!")
    except Exception as e:
        print(f"   ✗ Erro ao criar tabelas: {e}")
        sys.exit(1)

    print()
    print("3. Verificando tabelas criadas...")

    try:
        with engine.connect() as conn:
            # Verificar tabelas no PostgreSQL
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))

            tables = [row[0] for row in result]

            if tables:
                print(f"   ✓ {len(tables)} tabela(s) encontrada(s):")
                for table in tables:
                    print(f"     - {table}")
            else:
                print("   ⚠ Nenhuma tabela encontrada!")
    except Exception as e:
        print(f"   ✗ Erro ao verificar tabelas: {e}")
        sys.exit(1)

    print()
    print("=" * 60)
    print("✓ PROCESSO CONCLUÍDO COM SUCESSO!")
    print("=" * 60)

if __name__ == "__main__":
    create_tables()
