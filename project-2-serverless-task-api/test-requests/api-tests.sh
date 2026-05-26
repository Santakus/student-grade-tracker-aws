#!/bin/bash
# ==========================================
# Task Manager API — Test Script
# Replace YOUR_API_URL with your actual API Gateway Invoke URL
# Example: https://abc123.execute-api.us-east-1.amazonaws.com/prod
# ==========================================

API_URL="YOUR_API_URL"

echo "============================================"
echo "  Task Manager API — Integration Tests"
echo "============================================"
echo ""

# ----------------------------------------
# TEST 1: Create a Task
# ----------------------------------------
echo ">> TEST 1: Creating a task..."
CREATE_RESPONSE=$(curl -s -X POST "$API_URL/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete AWS Lambda lab",
    "description": "Build and deploy a serverless task manager API",
    "priority": "high",
    "due_date": "2026-06-01"
  }')

echo "$CREATE_RESPONSE" | python3 -m json.tool
TASK_ID=$(echo "$CREATE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['task']['task_id'])")
echo "Created Task ID: $TASK_ID"
echo ""

# ----------------------------------------
# TEST 2: Get All Tasks
# ----------------------------------------
echo ">> TEST 2: Getting all tasks..."
curl -s -X GET "$API_URL/tasks" | python3 -m json.tool
echo ""

# ----------------------------------------
# TEST 3: Get Single Task
# ----------------------------------------
echo ">> TEST 3: Getting task by ID..."
curl -s -X GET "$API_URL/tasks/$TASK_ID" | python3 -m json.tool
echo ""

# ----------------------------------------
# TEST 4: Update a Task
# ----------------------------------------
echo ">> TEST 4: Updating task status to 'in_progress'..."
curl -s -X PUT "$API_URL/tasks/$TASK_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "description": "Currently working on this lab"
  }' | python3 -m json.tool
echo ""

# ----------------------------------------
# TEST 5: Filter Tasks by Status
# ----------------------------------------
echo ">> TEST 5: Filtering tasks by status=in_progress..."
curl -s -X GET "$API_URL/tasks?status=in_progress" | python3 -m json.tool
echo ""

# ----------------------------------------
# TEST 6: Create Another Task
# ----------------------------------------
echo ">> TEST 6: Creating a second task..."
curl -s -X POST "$API_URL/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Study for AWS certification",
    "description": "Review Solutions Architect Associate material",
    "priority": "medium",
    "due_date": "2026-07-15"
  }' | python3 -m json.tool
echo ""

# ----------------------------------------
# TEST 7: Delete a Task
# ----------------------------------------
echo ">> TEST 7: Deleting the first task..."
curl -s -X DELETE "$API_URL/tasks/$TASK_ID" | python3 -m json.tool
echo ""

# ----------------------------------------
# TEST 8: Verify Deletion
# ----------------------------------------
echo ">> TEST 8: Verifying task was deleted (should return 404)..."
curl -s -X GET "$API_URL/tasks/$TASK_ID" | python3 -m json.tool
echo ""

echo "============================================"
echo "  All tests completed!"
echo "============================================"
