#!/usr/bin/env python3
"""Teste completo local de todas as APIs"""

import requests
from datetime import datetime
import time

BASE_URL = "http://localhost:8001"

def test_all_apis():
    print("=" * 80)
    print("Teste Completo de Todas as APIs (Local)")
    print("=" * 80)

    # 1. Health Check
    print("\n1. Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"   [OK] Status: {response.status_code}")
    except Exception as e:
        print(f"   [FAIL] {e}")

    # 2. Registro
    print("\n2. Registrando usuario...")
    email = f"test{int(time.time())}@test.com"

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json={
                "email": email,
                "password": "Test123!@#",
                "name": "Test User"
            },
            timeout=10
        )
        if response.status_code == 201:
            tokens = response.json()
            access_token = tokens["access_token"]
            print(f"   [OK] Usuario registrado: {email}")
        else:
            print(f"   [FAIL] Status: {response.status_code}")
            return
    except Exception as e:
        print(f"   [FAIL] {e}")
        return

    headers = {"Authorization": f"Bearer {access_token}"}

    # 3. Listar Workspaces
    print("\n3. Listando workspaces...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/workspaces/", headers=headers, timeout=10)
        if response.status_code == 200:
            workspaces = response.json()
            workspace_id = workspaces[0]["id"]
            print(f"   [OK] Workspaces encontrados: {len(workspaces)}")
        else:
            print(f"   [FAIL] Status: {response.status_code}")
            return
    except Exception as e:
        print(f"   [FAIL] {e}")
        return

    # 4. Criar Pagina
    print("\n4. Criando pagina...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/pages/",
            headers=headers,
            json={
                "workspace_id": workspace_id,
                "title": "Pagina de Teste de Busca",
                "icon": "search"
            },
            timeout=10
        )
        if response.status_code == 201:
            page = response.json()
            page_id = page["id"]
            print(f"   [OK] Pagina criada: {page['title']}")
        else:
            print(f"   [FAIL] Status: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"   [FAIL] {e}")
        return

    # 5. Criar Blocos
    print("\n5. Criando blocos...")
    blocks_created = 0

    try:
        # Bloco 1
        response = requests.post(
            f"{BASE_URL}/api/v1/blocks/",
            headers=headers,
            json={
                "page_id": page_id,
                "type": "paragraph",
                "content": {"text": "Este e um teste de busca em portugues com programacao."}
            },
            timeout=10
        )
        if response.status_code == 201:
            blocks_created += 1

        # Bloco 2
        response = requests.post(
            f"{BASE_URL}/api/v1/blocks/",
            headers=headers,
            json={
                "page_id": page_id,
                "type": "paragraph",
                "content": {"text": "Python e JavaScript sao linguagens poderosas para desenvolvimento."}
            },
            timeout=10
        )
        if response.status_code == 201:
            blocks_created += 1

        print(f"   [OK] Blocos criados: {blocks_created}")
    except Exception as e:
        print(f"   [FAIL] {e}")

    # 6. Testar Busca
    print("\n6. Testando busca...")
    print("-" * 80)

    # 6.1. Busca basica
    print("\n  6.1. Busca por 'teste'")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/search/",
            headers=headers,
            json={
                "query": "teste",
                "workspace_id": workspace_id,
                "limit": 10
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print(f"       [OK] Total: {result['total']}, Tempo: {result['execution_time_ms']:.2f}ms")

            if result['results']:
                first = result['results'][0]
                print(f"       Titulo: {first['page_title']}")
                print(f"       Rank: {first['rank']:.4f}")
                print(f"       Matched in: {first['matched_in']}")
        else:
            print(f"       [FAIL] Status: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"       [FAIL] {e}")

    # 6.2. Busca com filtro
    print("\n  6.2. Busca com filtro 'pages_only'")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/search/",
            headers=headers,
            json={
                "query": "busca",
                "workspace_id": workspace_id,
                "type_filter": "pages_only",
                "limit": 10
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print(f"       [OK] Total: {result['total']}, Tempo: {result['execution_time_ms']:.2f}ms")
        else:
            print(f"       [FAIL] Status: {response.status_code}")
    except Exception as e:
        print(f"       [FAIL] {e}")

    # 6.3. Stemming portugues
    print("\n  6.3. Teste de stemming portugues")
    print("       Buscando 'programar' para encontrar 'programacao'")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/search/",
            headers=headers,
            json={
                "query": "programar",
                "workspace_id": workspace_id,
                "limit": 10
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print(f"       [OK] Total: {result['total']}, Tempo: {result['execution_time_ms']:.2f}ms")
            if result['total'] > 0:
                print("       [OK] Stemming portugues funcionando!")
        else:
            print(f"       [FAIL] Status: {response.status_code}")
    except Exception as e:
        print(f"       [FAIL] {e}")

    # 6.4. Busca em blocos
    print("\n  6.4. Busca por 'python' (deve encontrar no bloco)")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/search/",
            headers=headers,
            json={
                "query": "python",
                "workspace_id": workspace_id,
                "limit": 10
            },
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            print(f"       [OK] Total: {result['total']}, Tempo: {result['execution_time_ms']:.2f}ms")

            if result['results'] and result['results'][0]['matched_blocks']:
                print(f"       [OK] Encontrou em blocos: {len(result['results'][0]['matched_blocks'])} blocos")
        else:
            print(f"       [FAIL] Status: {response.status_code}")
    except Exception as e:
        print(f"       [FAIL] {e}")

    print("\n" + "=" * 80)
    print("Testes Concluidos!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_all_apis()
    except KeyboardInterrupt:
        print("\nTestes interrompidos")
    except Exception as e:
        print(f"\nErro: {e}")
        import traceback
        traceback.print_exc()
