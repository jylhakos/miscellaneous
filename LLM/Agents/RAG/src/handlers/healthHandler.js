// src/handlers/healthHandler.js
const { enhancedRAGChatSystem } = require('../rag-enhanced');
const logger = require('../utils/logger');

const healthHandler = async (req, res) => {
  try {
    const healthStatus = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      version: process.env.npm_package_version || '1.0.0',
      environment: process.env.NODE_ENV || 'development',
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      services: {
        ragSystem: enhancedRAGChatSystem.initialized,
        ollama: 'unknown',
        chromadb: 'unknown',
      },
    };

    // Try to get conversation stats if RAG system is initialized
    if (enhancedRAGChatSystem.initialized) {
      try {
        healthStatus.conversationStats = enhancedRAGChatSystem.getConversationStats();
      } catch (error) {
        logger.warn('Could not get conversation stats:', error.message);
      }
    }

    // Test Ollama connection
    try {
      if (enhancedRAGChatSystem.llm) {
        // Simple test query to check if Ollama is responding
        await enhancedRAGChatSystem.llm.invoke('test');
        healthStatus.services.ollama = 'healthy';
      }
    } catch (error) {
      healthStatus.services.ollama = 'unhealthy';
      logger.warn('Ollama health check failed:', error.message);
    }

    // Test ChromaDB connection
    try {
      if (enhancedRAGChatSystem.vectorStore) {
        // Simple search to test ChromaDB
        await enhancedRAGChatSystem.searchDocuments('test', 1);
        healthStatus.services.chromadb = 'healthy';
      }
    } catch (error) {
      healthStatus.services.chromadb = 'unhealthy';
      logger.warn('ChromaDB health check failed:', error.message);
    }

    // Determine overall health
    const unhealthyServices = Object.values(healthStatus.services).filter(
      status => status === 'unhealthy'
    );
    
    if (unhealthyServices.length > 0) {
      healthStatus.status = 'degraded';
    }

    const statusCode = healthStatus.status === 'healthy' ? 200 : 503;
    res.status(statusCode).json(healthStatus);

  } catch (error) {
    logger.error('Health check error:', error);
    res.status(503).json({
      status: 'unhealthy',
      error: error.message,
      timestamp: new Date().toISOString(),
    });
  }
};

module.exports = { healthHandler };
