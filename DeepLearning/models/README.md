# Models Directory

This directory contains trained machine learning models.

## Model Files

- `time_series_lstm.keras` - Trained LSTM model for time-series prediction (generated after training)
- `time_series_lstm_checkpoint.keras` - Best model checkpoint during training
- `training_history.png` - Training history visualization

## Training

To train the model, run:

```bash
# Activate virtual environment
source venv/bin/activate

# Run training script
python src/models/train_model.py

# Or use the shell script
./scripts/train_model.sh
```

## Model Architecture

The default LSTM model has the following architecture:

- Input: (24, 1) - 24 time steps, 1 feature
- LSTM Layer: 64 units
- Dropout: 0.2
- Dense Layer: 32 units, ReLU activation
- Output: 1 unit (regression)

## Model Versions

| Version | Description | Date | Metrics |
|---------|-------------|------|---------|
| 1.0     | Initial LSTM model | 2026-07-18 | MSE: TBD |

