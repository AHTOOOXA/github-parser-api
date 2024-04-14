def handler(event, context):
    name = event['queryStringParameters']['name']

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/plain'
        },
        'isBase64Encoded': False,
        'body': 'Hello, {}!'.format(name)
    }
