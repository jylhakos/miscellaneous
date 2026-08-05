# !/usr/bin/python3
# $ pip3 install psycopg2

import sys
import getopt
import time
import os
import datetime
import json
import numpy as np

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

import zmq

#from psycopg2.extras import RealDictCursor
#import psycopg2

from multiprocessing import Pipe
from multiprocessing import Process
from multiprocessing import current_process

#import GPUtil

#from keras.utils import multi_gpu_model

from tensorflow.python.framework.errors_impl import ResourceExhaustedError, UnknownError

import keras.backend as K
import tensorflow as tf
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM

from psycopg2.extras import RealDictCursor
from psycopg2.extras import DictCursor
import psycopg2

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

global model_is_loaded
model_is_loaded = False

global model
model = None

#tf.logging.set_verbosity(tf.logging.WARN)

''' model = None
graph = None
session = None

num_cores = 8

GPU = True
CPU = False
num_CPU = 1
num_GPU = 0

if GPU:
	num_GPU = 2
	num_CPU = 1

if CPU:
	num_CPU = 1
	num_GPU = 0

gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction = 0.50, allow_growth = True)

config = tf.ConfigProto(intra_op_parallelism_threads = num_cores,
	inter_op_parallelism_threads = num_cores,
	allow_soft_placement = True,
	device_count = {'CPU' : num_CPU, 'GPU' : num_GPU},
	gpu_options = gpu_options)

print('\n\ngpu', str(gpu))

os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu)

session = tf.compat.v1.Session(config=config)

K.set_session(session) '''

#import logging

#logging.getLogger('tensorflow').disabled = True

#os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

#global db_cursor
#global db_connect

#user = "iot"
#password = "iot"
#topic = "iot"

''' constants '''

MODEL_FOLDER = "MODEL"

num_day = 1/12
horizon = 1
time_window = int(num_day * 4 * 24)

''' decorator pattern for processes '''

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

''' zmq pull settings '''

def zmq_input_settings():
	print('\nzmq_input_settings()')
	#port_iot_pull = "5555"
	port_iot_pull = "5551"
	zmq_context = zmq.Context()
	zmq_socket_pull = zmq_context.socket(zmq.PULL)
	zmq_socket_pull.connect("tcp://localhost:%s" % port_iot_pull)
	#print("port_iot_pull: %s" % port_iot_pull)
	return zmq_socket_pull

zmq_socket_pull = zmq_input_settings()

''' zqm push settings '''

def zmq_output_settings():
	port_iot_push = "5564"
	zmq_context_push = zmq.Context()
	zmq_socket_push = zmq_context_push.socket(zmq.PUSH)
	zmq_socket_push.setsockopt(zmq.LINGER,1000)
	zmq_socket_push.setsockopt(zmq.SNDTIMEO,5000)
	zmq_socket_push.bind("tcp://*:%s" % port_iot_push)
	#print("port_iot_push: %s" % port_iot_push)
	return zmq_socket_push

''' output from predict '''

def send_output(timestamp, feature, predicted):

	print('\nsend_output', timestamp, feature, predicted)

	zmq_socket_push = zmq_output_settings()

	message_dict = {}

	message_dict.update({'TIMESTAMP' : timestamp, 'FEATURE' : feature,  'PREDICTED' : predicted })

	try:

		zmq_socket_push.send_json(message_dict)

	except zmq.ZMQError as error:

		print(error)

	pass


''' machine learning errors '''

def rmse(real, predict):
    error = np.square(real - predict)
    return np.average(error) ** 0.5

def mape(real, predict):
    error = np.abs(real - predict)
    return np.average([error[i] / real[i] for i in range(error.shape[0])])

def mae(real, predict):
    error = np.abs(real - predict)
    return np.average(error)

def tilted_loss(q,y,f):
    e = (y-f)
    return K.mean(K.maximum(q*e, (q-1)*e), axis=-1)

''' dataset functions '''

''' def find_feature(place, meter, feature):

	COLUMN = 0
	SPLIT = 0

	feature_files = list()
	feature_dir = ""
	feature_string = None
	model_path = None

	#print("find_feature: ", place, meter, feature)

	if(place == "MSB"):
		SPLIT = 13
		sys.path.append(MODEL_FOLDER + "/" + place + "/")
		feature_dir = MODEL_FOLDER + "/" + place + "/"

	if(place == "HVSB"):
		SPLIT = 18
		sys.path.append(MODEL_FOLDER + "/" + place + "/")
		feature_dir = MODEL_FOLDER + "/" + place + "/"


	#print("feature_dir: ", feature_dir)

	for (dirpath, dirnames, filenames) in os.walk(feature_dir):
		feature_files  += [os.path.join(dirpath, file) for file in filenames]

	#print("feature_files: %s " % feature_files)

	length = len(feature_files)

	#if length > 0:
		#print('feature_files[0]',feature_files[0])

	if(feature == "voltage_B"):
		feature_string = meter[0:SPLIT] + "_" + "Vlnavg"
		COLUMN = 1
		try:
			model_path = os.path.basename(feature_files[0])
			model_path = model_path[0:SPLIT]
		except Exception as error:
			print(error)

	if(feature == "voltage_D"):
		feature_string = meter[0:SPLIT] + "_" + "Vllavg"
		COLUMN = 3
		model_path = os.path.basename(feature_files[0])
		model_path = model_path[0:SPLIT]

	if(feature == "current"):
		feature_string = meter[0:SPLIT] + "_" + "lavg"
		COLUMN = 5
		model_path = os.path.basename(feature_files[0])
		model_path = model_path[0:SPLIT]

	if(feature == "power"):
		feature_string = meter[0:SPLIT] + "_" + "KW"
		COLUMN = 7
		model_path = os.path.basename(feature_files[0])
		model_path = model_path[0:SPLIT]

	#print("feature_string: %s" % feature_string)

	print("\nmodel: ", model_path)

	return model_path, feature_string '''

''' def select_place(place, meter):

    #print('select_place: ', place, meter)

    list_files = list()

    dir_name = ""

    SPLIT = 0

    if(place == "MSB"):
        SPLIT = 13
        #sys.path.append("../MSB/" + meter[0:SPLIT])
        dir_name = MODEL_FOLDER  + "/" + "MSB" + "/"
        #dir_name = "../MSB/" + meter[0:SPLIT]

    if(place == "HVSB"):
        SPLIT = 18
        #sys.path.append("../HVSB/" + meter[0:SPLIT])
        dir_name = MODEL_FOLDER  + "/" + "HVSB"  + "/"
        #dir_name = "../HVSB/" + meter[0:SPLIT]
        #print('dir_name: ', dir_name)

    for (dirpath, dirnames, filenames) in os.walk(dir_name):
        list_files  += [os.path.join(dirpath, file) for file in filenames]

    list_files.sort()

    #print("list_files" + str(list_files))

    return list_files '''


''' def select_meter(meter, list_files):

	#print('\nselect_meter', meter)

	#print('\nlist_files: ', list_files)

	#temp_meter_file = meter + ".xls"
	temp_file = ""

	for file_name_path in list_files:
		temp_file = os.path.basename(file_name_path)
		#print('temp_file',temp_file)
		if meter in temp_file:
			return True

	return False '''


''' machine learning algorithm '''

#def process_feature(place, meter, feature, ml_selection, feature_string, values_list, timestamp_seconds_interval, timestamp_seconds_next, gpu):
def process_feature(feature, values_list, timestamp_seconds_interval, timestamp_seconds_next, gpu):

	process_name = current_process().name

	print('\n\nprocess_feature', process_name)

	process_start_time = time.process_time()

	global model_is_loaded

	global model

	#model = None

	test_pred = None
	unscaled_test_y_history = list()
	unscaled_test_pred_history = list()

	''' import keras.backend as K
	import tensorflow as tf
	from keras.models import load_model
	from keras.models import Sequential
	from keras.layers import Dense
	from keras.layers import LSTM '''

	tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

	#tf.logging.set_verbosity(tf.logging.WARN)

	''' graph = None
	session = None

	num_cores = 8

	GPU = True
	CPU = False
	num_CPU = 1
	num_GPU = 0

	if GPU:
		num_GPU = 2
		num_CPU = 1

	if CPU:
		num_CPU = 1
		num_GPU = 0

	gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction = 0.50, allow_growth = True)

	config = tf.ConfigProto(intra_op_parallelism_threads = num_cores,
		inter_op_parallelism_threads = num_cores,
		allow_soft_placement = True,
		device_count = {'CPU' : num_CPU, 'GPU' : num_GPU},
		gpu_options = gpu_options)

	print('\n\ngpu', str(gpu))

	os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu)

	session = tf.compat.v1.Session(config=config)

	K.set_session(session) '''
	
	#print('\n\nsession', session)

	process_name = current_process().name

	#print('\nprocess_name', process_name)

	#data = np.array([[[test_x_float],[1],[1]]])

	'''

	data_list = np.array(data_list)
	print(data_list.shape)

	mms = MinMaxScaler()
	scaled_data = mms.fit_transform(data_list.reshape(-1, 1))
	scaled_data = scaled_data[:, 0]

	num_day = 1/12
	#预测步数
	horizon = 1
	time_window = int(num_day * 4 * 24)

	label_set = scaled_data[time_window + horizon - 1:]

	feature_set = np.zeros([scaled_data.shape[0] - time_window - horizon + 1, time_window])
	for sampleidx in range(scaled_data.shape[0] - time_window - horizon + 1):
	    feature_set[sampleidx, :] = scaled_data[sampleidx:sampleidx + time_window]

	    
	feature_set, label_set = drop_nan(feature_set, label_set)

	'''

	#numpy.ndarray dtype: float64
	data = np.array(values_list,dtype=np.float64)

	if len(data) > 8:
		#print('K.clear_session()')
		K.clear_session()
		#print('return')
		return None

	#print("\ndata: ", data)

	#print("\ntype: ", type(data))

	mms = MinMaxScaler()

	scaled_data = mms.fit_transform(data.reshape(-1, 1))

	scaled_data = scaled_data[:, 0]

	print("\nscaled_data",scaled_data)

	#label_set = scaled_data[10:]

	label_set = scaled_data[7:]

	print("\nlabel_set", label_set)

	#print("\nlabel_set.shape[0]", label_set.shape[0])

	#print(type(label_set))

	#print(label_set.shape)

	scaled_data = np.reshape(scaled_data,(1,scaled_data.shape[0], 1))

	print(scaled_data)

	''' Check shape of scaled_data '''
	
	print('\n\nscaled_data.shape:',scaled_data.shape)

	if scaled_data.shape[0] != 1 and scaled_data.shape[1] != 8 and scaled_data.shape[2] != 1:
		print('K.clear_session()')
		K.clear_session()
		#print('return')
		return None

	#model_path = MODEL_FOLDER + "/" + place + "/" + feature_string + ".h5"

	model_path = MODEL_FOLDER + "/" + feature + ".h5"

	print("\nmodel_path",model_path)

	if model_is_loaded == False:

		#print("\nmodel_path",model_path)

		del model

		print('\nload_model: %s' % model_path)

		try:

			model = load_model(model_path)

			model_is_loaded = True

		except (OSError) as error:

			print('\nError',error)

			K.clear_session()

			model = None

			model_is_loaded = False

	if model != None:

		try:

			K.get_session()

			#with tf.device('/gpu:' + str(gpu)):
			
			test_pred = model.predict(scaled_data)

		except (ResourceExhaustedError, UnknownError, ValueError) as error:

			print('\nError',error)

			#K.clear_session()

			model_is_loaded = False

		if test_pred != None:

			#print("test_pred:", test_pred)

			unscaled_test_pred = mms.inverse_transform(test_pred.reshape(-1, 1))

			#print("\nunscaled_test_pred: ", unscaled_test_pred)

			unscaled_test_y = mms.inverse_transform(label_set.reshape(-1, 1))

			#print("\nunscaled_test_y: ", unscaled_test_y)

			print("\nErrors:", rmse(unscaled_test_y, unscaled_test_pred), mae(unscaled_test_y, unscaled_test_pred), mape(unscaled_test_y, unscaled_test_pred))

			predicted_temp_float = None

			if len(unscaled_test_pred) > 0 and unscaled_test_pred[0] != None:

				float_value_list = unscaled_test_pred[0]

				predicted_temp_float = float_value_list[0]

				predicted_value_str = str(predicted_temp_float)

				print('\npredicted_float: %s' % predicted_value_str)

				#timestamp_seconds_interval = abs(timestamp_seconds_0 - timestamp_seconds_1)

				#print("timestamp_seconds_interval: %d" % timestamp_seconds_interval)

				#timestamp_seconds_next = timestamp_seconds_0 + timestamp_seconds_interval

				utc_dt_next = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=timestamp_seconds_next)

				print('\nutc_dt_next: %s' % utc_dt_next.strftime('%Y-%m-%d %H:%M:%S'))

				utc_dt_next_str = utc_dt_next.strftime('%Y-%m-%d %H:%M:%S')

				#transaction_with_db(utc_dt_next, place, meter, feature, predicted_value_str)

				send_output(utc_dt_next_str, feature, predicted_value_str)

				#print('\nclear_session()')

				#K.clear_session()

				#return predicted_temp_float

				process_end_time = time.process_time()

				process_time = process_end_time - process_start_time

				print('\n\n\nprocess_time: ', process_time)

	pass

''' process script '''

#@child_process
def serving_process(msg, gpu):

	print('serving_process')

	values_list = list()

	msg_str = msg.decode('utf-8')

	#print('\nmsg_str:',msg_str)

	#print('\nmsg_split type:', type(msg_str))

	temp_dict = json.loads(msg_str)

	#print('\n\ntemp_dict',temp_dict)

	#place = temp_dict["PLACE"]

	#print('\nplace',place)

	#meter = temp_dict["METER"]

	#print('\nmeter',meter)

	feature = temp_dict["FEATURE"]

	#print('\nfeature',feature)

	timestamp_seconds_0 = 0

	timestamp_seconds_1 = 0

	timestamp_seconds_interval = 0

	print('\n\nserving_process', feature)

	for (key, value) in temp_dict.items():

		print("key: " + key)
		#print("value: " + str(value))
		print("value: ", value)

		if key == 'INPUT_LIST':

			#print('\nvalue type:', type(value))

			#print('n',value)

			for index, field in enumerate(value):

				timestamp_seconds = int(field['TIMESTAMP'])

				timestamp_dateformat = datetime.datetime.fromtimestamp(timestamp_seconds).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

				row_split = timestamp_dateformat.split('.')

				#print("row_split",row_split[1].split(' '))

				micro_seconds = row_split[1].split('Z')

				#print("micro_seconds: ",micro_seconds[0])

				timestamp_dateformat_str = datetime.datetime.fromtimestamp(timestamp_seconds).strftime('%Y-%m-%dT%H:%M:%S')

				#print('timestamp_dateformat_str', timestamp_dateformat_str)

				datetime_str_ISO_8601 = "%s.%03dZ" % (timestamp_dateformat_str, int(micro_seconds[0]) / 1000)

				timestamp_dateformat_ISO_8601 = "%s.%03dZ" % (timestamp_dateformat_str, int(micro_seconds[0]) / 1000)

				#print('%d TIMESTAMP_ISO_8601: %s %s' % (index, field['TIMESTAMP'], timestamp_dateformat_ISO_8601))

				field_value_float = round(float(field['VALUE']),2)

				#print('%d VALUE: %s is float: %f' % (index, field['VALUE'], field_value_float))

				values_list.append(field_value_float)

				#update_values(field_value_float)

				if index == 0:

					timestamp_seconds_0 = timestamp_seconds

				elif index == 1:

					timestamp_seconds_1 = timestamp_seconds

	#print("select_place(%s,%s)" % (place,meter))

	#list_files = select_place(place,meter)

	#print("find_feature(%s,%s,%s)" % (place,meter,feature))

	#feature_model, feature_string = find_feature(place,meter,feature)

	#feature_model = 'ai_cod2_cod'

	#feature_string = 'ai_cod2_cod.h5'

	#print("feature_model: %s, feature_string: %s" % (feature_model,feature_string))

	#print("select_meter(%s)" % meter)

	#meter_belongs_place = select_meter(meter,list_files)

	#print("meter_belongs_place: %s" % meter_belongs_place)

	timestamp_seconds_interval = abs(timestamp_seconds_0 - timestamp_seconds_1)

	timestamp_seconds_next = timestamp_seconds_0 + timestamp_seconds_interval

	#TODO: CHECK THERE IS MODEL FOR FEATURE
	meter_belongs_place = True

	if(meter_belongs_place):

		#print("\nprocess_feature\n")

		''' Check length of minimum array '''

		length = len(values_list)

		#if length > 10:
		if length > 7:

			#process_feature(place, meter, feature, feature_model, feature_string, values_list, timestamp_seconds_interval, timestamp_seconds_next, gpu)

			process_feature(feature, values_list, timestamp_seconds_interval, timestamp_seconds_next, gpu)

		else:

			print("Error: The length of values_list: %d" % length)


''' script loop '''
gpu = 1

#graph = None
session = None

num_cores = 8

GPU = True
CPU = False
num_CPU = 1
num_GPU = 0

if GPU:
	num_GPU = 2
	num_CPU = 1

if CPU:
	num_CPU = 1
	num_GPU = 0

gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction = 0.50, allow_growth = True)

config = tf.ConfigProto(intra_op_parallelism_threads = num_cores,
	inter_op_parallelism_threads = num_cores,
	allow_soft_placement = True,
	device_count = {'CPU' : num_CPU, 'GPU' : num_GPU},
	gpu_options = gpu_options)

print('\n\ngpu', str(gpu))

os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu)

session = tf.compat.v1.Session(config=config)

K.set_session(session)

while True:

	print("\nwater_machine_learning_GPU_3 %d\n" % gpu)

	''' toggle 0 or 1 '''
	#gpu ^= 1

	msg = None

	try:

		msg = zmq_socket_pull.recv()
		
	except zmq.ZMQError as error:

		print(error)

	#print("\nmessage",message)

	serving_process(msg, gpu)
