// src/handlers/chatHandler.js
const { enhancedRAGChatSystem } = require('../rag-enhanced');
const { v4: uuidv4 } = require('uuid');
const logger = require('../utils/logger');

const chatHandler = async (req, res) => {
  try {
    const { message, sessionId } = req.body;

    if (!message || typeof message !== 'string' || message.trim().length === 0) {
      return res.status(400).json({
        error: 'Message is required and cannot be empty',
        timestamp: new Date().toISOString(),
      });
    }

    // Generate session ID if not provided
    const activeSessionId = sessionId || uuidv4();

    logger.info(`Received chat request for session: ${activeSessionId}`);

    // Process the query through Enhanced RAG system
    const response = await enhancedRAGChatSystem.processQuery(message, activeSessionId);

    res.json({
      success: true,
      data: response,
    });

  } catch (error) {
    logger.error('Chat handler error:', error);

    // If the error is already a formatted response from RAG system
    if (error.answer && error.sessionId) {
      return res.status(500).json({
        success: false,
        data: error,
      });
    }

    // Generic error response
    res.status(500).json({
      success: false,
      error: 'Internal server error while processing chat request',
      message: error.message,
      timestamp: new Date().toISOString(),
    });
  }
};

module.exports = { chatHandler };
