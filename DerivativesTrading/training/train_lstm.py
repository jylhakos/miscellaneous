import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import argparse
import os

# Model hyperparameters
WINDOW_LENGTH = 96      # 24 hours × 4 (15-min intervals)
NUM_FEATURES = 3        # [actual_mw, wind_speed_ms, solar_irradiance]
HORIZON_LENGTH = 1      # Predict next 15-minute interval
LSTM_UNITS_L1 = 64
LSTM_UNITS_L2 = 32
DROPOUT_RATE = 0.2

def load_and_prepare_data(data_path):
    """Load and prepare time series data"""
    df = pd.read_csv(data_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    # Forward fill missing values
    df = df.fillna(method='ffill', limit=20)
    df = df.dropna()
    
    return df

def create_sequences(data, window_size, horizon):
    """Create supervised learning sequences"""
    X, y = [], []
    for i in range(len(data) - window_size - horizon + 1):
        X.append(data[i:i+window_size])
        y.append(data[i+window_size+horizon-1, 0])  # Target: actual_mw
    return np.array(X), np.array(y)

def build_lstm_model():
    """Build LSTM model architecture"""
    model = Sequential([
        LSTM(LSTM_UNITS_L1, 
             return_sequences=True, 
             input_shape=(WINDOW_LENGTH, NUM_FEATURES)),
        Dropout(DROPOUT_RATE),
        LSTM(LSTM_UNITS_L2),
        Dropout(DROPOUT_RATE),
        Dense(HORIZON_LENGTH)
    ])
    
    model.compile(
        optimizer='adam',
        loss='mse',
        metrics=['mae']
    )
    
    return model

def train_model(data_path, output_dir, epochs=100):
    """Train LSTM model and save artifacts"""
    
    # Load data
    print("Loading data...")
    df = load_and_prepare_data(data_path)
    
    # Extract features
    features = df[['actual_mw', 'wind_speed_ms', 'solar_irradiance']].values
    
    # Scale features
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_features = scaler.fit_transform(features)
    
    # Save scaler parameters
    os.makedirs(output_dir, exist_ok=True)
    np.save(os.path.join(output_dir, 'scaler_min.npy'), scaler.data_min_)
    np.save(os.path.join(output_dir, 'scaler_max.npy'), scaler.data_max_)
    
    # Create sequences
    print("Creating sequences...")
    X, y = create_sequences(scaled_features, WINDOW_LENGTH, HORIZON_LENGTH)
    
    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    
    # Build model
    print("Building model...")
    model = build_lstm_model()
    model.summary()
    
    # Define callbacks
    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True
    )
    
    checkpoint = ModelCheckpoint(
        os.path.join(output_dir, 'lstm_demand_model.h5'),
        monitor='val_loss',
        save_best_only=True
    )
    
    # Train model
    print("Training model...")
    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=32,
        validation_split=0.2,
        callbacks=[early_stop, checkpoint],
        verbose=1
    )
    
    # Evaluate on test set
    print("Evaluating model...")
    test_loss, test_mae = model.evaluate(X_test, y_test, verbose=0)
    print(f"Test Loss (MSE): {test_loss:.4f}")
    print(f"Test MAE: {test_mae:.4f}")
    
    print(f"\nModel and scaler saved to {output_dir}")
    
    return model, history

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Train LSTM model for energy demand forecasting')
    parser.add_argument('--data', type=str, required=True, help='Path to training data CSV')
    parser.add_argument('--epochs', type=int, default=100, help='Number of training epochs')
    parser.add_argument('--output', type=str, default='../models/', help='Output directory for model')
    
    args = parser.parse_args()
    
    train_model(args.data, args.output, args.epochs)
