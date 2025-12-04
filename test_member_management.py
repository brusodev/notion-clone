#!/usr/bin/env python3
"""
Test script for Member Management features
Tests invitation system and member CRUD operations
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "https://notion-clone-production-b81a.up.railway.app"
API_V1 = f"{BASE_URL}/api/v1"

# Test data
TEST_USER_1 = {
    "name": "Test Owner",
    "email": f"owner_{datetime.now().timestamp()}@test.com",
    "password": "TestPass123!"
}

TEST_USER_2 = {
    "name": "Test Member",
    "email": f"member_{datetime.now().timestamp()}@test.com",
    "password": "TestPass123!"
}

# Test state
test_state = {
    "owner_token": None,
    "member_token": None,
    "workspace_id": None,
    "invitation_id": None,
    "invitation_token": None,
    "member_user_id": None
}


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def log_test(message: str):
    """Log test message"""
    print(f"\n{Colors.BLUE}[TEST]{Colors.END} {message}")


def log_success(message: str):
    """Log success message"""
    print(f"{Colors.GREEN}[OK]{Colors.END} {message}")


def log_error(message: str):
    """Log error message"""
    print(f"{Colors.RED}[FAIL]{Colors.END} {message}")


def log_info(message: str):
    """Log info message"""
    print(f"{Colors.YELLOW}[INFO]{Colors.END} {message}")


def make_request(method: str, endpoint: str, token: Optional[str] = None, data: Optional[Dict] = None) -> tuple:
    """Make HTTP request"""
    url = f"{API_V1}{endpoint}"
    headers = {"Content-Type": "application/json"}

    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PATCH":
            response = requests.patch(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")

        return response.status_code, response.json() if response.text else {}
    except Exception as e:
        return 0, {"error": str(e)}


def test_setup():
    """Setup: Register two users and create workspace"""
    log_test("Setting up test environment...")

    # Register owner
    log_info("Registering owner user...")
    status, response = make_request("POST", "/auth/register", data=TEST_USER_1)
    if status != 201:
        log_error(f"Failed to register owner: {response}")
        return False

    test_state["owner_token"] = response["access_token"]
    log_success("Owner registered and logged in")

    # Get owner workspace
    log_info("Getting owner workspace...")
    status, response = make_request("GET", "/workspaces", token=test_state["owner_token"])
    if status != 200 or not response:
        log_error(f"Failed to get workspaces: {response}")
        return False

    test_state["workspace_id"] = response[0]["id"]
    log_success(f"Workspace ID: {test_state['workspace_id']}")

    # Register member user
    log_info("Registering member user...")
    status, response = make_request("POST", "/auth/register", data=TEST_USER_2)
    if status != 201:
        log_error(f"Failed to register member: {response}")
        return False

    test_state["member_token"] = response["access_token"]

    # Get member user ID
    status, response = make_request("GET", "/auth/me", token=test_state["member_token"])
    if status != 200:
        log_error(f"Failed to get member info: {response}")
        return False

    test_state["member_user_id"] = response["id"]
    log_success(f"Member registered (ID: {test_state['member_user_id']})")

    return True


def test_list_members():
    """Test: List workspace members"""
    log_test("Test 1: List workspace members")

    status, response = make_request(
        "GET",
        f"/workspaces/{test_state['workspace_id']}/members",
        token=test_state["owner_token"]
    )

    if status == 200:
        log_success(f"Listed {len(response)} member(s)")
        return True
    else:
        log_error(f"Failed to list members: {response}")
        return False


def test_invite_member():
    """Test: Invite a new member"""
    log_test("Test 2: Invite member to workspace")

    invitation_data = {
        "email": TEST_USER_2["email"],
        "role": "editor"
    }

    status, response = make_request(
        "POST",
        f"/workspaces/{test_state['workspace_id']}/invitations",
        token=test_state["owner_token"],
        data=invitation_data
    )

    if status == 201:
        test_state["invitation_id"] = response["id"]
        test_state["invitation_token"] = response["token"]
        log_success(f"Invitation created (ID: {response['id']})")
        log_info(f"Invitation token: {response['token'][:20]}...")
        return True
    else:
        log_error(f"Failed to create invitation: {response}")
        return False


def test_list_invitations():
    """Test: List workspace invitations"""
    log_test("Test 3: List workspace invitations")

    status, response = make_request(
        "GET",
        f"/workspaces/{test_state['workspace_id']}/invitations",
        token=test_state["owner_token"]
    )

    if status == 200:
        log_success(f"Listed {len(response)} invitation(s)")
        return True
    else:
        log_error(f"Failed to list invitations: {response}")
        return False


def test_accept_invitation():
    """Test: Accept invitation"""
    log_test("Test 4: Accept invitation")

    accept_data = {
        "token": test_state["invitation_token"]
    }

    status, response = make_request(
        "POST",
        "/invitations/accept",
        token=test_state["member_token"],
        data=accept_data
    )

    if status == 200:
        log_success(f"Invitation accepted: {response['message']}")
        return True
    else:
        log_error(f"Failed to accept invitation: {response}")
        return False


def test_verify_member_added():
    """Test: Verify member was added to workspace"""
    log_test("Test 5: Verify member was added")

    status, response = make_request(
        "GET",
        f"/workspaces/{test_state['workspace_id']}/members",
        token=test_state["owner_token"]
    )

    if status == 200:
        member_count = len(response)
        if member_count == 2:
            log_success(f"Workspace now has {member_count} members")
            return True
        else:
            log_error(f"Expected 2 members, found {member_count}")
            return False
    else:
        log_error(f"Failed to list members: {response}")
        return False


def test_update_member_role():
    """Test: Update member role"""
    log_test("Test 6: Update member role")

    role_data = {
        "role": "viewer"
    }

    status, response = make_request(
        "PATCH",
        f"/workspaces/{test_state['workspace_id']}/members/{test_state['member_user_id']}",
        token=test_state["owner_token"],
        data=role_data
    )

    if status == 200:
        log_success(f"Member role updated to: {response['role']}")
        return True
    else:
        log_error(f"Failed to update member role: {response}")
        return False


def test_remove_member():
    """Test: Remove member from workspace"""
    log_test("Test 7: Remove member from workspace")

    status, response = make_request(
        "DELETE",
        f"/workspaces/{test_state['workspace_id']}/members/{test_state['member_user_id']}",
        token=test_state["owner_token"]
    )

    if status == 204:
        log_success("Member removed successfully")
        return True
    else:
        log_error(f"Failed to remove member: {response}")
        return False


def test_verify_member_removed():
    """Test: Verify member was removed"""
    log_test("Test 8: Verify member was removed")

    status, response = make_request(
        "GET",
        f"/workspaces/{test_state['workspace_id']}/members",
        token=test_state["owner_token"]
    )

    if status == 200:
        member_count = len(response)
        if member_count == 1:
            log_success(f"Workspace now has {member_count} member (owner only)")
            return True
        else:
            log_error(f"Expected 1 member, found {member_count}")
            return False
    else:
        log_error(f"Failed to list members: {response}")
        return False


def test_member_cannot_access_after_removal():
    """Test: Verify removed member cannot access workspace"""
    log_test("Test 9: Verify removed member cannot access workspace")

    status, response = make_request(
        "GET",
        f"/workspaces/{test_state['workspace_id']}",
        token=test_state["member_token"]
    )

    if status == 403:
        log_success("Removed member correctly denied access")
        return True
    else:
        log_error(f"Removed member should not have access (got status {status})")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Member Management Test Suite")
    print("=" * 60)

    tests = [
        ("Setup", test_setup),
        ("List Members", test_list_members),
        ("Invite Member", test_invite_member),
        ("List Invitations", test_list_invitations),
        ("Accept Invitation", test_accept_invitation),
        ("Verify Member Added", test_verify_member_added),
        ("Update Member Role", test_update_member_role),
        ("Remove Member", test_remove_member),
        ("Verify Member Removed", test_verify_member_removed),
        ("Verify Access Denied", test_member_cannot_access_after_removal)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            log_error(f"Test '{name}' crashed: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total) * 100

    for name, result in results:
        status_icon = f"{Colors.GREEN}✓{Colors.END}" if result else f"{Colors.RED}✗{Colors.END}"
        print(f"{status_icon} {name}")

    print("\n" + "-" * 60)
    print(f"Passed: {passed}/{total} ({success_rate:.1f}%)")
    print("=" * 60)

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
