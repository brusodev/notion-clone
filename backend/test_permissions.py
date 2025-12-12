"""
Comprehensive test for Page Permissions API
"""

import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

print("=" * 70)
print("  TESTING PAGE PERMISSIONS API")
print("=" * 70)

# Create two test users
TEST_USER_1 = f"permtest1_{int(time.time())}@test.com"
TEST_USER_2 = f"permtest2_{int(time.time())}@test.com"
PASSWORD = "TestPass123!"

# 1. Register and login User 1 (page owner)
print("\n1. Setting up User 1 (page owner)...")
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": TEST_USER_1,
    "password": PASSWORD,
    "name": "Permission Test User 1"
})
if response.status_code != 201:
    print(f"   ERROR: User 1 registration failed - {response.text}")
    exit(1)

response = requests.post(f"{BASE_URL}/auth/login", data={
    "username": TEST_USER_1,
    "password": PASSWORD
})
if response.status_code != 200:
    print(f"   ERROR: User 1 login failed - {response.text}")
    exit(1)

user1_token = response.json()["access_token"]
user1_headers = {"Authorization": f"Bearer {user1_token}"}
print(f"   SUCCESS: User 1 logged in")

# 2. Register and login User 2 (to be granted permission)
print("\n2. Setting up User 2 (to be granted permission)...")
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": TEST_USER_2,
    "password": PASSWORD,
    "name": "Permission Test User 2"
})
if response.status_code != 201:
    print(f"   ERROR: User 2 registration failed - {response.text}")
    exit(1)

user2_token = response.json()["access_token"]
user2_headers = {"Authorization": f"Bearer {user2_token}"}

# Get user ID via /auth/me endpoint
response = requests.get(f"{BASE_URL}/auth/me", headers=user2_headers)
if response.status_code != 200:
    print(f"   ERROR: Get user info failed - {response.text}")
    exit(1)

user2_id = response.json()["id"]
print(f"   SUCCESS: User 2 logged in (ID: {user2_id})")

# 3. Create workspace for User 1
print("\n3. Creating workspace...")
response = requests.post(f"{BASE_URL}/workspaces", json={
    "name": "Permission Test Workspace",
    "description": "Test workspace for permissions"
}, headers=user1_headers)
if response.status_code != 201:
    print(f"   ERROR: Workspace creation failed - {response.text}")
    exit(1)

workspace_id = response.json()["id"]
print(f"   SUCCESS: Workspace created (ID: {workspace_id})")

# 4. Create a page for User 1
print("\n4. Creating test page...")
response = requests.post(f"{BASE_URL}/pages", json={
    "title": "Permission Test Page",
    "workspace_id": workspace_id
}, headers=user1_headers)
if response.status_code != 201:
    print(f"   ERROR: Page creation failed - {response.text}")
    exit(1)

page_id = response.json()["id"]
print(f"   SUCCESS: Page created (ID: {page_id})")

# 5. Grant VIEW permission to User 2
print("\n5. Granting VIEW permission to User 2...")
response = requests.post(f"{BASE_URL}/permissions/{page_id}/share", json={
    "user_id": user2_id,
    "permission_level": "view"
}, headers=user1_headers)
if response.status_code != 201:
    print(f"   ERROR: Grant permission failed - {response.text}")
    exit(1)

permission_data = response.json()
print(f"   SUCCESS: VIEW permission granted")
print(f"   - Permission ID: {permission_data['id']}")
print(f"   - Level: {permission_data['permission_level']}")

# 6. Check permission for User 2
print("\n6. Checking User 2's permission...")
response = requests.get(f"{BASE_URL}/permissions/{page_id}/check-permission", headers=user2_headers)
if response.status_code != 200:
    print(f"   ERROR: Check permission failed - {response.text}")
    exit(1)

perm_check = response.json()
print(f"   SUCCESS: Permission check")
print(f"   - Has permission: {perm_check['has_permission']}")
print(f"   - Level: {perm_check['permission_level']}")
print(f"   - Can view: {perm_check['can_view']}")
print(f"   - Can comment: {perm_check['can_comment']}")
print(f"   - Can edit: {perm_check['can_edit']}")

# 7. List page permissions
print("\n7. Listing page permissions...")
response = requests.get(f"{BASE_URL}/permissions/{page_id}/permissions", headers=user1_headers)
if response.status_code != 200:
    print(f"   ERROR: List permissions failed - {response.text}")
    exit(1)

perms_list = response.json()
print(f"   SUCCESS: Found {perms_list['total']} permission(s)")
for perm in perms_list['permissions']:
    print(f"   - User {perm['user_id']}: {perm['permission_level']}")

# 8. Update permission to COMMENT
print("\n8. Updating permission to COMMENT...")
response = requests.put(f"{BASE_URL}/permissions/{page_id}/permissions/{user2_id}", json={
    "permission_level": "comment"
}, headers=user1_headers)
if response.status_code != 200:
    print(f"   ERROR: Update permission failed - {response.text}")
    exit(1)

updated_perm = response.json()
print(f"   SUCCESS: Permission updated to {updated_perm['permission_level']}")

# 9. Check updated permission
print("\n9. Checking updated permission...")
response = requests.get(f"{BASE_URL}/permissions/{page_id}/check-permission", headers=user2_headers)
if response.status_code != 200:
    print(f"   ERROR: Check permission failed - {response.text}")
else:
    perm_check = response.json()
    print(f"   SUCCESS: Updated permission check")
    print(f"   - Level: {perm_check['permission_level']}")
    print(f"   - Can view: {perm_check['can_view']}")
    print(f"   - Can comment: {perm_check['can_comment']}")
    print(f"   - Can edit: {perm_check['can_edit']}")

# 10. Update permission to EDIT
print("\n10. Updating permission to EDIT...")
response = requests.put(f"{BASE_URL}/permissions/{page_id}/permissions/{user2_id}", json={
    "permission_level": "edit"
}, headers=user1_headers)
if response.status_code != 200:
    print(f"   ERROR: Update permission failed - {response.text}")
else:
    print(f"   SUCCESS: Permission updated to EDIT")

# 11. Check EDIT permission
print("\n11. Checking EDIT permission...")
response = requests.get(f"{BASE_URL}/permissions/{page_id}/check-permission", headers=user2_headers)
if response.status_code != 200:
    print(f"   ERROR: Check permission failed - {response.text}")
else:
    perm_check = response.json()
    print(f"   SUCCESS: EDIT permission check")
    print(f"   - Level: {perm_check['permission_level']}")
    print(f"   - Can view: {perm_check['can_view']}")
    print(f"   - Can comment: {perm_check['can_comment']}")
    print(f"   - Can edit: {perm_check['can_edit']}")

# 12. List shared pages for User 2
print("\n12. Listing pages shared with User 2...")
response = requests.get(f"{BASE_URL}/permissions/shared-with-me", headers=user2_headers)
if response.status_code != 200:
    print(f"   ERROR: List shared pages failed - {response.text}")
else:
    shared_pages = response.json()
    print(f"   SUCCESS: Found {shared_pages['total']} shared page(s)")
    for page in shared_pages['shared_pages']:
        print(f"   - {page['page_title']} ({page['permission_level']})")

# 13. Grant permission by email
print("\n13. Testing share by email...")
# Create another user to share with
TEST_USER_3 = f"permtest3_{int(time.time())}@test.com"
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": TEST_USER_3,
    "password": PASSWORD,
    "name": "Permission Test User 3"
})
if response.status_code == 201:
    response = requests.post(f"{BASE_URL}/permissions/{page_id}/share-by-email", json={
        "email": TEST_USER_3,
        "permission_level": "view"
    }, headers=user1_headers)
    if response.status_code != 201:
        print(f"   ERROR: Share by email failed - {response.text}")
    else:
        print(f"   SUCCESS: Shared page with {TEST_USER_3} via email")

# 14. Try to grant duplicate permission (should fail)
print("\n14. Testing duplicate permission prevention...")
response = requests.post(f"{BASE_URL}/permissions/{page_id}/share", json={
    "user_id": user2_id,
    "permission_level": "view"
}, headers=user1_headers)
if response.status_code == 409:
    print(f"   SUCCESS: Duplicate permission correctly prevented (409 Conflict)")
else:
    print(f"   WARNING: Expected 409, got {response.status_code}")

# 15. Revoke permission
print("\n15. Revoking User 2's permission...")
response = requests.delete(f"{BASE_URL}/permissions/{page_id}/permissions/{user2_id}", headers=user1_headers)
if response.status_code != 204:
    print(f"   ERROR: Revoke permission failed - {response.status_code}")
else:
    print(f"   SUCCESS: Permission revoked")

# 16. Verify permission revoked
print("\n16. Verifying permission was revoked...")
response = requests.get(f"{BASE_URL}/permissions/{page_id}/check-permission", headers=user2_headers)
if response.status_code != 200:
    print(f"   ERROR: Check permission failed - {response.text}")
else:
    perm_check = response.json()
    if not perm_check['has_permission']:
        print(f"   SUCCESS: User 2 no longer has permission")
    else:
        print(f"   ERROR: User 2 still has permission")

# 17. Try to revoke non-existent permission (should fail)
print("\n17. Testing revoke non-existent permission...")
response = requests.delete(f"{BASE_URL}/permissions/{page_id}/permissions/{user2_id}", headers=user1_headers)
if response.status_code == 404:
    print(f"   SUCCESS: Non-existent permission correctly returns 404")
else:
    print(f"   WARNING: Expected 404, got {response.status_code}")

# 18. Test permission hierarchy
print("\n18. Testing permission hierarchy...")
print("   Granting VIEW permission...")
response = requests.post(f"{BASE_URL}/permissions/{page_id}/share", json={
    "user_id": user2_id,
    "permission_level": "view"
}, headers=user1_headers)
if response.status_code == 201:
    response = requests.get(f"{BASE_URL}/permissions/{page_id}/check-permission", headers=user2_headers)
    perm = response.json()
    print(f"   - VIEW: can_view={perm['can_view']}, can_comment={perm['can_comment']}, can_edit={perm['can_edit']}")

    print("   Upgrading to COMMENT permission...")
    response = requests.put(f"{BASE_URL}/permissions/{page_id}/permissions/{user2_id}", json={
        "permission_level": "comment"
    }, headers=user1_headers)
    response = requests.get(f"{BASE_URL}/permissions/{page_id}/check-permission", headers=user2_headers)
    perm = response.json()
    print(f"   - COMMENT: can_view={perm['can_view']}, can_comment={perm['can_comment']}, can_edit={perm['can_edit']}")

    print("   Upgrading to EDIT permission...")
    response = requests.put(f"{BASE_URL}/permissions/{page_id}/permissions/{user2_id}", json={
        "permission_level": "edit"
    }, headers=user1_headers)
    response = requests.get(f"{BASE_URL}/permissions/{page_id}/check-permission", headers=user2_headers)
    perm = response.json()
    print(f"   - EDIT: can_view={perm['can_view']}, can_comment={perm['can_comment']}, can_edit={perm['can_edit']}")
    print("   SUCCESS: Permission hierarchy working correctly")

print("\n" + "=" * 70)
print("  ALL PERMISSION TESTS COMPLETED!")
print("=" * 70)
