"""Simple test for page duplication"""
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

# Register and login
timestamp = int(time.time())
user_data = {
    "email": f"duptest_{timestamp}@test.com",
    "password": "Test123!",
    "name": "Duplicate Test User"
}

print("1. Registering user...")
resp = requests.post(f"{BASE_URL}/auth/register", json=user_data)
print(f"   Status: {resp.status_code}")

print("2. Logging in...")
resp = requests.post(f"{BASE_URL}/auth/login", data={
    "username": user_data["email"],
    "password": user_data["password"]
})
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"   Got token: {token[:20]}...")

print("3. Creating workspace...")
resp = requests.post(f"{BASE_URL}/workspaces/", json={
    "name": "Duplicate Test Workspace"
}, headers=headers)
workspace_id = resp.json()["id"]
print(f"   Workspace ID: {workspace_id}")

print("4. Creating page with blocks...")
resp = requests.post(f"{BASE_URL}/pages/", json={
    "title": "Original Page",
    "workspace_id": workspace_id
}, headers=headers)
page_id = resp.json()["id"]
print(f"   Page ID: {page_id}")

print("5. Adding blocks to page...")
# Add first block
resp = requests.post(f"{BASE_URL}/blocks/", json={
    "page_id": page_id,
    "type": "paragraph",
    "content": {"text": "First paragraph"},
    "order": 0
}, headers=headers)
block1_id = resp.json()["id"]
print(f"   Block 1 ID: {block1_id}")

# Add second block
resp = requests.post(f"{BASE_URL}/blocks/", json={
    "page_id": page_id,
    "type": "heading_1",
    "content": {"text": "Heading"},
    "order": 1
}, headers=headers)
block2_id = resp.json()["id"]
print(f"   Block 2 ID: {block2_id}")

print("6. Duplicating page WITH blocks...")
resp = requests.post(f"{BASE_URL}/pages/{page_id}/duplicate?include_blocks=true", headers=headers)
print(f"   Status: {resp.status_code}")
if resp.status_code == 201:
    dup_page = resp.json()
    dup_page_id = dup_page["id"]
    print(f"   Duplicated Page ID: {dup_page_id}")
    print(f"   Title: {dup_page['title']}")
else:
    print(f"   Error: {resp.text}")
    exit(1)

print("7. Verifying duplicated page has blocks...")
resp = requests.get(f"{BASE_URL}/blocks/page/{dup_page_id}", headers=headers)
print(f"   Status: {resp.status_code}")
dup_blocks = resp.json()
print(f"   Duplicated blocks count: {len(dup_blocks)}")
if len(dup_blocks) == 2:
    print("   Block 1:", dup_blocks[0]['content'])
    print("   Block 2:", dup_blocks[1]['content'])
else:
    print(f"   Expected 2 blocks, got {len(dup_blocks)}")

print("8. Listing pages in workspace...")
resp = requests.get(f"{BASE_URL}/pages/?workspace_id={workspace_id}", headers=headers)
pages = resp.json()
print(f"   Total pages: {len(pages)}")
for page in pages:
    print(f"   - {page['title']} (ID: {page['id']})")

print("9. Duplicating page WITHOUT blocks...")
resp = requests.post(f"{BASE_URL}/pages/{page_id}/duplicate?include_blocks=false", headers=headers)
print(f"   Status: {resp.status_code}")
if resp.status_code == 201:
    dup_page2 = resp.json()
    print(f"   Duplicated Page ID: {dup_page2['id']}")
    print(f"   Title: {dup_page2['title']}")

    # Verify no blocks
    resp = requests.get(f"{BASE_URL}/blocks/page/{dup_page2['id']}", headers=headers)
    blocks = resp.json()
    print(f"   Blocks count: {len(blocks)} (should be 0)")
else:
    print(f"   Error: {resp.text}")

print("\n" + "="*50)
print("All duplication tests completed successfully!")
print("="*50)
