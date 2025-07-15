// lambda/handler.js
// AWS Lambda handler for LangChain.js UppercaseChain

const { UppercaseChain } = require('../src/index.js');

// Initialize the chain outside the handler for better performance (reuse across invocations)
const uppercaseChain = new UppercaseChain();

/**
 * AWS Lambda handler function
 * Processes text transformation requests via API Gateway
 */
exports.transformText = async (event, context) => {
  // Set up CORS headers
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
    'Content-Type': 'application/json'
  };

  try {
    // Handle OPTIONS preflight request for CORS
    if (event.httpMethod === 'OPTIONS') {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({ message: 'CORS preflight successful' })
      };
    }

    // Only allow POST requests
    if (event.httpMethod !== 'POST') {
      return {
        statusCode: 405,
        headers,
        body: JSON.stringify({ 
          error: 'Method not allowed',
          message: 'Only POST requests are supported'
        })
      };
    }

    // Parse request body
    let requestBody;
    try {
      requestBody = JSON.parse(event.body || '{}');
    } catch (parseError) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({
          error: 'Invalid JSON',
          message: 'Request body must be valid JSON'
        })
      };
    }

    // Validate input
    const { text } = requestBody;
    if (!text) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({
          error: 'Missing input',
          message: 'Text field is required in request body'
        })
      };
    }

    if (typeof text !== 'string') {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({
          error: 'Invalid input type',
          message: 'Text must be a string'
        })
      };
    }

    // Process the text using LangChain
    console.log(`Processing text: "${text}"`);
    const startTime = Date.now();
    
    const result = await uppercaseChain.call({ text });
    
    const processingTime = Date.now() - startTime;
    console.log(`Text processed in ${processingTime}ms`);

    // Return successful response
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        success: true,
        data: {
          originalText: text,
          transformedText: result.uppercaseText,
          processingTimeMs: processingTime,
          timestamp: new Date().toISOString()
        },
        meta: {
          requestId: context.awsRequestId,
          functionName: context.functionName,
          remainingTimeMs: context.getRemainingTimeInMillis()
        }
      })
    };

  } catch (error) {
    console.error('Error processing request:', error);
    
    // Return error response
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        success: false,
        error: 'Internal server error',
        message: error.message,
        meta: {
          requestId: context.awsRequestId,
          functionName: context.functionName
        }
      })
    };
  }
};

/**
 * Health check endpoint
 */
exports.healthCheck = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json'
  };

  try {
    // Test the chain functionality
    const testResult = await uppercaseChain.call({ text: 'health check' });
    
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        status: 'healthy',
        message: 'LangChain service is operational',
        test: {
          input: 'health check',
          output: testResult.uppercaseText
        },
        timestamp: new Date().toISOString(),
        meta: {
          requestId: context.awsRequestId,
          functionName: context.functionName
        }
      })
    };

  } catch (error) {
    console.error('Health check failed:', error);
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        status: 'unhealthy',
        error: error.message,
        timestamp: new Date().toISOString()
      })
    };
  }
};
