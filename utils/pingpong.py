import os
import json
import requests


def request(query, session_id):
    headers = {
        'Authorization': f'Basic {os.environ["PINGPONG_AUTH"]}',
        'Content-Type': 'application/json'
    }
    data = {'request': {'query': f'{query}'}}
    response = requests.post(
        f'https://builder.pingpong.us/api/builder/61053069e4b091a94bce21bd/integration/v0.2/custom/{session_id}',
        data=json.dumps(data), headers=headers
    )
    return response.json()['response']['replies']
