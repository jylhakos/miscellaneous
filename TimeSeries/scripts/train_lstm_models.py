"""
LSTM Model Training Script
Train time-series forecasting models for water quality parameters
"""

import os
import sys
import logging
import argparse
from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

import psycopg2
from psycopg2.extras import RealDictCursor

from config import config
from lstm_model_manager import build_lstm_model, train_lstm_model


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LSTMTrainer:
    """
    LSTM Model Trainer for Time-Series Forecasting
    
    Handles data extraction, preprocessing, training, and evaluation
    """
    
    def __init__(self, feature_name: str):
        """
        Initialize trainer for specific feature
        
        Args:
            feature_name: Name of feature to train model for
        """
        self.feature_name = feature_name
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.time_window = config.TIME_WINDOW
        self.horizon = config.PREDICTION_HORIZON
        
        logger.info(f"Initializing trainer for feature: {feature_name}")
    
    def fetch_data_from_db(self, limit: int = 10000) -> pd.DataFrame:
        """
        Fetch historical data from PostgreSQL
        
        Args:
            limit: Maximum number of records to fetch
            
        Returns:
            DataFrame with timestamp and value columns
        """
        logger.info(f"Fetching data from database (limit: {limit})")
        
        try:
            conn = psycopg2.connect(config.DB_URI)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            query = f"""
                SELECT timestamp, value 
                FROM {config.INPUT_TABLE}
                WHERE feature = %s
                ORDER BY timestamp ASC
                LIMIT %s
            """
            
            cursor.execute(query, (self.feature_name, limit))
            rows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Convert to DataFrame
            df = pd.DataFrame(rows)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['value'] = df['value'].astype(float)
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            logger.info(f"Fetched {len(df)} records")
            logger.info(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
            
            return df
            
        except Exception as e:
            logger.error(f"Database fetch failed: {e}")
            raise
    
    def load_data_from_csv(self, csv_path: str) -> pd.DataFrame:
        """
        Load historical data from CSV file
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            DataFrame with timestamp and value columns
        """
        logger.info(f"Loading data from CSV: {csv_path}")
        
        try:
            df = pd.read_csv(csv_path)
            
            # Ensure required columns exist
            if 'timestamp' not in df.columns or 'value' not in df.columns:
                raise ValueError("CSV must contain 'timestamp' and 'value' columns")
            
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['value'] = df['value'].astype(float)
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            logger.info(f"Loaded {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"CSV load failed: {e}")
            raise
    
    def create_sequences(
        self,
        data: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create time-series sequences for supervised learning
        
        Args:
            data: Scaled time-series data
            
        Returns:
            Tuple of (X, y) sequences
        """
        X, y = [], []
        
        for i in range(len(data) - self.time_window - self.horizon + 1):
            # Input sequence
            X.append(data[i:i + self.time_window])
            # Target value (next value after window)
            y.append(data[i + self.time_window + self.horizon - 1])
        
        X = np.array(X)
        y = np.array(y)
        
        # Reshape for LSTM: (samples, time_steps, features)
        X = X.reshape(X.shape[0], self.time_window, 1)
        
        logger.info(f"Created sequences - X: {X.shape}, y: {y.shape}")
        return X, y
    
    def prepare_data(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        val_size: float = 0.1
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare training, validation, and test datasets
        
        Args:
            df: Input DataFrame
            test_size: Proportion of data for testing
            val_size: Proportion of training data for validation
            
        Returns:
            Tuple of (X_train, y_train, X_val, y_val, X_test, y_test)
        """
        logger.info("Preparing datasets...")
        
        # Extract values
        values = df['value'].values.reshape(-1, 1)
        
        # Scale data
        scaled_data = self.scaler.fit_transform(values)
        scaled_data = scaled_data.flatten()
        
        logger.info(f"Data scaled - min: {scaled_data.min():.4f}, max: {scaled_data.max():.4f}")
        
        # Create sequences
        X, y = self.create_sequences(scaled_data)
        
        # Split into train+val and test
        X_trainval, X_test, y_trainval, y_test = train_test_split(
            X, y, test_size=test_size, shuffle=False
        )
        
        # Split train+val into train and val
        X_train, X_val, y_train, y_val = train_test_split(
            X_trainval, y_trainval, test_size=val_size, shuffle=False
        )
        
        logger.info(f"Train samples: {len(X_train)}")
        logger.info(f"Validation samples: {len(X_val)}")
        logger.info(f"Test samples: {len(X_test)}")
        
        return X_train, y_train, X_val, y_val, X_test, y_test
    
    def evaluate_model(
        self,
        model,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> dict:
        """
        Evaluate trained model on test data
        
        Args:
            model: Trained Keras model
            X_test: Test features
            y_test: Test labels
            
        Returns:
            Dictionary of evaluation metrics
        """
        logger.info("Evaluating model on test set...")
        
        # Make predictions
        y_pred_scaled = model.predict(X_test, verbose=0)
        
        # Inverse transform
        y_test_original = self.scaler.inverse_transform(y_test.reshape(-1, 1))
        y_pred_original = self.scaler.inverse_transform(y_pred_scaled.reshape(-1, 1))
        
        # Calculate metrics
        rmse = np.sqrt(np.mean((y_test_original - y_pred_original) ** 2))
        mae = np.mean(np.abs(y_test_original - y_pred_original))
        
        mask = y_test_original != 0
        mape = np.mean(np.abs((y_test_original[mask] - y_pred_original[mask]) / y_test_original[mask])) * 100
        
        metrics = {
            'rmse': float(rmse),
            'mae': float(mae),
            'mape': float(mape),
            'samples': len(y_test)
        }
        
        logger.info(f"Evaluation metrics:")
        logger.info(f"  RMSE: {rmse:.4f}")
        logger.info(f"  MAE: {mae:.4f}")
        logger.info(f"  MAPE: {mape:.2f}%")
        
        return metrics
    
    def plot_predictions(
        self,
        model,
        X_test: np.ndarray,
        y_test: np.ndarray,
        save_path: str = None
    ):
        """
        Plot actual vs predicted values
        
        Args:
            model: Trained model
            X_test: Test features
            y_test: Test labels
            save_path: Path to save plot
        """
        # Predictions
        y_pred_scaled = model.predict(X_test, verbose=0)
        
        # Inverse transform
        y_test_original = self.scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()
        y_pred_original = self.scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
        
        # Plot
        plt.figure(figsize=(15, 6))
        plt.plot(y_test_original, label='Actual', alpha=0.7)
        plt.plot(y_pred_original, label='Predicted', alpha=0.7)
        plt.title(f'LSTM Predictions - {self.feature_name}')
        plt.xlabel('Sample Index')
        plt.ylabel('Value')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def train(
        self,
        data_source: str,
        epochs: int = 100,
        batch_size: int = 32,
        save_plot: bool = True
    ):
        """
        Complete training pipeline
        
        Args:
            data_source: Path to CSV file or 'database'
            epochs: Number of training epochs
            batch_size: Training batch size
            save_plot: Whether to save prediction plots
        """
        logger.info(f"Starting training pipeline for {self.feature_name}")
        
        # Load data
        if data_source.lower() == 'database':
            df = self.fetch_data_from_db()
        else:
            df = self.load_data_from_csv(data_source)
        
        # Prepare datasets
        X_train, y_train, X_val, y_val, X_test, y_test = self.prepare_data(df)
        
        # Train model
        model, history = train_lstm_model(
            X_train, y_train,
            X_val, y_val,
            self.feature_name,
            epochs=epochs,
            batch_size=batch_size
        )
        
        # Evaluate model
        metrics = self.evaluate_model(model, X_test, y_test)
        
        # Plot predictions
        if save_plot:
            plot_path = os.path.join(config.MODEL_FOLDER, f"{self.feature_name}_predictions.png")
            self.plot_predictions(model, X_test, y_test, save_path=plot_path)
        
        logger.info(f"Training completed successfully for {self.feature_name}")
        
        return model, metrics


def main():
    """Main training script"""
    parser = argparse.ArgumentParser(description='Train LSTM models for time-series forecasting')
    parser.add_argument(
        '--feature',
        type=str,
        required=True,
        choices=config.FEATURE_LIST + ['all'],
        help='Feature name to train or "all" for all features'
    )
    parser.add_argument(
        '--data-source',
        type=str,
        default='database',
        help='Data source: "database" or path to CSV file'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=100,
        help='Number of training epochs'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=32,
        help='Training batch size'
    )
    
    args = parser.parse_args()
    
    # Determine features to train
    if args.feature == 'all':
        features = config.FEATURE_LIST
    else:
        features = [args.feature]
    
    # Train models
    results = {}
    for feature in features:
        logger.info(f"\n{'='*60}")
        logger.info(f"Training model for feature: {feature}")
        logger.info(f"{'='*60}\n")
        
        try:
            trainer = LSTMTrainer(feature)
            model, metrics = trainer.train(
                data_source=args.data_source,
                epochs=args.epochs,
                batch_size=args.batch_size
            )
            results[feature] = {'status': 'success', 'metrics': metrics}
            
        except Exception as e:
            logger.error(f"Training failed for {feature}: {e}", exc_info=True)
            results[feature] = {'status': 'failed', 'error': str(e)}
    
    # Print summary
    logger.info(f"\n{'='*60}")
    logger.info("Training Summary:")
    logger.info(f"{'='*60}")
    for feature, result in results.items():
        status = result['status']
        logger.info(f"{feature}: {status}")
        if status == 'success':
            metrics = result['metrics']
            logger.info(f"  RMSE: {metrics['rmse']:.4f}, MAE: {metrics['mae']:.4f}, MAPE: {metrics['mape']:.2f}%")
    logger.info(f"{'='*60}\n")


if __name__ == "__main__":
    main()
