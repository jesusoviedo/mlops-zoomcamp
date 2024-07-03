import os
import pandas as pd
import subprocess
from datetime import datetime


def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)


def test_save_input_data_s3(year, month):
    S3_ENDPOINT_URL="http://localhost:4566"
    input_file = f"s3://nyc-duration/in/{year:04d}-{month:02d}.parquet"
    columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']

    data = [
        (None, None, dt(1, 1), dt(1, 10)),
        (1, 1, dt(1, 2), dt(1, 10)),
        (1, None, dt(1, 2, 0), dt(1, 2, 59)),
        (3, 4, dt(1, 2, 0), dt(2, 2, 1)),      
    ]

    df_input = pd.DataFrame(data, columns=columns)
    options = {'client_kwargs': {'endpoint_url': S3_ENDPOINT_URL}}
    df_input.to_parquet(input_file, engine='pyarrow', compression=None, index=False, storage_options=options)


def test_save_result_data_s3(year, month):
    os.environ["S3_ENDPOINT_URL"] = "http://localhost:4566"
    os.environ["INPUT_FILE_PATTERN"] = "s3://nyc-duration/in/{year:04d}-{month:02d}.parquet"
    os.environ["OUTPUT_FILE_PATTERN"] = "s3://nyc-duration/out/{year:04d}-{month:02d}.parquet"
    os.system(f"cd .. && python batch.py {year} {month}")

    S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL')
    OUTPUT_FILE_PATTERN = os.getenv('OUTPUT_FILE_PATTERN')

    options = {'client_kwargs': {'endpoint_url': S3_ENDPOINT_URL}} 
    result = pd.read_parquet(OUTPUT_FILE_PATTERN.format(year=year, month=month), storage_options=options)
        
    print(f"sum of predicted duration: {result.predicted_duration.sum()}")

    

if __name__ == "__main__":
    test_save_input_data_s3(2023, 1)
    test_save_result_data_s3(2023, 1)
