import json
import requests
import os

def lambda_handler(event, context):
    url = 'https://devlake.internal.porter.in/api/rest/blueprints/{}/trigger'

    # Retrieve the token from environment variables
    token = os.getenv('API_TOKEN')

    if not token:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'API token not found in environment variables'})
        }

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    payload = {
        "fullSync": True,
        "skipCollectors": False,
        "skipOnFail": False,
        "timeAfter": "2024-01-01T05:00:00Z"
    }

    blueprint_ids = event.get('blueprint_ids', [])

    results = {}

    for blueprint_id in blueprint_ids:
        try:
            response = requests.post(url.format(blueprint_id), headers=headers, json=payload)
            results[blueprint_id] = {
                'status_code': response.status_code,
                'response_text': response.text
            }
        except Exception as e:
            results[blueprint_id] = {
                'error': str(e)
            }

    return {
        'statusCode': 200,
        'body': json.dumps(results)
    }
