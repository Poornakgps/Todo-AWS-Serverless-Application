import json
import boto3
import logging
from boto3.dynamodb.conditions import Attr

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))

    client = boto3.resource('dynamodb')
    table = client.Table('Todos')

    try:
        # Fetch items that are not deleted
        response = table.scan(
            FilterExpression=Attr('is_deleted').eq(False)
        )
        items = response.get('Items', [])
        logger.info(f"Retrieved {len(items)} todo items")

        return {
            "statusCode": 200,
            "body": json.dumps(items)
        }
    except Exception as e:
        logger.error(f"Failed to retrieve items from DynamoDB: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to retrieve items"})
        }
