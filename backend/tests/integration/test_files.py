"""
Integration tests for File Upload API endpoints
"""

import io
import sys
from pathlib import Path

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import requests
from uuid import UUID

# API Configuration
BASE_URL = "http://localhost:8000/api/v1"
AUTH_URL = f"{BASE_URL}/auth"
WORKSPACES_URL = f"{BASE_URL}/workspaces"
FILES_URL = f"{BASE_URL}/files"

# Test credentials
TEST_EMAIL = "testuser@example.com"
TEST_PASSWORD = "SecurePass123!"

# Global variables for test data
access_token = None
workspace_id = None
page_id = None
file_id = None


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def print_result(test_name: str, passed: bool, details: str = ""):
    """Print test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status} - {test_name}")
    if details:
        print(f"  → {details}")


def setup_test_user():
    """Setup test user and get access token"""
    global access_token

    print_section("SETUP: Creating Test User & Authentication")

    # Try to register user
    register_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "full_name": "Test User"
    }
    response = requests.post(f"{AUTH_URL}/register", json=register_data)

    if response.status_code == 201:
        print_result("User Registration", True, "New user created")
    elif response.status_code == 400:
        print_result("User Registration", True, "User already exists (expected)")
    else:
        print_result("User Registration", False, f"Status: {response.status_code}")
        return False

    # Login to get token
    login_data = {
        "username": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    response = requests.post(f"{AUTH_URL}/login", data=login_data)

    if response.status_code == 200:
        data = response.json()
        access_token = data["access_token"]
        print_result("User Login", True, f"Token: {access_token[:20]}...")
        return True
    else:
        print_result("User Login", False, f"Status: {response.status_code}")
        return False


def setup_workspace():
    """Create a test workspace"""
    global workspace_id

    print_section("SETUP: Creating Test Workspace")

    headers = {"Authorization": f"Bearer {access_token}"}
    workspace_data = {
        "name": "File Upload Test Workspace",
        "description": "Workspace for testing file uploads"
    }

    response = requests.post(WORKSPACES_URL, json=workspace_data, headers=headers)

    if response.status_code == 201:
        data = response.json()
        workspace_id = data["id"]
        print_result("Workspace Creation", True, f"ID: {workspace_id}")
        return True
    else:
        print_result("Workspace Creation", False, f"Status: {response.status_code}")
        return False


def setup_page():
    """Create a test page"""
    global page_id

    print_section("SETUP: Creating Test Page")

    headers = {"Authorization": f"Bearer {access_token}"}
    page_data = {
        "title": "File Upload Test Page",
        "workspace_id": workspace_id
    }

    response = requests.post(f"{BASE_URL}/pages", json=page_data, headers=headers)

    if response.status_code == 201:
        data = response.json()
        page_id = data["id"]
        print_result("Page Creation", True, f"ID: {page_id}")
        return True
    else:
        print_result("Page Creation", False, f"Status: {response.status_code}")
        return False


def test_upload_image_file():
    """Test uploading an image file"""
    global file_id

    print_section("TEST 1: Upload Image File")

    headers = {"Authorization": f"Bearer {access_token}"}

    # Create a fake image file (1x1 pixel PNG)
    fake_image_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01'
        b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )

    files = {
        'file': ('test_image.png', io.BytesIO(fake_image_data), 'image/png')
    }
    data = {
        'workspace_id': workspace_id,
        'page_id': page_id,
        'folder': 'test-files'
    }

    response = requests.post(f"{FILES_URL}/upload", files=files, data=data, headers=headers)

    if response.status_code == 201:
        result = response.json()
        file_id = result["id"]
        print_result("Image Upload", True, f"File ID: {file_id}")
        print(f"  → Filename: {result['filename']}")
        print(f"  → Type: {result['file_type']}")
        print(f"  → Size: {result['size_bytes']} bytes ({result['size_kb']} KB)")
        print(f"  → URL: {result['storage_url'][:60]}...")
        if result.get('thumbnail_url'):
            print(f"  → Thumbnail: {result['thumbnail_url'][:60]}...")
        return True
    else:
        print_result("Image Upload", False, f"Status: {response.status_code}")
        print(f"  → Response: {response.text}")
        return False


def test_upload_text_file():
    """Test uploading a text document"""
    print_section("TEST 2: Upload Text Document")

    headers = {"Authorization": f"Bearer {access_token}"}

    # Create a text file
    text_content = b"This is a test document for file upload testing."
    files = {
        'file': ('test_document.txt', io.BytesIO(text_content), 'text/plain')
    }
    data = {
        'workspace_id': workspace_id,
        'folder': 'test-files'
    }

    response = requests.post(f"{FILES_URL}/upload", files=files, data=data, headers=headers)

    if response.status_code == 201:
        result = response.json()
        print_result("Text Document Upload", True, f"File ID: {result['id']}")
        print(f"  → Filename: {result['filename']}")
        print(f"  → Type: {result['file_type']}")
        print(f"  → Size: {result['size_bytes']} bytes")
        return True
    else:
        print_result("Text Document Upload", False, f"Status: {response.status_code}")
        print(f"  → Response: {response.text}")
        return False


def test_get_file_by_id():
    """Test retrieving a file by ID"""
    print_section("TEST 3: Get File by ID")

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{FILES_URL}/{file_id}", headers=headers)

    if response.status_code == 200:
        result = response.json()
        print_result("Get File by ID", True, f"Retrieved file: {result['filename']}")
        print(f"  → Type: {result['file_type']}")
        print(f"  → Workspace: {result['workspace_id']}")
        return True
    else:
        print_result("Get File by ID", False, f"Status: {response.status_code}")
        return False


def test_list_workspace_files():
    """Test listing files in a workspace"""
    print_section("TEST 4: List Workspace Files")

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{FILES_URL}/workspace/{workspace_id}", headers=headers)

    if response.status_code == 200:
        result = response.json()
        print_result("List Workspace Files", True, f"Found {result['total']} files")
        for file in result['files']:
            print(f"  → {file['filename']} ({file['file_type']}) - {file['size_kb']} KB")
        return True
    else:
        print_result("List Workspace Files", False, f"Status: {response.status_code}")
        return False


def test_list_workspace_files_by_type():
    """Test listing files in a workspace filtered by type"""
    print_section("TEST 5: List Workspace Files (Filtered by Type)")

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(
        f"{FILES_URL}/workspace/{workspace_id}",
        params={"file_type": "IMAGE"},
        headers=headers
    )

    if response.status_code == 200:
        result = response.json()
        print_result("List Files by Type (IMAGE)", True, f"Found {result['total']} image files")
        for file in result['files']:
            print(f"  → {file['filename']} - {file['size_kb']} KB")
        return True
    else:
        print_result("List Files by Type", False, f"Status: {response.status_code}")
        return False


def test_list_page_files():
    """Test listing files attached to a page"""
    print_section("TEST 6: List Page Files")

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{FILES_URL}/page/{page_id}", headers=headers)

    if response.status_code == 200:
        result = response.json()
        print_result("List Page Files", True, f"Found {result['total']} files")
        for file in result['files']:
            print(f"  → {file['filename']} ({file['file_type']})")
        return True
    else:
        print_result("List Page Files", False, f"Status: {response.status_code}")
        return False


def test_workspace_storage_stats():
    """Test getting workspace storage statistics"""
    print_section("TEST 7: Get Workspace Storage Stats")

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{FILES_URL}/workspace/{workspace_id}/stats", headers=headers)

    if response.status_code == 200:
        result = response.json()
        print_result("Workspace Storage Stats", True, f"Total: {result['total_size_mb']} MB")
        print(f"  → Total Files: {result['total_files']}")
        print(f"  → Total Size: {result['total_size_bytes']} bytes ({result['total_size_mb']} MB)")
        print(f"  → Files by Type:")
        for file_type, count in result['files_by_type'].items():
            print(f"    - {file_type}: {count}")
        return True
    else:
        print_result("Workspace Storage Stats", False, f"Status: {response.status_code}")
        return False


def test_upload_invalid_file_type():
    """Test uploading an invalid file type (should fail)"""
    print_section("TEST 8: Upload Invalid File Type (Should Fail)")

    headers = {"Authorization": f"Bearer {access_token}"}

    # Create a fake executable file
    fake_exe_data = b'\x4d\x5a\x90\x00'  # DOS header for .exe files
    files = {
        'file': ('malicious.exe', io.BytesIO(fake_exe_data), 'application/x-msdownload')
    }
    data = {
        'workspace_id': workspace_id,
    }

    response = requests.post(f"{FILES_URL}/upload", files=files, data=data, headers=headers)

    if response.status_code == 415:
        print_result("Reject Invalid File Type", True, "Correctly rejected .exe file")
        return True
    else:
        print_result("Reject Invalid File Type", False, f"Should return 415, got {response.status_code}")
        return False


def test_delete_file():
    """Test deleting a file"""
    print_section("TEST 9: Delete File")

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.delete(f"{FILES_URL}/{file_id}", headers=headers)

    if response.status_code == 204:
        print_result("Delete File", True, f"File {file_id} deleted successfully")

        # Verify file is deleted
        verify_response = requests.get(f"{FILES_URL}/{file_id}", headers=headers)
        if verify_response.status_code == 404:
            print_result("Verify File Deletion", True, "File no longer accessible")
            return True
        else:
            print_result("Verify File Deletion", False, "File still accessible after deletion")
            return False
    else:
        print_result("Delete File", False, f"Status: {response.status_code}")
        return False


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "=" * 60)
    print("  FILE UPLOAD API - INTEGRATION TESTS")
    print("=" * 60)

    results = []

    # Setup
    if not setup_test_user():
        print("\n✗ Setup failed: Could not authenticate user")
        return

    if not setup_workspace():
        print("\n✗ Setup failed: Could not create workspace")
        return

    if not setup_page():
        print("\n✗ Setup failed: Could not create page")
        return

    # Run tests
    results.append(("Upload Image File", test_upload_image_file()))
    results.append(("Upload Text Document", test_upload_text_file()))
    results.append(("Get File by ID", test_get_file_by_id()))
    results.append(("List Workspace Files", test_list_workspace_files()))
    results.append(("List Files by Type", test_list_workspace_files_by_type()))
    results.append(("List Page Files", test_list_page_files()))
    results.append(("Workspace Storage Stats", test_workspace_storage_stats()))
    results.append(("Reject Invalid File Type", test_upload_invalid_file_type()))
    results.append(("Delete File", test_delete_file()))

    # Print summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
