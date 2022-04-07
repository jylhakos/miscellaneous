# Microservices and Deep Learning

The document contains information to implement Deep Learning (DL) applications using Tensorflow, Keras, Mosquitto, Node.js and Docker libraries.

## Recurrent Neural Networks (RNN) with Keras

Recurrent neural networks (RNN) are kind of neural networks that is useful for modeling sequence data such as time series.

Time series prediction using Long Short Term Memory (LSTM) Recurrent Neural Networks in Python with Keras

The Long Short Term Memory network (LSTM), is a recurrent neural network that is trained using backpropagation through time series.

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

Models trained in Tensorflow can be deployed on edge computing devices.

Keras is a deep learning library for Python.

![alt text](https://github.com/jylhakos/miscellaneous/blob/main/DeepLearning/1.png?raw=true)

Figure: Deep Learning with time series

### References

https://keras.io/getting_started/

https://keras.io/api/layers/recurrent_layers/lstm/

https://www.tensorflow.org/guide/keras/rnn

https://www.tensorflow.org/tutorials/structured_data/time_series
