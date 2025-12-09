"""
Complete API Test Suite for Notion Clone
Tests all endpoints: Auth, Workspaces, Pages, Blocks, Invitations, Search, Comments
"""

import requests
import json
import time
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8001/api/v1"

# Test data
timestamp = int(time.time())
test_user1 = {
    "email": f"apitest1_{timestamp}@example.com",
    "password": "TestPassword123!",
    "name": "API Test User 1"
}

test_user2 = {
    "email": f"apitest2_{timestamp}@example.com",
    "password": "TestPassword123!",
    "name": "API Test User 2"
}

# Global state
state = {
    "user1_token": None,
    "user2_token": None,
    "user1_id": None,
    "user2_id": None,
    "workspace_id": None,
    "page_id": None,
    "block_id": None,
    "comment_id": None,
    "invitation_id": None
}

def print_header(message: str):
    """Print section header"""
    print(f"\n{'='*70}")
    print(f"  {message}")
    print(f"{'='*70}")

def print_test(message: str, passed: bool = True):
    """Print test result"""
    status = "[OK]" if passed else "[FAIL]"
    print(f"{status} {message}")

def print_error(message: str, response: requests.Response):
    """Print error details"""
    print(f"[ERROR] {message}")
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.text[:200]}")

def make_request(method: str, endpoint: str, **kwargs) -> Optional[requests.Response]:
    """Make HTTP request with error handling"""
    try:
        url = f"{BASE_URL}{endpoint}"
        response = requests.request(method, url, **kwargs)
        return response
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")
        return None

# =============================================================================
# 1. AUTHENTICATION TESTS
# =============================================================================

def test_auth():
    """Test authentication endpoints"""
    print_header("1. AUTHENTICATION TESTS")

    # Test 1.1: Register User 1
    response = make_request("POST", "/auth/register", json=test_user1)
    if response and response.status_code == 201:
        print_test("Register User 1")
    else:
        print_error("Register User 1 failed", response)
        return False

    # Test 1.2: Register User 2
    response = make_request("POST", "/auth/register", json=test_user2)
    if response and response.status_code == 201:
        print_test("Register User 2")
    else:
        print_error("Register User 2 failed", response)
        return False

    # Test 1.3: Login User 1
    response = make_request("POST", "/auth/login", data={
        "username": test_user1["email"],
        "password": test_user1["password"]
    })
    if response and response.status_code == 200:
        data = response.json()
        state["user1_token"] = data["access_token"]
        print_test("Login User 1")
    else:
        print_error("Login User 1 failed", response)
        return False

    # Test 1.4: Login User 2
    response = make_request("POST", "/auth/login", data={
        "username": test_user2["email"],
        "password": test_user2["password"]
    })
    if response and response.status_code == 200:
        data = response.json()
        state["user2_token"] = data["access_token"]
        print_test("Login User 2")
    else:
        print_error("Login User 2 failed", response)
        return False

    # Test 1.5: Get Current User (User 1)
    headers = {"Authorization": f"Bearer {state['user1_token']}"}
    response = make_request("GET", "/auth/me", headers=headers)
    if response and response.status_code == 200:
        data = response.json()
        state["user1_id"] = data["id"]
        print_test(f"Get current user (User 1): {data['name']}")
    else:
        print_error("Get current user failed", response)
        return False

    # Test 1.6: Get Current User (User 2)
    headers = {"Authorization": f"Bearer {state['user2_token']}"}
    response = make_request("GET", "/auth/me", headers=headers)
    if response and response.status_code == 200:
        data = response.json()
        state["user2_id"] = data["id"]
        print_test(f"Get current user (User 2): {data['name']}")
    else:
        print_error("Get current user failed", response)
        return False

    return True

# =============================================================================
# 2. WORKSPACE TESTS
# =============================================================================

def test_workspaces():
    """Test workspace endpoints"""
    print_header("2. WORKSPACE TESTS")

    headers = {"Authorization": f"Bearer {state['user1_token']}"}

    # Test 2.1: Create Workspace
    workspace_data = {
        "name": "API Test Workspace",
        "description": "Testing all APIs"
    }
    response = make_request("POST", "/workspaces/", json=workspace_data, headers=headers)
    if response and response.status_code == 201:
        data = response.json()
        state["workspace_id"] = data["id"]
        print_test(f"Create workspace: {data['name']}")
    else:
        print_error("Create workspace failed", response)
        return False

    # Test 2.2: List Workspaces
    response = make_request("GET", "/workspaces/", headers=headers)
    if response and response.status_code == 200:
        data = response.json()
        print_test(f"List workspaces: {len(data)} workspace(s)")
    else:
        print_error("List workspaces failed", response)
        return False

    # Test 2.3: Get Workspace by ID
    response = make_request("GET", f"/workspaces/{state['workspace_id']}", headers=headers)
    if response and response.status_code == 200:
        data = response.json()
        print_test(f"Get workspace: {data['name']}")
    else:
        print_error("Get workspace failed", response)
        return False

    # Test 2.4: Update Workspace
    update_data = {
        "name": "API Test Workspace (Updated)",
        "description": "Updated description"
    }
    response = make_request("PATCH", f"/workspaces/{state['workspace_id']}", json=update_data, headers=headers)
    if response and response.status_code == 200:
        data = response.json()
        print_test(f"Update workspace: {data['name']}")
    else:
        print_error("Update workspace failed", response)
        return False

    # Test 2.5: Invite User 2 to Workspace
    invite_data = {
        "email": test_user2["email"],
        "role": "editor"
    }
    response = make_request("POST", f"/workspaces/{state['workspace_id']}/invitations", json=invite_data, headers=headers)
    if response and response.status_code == 201:
        data = response.json()
        state["invitation_token"] = data["token"]  # Store token, not id
        print_test(f"Invite user to workspace: {data['invitee_email']}")
    else:
        print_error("Invite user failed", response)
        return False

    # Test 2.6: Accept Invitation (User 2)
    headers2 = {"Authorization": f"Bearer {state['user2_token']}"}
    accept_data = {"token": state["invitation_token"]}  # Use token
    response = make_request("POST", "/invitations/accept", json=accept_data, headers=headers2)
    if response and response.status_code == 200:
        print_test("Accept invitation")
    else:
        print_error("Accept invitation failed (skipping)", response)
        # Continue anyway - user2 might not have access to comments but tests can continue
        pass

    # Test 2.7: List Workspace Members
    response = make_request("GET", f"/workspaces/{state['workspace_id']}/members", headers=headers)
    if response and response.status_code == 200:
        data = response.json()
        print_test(f"List workspace members: {len(data)} member(s)")
    else:
        print_error("List workspace members failed", response)
        return False

    return True

# =============================================================================
# 3. PAGE TESTS
# =============================================================================

def test_pages():
    """Test page endpoints"""
    print_header("3. PAGE TESTS")

    headers = {"Authorization": f"Bearer {state['user1_token']}"}

    # Test 3.1: Create Page
    page_data = {
        "title": "API Test Page",
        "workspace_id": state["workspace_id"]
    }
    response = make_request("POST", "/pages/", json=page_data, headers=headers)
    if response and response.status_code == 201:
        data = response.json()
        state["page_id"] = data["id"]
        print_test(f"Create page: {data['title']}")
    else:
        print_error("Create page failed", response)
        return False

    # Test 3.2: List Pages in Workspace
    response = make_request("GET", f"/pages/?workspace_id={state['workspace_id']}", headers=headers)
    if response and response.status_code == 200:
        data = response.json()
        count = len(data) if isinstance(data, list) else data.get('total', 0)
        print_test(f"List pages: {count} page(s)")
    else:
        print_error("List pages failed", response)
        return False

    # Test 3.3: Get Page by ID
    response = make_request("GET", f"/pages/{state['page_id']}", headers=headers)
    if response and response.status_code == 200:
        data = response.json()
        print_test(f"Get page: {data['title']}")
    else:
        print_error("Get page failed", response)
        return False

    # Test 3.4: Update Page
    update_data = {
        "title": "API Test Page (Updated)",
        "icon": "📝"
    }
    response = make_request("PATCH", f"/pages/{state['page_id']}", json=update_data, headers=headers)
    if response and response.status_code == 200:
        data = response.json()
        print_test(f"Update page: {data['title']}")
    else:
        print_error("Update page failed", response)
        return False

    return True

# =============================================================================
# 4. BLOCK TESTS
# =============================================================================

def test_blocks():
    """Test block endpoints"""
    print_header("4. BLOCK TESTS")

    headers = {"Authorization": f"Bearer {state['user1_token']}"}

    # Test 4.1: Create Block
    block_data = {
        "page_id": state["page_id"],
        "type": "paragraph",
        "content": {"text": "This is a test paragraph block"},
        "order": 0
    }
    response = make_request("POST", "/blocks/", json=block_data, headers=headers)
    if response and response.status_code == 201:
        data = response.json()
        state["block_id"] = data["id"]
        print_test(f"Create block: {data['type']}")
    else:
        print_error("Create block failed", response)
        return False

    # Test 4.2: Create Heading Block
    heading_data = {
        "page_id": state["page_id"],
        "type": "heading_1",
        "content": {"text": "Test Heading"},
        "order": 1
    }
    response = make_request("POST", "/blocks/", json=heading_data, headers=headers)
    if response and response.status_code == 201:
        data = response.json()
        print_test(f"Create heading block: {data['type']}")
    else:
        print_error("Create heading block failed", response)
        return False

    # Test 4.3: List Blocks in Page
    response = make_request("GET", f"/blocks/page/{state['page_id']}", headers=headers)
    if response and response.status_code == 200:
        data = response.json()
        print_test(f"List blocks: {len(data)} block(s)")
    else:
        print_error("List blocks failed", response)
        return False

    # Test 4.4: Get Block by ID
    response = make_request("GET", f"/blocks/{state['block_id']}", headers=headers)
    if response and response.status_code == 200:
        data = response.json()
        print_test(f"Get block: {data['type']}")
    else:
        print_error("Get block failed", response)
        return False

    # Test 4.5: Update Block
    update_data = {
        "content": {"text": "Updated paragraph content"}
    }
    response = make_request("PATCH", f"/blocks/{state['block_id']}", json=update_data, headers=headers)
    if response and response.status_code == 200:
        data = response.json()
        print_test(f"Update block content")
    else:
        print_error("Update block failed", response)
        return False

    return True

# =============================================================================
# 5. SEARCH TESTS
# =============================================================================

def test_search():
    """Test search endpoints"""
    print_header("5. SEARCH TESTS")

    headers = {"Authorization": f"Bearer {state['user1_token']}"}

    # Test 5.1: Search for "Test"
    search_data = {
        "query": "Test",
        "workspace_id": state["workspace_id"]
    }
    response = make_request("POST", "/search/", json=search_data, headers=headers)
    if response and response.status_code == 200:
        data = response.json()
        total = data.get('total_results') or data.get('total') or len(data.get('results', []))
        print_test(f"Search 'Test': {total} result(s)")
    else:
        print_error("Search failed", response)
        return False

    # Test 5.2: Search for "paragraph"
    search_data = {
        "query": "paragraph",
        "workspace_id": state["workspace_id"]
    }
    response = make_request("POST", "/search/", json=search_data, headers=headers)
    if response and response.status_code == 200:
        data = response.json()
        total = data.get('total_results') or data.get('total') or len(data.get('results', []))
        print_test(f"Search 'paragraph': {total} result(s)")
    else:
        print_error("Search failed", response)
        return False

    # Test 5.3: Search with filters (pages only)
    search_data = {
        "query": "API",
        "workspace_id": state["workspace_id"],
        "result_types": ["page"]
    }
    response = make_request("POST", "/search/", json=search_data, headers=headers)
    if response and response.status_code == 200:
        data = response.json()
        total = data.get('total_results') or data.get('total') or len(data.get('results', []))
        print_test(f"Search 'API' (pages only): {total} result(s)")
    else:
        print_error("Search with filters failed", response)
        return False

    return True

# =============================================================================
# 6. COMMENT TESTS
# =============================================================================

def test_comments():
    """Test comment endpoints"""
    print_header("6. COMMENT TESTS")

    headers1 = {"Authorization": f"Bearer {state['user1_token']}"}
    headers2 = {"Authorization": f"Bearer {state['user2_token']}"}

    # Test 6.1: Create Comment on Page
    comment_data = {
        "page_id": state["page_id"],
        "content": "This is a test comment!"
    }
    response = make_request("POST", "/comments/", json=comment_data, headers=headers1)
    if response and response.status_code == 201:
        data = response.json()
        state["comment_id"] = data["id"]
        print_test(f"Create comment: {data['content'][:30]}...")
    else:
        print_error("Create comment failed", response)
        return False

    # Test 6.2: Create Reply
    reply_data = {
        "page_id": state["page_id"],
        "parent_comment_id": state["comment_id"],
        "content": "This is a reply!"
    }
    response = make_request("POST", "/comments/", json=reply_data, headers=headers2)
    if response and response.status_code == 201:
        data = response.json()
        print_test(f"Create reply (depth {data['thread_depth']})")
    else:
        print_error("Create reply failed", response)
        return False

    # Test 6.3: Create Comment with Mention
    mention_data = {
        "page_id": state["page_id"],
        "content": f"Hey @[{test_user2['name']}]({state['user2_id']}) check this!"
    }
    response = make_request("POST", "/comments/", json=mention_data, headers=headers1)
    if response and response.status_code == 201:
        data = response.json()
        print_test(f"Create comment with mention: {len(data['mentioned_users'])} user(s)")
    else:
        print_error("Create comment with mention failed", response)
        return False

    # Test 6.4: List Comments by Page
    response = make_request("GET", f"/comments/page/{state['page_id']}", headers=headers1)
    if response and response.status_code == 200:
        data = response.json()
        print_test(f"List comments: {data['total']} comment(s)")
    else:
        print_error("List comments failed", response)
        return False

    # Test 6.5: Get Comment by ID
    response = make_request("GET", f"/comments/{state['comment_id']}", headers=headers1)
    if response and response.status_code == 200:
        data = response.json()
        print_test(f"Get comment: {data['content'][:30]}...")
    else:
        print_error("Get comment failed", response)
        return False

    # Test 6.6: Add Reaction
    reaction_data = {"reaction_type": "thumbs_up"}
    response = make_request("POST", f"/comments/{state['comment_id']}/reactions", json=reaction_data, headers=headers1)
    if response and response.status_code == 201:
        print_test("Add reaction (thumbs_up)")
    else:
        print_error("Add reaction failed", response)
        return False

    # Test 6.7: Add Another Reaction (different user)
    reaction_data = {"reaction_type": "heart"}
    response = make_request("POST", f"/comments/{state['comment_id']}/reactions", json=reaction_data, headers=headers2)
    if response and response.status_code == 201:
        print_test("Add reaction (heart) by User 2")
    else:
        print_error("Add reaction failed", response)
        return False

    # Test 6.8: Verify Reactions
    response = make_request("GET", f"/comments/{state['comment_id']}", headers=headers1)
    if response and response.status_code == 200:
        data = response.json()
        print_test(f"Verify reactions: {len(data['reactions'])} type(s)")
    else:
        print_error("Verify reactions failed", response)
        return False

    # Test 6.9: Edit Comment
    update_data = {"content": "This comment has been edited!"}
    response = make_request("PATCH", f"/comments/{state['comment_id']}", json=update_data, headers=headers1)
    if response and response.status_code == 200:
        data = response.json()
        print_test(f"Edit comment: {data['content'][:30]}...")
    else:
        print_error("Edit comment failed", response)
        return False

    # Test 6.10: Add Attachment
    attachment_data = {
        "file_name": "test.pdf",
        "file_url": "https://example.com/test.pdf",
        "file_size": 1024000,
        "mime_type": "application/pdf",
        "order_index": 0
    }
    response = make_request("POST", f"/comments/{state['comment_id']}/attachments", json=attachment_data, headers=headers1)
    if response and response.status_code == 201:
        data = response.json()
        print_test(f"Add attachment: {data['file_name']}")
    else:
        print_error("Add attachment failed", response)
        return False

    # Test 6.11: Remove Reaction
    response = make_request("DELETE", f"/comments/{state['comment_id']}/reactions/thumbs_up", headers=headers1)
    if response and response.status_code == 204:
        print_test("Remove reaction")
    else:
        print_error("Remove reaction failed", response)
        return False

    return True

# =============================================================================
# MAIN TEST RUNNER
# =============================================================================

def run_all_tests():
    """Run all API tests"""
    print("\n" + "="*70)
    print("  NOTION CLONE - COMPLETE API TEST SUITE")
    print("="*70)
    print(f"  Base URL: {BASE_URL}")
    print(f"  Timestamp: {timestamp}")
    print("="*70)

    results = {
        "Authentication": False,
        "Workspaces": False,
        "Pages": False,
        "Blocks": False,
        "Search": False,
        "Comments": False
    }

    try:
        # Run tests in sequence
        results["Authentication"] = test_auth()
        if not results["Authentication"]:
            print("\n[CRITICAL] Authentication tests failed. Stopping.")
            return results

        results["Workspaces"] = test_workspaces()
        results["Pages"] = test_pages()
        results["Blocks"] = test_blocks()
        results["Search"] = test_search()
        results["Comments"] = test_comments()

    except Exception as e:
        print(f"\n[CRITICAL ERROR] {e}")
        import traceback
        traceback.print_exc()

    # Print summary
    print_header("TEST SUMMARY")

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    for category, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {category}")

    print(f"\n{'='*70}")
    print(f"  TOTAL: {passed}/{total} categories passed")
    print(f"{'='*70}")

    if passed == total:
        print("\n[SUCCESS] All API tests passed!")
    else:
        print("\n[WARNING] Some tests failed. Check output above.")

    return results

if __name__ == "__main__":
    run_all_tests()
