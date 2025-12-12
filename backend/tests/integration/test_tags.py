"""
Integration tests for Tags system
Tests:
1. Create tags in a workspace
2. List workspace tags
3. Get specific tag
4. Update tag name and color
5. Add tags to pages
6. List page tags
7. Get pages by tag
8. Remove tag from page
9. Delete tag
10. Prevent duplicate tags
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def print_step(step_num, description):
    print(f"\n{'='*60}")
    print(f"Step {step_num}: {description}")
    print('='*60)


def test_tags():
    """Test the tags system end-to-end"""

    # Step 1: Register a new user
    print_step(1, "Registering new user")
    register_data = {
        "email": f"tagstest{__import__('time').time()}@test.com",
        "password": "testpass123",
        "name": "Tags Test User"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"Status: {response.status_code}")
    assert response.status_code == 201, f"Failed to register: {response.text}"
    tokens = response.json()
    print(f"User created: {register_data['email']}")

    access_token = tokens["access_token"]
    print(f"Token: {access_token[:50]}...")

    headers = {"Authorization": f"Bearer {access_token}"}

    # Step 2: Create a workspace
    print_step(2, "Creating workspace")
    workspace_data = {
        "name": "Tags Test Workspace",
        "description": "Testing tags"
    }
    response = requests.post(f"{BASE_URL}/workspaces/", json=workspace_data, headers=headers)
    print(f"Status: {response.status_code}")
    assert response.status_code == 201, f"Failed to create workspace: {response.text}"
    workspace = response.json()
    workspace_id = workspace["id"]
    print(f"Workspace created: {workspace['name']} ({workspace_id})")

    # Step 3: Create multiple tags
    print_step(3, "Creating tags")
    tags = []
    tag_names = ["Feature", "Bug", "Enhancement"]
    tag_colors = ["#FF5733", "#33FF57", "#3357FF"]
    for i, (name, color) in enumerate(zip(tag_names, tag_colors)):
        tag_data = {
            "name": name,
            "color": color
        }
        response = requests.post(
            f"{BASE_URL}/workspaces/{workspace_id}/tags",
            json=tag_data,
            headers=headers
        )
        print(f"Status: {response.status_code}")
        assert response.status_code == 201, f"Failed to create tag: {response.text}"
        tag = response.json()
        tags.append(tag)
        print(f"Tag {i+1} created: {tag['name']} ({tag['color']})")

    # Step 4: Try to create duplicate tag (should fail with 409)
    print_step(4, "Trying to create duplicate tag (should fail)")
    duplicate_tag = {
        "name": "Feature",
        "color": "#FFFFFF"
    }
    response = requests.post(
        f"{BASE_URL}/workspaces/{workspace_id}/tags",
        json=duplicate_tag,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    assert response.status_code == 409, f"Expected 409, got {response.status_code}"
    print("Correctly rejected duplicate tag!")

    # Step 5: List all workspace tags
    print_step(5, "Listing all workspace tags")
    response = requests.get(
        f"{BASE_URL}/workspaces/{workspace_id}/tags",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, f"Failed to list tags: {response.text}"
    all_tags = response.json()
    print(f"Found {len(all_tags)} tags:")
    for tag in all_tags:
        print(f"  - {tag['name']} ({tag['color']}) - {tag['page_count']} pages")
    assert len(all_tags) == 3

    # Step 6: Get a specific tag
    print_step(6, "Getting specific tag")
    tag_id = tags[0]["id"]
    response = requests.get(
        f"{BASE_URL}/workspaces/{workspace_id}/tags/{tag_id}",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, f"Failed to get tag: {response.text}"
    tag = response.json()
    print(f"Tag: {tag['name']} ({tag['color']})")
    assert tag["name"] == "Feature"

    # Step 7: Update a tag
    print_step(7, "Updating tag")
    update_data = {
        "name": "Feature Request",
        "color": "#FF0000"
    }
    response = requests.put(
        f"{BASE_URL}/workspaces/{workspace_id}/tags/{tag_id}",
        json=update_data,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, f"Failed to update tag: {response.text}"
    updated_tag = response.json()
    print(f"Updated tag: {updated_tag['name']} ({updated_tag['color']})")
    assert updated_tag["name"] == "Feature Request"
    assert updated_tag["color"] == "#FF0000"

    # Step 8: Create pages
    print_step(8, "Creating pages")
    pages = []
    for i in range(3):
        page_data = {
            "title": f"Test Page {i+1}",
            "workspace_id": workspace_id
        }
        response = requests.post(f"{BASE_URL}/pages/", json=page_data, headers=headers)
        print(f"Status: {response.status_code}")
        assert response.status_code == 201, f"Failed to create page: {response.text}"
        page = response.json()
        pages.append(page)
        print(f"Page {i+1} created: {page['title']} ({page['id']})")

    # Step 9: Add tags to pages
    print_step(9, "Adding tags to pages")
    # Add first two tags to page 1
    for i in [0, 1]:
        response = requests.post(
            f"{BASE_URL}/pages/{pages[0]['id']}/tags/{tags[i]['id']}",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        assert response.status_code == 201, f"Failed to add tag to page: {response.text}"
        print(f"Added '{tags[i]['name']}' to '{pages[0]['title']}'")

    # Add first tag to page 2
    response = requests.post(
        f"{BASE_URL}/pages/{pages[1]['id']}/tags/{tags[0]['id']}",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    assert response.status_code == 201
    print(f"Added '{tags[0]['name']}' to '{pages[1]['title']}'")

    # Step 10: Try to add same tag again (should fail with 409)
    print_step(10, "Trying to add duplicate tag to page (should fail)")
    response = requests.post(
        f"{BASE_URL}/pages/{pages[0]['id']}/tags/{tags[0]['id']}",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    assert response.status_code == 409, f"Expected 409, got {response.status_code}"
    print("Correctly rejected duplicate page-tag!")

    # Step 11: List tags for a page
    print_step(11, "Listing tags for page 1")
    response = requests.get(
        f"{BASE_URL}/pages/{pages[0]['id']}/tags",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, f"Failed to list page tags: {response.text}"
    page_tags = response.json()
    print(f"Page 1 has {len(page_tags)} tags:")
    for tag in page_tags:
        print(f"  - {tag['name']} ({tag['color']})")
    assert len(page_tags) == 2

    # Step 12: List pages by tag
    print_step(12, "Listing pages with 'Feature Request' tag")
    response = requests.get(
        f"{BASE_URL}/workspaces/{workspace_id}/tags/{tags[0]['id']}/pages",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, f"Failed to list pages by tag: {response.text}"
    tagged_pages = response.json()
    print(f"Found {len(tagged_pages)} pages with this tag:")
    for page in tagged_pages:
        print(f"  - {page['title']}")
    assert len(tagged_pages) == 2

    # Step 13: Remove tag from page
    print_step(13, "Removing tag from page")
    response = requests.delete(
        f"{BASE_URL}/pages/{pages[0]['id']}/tags/{tags[0]['id']}",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    assert response.status_code == 204, f"Failed to remove tag: {response.text}"
    print("Tag removed from page!")

    # Step 14: Verify removal
    print_step(14, "Verifying tag removal")
    response = requests.get(
        f"{BASE_URL}/pages/{pages[0]['id']}/tags",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    page_tags = response.json()
    print(f"Page 1 now has {len(page_tags)} tags")
    assert len(page_tags) == 1

    # Step 15: Delete a tag
    print_step(15, "Deleting tag")
    response = requests.delete(
        f"{BASE_URL}/workspaces/{workspace_id}/tags/{tags[2]['id']}",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    assert response.status_code == 204, f"Failed to delete tag: {response.text}"
    print("Tag deleted!")

    # Step 16: Verify tag deletion
    print_step(16, "Verifying tag deletion")
    response = requests.get(
        f"{BASE_URL}/workspaces/{workspace_id}/tags",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    all_tags = response.json()
    print(f"Workspace now has {len(all_tags)} tags")
    assert len(all_tags) == 2

    # Step 17: Verify tag was removed from pages on deletion
    print_step(17, "Verifying CASCADE delete worked")
    response = requests.get(
        f"{BASE_URL}/workspaces/{workspace_id}/tags/{tags[0]['id']}/pages",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    tagged_pages = response.json()
    print(f"'Feature Request' tag is on {len(tagged_pages)} page(s)")
    assert len(tagged_pages) == 1  # Should only be on page 2 now

    print("\n" + "="*60)
    print("ALL TESTS PASSED!")
    print("="*60)


if __name__ == "__main__":
    try:
        test_tags()
    except AssertionError as e:
        print(f"\nTest failed: {e}")
        exit(1)
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to API. Make sure the server is running on http://localhost:8000")
        exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
