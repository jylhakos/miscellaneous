# Python Virtual Environment Setup Guide

## What is a Virtual Environment?

A **Python virtual environment** is an isolated Python runtime environment that allows you to install packages and dependencies specific to a project without affecting the system-wide Python installation or other projects.

### Benefits

-  **Dependency Isolation**: Each project has its own dependencies
-  **Version Control**: Different projects can use different package versions
-  **Clean System**: System Python remains unmodified
-  **Reproducibility**: `requirements.txt` ensures consistent environments
-  **No Conflicts**: Avoid dependency hell between projects

## Virtual Environment: Development vs Production

### Development on Linux (Virtual Environment **RECOMMENDED**)

**Why use virtual environments in development?**

- Multiple projects with different dependencies
- Experimentation without affecting system
- Easy to recreate or delete environments
- Matches team development standards
- Testing different package versions

```bash
# Development workflow with venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python scripts/water_lstm_service_improved.py 0
```

### Production with Docker (Virtual Environment **NOT NEEDED**)

**Why Docker containers don't need virtual environments?**

-  **Container Isolation**: Docker provides OS-level isolation
-  **Single Application**: Each container runs one service
-  **Immutable Images**: Dependencies baked into image layers
-  **Smaller Images**: No extra venv overhead
-  **Standard Practice**: Official Python images install globally

```dockerfile
# Docker approach - NO venv needed
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt  # Global install
COPY . .
CMD ["python", "scripts/water_lstm_service_improved.py", "0"]
```

### Production on Linux Bare Metal (Virtual Environment **RECOMMENDED**)

**When deploying directly to Linux servers (without Docker):**

-  **Use virtual environment** for isolation
-  **Use systemd** for service management
-  **Use separate user** for security

```bash
# Production bare-metal deployment
sudo useradd -r -s /bin/false timeseries
sudo mkdir -p /opt/timeseries
sudo chown timeseries:timeseries /opt/timeseries

# Setup as timeseries user
sudo -u timeseries bash
cd /opt/timeseries
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Quick Decision Matrix

| Environment | Virtual Env? | Why? |
|-------------|--------------|------|
| **Local Development** |   YES | Isolate from system Python, team consistency |
| **Docker Production** | ❌ NO | Container provides isolation, simpler, smaller images |
| **Linux Production (Bare Metal)** |   YES | Multi-service isolation, security, dependency management |
| **CI/CD Pipeline** | ⚠️ OPTIONAL | Depends on runner type (bare metal: yes, Docker: no) |

## Setup Virtual Environment on Linux

### Method 1: Using venv (Built-in, Recommended)

```bash
# Navigate to project directory
cd /home/laptop/EXERCISES/MISCELLANEOUS/miscellaneous/TimeSeries

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (prompt should show (venv))
which python
# Output: /home/laptop/EXERCISES/.../TimeSeries/venv/bin/python

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installations
pip list

# Run services
cd scripts/
python water_lstm_service_improved.py 0
```

### Method 2: Using virtualenv (Third-party)

```bash
# Install virtualenv
pip install virtualenv

# Create virtual environment
virtualenv venv

# Or specify Python version
virtualenv -p python3.9 venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Method 3: Using conda (Data Science)

```bash
# Create conda environment
conda create -n timeseries python=3.9

# Activate
conda activate timeseries

# Install dependencies
pip install -r requirements.txt

# Or use conda packages
conda install tensorflow keras numpy pandas scikit-learn
```

## Activation and Deactivation

### Activating Virtual Environment

```bash
# On Linux/macOS
source venv/bin/activate

# Alternative syntax
. venv/bin/activate
```

**Verification**:
```bash
# Check Python path
which python
# Should show: /path/to/project/venv/bin/python

# Check pip path
which pip
# Should show: /path/to/project/venv/bin/pip

# Prompt changes
(venv) user@hostname:~/project$
```

### Deactivating Virtual Environment

```bash
# Deactivate (works from any directory)
deactivate

# Prompt returns to normal
user@hostname:~/project$
```

## Managing Dependencies

### Freezing Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install packages
pip install tensorflow keras numpy

# Generate requirements.txt
pip freeze > requirements.txt

# Or only project dependencies (cleaner)
pip list --format=freeze > requirements.txt
```

### Installing from requirements.txt

```bash
# Fresh environment
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# Or upgrade existing packages
pip install --upgrade -r requirements.txt
```

### Updating Dependencies

```bash
# Check outdated packages
pip list --outdated

# Update specific package
pip install --upgrade tensorflow

# Update all packages
pip install --upgrade $(pip list --outdated --format=freeze | cut -d = -f 1)

# Regenerate requirements.txt
pip freeze > requirements.txt
```

## Running Services with Virtual Environment

### Training LSTM Models

```bash
# Activate environment
source venv/bin/activate

# Run training script
cd scripts/
python train_lstm_models.py \
  --feature ai_cod1_cod \
  --data-source database \
  --epochs 100 \
  --batch-size 32

# Check generated model
ls -lh ../MODEL/
```

### Starting Individual Services

```bash
# Activate environment
source venv/bin/activate
cd scripts/

# Terminal 1: Data Collector
python water_data_collector.py

# Terminal 2: LSTM Service (GPU 0)
python water_lstm_service_improved.py 0

# Terminal 3: Output Service
python water_output_service_0.py

# Terminal 4: Web Application
node water_app.js
```

### Running in Background

```bash
# Activate environment
source venv/bin/activate
cd scripts/

# Start services in background
nohup python water_data_collector.py > ../logs/collector.log 2>&1 &
nohup python water_lstm_service_improved.py 0 > ../logs/lstm.log 2>&1 &
nohup python water_output_service_0.py > ../logs/output.log 2>&1 &

# Check processes
ps aux | grep python

# View logs
tail -f ../logs/*.log
```

## Systemd Service with Virtual Environment

For production deployment on Linux:

```bash
# Create systemd service file
sudo nano /etc/systemd/system/timeseries-lstm.service
```

```ini
[Unit]
Description=Time-Series LSTM Inference Service
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=timeseries
Group=timeseries
WorkingDirectory=/opt/timeseries/scripts
Environment="PATH=/opt/timeseries/venv/bin"
ExecStart=/opt/timeseries/venv/bin/python water_lstm_service_improved.py 0
Restart=always
RestartSec=10
StandardOutput=append:/var/log/timeseries/lstm.log
StandardError=append:/var/log/timeseries/lstm.error.log

[Install]
WantedBy=multi-user.target
```

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable timeseries-lstm.service

# Start service
sudo systemctl start timeseries-lstm.service

# Check status
sudo systemctl status timeseries-lstm.service

# View logs
sudo journalctl -u timeseries-lstm.service -f
```

## Docker vs Virtual Environment

### Development Workflow Comparison

**With Virtual Environment**:
```bash
# Setup (once)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Daily work
source venv/bin/activate
python scripts/water_lstm_service_improved.py 0
# Fast iteration, direct access to code
```

**With Docker**:
```bash
# Setup (once)
docker-compose build

# Daily work
docker-compose up lstm-gpu-0
# Slower rebuild, production-like environment
```

### When to Use Each

| Scenario | Best Choice | Reason |
|----------|-------------|--------|
| Local development, debugging | Virtual Environment | Fast iteration, direct code access |
| Testing integration | Docker Compose | Full stack simulation |
| Production deployment | Docker | Consistency, isolation, portability |
| Training models | Virtual Environment | GPU access, interactive debugging |
| CI/CD testing | Docker | Clean, reproducible environment |

## Troubleshooting

### Virtual Environment Not Activating

```bash
# Check if venv exists
ls -la venv/

# Recreate if corrupted
rm -rf venv/
python3 -m venv venv
source venv/bin/activate
```

### Wrong Python Version

```bash
# Check Python version
python --version

# Create with specific version
python3.9 -m venv venv
```

### Permission Denied

```bash
# Fix ownership
sudo chown -R $USER:$USER venv/

# Or recreate
rm -rf venv/
python3 -m venv venv
```

### ImportError: No module named X

```bash
# Verify virtual environment is active
which python

# Reinstall dependencies
pip install -r requirements.txt

# Check installed packages
pip list | grep tensorflow
```

### venv Not Found

```bash
# Install venv module (Ubuntu/Debian)
sudo apt-get install python3-venv

# Or use virtualenv
pip install virtualenv
virtualenv venv
```

## Best Practices

1.   **One venv per project**: Don't share virtual environments
2.   **Add venv/ to .gitignore**: Don't commit virtual environments
3.   **Use requirements.txt**: Track dependencies, not environments
4.   **Activate before work**: Always activate before running code
5.   **Update regularly**: Keep dependencies up to date
6.   **Document Python version**: Specify in README.md
7.   **Use Docker for production**: Virtual environments for development

## Quick Reference

```bash
# Create
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run code
python script.py

# Deactivate
deactivate

# Delete
rm -rf venv/
```

## Summary

- **Development on Linux**: Use virtual environment for isolation and flexibility
- **Production with Docker**: No virtual environment needed, containers provide isolation
- **Production on bare Linux**: Use virtual environment with systemd for service management
- **Team collaboration**: Commit `requirements.txt`, not `venv/` directory
- **Best of both**: Use venv for development, Docker for deployment
