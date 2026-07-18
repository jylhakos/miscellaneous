#!/bin/bash

# Train LSTM model for time-series prediction

set -e

echo "========================================="
echo "Training LSTM Model"
echo "========================================="

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Virtual environment is not activated. Activating..."
    source venv/bin/activate
fi

# Check if models directory exists
mkdir -p models

# Run training script
echo ""
echo "Starting model training..."
python src/models/train_model.py

# Check if model was created
if [ -f "models/time_series_lstm.keras" ]; then
    echo ""
    echo "========================================="
    echo "Model training completed successfully!"
    echo "========================================="
    echo ""
    echo "Model saved at: models/time_series_lstm.keras"
    ls -lh models/time_series_lstm.keras
else
    echo ""
    echo "Error: Model file was not created!"
    exit 1
fi
