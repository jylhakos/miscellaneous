// src/handlers/documentHandler.js
const fs = require('fs').promises;
const path = require('path');
const pdfParse = require('pdf-parse');
const { TextLoader } = require('langchain/document_loaders/fs/text');
const { PDFLoader } = require('langchain/document_loaders/fs/pdf');
const { RecursiveCharacterTextSplitter } = require('langchain/text_splitter');
const { enhancedRAGChatSystem } = require('../rag-enhanced');
const logger = require('../utils/logger');
const { v4: uuidv4 } = require('uuid');

class DocumentHandler {
  constructor() {
    this.textSplitter = new RecursiveCharacterTextSplitter({
      chunkSize: parseInt(process.env.CHUNK_SIZE) || 1000,
      chunkOverlap: parseInt(process.env.CHUNK_OVERLAP) || 200,
    });
  }

  async upload(req, res) {
    try {
      if (!req.file) {
        return res.status(400).json({
          success: false,
          error: 'No file uploaded',
          timestamp: new Date().toISOString(),
        });
      }

      const { originalname, filename, path: filePath, mimetype, size } = req.file;
      const documentId = uuidv4();

      logger.info(`Processing uploaded document: ${originalname} (${size} bytes)`);

      // Load and process the document
      let documents;
      const fileExtension = path.extname(originalname).toLowerCase();

      switch (fileExtension) {
        case '.txt':
        case '.md':
          const textLoader = new TextLoader(filePath);
          documents = await textLoader.load();
          break;
        
        case '.pdf':
          const pdfLoader = new PDFLoader(filePath);
          documents = await pdfLoader.load();
          break;
        
        default:
          // For other text files, try to read as text
          const content = await fs.readFile(filePath, 'utf-8');
          documents = [{
            pageContent: content,
            metadata: {
              source: originalname,
              type: fileExtension,
            },
          }];
      }

      // Split documents into chunks
      const chunks = await this.textSplitter.splitDocuments(documents);

      // Add metadata to chunks
      const chunksWithMetadata = chunks.map((chunk, index) => ({
        ...chunk,
        metadata: {
          ...chunk.metadata,
          documentId,
          originalName: originalname,
          uploadDate: new Date().toISOString(),
          chunkIndex: index,
          totalChunks: chunks.length,
        },
      }));

      // Add to vector store
      await enhancedRAGChatSystem.addDocuments(chunksWithMetadata);

      // Clean up uploaded file
      await fs.unlink(filePath);

      logger.info(`Successfully processed document ${originalname} into ${chunks.length} chunks`);

      res.json({
        success: true,
        data: {
          documentId,
          originalName: originalname,
          chunksCreated: chunks.length,
          totalSize: size,
          uploadDate: new Date().toISOString(),
        },
      });

    } catch (error) {
      logger.error('Document upload error:', error);

      // Clean up file on error
      if (req.file && req.file.path) {
        try {
          await fs.unlink(req.file.path);
        } catch (cleanupError) {
          logger.error('Error cleaning up file:', cleanupError);
        }
      }

      res.status(500).json({
        success: false,
        error: 'Failed to process uploaded document',
        message: error.message,
        timestamp: new Date().toISOString(),
      });
    }
  }

  async list(req, res) {
    try {
      // This is a simplified version - in a real implementation,
      // you'd want to store document metadata in a database
      const stats = enhancedRAGChatSystem.getConversationStats();
      
      res.json({
        success: true,
        data: {
          message: 'Document listing not fully implemented - using conversation stats',
          conversationStats: stats,
          timestamp: new Date().toISOString(),
        },
      });

    } catch (error) {
      logger.error('Document list error:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to list documents',
        message: error.message,
        timestamp: new Date().toISOString(),
      });
    }
  }

  async delete(req, res) {
    try {
      const { id } = req.params;

      if (!id) {
        return res.status(400).json({
          success: false,
          error: 'Document ID is required',
          timestamp: new Date().toISOString(),
        });
      }

      // This would require implementing document deletion in ChromaDB
      // For now, return a placeholder response
      res.json({
        success: true,
        data: {
          message: 'Document deletion not fully implemented',
          documentId: id,
          timestamp: new Date().toISOString(),
        },
      });

    } catch (error) {
      logger.error('Document delete error:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to delete document',
        message: error.message,
        timestamp: new Date().toISOString(),
      });
    }
  }
}

const documentHandler = new DocumentHandler();

module.exports = { documentHandler };
