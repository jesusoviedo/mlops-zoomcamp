import mlflow
from flask import Flask, request, jsonify
import os

#el run_id se puede obtener como variables del entorno
#en la terminal ejecutar -->  export RUN_ID="b359abb9c3284227871ed15e1bddbf3f"
#RUN_ID = os.getenv("RUN_ID")

RUN_ID = "b359abb9c3284227871ed15e1bddbf3f"

#forma 1 con server mlflow activo
"""
MLFLOW_TRACKING_URI = 'http://127.0.0.1:5000'
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
logged_model = f'runs:/{RUN_ID}/model'
"""

#forma 2 apuntando a la ubicacion del modelo, sin servidor de mlflow activo
#file:///E:/Documentos/Coderepository/mlops-zoomcamp/04-deployment/webservice-mlflow/artifacts/1/{RUN_ID}/artifacts/model
logged_model = f'./artifacts/1/{RUN_ID}/artifacts/model'


model = mlflow.pyfunc.load_model(logged_model)


def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features


def predict(features):
    #X = dv.transform(features)
    #preds = model.predict(X)
    preds = model.predict(features)
    return float(preds[0])


app = Flask('duration-prediction')


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    ride = request.get_json()

    features = prepare_features(ride)
    pred = predict(features)

    result = {
        'duration': pred,
        'model_version': RUN_ID
    }

    return jsonify(result)

#para prod se recomienda usar un servidor como:
# gunicorn -> https://gunicorn.org/
# waitress -> https://flask.palletsprojects.com/en/3.0.x/deploying/waitress/
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)