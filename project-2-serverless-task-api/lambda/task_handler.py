import json
import boto3
import uuid
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TaskManager')


def decimal_default(obj):
    """Handle Decimal serialization for JSON responses."""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def build_response(status_code, body):
    """Build a standardized API response with CORS headers."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(body, default=decimal_default)
    }


def lambda_handler(event, context):
    """Main Lambda handler — routes requests based on HTTP method and path."""
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')
    path_params = event.get('pathParameters') or {}

    try:
        # Route: GET /tasks — List all tasks
        if http_method == 'GET' and path == '/tasks':
            return get_all_tasks(event)

        # Route: GET /tasks/{id} — Get a single task
        elif http_method == 'GET' and 'id' in path_params:
            return get_task(path_params['id'])

        # Route: POST /tasks — Create a new task
        elif http_method == 'POST' and path == '/tasks':
            return create_task(event)

        # Route: PUT /tasks/{id} — Update a task
        elif http_method == 'PUT' and 'id' in path_params:
            return update_task(path_params['id'], event)

        # Route: DELETE /tasks/{id} — Delete a task
        elif http_method == 'DELETE' and 'id' in path_params:
            return delete_task(path_params['id'])

        # Route: OPTIONS (CORS preflight)
        elif http_method == 'OPTIONS':
            return build_response(200, {'message': 'CORS preflight OK'})

        else:
            return build_response(404, {'error': f'Route not found: {http_method} {path}'})

    except Exception as e:
        print(f"Error: {str(e)}")
        return build_response(500, {'error': 'Internal server error', 'details': str(e)})


# ==========================================
# CRUD OPERATIONS
# ==========================================

def get_all_tasks(event):
    """Retrieve all tasks, with optional filtering by status."""
    query_params = event.get('queryStringParameters') or {}
    status_filter = query_params.get('status')

    if status_filter:
        # Use a scan with a filter expression
        response = table.scan(
            FilterExpression='#s = :status',
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={':status': status_filter}
        )
    else:
        response = table.scan()

    tasks = response.get('Items', [])

    # Sort by created_at (newest first)
    tasks.sort(key=lambda x: x.get('created_at', ''), reverse=True)

    return build_response(200, {
        'count': len(tasks),
        'tasks': tasks
    })


def get_task(task_id):
    """Retrieve a single task by ID."""
    response = table.get_item(Key={'task_id': task_id})
    item = response.get('Item')

    if not item:
        return build_response(404, {'error': f'Task not found: {task_id}'})

    return build_response(200, item)


def create_task(event):
    """Create a new task."""
    body = json.loads(event.get('body', '{}'))

    # Validate required fields
    title = body.get('title', '').strip()
    if not title:
        return build_response(400, {'error': 'Title is required'})

    task_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + 'Z'

    item = {
        'task_id': task_id,
        'title': title,
        'description': body.get('description', ''),
        'status': body.get('status', 'pending'),
        'priority': body.get('priority', 'medium'),
        'due_date': body.get('due_date', ''),
        'created_at': now,
        'updated_at': now
    }

    table.put_item(Item=item)

    return build_response(201, {
        'message': 'Task created successfully',
        'task': item
    })


def update_task(task_id, event):
    """Update an existing task."""
    # Check if task exists
    response = table.get_item(Key={'task_id': task_id})
    if 'Item' not in response:
        return build_response(404, {'error': f'Task not found: {task_id}'})

    body = json.loads(event.get('body', '{}'))
    now = datetime.utcnow().isoformat() + 'Z'

    # Build update expression dynamically
    update_parts = []
    expression_values = {':updated_at': now}
    expression_names = {}

    allowed_fields = ['title', 'description', 'status', 'priority', 'due_date']

    for field in allowed_fields:
        if field in body:
            placeholder = f':{field}'
            name_placeholder = f'#{field}'
            update_parts.append(f'{name_placeholder} = {placeholder}')
            expression_values[placeholder] = body[field]
            expression_names[name_placeholder] = field

    if not update_parts:
        return build_response(400, {'error': 'No fields to update'})

    update_parts.append('#updated_at = :updated_at')
    expression_names['#updated_at'] = 'updated_at'

    update_expression = 'SET ' + ', '.join(update_parts)

    result = table.update_item(
        Key={'task_id': task_id},
        UpdateExpression=update_expression,
        ExpressionAttributeNames=expression_names,
        ExpressionAttributeValues=expression_values,
        ReturnValues='ALL_NEW'
    )

    return build_response(200, {
        'message': 'Task updated successfully',
        'task': result['Attributes']
    })


def delete_task(task_id):
    """Delete a task by ID."""
    # Check if task exists
    response = table.get_item(Key={'task_id': task_id})
    if 'Item' not in response:
        return build_response(404, {'error': f'Task not found: {task_id}'})

    table.delete_item(Key={'task_id': task_id})

    return build_response(200, {
        'message': f'Task {task_id} deleted successfully'
    })
