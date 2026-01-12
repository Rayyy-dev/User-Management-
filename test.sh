#!/bin/bash

# User Registration System - API Test Script
# This script tests all API endpoints using curl commands
# Usage: ./test.sh or bash test.sh

BASE_URL="http://localhost:5000"

echo "=========================================="
echo "  User Registration System - API Tests"
echo "=========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
    echo ""
    echo -e "${BLUE}------------------------------------------${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}------------------------------------------${NC}"
}

# Test 1: Health Check
print_header "Test 1: Health Check"
echo "GET /health"
curl -s -X GET "$BASE_URL/health" | python -m json.tool 2>/dev/null || curl -s -X GET "$BASE_URL/health"
echo ""

# Test 2: Root Endpoint
print_header "Test 2: Root Endpoint (API Info)"
echo "GET /"
curl -s -X GET "$BASE_URL/" | python -m json.tool 2>/dev/null || curl -s -X GET "$BASE_URL/"
echo ""

# Test 3: Register First User
print_header "Test 3: Register First User"
echo "POST /api/users"
curl -s -X POST "$BASE_URL/api/users" \
    -H "Content-Type: application/json" \
    -d '{"username": "john_doe", "email": "john@example.com", "password": "securepass123"}' \
    | python -m json.tool 2>/dev/null || \
curl -s -X POST "$BASE_URL/api/users" \
    -H "Content-Type: application/json" \
    -d '{"username": "john_doe", "email": "john@example.com", "password": "securepass123"}'
echo ""

# Test 4: Register Second User
print_header "Test 4: Register Second User"
echo "POST /api/users"
curl -s -X POST "$BASE_URL/api/users" \
    -H "Content-Type: application/json" \
    -d '{"username": "jane_smith", "email": "jane@example.com", "password": "mypassword456"}' \
    | python -m json.tool 2>/dev/null || \
curl -s -X POST "$BASE_URL/api/users" \
    -H "Content-Type: application/json" \
    -d '{"username": "jane_smith", "email": "jane@example.com", "password": "mypassword456"}'
echo ""

# Test 5: Register Third User
print_header "Test 5: Register Third User"
echo "POST /api/users"
curl -s -X POST "$BASE_URL/api/users" \
    -H "Content-Type: application/json" \
    -d '{"username": "alice_wonder", "email": "alice@example.com", "password": "alicepass789"}' \
    | python -m json.tool 2>/dev/null || \
curl -s -X POST "$BASE_URL/api/users" \
    -H "Content-Type: application/json" \
    -d '{"username": "alice_wonder", "email": "alice@example.com", "password": "alicepass789"}'
echo ""

# Test 6: List All Users
print_header "Test 6: List All Users"
echo "GET /api/users"
curl -s -X GET "$BASE_URL/api/users" | python -m json.tool 2>/dev/null || curl -s -X GET "$BASE_URL/api/users"
echo ""

# Test 7: Get User by ID (ID=1)
print_header "Test 7: Get User by ID (ID=1)"
echo "GET /api/users/1"
curl -s -X GET "$BASE_URL/api/users/1" | python -m json.tool 2>/dev/null || curl -s -X GET "$BASE_URL/api/users/1"
echo ""

# Test 8: Duplicate Email (should fail)
print_header "Test 8: Duplicate Email (Expected: Error)"
echo "POST /api/users (duplicate email)"
curl -s -X POST "$BASE_URL/api/users" \
    -H "Content-Type: application/json" \
    -d '{"username": "another_user", "email": "john@example.com", "password": "testpass123"}' \
    | python -m json.tool 2>/dev/null || \
curl -s -X POST "$BASE_URL/api/users" \
    -H "Content-Type: application/json" \
    -d '{"username": "another_user", "email": "john@example.com", "password": "testpass123"}'
echo ""

# Test 9: Invalid Email Format (should fail)
print_header "Test 9: Invalid Email (Expected: Error)"
echo "POST /api/users (invalid email)"
curl -s -X POST "$BASE_URL/api/users" \
    -H "Content-Type: application/json" \
    -d '{"username": "test_user", "email": "invalid-email", "password": "testpass123"}' \
    | python -m json.tool 2>/dev/null || \
curl -s -X POST "$BASE_URL/api/users" \
    -H "Content-Type: application/json" \
    -d '{"username": "test_user", "email": "invalid-email", "password": "testpass123"}'
echo ""

# Test 10: Short Password (should fail)
print_header "Test 10: Short Password (Expected: Error)"
echo "POST /api/users (short password)"
curl -s -X POST "$BASE_URL/api/users" \
    -H "Content-Type: application/json" \
    -d '{"username": "test_user2", "email": "test2@example.com", "password": "123"}' \
    | python -m json.tool 2>/dev/null || \
curl -s -X POST "$BASE_URL/api/users" \
    -H "Content-Type: application/json" \
    -d '{"username": "test_user2", "email": "test2@example.com", "password": "123"}'
echo ""

# Test 11: Get Non-Existent User (should fail)
print_header "Test 11: Get Non-Existent User (Expected: 404)"
echo "GET /api/users/999"
curl -s -X GET "$BASE_URL/api/users/999" | python -m json.tool 2>/dev/null || curl -s -X GET "$BASE_URL/api/users/999"
echo ""

# Test 12: Delete User (ID=3)
print_header "Test 12: Delete User (ID=3)"
echo "DELETE /api/users/3"
curl -s -X DELETE "$BASE_URL/api/users/3" | python -m json.tool 2>/dev/null || curl -s -X DELETE "$BASE_URL/api/users/3"
echo ""

# Test 13: Verify Deletion - List All Users
print_header "Test 13: Verify Deletion - List All Users"
echo "GET /api/users"
curl -s -X GET "$BASE_URL/api/users" | python -m json.tool 2>/dev/null || curl -s -X GET "$BASE_URL/api/users"
echo ""

# Test 14: Delete Non-Existent User (should fail)
print_header "Test 14: Delete Non-Existent User (Expected: 404)"
echo "DELETE /api/users/999"
curl -s -X DELETE "$BASE_URL/api/users/999" | python -m json.tool 2>/dev/null || curl -s -X DELETE "$BASE_URL/api/users/999"
echo ""

echo "=========================================="
echo "  All tests completed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  - Visit http://localhost:8080 to access Adminer"
echo "  - Login with: System=PostgreSQL, Server=postgres, Username=admin, Password=secretpassword, Database=userdb"
