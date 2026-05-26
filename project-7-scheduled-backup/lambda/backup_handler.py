import json
import boto3
import os
from datetime import datetime

s3 = boto3.client('s3')
sns = boto3.client('sns')

SOURCE_BUCKET = os.environ.get('SOURCE_BUCKET', 'backup-source-YOURNAME')
BACKUP_BUCKET = os.environ.get('BACKUP_BUCKET', 'backup-destination-YOURNAME')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')


def lambda_handler(event, context):
    """
    Automated backup Lambda function.
    Triggered by EventBridge on a schedule.
    Copies all objects from source bucket to backup bucket with timestamped prefix.
    Sends a summary email via SNS.
    """
    timestamp = datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
    backup_prefix = f'backup-{timestamp}/'

    print(f"Starting backup: {SOURCE_BUCKET} → {BACKUP_BUCKET}/{backup_prefix}")

    files_backed_up = 0
    total_size = 0
    errors = []

    try:
        # List all objects in the source bucket
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=SOURCE_BUCKET)

        for page in pages:
            contents = page.get('Contents', [])
            if not contents:
                print("Source bucket is empty.")
                break

            for obj in contents:
                source_key = obj['Key']
                dest_key = f'{backup_prefix}{source_key}'
                file_size = obj['Size']

                try:
                    # Copy the object
                    s3.copy_object(
                        Bucket=BACKUP_BUCKET,
                        Key=dest_key,
                        CopySource={'Bucket': SOURCE_BUCKET, 'Key': source_key}
                    )
                    files_backed_up += 1
                    total_size += file_size
                    print(f"  ✓ Copied: {source_key} ({file_size} bytes)")

                except Exception as copy_error:
                    error_msg = f"Failed to copy {source_key}: {str(copy_error)}"
                    errors.append(error_msg)
                    print(f"  ✗ {error_msg}")

    except Exception as e:
        errors.append(f"Failed to list source bucket: {str(e)}")
        print(f"Error listing source bucket: {e}")

    # Build summary
    summary = {
        'backup_timestamp': timestamp,
        'source_bucket': SOURCE_BUCKET,
        'backup_bucket': BACKUP_BUCKET,
        'backup_folder': backup_prefix,
        'files_backed_up': files_backed_up,
        'total_size_bytes': total_size,
        'total_size_readable': format_size(total_size),
        'errors': errors,
        'status': 'SUCCESS' if not errors else 'COMPLETED WITH ERRORS'
    }

    print(f"\nBackup Summary: {json.dumps(summary, indent=2)}")

    # Send SNS notification
    if SNS_TOPIC_ARN:
        subject = f"Backup {'✅ Complete' if not errors else '⚠️ Completed with Errors'} — {timestamp}"

        message = f"""
=== S3 Backup Report ===

Timestamp: {timestamp}
Source: s3://{SOURCE_BUCKET}
Destination: s3://{BACKUP_BUCKET}/{backup_prefix}

Files Backed Up: {files_backed_up}
Total Size: {format_size(total_size)}
Status: {summary['status']}
"""
        if errors:
            message += f"\nErrors ({len(errors)}):\n"
            for err in errors:
                message += f"  - {err}\n"

        message += f"\n--- End of Report ---"

        try:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=subject,
                Message=message
            )
            print("SNS notification sent.")
        except Exception as sns_error:
            print(f"Failed to send SNS notification: {sns_error}")

    return summary


def format_size(size_bytes):
    """Convert bytes to a human-readable format."""
    if size_bytes == 0:
        return '0 B'
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    i = 0
    size = float(size_bytes)
    while size >= 1024 and i < len(units) - 1:
        size /= 1024
        i += 1
    return f'{size:.1f} {units[i]}'
