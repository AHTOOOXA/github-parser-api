from parser import parse


def handler(event, context):
    # repository_quantity = event["queryStringParameters"]["repository_quantity"]
    # commit_quantity = event["queryStringParameters"]["commit_quantity"]

    try:
        parse()
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "text/plain"
            },
            "isBase64Encoded": False,
            "body": f"Failed to parse data from Github API, error: {e}"
        }
    else:
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/plain"
            },
            "isBase64Encoded": False,
            "body": "Successfully parsed data from Github API"
        }
