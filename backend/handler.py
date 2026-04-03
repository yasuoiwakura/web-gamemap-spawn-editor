import json
from mangum import Mangum
from app.main import app

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
}

_mangum_handler = Mangum(app, lifespan="auto")

def handler(event, context):
    method = event.get('httpMethod', '')
    if method == 'OPTIONS':
        return {
            'statusCode': 204,
            'headers': CORS_HEADERS,
            'body': ''
        }
    
    try:
        response = _mangum_handler(event, context)
        response['headers'] = {**response.get('headers', {}), **CORS_HEADERS}
        return response
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }