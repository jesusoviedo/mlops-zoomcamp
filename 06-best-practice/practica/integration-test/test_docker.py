# pylint: disable=duplicate-code

import json

import requests
from deepdiff import DeepDiff

with open('event.json', 'rt', encoding='utf-8') as f_in:
    event = json.load(f_in)


url = 'http://localhost:9000/2015-03-31/functions/function/invocations'
actual_response = requests.post(url, json=event).json()
print('actual response:')

print(json.dumps(actual_response, indent=3))

expected_response = {
    'predictions': [
        {
            'model': 'ride_duration_prediction_model',
            'version': 'Test123',
            'prediction': {
                'ride_duration': 18.1689,
                'ride_id': 256,
            },
        }
    ]
}

diff = DeepDiff(actual_response, expected_response, significant_digits=4)

if diff:
    print(f'\n\ndiff={diff}\n\n')
else:
    print(f'\n\n{__file__.split("/")[-1]} -> ok\n\n')

assert 'type_changes' not in diff
assert 'values_changed' not in diff
