"""LSTM model architecture for time-series prediction."""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from typing import Tuple


def build_lstm_model(
    window_size: int,
    features: int = 1,
    lstm_units: Tuple[int, ...] = (64,),
    dense_units: int = 32,
    dropout_rate: float = 0.2
) -> keras.Model:
    """
    Build LSTM model for time-series prediction.
    
    Args:
        window_size: Number of time steps in input sequence
        features: Number of features per time step
        lstm_units: Tuple of LSTM layer sizes
        dense_units: Number of units in dense layer
        dropout_rate: Dropout rate for regularization
    
    Returns:
        Compiled Keras model
    """
    model = models.Sequential(name='TimeSeries_LSTM')
    
    # Input layer
    model.add(layers.Input(shape=(window_size, features)))
    
    # LSTM layers
    for i, units in enumerate(lstm_units):
        return_sequences = i < len(lstm_units) - 1
        model.add(layers.LSTM(units, return_sequences=return_sequences))
        model.add(layers.Dropout(dropout_rate))
    
    # Dense layers
    model.add(layers.Dense(dense_units, activation='relu'))
    model.add(layers.Dense(1))  # Regression output
    
    # Compile model
    model.compile(
        optimizer='adam',
        loss='mse',
        metrics=['mae', 'mse']
    )
    
    return model


def build_bidirectional_lstm(
    window_size: int,
    features: int = 1,
    lstm_units: int = 64,
    dropout_rate: float = 0.2
) -> keras.Model:
    """
    Build Bidirectional LSTM for improved time-series prediction.
    
    Args:
        window_size: Number of time steps in input sequence
        features: Number of features per time step
        lstm_units: Number of LSTM units
        dropout_rate: Dropout rate
    
    Returns:
        Compiled Keras model
    """
    model = models.Sequential([
        layers.Input(shape=(window_size, features)),
        layers.Bidirectional(layers.LSTM(lstm_units, return_sequences=True)),
        layers.Dropout(dropout_rate),
        layers.Bidirectional(layers.LSTM(lstm_units // 2)),
        layers.Dropout(dropout_rate),
        layers.Dense(32, activation='relu'),
        layers.Dense(1)
    ], name='Bidirectional_LSTM')
    
    model.compile(
        optimizer='adam',
        loss='mse',
        metrics=['mae']
    )
    
    return model


def build_cnn_lstm_hybrid(
    window_size: int,
    features: int = 1,
    conv_filters: int = 64,
    lstm_units: int = 50
) -> keras.Model:
    """
    Build CNN-LSTM hybrid model for time-series prediction.
    Extracts temporal features with CNN before LSTM processing.
    
    Args:
        window_size: Number of time steps
        features: Number of features per time step
        conv_filters: Number of convolutional filters
        lstm_units: Number of LSTM units
    
    Returns:
        Compiled Keras model
    """
    model = models.Sequential([
        layers.Input(shape=(window_size, features)),
        layers.Conv1D(filters=conv_filters, kernel_size=3, activation='relu'),
        layers.MaxPooling1D(pool_size=2),
        layers.LSTM(lstm_units),
        layers.Dropout(0.2),
        layers.Dense(32, activation='relu'),
        layers.Dense(1)
    ], name='CNN_LSTM_Hybrid')
    
    model.compile(
        optimizer='adam',
        loss='mse',
        metrics=['mae']
    )
    
    return model
