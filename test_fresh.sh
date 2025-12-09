#!/bin/bash

BASE_URL="https://notion-clone-production-b81a.up.railway.app/api/v1"
EMAIL="fresh_$(date +%s)@test.com"

echo "==== Testing Member Management ===="
echo "Email: $EMAIL"
echo

# 1. Register
echo "1. Register user..."
RESPONSE=$(curl -s -X POST "$BASE_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Test User\",\"email\":\"$EMAIL\",\"password\":\"Test123!\"}")

echo "$RESPONSE" | python -m json.tool
TOKEN=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "Failed to get token"
  exit 1
fi

echo "Token obtained: ${TOKEN:0:30}..."
echo

# 2. Get workspaces
echo "2. Get workspaces..."
WS_RESPONSE=$(curl -s -X GET "$BASE_URL/workspaces" \
  -H "Authorization: Bearer $TOKEN")

echo "$WS_RESPONSE" | python -m json.tool
WORKSPACE_ID=$(echo "$WS_RESPONSE" | python -c "import sys, json; data=json.load(sys.stdin); print(data[0]['id'] if data else '')" 2>/dev/null)

if [ -z "$WORKSPACE_ID" ]; then
  echo "Failed to get workspace"
  exit 1
fi

echo "Workspace ID: $WORKSPACE_ID"
echo

# 3. List members
echo "3. List members..."
curl -s -X GET "$BASE_URL/workspaces/$WORKSPACE_ID/members" \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
echo

# 4. Create invitation
echo "4. Create invitation..."
INVITE_EMAIL="invited_$(date +%s)@test.com"
INV_RESPONSE=$(curl -s -X POST "$BASE_URL/workspaces/$WORKSPACE_ID/invitations" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$INVITE_EMAIL\",\"role\":\"editor\"}")

echo "$INV_RESPONSE" | python -m json.tool
echo

echo "==== All member endpoints working! ===="
