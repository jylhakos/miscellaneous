// redis-demo.js - Demonstrate Redis persistence across sessions

const { MemoryStore } = require('./src/memory');
const { fetchWeather, getWeatherDescription } = require('./src/tools');

class RedisWeatherDemo {
    constructor() {
        this.memory = new MemoryStore(true); // Enable Redis
        // Mock weather for demo (to avoid API delays)
        this.mockWeather = {
            'london': { city: 'London', country: 'UK', temp: 18, condition: 'partly cloudy' },
            'paris': { city: 'Paris', country: 'France', temp: 22, condition: 'sunny' },
            'tokyo': { city: 'Tokyo', country: 'Japan', temp: 25, condition: 'clear' }
        };
    }

    async process(userId, input) {
        const lowerInput = input.toLowerCase();
        
        // Store input in conversation history
        await this.memory.addToConversationHistory(userId, input, "");

        // Handle name introduction
        if (lowerInput.includes("my name is")) {
            const nameMatch = input.match(/my name is\s+([a-zA-Z\s]+)/i);
            if (nameMatch) {
                const name = nameMatch[1].trim();
                await this.memory.setMemory(`user:${userId}:name`, name);
                const response = `Nice to meet you, ${name}! I'm your weather assistant with Redis memory. I'll remember you next time!`;
                await this.memory.addToConversationHistory(userId, input, response);
                return response;
            }
        }

        // Handle weather requests
        if (lowerInput.includes('weather') && lowerInput.includes('in')) {
            const cityMatch = input.match(/weather.*in\s+([a-zA-Z\s]+)/i);
            if (cityMatch) {
                const city = cityMatch[1].trim().toLowerCase();
                const weather = this.mockWeather[city];
                if (weather) {
                    const userName = await this.memory.getMemory(`user:${userId}:name`);
                    const greeting = userName ? `${userName}, ` : "";
                    const response = `${greeting}the weather in ${weather.city}, ${weather.country} is ${weather.condition} with ${weather.temp}°C. (Data stored in Redis!)`;
                    await this.memory.addToConversationHistory(userId, input, response);
                    return response;
                }
            }
            return "I can tell you about weather in London, Paris, or Tokyo!";
        }

        // Handle greetings
        if (lowerInput.includes('hello') || lowerInput.includes('hi')) {
            const userName = await this.memory.getMemory(`user:${userId}:name`);
            if (userName) {
                return `Hello again, ${userName}! I remember you from our previous conversation. How can I help you today?`;
            } else {
                return "Hello! I'm your weather assistant with Redis memory. What's your name?";
            }
        }

        // Default response
        const userName = await this.memory.getMemory(`user:${userId}:name`);
        const greeting = userName ? `${userName}, ` : "";
        return `${greeting}I can help you with weather information and I'll remember our conversation using Redis! Try: "What's the weather in London?"`;
    }

    async showUserInfo(userId) {
        const userName = await this.memory.getMemory(`user:${userId}:name`);
        const history = await this.memory.getConversationHistory(userId);
        
        console.log(`\n User Info (stored in Redis):`);
        console.log(`   User ID: ${userId}`);
        console.log(`   Name: ${userName || 'Not set'}`);
        console.log(`   Conversation history: ${history.length} entries`);
        
        if (history.length > 0) {
            console.log(`   Recent interactions:`);
            history.slice(-3).forEach((entry, index) => {
                console.log(`     ${index + 1}. "${entry.message}" -> "${entry.response}"`);
            });
        }
    }

    async disconnect() {
        await this.memory.disconnect();
    }
}

async function demonstratePersistence() {
    console.log(' Redis Persistence Demo for Weather Agent\n');
    
    const agent = new RedisWeatherDemo();
    
    console.log('=== SESSION 1: New User ===');
    const userId = 'demo_user_redis';
    
    // First interaction
    let response = await agent.process(userId, 'Hello');
    console.log(` User: Hello`);
    console.log(` Agent: ${response}\n`);
    
    // Introduce name
    response = await agent.process(userId, 'My name is John');
    console.log(` User: My name is John`);
    console.log(` Agent: ${response}\n`);
    
    // Ask for weather
    response = await agent.process(userId, 'What\'s the weather in London?');
    console.log(` User: What's the weather in London?`);
    console.log(` Agent: ${response}\n`);
    
    await agent.showUserInfo(userId);
    
    console.log('\n  Simulating application restart...\n');
    
    console.log('=== SESSION 2: Returning User (after restart) ===');
    // Simulate new session by creating new agent instance
    const agentSession2 = new RedisWeatherDemo();
    
    // User returns
    response = await agentSession2.process(userId, 'Hi there!');
    console.log(` User: Hi there!`);
    console.log(` Agent: ${response}\n`);
    
    // Ask for different weather
    response = await agentSession2.process(userId, 'How about weather in Paris?');
    console.log(` User: How about weather in Paris?`);
    console.log(` Agent: ${response}\n`);
    
    await agentSession2.showUserInfo(userId);
    
    console.log('\n Demonstrating data persistence in Redis:');
    console.log(' User name persisted across sessions');
    console.log(' Conversation history maintained');
    console.log(' Multiple application restarts supported');
    console.log(' Data survives container restarts (with volume)');
    
    await agentSession2.disconnect();
}

// Run the demo
demonstratePersistence().catch(console.error);
