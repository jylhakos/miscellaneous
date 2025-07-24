// src/server.js
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
require('dotenv').config();

const { chatHandler } = require('./handlers/chatHandler');
const { documentHandler } = require('./handlers/documentHandler');
const { healthHandler } = require('./handlers/healthHandler');
const { vectorizationHandler } = require('./handlers/vectorizationHandler');
const logger = require('./utils/logger');
const { errorHandler } = require('./middleware/errorHandler');
const { rateLimiter } = require('./middleware/rateLimiter');

const app = express();
const PORT = process.env.PORT || 3000;

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000', 'http://localhost:8080'],
  credentials: true
}));

// Rate limiting
app.use('/api', rateLimiter);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// File upload configuration
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = path.join(__dirname, '../uploads');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage: storage,
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['.txt', '.pdf', '.md', '.doc', '.docx'];
    const fileExt = path.extname(file.originalname).toLowerCase();
    if (allowedTypes.includes(fileExt)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only txt, pdf, md, doc, docx files are allowed.'));
    }
  }
});

// API Routes
app.get('/api/health', healthHandler);
app.post('/api/chat', chatHandler);
app.post('/api/documents/upload', upload.single('document'), documentHandler.upload);
app.get('/api/documents', documentHandler.list);
app.delete('/api/documents/:id', documentHandler.delete);

// Vectorization API Routes
app.get('/api/vectorization/stats', vectorizationHandler.getStats);
app.post('/api/vectorization/search', vectorizationHandler.searchVectors);
app.post('/api/vectorization/analyze-query', vectorizationHandler.analyzeQuery);
app.get('/api/vectorization/embeddings-info', vectorizationHandler.getEmbeddingsInfo);
app.post('/api/vectorization/process-text', vectorizationHandler.processText);

// Serve static files for simple web interface
app.use(express.static(path.join(__dirname, '../public')));

// Default route
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../public/index.html'));
});

// Error handling middleware (must be last)
app.use(errorHandler);

// Start server
app.listen(PORT, () => {
  logger.info(`RAG Chat Application server running on port ${PORT}`);
  logger.info(`Health check available at: http://localhost:${PORT}/api/health`);
  logger.info(`Chat endpoint available at: http://localhost:${PORT}/api/chat`);
  logger.info(`Document upload endpoint available at: http://localhost:${PORT}/api/documents/upload`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  process.exit(0);
});

module.exports = app;
