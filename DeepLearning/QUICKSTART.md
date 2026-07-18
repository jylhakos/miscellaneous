# Quick Start Guide

This guide will help you get the ETL Pipeline up and running quickly.

## Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose
- 8GB+ RAM recommended
- (Optional) NVIDIA GPU with CUDA for faster training/inference

## Step 1: Setup Environment

```bash
# Navigate to project directory (from repository root)
# cd DeepLearning

# Run setup script
./scripts/setup_env.sh

# This will:
# - Create virtual environment
# - Install dependencies
# - Create necessary directories
# - Copy .env.example to .env
```

## Step 2: Start Infrastructure

```bash
# Start Kafka and Redis using Docker
./scripts/start_kafka.sh

# This will:
# - Start Zookeeper and Kafka containers
# - Create required topics
# - Verify infrastructure is ready
```

## Step 3: Train the Model

```bash
# Activate virtual environment
source venv/bin/activate

# Train LSTM model
./scripts/train_model.sh

# This will:
# - Generate synthetic training data
# - Build and train LSTM model
# - Save model to models/time_series_lstm.keras
```

## Step 4: Start Microservices

```bash
# Start all services using Docker Compose
cd docker
docker-compose up -d

# Check logs
docker-compose logs -f etl-service inference-service
```

## Step 5: Test the Pipeline

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Produce sample sensor data
python scripts/produce_sample_data.py

# Monitor predictions
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic ml-predictions \
  --from-beginning
```

## Alternative: Run Services Locally (Without Docker)

If you prefer to run services without Docker:

```bash
# Terminal 1: Start Kafka and Redis
docker-compose -f docker/docker-compose.yml up -d kafka redis

# Terminal 2: Run ETL service
source venv/bin/activate
python src/etl_service/kafka_etl_worker.py

# Terminal 3: Run Inference service
source venv/bin/activate
python src/inference_service/kafka_ml_inference.py

# Terminal 4: Produce sample data
source venv/bin/activate
python scripts/produce_sample_data.py
```

## Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_etl.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Troubleshooting

### Kafka Connection Issues

```bash
# Check if Kafka is running
docker ps | grep kafka

# View Kafka logs
docker logs kafka

# Restart Kafka
docker-compose -f docker/docker-compose.yml restart kafka
```

### Model Loading Issues

```bash
# Verify model file exists
ls -lh models/time_series_lstm.keras

# Retrain if necessary
python src/models/train_model.py
```

### GPU Issues (Inference Service)

```bash
# Check GPU availability
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi

# Run without GPU
# Edit docker-compose.yml and remove the GPU deployment section
```

## Next Steps

- Explore the Jupyter notebooks in `notebooks/` for data analysis
- Modify model architecture in `src/models/lstm_model.py`
- Add custom data sources to `src/etl_service/`
- Deploy to AWS (see README.md for AWS deployment guide)

## Configuration

Edit `.env` file to customize:

- Kafka topics
- Model parameters
- Window size
- Logging levels
- AWS credentials (for cloud deployment)

## Cleanup

```bash
# Stop all services
docker-compose -f docker/docker-compose.yml down

# Remove volumes (clears all data)
docker-compose -f docker/docker-compose.yml down -v

# Deactivate virtual environment
deactivate
```

## Support

For issues or questions, refer to the main README.md file.
