"""Data transformation functions for ETL pipeline."""

import numpy as np
from typing import List, Dict, Any
import json


def transform_timeseries_event(raw_event: str) -> Dict[str, Any]:
    """
    Basic ETL transformation function for a single event.
    
    Args:
        raw_event: Raw JSON event string
    
    Returns:
        Transformed payload dictionary
    """
    from datetime import datetime
    
    # Extract raw payload
    data = json.loads(raw_event)
    
    # Transform: validate timestamp and scale a metric
    timestamp = datetime.fromisoformat(data['timestamp'])
    scaled_value = data['value'] / 100.0  # Normalization example
    
    # Load: structure transformed event
    transformed_payload = {
        'timestamp': timestamp.isoformat(),
        'normalized_value': scaled_value,
        'feature_group': 'sensor_metrics'
    }
    
    return transformed_payload


def transform_window(window_data: List[float]) -> np.ndarray:
    """
    Apply transformations to a sliding window of time-series data.
    
    - Normalize using z-score normalization
    - Handle edge cases (constant values)
    
    Args:
        window_data: List of float values representing a time window
    
    Returns:
        Normalized numpy array
    """
    window_arr = np.array(window_data, dtype=np.float32)
    
    mean = np.mean(window_arr)
    std = np.std(window_arr)
    
    # Avoid division by zero for constant values
    if std < 1e-5:
        normalized = window_arr - mean
    else:
        normalized = (window_arr - mean) / std
    
    return normalized


def calculate_sma_incremental(
    old_avg: float,
    new_value: float,
    old_value: float,
    window_size: int
) -> float:
    """
    Calculate Simple Moving Average incrementally.
    
    Formula: μ_new = μ_old + (x_new - x_old) / N
    
    Args:
        old_avg: Previous moving average
        new_value: Newly arrived data point
        old_value: Oldest data point being dropped
        window_size: Fixed window size N
    
    Returns:
        Updated moving average
    """
    return old_avg + (new_value - old_value) / window_size


def calculate_ema(
    old_ema: float,
    new_value: float,
    alpha: float = 0.3
) -> float:
    """
    Calculate Exponential Moving Average.
    
    Formula: μ_new = α · x_new + (1 - α) · μ_old
    
    Args:
        old_ema: Previous exponential moving average
        new_value: Newly arrived data point
        alpha: Smoothing factor (0 < α < 1)
    
    Returns:
        Updated exponential moving average
    """
    return alpha * new_value + (1 - alpha) * old_ema


def detect_outliers_zscore(window_data: List[float], threshold: float = 3.0) -> List[bool]:
    """
    Detect outliers using Z-score method.
    
    Args:
        window_data: List of values
        threshold: Z-score threshold (typically 2.5 or 3.0)
    
    Returns:
        List of boolean values indicating outliers
    """
    window_arr = np.array(window_data)
    mean = np.mean(window_arr)
    std = np.std(window_arr)
    
    if std < 1e-5:
        return [False] * len(window_data)
    
    z_scores = np.abs((window_arr - mean) / std)
    return (z_scores > threshold).tolist()
