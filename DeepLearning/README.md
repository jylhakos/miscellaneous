# Deep Learning in microservices

The document contains information to implement Deep Learning (DL) applications using Tensorflow, Keras, Mosquitto, MQTT, Node.js and Docker libraries.

## Time Series

Learning to store information over extended time intervals via recurrent backpropagation takes a long time.

The sequence of values is important with time series data.

Time series forecasting is predicting future values in time intervals.

The graph below visualizes the problem using values from t-n to t-1 time intervals to predict the target value in t+1 time.

Open loop forecasting predicts the next time step in a sequence using only the input data.

You can use an Long Short Term Memory (LSTM) network to forecast subsequent values of a time series or sequence using previous time steps as input. 

## Recurrent Neural Networks (RNN)

Recurrent neural networks (RNN) are kind of neural networks that is useful for modeling sequence data such as time series.

Time series prediction using Long Short Term Memory (LSTM) Recurrent Neural Networks in Python with Keras

The LSTM, is a recurrent neural network that is trained using backpropagation through time series.

A neural network does a forward pass and computes the prediction errors to obtain the loss values on the training dataset and on the validation set.

The gradient descent refers to the search for a global minimum by evaluating the partial derivatives.

The neural network seeks to minimize the error by adjusting its internal weights during training.

Backpropagation calculates the partial derivatives of the error with respect to the weights.

The loss or error measures the prediction error of the network as a number.

Then the RNN resets the weights, up or down, based on the partial derivatives.

Split the data for the training, validation, and test sets.

Normalization is a way to scale features before training a neural network.

The main features of the input windows are number of time steps of the input and label windows.

Given a list of consecutive inputs, the split will convert them to a window of inputs and a window of labels.

RNN layer uses a for loop to iterate over the timesteps of a sequenc

### Long Short Term Memory (LSTM)

You can use a LSTM network to train a deep neural network to predict numeric values from time series.

At each time step of the input sequence, the LSTM network learns to predict the value of the next time step.

For each prediction, use the previous prediction as the input to the function to predict time steps one at a time.

A sequence input layer inputs time series data into the network. 

LSTM layer learns dependencies between time steps of sequence data.

### Keras

Keras is a deep learning library for Python.

Keras provides default training and evaluation loops, fit() and evaluate() functions.

To forecast the values of future time steps of a sequence, specify the targets as the training sequences with values shifted by one time step.

Models trained in Keras can be deployed on edge computing devices.

```

import tensorflow as tf

from tensorflow import keras

from tensorflow.keras import layers

model = keras.Sequential()

model.add(layers.Embedding(input_dim=1000, output_dim=64))

model.add(layers.LSTM(128))

model.add(layers.Dense(10))

model.summary()

```
![alt text](https://github.com/jylhakos/miscellaneous/blob/main/DeepLearning/1.png?raw=true)

Figure: Deep Learning with time series

## The microservices

The microservice architectural style is an approach to developing an application of components as services, each running in its own process and communicating with lightweight mechanisms.

Each function of the application is implemented by its own microservice.

The messaging between microservices can be based on event driven messaging.

A reason for using services as components is that services are independently deployable.

Docker provides a way to deploy microservices.

### MQ Telemetry Transport (MQTT)

MQTT is a messaging protocol based on the publish/subscribe model. 

MQTT provides real-time and reliable messaging services for networked devices

MQTT is a publish and subscribe protocol which comprises of the broker and client apps, which can either be subscribers or publishers of messages.

MQTT broker would receive messages from a producer and forward them to correspondent subscribers.

A client publishes a message to the topic, while other clients subscribe to the topic to indicate they are interested in receiving messages about the topic.

### References

https://keras.io/getting_started/

https://keras.io/api/layers/recurrent_layers/lstm/

https://www.tensorflow.org/guide/keras/rnn

https://www.tensorflow.org/tutorials/structured_data/time_series
