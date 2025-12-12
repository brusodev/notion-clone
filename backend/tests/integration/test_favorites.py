"""
Test script for Page Favorites functionality
Tests:
1. Add page to favorites
2. Get all favorites
3. Check favorite status
4. Remove page from favorites
5. Prevent duplicate favorites
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def print_step(step_num, description):
    print(f"\n{'='*60}")
    print(f"Step {step_num}: {description}")
    print('='*60)


def test_favorites():
    """Test the favorites system end-to-end"""

    # Step 1: Register a new user
    print_step(1, "Registering new user")
    register_data = {
        "email": f"favoritetest{__import__('time').time()}@test.com",
        "password": "testpass123",
        "name": "Favorite Test User"
    }
    response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
    print(f"Status: {response.status_code}")
    assert response.status_code == 201, f"Failed to register: {response.text}"
    tokens = response.json()
    print(f"Response: {json.dumps(tokens, indent=2, default=str)}")
    print(f"User created: {register_data['email']}")

    access_token = tokens["access_token"]
    print(f"Token: {access_token[:50]}...")

    headers = {"Authorization": f"Bearer {access_token}"}

    # Step 2: Create a workspace
    print_step(2, "Creating workspace")
    workspace_data = {
        "name": "Favorites Test Workspace",
        "description": "Testing favorites"
    }
    response = requests.post(f"{BASE_URL}/workspaces/", json=workspace_data, headers=headers)
    print(f"Status: {response.status_code}")
    assert response.status_code == 201, f"Failed to create workspace: {response.text}"
    workspace = response.json()
    workspace_id = workspace["id"]
    print(f"Workspace created: {workspace['name']} ({workspace_id})")

    # Step 3: Create multiple pages
    print_step(3, "Creating pages")
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

    # Step 5: Add first page to favorites
    print_step(5, "Adding page to favorites")
    page_id = pages[0]["id"]
    response = requests.post(f"{BASE_URL}/pages/{page_id}/favorite", headers=headers)
    print(f"Status: {response.status_code}")
    assert response.status_code == 201, f"Failed to add favorite: {response.text}"
    favorite = response.json()
    print(f"Added to favorites:")
    print(json.dumps(favorite, indent=2))
    assert favorite["page_id"] == page_id

    # Step 6: Try to add same page again (should fail with 409)
    print_step(6, "Trying to add duplicate favorite (should fail)")
    response = requests.post(f"{BASE_URL}/pages/{page_id}/favorite", headers=headers)
    print(f"Status: {response.status_code}")
    assert response.status_code == 409, f"Expected 409, got {response.status_code}"
    print("Correctly rejected duplicate favorite!")

    # Step 7: Check favorite status
    print_step(7, "Checking favorite status")
    response = requests.get(f"{BASE_URL}/pages/{page_id}/favorite", headers=headers)
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, f"Failed to check status: {response.text}"
    status = response.json()
    print(f"Favorite status:")
    print(json.dumps(status, indent=2, default=str))
    assert status["is_favorited"] == True
    assert status["favorited_at"] is not None

    # Step 8: Add more pages to favorites
    print_step(8, "Adding more pages to favorites")
    for i in [1, 2]:
        page_id = pages[i]["id"]
        response = requests.post(f"{BASE_URL}/pages/{page_id}/favorite", headers=headers)
        print(f"Status: {response.status_code}")
        assert response.status_code == 201
        print(f"Added page {i+1} to favorites")

    # Step 9: Get all favorites
    print_step(9, "Getting all favorites")
    response = requests.get(f"{BASE_URL}/pages/favorites", headers=headers)
    print(f"Status: {response.status_code}")
    assert response.status_code == 200, f"Failed to get favorites: {response.text}"
    favorites = response.json()
    print(f"Found {len(favorites)} favorites:")
    for fav in favorites:
        print(f"  - {fav['title']} ({fav['id']})")
    assert len(favorites) == 3

    # Step 10: Remove a page from favorites
    print_step(10, "Removing page from favorites")
    page_id = pages[1]["id"]
    response = requests.delete(f"{BASE_URL}/pages/{page_id}/favorite", headers=headers)
    print(f"Status: {response.status_code}")
    assert response.status_code == 204, f"Failed to remove favorite: {response.text}"
    print("Removed from favorites!")

    # Step 11: Verify it was removed
    print_step(11, "Verifying removal")
    response = requests.get(f"{BASE_URL}/pages/favorites", headers=headers)
    print(f"Status: {response.status_code}")
    favorites = response.json()
    print(f"Now {len(favorites)} favorites remain")
    assert len(favorites) == 2

    # Step 12: Check status of removed page
    print_step(12, "Checking status of removed page")
    response = requests.get(f"{BASE_URL}/pages/{page_id}/favorite", headers=headers)
    print(f"Status: {response.status_code}")
    status = response.json()
    print(f"Favorite status:")
    print(json.dumps(status, indent=2, default=str))
    assert status["is_favorited"] == False
    assert status["favorited_at"] is None

    print("\n" + "="*60)
    print("ALL TESTS PASSED!")
    print("="*60)


if __name__ == "__main__":
    try:
        test_favorites()
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
