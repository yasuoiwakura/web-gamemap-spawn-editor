import json
import sys
from mangum import Mangum

try:
    from app.main import app
    _mangum_handler = Mangum(app, lifespan="auto")
except Exception as e:
    print(f"IMPORT ERROR: {e}", file=sys.stderr)
    _mangum_handler = None

def handler(event, context):
    # HTTP API v2.0: non-$default stage prefixes rawPath with /{stage}
    stage = event.get('requestContext', {}).get('stage', '')
    raw_path = event.get('rawPath', '')
    if stage and raw_path.startswith(f'/{stage}'):
        raw_path = raw_path[len(stage) + 1:] or '/'
        event['rawPath'] = raw_path

    print(f"DEBUG rawPath: {raw_path}", file=sys.stderr)
    print(f"DEBUG method: {event.get('requestContext', {}).get('http', {}).get('method', event.get('httpMethod'))}", file=sys.stderr)

    if _mangum_handler is None:
        return {'statusCode': 500, 'body': json.dumps({'error': 'Import failed'})}

    return _mangum_handler(event, context)
