// src/handlers/vectorizationHandler.js
// Detailed API for vectorization and document processing insights

const { ragChatSystem } = require('../rag');
const { enhancedRAGChatSystem } = require('../rag-enhanced');
const logger = require('../utils/logger');

class VectorizationHandler {

  /**
   * GET /api/vectorization/stats
   * Get detailed statistics about the vectorization process
   */
  async getStats(req, res) {
    try {
      const stats = await enhancedRAGChatSystem.getSystemStats();
      
      res.json({
        success: true,
        data: {
          ...stats,
          timestamp: new Date().toISOString(),
        }
      });
    } catch (error) {
      logger.error('Error getting vectorization stats:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to get vectorization statistics',
        message: error.message,
        timestamp: new Date().toISOString(),
      });
    }
  }

  /**
   * POST /api/vectorization/search
   * Search the vector database with detailed scoring
   */
  async searchVectors(req, res) {
    try {
      const { query, k = 5, includeScores = true } = req.body;

      if (!query || typeof query !== 'string' || query.trim().length === 0) {
        return res.status(400).json({
          success: false,
          error: 'Query is required and cannot be empty',
          timestamp: new Date().toISOString(),
        });
      }

      logger.info(`Vector search request: "${query}" (k=${k})`);

      const results = await enhancedRAGChatSystem.searchDocuments(query, k);

      res.json({
        success: true,
        data: {
          query,
          results: results.map(result => ({
            content: result.document.pageContent,
            score: includeScores ? result.score : undefined,
            relevance: result.relevance,
            metadata: result.metadata,
          })),
          totalResults: results.length,
          searchParams: { k, includeScores },
          timestamp: new Date().toISOString(),
        }
      });

    } catch (error) {
      logger.error('Error in vector search:', error);
      res.status(500).json({
        success: false,
        error: 'Vector search failed',
        message: error.message,
        timestamp: new Date().toISOString(),
      });
    }
  }

  /**
   * POST /api/vectorization/analyze-query
   * Analyze how a query would be processed (RAG vs Pure LLM)
   */
  async analyzeQuery(req, res) {
    try {
      const { query } = req.body;

      if (!query || typeof query !== 'string' || query.trim().length === 0) {
        return res.status(400).json({
          success: false,
          error: 'Query is required and cannot be empty',
          timestamp: new Date().toISOString(),
        });
      }

      logger.info(`Query analysis request: "${query}"`);

      // Get classification without processing the full query
      const classification = await enhancedRAGChatSystem.classifyQuery(query);
      
      // Get similarity scores for top documents
      let similarityResults = [];
      try {
        similarityResults = await enhancedRAGChatSystem.searchDocuments(query, 3);
      } catch (error) {
        logger.warn('Could not get similarity results:', error.message);
      }

      res.json({
        success: true,
        data: {
          query,
          classification: {
            strategy: classification.useRAG ? 'RAG (Retrieval-Augmented Generation)' : 'Pure LLM',
            reasoning: classification.reasoning,
            confidence: classification.confidence,
            useRAG: classification.useRAG
          },
          similarityAnalysis: {
            topDocuments: similarityResults.slice(0, 3).map(result => ({
              score: result.score,
              relevance: result.relevance,
              preview: result.document.pageContent.substring(0, 150) + '...',
              source: result.metadata?.originalName || 'Unknown'
            })),
            threshold: enhancedRAGChatSystem.SIMILARITY_THRESHOLD,
            wouldRetrieve: similarityResults.some(r => r.score > enhancedRAGChatSystem.SIMILARITY_THRESHOLD)
          },
          recommendation: this.getProcessingRecommendation(classification, similarityResults),
          timestamp: new Date().toISOString(),
        }
      });

    } catch (error) {
      logger.error('Error in query analysis:', error);
      res.status(500).json({
        success: false,
        error: 'Query analysis failed',
        message: error.message,
        timestamp: new Date().toISOString(),
      });
    }
  }

  /**
   * GET /api/vectorization/embeddings-info
   * Get information about the embedding model and process
   */
  async getEmbeddingsInfo(req, res) {
    try {
      const embeddingModel = process.env.EMBEDDING_MODEL || 'nomic-embed-text';
      const ollamaUrl = process.env.OLLAMA_BASE_URL || 'http://localhost:11434';

      // Test embedding generation
      let testEmbedding = null;
      let embeddingDimensions = null;
      let embeddingTime = null;

      try {
        const startTime = Date.now();
        const testResult = await enhancedRAGChatSystem.embeddings.embedQuery('test embedding');
        embeddingTime = Date.now() - startTime;
        embeddingDimensions = testResult.length;
        testEmbedding = testResult.slice(0, 5); // First 5 dimensions as example
      } catch (error) {
        logger.warn('Could not test embedding generation:', error.message);
      }

      res.json({
        success: true,
        data: {
          embeddingModel: {
            name: embeddingModel,
            provider: 'Ollama',
            baseUrl: ollamaUrl,
            dimensions: embeddingDimensions,
            testProcessingTime: embeddingTime ? `${embeddingTime}ms` : 'N/A'
          },
          testEmbedding: {
            input: 'test embedding',
            outputSample: testEmbedding,
            note: 'Showing first 5 dimensions only'
          },
          vectorizationProcess: {
            steps: [
              '1. Document uploaded via API',
              '2. Text extracted and cleaned',
              '3. Split into chunks (1000 chars, 200 overlap)',
              '4. Each chunk sent to embedding model',
              '5. Vector embeddings generated',
              '6. Stored in ChromaDB with metadata',
              '7. Indexed for similarity search'
            ],
            chunkSize: parseInt(process.env.CHUNK_SIZE) || 1000,
            chunkOverlap: parseInt(process.env.CHUNK_OVERLAP) || 200,
            batchSize: parseInt(process.env.EMBEDDING_BATCH_SIZE) || 10
          },
          timestamp: new Date().toISOString(),
        }
      });

    } catch (error) {
      logger.error('Error getting embeddings info:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to get embeddings information',
        message: error.message,
        timestamp: new Date().toISOString(),
      });
    }
  }

  /**
   * POST /api/vectorization/process-text
   * Process raw text and show the chunking and vectorization steps
   */
  async processText(req, res) {
    try {
      const { text, preview = true } = req.body;

      if (!text || typeof text !== 'string' || text.trim().length === 0) {
        return res.status(400).json({
          success: false,
          error: 'Text is required and cannot be empty',
          timestamp: new Date().toISOString(),
        });
      }

      // Import text splitter
      const { RecursiveCharacterTextSplitter } = require('langchain/text_splitter');
      
      const textSplitter = new RecursiveCharacterTextSplitter({
        chunkSize: parseInt(process.env.CHUNK_SIZE) || 1000,
        chunkOverlap: parseInt(process.env.CHUNK_OVERLAP) || 200,
      });

      // Split text into chunks
      const chunks = await textSplitter.splitText(text);
      
      let embeddings = [];
      let processingTime = null;

      if (!preview) {
        // Generate embeddings for all chunks
        const startTime = Date.now();
        embeddings = await Promise.all(
          chunks.map(chunk => enhancedRAGChatSystem.embeddings.embedQuery(chunk))
        );
        processingTime = Date.now() - startTime;
      }

      res.json({
        success: true,
        data: {
          originalText: {
            length: text.length,
            preview: text.substring(0, 200) + (text.length > 200 ? '...' : '')
          },
          chunks: {
            count: chunks.length,
            details: chunks.map((chunk, index) => ({
              index,
              length: chunk.length,
              preview: chunk.substring(0, 100) + (chunk.length > 100 ? '...' : ''),
              fullText: preview ? undefined : chunk
            }))
          },
          embeddings: preview ? {
            note: 'Set preview=false to generate actual embeddings',
            wouldGenerate: chunks.length + ' embedding vectors'
          } : {
            count: embeddings.length,
            dimensions: embeddings[0]?.length || 0,
            processingTime: processingTime + 'ms',
            samples: embeddings.slice(0, 2).map((emb, idx) => ({
              chunkIndex: idx,
              vectorSample: emb.slice(0, 5), // First 5 dimensions
              vectorLength: emb.length
            }))
          },
          metadata: {
            chunkSize: parseInt(process.env.CHUNK_SIZE) || 1000,
            chunkOverlap: parseInt(process.env.CHUNK_OVERLAP) || 200,
            embeddingModel: process.env.EMBEDDING_MODEL || 'nomic-embed-text'
          },
          timestamp: new Date().toISOString(),
        }
      });

    } catch (error) {
      logger.error('Error processing text:', error);
      res.status(500).json({
        success: false,
        error: 'Text processing failed',
        message: error.message,
        timestamp: new Date().toISOString(),
      });
    }
  }

  /**
   * Helper method to provide processing recommendations
   */
  getProcessingRecommendation(classification, similarityResults) {
    if (classification.useRAG && similarityResults.length > 0) {
      const maxScore = Math.max(...similarityResults.map(r => r.score));
      if (maxScore > 0.8) {
        return 'Excellent match found in knowledge base. RAG will provide highly relevant context.';
      } else if (maxScore > 0.6) {
        return 'Good match found in knowledge base. RAG will provide relevant context.';
      } else {
        return 'Moderate match found. RAG may provide some relevant context.';
      }
    } else if (!classification.useRAG) {
      return `Pure LLM mode recommended: ${classification.reasoning}`;
    } else {
      return 'No relevant documents found. Consider using pure LLM mode or adding more documents to the knowledge base.';
    }
  }
}

const vectorizationHandler = new VectorizationHandler();

module.exports = { vectorizationHandler };
