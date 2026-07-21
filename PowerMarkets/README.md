# Power Markets and Power Purchase Agreements: A Platform for Intraday Trading Analysis

## Table of Contents

1. [Introduction](#1-introduction)
2. [Project Overview](#2-project-overview)
   - 2.1 [Project Structure](#21-project-structure)
   - 2.2 [System Architecture](#22-system-architecture)
   - 2.3 [Data Flow Diagram](#23-data-flow-diagram)
3. [Power Purchase Agreements (PPAs)](#3-power-purchase-agreements-ppas)
   - 3.1 [Definition and Purpose](#31-definition-and-purpose)
   - 3.2 [Key Features of PPAs](#32-key-features-of-ppas)
   - 3.3 [Types of Power Purchase Agreements](#33-types-of-power-purchase-agreements)
   - 3.4 [Flows Between PPA Parties](#34-flows-between-ppa-parties)
   - 3.5 [Strategic Importance for Energy Investors](#35-strategic-importance-for-energy-investors)
4. [Intraday Power Trading](#4-intraday-power-trading)
   - 4.1 [Definition and Concept](#41-definition-and-concept)
   - 4.2 [Role in Power Markets](#42-role-in-power-markets)
   - 4.3 [Intraday Trading in Nordic Markets](#43-intraday-trading-in-nordic-markets)
5. [Market Data and Infrastructure](#5-market-data-and-infrastructure)
   - 5.1 [Nord Pool Exchange](#51-nord-pool-exchange)
   - 5.2 [ENTSO-E Transparency Platform](#52-entso-e-transparency-platform)
   - 5.3 [Data Sources for Nordic Markets (2024-2026)](#53-data-sources-for-nordic-markets-2024-2026)
6. [Intraday Market Statistics](#6-intraday-market-statistics)
   - 6.1 [Hourly Statistics Calculation](#61-hourly-statistics-calculation)
   - 6.2 [Key Performance Metrics](#62-key-performance-metrics)
7. [Trading Strategies](#7-trading-strategies)
   - 7.1 [Imbalance Arbitrage](#71-imbalance-arbitrage)
   - 7.2 [Energy Arbitrage](#72-energy-arbitrage)
8. [Setup and Installation](#8-setup-and-installation)
   - 8.1 [Prerequisites](#81-prerequisites)
   - 8.2 [Virtual Environment Setup](#82-virtual-environment-setup)
   - 8.3 [Installing Dependencies](#83-installing-dependencies)
   - 8.4 [Environment Configuration](#84-environment-configuration)
9. [Running the Application](#9-running-the-application)
   - 9.1 [Standalone Python Scripts](#91-standalone-python-scripts)
   - 9.2 [FastAPI Backend Server](#92-fastapi-backend-server)
   - 9.3 [Docker Deployment](#93-docker-deployment)
   - 9.4 [Docker Compose Full Stack](#94-docker-compose-full-stack)
10. [Python Scripts Documentation](#10-python-scripts-documentation)
    - 10.1 [ENTSO-E Data Collector](#101-entsoe-data-collector)
    - 10.2 [Nord Pool Data Collector](#102-nord-pool-data-collector)
    - 10.3 [Automated Background Tasks](#103-automated-background-tasks)
11. [Database Configuration](#11-database-configuration)
    - 11.1 [TimescaleDB Setup](#111-timescaledb-setup)
    - 11.2 [Schema and Indexes](#112-schema-and-indexes)
    - 11.3 [Data Retention Policies](#113-data-retention-policies)
12. [Visualization with Grafana](#12-visualization-with-grafana)
    - 12.1 [Grafana Setup](#121-grafana-setup)
    - 12.2 [Dashboard Configuration](#122-dashboard-configuration)
    - 12.3 [Query Examples](#123-query-examples)
    - 12.4 [Alert Configuration](#124-alert-configuration)
13. [Cloud Deployment on AWS](#13-cloud-deployment-on-aws)
    - 13.1 [Infrastructure Requirements](#131-infrastructure-requirements)
    - 13.2 [IAM Roles and Security](#132-iam-roles-and-security)
    - 13.3 [Deployment Architecture](#133-deployment-architecture)
    - 13.4 [Step-by-Step AWS Deployment](#134-step-by-step-aws-deployment)
14. [API Documentation](#14-api-documentation)
    - 14.1 [REST API Endpoints](#141-rest-api-endpoints)
    - 14.2 [Authentication](#142-authentication)
    - 14.3 [Rate Limiting](#143-rate-limiting)
15. [Troubleshooting](#15-troubleshooting)
16. [References](#16-references)

---

## 1. Introduction

Today's power markets are experiencing uncertainty due to the transition to renewable energy sources, increased market volatility, and evolving regulatory frameworks. Power Purchase Agreements (PPAs) have emerged as an important financial instruments that provide stability and predictability in an otherwise volatile energy landscape. This document examines the structure and function of PPAs, with particular emphasis on intraday trading mechanisms that enable market participants to manage renewable energy intermittency and optimize their positions.

The integration of variable renewable energy sources such as solar and wind power has fundamentally altered electricity market dynamics. Traditional power systems relied on dispatchable generation that could be scheduled with high certainty. In contrast, renewable generation exhibits inherent variability that necessitates more sophisticated trading mechanisms and risk management strategies. Intraday markets have evolved to address these challenges by providing continuous trading opportunities up to minutes before physical delivery.

This repository provides a complete implementation of an automated power market data collection and analysis platform, featuring:

- Automated data collection from ENTSO-E Transparency Platform and Nord Pool Exchange
- TimescaleDB-powered time-series database for high-performance storage
- FastAPI backend with REST API endpoints and scheduled background tasks
- Grafana dashboards for real-time visualization and alerting
- Docker containerization for easy deployment
- The documentation for cloud deployment on AWS

---

## 2. Project Overview

### 2.1 Project Structure

```
EnergyMarkets/
├── 📁 scripts/                    # Python application code
│   ├── 📄 database.py             # SQLAlchemy async database configuration
│   ├── 📄 models.py               # ORM models for TimescaleDB tables
│   ├── 📄 schemas.py              # Pydantic validation schemas
│   ├── 📄 connectors.py           # Nord Pool API connector
│   ├── 📄 tasks.py                # Background scheduled tasks
│   ├── 📄 main.py                 # FastAPI application entry point
│   ├── 📄 entsoe_client.py        # Standalone ENTSO-E data collector
│   └── 📄 nordpool_client.py      # Standalone Nord Pool data collector
│
├── 📁 init-db/                    # Database initialization scripts
│   └── 📄 01_timescale.sql        # TimescaleDB hypertable setup
│
├── 📁 grafana/                    # Grafana configuration
│   └── 📁 provisioning/
│       ├── 📁 datasources/        # Auto-configured data sources
│       │   └── datasource.yml
│       └── 📁 alerting/           # Alert rules and notification channels
│
├── 📁 data/                       # Output directory for collected data
│
├── 📄 Dockerfile                  # Multi-stage Docker build
├── 📄 docker-compose.yml          # Multi-container orchestration
├── 📄 requirements.txt            # Python dependencies
├── 📄 .env.example                # Environment variables template
├── 📄 .gitignore                  # Git ignore patterns
├── 📄 setup.sh                    # Automated setup script
└── 📄 README.md                   # This documentation file
```

### 2.2 System Architecture

The platform implements a three-tier architecture optimized for high-throughput time-series data processing:

```
┌────────────────────────────────────────────────────────────────────┐
│                        External Data Sources                       │
│  ┌──────────────────────┐          ┌──────────────────────┐        │
│  │   ENTSO-E Platform   │          │   Nord Pool Exchange │        │
│  │  (Transparency API)  │          │    (Market Data API) │        │
│  └──────────┬───────────┘          └───────────┬──────────┘        │
└─────────────┼──────────────────────────────────┼───────────────────┘
              │                                  │
              │ REST API (15-min polling)        │
              ▼                                  ▼
┌────────────────────────────────────────────────────────────────────┐
│                      Application Layer (FastAPI)                   │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Background Schedulers (APScheduler)                         │  │
│  │  ├─ ENTSO-E Scraper Task (every 15 min)                      │  │
│  │  └─ Nord Pool Scraper Task (every 15 min, offset +1min)      │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  REST API Endpoints                                          │  │
│  │  ├─ /api/v1/market-data/fetch (Nord Pool on-demand)          │  │
│  │  ├─ /api/v1/prices/latest (Query stored prices)              │  │
│  │  ├─ /api/v1/entsoe/latest (Query grid data)                  │  │
│  │  └─ /api/v1/health (Health check)                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────┬──────────────────────────────────────────────┘
                      │ SQLAlchemy ORM (async)
                      ▼
┌────────────────────────────────────────────────────────────────────┐
│                    Data Layer (TimescaleDB)                        │
│  ┌──────────────────────┐      ┌──────────────────────┐            │
│  │ intraday_prices      │      │ entsoe_grid_data     │            │
│  │ (Hypertable)         │      │ (Hypertable)         │            │
│  │ - 7-day chunks       │      │ - 7-day chunks       │            │
│  │ - Composite indexes  │      │ - Composite indexes  │            │
│  └──────────────────────┘      └──────────────────────┘            │
└─────────────────────┬──────────────────────────────────────────────┘
                      │ PostgreSQL Protocol
                      ▼
┌────────────────────────────────────────────────────────────────────┐
│              Visualization Layer (Grafana)                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Dashboards                                                  │  │
│  │  ├─ Real-time Price Monitoring                               │  │
│  │  ├─ Multi-Zone Comparison Charts                             │  │
│  │  ├─ Volatility Analysis                                      │  │
│  │  └─ Data Pipeline Health Metrics                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Alerting System                                             │  │
│  │  ├─ Price Spike Alerts (>€250/MWh)                           │  │
│  │  └─ Data Ingestion Failure Alerts                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

### 2.3 Data Flow Diagram

```
┌──────────────┐
│ External API │
│   Sources    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 1: API Request & Authentication                         │
│ - Add Bearer token to Authorization header                   │
│ - Set query parameters (zones, dates, metrics)               │
│ - Handle rate limiting and retry logic                       │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 2: Response Parsing & Validation                        │
│ - Parse JSON/XML responses                                   │
│ - Convert to Pydantic models for type validation             │
│ - Handle timezone conversions (UTC normalization)            │
│ - Filter invalid/missing data points                         │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 3: Database Upsert Operation                            │
│ - Open async SQLAlchemy session                              │
│ - Construct PostgreSQL INSERT ... ON CONFLICT DO UPDATE      │
│ - Batch insert for performance (handles duplicates)          │
│ - Commit transaction                                         │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 4: TimescaleDB Processing                               │
│ - Data automatically partitioned into 7-day chunks           │
│ - Indexes updated (area + timestamp composite)               │
│ - Compression applied to old chunks (optional)               │
│ - Retention policy enforced (optional, e.g., 90 days)        │
└──────┬───────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ Step 5: Data Available for Queries                           │
│ - REST API endpoints serve latest data                       │
│ - Grafana dashboards query via PostgreSQL data source        │
│ - Real-time alerts evaluated every 5 minutes                 │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. Power Purchase Agreements (PPAs)

### 3.1 Definition and Purpose

A Power Purchase Agreement (PPA) is a legal contract between an electricity generator and a buyer (referred to as the offtaker) to sell and purchase electric power at a pre-agreed tariff for a specified period. PPAs serve multiple strategic purposes in modern energy markets:

- **Price Stability**: PPAs establish long-term price certainty, insulating both parties from market volatility
- **Investment Predictability**: Fixed revenue streams facilitate project financing and reduce investment risk
- **Market Risk Mitigation**: Both generators and offtakers reduce their exposure to spot market price fluctuations
- **Renewable Energy Deployment**: PPAs accelerate clean energy build-out by providing revenue certainty to developers

PPAs have become instrumental in removing barriers to renewable energy investments and supporting the transition to cleaner energy systems. Regulatory bodies have published recommendations encouraging the adoption of PPAs and similar energy purchase agreements to facilitate market development.

### 3.2 Key Features of PPAs

PPAs are characterized by several essential contractual elements:

**Long-Term Contract Duration**: Typically signed for periods ranging from 10 to 25 years, providing extended revenue visibility for project developers and price certainty for offtakers.

**Fixed or Escalating Tariff Structure**: The price per unit of electricity (measured in currency per kilowatt-hour or megawatt-hour) is agreed upon at contract inception. Tariffs may be fixed or include predetermined escalation clauses to account for inflation or other economic factors.

**Defined Quantity Specifications**: Contracts specify the contracted capacity (measured in megawatts) and expected annual energy supply (measured in megawatt-hours), establishing clear performance expectations.

**Delivery Terms and Milestones**: PPAs delineate dates including project commencement, Commercial Operation Date (COD), billing cycles, and penalty provisions for non-performance.

**Point of Delivery**: The contract specifies the location where power will be injected into the transmission or distribution grid, which has implications for transmission costs and losses.

### 3.3 Types of Power Purchase Agreements

PPAs can be categorized into several distinct types based on the nature of the offtaker and the contractual arrangement:

| PPA Type | Offtaker | Characteristics |
|----------|----------|-----------------|
| **Utility/DISCOM PPA** | Government Distribution Company | Common in large-scale solar and wind tenders conducted at central or state government level |
| **Corporate/Private PPA** | Commercial or Industrial Users | Growing trend facilitated via Open Access route, allowing direct procurement from generators |
| **Captive PPA** | Self-Owned Industry | Industry generates and consumes its own power, common in industrial facilities with on-site generation |
| **Merchant (No PPA)** | N/A | Power sold directly into spot markets without long-term contract (technically not a PPA arrangement) |

### 3.4 Flows Between PPA Parties

The relationship between PPA parties involves distinct physical and financial flows that differ fundamentally from traditional spot market transactions. The diagram below illustrates the net flows between the three primary participants: the power plant (generator), the National Electricity Market (NEM), and the offtaker.

```
┌─────────────────────────────┐                          ┌──────────────────────────────┐
│                             │      Electricity         │                              │
│   National Electricity      │◄─────────────────────────│       Power Plant            │
│      Market (NEM)           │                          │   (Renewable Generator)      │
│                             │    Floating Revenue      │                              │
│    [Transmission Grid]      │- - - - - X - - - - - - - │    [Solar/Wind Assets]       │
│                             │      (Bypassed)          │                              │
└──────────────┬──────────────┘                          └────────────┬─────────────────┘
               │                                                      │
               │ Electricity                                          │
               │                                                      │
               ▼                                                      │ Fixed Revenue
      ┌────────────────┐                                              │ (Contract Price)
      │     Fees       │                                              │
      │ - - - X - - -  │                                              │
      │  (Bypassed)    │                                              │
      ▼                │                                              │
┌─────────────────────────────┐                          ◄────────────┘
│                             │    Floating Revenue      
│         Offtaker            │- - - - - X - - - - - - - 
│   (PPA Counterparty)        │      (Bypassed)          
│                             │                          
│  [Industrial/Commercial]    │                          
│                             │                          
└─────────────────────────────┘                          
```

**Physical Flows**:
1. The power plant generates electricity and injects it into the National Electricity Market grid
2. The offtaker withdraws electricity from the grid to meet its consumption requirements

**Financial Flows (Traditional Spot Market - Crossed Out)**:
- Floating revenue from NEM to power plant (market-based pricing) - ELIMINATED
- Variable fees from offtaker to NEM (retail pricing) - ELIMINATED
- Floating revenue between offtaker and plant - ELIMINATED

**Financial Flows (PPA Arrangement - Active)**:
- Fixed revenue payment from offtaker directly to power plant at the pre-agreed contract rate

**Key Insight**: The PPA structure effectively decouples the physical electricity flows (which still occur through the grid) from the financial settlement flows. While electricity physically flows through the market infrastructure, the financial exposure to spot market price volatility is eliminated for both the generator and the offtaker. The generator receives predictable revenue regardless of wholesale market prices, and the offtaker pays a fixed rate independent of retail market fluctuations.

This arrangement provides several benefits:
- **For Generators**: Revenue certainty facilitates project financing and reduces merchant risk
- **For Offtakers**: Cost predictability supports long-term budgeting and reduces exposure to energy price volatility
- **For Energy Markets**: Stable demand signals encourage new renewable energy capacity additions
- **For Society**: Lower cost of capital for renewable projects can reduce overall electricity costs and accelerate decarbonization

### 3.5 Strategic Importance for Energy Investors

Energy investors utilize Power Purchase Agreements as foundational instruments for renewable energy project development. The strategic advantages include:

**Secure Revenue Streams**: By signing a PPA, energy developers lock in predictable income streams that extend over the project's operational life. This revenue certainty is needed for securing debt financing from banks and attracting equity investors who require stable return projections.

**Energy Cost Management**: Corporate offtakers employ PPAs to control their power expenses by procuring clean electricity at stable, long-term prices. This hedges against energy price volatility and supports corporate sustainability objectives. Major technology companies have leveraged this strategy; for instance, Microsoft reported matching 100 percent of its annual global electricity consumption with renewable energy, with PPAs playing a central role in this achievement.

**Accelerating Clean Energy Deployment**: PPAs guarantee demand for renewable projects before construction commences, thereby reducing market risk and enabling project developers to secure necessary capital. This demand guarantee facilitates the addition of substantial solar and wind generation capacity to electricity grids.

**Price Risk Hedging**: PPAs function as effective hedging instruments against price volatility in wholesale electricity markets. Both generators and consumers benefit from reduced exposure to spot market fluctuations, which have become more pronounced with increased renewable penetration and fossil fuel price volatility.

## 4. Intraday Power Trading

### 4.1 Definition and Concept

Intraday trading refers to the buying and selling of electricity for delivery on the same day, occurring after the day-ahead market has closed and continuing until shortly before physical delivery. This market segment allows participants to adjust their positions based on updated forecasts, unexpected outages, or changes in consumption patterns. The intraday market serves as a mechanism for managing short-term imbalances and optimizing portfolio positions.

For additional technical details, refer to the guide on intraday trading concepts: [Next Kraftwerke - Intraday Trading](https://www.next-kraftwerke.com/knowledge/intraday-trading)

### 4.2 Role in Power Markets

Intraday markets fulfill several essential functions in modern electricity systems:

**Forecast Deviation Management**: Renewable energy sources such as wind and solar exhibit inherent production variability. Weather conditions can change significantly between the day-ahead market closure (typically around noon on the previous day) and actual delivery. Intraday markets enable generators to correct their positions as forecasts improve.

**Demand Response Integration**: Large consumers can adjust their procurement strategies in response to real-time price signals and operational requirements.

**Balance Responsibility Optimization**: Balance Responsible Parties (BRPs) utilize intraday markets to minimize imbalance charges by refining their positions closer to delivery time when forecast accuracy is higher.

**Market Liquidity Enhancement**: Continuous trading provides liquidity and price discovery throughout the day, facilitating efficient resource allocation and system balancing.

### 4.3 Intraday Trading in Nordic Markets

The Nordic countries (Sweden, Norway, Finland, and Denmark) have implemented sophisticated intraday trading mechanisms to support their renewable energy transition. For the period covering 2024, 2025, and 2026, the short-term electricity landscape is characterized by granular market structures:

**15-Minute Market Time Units (MTU)**: The Nordic region has fully transitioned to 15-minute settlement periods, providing finer temporal resolution for balancing renewable generation variability.

**Intraday Auctions (IDA)**: Introduced to complement continuous trading, the auction mechanism allocates cross-zonal transmission capacity through three daily auctions. This mechanism became operational in June 2024.

**Balance Responsibility Trading**: Professional intraday traders manage balance responsibility for production and consumption units, optimizing positions to minimize imbalance costs.

## 5. Market Data and Infrastructure

### 5.1 Nord Pool Exchange

Nord Pool operates as the dominant power exchange for Nordic electricity trading, providing infrastructure for both day-ahead and intraday markets. The exchange offers two distinct intraday product categories:

**Intraday Continuous Market**:
- Operates as a continuous, over-the-counter-style trading platform
- Provides real-time order matching throughout the trading period
- Data availability includes:
  - Historical order data (extending back to 2018)
  - Executed transaction records
  - Level 2 order book depth
  - Hub-to-hub transmission capacity allocations

**Access Methods**:
- Free summary statistics: [Nord Pool Intraday Hourly Statistics](https://data.nordpoolgroup.com/intraday/intraday-hourly-statistics?deliveryDate=latest&deliveryArea=DK1)
- Systematic data access: Subscription to Intraday Public Market Data API or Intraday Delayed bulk file feeds required for algorithmic analysis

**Intraday Auctions (IDA)**:
- Launched June 2024 to handle cross-zonal capacity pricing
- Three daily auction sessions
- Data includes:
  - Auction clearing prices by delivery period
  - Executed volumes
  - Aggregated Bidding Curves revealing structural supply and demand

**Access Method**: [Nord Pool Auctions Portal](https://www.nordpoolgroup.com/en/services/power-market-data-services/intraday-auctions/)

### 5.2 ENTSO-E Transparency Platform

The European Network of Transmission System Operators for Electricity (ENTSO-E) provides an open-access data repository mandated by regulatory requirements. This platform serves as a free alternative for fundamental market analysis.

**Available Data**:
- Cross-border physical intraday electricity flows
- Commercial trade schedules between bidding zones
- Available Transfer Capacity (ATC) between Nordic price zones (e.g., SE3 to NO1)
- Imbalance pricing and settlement data
- Generation forecasts and actual production by fuel type
- Scheduled and realized commercial exchanges

**Access Method**: Registration for a free API token at [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/)

**Data Query Example**: To retrieve data for Finland, use the search parameter `BZN|FI`

**Technical Implementation**: The most efficient method for loading historical intraday data from ENTSO-E involves using the official RESTful API through the Python wrapper library `entsoe-py`. Researchers must register for an API key by contacting ENTSO-E support.

### 5.3 Data Sources for Nordic Markets (2024-2026)

The following table summarizes primary data sources for analyzing Nordic intraday markets:

| Data Source | Content Type | Cost Structure | Best Use Case |
|-------------|-------------|----------------|---------------|
| Nord Pool API | Order Book Depth, 15-Minute Continuous Trades, Tick-by-Tick Data | Paid (Commercial License) | High-frequency trading backtesting, Algorithmic strategy development |
| Nord Pool Data Portal | Contract Statistics, VWAP Indexes, Summary Statistics | Free (Web Interface) | General quantitative analysis, Academic research, Report generation |
| ENTSO-E Platform | Balancing Data, Grid Flow, Cross-Border Capacity, Imbalance Pricing | Free (Requires Registration) | Fundamental market modeling, Macro analytics, Transmission constraint analysis |

## 6. Intraday Market Statistics

### 6.1 Hourly Statistics Calculation

Intraday hourly statistics aggregate continuous, individual transactions executed within a specific delivery hour. Power exchanges employ standardized financial and energy metrics to synthesize transaction data into performance indicators.

The calculation methodology addresses a fundamental question: How should discrete trades occurring at different times and prices be summarized to represent the market state for a given delivery period?

Exchanges such as Nord Pool and EPEX SPOT apply the following aggregation methods:

**Transaction-Based Aggregation**: Only executed transactions contribute to statistics. Unmatched orders do not affect volume or price calculations.

**Temporal Assignment**: Each transaction is assigned to the delivery hour(s) it affects, not the time of execution. A trade executed at 10:00 for delivery hour 14:00-15:00 is included in hour 14 statistics.

**Single-Counting Principle**: Transaction volume represents the actual energy traded, not the sum of buy and sell sides (which would double-count the same energy).

### 6.2 Key Performance Metrics

**High/Low Price**: The maximum and minimum execution prices across all trades during the specified delivery hour. These values bound the price range and indicate intraday volatility.

**Transaction Volume**: The sum of volumes for all executed transactions within the delivery hour, measured in megawatt-hours (MWh). This metric indicates market liquidity and trading activity.

**Time-Specific Statistics**:
- Timestamp of the first trade for the delivery hour
- Timestamp of the last trade for the delivery hour
- Opening trade price (price of the first transaction)
- Closing trade price (price of the final transaction)

**Volume Weighted Average Price (VWAP)**:

The VWAP represents the average price weighted by the volume of each transaction, calculated as:

```
VWAP = Σ(Price_i × Volume_i) / Σ(Volume_i)
```

Where:
- Price_i = execution price of transaction i
- Volume_i = volume of transaction i
- Σ denotes summation across all transactions in the delivery hour

The VWAP provides a more representative average price than a simple arithmetic mean because it accounts for the economic significance of each trade.

**Gate Closure-Adjusted Metrics**: Energy-focused exchanges calculate specialized metrics that isolate trading activity close to delivery. For example, EPEX SPOT computes VWAP values specifically for:
- Trades executed within the final hour before gate closure
- Trades executed within the final three hours before gate closure

These metrics reflect real-time balancing behavior as participants make final position adjustments based on the most recent information.

For detailed methodologies and advanced trading strategies, consult: [SmartPulse - Intraday Power Trading Strategies](https://www.smartpulse.io/intraday-power-trading-2-how-to-trade-strategies-algorithms/)

## 7. Trading Strategies

### 7.1 Imbalance Arbitrage

Imbalance arbitrage represents the most fundamental intraday trading strategy, employed by every Balance Responsible Party managing generation or consumption portfolios. The strategy addresses the inherent mismatch between scheduled positions and actual physical delivery.

**The Fundamental Problem**:

Electricity markets operate on a scheduling paradigm where participants submit production or consumption schedules to Transmission System Operators (TSOs) in advance. However, actual physical outcomes frequently deviate from these schedules due to:
- Forecast errors (particularly for wind and solar generation)
- Unplanned equipment outages
- Demand fluctuations
- External weather impacts

When a market participant's actual position differs from their scheduled position at the time of delivery, they incur an imbalance. TSOs resolve these imbalances through balancing markets, charging or crediting participants based on imbalance prices.

**The Economic Incentive**:

Balancing prices are almost universally more expensive (for deficits) or less favorable (for surpluses) than intraday market prices. This price differential creates a clear economic incentive for participants to self-balance by trading in intraday markets before gate closure.

**Operational Mechanism**:

1. **Initial Schedule Submission**: A renewable plant operator submits a day-ahead schedule estimating generation based on weather forecasts available at that time.

2. **Forecast Updates**: As delivery approaches, meteorological forecasts improve in accuracy. Updated wind speed or solar irradiation forecasts may indicate that actual generation will differ substantially from the day-ahead schedule.

3. **Position Correction**:
   - **Surplus Scenario**: If forecasts show higher-than-scheduled generation, the operator sells the expected surplus in the intraday market, converting potential negative imbalance exposure into locked-in revenue.
   - **Deficit Scenario**: If forecasts show lower-than-scheduled generation, the operator buys replacement energy in the intraday market at current prices, avoiding higher imbalance settlement costs.

4. **Gate Closure**: Positions must be corrected before the intraday market closes for each delivery period (gate closure time varies by market but is typically 5-60 minutes before delivery).

**Who Employs This Strategy**:

Every Balance Responsible Party managing renewable generation, conventional power plants, or industrial consumption portfolios utilizes imbalance arbitrage. It constitutes the baseline activity underpinning all other intraday strategies and is essential for operational risk management.

**Relationship to Renewable Energy**:

The transition to renewable energy has dramatically increased the importance of imbalance arbitrage. Wind and solar power exhibit high production variability, making forecast deviations larger and more frequent than with conventional dispatchable generation. This structural characteristic makes intraday trading valuable for renewable asset operators.

**Risk Management Perspective**:

From a portfolio management standpoint, imbalance arbitrage transfers price risk from the unpredictable imbalance settlement mechanism (controlled by the TSO) to the transparent intraday market (where participants can observe prices and make informed decisions). This transformation of opaque risk into manageable market exposure represents a fundamental risk management principle.

### 7.2 Energy Arbitrage

Energy arbitrage extends beyond simple imbalance correction to exploit systematic price differentials in electricity markets. This strategy has become increasingly important as renewable energy sources add temporal and spatial variability to grid operations.

**Definition**:

Energy arbitrage is the practice of buying electricity when prices are low (typically during periods of excess supply or low demand) and selling when prices are high (typically during periods of tight supply or peak demand). This strategy can be executed across different timeframes (day-ahead to intraday, or between different intraday trading sessions) or across different locations (between price zones with transmission capacity).

**Market Context**:

Electricity prices exhibit substantial intraday volatility driven by:
- Renewable generation variability (solar production peaks mid-day, wind production varies with weather patterns)
- Demand patterns (morning and evening peaks in consumption)
- Transmission constraints between price zones
- Unexpected generation or transmission outages

**Implementation Approaches**:

**Temporal Arbitrage**: Traders identify periods where intraday prices are expected to be significantly below or above the day-ahead cleared price, executing positions in the intraday market to profit from these differentials.

**Spatial Arbitrage**: When transmission capacity exists between price zones with different clearing prices, traders can buy in the lower-priced zone and sell in the higher-priced zone, capturing the price spread (minus transmission costs).

**Storage-Enabled Arbitrage**: Battery storage systems and pumped hydro facilities can physically store energy during low-price periods and discharge during high-price periods, providing both arbitrage profits and grid balancing services.

**Strategic Importance**:

Energy arbitrage provides market liquidity and contributes to price convergence across time periods and locations. These trading activities support grid stability by incentivizing resources to respond to supply-demand imbalances. As renewable penetration increases, the value of energy arbitrage grows because renewable generation patterns create larger and more frequent price differentials.

For analysis of intraday trading strategies including quantitative algorithms, refer to: [SmartPulse - Intraday Trading Strategies and Algorithms](https://www.smartpulse.io/intraday-power-trading-2-how-to-trade-strategies-algorithms/)

---

## 8. Setup and Installation

### 8.1 Prerequisites

Before setting up the Power Trading Data Platform, ensure your system meets the following requirements:

**System Requirements**:
- Operating System: Linux (Ubuntu 20.04+), macOS (10.15+), or Windows 10+ with WSL2
- Python: Version 3.11 or higher
- Docker: Version 20.10+ (for containerized deployment)
- Docker Compose: Version 2.0+ (for multi-container orchestration)
- RAM: Minimum 4GB (8GB recommended for full stack)
- Disk Space: Minimum 10GB free (for database and logs)

**API Keys Required**:
1. **ENTSO-E API Key**: Register at [transparency.entsoe.eu](https://transparency.entsoe.eu/) and email transparency@entsoe.eu to request API token
2. **Nord Pool API Key** (optional): Contact Nord Pool commercial team for access. Free tier provides limited access via web portal.

### 8.2 Virtual Environment Setup

Setting up an isolated Python virtual environment ensures dependency management and avoids conflicts with system packages.

**Option 1: Automated Setup (Recommended)**

```bash
# Navigate to project directory
cd EnergyMarkets

# Make setup script executable
chmod +x setup.sh

# Run automated setup
./setup.sh
```

The setup script will:
- Create Python virtual environment in `venv/` directory
- Install all required dependencies
- Create `.env` file from template
- Create necessary directories (data/, logs/)

**Option 2: Manual Setup**

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows (PowerShell):
venv\Scripts\Activate.ps1

# Upgrade pip to latest version
pip install --upgrade pip
```

**Activating Virtual Environment in VS Code**:

1. Open Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`)
2. Type "Python: Select Interpreter"
3. Choose the interpreter from `./venv/bin/python`
4. VS Code will automatically activate the virtual environment in integrated terminal

### 8.3 Installing Dependencies

After activating the virtual environment, install all required Python packages:

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Verify installation
pip list | grep -E 'fastapi|sqlalchemy|entsoe|httpx|apscheduler'
```

**Key Dependencies**:
- `fastapi==0.109.0` - Modern web framework for building APIs
- `uvicorn[standard]==0.27.0` - ASGI server for FastAPI
- `sqlalchemy==2.0.25` - SQL toolkit and ORM
- `asyncpg==0.29.0` - PostgreSQL async driver
- `entsoe-py==0.6.0` - ENTSO-E Transparency Platform client
- `httpx==0.26.0` - Async HTTP client
- `apscheduler==3.10.4` - Background task scheduler
- `pandas==2.1.4` - Data manipulation library

### 8.4 Environment Configuration

Configure environment variables for API keys and database connections:

```bash
# Create .env file from template
cp .env.example .env

# Edit .env file with your credentials
nano .env  # or use your preferred editor
```

**Required Environment Variables**:

```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://trader_admin:SecureTradingPassword2026!@localhost:5432/power_db

# ENTSO-E API Configuration
ENTSOE_API_KEY=your_entsoe_api_key_here

# Nord Pool API Configuration (optional)
NORDPOOL_API_KEY=your_nordpool_api_key_here

# PostgreSQL/TimescaleDB Configuration
POSTGRES_USER=trader_admin
POSTGRES_PASSWORD=SecureTradingPassword2026!
POSTGRES_DB=power_db

# Application Settings
APP_ENV=development
LOG_LEVEL=INFO
```

**Security Best Practices**:
- Never commit `.env` file to version control (already in `.gitignore`)
- Use strong, unique passwords for database
- Rotate API keys periodically
- In production, use secrets management services (AWS Secrets Manager, HashiCorp Vault)

---

## 9. Running the Application

### 9.1 Standalone Python Scripts

The platform includes two standalone data collection scripts for on-demand data retrieval without running the full backend.

**A) ENTSO-E Data Collector**

[scripts/entsoe_client.py](scripts/entsoe_client.py)

This script fetches historical and real-time data from ENTSO-E Transparency Platform. It supports multiple data types including actual load, day-ahead prices, generation by fuel type, and cross-border flows.

**Purpose**: Collect fundamental grid data for analysis of electricity demand, generation patterns, and transmission flows across European bidding zones.

**Usage Examples**:

```bash
# Activate virtual environment first
source venv/bin/activate

# Fetch Finnish load data for January 2026
python scripts/entsoe_client.py --zone FI --start 2026-01-01 --end 2026-01-31 --metrics load

# Fetch multiple metrics for Sweden
python scripts/entsoe_client.py --zone SE --start 2026-07-01 --end 2026-07-07 --metrics load,prices,generation

# Fetch cross-border flows between Sweden and Finland
python scripts/entsoe_client.py --flow SE FI --start 2026-01-01 --end 2026-01-31

# Save to custom output directory
python scripts/entsoe_client.py --zone FI --start 2026-07-01 --end 2026-07-21 --output exports/
```

**Available Metrics**:
- `load` - Actual electricity consumption (MW)
- `prices` - Day-ahead market clearing prices (EUR/MWh)
- `generation` - Actual generation by production type
- Use `--flow FROM TO` for cross-border physical flows

**Output**: CSV files saved to `data/` directory (or custom directory specified with `--output`)

**B) Nord Pool Data Collector**

[scripts/nordpool_client.py](scripts/nordpool_client.py)

This script fetches intraday market statistics from Nord Pool Exchange, including VWAP prices, trading volumes, and high/low price ranges for 15-minute Market Time Units.

**Purpose**: Collect market trading data for intraday price analysis, volatility monitoring, and trading strategy backtesting across Nordic bidding zones.

**Usage Examples**:

```bash
# Fetch data for Swedish and Finnish markets
python scripts/nordpool_client.py --areas SE3,FI --date 2026-07-21

# Fetch data for all Nordic bidding zones
python scripts/nordpool_client.py --areas SE1,SE2,SE3,SE4,FI,NO1,NO2,NO3,NO4,NO5,DK1,DK2 --date 2026-07-21

# Save output as JSON instead of CSV
python scripts/nordpool_client.py --areas FI --date 2026-07-21 --format json

# Save both CSV and JSON
python scripts/nordpool_client.py --areas SE3,FI --date 2026-07-21 --format both
```

**Available Bidding Zones**:
- Sweden: SE1, SE2, SE3, SE4
- Finland: FI
- Norway: NO1, NO2, NO3, NO4, NO5
- Denmark: DK1, DK2

**Output**: CSV or JSON files saved to `data/` directory

### 9.2 FastAPI Backend Server

The FastAPI backend provides REST API endpoints and automated background data collection.

**Starting the Development Server**:

```bash
# Activate virtual environment
source venv/bin/activate

# Start FastAPI with auto-reload
python scripts/main.py
```

The server will start on `http://localhost:8000` with the following features:
- Interactive API documentation at `http://localhost:8000/docs`
- Alternative API docs at `http://localhost:8000/redoc`
- Background schedulers running every 15 minutes
- Health check endpoint at `http://localhost:8000/api/v1/health`

**Using Uvicorn Directly** (Production):

```bash
uvicorn scripts.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Testing API Endpoints**:

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Fetch latest prices for SE3
curl "http://localhost:8000/api/v1/prices/latest?area=SE3&limit=96"

# Fetch latest ENTSO-E load data for Finland
curl "http://localhost:8000/api/v1/entsoe/latest?zone=FI&metric=actual_load"

# Trigger on-demand Nord Pool data fetch
curl -X POST "http://localhost:8000/api/v1/market-data/fetch" \
  -H "Content-Type: application/json" \
  -d '{"areas": ["SE3", "FI"], "delivery_date": "2026-07-21"}'
```

### 9.3 Docker Deployment

Deploy the FastAPI backend as a standalone Docker container.

**Build Docker Image**:

```bash
# Build with custom tag
docker build -t power-trading-backend:1.0 .

# Build without cache (clean build)
docker build --no-cache -t power-trading-backend:1.0 .
```

**Run Container**:

```bash
# Run with environment variables
docker run -d \
  --name power-backend \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://trader_admin:SecureTradingPassword2026!@host.docker.internal:5432/power_db" \
  -e ENTSOE_API_KEY="your_api_key" \
  -e NORDPOOL_API_KEY="your_api_key" \
  power-trading-backend:1.0

# View logs
docker logs -f power-backend

# Stop container
docker stop power-backend
```

### 9.4 Docker Compose Full Stack

Deploy the complete platform including FastAPI backend, TimescaleDB, and Grafana.

**Start All Services**:

```bash
# Start in detached mode
docker-compose up -d

# View logs from all services
docker-compose logs -f

# View logs from specific service
docker-compose logs -f trading-backend
```

**Service Access**:
- FastAPI Backend: `http://localhost:8000`
- Grafana Dashboard: `http://localhost:3000` (admin/admin_grafana_pass)
- PostgreSQL/TimescaleDB: `localhost:5432`

**Stop All Services**:

```bash
# Stop services but keep data
docker-compose stop

# Stop and remove containers (keeps volumes)
docker-compose down

# Stop, remove containers and volumes (deletes all data)
docker-compose down -v
```

**Useful Docker Compose Commands**:

```bash
# Rebuild specific service
docker-compose up -d --build trading-backend

# View service status
docker-compose ps

# Execute command in running container
docker-compose exec trading-backend bash

# Access database shell
docker-compose exec timeseries-db psql -U trader_admin -d power_db
```

---

## 10. Python Scripts Documentation

### 10.1 ENTSO-E Data Collector

**File**: [scripts/entsoe_client.py](scripts/entsoe_client.py)

**Class**: `EntsoeDataCollector`

This module provides an interface to the ENTSO-E Transparency Platform REST API using the `entsoe-py` wrapper library.

**Core Methods**:

```python
def fetch_load_data(country_code: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame
```
Retrieves actual load (electricity demand) time-series data for a specified bidding zone.

```python
def fetch_day_ahead_prices(country_code: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame
```
Retrieves day-ahead market clearing prices for specified bidding zone.

```python
def fetch_generation_data(country_code: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame
```
Retrieves actual generation broken down by production type (wind, solar, hydro, nuclear, fossil).

```python
def fetch_cross_border_flows(country_from: str, country_to: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame
```
Retrieves physical electricity flows between two bidding zones.

**Command-Line Interface**:

```
usage: entsoe_client.py [-h] --start START --end END [--zone ZONE] 
                        [--metrics METRICS] [--flow FROM TO] [--output OUTPUT]

arguments:
  --zone          Bidding zone code (e.g., FI, SE, NO, DK)
  --start         Start date (YYYY-MM-DD)
  --end           End date (YYYY-MM-DD)
  --metrics       Comma-separated: load,prices,generation
  --flow FROM TO  Fetch cross-border flow between two zones
  --output        Output directory (default: data)
```

**Error Handling**:
- Automatically handles API rate limiting
- Retries failed requests with exponential backoff
- Validates timezone conversions (all data normalized to UTC)
- Handles missing data points gracefully

**Output Format**: CSV files with timestamp index and metric columns

### 10.2 Nord Pool Data Collector

**File**: [scripts/nordpool_client.py](scripts/nordpool_client.py)

**Class**: `NordPoolDataCollector`

This module provides an asynchronous HTTP client for fetching intraday market statistics from Nord Pool Exchange APIs.

**Core Methods**:

```python
async def fetch_intraday_statistics(areas: List[str], delivery_date: date) -> List[Dict[str, Any]]
```
Fetches intraday hourly statistics including VWAP, high/low prices, volumes, and first/last trade times.

**Response Fields**:
- `start_time` - Market time unit start (ISO format)
- `end_time` - Market time unit end (ISO format)
- `area` - Bidding zone code
- `vwap_eur_mwh` - Volume-weighted average price
- `high_price` - Highest execution price
- `low_price` - Lowest execution price
- `volume_mwh` - Total traded volume
- `first_trade_time` - Timestamp of first trade
- `last_trade_time` - Timestamp of last trade

**Command-Line Interface**:

```
usage: nordpool_client.py [-h] --areas AREAS --date DATE
                          [--api-key API_KEY] [--format {csv,json,both}]
                          [--output OUTPUT]

arguments:
  --areas    Comma-separated bidding zones (e.g., SE3,FI,NO1)
  --date     Delivery date (YYYY-MM-DD)
  --api-key  Nord Pool API key (overrides env var)
  --format   Output format: csv, json, or both (default: csv)
  --output   Output directory (default: data)
```

**Error Handling**:
- HTTP 401: Authentication failure (invalid API key)
- HTTP 429: Rate limit exceeded (retry with backoff)
- HTTP 503: Service unavailable (connection timeout)

**Output Format**: CSV or JSON files with market statistics per 15-minute MTU

### 10.3 Automated Background Tasks

**File**: [scripts/tasks.py](scripts/tasks.py)

This module defines scheduled background jobs executed by APScheduler within the FastAPI application lifecycle.

**Task**: `auto_fetch_nordpool_job()`

**Schedule**: Every 15 minutes
**Purpose**: Automatically fetch Nord Pool intraday statistics for configured bidding zones and store in TimescaleDB

**Execution Flow**:
1. Initialize Nord Pool connector with API credentials
2. Query today's delivery date for zones: SE3, FI, NO1, DK1
3. Parse API response into PriceRecord objects
4. Open async database session
5. Upsert records using PostgreSQL `INSERT ... ON CONFLICT DO UPDATE`
6. Handle duplicates by updating price with latest value
7. Commit transaction and log success

**Task**: `auto_fetch_entsoe_job()`

**Schedule**: Every 15 minutes (offset +10 seconds)
**Purpose**: Automatically fetch ENTSO-E grid metrics (load and prices) and store in TimescaleDB

**Execution Flow**:
1. Initialize ENTSO-E client with API token
2. Define sliding 24-hour window (12 hours past to 12 hours future)
3. For each bidding zone (FI, SE3, NO1):
   - Query actual load data
   - Query day-ahead prices
   - Parse pandas Series/DataFrame responses
   - Filter invalid/missing data points
4. Batch upsert to database with conflict handling
5. Log metrics per zone

**Configuration**:

Both tasks are configured in [scripts/main.py](scripts/main.py) within the FastAPI lifespan context:

```python
scheduler.add_job(
    auto_fetch_nordpool_job,
    trigger=IntervalTrigger(minutes=15),
    id="nordpool_15min_scraper",
    replace_existing=True,
    max_instances=1  # Prevents overlapping executions
)
```

**Monitoring**:
- Check task execution via logs: `docker-compose logs -f trading-backend`
- Query scheduler status: `GET /api/v1/scheduler/status`
- Monitor data freshness: Query `fetched_at` timestamps in database

---

## 11. Database Configuration

### 11.1 TimescaleDB Setup

TimescaleDB is a time-series database built on PostgreSQL that provides automatic data partitioning (hypertables), advanced indexing, and efficient compression for time-series workloads.

**Automatic Initialization**:

When using Docker Compose, the database is automatically initialized with the SQL script in [init-db/01_timescale.sql](init-db/01_timescale.sql).

**Manual Setup** (if running PostgreSQL locally):

```bash
# Install TimescaleDB extension (Ubuntu/Debian)
sudo apt install postgresql-16-timescaledb

# Or use Docker official image
docker run -d --name timescaledb -p 5432:5432 \
  -e POSTGRES_PASSWORD=mypassword \
  timescale/timescaledb-ha:pg16

# Connect and create extension
psql -U postgres -c "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"
```

### 11.2 Schema and Indexes

**Table: `intraday_prices`**

Stores Nord Pool intraday market price records with 15-minute granularity.

```sql
CREATE TABLE intraday_prices (
    id VARCHAR(100) PRIMARY KEY,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    area VARCHAR(10) NOT NULL,
    price_eur DOUBLE PRECISION NOT NULL,
    fetched_at TIMESTAMP DEFAULT NOW()
);

-- Convert to hypertable (7-day chunks)
SELECT create_hypertable('intraday_prices', 'start_time',
    chunk_time_interval => INTERVAL '7 days');

-- Composite index for fast queries
CREATE INDEX idx_area_start_time ON intraday_prices (area, start_time DESC);

-- Unique constraint to prevent duplicates
ALTER TABLE intraday_prices
    ADD CONSTRAINT _start_time_area_uc UNIQUE (start_time, area);
```

**Table: `entsoe_grid_data`**

Stores ENTSO-E Transparency Platform metrics (load, generation, prices).

```sql
CREATE TABLE entsoe_grid_data (
    id VARCHAR(120) PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    bidding_zone VARCHAR(10) NOT NULL,
    metric_name VARCHAR(30) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    fetched_at TIMESTAMP DEFAULT NOW()
);

-- Convert to hypertable
SELECT create_hypertable('entsoe_grid_data', 'timestamp',
    chunk_time_interval => INTERVAL '7 days');

-- Composite index for metric queries
CREATE INDEX idx_entsoe_lookup ON entsoe_grid_data
    (bidding_zone, metric_name, timestamp DESC);

-- Unique constraint
ALTER TABLE entsoe_grid_data
    ADD CONSTRAINT _entsoe_metric_uc
    UNIQUE (timestamp, bidding_zone, metric_name);
```

**Index Strategy**:
- Composite indexes on `(area/zone, timestamp)` optimize queries filtering by zone and time range
- Descending timestamp order optimizes `ORDER BY timestamp DESC` queries (latest data first)
- B-tree indexes on individual columns for flexible query patterns

### 11.3 Data Retention Policies

TimescaleDB supports automatic data retention to manage storage costs.

**Enable Retention** (optional, uncomment in init script):

```sql
-- Auto-delete data older than 90 days
SELECT add_retention_policy('intraday_prices', INTERVAL '90 days');
SELECT add_retention_policy('entsoe_grid_data', INTERVAL '90 days');
```

**Manual Data Cleanup**:

```sql
-- Delete data older than 6 months
DELETE FROM intraday_prices WHERE start_time < NOW() - INTERVAL '6 months';
DELETE FROM entsoe_grid_data WHERE timestamp < NOW() - INTERVAL '6 months';

-- Check table sizes
SELECT 
    hypertable_name,
    pg_size_pretty(hypertable_size(format('%I.%I', hypertable_schema, hypertable_name)::regclass)) as size
FROM timescaledb_information.hypertables;
```

**Compression** (for older data):

```sql
-- Enable compression on chunks older than 7 days
SELECT add_compression_policy('intraday_prices', INTERVAL '7 days');
SELECT add_compression_policy('entsoe_grid_data', INTERVAL '7 days');
```

---

## 12. Visualization with Grafana

### 12.1 Grafana Setup

Grafana is automatically configured via Docker Compose with PostgreSQL data source provisioning.

**Access Grafana**:
- URL: `http://localhost:3000`
- Username: `admin`
- Password: `admin_grafana_pass` (configured in docker-compose.yml)

**Data Source**: PostgreSQL-PowerDB is automatically provisioned from [grafana/provisioning/datasources/datasource.yml](grafana/provisioning/datasources/datasource.yml)

### 12.2 Dashboard Configuration

**Creating a New Dashboard**:

1. Click "+" icon → "Dashboard" → "Add new panel"
2. Select "PostgreSQL-PowerDB" as data source
3. Choose "Table" or "Time series" visualization
4. Write SQL query (see examples below)
5. Configure visualization options (axes, legends, colors)
6. Save dashboard

**Dashboard Layout Best Practices**:
- Use time-series panels for price trends and load curves
- Use stat panels for current/latest values
- Use table panels for detailed transaction lists
- Group related panels in rows
- Add variables for dynamic zone selection

### 12.3 Query Examples

**Query 1: Intraday Price Time Series (Multi-Zone)**

```sql
SELECT
  start_time AS "time",
  area AS metric,
  price_eur AS value
FROM intraday_prices
WHERE
  $__timeFilter(start_time)
  AND area IN ('SE3', 'FI', 'NO1')
ORDER BY start_time ASC;
```

**Grafana Settings**:
- Visualization: Time series
- Legend: {{metric}} (shows area names)
- Y-axis: EUR/MWh
- Time range: Use dashboard time picker

**Query 2: Price Volatility Analysis (Table)**

```sql
SELECT
  area AS "Zone",
  ROUND(AVG(price_eur)::numeric, 2) AS "Avg Price (EUR/MWh)",
  ROUND(MAX(price_eur)::numeric, 2) AS "Peak (EUR/MWh)",
  ROUND(MIN(price_eur)::numeric, 2) AS "Floor (EUR/MWh)",
  ROUND((MAX(price_eur) - MIN(price_eur))::numeric, 2) AS "Spread (EUR/MWh)",
  ROUND(STDDEV(price_eur)::numeric, 2) AS "Std Dev"
FROM intraday_prices
WHERE
  $__timeFilter(start_time)
GROUP BY area
ORDER BY "Spread (EUR/MWh)" DESC;
```

**Query 3: Data Pipeline Health Check (Stat Panel)**

```sql
SELECT
  EXTRACT(EPOCH FROM (NOW() - MAX(fetched_at))) / 60 AS value
FROM intraday_prices;
```

**Grafana Settings**:
- Visualization: Stat
- Unit: minutes (m)
- Thresholds: Green <16, Yellow 16-30, Red >30
- Title: "Minutes Since Last Data Update"

**Query 4: ENTSO-E Load vs Price Correlation**

```sql
-- Load data
SELECT
  timestamp AS "time",
  'Actual Load (MW)' AS metric,
  metric_value AS value
FROM entsoe_grid_data
WHERE
  $__timeFilter(timestamp)
  AND bidding_zone = 'FI'
  AND metric_name = 'actual_load'

UNION ALL

-- Price data (scaled for visualization)
SELECT
  g.timestamp AS "time",
  'Day-Ahead Price (EUR/MWh × 10)' AS metric,
  g.metric_value * 10 AS value
FROM entsoe_grid_data g
WHERE
  $__timeFilter(g.timestamp)
  AND g.bidding_zone = 'FI'
  AND g.metric_name = 'intraday_price'

ORDER BY "time" ASC;
```

**Grafana Settings**:
- Visualization: Time series
- Use dual Y-axes (one for MW, one for EUR/MWh)
- Override field: Set unit for each metric

### 12.4 Alert Configuration

Grafana alerts monitor data quality and detect market anomalies.

**Alert 1: Price Spike Detection**

**Condition**: Alert when intraday price exceeds €250/MWh for more than 2 minutes

**Configuration**:
```
Query: SELECT MAX(price_eur) FROM intraday_prices
       WHERE start_time >= NOW() - INTERVAL '15 minutes'
       
Condition: WHEN max() OF query(A, 15m, now) IS ABOVE 250

For: 2m (must sustain for 2 minutes)

Notification: Slack channel #energy-alerts
```

**Alert 2: Data Ingestion Failure**

**Condition**: Alert when no new data received in last 30 minutes

**Configuration**:
```
Query: SELECT COUNT(*) FROM intraday_prices
       WHERE fetched_at >= NOW() - INTERVAL '30 minutes'
       
Condition: WHEN count() OF query(A, 30m, now) IS BELOW 1

For: 5m

Notification: Slack channel #infrastructure-alerts
```

**Setting Up Slack Notifications**:

1. Create Slack incoming webhook: `https://api.slack.com/messaging/webhooks`
2. Add webhook URL to Grafana contact point
3. Configure alert routing rules
4. Test notification delivery

---

## 13. Cloud Deployment on AWS

### 13.1 Infrastructure Requirements

Deploying the Power Trading Platform on AWS requires the following infrastructure components:

**Compute**:
- EC2 Instance or ECS Fargate for FastAPI backend
- Recommended: t3.medium (2 vCPU, 4 GB RAM) or larger
- Auto Scaling Group for high availability

**Database**:
- RDS PostgreSQL with TimescaleDB extension
- Recommended: db.t3.medium or larger
- Multi-AZ deployment for production
- Automated backups enabled

**Container Registry**:
- Amazon ECR for Docker image storage
- Private repository for backend image

**Networking**:
- VPC with public and private subnets
- Application Load Balancer for HTTPS termination
- Security Groups for access control

**Monitoring**:
- CloudWatch for logs and metrics
- CloudWatch Alarms for automated alerting
- Optional: Grafana on EC2 or Grafana Cloud

**Storage**:
- EBS volumes for database storage
- S3 bucket for data exports and backups

### 13.2 IAM Roles and Security

**IAM Role for EC2/ECS**:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:*:*:secret:power-trading/*"
    }
  ]
}
```

**Security Groups**:

**ALB Security Group**:
- Inbound: HTTPS (443) from 0.0.0.0/0
- Inbound: HTTP (80) from 0.0.0.0/0 (redirect to HTTPS)
- Outbound: All traffic

**Backend Security Group**:
- Inbound: 8000 from ALB Security Group
- Outbound: 443 to 0.0.0.0/0 (for API calls)
- Outbound: 5432 to RDS Security Group

**RDS Security Group**:
- Inbound: 5432 from Backend Security Group
- Outbound: None required

**Grafana Security Group** (if EC2):
- Inbound: 3000 from ALB Security Group or specific IPs
- Outbound: 5432 to RDS Security Group

**API Key Management**:

Store sensitive credentials in AWS Secrets Manager:

```bash
# Store ENTSO-E API key
aws secretsmanager create-secret \
  --name power-trading/entsoe-api-key \
  --secret-string "your_entsoe_api_key"

# Store Nord Pool API key
aws secretsmanager create-secret \
  --name power-trading/nordpool-api-key \
  --secret-string "your_nordpool_api_key"

# Store database password
aws secretsmanager create-secret \
  --name power-trading/db-password \
  --secret-string "SecureTradingPassword2026!"
```

**Dashboard Authorization**:

Implement authentication for public-facing Grafana:
- Use Grafana OAuth integration with AWS Cognito
- Configure IAM roles for read-only vs admin access
- Enable Grafana LDAP/SAML for enterprise SSO

### 13.3 Deployment Architecture

```
                            ┌─────────────────────────┐
                            │    Route 53 (DNS)       │
                            │ trading.yourdomain.com  │
                            └────────────┬────────────┘
                                         │
                                         ▼
                            ┌─────────────────────────┐
                            │  Application Load       │
                            │  Balancer (ALB)         │
                            │  - HTTPS Termination    │
                            │  - Path-based routing   │
                            └────────────┬────────────┘
                                         │
                   ┌─────────────────────┼─────────────────────┐
                   │                     │                     │
                   ▼                     ▼                     ▼
        ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
        │  ECS Fargate     │  │  ECS Fargate     │  │  EC2 Instance    │
        │  FastAPI Backend │  │  FastAPI Backend │  │  Grafana         │
        │  Task 1          │  │  Task 2          │  │                  │
        └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘
                 │                     │                     │
                 └─────────────────────┴─────────────────────┘
                                       │
                                       ▼
                          ┌─────────────────────────┐
                          │  RDS PostgreSQL         │
                          │  with TimescaleDB       │
                          │  - Multi-AZ             │
                          │  - Automated Backups    │
                          └─────────────────────────┘

                                       │
                                       ▼
                          ┌─────────────────────────┐
                          │  External APIs          │
                          │  - ENTSO-E Platform     │
                          │  - Nord Pool Exchange   │
                          └─────────────────────────┘
```

### 13.4 Step-by-Step AWS Deployment

**Step 1: Create ECR Repository**

```bash
# Create ECR repository
aws ecr create-repository --repository-name power-trading-backend

# Get repository URI
REPO_URI=$(aws ecr describe-repositories --repository-names power-trading-backend \
  --query 'repositories[0].repositoryUri' --output text)

echo $REPO_URI
```

**Step 2: Build and Push Docker Image**

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $REPO_URI

# Build image
docker build -t power-trading-backend:latest .

# Tag image
docker tag power-trading-backend:latest $REPO_URI:latest

# Push to ECR
docker push $REPO_URI:latest
```

**Step 3: Create RDS PostgreSQL Instance**

```bash
# Create DB subnet group
aws rds create-db-subnet-group \
  --db-subnet-group-name power-trading-db-subnet \
  --db-subnet-group-description "Subnet group for power trading DB" \
  --subnet-ids subnet-xxx subnet-yyy

# Create RDS instance with PostgreSQL
aws rds create-db-instance \
  --db-instance-identifier power-trading-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 16.1 \
  --master-username trader_admin \
  --master-user-password SecureTradingPassword2026! \
  --allocated-storage 100 \
  --storage-type gp3 \
  --vpc-security-group-ids sg-xxxxx \
  --db-subnet-group-name power-trading-db-subnet \
  --backup-retention-period 7 \
  --multi-az \
  --publicly-accessible false

# Wait for instance to be available
aws rds wait db-instance-available --db-instance-identifier power-trading-db
```

**Step 4: Install TimescaleDB Extension**

```bash
# Connect to RDS instance
psql -h power-trading-db.xxxxx.us-east-1.rds.amazonaws.com \
  -U trader_admin -d postgres

# Create database and enable TimescaleDB
CREATE DATABASE power_db;
\c power_db
CREATE EXTENSION timescaledb;

# Run initialization script
\i init-db/01_timescale.sql
```

**Step 5: Create ECS Cluster and Task Definition**

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name power-trading-cluster

# Register task definition (see task-definition.json below)
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

**task-definition.json**:

```json
{
  "family": "power-trading-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "{REPO_URI}:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "APP_ENV",
          "value": "production"
        },
        {
          "name": "DATABASE_URL",
          "value": "postgresql+asyncpg://trader_admin:SecureTradingPassword2026!@power-trading-db.xxxxx.us-east-1.rds.amazonaws.com:5432/power_db"
        }
      ],
      "secrets": [
        {
          "name": "ENTSOE_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:power-trading/entsoe-api-key"
        },
        {
          "name": "NORDPOOL_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT_ID:secret:power-trading/nordpool-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/power-trading-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**Step 6: Create Application Load Balancer**

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name power-trading-alb \
  --subnets subnet-xxx subnet-yyy \
  --security-groups sg-alb-xxxxx

# Create target group
aws elbv2 create-target-group \
  --name power-trading-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-xxxxx \
  --target-type ip \
  --health-check-path /api/v1/health

# Create listener
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...
```

**Step 7: Create ECS Service**

```bash
aws ecs create-service \
  --cluster power-trading-cluster \
  --service-name power-trading-service \
  --task-definition power-trading-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-backend-xxxxx],assignPublicIp=DISABLED}" \
  --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=backend,containerPort=8000
```

**Step 8: Configure CloudWatch Monitoring**

```bash
# Create CloudWatch log group
aws logs create-log-group --log-group-name /ecs/power-trading-backend

# Create alarm for high error rate
aws cloudwatch put-metric-alarm \
  --alarm-name power-trading-high-errors \
  --alarm-description "Alert when error rate exceeds 10%" \
  --metric-name Errors \
  --namespace AWS/ApplicationELB \
  --statistic Average \
  --period 300 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

**Cost Estimation** (Monthly, US East):
- ECS Fargate (2 tasks, t3.medium equivalent): ~$60
- RDS PostgreSQL (db.t3.medium, Multi-AZ): ~$150
- Application Load Balancer: ~$25
- Data Transfer (estimate): ~$10
- **Total**: ~$245/month

---

## 14. API Documentation

### 14.1 REST API Endpoints

The FastAPI backend provides a RESTful API for data access and on-demand collection.

**Base URL**: `http://localhost:8000` (development) or `https://trading.yourdomain.com` (production)

**Interactive Documentation**: `http://localhost:8000/docs` (Swagger UI)

**Endpoints**:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint with API information |
| GET | `/api/v1/health` | Health check (database and scheduler status) |
| POST | `/api/v1/market-data/fetch` | Trigger on-demand Nord Pool data fetch |
| GET | `/api/v1/prices/latest` | Get latest stored Nord Pool prices |
| GET | `/api/v1/entsoe/latest` | Get latest ENTSO-E grid data |
| GET | `/api/v1/scheduler/status` | Get background scheduler status |

**Detailed Endpoint Specifications**:

**`GET /api/v1/health`**

Returns system health status including database connectivity and scheduler state.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-07-21T12:00:00",
  "database_connected": true,
  "scheduler_running": true
}
```

**`POST /api/v1/market-data/fetch`**

Triggers real-time Nord Pool data collection for specified bidding zones.

**Request Body**:
```json
{
  "areas": ["SE3", "FI", "NO1"],
  "delivery_date": "2026-07-21"
}
```

**Response**:
```json
{
  "status": "success",
  "source": "NordPool_V2",
  "records_count": 288,
  "data": [
    {
      "start_time": "2026-07-21T00:00:00",
      "end_time": "2026-07-21T00:15:00",
      "area": "SE3",
      "price_eur": 42.35
    }
  ]
}
```

**`GET /api/v1/prices/latest`**

Retrieves latest stored intraday prices from database.

**Query Parameters**:
- `area` (string, required): Bidding zone code (e.g., "SE3")
- `limit` (integer, optional, default=96): Number of records to return

**Example Request**:
```
GET /api/v1/prices/latest?area=FI&limit=48
```

**Response**:
```json
{
  "area": "FI",
  "count": 48,
  "data": [
    {
      "start_time": "2026-07-21T11:45:00",
      "end_time": "2026-07-21T12:00:00",
      "price_eur_mwh": 45.67
    }
  ]
}
```

**`GET /api/v1/entsoe/latest`**

Retrieves latest ENTSO-E grid metrics from database.

**Query Parameters**:
- `zone` (string, required): Bidding zone code (e.g., "FI")
- `metric` (string, required): Metric name ("actual_load" or "intraday_price")
- `limit` (integer, optional, default=48): Number of records

**Example Request**:
```
GET /api/v1/entsoe/latest?zone=FI&metric=actual_load&limit=24
```

**Response**:
```json
{
  "bidding_zone": "FI",
  "metric": "actual_load",
  "count": 24,
  "data": [
    {
      "timestamp": "2026-07-21T11:00:00",
      "value": 7234.5
    }
  ]
}
```

### 14.2 Authentication

**Current Implementation**: No authentication required (development mode)

**Production Recommendations**:

Implement API key authentication using FastAPI dependencies:

```python
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

API_KEY = "your-secure-api-key"
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    return api_key

# Protect endpoints
@app.get("/api/v1/prices/latest", dependencies=[Depends(verify_api_key)])
async def get_latest_prices(...):
    pass
```

**Using API Keys**:
```bash
curl -H "X-API-Key: your-secure-api-key" \
  http://localhost:8000/api/v1/prices/latest?area=SE3
```

### 14.3 Rate Limiting

**Current Implementation**: No rate limiting (development mode)

**Production Implementation**:

Use `slowapi` library for rate limiting:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/v1/prices/latest")
@limiter.limit("100/minute")
async def get_latest_prices(request: Request, ...):
    pass
```

**Recommended Limits**:
- Public endpoints: 100 requests/minute per IP
- Authenticated users: 1000 requests/minute per API key
- Admin endpoints: 10 requests/minute

---

## 15. Troubleshooting

**Issue**: `ModuleNotFoundError: No module named 'entsoe'`

**Solution**: Activate virtual environment and install dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Issue**: ENTSO-E API returns 401 Unauthorized

**Solution**: Verify API key is correctly set in `.env` file and registered with ENTSO-E
```bash
# Check environment variable
echo $ENTSOE_API_KEY

# Test API key manually
curl -H "securityToken: YOUR_API_KEY" \
  "https://web-api.tp.entsoe.eu/api?documentType=A44&..."
```

**Issue**: Docker Compose database connection refused

**Solution**: Ensure database service is healthy before backend starts
```bash
# Check service health
docker-compose ps

# View database logs
docker-compose logs timeseries-db

# Restart services in correct order
docker-compose down
docker-compose up -d timeseries-db
# Wait 10 seconds
docker-compose up -d trading-backend
```

**Issue**: Grafana shows "Database connection failed"

**Solution**: Verify PostgreSQL data source configuration
```bash
# Access Grafana container
docker-compose exec grafana-dashboard bash

# Test database connection
psql -h timeseries-db -U trader_admin -d power_db -c "SELECT 1;"
```

**Issue**: Background tasks not executing

**Solution**: Check scheduler logs and verify APScheduler is running
```bash
# View backend logs
docker-compose logs -f trading-backend

# Check scheduler status via API
curl http://localhost:8000/api/v1/scheduler/status
```

**Issue**: High memory usage in Docker containers

**Solution**: Adjust resource limits in docker-compose.yml
```yaml
services:
  trading-backend:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

**Issue**: TimescaleDB hypertable not created

**Solution**: Manually run initialization script
```bash
docker-compose exec timeseries-db psql -U trader_admin -d power_db -f /docker-entrypoint-initdb.d/01_timescale.sql
```

**Getting Help**:
- Check application logs: `docker-compose logs -f`
- Query database directly: `docker-compose exec timeseries-db psql -U trader_admin -d power_db`
- View FastAPI interactive docs: `http://localhost:8000/docs`
- Enable debug logging: Set `LOG_LEVEL=DEBUG` in `.env`

---

## 16. References

### Official Market Documentation

1. **Nord Pool Exchange**
   - [Intraday Hourly Statistics Portal](https://data.nordpoolgroup.com/intraday/intraday-hourly-statistics)
   - [Intraday Auctions Documentation](https://www.nordpoolgroup.com/en/services/power-market-data-services/intraday-auctions/)
   - [Market Data Services Overview](https://www.nordpoolgroup.com/en/services/power-market-data-services/)
   - [Nord Pool Trading Rules and Regulations](https://www.nordpoolgroup.com/en/trading/trading-rules/)

2. **ENTSO-E Transparency Platform**
   - [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/)
   - [RESTful API Documentation](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html)
   - [Data Portal and Downloads](https://transparency.entsoe.eu/dashboard/show)

3. **Regulatory and Market Guidelines**
   - European Commission. "Commission Recommendation on long-term Power Purchase Agreements." [EUR-Lex Access](https://eur-lex.europa.eu/)
   - ACER (Agency for the Cooperation of Energy Regulators). "Decision on the establishment of a common methodology for intraday cross-zonal capacity allocation."
   - ENTSO-E Network Codes: Balancing, Capacity Allocation, and Congestion Management

### Technical Documentation and Libraries

4. **Python Libraries**
   - [entsoe-py GitHub Repository](https://github.com/EnergieID/entsoe-py) - Official Python client for ENTSO-E API
   - [FastAPI Documentation](https://fastapi.tiangolo.com/) - Modern web framework for building APIs
   - [SQLAlchemy Documentation](https://docs.sqlalchemy.org/en/20/) - SQL toolkit and ORM
   - [TimescaleDB Documentation](https://docs.timescale.com/) - Time-series database for PostgreSQL
   - [APScheduler Documentation](https://apscheduler.readthedocs.io/) - Advanced Python scheduler

5. **Database and Time-Series Management**
   - [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
   - [TimescaleDB Best Practices](https://docs.timescale.com/use-timescale/latest/best-practices/)
   - [TimescaleDB Hypertables Guide](https://docs.timescale.com/use-timescale/latest/hypertables/)
   - [asyncpg Documentation](https://magicstack.github.io/asyncpg/current/) - Fast PostgreSQL client for Python

6. **Visualization and Monitoring**
   - [Grafana Documentation](https://grafana.com/docs/)
   - [PostgreSQL Data Source for Grafana](https://grafana.com/docs/grafana/latest/datasources/postgres/)
   - [Grafana Alerting Documentation](https://grafana.com/docs/grafana/latest/alerting/)

7. **Cloud Deployment Guides**
   - [AWS ECS Fargate Documentation](https://docs.aws.amazon.com/ecs/index.html)
   - [Amazon RDS for PostgreSQL](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
   - [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/)
   - [Docker Compose Documentation](https://docs.docker.com/compose/)

### Energy Market Research and Analysis

8. **Power Purchase Agreements (PPAs)**
   - Microsoft 2024 Environmental Sustainability Report. "Renewable Energy Procurement." [Microsoft Sustainability](https://www.microsoft.com/en-us/sustainability)
   - BloombergNEF. "Corporate Clean Energy Buying Surges to New Record." BNEF Report, 2024.
   - International Renewable Energy Agency (IRENA). "Renewable Power Purchase Agreements: Scaling up Globally." 2023.

9. **Intraday Trading and Market Analysis**
   - [Next Kraftwerke - Intraday Trading Guide](https://www.next-kraftwerke.com/knowledge/intraday-trading)
   - [SmartPulse - Intraday Power Trading Strategies](https://www.smartpulse.io/intraday-power-trading-2-how-to-trade-strategies-algorithms/)
   - EPEX SPOT Market Data Portal. "Continuous Intraday Trading Statistics."

10. **Academic Literature on Energy Markets**
    - Weron, R. (2014). "Electricity price forecasting: A review of the state-of-the-art with a look into the future." *International Journal of Forecasting*, 30(4), 1030-1081.
    - Kiesel, R., & Paraschiv, F. (2017). "Econometric analysis of 15-minute intraday electricity prices." *Energy Economics*, 64, 77-90.
    - Hagemann, S., & Weber, C. (2015). "Trading volumes in intraday markets: Theoretical reference model and empirical observations in selected European markets." *Zeitschrift für Energiewirtschaft*, 39(2), 121-134.

### Community and Support

11. **Developer Communities**
    - [Stack Overflow - TimescaleDB Tag](https://stackoverflow.com/questions/tagged/timescaledb)
    - [FastAPI GitHub Discussions](https://github.com/tiangolo/fastapi/discussions)
    - [ENTSO-E API Support Forum](https://transparency.entsoe.eu/content/static_content/Static%20content/support.html)

12. **Professional Networks**
    - Energy Data Analytics LinkedIn Group
    - Renewable Energy Trading Professionals Network
    - European Power Trading Forum

---

### Primary Data Sources

1. Nord Pool Group - Intraday Auctions
   [https://www.nordpoolgroup.com/en/services/power-market-data-services/intraday-auctions/](https://www.nordpoolgroup.com/en/services/power-market-data-services/intraday-auctions/)

2. Nord Pool Data Portal - Intraday Hourly Statistics
   [https://data.nordpoolgroup.com/intraday/intraday-hourly-statistics?deliveryDate=latest&deliveryArea=DK1](https://data.nordpoolgroup.com/intraday/intraday-hourly-statistics?deliveryDate=latest&deliveryArea=DK1)

3. ENTSO-E Transparency Platform
   [https://transparency.entsoe.eu/](https://transparency.entsoe.eu/)

### Technical and Educational Resources

4. Next Kraftwerke - Intraday Trading Knowledge Base
   [https://www.next-kraftwerke.com/knowledge/intraday-trading](https://www.next-kraftwerke.com/knowledge/intraday-trading)

5. SmartPulse - Intraday Power Trading Strategies and Algorithms
   [https://www.smartpulse.io/intraday-power-trading-2-how-to-trade-strategies-algorithms/](https://www.smartpulse.io/intraday-power-trading-2-how-to-trade-strategies-algorithms/)

### Market Context

- Microsoft's announcement of matching 100% of annual global electricity consumption with renewable energy through PPAs and renewable energy certificates demonstrates the scale and strategic importance of corporate PPAs in renewable energy deployment.

- Regulatory recommendations on removing barriers to Power Purchase Agreements emphasize policy support for these instruments as mechanisms to accelerate clean energy transition and support affordable energy objectives.

- The transition of Nordic markets to 15-minute Market Time Units (MTU) and the introduction of Intraday Auctions in June 2024 represent significant market design evolution to accommodate renewable energy integration.

---

*Document prepared as an academic resource for understanding power markets, PPAs, and intraday trading mechanisms. Data and examples focus on Nordic markets (Sweden, Norway, Finland, Denmark) for the period 2024-2026.*

**License**: MIT (for source code) | CC BY 4.0 (for documentation)

**Last Updated**: July 21, 2026
