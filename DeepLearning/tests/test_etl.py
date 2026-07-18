"""
Unit tests for ETL transformation functions.
"""

import pytest
import numpy as np
import json
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.etl_service.transform import (
    transform_timeseries_event,
    transform_window,
    calculate_sma_incremental,
    calculate_ema,
    detect_outliers_zscore
)


class TestETLTransformations:
    """Test suite for ETL transformation functions."""
    
    def test_transform_timeseries_event(self):
        """Test basic event transformation."""
        raw_event = json.dumps({
            'timestamp': '2026-07-18T12:00:00',
            'value': 100.0
        })
        
        result = transform_timeseries_event(raw_event)
        
        assert 'timestamp' in result
        assert 'normalized_value' in result
        assert result['normalized_value'] == 1.0  # 100 / 100
        assert result['feature_group'] == 'sensor_metrics'
    
    def test_transform_window_normal(self):
        """Test window transformation with normal data."""
        window_data = [10.0, 20.0, 30.0, 40.0, 50.0]
        
        result = transform_window(window_data)
        
        assert isinstance(result, np.ndarray)
        assert len(result) == len(window_data)
        assert abs(np.mean(result)) < 1e-5  # Mean should be near zero
    
    def test_transform_window_constant(self):
        """Test window transformation with constant values."""
        window_data = [5.0] * 10
        
        result = transform_window(window_data)
        
        assert isinstance(result, np.ndarray)
        assert len(result) == len(window_data)
        # All values should be zero after normalization
        assert np.all(result == 0.0)
    
    def test_calculate_sma_incremental(self):
        """Test incremental SMA calculation."""
        old_avg = 50.0
        new_value = 60.0
        old_value = 40.0
        window_size = 10
        
        result = calculate_sma_incremental(old_avg, new_value, old_value, window_size)
        
        expected = 50.0 + (60.0 - 40.0) / 10
        assert abs(result - expected) < 1e-10
        assert result == 52.0
    
    def test_calculate_ema(self):
        """Test exponential moving average calculation."""
        old_ema = 50.0
        new_value = 60.0
        alpha = 0.3
        
        result = calculate_ema(old_ema, new_value, alpha)
        
        expected = 0.3 * 60.0 + 0.7 * 50.0
        assert abs(result - expected) < 1e-10
        assert result == 53.0
    
    def test_detect_outliers_zscore(self):
        """Test outlier detection using Z-score."""
        # Normal data with one outlier
        window_data = [10.0, 11.0, 9.0, 10.5, 9.5, 100.0]
        
        result = detect_outliers_zscore(window_data, threshold=2.0)
        
        assert isinstance(result, list)
        assert len(result) == len(window_data)
        assert result[-1] == True  # Last value is outlier
        assert sum(result) == 1  # Only one outlier
    
    def test_detect_outliers_no_outliers(self):
        """Test outlier detection with no outliers."""
        window_data = [10.0, 11.0, 9.0, 10.5, 9.5, 10.2]
        
        result = detect_outliers_zscore(window_data, threshold=3.0)
        
        assert sum(result) == 0  # No outliers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
