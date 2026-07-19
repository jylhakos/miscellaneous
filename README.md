# Miscellaneous Projects

A collection of software development projects demonstrating multiple domains including machine learning, large language models, blockchain, embedded systems, web services, and enterprise applications. Each project showcases practical implementations using modern technologies and industry best practices.

## Project Structure

```
miscellaneous/
├── 📊 BigData/              # Machine Learning & Data Processing
├── 🏗️ BIM/                 # Building Information Modeling
├── 💬 ChatBot/             # AI Conversational Agents
├── 🔧 ChatService/         # Real-time Messaging API
├── 📈 DataAnalytics/       # Full-Stack Analytics Platform
├── � Datasets/            # Feature Selection & Regression ML
├── �🔢 DataStructures/      # Data Manipulation & Processing
├── 📈 DeepLearning/        # Neural Networks & Time Series
├── 🖼️ DigitRecognizer/     # Computer Vision & CNNs
├── ⚙️ EmbeddedSystems/     # Low-Level System Programming
├── 🏢 ERP/                 # Enterprise Resource Planning
├── 🔄 ETL/                 # Data Pipeline Processing
├── 🤖 LLM/                 # Large Language Model Integration
├── 📄 OCR/                 # Optical Character Recognition
├── 🎯 Patterns/            # Software Design Patterns
├── ❓ QUESTIONS/           # Technical Interview Q&A
├── 🏠 SmartBuildings/      # IoT & Building Automation
└── ⛓️ SupplyChain/         # Blockchain Distribution Network
```

---

## 📊 BigData

**Overview:** Production-ready machine learning pipeline implementing binary classification to predict customer subscription behavior using distributed computing with Apache Spark. The project demonstrates end-to-end ML workflow from data ingestion to model deployment with comprehensive feature engineering and validation.

**Key Insights:**
- Implements proper data transformation pipeline with type casting for MLlib compatibility
- Solved issue with DoubleType label column requirement for LogisticRegression
- Demonstrates feature engineering by renaming and encoding categorical variables
- Uses gaming customer data to predict paid subscriber likelihood with 5-iteration logistic regression

**Technologies:** Python, PySpark, Apache Spark MLlib, Jupyter Notebook, Pandas, NumPy, Machine Learning, Binary Classification, Feature Engineering, Data Transformation

---

## 🏗️ BIM (Building Information Modeling)

**Overview:** Web-based 3D building model visualization system leveraging Industry Foundation Classes (IFC) standard. Integrates BIMServer with WebGL rendering for interactive architectural model exploration with GUID-based object linking and Berkeley database storage.

**Key Insights:**
- Implements open-source BIM stack with BIMServer, BIMSurfer, and bimvie.ws plugin architecture
- Uses xeokit's BIMServerLoaderPlugin for efficient model loading and 3D visualization
- Demonstrates RESTful API integration with Tomcat server deployment
- Supports IFC file deserialization and structured data extraction for architectural projects

**Technologies:** JavaScript, Java, HTML, WebGL, HTTP, REST API, Apache Tomcat, IFC (Industry Foundation Classes), Berkeley DB, BIMServer, xeokit, Linux

---

## 💬 ChatBot

**Overview:** Advanced AI chatbot system implementing Retrieval Augmented Generation (RAG) architecture to provide context-aware responses from uploaded documents. Combines large language models with vector database retrieval for accurate, source-grounded question answering.

**Key Insights:**
- Implements complete RAG workflow: data ingestion → embedding → vector storage → retrieval → augmentation → generation
- Supports deployment on AWS SageMaker with Hugging Face Sentence Transformers for embedding generation
- Uses vector similarity search for relevant context retrieval before LLM response generation
- Demonstrates cloud-native architecture with S3 storage and processing jobs

**Technologies:** Python, FastAPI, LangChain, Ollama, ChromaDB, Vector Databases, Hugging Face Transformers, AWS SageMaker, Docker, Natural Language Processing (NLP), Retrieval Augmented Generation (RAG), Embeddings

---

## 🔧 ChatService

**Overview:** High-performance RESTful API service for chat message management with MongoDB backend. Features production-ready architecture including JWT authentication, rate limiting, anomaly detection for spam filtering, and horizontal scaling capabilities.

**Key Insights:**
- Implements clean architecture with separation of handlers, services, and middleware layers
- Includes anomaly detection scoring for spam message identification
- Features comprehensive security middleware (CORS, JWT, rate limiting)
- Containerized with Docker and ready for Kubernetes deployment with GCP Cloud Run support

**Technologies:** Go (Golang), Gin Framework, MongoDB, JWT Authentication, REST API, CORS, Rate Limiting, Docker, Docker Compose, Kubernetes, GCP Cloud Run, Middleware, JSON, Alpine Linux

---

## 📈 DataAnalytics

**Overview:** Full-stack data analytics platform with Go backend and React frontend, featuring secure JWT-based authentication with HttpOnly cookies and interactive data visualization. Demonstrates modern web architecture with Chart.js integration for real-time analytics display.

**Key Insights:**
- Implements secure authentication flow with HttpOnly cookies and SameSite/Secure attributes
- Uses Axios interceptors for automatic token refresh on 401 responses
- Demonstrates CORS configuration for cross-origin resource sharing with credentials
- Features PostgreSQL integration with GORM ORM and Chart.js for data visualization

**Technologies:** **Backend:** Go (Golang), Gin, JWT, GORM, PostgreSQL, SQL, CORS | **Frontend:** JavaScript (ES6+), React, Redux, JSX, Axios, Node.js, npm, Material UI, Chart.js, Webpack, HTML, CSS | **Infrastructure:** Docker, Linux

---

## � Datasets

**Overview:** Anonymised dataset (`dataset.csv`) with 135 unlabelled columns (`COL_000`–`COL_134`) and a hashed `ID`, likely sourced from elevator component measurements. The project demonstrates feature selection and regression ML workflows on an unknown dataset where column semantics are not disclosed — mirroring privacy-constrained, third-party, or pre-processed feature-store scenarios. Python scripts generate and save diagnostic plots to the `plots/` directory.

> **Note:** `dataset.csv` is potentially synthetic or privacy-masked data. All 135 feature columns are anonymised; the target `COL_134` is a normalised continuous value in `[0, 1]` inferred to represent a physical or performance property (e.g., wear index, efficiency ratio). The true domain, units, and column meanings are not disclosed — a pattern common in data received under privacy constraints or from automated feature-engineering pipelines.

**Key Insights:**
- `dataset.csv` contains 135 anonymised columns (`COL_000`–`COL_134`) plus a hashed `ID`; the dataset is likely synthetic or privacy-masked, with columns consistent with elevator component sensor measurements
- Feature selection applies four complementary methods — Pearson correlation heatmap, Lasso regularisation path, Mutual Information regression, and Random Forest importances — to rank predictors of target column `COL_134`
- Regression pipeline compares multiple algorithms (Random Forest, Linear Regression, and others) using R², RMSE, and MAE metrics for best-model selection and residual analysis
- Running `feature_selection.py` and `regression_ml.py` automatically generates and saves all diagnostic plots (heatmaps, regularisation paths, model comparisons, actual-vs-predicted, residual charts) to the `plots/` directory

**Technologies:** Python, Pandas, NumPy, scikit-learn, Matplotlib, Seaborn, Feature Selection (Pearson Correlation, Lasso Regularisation, Mutual Information, Random Forest Importances), Regression (Random Forest, Linear Regression), Machine Learning, Data Visualization

---

## �🔢 DataStructures

**Overview:** Python-based data manipulation utilities demonstrating efficient file I/O operations and JSON processing with Pandas for structured data transformation and analysis.

**Key Insights:**
- Focuses on practical data manipulation techniques using Pandas DataFrames
- Demonstrates JSON file reading and structured data processing workflows
- Provides reusable patterns for data transformation operations

**Technologies:** Python, Pandas, JSON, NumPy, File I/O, Data Manipulation

---

## 📈 DeepLearning

**Overview:** Scalable microservices-based deep learning system implementing Recurrent Neural Networks with LSTM for time series forecasting. Implements complete event-driven ETL pipeline with Apache Kafka for real-time data ingestion, transformation, and model inference. Features comprehensive deployment strategies for both on-premises and AWS cloud environments with Docker containerization and Kubernetes orchestration.

**Key Insights:**
- Implements end-to-end ETL pipeline: Extract from Kafka → Transform with normalization/windowing → Load to feature store for ML inference
- Demonstrates event-driven microservices architecture with separate ETL and inference workers consuming from Kafka topics
- Uses LSTM neural networks for sequence prediction with backpropagation through time on streaming time-series data
- Provides dual deployment strategies: on-premises with local Kafka clusters and AWS deployment with MSK, ECS/EKS, and SageMaker integration
- Features real-time data processing with moving averages, rolling statistics, and temporal feature engineering for time-series forecasting

**Technologies:** **Core ML:** Python, TensorFlow, Keras, LSTM, RNN, NumPy, Pandas, scikit-learn | **Event-Driven Messaging:** Apache Kafka, Confluent Kafka (Python Client), Pika (RabbitMQ), Azure Service Bus, Paho MQTT (Eclipse Mosquitto), ZMQ, WebSockets | **Time-Series Storage:** Redis TimeSeries, TimescaleDB, PostgreSQL | **Infrastructure:** Docker, Docker Compose, Kubernetes, AWS (MSK, ECS, EKS, SageMaker), CUDA, NVIDIA GPU | **Monitoring:** Prometheus Client | **Utilities:** python-dotenv, Requests, Jupyter Notebook, Matplotlib, Seaborn | **Deployment:** Linux, Node.js (for frontend/dashboard), Uvicorn, Deep Learning, Streaming Data Processing, ETL Pipelines

---

## 🖼️ DigitRecognizer

**Overview:** Computer vision application implementing VGG-19 Convolutional Neural Network architecture for MNIST digit classification, demonstrating transfer learning and deep CNN techniques for image recognition tasks.

**Key Insights:**
- Leverages VGG-19 pre-trained architecture for digit recognition
- Demonstrates deep CNN implementation with multiple convolutional and pooling layers
- Achieves high accuracy on MNIST dataset through proper image preprocessing

**Technologies:** Python, TensorFlow, Keras, VGG-19, Convolutional Neural Networks (CNN), NumPy, Image Processing, MNIST Dataset, Deep Learning, Computer Vision

---

## ⚙️ EmbeddedSystems

**Overview:** Comprehensive embedded software development framework covering cross-compilation, multi-language programming (Assembly, C, C++, Qt), debugging strategies, IPC mechanisms, and RTOS concepts. Includes Yocto Linux integration and toolchain configurations for ARM/x86 architectures.

**Key Insights:**
- Demonstrates professional embedded development workflow with GCC/Clang compiler comparison
- Implements cross-compilation for ARM (aarch64, armhf) and x86_64 targets
- Provides debugging strategies using GDB/LLDB with VS Code integration
- Includes CMake and Make build systems with performance benchmarking scripts

**Technologies:** C, C++, Assembly (ARM, x86_64), Qt, GCC, Clang, CMake, Make, ARM, x86_64, Yocto Linux, RTOS, Cross-compilation, GDB, LLDB, IPC, Linux

---

## 🏢 ERP (Enterprise Resource Planning)

**Overview:** Odoo-based enterprise resource planning system with custom modules for video conferencing (Jitsi Meet) integration and geolocation mapping. Demonstrates ERP customization with client-server architecture using PostgreSQL and Nginx reverse proxy.

**Key Insights:**
- Implements custom Odoo modules with QWeb templating for client-side rendering
- Integrates Jitsi Meet for real-time video conferencing within ERP workflow
- Uses Nginx reverse proxy for HTTPS/SSL termination and load balancing
- Demonstrates PostgreSQL integration with RPC-based client-server communication

**Technologies:** Python, JavaScript, React, React Native, HTML, XML, Odoo, PostgreSQL, Nginx, Docker, SSL/TLS, HTTP, Jitsi Meet, Ubuntu Linux, QWeb Templates

---

## 🔄 ETL (Extract, Transform, Load)

**Overview:** Python-based data pipeline for extracting data from JSON sources, transforming business logic, and loading into PostgreSQL database. Implements Docker containerization for reproducible ETL execution with environment-based configuration.

**Key Insights:**
- Demonstrates ETL pattern with data extraction from JSON files and loading to RDBMS
- Uses psycopg2 for PostgreSQL connectivity with transaction management
- Implements schema creation with foreign key constraints for data integrity
- Features Docker Compose orchestration for database and application services

**Technologies:** Python, JSON, SQL, PostgreSQL, psycopg2, Docker, Docker Compose, python-dotenv, Linux, Data Pipeline

---

## 🤖 LLM (Large Language Models)

**Overview:** Comprehensive exploration of large language model integration frameworks including LangChain chains, LangGraph workflows, Arcee Agent for function calling, and vLLM for high-performance inference.

**Key Insights:**
- Demonstrates async/await patterns in LangChain.js for streaming LLM outputs
- Implements prompt templates and output parsers for structured LLM interactions
- Uses Arcee Agent (7B model) specifically designed for tool use and function calling
- Covers chain composition for multi-step LLM workflows with custom logic

**Technologies:** Python, JavaScript, LangChain, LangGraph, Ollama, vLLM, Arcee Agent, OpenAI API, Prompt Engineering, Async/Await, Natural Language Processing

---

## 📄 OCR (Optical Character Recognition)

**Overview:** Multi-engine OCR system combining traditional (Tesseract, EasyOCR), deep learning (CNN, Transformers), and LLM-based approaches for text extraction from PDFs, BIM images, and scanned documents. Features FastAPI REST service with OpenAI-compatible endpoints.

**Key Insights:**
- Implements three-tier OCR approach: traditional ML, deep learning, and vision-enabled LLMs
- Provides comprehensive preprocessing pipeline (de-skewing, noise reduction, binarization)
- Features batch processing capabilities with structured JSON/TXT output
- Includes web frontend for interactive OCR testing and API client examples

**Technologies:** Python, FastAPI, Tesseract, EasyOCR, OpenCV, TensorFlow, PyTorch, Ollama, PyMuPDF, pdf2image, Pillow, NumPy, Uvicorn, Machine Learning, Deep Learning, Computer Vision, REST API, CNNs, Transformers

---

## 🎯 Patterns

**Overview:** Software design pattern implementations demonstrating best practices for common programming problems. Focuses on the Visitor pattern for extending class hierarchies with new behaviors without modifying existing code.

**Key Insights:**
- Demonstrates Visitor pattern for separating algorithms from object structures
- Implements double dispatch technique through visitor acceptance methods
- Shows how to add new operations to fixed class hierarchies from external sources
- Provides reusable pattern templates for object-oriented design

**Technologies:** Design Patterns, Object-Oriented Programming, Visitor Pattern, Software Architecture, Interface Design

---

## ❓ QUESTIONS

**Overview:** Curated collection of technical interview questions and answers organized by technology domains, providing comprehensive reference material for common development scenarios and concepts.

**Key Insights:**
- Covers multiple domains: Artificial Intelligence, Golang, Python, and React
- Serves as knowledge base for technical interview preparation
- Includes practical examples and code snippets for key concepts

**Categories:** Artificial Intelligence, Go (Golang), Python, React, Technical Interviews

---

## 🏠 SmartBuildings

**Overview:** IoT-enabled building automation system using Bluetooth Mesh networking for connected lighting control. Implements gateway architecture bridging Bluetooth mesh devices to cloud services with sensor integration for time-based automation.

**Key Insights:**
- Demonstrates Bluetooth Low Energy (BLE) mesh network for scalable IoT device communication
- Implements IoT gateway pattern for edge processing and cloud connectivity
- Uses JSON-based provisioning data management for Bluetooth mesh configuration
- Features multiple communication protocols (MQTT, HTTP, gRPC) for gateway-to-cloud integration

**Technologies:** C, Python, Bluetooth Mesh, Bluetooth Low Energy (BLE), IoT, MQTT, HTTP, gRPC, TCP/IP, Raspberry Pi (ARM), nRF52 MCU, JSON, Ubuntu Linux, Edge Computing

---

## ⛓️ SupplyChain

**Overview:** Blockchain-based supply chain tracking application using Hyperledger Sawtooth for distributed ledger management. Implements custom transaction processors for product tracking with validator network consensus and cryptographic hash linking.

**Key Insights:**
- Implements blockchain consensus mechanism for distributed supply chain validation
- Uses custom transaction processors for domain-specific supply chain business logic
- Features REST API and validator network for batch submission and state queries
- Demonstrates cryptographic block linking with genesis block configuration

**Technologies:** Hyperledger Sawtooth, JavaScript, Python, Rust, Angular, React, HTML, CSS, JSON, Google Maps API, OpenStreetMap, RethinkDB, Flask, Node.js, Express, Apache, Nginx, ZMQ, MQTT, HTTP, gRPC, BSON, SSL/TLS, iptables, Docker, Docker Compose, Ubuntu Linux, Blockchain

---

## Summary

This repository demonstrates practical implementation of modern technologies with production-ready architecture patterns, documentation, and deployment configurations.
