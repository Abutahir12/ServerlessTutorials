import json
import boto3
from botocore.exceptions import ClientError
import os
from html_input import html_content
from constants import SUBSCRIBERS_DDB_GSI

sns = boto3.client("sns")
DDB_Table = os.environ["DDB_TABLE_NAME"]


def send_sms(event, context):
    print(event)
    body = json.loads(event.get("body"))
    message = body.get("message")
    phone_number = body.get("phone_number")

    try:
        # sms type can be either "Promotional" or "Transactional"
        # If you don't specify "set_sms_attributes", the type will be "Promotional by default"
        sns.set_sms_attributes(attributes={"DefaultSMSType": "Transactional"})
        response = sns.publish(
            PhoneNumber=phone_number, Message=message, Subject="This is a test"
        )
        response = {"message": f"Message sent to: {phone_number}"}
        return {"statusCode": 200, "body": json.dumps(response)}
    except ClientError:
        return {"statusCode": 500, "body": json.dumps({"message": "failed"})}


def create_topic(event, context):
    print(event)
    body = json.loads(event.get("body"))
    name = body.get("name")
    try:
        topic = sns.create_topic(Name=name)
        print("Created topic %s with ARN %s.", name, topic.get("arn"))
    except ClientError:
        print("Couldn't create topic %s.", name)
        return {"statusCode": 500, "body": json.dumps({"message": "failed"})}
    else:
        return {"statusCode": 200, "body": json.dumps(topic)}


def subscribe_to_newsletter(event, context):
    print(event)
    body = json.loads(event.get("body"))
    email = body.get("email")
    newsletter_name = body.get("newsletter_name")
    # TODO: if we have an email in the request we can subscribe through email,
    # if phone number is provided, we can use the phone number

    try:
        arns = sns.list_topics()["Topics"]
        newsletter_arn = ""
        for arn in arns:
            topic_arn = arn.get("TopicArn")
            if newsletter_name in topic_arn:
                newsletter_arn += topic_arn
        response = sns.subscribe(
            TopicArn=newsletter_arn, Protocol="email", Endpoint=email
        )
        # TODO: The admin email should also come in api request to add it in db
        data = {
            "admin_email": "abutahirism@gmail.com",
            "news_letter": newsletter_name,
            "user_email": email
        }
        res=DDB_Table.putItem(data)
        # Record logger info indicating the success of putItem
        print(res)
    except ClientError:
        print("Couldn't subscribe from email %s.", email)
        return {"statusCode": 500, "body": json.dumps({"message": "failed"})}
    else:
        return {"statusCode": 200, "body": json.dumps(response)}

def publish_to_newsletter(event, context):
    print(event)
    body = json.loads(event.get("body"))
    message = body.get("message")
    # message = html_content.get("NEWSLETTER")
    newsletter_name = body.get("newsletter_name")
    try:
        # sms type can be either "Promotional" or "Transactional"
        # If you don't specify "set_sms_attributes", the type will be "Promotional by default"
        arns = sns.list_topics()["Topics"]
        newsletter_arn = ""
        for arn in arns:
            topic_arn = arn.get("TopicArn")
            if newsletter_name in topic_arn:
                newsletter_arn += topic_arn

        resp = sns.publish(
            TopicArn=newsletter_arn, Message=message, Subject="This is a test"
        )
        response = {"message": f"Message sent to: {newsletter_name}"}
    except ClientError:
        # print("Couldn't subscribe from email %s.", email)
        return {"statusCode": 500, "body": json.dumps({"message": "failed"})}
    else:
        return {"statusCode": 200, "body": json.dumps(newsletter_arn)}


def send_email(event, context):
    dynamodb = boto3.client("dynamodb")
    body = json.loads(event.get("body"))
    newsletter_name = body["newsletter_name"]
    # TODO: Filter the results by admin email and then use key condition expressions to filter by newsletter, also add pagination
    results = dynamodb.query(
        TableName=DDB_Table,
        IndexName=SUBSCRIBERS_DDB_GSI.get("NEWSLETTER"),
        KeyConditionExpression="news_letter = :newsletter",
        ExpressionAttributeValues={":newsletter": newsletter_name},
    )
    # TODO: Send Email to all subscribers
    print("///////", results)
