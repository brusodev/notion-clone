#!/usr/bin/env python3
"""Teste simples do endpoint de busca em produção"""

import requests
from datetime import datetime
import json

BASE_URL = "https://notion-clone-production-b81a.up.railway.app"

def test_production_search():
    print("=" * 80)
    print("Testando Endpoint de Busca em Produção (Railway)")
    print("=" * 80)

    # 1. Registrar usuário
    print("\n1. Registrando usuário...")
    email = f"searchtest_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com"

    register_response = requests.post(
        f"{BASE_URL}/api/v1/auth/register",
        json={
            "email": email,
            "password": "Test@123",
            "name": "Search Tester"
        },
        timeout=30
    )

    if register_response.status_code != 201:
        print(f"✗ Falha no registro: {register_response.text}")
        return

    tokens = register_response.json()
    access_token = tokens["access_token"]
    print(f"✓ Usuário registrado: {email}")

    # 2. Criar workspace (já é criado automaticamente no registro)
    print("\n2. Listando workspaces...")
    headers = {"Authorization": f"Bearer {access_token}"}

    workspaces_response = requests.get(
        f"{BASE_URL}/api/v1/workspaces/",
        headers=headers,
        timeout=30
    )

    if workspaces_response.status_code != 200:
        print(f"✗ Falha ao listar workspaces: {workspaces_response.text}")
        return

    workspaces = workspaces_response.json()
    if not workspaces:
        print("✗ Nenhum workspace encontrado")
        return

    workspace_id = workspaces[0]["id"]
    print(f"✓ Workspace encontrado: {workspace_id}")

    # 3. Criar página de teste
    print("\n3. Criando página de teste...")
    page_response = requests.post(
        f"{BASE_URL}/api/v1/pages/",
        headers=headers,
        json={
            "workspace_id": workspace_id,
            "title": "Página de Teste para Busca",
            "icon": "🔍"
        },
        timeout=30
    )

    if page_response.status_code != 201:
        print(f"✗ Falha ao criar página: {page_response.text}")
        return

    page = page_response.json()
    print(f"✓ Página criada: {page['title']}")

    # 4. Criar bloco com conteúdo
    print("\n4. Criando bloco com conteúdo...")
    block_response = requests.post(
        f"{BASE_URL}/api/v1/blocks/",
        headers=headers,
        json={
            "page_id": page["id"],
            "type": "paragraph",
            "content": {"text": "Este é um teste de busca full-text em português."}
        },
        timeout=30
    )

    if block_response.status_code == 201:
        print("✓ Bloco criado com sucesso")
    else:
        print(f"⚠ Aviso ao criar bloco: {block_response.status_code}")

    # 5. Aguardar um momento para o índice ser atualizado
    print("\n5. Aguardando indexação...")
    import time
    time.sleep(2)

    # 6. Testar busca
    print("\n6. Testando busca...")
    print("-" * 80)

    # Teste 6.1: Busca básica
    print("\n  6.1. Busca por 'teste'")
    search_response = requests.post(
        f"{BASE_URL}/api/v1/search/",
        headers=headers,
        json={
            "query": "teste",
            "workspace_id": workspace_id,
            "limit": 10
        },
        timeout=30
    )

    print(f"      Status: {search_response.status_code}")

    if search_response.status_code == 200:
        result = search_response.json()
        print(f"      ✓ Total de resultados: {result['total']}")
        print(f"      ✓ Tempo de execução: {result['execution_time_ms']:.2f}ms")

        if result['results']:
            first = result['results'][0]
            print(f"\n      Primeiro resultado:")
            print(f"        - Título: {first['page_title']}")
            print(f"        - Rank: {first['rank']:.4f}")
            print(f"        - Matched in: {first['matched_in']}")
            print(f"        - Highlight: {first['highlight'][:80]}...")
    else:
        print(f"      ✗ Erro: {search_response.text}")

    # Teste 6.2: Busca com filtro
    print("\n  6.2. Busca com filtro 'pages_only'")
    search_filter_response = requests.post(
        f"{BASE_URL}/api/v1/search/",
        headers=headers,
        json={
            "query": "busca",
            "workspace_id": workspace_id,
            "type_filter": "pages_only",
            "limit": 10
        },
        timeout=30
    )

    print(f"      Status: {search_filter_response.status_code}")

    if search_filter_response.status_code == 200:
        result = search_filter_response.json()
        print(f"      ✓ Total de resultados: {result['total']}")
        print(f"      ✓ Tempo de execução: {result['execution_time_ms']:.2f}ms")
    else:
        print(f"      ✗ Erro: {search_filter_response.text}")

    # Teste 6.3: Stemming português
    print("\n  6.3. Teste de stemming português")
    print("      Buscando 'buscar' para encontrar páginas com 'busca'")

    stemming_response = requests.post(
        f"{BASE_URL}/api/v1/search/",
        headers=headers,
        json={
            "query": "buscar",
            "workspace_id": workspace_id,
            "limit": 10
        },
        timeout=30
    )

    print(f"      Status: {stemming_response.status_code}")

    if stemming_response.status_code == 200:
        result = stemming_response.json()
        print(f"      ✓ Total de resultados: {result['total']}")
        print(f"      ✓ Stemming português funcionando!")
    else:
        print(f"      ✗ Erro: {stemming_response.text}")

    print("\n" + "=" * 80)
    print("Testes de Busca Concluídos!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_production_search()
    except Exception as e:
        print(f"\n✗ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
