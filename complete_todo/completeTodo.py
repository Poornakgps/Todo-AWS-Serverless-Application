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

    client = boto3.resource('dynamodb')
    table = client.Table('Todos')

    try:
        # Update the item to mark it as completed
        table.update_item(
            Key={'item_id': body['item_id']},
            UpdateExpression="SET is_done = :is_done, updated_date = :updated_date",
            ExpressionAttributeValues={
                ":is_done": True,
                ":updated_date": datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            },
            ConditionExpression="attribute_exists(item_id)"  # Ensure item exists
        )
        logger.info(f"Marked todo with id {body['item_id']} as completed")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Todo marked as completed"})
        }
    except Exception as e:
        logger.error(f"Failed to mark item as completed in DynamoDB: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to mark item as completed"})
        }
