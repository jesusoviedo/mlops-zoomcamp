### Ejecución de un pipeline mediante solicitud de API

Ver la documentación [aqui](https://docs.mage.ai/orchestration/triggers/trigger-pipeline-api)

```
curl --location --request POST 'http://127.0.0.1:6789/api/runs' \
--header 'Content-Type: application/json' \
--header 'Cookie: lng=en' \
--header 'Authorization: Bearer 32c6edb3e9fb463da615eb727fa4c50d' \
--data '{
    "run": {
        "pipeline_uuid": "pl_predict_online_trips",
        "block_uuid": "c_inferencia",
        "variables": {
            "inputs": [
                {
                    "DOLocationID": "170",
                    "PULocationID": "65",
                    "trip_distance": 6.54
                },
                {
                    "DOLocationID": "17",
                    "PULocationID": "67",
                    "trip_distance": 8.5
                }
            ]
        }
    }
}'
```