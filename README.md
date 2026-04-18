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
├── 🔢 DataStructures/      # Data Manipulation & Processing
├── 🧠 DeepLearning/        # Neural Networks & Time Series
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
- Solved critical issue with DoubleType label column requirement for LogisticRegression
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

## 🔢 DataStructures

**Overview:** Python-based data manipulation utilities demonstrating efficient file I/O operations and JSON processing with Pandas for structured data transformation and analysis.

**Key Insights:**
- Focuses on practical data manipulation techniques using Pandas DataFrames
- Demonstrates JSON file reading and structured data processing workflows
- Provides reusable patterns for data transformation operations

**Technologies:** Python, Pandas, JSON, NumPy, File I/O, Data Manipulation

---

## 🧠 DeepLearning

**Overview:** Microservices-based deep learning system implementing LSTM Recurrent Neural Networks for time series forecasting. Features event-driven messaging architecture with multiple communication protocols and time-series database integration.

**Key Insights:**
- Implements LSTM for sequence prediction with backpropagation through time
- Demonstrates normalization and windowing techniques for time series data preparation
- Uses microservices architecture with MQTT, ZMQ, and WebSockets for inter-service communication
- Integrates Redis TimeSeries and TimescaleDB for efficient time-series data storage

**Technologies:** Python, JavaScript, TensorFlow, Keras, LSTM, RNN, Redis, RedisTimeSeries, TimescaleDB, ZMQ, MQTT, WebSockets, Node.js, Mosquitto, CUDA, NVIDIA GPU, Docker, Linux, Deep Learning, Time Series Forecasting

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

This repository demonstrates practical implementation of modern technologies with production-ready architecture patterns, comprehensive documentation, and deployment configurations.
