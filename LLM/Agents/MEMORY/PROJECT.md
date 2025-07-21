# LangChain.js Weather Agent

## **Features**

### 1. **LangChain.js**
-  Custom `WeatherAgentChain` extending `BaseChain`
-  `ChatOpenAI` integration for intelligent responses  
-  `PromptTemplate` for structured query processing
-  `LLMChain` for chaining operations
-  Graceful fallback to pattern matching without OpenAI API key

### 2. **Weather API**
-  **Open-Meteo API** integration (free, no API key required)
-  **Geocoding support** to convert city names to coordinates
-  Real-time weather data fetching
-  Weather condition descriptions from weather codes
-  Error handling for invalid cities

### 3. **Memory**
-  **Redis integration** with automatic fallback to in-memory storage
-  **User name storage** for personalized responses
-  **Conversation history** with configurable limits
-  **TTL (Time To Live)** for memory management
-  Memory size limits to prevent overflow

### 4. **Intelligent query processing**
-  **Greeting detection** and name extraction
-  **Weather request classification** 
-  **City name extraction** from natural language
-  **Context-aware responses** using stored user data
-  **Default handling** for unknown requests

### 5. **RESTful API**
-  **Express.js server** with CORS support
-  **POST /chat** endpoint for conversations
-  **GET /history/:userId** for conversation history
-  **GET /health** for system status
-  **JSON response format** with timestamps

### 6. **Error handling**
-  **Graceful fallbacks** at every level
-  **Redis connection failure handling**
-  **OpenAI API error handling**
-  **Weather API timeout handling**
-  **Input validation and sanitization**

## 📁 **Structure**

```
LangChain Weather Agent
├──   package.json          # Dependencies & scripts
├──   .env                  # Environment configuration
├──   README.md             # Comprehensive documentation
├──   QUICKSTART.md         # Quick setup guide
├──   open-webui-examples.md # Open WebUI integration guide
├──   demo.js               # Offline demo script
├──   simple-agent.js       # Simplified version for testing
└── 📁 src/
    ├──   index.js          # Main application entry point
    ├──   agents.js         # LangChain agents & custom chains
    ├──   memory.js         # Redis & in-memory storage
    └──   tools.js          # Weather API & geocoding tools
```

##  **Dependencies**

```json
{
  "langchain": "^0.1.0",
  "@langchain/core": "^0.1.0", 
  "@langchain/openai": "^0.0.14",
  "axios": "^1.6.0",
  "dotenv": "^16.3.0",
  "redis": "^4.6.0",
  "express": "^4.18.0",
  "cors": "^2.8.5"
}
```

##  **Testing & validation**

###  **Tests**
1. **Basic functionality test** - Memory store working
2. **Weather API test** - Open-Meteo API integration working  
3. **Offline demo** - Pattern matching and conversation flow working
4. **Dependencies installation** - All packages installed successfully
5. **Error handling** - Graceful fallbacks functioning

### **Interactions**

```
👤 User: Hello, my name is Alice
🤖 Agent: Nice to meet you, Alice! I'm your weather assistant. 

👤 User: What's the weather in London?
🤖 Agent: Alice, the weather in London, UK is currently partly cloudy with a temperature of 18°C.

👤 User: Hi there!
🤖 Agent: Hello again, Alice! How can I help you today?
```

## **Running the application**

### **Quick start (Basic Mode)**
```bash
node demo.js           # Offline demo with mock data
node simple-agent.js   # Full agent without LangChain
node src/index.js      # Full application with LangChain fallback
```

### **Advanced (With OpenAI)**
1. Add OpenAI API key to `.env`
2. Run: `node src/index.js`
3. Get intelligent LangChain-powered responses

### **API usage**
```bash
# Start server
node src/index.js

# Test API
curl -X POST http://localhost:3000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What'\''s the weather in Paris?","userId":"test"}'
```

##  **Open WebUI**

-  **System Prompts** provided for Open WebUI setup
-  **API Endpoints** compatible with Open WebUI

## **Documentation**

- **README.md**: Complete setup and usage guide
- **QUICKSTART.md**: Quick start instructions
- **open-webui-examples.md**: Open WebUI integration guide
- **Inline comments**: Comprehensive code documentation
- **Example scripts**: Multiple demo and testing scripts
