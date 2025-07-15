// example.js
// Example showing how to use the UppercaseChain from index.js

const { UppercaseChain } = require('./src/index.js');

/**
 * Example 1: Basic usage
 */
async function basicExample() {
  console.log('=== Basic Example ===');
  
  const chain = new UppercaseChain();
  const input = { text: 'Hello LangChain.js!' };
  
  try {
    const result = await chain.call(input);
    console.log('Input:', input.text);
    console.log('Output:', result.uppercaseText);
    console.log('');
  } catch (error) {
    console.error('Error:', error.message);
  }
}

/**
 * Example 2: Processing multiple texts
 */
async function multipleTextsExample() {
  console.log('=== Multiple Texts Example ===');
  
  const chain = new UppercaseChain();
  const texts = [
    'artificial intelligence',
    'machine learning',
    'natural language processing',
    'large language models'
  ];
  
  try {
    for (const text of texts) {
      const result = await chain.call({ text });
      console.log(`"${text}" -> "${result.uppercaseText}"`);
    }
    console.log('');
  } catch (error) {
    console.error('Error:', error.message);
  }
}

/**
 * Example 3: Parallel processing
 */
async function parallelProcessingExample() {
  console.log('=== Parallel Processing Example ===');
  
  const chain = new UppercaseChain();
  const inputs = [
    { text: 'concurrent processing' },
    { text: 'async operations' },
    { text: 'promise handling' }
  ];
  
  try {
    const promises = inputs.map(input => chain.call(input));
    const results = await Promise.all(promises);
    
    results.forEach((result, index) => {
      console.log(`Input ${index + 1}: "${inputs[index].text}" -> "${result.uppercaseText}"`);
    });
    console.log('');
  } catch (error) {
    console.error('Error:', error.message);
  }
}

/**
 * Example 4: Error handling
 */
async function errorHandlingExample() {
  console.log('=== Error Handling Example ===');
  
  const chain = new UppercaseChain();
  const invalidInputs = [
    { text: 123 },
    { text: null },
    { text: undefined },
    { text: {} }
  ];
  
  for (const input of invalidInputs) {
    try {
      const result = await chain.call(input);
      console.log('Unexpected success:', result);
    } catch (error) {
      console.log(`Input: ${JSON.stringify(input.text)} -> Error: ${error.message}`);
    }
  }
  console.log('');
}

/**
 * Example 5: Chain properties inspection
 */
function inspectChainExample() {
  console.log('=== Chain Properties Example ===');
  
  const chain = new UppercaseChain();
  
  console.log('Chain Type:', chain._chainType());
  console.log('Input Keys:', chain.inputKeys);
  console.log('Output Keys:', chain.outputKeys);
  console.log('');
}

/**
 * Run all examples
 */
async function runAllExamples() {
  console.log('🚀 LangChain.js UppercaseChain Examples\n');
  
  await basicExample();
  await multipleTextsExample();
  await parallelProcessingExample();
  await errorHandlingExample();
  inspectChainExample();
  
  console.log('✅ All examples completed!');
}

// Run examples if this file is executed directly
if (require.main === module) {
  runAllExamples().catch(console.error);
}

module.exports = {
  basicExample,
  multipleTextsExample,
  parallelProcessingExample,
  errorHandlingExample,
  inspectChainExample,
  runAllExamples
};
