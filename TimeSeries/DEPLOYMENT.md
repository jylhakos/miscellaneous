# Deployment and Operations Guide

## Table of Contents

- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Model Training](#model-training)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting](#troubleshooting)
- [Performance Tuning](#performance-tuning)

## Quick Start

### Local Development (Single Machine)

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd TimeSeries
   ```

2. **Install Dependencies**
   ```bash
   # Python dependencies
   pip install -r requirements.txt
   
   # Node.js dependencies
   cd scripts/
   npm install
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize Database**
   ```bash
   psql -h localhost -U demo -d demo -f init-db.sql
   ```

5. **Start Services**
   ```bash
   # Terminal 1: Data Collector
   python scripts/water_data_collector.py
   
   # Terminal 2: LSTM Service
   python scripts/water_lstm_service_improved.py 0
   
   # Terminal 3: Output Service
   python scripts/water_output_service_0.py
   
   # Terminal 4: Web Application
   node scripts/water_app.js
   ```

6. **Access Dashboard**
   Open browser to `http://localhost:3001/predict`

## Development Setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 12+
- Redis 6+
- CUDA 11+ (for GPU support)
- NVIDIA GPU with 4GB+ VRAM (recommended)

### Environment Configuration

Create `.env` file from template:
```bash
cp .env.example .env
```

Key configuration parameters:
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`: Database connection
- `MQTT_BROKER`, `MQTT_PORT`: MQTT broker settings
- `GPU_MEMORY_FRACTION`: GPU memory allocation (0.0-1.0)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Code Improvements

The improved codebase includes:

1. **Configuration Management** (`config.py`)
   - Centralized configuration
   - Environment variable support
   - Development/production profiles

2. **LSTM Model Manager** (`lstm_model_manager.py`)
   - Model caching and lifecycle management
   - Memory-efficient inference
   - Automatic error recovery
   - Metrics calculation

3. **Improved LSTM Service** (`water_lstm_service_improved.py`)
   - Better error handling
   - Statistics tracking
   - Graceful shutdown
   - Enhanced logging

4. **Training Pipeline** (`train_lstm_models.py`)
   - Automated model training
   - Hyperparameter configuration
   - Model evaluation and visualization
   - Database and CSV data sources

## Production Deployment

### System Requirements

- **CPU**: 8+ cores recommended
- **RAM**: 16GB minimum, 32GB recommended
- **GPU**: NVIDIA GPU with 6GB+ VRAM per ML service
- **Storage**: 50GB+ for data and models
- **Network**: 1Gbps recommended

### Architecture Considerations

1. **Load Balancing**: Use multiple LSTM services across GPUs
2. **High Availability**: Deploy redundant instances
3. **Data Persistence**: Regular database backups
4. **Monitoring**: Prometheus/Grafana for metrics
5. **Logging**: ELK stack or Loki for log aggregation

### Security Hardening

```bash
# Use strong passwords
export DB_PASSWORD=$(openssl rand -base64 32)

# Enable SSL/TLS for PostgreSQL
# Edit postgresql.conf:
ssl = on
ssl_cert_file = '/path/to/server.crt'
ssl_key_file = '/path/to/server.key'

# Use MQTT with authentication
mosquitto_passwd -c /etc/mosquitto/passwd <username>
```

### Process Management with Systemd

Create service files for each component:

**`/etc/systemd/system/timeseries-collector.service`**
```ini
[Unit]
Description=Time-Series Data Collector
After=network.target postgresql.service

[Service]
Type=simple
User=timeseries
WorkingDirectory=/opt/timeseries
Environment="PYTHONUNBUFFERED=1"
ExecStart=/usr/bin/python3 /opt/timeseries/scripts/water_data_collector.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable timeseries-collector
sudo systemctl start timeseries-collector
sudo systemctl status timeseries-collector
```

## Docker Deployment

### Using Docker Compose

1. **Build Images**
   ```bash
   docker-compose build
   ```

2. **Start Services**
   ```bash
   docker-compose up -d
   ```

3. **View Logs**
   ```bash
   docker-compose logs -f lstm-gpu-0
   ```

4. **Stop Services**
   ```bash
   docker-compose down
   ```

### GPU Support

Ensure NVIDIA Container Toolkit is installed:
```bash
# Install nvidia-docker2
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# Test
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster 1.24+
- NVIDIA GPU Operator installed
- Helm 3+

### Deploy with Helm

```bash
# Create namespace
kubectl create namespace timeseries

# Deploy PostgreSQL
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgres bitnami/postgresql \
  --namespace timeseries \
  --set auth.database=demo \
  --set auth.username=demo \
  --set auth.password=demo

# Deploy Redis
helm install redis bitnami/redis \
  --namespace timeseries \
  --set auth.enabled=false

# Deploy application
kubectl apply -f k8s/ -n timeseries
```

### Scaling LSTM Services

```bash
# Scale to 4 GPU instances
kubectl scale deployment lstm-service --replicas=4 -n timeseries
```

## Model Training

### Training New Models

1. **Prepare Training Data**
   ```bash
   # Export data from database
   psql -h localhost -U demo -d demo -c \
     "COPY (SELECT timestamp, value FROM water_input WHERE feature='ai_cod1_cod' ORDER BY timestamp) TO STDOUT CSV HEADER" \
     > training_data.csv
   ```

2. **Train Single Feature**
   ```bash
   python scripts/train_lstm_models.py \
     --feature ai_cod1_cod \
     --data-source training_data.csv \
     --epochs 100 \
     --batch-size 32
   ```

3. **Train All Features**
   ```bash
   python scripts/train_lstm_models.py \
     --feature all \
     --data-source database \
     --epochs 100 \
     --batch-size 32
   ```

### Model Versioning

```bash
# Create MODEL directory structure
mkdir -p MODEL/v1.0/{ai_cod1_cod,ai_ph1_temp,ai_ph1_ph,ai_ss1_ss}

# Version models
cp MODEL/*.h5 MODEL/v1.0/
ln -sf v1.0 MODEL/current

# Update config to use versioned models
export MODEL_FOLDER=MODEL/current
```

### Hyperparameter Tuning

Edit `lstm_model_manager.py`:
```python
# Adjust LSTM architecture
model = build_lstm_model(
    time_steps=8,
    lstm_units=[128, 64, 32],  # Deeper network
    dropout_rate=0.3,           # More regularization
    learning_rate=0.0005        # Lower learning rate
)
```

## Monitoring and Maintenance

### Health Checks

```bash
# Check service status
curl http://localhost:3001/health

# Check database connection
psql -h localhost -U demo -d demo -c "SELECT 1;"

# Check MQTT broker
mosquitto_sub -h localhost -t '#' -C 1 -W 5

# Check Redis
redis-cli ping
```

### Performance Monitoring

**Prometheus Metrics** (add to services):
```python
from prometheus_client import Counter, Histogram, start_http_server

prediction_counter = Counter('predictions_total', 'Total predictions')
inference_time = Histogram('inference_seconds', 'Inference time')

# Start metrics server
start_http_server(8000)
```

**Query Performance**:
```sql
-- Monitor prediction latency
SELECT 
    feature,
    COUNT(*) as predictions,
    AVG(EXTRACT(EPOCH FROM (created_at - timestamp))) as avg_latency_seconds
FROM water_output
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY feature;
```

### Log Management

**Centralized Logging**:
```bash
# Configure rsyslog
sudo tee /etc/rsyslog.d/timeseries.conf <<EOF
:programname, isequal, "timeseries" /var/log/timeseries.log
EOF

sudo systemctl restart rsyslog
```

**Log Rotation**:
```bash
sudo tee /etc/logrotate.d/timeseries <<EOF
/var/log/timeseries.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 syslog adm
    sharedscripts
    postrotate
        systemctl reload rsyslog > /dev/null 2>&1 || true
    endscript
}
EOF
```

### Database Maintenance

```bash
# Vacuum and analyze
psql -h localhost -U demo -d demo -c "VACUUM ANALYZE;"

# Backup
pg_dump -h localhost -U demo demo > backup_$(date +%Y%m%d).sql

# Archive old data
psql -h localhost -U demo -d demo <<EOF
DELETE FROM water_input WHERE timestamp < NOW() - INTERVAL '90 days';
DELETE FROM water_output WHERE timestamp < NOW() - INTERVAL '90 days';
EOF
```

## Troubleshooting

### Common Issues

**1. GPU Out of Memory**
```bash
# Reduce GPU memory fraction
export GPU_MEMORY_FRACTION=0.3

# Or reduce batch processing
export TIME_WINDOW=6
```

**2. ZeroMQ Connection Timeout**
```bash
# Check if ports are available
netstat -tuln | grep 5548
netstat -tuln | grep 5561

# Increase timeout
# Edit config.py:
ZMQ_TIMEOUT = 10000  # 10 seconds
```

**3. Model Loading Fails**
```bash
# Verify model files exist
ls -lh MODEL/

# Check permissions
chmod 644 MODEL/*.h5

# Validate model format
python -c "from keras.models import load_model; load_model('MODEL/ai_cod1_cod.h5')"
```

**4. Database Connection Refused**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify connection parameters
psql -h localhost -U demo -d demo -c "SELECT version();"

# Check pg_hba.conf for access rules
sudo cat /etc/postgresql/14/main/pg_hba.conf
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run service in foreground
python scripts/water_lstm_service_improved.py 0

# Trace execution
python -m pdb scripts/water_lstm_service_improved.py 0
```

### Performance Issues

**High Latency**:
- Check network latency between services
- Verify database query performance
- Monitor GPU utilization: `nvidia-smi -l 1`
- Profile Python code: `python -m cProfile`

**Low Throughput**:
- Scale LSTM services horizontally
- Increase batch processing
- Optimize database indexes
- Use connection pooling

## Performance Tuning

### Database Optimization

```sql
-- Tune PostgreSQL config
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET maintenance_work_mem = '1GB';
ALTER SYSTEM SET work_mem = '64MB';
ALTER SYSTEM SET max_connections = 100;

-- Reload configuration
SELECT pg_reload_conf();
```

### GPU Optimization

```python
# config.py adjustments for production
GPU_MEMORY_FRACTION = 0.7  # Use more GPU memory
NUM_GPU = 4                # Use all available GPUs
NUM_CORES = 16             # Match CPU cores
```

### ZeroMQ Tuning

```python
# Adjust socket options for high throughput
socket.setsockopt(zmq.SNDHWM, 10000)  # Send high water mark
socket.setsockopt(zmq.RCVHWM, 10000)  # Receive high water mark
socket.setsockopt(zmq.LINGER, 0)       # No linger on close
```

---

**For additional support, consult the main README.md and source code documentation.**
