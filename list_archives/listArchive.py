import json
import boto3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Todos')

    try:
        # Scan the table for todos that are archived
        response = table.scan(
            FilterExpression="is_archived = :is_archived",
            ExpressionAttributeValues={
                ":is_archived": True
            }
        )

        items = response.get('Items', [])
        logger.info(f"Retrieved {len(items)} archived todos")

        return {
            "statusCode": 200,
            "body": json.dumps(items)
        }
    except Exception as e:
        logger.error(f"Failed to retrieve archived todos: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to retrieve archived todos"})
        }
