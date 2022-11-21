import json
import boto3
from html_input import html_content
SES = boto3.client("ses")
def send_email(event, context):

    SES.send_email(
        Source = "abutahirism@gmail.com",
        Destination = {
            "ToAddresses": ["abutahirism@gmail.com"]
        },
        Message = {
            "Subject": {
                "Data": "This is an SES test email"
            },
            "Body": {
                "Html": {
                    "Data": html_content["NEWSLETTER"]
                }
            }
        }
    )
    body = {
        "message": "Go Serverless v3.0! Your function executed successfully!",
        "input": event,
    }

    return {"statusCode": 200, "body": json.dumps(body)}
