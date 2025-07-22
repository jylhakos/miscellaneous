// qa.js
require("dotenv").config();

const { Ollama } = require("@langchain/ollama");
const { PromptTemplate } = require("@langchain/core/prompts");
const { LLMChain } = require("langchain/chains");
const { BufferMemory } = require("langchain/memory");

// Session management for conversation memory
const sessions = new Map();

// Initialize Ollama model
const initializeOllama = () => {
    return new Ollama({
        baseUrl: process.env.OLLAMA_BASE_URL || "http://localhost:11434",
        model: process.env.OLLAMA_MODEL || "llama4:scout",
        temperature: 0.7,
        topP: 0.9,
        numCtx: 4096, // Context window size
        numPredict: 1024, // Max tokens to predict
    });
};

// Create a session with memory
const createSession = (sessionId) => {
    if (!sessions.has(sessionId)) {
        const memory = new BufferMemory({
            memoryKey: "chat_history",
            maxTokenLimit: parseInt(process.env.MAX_MEMORY_HISTORY) || 20,
            returnMessages: true,
        });
        
        sessions.set(sessionId, {
            memory,
            createdAt: new Date(),
            lastUsed: new Date(),
        });
        
        // Clean up old sessions
        cleanupSessions();
    }
    return sessions.get(sessionId);
};

// Clean up expired sessions
const cleanupSessions = () => {
    const timeout = parseInt(process.env.SESSION_TIMEOUT) || 3600000; // 1 hour default
    const now = new Date();
    
    for (const [sessionId, session] of sessions.entries()) {
        if (now - session.lastUsed > timeout) {
            sessions.delete(sessionId);
            console.log(`🗑️ Session ${sessionId} expired and cleaned up`);
        }
    }
};

// Get session history
const getSessionHistory = (sessionId) => {
    const session = sessions.get(sessionId);
    if (!session) {
        return [];
    }
    
    return session.memory.chatHistory || [];
};

// Clear session
const clearSession = (sessionId) => {
    if (sessions.has(sessionId)) {
        sessions.delete(sessionId);
        return true;
    }
    return false;
};

// Define the chat prompt template for Llama 4 (Scout)
const createChatPromptTemplate = () => {
    return PromptTemplate.fromTemplate(
        "You are Scout, an intelligent and helpful AI assistant based on Llama 4. You provide accurate, detailed, and contextual responses to user questions. You maintain conversation context and can reference previous parts of our conversation.\n\nCurrent conversation context:\n{chat_history}\n\nHuman: {question}\n\nAssistant:"
    );
};

// Initialize global Ollama model and prompt template
let ollamaModel = null;
let promptTemplate = null;
let llmChain = null;

// Initialize the LLM chain
const initializeLLMChain = async () => {
    try {
        if (!ollamaModel) {
            ollamaModel = initializeOllama();
            promptTemplate = createChatPromptTemplate();
            llmChain = new LLMChain({
                llm: ollamaModel,
                prompt: promptTemplate,
                verbose: process.env.NODE_ENV === 'development',
            });
            console.log("✅ Ollama LLM Chain initialized successfully");
        }
        return llmChain;
    } catch (error) {
        console.error("❌ Error initializing LLM chain:", error);
        throw new Error("Failed to initialize Ollama connection");
    }
};

// Main function to handle user queries
async function getAnswer(question, sessionId = 'default') {
    try {
        // Initialize LLM chain if not already done
        await initializeLLMChain();
        
        // Create or get existing session
        const session = createSession(sessionId);
        session.lastUsed = new Date();
        
        // Get conversation history
        const chatHistory = await session.memory.getChatHistory();
        const historyString = chatHistory.map(msg => `${msg.type}: ${msg.text}`).join('\n');
        
        console.log(`💭 Processing question for session ${sessionId}: ${question}`);
        
        // Generate response using LLM chain
        const response = await llmChain.call({
            question: question,
            chat_history: historyString || "No previous conversation."
        });
        
        // Save conversation to memory
        await session.memory.saveContext(
            { input: question },
            { output: response.text }
        );
        
        console.log(`✅ Generated response for session ${sessionId}`);
        return response.text;
        
    } catch (error) {
        console.error("❌ Error handling query:", error);
        
        // Fallback response if Ollama is not available
        if (error.message.includes('fetch') || error.message.includes('ECONNREFUSED')) {
            return "⚠️ I'm sorry, but I'm currently unable to connect to the Ollama server. Please ensure that Ollama is running and the Llama 4 (Scout) model is available. You can start Ollama with: `ollama serve` and pull the model with: `ollama pull llama4:scout`";
        }
        
        throw new Error(`Failed to process the query: ${error.message}`);
    }
}

// Test Ollama connection
const testOllamaConnection = async () => {
    try {
        const testModel = initializeOllama();
        const testResponse = await testModel.call("Hello, are you working?");
        console.log("✅ Ollama connection test successful");
        return true;
    } catch (error) {
        console.error("❌ Ollama connection test failed:", error.message);
        return false;
    }
};

// Export functions
module.exports = {
    getAnswer,
    createSession,
    getSessionHistory,
    clearSession,
    testOllamaConnection,
    initializeLLMChain
};
