// src/index.js

require('dotenv').config();

// Import basic modules
const { SessionMemoryStore, SESSION_CONFIG } = require("./memory");
const { fetchWeather, getWeatherDescription } = require("./tools");
const express = require('express');
const cors = require('cors');

// Try to import LangChain modules with fallback
let WeatherAgentChain, ChatOpenAI, PromptTemplate, LLMChain;
let langChainAvailable = false;

try {
    const langchainModules = require("./agents");
    WeatherAgentChain = langchainModules.WeatherAgentChain;
    langChainAvailable = process.env.OPENAI_API_KEY && process.env.OPENAI_API_KEY !== 'your_openai_api_key_here';
    console.log(langChainAvailable ? 'LangChain modules loaded successfully' : '⚠️ LangChain available but OpenAI API key not configured');
} catch (error) {
    console.log('⚠️ LangChain modules not available, using basic pattern matching');
    console.log('Install LangChain dependencies and add OpenAI API key for full features');
}

/**
 * Simple Agent implementation without LangChain
 */
class SimpleWeatherAgent {
    constructor() {
        this.memory = new SessionMemoryStore(true);
		// Enable Redis with session management
        console.log(`   Session Configuration:`);
        console.log(`   Session Duration: ${SESSION_CONFIG.SESSION_DURATION}s`);
        console.log(`   Max Conversations per Session: ${SESSION_CONFIG.MAX_CONVERSATIONS_PER_SESSION}`);
        console.log(`   Inactivity Timeout: ${SESSION_CONFIG.INACTIVITY_TIMEOUT}s`);
        console.log(`   Cleanup Interval: ${SESSION_CONFIG.CLEANUP_INTERVAL/1000}s`);
    }

    async process(userId, input) {
        const lowerInput = input.toLowerCase();
        
        try {
            // Store input in conversation history
            await this.memory.addToConversationHistory(userId, input, "");

            // Check if it's a greeting with name introduction
            if (lowerInput.includes("my name is") || lowerInput.includes("i'm") || lowerInput.includes("i am")) {
                return await this.handleNameIntroduction(input, userId);
            }
            
            // Check if it's a weather request
            if (this.isWeatherRequest(lowerInput)) {
                return await this.handleWeatherRequest(input, userId);
            }
            
            // Check if it's a general greeting
            if (this.isGreeting(lowerInput)) {
                return await this.handleGreeting(userId);
            }
            
            // Default response
            return await this.handleDefault(userId);
            
        } catch (error) {
            console.error("Error processing request:", error);
            return "I'm sorry, I encountered an error. Please try again.";
        }
    }

    isGreeting(input) {
        const greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'];
        return greetings.some(greeting => input.includes(greeting));
    }

    isWeatherRequest(input) {
        return (input.includes('weather') && input.includes('in')) || 
               input.includes('temperature') || 
               input.includes('how hot') ||
               input.includes('how cold') ||
               input.includes('forecast');
    }

    extractCityFromWeatherRequest(input) {
        const patterns = [
            /weather.*in\s+([a-zA-Z\s]+?)(\?|$|\.)/i,
            /temperature.*in\s+([a-zA-Z\s]+?)(\?|$|\.)/i,
            /in\s+([a-zA-Z\s]+?)(\?|$|\.)/i
        ];
        
        for (const pattern of patterns) {
            const match = input.match(pattern);
            if (match) {
                return match[1].trim();
            }
        }
        return null;
    }

    extractNameFromIntroduction(input) {
        const patterns = [
            /my name is\s+([a-zA-Z\s]+?)(\.|$)/i,
            /i'm\s+([a-zA-Z\s]+?)(\.|$)/i,
            /i am\s+([a-zA-Z\s]+?)(\.|$)/i
        ];
        
        for (const pattern of patterns) {
            const match = input.match(pattern);
            if (match) {
                return match[1].trim();
            }
        }
        return null;
    }

    async handleNameIntroduction(input, userId) {
        const name = this.extractNameFromIntroduction(input);
        if (name) {
            await this.memory.setMemory(`user:${userId}:name`, name);
            const response = `Nice to meet you, ${name}! I'm your weather assistant. You can ask me about the weather in any city.`;
            await this.memory.addToConversationHistory(userId, input, response);
            return response;
        }
        return "Nice to meet you! What's your name?";
    }

    async handleWeatherRequest(input, userId) {
        const city = this.extractCityFromWeatherRequest(input);
        
        if (!city) {
            return "I'd be happy to help you with the weather! Could you please tell me which city you'd like to know about?";
        }

        try {
            const weatherData = await fetchWeather(city);
            const weatherDescription = getWeatherDescription(weatherData.current.weathercode);
            
            const userName = await this.memory.getMemory(`user:${userId}:name`);
            const greeting = userName ? `${userName}, ` : "";

            const response = `${greeting}the weather in ${weatherData.location.name}, ${weatherData.location.country} is currently ${weatherDescription.toLowerCase()} with a temperature of ${weatherData.current.temperature}${weatherData.units.temperature}. Wind speed is ${weatherData.current.windspeed} ${weatherData.units.windspeed}.`;
            
            await this.memory.addToConversationHistory(userId, input, response);
            return response;

        } catch (error) {
            console.error("Weather request error:", error);
            if (error.message.includes("not found")) {
                return "I couldn't find that city. Please check the spelling and try again.";
            }
            return "I'm sorry, I couldn't fetch the weather data right now. Please try again later.";
        }
    }

    async handleGreeting(userId) {
        const userName = await this.memory.getMemory(`user:${userId}:name`);
        
        if (userName) {
            return `Hello again, ${userName}! How can I help you today? You can ask me about the weather in any city.`;
        } else {
            return "Hello! I'm your weather assistant. What's your name? You can also ask me about the weather in any city.";
        }
    }

    async handleDefault(userId) {
        const userName = await this.memory.getMemory(`user:${userId}:name`);
        const greeting = userName ? `${userName}, ` : "";

        return `${greeting}I'm a weather assistant. I can help you with:
- Getting weather information for any city (just ask "What's the weather in [city]?")
- Remembering your name for personalized responses

You can also greet me or introduce yourself. How can I help you today?`;
    }

    async getConversationHistory(userId) {
        return await this.memory.getConversationHistory(userId);
    }

    async disconnect() {
        await this.memory.disconnect();
    }
}

/**
 * Enhanced agent that uses LangChain when available
 */
class EnhancedWeatherAgent {
    constructor() {
        this.simpleAgent = new SimpleWeatherAgent();
        this.langchainAgent = null;
        
        if (langChainAvailable && WeatherAgentChain) {
            try {
                this.langchainAgent = new WeatherAgentChain();
                console.log(' Using LangChain-powered agent');
            } catch (error) {
                console.log('⚠️ LangChain agent initialization failed, using simple agent');
            }
        }
    }

    async process(userId, input) {
        if (this.langchainAgent) {
            try {
                const result = await this.langchainAgent.call({
                    input: input,
                    userId: userId
                });
                return result.output;
            } catch (error) {
                console.log('LangChain processing failed, falling back to simple agent:', error.message);
            }
        }
        
        // Fallback to simple agent
        return await this.simpleAgent.process(userId, input);
    }

    async getConversationHistory(userId) {
        return await this.simpleAgent.getConversationHistory(userId);
    }

    async disconnect() {
        await this.simpleAgent.disconnect();
    }
}

// Express server setup
const app = express();
app.use(cors());
app.use(express.json());

const agent = new EnhancedWeatherAgent();

// API endpoints
app.post('/chat', async (req, res) => {
    try {
        const { message, userId = 'default' } = req.body;
        
        if (!message) {
            return res.status(400).json({ error: 'Message is required' });
        }

        const response = await agent.process(userId, message);
        
        res.json({
            response,
            userId,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error('Chat API error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.get('/history/:userId', async (req, res) => {
    try {
        const { userId } = req.params;
        const history = await agent.getConversationHistory(userId);
        res.json({ history, userId });
    } catch (error) {
        console.error('History API error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.get('/health', (req, res) => {
    res.json({ 
        status: 'healthy', 
        timestamp: new Date().toISOString(),
        features: {
            langchain: langChainAvailable,
            redis: agent.simpleAgent.memory.redisConnected,
            weatherAPI: true,
            sessionManagement: true
        }
    });
});

// Session Management API Endpoints
app.get('/sessions/:userId', async (req, res) => {
    try {
        const { userId } = req.params;
        const stats = await agent.simpleAgent.memory.getSessionStats(userId);
        res.json({
            success: true,
            userId,
            ...stats
        });
    } catch (error) {
        console.error('Session stats error:', error);
        res.status(500).json({ 
            success: false, 
            error: 'Failed to get session stats' 
        });
    }
});

app.post('/sessions/:userId/end', async (req, res) => {
    try {
        const { userId } = req.params;
        const { reason } = req.body;
        
        await agent.simpleAgent.memory.endUserSession(userId, reason || 'manual');
        
        res.json({
            success: true,
            message: `All sessions ended for user ${userId}`,
            reason: reason || 'manual'
        });
    } catch (error) {
        console.error('End session error:', error);
        res.status(500).json({ 
            success: false, 
            error: 'Failed to end session' 
        });
    }
});

app.get('/system/memory', async (req, res) => {
    try {
        const memoryStats = await agent.simpleAgent.memory.getMemoryStats();
        res.json({
            success: true,
            ...memoryStats
        });
    } catch (error) {
        console.error('Memory stats error:', error);
        res.status(500).json({ 
            success: false, 
            error: 'Failed to get memory stats' 
        });
    }
});

app.get('/system/status', async (req, res) => {
    try {
        const memoryStats = await agent.simpleAgent.memory.getMemoryStats();
        
        res.json({
            success: true,
            status: 'operational',
            timestamp: new Date().toISOString(),
            system: {
                nodeVersion: process.version,
                uptime: process.uptime(),
                memoryUsage: process.memoryUsage()
            },
            features: {
                langchain: langChainAvailable,
                redis: agent.simpleAgent.memory.redisConnected,
                weatherAPI: true,
                sessionManagement: true
            },
            sessionConfig: SESSION_CONFIG,
            memoryStats
        });
    } catch (error) {
        console.error('System status error:', error);
        res.status(500).json({ 
            success: false, 
            error: 'Failed to get system status' 
        });
    }
});

app.get('/sessions/:userId/history/:sessionId?', async (req, res) => {
    try {
        const { userId, sessionId } = req.params;
        const { limit = 10 } = req.query;
        
        let history;
        if (sessionId) {
            history = await agent.simpleAgent.memory.getSessionConversationHistory(sessionId, parseInt(limit));
        } else {
            history = await agent.simpleAgent.memory.getConversationHistory(userId, parseInt(limit));
        }
        
        res.json({
            success: true,
            userId,
            sessionId: sessionId || 'current',
            history,
            count: history.length
        });
    } catch (error) {
        console.error('Get session history error:', error);
        res.status(500).json({ 
            success: false, 
            error: 'Failed to get session history' 
        });
    }
});

/**
 * Demo function
 */
async function runDemo() {
    console.log(" Weather Agent Demo\n");
    
    const userId = "demo_user";
    const testMessages = [
        "Hello",
        "My name is Alice",
        "What's the weather in London?",
        "Hi there",
        "How about Tokyo weather?",
        "What can you help me with?"
    ];

    for (const message of testMessages) {
        try {
            console.log(`User: ${message}`);
            const response = await agent.process(userId, message);
            console.log(`Agent: ${response}\n`);
            
            await new Promise(resolve => setTimeout(resolve, 1000));
        } catch (error) {
            console.log(`❌ Error: ${error.message}\n`);
        }
    }

    console.log("Conversation History:");
    try {
        const history = await agent.getConversationHistory(userId);
        console.log(JSON.stringify(history, null, 2));
    } catch (error) {
        console.log("Could not retrieve conversation history:", error.message);
    }
}

// Main application entry point (IIFE)
(async () => {
    try {
        console.log("Starting Weather Agent...\n");
        
        // Test weather API first
        console.log("🌤️  Testing weather API...");
        try {
            const testWeather = await fetchWeather('London');
            console.log(`Weather API working: ${testWeather.location.name}, ${testWeather.current.temperature}°C\n`);
        } catch (error) {
            console.log(`❌ Weather API test failed: ${error.message}\n`);
        }
        
        // Run demo
        await runDemo();

        // Start the Express server
        const PORT = process.env.PORT || 3000;
        app.listen(PORT, () => {
            console.log(`\n Server running on http://localhost:${PORT}`);
            console.log(` Chat API: POST http://localhost:${PORT}/chat`);
            console.log(` History API: GET http://localhost:${PORT}/history/:userId`);
            console.log(` Health check: GET http://localhost:${PORT}/health`);
            
            console.log("\n Example API calls:");
            console.log(`curl -X POST http://localhost:${PORT}/chat -H "Content-Type: application/json" -d '{"message":"Hello, my name is John","userId":"test"}'`);
            console.log(`curl -X POST http://localhost:${PORT}/chat -H "Content-Type: application/json" -d '{"message":"What's the weather in Paris?","userId":"test"}'`);
            console.log(`curl http://localhost:${PORT}/health`);
            
            console.log("\n Weather Agent is ready!");
            
            if (!langChainAvailable) {
                console.log("\n To enable advanced LangChain features:");
                console.log("   1. Add your OpenAI API key to the .env file");
                console.log("   2. Restart the application");
            }
        });

    } catch (error) {
        console.error("❌ Error starting application:", error.message);
        process.exit(1);
    }
})();

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('\nShutting down gracefully...');
    await agent.disconnect();
    process.exit(0);
});

process.on('SIGTERM', async () => {
    console.log('\nShutting down gracefully...');
    await agent.disconnect();
    process.exit(0);
});