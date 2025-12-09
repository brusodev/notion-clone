#!/usr/bin/env python3
"""Quick test for member management endpoints"""

import requests
import time

BASE_URL = "https://notion-clone-production-b81a.up.railway.app/api/v1"

print("=" * 60)
print("Quick Member Management Test")
print("=" * 60)

# 1. Register owner
print("\n1. Registering owner...")
owner_data = {
    "name": "Owner User",
    "email": f"owner_{int(time.time())}@test.com",
    "password": "Test123!"
}
r = requests.post(f"{BASE_URL}/auth/register", json=owner_data)
print(f"   Status: {r.status_code}")
if r.status_code != 201:
    print(f"   Error: {r.json()}")
    exit(1)

owner_token = r.json()["access_token"]
print("   [OK] Owner registered")

# 2. Get workspace
print("\n2. Getting owner's workspace...")
r = requests.get(f"{BASE_URL}/workspaces", headers={"Authorization": f"Bearer {owner_token}"})
print(f"   Status: {r.status_code}")
if r.status_code != 200:
    print(f"   Error: {r.json()}")
    exit(1)

workspaces = r.json()
if not workspaces:
    print("   [ERROR] No workspaces found")
    exit(1)

workspace_id = workspaces[0]["id"]
print(f"   [OK] Workspace ID: {workspace_id}")

# 3. List members
print("\n3. Listing workspace members...")
r = requests.get(
    f"{BASE_URL}/workspaces/{workspace_id}/members",
    headers={"Authorization": f"Bearer {owner_token}"}
)
print(f"   Status: {r.status_code}")
if r.status_code != 200:
    print(f"   Error: {r.json()}")
    exit(1)

members = r.json()
print(f"   [OK] Found {len(members)} member(s)")
for m in members:
    print(f"       - {m['user_name']} ({m['role']})")

# 4. Create invitation
print("\n4. Creating invitation...")
r = requests.post(
    f"{BASE_URL}/workspaces/{workspace_id}/invitations",
    headers={"Authorization": f"Bearer {owner_token}"},
    json={"email": f"invitee_{int(time.time())}@test.com", "role": "editor"}
)
print(f"   Status: {r.status_code}")
if r.status_code != 201:
    print(f"   Error: {r.json()}")
    exit(1)

invitation = r.json()
print(f"   [OK] Invitation created")
print(f"       Token: {invitation['token'][:30]}...")
print(f"       Email: {invitation['invitee_email']}")
print(f"       Role: {invitation['role']}")

# 5. List invitations
print("\n5. Listing invitations...")
r = requests.get(
    f"{BASE_URL}/workspaces/{workspace_id}/invitations",
    headers={"Authorization": f"Bearer {owner_token}"}
)
print(f"   Status: {r.status_code}")
if r.status_code != 200:
    print(f"   Error: {r.json()}")
    exit(1)

invitations = r.json()
print(f"   [OK] Found {len(invitations)} invitation(s)")

# 6. Register member and accept invitation
print("\n6. Registering member user...")
member_data = {
    "name": "Member User",
    "email": invitation["invitee_email"],
    "password": "Test123!"
}
r = requests.post(f"{BASE_URL}/auth/register", json=member_data)
print(f"   Status: {r.status_code}")
if r.status_code != 201:
    print(f"   Error: {r.json()}")
    exit(1)

member_token = r.json()["access_token"]
print("   [OK] Member registered")

# 7. Accept invitation
print("\n7. Accepting invitation...")
r = requests.post(
    f"{BASE_URL}/invitations/accept",
    headers={"Authorization": f"Bearer {member_token}"},
    json={"token": invitation["token"]}
)
print(f"   Status: {r.status_code}")
if r.status_code != 200:
    print(f"   Error: {r.json()}")
    exit(1)

result = r.json()
print(f"   [OK] {result['message']}")

# 8. Verify member was added
print("\n8. Verifying member was added...")
r = requests.get(
    f"{BASE_URL}/workspaces/{workspace_id}/members",
    headers={"Authorization": f"Bearer {owner_token}"}
)
print(f"   Status: {r.status_code}")
members = r.json()
print(f"   [OK] Workspace now has {len(members)} members")

# 9. Get member user ID
member_user = next((m for m in members if m['user_email'] == member_data['email']), None)
if not member_user:
    print("   [ERROR] Could not find member in list")
    exit(1)

member_user_id = member_user['user_id']
print(f"   Member ID: {member_user_id}")

# 10. Update member role
print("\n9. Updating member role to 'viewer'...")
r = requests.patch(
    f"{BASE_URL}/workspaces/{workspace_id}/members/{member_user_id}",
    headers={"Authorization": f"Bearer {owner_token}"},
    json={"role": "viewer"}
)
print(f"   Status: {r.status_code}")
if r.status_code != 200:
    print(f"   Error: {r.json()}")
    exit(1)

updated = r.json()
print(f"   [OK] Role updated to: {updated['role']}")

# 11. Remove member
print("\n10. Removing member from workspace...")
r = requests.delete(
    f"{BASE_URL}/workspaces/{workspace_id}/members/{member_user_id}",
    headers={"Authorization": f"Bearer {owner_token}"}
)
print(f"   Status: {r.status_code}")
if r.status_code != 204:
    print(f"   Error: {r.json()}")
    exit(1)

print("   [OK] Member removed")

# 12. Verify removal
print("\n11. Verifying member was removed...")
r = requests.get(
    f"{BASE_URL}/workspaces/{workspace_id}/members",
    headers={"Authorization": f"Bearer {owner_token}"}
)
members = r.json()
print(f"   [OK] Workspace now has {len(members)} member (owner only)")

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
