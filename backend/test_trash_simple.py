"""Simple test for trash functionality"""
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

# Register and login
timestamp = int(time.time())
user_data = {
    "email": f"trashtest_{timestamp}@test.com",
    "password": "Test123!",
    "name": "Trash Test User"
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
    "name": "Trash Test Workspace"
}, headers=headers)
workspace_id = resp.json()["id"]
print(f"   Workspace ID: {workspace_id}")

print("4. Creating page...")
resp = requests.post(f"{BASE_URL}/pages/", json={
    "title": "Page to delete",
    "workspace_id": workspace_id
}, headers=headers)
page_id = resp.json()["id"]
print(f"   Page ID: {page_id}")

print("5. Archiving page (move to trash)...")
resp = requests.delete(f"{BASE_URL}/pages/{page_id}", headers=headers)
print(f"   Status: {resp.status_code}")

print("6. Listing trash...")
resp = requests.get(f"{BASE_URL}/pages/trash?workspace_id={workspace_id}", headers=headers)
print(f"   Status: {resp.status_code}")
print(f"   Trash items: {len(resp.json())}")

print("7. Restoring page...")
resp = requests.post(f"{BASE_URL}/pages/{page_id}/restore", headers=headers)
print(f"   Status: {resp.status_code}")
print(f"   Is archived: {resp.json().get('is_archived')}")

print("8. Verifying trash is empty...")
resp = requests.get(f"{BASE_URL}/pages/trash?workspace_id={workspace_id}", headers=headers)
print(f"   Status: {resp.status_code}")
print(f"   Trash items: {len(resp.json())}")

print("9. Archiving again...")
resp = requests.delete(f"{BASE_URL}/pages/{page_id}", headers=headers)
print(f"   Status: {resp.status_code}")

print("10. Permanently deleting...")
resp = requests.delete(f"{BASE_URL}/pages/{page_id}/permanent", headers=headers)
print(f"   Status: {resp.status_code}")

print("11. Verifying page is gone (should get 404)...")
try:
    resp = requests.get(f"{BASE_URL}/pages/{page_id}", headers=headers)
    print(f"   Status: {resp.status_code}")
    if resp.status_code == 404:
        print("   ✓ Page successfully deleted!")
    else:
        print(f"   ✗ Expected 404, got {resp.status_code}")
except Exception as e:
    print(f"   ✗ Request failed: {e}")

print("\n✅ All trash/restore tests completed!")
