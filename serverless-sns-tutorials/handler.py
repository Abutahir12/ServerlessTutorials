import json
import boto3
from botocore.exceptions import ClientError
import os
from constants import SUBSCRIBERS_DDB_GSI
from dotenv import load_dotenv
from html_input import html_content

load_dotenv()
sns = boto3.client("sns")

# DDB_Table = os.getenv("DDB_TABLE_NAME")
DDB_Table = "SubscribersDDBTable-dev"
DynamoDb_Table = boto3.resource("dynamodb").Table(DDB_Table)


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
        # TODO: Add validations for topic name, also add full string match, for example:
        # there can be a topic with the name Developer-Essentials, and one topic can be created called Essentials
        arns = sns.list_topics()["Topics"]

        if arn := [
            arn_dict.get("TopicArn")
            for arn_dict in arns
            if name in arn_dict.get("TopicArn")
        ][0]:
            print(arn)
            return {"statusCode": 200, "body": json.dumps("Topic Already exists")}
        topic = sns.create_topic(Name=name)
        response = f"Created topic {name} with ARN {topic.get('arn')}."
    except ClientError:
        print("Couldn't create topic %s.", name)
        return {"statusCode": 500, "body": json.dumps({"message": "failed"})}
    else:
        return {"statusCode": 201, "body": json.dumps(response)}


def subscribe_to_newsletter(event, context):
    print(event)
    body = json.loads(event.get("body"))
    email = body.get("email")
    newsletter_name = body.get("newsletter_name")
    # TODO: if we have an email in the request we can subscribe through email,
    # if phone number is provided, we can use the phone number

    try:
        arns = sns.list_topics()["Topics"]
        print(arns)
        newsletter_arn = [
            arn_dict.get("TopicArn")
            for arn_dict in arns
            if newsletter_name in arn_dict.get("TopicArn")
        ]
        if not len(newsletter_arn):
            return {"statusCode": 200, "body": json.dumps("Newsletter does not exists")}
        print(newsletter_arn)
        response = sns.subscribe(
            TopicArn=newsletter_arn[0], Protocol="email", Endpoint=email
        )

        # TODO: The admin email should also come in api request to add it in db
        data = {
            "admin_email": "abutahirism@gmail.com",
            "news_letter": newsletter_name,
            "user_email": email,
        }
        # res = dynamodb.put_item(TableName = DDB_Table, Item = data, ReturnValues = "ALL_NEW")
        DynamoDb_Table.put_item(Item=data)
        # Record logger info indicating the success of putItem

    except ClientError:
        print("Couldn't subscribe from email %s.", email)
        return {"statusCode": 500, "body": json.dumps({"message": "failed"})}
    else:
        return {"statusCode": 200, "body": json.dumps(response)}


def publish_to_newsletter(event, context):
    # print(event)
    body = json.loads(event.get("body"))
    # message = body.get("message")
    # TODO: Get email content from body
    # message = html_content.get("NEWSLETTER")
    newsletter_name = body.get("newsletter_name")
    message = {
        "newsletter_name": newsletter_name,
        "email_content": "This is a sample test for publishing emails to subscribers",
    }
    try:
        # sms type can be either "Promotional" or "Transactional"
        # If you don't specify "set_sms_attributes", the type will be "Promotional by default"
        arns = sns.list_topics()["Topics"]
        newsletter_arn = [
            arn_dict.get("TopicArn")
            for arn_dict in arns
            if newsletter_name in arn_dict.get("TopicArn")
        ]
        print("XXX", newsletter_arn)
        if not len(newsletter_arn):
            return {"statusCode": 404, "body": json.dumps("Newsletter does not exists")}
        print("Publishing to topic")    
        resp = sns.publish(TargetArn=newsletter_arn[0], Message= json.dumps(message))
        
        response = {"message": f"Message sent to: {newsletter_name}"}
    except ClientError:
        # print("Couldn't subscribe from email %s.", email)
        return {"statusCode": 500, "body": json.dumps({"message": "failed"})}
    else:
        return {"statusCode": 200, "body": json.dumps(newsletter_arn)}


def send_email(event, context):
    print("SEND EMAIL LAMBDA:",event)
    SES = boto3.client("ses")
    body = json.loads(event.get("body"))
    newsletter_name = body["newsletter_name"]
    # TODO: Filter the results by admin email and then use key condition expressions to filter by newsletter
    # because there can be many admins who will use this service, also add pagination if required
    results = DynamoDb_Table.query(
        IndexName=SUBSCRIBERS_DDB_GSI.get("NEWSLETTER"),
        KeyConditionExpression="news_letter = :newsletter",
        ExpressionAttributeValues={":newsletter": newsletter_name},
    )["Items"]

    # TODO: How should we notify this 400 to the topic or function that triggered this?
    if not len(results):
        return {"statusCode": 404, "body": json.dumps("No Subscriptions found")}
    # TODO: Send Email to all subscribers
    # TODO: Add logger saying sending emails
    for record in results:
        SES.send_email(
            Source="abutahirism@gmail.com",
            Destination={"ToAddresses": [record["user_email"]]},
            Message={
                "Subject": {"Data": "This is an SES test email"},
                "Body": {"Html": {"Data": body["email_content"]}},
            },
        )
    body = {"message": "Go Serverless v3.0! Your function executed successfully!"}

    return {"statusCode": 200, "body": json.dumps(body)}

#TODO: Dynamically subscribe to a topic depending on the type of protocol, ex: email, sms, lambda endpoint etc.

