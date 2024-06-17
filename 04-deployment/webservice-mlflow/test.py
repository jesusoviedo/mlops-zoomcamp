#usamos pipenv para la gestion de paquetes en lugar de conda o envpip -> https://pipenv.pypa.io/en/latest/installation.html

import requests

ride = {
    "PULocationID": 10,
    "DOLocationID": 50,
    "trip_distance": 20
}

url = 'http://localhost:9696/predict'
response = requests.post(url, json=ride)
print(response.json())