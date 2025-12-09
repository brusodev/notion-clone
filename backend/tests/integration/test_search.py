import requests
import json
from uuid import UUID

# Configuration
BASE_URL = "http://localhost:8001/api/v1"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiZDY2ZDMyMi1hNmRhLTQ3OWItYWI4NC1hYjQ1M2Q4MGJhMTEiLCJlbWFpbCI6ImZyZXNodGVzdDE3MzMzMTcxMDBAdGVzdC5jb20iLCJleHAiOjE3NjQ4NTYzOTEsInR5cGUiOiJhY2Nlc3MifQ.aU9HconXoeSXdYiV0BajrwvIpU3pdUB-mYW2X5n0EEE"
WORKSPACE_ID = "a6b5abd3-0d78-4ee6-a61b-aa778a1c0582"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_search():
    """Test the search endpoint"""
    print("=" * 60)
    print("Testing Full-Text Search Endpoint")
    print("=" * 60)

    # Test 1: Basic search
    print("\n1. Testing basic search for 'test'...")
    search_data = {
        "query": "test",
        "workspace_id": WORKSPACE_ID,
        "limit": 10,
        "offset": 0
    }

    response = requests.post(
        f"{BASE_URL}/search/",
        headers=headers,
        json=search_data
    )

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Total Results: {result['total']}")
        print(f"Query: {result['query']}")
        print(f"Execution Time: {result['execution_time_ms']:.2f}ms")
        print(f"Results Returned: {len(result['results'])}")

        if result['results']:
            print("\nFirst Result:")
            first = result['results'][0]
            print(f"  Page Title: {first['page_title']}")
            print(f"  Rank: {first['rank']:.4f}")
            print(f"  Matched In: {first['matched_in']}")
            print(f"  Highlight: {first['highlight'][:100]}...")
            if first['matched_blocks']:
                print(f"  Matched Blocks: {len(first['matched_blocks'])}")
        else:
            print("\nNo results found. This is expected if no pages exist yet.")
    else:
        print(f"Error: {response.text}")

    # Test 2: Search with type filter
    print("\n2. Testing search with type_filter='pages_only'...")
    search_data['type_filter'] = 'pages_only'

    response = requests.post(
        f"{BASE_URL}/search/",
        headers=headers,
        json=search_data
    )

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Total Results: {result['total']}")
        print(f"Execution Time: {result['execution_time_ms']:.2f}ms")
    else:
        print(f"Error: {response.text}")

    # Test 3: Portuguese stemming test (if data exists)
    print("\n3. Testing Portuguese stemming (search for 'programar')...")
    search_data = {
        "query": "programar",
        "workspace_id": WORKSPACE_ID,
        "limit": 5
    }

    response = requests.post(
        f"{BASE_URL}/search/",
        headers=headers,
        json=search_data
    )

    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Total Results: {result['total']}")
        print(f"Execution Time: {result['execution_time_ms']:.2f}ms")
        print("Note: Should match 'programação', 'programado', etc. if such pages exist")

    print("\n" + "=" * 60)
    print("Testing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_search()
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to the API. Is the server running?")
        print("Start the server with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"Error: {e}")
