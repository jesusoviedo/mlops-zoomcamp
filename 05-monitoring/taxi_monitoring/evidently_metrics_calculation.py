import datetime
import time
import random
import logging 
import pandas as pd
import psycopg
import joblib

#from prefect import task, flow

from evidently.report import Report
from evidently import ColumnMapping
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric, DatasetMissingValuesMetric

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

SEND_TIMEOUT = 10
rand = random.Random()

create_table_statement = """
drop table if exists evidently_metrics;
create table evidently_metrics(
	timestamp timestamp,
	prediction_drift float,
	num_drifted_columns integer,
	share_missing_values float
)
"""

reference_data = pd.read_parquet('data/reference.parquet')
with open('models/lin_reg.bin', 'rb') as f_in:
	model = joblib.load(f_in)

raw_data = pd.read_parquet('data/green_tripdata_2022-02.parquet')

begin = datetime.datetime(2022, 2, 1, 0, 0)
num_features = ['passenger_count', 'trip_distance', 'fare_amount', 'total_amount']
cat_features = ['PULocationID', 'DOLocationID']
column_mapping = ColumnMapping(
    prediction='prediction',
    numerical_features=num_features,
    categorical_features=cat_features,
    target=None
)

report = Report(metrics = [
    ColumnDriftMetric(column_name='prediction'),
    DatasetDriftMetric(),
    DatasetMissingValuesMetric()
])


#@task
def prepare_db():
	with psycopg.connect("host=127.0.0.1 port=5432 user=postgres password=LIsa929322*", autocommit=True) as conn:
		res = conn.execute("SELECT 1 FROM pg_database WHERE datname='test'")
		if len(res.fetchall()) == 0:
			conn.execute("create database test;")
			logging.info("base de datos creada con éxito")
	
	with psycopg.connect("host=127.0.0.1 port=5432 dbname=test user=postgres password=LIsa929322*", autocommit=True) as conn:
		conn.execute(create_table_statement)
		logging.info("tabla creada con éxito")


#@task
def calculate_metrics_postgresql(curr, i):
	current_data = raw_data[(raw_data.lpep_pickup_datetime >= (begin + datetime.timedelta(i))) &
		(raw_data.lpep_pickup_datetime < (begin + datetime.timedelta(i + 1)))]

	#current_data.fillna(0, inplace=True)
	current_data['prediction'] = model.predict(current_data[num_features + cat_features].fillna(0))

	report.run(reference_data = reference_data, current_data = current_data, column_mapping=column_mapping)
	result = report.as_dict()
	prediction_drift = result['metrics'][0]['result']['drift_score']
	num_drifted_columns = result['metrics'][1]['result']['number_of_drifted_columns']
	share_missing_values = result['metrics'][2]['result']['current']['share_of_missing_values']
	date_predict = begin + datetime.timedelta(i)
	date_predict_format = date_predict.strftime("%Y-%m-%d")

	curr.execute(
		"insert into evidently_metrics(timestamp, prediction_drift, num_drifted_columns, share_missing_values) values (%s, %s, %s, %s)",
		(date_predict, prediction_drift, num_drifted_columns, share_missing_values)
	)
	logging.info(f"registros insertados con éxito para el dia: {date_predict_format}")


#@task
def sleep_seconds(last_send):
	new_send = datetime.datetime.now()
	seconds_elapsed = (new_send - last_send).total_seconds()
	if seconds_elapsed < SEND_TIMEOUT:
		time.sleep(SEND_TIMEOUT - seconds_elapsed)
	return new_send


#@task
def update_last_send(last_send, new_send):
	while last_send < new_send:
		last_send = last_send + datetime.timedelta(seconds=SEND_TIMEOUT)
	return last_send


#@flow
def run_process():
	with psycopg.connect("host=127.0.0.1 port=5432 dbname=test user=postgres password=LIsa929322*", autocommit=True) as conn:
		
		last_send = datetime.datetime.now()# - datetime.timedelta(seconds=SEND_TIMEOUT)
		for i in range(0, 28):
			calculate_metrics_postgresql(conn, i)
			new_send = sleep_seconds(last_send)
			last_send = update_last_send(last_send, new_send)
			#logging.info(f"siguiente insert {last_send}")
		logging.info("operación finalizada")

def metrics_calculation():
	prepare_db()
	run_process()


if __name__ == '__main__':
	metrics_calculation()
