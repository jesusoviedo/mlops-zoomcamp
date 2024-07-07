import os
import pandas as pd
import boto3
import subprocess
import time
from datetime import datetime
from deepdiff import DeepDiff
from pprint import pprint


def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)


def test_save_input_data_s3(year, month):
    S3_ENDPOINT_URL="http://localhost:4566"
    bucket_name = "nyc-duration"
    input_file = f"s3://{bucket_name}/in/{year:04d}-{month:02d}.parquet"
    file = input_file.split(bucket_name+"/")[1]
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
    
    s3_client = boto3.client('s3', endpoint_url=S3_ENDPOINT_URL)
    response_bucket_object = s3_client.list_objects_v2(Bucket=bucket_name)

    list_archivo = []
    if 'Contents' in response_bucket_object:
        print(f"\n\nBucket name: {bucket_name}")    
        for obj in response_bucket_object['Contents']:
            print(f"file name: {obj['Key']} | size: {obj['Size']}")
            list_archivo.append(obj['Key'])
    else:
        print("empty bucket")
    print("\n\n")
    assert file in list_archivo


def test_save_result_data_s3(year, month):
    #os.system(f"cd .. && python batch.py {year} {month}")
    
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    os.chdir(parent_dir)
    subprocess.run(["python", "batch.py", str(year), str(month)])
    os.chdir(current_dir) 

    S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL')
    OUTPUT_FILE_PATTERN = os.getenv('OUTPUT_FILE_PATTERN')

    options = {'client_kwargs': {'endpoint_url': S3_ENDPOINT_URL}} 
    actual_response = pd.read_parquet(OUTPUT_FILE_PATTERN.format(year=year, month=month), storage_options=options)
    sum_predict = actual_response["predicted_duration"].sum()
    actual_response = actual_response.to_dict(orient='records')
    
    expected_response = [{'ride_id': '2023/01_0', 'predicted_duration': 23.197},
                         {'ride_id': '2023/01_1', 'predicted_duration': 13.080},
                        ]

    diff = DeepDiff(actual_response, expected_response, significant_digits=3)

    print('diff =')
    pprint(diff)
    if diff:
        print('\n\nactual =')
        pprint(actual_response)
        print('\n\nexpected =')
        pprint(expected_response)

    print(f"sum of predict: {sum_predict}\n\n")

    assert 'iterable_item_added' not in diff
    assert 'type_changes' not in diff
    assert 'values_changed' not in diff


if __name__ == "__main__":
    test_save_input_data_s3(2023, 1)
    time.sleep(5)
    test_save_result_data_s3(2023, 1)
