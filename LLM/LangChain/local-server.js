// local-server.js
// Local development server for testing Lambda functions

const express = require('express');
const cors = require('cors');
const { transformText, healthCheck } = require('./lambda/handler');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Mock AWS Lambda context for local testing
const createMockContext = () => ({
  awsRequestId: `local-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
  functionName: 'langchain-text-transformer-dev-transformText',
  getRemainingTimeInMillis: () => 30000,
  callbackWaitsForEmptyEventLoop: false
});

// Mock API Gateway event structure
const createMockEvent = (method, path, body, headers = {}) => ({
  httpMethod: method,
  path,
  headers: {
    'Content-Type': 'application/json',
    ...headers
  },
  body: body ? JSON.stringify(body) : null,
  queryStringParameters: null,
  pathParameters: null,
  requestContext: {
    requestId: `local-${Date.now()}`,
    stage: 'local',
    httpMethod: method,
    path
  }
});

// Routes
app.post('/transform', async (req, res) => {
  try {
    const event = createMockEvent('POST', '/transform', req.body);
    const context = createMockContext();
    
    const result = await transformText(event, context);
    
    res.status(result.statusCode)
       .set(result.headers)
       .send(result.body);
  } catch (error) {
    console.error('Error in /transform:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/health', async (req, res) => {
  try {
    const event = createMockEvent('GET', '/health');
    const context = createMockContext();
    
    const result = await healthCheck(event, context);
    
    res.status(result.statusCode)
       .set(result.headers)
       .send(result.body);
  } catch (error) {
    console.error('Error in /health:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    message: 'LangChain Text Transformer API - Local Development Server',
    endpoints: {
      'POST /transform': 'Transform text to uppercase',
      'GET /health': 'Health check'
    },
    timestamp: new Date().toISOString()
  });
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Unhandled error:', error);
  res.status(500).json({
    error: 'Internal server error',
    message: error.message
  });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Not found',
    message: `Endpoint ${req.method} ${req.originalUrl} not found`
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 LangChain Local Server running on http://localhost:${PORT}`);
  console.log('📝 Available endpoints:');
  console.log(`  GET  http://localhost:${PORT}/health`);
  console.log(`  POST http://localhost:${PORT}/transform`);
  console.log('');
  console.log('📋 Example usage:');
  console.log(`  curl -X POST http://localhost:${PORT}/transform \\`);
  console.log(`    -H 'Content-Type: application/json' \\`);
  console.log(`    -d '{"text": "hello world"}'`);
});

module.exports = app;
