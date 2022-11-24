import json


def get_item(event, context):
    if not event or event.get("pathParametes"):
        return {"statusCode": 400, "body": json.dumps("Missing necessary input")}
    eid = int(event.get("pathParameters").get("eid"))
    if not eid:
        return {"statusCode": 400, "body": json.dumps("Mandatory field is missing: eid")}
    try:
        response =data.get(eid)
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(e)}
    else:
        return {"statusCode": 200, "body": json.dumps(response)}    

def post_item(event, context):
    print("POST DATA FUNCTION:", event)
    if not (event or event.get("body")):
        return {"statusCode": 400, "body": json.dumps("Missing necessary input")}
    body = json.loads(event.get("body"))
    try:
        data[104]=body
        print(data)
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(e)}
    else:
        return {"statusCode": 201, "body": json.dumps("Added Succesfully")}    


data = {
    101: {
        "name": "Tahir",
        "designation": "Software Engineer",
        "company": "KonfHub Technologies",
    },
    102: {
        "name": "Rashmi",
        "designation": "Senior Software Engineer",
        "company": "KonfHub Technologies",
    },
    103: {
        "name": "Srushith",
        "designation": "Head Of Engineering",
        "company": "KonfHub Technologies",
    },
}
