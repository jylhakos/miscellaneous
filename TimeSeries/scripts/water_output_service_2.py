# !/usr/bin/python3
# https://github.com/zeromq/pyzmq
# $ pip install pyzmq

import time

import datetime

import json

import zmq

from psycopg2.extras import RealDictCursor
from psycopg2.extras import DictCursor
import psycopg2

from multiprocessing import Pipe

from multiprocessing import Process

from multiprocessing import current_process

import threading

DB_URI_STR = "postgres://demo:demo@192.168.3.2:5432/demo?sslmode=require"

''' msg queue for gpu 0 '''

port_iot_sub_0 = "5563"

zmq_context_sub_0 = zmq.Context()

zmq_socket_sub_0 = zmq_context_sub_0.socket(zmq.PULL)

print("zmq_socket_sub_0: %s" % port_iot_sub_0)

zmq_socket_sub_0.connect("tcp://localhost:%s" % port_iot_sub_0)


''' msg queue for gpu 1 '''

''' port_iot_sub_1 = "5558"

zmq_context_sub_1 = zmq.Context()

zmq_socket_sub_1 = zmq_context_sub_1.socket(zmq.PULL)

print("zmq_socket_sub_1: %s" % port_iot_sub_1)

zmq_socket_sub_1.connect("tcp://localhost:%s" % port_iot_sub_1)

#socket.setsockopt_string(zmq.SUBSCRIBE, topic)
#zmq_socket_sub.setsockopt_string(zmq.SUBSCRIBE, "") '''

def child_process(function):

	def wrapper(*args, **kwargs):

		def worker(connection, function, args, kwargs):

			connection.send(function(*args, **kwargs))

			connection.close()

		parent_connection, child_connection = Pipe()

		process = Process(target=worker, args=(child_connection, function, args, kwargs))

		process.start()

		result = parent_connection.recv()

		process.join()

		return result

	return wrapper


@child_process
def process_output(msg):

	print("\n\nprocess_output")

	msg_str = msg.decode('utf-8')

	temp_dict = json.loads(msg_str)

	print('\n\ntemp_dict',temp_dict)

	timestamp = temp_dict["TIMESTAMP"]

	#print('\ntimestamp',timestamp)

	#place = temp_dict["PLACE"]

	#print('\nplace',place)

	#meter = temp_dict["METER"]

	#print('\nmeter',meter)

	feature = temp_dict["FEATURE"]

	#print('\nfeature',feature)

	predicted = temp_dict["PREDICTED"]

	#print('\npredicted',predicted)

	#transaction_thread = threading.Thread(target=transaction_with_db,args=(timestamp,place,meter,feature,predicted))

	transaction_thread = threading.Thread(target=transaction_with_db,args=(timestamp,feature,predicted))

	transaction_thread.start()

	#transaction_with_db(timestamp,place,meter,feature,predicted)

def sql_create_table(table_name):

	db_cursor = None

	db_connect = None

	try:

		db_connect = psycopg2.connect(DB_URI_STR)

		db_cursor = db_connect.cursor(cursor_factory=DictCursor)

		db_cursor.execute("CREATE TABLE " + table_name + "(feature VARCHAR(255) NOT NULL, timestamp TIMESTAMPTZ NOT NULL, value VARCHAR(255) NOT NULL,  PRIMARY KEY (feature, timestamp));")

		db_connect.commit()

		db_cursor.close()

		db_connect.close()

	except Exception as error:

		if db_connect:
			db_connect.rollback()

		print("\n Error", error)

	pass

#def transaction_with_db(timestamp, place, meter, feature, predicted):
def transaction_with_db(timestamp, feature, predicted):

	db_cursor = None

	db_connect = None

	db_uri = "postgres://demo:demo@192.168.3.2:5432/demo?sslmode=require"

	db_connect = psycopg2.connect(db_uri)

	db_cursor = db_connect.cursor(cursor_factory=RealDictCursor)

	table = 'water_output'

	#columns = 'timestamp, place, meter, feature, value'

	#columns = 'timestamp, feature, value'

	print ('\n\ntransaction_with_db: %s %s %s' % (timestamp, feature, predicted))

	#db_cursor.execute("INSERT INTO output_dataset(timestamp, place, meter, feature, value) VALUES (%s, %s, %s, %s, %s);" , (timestamp, place, meter, feature, predicted))

	db_cursor.execute("INSERT INTO " + table + "(timestamp, feature, value) VALUES (%s, %s, %s);" , (timestamp, feature, predicted))

	db_connect.commit()

	db_cursor.close()

	pass

''' zmq message queue subscriber '''

def loop_0():

	msg = None

	while True:

		print("\n\nwater_zmq_socket_sub_2")

		msg = zmq_socket_sub_0.recv()

		#zmq_socket_sub.send_string("")

		print("\nrecv()",msg)

		process_output(msg)

		''' msg_str = message.decode('utf-8')

		temp_dict = json.loads(msg_str)

		print('\n\ntemp_dict',temp_dict)

		timestamp = temp_dict["TIMESTAMP"]

		print('\ntimestamp',timestamp)

		place = temp_dict["PLACE"]

		print('\nplace',place)

		meter = temp_dict["METER"]

		print('\nmeter',meter)

		feature = temp_dict["FEATURE"]

		print('\nfeature',feature)

		predicted = temp_dict["PREDICTED"]

		print('\npredicted',predicted)

		transaction_with_db(timestamp,place,meter,feature,predicted) '''

''' def loop_1():

	msg = None

	while True:

		print("\n\nzmq_socket_sub_1")

		msg = zmq_socket_sub_1.recv()

		#zmq_socket_sub.send_string("")

		print("\nrecv()",msg)

		process_output(msg) '''

table_name = 'water_output'

sql_create_table(table_name)

loop_0_thread = threading.Thread(target=loop_0,args=())
	
loop_0_thread.start()

''' loop_1_thread = threading.Thread(target=loop_1,args=())
	
loop_1_thread.start() '''
