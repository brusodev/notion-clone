#!/usr/bin/env python3
"""
Script de teste abrangente para a API Notion Clone
Testa todos os endpoints disponíveis
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any

# Configuração
BASE_URL = "https://notion-clone-production-b81a.up.railway.app"
TEST_USER_EMAIL = f"teste_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com"
TEST_USER_PASSWORD = "Test@123456"
TEST_USER_NAME = "Usuário de Teste"

# Variáveis globais para armazenar dados durante os testes
tokens = {}
user_data = {}
workspace_data = {}
page_data = {}
block_data = {}
test_results = []


class Colors:
    """Cores para output no terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def log_test(endpoint: str, method: str, status: str, response_code: int = None, message: str = ""):
    """Registra resultado de um teste"""
    result = {
        "endpoint": endpoint,
        "method": method,
        "status": status,
        "response_code": response_code,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    test_results.append(result)

    # Print colorido
    color = Colors.GREEN if status == "PASS" else Colors.RED if status == "FAIL" else Colors.YELLOW
    symbol = "[OK]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[SKIP]"

    print(f"{color}{symbol} {method:6} {endpoint:50} [{response_code or 'N/A'}]{Colors.END} {message}")


def print_section(title: str):
    """Imprime um cabeçalho de seção"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{title.center(80)}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.END}\n")


def print_data(title: str, data: Any):
    """Imprime dados formatados"""
    print(f"{Colors.YELLOW}{title}:{Colors.END}")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print()


# ============================================================================
# TESTES DE ENDPOINTS PÚBLICOS
# ============================================================================

def test_health():
    """Testa o endpoint de health check"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            log_test("/health", "GET", "PASS", response.status_code)
            print_data("Health Response", response.json())
            return True
        else:
            log_test("/health", "GET", "FAIL", response.status_code, "Status code inesperado")
            return False
    except Exception as e:
        log_test("/health", "GET", "FAIL", message=str(e))
        return False


def test_root():
    """Testa o endpoint raiz"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            log_test("/", "GET", "PASS", response.status_code)
            print_data("Root Response", response.json())
            return True
        else:
            log_test("/", "GET", "FAIL", response.status_code)
            return False
    except Exception as e:
        log_test("/", "GET", "FAIL", message=str(e))
        return False


# ============================================================================
# TESTES DE AUTENTICAÇÃO
# ============================================================================

def test_register():
    """Testa o registro de novo usuário"""
    global user_data
    try:
        payload = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD,
            "name": TEST_USER_NAME
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=payload, timeout=10)

        if response.status_code == 201:
            data = response.json()
            user_data = data.get("user", {})
            log_test("/api/v1/auth/register", "POST", "PASS", response.status_code,
                    f"Usuário criado: {user_data.get('email')}")
            print_data("User Data", user_data)
            return True
        else:
            log_test("/api/v1/auth/register", "POST", "FAIL", response.status_code,
                    response.text)
            return False
    except Exception as e:
        log_test("/api/v1/auth/register", "POST", "FAIL", message=str(e))
        return False


def test_login():
    """Testa o login"""
    global tokens
    try:
        # FastAPI OAuth2 usa form data, não JSON
        payload = {
            "username": TEST_USER_EMAIL,  # OAuth2 usa 'username' não 'email'
            "password": TEST_USER_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=payload, timeout=10)

        if response.status_code == 200:
            tokens = response.json()
            log_test("/api/v1/auth/login", "POST", "PASS", response.status_code,
                    "Tokens obtidos com sucesso")
            print_data("Tokens", {
                "access_token": tokens.get("access_token", "")[:50] + "...",
                "refresh_token": tokens.get("refresh_token", "")[:50] + "...",
                "token_type": tokens.get("token_type")
            })
            return True
        else:
            log_test("/api/v1/auth/login", "POST", "FAIL", response.status_code,
                    response.text)
            return False
    except Exception as e:
        log_test("/api/v1/auth/login", "POST", "FAIL", message=str(e))
        return False


def test_get_me():
    """Testa o endpoint /me"""
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            log_test("/api/v1/auth/me", "GET", "PASS", response.status_code)
            print_data("User Profile", data)
            return True
        else:
            log_test("/api/v1/auth/me", "GET", "FAIL", response.status_code)
            return False
    except Exception as e:
        log_test("/api/v1/auth/me", "GET", "FAIL", message=str(e))
        return False


def test_update_me():
    """Testa atualização de perfil"""
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        payload = {"name": "Usuário Atualizado"}
        response = requests.patch(f"{BASE_URL}/api/v1/auth/me",
                                 headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            log_test("/api/v1/auth/me", "PATCH", "PASS", response.status_code,
                    "Perfil atualizado")
            return True
        else:
            log_test("/api/v1/auth/me", "PATCH", "FAIL", response.status_code)
            return False
    except Exception as e:
        log_test("/api/v1/auth/me", "PATCH", "FAIL", message=str(e))
        return False


def test_refresh_token():
    """Testa renovação de token"""
    try:
        payload = {"refresh_token": tokens['refresh_token']}
        response = requests.post(f"{BASE_URL}/api/v1/auth/refresh",
                                json=payload, timeout=10)

        if response.status_code == 200:
            new_tokens = response.json()
            log_test("/api/v1/auth/refresh", "POST", "PASS", response.status_code,
                    "Token renovado")
            # Atualizar o access token
            tokens['access_token'] = new_tokens.get('access_token', tokens['access_token'])
            return True
        else:
            log_test("/api/v1/auth/refresh", "POST", "FAIL", response.status_code)
            return False
    except Exception as e:
        log_test("/api/v1/auth/refresh", "POST", "FAIL", message=str(e))
        return False


# ============================================================================
# TESTES DE WORKSPACES
# ============================================================================

def test_list_workspaces():
    """Testa listagem de workspaces"""
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = requests.get(f"{BASE_URL}/api/v1/workspaces",
                               headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            log_test("/api/v1/workspaces", "GET", "PASS", response.status_code,
                    f"{len(data)} workspace(s) encontrado(s)")
            print_data("Workspaces", data)
            return True
        else:
            log_test("/api/v1/workspaces", "GET", "FAIL", response.status_code)
            return False
    except Exception as e:
        log_test("/api/v1/workspaces", "GET", "FAIL", message=str(e))
        return False


def test_create_workspace():
    """Testa criação de workspace"""
    global workspace_data
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        payload = {
            "name": "Workspace de Teste",
            "description": "Workspace criado para testes automatizados"
        }
        response = requests.post(f"{BASE_URL}/api/v1/workspaces",
                                headers=headers, json=payload, timeout=10)

        if response.status_code == 201:
            workspace_data = response.json()
            log_test("/api/v1/workspaces", "POST", "PASS", response.status_code,
                    f"Workspace criado: {workspace_data.get('id')}")
            print_data("Workspace Created", workspace_data)
            return True
        else:
            log_test("/api/v1/workspaces", "POST", "FAIL", response.status_code,
                    response.text)
            return False
    except Exception as e:
        log_test("/api/v1/workspaces", "POST", "FAIL", message=str(e))
        return False


def test_get_workspace():
    """Testa obtenção de workspace específico"""
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        workspace_id = workspace_data.get('id')
        response = requests.get(f"{BASE_URL}/api/v1/workspaces/{workspace_id}",
                               headers=headers, timeout=10)

        if response.status_code == 200:
            log_test(f"/api/v1/workspaces/{workspace_id}", "GET", "PASS",
                    response.status_code)
            return True
        else:
            log_test(f"/api/v1/workspaces/{workspace_id}", "GET", "FAIL",
                    response.status_code)
            return False
    except Exception as e:
        log_test(f"/api/v1/workspaces/{{id}}", "GET", "FAIL", message=str(e))
        return False


def test_update_workspace():
    """Testa atualização de workspace"""
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        workspace_id = workspace_data.get('id')
        payload = {
            "name": "Workspace Atualizado",
            "description": "Descrição atualizada"
        }
        response = requests.patch(f"{BASE_URL}/api/v1/workspaces/{workspace_id}",
                                 headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            log_test(f"/api/v1/workspaces/{workspace_id}", "PATCH", "PASS",
                    response.status_code, "Workspace atualizado")
            return True
        else:
            log_test(f"/api/v1/workspaces/{workspace_id}", "PATCH", "FAIL",
                    response.status_code)
            return False
    except Exception as e:
        log_test(f"/api/v1/workspaces/{{id}}", "PATCH", "FAIL", message=str(e))
        return False


# ============================================================================
# TESTES DE PÁGINAS
# ============================================================================

def test_create_page():
    """Testa criação de página"""
    global page_data
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        payload = {
            "title": "Minha Primeira Página",
            "workspace_id": workspace_data.get('id'),
            "icon": "📄"
        }
        response = requests.post(f"{BASE_URL}/api/v1/pages",
                                headers=headers, json=payload, timeout=10)

        if response.status_code == 201:
            page_data = response.json()
            log_test("/api/v1/pages", "POST", "PASS", response.status_code,
                    f"Página criada: {page_data.get('id')}")
            print_data("Page Created", page_data)
            return True
        else:
            log_test("/api/v1/pages", "POST", "FAIL", response.status_code,
                    response.text)
            return False
    except Exception as e:
        log_test("/api/v1/pages", "POST", "FAIL", message=str(e))
        return False


def test_list_pages():
    """Testa listagem de páginas"""
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        workspace_id = workspace_data.get('id')
        response = requests.get(f"{BASE_URL}/api/v1/pages?workspace_id={workspace_id}",
                               headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            log_test("/api/v1/pages", "GET", "PASS", response.status_code,
                    f"{len(data)} página(s) encontrada(s)")
            print_data("Pages", data)
            return True
        else:
            log_test("/api/v1/pages", "GET", "FAIL", response.status_code)
            return False
    except Exception as e:
        log_test("/api/v1/pages", "GET", "FAIL", message=str(e))
        return False


def test_get_page():
    """Testa obtenção de página específica"""
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        page_id = page_data.get('id')
        response = requests.get(f"{BASE_URL}/api/v1/pages/{page_id}",
                               headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            log_test(f"/api/v1/pages/{page_id}", "GET", "PASS", response.status_code)
            print_data("Page Details", data)
            return True
        else:
            log_test(f"/api/v1/pages/{page_id}", "GET", "FAIL", response.status_code)
            return False
    except Exception as e:
        log_test(f"/api/v1/pages/{{id}}", "GET", "FAIL", message=str(e))
        return False


def test_update_page():
    """Testa atualização de página"""
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        page_id = page_data.get('id')
        payload = {
            "title": "Página Atualizada",
            "icon": "📝"
        }
        response = requests.patch(f"{BASE_URL}/api/v1/pages/{page_id}",
                                 headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            log_test(f"/api/v1/pages/{page_id}", "PATCH", "PASS",
                    response.status_code, "Página atualizada")
            return True
        else:
            log_test(f"/api/v1/pages/{page_id}", "PATCH", "FAIL",
                    response.status_code)
            return False
    except Exception as e:
        log_test(f"/api/v1/pages/{{id}}", "PATCH", "FAIL", message=str(e))
        return False


def test_get_page_tree():
    """Testa obtenção da árvore de páginas"""
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        workspace_id = workspace_data.get('id')
        response = requests.get(
            f"{BASE_URL}/api/v1/pages/workspace/{workspace_id}/tree",
            headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            log_test(f"/api/v1/pages/workspace/{workspace_id}/tree", "GET",
                    "PASS", response.status_code)
            print_data("Page Tree", data)
            return True
        else:
            log_test(f"/api/v1/pages/workspace/{{id}}/tree", "GET", "FAIL",
                    response.status_code)
            return False
    except Exception as e:
        log_test(f"/api/v1/pages/workspace/{{id}}/tree", "GET", "FAIL",
                message=str(e))
        return False


def test_move_page():
    """Testa mover página"""
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        page_id = page_data.get('id')
        payload = {"order": 1}
        response = requests.patch(f"{BASE_URL}/api/v1/pages/{page_id}/move",
                                 headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            log_test(f"/api/v1/pages/{page_id}/move", "PATCH", "PASS",
                    response.status_code, "Página movida")
            return True
        else:
            log_test(f"/api/v1/pages/{page_id}/move", "PATCH", "FAIL",
                    response.status_code)
            return False
    except Exception as e:
        log_test(f"/api/v1/pages/{{id}}/move", "PATCH", "FAIL", message=str(e))
        return False


# ============================================================================
# TESTES DE BLOCOS
# ============================================================================

def test_create_block():
    """Testa criação de bloco"""
    global block_data
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        payload = {
            "page_id": page_data.get('id'),
            "type": "paragraph",
            "content": {"text": "Este é um parágrafo de teste"},
            "order": 0
        }
        response = requests.post(f"{BASE_URL}/api/v1/blocks",
                                headers=headers, json=payload, timeout=10)

        if response.status_code == 201:
            block_data = response.json()
            log_test("/api/v1/blocks", "POST", "PASS", response.status_code,
                    f"Bloco criado: {block_data.get('id')}")
            print_data("Block Created", block_data)
            return True
        else:
            log_test("/api/v1/blocks", "POST", "FAIL", response.status_code,
                    response.text)
            return False
    except Exception as e:
        log_test("/api/v1/blocks", "POST", "FAIL", message=str(e))
        return False


def test_list_blocks():
    """Testa listagem de blocos de uma página"""
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        page_id = page_data.get('id')
        response = requests.get(f"{BASE_URL}/api/v1/blocks/page/{page_id}",
                               headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            log_test(f"/api/v1/blocks/page/{page_id}", "GET", "PASS",
                    response.status_code, f"{len(data)} bloco(s) encontrado(s)")
            print_data("Blocks", data)
            return True
        else:
            log_test(f"/api/v1/blocks/page/{page_id}", "GET", "FAIL",
                    response.status_code)
            return False
    except Exception as e:
        log_test(f"/api/v1/blocks/page/{{id}}", "GET", "FAIL", message=str(e))
        return False


def test_update_block():
    """Testa atualização de bloco"""
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        block_id = block_data.get('id')
        payload = {
            "content": {"text": "Parágrafo atualizado"},
            "type": "paragraph"
        }
        response = requests.patch(f"{BASE_URL}/api/v1/blocks/{block_id}",
                                 headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            log_test(f"/api/v1/blocks/{block_id}", "PATCH", "PASS",
                    response.status_code, "Bloco atualizado")
            return True
        else:
            log_test(f"/api/v1/blocks/{block_id}", "PATCH", "FAIL",
                    response.status_code)
            return False
    except Exception as e:
        log_test(f"/api/v1/blocks/{{id}}", "PATCH", "FAIL", message=str(e))
        return False


def test_move_block():
    """Testa mover bloco"""
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        block_id = block_data.get('id')
        payload = {"order": 1}
        response = requests.patch(f"{BASE_URL}/api/v1/blocks/{block_id}/move",
                                 headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            log_test(f"/api/v1/blocks/{block_id}/move", "PATCH", "PASS",
                    response.status_code, "Bloco movido")
            return True
        else:
            log_test(f"/api/v1/blocks/{block_id}/move", "PATCH", "FAIL",
                    response.status_code)
            return False
    except Exception as e:
        log_test(f"/api/v1/blocks/{{id}}/move", "PATCH", "FAIL", message=str(e))
        return False


def test_delete_block():
    """Testa deleção de bloco"""
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        block_id = block_data.get('id')
        response = requests.delete(f"{BASE_URL}/api/v1/blocks/{block_id}",
                                  headers=headers, timeout=10)

        if response.status_code == 204:
            log_test(f"/api/v1/blocks/{block_id}", "DELETE", "PASS",
                    response.status_code, "Bloco deletado")
            return True
        else:
            log_test(f"/api/v1/blocks/{block_id}", "DELETE", "FAIL",
                    response.status_code)
            return False
    except Exception as e:
        log_test(f"/api/v1/blocks/{{id}}", "DELETE", "FAIL", message=str(e))
        return False


# ============================================================================
# TESTES DE BUSCA
# ============================================================================

def test_search():
    """Testa busca full-text"""
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        workspace_id = workspace_data.get('id')

        # Teste 1: Busca básica
        payload = {
            "query": "teste",
            "workspace_id": workspace_id,
            "limit": 10,
            "offset": 0
        }

        response = requests.post(f"{BASE_URL}/api/v1/search/",
                                headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            data = response.json()
            log_test("/api/v1/search/", "POST", "PASS", response.status_code,
                    f"Busca retornou {data.get('total', 0)} resultados em {data.get('execution_time_ms', 0):.2f}ms")

            if data.get('results'):
                print_data("Primeiro Resultado da Busca", {
                    "page_title": data['results'][0].get('page_title'),
                    "rank": data['results'][0].get('rank'),
                    "matched_in": data['results'][0].get('matched_in'),
                    "highlight": data['results'][0].get('highlight', '')[:100] + "..."
                })

            return True
        else:
            log_test("/api/v1/search/", "POST", "FAIL", response.status_code)
            return False
    except Exception as e:
        log_test("/api/v1/search/", "POST", "FAIL", message=str(e))
        return False


def test_search_with_filter():
    """Testa busca com filtro de tipo"""
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        workspace_id = workspace_data.get('id')

        payload = {
            "query": "teste",
            "workspace_id": workspace_id,
            "type_filter": "pages_only",
            "limit": 10
        }

        response = requests.post(f"{BASE_URL}/api/v1/search/",
                                headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            data = response.json()
            log_test("/api/v1/search/ (filtro)", "POST", "PASS", response.status_code,
                    f"Busca com filtro retornou {data.get('total', 0)} resultados")
            return True
        else:
            log_test("/api/v1/search/ (filtro)", "POST", "FAIL", response.status_code)
            return False
    except Exception as e:
        log_test("/api/v1/search/ (filtro)", "POST", "FAIL", message=str(e))
        return False


# ============================================================================
# TESTES DE LIMPEZA E DELEÇÃO
# ============================================================================

def test_delete_page():
    """Testa deleção de página"""
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        page_id = page_data.get('id')
        response = requests.delete(f"{BASE_URL}/api/v1/pages/{page_id}",
                                  headers=headers, timeout=10)

        if response.status_code == 204:
            log_test(f"/api/v1/pages/{page_id}", "DELETE", "PASS",
                    response.status_code, "Página arquivada")
            return True
        else:
            log_test(f"/api/v1/pages/{page_id}", "DELETE", "FAIL",
                    response.status_code)
            return False
    except Exception as e:
        log_test(f"/api/v1/pages/{{id}}", "DELETE", "FAIL", message=str(e))
        return False


def test_delete_workspace():
    """Testa deleção de workspace"""
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        workspace_id = workspace_data.get('id')
        response = requests.delete(f"{BASE_URL}/api/v1/workspaces/{workspace_id}",
                                  headers=headers, timeout=10)

        if response.status_code == 204:
            log_test(f"/api/v1/workspaces/{workspace_id}", "DELETE", "PASS",
                    response.status_code, "Workspace deletado")
            return True
        else:
            log_test(f"/api/v1/workspaces/{workspace_id}", "DELETE", "FAIL",
                    response.status_code)
            return False
    except Exception as e:
        log_test(f"/api/v1/workspaces/{{id}}", "DELETE", "FAIL", message=str(e))
        return False


def test_logout():
    """Testa logout (invalidação de token)"""
    try:
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        payload = {"refresh_token": tokens['refresh_token']}
        response = requests.post(f"{BASE_URL}/api/v1/auth/logout",
                                headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            log_test("/api/v1/auth/logout", "POST", "PASS", response.status_code,
                    "Logout realizado")
            return True
        else:
            log_test("/api/v1/auth/logout", "POST", "FAIL", response.status_code)
            return False
    except Exception as e:
        log_test("/api/v1/auth/logout", "POST", "FAIL", message=str(e))
        return False


# ============================================================================
# RELATÓRIO FINAL
# ============================================================================

def generate_report():
    """Gera relatório final dos testes"""
    print_section("RELATÓRIO FINAL DE TESTES")

    total = len(test_results)
    passed = len([r for r in test_results if r['status'] == 'PASS'])
    failed = len([r for r in test_results if r['status'] == 'FAIL'])
    skipped = len([r for r in test_results if r['status'] == 'SKIP'])

    success_rate = (passed / total * 100) if total > 0 else 0

    print(f"{Colors.BOLD}Total de Testes:{Colors.END} {total}")
    print(f"{Colors.GREEN}Aprovados:{Colors.END} {passed}")
    print(f"{Colors.RED}Falhados:{Colors.END} {failed}")
    print(f"{Colors.YELLOW}Pulados:{Colors.END} {skipped}")
    print(f"{Colors.BOLD}Taxa de Sucesso:{Colors.END} {success_rate:.1f}%")

    if failed > 0:
        print(f"\n{Colors.RED}{Colors.BOLD}Testes Falhados:{Colors.END}")
        for result in test_results:
            if result['status'] == 'FAIL':
                print(f"  - {result['method']} {result['endpoint']} - {result['message']}")

    # Salvar relatório em JSON
    report_file = "test_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "success_rate": success_rate,
                "timestamp": datetime.now().isoformat()
            },
            "results": test_results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n{Colors.CYAN}Relatório salvo em: {report_file}{Colors.END}")


# ============================================================================
# MAIN - EXECUÇÃO DOS TESTES
# ============================================================================

def main():
    """Função principal que executa todos os testes"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("="*80)
    print("              TESTE ABRANGENTE DA API NOTION CLONE                         ")
    print("="*80)
    print(f"{Colors.END}\n")

    print(f"{Colors.YELLOW}URL Base:{Colors.END} {BASE_URL}")
    print(f"{Colors.YELLOW}Email de Teste:{Colors.END} {TEST_USER_EMAIL}")
    print(f"{Colors.YELLOW}Início:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 1. Testes Públicos
    print_section("1. TESTES DE ENDPOINTS PÚBLICOS")
    test_health()
    test_root()

    # 2. Autenticação
    print_section("2. TESTES DE AUTENTICAÇÃO")
    if not test_register():
        print(f"{Colors.RED}Falha no registro. Abortando testes.{Colors.END}")
        return

    if not test_login():
        print(f"{Colors.RED}Falha no login. Abortando testes.{Colors.END}")
        return

    test_get_me()
    test_update_me()
    test_refresh_token()

    # 3. Workspaces
    print_section("3. TESTES DE WORKSPACES")
    test_list_workspaces()
    test_create_workspace()
    if workspace_data:
        test_get_workspace()
        test_update_workspace()

    # 4. Páginas
    print_section("4. TESTES DE PÁGINAS")
    test_create_page()
    if page_data:
        test_list_pages()
        test_get_page()
        test_update_page()
        test_get_page_tree()
        test_move_page()

    # 5. Blocos
    print_section("5. TESTES DE BLOCOS")
    test_create_block()
    if block_data:
        test_list_blocks()
        test_update_block()
        test_move_block()
        test_delete_block()

    # 6. Busca
    print_section("6. TESTES DE BUSCA")
    test_search()
    test_search_with_filter()

    # 7. Limpeza
    print_section("7. TESTES DE DELEÇÃO")
    if page_data:
        test_delete_page()
    if workspace_data:
        test_delete_workspace()

    # 8. Logout
    print_section("8. LOGOUT")
    test_logout()

    # Relatório Final
    generate_report()

    print(f"\n{Colors.YELLOW}Fim:{Colors.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Testes interrompidos pelo usuário{Colors.END}")
    except Exception as e:
        print(f"\n\n{Colors.RED}Erro fatal: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
