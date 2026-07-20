# Renewable Energy Trading Platform with Time Series Forecasting

A microservices-based electronic trading platform for renewable energy derivatives that leverages LSTM deep learning models to predict electrical grid consumption and solar/wind generation patterns. This platform enables automated trading decisions based on real-time forecasts and market analytics.

## Table of Contents

- [Introduction](#introduction)
- [Energy Derivatives Background](#energy-derivatives-background)
- [SCADA Systems in Energy Derivatives Trading](#scada-systems-in-energy-derivatives-trading)
- [Time-Series Algorithm Comparison](#time-series-algorithm-comparison)
- [System Architecture](#system-architecture)
- [Event-Driven Processing Architecture](#event-driven-processing-architecture)
- [Microservices Architecture](#microservices-architecture)
- [Deep Learning with RNN and LSTM](#deep-learning-with-rnn-and-lstm)
- [Time-Series Data Pipeline](#time-series-data-pipeline)
- [Data Sources and Market Integration](#data-sources-and-market-integration)
- [Feature Engineering and Data Preparation](#feature-engineering-and-data-preparation)
- [Microservice Implementation Details](#microservice-implementation-details)
- [Trading Strategy and Derivatives Logic](#trading-strategy-and-derivatives-logic)
- [Docker Deployment Architecture](#docker-deployment-architecture)
- [Service Access and API Gateway](#service-access-and-api-gateway)
- [Security and Compliance](#security-and-compliance)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [References](#references)

## Introduction

The renewable energy market presents unique challenges due to the intermittent nature of wind and solar power generation. Electricity cannot be easily stored at grid scale, creating significant price volatility and imbalance risks. This platform addresses these challenges by combining:

- Real-time time-series forecasting using deep learning (LSTM/RNN architectures)
- Event-driven microservices for scalable data processing
- Automated trading strategies for energy derivatives (futures, options, forward contracts)
- Docker-based containerized deployment for local and production environments

## Energy Derivatives Background

Energy derivatives are financial instruments whose value derives from underlying energy commodities such as electricity, natural gas, or oil. According to research from Stanford University on [Energy Derivatives](http://large.stanford.edu/courses/2017/ph240/noordeh2/), these instruments serve functions in the energy market:

**Primary Derivative Types:**

- **Forward Contracts**: Bilateral agreements to buy/sell energy at a specific future date and price
- **Futures**: Standardized contracts traded on open exchanges with price transparency
- **Options**: Contracts providing the right (not obligation) to buy/sell at predetermined prices

**Risk Management Applications:**

The California energy crisis of 2000-2001 demonstrated the importance of hedging strategies. Wholesale power prices at the California-Oregon border surged from $30-60 per MWh to over $7000 per MWh. Utility providers that failed to hedge against spot market volatility faced severe financial consequences.

**Imbalance Risk in Renewable Energy:**

For renewable energy producers, derivatives hedge against two primary scenarios:

1. **Overproduction Risk**: Wind or solar generation exceeds day-ahead commitments, forcing sales at depressed or negative intraday prices
2. **Underproduction Risk**: Generation shortfalls require purchasing expensive balancing energy from spot markets to fulfill delivery obligations

## SCADA Systems in Energy Derivatives Trading

### What is SCADA and Why Does it Matter in Renewable Energy?

A **SCADA (Supervisory Control and Data Acquisition)** system is a software and hardware solution that enables real-time monitoring, control and data acquisition in industrial and energy infrastructures. Through sensors, controllers and digital platforms, these systems collect and process key information, facilitating decision-making and optimising the operation of complex installations such as power grids, generation plants and power distribution systems.

SCADA systems make it possible to monitor and control infrastructures such as electricity grids, wind farms or hydroelectric power plants in real time. For more information about SCADA technology and industrial applications, see [Iberdrola's guide to SCADA systems](https://www.iberdrola.com/about-us/our-innovation-model/scada-systems).

### SCADA as the Physical-to-Digital Bridge

In energy derivatives trading, a SCADA system serves as the foundational physical-to-digital bridge. It monitors and controls real-world power assets (like wind farms or power plants), providing the real-time data and remote execution needed to validate energy output and execute financial or physical derivatives contracts.

### How SCADA Supports the Derivatives Market

SCADA systems support the derivatives market by acting as the primary source of truth for the physical assets underlying the trades:

**1. Verifying Contract Deliverables**

Derivative contracts (such as futures, forwards, or swaps) rely on the physical generation or consumption of energy. SCADA provides continuous, real-time tracking of megawatt (MW) output, ensuring that a trading party is actually producing or consuming the energy they promised to deliver.

**2. Executing Algorithmic & Automated Trades**

Advanced SCADA systems integrate with algorithmic trading and Energy Trading Risk Management (ETRM) platforms. This allows operators to automatically adjust physical generation to capitalize on spot prices, capacity markets, and ancillary service bids.

**3. Compliance and Settlement**

Energy markets require strict, continuous data reporting to grid operators. SCADA logs provide the precise historical and real-time data necessary for auditing trades, verifying regulatory compliance, and executing financial settlement.

### How SCADA Operates

SCADA operates through a combination of hardware and software to manage the physical flow of energy:

**Data Acquisition**: Sensors measure real-time variables like voltage, active power, and wind speed.

**Supervisory Control**: Centralized systems allow operators or automated algorithms to remotely adjust equipment setpoints, manage circuit breakers, or alter energy direction.

**Alarming and Analytics**: SCADA immediately flags deviations from standard parameters, helping to avoid costly downtime that would cause a trader to breach a supply contract.

### The Link to ETRM Software

In modern energy trading, standalone SCADA data is piped directly into Energy Trading and Risk Management (ETRM) platforms. While SCADA manages the physical turbine, solar array, or battery, the ETRM system prices the trade, manages market risks, and handles the financial invoicing. SCADA acts as the "eyes and ears" that feed the ETRM platform the exact generation figures.

### Platform Integration Architecture

The following diagram maps out how this microservices architecture integrates the physical SCADA system with the data pipeline, machine learning models, and client-facing API:

```
        [ PHYSICAL ASSETS ]
    (Solar Arrays / Wind Farms)
                 │
                 ▼
       ┌──────────────────┐
       │   SCADA System   │ ──(Sensors: MW, Voltage, Weather)
       └──────────────────┘
                 │
                 ▼ (MQTT / Kafka Stream)
 ┌────────────────────────────────┐
 │     ETL Pipeline Service       │
 │  • Extract: Real-time Streams  │
 │  • Transform: Clean, Impute    │
 │  • Load: Time-Series Database  │
 └────────────────────────────────┘
                 │
                 ├─────────────────────────┐
                 ▼                         ▼
 ┌────────────────────────────────┐  ┌─────────────────────────────┐
 │    ML Forecasting Service      │  │  Client-Facing REST API     │
 │  • RNN / LSTM Sequences        │  │  • GET /predictions         │
 │  • Predicts Future Generation  │─▶│  • POST /hedging-signals    │
 └────────────────────────────────┘  └─────────────────────────────┘
                                                   │
                                                   ▼
                                       ┌──────────────────────┐
                                       │   Derivatives Desk   │
                                       │ (Solar/Wind Futures) │
                                       └──────────────────────┘
```

### Key Components

#### 1. Real-time ETL Pipeline

The ETL (Extract, Transform, Load) service processes high-velocity SCADA tags from fields into a usable format:

**Extract**: Ingests protocol streams (like MQTT, Kafka, or OPC UA) tracking target metrics:
- **Solar**: Irradiance, panel temperature, inverter DC/AC efficiency, and grid voltage
- **Wind**: Wind speed, wind direction, nacelle orientation, blade pitch, and ambient temperature

**Transform**: Cleans bad or missing sensor records through statistical imputation. It normalizes distinct time horizons into standardized 5-minute, 15-minute, or hourly intervals required by the deep learning network.

**Load**: Pipelines structured, time-stamped parameters into dedicated time-series databases (such as InfluxDB or TimescaleDB).

#### 2. Hybrid RNN + LSTM Forecasting Service

Physical weather and asset degradation introduce severe volatility into renewable generation. This service applies sequential deep learning to forecast future energy volumes:

**Sequence Processing**: Recurrent Neural Networks (RNN) and Long Short-Term Memory (LSTM) layers ingest the sequential historical SCADA data. They capture time-dependent features like solar diurnal patterns (day/night cycles) and wind ramp events (sudden changes in wind velocity).

**Generation Forecast**: Output layers project a rolling curve of expected asset capacity (MW) over standard futures delivery windows (e.g., Day-Ahead, Balance-of-Month).

**Trading Edge**: Accurate load and generation predictions minimize the basis risk of being under-hedged or paying grid imbalance penalties.

#### 3. Client-Facing REST API

This microservice serves as the digital interface for proprietary traders, risk managers, and external ETRM systems:

**Endpoints Offered**: Provides reliable access to predictions and underlying asset state:
- `GET /v1/assets/{id}/telemetry` – Fetch current SCADA state (e.g., current wind speed, active generation)
- `GET /v1/predictions/generation` – Retrieve rolling RNN/LSTM capacity forecasts (MWh)
- `POST /v1/trading/signals` – Evaluates forecast variances to trigger automated market buy/sell actions for solar/wind futures

**Performance**: Relies on caching layers (like Redis) to handle high-frequency requests from automated execution algorithms without straining the deep learning backend.

### Monetizing the Stack

This architecture directly optimizes how you trade financial and physical contracts:

| Contract Type | SCADA + Pipeline Action | ML Model Benefit | API / Trading Execution |
|---------------|------------------------|------------------|------------------------|
| **Day-Ahead Futures** | Tracks physical asset health and immediate baseline generation | Forecasts exact solar/wind curves for the next day's settlement | Automatically locks in prices to clear tomorrow's position |
| **Intraday / Spot Market** | Detects real-time deviations (e.g., sudden drop in wind speed) | Predicts how long a generation deficit will last | API alerts the desk to purchase spot energy to prevent delivery penalties |
| **Virtual PPA Swaps** | Aggregates precise multi-asset generation across regions | Projects long-term generation capacity over weeks | Simplifies financial settlement calculations against index prices |

## Time-Series Algorithm Comparison

Before implementing the LSTM-based forecasting system, it is essential to understand the comparative strengths of various time-series algorithms for energy market prediction.

### Traditional Statistical Methods

| Algorithm | Strengths | Weaknesses | Use Case |
|-----------|-----------|------------|----------|
| **ARIMA** | Simple, interpretable, fast training | Assumes linear relationships, struggles with seasonality | Short-term stationary price forecasting |
| **SARIMA** | Handles seasonal patterns | Requires manual parameter tuning, poor with non-linear dynamics | Day-ahead pricing with clear seasonal cycles |
| **Prophet** | Automatic seasonality detection, handles missing data | Limited for complex multivariate scenarios | Quick baseline forecasts with minimal tuning |
| **Exponential Smoothing** | Lightweight, fast inference | Cannot capture complex patterns | Simple trend extrapolation |

### Machine Learning Methods

| Algorithm | Strengths | Weaknesses | Use Case |
|-----------|-----------|------------|----------|
| **Random Forest** | Handles non-linearity, feature importance analysis | Does not capture temporal dependencies | Feature-rich spot price prediction |
| **XGBoost** | High accuracy with tabular data, robust to outliers | Requires extensive feature engineering for time dependencies | Ensemble forecasting with external variables |
| **SVR** | Effective in high-dimensional spaces | Computationally expensive, sensitive to kernel choice | Medium-term load forecasting |

### Deep Learning Methods

| Algorithm | Strengths | Weaknesses | Use Case |
|-----------|-----------|------------|----------|
| **LSTM** | Captures long-term dependencies, handles sequential data naturally | Requires large datasets, computationally intensive | Multi-step grid demand forecasting |
| **GRU** | Faster training than LSTM, fewer parameters | Slightly less expressive than LSTM | Real-time streaming predictions |
| **Bidirectional LSTM** | Leverages past and future context | Not suitable for true online predictions | Historical data analysis and backtesting |
| **Transformer** | Parallel processing, attention mechanisms | Very large data requirements, complex architecture | Long-horizon multi-region forecasting |
| **Conv1D + LSTM** | Extracts local patterns before sequential modeling | Architecture complexity | Detecting sudden demand spikes |

### Recommendation for Energy Trading

**Selected Architecture: Stacked LSTM with Dropout**

For solar and wind energy derivatives trading, LSTM networks provide the optimal balance between accuracy and operational feasibility:

- **Sequential Nature**: Grid consumption and generation exhibit strong temporal autocorrelation
- **Non-linear Dynamics**: Weather variables and market clearing prices have complex interdependencies
- **Multi-step Forecasting**: Trading strategies require predictions across 15-minute to 24-hour horizons
- **Negative Price Handling**: Unlike traditional markets, European power markets frequently exhibit negative clearing prices during renewable oversupply, requiring robust non-linear modeling

## System Architecture

The platform implements a modular, event-driven architecture that decouples data ingestion, machine learning inference, market analytics, and trade execution into independent microservices.

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        RENEWABLE ENERGY TRADING PLATFORM                │
└─────────────────────────────────────────────────────────────────────────┘

  [ Grid Telemetry ]              [ Weather Feeds ]         [ Market Data ]
  [ SCADA Systems  ]              [ Solar/Wind APIs]        [ Nord Pool   ]
  [ Smart Meters   ]              [ Cloud Coverage ]        [ EPEX SPOT   ]
         │                               │                         │
         └───────────────┬───────────────┘                         │
                         ▼                                         ▼
         ┌───────────────────────────┐              ┌─────────────────────┐
         │  Data Ingestion Service   │              │ Market Analytics    │
         │  (Python / FastStream)    │              │ Service (Go/Java)   │
         │  - MQTT / WebSocket       │              │ - WebSocket / FIX   │
         │  - Schema Validation      │              │ - Order Book Feed   │
         └──────────┬────────────────┘              └──────────┬──────────┘
                    │                                           │
                    ▼                                           ▼
         ┌──────────────────────────────────────────────────────────────┐
         │                    Apache Kafka Message Broker               │
         │   Topics:                                                    │
         │   - grid-consumption-raw                                     │
         │   - demand-forecasts-15m / demand-forecasts-30m              │
         │   - market-ticks-raw                                         │
         └──────────┬───────────────────────────────┬───────────────────┘
                    │                               │
        ┌───────────▼──────────┐         ┌──────────▼───────────────┐
        │  TimescaleDB         │         │  LSTM Inference Service  │
        │  (Time-Series Store) │◄────────│  (TensorFlow/PyTorch)    │
        │  - Historical data   │         │  - Model Loading         │
        │  - Feature archive   │         │  - Sliding Window Buffer │
        └──────────────────────┘         │  - Real-time Predictions │
                                         └─────────┬────────────────┘
                                                   │
                                                   ▼
                                         [ Kafka Topic ]
                                      demand-forecasts-15m
                                                   │
                                                   ▼
                               ┌───────────────────────────────────┐
                               │  Trading Strategy Service (OMS)   │
                               │  - Imbalance Risk Calculation     │
                               │  - Derivative Position Management │
                               │  - Stop-Loss / Take-Profit Logic  │
                               └──────────────┬────────────────────┘
                                              │
                                              ▼
                               ┌──────────────────────────────┐
                               │   Energy Exchange API        │
                               │   (ICE / CME / Mock Service) │
                               │   - Order Execution          │
                               │   - Position Reconciliation  │
                               └──────────────────────────────┘
```

### Data Flow Sequence

```
┌──────────┐       ┌──────────┐       ┌──────────┐       ┌──────────┐
│  SCADA   │──(1)─▶│ Ingestion│──(2)─▶│  Kafka   │──(3)─▶│  LSTM    │
│ Systems  │       │ Service  │       │  Broker  │       │ Service  │
└──────────┘       └──────────┘       └──────────┘       └────┬─────┘
                                                               │
                                                              (4)
                                                               │
┌──────────┐       ┌──────────┐       ┌──────────┐       ┌───▼──────┐
│ Exchange │◀─(7)──│ Trading  │◀─(6)──│  Kafka   │◀─(5)──│ Forecast │
│   API    │       │ Strategy │       │  Topic   │       │  Output  │
└──────────┘       └──────────┘       └──────────┘       └──────────┘

(1) Raw telemetry streaming
(2) Publish to grid-consumption-raw topic
(3) LSTM consumes and buffers 24-hour window
(4) Model inference produces demand forecast
(5) Publish prediction to demand-forecasts-15m
(6) Trading service evaluates imbalance risk
(7) Execute derivative order (buy/sell signal)
```

## Event-Driven Processing Architecture

Event-driven architecture enables the platform to process high-velocity streaming data from renewable energy sources and financial markets with minimal latency and maximum scalability.

### Core Principles

**1. Asynchronous Message Passing**

Services communicate exclusively through Kafka topics rather than synchronous HTTP requests. This decoupling provides:

- **Fault Tolerance**: If the Trading Strategy service fails, the LSTM Inference service continues producing forecasts that are buffered in Kafka
- **Horizontal Scalability**: Multiple LSTM inference containers can consume from partitioned Kafka topics in parallel
- **Replay Capability**: Historical events can be replayed for backtesting or model retraining

**2. Event Sourcing**

Every state change in the system is captured as an immutable event:

```json
{
  "event_id": "evt_20260719_070015_grid_zone1",
  "event_type": "GridConsumptionMeasured",
  "timestamp": "2026-07-19T07:00:15Z",
  "region_id": "wind_farm_zone_1",
  "payload": {
    "actual_mw": 42.5,
    "wind_speed_ms": 12.4,
    "solar_irradiance": 0.0
  }
}
```

**3. Consumer Groups and Partitioning**

Kafka partitions events by region_id, ensuring that all consumption data from a specific wind/solar farm arrives at the same LSTM inference worker, maintaining the sequential integrity of the sliding window buffer.

**4. Exactly-Once Semantics**

Trade execution requires exactly-once processing guarantees. The Trading Strategy service uses Kafka transactions to ensure that a single forecast event never triggers duplicate orders.

### Streaming Data Processing Flow

```
[ Renewable Energy Source ] ──▶ [ MQTT / WebSocket ]
                                          │
                                          ▼
                            ┌─────────────────────────┐
                            │  Ingestion Transformer  │
                            │  - Schema validation    │
                            │  - Timestamp alignment  │
                            │  - Feature extraction   │
                            └────────────┬────────────┘
                                         │
                                         ▼
                            ┌─────────────────────────┐
                            │    Kafka Producer       │
                            │  Topic: grid-raw        │
                            │  Partition Key: region  │
                            └────────────┬────────────┘
                                         │
                                    [ Kafka Cluster ]
                                         │
                    ┌────────────────────┼────────────────────┐
                    ▼                    ▼                    ▼
            [ Consumer Group: LSTM-workers ]
         ┌──────────┐         ┌──────────┐         ┌──────────┐
         │  Worker  │         │  Worker  │         │  Worker  │
         │  Region1 │         │  Region2 │         │  Region3 │
         └──────────┘         └──────────┘         └──────────┘
```

## Microservices Architecture

The platform decomposes functionality into specialized, independently deployable services that communicate via Kafka and REST APIs.

### Microservice Catalog

#### 1. Data Ingestion Service

**Technology Stack**: Python, FastStream, confluent-kafka, MQTT

**Responsibilities**:
- Connect to renewable energy SCADA systems via MQTT or WebSocket protocols
- Retrieve real-time weather data from external APIs (wind speed, solar irradiance, cloud coverage, temperature)
- Merge generation telemetry with grid consumption measurements
- Validate data schemas and handle missing/corrupted sensor readings
- Publish normalized events to Kafka topic `grid-consumption-raw`

**Key Operations**:
- Forward-fill missing values for sensor dropout periods up to 5 minutes
- Timestamp synchronization across heterogeneous data sources
- Regional aggregation for distributed solar installations

#### 2. LSTM Inference Service

**Technology Stack**: Python, TensorFlow/Keras, confluent-kafka, NumPy

**Responsibilities**:
- Maintain sliding window buffers (96 time steps = 24 hours of 15-minute intervals) per production region
- Load pre-trained LSTM model from shared Docker volume
- Execute forward inference passes to generate demand forecasts
- Publish predictions to Kafka topic `demand-forecasts-15m`

**Key Operations**:
- Min-Max feature scaling using pre-computed normalization constants
- Stateful window management with automatic buffer rotation
- Batch prediction for multiple regions when horizontal scaling is deployed

**Model Loading Pattern**:

```python
import tensorflow as tf
import os

MODEL_PATH = os.getenv("MODEL_PATH", "/models/lstm_demand_model.h5")
model = tf.keras.models.load_model(MODEL_PATH)
```

#### 3. Market Analytics Service

**Technology Stack**: Go or Java, WebSocket clients, FIX protocol libraries

**Responsibilities**:
- Establish persistent connections to European energy exchanges (Nord Pool, EPEX SPOT)
- Parse order book depth and clearing price feeds
- Track bid-ask spreads and liquidity indicators
- Publish market snapshot events to Kafka topic `market-ticks-raw`

**Key Operations**:
- Reconnection logic with exponential backoff for WebSocket failures
- FIX protocol message parsing for institutional exchange APIs
- Rate limiting and compliance with exchange API usage policies

#### 4. Trading Strategy and Order Management Service

**Technology Stack**: Python or Go, confluent-kafka, REST clients

**Responsibilities**:
- Subscribe to both `demand-forecasts-15m` and `market-ticks-raw` topics
- Calculate imbalance risk by comparing forecasted generation against day-ahead contract commitments
- Generate buy/sell signals for energy derivative instruments
- Enforce position limits, stop-loss thresholds, and margin requirements
- Execute orders via exchange APIs or mock trading endpoints

**Key Operations**:
- Delta calculation: `imbalance = predicted_generation - committed_delivery`
- Risk-adjusted position sizing using volatility-based models
- Order validation and pre-trade compliance checks

**Trading Logic Decision Tree**:

```
IF imbalance > +2.5 MW THEN
    Signal: SELL SHORT intraday futures
    Reason: Overproduction will depress clearing prices

ELSE IF imbalance < -2.5 MW THEN
    Signal: BUY LONG intraday call options
    Reason: Underproduction requires expensive balancing purchases

ELSE
    Signal: HOLD
    Reason: Generation aligned with commitments
```

#### 5. Model Training Service

**Technology Stack**: Python, TensorFlow/Keras, Apache Airflow, TimescaleDB

**Responsibilities**:
- Extract historical time-series data from TimescaleDB on a daily schedule
- Perform feature engineering and train/test split
- Train LSTM model with hyperparameter optimization
- Validate model performance using holdout data
- Save trained model to shared volume for inference service consumption

**Deployment Pattern**: Scheduled batch job orchestrated by Apache Airflow, not a persistent service

### Service Communication Patterns

**Synchronous (REST API)**:
- Admin dashboard querying service health metrics
- Manual model deployment triggers

**Asynchronous (Kafka Events)**:
- All data pipeline and trading workflow interactions
- Guaranteed message ordering per partition key (region_id)

## Deep Learning with RNN and LSTM

Long Short-Term Memory networks are a specialized form of Recurrent Neural Networks designed to capture long-term temporal dependencies in sequential data. For renewable energy forecasting, LSTMs address the vanishing gradient problem inherent in traditional RNNs when learning patterns across extended time horizons.

### Why LSTM for Energy Forecasting

**Temporal Dependencies in Grid Demand**:

Grid consumption exhibits hierarchical patterns:
- **Intra-day cycles**: Morning and evening demand peaks
- **Weekly cycles**: Weekday vs. weekend consumption profiles
- **Seasonal cycles**: Summer cooling load vs. winter heating load
- **Weather coupling**: Non-linear relationships between temperature, cloud cover, and solar generation

Traditional statistical models like ARIMA assume linear relationships and struggle with these nested temporal structures. LSTMs learn these patterns directly from data through recurrent connections and gating mechanisms.

### LSTM Architecture Components

**1. Memory Cell State (Ct)**

A conveyor belt that carries information across time steps with minimal modification, enabling long-term memory.

**2. Forget Gate (ft)**

Controls which information from the previous cell state should be discarded:

```
ft = σ(Wf · [ht-1, xt] + bf)
```

Where σ is the sigmoid activation function, producing values between 0 (forget completely) and 1 (retain completely).

**3. Input Gate (it)**

Determines which new information should be added to the cell state:

```
it = σ(Wi · [ht-1, xt] + bi)
C̃t = tanh(WC · [ht-1, xt] + bC)
```

**4. Output Gate (ot)**

Controls which parts of the cell state should influence the hidden state output:

```
ot = σ(Wo · [ht-1, xt] + bo)
ht = ot ⊙ tanh(Ct)
```

### Platform LSTM Model Architecture

**Network Configuration for 15-Minute Grid Demand Forecasting**:

```python
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

# Model hyperparameters
WINDOW_LENGTH = 96      # 24 hours × 4 (15-min intervals)
NUM_FEATURES = 3        # [actual_mw, wind_speed_ms, solar_irradiance]
HORIZON_LENGTH = 1      # Predict next 15-minute interval
LSTM_UNITS_L1 = 64
LSTM_UNITS_L2 = 32
DROPOUT_RATE = 0.2

model = Sequential([
    # First LSTM layer with return sequences
    LSTM(LSTM_UNITS_L1, 
         return_sequences=True, 
         input_shape=(WINDOW_LENGTH, NUM_FEATURES)),
    
    # Dropout for regularization
    Dropout(DROPOUT_RATE),
    
    # Second LSTM layer
    LSTM(LSTM_UNITS_L2),
    
    # Dropout for regularization
    Dropout(DROPOUT_RATE),
    
    # Dense output layer for regression
    Dense(HORIZON_LENGTH)
])

# Compile with Adam optimizer and MSE loss
model.compile(
    optimizer='adam',
    loss='mse',
    metrics=['mae']
)

# Model summary
model.summary()
```

**Architecture Rationale**:

- **Stacked LSTM Layers**: The first layer extracts temporal features across the 24-hour window; the second layer learns higher-order patterns
- **return_sequences=True**: Enables the first LSTM to pass sequential outputs to the second layer
- **Dropout Layers**: Prevent overfitting by randomly deactivating 20% of neurons during training
- **Dense Output**: Single neuron for univariate regression (predicting MW consumption)

### Training Data Preparation

**1. Feature Scaling**

LSTM performance degrades with unnormalized features. Apply Min-Max scaling:

```python
from sklearn.preprocessing import MinMaxScaler
import numpy as np

# Fit scaler on training data only
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_train = scaler.fit_transform(train_data)
scaled_test = scaler.transform(test_data)

# Save scaler parameters for inference service
np.save('/models/scaler_min.npy', scaler.data_min_)
np.save('/models/scaler_max.npy', scaler.data_max_)
```

**2. Handling Missing Values**

Forward-fill sensor dropouts:

```python
import pandas as pd

df = pd.read_csv('grid_data.csv')
df['actual_mw'] = df['actual_mw'].fillna(method='ffill', limit=20)
df = df.dropna()  # Drop remaining gaps longer than 5 hours
```

**3. Time-Series Windowing**

Create supervised learning samples using sliding windows:

```python
def create_sequences(data, window_size, horizon):
    X, y = [], []
    for i in range(len(data) - window_size - horizon + 1):
        X.append(data[i:i+window_size])
        y.append(data[i+window_size+horizon-1, 0])  # Target: actual_mw
    return np.array(X), np.array(y)

X_train, y_train = create_sequences(scaled_train, WINDOW_LENGTH, HORIZON_LENGTH)
X_test, y_test = create_sequences(scaled_test, WINDOW_LENGTH, HORIZON_LENGTH)

print(f"X_train shape: {X_train.shape}")  # (samples, 96, 3)
print(f"y_train shape: {y_train.shape}")  # (samples,)
```

**4. Model Training**

```python
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# Define callbacks
early_stop = EarlyStopping(
    monitor='val_loss',
    patience=10,
    restore_best_weights=True
)

checkpoint = ModelCheckpoint(
    '/models/lstm_demand_model.h5',
    monitor='val_loss',
    save_best_only=True
)

# Train model
history = model.fit(
    X_train, y_train,
    epochs=100,
    batch_size=32,
    validation_split=0.2,
    callbacks=[early_stop, checkpoint],
    verbose=1
)
```

### Alternative Deep Learning Architectures

**Bidirectional LSTM**

Processes sequences in both forward and backward directions, useful for offline backtesting:

```python
from tensorflow.keras.layers import Bidirectional

model = Sequential([
    Bidirectional(LSTM(64, return_sequences=True), 
                  input_shape=(WINDOW_LENGTH, NUM_FEATURES)),
    Dropout(0.2),
    Bidirectional(LSTM(32)),
    Dropout(0.2),
    Dense(HORIZON_LENGTH)
])
```

**CNN-LSTM Hybrid**

Convolutional layers extract local patterns before LSTM processes sequences:

```python
from tensorflow.keras.layers import Conv1D, MaxPooling1D

model = Sequential([
    Conv1D(filters=64, kernel_size=3, activation='relu', 
           input_shape=(WINDOW_LENGTH, NUM_FEATURES)),
    MaxPooling1D(pool_size=2),
    LSTM(64, return_sequences=True),
    Dropout(0.2),
    LSTM(32),
    Dropout(0.2),
    Dense(HORIZON_LENGTH)
])
```

## Time-Series Data Pipeline

Building a robust data pipeline is essential for training accurate LSTM models and enabling real-time inference.

### Data Sources and Market Integration

**European Energy Markets**

To train RNN and LSTM models for algorithmic trading in European electricity markets, you must integrate day-ahead and intraday price histories, physical system constraints, and weather variables.

**Nord Pool**

The leading power market in the Nordic and Baltic regions. Access historical and live physical spot prices through the Nord Pool Data Manager.

- **API Endpoint**: `https://data.nordpoolgroup.com/auction/day-ahead/prices`
- **Parameters**: `deliveryDate`, `currency=EUR`, `aggregation=DeliveryPeriod`, `deliveryAreas=AT,FI,SE`
- **Historical Range**: Data available from 1995 to present
- **Update Frequency**: Hourly day-ahead auction results published at 12:42 CET

**Example API Call**:

```bash
curl "https://data.nordpoolgroup.com/auction/day-ahead/prices?deliveryDate=latest&currency=EUR&aggregation=DeliveryPeriod&deliveryAreas=FI"
```

**EPEX SPOT**

Central Western European power exchange covering Germany, France, Austria, Belgium, Netherlands, Luxembourg, Switzerland.

- **Data Portal**: EPEX SPOT Web API (requires registration)
- **Products**: Day-ahead auction, intraday continuous, intraday auction
- **Key Metrics**: Clearing prices, traded volumes, cross-border flows

**ENTSO-E Transparency Platform**

European Network of Transmission System Operators provides:

- Real-time generation by source (wind, solar, nuclear, hydro, thermal)
- Actual vs. forecasted renewable production
- Cross-border transmission capacities
- System-wide load forecasts

**API Access**: RESTful API with free registration at `https://transparency.entsoe.eu/`

**Weather Data Integration**

Solar and wind generation forecasting requires meteorological inputs:

- **OpenWeatherMap API**: Solar irradiance, cloud coverage, UV index
- **Meteomatics API**: High-resolution wind speed forecasts at turbine hub height
- **ECMWF ERA5**: Historical reanalysis data for model training

### Feature Engineering Pipeline

Raw data must be transformed into LSTM-compatible features.

**Temporal Features**

Encode cyclical time patterns using sine/cosine transformations:

```python
import numpy as np

def create_temporal_features(df):
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['month'] = df['timestamp'].dt.month
    
    # Cyclical encoding
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
    df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
    
    return df
```

**Physical Ratios**

Calculate net load proxy:

```python
df['net_load'] = df['total_demand_mw'] - (df['wind_generation_mw'] + df['solar_generation_mw'])
df['renewable_penetration'] = (df['wind_generation_mw'] + df['solar_generation_mw']) / df['total_demand_mw']
```

**Market Momentum Indicators**

```python
# Price lagged differentials
df['price_lag_1h'] = df['clearing_price_eur'].shift(4)  # 4 × 15min = 1 hour
df['price_lag_24h'] = df['clearing_price_eur'].shift(96)
df['price_momentum_1h'] = df['clearing_price_eur'] - df['price_lag_1h']
df['price_momentum_24h'] = df['clearing_price_eur'] - df['price_lag_24h']

# Rolling volatility
df['price_volatility_24h'] = df['clearing_price_eur'].rolling(window=96).std()
```

**Handling Negative Prices**

European power markets frequently exhibit negative prices during renewable oversupply. Avoid log transformations; use symmetric log or quantile transformers:

```python
from sklearn.preprocessing import QuantileTransformer

# Quantile transformer handles negative values and outliers
qt = QuantileTransformer(output_distribution='normal')
df['price_transformed'] = qt.fit_transform(df[['clearing_price_eur']])
```

### Data Storage Architecture

**TimescaleDB for Historical Data**

PostgreSQL extension optimized for time-series workloads:

```sql
CREATE TABLE grid_consumption (
    timestamp TIMESTAMPTZ NOT NULL,
    region_id TEXT NOT NULL,
    actual_mw DOUBLE PRECISION,
    wind_speed_ms DOUBLE PRECISION,
    solar_irradiance DOUBLE PRECISION,
    clearing_price_eur DOUBLE PRECISION
);

-- Convert to hypertable for automatic partitioning
SELECT create_hypertable('grid_consumption', 'timestamp');

-- Create index on region and timestamp
CREATE INDEX ON grid_consumption (region_id, timestamp DESC);
```

**Kafka for Streaming Ingestion**

Route live data through message broker:

```
[ Raw APIs ] ──▶ [ Kafka ] ──▶ [ TimescaleDB ] ──▶ [ LSTM Training ]
                     │
                     └──▶ [ LSTM Inference Service ]
```

## Microservice Implementation Details

#### Data Ingestion Service
- `services/ingestion_service/main.py`: Streams grid consumption data to Kafka
- `services/ingestion_service/Dockerfile`: Container configuration
- `services/ingestion_service/requirements.txt`: Service dependencies

#### LSTM Inference Service
- `services/lstm_service/main.py`: Real-time LSTM predictions with sliding window
- `services/lstm_service/Dockerfile`: Container configuration
- `services/lstm_service/requirements.txt`: TensorFlow and Kafka dependencies

#### Trading Strategy Engine
- `services/trading_engine/main.py`: Automated trading decisions based on forecasts
- `services/trading_engine/Dockerfile`: Container configuration
- `services/trading_engine/requirements.txt`: Service dependencies

### 4. Model Training Pipeline
- `training/train_lstm.py`: Complete LSTM training script with early stopping
- `training/feature_engineering.py`: Time-series feature creation utilities
- `training/requirements.txt`: Training dependencies

### 5. Database Configuration
- `config/timescaledb_init.sql`: Database schema for time-series data
- `config/kafka_topics.json`: Kafka topic definitions and configurations

### 6. Testing Suite
- `tests/test_lstm_service.py`: Unit tests for LSTM inference
- `tests/test_trading_engine.py`: Unit tests for trading logic
- `tests/test_integration.py`: End-to-end integration tests

### 7. Data Directories
- `data/raw/`: Historical grid consumption data
- `data/processed/`: Cleaned and scaled datasets
- `models/`: Trained LSTM models and scaler parameters
- `notebooks/`: Jupyter notebooks for analysis

### Data Ingestion Service

**Python Implementation** (services/ingestion_service/main.py):

```python
import os
import json
import requests
from confluent_kafka import Producer
from datetime import datetime
import time

KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092")
NORD_POOL_API = "https://data.nordpoolgroup.com/auction/day-ahead/prices"
POLL_INTERVAL = 900  # 15 minutes

producer = Producer({'bootstrap.servers': KAFKA_BROKERS})

def fetch_market_data(region="FI"):
    """Fetch latest Nord Pool pricing data"""
    params = {
        'deliveryDate': 'latest',
        'currency': 'EUR',
        'aggregation': 'DeliveryPeriod',
        'deliveryAreas': region
    }
    response = requests.get(NORD_POOL_API, params=params)
    return response.json()

def fetch_scada_telemetry():
    """Simulate SCADA system telemetry"""
    # In production, connect to actual MQTT broker
    return {
        'actual_mw': 42.5,
        'wind_speed_ms': 12.4,
        'solar_irradiance': 150.0
    }

def publish_to_kafka(topic, key, payload):
    producer.produce(
        topic,
        key=key.encode('utf-8'),
        value=json.dumps(payload).encode('utf-8')
    )
    producer.flush()

print("Data Ingestion Service Started")

while True:
    try:
        # Collect telemetry
        telemetry = fetch_scada_telemetry()
        
        # Construct payload
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "region_id": "wind_farm_zone_1",
            "actual_mw": telemetry['actual_mw'],
            "wind_speed_ms": telemetry['wind_speed_ms'],
            "solar_irradiance": telemetry['solar_irradiance']
        }
        
        # Publish to Kafka
        publish_to_kafka('grid-consumption-raw', payload['region_id'], payload)
        print(f"Published: {payload}")
        
        time.sleep(POLL_INTERVAL)
        
    except Exception as e:
        print(f"Error in ingestion loop: {e}")
        time.sleep(60)
```

### LSTM Inference Service

**Complete Implementation** (services/lstm_service/main.py):

```python
import os
import json
import numpy as np
import tensorflow as tf
from confluent_kafka import Consumer, Producer, KafkaError

# Configuration
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092")
MODEL_PATH = os.getenv("MODEL_PATH", "/models/lstm_demand_model.h5")
WINDOW_SIZE = 96  # 24 hours * 4 intervals per hour
NUM_FEATURES = 3  # [actual_mw, wind_speed_ms, solar_irradiance]

# Min-Max Normalization Constants (Example Values)
SCALER_MIN = np.array([0.0, 0.0, 0.0])
SCALER_MAX = np.array([200.0, 30.0, 1000.0])

def scale_features(raw_features):
    return (np.array(raw_features) - SCALER_MIN) / (SCALER_MAX - SCALER_MIN + 1e-8)

def descale_target(scaled_val):
    return scaled_val * (SCALER_MAX[0] - SCALER_MIN[0]) + SCALER_MIN[0]

# Load Trained Keras Model
model = tf.keras.models.load_model(MODEL_PATH)

# In-memory sliding window buffer per production region
region_buffers = {}

# Kafka Setup
consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKERS,
    'group.id': 'lstm-inference-group',
    'auto.offset.reset': 'latest'
})
consumer.subscribe(['grid-consumption-raw'])

producer = Producer({'bootstrap.servers': KAFKA_BROKERS})

print("LSTM Inference Service Started. Listening for 15-minute ticks...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Kafka Error: {msg.error()}")
                break

        # Parse Incoming Stream Metric
        data = json.loads(msg.value().decode('utf-8'))
        region = data['region_id']
        
        # Extract features
        features = [data['actual_mw'], data['wind_speed_ms'], data['solar_irradiance']]
        scaled = scale_features(features)

        # Update sliding window state
        if region not in region_buffers:
            region_buffers[region] = []
        
        region_buffers[region].append(scaled)
        
        # Enforce rolling 24-hour limit
        if len(region_buffers[region]) > WINDOW_SIZE:
            region_buffers[region].pop(0)

        # Run prediction if window state is fully ready
        if len(region_buffers[region]) == WINDOW_SIZE:
            # Prepare tensor array input shape: [Batch=1, TimeSteps=96, Features=3]
            input_tensor = np.array([region_buffers[region]], dtype=np.float32)
            
            # Executing forward inference pass
            scaled_prediction = model.predict(input_tensor, verbose=0)[0][0]
            predicted_mw = float(descale_target(scaled_prediction))

            # Publish Forecast Event payload
            outbound_payload = {
                "timestamp": data['timestamp'],
                "forecast_target_time": (np.datetime64(data['timestamp']) + np.timedelta64(15, 'm')).astype(str) + "Z",
                "region_id": region,
                "predicted_mw": round(predicted_mw, 2)
            }
            
            producer.produce(
                'demand-forecasts-15m',
                key=region.encode('utf-8'),
                value=json.dumps(outbound_payload).encode('utf-8')
            )
            producer.flush()

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
```

### Trading Strategy and Execution Service

**Implementation** (services/trading_engine/main.py):

```python
import os
import json
from confluent_kafka import Consumer

KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092")
IMBALANCE_THRESHOLD_MW = float(os.getenv("TRADING_THRESHOLD_MW", "2.5"))

# Dummy registry representing your fixed Day-Ahead forward sale delivery commitments
DAY_AHEAD_COMMITMENTS = {
    "wind_farm_zone_1": 40.0  # Enterprise committed to deliver 40 MW this hour
}

consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKERS,
    'group.id': 'trading-strategy-group',
    'auto.offset.reset': 'latest'
})
consumer.subscribe(['demand-forecasts-15m'])

print("Trading Engine Online. Evaluating positions against Keras model updates...")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            continue

        forecast = json.loads(msg.value().decode('utf-8'))
        region = forecast['region_id']
        predicted_generation = forecast['predicted_mw']
        
        committed_mw = DAY_AHEAD_COMMITMENTS.get(region, 0.0)
        imbalance = predicted_generation - committed_mw

        print(f"Region: {region} | Forecast: {predicted_generation}MW | Committed: {committed_mw}MW | Delta: {imbalance:.2f}MW")

        # Trading Financial Decisions Execution Logic
        if imbalance > IMBALANCE_THRESHOLD_MW:
            # Overproduction Risk: Extra power will drop Intraday Market clearing price.
            # Strategy: Short futures or buy puts immediately to protect asset revenue.
            print(f"[TRADE SIGNAL] ORDER -> SELL SHORT Intraday Derivative for {abs(imbalance):.2f} MW to hedge OVERPRODUCTION risk.")
            
        elif imbalance < -IMBALANCE_THRESHOLD_MW:
            # Underproduction Deficit Penalty Risk: Forced to purchase balancing grid penalties.
            # Strategy: Go Long on Intraday Hourly Options to secure replacement supply cheaply.
            print(f"[TRADE SIGNAL] ORDER -> BUY LONG Intraday Derivative for {abs(imbalance):.2f} MW to hedge UNDERPRODUCTION penalty.")

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
```

## Trading Strategy and Derivatives Logic

### The Imbalance Problem

Renewable energy trading relies heavily on predicting the spread between the Day-Ahead market price and the Intraday/Imbalance market price.

**Scenario A: Overproduction / Low Demand**

The wind blows harder than expected, or grid demand drops. Your enterprise produces excess electricity. If the grid is oversupplied, the intraday price collapses (sometimes turning negative). You must hedge by selling futures early or buying put options to lock in a floor price.

**Scenario B: Underproduction / High Demand**

The sun goes behind clouds, or grid demand spikes. Your enterprise fails to deliver its committed day-ahead volume. You are forced to buy the deficit from the intraday/imbalance market at a massive premium. You need to buy call options or long futures to mitigate this peak price risk.

### Derivative Trading Strategy

The Python Trading Strategy microservice subscribes to the predictions Kafka topic populated by your LSTM service. It translates consumption forecasts directly into energy derivative positions.

**Arbitrage Logic**

If your LSTM predicts a massive surge in grid demand (or a plunge in solar generation due to incoming cloud cover), the service calculates that spot prices will spike. It fires an automated signal to buy short-term call options or long futures contracts.

**Risk Management Framework**

Derivatives involve leverage. The trading microservice must enforce strict stop-loss and take-profit limits, factoring in the margin requirements unique to energy assets.

**Market Execution Interface**

For local testing, use a mock exchange container (a Python Flask/FastAPI app mimicking market APIs). For production, replace this target with a live electronic market API (e.g., ICE, CME, or regional spot market APIs).

### Day-Ahead vs. 15-Minute Continuous Intraday

**Day-Ahead Auction Pricing**

To predict the Day-Ahead auction pricing for the FI (Finland) bidding zone, your model must capture the specific dynamics of the Nord Pool market. Finland's prices are heavily influenced by:

- Domestic nuclear baseload capacity
- Transmission capacities from Sweden (SE1, SE3) and Estonia (EE)
- Norwegian and Swedish hydro reservoir levels
- Industrial demand profiles

**15-Minute Continuous Intraday Trading**

For real-time balancing, the platform implements 15-minute interval forecasting:

```
[Kafka: grid-consumption-raw] ──▶ [15-Min Buffer Window] ──▶ 
[TensorFlow Inference Engine] ──▶ [Kafka: demand-forecasts-15m]
```

This setup processes data sequences of length 96 (exactly 24 hours of historical 15-minute intervals) to forecast the next 15-minute grid demand step.

## Docker Deployment Architecture

### Multi-Container Stack Configuration

Create a `docker-compose.yml` file to orchestrate the following containers:

- **timescaledb**: PostgreSQL enhanced with time-series extensions for storing historical and streaming prices/grid data
- **kafka & zookeeper**: The event bus to stream tick data and broadcast forecast results between services
- **airflow**: For scheduling daily batch training of the LSTM model
- **ml-service**: A Python application container loading your deep learning framework (TensorFlow/PyTorch)
- **trading-agent**: A microservice running event-loop algorithms to place trades

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:7.4.0
    depends_on:
      - zookeeper
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
    ports:
      - "9092:9092"

  timescaledb:
    image: timescale/timescaledb:latest-pg14
    environment:
      POSTGRES_DB: energy_trading
      POSTGRES_USER: trading_user
      POSTGRES_PASSWORD: secure_password
    ports:
      - "5432:5432"
    volumes:
      - timescaledb-data:/var/lib/postgresql/data

  lstm-service:
    build:
      context: ./services/lstm_service
      dockerfile: Dockerfile
    depends_on:
      - kafka
    environment:
      KAFKA_BROKERS: kafka:9092
      MODEL_PATH: /models/lstm_demand_model.h5
    volumes:
      - ./models:/models:ro

  trading-engine:
    build:
      context: ./services/trading_engine
      dockerfile: Dockerfile
    depends_on:
      - kafka
      - lstm-service
    environment:
      KAFKA_BROKERS: kafka:9092
      TRADING_THRESHOLD_MW: 2.5

  ingestion-service:
    build:
      context: ./services/ingestion_service
      dockerfile: Dockerfile
    depends_on:
      - kafka
    environment:
      KAFKA_BROKERS: kafka:9092

volumes:
  timescaledb-data:
```

### Dockerfile Template

**services/lstm_service/Dockerfile**:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run service
CMD ["python", "main.py"]
```

**services/lstm_service/requirements.txt**:

```
tensorflow-cpu==2.13.0
confluent-kafka==2.2.0
numpy==1.24.3
```

### Deployment Workspace Layout

Organize components within your local multi-container workspace:

```
.
├── docker-compose.yml
├── models/
│   ├── lstm_demand_model.h5
│   ├── scaler_min.npy
│   └── scaler_max.npy
└── services/
    ├── ingestion_service/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── main.py
    ├── lstm_service/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── main.py
    └── trading_engine/
        ├── Dockerfile
        ├── requirements.txt
        └── main.py
```

### Data Contract and Schema

To maintain consistency across microservices, all messages sent to Apache Kafka are structured as JSON data packets.

**Raw Metric Payload** (grid-consumption-raw):

```json
{
  "timestamp": "2026-07-19T07:00:00Z",
  "region_id": "wind_farm_zone_1",
  "actual_mw": 42.5,
  "wind_speed_ms": 12.4,
  "solar_irradiance": 0.0
}
```

**Forecast Output Payload** (demand-forecasts-15m):

```json
{
  "timestamp": "2026-07-19T07:00:00Z",
  "forecast_target_time": "2026-07-19T07:15:00Z",
  "region_id": "wind_farm_zone_1",
  "predicted_mw": 44.1
}
```

## Service Access and API Gateway

### How Users Access the Platform

The platform is designed as an internal event-driven system using Kafka for inter-service communication. To expose functionality to external users (traders, analysts, portfolio managers), you need to implement an **API Gateway** layer.

### Architecture for External Access

```
External Users
      ↓
  [API Gateway] ← Authentication & Rate Limiting
      ↓
  ┌───┴────┬──────────┬───────────┐
  ↓        ↓          ↓           ↓
LSTM     Trading   Market    Admin
API      API       Data API   API
  ↓        ↓          ↓           ↓
[Internal Microservices + Kafka]
  ↓
[TimescaleDB + Models]
```

### Recommended API Gateway Solutions

**Option 1: Kong API Gateway (Recommended for Production)**

```yaml
# Add to docker-compose.yml
services:
  kong-gateway:
    image: kong:3.3.0-alpine
    ports:
      - "8000:8000"  # HTTP API
      - "8443:8443"  # HTTPS API
      - "8001:8001"  # Admin API
    environment:
      KONG_DATABASE: postgres
      KONG_PG_HOST: timescaledb
      KONG_PG_USER: trading_user
      KONG_PG_PASSWORD: secure_password
      KONG_PROXY_ACCESS_LOG: /dev/stdout
      KONG_ADMIN_ACCESS_LOG: /dev/stdout
    depends_on:
      - timescaledb
```

**Option 2: NGINX with Lua (Lightweight Alternative)**

```nginx
# nginx.conf
upstream lstm_service {
    server lstm-service:5000;
}

upstream trading_service {
    server trading-engine:5001;
}

server {
    listen 443 ssl;
    server_name api.energytrading.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # JWT Authentication
    location /api/v1/forecasts {
        auth_request /auth;
        proxy_pass http://lstm_service;
    }

    location /api/v1/trades {
        auth_request /auth;
        proxy_pass http://trading_service;
    }

    location = /auth {
        internal;
        proxy_pass http://auth-service:8080/verify;
        proxy_set_header Authorization $http_authorization;
    }
}
```

### REST API Endpoints for User Access

To enable external access, each microservice should expose REST APIs alongside Kafka consumers:

#### 1. LSTM Forecast API

**Service Enhancement:** Add Flask/FastAPI endpoints to `lstm_service`:

```python
# services/lstm_service/api.py
from fastapi import FastAPI, HTTPException, Depends, Header
from typing import Optional
import jwt

app = FastAPI()

SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key")

def verify_token(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/api/v1/forecasts/latest")
async def get_latest_forecast(
    region_id: str,
    user: dict = Depends(verify_token)
):
    """Get latest LSTM forecast for a region"""
    # Query from buffer or database
    forecast = get_forecast_from_buffer(region_id)
    return {
        "region_id": region_id,
        "predicted_mw": forecast['predicted_mw'],
        "timestamp": forecast['timestamp'],
        "confidence_interval": [38.2, 50.8]
    }

@app.get("/api/v1/forecasts/history")
async def get_forecast_history(
    region_id: str,
    start_time: str,
    end_time: str,
    user: dict = Depends(verify_token)
):
    """Get historical forecasts for analysis"""
    # Query TimescaleDB
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT forecast_timestamp, predicted_mw, actual_mw, error_mw
        FROM demand_forecasts
        WHERE region_id = %s
          AND forecast_timestamp BETWEEN %s AND %s
        ORDER BY forecast_timestamp DESC
    """, (region_id, start_time, end_time))
    
    results = cursor.fetchall()
    return {"forecasts": results}
```

#### 2. Trading Signal API

```python
# services/trading_engine/api.py
from fastapi import FastAPI, HTTPException, Depends
from enum import Enum

app = FastAPI()

class TraderRole(str, Enum):
    TRADER = "trader"
    ANALYST = "analyst"
    ADMIN = "admin"

def check_role(user: dict, required_role: TraderRole):
    if user.get('role') != required_role.value:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

@app.get("/api/v1/signals/latest")
async def get_latest_signals(user: dict = Depends(verify_token)):
    """Get latest trading signals (any authenticated user)"""
    signals = get_active_signals()
    return {"signals": signals}

@app.post("/api/v1/trades/execute")
async def execute_trade(
    trade_params: dict,
    user: dict = Depends(verify_token)
):
    """Execute a trade (traders only)"""
    check_role(user, TraderRole.TRADER)
    
    # Validate trade parameters
    if trade_params['quantity_mw'] > 100:
        raise HTTPException(status_code=400, detail="Exceeds position limit")
    
    # Submit to exchange
    order_id = submit_to_exchange(trade_params)
    
    return {
        "order_id": order_id,
        "status": "submitted",
        "timestamp": datetime.utcnow().isoformat()
    }
```

#### 3. Market Data API (Real-time WebSocket)

```python
# services/market_data/websocket.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from confluent_kafka import Consumer

app = FastAPI()

@app.websocket("/ws/market-ticks")
async def market_data_stream(websocket: WebSocket):
    await websocket.accept()
    
    # Verify token from query params
    token = websocket.query_params.get("token")
    user = verify_token(f"Bearer {token}")
    
    # Subscribe to Kafka topic
    consumer = Consumer({
        'bootstrap.servers': KAFKA_BROKERS,
        'group.id': f"websocket-{user['user_id']}",
        'auto.offset.reset': 'latest'
    })
    consumer.subscribe(['market-ticks-raw', 'demand-forecasts-15m'])
    
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg:
                await websocket.send_json({
                    'topic': msg.topic(),
                    'data': json.loads(msg.value())
                })
    except WebSocketDisconnect:
        consumer.close()
```

### User Access Methods Summary

| Access Method | Use Case | Authentication Required |
|---------------|----------|-------------------------|
| **REST API** | Historical data queries, trade submission | JWT Token |
| **WebSocket** | Real-time market data streaming | Token in query params |
| **GraphQL API** (Optional) | Complex multi-service queries | JWT Token |
| **gRPC** (Optional) | High-frequency trading, low latency | mTLS Certificates |

## Security and Compliance

Security is a top priority for trading platforms, and microservices can enhance it when implemented correctly. By isolating sensitive components — such as authentication or payment processing — platforms reduce the attack surface and improve access control.

### Authentication and Authorization

#### 1. User Authentication with JWT (JSON Web Tokens)

**Authentication Service Implementation:**

```python
# services/auth_service/main.py
from fastapi import FastAPI, HTTPException
from passlib.hash import bcrypt
import jwt
from datetime import datetime, timedelta

app = FastAPI()

SECRET_KEY = os.getenv("JWT_SECRET", "your-256-bit-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# User database (use PostgreSQL in production)
users_db = {
    "trader1": {
        "username": "trader1",
        "password_hash": bcrypt.hash("secure_password"),
        "role": "trader",
        "organization": "GreenEnergy Ltd",
        "permissions": ["read_forecasts", "submit_trades", "view_positions"]
    },
    "analyst1": {
        "username": "analyst1",
        "password_hash": bcrypt.hash("analyst_password"),
        "role": "analyst",
        "organization": "MarketAnalytics Corp",
        "permissions": ["read_forecasts", "view_history", "export_data"]
    }
}

@app.post("/auth/login")
async def login(username: str, password: str):
    user = users_db.get(username)
    
    if not user or not bcrypt.verify(password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create JWT token
    token_data = {
        "sub": username,
        "role": user['role'],
        "permissions": user['permissions'],
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.post("/auth/verify")
async def verify_token(authorization: str):
    """Endpoint for API Gateway to verify tokens"""
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"valid": True, "user": payload}
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    """Issue new access token"""
    # Verify refresh token and issue new access token
    pass
```

#### 2. Role-Based Access Control (RBAC)

**User Roles and Permissions:**

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Trader** | View forecasts, Submit trades, View positions, Cancel orders | Active trading desk |
| **Analyst** | View forecasts, View history, Export data, Generate reports | Market research team |
| **Portfolio Manager** | View all positions, Set risk limits, Approve large trades | Risk management |
| **Admin** | All permissions, Manage users, Configure services | Platform administration |
| **Read-Only** | View public forecasts only | External partners |

**Permission Middleware:**

```python
from functools import wraps
from fastapi import HTTPException

def require_permission(permission: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: dict = None, **kwargs):
            if permission not in user.get('permissions', []):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: requires '{permission}'"
                )
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator

# Usage
@app.post("/api/v1/trades/execute")
@require_permission("submit_trades")
async def execute_trade(trade_params: dict, user: dict = Depends(verify_token)):
    # Only users with 'submit_trades' permission can access
    pass
```

#### 3. API Key Authentication (for Automated Systems)

For automated trading bots and scheduled jobs:

```python
# Alternative authentication method
API_KEYS = {
    "sk_live_abc123xyz": {
        "organization": "HFT Trading Firm",
        "rate_limit": 1000,  # requests per minute
        "permissions": ["read_forecasts", "submit_trades"]
    }
}

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return API_KEYS[x_api_key]

@app.get("/api/v1/forecasts/latest")
async def get_forecast_with_api_key(
    region_id: str,
    api_client: dict = Depends(verify_api_key)
):
    # Check rate limit
    check_rate_limit(api_client)
    
    return get_forecast(region_id)
```

#### 4. OAuth 2.0 Integration (Enterprise)

For enterprise customers integrating with existing identity providers:

```python
# OAuth 2.0 flow for SSO integration
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
oauth.register(
    name='azure_ad',
    client_id=os.getenv('AZURE_CLIENT_ID'),
    client_secret=os.getenv('AZURE_CLIENT_SECRET'),
    server_metadata_url='https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@app.get('/auth/login/azure')
async def azure_login(request: Request):
    redirect_uri = request.url_for('azure_callback')
    return await oauth.azure_ad.authorize_redirect(request, redirect_uri)

@app.get('/auth/callback/azure')
async def azure_callback(request: Request):
    token = await oauth.azure_ad.authorize_access_token(request)
    user = await oauth.azure_ad.parse_id_token(request, token)
    # Create internal JWT session
    return create_session(user)
```

### Key Security Measures

**1. Service Isolation**

Each microservice runs in its own Docker container with minimal privileges. Trade execution services have no direct access to data ingestion or model training environments.

**2. Kafka Authentication**

Enable SASL/SCRAM authentication for Kafka:

```yaml
kafka:
  environment:
    KAFKA_SASL_ENABLED_MECHANISMS: SCRAM-SHA-512
    KAFKA_SASL_MECHANISM_INTER_BROKER_PROTOCOL: SCRAM-SHA-512
```

**3. TLS Encryption**

Encrypt data in transit between services using TLS certificates.

**4. API Key Management**

Store exchange API credentials in environment variables or secret management systems (HashiCorp Vault, AWS Secrets Manager), never in source code.

**5. Rate Limiting**

Enforce rate limits on exchange API calls to comply with usage policies and prevent denial-of-service scenarios.

**6. Audit Logging**

Log all trade execution decisions with timestamps, imbalance calculations, and order IDs for regulatory compliance and post-trade analysis.

**7. Network Segmentation**

Use Docker networks to isolate different tiers:

```yaml
# docker-compose.yml
networks:
  frontend:  # API Gateway and public-facing services
  backend:   # Internal services (Kafka, databases)
  
services:
  kong-gateway:
    networks:
      - frontend
      - backend
  
  trading-engine:
    networks:
      - backend  # No direct external access
```

**8. Data Encryption**

- **At Rest**: Enable TimescaleDB encryption for sensitive trading data
- **In Transit**: Enforce TLS 1.3 for all API communications
- **Kafka Encryption**: Enable SSL/TLS for Kafka brokers

```yaml
# Kafka with TLS
kafka:
  environment:
    KAFKA_SSL_KEYSTORE_LOCATION: /etc/kafka/secrets/kafka.keystore.jks
    KAFKA_SSL_KEYSTORE_PASSWORD: ${KEYSTORE_PASSWORD}
    KAFKA_SSL_KEY_PASSWORD: ${KEY_PASSWORD}
    KAFKA_SSL_TRUSTSTORE_LOCATION: /etc/kafka/secrets/kafka.truststore.jks
    KAFKA_SSL_TRUSTSTORE_PASSWORD: ${TRUSTSTORE_PASSWORD}
    KAFKA_SSL_CLIENT_AUTH: required
```

**9. Secrets Management**

Use HashiCorp Vault or AWS Secrets Manager for sensitive credentials:

```python
# Integration with HashiCorp Vault
import hvac

client = hvac.Client(url='http://vault:8200', token=os.getenv('VAULT_TOKEN'))

# Read database credentials
db_secret = client.secrets.kv.v2.read_secret_version(path='database/timescaledb')
db_password = db_secret['data']['data']['password']

# Read exchange API keys
exchange_secret = client.secrets.kv.v2.read_secret_version(path='exchanges/nordpool')
api_key = exchange_secret['data']['data']['api_key']
```

**10. Rate Limiting and DDoS Protection**

Implement multi-level rate limiting:

```python
# Per-user rate limiting with Redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis

@app.on_event("startup")
async def startup():
    redis_client = await redis.from_url("redis://localhost")
    await FastAPILimiter.init(redis_client)

@app.get("/api/v1/forecasts/latest")
@limits(calls=100, period=60)  # 100 calls per minute
async def get_forecast(user: dict = Depends(verify_token)):
    pass
```

Rate limit tiers by user role:

| Role | API Calls/Minute | WebSocket Connections | Max Position Size |
|------|------------------|----------------------|-------------------|
| Trader | 1000 | 10 | 500 MW |
| Analyst | 200 | 5 | N/A (read-only) |
| Admin | Unlimited | Unlimited | N/A |
| API Key (Bot) | 5000 | 50 | 1000 MW |

**11. Input Validation and Sanitization**

Prevent injection attacks:

```python
from pydantic import BaseModel, validator, Field

class TradeRequest(BaseModel):
    region_id: str = Field(..., regex="^[a-zA-Z0-9_-]+$")
    quantity_mw: float = Field(..., gt=0, le=1000)
    order_type: str = Field(..., regex="^(LIMIT|MARKET)$")
    
    @validator('region_id')
    def validate_region(cls, v):
        allowed_regions = ['wind_farm_zone_1', 'solar_park_zone_2']
        if v not in allowed_regions:
            raise ValueError(f'Invalid region: {v}')
        return v

@app.post("/api/v1/trades/execute")
async def execute_trade(trade: TradeRequest, user: dict = Depends(verify_token)):
    # Pydantic automatically validates and sanitizes
    pass
```

**12. Security Monitoring and Alerting**

Implement real-time security monitoring:

```python
# Anomaly detection for suspicious trading patterns
from prometheus_client import Counter, Histogram

failed_auth_attempts = Counter('auth_failures_total', 'Failed authentication attempts', ['username'])
trade_size_histogram = Histogram('trade_size_mw', 'Distribution of trade sizes')

@app.post("/auth/login")
async def login(username: str, password: str):
    if not verify_credentials(username, password):
        failed_auth_attempts.labels(username=username).inc()
        
        # Alert if >5 failures in 5 minutes
        recent_failures = check_recent_failures(username)
        if recent_failures > 5:
            send_security_alert(f"Potential brute force: {username}")
        
        raise HTTPException(status_code=401)
```

### Compliance and Regulatory Requirements

**MiFID II / REMIT Compliance (EU Energy Markets):**

1. **Transaction Reporting**: Log all orders with UTC timestamps, unique transaction IDs, and counterparty details
2. **Clock Synchronization**: Synchronize all services to NTP servers (accuracy ±1 second)
3. **Order Audit Trail**: Maintain immutable logs for 7 years minimum
4. **Pre-Trade Risk Checks**: Validate position limits before order submission

```python
# Regulatory reporting
@app.post("/api/v1/trades/execute")
async def execute_trade(trade: TradeRequest, user: dict = Depends(verify_token)):
    # Pre-trade risk checks (MiFID II Article 17)
    check_position_limits(user, trade.quantity_mw)
    check_credit_limits(user)
    
    # Execute trade
    order_id = submit_to_exchange(trade)
    
    # Transaction reporting (REMIT Article 8)
    report_to_regulator({
        "transaction_id": order_id,
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user['sub'],
        "organization": user['organization'],
        "instrument": "POWER_FWD_FI_15MIN",
        "quantity_mw": trade.quantity_mw,
        "order_type": trade.order_type,
        "venue": "NORD_POOL_INTRADAY"
    })
    
    return {"order_id": order_id}
```

**GDPR Compliance (Data Privacy):**

- Encrypt personally identifiable information (PII)
- Implement data retention policies
- Provide user data export endpoints
- Support right to erasure (anonymization of trading history)

**SOC 2 Type II Requirements:**

- Change management procedures for production deployments
- Multi-factor authentication for admin access
- Encrypted backups with tested restore procedures
- Annual penetration testing and vulnerability assessments

### Production Security Checklist

Before deploying to production:

- [ ] Enable TLS/SSL for all external endpoints
- [ ] Rotate all default passwords and API keys
- [ ] Configure firewall rules (allow only necessary ports)
- [ ] Enable Kafka SASL/SCRAM authentication
- [ ] Implement database connection encryption
- [ ] Set up automated vulnerability scanning (Snyk, Trivy)
- [ ] Configure intrusion detection system (Fail2ban, ModSecurity)
- [ ] Enable container image scanning in CI/CD
- [ ] Implement secrets rotation policy (90-day cycle)
- [ ] Set up security incident response plan
- [ ] Enable audit logging to SIEM system
- [ ] Conduct load testing with rate limiting enabled
- [ ] Implement database backup and disaster recovery
- [ ] Configure monitoring alerts for security events
- [ ] Document security procedures and train operators

## Project Structure

```
📁 EnergyTrading/
├── 📄 README.md                          # This document
├── 📄 .gitignore                         # Git exclusion rules
├── 📄 docker-compose.yml                 # Multi-container orchestration
├── 📄 requirements.txt                   # Python dependencies for local dev
│
├── 📁 models/                            # Trained LSTM models and scalers
│   ├── lstm_demand_model.h5              # Pre-trained Keras model
│   ├── scaler_min.npy                    # Min-Max scaler minimum values
│   └── scaler_max.npy                    # Min-Max scaler maximum values
│
├── 📁 services/                          # Microservices source code
│   ├── 📁 ingestion_service/             # Data collection and streaming
│   │   ├── 🐳 Dockerfile
│   │   ├── 📄 requirements.txt
│   │   └── 🐍 main.py
│   │
│   ├── 📁 lstm_service/                  # LSTM inference engine
│   │   ├── 🐳 Dockerfile
│   │   ├── 📄 requirements.txt
│   │   └── 🐍 main.py
│   │
│   ├── 📁 trading_engine/                # Trading strategy and OMS
│   │   ├── 🐳 Dockerfile
│   │   ├── 📄 requirements.txt
│   │   └── 🐍 main.py
│   │
│   └── 📁 market_analytics/              # Market data processor (optional)
│       ├── 🐳 Dockerfile
│       ├── 📄 requirements.txt
│       └── 🐍 main.py
│
├── 📁 training/                          # Model training scripts
│   ├── 🐍 train_lstm.py                  # LSTM training pipeline
│   ├── 🐍 feature_engineering.py         # Data preprocessing
│   └── 📄 requirements.txt
│
├── 📁 data/                              # Local data storage (gitignored)
│   ├── 📁 raw/                           # Unprocessed historical data
│   └── 📁 processed/                     # Cleaned and scaled datasets
│
├── 📁 notebooks/                         # Jupyter notebooks for analysis
│   ├── exploratory_analysis.ipynb
│   └── model_evaluation.ipynb
│
├── 📁 config/                            # Configuration files
│   ├── ⚙️ kafka_topics.json              # Kafka topic definitions
│   └── ⚙️ timescaledb_init.sql           # Database initialization
│
└── 📁 tests/                             # Unit and integration tests
    ├── test_lstm_service.py
    ├── test_trading_engine.py
    └── test_integration.py
```
## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Python 3.10 or higher
- At least 8GB RAM for local deployment
- Git

### Step 1: Clone and Setup Virtual Environment

**Important: This project uses `venv/` as the single virtual environment. Only ONE virtual environment should exist to avoid confusion and package inconsistencies.**

```bash
# Navigate to project directory
cd /home/laptop/EXERCISES/MISCELLANEOUS/miscellaneous/EnergyTrading

# IMPORTANT: Remove any duplicate virtual environments
# Some IDEs or tools may auto-create .venv/ - delete it if present
rm -rf .venv

# Verify only venv/ exists (or create it if missing)
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Created venv/ virtual environment"
else
    echo "✓ Using existing venv/ virtual environment"
fi

# Activate the ONLY virtual environment: venv/
source venv/bin/activate

# Verify correct Python interpreter is active
which python  # Should show: .../EnergyTrading/venv/bin/python

# Upgrade pip
pip install --upgrade pip

# Install development dependencies
pip install -r requirements.txt
```

**Note:** If you see both `.venv/` and `venv/` folders in your project directory, delete `.venv/` immediately:
```bash
rm -rf .venv
```
Always use `source venv/bin/activate` to activate the virtual environment.

### Step 2: Prepare Training Data

Before running the platform, you need to train the LSTM model or use a pre-trained model.

**Option A: Use Sample Pre-trained Model**

```bash
# Download sample trained model (mock for demonstration)
mkdir -p models
# Place your lstm_demand_model.h5 file in models/
```

**Option B: Train Your Own Model**

```bash
# Activate virtual environment
source venv/bin/activate

# Run training script
cd training
python train_lstm.py --data ../data/raw/grid_history.csv --epochs 100 --output ../models/
```

### Step 3: Initialize Database Schema

```bash
# Start TimescaleDB container
docker-compose up -d timescaledb

# Wait for database initialization (30 seconds)
sleep 30

# Run schema initialization
docker exec -i energytrading_timescaledb_1 psql -U trading_user -d energy_trading < config/timescaledb_init.sql
```

### Step 4: Start All Services

```bash
# Build and start all containers
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### Step 5: Verify Service Health

```bash
# Check container status
docker-compose ps

# View logs for LSTM service
docker-compose logs -f lstm-service

# View logs for trading engine
docker-compose logs -f trading-engine
```

### Step 6: Monitor Kafka Topics

```bash
# Connect to Kafka container
docker exec -it energytrading_kafka_1 bash

# List topics
kafka-topics --list --bootstrap-server localhost:9092

# Consume messages from forecast topic
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic demand-forecasts-15m --from-beginning
```

### Step 7: Send Test Data

```bash
# Activate virtual environment
source venv/bin/activate

# Run ingestion simulator
python services/ingestion_service/main.py
```

### Step 8: Local Development Workflow

**Modify a Service**:

```bash
# Edit service code
nano services/lstm_service/main.py

# Rebuild and restart specific service
docker-compose up -d --build lstm-service

# View updated logs
docker-compose logs -f lstm-service
```

**Stop All Services**:

```bash
docker-compose down

# Remove volumes (clears database)
docker-compose down -v
```

### Step 9: Run Integration Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run test suite
pytest tests/ -v

# Run specific test
pytest tests/test_lstm_service.py -v
```

### Step 10: Production Deployment Considerations

**Kafka Partitioning Strategy**

Partition topics by Grid Region ID. This ensures that the LSTM service scales horizontally using Kafka consumer groups while guaranteeing that data from the same geographical solar/wind farm arrives sequentially.

**Model Retraining Schedule**

Route the Trading Engine signals to a simulated clearing mock container to validate if your LSTM prediction accuracy outweighs exchange transaction costs and option premiums before deploying to production.

**Monitoring and Observability**

- Deploy Prometheus for metrics collection
- Use Grafana dashboards for real-time monitoring
- Implement distributed tracing with Jaeger
- Set up alerting for prediction accuracy degradation

### Troubleshooting

**Kafka Connection Errors**:

```bash
# Check Kafka broker is accessible
docker exec energytrading_kafka_1 kafka-broker-api-versions --bootstrap-server localhost:9092
```

**LSTM Model Loading Failures**:

```bash
# Verify model file exists and is readable
docker exec energytrading_lstm-service_1 ls -lh /models/
```

**TimescaleDB Connection Issues**:

```bash
# Test database connection
docker exec energytrading_timescaledb_1 psql -U trading_user -d energy_trading -c "SELECT version();"
```

**Start the Platform**

```bash
cd /home/laptop/EXERCISES/MISCELLANEOUS/miscellaneous/EnergyTrading
source venv/bin/activate
docker-compose up -d --build
```

**Train LSTM Model**
```bash
python training/train_lstm.py --data data/raw/grid_history.csv --epochs 100 --output models/
```

**Monitor Services**
```bash
docker-compose logs -f lstm-service
docker-compose logs -f trading-engine
```

**Run Tests**
```bash
pytest tests/ -v
```

## References

1. [Energy Derivatives - Stanford University](http://large.stanford.edu/courses/2017/ph240/noordeh2/) - An overview of derivative securities in energy markets, including forwards, futures, and options
2. [Nord Pool Market Data API](https://data.nordpoolgroup.com/) - European electricity spot price data for Nordic and Baltic regions
3. [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/) - Real-time European transmission system operator data
4. TensorFlow Keras LSTM Documentation - Time series forecasting with recurrent neural networks
5. Apache Kafka Documentation - Event streaming platform for microservices architecture
6. TimescaleDB Documentation - Time-series database built on PostgreSQL

---

**License**: MIT

**Last Updated**: July 20, 2026
