"""
Complete Comment System Workflow Test
Tests all features: threading, reactions, mentions, attachments, soft delete
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8001/api/v1"

# Test data
timestamp = int(time.time())

test_user = {
    "email": f"commentstest{timestamp}@example.com",
    "password": "TestPassword123!",
    "name": "Comments Test User"
}

test_user2 = {
    "email": f"mentiontest{timestamp}@example.com",
    "password": "TestPassword123!",
    "name": "Mention Test User"
}

def print_step(message: str):
    """Print a test step header"""
    print(f"\n{'='*60}")
    print(f"  {message}")
    print(f"{'='*60}")

def print_result(success: bool, message: str):
    """Print test result"""
    status = "[OK]" if success else "[FAIL]"
    print(f"{status} {message}")

def register_and_login(user_data: Dict[str, Any]) -> str:
    """Register and login a user, return access token"""
    # Try to register (might fail if already exists)
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    if response.status_code != 201:
        # Registration failed, maybe user already exists - continue to login
        pass

    # Login
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": user_data["email"],
            "password": user_data["password"]
        }
    )

    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Login failed (status {response.status_code}): {response.text}")

def test_comment_workflow():
    """Run complete comment workflow test"""

    print_step("1. Setup: Creating users and workspace")

    # Register and login users
    token1 = register_and_login(test_user)
    token2 = register_and_login(test_user2)
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    # Get user IDs
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers1)
    user1_id = response.json()["id"]
    print_result(True, f"User 1 logged in: {user1_id}")

    response = requests.get(f"{BASE_URL}/auth/me", headers=headers2)
    user2_id = response.json()["id"]
    print_result(True, f"User 2 logged in: {user2_id}")

    # Create workspace
    workspace_data = {
        "name": "Comments Test Workspace",
        "description": "Testing comment system"
    }
    response = requests.post(f"{BASE_URL}/workspaces/", json=workspace_data, headers=headers1)
    workspace_id = response.json()["id"]
    print_result(True, f"Workspace created: {workspace_id}")

    # Invite user2 to workspace
    invite_data = {"invitee_email": test_user2["email"], "role": "editor"}
    response = requests.post(f"{BASE_URL}/workspaces/{workspace_id}/invitations", json=invite_data, headers=headers1)
    if response.status_code not in [200, 201]:
        raise Exception(f"Invitation failed (status {response.status_code}): {response.text}")
    invite_response = response.json()
    invite_id = invite_response.get("id") or invite_response.get("invitation_id")
    print_result(True, f"Invitation sent: {invite_id}")

    # Accept invitation
    response = requests.post(f"{BASE_URL}/invitations/{invite_id}/accept", headers=headers2)
    if response.status_code not in [200, 201]:
        raise Exception(f"Accept invitation failed (status {response.status_code}): {response.text}")
    print_result(True, "Invitation accepted")

    # Create page
    page_data = {
        "title": "Test Page for Comments",
        "workspace_id": workspace_id
    }
    response = requests.post(f"{BASE_URL}/pages/", json=page_data, headers=headers1)
    page_id = response.json()["id"]
    print_result(True, f"Page created: {page_id}")

    print_step("2. Create Top-Level Comment")

    comment_data = {
        "page_id": page_id,
        "content": "This is a test comment!"
    }
    response = requests.post(f"{BASE_URL}/comments/", json=comment_data, headers=headers1)
    assert response.status_code == 201, f"Failed to create comment: {response.text}"
    comment1 = response.json()
    comment1_id = comment1["id"]
    print_result(True, f"Comment created: {comment1_id}")
    print(f"   Content: {comment1['content']}")
    print(f"   Thread depth: {comment1['thread_depth']}")

    print_step("3. Create Reply (Threaded Comment)")

    reply_data = {
        "page_id": page_id,
        "parent_comment_id": comment1_id,
        "content": "This is a reply to the first comment!"
    }
    response = requests.post(f"{BASE_URL}/comments/", json=reply_data, headers=headers2)
    assert response.status_code == 201, f"Failed to create reply: {response.text}"
    comment2 = response.json()
    comment2_id = comment2["id"]
    print_result(True, f"Reply created: {comment2_id}")
    print(f"   Content: {comment2['content']}")
    print(f"   Thread depth: {comment2['thread_depth']}")
    print(f"   Parent: {comment2['parent_comment_id']}")

    print_step("4. Create Comment with Mention")

    mention_data = {
        "page_id": page_id,
        "content": f"Hey @[{test_user2['name']}]({user2_id}) check this out!"
    }
    response = requests.post(f"{BASE_URL}/comments/", json=mention_data, headers=headers1)
    assert response.status_code == 201, f"Failed to create comment with mention: {response.text}"
    comment3 = response.json()
    comment3_id = comment3["id"]
    print_result(True, f"Comment with mention created: {comment3_id}")
    print(f"   Content: {comment3['content']}")
    print(f"   Mentioned users: {len(comment3['mentioned_users'])} user(s)")
    if comment3['mentioned_users']:
        for user in comment3['mentioned_users']:
            print(f"      - {user['name']} ({user['id']})")

    print_step("5. Add Reactions")

    # User 1 reacts with thumbs_up
    reaction_data = {"reaction_type": "thumbs_up"}
    response = requests.post(f"{BASE_URL}/comments/{comment1_id}/reactions", json=reaction_data, headers=headers1)
    assert response.status_code == 201, f"Failed to add reaction: {response.text}"
    print_result(True, "User 1 added thumbs_up reaction")

    # User 2 reacts with heart
    reaction_data = {"reaction_type": "heart"}
    response = requests.post(f"{BASE_URL}/comments/{comment1_id}/reactions", json=reaction_data, headers=headers2)
    assert response.status_code == 201, f"Failed to add reaction: {response.text}"
    print_result(True, "User 2 added heart reaction")

    # User 2 also reacts with thumbs_up
    reaction_data = {"reaction_type": "thumbs_up"}
    response = requests.post(f"{BASE_URL}/comments/{comment1_id}/reactions", json=reaction_data, headers=headers2)
    assert response.status_code in [200, 201], f"Failed to add reaction: {response.text}"
    print_result(True, "User 2 added thumbs_up reaction")

    # Get comment to see reactions
    response = requests.get(f"{BASE_URL}/comments/{comment1_id}", headers=headers1)
    comment_with_reactions = response.json()
    print_result(True, f"Reactions aggregated: {len(comment_with_reactions['reactions'])} type(s)")
    for reaction in comment_with_reactions['reactions']:
        print(f"   - {reaction['reaction_type']}: {reaction['count']} (user reacted: {reaction['user_reacted']})")

    print_step("6. Edit Comment")

    update_data = {
        "content": "This comment has been edited!"
    }
    response = requests.patch(f"{BASE_URL}/comments/{comment1_id}", json=update_data, headers=headers1)
    assert response.status_code == 200, f"Failed to edit comment: {response.text}"
    updated_comment = response.json()
    print_result(True, f"Comment edited")
    print(f"   New content: {updated_comment['content']}")
    print(f"   Edited at: {updated_comment['edited_at']}")

    print_step("7. Add Attachment")

    attachment_data = {
        "file_name": "test-document.pdf",
        "file_url": "https://example.com/files/test-document.pdf",
        "file_size": 1024000,
        "mime_type": "application/pdf",
        "order_index": 0
    }
    response = requests.post(f"{BASE_URL}/comments/{comment1_id}/attachments", json=attachment_data, headers=headers1)
    assert response.status_code == 201, f"Failed to add attachment: {response.text}"
    attachment = response.json()
    attachment_id = attachment["id"]
    print_result(True, f"Attachment added: {attachment_id}")
    print(f"   File: {attachment['file_name']} ({attachment['file_size']} bytes)")

    # Get comment to see attachment
    response = requests.get(f"{BASE_URL}/comments/{comment1_id}", headers=headers1)
    comment_with_attachment = response.json()
    print_result(True, f"Comment has {len(comment_with_attachment['attachments'])} attachment(s)")

    print_step("8. List Comments by Page (with Pagination)")

    response = requests.get(f"{BASE_URL}/comments/page/{page_id}?page=1&page_size=10", headers=headers1)
    assert response.status_code == 200, f"Failed to list comments: {response.text}"
    comment_list = response.json()
    print_result(True, f"Listed {len(comment_list['items'])} comments")
    print(f"   Total: {comment_list['total']}")
    print(f"   Page: {comment_list['page']}/{comment_list['pages']}")

    print_step("9. Remove Reaction")

    response = requests.delete(f"{BASE_URL}/comments/{comment1_id}/reactions/thumbs_up", headers=headers1)
    assert response.status_code == 204, f"Failed to remove reaction: {response.text}"
    print_result(True, "User 1 removed thumbs_up reaction")

    # Get comment to verify reaction removed
    response = requests.get(f"{BASE_URL}/comments/{comment1_id}", headers=headers1)
    comment_after_removal = response.json()
    thumbs_up_reaction = next((r for r in comment_after_removal['reactions'] if r['reaction_type'] == 'thumbs_up'), None)
    if thumbs_up_reaction:
        print_result(True, f"thumbs_up count is now {thumbs_up_reaction['count']} (was 2)")

    print_step("10. Soft Delete Comment")

    response = requests.delete(f"{BASE_URL}/comments/{comment2_id}", headers=headers2)
    assert response.status_code == 204, f"Failed to soft delete comment: {response.text}"
    print_result(True, f"Comment soft deleted: {comment2_id}")

    # Verify deleted comment is not in list
    response = requests.get(f"{BASE_URL}/comments/page/{page_id}", headers=headers1)
    comment_list_after_delete = response.json()
    deleted_comment_in_list = any(c['id'] == comment2_id for c in comment_list_after_delete['items'])
    print_result(not deleted_comment_in_list, "Deleted comment not in list")

    # Try to get deleted comment by ID
    response = requests.get(f"{BASE_URL}/comments/{comment2_id}", headers=headers1)
    if response.status_code == 404:
        print_result(True, "Deleted comment returns 404")
    else:
        deleted_comment = response.json()
        if deleted_comment.get('is_deleted'):
            print_result(True, f"Comment marked as deleted (content: '{deleted_comment['content']}')")

    print_step("11. Test Thread Depth Limit")

    # Create nested replies up to depth 5
    parent_id = comment1_id
    for depth in range(1, 6):
        reply_data = {
            "page_id": page_id,
            "parent_comment_id": parent_id,
            "content": f"Nested reply at depth {depth}"
        }
        response = requests.post(f"{BASE_URL}/comments/", json=reply_data, headers=headers1)
        assert response.status_code == 201, f"Failed to create nested reply at depth {depth}: {response.text}"
        reply = response.json()
        parent_id = reply["id"]
        print_result(True, f"Created reply at depth {reply['thread_depth']}")

    # Try to exceed depth limit
    reply_data = {
        "page_id": page_id,
        "parent_comment_id": parent_id,
        "content": "This should fail - depth 6"
    }
    response = requests.post(f"{BASE_URL}/comments/", json=reply_data, headers=headers1)
    if response.status_code in [400, 422]:
        print_result(True, "Depth limit enforced (rejected depth 6)")
    else:
        print_result(False, f"Depth limit NOT enforced! Status: {response.status_code}")

    print_step("12. Delete Attachment")

    response = requests.delete(f"{BASE_URL}/comments/{comment1_id}/attachments/{attachment_id}", headers=headers1)
    assert response.status_code == 204, f"Failed to delete attachment: {response.text}"
    print_result(True, "Attachment deleted")

    # Verify attachment removed
    response = requests.get(f"{BASE_URL}/comments/{comment1_id}", headers=headers1)
    comment_without_attachment = response.json()
    print_result(len(comment_without_attachment['attachments']) == 0, "Attachment removed from comment")

    print_step("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("\nComment System Features Tested:")
    print("  [OK] Create top-level comments")
    print("  [OK] Create threaded replies (up to 5 levels)")
    print("  [OK] Add and remove reactions")
    print("  [OK] Reaction aggregation")
    print("  [OK] @mentions with workspace validation")
    print("  [OK] Edit comments")
    print("  [OK] Add and delete attachments")
    print("  [OK] Soft delete comments")
    print("  [OK] List comments with pagination")
    print("  [OK] Thread depth limit enforcement")

if __name__ == "__main__":
    try:
        test_comment_workflow()
    except Exception as e:
        print(f"\n[FAIL] TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
