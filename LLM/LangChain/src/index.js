// src/index.js
// The index.js file serves as the entry point for the Langchain application.

const { BaseChain } = require('langchain/chains');

// A chain that transforms text to uppercase

class UppercaseChain extends BaseChain {
  async _call(inputs) {
    const text = inputs.text;
    if (typeof text !== 'string') {
      throw new Error('Input must be a string');
    }
    return { uppercaseText: text.toUpperCase() };
  }

  get inputKeys() {
    return ['text'];
  }

  get outputKeys() {
    return ['uppercaseText'];
  }

  _chainType() {
    return 'uppercase_chain';
  }
}

(async () => {
  const chain = new UppercaseChain();
  const input = { text: 'Hello World' };
  
  try {
    const result = await chain.call(input);
    console.log(result); // { uppercaseText: 'HELLO WORLD' }
  } catch (error) {
    console.error('Error:', error.message);
  }
})();
module.exports = { UppercaseChain };
