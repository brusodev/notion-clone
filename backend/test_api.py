"""Script para testar todas as rotas da API"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Variáveis globais para armazenar dados entre testes
test_data = {
    "user": None,
    "access_token": None,
    "refresh_token": None,
    "workspace_id": None,
    "page_id": None,
    "block_id": None
}


def print_test(test_name: str):
    """Imprime cabeçalho do teste"""
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")


def print_result(response: requests.Response):
    """Imprime resultado da requisição"""
    status_emoji = "✅" if response.status_code < 400 else "❌"
    print(f"{status_emoji} Status: {response.status_code}")
    try:
        data = response.json()
        print(f"📦 Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"📦 Response: {response.text}")


def test_health():
    """Teste: GET /health"""
    print_test("Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_result(response)
    return response.status_code == 200


def test_root():
    """Teste: GET /"""
    print_test("Root Endpoint")
    response = requests.get(BASE_URL)
    print_result(response)
    return response.status_code == 200


def test_register():
    """Teste: POST /api/v1/auth/register"""
    print_test("Registrar Novo Usuário")
    payload = {
        "email": "teste@notion.com",
        "password": "senha123456",
        "name": "Usuário de Teste"
    }
    response = requests.post(f"{API_V1}/auth/register", json=payload)
    print_result(response)
    
    if response.status_code == 201:
        data = response.json()
        test_data["access_token"] = data["access_token"]
        test_data["refresh_token"] = data["refresh_token"]
        return True
    elif response.status_code == 400 and "already registered" in response.json().get("detail", ""):
        # Se o usuário já existe, não é erro (vamos logar na próxima etapa)
        print("⚠️  Usuário já existe, continuando com login...")
        return True
    return False


def test_login():
    """Teste: POST /api/v1/auth/login"""
    print_test("Login")
    payload = {
        "username": "teste@notion.com",
        "password": "senha123456"
    }
    response = requests.post(
        f"{API_V1}/auth/login",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print_result(response)
    
    if response.status_code == 200:
        data = response.json()
        test_data["access_token"] = data["access_token"]
        test_data["refresh_token"] = data["refresh_token"]
        return True
    return False


def test_me():
    """Teste: GET /api/v1/auth/me"""
    print_test("Obter Dados do Usuário Logado")
    headers = {"Authorization": f"Bearer {test_data['access_token']}"}
    response = requests.get(f"{API_V1}/auth/me", headers=headers)
    print_result(response)
    return response.status_code == 200


def test_update_me():
    """Teste: PATCH /api/v1/auth/me"""
    print_test("Atualizar Perfil do Usuário")
    headers = {"Authorization": f"Bearer {test_data['access_token']}"}
    payload = {"name": "Usuário Atualizado"}
    response = requests.patch(f"{API_V1}/auth/me", json=payload, headers=headers)
    print_result(response)
    return response.status_code == 200


def test_list_workspaces():
    """Teste: GET /api/v1/workspaces/"""
    print_test("Listar Workspaces do Usuário")
    headers = {"Authorization": f"Bearer {test_data['access_token']}"}
    response = requests.get(f"{API_V1}/workspaces/", headers=headers)
    print_result(response)
    
    if response.status_code == 200:
        data = response.json()
        if data:
            test_data["workspace_id"] = data[0]["id"]
        return True
    return False


def test_create_workspace():
    """Teste: POST /api/v1/workspaces/"""
    print_test("Criar Novo Workspace")
    headers = {"Authorization": f"Bearer {test_data['access_token']}"}
    payload = {
        "name": "Meu Workspace de Testes",
        "icon": "🚀"
    }
    response = requests.post(f"{API_V1}/workspaces/", json=payload, headers=headers)
    print_result(response)
    
    if response.status_code == 201:
        data = response.json()
        test_data["workspace_id"] = data["id"]
        return True
    return False


def test_get_workspace():
    """Teste: GET /api/v1/workspaces/{id}"""
    print_test("Obter Detalhes do Workspace")
    headers = {"Authorization": f"Bearer {test_data['access_token']}"}
    response = requests.get(
        f"{API_V1}/workspaces/{test_data['workspace_id']}", 
        headers=headers
    )
    print_result(response)
    return response.status_code == 200


def test_update_workspace():
    """Teste: PATCH /api/v1/workspaces/{id}"""
    print_test("Atualizar Workspace")
    headers = {"Authorization": f"Bearer {test_data['access_token']}"}
    payload = {
        "name": "Workspace Atualizado",
        "icon": "🎯"
    }
    response = requests.patch(
        f"{API_V1}/workspaces/{test_data['workspace_id']}", 
        json=payload,
        headers=headers
    )
    print_result(response)
    return response.status_code == 200


def test_create_page():
    """Teste: POST /api/v1/pages/"""
    print_test("Criar Nova Página")
    headers = {"Authorization": f"Bearer {test_data['access_token']}"}
    payload = {
        "workspace_id": test_data["workspace_id"],
        "title": "Minha Primeira Página",
        "icon": "📝"
    }
    response = requests.post(f"{API_V1}/pages/", json=payload, headers=headers)
    print_result(response)
    
    if response.status_code == 201:
        data = response.json()
        test_data["page_id"] = data["id"]
        return True
    return False


def test_list_pages():
    """Teste: GET /api/v1/pages/"""
    print_test("Listar Páginas do Workspace")
    headers = {"Authorization": f"Bearer {test_data['access_token']}"}
    params = {"workspace_id": test_data["workspace_id"]}
    response = requests.get(f"{API_V1}/pages/", params=params, headers=headers)
    print_result(response)
    return response.status_code == 200


def test_get_page():
    """Teste: GET /api/v1/pages/{id}"""
    print_test("Obter Detalhes da Página")
    headers = {"Authorization": f"Bearer {test_data['access_token']}"}
    response = requests.get(f"{API_V1}/pages/{test_data['page_id']}", headers=headers)
    print_result(response)
    return response.status_code == 200


def test_update_page():
    """Teste: PATCH /api/v1/pages/{id}"""
    print_test("Atualizar Página")
    headers = {"Authorization": f"Bearer {test_data['access_token']}"}
    payload = {
        "title": "Página Atualizada",
        "icon": "✏️"
    }
    response = requests.patch(
        f"{API_V1}/pages/{test_data['page_id']}", 
        json=payload,
        headers=headers
    )
    print_result(response)
    return response.status_code == 200


def test_get_page_tree():
    """Teste: GET /api/v1/pages/workspace/{workspace_id}/tree"""
    print_test("Obter Árvore de Páginas")
    headers = {"Authorization": f"Bearer {test_data['access_token']}"}
    response = requests.get(
        f"{API_V1}/pages/workspace/{test_data['workspace_id']}/tree",
        headers=headers
    )
    print_result(response)
    return response.status_code == 200


def test_create_block():
    """Teste: POST /api/v1/blocks/"""
    print_test("Criar Bloco de Conteúdo")
    headers = {"Authorization": f"Bearer {test_data['access_token']}"}
    payload = {
        "page_id": test_data["page_id"],
        "type": "heading1",
        "content": {"text": "Introdução", "level": 1},
        "order": 0
    }
    response = requests.post(f"{API_V1}/blocks/", json=payload, headers=headers)
    print_result(response)
    
    if response.status_code == 201:
        data = response.json()
        test_data["block_id"] = data["id"]
        return True
    return False


def test_create_paragraph_block():
    """Teste: POST /api/v1/blocks/ - Parágrafo"""
    print_test("Criar Bloco de Parágrafo")
    headers = {"Authorization": f"Bearer {test_data['access_token']}"}
    payload = {
        "page_id": test_data["page_id"],
        "type": "paragraph",
        "content": {
            "text": "Este é um parágrafo de exemplo com **negrito** e *itálico*.",
            "marks": [
                {"type": "bold", "start": 39, "end": 47},
                {"type": "italic", "start": 50, "end": 58}
            ]
        },
        "order": 1
    }
    response = requests.post(f"{API_V1}/blocks/", json=payload, headers=headers)
    print_result(response)
    return response.status_code == 201


def test_list_blocks():
    """Teste: GET /api/v1/blocks/page/{page_id}"""
    print_test("Listar Blocos da Página")
    headers = {"Authorization": f"Bearer {test_data['access_token']}"}
    response = requests.get(
        f"{API_V1}/blocks/page/{test_data['page_id']}", 
        headers=headers
    )
    print_result(response)
    return response.status_code == 200


def test_update_block():
    """Teste: PATCH /api/v1/blocks/{id}"""
    print_test("Atualizar Bloco")
    headers = {"Authorization": f"Bearer {test_data['access_token']}"}
    payload = {
        "content": {"text": "Título Atualizado", "level": 1}
    }
    response = requests.patch(
        f"{API_V1}/blocks/{test_data['block_id']}", 
        json=payload,
        headers=headers
    )
    print_result(response)
    return response.status_code == 200


def test_move_block():
    """Teste: PATCH /api/v1/blocks/{id}/move"""
    print_test("Reordenar Bloco")
    headers = {"Authorization": f"Bearer {test_data['access_token']}"}
    payload = {"new_order": 10}
    response = requests.patch(
        f"{API_V1}/blocks/{test_data['block_id']}/move", 
        json=payload,
        headers=headers
    )
    print_result(response)
    return response.status_code == 200


def test_delete_block():
    """Teste: DELETE /api/v1/blocks/{id}"""
    print_test("Deletar Bloco")
    headers = {"Authorization": f"Bearer {test_data['access_token']}"}
    response = requests.delete(
        f"{API_V1}/blocks/{test_data['block_id']}", 
        headers=headers
    )
    print_result(response)
    return response.status_code == 204


def test_archive_page():
    """Teste: DELETE /api/v1/pages/{id}"""
    print_test("Arquivar Página")
    headers = {"Authorization": f"Bearer {test_data['access_token']}"}
    response = requests.delete(f"{API_V1}/pages/{test_data['page_id']}", headers=headers)
    print_result(response)
    return response.status_code == 204


def run_all_tests():
    """Executa todos os testes em ordem"""
    print("\n" + "="*60)
    print("🚀 INICIANDO TESTES COMPLETOS DA API")
    print("="*60)
    
    tests = [
        # Health & Root
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        
        # Auth
        ("Registrar Usuário", test_register),
        ("Login", test_login),
        ("Obter Perfil", test_me),
        ("Atualizar Perfil", test_update_me),
        
        # Workspaces
        ("Listar Workspaces", test_list_workspaces),
        ("Criar Workspace", test_create_workspace),
        ("Obter Workspace", test_get_workspace),
        ("Atualizar Workspace", test_update_workspace),
        
        # Pages
        ("Criar Página", test_create_page),
        ("Listar Páginas", test_list_pages),
        ("Obter Página", test_get_page),
        ("Atualizar Página", test_update_page),
        ("Árvore de Páginas", test_get_page_tree),
        
        # Blocks
        ("Criar Bloco Heading", test_create_block),
        ("Criar Bloco Parágrafo", test_create_paragraph_block),
        ("Listar Blocos", test_list_blocks),
        ("Atualizar Bloco", test_update_block),
        ("Mover Bloco", test_move_block),
        ("Deletar Bloco", test_delete_block),
        
        # Cleanup
        ("Arquivar Página", test_archive_page),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ ERRO: {e}")
            results.append((name, False))
    
    # Resumo
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        emoji = "✅" if result else "❌"
        print(f"{emoji} {name}")
    
    print(f"\n📈 Resultado: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam")


if __name__ == "__main__":
    run_all_tests()
