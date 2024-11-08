import json
import boto3
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))

    try:
        body = json.loads(event.get('body', '{}'))
        logger.info("Parsed body: %s", json.dumps(body))
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {e}")
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid JSON"})}

    # Validate input
    if not body.get('item_id'):
        logger.error("Missing item_id in request body")
        return {"statusCode": 400, "body": json.dumps({"error": "Missing item_id"})}

    dynamodb = boto3.resource('dynamodb')
    s3 = boto3.client('s3')
    table = dynamodb.Table('Todos')
    bucket_name = 'serverless-todo-v1'

    try:
        # Retrieve the todo item from DynamoDB
        response = table.get_item(Key={'item_id': body['item_id']})
        item = response.get('Item')
        
        if not item:
            logger.error("Todo item not found")
            return {"statusCode": 404, "body": json.dumps({"error": "Todo item not found"})}

        # Archive the item to S3
        archive_key = f"archive/{item['item_id']}.json"
        s3.put_object(
            Bucket=bucket_name,
            Key=archive_key,
            Body=json.dumps(item),
            ContentType="application/json"
        )
        logger.info(f"Archived todo with id {item['item_id']} to S3")

        # Update the item in DynamoDB to mark it as archived
        table.update_item(
            Key={'item_id': body['item_id']},
            UpdateExpression="SET is_archived = :is_archived, updated_date = :updated_date",
            ExpressionAttributeValues={
                ":is_archived": True,
                ":updated_date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Todo archived successfully"})
        }
    except Exception as e:
        logger.error(f"Failed to archive item: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to archive item"})
        }
