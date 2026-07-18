"""
Train LSTM model for time-series prediction.

This script:
1. Generates synthetic time-series data (or loads from file)
2. Builds LSTM model architecture
3. Trains the model with validation
4. Saves the trained model
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import logging
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.logger import setup_logger
from src.models.lstm_model import build_lstm_model

logger = setup_logger(__name__)

# Model parameters
WINDOW_SIZE = 24  # Time steps in input sequence
FEATURES = 1      # Number of features per time step
EPOCHS = 50
BATCH_SIZE = 32
VALIDATION_SPLIT = 0.2

# Create models directory if it doesn't exist
os.makedirs('models', exist_ok=True)


def generate_synthetic_data(num_samples: int = 10000, window_size: int = 24):
    """
    Generate synthetic time-series data for training.
    Simulates sensor readings with trend, seasonality, and noise.
    
    Args:
        num_samples: Number of training samples to generate
        window_size: Size of sliding window
    
    Returns:
        Tuple of (X_train, y_train) numpy arrays
    """
    logger.info(f'Generating {num_samples} synthetic samples...')
    
    time = np.arange(num_samples + window_size)
    
    # Components: trend + seasonality + noise
    trend = 0.01 * time
    seasonality = 10 * np.sin(2 * np.pi * time / 24)  # Daily pattern
    noise = np.random.normal(0, 1, len(time))
    
    series = trend + seasonality + noise
    
    # Create sliding windows
    X, y = [], []
    for i in range(num_samples):
        X.append(series[i:i+window_size])
        y.append(series[i+window_size])
    
    X = np.array(X).reshape(-1, window_size, 1)
    y = np.array(y).reshape(-1, 1)
    
    logger.info(f'Generated data shapes: X={X.shape}, y={y.shape}')
    
    return X, y


def plot_training_history(history, save_path: str = 'models/training_history.png'):
    """
    Plot training history (loss and metrics).
    
    Args:
        history: Keras History object
        save_path: Path to save the plot
    """
    try:
        import matplotlib.pyplot as plt
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        # Plot loss
        ax1.plot(history.history['loss'], label='Training Loss')
        ax1.plot(history.history['val_loss'], label='Validation Loss')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss (MSE)')
        ax1.set_title('Model Loss')
        ax1.legend()
        ax1.grid(True)
        
        # Plot MAE
        ax2.plot(history.history['mae'], label='Training MAE')
        ax2.plot(history.history['val_mae'], label='Validation MAE')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('MAE')
        ax2.set_title('Model MAE')
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig(save_path)
        logger.info(f'Training history plot saved to {save_path}')
        
    except ImportError:
        logger.warning('Matplotlib not available. Skipping plot generation.')


def main():
    """Train and save LSTM model."""
    logger.info('='*60)
    logger.info('Starting LSTM Model Training')
    logger.info('='*60)
    
    # Set random seeds for reproducibility
    np.random.seed(42)
    tf.random.set_seed(42)
    
    # Generate training data
    X_train, y_train = generate_synthetic_data(num_samples=10000, window_size=WINDOW_SIZE)
    
    # Build model
    logger.info('Building LSTM model...')
    model = build_lstm_model(window_size=WINDOW_SIZE, features=FEATURES)
    
    # Display model architecture
    logger.info('\nModel Architecture:')
    model.summary(print_fn=logger.info)
    
    # Configure callbacks
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True,
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=3,
            min_lr=1e-6,
            verbose=1
        ),
        ModelCheckpoint(
            filepath='models/time_series_lstm_checkpoint.keras',
            monitor='val_loss',
            save_best_only=True,
            verbose=1
        )
    ]
    
    # Train model
    logger.info('\n' + '='*60)
    logger.info('Training model...')
    logger.info('='*60)
    
    history = model.fit(
        X_train, y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_split=VALIDATION_SPLIT,
        callbacks=callbacks,
        verbose=1
    )
    
    # Save model in Keras format
    model_path = 'models/time_series_lstm.keras'
    model.save(model_path)
    logger.info(f'\nModel saved to {model_path}')
    
    # Evaluate on validation data
    val_samples = int(len(X_train) * VALIDATION_SPLIT)
    X_val = X_train[-val_samples:]
    y_val = y_train[-val_samples:]
    
    logger.info('\nEvaluating model on validation set...')
    val_loss, val_mae, val_mse = model.evaluate(X_val, y_val, verbose=0)
    
    logger.info('='*60)
    logger.info('Training Complete!')
    logger.info('='*60)
    logger.info(f'Validation Loss (MSE): {val_loss:.4f}')
    logger.info(f'Validation MAE: {val_mae:.4f}')
    logger.info(f'Validation RMSE: {np.sqrt(val_mse):.4f}')
    logger.info(f'Model saved at: {model_path}')
    
    # Plot training history
    plot_training_history(history)
    
    # Test prediction
    logger.info('\nTesting prediction on sample data...')
    sample_input = X_val[0:1]
    sample_prediction = model.predict(sample_input, verbose=0)
    sample_actual = y_val[0]
    
    logger.info(f'Sample prediction: {sample_prediction[0][0]:.4f}')
    logger.info(f'Actual value: {sample_actual[0]:.4f}')
    logger.info(f'Prediction error: {abs(sample_prediction[0][0] - sample_actual[0]):.4f}')


if __name__ == "__main__":
    main()
