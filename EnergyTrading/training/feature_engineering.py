import pandas as pd
import numpy as np

def create_temporal_features(df):
    """Create cyclical time features"""
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['month'] = df['timestamp'].dt.month
    
    # Cyclical encoding
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    
    return df

def create_lagged_features(df, columns, lags):
    """Create lagged features"""
    for col in columns:
        for lag in lags:
            df[f'{col}_lag_{lag}'] = df[col].shift(lag)
    return df

def create_rolling_features(df, columns, windows):
    """Create rolling window statistics"""
    for col in columns:
        for window in windows:
            df[f'{col}_rolling_mean_{window}'] = df[col].rolling(window=window).mean()
            df[f'{col}_rolling_std_{window}'] = df[col].rolling(window=window).std()
    return df

if __name__ == "__main__":
    # Example usage
    df = pd.read_csv('../data/raw/grid_history.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Apply feature engineering
    df = create_temporal_features(df)
    df = create_lagged_features(df, ['actual_mw'], [4, 96])  # 1 hour, 24 hours
    df = create_rolling_features(df, ['actual_mw'], [12, 96])  # 3 hours, 24 hours
    
    # Save processed data
    df.to_csv('../data/processed/grid_features.csv', index=False)
    print("Feature engineering complete!")
