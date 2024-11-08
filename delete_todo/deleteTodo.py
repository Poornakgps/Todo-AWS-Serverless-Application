import json
import boto3
import logging

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
    sqs = boto3.client('sqs')
    table = dynamodb.Table('Todos')
    queue_url = "<DELETE_QUEUE_URL>"  # Replace with the actual SQS queue URL

    try:
        # Update the item in DynamoDB to mark it as deleted
        table.update_item(
            Key={'item_id': body['item_id']},
            UpdateExpression="SET is_deleted = :is_deleted",
            ExpressionAttributeValues={":is_deleted": True},
            ConditionExpression="attribute_exists(item_id)"  # Ensure item exists
        )
        logger.info(f"Marked todo with id {body['item_id']} as deleted in DynamoDB")

        # Send a message to the delete queue
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps({"item_id": body['item_id']})
        )
        logger.info(f"Sent delete message for todo with id {body['item_id']} to SQS")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Todo marked as deleted"})
        }
    except Exception as e:
        logger.error(f"Failed to mark item as deleted or send message to SQS: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to delete item"})
        }
