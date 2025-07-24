// src/rag.js

require('dotenv').config();

const {BufferMemory} = require('langchain/memory');

const memory = new BufferMemory();

const{ LLMChain, PromptTemplate } = require('langchain');

// Using custome knowledge sources (RAG)

const {TextLoader } = require('langchain/document_loaders/fs/text');

const loader = new TextLoader('knowledge_base.txt', 'utf-8');

const documents = loader.load();

// Define the Prompt Template
const PromptTemplate = new PromptTemplate.fromTemplate({inputVariables: ['question'], template: "<|question|>"});

// Create an LLMChain instance
const llmChain = new LLMChain({llm: process.env.LLM, prompt: PromptTemplate});

// Handles user queries by sending queries to the LLM model and returning a response
async function getAnswer(query) {
    try {
        if (!query) {
            throw new Error("Question cannot be empty");
        }
        // This makes Q&A chat domain-specific retrieving answer from a dataset
        const knowledgeBase = await documents;

        if (!knowledgeBase || knowledgeBase.length === 0) {
            throw new Error("Knowledge base is empty");
        }
        else {
            context = knowledgeBase.join("")
            const fullQuery = `Using the context: ${context}, answer the question: ${question}`;
            query = fullQuery;
        }
        const previousContext = await memory.loadMemoryVariables({});
        if (previousContext) {
            const newQuestion = `${query} Previous context: ${JSON.stringify(previousContext)}`;
            query = newQuestion;
        }
        const response = await llmChain.call({ question: query });
        memory.saveMemory(response.text);
        return response;

    } catch (error) {
        console.error("Error occurred while getting answer:", error);
        throw error;
    }
}

module.exports = {getAnswer};

