"""
Test script for Page Version History API
Tests: create version on update, list versions, get version, restore version
"""
import requests
import time
import sys
from typing import Optional

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"


def print_step(step: int, description: str):
    """Print test step"""
    print(f"\n{'='*60}")
    print(f"STEP {step}: {description}")
    print('='*60)


def print_success(message: str):
    """Print success message"""
    print(f"✓ {message}")


def print_error(message: str, response: Optional[requests.Response] = None):
    """Print error details"""
    print(f"[ERROR] {message}")
    if response:
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.text[:200]}")


# Test execution
print("\n" + "="*60)
print("PAGE VERSION HISTORY API TESTS")
print("="*60)

try:
    # Step 1: Register and login
    print_step(1, "Register and authenticate user")

    register_data = {
        "email": f"freshtest{int(time.time())}@test.com",
        "password": "Test123!@#",
        "name": "Test User"
    }

    response = requests.post(f"{API_V1}/auth/register", json=register_data)
    if response.status_code != 201:
        print_error("Registration failed", response)
        exit(1)

    print_success("User registered successfully")

    # Login
    login_data = {
        "username": register_data["email"],
        "password": register_data["password"]
    }

    response = requests.post(f"{API_V1}/auth/login", data=login_data)
    if response.status_code != 200:
        print_error("Login failed", response)
        exit(1)

    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print_success("User logged in successfully")

    # Step 2: Create workspace
    print_step(2, "Create workspace")

    workspace_data = {
        "name": "Version Test Workspace",
        "icon": "🔄"
    }

    response = requests.post(f"{API_V1}/workspaces", json=workspace_data, headers=headers)
    if response.status_code != 201:
        print_error("Workspace creation failed", response)
        exit(1)

    workspace_id = response.json()["id"]
    print_success(f"Workspace created: {workspace_id}")

    # Step 3: Create a page
    print_step(3, "Create a page")

    page_data = {
        "workspace_id": workspace_id,
        "title": "Original Title",
        "icon": "📄",
        "cover_image": None,
        "parent_id": None,
        "order": 0
    }

    response = requests.post(f"{API_V1}/pages", json=page_data, headers=headers)
    if response.status_code != 201:
        print_error("Page creation failed", response)
        exit(1)

    page_id = response.json()["id"]
    print_success(f"Page created: {page_id}")
    print_success(f"Original title: '{page_data['title']}'")

    # Step 4: Add some blocks to the page
    print_step(4, "Add blocks to the page")

    block1_data = {
        "page_id": page_id,
        "type": "paragraph",
        "content": {"text": "First paragraph"},
        "order": 0,
        "parent_block_id": None
    }

    response = requests.post(f"{API_V1}/blocks", json=block1_data, headers=headers)
    if response.status_code != 201:
        print_error("Block 1 creation failed", response)
        exit(1)

    block1_id = response.json()["id"]
    print_success(f"Block 1 created: {block1_id}")

    block2_data = {
        "page_id": page_id,
        "type": "paragraph",
        "content": {"text": "Second paragraph"},
        "order": 1,
        "parent_block_id": None
    }

    response = requests.post(f"{API_V1}/blocks", json=block2_data, headers=headers)
    if response.status_code != 201:
        print_error("Block 2 creation failed", response)
        exit(1)

    block2_id = response.json()["id"]
    print_success(f"Block 2 created: {block2_id}")

    # Step 5: Update page title (should create version 1)
    print_step(5, "Update page title (should create version)")

    update_data = {
        "title": "Updated Title - Version 1"
    }

    response = requests.patch(
        f"{API_V1}/pages/{page_id}?change_summary=Changed+title+to+version+1",
        json=update_data,
        headers=headers
    )
    if response.status_code != 200:
        print_error("Page update failed", response)
        exit(1)

    print_success(f"Page updated with new title: '{update_data['title']}'")
    print_success("Version 1 should have been created automatically")

    # Step 6: Update page title again (should create version 2)
    print_step(6, "Update page title again (should create version 2)")

    update_data2 = {
        "title": "Updated Title - Version 2"
    }

    response = requests.patch(
        f"{API_V1}/pages/{page_id}?change_summary=Changed+title+to+version+2",
        json=update_data2,
        headers=headers
    )
    if response.status_code != 200:
        print_error("Second page update failed", response)
        exit(1)

    print_success(f"Page updated with new title: '{update_data2['title']}'")
    print_success("Version 2 should have been created automatically")

    # Step 7: List all versions
    print_step(7, "List all page versions")

    response = requests.get(f"{API_V1}/pages/{page_id}/versions", headers=headers)
    if response.status_code != 200:
        print_error("Failed to list versions", response)
        exit(1)

    versions = response.json()
    print_success(f"Found {len(versions)} version(s)")

    for version in versions:
        print(f"  - Version {version['version_number']}: '{version['title']}'")
        print(f"    Blocks: {version['blocks_count']}, Created: {version['created_at']}")
        if version.get('change_summary'):
            print(f"    Summary: {version['change_summary']}")

    if len(versions) < 2:
        print_error(f"Expected at least 2 versions, but found {len(versions)}")
        exit(1)

    # Step 8: Get specific version (version 1)
    print_step(8, "Get specific version (version 1)")

    response = requests.get(f"{API_V1}/pages/{page_id}/versions/1", headers=headers)
    if response.status_code != 200:
        print_error("Failed to get version 1", response)
        exit(1)

    version1 = response.json()
    print_success(f"Retrieved version 1: '{version1['title']}'")
    print_success(f"Content snapshot has {len(version1['content_snapshot'])} block(s)")

    if version1['title'] != "Original Title":
        print_error(f"Version 1 title mismatch! Expected 'Original Title', got '{version1['title']}'")
        exit(1)

    print_success("Version 1 title matches original title")

    # Step 9: Restore to version 1
    print_step(9, "Restore page to version 1")

    response = requests.post(
        f"{API_V1}/pages/{page_id}/versions/1/restore",
        headers=headers
    )
    if response.status_code != 200:
        print_error("Failed to restore version 1", response)
        exit(1)

    restored_page = response.json()
    print_success(f"Page restored to version 1")
    print_success(f"Current title: '{restored_page['title']}'")

    if restored_page['title'] != "Original Title":
        print_error(f"Restored title mismatch! Expected 'Original Title', got '{restored_page['title']}'")
        exit(1)

    print_success("Restore successful - title matches version 1")

    # Step 10: Verify blocks were also restored
    print_step(10, "Verify blocks were restored")

    response = requests.get(f"{API_V1}/pages/{page_id}", headers=headers)
    if response.status_code != 200:
        print_error("Failed to get page details", response)
        exit(1)

    page_details = response.json()
    restored_blocks = page_details.get('blocks', [])
    print_success(f"Page has {len(restored_blocks)} block(s)")

    if len(restored_blocks) != 2:
        print_error(f"Expected 2 blocks, but found {len(restored_blocks)}")
        exit(1)

    print_success("Correct number of blocks restored")

    # Verify block content
    for block in restored_blocks:
        print(f"  - Block {block['order']}: {block['content'].get('text', 'N/A')}")

    # Step 11: List versions again (should have 1 more from restore)
    print_step(11, "List versions after restore")

    response = requests.get(f"{API_V1}/pages/{page_id}/versions", headers=headers)
    if response.status_code != 200:
        print_error("Failed to list versions after restore", response)
        exit(1)

    versions_after = response.json()
    print_success(f"Found {len(versions_after)} version(s) after restore")

    if len(versions_after) <= len(versions):
        print_error(f"Expected more versions after restore (had {len(versions)}, now {len(versions_after)})")
        exit(1)

    print_success("A new version was created before restoring (preserving current state)")

    # Final summary
    print("\n" + "="*60)
    print("ALL TESTS PASSED! ✓")
    print("="*60)
    print(f"\nVersion History Summary:")
    print(f"  - Total versions: {len(versions_after)}")
    print(f"  - Original title: 'Original Title'")
    print(f"  - Updated to: 'Updated Title - Version 1'")
    print(f"  - Updated to: 'Updated Title - Version 2'")
    print(f"  - Restored to: 'Original Title'")
    print(f"  - Blocks restored: {len(restored_blocks)}")

except Exception as e:
    print(f"\n[ERROR] Test failed with exception: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)
