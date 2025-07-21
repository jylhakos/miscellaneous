// demo.js - Standalone demo without external API calls

const { MemoryStore } = require('./src/memory');

class DemoWeatherAgent {
    constructor() {
        this.memory = new MemoryStore(false); // In-memory only
        // Mock weather data for demo
        this.mockWeatherData = {
            'london': { city: 'London', country: 'UK', temp: '18°C', condition: 'partly cloudy' },
            'paris': { city: 'Paris', country: 'France', temp: '22°C', condition: 'sunny' },
            'tokyo': { city: 'Tokyo', country: 'Japan', temp: '25°C', condition: 'clear' },
            'new york': { city: 'New York', country: 'USA', temp: '20°C', condition: 'cloudy' }
        };
    }

    async process(userId, input) {
        const lowerInput = input.toLowerCase();
        
        try {
            // Handle name introduction
            if (lowerInput.includes("my name is") || lowerInput.includes("i'm") || lowerInput.includes("i am")) {
                const name = this.extractName(input);
                if (name) {
                    await this.memory.setMemory(`user:${userId}:name`, name);
                    return `Nice to meet you, ${name}! I'm your weather assistant. You can ask me about the weather in any city.`;
                }
                return "Nice to meet you! What's your name?";
            }
            
            // Handle weather requests
            if (this.isWeatherRequest(lowerInput)) {
                const city = this.extractCity(input);
                if (city) {
                    const weatherData = this.mockWeatherData[city.toLowerCase()];
                    if (weatherData) {
                        const userName = await this.memory.getMemory(`user:${userId}:name`);
                        const greeting = userName ? `${userName}, ` : "";
                        return `${greeting}the weather in ${weatherData.city}, ${weatherData.country} is currently ${weatherData.condition} with a temperature of ${weatherData.temp}.`;
                    } else {
                        return `I don't have weather data for "${city}" in my demo database. Try London, Paris, Tokyo, or New York!`;
                    }
                }
                return "Which city would you like to know the weather for?";
            }
            
            // Handle greetings
            if (this.isGreeting(lowerInput)) {
                const userName = await this.memory.getMemory(`user:${userId}:name`);
                if (userName) {
                    return `Hello again, ${userName}! How can I help you today?`;
                } else {
                    return "Hello! I'm your weather assistant. What's your name?";
                }
            }
            
            // Default response
            const userName = await this.memory.getMemory(`user:${userId}:name`);
            const greeting = userName ? `${userName}, ` : "";
            return `${greeting}I'm a weather assistant. I can help you with weather information for cities like London, Paris, Tokyo, and New York. You can also introduce yourself to me!`;
            
        } catch (error) {
            console.error("Error processing request:", error);
            return "I'm sorry, I encountered an error. Please try again.";
        }
    }

    extractName(input) {
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

    extractCity(input) {
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

    isGreeting(input) {
        const greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'];
        return greetings.some(greeting => input.includes(greeting));
    }

    isWeatherRequest(input) {
        return input.includes('weather') || input.includes('temperature') || input.includes('forecast');
    }

    async getConversationHistory(userId) {
        return await this.memory.getConversationHistory(userId);
    }

    async disconnect() {
        await this.memory.disconnect();
    }
}

async function runDemo() {
    console.log("Weather Agent Demo (Offline Mode)\n");
    
    const agent = new DemoWeatherAgent();
    const userId = "demo_user";
    
    const testMessages = [
        "Hello",
        "My name is Alice", 
        "What's the weather in London?",
        "Hi there",
        "How about Tokyo weather?",
        "Weather in Miami?",  // Not in demo database
        "What can you help me with?"
    ];

    for (const message of testMessages) {
        try {
            console.log(`User: ${message}`);
            const response = await agent.process(userId, message);
            console.log(`Agent: ${response}\n`);
            
            // Small delay for readability
            await new Promise(resolve => setTimeout(resolve, 1000));
        } catch (error) {
            console.log(`❌ Error: ${error.message}\n`);
        }
    }

    console.log("Conversation History:");
    try {
        const history = await agent.getConversationHistory(userId);
        if (history.length > 0) {
            history.forEach((interaction, index) => {
                console.log(`${index + 1}. [${interaction.timestamp}]`);
                console.log(`   User: ${interaction.message}`);
                console.log(`   Agent: ${interaction.response}`);
            });
        } else {
            console.log("   No conversation history available");
        }
    } catch (error) {
        console.log("   Error retrieving history:", error.message);
    }

    await agent.disconnect();
}

// Run the demo
runDemo().catch(console.error);
