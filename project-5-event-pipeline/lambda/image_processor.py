import json
import boto3
import os
import uuid
from datetime import datetime
from urllib.parse import unquote_plus

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')
sns = boto3.client('sns')

OUTPUT_BUCKET = os.environ.get('OUTPUT_BUCKET', 'image-pipeline-output-YOURNAME')
METADATA_TABLE = os.environ.get('METADATA_TABLE', 'ImageMetadata')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', '')


def lambda_handler(event, context):
    """
    Processes images from SQS messages triggered by S3 upload events.
    - Reads the image from the input bucket
    - Creates a thumbnail (resized copy)
    - Uploads the thumbnail to the output bucket
    - Stores metadata in DynamoDB
    - Sends a notification via SNS
    """
    table = dynamodb.Table(METADATA_TABLE)

    for record in event['Records']:
        try:
            # Parse the SQS message body (which contains the S3 event)
            body = json.loads(record['body'])

            # Handle S3 test events
            if 'Event' in body and body['Event'] == 's3:TestEvent':
                print("Received S3 test event, skipping.")
                continue

            s3_event = body.get('Records', [body])[0]
            bucket = s3_event['s3']['bucket']['name']
            key = unquote_plus(s3_event['s3']['object']['key'])
            size = s3_event['s3']['object'].get('size', 0)

            print(f"Processing image: s3://{bucket}/{key} ({size} bytes)")

            # Skip non-image files
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            file_ext = os.path.splitext(key)[1].lower()
            if file_ext not in valid_extensions:
                print(f"Skipping non-image file: {key}")
                continue

            # Download the image
            download_path = f'/tmp/{uuid.uuid4()}{file_ext}'
            s3.download_file(bucket, key, download_path)

            # Create thumbnail using PIL (Pillow)
            from PIL import Image
            img = Image.open(download_path)
            original_width, original_height = img.size
            original_format = img.format or 'JPEG'

            # Resize to thumbnail (max 200x200, maintaining aspect ratio)
            img.thumbnail((200, 200))
            thumbnail_path = f'/tmp/thumb_{uuid.uuid4()}{file_ext}'
            img.save(thumbnail_path, original_format)
            thumb_width, thumb_height = img.size

            # Upload thumbnail to output bucket
            thumbnail_key = f'thumbnails/{os.path.basename(key)}'
            s3.upload_file(
                thumbnail_path,
                OUTPUT_BUCKET,
                thumbnail_key,
                ExtraArgs={'ContentType': f'image/{original_format.lower()}'}
            )

            print(f"Thumbnail uploaded to s3://{OUTPUT_BUCKET}/{thumbnail_key}")

            # Store metadata in DynamoDB
            metadata_item = {
                'image_id': str(uuid.uuid4()),
                'original_bucket': bucket,
                'original_key': key,
                'original_size': size,
                'original_dimensions': f'{original_width}x{original_height}',
                'thumbnail_bucket': OUTPUT_BUCKET,
                'thumbnail_key': thumbnail_key,
                'thumbnail_dimensions': f'{thumb_width}x{thumb_height}',
                'format': original_format,
                'processed_at': datetime.utcnow().isoformat() + 'Z',
                'status': 'completed'
            }

            table.put_item(Item=metadata_item)
            print(f"Metadata stored in DynamoDB: {metadata_item['image_id']}")

            # Send SNS notification
            if SNS_TOPIC_ARN:
                sns.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject='Image Processing Complete',
                    Message=json.dumps({
                        'status': 'success',
                        'original_image': f's3://{bucket}/{key}',
                        'thumbnail': f's3://{OUTPUT_BUCKET}/{thumbnail_key}',
                        'original_size': f'{size} bytes',
                        'dimensions': f'{original_width}x{original_height} → {thumb_width}x{thumb_height}',
                        'processed_at': metadata_item['processed_at']
                    }, indent=2)
                )
                print("SNS notification sent.")

            # Cleanup temp files
            os.remove(download_path)
            os.remove(thumbnail_path)

        except Exception as e:
            print(f"Error processing record: {e}")

            # Send failure notification
            if SNS_TOPIC_ARN:
                sns.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject='Image Processing FAILED',
                    Message=f'Error processing image: {str(e)}\n\nRecord: {json.dumps(record, indent=2)}'
                )

            raise e

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Processing complete'})
    }
