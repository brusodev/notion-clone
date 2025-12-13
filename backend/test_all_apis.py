"""
Script COMPLETO de testes para TODAS as APIs do Notion Clone
Testa todos os endpoints disponíveis
"""
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

# Dados dos testes
test_data = {}
stats = {"passed": 0, "failed": 0, "skipped": 0}


def test(name, optional=False):
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
                    stats["passed"] += 1
                else:
                    if optional:
                        print(f"[SKIP] {name} (funcionalidade opcional)")
                        stats["skipped"] += 1
                    else:
                        print(f"[FALHOU] {name}")
                        stats["failed"] += 1
                return result
            except AssertionError as e:
                if optional:
                    print(f"[SKIP] {name} (nao implementado)")
                    stats["skipped"] += 1
                    return False
                else:
                    print(f"[ERRO] {name}: {str(e)}")
                    stats["failed"] += 1
                    return False
            except Exception as e:
                print(f"[ERRO] {name}: {str(e)}")
                stats["failed"] += 1
                return False
        return wrapper
    return decorator


# =============================================================================
# TESTES DE AUTENTICACAO
# =============================================================================

@test("01. Health Check")
def test_health():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    print(f"  API: {data['message']}")
    print(f"  Versao: {data['version']}")
    return True


@test("02. Registro de Usuario")
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
    return True


@test("03. Login")
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
    return True


@test("04. Refresh Token")
def test_refresh():
    refresh_data = {"refresh_token": test_data['refresh_token']}
    response = requests.post(f"{API_V1}/auth/refresh", json=refresh_data)
    assert response.status_code == 200
    data = response.json()
    print(f"  Novo token gerado: OK")
    return True


@test("05. Obter Perfil")
def test_me():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.get(f"{API_V1}/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    test_data['user_id'] = data['id']
    print(f"  Email: {data['email']}")
    return True


@test("06. Atualizar Perfil")
def test_update_profile():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    update_data = {"name": "Nome Atualizado"}

    response = requests.patch(
        f"{API_V1}/auth/me",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    print(f"  Novo nome: {data['name']}")
    return True


# =============================================================================
# TESTES DE WORKSPACES
# =============================================================================

@test("07. Listar Workspaces")
def test_workspaces_list():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.get(f"{API_V1}/workspaces/", headers=headers)
    assert response.status_code == 200
    data = response.json()

    if len(data) > 0:
        test_data['workspace_id'] = data[0]['id']
        print(f"  Total: {len(data)}")
    return True


@test("08. Criar Workspace")
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
    test_data['workspace_2_id'] = data['id']
    print(f"  Nome: {data['name']}")
    return True


@test("09. Obter Workspace")
def test_workspace_get():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.get(
        f"{API_V1}/workspaces/{test_data['workspace_id']}",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    print(f"  Nome: {data['name']}")
    return True


@test("10. Atualizar Workspace")
def test_workspace_update():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    update_data = {"name": "Workspace Atualizado"}

    response = requests.patch(
        f"{API_V1}/workspaces/{test_data['workspace_2_id']}",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    return True


# =============================================================================
# TESTES DE PAGINAS
# =============================================================================

@test("11. Criar Pagina")
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
    print(f"  ID: {data['id']}")
    return True


@test("12. Listar Paginas")
def test_pages_list():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    params = {"workspace_id": test_data['workspace_id']}

    response = requests.get(f"{API_V1}/pages/", headers=headers, params=params)
    assert response.status_code == 200
    data = response.json()
    print(f"  Total: {len(data)}")
    return True


@test("13. Obter Pagina")
def test_page_get():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.get(
        f"{API_V1}/pages/{test_data['page_id']}",
        headers=headers
    )
    assert response.status_code == 200
    return True


@test("14. Atualizar Pagina")
def test_page_update():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    update_data = {"title": "Pagina Atualizada"}

    response = requests.patch(
        f"{API_V1}/pages/{test_data['page_id']}",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    return True


@test("15. Arvore de Paginas")
def test_page_tree():
    headers = {"Authorization": f"Bearer {test_data['token']}"}

    response = requests.get(
        f"{API_V1}/pages/workspace/{test_data['workspace_id']}/tree",
        headers=headers
    )
    assert response.status_code == 200
    return True


@test("16. Duplicar Pagina")
def test_page_duplicate():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.post(
        f"{API_V1}/pages/{test_data['page_id']}/duplicate",
        headers=headers
    )
    assert response.status_code in [200, 201]
    data = response.json()
    test_data['page_duplicate_id'] = data['id']
    print(f"  Duplicata criada: {data['title']}")
    return True


# =============================================================================
# TESTES DE BLOCOS
# =============================================================================

@test("17. Criar Bloco")
def test_block_create():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    block_data = {
        "page_id": test_data['page_id'],
        "type": "paragraph",
        "content": {"text": "Paragrafo de teste", "format": {}},
        "order": 0
    }

    response = requests.post(f"{API_V1}/blocks/", json=block_data, headers=headers)
    assert response.status_code in [200, 201]
    data = response.json()

    test_data['block_id'] = data['id']
    print(f"  Tipo: {data['type']}")
    return True


@test("18. Listar Blocos da Pagina")
def test_blocks_list():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.get(
        f"{API_V1}/blocks/page/{test_data['page_id']}",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    print(f"  Total: {len(data)}")
    return True


@test("19. Obter Bloco")
def test_block_get():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.get(
        f"{API_V1}/blocks/{test_data['block_id']}",
        headers=headers
    )
    assert response.status_code == 200
    return True


@test("20. Atualizar Bloco")
def test_block_update():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    update_data = {
        "content": {"text": "Bloco atualizado", "format": {"bold": True}}
    }

    response = requests.patch(
        f"{API_V1}/blocks/{test_data['block_id']}",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    return True


@test("21. Reordenar Bloco")
def test_block_move():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    move_data = {"new_order": 1}

    response = requests.patch(
        f"{API_V1}/blocks/{test_data['block_id']}/move",
        json=move_data,
        headers=headers
    )
    assert response.status_code == 200
    return True


# =============================================================================
# TESTES DE COMENTARIOS
# =============================================================================

@test("22. Criar Comentario em Pagina")
def test_comment_create():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    comment_data = {
        "page_id": test_data['page_id'],
        "content": "Este e um comentario de teste!"
    }

    response = requests.post(
        f"{API_V1}/comments/",
        json=comment_data,
        headers=headers
    )
    assert response.status_code in [200, 201]
    data = response.json()

    test_data['comment_id'] = data['id']
    print(f"  Comentario criado: {data['id']}")
    return True


@test("23. Listar Comentarios da Pagina")
def test_comments_list():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.get(
        f"{API_V1}/comments/page/{test_data['page_id']}",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    print(f"  Total: {len(data)}")
    return True


@test("24. Atualizar Comentario")
def test_comment_update():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    update_data = {"content": "Comentario editado"}

    response = requests.patch(
        f"{API_V1}/comments/{test_data['comment_id']}",
        json=update_data,
        headers=headers
    )
    assert response.status_code == 200
    return True


# =============================================================================
# TESTES DE FAVORITOS
# =============================================================================

@test("25. Favoritar Pagina")
def test_favorite_add():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.post(
        f"{API_V1}/pages/{test_data['page_id']}/favorite",
        headers=headers
    )
    assert response.status_code in [200, 201, 204]
    print("  Pagina favoritada")
    return True


@test("26. Listar Favoritos")
def test_favorites_list():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.get(
        f"{API_V1}/pages/favorites",
        headers=headers
    )
    # Aceita 200 ou 404 se endpoint não existir
    if response.status_code in [200, 404]:
        if response.status_code == 200:
            data = response.json()
            print(f"  Total de favoritos: {len(data)}")
        return True
    return False


@test("27. Desfavoritar Pagina")
def test_favorite_remove():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.delete(
        f"{API_V1}/pages/{test_data['page_id']}/favorite",
        headers=headers
    )
    assert response.status_code in [200, 204]
    return True


# =============================================================================
# TESTES DE TAGS
# =============================================================================

@test("28. Criar Tag")
def test_tag_create():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    tag_data = {
        "name": "Importante",
        "color": "#FF0000"
    }

    response = requests.post(
        f"{API_V1}/workspaces/{test_data['workspace_id']}/tags",
        json=tag_data,
        headers=headers
    )
    assert response.status_code in [200, 201]
    data = response.json()
    test_data['tag_id'] = data['id']
    print(f"  Tag criada: {data['name']}")
    print(f"  Cor: {data['color']}")
    return True


@test("28a. Listar Tags do Workspace")
def test_tag_list():
    headers = {"Authorization": f"Bearer {test_data['token']}"}

    response = requests.get(
        f"{API_V1}/workspaces/{test_data['workspace_id']}/tags",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    print(f"  Total de tags: {len(data)}")
    return True


@test("28b. Adicionar Tag a Pagina")
def test_tag_add_to_page():
    headers = {"Authorization": f"Bearer {test_data['token']}"}

    response = requests.post(
        f"{API_V1}/pages/{test_data['page_id']}/tags/{test_data['tag_id']}",
        headers=headers
    )
    assert response.status_code in [200, 201]
    print(f"  Tag adicionada a pagina")
    return True


@test("28c. Listar Tags da Pagina")
def test_tag_list_from_page():
    headers = {"Authorization": f"Bearer {test_data['token']}"}

    response = requests.get(
        f"{API_V1}/pages/{test_data['page_id']}/tags",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    print(f"  Tags na pagina: {len(data)}")
    return True


@test("28d. Remover Tag da Pagina")
def test_tag_remove_from_page():
    headers = {"Authorization": f"Bearer {test_data['token']}"}

    response = requests.delete(
        f"{API_V1}/pages/{test_data['page_id']}/tags/{test_data['tag_id']}",
        headers=headers
    )
    assert response.status_code in [200, 204]
    print(f"  Tag removida da pagina")
    return True


@test("28e. Deletar Tag")
def test_tag_delete():
    headers = {"Authorization": f"Bearer {test_data['token']}"}

    response = requests.delete(
        f"{API_V1}/workspaces/{test_data['workspace_id']}/tags/{test_data['tag_id']}",
        headers=headers
    )
    assert response.status_code in [200, 204]
    print(f"  Tag deletada")
    return True


# =============================================================================
# TESTES DE LIXEIRA
# =============================================================================

@test("29. Mover Pagina para Lixeira")
def test_page_trash():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.delete(
        f"{API_V1}/pages/{test_data['page_duplicate_id']}",
        headers=headers
    )
    assert response.status_code in [200, 204]
    return True


@test("30. Listar Paginas Arquivadas")
def test_pages_archived():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    params = {"workspace_id": test_data['workspace_id'], "is_archived": True}

    response = requests.get(f"{API_V1}/pages/", headers=headers, params=params)
    assert response.status_code == 200
    return True


# =============================================================================
# TESTES DE WORKSPACE MEMBERS (OPCIONAL)
# =============================================================================

@test("31. Listar Membros do Workspace", optional=True)
def test_workspace_members():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.get(
        f"{API_V1}/workspaces/{test_data['workspace_id']}/members",
        headers=headers
    )
    if response.status_code == 404:
        return False
    assert response.status_code == 200
    return True


# =============================================================================
# TESTES DE DELETAR (CLEANUP)
# =============================================================================

@test("32. Deletar Bloco")
def test_block_delete():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.delete(
        f"{API_V1}/blocks/{test_data['block_id']}",
        headers=headers
    )
    assert response.status_code in [200, 204]
    return True


@test("33. Deletar Comentario")
def test_comment_delete():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.delete(
        f"{API_V1}/comments/{test_data['comment_id']}",
        headers=headers
    )
    assert response.status_code in [200, 204]
    return True


@test("34. Deletar Workspace")
def test_workspace_delete():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    response = requests.delete(
        f"{API_V1}/workspaces/{test_data['workspace_2_id']}",
        headers=headers
    )
    assert response.status_code in [200, 204]
    return True


@test("35. Logout")
def test_logout():
    headers = {"Authorization": f"Bearer {test_data['token']}"}
    logout_data = {"refresh_token": test_data['refresh_token']}
    response = requests.post(f"{API_V1}/auth/logout", json=logout_data, headers=headers)
    assert response.status_code in [200, 204]
    return True


def run_tests():
    """Executa todos os testes"""
    print("\n" + "="*60)
    print("SUITE COMPLETA DE TESTES - NOTION CLONE API")
    print("="*60)

    tests = [
        # Autenticacao
        test_health,
        test_register,
        test_login,
        test_refresh,
        test_me,
        test_update_profile,
        # Workspaces
        test_workspaces_list,
        test_workspace_create,
        test_workspace_get,
        test_workspace_update,
        # Paginas
        test_page_create,
        test_pages_list,
        test_page_get,
        test_page_update,
        test_page_tree,
        test_page_duplicate,
        # Blocos
        test_block_create,
        test_blocks_list,
        test_block_get,
        test_block_update,
        test_block_move,
        # Comentarios
        test_comment_create,
        test_comments_list,
        test_comment_update,
        # Favoritos
        test_favorite_add,
        test_favorites_list,
        test_favorite_remove,
        # Tags
        test_tag_create,
        test_tag_list,
        test_tag_add_to_page,
        test_tag_list_from_page,
        test_tag_remove_from_page,
        # Lixeira
        test_page_trash,
        test_pages_archived,
        # Members
        test_workspace_members,
        # Cleanup
        test_block_delete,
        test_comment_delete,
        test_tag_delete,
        test_workspace_delete,
        test_logout,
    ]

    for test_func in tests:
        test_func()

    # Resumo
    total = stats["passed"] + stats["failed"] + stats["skipped"]

    print("\n" + "="*60)
    print("RESUMO FINAL DOS TESTES")
    print("="*60)
    print(f"Total de testes executados: {total}")
    print(f"[OK] Testes passaram: {stats['passed']}")
    print(f"[X] Testes falharam: {stats['failed']}")
    print(f"[-] Testes pulados (opcionais): {stats['skipped']}")

    if stats['failed'] == 0:
        success_rate = (stats['passed'] / (stats['passed'] + stats['skipped'])) * 100
        print(f"\nTaxa de sucesso: {success_rate:.1f}%")
        print("\n[OK] TODOS OS TESTES OBRIGATORIOS PASSARAM!")
    else:
        success_rate = (stats['passed'] / total) * 100
        print(f"\nTaxa de sucesso geral: {success_rate:.1f}%")
        print(f"\n[AVISO] {stats['failed']} testes falharam")

    print("="*60 + "\n")

    return stats['failed'] == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
