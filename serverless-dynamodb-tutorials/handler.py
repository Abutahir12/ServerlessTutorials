import json
import boto3
dynamodb = boto3.resource("dynamodb").Table("developer_essentials")

def add_data(event, context):
    print(event)
    request = json.loads(event.get("body"))
    try:
        dynamodb.put_item(Item = request)
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
    else:    
        return {"statusCode": 200, "body": json.dumps("Success")}
