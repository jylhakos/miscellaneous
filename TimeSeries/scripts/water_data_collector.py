# !/usr/bin/python3
# $ psql -U psql -h 192.168.3.2
# demo=> SELECT timestamp, place, meter, feature, value FROM input_dataset ORDER BY timestamp;
# demo=> DELETE FROM input_dataset WHERE timestamp >= '1970-01-01 00:00:00';
# $ sudo apt-get install postgresql-client
# $ mosquitto_passwd -b passwordfile user password
# $ mosquitto_sub -t iot -h 114.55.211.112 -p 1883 -u iot -P iot
# $ mosquitto_sub -t api/v1/json/uploadmessage -h 114.55.211.112
# https://github.com/zeromq/pyzmq
# $ pip install paho.mqtt
# $ pip install pyzmq
# $ pip install zerorpc
# $ sudo python3 -m pip install zerorpc
''' {
	"MESSAGE": {
		"PLACE": "HVSB",
		"METER": "HVSB_S_B2_G001-J03",
		"FEATURE": "voltage_B",
		"TIMESTAMP": "1970-01-01T01:45:00.000Z",
		"VALUE": 12880.67
	}
} '''
''' MQTT: {"MESSAGE": {"PLACE": "HVSB", "METER": "HVSB_S_B2_G001-J03", "FEATURE": "voltage_B", "TIMESTAMP": "1970-01-03T17:30:00.000Z", "VALUE": 12593.24}} '''
''' $ redis-cli '''
''' 127.0.0.1:6379> TS.RANGE HVSB:HVSB_S_B2_G001-J03:voltage_B 1 2000000000 '''
''' CREATE TABLE devices(
	place VARCHAR(255) NOT NULL, 
	meter VARCHAR(255) NOT NULL, 
	feature VARCHAR(255) NOT NULL,
	PRIMARY KEY (place, meter, feature)
	); '''

import sys

import os

import site

import getopt

import time

import datetime

import matplotlib.pyplot as plt

import numpy as np

import pandas as pd

import json

import paho.mqtt.client as mqtt

#import random

import itertools

#import zerorpc

import gevent

#import zmq
import zmq

from redistimeseries.client import Client as RedisTimeSeries
from redistimeseries.client import TSInfo as TSInfo
from redis.exceptions import ResponseError

''' $ sudo apt-get install python3-psycopg2 '''
from psycopg2.extras import RealDictCursor
from psycopg2.extras import DictCursor
import psycopg2

from multiprocessing import Pipe
from multiprocessing import Process
from multiprocessing import current_process

import threading

global db_cursor
global db_connect

#user = "iot"
#password = "iot"
#topic = "iot"
TOPIC = "api/v1/json/uploadmessage"

DB_URI_STR = "postgres://demo:demo@192.168.3.2:5432/demo?sslmode=require"

global TIMESTAMP_KEY
#TIMESTAMP_KEY = 'TIMESTAMP'
TIMESTAMP_KEY = 'dataTime'

#global VALUE_KEY
#VALUE_KEY = 'VALUE'

#TODO: LIST OF KEYS
FEATURE_KEY_LIST = ['ai_cod1_cod', 'ai_ph1_temp', 'ai_ph1_ph', 'ai_ss1_ss']

IGNORE_PAYLOAD = "clientOffline"

#global PLACE

#global METER

#global FEATURE

global DEVICES_TABLE_NAME
#DEVICES_TABLE_NAME = 'iot_devices'
DEVICES_TABLE_NAME = 'water_devices'

#global devices_dict_list
#devices_dict_list = list()

#global DEVICES_DICT_LIST
#DEVICES_DICT_LIST = list()

#global INPUT_LIST
#INPUT_LIST = list()

global MIN_INPUT_LIST_LENGTH
#MIN_INPUT_LIST_LENGTH = 11
MIN_INPUT_LIST_LENGTH = 8

#global gpu
#gpu = 0

global toggle
#toggle = itertools.cycle([0, 1, 2, 3])
toggle = itertools.cycle([0])

#global prediction_interval_list
#prediction_interval_list = list()

#port = "5556"

#port = [5548,5549,5550,5551]

''' ØMQ sockets are NOT thread safe. 

Applications MUST NOT use a socket from multiple threads except after migrating a socket 

from one thread to another with a "full fence" memory barrier. '''

''' global zmq_socket_0
global zmq_socket_1
global zmq_socket_2
global zmq_socket_3

context_0 = zmq.Context()

zmq_socket_0 = context_0.socket(zmq.PUSH)
zmq_socket_0.setsockopt(zmq.LINGER,500)
zmq_socket_0.setsockopt(zmq.SNDTIMEO,1000)
zmq_socket_0.bind("tcp://*:%s" % port[0])

context_1 = zmq.Context()

zmq_socket_1 = context_1.socket(zmq.PUSH)
zmq_socket_1.setsockopt(zmq.LINGER,500)
zmq_socket_1.setsockopt(zmq.SNDTIMEO,1000)
zmq_socket_1.bind("tcp://*:%s" % port[1])

context_2 = zmq.Context()

zmq_socket_2 = context_2.socket(zmq.PUSH)
zmq_socket_2.setsockopt(zmq.LINGER,500)
zmq_socket_2.setsockopt(zmq.SNDTIMEO,1000)
zmq_socket_2.bind("tcp://*:%s" % port[2])

context_3 = zmq.Context()

zmq_socket_3 = context_3.socket(zmq.PUSH)
zmq_socket_3.setsockopt(zmq.LINGER,500)
zmq_socket_3.setsockopt(zmq.SNDTIMEO,1000)
zmq_socket_3.bind("tcp://*:%s" % port[3]) '''


#if len(sys.argv) > 1:
#	port =  sys.argv[1]
#	int(port)

#context = zmq.Context()
#zmq_socket = context.socket(zmq.PUB)
#zmq_socket.bind("tcp://*:%s" % port)

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

def sql_check_table(table_name):

	print('\nSELECT EXISTS TABLE IN DATABASE: %s \n' % table_name)

	table_exists = False

	try:

		db_connect = psycopg2.connect(DB_URI_STR)

		db_cursor = db_connect.cursor(cursor_factory=DictCursor)

		db_cursor.execute("SELECT EXISTS(SELECT * FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '" + table_name + "');")

		table_exists = db_cursor.fetchall()[0]['exists']

		print('table_exists',table_exists)

		db_connect.commit()

		db_cursor.close()

		db_connect.close()

	except Exception as error:

		if db_connect:
			
			db_connect.rollback()

		print("\n Error", error)

	return table_exists

def sql_create_table(table_name):

	try:

		db_connect = psycopg2.connect(DB_URI_STR)

		db_cursor = db_connect.cursor(cursor_factory=DictCursor)

		db_cursor.execute("CREATE TABLE " + table_name + "(place VARCHAR(255) NOT NULL, meter VARCHAR(255) NOT NULL, feature VARCHAR(255) NOT NULL, PRIMARY KEY (place, meter, feature));")

		db_connect.commit()

		db_cursor.close()

		db_connect.close()

	except Exception as error:

		if db_connect:
			
			db_connect.rollback()

		print("\n Error", error)

	pass

def sql_select_devices(table_name):

	result_devices = None

	try:

		db_connect = psycopg2.connect(DB_URI_STR)

		db_cursor = db_connect.cursor(cursor_factory=RealDictCursor)

		db_cursor.execute("SELECT * FROM " + table_name + ";")

		result_devices = db_cursor.fetchall()

		print('result_devices',result_devices)

		db_connect.commit()

		db_cursor.close()

		db_connect.close()

	except Exception as error:

		if db_connect:
			
			db_connect.rollback()

		print("\n Error", error)

	return result_devices

def sql_insert_data(place, meter, feature, timestamp, data):

	print('\n\nsql_insert_data: ', timestamp, data)

	try:
		# TODO: DO NOT ACCEPT NAN VALUES FOR DATA

		''' UNIX SECONDS TO DATETIME '''

		utc_dt = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds = timestamp)

		print('utc_dt: %s' % utc_dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

		timestamp_datetime = utc_dt.strftime('%Y-%m-%d %H:%M:%S')

		#print('timestamp_datetime: %s type: %s' % (timestamp_datetime, type(timestamp_datetime)))

		''' DATABASE '''

		db_connect = psycopg2.connect(DB_URI_STR)

		db_cursor = db_connect.cursor(cursor_factory=DictCursor)

		table = 'input_dataset'

		columns = 'timestamp, place, meter, feature, value'

		db_cursor.execute("INSERT INTO " + table + "(" + columns + ") VALUES (%s, %s, %s, %s, %s);" , (timestamp_datetime,place,meter,feature,data))

		print("INSERT INTO " + table + "(" + columns + ") VALUES (%s, %s, %s, %s, %s);" % (timestamp_datetime,place,meter,feature,data))

		db_connect.commit()

		db_cursor.close()

		db_connect.close()

	except Exception as error:

		print("\nException: ", error, timestamp, data)

	pass


def sql_insert_device(table_name, device_dict):

	try:

		db_connect = psycopg2.connect(DB_URI_STR)

		db_cursor = db_connect.cursor(cursor_factory=DictCursor)

		db_cursor.execute("INSERT INTO " + table_name + "(place, meter, feature) VALUES (%s, %s, %s);" , (device_dict['PLACE'], device_dict['METER'], device_dict['FEATURE']))

		db_connect.commit()

		db_cursor.close()

		db_connect.close()

	except Exception as error:

		if db_connect:
			
			db_connect.rollback()

		print("\n Error", error)

	pass


def prediction_interval_refresh(feature, timestamp, interval):

	#global prediction_interval_list

	prediction_interval_list = list()

	refresh_prediction = False

	feature_exists = False

	feature_dict = dict(FEATURE=feature, TIMESTAMP=timestamp)

	feature_table_result = None

	table_name = 'REFRESH_FEATURE'

	try:

		db_connect = psycopg2.connect(DB_URI_STR)

		db_cursor = db_connect.cursor(cursor_factory=RealDictCursor)

		db_cursor.execute("SELECT * FROM " + table_name + ";")

		feature_table_result = db_cursor.fetchall()

		print('feature_table_result', feature_table_result)

		db_connect.commit()

		db_cursor.close()

		db_connect.close()

		if feature_table_result != None:

			for feature_result in feature_table_result:

				print('feature_result', feature_result)

				feature_dict_real = dict(FEATURE=feature_result['feature'], TIMESTAMP=feature_result['timestamp'])

				prediction_interval_list.append(feature_dict_real)

	except Exception as error:

		print("\n Error", error)

		db_connect.commit()

		db_cursor.close()

		db_connect.close()

		return refresh_prediction

	if len(prediction_interval_list) > 0:

		for index, feature_temp_dict in enumerate(prediction_interval_list):

			print('feature_temp_dict', feature_temp_dict)

			if feature_temp_dict['FEATURE'] == feature_dict['FEATURE']:

				feature_exists = True

				print('feature_dict', feature_dict, feature_exists)

				temp_timestamp = (int(feature_temp_dict['TIMESTAMP']) + interval)

				print('timestamp > temp_timestamp',timestamp, temp_timestamp)

				if timestamp > temp_timestamp:

					refresh_prediction = True

					print('prediction_interval_list refresh', prediction_interval_list[index])

					try:

						table_name = 'REFRESH_FEATURE'

						if feature_dict['TIMESTAMP'] != None:

							timestamp_str = str(feature_dict['TIMESTAMP'])

							feature_str = feature_dict['FEATURE']

							db_connect = psycopg2.connect(DB_URI_STR)

							db_cursor = db_connect.cursor(cursor_factory=DictCursor)

							update_sql_str = "UPDATE " + table_name + " SET timestamp = " + timestamp_str + " WHERE feature = " + "'" + feature_str + "'" + ";"

							print('update_sql_str', update_sql_str)

							db_cursor.execute(update_sql_str)

							db_connect.commit()

							db_cursor.close()

							db_connect.close()

					except Exception as error:

						print("\n ERROR: ", error)

						db_connect.commit()

						db_cursor.close()

						db_connect.close()

				break

	if feature_exists == False or len(prediction_interval_list) == 0:

		print('prediction_interval_list.append', feature_dict)

		try:

			table_name = 'REFRESH_FEATURE'

			db_connect = psycopg2.connect(DB_URI_STR)

			db_cursor = db_connect.cursor(cursor_factory=DictCursor)

			db_cursor.execute("INSERT INTO " + table_name + "(feature, timestamp) VALUES (%s, %s);" , (feature_dict['FEATURE'], feature_dict['TIMESTAMP']))

			db_connect.commit()

			db_cursor.close()

			db_connect.close()

		except Exception as error:

			print("\n ERROR: ", error)

			db_connect.commit()

			db_cursor.close()

			db_connect.close()

		refresh_prediction = True

	return refresh_prediction


def check_devices_list(place, meter, feature):

	global DEVICES_TABLE_NAME

	#print('check_devices_list', DEVICES_TABLE_NAME, place, meter, feature)

	#devices_dict_list = sql_select_devices(DEVICES_TABLE_NAME)

	devices_real_dict_row = sql_select_devices(DEVICES_TABLE_NAME)

	#print('devices_real_dict_row', devices_real_dict_row)

	devices_dict_list = list()

	if devices_real_dict_row != None:

		for device in devices_real_dict_row:

			device_dict_real = dict(PLACE=device['place'], METER=device['meter'], FEATURE=device['feature'])

			devices_dict_list.append(device_dict_real)

	#print('devices_dict_list', devices_dict_list)

	device_dict = dict(PLACE=place, METER=meter, FEATURE=feature)

	device_exists = False

	if len(devices_dict_list) > 0:

		for device in devices_dict_list:

			#print('device', device)

			if device_dict['PLACE'] == device['PLACE'] and device_dict['METER'] == device['METER'] and device_dict['FEATURE'] == device['FEATURE']:

				device_exists = True

				#print('device_dict', device_dict, device_exists)

				break

	if device_exists == False or len(devices_dict_list) == 0:

		print('sql_insert_device', device_dict)

		#DEVICES_DICT_LIST.append(dict(device_dict))

		#devices_dict_list.append(device_dict)

		sql_insert_device(DEVICES_TABLE_NAME, device_dict)
	
	pass

#def publish_input_dataset(input_dataset, place, meter, feature, port):
def publish_input_dataset(input_dataset, feature, zmq_socket_index):

	print('\npublish_input_dataset', zmq_socket_index)

	''' global zmq_socket_0
	global zmq_socket_1
	global zmq_socket_2
	global zmq_socket_3 '''


	#global PLACE
	#global METER
	#global FEATURE
	global MIN_INPUT_LIST_LENGTH

	if len(input_dataset) < MIN_INPUT_LIST_LENGTH:
		print('INPUT_LIST_LENGTH: %d' % len(input_dataset))
	else:
		#port = "5556"
		''' context = zmq.Context()
		zmq_socket = context.socket(zmq.PUSH)
		zmq_socket.setsockopt(zmq.LINGER,500)
		zmq_socket.setsockopt(zmq.SNDTIMEO,1000)
		zmq_socket.bind("tcp://*:%s" % port) '''

		#print("port: %s" % port)

		print("\n\n\npublish_input_dataset: %s" % input_dataset)

		input_dataset_list = list()

		for index, field in enumerate(input_dataset):

			#print('field:',field[0])

			timestamp_str = str(field[0])

			temp = list(input_dataset[index])

			temp[0] = timestamp_str
			
			input_dataset[index] = tuple(temp)

		#input_dataset_json = json.dumps([{"TIMESTAMP": field[0], "VALUE": field[1]} for field in input_dataset])

		input_dataset_dict = ([{"TIMESTAMP": field[0], "VALUE": field[1]} for field in input_dataset])

		#topic = 'DATASET'
			
		message_dict = {}

		#message_dict.update({'PLACE': place, 'METER' : meter, 'FEATURE' : feature, 'INPUT_LIST' : input_dataset_dict})

		message_dict.update({'FEATURE' : feature, 'INPUT_LIST' : input_dataset_dict})

		#message_json = json.dumps(message_dict)

		#print('\n\njson',message_json)

		
		#socket.setsockopt('topic',topic)
		
		#socket.send_string("%s %s" % (topic, message_dict))

		print('\n\nmessage_dict', message_dict)

		print('\nzmq_socket_index', zmq_socket_index)

		try:

			context = zmq.Context()
			zmq_socket = context.socket(zmq.PUSH)
			zmq_socket.setsockopt(zmq.LINGER,500)
			zmq_socket.setsockopt(zmq.SNDTIMEO,1000)

			port = [5548,5549,5550,5551]

			if zmq_socket_index == 0:
				zmq_socket.bind("tcp://*:%s" % port[0]) 
			if zmq_socket_index == 1:
				zmq_socket.bind("tcp://*:%s" % port[1]) 
			if zmq_socket_index == 2:
				zmq_socket.bind("tcp://*:%s" % port[2]) 
			if zmq_socket_index == 3:
				zmq_socket.bind("tcp://*:%s" % port[3]) 

			''' if zmq_socket_index == 0:
				print('\nzmq_socket_0.send_json')
				zmq_socket_0.send_json(message_dict)
			if zmq_socket_index == 1:
				print('\nzmq_socket_1.send_json')
				zmq_socket_0.send_json(message_dict)
			if zmq_socket_index == 2:
				print('\nzmq_socket_2.send_json')
				zmq_socket_0.send_json(message_dict)
			if zmq_socket_index == 3:
				print('\nzmq_socket_3.send_json')
				zmq_socket_0.send_json(message_dict) '''

			zmq_socket.send_json(message_dict)

			zmq_socket.close()

		except zmq.ZMQError as error:

			print(error)

			zmq_socket.close()

	pass

''' def create_key(key, place, meter, feature):

	#global PLACE
	#global METER
	# FEATURE

	try:

		ts.create(key, retentionSecs=60*60*24*365*1, labels={'PLACE' : place, 'FEATURE' : feature, 'METER' : meter})

	except ResponseError as error:

		print("\n ERROR: %s\n" % error)
	pass
'''

def parse_key(place, meter, feature):

	#global PLACE
	#global METER
	#global FEATURE

	#print("\nparse_key")

	#print(" parse_key(timestamp: %s)" % (timestamp))

	key = None

	try:

		key = place + ':' + meter + ':' + feature # +  ':'

		#index = timestamp.find('T')

		#temp_timestamp = timestamp[0:index]

		#print(' temp_timestamp=%s' % (temp_timestamp))

		#key = key + temp_timestamp

		print('\nkey=%s' % (key))

	except Exception as error:

		print("\n Error", error)

	return key




def store_data_redis(key, timestamp, input_value):
#def store_data_redis(key, timestamp, input_value, place, meter, feature):

	#global PLACE
	#global METER
	#global FEATURE

	#global db_cursor
	#global db_connect

	print('\nRedisTimeSeries: ', key, timestamp, input_value)

	try:

		# TODO: DO NOT ACCEPT NAN VALUES FOR DATA

		#ts.add(key, timestamp, input_value, retentionSecs=60*60*24*5, labels={ 'PLACE' : place, 'METER' : meter, 'FEATURE' : feature })
		ts.add(key, timestamp, input_value, retentionSecs=60*60*24*5, labels={ 'FEATURE' : key })
		#ts.add(key, timestamp, input_value, labels={ 'FEATURE' : key })

		#db_connect = psycopg2.connect(DB_URI_STR)

		#db_cursor = db_connect.cursor(cursor_factory=DictCursor)

		# UNIX SECONDS TO DATETIME

		#utc_dt = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=timestamp)

		#print('utc_dt: %s' % utc_dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

		#timestamp_datetime = utc_dt.strftime('%Y-%m-%d %H:%M:%S')

		# DATETIME WITH LOCAL TIME
		# timestamp_datetime = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')

		#print('add_data into database timestamp_datetime: %s type: %s' % (timestamp_datetime, type(timestamp_datetime)))

		#table = 'input_dataset'

		#columns = 'timestamp, place, meter, feature, value'

		#data_float = float(data)

		#print('\ndata:',data,type(data))

		#print('DATABASE: %s %s %s %s %s' % timestamp_datetime,PLACE,METER,FEATURE,data)

		#statement = ('INSERT INTO ' + table + ' (' + columns + ') VALUES (' + %s, %s, %s, %s, %f + ');' % (timestamp_datetime,PLACE,METER,FEATURE,data_float))

		#statement = """INSERT INTO input_dataset(ts, place, meter, feature, value) VALUES (%s, %s, %s, %s, %f);""" % (timestamp_datetime,PLACE,METER,FEATURE,data_float)

		#"""INSERT INTO database (date, id) VALUES (now(), %s );""" % (user,)

		#print('\n\nstatement',statement)

		#db_cursor.execute("INSERT INTO input_dataset(ts, place, meter, feature, value) VALUES (to_timestamp(%s), %s, %s, %s, %s);" , (timestamp_datetime,PLACE,METER,FEATURE,data))

		#db_cursor.execute("INSERT INTO input_dataset(timestamp, place, meter, feature, value) VALUES (%s, %s, %s, %s, %s);" , (timestamp_datetime,PLACE,METER,FEATURE,data))

		#db_connect.commit()

		#db_cursor.close()

		#db_connect.close()

		ts.expire(key, 60*60*24*5)

	except ResponseError as error:

		print("\n Error", error, timestamp, input_value)

	pass

def convert_seconds(timestamp):

	datetime_seconds = 0

	print(' \nconvert_seconds: %s' % timestamp)

	try:

		# UNIX SECONDS (UTC)
		#utc_dt = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
		utc_dt = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

		#print(' dt.timetuple() ', dt.timetuple())
		#datetime_seconds = time.mktime(dt.timetuple())

		unix_seconds = (utc_dt - datetime.datetime(1970, 1, 1)).total_seconds()

		#print(' unix_seconds: %f' % unix_seconds)

	except Exception as error:

		print("\n ERROR: convert seconds: ", error)

	return unix_seconds

''' def get_key(key_order):

	print('get_key(%d)' % (key_order))

	key = None

	try:
		if len(keys_list) > 0:
			key = keys_list[len(keys_list) - key_order]
	except IndexError as error:
		print('ERROR: ', error)
	return key '''

def get_range(begin_time_range):

	datetime_seconds = begin_time_range

	begin_time = datetime_seconds

	begin_time_datetime = datetime.datetime.fromtimestamp(begin_time).strftime('%Y-%m-%d %H:%M:%S')

	#print(' begin_time: %d %s' % (begin_time,begin_time_datetime))

	end_time = int(time.time())

	end_time_datetime = datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')

	#print(' end_time: %d %s' % (end_time,end_time_datetime))

	return (begin_time, end_time)

#def select_input(input_stop, initial):
#def select_input(key, place, meter, feature, port):
def select_input(key, zmq_socket_index):

	feature = key

	print('\n\nselect_input', key, feature, zmq_socket_index)

	#TODO: ITERATE DEVICES LIST (DATABASE), PLACE, METER AND FEATURE, GET RELEVANT REDIS KEY CORRESPONDING TO QUERY

	#global INPUT_LIST

	INPUT_LIST = list()

	redis_list = list()

	INTERVAL = 60*60*24*4

	''' The last key in the key list '''
	#key = get_key(1)

	print("\n\nkey=%s" % key)

	info = None

	end_time = None

	begin_time = None

	#if key != None and initial != True:
	if key != None:

		try:

			info = ts.info(key)

		except ResponseError as error:

			print("\n\nError", error)


		#print('\nTimeseries info\n',info)

		#variables = info.__dict__.keys()

		#print('variables',variables)

		#methods = dir(info)

		#print('methods',methods)

		print('\ninfo', info)

		if info != None:

			end_time = info.__dict__['lastTimeStamp']

			#print('Algorithm of end_time: %d' % end_time)

			''' The timeseries range from the last 4 days. '''
			begin_time = end_time - INTERVAL

		#print('\nAlgorithm of begin_time: %d' % begin_time)

		#print('\nQuery timeseries begin_time: %d end_time: %d' % (begin_time,end_time))

		if begin_time != None and end_time != None:

			try:

				#print('\n\nINPUT DATASET:\n')

				for record in ts.range(key, begin_time, end_time, bucketSizeSeconds = 1):

					redis_list.append(record)

					#print('\nrecord:',record)

			except ResponseError as error:

				print("\nError", error)

		''' The input features are T-1 to T-8, T-96, T-192, T-288'''
		length = len(redis_list)

		print('\nThe length of redis_list: %d' % length)

		''' T-1 to T-8 '''
		sample_size = 8

		if length < sample_size:

			sample_size = length

		for i in range(sample_size):

			INPUT_LIST.append(redis_list[length-1-i])

			print('T-%d %s' % (i+1,INPUT_LIST[i]))

		''' T-96 '''

		''' if length > 96:

			print('\nThe length of redis_list > 96 %d' % length)

			INPUT_LIST.append(redis_list[length-96-1])

			print('\n\nT-96',redis_list[length-96-1])
		elif length > sample_size + 1 or length == sample_size + 1:

			print('\nThe length of redis_list >= sample_size + 1 %d' % length)

			INPUT_LIST.append(redis_list[length-1-i-1])

			print('T-%d %s' % (i+2,INPUT_LIST[i+1]))

			if length > sample_size + 2 or length == sample_size + 2:

				print('\nThe length of redis_list >= sample_size + 2 %d' % length)

				INPUT_LIST.append(redis_list[length-1-i-2])

				print('T-%d %s' % (i+3,INPUT_LIST[i+2]))

			if length > sample_size + 3 or length == sample_size + 3:

				print('\nThe length of redis_list >= sample_size + 3 %d' % length)

				INPUT_LIST.append(redis_list[length-1-i-3])

				print('T-%d %s' % (i+4,INPUT_LIST[i+3])) '''

		''' T-192 '''

		''' if length > 192:

			INPUT_LIST.append(redis_list[length-192-1])

			print('\n\nT-192',redis_list[length-192-1])

		elif length > 96:

			temp_record = INPUT_LIST.pop(8)

			#print('temp_record:', temp_record)

			INPUT_LIST.append(redis_list[length-1-i-2])

			#print('append:', redis_list[length-1-i-2])

			print('T-%d %s' % (i+2,INPUT_LIST[i+1]))

			INPUT_LIST.append(redis_list[length-1-i-3])

			print('T-%d %s' % (i+3,INPUT_LIST[i+2]))

			INPUT_LIST.append(temp_record)

			print('T-%d %s' % (i+4,INPUT_LIST[i+3])) '''

		''' T-288 '''

		''' if length > 288:

			INPUT_LIST.append(redis_list[length-288-1])

			print('\n\nT-288',redis_list[length-288-1])

		elif length > 96 and length > 192:

			temp_record_9 = INPUT_LIST[9]

			INPUT_LIST.pop(9)

			temp_record_8 = INPUT_LIST[8]

			INPUT_LIST.pop(8)
			
			INPUT_LIST.append(redis_list[length-1-i-3])

			print('T-%d %s' % (i+2,INPUT_LIST[i+1]))

			INPUT_LIST.append(temp_record_8)

			print('T-%d %s' % (i+3,INPUT_LIST[i+2]))

			INPUT_LIST.append(temp_record_9)

			print('T-%d %s' % (i+4,INPUT_LIST[i+3])) '''

		''' INPUT DATASET HAS 11 TIMESTAMPS '''
		#print('\n\nINPUT_LIST:',INPUT_LIST)

		for field in INPUT_LIST:

			print(field[1])

		#publish_thread = threading.Thread(target=publish_input_dataset,args=(INPUT_LIST, place, meter, feature, port))

		#publish_thread = threading.Thread(target=publish_input_dataset,args=(INPUT_LIST, feature, port))

		publish_thread = threading.Thread(target=publish_input_dataset,args=(INPUT_LIST, feature, zmq_socket_index))

		publish_thread.start()

		#publish_input_dataset(INPUT_LIST, port)

	#if not input_stop.is_set():

		#threading.Timer(30, select_input, [input_stop,False]).start()
		#threading.Timer(15, select_input, [input_stop,False]).start()


''' def query(query_stop):

	print('query')

	# The last key in the key list
	key = get_key(1)

	print("key=%s" % key)

	if key != None:

		begin_time, end_time = get_range(1)

		print('begin_time: %d end_time: %d' % (begin_time,end_time))

		try:
			for record in ts.range(key,begin_time,end_time,bucketSizeSeconds=1):

				timestamp = datetime.datetime.fromtimestamp(record[0]).strftime('%Y-%m-%d %H:%M:%S')
				
				#print('type',type(record[1]))

				if type(record[1]) == str or type(record[1]) == unicode:
					#print('str')
					if sys.version_info < (3, 0):
						data = round(float(unicode(record[1]).encode('utf8')),2)
						print(' %s : %.2f ' % (timestamp, data))
					else:
						data = round(float(record[1]),2)
						print(' %s : %.2f ' % (timestamp, data))
				elif type(record[1]) == float:
					#print('float')
					data = round(record[1],2)
					print(' %s : %.2f ' % (timestamp, data))
				else:
					print('The query did not get data.')
		except ResponseError:
			print("\n ERROR: query key")

	if not query_stop.is_set():
		threading.Timer(30, query, [query_stop]).start()
'''

def update_keys_24_hours(update_stop, initial):

	print('\n\nupdate_keys_24_hours\n\n')

	redis_list = list()

	for key in ts.keys('*'):

		print(' key=%s' % (key.decode('utf8')))

		#key = get_key(1)

		print("key=%s" % key)

		if key != None and initial != True:

			print('QUERY INFO OF KEYS')

			info = ts.info(key)

			print(info)

			place = info.labels['PLACE']

			print(place)

			meter = info.labels['METER']

			print(meter)

			feature = info.labels['FEATURE']

			print(feature)

			''' The most recent timestamp from Redis '''
			stop_time = info.__dict__['lastTimeStamp']

			''' The start timestamp where to copy timestamp to Redis '''
			start_time = stop_time - (60*60*24*4)

			print('\n\nCopy timestamps from start time: %d to stop time: %d' % (start_time,stop_time))

			try:
				for redis_record in ts.range(key,start_time,stop_time,bucketSizeSeconds=1):

					redis_list.append(redis_record)

					timestamp = datetime.datetime.fromtimestamp(redis_record[0]).strftime('%Y-%m-%d %H:%M:%S')
					
					#print('type',type(record[1]))

					if type(redis_record[1]) == str or type(redis_record[1]) == unicode:
						#print('str')
						if sys.version_info < (3, 0):
							data = round(float(unicode(redis_record[1]).encode('utf8')),2)
							print(' %s : %.2f ' % (timestamp, data))
						else:
							data = round(float(redis_record[1]),2)
							print(' %s : %.2f ' % (timestamp, data))
					elif type(redis_record[1]) == float:
						#print('float')
						data = round(redis_record[1],2)
						print(' %s : %.2f ' % (timestamp, data))
					else:
						print('The query did not get data.')

			except ResponseError as error:

				print("\n ERROR: %s" % error)

			try:

				ts.delete(key)

			except redis.exceptions.ResponseError:

				print("\n Error: delete key")

			print('UPDATE KEYS 24 HOURS')

			for index, redis_record in enumerate(redis_list):

				timestamp_str = datetime.datetime.fromtimestamp(redis_record[0]).strftime('%Y-%m-%d %H:%M:%S')

				print('timestamp_str: %s' % timestamp_str)

				timestamp = redis_record[0]

				try:

					if type(redis_record[1]) == str or type(redis_record[1]) == unicode:
						#print('str')
						if sys.version_info < (3, 0):
							data = round(float(unicode(redis_record[1]).encode('utf8')),2)
							ts.add(key, timestamp, data, retentionSecs=60*60*24*5, labels={ 'PLACE' : place, 'METER' : meter, 'FEATURE' : feature })
							print(' %s : %.2f ' % (timestamp, data))
						else:
							data = round(float(redis_record[1]),2)
							ts.add(key, timestamp, data, retentionSecs=60*60*24*5, labels={ 'PLACE' : place, 'METER' : meter, 'FEATURE' : feature })
							print(' %s : %.2f ' % (timestamp, data))
					elif type(redis_record[1]) == float:
						#print('float')
						data = round(redis_record[1],2)
						ts.add(key, timestamp, data, retentionSecs=60*60*24*5, labels={ 'PLACE' : place, 'METER' : meter, 'FEATURE' : feature })
						print(' %s : %.2f ' % (timestamp, data))
					else:
						print('The query did not get data.')

					print('The key added: ', key, timestamp)

				except ResponseError as error:

					print("\n ERROR: %s : %d : %s\n" % (error, timestamp, data))

	print('SET TIMER 24 HOURS:')

	if not update_stop.is_set():
		threading.Timer(60*60*24*5, update_keys_24_hours, [update_stop,False]).start()

	pass

@child_process
def process_received_message(message):

	print('\nprocess_received_message')

	#global VALUE_KEY
	#global PLACE
	#global METER
	#global FEATURE

	feature_key = None

	#temp_dict = json.loads(message.payload)

	print("\ntopic",message.topic)

	temp_timestamp = None

	temp_float = None

	if message.topic == TOPIC:

		#print("\npayload:",message.payload)

		payload_str = message.payload.decode("utf-8")

		#print("\npayload_str",payload_str)

		#print("\npayload_str type",type(payload_str))

		#payload_dumps = json.dumps(payload_str)

		#print('\npayload_dumps type',type(payload_dumps))

		#print('\npayload_dumps',payload_dumps)

		if(payload_str != IGNORE_PAYLOAD):

			payload_loads = None

			try:

				payload_loads = json.loads(str(payload_str))

			except Exception as error:

				print(error)

			list_length = len(FEATURE_KEY_LIST)

			index = 0

			#FEATURE_KEY_LIST = ['ai_cod1_cod', 'ai_ph1_temp', 'ai_ph1_ph', 'ai_ss1_ss']

			for index in range(list_length):

				print('\nFEATURE_KEY_LIST[index]', FEATURE_KEY_LIST[index])

				feature_key = None

				temp_timestamp = None

				temp_float = None

				try:

					#payload_loads = json.loads(str(payload_str))
					#print('\npayload_loads',payload_loads)
					print('\n"dataTime"', payload_loads["dataTime"])

					feature_key = FEATURE_KEY_LIST[index]

					print('\nFEATURE: %s VALUE: %s' % (feature_key, payload_loads[feature_key]))

					temp_timestamp = payload_loads["dataTime"]

					temp_float = payload_loads[feature_key]
			
				except Exception as error:

					feature_key = None

					print(error)

				#for key, value in payload_loads.items():
				#	print('\nkey:', key)
				#	print('\nvalue:', value)
				
				#print('\n"dataTime":', payload_dumps["dataTime"])
				#print('\nFEATURE_KEY_LIST[0]:', payload_loads["dataTime"])
				#for key, value in payload_loads.items():
					#print('\nkey:', key)
					#print('\nvalue:', value)
				#print('\nFEATURE_KEY_LIST[0]:', payload_loads[FEATURE_KEY_LIST[0]])

				#print("\ntemp_dict",temp_dict)

				#payload_json = json.dumps(payload_str)

				#print('\npayload_json',payload_json)

				#print('\npayload_0',payload_json[0])

				#temp_dict = str(message)

				#temp_dict = json.loads(str(message))

				#temp_obj = json.loads(message.decode("utf-8"))

				#print('\ntemp_obj',temp_obj)

				#temp_dict = temp_obj

				#temp_dict = str(message.payload.decode("utf-8"))

				#temp_msg = temp_dict['clientOffline']

				#temp_msg = temp_dict[0]

				#print('\ntemp_msg',temp_msg)

				#received = message.payload.decode("utf-8","ignore")

				#received = json.loads(received)

				
				#print('\nreceived', received)

				#temp_msg = temp_dict['MESSAGE']

				#TODO: ITERATE FEATURE KEY LIST AND GET FEATURE VALUES

				#temp_timestamp = temp_msg[TIMESTAMP_KEY]

				#temp_timestamp = temp_dict[TIMESTAMP_KEY]

				#temp_float = temp_msg[VALUE_KEY]
				#feature = FEATURE_KEY_LIST[0]

				#print('FEATURE: %s' % FEATURE_KEY_LIST[0])

				#temp_float = temp_dict[feature]

				#print(TIMESTAMP_KEY,temp_timestamp)

				#print('temp_timestamp type: %s' % type(temp_timestamp))

				#print(feature,temp_float)

				#place = temp_msg['PLACE']

				#print('PLACE: %s' % place)

				#meter = temp_msg['METER']

				#print('METER: %s' % meter)

				#feature = temp_msg['FEATURE']

				
				#if place != None and meter != None and feature != None:

				if feature_key != None:

					#key = parse_key(place,meter,feature)

					print('\nkey',feature_key)

					print('\ntimestamp convert_seconds: %s' % temp_timestamp)

					timestamp_seconds = int(convert_seconds(temp_timestamp))

					print('\ntimestamp_seconds', timestamp_seconds)

					value_str = str(temp_float)

					#print('thread_redis')

					refresh_feature = False

					if feature_key != None:

						#redis_thread = threading.Thread(target=store_data_redis, args=(key, timestamp_seconds, value_str, place, meter, feature))

						redis_thread = threading.Thread(target=store_data_redis, args=(feature_key, timestamp_seconds, value_str))

						redis_thread.start()

						#store_data_redis(feature_key,timestamp_seconds,value_str)

						#print('thread: select_input')

						#select_input_thread = threading.Timer(0, select_input, [key, place, meter, feature, port])

						REFRESH_INTERVAL_SECONDS = 1

						#refresh_feature = prediction_interval_refresh(feature_key, timestamp_seconds, REFRESH_INTERVAL_SECONDS)

						refresh_feature = True

						print('\nrefresh_feature',refresh_feature)

						#FEATURE_KEY_LIST = ['ai_cod1_cod', 'ai_ph1_temp', 'ai_ph1_ph', 'ai_ss1_ss']

						if refresh_feature == True:

							print('\nFEATURE_KEY_LIST[index]',FEATURE_KEY_LIST[index], index)

							#[5548,5549,5550,5551]

							select_input_thread = threading.Timer(0, select_input, [feature_key, index])
							print('\nindex', index)
							select_input_thread.start()

							'''if index == 0:
								select_input_thread = threading.Timer(0, select_input, [feature_key, index])
								print('\nindex', index)
								select_input_thread.start()
							if index == 1:
								select_input_thread = threading.Timer(0, select_input, [feature_key, index])
								print('\nindex', index)
								select_input_thread.start()
							if index == 2:
								select_input_thread = threading.Timer(0, select_input, [feature_key, index])
								print('\nindex', index)
								select_input_thread.start()
							if index == 3:
								select_input_thread = threading.Timer(0, select_input, [feature_key, index])
								print('\nindex', index)
								select_input_thread.start() '''

							index = index + 1

				#select_input_thread.start()

				#print('thread: sql_insert_data')

				#sql_insert_data_thread = threading.Timer(0, sql_insert_data, [place, meter, feature, timestamp_seconds,value_str])

				#sql_insert_data_thread = threading.Timer(0, sql_insert_data, [place, meter, feature, timestamp_seconds,value_str])

				#sql_insert_data_thread.start()

				#sql_insert_data_thread.start()

				#threading.Timer(0, check_devices_list, []).start()

			''' check iot exists on devices list '''
			#devices_thread = threading.Thread(target=check_devices_list, args=(place, meter, feature))

			#devices_thread.start()

	pass

def on_connect(client, data, flags, result):

	if result == 0:

		print("on_connect: ", str(result))

		client.subscribe(TOPIC)

	else:

		print("Error on_connect: ", str(result))

	pass

def on_subscribe(client, obj, result, qos):

    print("on_subscribe: ", str(result))

def on_log(client, data, level, buf):

	print("on_log: ", buf)

	pass

def on_message(client, data, message):

	print('\non_message')

	''' global TIMESTAMP_KEY
	global VALUE_KEY
	global PLACE
	global METER
	global FEATURE '''
	#global DEVICES_DICT_LIST

	'''global zmq_socket_0
	global zmq_socket_1
	global zmq_socket_2
	global zmq_socket_3

	print('zmq_socket_0', zmq_socket_0)
	print('zmq_socket_1', zmq_socket_1)
	print('zmq_socket_2', zmq_socket_2)
	print('zmq_socket_3', zmq_socket_3) '''

	#global toggle

	#global gpu

	#gpu ^= 1

	#port_toggle = next(toggle)

	#port_toggle = 0

	

	#gpu ^= 1

	'''if gpu == 0:
		port = "5555"

	if gpu == 1:
		port = "5556" '''

	''' if port_toggle == 0:
		port = "5555"

	if port_toggle == 1:
		port = "5556"

	if port_toggle == 2:
		port = "5552"

	if port_toggle == 3:
		port = "5553" '''


	print("\n\non_message: ", message.topic, str(message))

	if message.topic == TOPIC:

		process_received_message(message)

		#time.sleep(1)

		#print("message.payload: ", str(message.payload.decode("utf-8")))

		''' temp_dict = json.loads(message.payload)

		temp_msg = temp_dict['MESSAGE']

		temp_timestamp = temp_msg[TIMESTAMP_KEY]

		temp_float = temp_msg[VALUE_KEY]

		print(TIMESTAMP_KEY,temp_timestamp)

		print('temp_timestamp type: %s' % type(temp_timestamp))

		print(VALUE_KEY,temp_float)

		PLACE = temp_msg['PLACE']

		print('PLACE: %s' % PLACE)

		METER = temp_msg['METER']

		print('METER: %s' % METER)

		FEATURE = temp_msg['FEATURE']

		print('FEATURE: %s' % FEATURE) '''

		#data_dict = { 'DATA' : { "x" : temp_timestamp , "y" : str(temp_float) } }

		#data_json = json.dumps(data_dict)

		#print(data_json)

		#key = parse_key(temp_timestamp)

		''' key = parse_key()

		print('\nkey',key) '''

		# keys_list.append(key)

		# print('\nkeys_list: ',keys_list)

		''' print('\non_message convert_seconds: %s' % temp_timestamp)

		timestamp_seconds = int(convert_seconds(temp_timestamp))

		print('\ntimestamp_seconds: %s' % timestamp_seconds)

		value_str = str(temp_float)

		store_data_redis(key,timestamp_seconds,value_str)

		threading.Timer(0, select_input, [key]).start()

		threading.Timer(0, sql_insert_data, [timestamp_seconds,value_str]).start()

		threading.Timer(0, check_devices_list, []).start() '''

		#sql_insert_data(timestamp_seconds,value_str)

		#ts.expire(key, 60*60*24*5) '''

		''' if device_exists == False:

			print('DEVICES_DICT_LIST.append(%s)' % (device_dict))

			#DEVICES_DICT_LIST.append(dict(device_dict))

			DEVICES_DICT_LIST.append(device_dict)

			table_name = 'devices'
			sql_insert_device(table_name,device_dict) '''

	pass

''' main program '''

#port = [5548,5549,5550,5551]

try:

	db_connect = psycopg2.connect(DB_URI_STR)

	db_cursor = db_connect.cursor(cursor_factory=DictCursor)

	table_name = 'REFRESH_FEATURE'

	db_cursor.execute("CREATE TABLE " + table_name + "(feature VARCHAR(255) NOT NULL, timestamp VARCHAR(255) NOT NULL, PRIMARY KEY (feature));")

	db_connect.commit()

	db_cursor.close()

	db_connect.close()

except Exception as error:

	if db_connect:

		db_connect.rollback()

	print("\n Error", error)

print('\n '.join(sys.path))

#table_exists = sql_check_table(DEVICES_TABLE_NAME)

#print('table_exists', table_exists)

#if table_exists == False:
#	print('CREATE TABLE: ' + DEVICES_TABLE_NAME)
#	sql_create_table(DEVICES_TABLE_NAME)

''' table_name = 'devices'

table_exists = sql_check_table(table_name)

if table_exists == False:
	print('CREATE TABLE: ' + table_name)
	sql_create_table(table_name)
else:
	result_devices = sql_select_devices(table_name)
	for device in result_devices:
		DEVICES_DICT_LIST.append(dict(PLACE=device['place'],METER=device['meter'],FEATURE=device['feature']))
		print('device',device['place'],device['meter'],device['feature']) '''

#ts = RedisTimeSeries(host='localhost',port=6379)

ts = RedisTimeSeries(host='127.0.0.1',port=6379)

#ts.flushdb()

# keys_list = list()

#client = mqtt.Client("iot-script")

client = mqtt.Client("water-script")

#client.username_pw_set(user,password=password)

client.on_connect = on_connect

client.on_subscribe = on_subscribe

client.on_message = on_message

client.on_log = on_log

#client.connect("192.168.3.2",1883,60)

client.connect("114.55.211.112",1883,60)

#query_stop = threading.Event()

# start calling query now and every 60 seconds
#query(query_stop)

#input_stop = threading.Event()

#select_input(input_stop,True)

# stop the thread when needed
#query_stop.set()

#client.loop_start()

update_stop  = threading.Event()

print('UPDATE_KEYS_24_HOURS')

#update_keys_24_hours(update_stop,True)

#print('CONNECT DATABASE')

#db_uri = "postgres://demo:demo@192.168.3.2:5432/demo?sslmode=require"

#db_connect = psycopg2.connect(db_uri)

#print(db_connect)

#db_cursor = db_connect.cursor(cursor_factory=DictCursor)

#db_cursor.execute("SELECT * FROM input_dataset;")

#result_input_dataset = db_cursor.fetchone()

#db_cursor.close()

#print(result_input_dataset)

print('loop_forever')

client.loop_forever()


#client.loop_forever()

#client.connect("192.168.3.2", 1883, 60)

#client.subscribe(topic)

#client.subscribe([("iot", 0), ("demo", 0)])

#print("SUBSCRIBE: " + topic)

#client.loop_forever()

#try:
	#while True:
		#time.sleep(1)

if __name__ == "__main__":
	print("Python script: %s" % time.ctime())
	main(sys.argv[1:])
