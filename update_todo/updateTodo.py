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

    # Prepare update expression based on available fields
    update_expression = []
    expression_values = {}

    if 'title' in body:
        update_expression.append("title = :title")
        expression_values[":title"] = body['title']
    if 'content' in body:
        update_expression.append("content = :content")
        expression_values[":content"] = body['content']
    
    # Ensure there's something to update
    if not update_expression:
        return {"statusCode": 400, "body": json.dumps({"error": "No fields to update"})}

    # Add updated date
    update_expression.append("updated_date = :updated_date")
    expression_values[":updated_date"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # Build the full update expression
    update_expression = "SET " + ", ".join(update_expression)

    try:
        # Update the item
        table.update_item(
            Key={'item_id': body['item_id']},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ConditionExpression="attribute_exists(item_id)"  # Ensure item exists
        )
        logger.info(f"Updated todo with id {body['item_id']}")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Todo updated successfully"})
        }
    except Exception as e:
        logger.error(f"Failed to update item in DynamoDB: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to update item"})
        }
