import traceback
from parser import parse


def handler(event, context):
    try:
        parse()
    except Exception:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "text/plain"
            },
            "isBase64Encoded": False,
            "body": f"Failed to parse data from Github API, error: {traceback.format_exc()}"
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
