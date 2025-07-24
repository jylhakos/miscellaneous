// src/rag.js
const { Ollama } = require('@langchain/ollama');
const { ChatPromptTemplate, MessagesPlaceholder } = require('@langchain/core/prompts');
const { RunnableSequence } = require('@langchain/core/runnables');
const { ChromaVectorStore } = require('@langchain/community/vectorstores/chroma');
const { OllamaEmbeddings } = require('@langchain/ollama');
const { BufferMemory } = require('langchain/memory');
const { ConversationSummaryBufferMemory } = require('langchain/memory');
const { formatDocumentsAsString } = require('langchain/util/document');
const logger = require('./utils/logger');
require('dotenv').config();

class RAGChatSystem {
  constructor() {
    this.llm = null;
    this.vectorStore = null;
    this.retriever = null;
    this.embeddings = null;
    this.conversations = new Map(); // Store conversations by session ID
    this.initialized = false;
  }

  async initialize() {
    try {
      logger.info('Initializing RAG Chat System...');
      
      // Initialize Ollama LLM
      this.llm = new Ollama({
        baseUrl: process.env.OLLAMA_BASE_URL || 'http://localhost:11434',
        model: process.env.OLLAMA_MODEL || 'llama3.1:8b',
        temperature: parseFloat(process.env.LLM_TEMPERATURE) || 0.7,
        topP: parseFloat(process.env.LLM_TOP_P) || 0.9,
        topK: parseInt(process.env.LLM_TOP_K) || 40,
      });

      // Initialize embeddings
      this.embeddings = new OllamaEmbeddings({
        baseUrl: process.env.OLLAMA_BASE_URL || 'http://localhost:11434',
        model: process.env.EMBEDDING_MODEL || 'nomic-embed-text',
      });

      // Initialize ChromaDB vector store
      this.vectorStore = new ChromaVectorStore(this.embeddings, {
        collectionName: process.env.CHROMA_COLLECTION || 'rag_documents',
        url: process.env.CHROMA_URL || 'http://localhost:8000',
      });

      // Create retriever
      this.retriever = this.vectorStore.asRetriever({
        k: parseInt(process.env.RETRIEVAL_K) || 4,
        searchType: 'similarity',
      });

      this.initialized = true;
      logger.info('RAG Chat System initialized successfully');
    } catch (error) {
      logger.error('Failed to initialize RAG Chat System:', error);
      throw error;
    }
  }

  getOrCreateConversation(sessionId) {
    if (!this.conversations.has(sessionId)) {
      const memory = new ConversationSummaryBufferMemory({
        llm: this.llm,
        maxTokenLimit: parseInt(process.env.MEMORY_TOKEN_LIMIT) || 2000,
        returnMessages: true,
        memoryKey: 'chat_history',
      });
      
      this.conversations.set(sessionId, {
        memory,
        createdAt: new Date(),
        lastAccessed: new Date(),
      });
      
      logger.info(`Created new conversation for session: ${sessionId}`);
    }
    
    this.conversations.get(sessionId).lastAccessed = new Date();
    return this.conversations.get(sessionId);
  }

  cleanupOldConversations() {
    const maxAge = parseInt(process.env.SESSION_MAX_AGE_HOURS) * 60 * 60 * 1000 || 24 * 60 * 60 * 1000; // 24 hours default
    const now = new Date();
    
    for (const [sessionId, conversation] of this.conversations.entries()) {
      if (now - conversation.lastAccessed > maxAge) {
        this.conversations.delete(sessionId);
        logger.info(`Cleaned up expired conversation for session: ${sessionId}`);
      }
    }
  }

  createPromptTemplate() {
    return ChatPromptTemplate.fromMessages([
      [
        'system',
        `You are a helpful AI assistant with access to a knowledge base. Use the provided context to answer questions accurately and helpfully.

Context from knowledge base:
{context}

Instructions:
- Answer based on the provided context when relevant
- If the context doesn't contain relevant information, say so clearly
- Be concise but comprehensive
- Maintain conversation context from previous messages
- Use a friendly, professional tone
- If asked about Meta Llama 4 Scout or similar models, refer to the documentation and capabilities provided in the context

Current conversation:`
      ],
      new MessagesPlaceholder('chat_history'),
      ['human', '{question}']
    ]);
  }

  async processQuery(query, sessionId = 'default') {
    try {
      if (!this.initialized) {
        await this.initialize();
      }

      if (!query || typeof query !== 'string' || query.trim().length === 0) {
        throw new Error('Query cannot be empty');
      }

      logger.info(`Processing query for session ${sessionId}: ${query.substring(0, 100)}...`);

      // Get or create conversation
      const conversation = this.getOrCreateConversation(sessionId);
      
      // Clean up old conversations periodically
      if (Math.random() < 0.1) { // 10% chance to trigger cleanup
        this.cleanupOldConversations();
      }

      // Retrieve relevant documents
      const relevantDocs = await this.retriever.getRelevantDocuments(query);
      const context = formatDocumentsAsString(relevantDocs);

      logger.info(`Retrieved ${relevantDocs.length} relevant documents`);

      // Create the prompt template
      const promptTemplate = this.createPromptTemplate();

      // Create the chain
      const chain = RunnableSequence.from([
        {
          question: (input) => input.question,
          context: () => context,
          chat_history: async () => {
            const memoryVariables = await conversation.memory.loadMemoryVariables({});
            return memoryVariables.chat_history || [];
          },
        },
        promptTemplate,
        this.llm,
      ]);

      // Generate response
      const response = await chain.invoke({ question: query });

      // Save to memory
      await conversation.memory.saveContext(
        { input: query },
        { output: response.content }
      );

      logger.info(`Generated response for session ${sessionId}`);

      return {
        answer: response.content,
        sources: relevantDocs.map(doc => ({
          content: doc.pageContent.substring(0, 200) + '...',
          metadata: doc.metadata,
        })),
        sessionId,
        timestamp: new Date().toISOString(),
      };

    } catch (error) {
      logger.error(`Error processing query for session ${sessionId}:`, error);
      
      // Return a user-friendly error response
      const errorResponse = {
        answer: 'I apologize, but I encountered an error while processing your question. Please try again later.',
        error: error.message,
        sessionId,
        timestamp: new Date().toISOString(),
      };

      // If it's a connection error, provide specific guidance
      if (error.message.includes('ECONNREFUSED') || error.message.includes('fetch')) {
        errorResponse.answer = 'I\'m unable to connect to the AI model or vector database. Please ensure all services are running and try again.';
      }

      throw errorResponse;
    }
  }

  async addDocuments(documents) {
    try {
      if (!this.initialized) {
        await this.initialize();
      }

      await this.vectorStore.addDocuments(documents);
      logger.info(`Added ${documents.length} documents to vector store`);
    } catch (error) {
      logger.error('Error adding documents to vector store:', error);
      throw error;
    }
  }

  async searchDocuments(query, k = 5) {
    try {
      if (!this.initialized) {
        await this.initialize();
      }

      const results = await this.vectorStore.similaritySearch(query, k);
      return results;
    } catch (error) {
      logger.error('Error searching documents:', error);
      throw error;
    }
  }

  getConversationStats() {
    return {
      activeConversations: this.conversations.size,
      totalConversations: this.conversations.size,
      oldestConversation: Math.min(...Array.from(this.conversations.values()).map(c => c.createdAt)),
    };
  }
}

// Create singleton instance
const ragChatSystem = new RAGChatSystem();

module.exports = {
  ragChatSystem,
  RAGChatSystem,
};
