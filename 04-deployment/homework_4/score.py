#!/usr/bin/env python
# coding: utf-8

#import sys
import argparse
import os
import pickle
import datetime
import pandas as pd
import numpy as np


def parse_arg():
    parser = argparse.ArgumentParser(description='Calculo de duracion de viajes offline (batch)')
    
    parser.add_argument("year", type=int, choices=range(2009, datetime.date.today().year + 1))
    parser.add_argument("month", type=int, choices=range(1, 12 + 1))
    
    return parser.parse_args()


def generate_filename(year, month, type_file):
    if type_file.lower() == "inp":
        return f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    if type_file.lower() == "out":
        directorio_out = "output"
        if not os.path.exists(f"{directorio_out}"):
            os.mkdir(f"{directorio_out}")
        return f"{directorio_out}/yellow_tripdata_{year:04d}-{month:02d}.parquet"


def read_data(filename, categorical, year, month):
    df = pd.read_parquet(filename)
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()
    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    #generate ride_id
    df["ride_id"] = f'{year:04d}/{month:02d}_' + df.index.astype('str')
    
    return df


def prepare_data(df, categorical):
    return df[categorical].to_dict(orient='records')


def load_model():
    with open('model.bin', 'rb') as f_in:
        dv, model = pickle.load(f_in)

    return dv, model


def apply_model(df, categorical):
    print(f"preparando los datos.....")
    X_dicts = prepare_data(df, categorical)
    
    print(f"cargando el modelo.....")
    dv_sl, model_sl = load_model()

    print(f"transformando los datos.....")
    X_val = dv_sl.transform(X_dicts)

    print(f"prediciendo los resultados.....")
    y_pred = model_sl.predict(X_val)

    return y_pred


def calculate_statistics(y_predic):
    dict_statistics = dict()
    dict_statistics["std_y_predic"] = float(np.std(y_predic))
    dict_statistics["mean_y_predic"] = float(np.mean(y_predic))
    
    return dict_statistics


def save_result(df, y_predic, filename):
    df_result = pd.DataFrame()
    df_result["ride_id"] = df["ride_id"]
    df_result["y_predic"] = y_predic
    
    df_result.to_parquet(filename, engine='pyarrow', compression=None, index=False)


def run():
    args = parse_arg()

    year = args.year #int(sys.argv[1]) #ejemplo -> 2023
    month = args.month #int(sys.argv[2]) #ejemplo -> 4
    CATEGORICAL = ['PULocationID', 'DOLocationID']
   
    input_file = generate_filename(year, month, "inp")
    output_file = generate_filename(year, month, "out")

    print(f"leyendo los datos de {input_file}.....")
    data_fram = read_data(input_file, CATEGORICAL, year, month)
    
    predictions = apply_model(data_fram, CATEGORICAL)

    print(f"calculando estadisticas.....")
    print(calculate_statistics(predictions))

    print(f"guardando los resultados en {output_file}.....")
    save_result(data_fram, predictions, output_file)


if __name__ == "__main__":
    run()

