# Quick Start

## Prerequisites Check

1. **Node.js installed**:  (version 22.14.0 detected)
2. **Dependencies installed**:  (npm install completed)

## Basic usage (Without OpenAI)

Run the application without LangChain (uses pattern matching):

```bash
node src/index.js
```

This will:
- Start a demo conversation
- Launch an API server on port 3000
- Work without Redis or OpenAI API key

## Advanced usage (With LangChain)

1. **Get an OpenAI API key** from https://platform.openai.com/
2. **Update the .env file**:
   ```
   OPENAI_API_KEY=your_actual_openai_api_key_here
   ```
3. **Run the application**:
   ```bash
   node src/index.js
   ```

## Redis setup (Optional)

To enable persistent memory:

1. **Install Redis**:
   ```bash
   # Ubuntu/Debian
   sudo apt install redis-server
   sudo systemctl start redis-server
   
   # macOS
   brew install redis
   brew services start redis
   ```

2. **Update memory.js** to enable Redis:
   ```javascript
   this.memory = new MemoryStore(true); // Enable Redis
   ```

## API testing

Once the server is running, test with curl:

```bash
# Chat endpoint
curl -X POST http://localhost:3000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello, my name is John","userId":"test"}'

curl -X POST http://localhost:3000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What'\''s the weather in London?","userId":"test"}'

# History endpoint
curl http://localhost:3000/history/test

# Health check
curl http://localhost:3000/health
```

## Features

 **Weather API**: Uses free Open-Meteo API (no key required)
 **Memory**: In-memory storage with fallback
 **Pattern matching**: Works without OpenAI
 **Express API**: RESTful endpoints
 **Conversation history**: Stores recent interactions
 **Graceful fallbacks**: Handles errors gracefully

## Features available with OpenAI key

 ** LangChain features**:
- Intelligent query classification
- Context-aware conversations

## Troubleshooting

1. **"LangChain modules not available"**: This is normal without OpenAI key
2. **Weather API slow/timeout**: Open-Meteo can be slow, but it's free
3. **Redis connection failed**: App falls back to in-memory storage
4. **Port 3000 in use**: Change PORT in .env file

## Files

```
src/
├── index.js      # Main application ( Working)
├── agents.js     # LangChain agents ( Working with OpenAI key)
├── memory.js     # Memory management ( Working)
├── tools.js      # Weather API tools ( Working)

# Configuration
├── .env          # Environment variables
├── package.json  # Dependencies
└── README.md     # Documentation
```