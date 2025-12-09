# Tests Directory

This directory contains all test files for the Notion Clone backend API.

## Structure

```
tests/
├── __init__.py              # Makes tests a Python package
├── integration/             # Integration tests (API endpoints)
│   ├── test_all_apis.py         # Comprehensive API tests
│   ├── test_versions.py         # Version history tests
│   ├── test_duplicate.py        # Page duplication tests
│   ├── test_trash_simple.py     # Trash/restore tests
│   ├── test_comments_workflow.py # Comment system tests
│   ├── test_api.py              # General API tests
│   ├── test_search.py           # Search functionality tests
│   └── test_search_complete.py  # Complete search tests
├── unit/                    # Unit tests (coming soon)
└── fixtures/                # Test data and JSON payloads
    ├── invite.json              # Invitation test data
    ├── newtoken.json            # Token test data
    ├── newuser.json             # User registration data
    ├── reg.json                 # Registration data
    ├── response.json            # API response examples
    ├── test_payload.json        # Generic test payload
    └── test_report.json         # Test report data
```

## Running Tests

### Run all integration tests
```bash
cd backend
python -m pytest tests/integration/
```

### Run specific test file
```bash
cd backend
python tests/integration/test_versions.py
```

### Run with verbose output
```bash
cd backend
python -m pytest tests/integration/ -v
```

## Test Categories

### Integration Tests (`/integration/`)
These tests verify that different parts of the system work together correctly:
- **test_all_apis.py**: Tests all API endpoints (36 tests)
- **test_versions.py**: Tests version history feature (11 steps)
- **test_duplicate.py**: Tests page duplication with blocks
- **test_trash_simple.py**: Tests trash/restore functionality
- **test_comments_workflow.py**: Tests comment system
- **test_search.py**: Tests search functionality

### Unit Tests (`/unit/`)
Coming soon - will contain isolated tests for individual functions and classes.

## Test Fixtures (`/fixtures/`)
JSON files containing sample data used across multiple tests. These files help maintain consistency and reduce code duplication.

## Writing New Tests

When adding new tests:
1. Place integration tests in `/integration/`
2. Place unit tests in `/unit/`
3. Add reusable test data to `/fixtures/`
4. Follow existing naming conventions (`test_*.py`)
5. Include docstrings explaining what each test verifies

## Test Coverage

Current test coverage includes:
- Authentication (login, refresh, logout)
- Workspaces (CRUD + members)
- Pages (CRUD + hierarchy + versions)
- Blocks (CRUD + ordering)
- Comments (CRUD + reactions + mentions)
- Search (full-text across workspaces)
- Invitations (create, accept, decline)
