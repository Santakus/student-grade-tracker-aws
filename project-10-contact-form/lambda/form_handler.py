import json
import boto3
import uuid
import re
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')

TABLE_NAME = 'ContactFormSubmissions'
RECIPIENT_EMAIL = 'YOUR_VERIFIED_EMAIL@example.com'  # Must be verified in SES
SENDER_EMAIL = 'YOUR_VERIFIED_EMAIL@example.com'     # Must be verified in SES


def build_response(status_code, body):
    """Build a standardized API response with CORS headers."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(body)
    }


def validate_email(email):
    """Basic email validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def lambda_handler(event, context):
    """Handle contact form submissions."""
    http_method = event.get('httpMethod', '')

    # Handle CORS preflight
    if http_method == 'OPTIONS':
        return build_response(200, {'message': 'OK'})

    if http_method != 'POST':
        return build_response(405, {'error': 'Method not allowed'})

    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return build_response(400, {'error': 'Invalid JSON'})

    # ==========================================
    # INPUT VALIDATION
    # ==========================================
    name = body.get('name', '').strip()
    email = body.get('email', '').strip()
    subject = body.get('subject', '').strip() or 'No Subject'
    message = body.get('message', '').strip()

    errors = []
    if not name:
        errors.append('Name is required')
    elif len(name) > 100:
        errors.append('Name must be 100 characters or less')

    if not email:
        errors.append('Email is required')
    elif not validate_email(email):
        errors.append('Invalid email address')

    if not message:
        errors.append('Message is required')
    elif len(message) > 5000:
        errors.append('Message must be 5000 characters or less')

    if len(subject) > 200:
        errors.append('Subject must be 200 characters or less')

    if errors:
        return build_response(400, {'error': 'Validation failed', 'details': errors})

    # ==========================================
    # STORE IN DYNAMODB
    # ==========================================
    submission_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + 'Z'

    table = dynamodb.Table(TABLE_NAME)
    item = {
        'submission_id': submission_id,
        'name': name,
        'email': email,
        'subject': subject,
        'message': message,
        'submitted_at': timestamp,
        'source_ip': event.get('requestContext', {}).get('identity', {}).get('sourceIp', 'unknown')
    }

    table.put_item(Item=item)
    print(f"Submission stored: {submission_id}")

    # ==========================================
    # SEND EMAIL VIA SES
    # ==========================================
    try:
        email_body = f"""
New Contact Form Submission
============================

Name: {name}
Email: {email}
Subject: {subject}
Date: {timestamp}

Message:
{message}

---
Submission ID: {submission_id}
"""

        ses.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [RECIPIENT_EMAIL]},
            Message={
                'Subject': {'Data': f'Contact Form: {subject}'},
                'Body': {
                    'Text': {'Data': email_body},
                    'Html': {'Data': f"""
                        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                            <h2 style="color: #6366f1;">New Contact Form Submission</h2>
                            <table style="width: 100%; border-collapse: collapse;">
                                <tr><td style="padding: 8px; color: #666; font-weight: bold;">Name</td><td style="padding: 8px;">{name}</td></tr>
                                <tr style="background: #f9f9f9;"><td style="padding: 8px; color: #666; font-weight: bold;">Email</td><td style="padding: 8px;"><a href="mailto:{email}">{email}</a></td></tr>
                                <tr><td style="padding: 8px; color: #666; font-weight: bold;">Subject</td><td style="padding: 8px;">{subject}</td></tr>
                                <tr style="background: #f9f9f9;"><td style="padding: 8px; color: #666; font-weight: bold;">Date</td><td style="padding: 8px;">{timestamp}</td></tr>
                            </table>
                            <h3 style="margin-top: 20px; color: #333;">Message</h3>
                            <div style="background: #f5f5f5; padding: 16px; border-radius: 8px; white-space: pre-wrap;">{message}</div>
                            <p style="margin-top: 20px; font-size: 12px; color: #999;">Submission ID: {submission_id}</p>
                        </div>
                    """}
                }
            }
        )
        print("Email sent successfully")
    except Exception as email_error:
        print(f"Email send failed: {email_error}")
        # Don't fail the request just because email failed — data is already stored
        return build_response(200, {
            'message': 'Your message has been received! (Email notification may be delayed)',
            'submission_id': submission_id
        })

    return build_response(200, {
        'message': 'Thank you! Your message has been sent successfully.',
        'submission_id': submission_id
    })
