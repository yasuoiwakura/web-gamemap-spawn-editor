import json
import sys
from mangum import Mangum

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
}

CORS_MULTI_HEADERS = {
    'Access-Control-Allow-Origin': ['*'],
    'Access-Control-Allow-Methods': ['GET,POST,PUT,DELETE,OPTIONS'],
    'Access-Control-Allow-Headers': ['Content-Type'],
}

try:
    from app.main import app
    _mangum_handler = Mangum(app, lifespan="auto")
    _import_error = None
except Exception as e:
    print(f"IMPORT ERROR: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    _mangum_handler = None
    _import_error = str(e)

def handler(event, context):
    # Strip stage prefix from HTTP API path (e.g. /Prod/games -> /games)
    stage = event.get('requestContext', {}).get('stage', '')
    raw_path = event.get('rawPath', '')
    if stage and raw_path.startswith(f'/{stage}'):
        raw_path = raw_path[len(stage) + 1:] or '/'
        event['rawPath'] = raw_path

    method = event.get('httpMethod', '')
    if method == 'OPTIONS':
        return {
            'statusCode': 204,
            'headers': CORS_HEADERS,
            'multiValueHeaders': CORS_MULTI_HEADERS,
            'body': ''
        }
    
    if _import_error:
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'multiValueHeaders': CORS_MULTI_HEADERS,
            'body': json.dumps({'error': f'Import error: {_import_error}'})
        }
    
    try:
        response = _mangum_handler(event, context)
        response['headers'] = {**response.get('headers', {}), **CORS_HEADERS}
        response['multiValueHeaders'] = {**response.get('multiValueHeaders', {}), **CORS_MULTI_HEADERS}
        return response
    except Exception as e:
        print(f"HANDLER ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'multiValueHeaders': CORS_MULTI_HEADERS,
            'body': json.dumps({'error': str(e)})
        }
