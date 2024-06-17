#!/usr/bin/env python
# coding: utf-8


import os
import sys
import mlflow
import pandas as pd
import numpy as np
import uuid
from typing import List, Dict
from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import make_pipeline


def generate_uuid(n: int) -> List[str]:
    return [str(uuid.uuid4()) for ni in range(n)]


def read_dataframe(filename: str) -> pd.DataFrame:
    df = pd.read_parquet(filename)
    
    df['duration'] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df.duration = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)]
    df["id_viaje"] = generate_uuid(df.shape[0])
    
    return df


def prepare_dictionaries(df: pd.DataFrame) -> Dict:
    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)
    
    df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']
    categorical = ['PU_DO']
    numerical = ['trip_distance']
    dicts = df[categorical + numerical].to_dict(orient='records')
    
    return dicts

def load_model(rund_id: str):
    logged_model = f'../webservice-mlflow/artifacts/1/{rund_id}/artifacts/model'
    return mlflow.pyfunc.load_model(logged_model)

def save_result(df: pd.DataFrame, run_id: str, y_pred: np.ndarray, output_file: str):
    df_result = pd.DataFrame()
    df_result["id_viaje"] = df["id_viaje"]
    df_result["lpep_pickup_datetime"] = df["lpep_pickup_datetime"]
    df_result["PULocationID"] = df["PULocationID"]
    df_result["DOLocationID"] = df["DOLocationID"]
    df_result["trip_distance"] = df["trip_distance"]
    df_result["duracion_real"] = df["duration"]
    df_result["duracion_estimada"] = y_pred
    df_result["dif_real_estimada"] = df_result["duracion_real"] - df_result["duracion_estimada"]
    df_result["model_version"] = run_id
    #en vez de guarda localmente podria guardarse en la nube como en S3
    df_result.to_parquet(output_file, index=False)

def apply_model(input_file: str, output_file: str, run_id: str):
    print(f"leyendo los datos de {input_file}...")
    df = read_dataframe(input_file)
    dict_values = prepare_dictionaries(df)
    
    print(f"cargando el modelo con run id={run_id}...")
    model = load_model(run_id)

    print(f"aplicando el modelo...")
    y_pred = model.predict(dict_values)

    print(f"guardando los resultados en {output_file}...")
    save_result(df, run_id, y_pred, output_file)

def run():
    #esto se puede mejorar con -> https://docs.python.org/3/library/argparse.html o https://click.palletsprojects.com/en/8.1.x/
    year =  int(sys.argv[1]) #2021
    month = int(sys.argv[2]) #1
    taxy_type = sys.argv[3] #"green"
    RUN_ID = sys.argv[4] # "b359abb9c3284227871ed15e1bddbf3f"

    directorio_out = "output"
    if not os.path.exists(f"{directorio_out}"):
        os.mkdir(f"{directorio_out}")

    if not os.path.exists(f"{directorio_out}/{taxy_type}"):
        os.mkdir(f'{directorio_out}/{taxy_type}')

    INPUT_FILE = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{taxy_type}_tripdata_{year:04d}-{month:02d}.parquet"
    OUTPUT_FILE = f"{directorio_out}/{taxy_type}/tripdata_{year:04d}-{month:02d}.parquet"
    

    apply_model(INPUT_FILE, OUTPUT_FILE, RUN_ID)


if __name__ == "__main__":
    run()
