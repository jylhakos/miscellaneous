// src/agents.js

const { SessionMemoryStore } = require("./memory");
const { fetchWeather, getWeatherDescription } = require("./tools");
const { BaseChain } = require("@langchain/core/chains/base");
const { ChatOpenAI } = require("@langchain/openai");
const { PromptTemplate } = require("@langchain/core/prompts");
const { LLMChain } = require("langchain/chains");
const { CallbackManagerForChainRun } = require("@langchain/core/callbacks/manager");

require('dotenv').config();

/**
 * Custom LangChain for processing user queries
 */
class WeatherAgentChain extends BaseChain {
    constructor() {
        super({});
        this.memory = new SessionMemoryStore();
        
        // Initialize OpenAI model
        this.llm = new ChatOpenAI({
            openAIApiKey: process.env.OPENAI_API_KEY,
            temperature: 0.3,
            modelName: "gpt-3.5-turbo"
        });

        // Create prompt template for classification
        this.classificationPrompt = PromptTemplate.fromTemplate(`
            Classify the user's message into one of these categories:
            1. "greeting" - if the user is greeting or introducing themselves
            2. "weather" - if the user is asking about weather in any city
            3. "other" - for any other type of message

            User message: {input}
            
            Classification (respond with only one word: greeting, weather, or other):
        `);

        this.classificationChain = new LLMChain({
            llm: this.llm,
            prompt: this.classificationPrompt
        });

        // Create prompt for extracting city from weather requests
        this.cityExtractionPrompt = PromptTemplate.fromTemplate(`
            Extract the city name from the user's weather request.
            If no specific city is mentioned, respond with "unknown".
            
            User message: {input}
            
            City name:
        `);

        this.cityExtractionChain = new LLMChain({
            llm: this.llm,
            prompt: this.cityExtractionPrompt
        });

        // Create prompt for extracting user name
        this.nameExtractionPrompt = PromptTemplate.fromTemplate(`
            Extract the user's name from their greeting or introduction.
            If no name is mentioned, respond with "unknown".
            
            User message: {input}
            
            User name:
        `);

        this.nameExtractionChain = new LLMChain({
            llm: this.llm,
            prompt: this.nameExtractionPrompt
        });
    }

    get _chainType() {
        return "weather_agent_chain";
    }

    get inputKeys() {
        return ["input", "userId"];
    }

    get outputKeys() {
        return ["output"];
    }

    async _call(values, runManager) {
        const { input, userId } = values;
        
        try {
            // Store the user input for conversation history
            await this.memory.addToConversationHistory(userId, input, "");

            // Classify the input
            const classificationResult = await this.classificationChain.call({ input });
            const classification = classificationResult.text.trim().toLowerCase();

            let response = "";

            switch (classification) {
                case "greeting":
                    response = await this.handleGreeting(input, userId);
                    break;
                
                case "weather":
                    response = await this.handleWeatherRequest(input, userId);
                    break;
                
                default:
                    response = await this.handleDefault(input, userId);
                    break;
            }

            // Update conversation history with response
            await this.memory.addToConversationHistory(userId, input, response);

            return { output: response };

        } catch (error) {
            console.error("Error in WeatherAgentChain:", error);
            return { output: "I'm sorry, I encountered an error while processing your request. Please try again." };
        }
    }

    async handleGreeting(input, userId) {
        try {
            // Extract name from greeting
            const nameResult = await this.nameExtractionChain.call({ input });
            const extractedName = nameResult.text.trim();

            // Get existing name from memory
            const existingName = await this.memory.getMemory(`user:${userId}:name`);

            if (extractedName && extractedName.toLowerCase() !== "unknown") {
                // Store the name in memory
                await this.memory.setMemory(`user:${userId}:name`, extractedName);
                return `Nice to meet you, ${extractedName}! I'm your weather assistant. You can ask me about the weather in any city.`;
            } else if (existingName) {
                return `Hello again, ${existingName}! How can I help you today? You can ask me about the weather in any city.`;
            } else {
                return "Hello! I'm your weather assistant. What's your name? You can also ask me about the weather in any city.";
            }
        } catch (error) {
            console.error("Error handling greeting:", error);
            return "Hello! I'm your weather assistant. How can I help you today?";
        }
    }

    async handleWeatherRequest(input, userId) {
        try {
            // Extract city from input
            const cityResult = await this.cityExtractionChain.call({ input });
            const city = cityResult.text.trim();

            if (!city || city.toLowerCase() === "unknown") {
                return "I'd be happy to help you with the weather! Could you please tell me which city you'd like to know about?";
            }

            // Get weather data
            const weatherData = await fetchWeather(city);

            const weatherDescription = getWeatherDescription(weatherData.current.weathercode);

            // Get user name for personalized response
            const userName = await this.memory.getMemory(`user:${userId}:name`);

            const greeting = userName ? `${userName}, ` : "";

            return `${greeting}the weather in ${weatherData.location.name}, ${weatherData.location.country} is currently ${weatherDescription.toLowerCase()} with a temperature of ${weatherData.current.temperature}${weatherData.units.temperature}. Wind speed is ${weatherData.current.windspeed} ${weatherData.units.windspeed}.`;

        } catch (error) {
            console.error("Error handling weather request:", error);
            if (error.message.includes("not found")) {
                return "I couldn't find that city. Please check the spelling and try again.";
            }
            return "I'm sorry, I couldn't fetch the weather data right now. Please try again later.";
        }
    }

    async handleDefault(input, userId) {
        const userName = await this.memory.getMemory(`user:${userId}:name`);
        const greeting = userName ? `${userName}, ` : "";

        return `${greeting}I'm an assistant. I can help you with the following:
- Getting weather information for any city (just ask "What's the weather in [city]?")
- Remembering your name for personalized responses

You can also greet me or introduce yourself. How can I help you today?`;
    }
}

/**
 * Simple Agent class for basic functionality
 */
class SimpleAgent {
    async process(input) {
        const lowerInput = input.toLowerCase();

        if (lowerInput.includes("weather") && lowerInput.includes(" in ")) {
            const cityMatch = lowerInput.match(/weather.*in\s+([a-zA-Z\s]+)/);
            if (cityMatch) {
                const city = cityMatch[1].trim();
                try {
                    const weatherData = await fetchWeather(city);
                    const weatherDescription = getWeatherDescription(weatherData.current.weathercode);
                    return `The weather in ${weatherData.location.name} is ${weatherDescription.toLowerCase()} with a temperature of ${weatherData.current.temperature}${weatherData.units.temperature}.`;
                } catch (error) {
                    return `Sorry, I couldn't find weather information for "${city}".`;
                }
            }
        }

        return "I can help you with the weather. Please ask about the weather in a specific city.";
    }

    async getWeather(city) {
        try {
            const weatherData = await fetchWeather(city);
            return weatherData;
        } catch (error) {
            throw error;
        }
    }
}

/**
 * Enhanced Memory Agent with LangChain integration
 */
class MemoryAgent {
    constructor() {
        this.memory = new SessionMemoryStore();
        this.weatherChain = new WeatherAgentChain();
    }

    async process(userId, input) {
        try {
            // Use the LangChain for processing
            const result = await this.weatherChain.call({
                input: input,
                userId: userId
            });

            return result.output;

        } catch (error) {
            console.error("Error in MemoryAgent.process:", error);
            
            // Fallback to simple processing
            const lowerInput = input.toLowerCase();

            if (lowerInput.startsWith("my name is ")) {
                const name = input.split(" ").slice(3).join(" ");
                await this.memory.setMemory(`user:${userId}:name`, name);
                return `Nice to meet you, ${name}! How can I help you?`;
            }

            const name = await this.memory.getMemory(`user:${userId}:name`);

            if (name) {
                return `Hello, ${name}! How can I help you today?`;
            }

            return "Hello! What's your name?";
        }
    }

    async getConversationHistory(userId) {
        return await this.memory.getConversationHistory(userId);
    }

    async disconnect() {
        await this.memory.disconnect();
    }
}

module.exports = {
    SimpleAgent,
    MemoryAgent,
    WeatherAgentChain
};

module.exports = { MemoryAgent }

