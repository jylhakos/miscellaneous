# Reverse Engineering Analysis

## What is Reverse Engineering in Software Architecture?

**Reverse engineering** is the process of analyzing existing source code to extract high-level architectural patterns, design decisions, and system behavior without access to original design documentation. It involves:

1. **Static Code Analysis**: Examining source code structure, dependencies, and relationships
2. **Dynamic Analysis**: Observing runtime behavior, message flows, and interactions
3. **Pattern Recognition**: Identifying architectural patterns and design principles
4. **Documentation Recreation**: Creating architecture diagrams and documentation from code

### Why Reverse Engineering?

- **Legacy System Understanding**: Systems without documentation
- **Modernization Planning**: Identify refactoring opportunities
- **Architecture Recovery**: Extract design patterns and architectural decisions
- **Knowledge Transfer**: Enable new team members to understand the system
- **Quality Assessment**: Evaluate code quality and architectural soundness

## Reverse Engineering This Microservices System

### Discovery Process

By analyzing the Python scripts in the `scripts/` folder, we applied reverse engineering techniques to uncover:

#### 1. **Architectural Pattern Discovery**

**Code Evidence**:
```python
# water_data_collector.py - Producer pattern
zmq_socket_pub = zmq_context_pub.socket(zmq.PUSH)
zmq_socket_pub.bind("tcp://*:%s" % port_iot_pub_0)

# water_LSTM_GPU_0.py - Consumer pattern
zmq_socket_sub = zmq_context_sub.socket(zmq.PULL)
zmq_socket_sub.connect("tcp://localhost:%s" % port_iot_sub)
```

**Discovered Pattern**: **Event-Driven Microservices Architecture**
- Producer-Consumer pattern using ZeroMQ PUSH-PULL sockets
- Asynchronous message passing
- Loose coupling between services

#### 2. **Component Relationship Analysis**

By tracing message flows through ports:

```
MQTT Broker (port 1883)
    ↓
Data Collector Service
    ↓ ZeroMQ PUSH (port 5548)
LSTM Inference Services (GPU 0-3)
    ↓ ZeroMQ PUSH (ports 5561-5564)
Output Processing Services
    ↓ Database Write
PostgreSQL Database
    ↓ REST API
Web Application (port 3001)
    ↓ WebSocket
Browser Clients
```

**Discovered Pattern**: **Pipeline Architecture with Fan-Out**
- Data flows through transformation stages
- Load balancing across multiple GPU services
- Fan-out pattern for parallel processing

#### 3. **Design Patterns Identified**

| Pattern | Evidence in Code | Purpose |
|---------|------------------|---------|
| **Producer-Consumer** | ZeroMQ PUSH-PULL sockets | Decouple message generation from consumption |
| **Pipeline** | Sequential data transformation stages | Process data through multiple steps |
| **Load Balancer** | ZeroMQ round-robin message distribution | Distribute load across GPU services |
| **Singleton** | `global model_is_loaded`, shared model instance | Single model instance per service |
| **Repository** | Database access in output services | Abstract data persistence |
| **Facade** | REST API in web application | Simplify client access to backend |

#### 4. **Technology Stack Discovery**

Reverse engineering import statements revealed:

```python
import zmq                    # → Messaging layer
import paho.mqtt.client       # → IoT data ingestion
from keras.models import load_model  # → ML model serving
import psycopg2               # → PostgreSQL database
import tensorflow as tf       # → Deep learning framework
```

**Architectural Layers**:
1. **Presentation Layer**: Express.js web server, Handlebars templates
2. **Application Layer**: LSTM inference services, output processors
3. **Data Layer**: PostgreSQL, Redis TimeSeries
4. **Integration Layer**: ZeroMQ, MQTT, Socket.IO

#### 5. **Scalability Analysis**

By examining multiple GPU service files:

```
water_LSTM_GPU_0.py  (port 5561)
water_LSTM_GPU_1.py  (port 5562)
water_LSTM_GPU_2.py  (port 5563)
water_LSTM_GPU_3.py  (port 5564)
```

**Discovered Pattern**: **Horizontal Scaling**
- Multiple identical services on different GPUs
- Independent failure domains
- Linear scalability with GPU count

#### 6. **Data Flow Analysis**

Tracing data transformations:

```python
# Input: Raw MQTT message
{"MESSAGE": {"PLACE": "HVSB", "METER": "...", "FEATURE": "ai_cod1_cod", "VALUE": 123.45}}

# Stage 1: Data Collection (water_data_collector.py)
#   - MQTT subscription
#   - JSON parsing
#   - ZeroMQ publishing

# Stage 2: Preprocessing (water_LSTM_GPU_0.py)
scaler = MinMaxScaler(feature_range=(0, 1))
dataset_scaled = scaler.fit_transform(dataset)

# Stage 3: Inference
model = load_model(MODEL_FOLDER + feature_name + '.h5')
prediction = model.predict(X_test)

# Stage 4: Denormalization
yhat = scaler.inverse_transform(prediction)

# Stage 5: Output (water_output_service_0.py)
#   - Database persistence
#   - WebSocket broadcasting
```

**Discovered Pattern**: **ETL Pipeline**
- Extract: MQTT data ingestion
- Transform: Normalization, windowing, LSTM inference
- Load: Database writes and real-time updates

## Reverse Engineering Tools Used

### Static Analysis Tools

| Tool | Purpose | Use Case |
|------|---------|----------|
| **Pylint** | Code quality analysis | Identify code smells, complexity metrics |
| **Pyreverse** | UML diagram generation | Generate class and package diagrams |
| **Radon** | Complexity metrics | Calculate cyclomatic complexity, maintainability index |
| **Vulture** | Dead code detection | Find unused code and imports |
| **Bandit** | Security vulnerability scanning | Identify security issues |

### Dynamic Analysis Tools

| Tool | Purpose | Use Case |
|------|---------|----------|
| **cProfile** | Performance profiling | Identify bottlenecks, hot paths |
| **py-spy** | Sampling profiler | Profile running processes |
| **tracemalloc** | Memory profiling | Track memory allocation |
| **strace** | System call tracing | Observe file I/O, network calls |

### Architecture Visualization Tools

| Tool | Purpose | Use Case |
|------|---------|----------|
| **Graphviz** | Graph visualization | Visualize dependency graphs |
| **PlantUML** | UML diagram creation | Document architecture |
| **Mermaid** | Markdown-based diagrams | Create flowcharts, sequence diagrams |
| **pydeps** | Python dependency visualization | Generate module dependency graphs |

### Network Analysis Tools

| Tool | Purpose | Use Case |
|------|---------|----------|
| **Wireshark** | Network protocol analyzer | Inspect ZeroMQ, MQTT traffic |
| **tcpdump** | Packet capture | Capture network messages |
| **netstat** | Network statistics | Identify listening ports, connections |

## Practical Reverse Engineering Workflow

### Step 1: Static Code Analysis

```bash
# Install analysis tools
pip install pylint radon pyreverse pydeps

# Analyze code quality
pylint scripts/water_LSTM_GPU_0.py

# Calculate complexity metrics
radon cc scripts/ -a

# Generate class diagrams
pyreverse -o png -p WaterQuality scripts/

# Visualize dependencies
pydeps scripts/water_data_collector.py --noshow --max-bacon 2
```

### Step 2: Dynamic Analysis

```bash
# Profile a running service
python -m cProfile -o profile.stats scripts/water_LSTM_GPU_0.py

# Visualize profile
python -m pstats profile.stats
# > sort cumtime
# > stats 20

# Memory profiling
python -m memory_profiler scripts/water_LSTM_GPU_0.py

# Real-time profiling
py-spy top --pid <process_id>
```

### Step 3: Network Traffic Analysis

```bash
# Capture ZeroMQ traffic
sudo tcpdump -i lo -A 'tcp port 5548 or tcp port 5561'

# Monitor MQTT messages
mosquitto_sub -h localhost -t 'api/v1/json/uploadmessage' -v

# Check active connections
netstat -tulpn | grep python
```

### Step 4: Architecture Documentation

```bash
# Generate module dependency graph
pydeps scripts/ --max-bacon 3 -o architecture.png

# Create UML diagrams
pyreverse -o png -p TimeSeries scripts/*.py

# Document discovered patterns in Markdown
```

## Key Findings from Reverse Engineering

### Strengths Identified

1.  **Clear Separation of Concerns**: Each service has a single responsibility
2.  **Scalable Architecture**: Horizontal scaling via multiple GPU services
3.  **Event-Driven Design**: Asynchronous, non-blocking communication
4.  **Technology Fit**: Appropriate tools for each layer (ZeroMQ for messaging, LSTM for forecasting)

### Areas for Modernization

1.  **Configuration Management**: Hard-coded ports and connection strings
2.  **Error Handling**: Limited retry logic and error recovery
3.  **Observability**: Minimal structured logging and monitoring
4.  **Testing**: No visible unit tests or integration tests
5.  **API Documentation**: No OpenAPI/Swagger specification

### Architectural Insights

- **Pattern**: Event-Driven Microservices with Pipeline Architecture
- **Communication**: Asynchronous message passing (ZeroMQ PUSH-PULL)
- **Scalability**: Horizontal scaling via service replication
- **Resilience**: Independent failure domains, but limited fault tolerance
- **Data Flow**: Unidirectional pipeline (Ingestion → Processing → Storage → Presentation)

## References

### Tools Documentation
- **Pylint**: https://pylint.org
- **Radon**: https://radon.readthedocs.io
- **Pyreverse**: https://pylint.readthedocs.io/en/latest/pyreverse.html
- **pydeps**: https://github.com/thebjorn/pydeps
- **Graphviz**: https://graphviz.org
- **PlantUML**: https://plantuml.com
- **Wireshark**: https://www.wireshark.org

### Architectural Patterns
- **Event-Driven Architecture**: https://martinfowler.com/articles/201701-event-driven.html
- **Microservices Patterns**: https://microservices.io/patterns/index.html
- **Enterprise Integration Patterns**: https://www.enterpriseintegrationpatterns.com
