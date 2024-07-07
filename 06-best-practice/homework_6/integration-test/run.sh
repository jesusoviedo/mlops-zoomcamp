#!/usr/bin/env bash

export AWS_ACCESS_KEY_ID="abc"
export AWS_SECRET_ACCESS_KEY="xyz"
export AWS_DEFAULT_REGION="eu-west-1"
export S3_ENDPOINT_URL="http://localhost:4566"
export INPUT_FILE_PATTERN="s3://nyc-duration/in/{year:04d}-{month:02d}.parquet"
export OUTPUT_FILE_PATTERN="s3://nyc-duration/out/{year:04d}-{month:02d}.parquet"

docker-compose up -d
sleep 4

aws --endpoint-url=${S3_ENDPOINT_URL} s3 mb s3://nyc-duration
sleep 4

pipenv run python integration_test.py
sleep 4

ERROR_CODE=$?
if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi

docker-compose down