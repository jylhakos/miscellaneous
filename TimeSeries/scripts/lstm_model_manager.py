"""
Improved LSTM Model Manager for Time-Series Forecasting
Handles model loading, caching, inference, and memory management
"""

import os
import time
import logging
from typing import Optional, Tuple, List

import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

import tensorflow as tf
from tensorflow import keras
from keras.models import load_model
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
import keras.backend as K

from config import config


# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LSTMModelManager:
    """
    Enhanced LSTM Model Manager with better memory management,
    model caching, and error handling
    """
    
    def __init__(self, gpu_id: int = 0):
        """
        Initialize LSTM Model Manager
        
        Args:
            gpu_id: GPU device ID for model execution
        """
        self.gpu_id = gpu_id
        self.model = None
        self.current_feature = None
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.is_loaded = False
        
        # Configure TensorFlow session
        self._configure_tensorflow()
        
        logger.info(f"LSTMModelManager initialized for GPU {gpu_id}")
    
    def _configure_tensorflow(self):
        """Configure TensorFlow GPU settings"""
        try:
            # Set visible GPU
            os.environ["CUDA_VISIBLE_DEVICES"] = str(self.gpu_id)
            
            # Configure GPU memory
            gpus = tf.config.experimental.list_physical_devices('GPU')
            if gpus:
                try:
                    # Enable memory growth
                    for gpu in gpus:
                        tf.config.experimental.set_memory_growth(gpu, config.GPU_ALLOW_GROWTH)
                    
                    # Set memory limit if specified
                    tf.config.experimental.set_virtual_device_configuration(
                        gpus[0],
                        [tf.config.experimental.VirtualDeviceConfiguration(
                            memory_limit=int(1024 * config.GPU_MEMORY_FRACTION)
                        )]
                    )
                    logger.info(f"GPU {self.gpu_id} configured successfully")
                except RuntimeError as e:
                    logger.error(f"GPU configuration error: {e}")
            else:
                logger.warning("No GPU detected, using CPU")
                
        except Exception as e:
            logger.error(f"TensorFlow configuration failed: {e}")
    
    def load_model(self, feature: str) -> bool:
        """
        Load LSTM model for specific feature with caching
        
        Args:
            feature: Feature name (e.g., 'ai_cod1_cod')
            
        Returns:
            bool: True if model loaded successfully
        """
        # Check if model is already loaded for this feature
        if self.is_loaded and self.current_feature == feature:
            logger.debug(f"Model for {feature} already loaded")
            return True
        
        model_path = os.path.join(config.MODEL_FOLDER, f"{feature}.h5")
        
        if not os.path.exists(model_path):
            logger.error(f"Model file not found: {model_path}")
            return False
        
        try:
            # Clear previous session
            if self.model is not None:
                del self.model
                K.clear_session()
            
            # Load new model
            logger.info(f"Loading model from {model_path}")
            self.model = load_model(model_path, compile=False)
            
            # Recompile model for inference
            self.model.compile(
                optimizer='adam',
                loss='mse',
                metrics=['mae']
            )
            
            self.current_feature = feature
            self.is_loaded = True
            
            logger.info(f"Model loaded successfully for feature: {feature}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model for {feature}: {e}")
            self.is_loaded = False
            return False
    
    def preprocess_data(self, values: List[float]) -> Optional[np.ndarray]:
        """
        Preprocess time-series data for model input
        
        Args:
            values: List of time-series values
            
        Returns:
            Preprocessed numpy array or None if invalid
        """
        try:
            # Validate input length
            if len(values) != config.TIME_WINDOW:
                logger.warning(f"Invalid input length: {len(values)}, expected {config.TIME_WINDOW}")
                return None
            
            # Convert to numpy array
            data = np.array(values, dtype=np.float64).reshape(-1, 1)
            
            # Apply MinMax scaling
            scaled_data = self.scaler.fit_transform(data)
            
            # Reshape for LSTM input: (batch_size, time_steps, features)
            scaled_data = scaled_data.reshape(1, config.TIME_WINDOW, 1)
            
            logger.debug(f"Data preprocessed: shape={scaled_data.shape}")
            return scaled_data
            
        except Exception as e:
            logger.error(f"Preprocessing failed: {e}")
            return None
    
    def predict(self, scaled_data: np.ndarray) -> Optional[float]:
        """
        Run inference on preprocessed data
        
        Args:
            scaled_data: Preprocessed and scaled input data
            
        Returns:
            Predicted value or None if prediction fails
        """
        if not self.is_loaded or self.model is None:
            logger.error("Model not loaded, cannot predict")
            return None
        
        try:
            start_time = time.time()
            
            # Run prediction
            prediction_scaled = self.model.predict(scaled_data, verbose=0)
            
            # Inverse transform to original scale
            prediction = self.scaler.inverse_transform(prediction_scaled.reshape(-1, 1))
            predicted_value = float(prediction[0, 0])
            
            inference_time = time.time() - start_time
            logger.info(f"Prediction: {predicted_value:.4f}, Time: {inference_time:.4f}s")
            
            return predicted_value
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            # Clear session on error to prevent memory leaks
            K.clear_session()
            self.is_loaded = False
            return None
    
    def calculate_metrics(self, actual: np.ndarray, predicted: np.ndarray) -> dict:
        """
        Calculate prediction error metrics
        
        Args:
            actual: Actual values
            predicted: Predicted values
            
        Returns:
            Dictionary of metrics
        """
        try:
            rmse = np.sqrt(mean_squared_error(actual, predicted))
            mae = np.mean(np.abs(actual - predicted))
            
            # Avoid division by zero
            mask = actual != 0
            mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
            
            metrics = {
                'rmse': float(rmse),
                'mae': float(mae),
                'mape': float(mape)
            }
            
            logger.debug(f"Metrics - RMSE: {rmse:.4f}, MAE: {mae:.4f}, MAPE: {mape:.2f}%")
            return metrics
            
        except Exception as e:
            logger.error(f"Metrics calculation failed: {e}")
            return {'rmse': None, 'mae': None, 'mape': None}
    
    def process_and_predict(self, feature: str, values: List[float]) -> Optional[float]:
        """
        Complete pipeline: load model, preprocess, predict
        
        Args:
            feature: Feature name
            values: Time-series values
            
        Returns:
            Predicted value or None
        """
        # Load model if needed
        if not self.load_model(feature):
            return None
        
        # Preprocess data
        scaled_data = self.preprocess_data(values)
        if scaled_data is None:
            return None
        
        # Run prediction
        prediction = self.predict(scaled_data)
        
        return prediction
    
    def cleanup(self):
        """Clean up resources and clear session"""
        try:
            if self.model is not None:
                del self.model
            K.clear_session()
            self.is_loaded = False
            logger.info("Model manager cleaned up")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()


def build_lstm_model(
    time_steps: int = 8,
    n_features: int = 1,
    lstm_units: List[int] = [64, 32],
    dropout_rate: float = 0.2,
    learning_rate: float = 0.001
) -> Sequential:
    """
    Build and compile LSTM model for time-series forecasting
    
    Args:
        time_steps: Number of time steps in input sequence
        n_features: Number of features per time step
        lstm_units: List of LSTM layer units
        dropout_rate: Dropout rate for regularization
        learning_rate: Learning rate for optimizer
        
    Returns:
        Compiled Keras Sequential model
    """
    model = Sequential()
    
    # First LSTM layer
    model.add(LSTM(
        units=lstm_units[0],
        return_sequences=len(lstm_units) > 1,
        input_shape=(time_steps, n_features)
    ))
    model.add(Dropout(dropout_rate))
    
    # Additional LSTM layers
    for i, units in enumerate(lstm_units[1:], 1):
        return_seq = i < len(lstm_units) - 1
        model.add(LSTM(units=units, return_sequences=return_seq))
        model.add(Dropout(dropout_rate))
    
    # Output layer
    model.add(Dense(units=1))
    
    # Compile model
    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(
        optimizer=optimizer,
        loss='mse',
        metrics=['mae', 'mse']
    )
    
    logger.info(f"Model built: {len(lstm_units)} LSTM layers, dropout={dropout_rate}")
    return model


def train_lstm_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    feature_name: str,
    epochs: int = 100,
    batch_size: int = 32
) -> Tuple[Sequential, dict]:
    """
    Train LSTM model with early stopping and checkpointing
    
    Args:
        X_train: Training features
        y_train: Training labels
        X_val: Validation features
        y_val: Validation labels
        feature_name: Name of feature for model saving
        epochs: Maximum number of epochs
        batch_size: Training batch size
        
    Returns:
        Tuple of (trained model, training history)
    """
    logger.info(f"Training LSTM model for {feature_name}")
    
    # Build model
    model = build_lstm_model(
        time_steps=config.TIME_WINDOW,
        n_features=1
    )
    
    # Callbacks
    model_path = os.path.join(config.MODEL_FOLDER, f"{feature_name}.h5")
    os.makedirs(config.MODEL_FOLDER, exist_ok=True)
    
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True,
            verbose=1
        ),
        ModelCheckpoint(
            filepath=model_path,
            monitor='val_loss',
            save_best_only=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            verbose=1
        )
    ]
    
    # Train model
    logger.info(f"Starting training: {epochs} epochs, batch_size={batch_size}")
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=1
    )
    
    logger.info(f"Training completed. Model saved to {model_path}")
    
    return model, history.history


if __name__ == "__main__":
    # Test model manager
    logger.info("Testing LSTMModelManager...")
    
    manager = LSTMModelManager(gpu_id=0)
    
    # Test data
    test_values = [100.5, 102.3, 98.7, 101.2, 99.8, 103.1, 100.4, 102.0]
    test_feature = "ai_cod1_cod"
    
    # Test prediction
    prediction = manager.process_and_predict(test_feature, test_values)
    
    if prediction:
        logger.info(f"Test prediction successful: {prediction:.4f}")
    else:
        logger.error("Test prediction failed")
    
    manager.cleanup()
