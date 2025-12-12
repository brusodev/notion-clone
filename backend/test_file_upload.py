"""
Quick test for file upload API
"""

import requests
import io

BASE_URL = "http://localhost:8000/api/v1"

# Create new test user
import time
TEST_EMAIL = f"filetest{int(time.time())}@test.com"
TEST_PASSWORD = "TestPass123!"

print("=" * 60)
print("  TESTING FILE UPLOAD API")
print("=" * 60)

# 1. Register user
print("\n1. Registering test user...")
register_data = {
    "email": TEST_EMAIL,
    "password": TEST_PASSWORD,
    "name": "File Upload Tester"
}
response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
if response.status_code != 201:
    print(f"   ERROR: Registration failed - {response.status_code}")
    print(f"   Response: {response.text}")
    exit(1)
print(f"   SUCCESS: User registered")

# 2. Login
print("\n2. Logging in...")
login_data = {
    "username": TEST_EMAIL,
    "password": TEST_PASSWORD
}
response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
if response.status_code != 200:
    print(f"   ERROR: Login failed - {response.status_code}")
    print(f"   Response: {response.text}")
    exit(1)

token = response.json()["access_token"]
print(f"   SUCCESS: Got token")

headers = {"Authorization": f"Bearer {token}"}

# 3. Get or create workspace
print("\n3. Getting or creating workspace...")
response = requests.get(f"{BASE_URL}/workspaces", headers=headers)
if response.status_code == 200 and response.json():
    workspace_id = response.json()[0]["id"]
else:
    # Create workspace
    ws_data = {"name": "File Upload Test Workspace", "description": "Test workspace"}
    response = requests.post(f"{BASE_URL}/workspaces", json=ws_data, headers=headers)
    if response.status_code != 201:
        print(f"   ERROR: Workspace creation failed - {response.status_code}")
        exit(1)
    workspace_id = response.json()["id"]
print(f"   SUCCESS: Using workspace {workspace_id}")

# 4. Create a test page
print("\n4. Creating test page...")
page_data = {
    "title": "File Upload Test Page",
    "workspace_id": workspace_id
}
response = requests.post(f"{BASE_URL}/pages", json=page_data, headers=headers)
if response.status_code != 201:
    print(f"   ERROR: Page creation failed - {response.status_code}")
    print(f"   Response: {response.text}")
    exit(1)

page_id = response.json()["id"]
print(f"   SUCCESS: Created page {page_id}")

# 5. Upload an image file
print("\n5. Uploading image file...")

# Create a small PNG image (1x1 pixel)
png_data = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01'
    b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
)

files = {
    'file': ('test_image.png', io.BytesIO(png_data), 'image/png')
}
data = {
    'workspace_id': workspace_id,
    'page_id': page_id,
    'folder': 'test-uploads'
}

response = requests.post(f"{BASE_URL}/files/upload", files=files, data=data, headers=headers)
if response.status_code != 201:
    print(f"   ERROR: Upload failed - {response.status_code}")
    print(f"   Response: {response.text}")
    exit(1)

file_info = response.json()
file_id = file_info["id"]
print(f"   SUCCESS: File uploaded!")
print(f"   - File ID: {file_id}")
print(f"   - Filename: {file_info['filename']}")
print(f"   - Type: {file_info['file_type']}")
print(f"   - Size: {file_info['size_bytes']} bytes ({file_info['size_kb']} KB)")
print(f"   - URL: {file_info['storage_url']}")
if file_info.get('thumbnail_url'):
    print(f"   - Thumbnail: {file_info['thumbnail_url']}")

# 6. Get file by ID
print("\n6. Retrieving file by ID...")
response = requests.get(f"{BASE_URL}/files/{file_id}", headers=headers)
if response.status_code != 200:
    print(f"   ERROR: Get file failed - {response.status_code}")
else:
    print(f"   SUCCESS: Retrieved file")

# 7. List workspace files
print("\n7. Listing workspace files...")
response = requests.get(f"{BASE_URL}/files/workspace/{workspace_id}", headers=headers)
if response.status_code != 200:
    print(f"   ERROR: List files failed - {response.status_code}")
else:
    files_data = response.json()
    print(f"   SUCCESS: Found {files_data['total']} file(s)")
    for f in files_data['files']:
        print(f"   - {f['filename']} ({f['file_type']}) - {f['size_kb']} KB")

# 8. List page files
print("\n8. Listing page files...")
response = requests.get(f"{BASE_URL}/files/page/{page_id}", headers=headers)
if response.status_code != 200:
    print(f"   ERROR: List page files failed - {response.status_code}")
else:
    files_data = response.json()
    print(f"   SUCCESS: Found {files_data['total']} file(s) in page")

# 9. Get workspace storage stats
print("\n9. Getting workspace storage stats...")
response = requests.get(f"{BASE_URL}/files/workspace/{workspace_id}/stats", headers=headers)
if response.status_code != 200:
    print(f"   ERROR: Get stats failed - {response.status_code}")
else:
    stats = response.json()
    print(f"   SUCCESS: Storage statistics")
    print(f"   - Total files: {stats['total_files']}")
    print(f"   - Total size: {stats['total_size_bytes']} bytes ({stats['total_size_mb']} MB)")
    print(f"   - Files by type: {stats['files_by_type']}")

# 10. Upload a text document
print("\n10. Uploading text document...")
text_data = b"This is a test document for file upload testing."
files = {
    'file': ('test_document.txt', io.BytesIO(text_data), 'text/plain')
}
data = {
    'workspace_id': workspace_id,
    'folder': 'test-uploads'
}

response = requests.post(f"{BASE_URL}/files/upload", files=files, data=data, headers=headers)
if response.status_code != 201:
    print(f"   ERROR: Upload failed - {response.status_code}")
else:
    file_info = response.json()
    print(f"   SUCCESS: Document uploaded!")
    print(f"   - Filename: {file_info['filename']}")
    print(f"   - Type: {file_info['file_type']}")

# 11. Delete a file
print("\n11. Deleting file...")
response = requests.delete(f"{BASE_URL}/files/{file_id}", headers=headers)
if response.status_code != 204:
    print(f"   ERROR: Delete failed - {response.status_code}")
else:
    print(f"   SUCCESS: File deleted")

    # Verify deletion
    response = requests.get(f"{BASE_URL}/files/{file_id}", headers=headers)
    if response.status_code == 404:
        print(f"   SUCCESS: File no longer accessible")
    else:
        print(f"   ERROR: File still accessible after deletion")

print("\n" + "=" * 60)
print("  ALL TESTS COMPLETED!")
print("=" * 60)
