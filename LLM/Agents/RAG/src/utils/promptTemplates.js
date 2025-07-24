// src/utils/promptTemplates.js
// Prompt templates for different LLM models

/**
 * Meta Llama 4 Scout prompt template
 * Based on: https://www.llama.com/docs/model-cards-and-prompt-formats/llama4/
 */
const createLlama4ScoutPrompt = (context, question, chatHistory = []) => {
  let prompt = '<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n';
  
  prompt += `You are a helpful AI assistant with access to a knowledge base. Use the provided context to answer questions accurately and helpfully.

Context from knowledge base:
${context}

Instructions:
- Answer based on the provided context when relevant
- If the context doesn't contain relevant information, say so clearly
- Be concise but comprehensive
- Maintain conversation context from previous messages
- Use a friendly, professional tone

<|eot_id|>`;

  // Add chat history
  if (chatHistory && chatHistory.length > 0) {
    for (const message of chatHistory) {
      if (message.type === 'human') {
        prompt += `<|start_header_id|>user<|end_header_id|>\n\n${message.content}<|eot_id|>`;
      } else if (message.type === 'ai') {
        prompt += `<|start_header_id|>assistant<|end_header_id|>\n\n${message.content}<|eot_id|>`;
      }
    }
  }

  // Add current question
  prompt += `<|start_header_id|>user<|end_header_id|>\n\n${question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n`;

  return prompt;
};

/**
 * Generic Llama 3.1 prompt template
 */
const createLlama31Prompt = (context, question, chatHistory = []) => {
  let prompt = '<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n';
  
  prompt += `You are a helpful AI assistant with access to a knowledge base.

Context: ${context}

Answer the user's question based on the provided context. If the context doesn't contain relevant information, say so clearly.<|eot_id|>`;

  // Add chat history
  if (chatHistory && chatHistory.length > 0) {
    for (const message of chatHistory) {
      if (message.type === 'human') {
        prompt += `<|start_header_id|>user<|end_header_id|>\n\n${message.content}<|eot_id|>`;
      } else if (message.type === 'ai') {
        prompt += `<|start_header_id|>assistant<|end_header_id|>\n\n${message.content}<|eot_id|>`;
      }
    }
  }

  prompt += `<|start_header_id|>user<|end_header_id|>\n\n${question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n`;

  return prompt;
};

/**
 * Get appropriate prompt template based on model
 */
const getPromptTemplate = (modelName, context, question, chatHistory = []) => {
  const model = modelName.toLowerCase();
  
  if (model.includes('llama4-scout') || model.includes('llama4_scout')) {
    return createLlama4ScoutPrompt(context, question, chatHistory);
  } else if (model.includes('llama3.1') || model.includes('llama3_1')) {
    return createLlama31Prompt(context, question, chatHistory);
  } else {
    // Default template for other models
    return `Context: ${context}\n\nQuestion: ${question}\n\nAnswer:`;
  }
};

module.exports = {
  createLlama4ScoutPrompt,
  createLlama31Prompt,
  getPromptTemplate,
};
