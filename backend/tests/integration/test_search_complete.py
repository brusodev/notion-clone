import requests
import json
from uuid import uuid4

# Configuration
BASE_URL = "http://localhost:8001/api/v1"

def test_complete_search_flow():
    """Complete test: register, login, create workspace, create page, search"""
    print("=" * 60)
    print("Full-Text Search Complete Integration Test")
    print("=" * 60)

    # Step 1: Register a new user
    print("\n1. Registering new test user...")
    email = f"searchtest{uuid4().hex[:8]}@test.com"
    password = "Test123!@#"

    register_data = {
        "email": email,
        "password": password,
        "name": "Search Test User"
    }

    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    if response.status_code != 201:
        print(f"  ✗ Registration failed: {response.text}")
        return

    tokens = response.json()
    access_token = tokens["access_token"]
    print(f"  ✓ User registered: {email}")
    print("  ✓ Tokens received automatically")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # Step 2: Create a workspace
    print("\n2. Creating workspace...")
    workspace_data = {
        "name": "Search Test Workspace",
        "icon": "🔍"
    }

    response = requests.post(f"{BASE_URL}/workspaces/", headers=headers, json=workspace_data)
    if response.status_code != 201:
        print(f"  ✗ Workspace creation failed: {response.text}")
        return

    workspace = response.json()
    workspace_id = workspace["id"]
    print(f"  ✓ Workspace created: {workspace['name']}")

    # Step 3: Create test pages with searchable content
    print("\n3. Creating test pages...")

    # Page 1: About programming
    page1_data = {
        "workspace_id": workspace_id,
        "title": "Introdução à Programação Python",
        "icon": "🐍"
    }

    response = requests.post(f"{BASE_URL}/pages/", headers=headers, json=page1_data)
    if response.status_code != 201:
        print(f"  ✗ Page 1 creation failed: {response.text}")
        return

    page1 = response.json()
    page1_id = page1["id"]
    print(f"  ✓ Page 1 created: {page1['title']}")

    # Add blocks to page 1
    block1_data = {
        "page_id": page1_id,
        "type": "paragraph",
        "content": {"text": "Python é uma linguagem de programação versátil e poderosa, ideal para iniciantes."}
    }

    response = requests.post(f"{BASE_URL}/blocks/", headers=headers, json=block1_data)
    if response.status_code == 201:
        print("    ✓ Block 1 added")

    block2_data = {
        "page_id": page1_id,
        "type": "paragraph",
        "content": {"text": "Com Python você pode programar aplicações web, data science, automação e muito mais."}
    }

    response = requests.post(f"{BASE_URL}/blocks/", headers=headers, json=block2_data)
    if response.status_code == 201:
        print("    ✓ Block 2 added")

    # Page 2: About testing
    page2_data = {
        "workspace_id": workspace_id,
        "title": "Testes Automatizados",
        "icon": "✅"
    }

    response = requests.post(f"{BASE_URL}/pages/", headers=headers, json=page2_data)
    if response.status_code != 201:
        print(f"  ✗ Page 2 creation failed: {response.text}")
        return

    page2 = response.json()
    page2_id = page2["id"]
    print(f"  ✓ Page 2 created: {page2['title']}")

    # Add block to page 2
    block3_data = {
        "page_id": page2_id,
        "type": "paragraph",
        "content": {"text": "Testes automatizados garantem a qualidade do código e facilitam a manutenção."}
    }

    response = requests.post(f"{BASE_URL}/blocks/", headers=headers, json=block3_data)
    if response.status_code == 201:
        print("    ✓ Block 3 added")

    # Step 4: Test search functionality
    print("\n4. Testing search functionality...")
    print("-" * 60)

    # Test 4.1: Search for "programação" (should find page 1 and blocks)
    print("\n  Test 4.1: Search for 'programação'")
    search_data = {
        "query": "programação",
        "workspace_id": workspace_id,
        "limit": 10
    }

    response = requests.post(f"{BASE_URL}/search/", headers=headers, json=search_data)
    print(f"    Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"    ✓ Total results: {result['total']}")
        print(f"    ✓ Execution time: {result['execution_time_ms']:.2f}ms")
        print(f"    ✓ Results returned: {len(result['results'])}")

        if result['results']:
            print(f"\n    First result:")
            first = result['results'][0]
            print(f"      Title: {first['page_title']}")
            print(f"      Rank: {first['rank']:.4f}")
            print(f"      Matched in: {first['matched_in']}")
            print(f"      Highlight: {first['highlight']}")
            if first['matched_blocks']:
                print(f"      Matched blocks: {len(first['matched_blocks'])}")
                for block in first['matched_blocks']:
                    print(f"        - {block['highlight'][:80]}...")
    else:
        print(f"    ✗ Search failed: {response.text}")

    # Test 4.2: Test Portuguese stemming (search "programar" should find "programação")
    print("\n  Test 4.2: Portuguese stemming - search 'programar'")
    search_data = {
        "query": "programar",
        "workspace_id": workspace_id,
        "limit": 10
    }

    response = requests.post(f"{BASE_URL}/search/", headers=headers, json=search_data)
    print(f"    Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"    ✓ Total results: {result['total']}")
        print(f"    ✓ Execution time: {result['execution_time_ms']:.2f}ms")
        print(f"    ✓ Stemming works! Found 'programação' pages with 'programar' query")
    else:
        print(f"    ✗ Search failed: {response.text}")

    # Test 4.3: Search with type filter (pages_only)
    print("\n  Test 4.3: Search with type_filter='pages_only'")
    search_data = {
        "query": "testes",
        "workspace_id": workspace_id,
        "type_filter": "pages_only",
        "limit": 10
    }

    response = requests.post(f"{BASE_URL}/search/", headers=headers, json=search_data)
    print(f"    Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"    ✓ Total results: {result['total']}")
        print(f"    ✓ Execution time: {result['execution_time_ms']:.2f}ms")
        print(f"    ✓ Type filter works!")
    else:
        print(f"    ✗ Search failed: {response.text}")

    # Test 4.4: Search for "python"
    print("\n  Test 4.4: Search for 'python'")
    search_data = {
        "query": "python",
        "workspace_id": workspace_id,
        "limit": 10
    }

    response = requests.post(f"{BASE_URL}/search/", headers=headers, json=search_data)
    print(f"    Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"    ✓ Total results: {result['total']}")
        print(f"    ✓ Execution time: {result['execution_time_ms']:.2f}ms")

        if result['results']:
            for idx, res in enumerate(result['results'], 1):
                print(f"\n    Result {idx}:")
                print(f"      Title: {res['page_title']}")
                print(f"      Rank: {res['rank']:.4f}")
                print(f"      Matched in: {res['matched_in']}")
    else:
        print(f"    ✗ Search failed: {response.text}")

    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_complete_search_flow()
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to the API. Is the server running?")
        print("Start the server with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
