import time
import datetime
import calendar
import logging 
import pandas as pd
import psycopg
import joblib
import os
import argparse
from evidently.report import Report
from evidently import ColumnMapping
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric, DatasetMissingValuesMetric, ColumnSummaryMetric, ColumnQuantileMetric
#from prefect import task, flow


#@task
def parse_arg():
    parser = argparse.ArgumentParser(description='Calculo de duracion de viajes')
    parser.add_argument("year", type=int, choices=range(2009, datetime.date.today().year + 1))
    parser.add_argument("month", type=int, choices=range(1, 12 + 1))

    return parser.parse_args()


#@task
def config_log(year, month, FOLDER_LOG):
	logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
	if not os.path.exists(f"{FOLDER_LOG}"):
		os.mkdir(f"{FOLDER_LOG}")
	file_handler = logging.FileHandler(f'{FOLDER_LOG}/evidently_metrics_calculation_batch_{year:04d}_{month:02d}.log', encoding='utf-8')
	file_handler.setLevel(logging.ERROR)
	logging.getLogger('').addHandler(file_handler)


#@task
def statement_create_table():
		
    create_table_statement = """
	drop table if exists evidently_metrics;
	create table evidently_metrics(
		timestamp timestamp,
		prediction_drift float,
		num_drifted_columns integer,
		share_missing_values float,
		fare_amount_mean float,
		fare_amount_std float,
		fare_amount_p25 float,
		fare_amount_p50 float, 
		fare_amount_p75 float, 
		fare_amount_min float,
		fare_amount_max float,
		fare_amount_q05 float
	)
	"""

    return create_table_statement


#@task
def prepare_db():
	with psycopg.connect("host=127.0.0.1 port=5432 user=postgres password=LIsa929322*", autocommit=True) as conn:
		res = conn.execute("SELECT 1 FROM pg_database WHERE datname='test'")
		if len(res.fetchall()) == 0:
			conn.execute("create database test;")
			logging.info("base de datos creada con éxito")
	
	with psycopg.connect("host=127.0.0.1 port=5432 dbname=test user=postgres password=LIsa929322*", autocommit=True) as conn:
		conn.execute(statement_create_table())
		logging.info("tabla creada con éxito")


#@task
def load_data_and_model(FOLDER_DATA, FOLDER_MODEL, year, month):
    reference_data = pd.read_parquet(f'{FOLDER_DATA}/reference.parquet')
    raw_data = pd.read_parquet(f'{FOLDER_DATA}/green_tripdata_{year:04d}-{month:02d}.parquet')

    with open(f'{FOLDER_MODEL}/lin_reg.bin', 'rb') as f_in:
        model = joblib.load(f_in)
    
    return reference_data, raw_data, model


#@task
def config_report():
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
		DatasetMissingValuesMetric(),
		ColumnSummaryMetric(column_name='fare_amount'),
		ColumnQuantileMetric(column_name='fare_amount', quantile=0.5)
	])

    return report, column_mapping, num_features, cat_features


#@task
def calculate_metrics(FOLDER_DATA, FOLDER_MODEL, year, month, conn, i):
	begin = datetime.datetime(year, month, 1, 0, 0)
	reference_data, raw_data, model = load_data_and_model(FOLDER_DATA, FOLDER_MODEL, year, month)
	report, column_mapping, num_features, cat_features = config_report()

	current_data = raw_data[(raw_data.lpep_pickup_datetime >= (begin + datetime.timedelta(i))) & 
						 (raw_data.lpep_pickup_datetime < (begin + datetime.timedelta(i + 1)))]

	current_data['prediction'] = model.predict(current_data[num_features + cat_features].fillna(0))

	report.run(reference_data = reference_data, current_data = current_data, column_mapping=column_mapping)
	result = report.as_dict()

	prediction_drift = result['metrics'][0]['result']['drift_score']
	num_drifted_columns = result['metrics'][1]['result']['number_of_drifted_columns']
	share_missing_values = result['metrics'][2]['result']['current']['share_of_missing_values']
	fare_amount_mean = result['metrics'][3]['result']['current_characteristics']['mean']
	fare_amount_std = result['metrics'][3]['result']['current_characteristics']['std']
	fare_amount_p25 = result['metrics'][3]['result']['current_characteristics']['p25']
	fare_amount_p50 = result['metrics'][3]['result']['current_characteristics']['p50']
	fare_amount_p75 = result['metrics'][3]['result']['current_characteristics']['p75']
	fare_amount_min = result['metrics'][3]['result']['current_characteristics']['min']
	fare_amount_max = result['metrics'][3]['result']['current_characteristics']['max']
	fare_amount_q05 = result['metrics'][4]['result']['current']['value']

	date_predict = begin + datetime.timedelta(i)
	date_predict_format = date_predict.strftime("%Y-%m-%d")

	conn.execute(
		"insert into evidently_metrics(timestamp, prediction_drift, num_drifted_columns, share_missing_values, fare_amount_mean, fare_amount_std, fare_amount_p25, fare_amount_p50, fare_amount_p75, fare_amount_min, fare_amount_max, fare_amount_q05) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
		(date_predict, prediction_drift, num_drifted_columns, share_missing_values, fare_amount_mean, fare_amount_std, fare_amount_p25, fare_amount_p50, fare_amount_p75, fare_amount_min, fare_amount_max, fare_amount_q05)
	)
	logging.info(f"registros insertados con éxito para la fecha: {date_predict_format}")


#@task
def sleep_seconds(last_send, SEND_TIMEOUT):
	new_send = datetime.datetime.now()
	seconds_elapsed = (new_send - last_send).total_seconds()
	if seconds_elapsed < SEND_TIMEOUT:
		time.sleep(SEND_TIMEOUT - seconds_elapsed)
	return new_send


#@task
def update_last_send(last_send, new_send, SEND_TIMEOUT):
	while last_send < new_send:
		last_send = last_send + datetime.timedelta(seconds=SEND_TIMEOUT)
	return last_send


#@flow
def run_process(FOLDER_DATA, FOLDER_MODEL, SEND_TIMEOUT, year, month):
	with psycopg.connect("host=127.0.0.1 port=5432 dbname=test user=postgres password=LIsa929322*", autocommit=True) as conn:
		last_send = datetime.datetime.now()
		max_day = calendar.monthrange(year, month)[1]
		for i in range(0, max_day):
			calculate_metrics(FOLDER_DATA, FOLDER_MODEL, year, month, conn, i)
			new_send = sleep_seconds(last_send, SEND_TIMEOUT)
			last_send = update_last_send(last_send, new_send, SEND_TIMEOUT)
		logging.info("operación finalizada")


if __name__ == '__main__':
	args = parse_arg()
	year = args.year
	month = args.month

	FOLDER_LOG = "./logs"
	FOLDER_DATA = "./data"
	FOLDER_MODEL = "./model"
	SEND_TIMEOUT = 2

	config_log(year, month, FOLDER_LOG)
	prepare_db()
	run_process(FOLDER_DATA, FOLDER_MODEL, SEND_TIMEOUT, year, month)
