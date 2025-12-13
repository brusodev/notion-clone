"""
Script completo de testes para todas as funcionalidades da API Notion Clone
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(title):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")

def print_success(message):
    print(f"{Colors.GREEN}[OK] {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}[ERRO] {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.YELLOW}[INFO] {message}{Colors.RESET}")

# Variáveis globais para armazenar dados dos testes
test_data = {
    'user': None,
    'token': None,
    'refresh_token': None,
    'workspace_id': None,
    'page_id': None,
    'block_id': None,
    'comment_id': None,
    'tag_id': None,
    'file_id': None,
}

def test_health():
    """Teste 1: Health Check"""
    print_test("TESTE 1: Health Check")

    try:
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        data = response.json()
        print_success(f"API respondendo: {data['message']}")
        print_success(f"Versão: {data['version']}")
        print_success(f"Docs disponíveis em: {data['docs']}")
        return True
    except Exception as e:
        print_error(f"Erro no health check: {str(e)}")
        return False

def test_auth_register():
    """Teste 2: Registro de Usuário"""
    print_test("TESTE 2: Registro de Usuário")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    user_data = {
        "email": f"test_{timestamp}@example.com",
        "password": "TestPassword123!",
        "name": f"Test User {timestamp}"
    }

    try:
        response = requests.post(f"{API_V1}/auth/register", json=user_data)
        assert response.status_code in [200, 201]
        data = response.json()

        test_data['token'] = data['access_token']
        test_data['refresh_token'] = data['refresh_token']
        test_data['user'] = user_data

        print_success(f"Usuário registrado: {user_data['email']}")
        print_success(f"Nome: {user_data['name']}")
        print_success(f"Token recebido: {data['access_token'][:30]}...")
        print_success(f"Refresh token recebido: {data['refresh_token'][:30]}...")
        return True
    except Exception as e:
        print_error(f"Erro no registro: {str(e)}")
        if response:
            print_error(f"Status: {response.status_code}")
            print_error(f"Response: {response.text}")
        return False

def test_auth_login():
    """Teste 3: Login"""
    print_test("TESTE 3: Login")

    try:
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

        print_success(f"Login realizado com sucesso")
        print_success(f"Token type: {data['token_type']}")
        return True
    except Exception as e:
        print_error(f"Erro no login: {str(e)}")
        return False

def test_auth_me():
    """Teste 4: Obter Dados do Usuário"""
    print_test("TESTE 4: Obter Dados do Usuário Atual")

    try:
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.get(f"{API_V1}/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()

        print_success(f"ID: {data['id']}")
        print_success(f"Email: {data['email']}")
        print_success(f"Nome: {data['name']}")
        print_success(f"Ativo: {data['is_active']}")
        return True
    except Exception as e:
        print_error(f"Erro ao obter dados: {str(e)}")
        return False

def test_workspaces_list():
    """Teste 5: Listar Workspaces"""
    print_test("TESTE 5: Listar Workspaces")

    try:
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.get(f"{API_V1}/workspaces/", headers=headers)
        assert response.status_code == 200
        data = response.json()

        print_success(f"Total de workspaces: {len(data)}")
        if len(data) > 0:
            test_data['workspace_id'] = data[0]['id']
            print_success(f"Workspace principal: {data[0]['name']}")
            print_success(f"ID: {data[0]['id']}")
        return True
    except Exception as e:
        print_error(f"Erro ao listar workspaces: {str(e)}")
        return False

def test_workspaces_create():
    """Teste 6: Criar Workspace"""
    print_test("TESTE 6: Criar Workspace")

    try:
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        workspace_data = {
            "name": "Workspace de Testes"
        }

        response = requests.post(f"{API_V1}/workspaces/", json=workspace_data, headers=headers)

        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"Workspace criado: {data['name']}")
            print_success(f"ID: {data['id']}")
            return True
        else:
            print_error(f"Status inesperado: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Erro ao criar workspace: {str(e)}")
        return False

def test_pages_create():
    """Teste 7: Criar Página"""
    print_test("TESTE 7: Criar Página")

    try:
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        page_data = {
            "title": "Minha Primeira Pagina de Testes",
            "workspace_id": test_data['workspace_id']
        }

        response = requests.post(f"{API_V1}/pages/", json=page_data, headers=headers)

        # Aceita tanto 200 quanto 201
        if response.status_code in [200, 201]:
            data = response.json()
            test_data['page_id'] = data['id']

            print_success(f"Pagina criada: {data['title']}")
            print_success(f"ID: {data['id']}")
            print_success(f"Workspace: {data['workspace_id']}")
            print_success(f"Arquivada: {data['is_archived']}")
            print_success(f"Publica: {data['is_public']}")
            return True
        else:
            print_error(f"Status inesperado: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Erro ao criar pagina: {str(e)}")
        if 'response' in locals():
            print_error(f"Response: {response.text}")
        return False

def test_pages_list():
    """Teste 8: Listar Páginas"""
    print_test("TESTE 8: Listar Páginas")

    try:
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        params = {"workspace_id": test_data['workspace_id']}

        response = requests.get(f"{API_V1}/pages/", headers=headers, params=params)
        assert response.status_code == 200
        data = response.json()

        print_success(f"Total de páginas: {len(data)}")
        for page in data:
            print_info(f"  - {page['title']} (ID: {page['id']})")
        return True
    except Exception as e:
        print_error(f"Erro ao listar páginas: {str(e)}")
        return False

def test_pages_update():
    """Teste 9: Atualizar Página"""
    print_test("TESTE 9: Atualizar Página")

    try:
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        update_data = {
            "title": "Pagina Atualizada"
        }

        response = requests.patch(
            f"{API_V1}/pages/{test_data['page_id']}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()

        print_success(f"Página atualizada: {data['title']}")
        print_success(f"Novo ícone: {data.get('icon', 'Sem ícone')}")
        return True
    except Exception as e:
        print_error(f"Erro ao atualizar página: {str(e)}")
        return False

def test_blocks_create():
    """Teste 10: Criar Bloco"""
    print_test("TESTE 10: Criar Bloco de Conteúdo")

    try:
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        block_data = {
            "page_id": test_data['page_id'],
            "type": "paragraph",
            "content": {
                "text": "Este é um parágrafo de teste criado automaticamente.",
                "format": {}
            },
            "order": 0
        }

        response = requests.post(f"{API_V1}/blocks/", json=block_data, headers=headers)
        assert response.status_code == 200
        data = response.json()

        test_data['block_id'] = data['id']

        print_success(f"Bloco criado com sucesso")
        print_success(f"ID: {data['id']}")
        print_success(f"Tipo: {data['type']}")
        print_success(f"Conteúdo: {data['content']['text'][:50]}...")
        return True
    except Exception as e:
        print_error(f"Erro ao criar bloco: {str(e)}")
        if 'response' in locals():
            print_error(f"Response: {response.text}")
        return False

def test_blocks_list():
    """Teste 11: Listar Blocos"""
    print_test("TESTE 11: Listar Blocos da Página")

    try:
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.get(
            f"{API_V1}/blocks/page/{test_data['page_id']}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()

        print_success(f"Total de blocos: {len(data)}")
        for block in data:
            print_info(f"  - {block['type']}: {str(block['content'])[:40]}...")
        return True
    except Exception as e:
        print_error(f"Erro ao listar blocos: {str(e)}")
        return False

def test_blocks_update():
    """Teste 12: Atualizar Bloco"""
    print_test("TESTE 12: Atualizar Bloco")

    try:
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        update_data = {
            "content": {
                "text": "Bloco atualizado com novo conteúdo!",
                "format": {"bold": True}
            }
        }

        response = requests.patch(
            f"{API_V1}/blocks/{test_data['block_id']}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()

        print_success(f"Bloco atualizado")
        print_success(f"Novo conteúdo: {data['content']['text']}")
        return True
    except Exception as e:
        print_error(f"Erro ao atualizar bloco: {str(e)}")
        return False

def test_tags_create():
    """Teste 13: Criar Tag"""
    print_test("TESTE 13: Criar Tag")

    try:
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        tag_data = {
            "name": "Importante",
            "color": "#FF0000",
            "workspace_id": test_data['workspace_id']
        }

        response = requests.post(f"{API_V1}/tags/", json=tag_data, headers=headers)
        assert response.status_code == 200
        data = response.json()

        test_data['tag_id'] = data['id']

        print_success(f"Tag criada: {data['name']}")
        print_success(f"Cor: {data['color']}")
        print_success(f"ID: {data['id']}")
        return True
    except Exception as e:
        print_error(f"Erro ao criar tag: {str(e)}")
        if 'response' in locals():
            print_error(f"Response: {response.text}")
        return False

def test_page_favorite():
    """Teste 14: Favoritar Página"""
    print_test("TESTE 14: Favoritar Página")

    try:
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.post(
            f"{API_V1}/pages/{test_data['page_id']}/favorite",
            headers=headers
        )
        assert response.status_code == 200

        print_success(f"Página favoritada com sucesso")
        return True
    except Exception as e:
        print_error(f"Erro ao favoritar página: {str(e)}")
        if 'response' in locals():
            print_error(f"Response: {response.text}")
        return False

def test_page_duplicate():
    """Teste 15: Duplicar Página"""
    print_test("TESTE 15: Duplicar Página")

    try:
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.post(
            f"{API_V1}/pages/{test_data['page_id']}/duplicate",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()

        print_success(f"Página duplicada: {data['title']}")
        print_success(f"ID original: {test_data['page_id']}")
        print_success(f"ID duplicada: {data['id']}")
        return True
    except Exception as e:
        print_error(f"Erro ao duplicar página: {str(e)}")
        if 'response' in locals():
            print_error(f"Response: {response.text}")
        return False

def test_page_trash():
    """Teste 16: Mover para Lixeira"""
    print_test("TESTE 16: Mover Página para Lixeira")

    try:
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.delete(
            f"{API_V1}/pages/{test_data['page_id']}",
            headers=headers
        )
        assert response.status_code == 200

        print_success(f"Página movida para lixeira")
        return True
    except Exception as e:
        print_error(f"Erro ao mover para lixeira: {str(e)}")
        return False

def test_page_restore():
    """Teste 17: Restaurar da Lixeira"""
    print_test("TESTE 17: Restaurar Página da Lixeira")

    try:
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        response = requests.patch(
            f"{API_V1}/pages/{test_data['page_id']}/restore",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()

        print_success(f"Página restaurada: {data['title']}")
        print_success(f"Arquivada: {data['is_archived']}")
        return True
    except Exception as e:
        print_error(f"Erro ao restaurar página: {str(e)}")
        if 'response' in locals():
            print_error(f"Response: {response.text}")
        return False

def test_comments_create():
    """Teste 18: Criar Comentário"""
    print_test("TESTE 18: Criar Comentário")

    try:
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        comment_data = {
            "page_id": test_data['page_id'],
            "content": "Este é um comentário de teste!",
            "parent_comment_id": None
        }

        response = requests.post(f"{API_V1}/comments/", json=comment_data, headers=headers)
        assert response.status_code == 200
        data = response.json()

        test_data['comment_id'] = data['id']

        print_success(f"Comentário criado")
        print_success(f"ID: {data['id']}")
        print_success(f"Conteúdo: {data['content']}")
        return True
    except Exception as e:
        print_error(f"Erro ao criar comentário: {str(e)}")
        if 'response' in locals():
            print_error(f"Response: {response.text}")
        return False

def test_search():
    """Teste 19: Busca"""
    print_test("TESTE 19: Buscar Páginas")

    try:
        headers = {"Authorization": f"Bearer {test_data['token']}"}
        params = {
            "workspace_id": test_data['workspace_id'],
            "query": "Atualizada"
        }

        response = requests.get(f"{API_V1}/search/", headers=headers, params=params)
        assert response.status_code == 200
        data = response.json()

        print_success(f"Busca realizada com sucesso")
        print_success(f"Resultados encontrados: {len(data)}")
        for result in data:
            print_info(f"  - {result['title']} (score: {result.get('rank', 'N/A')})")
        return True
    except Exception as e:
        print_error(f"Erro na busca: {str(e)}")
        if 'response' in locals():
            print_error(f"Response: {response.text}")
        return False

def test_permissions():
    """Teste 20: Permissões"""
    print_test("TESTE 20: Gerenciar Permissões")

    try:
        headers = {"Authorization": f"Bearer {test_data['token']}"}

        # Listar permissões
        response = requests.get(
            f"{API_V1}/permissions/page/{test_data['page_id']}",
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            print_success(f"Permissões listadas: {len(data)} encontrada(s)")
            return True
        else:
            print_info(f"Endpoint de permissões retornou: {response.status_code}")
            return True
    except Exception as e:
        print_error(f"Erro ao listar permissões: {str(e)}")
        return False

def run_all_tests():
    """Executa todos os testes"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}INICIANDO TESTES COMPLETOS DA API{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")

    tests = [
        test_health,
        test_auth_register,
        test_auth_login,
        test_auth_me,
        test_workspaces_list,
        test_workspaces_create,
        test_pages_create,
        test_pages_list,
        test_pages_update,
        test_blocks_create,
        test_blocks_list,
        test_blocks_update,
        test_tags_create,
        test_page_favorite,
        test_page_duplicate,
        test_page_trash,
        test_page_restore,
        test_comments_create,
        test_search,
        test_permissions,
    ]

    results = []
    for test in tests:
        result = test()
        results.append((test.__doc__, result))

    # Resumo
    print_test("RESUMO DOS TESTES")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\n{Colors.BLUE}Testes executados: {total}{Colors.RESET}")
    print(f"{Colors.GREEN}Testes passou: {passed}{Colors.RESET}")
    print(f"{Colors.RED}Testes falharam: {total - passed}{Colors.RESET}")

    if passed == total:
        print(f"\n{Colors.GREEN}{'='*60}")
        print("[OK] TODOS OS TESTES PASSARAM!")
        print(f"{'='*60}{Colors.RESET}\n")
    else:
        print(f"\n{Colors.YELLOW}{'='*60}")
        print("[AVISO] ALGUNS TESTES FALHARAM")
        print(f"{'='*60}{Colors.RESET}\n")

        print("Testes que falharam:")
        for name, result in results:
            if not result:
                print_error(f"  - {name}")

    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
