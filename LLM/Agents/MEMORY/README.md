# An Agent with LangChain.js and Memory

An weather assistant built with LangChain.js that can process user queries, fetch weather information, and remember user interactions using Redis cache.

An Agent may store and maintain information internally for multi-step interaction with the world.

## Features

-  **AI query classification** using LangChain.js and OpenAI
- 🌤️ **Real-time weather data** from Open-Meteo API (free, no API key required)
-  **Session-based memory management** with automatic cleanup and Redis optimization
-  **Conversation history** tracking within user sessions
-  **RESTful API** for easy integration with session management endpoints
-  **Geocoding support** for city name to coordinates conversion
-  **Graceful error handling** and fallback mechanisms
-  **Configurable session limits** to control memory usage
-  **Automatic cleanup** of expired sessions and conversations

## System Management

The project includes management scripts for operation:

### Process Manager (Recommended)

Use the unified process manager for complete system control:

```bash
# Show help and available commands
./process-manager.sh help

# Start the complete system (Redis + Node.js)
./process-manager.sh start

# Check system status
./process-manager.sh status

# Live monitoring (refreshes every 5 seconds)
./process-manager.sh monitor

# Stop the complete system
./process-manager.sh stop

# Restart everything
./process-manager.sh restart

# View application logs
./process-manager.sh logs
```

### NPM scripts

The npm commands for System Management:

```bash
# Complete system management
npm run system:start      # Start everything
npm run system:stop       # Stop everything
npm run system:restart    # Restart everything
npm run system:status     # System status
npm run system:monitor    # Live monitoring
npm run system:logs       # View logs

# Individual component management
npm run redis:start       # Start Redis only
npm run redis:stop        # Stop Redis only
npm run redis:status      # Redis status
npm run redis:logs        # Redis logs

# Application management
npm start                 # Start Node.js app only
npm run dev               # Development mode with nodemon
npm run shutdown          # Graceful shutdown
npm run cleanup           # Complete cleanup
npm run kill-all          # Force stop everything
```

### Manual scripts

Individual scripts for specific tasks:

```bash
# Redis management
./redis-manager.sh start|stop|restart|status|logs

# Graceful shutdown
./shutdown.sh

# Complete cleanup (with data preservation options)
./cleanup.sh              # Interactive cleanup
./cleanup.sh --force      # Force cleanup everything
./cleanup.sh --preserve   # Cleanup but preserve data
```

## Quick Start

### Using Process Manager

```bash
# Make scripts executable (first time only)
chmod +x *.sh

# Start everything
./process-manager.sh start

# Check if running
./process-manager.sh status

# Test the API
curl http://localhost:3000/health

# When done
./process-manager.sh stop
```

### Using NPM scripts

```bash
# Start the complete system
npm run system:start

# Monitor the system
npm run system:monitor

# Stop when done
npm run system:stop
```

## Installation

- **Node.js** (version 16 or higher)
- **npm** or **yarn** package manager
- **Redis** (optional - will fallback to in-memory storage)
- **OpenAI API Key** (for advanced LangChain features)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd langchain-weather-agent
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file and add your OpenAI API key
   ```

4. **Install and start Redis** (recommended for persistence)
   ```bash
   # Option 1: Using Docker (Recommended)
   docker run -d --name langchain-redis -p 6379:6379 redis:7-alpine redis-server --appendonly yes
   
   # Option 2: Using the provided manager script
   ./redis-manager.sh start
   
   # Option 3: Native installation
   # Ubuntu/Debian
   sudo apt update
   sudo apt install redis-server
   sudo systemctl start redis-server

   # macOS with Homebrew
   brew install redis
   brew services start redis
   ```

## Configuration

Edit the `.env` file with your configuration:

```env
# Required for advanced LangChain features
OPENAI_API_KEY=your_openai_api_key_here

# Redis Configuration (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# Server Configuration
PORT=3000
```

## Redis Docker management

### Quick Redis setup
```bash
# Start Redis with Docker
./redis-manager.sh start

# Check status
./redis-manager.sh status

# Test functionality
./redis-manager.sh test

# View logs
./redis-manager.sh logs

# Stop Redis
./redis-manager.sh stop
```

## Usage

### Running the application

```bash
# Development mode with auto-reload
npm run dev

# Production mode
npm start
```

### API Endpoints

#### Chat Endpoint
```bash
curl -X POST http://localhost:3000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What'\''s the weather in London?",
    "userId": "user123"
  }'
```

#### Conversation History
```bash
curl http://localhost:3000/history/user123
```

#### Health Check
```bash
curl http://localhost:3000/health
```

#### System Information
```bash
# Get memory system status
curl http://localhost:3000/system/memory

# Get application status
curl http://localhost:3000/system/status
```

#### Session Management
```bash
# Get user's session information
curl http://localhost:3000/sessions/user123

# Get session conversation history
curl http://localhost:3000/sessions/user123/history

# End user's current session
curl -X POST http://localhost:3000/sessions/user123/end \
  -H "Content-Type: application/json" \
  -d '{"reason": "user_requested"}'
```

## Session Management

The system implements intelligent session-based memory management:

- **Sessions**: Time-bounded conversation periods (default: 30 minutes)
- **Conversation Limits**: Maximum conversations per session (default: 20)
- **Auto-cleanup**: Expired and inactive sessions are automatically cleaned up
- **Memory Efficiency**: Redis memory usage is bounded and predictable

### Session Configuration
Configure session behavior via environment variables:
```bash
SESSION_DURATION=1800          # 30 minutes
MAX_CONVERSATIONS_PER_SESSION=20
INACTIVITY_TIMEOUT=900         # 15 minutes
CLEANUP_INTERVAL=300000        # 5 minutes
```

### Testing Session Management
```bash
# Run session management demo
npm run session-demo

# Monitor system with session stats
npm run system:monitor
```

For detailed session management documentation, see [SESSION_MANAGEMENT.md](SESSION_MANAGEMENT.md).

### Interactions

1. **Greeting and Name Storage**
   ```
   User: Hello, my name is Alice
   Agent: Nice to meet you, Alice! I'm your weather assistant. You can ask me about the weather in any city.
   ```

2. **Weather Queries**
   ```
   User: What's the weather in Tokyo?
   Agent: Alice, the weather in Tokyo, Japan is currently clear sky with a temperature of 22°C. Wind speed is 5 km/h.
   ```

3. **Default Responses**
   ```
   User: What can you do?
   Agent: Alice, I'm a weather assistant. I can help you with:
   - Getting weather information for any city
   - Remembering your name for personalized responses
   ```

## LangChain.js

This project demonstrates advanced LangChain.js concepts:

### Chain Implementation

```javascript
class WeatherAgentChain extends BaseChain {
    // Custom chain that extends LangChain's BaseChain
    // Handles input classification, weather requests, and memory
}
```

### LangChain Components

- **BaseChain**: Custom chain implementation
- **ChatOpenAI**: OpenAI integration for intelligent responses
- **PromptTemplate**: Structured prompts for classification and extraction
- **LLMChain**: Chaining LLM operations
- **CallbackManager**: Managing chain execution callbacks

### Chain Flow

1. **Input Classification** → Determines if input is greeting, weather request, or other
2. **Information Extraction** → Extracts names from greetings or cities from weather requests
3. **Action Execution** → Fetches weather data or processes greetings
4. **Response Generation** → Creates personalized responses using memory

## Open WebUI

To test the agent with Open WebUI, use these example prompts:

```
System Prompt:
You are interacting with a weather assistant that can remember your name and provide weather information for any city. The assistant uses LangChain.js for intelligent query processing.

Example conversations:
- "Hello, my name is John" → Remembers your name
- "What's the weather in Paris?" → Fetches real weather data  
- "Hi there!" → Uses remembered name if available
```

## Weather API

The application uses the free Open-Meteo API:

- **Geocoding**: `https://geocoding-api.open-meteo.com/v1/search`
- **Weather**: `https://api.open-meteo.com/v1/forecast`

No API key required for weather data!

## Memory System

### Redis
- Stores user names and conversation history
- Configurable TTL (Time To Live)
- Automatic fallback to in-memory storage

### Memory Limits
- Max 100 recent interactions per user
- 2-hour TTL for conversation history
- 1-hour TTL for user preferences

## Error Handling

The application includes comprehensive error handling:

- **Network failures**: Graceful API error responses
- **Redis connection issues**: Automatic fallback to in-memory storage
- **Invalid city names**: User-friendly error messages
- **Missing OpenAI key**: Falls back to basic pattern matching

## Development

### Project

```
src/
├── index.js      # Main application entry point
├── agents.js     # LangChain agents and custom chains
├── memory.js     # Redis memory management
└── tools.js      # Weather API and geocoding tools
```

### Tests

```bash
# Test weather API
node -e "
const { fetchWeather } = require('./src/tools');
fetchWeather('London').then(console.log).catch(console.error);
"

# Test Redis connection
node -e "
const { MemoryStore } = require('./src/memory');
const store = new MemoryStore();
store.initialize().then(() => console.log('Redis connected')).catch(console.error);
"
```
## Troubleshooting

### Issues

1. **"Redis Client Error"**
   - Ensure Redis is running: `redis-server`
   - Check connection settings in `.env`
   - Application will use in-memory fallback

2. **"OpenAI API Error"**
   - Verify API key in `.env` file
   - Check OpenAI account credits
   - Application will use basic pattern matching

3. **"City not found"**
   - Check city name spelling
   - Try alternate names (e.g., "New York" vs "NYC")

### Debug mode

Set environment variable for detailed logging:
```bash
DEBUG=langchain* npm start
```
### References

Memory for agents

https://blog.langchain.com/memory-for-agents/

## License

MIT License - see LICENSE file for details.
