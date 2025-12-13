"""
Script de testes focado nas funcionalidades principais da API
"""
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Dados dos testes
test_data = {}

def test(name):
    """Decorator para testes"""
    def decorator(func):
        def wrapper():
            print(f"\n{'='*60}")
            print(f"TESTE: {name}")
            print('='*60)
            try:
                result = func()
                if result:
                    print(f"[OK] {name}")
                else:
                    print(f"[FALHOU] {name}")
                return result
            except Exception as e:
                print(f"[ERRO] {name}: {str(e)}")
                return False
        return wrapper
    return decorator


@test("Health Check")
def test_health():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    print(f"  API: {data['message']}")
    print(f"  Versao: {data['version']}")
    return True


@test("Registro de Usuario")
def test_register():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    user_data = {
        "email": f"test_{timestamp}@example.com",
        "password": "TestPassword123!",
        "name": f"Test User {timestamp}"
    }

    response = requests.post(f"{API_V1}/auth/register", json=user_data)
    assert response.status_code in [200, 201]
    data = response.json()

    test_data['user'] = user_data
    test_data['token'] = data['access_token']
    test_data['refresh_token'] = data['refresh_token']

    print(f"  Usuario: {user_data['email']}")
    print(f"  Token recebido: OK")
    return True


@test("Login")
def test_login():
    login_data = {
        "username": test_data['user']['email'],
        "password": test_data['user']['password']
    }

    response = requests.post(
        f"{API_V1}/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    data = response.json()
    print(f"  Token type: {data['token_type']}")
    return True


@test("Obter Dados do Usuario")
def test_me():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.get(f"{API_V1}/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    print(f"  Email: {data['email']}")
    print(f"  Nome: {data['name']}")
    return True


@test("Listar Workspaces")
def test_workspaces_list():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.get(f"{API_V1}/workspaces/", headers=headers)
    assert response.status_code == 200
    data = response.json()

    if len(data) > 0:
        test_data['workspace_id'] = data[0]['id']
        print(f"  Total: {len(data)}")
        print(f"  Workspace principal: {data[0]['name']}")
    return True


@test("Criar Workspace")
def test_workspace_create():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    workspace_data = {"name": "Workspace de Testes"}

    response = requests.post(
        f"{API_V1}/workspaces/",
        json=workspace_data,
        headers=headers
    )
    assert response.status_code in [200, 201]
    data = response.json()
    print(f"  Nome: {data['name']}")
    return True


@test("Criar Pagina")
def test_page_create():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    page_data = {
        "title": "Pagina de Teste",
        "workspace_id": test_data['workspace_id']
    }

    response = requests.post(f"{API_V1}/pages/", json=page_data, headers=headers)
    assert response.status_code in [200, 201]
    data = response.json()

    test_data['page_id'] = data['id']
    print(f"  Titulo: {data['title']}")
    print(f"  ID: {data['id']}")
    return True


@test("Listar Paginas")
def test_pages_list():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    params = {"workspace_id": test_data['workspace_id']}

    response = requests.get(f"{API_V1}/pages/", headers=headers, params=params)
    assert response.status_code == 200
    data = response.json()
    print(f"  Total de paginas: {len(data)}")
    return True


@test("Atualizar Pagina")
def test_page_update():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    update_data = {"title": "Pagina Atualizada"}

    response = requests.patch(
        f"{API_V1}/pages/{test_data['page_id']}",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    print(f"  Novo titulo: {data['title']}")
    return True


@test("Criar Bloco")
def test_block_create():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    block_data = {
        "page_id": test_data['page_id'],
        "type": "paragraph",
        "content": {
            "text": "Este e um paragrafo de teste.",
            "format": {}
        },
        "order": 0
    }

    response = requests.post(f"{API_V1}/blocks/", json=block_data, headers=headers)
    assert response.status_code in [200, 201]
    data = response.json()

    test_data['block_id'] = data['id']
    print(f"  Tipo: {data['type']}")
    print(f"  ID: {data['id']}")
    return True


@test("Listar Blocos")
def test_blocks_list():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.get(
        f"{API_V1}/blocks/page/{test_data['page_id']}",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    print(f"  Total de blocos: {len(data)}")
    return True


@test("Atualizar Bloco")
def test_block_update():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    update_data = {
        "content": {
            "text": "Bloco atualizado com sucesso!",
            "format": {"bold": True}
        }
    }

    response = requests.patch(
        f"{API_V1}/blocks/{test_data['block_id']}",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    print("  Conteudo atualizado")
    return True


@test("Duplicar Pagina")
def test_page_duplicate():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.post(
        f"{API_V1}/pages/{test_data['page_id']}/duplicate",
        headers=headers
    )
    assert response.status_code in [200, 201]
    data = response.json()
    print(f"  Pagina duplicada: {data['title']}")
    return True


@test("Mover para Lixeira")
def test_page_trash():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.delete(
        f"{API_V1}/pages/{test_data['page_id']}",
        headers=headers
    )
    assert response.status_code in [200, 204]
    print("  Pagina arquivada")
    return True


def run_tests():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("INICIANDO TESTES DA API NOTION CLONE")
    print("="*60)

    tests = [
        test_health,
        test_register,
        test_login,
        test_me,
        test_workspaces_list,
        test_workspace_create,
        test_page_create,
        test_pages_list,
        test_page_update,
        test_block_create,
        test_blocks_list,
        test_block_update,
        test_page_duplicate,
        test_page_trash,
    ]

    results = []
    for test_func in tests:
        result = test_func()
        results.append(result)

    # Resumo
    passed = sum(results)
    total = len(results)

    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    print(f"Total de testes: {total}")
    print(f"Testes passaram: {passed}")
    print(f"Testes falharam: {total - passed}")
    print(f"Taxa de sucesso: {(passed/total)*100:.1f}%")

    if passed == total:
        print("\n[OK] TODOS OS TESTES PASSARAM!")
    else:
        print(f"\n[AVISO] {total - passed} testes falharam")

    print("="*60 + "\n")

    return passed == total


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
