import json
import boto3
import uuid
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))

    try:
        body = json.loads(event.get('body', '{}'))
        logger.info("Parsed body: %s", json.dumps(body))  # Log the parsed body
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON: {e}")
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid JSON"})}

    # Check if 'title' and 'content' are in the body
    if not body.get('title') or not body.get('content'):
        logger.error("Missing title or content in request body")
        return {"statusCode": 400, "body": json.dumps({"error": "Missing title or content"})}

    client = boto3.resource('dynamodb')
    table = client.Table('Todos')
    item_id = str(uuid.uuid1())
    try:
        table.put_item(
            Item={
                'item_id': item_id,
                'title': body.get('title'),
                'content': body.get('content'),
                'created_date': datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                'updated_date': None,
                'is_archived': False,
                'is_deleted': False,
                'is_done': False
            }
        )
    except Exception as e:
        logger.error(f"Failed to insert item into DynamoDB: {e}")
        return {"statusCode": 500, "body": json.dumps({"error": "Failed to insert item into database"})}

    logger.info(f"Inserted todo with id {item_id} into database")

    response = {
        "statusCode": 201,
        "body": json.dumps({
            "item_id": item_id,
            "title": body.get('title'),
            "content": body.get('content'),
            "created_date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        })
    }

    return response
