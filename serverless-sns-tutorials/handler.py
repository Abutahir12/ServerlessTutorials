import json
import boto3
from botocore.exceptions import ClientError

def send_sms(event, context):
    print(event)
    body = json.loads(event.get("body"))
    message = body.get("message")
    phone_number = body.get("phone_number")
    sns = boto3.client("sns")
    try:
        # sms type can be either "Promotional" or "Transactional"
        # If you don't specify "set_sms_attributes", the type will be "Promotional by default"
        sns.set_sms_attributes(attributes={"DefaultSMSType": "Transactional"})
        response = sns.publish(
            PhoneNumber="+918050797576", Message=message, Subject="This is a test"
        )
        response = {"message": f"Message sent to: {phone_number}"}
        return {"statusCode": 200, "body": json.dumps(response)}
    except ClientError:
        return {"statusCode": 500, "body": json.dumps({"message": "failed"})}
