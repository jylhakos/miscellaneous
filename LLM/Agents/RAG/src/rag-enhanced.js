// src/rag-enhanced.js - Enhanced RAG system with smart routing
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

class EnhancedRAGChatSystem {
  constructor() {
    this.llm = null;
    this.vectorStore = null;
    this.retriever = null;
    this.embeddings = null;
    this.conversations = new Map();
    this.initialized = false;
    
    // Query classification thresholds
    this.SIMILARITY_THRESHOLD = parseFloat(process.env.SIMILARITY_THRESHOLD) || 0.5;
    this.MIN_RELEVANT_DOCS = parseInt(process.env.MIN_RELEVANT_DOCS) || 1;
  }

  async initialize() {
    try {
      logger.info('Initializing Enhanced RAG Chat System...');
      
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

      // Create retriever with score threshold
      this.retriever = this.vectorStore.asRetriever({
        k: parseInt(process.env.RETRIEVAL_K) || 4,
        searchType: 'similarity_score_threshold',
        searchKwargs: {
          scoreThreshold: this.SIMILARITY_THRESHOLD
        }
      });

      this.initialized = true;
      logger.info('Enhanced RAG Chat System initialized successfully');
    } catch (error) {
      logger.error('Failed to initialize Enhanced RAG Chat System:', error);
      throw error;
    }
  }

  /**
   * Classify query to determine if RAG or pure LLM should be used
   */
  async classifyQuery(query) {
    const classification = {
      useRAG: true,
      reasoning: '',
      confidence: 0.5
    };

    // Pattern-based classification
    const patterns = {
      factual: /what is|who is|when did|where is|how does|define|explain/i,
      personal: /my name is|i am|i work|remember that/i,
      general: /hello|hi|goodbye|thank you|how are you/i,
      computational: /calculate|compute|solve|what's \d+/i,
      creative: /write a story|create a poem|imagine/i
    };

    // Check for general conversation patterns
    if (patterns.general.test(query)) {
      classification.useRAG = false;
      classification.reasoning = 'General conversational query';
      classification.confidence = 0.8;
      return classification;
    }

    // Check for computational queries
    if (patterns.computational.test(query)) {
      classification.useRAG = false;
      classification.reasoning = 'Computational/mathematical query';
      classification.confidence = 0.9;
      return classification;
    }

    // Check for creative writing
    if (patterns.creative.test(query)) {
      classification.useRAG = false;
      classification.reasoning = 'Creative writing request';
      classification.confidence = 0.7;
      return classification;
    }

    // For other queries, check vector database relevance
    try {
      const relevantDocs = await this.vectorStore.similaritySearchWithScore(query, 1);
      
      if (relevantDocs.length === 0) {
        classification.useRAG = false;
        classification.reasoning = 'No relevant documents found';
        classification.confidence = 0.9;
      } else {
        const [doc, score] = relevantDocs[0];
        if (score < this.SIMILARITY_THRESHOLD) {
          classification.useRAG = false;
          classification.reasoning = `Low similarity score: ${score}`;
          classification.confidence = 0.8;
        } else {
          classification.useRAG = true;
          classification.reasoning = `High similarity score: ${score}`;
          classification.confidence = score;
        }
      }
    } catch (error) {
      logger.warn('Error during query classification, defaulting to RAG:', error.message);
    }

    return classification;
  }

  /**
   * Create Llama 4 Scout specific prompt template
   */
  createLlama4ScoutPrompt(includeContext = true) {
    const systemMessage = includeContext ? 
      `You are a helpful AI assistant with access to a knowledge base. Use the provided context to answer questions accurately and helpfully.

Context from knowledge base:
{context}

Instructions:
- Answer based on the provided context when relevant
- If the context doesn't contain relevant information, say so clearly
- Be concise but comprehensive
- Maintain conversation context from previous messages
- Use a friendly, professional tone
- Cite sources when possible

Current conversation:` :
      `You are a helpful AI assistant. Answer questions based on your training knowledge.

Instructions:
- Provide accurate and helpful responses
- Be concise but comprehensive
- Maintain conversation context from previous messages
- Use a friendly, professional tone
- If you're unsure about something, say so clearly

Current conversation:`;

    return ChatPromptTemplate.fromMessages([
      ['system', systemMessage],
      new MessagesPlaceholder('chat_history'),
      ['human', '{question}']
    ]);
  }

  /**
   * Enhanced query processing with smart routing
   */
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
      
      // Classify query to determine processing strategy
      const classification = await this.classifyQuery(query);
      logger.info(`Query classification: ${classification.useRAG ? 'RAG' : 'Pure LLM'} (${classification.reasoning})`);

      let context = '';
      let relevantDocs = [];
      let processingStrategy = classification.useRAG ? 'RAG' : 'Pure LLM';

      if (classification.useRAG) {
        // Retrieve relevant documents
        relevantDocs = await this.retriever.getRelevantDocuments(query);
        context = formatDocumentsAsString(relevantDocs);
        
        logger.info(`Retrieved ${relevantDocs.length} relevant documents`);
        
        // If no relevant docs found, fall back to pure LLM
        if (relevantDocs.length === 0) {
          processingStrategy = 'Pure LLM (Fallback)';
          logger.info('No relevant documents found, falling back to pure LLM');
        }
      }

      // Create appropriate prompt template
      const promptTemplate = this.createLlama4ScoutPrompt(relevantDocs.length > 0);

      // Create the chain based on strategy
      const chainInput = relevantDocs.length > 0 ? {
        question: (input) => input.question,
        context: () => context,
        chat_history: async () => {
          const memoryVariables = await conversation.memory.loadMemoryVariables({});
          return memoryVariables.chat_history || [];
        },
      } : {
        question: (input) => input.question,
        chat_history: async () => {
          const memoryVariables = await conversation.memory.loadMemoryVariables({});
          return memoryVariables.chat_history || [];
        },
      };

      const chain = RunnableSequence.from([
        chainInput,
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

      logger.info(`Generated response for session ${sessionId} using ${processingStrategy}`);

      return {
        answer: response.content,
        sources: relevantDocs.map(doc => ({
          content: doc.pageContent.substring(0, 200) + '...',
          metadata: doc.metadata,
        })),
        sessionId,
        timestamp: new Date().toISOString(),
        processingStrategy,
        classification: {
          useRAG: classification.useRAG,
          reasoning: classification.reasoning,
          confidence: classification.confidence
        }
      };

    } catch (error) {
      logger.error(`Error processing query for session ${sessionId}:`, error);
      
      const errorResponse = {
        answer: 'I apologize, but I encountered an error while processing your question. Please try again later.',
        error: error.message,
        sessionId,
        timestamp: new Date().toISOString(),
        processingStrategy: 'Error',
      };

      if (error.message.includes('ECONNREFUSED') || error.message.includes('fetch')) {
        errorResponse.answer = 'I\'m unable to connect to the AI model or vector database. Please ensure all services are running and try again.';
      }

      throw errorResponse;
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

  /**
   * Enhanced document addition with detailed vectorization logging
   */
  async addDocuments(documents) {
    try {
      if (!this.initialized) {
        await this.initialize();
      }

      logger.info(`Starting vectorization of ${documents.length} document chunks`);
      
      // Process documents in batches to avoid overwhelming the embedding model
      const batchSize = parseInt(process.env.EMBEDDING_BATCH_SIZE) || 10;
      const batches = [];
      
      for (let i = 0; i < documents.length; i += batchSize) {
        batches.push(documents.slice(i, i + batchSize));
      }

      let totalProcessed = 0;
      for (const [batchIndex, batch] of batches.entries()) {
        logger.info(`Processing batch ${batchIndex + 1}/${batches.length} (${batch.length} chunks)`);
        
        // Generate embeddings and store
        await this.vectorStore.addDocuments(batch);
        totalProcessed += batch.length;
        
        logger.info(`Batch ${batchIndex + 1} completed. Total processed: ${totalProcessed}/${documents.length}`);
      }

      logger.info(`Successfully vectorized and stored ${documents.length} document chunks`);
      
      return {
        totalChunks: documents.length,
        batchesProcessed: batches.length,
        success: true
      };
    } catch (error) {
      logger.error('Error adding documents to vector store:', error);
      throw error;
    }
  }

  /**
   * Search documents with detailed scoring
   */
  async searchDocuments(query, k = 5) {
    try {
      if (!this.initialized) {
        await this.initialize();
      }

      // Perform similarity search with scores
      const results = await this.vectorStore.similaritySearchWithScore(query, k);
      
      return results.map(([doc, score]) => ({
        document: doc,
        score: score,
        relevance: score > this.SIMILARITY_THRESHOLD ? 'High' : 'Low',
        metadata: doc.metadata
      }));
    } catch (error) {
      logger.error('Error searching documents:', error);
      throw error;
    }
  }

  /**
   * Get detailed system statistics
   */
  async getSystemStats() {
    try {
      const stats = {
        activeConversations: this.conversations.size,
        vectorDatabase: {
          connected: false,
          collections: 0,
          documents: 0
        },
        llmModel: {
          connected: false,
          model: this.llm?.model || 'unknown'
        },
        configuration: {
          similarityThreshold: this.SIMILARITY_THRESHOLD,
          retrievalK: parseInt(process.env.RETRIEVAL_K) || 4,
          chunkSize: parseInt(process.env.CHUNK_SIZE) || 1000,
          embeddingModel: process.env.EMBEDDING_MODEL || 'nomic-embed-text'
        }
      };

      // Test vector database connection
      try {
        const testResults = await this.vectorStore.similaritySearch('test', 1);
        stats.vectorDatabase.connected = true;
        // Note: ChromaDB doesn't directly expose collection stats via LangChain
      } catch (error) {
        logger.warn('Vector database connection test failed:', error.message);
      }

      // Test LLM connection
      try {
        await this.llm.invoke('test');
        stats.llmModel.connected = true;
      } catch (error) {
        logger.warn('LLM connection test failed:', error.message);
      }

      return stats;
    } catch (error) {
      logger.error('Error getting system stats:', error);
      throw error;
    }
  }

  cleanupOldConversations() {
    const maxAge = parseInt(process.env.SESSION_MAX_AGE_HOURS) * 60 * 60 * 1000 || 24 * 60 * 60 * 1000;
    const now = new Date();
    
    for (const [sessionId, conversation] of this.conversations.entries()) {
      if (now - conversation.lastAccessed > maxAge) {
        this.conversations.delete(sessionId);
        logger.info(`Cleaned up expired conversation for session: ${sessionId}`);
      }
    }
  }
}

// Create singleton instance
const enhancedRAGChatSystem = new EnhancedRAGChatSystem();

module.exports = {
  enhancedRAGChatSystem,
  EnhancedRAGChatSystem,
};
