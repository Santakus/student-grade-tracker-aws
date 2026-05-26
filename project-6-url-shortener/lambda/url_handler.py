import json
import boto3
import string
import random
import time
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UrlShortener')


def build_response(status_code, body, headers=None):
    """Build a standardized API response."""
    response = {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(body, default=str)
    }
    if headers:
        response['headers'].update(headers)
    return response


def build_redirect(url):
    """Build a 301 redirect response."""
    return {
        'statusCode': 301,
        'headers': {
            'Location': url,
            'Access-Control-Allow-Origin': '*'
        },
        'body': ''
    }


def generate_short_code(length=6):
    """Generate a random alphanumeric short code."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def lambda_handler(event, context):
    """Main handler — routes based on HTTP method and path."""
    http_method = event.get('httpMethod', '')
    path = event.get('path', '')
    path_params = event.get('pathParameters') or {}

    try:
        # POST /shorten — Create a short URL
        if http_method == 'POST' and path == '/shorten':
            return create_short_url(event)

        # GET /stats/{code} — Get click statistics
        elif http_method == 'GET' and path.startswith('/stats/'):
            code = path_params.get('code', path.split('/')[-1])
            return get_stats(code)

        # GET /{code} — Redirect to the original URL
        elif http_method == 'GET' and path_params and 'code' in path_params:
            return redirect_url(path_params['code'])

        # OPTIONS — CORS preflight
        elif http_method == 'OPTIONS':
            return build_response(200, {'message': 'OK'})

        else:
            return build_response(404, {'error': 'Route not found'})

    except Exception as e:
        print(f"Error: {str(e)}")
        return build_response(500, {'error': 'Internal server error'})


def create_short_url(event):
    """Create a new short URL."""
    body = json.loads(event.get('body', '{}'))
    original_url = body.get('url', '').strip()

    if not original_url:
        return build_response(400, {'error': 'URL is required'})

    # Add protocol if missing
    if not original_url.startswith(('http://', 'https://')):
        original_url = 'https://' + original_url

    # Generate unique short code
    short_code = body.get('custom_code', '').strip() or generate_short_code()

    # Check if custom code already exists
    existing = table.get_item(Key={'short_code': short_code})
    if 'Item' in existing:
        if body.get('custom_code'):
            return build_response(409, {'error': f'Code "{short_code}" is already taken'})
        # Regenerate if collision
        short_code = generate_short_code(8)

    # TTL: expire after 30 days if requested
    ttl_days = body.get('expire_days', 0)
    item = {
        'short_code': short_code,
        'original_url': original_url,
        'click_count': 0,
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'created_by': event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'unknown')
    }

    if ttl_days and int(ttl_days) > 0:
        item['ttl'] = int(time.time()) + (int(ttl_days) * 86400)

    table.put_item(Item=item)

    # Build the short URL
    api_url = f"https://{event['requestContext']['domainName']}/{event['requestContext']['stage']}"
    short_url = f"{api_url}/{short_code}"

    return build_response(201, {
        'short_url': short_url,
        'short_code': short_code,
        'original_url': original_url,
        'expires_in_days': ttl_days if ttl_days else 'never'
    })


def redirect_url(short_code):
    """Look up the short code and redirect to the original URL."""
    response = table.get_item(Key={'short_code': short_code})
    item = response.get('Item')

    if not item:
        return build_response(404, {'error': 'Short URL not found'})

    # Increment click count
    table.update_item(
        Key={'short_code': short_code},
        UpdateExpression='SET click_count = click_count + :inc, last_clicked = :now',
        ExpressionAttributeValues={
            ':inc': 1,
            ':now': datetime.utcnow().isoformat() + 'Z'
        }
    )

    return build_redirect(item['original_url'])


def get_stats(short_code):
    """Get statistics for a short URL."""
    response = table.get_item(Key={'short_code': short_code})
    item = response.get('Item')

    if not item:
        return build_response(404, {'error': 'Short URL not found'})

    return build_response(200, {
        'short_code': item['short_code'],
        'original_url': item['original_url'],
        'click_count': int(item.get('click_count', 0)),
        'created_at': item['created_at'],
        'last_clicked': item.get('last_clicked', 'never')
    })
