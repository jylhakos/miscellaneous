#  Questions-and-Answers (Q&A)

Question Answering (QA) is a Natural Language Processing (NLP) task in which a model produces an answer to a question by using the information provided in a given context. Large Language Models (LLMs) such as BERT and GPT have improved the accuracy and practicality of question answering systems. These models are superior at understanding context, retrieving relevant information, and providing precise answers.

## How to build a pipeline for Questions and Answers with an LLM model?

1. Define the use case and requirements

What types of questions will be asked? (e.g., domain-specific)

What sources will the answers be based on? (e.g., documents or web)

2. Data preparation

**Source**

Collect relevant documents or datasets (FAQs, web pages)

**Preprocessing**

Clean and preprocess text (tokenization, removal of irrelevant information)

**Indexing (optional)**

For retrieval-augmented pipelines, create an index of your data using tools like Elasticsearch.

3. Pipeline

There are two main approaches

3.1  Retrieval Augmented Generation (RAG) pipeline

**Query processing**

Preprocess and possibly rephrase the question.

**Document retrieval**

Use a retriever (BM25, Dense embedding, etc.) to fetch relevant context passages.

**Context construction**

Combine retrieved texts into a prompt.

**Answer generation**

Pass the prompt to the LLM (e.g., OpenAI GPT, Llama, etc.) to generate an answer.

**Post-processing**

Clean and format the answer as needed.

3.2 Q&A with LLM

If using an LLM or your knowledge base is small, you can directly prompt the LLM with the question and the context.

4. Model selection

Choose an LLM that fits your needs (e.g., Meta Llama 4, Mistral or open-source models).

For domain-specific tasks, consider fine-tuning, using adapters or LoRA.

5. Implementation

Frameworks

Use frameworks like LangChain or LlamaIndex for prototyping.

API Integration

Use the model’s API (OpenAI, Azure, HuggingFace, etc.).

Prompt Engineering

Design prompts that elicit accurate answers, possibly including context and instructions.

6. Evaluation

Use benchmarks like SQuAD, Natural Questions, or your own test set.

Evaluate for accuracy and relevance.

7. Deployment

Use an API (FastAPI, Flask, etc.)

Deploy to a cloud service or on-premises.

### LangChain.js, Node.js, Ollama, Llama 4 (Scout)

## Prerequisites

Before setting up the Q&A chat system, ensure you have the following installed:

- **Docker**: For running Ollama and Open WebUI containers
- **Node.js** (v16 or higher): For the Express.js API server
- **npm**: For managing JavaScript dependencies
- **Nginx**: For reverse proxy and HTTPS termination
- **curl**: For testing API endpoints

## Ollama server setup with Docker

### 1. Install and start Ollama server

```bash
# Pull and run Ollama server in Docker
docker run -d \
  --name ollama-server \
  -p 11434:11434 \
  -v ollama:/root/.ollama \
  --restart unless-stopped \
  ollama/ollama:latest
```

### 2. Pull Llama 4 (Scout) model

```bash
# Pull the Llama 4 Scout model (this may take several minutes)
docker exec ollama-server ollama pull llama4:scout

# Alternative: Pull Llama 3.1 if Scout is not available
docker exec ollama-server ollama pull llama3.1
```

### 3. Verify Ollama

```bash
# Test Ollama API
curl http://localhost:11434

# List available models
docker exec ollama-server ollama list
```

## Node.js dependencies

### 1. Install dependencies

```bash
# Install Node.js dependencies
npm install

# Install development dependencies (optional)
npm install --save-dev nodemon
```

### 2. Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` file with your settings:

```env
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama4:scout

# Server Configuration
PORT=3000
NODE_ENV=development

# Memory Configuration
MAX_MEMORY_HISTORY=20
SESSION_TIMEOUT=3600000

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3001,https://localhost:8080
```

## Open WebUI setup

### 1. Run Open WebUI in Docker

```bash
# Start Open WebUI container
docker run -d \
  --name open-webui \
  -p 8080:8080 \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --restart unless-stopped \
  ghcr.io/open-webui/open-webui:main
```

### 2. Access Open WebUI

Open your browser and navigate to: `http://localhost:8080`

## Nginx Reverse Proxy configuration

### 1. SSL certificate generation

Generate self-signed certificates for HTTPS:

```bash
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/key.pem \
  -out /etc/nginx/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

### 2. Configure Nginx

Copy the nginx configuration:

```bash
sudo cp nginx.conf /etc/nginx/sites-available/qa-chat
sudo ln -sf /etc/nginx/sites-available/qa-chat /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

## iptables configuration (Debian/Ubuntu)

Configure firewall rules to allow necessary connections:

```bash
# Allow HTTP and HTTPS
sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow Node.js service
sudo iptables -A INPUT -p tcp --dport 3000 -j ACCEPT

# Allow Ollama
sudo iptables -A INPUT -p tcp --dport 11434 -j ACCEPT

# Allow Open WebUI
sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT

# Save rules
sudo iptables-save > /etc/iptables/rules.v4
```

## Starting the services

### Option 1: Automated startup

Use the provided startup script to start all services:

```bash
# Start everything automatically
./startup.sh
```

### Option 2: Manual startup

Start services individually:

```bash
# 1. Start Docker services (Ollama + Open WebUI)
./start-docker.sh

# 2. Start Node.js QA service
./start-nodejs.sh

# 3. Configure Nginx (if not done automatically)
sudo systemctl restart nginx
```

## API usage

### Using cURL

```bash
# Health check
curl https://localhost/health

# Ask a question (GET method)
curl -X GET "https://localhost/api/ask?question=What is artificial intelligence?"

# Ask a question with session (POST method)
curl -X POST https://localhost/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain machine learning", "sessionId": "user123"}'

# Create a new session
curl -X POST https://localhost/api/session

# Get session history
curl -X GET https://localhost/api/session/user123/history

# Clear session
curl -X DELETE https://localhost/api/session/user123
```

### Using Open WebUI

1. Navigate to `http://localhost:8080`
2. Create an account or sign in
3. Configure the Ollama connection if needed
4. Start chatting with the Llama 4 (Scout) model

## Conversation memory

The Q&A system implements conversational memory with the following features:

- **Session-based memory**: Each user session maintains its own conversation history
- **Limited history**: Configurable maximum number of conversation turns (default: 20)
- **Automatic cleanup**: Sessions expire after inactivity (default: 1 hour)
- **Memory persistence**: Conversations are stored in memory during the session
- **Context awareness**: The AI remembers previous interactions within the same session

### Memory configuration

Configure memory settings in `.env`:

```env
MAX_MEMORY_HISTORY=20      # Maximum conversation turns to remember
SESSION_TIMEOUT=3600000    # Session timeout in milliseconds (1 hour)
```

## Services

```
Client (cURL/Open WebUI) 
    ↓ HTTPS
Nginx Reverse Proxy 
    ↓ HTTP
Node.js Express Server (Port 3000)
    ↓ HTTP API
Ollama Server (Port 11434)
    ↓ Model Inference
Llama 4 (Scout) Model
```

## Message Format for Open WebUI

When using Open WebUI, messages follow this format:

```json
{
  "message": "Your question here",
  "model": "llama4:scout",
  "stream": true
}
```

## Stopping Services

### Stop All Services

```bash
./shutdown.sh
```

### Stop Individual Services

```bash
# Stop Node.js service only
./stop-nodejs.sh

# Stop Docker services only
./stop-docker.sh
```

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   ```bash
   # Check if Ollama is running
   docker ps | grep ollama-server
   
   # Check Ollama logs
   docker logs ollama-server
   ```

2. **Model Not Found**
   ```bash
   # List available models
   docker exec ollama-server ollama list
   
   # Pull missing model
   docker exec ollama-server ollama pull llama4:scout
   ```

3. **Port Already in Use**
   ```bash
   # Check what's using the port
   sudo netstat -tlnp | grep :3000
   
   # Kill the process if needed
   sudo kill -9 <PID>
   ```

4. **Nginx SSL Certificate Issues**
   ```bash
   # Regenerate certificates
   sudo rm /etc/nginx/ssl/*
   ./startup.sh  # Will regenerate certificates
   ```

### Logs and Debugging

```bash
# Node.js service logs
npm run dev  # Shows console output

# Docker container logs
docker logs ollama-server
docker logs open-webui

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## File Structure

```
qa/
├── src/
│   ├── index.js          # Express.js server
│   └── qa.js             # LangChain.js QA logic
├── nginx.conf            # Nginx configuration
├── .env                  # Environment variables
├── .env.example          # Environment template
├── .gitignore           # Git ignore rules
├── package.json         # Node.js dependencies
├── startup.sh           # Complete system startup
├── shutdown.sh          # Complete system shutdown
├── start-docker.sh      # Docker services startup
├── stop-docker.sh       # Docker services shutdown
├── start-nodejs.sh      # Node.js service startup
├── stop-nodejs.sh       # Node.js service shutdown
└── README.md            # This file
```

## Development

### Running in Development Mode

```bash
# Set development environment
export NODE_ENV=development

# Start with auto-reload
npm run dev
```

### Testing

```bash
# Test basic functionality
curl -X GET "http://localhost:3000/health"

# Test QA endpoint
curl -X GET "http://localhost:3000/api/ask?question=Hello"

# Test with session
curl -X POST http://localhost:3000/api/session
curl -X POST http://localhost:3000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is 2+2?", "sessionId": "test123"}'
```

## Security Considerations

- Use proper SSL certificates in production
- Configure proper CORS origins
- Implement rate limiting for production use
- Secure your Ollama instance
- Use environment variables for sensitive configuration
- Keep Docker containers updated

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

**References**

- [LangChain.js Documentation](https://js.langchain.com/)
- [Ollama Documentation](https://ollama.com/)
- [Open WebUI Documentation](https://docs.openwebui.com/)
- [Express.js Documentation](https://expressjs.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [How-to guides](https://python.langchain.com/docs/how_to/)
- [Question answering](https://huggingface.co/learn/llm-course/en/chapter7/7)

