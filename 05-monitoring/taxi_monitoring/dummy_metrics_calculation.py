import datetime
import time
import random
import logging 
import uuid
import pytz
import pandas as pd
import os
import psycopg

FOLDER_LOG = "./logs"
SEND_TIMEOUT = 10 #5, 2, 1, 0.5
rand = random.Random()

create_table_statement = """
drop table if exists dummy_metrics;
create table dummy_metrics(
	timestamp timestamp,
	value1 integer,
	value2 varchar,
	value3 float
)
"""

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
if not os.path.exists(f"{FOLDER_LOG}"):
	os.mkdir(f"{FOLDER_LOG}")
file_handler = logging.FileHandler(f'{FOLDER_LOG}/app_dummy_metrics_cal.log', encoding='utf-8')
file_handler.setLevel(logging.ERROR)
logging.getLogger('').addHandler(file_handler)

def prepare_db():
	with psycopg.connect("host=127.0.0.1 port=5432 user=postgres password=LIsa929322*", autocommit=True) as conn:
		res = conn.execute("SELECT 1 FROM pg_database WHERE datname='test'")
		if len(res.fetchall()) == 0:
			conn.execute("create database test;")
			logging.info("base de datos creada con éxito")
	
	with psycopg.connect("host=127.0.0.1 port=5432 dbname=test user=postgres password=LIsa929322*", autocommit=True) as conn:
		conn.execute(create_table_statement)
		logging.info("tabla creada con éxito")

def insert_dummy_metrics_postgresql(conexion):
	value1 = rand.randint(0, 1000)
	value2 = str(uuid.uuid4())
	value3 = rand.random()

	conexion.execute(
		"insert into dummy_metrics(timestamp, value1, value2, value3) values (%s, %s, %s, %s)",
		(datetime.datetime.now(pytz.timezone('America/Asuncion')), value1, value2, value3)
	)
	logging.info("registro insertado con éxito")


def sleep_seconds(last_send):
	new_send = datetime.datetime.now()
	seconds_elapsed = (new_send - last_send).total_seconds()
	if seconds_elapsed < SEND_TIMEOUT:
		time.sleep(SEND_TIMEOUT - seconds_elapsed)
	return new_send


def update_last_send(last_send, new_send):
	while last_send < new_send:
		last_send = last_send + datetime.timedelta(seconds=SEND_TIMEOUT)
	return last_send


def run_process():
	with psycopg.connect("host=127.0.0.1 port=5432 dbname=test user=postgres password=LIsa929322*", autocommit=True) as conn:
		
		last_send = datetime.datetime.now()# - datetime.timedelta(seconds=SEND_TIMEOUT)
		for i in range(0, 1000):
			insert_dummy_metrics_postgresql(conn)
			new_send = sleep_seconds(last_send)
			last_send = update_last_send(last_send, new_send)
			#logging.info(f"siguiente insert {last_send}")
		logging.info("operación finalizada")

def metrics_calculation():
	prepare_db()
	run_process()


if __name__ == '__main__':
	metrics_calculation()