// simple-agent.js - Simplified version without LangChain for testing

const { MemoryStore } = require('./src/memory');
const { fetchWeather, getWeatherDescription } = require('./src/tools');
const express = require('express');
const cors = require('cors');
require('dotenv').config();

class SimpleWeatherAgent {
    constructor() {
        this.memory = new MemoryStore(false); // Disable Redis for now
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
        // Simple regex to extract city name after "in" keyword
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
            
            // Get user name for personalized response
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

// Express server
const app = express();
app.use(cors());
app.use(express.json());

const agent = new SimpleWeatherAgent();

// API endpoint for chat interaction
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

// API endpoint for conversation history
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

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Demo function
async function runDemo() {
    console.log("🚀 Simple Weather Agent Demo\n");
    
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
            console.log(` User: ${message}`);
            const response = await agent.process(userId, message);
            console.log(` Agent: ${response}\n`);
            
            // Small delay between messages
            await new Promise(resolve => setTimeout(resolve, 500));
        } catch (error) {
            console.log(`❌ Error: ${error.message}\n`);
        }
    }

    // Show conversation history
    try {
        console.log(" Conversation History:");
        const history = await agent.getConversationHistory(userId);
        console.log(JSON.stringify(history, null, 2));
    } catch (error) {
        console.log("Could not retrieve conversation history:", error.message);
    }
}

// Start the application
(async () => {
    try {
        console.log(" Starting Simple Weather Agent...\n");
        
        // Run demo
        await runDemo();

        // Start the Express server
        const PORT = process.env.PORT || 3000;
        app.listen(PORT, () => {
            console.log(`\n Server running on http://localhost:${PORT}`);
            console.log(` Chat API: POST http://localhost:${PORT}/chat`);
            console.log(` History API: GET http://localhost:${PORT}/history/:userId`);
            console.log(` Health check: GET http://localhost:${PORT}/health`);
            console.log("\n Example curl command:");
            console.log(`curl -X POST http://localhost:${PORT}/chat -H "Content-Type: application/json" -d '{"message":"What's the weather in Paris?","userId":"test"}'`);
            console.log("\n Agent is ready to receive requests!");
        });

    } catch (error) {
        console.error("❌ Error starting application:", error.message);
        process.exit(1);
    }
})();

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('\n🛑 Shutting down gracefully...');
    await agent.disconnect();
    process.exit(0);
});

process.on('SIGTERM', async () => {
    console.log('\n🛑 Shutting down gracefully...');
    await agent.disconnect();
    process.exit(0);
});
