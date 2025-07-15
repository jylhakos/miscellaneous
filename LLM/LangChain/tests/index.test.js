// tests/index.test.js
// Test cases to validate the LangChain.js application

const { UppercaseChain } = require('../src/index.js');

describe('UppercaseChain', () => {
  let chain;

  beforeEach(() => {
    chain = new UppercaseChain();
  });

  test('should be properly instantiated', () => {
    expect(chain).toBeInstanceOf(UppercaseChain);
    expect(chain.inputKeys).toEqual(['text']);
    expect(chain.outputKeys).toEqual(['uppercaseText']);
  });

  test('should convert text to uppercase', async () => {
    const input = { text: 'hello world' };
    const result = await chain.call(input);
    
    expect(result).toHaveProperty('uppercaseText');
    expect(result.uppercaseText).toBe('HELLO WORLD');
  });

  test('should handle empty string', async () => {
    const input = { text: '' };
    const result = await chain.call(input);
    
    expect(result).toHaveProperty('uppercaseText');
    expect(result.uppercaseText).toBe('');
  });

  test('should handle special characters and numbers', async () => {
    const input = { text: 'hello world! 123 @#$' };
    const result = await chain.call(input);
    
    expect(result).toHaveProperty('uppercaseText');
    expect(result.uppercaseText).toBe('HELLO WORLD! 123 @#$');
  });

  test('should throw error for non-string input', async () => {
    const input = { text: 123 };
    
    await expect(chain.call(input)).rejects.toThrow('Input must be a string');
  });

  test('should throw error for null input', async () => {
    const input = { text: null };
    
    await expect(chain.call(input)).rejects.toThrow('Input must be a string');
  });

  test('should throw error for undefined input', async () => {
    const input = { text: undefined };
    
    await expect(chain.call(input)).rejects.toThrow('Input must be a string');
  });

  test('should have correct chain type', () => {
    expect(chain._chainType()).toBe('uppercase_chain');
  });
});

describe('LangChain.js Integration', () => {
  test('should properly import and execute LangChain functionality', async () => {
    const chain = new UppercaseChain();
    const testInput = { text: 'langchain integration test' };
    
    const result = await chain.call(testInput);
    
    expect(result).toBeDefined();
    expect(result.uppercaseText).toBe('LANGCHAIN INTEGRATION TEST');
  });

  test('should validate asynchronous processing', async () => {
    const chain = new UppercaseChain();
    const promises = [
      chain.call({ text: 'test 1' }),
      chain.call({ text: 'test 2' }),
      chain.call({ text: 'test 3' })
    ];
    
    const results = await Promise.all(promises);
    
    expect(results).toHaveLength(3);
    expect(results[0].uppercaseText).toBe('TEST 1');
    expect(results[1].uppercaseText).toBe('TEST 2');
    expect(results[2].uppercaseText).toBe('TEST 3');
  });
});
