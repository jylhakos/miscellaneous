#  Large Language Models (LLM)

## Arcee Agent

Arcee Agent is a 7B parameter language model specifically designed for function calling and tool use.

## LangChain

What are LangChain chains?

In LangChain, chains are a concept, representing sequences of components or operations that work together to accomplish a larger task.

These LangChain components can include the following.

Prompt templates

Structured inputs for Large Language Models (LLMs).

LLMs

The core language models themselves, performing tasks like text generation or classification.

Parsers

Components that process and format the output of an LLM or another component.

Custom functions

User-defined functions to add specific logic or data processing steps.

How asynchronous chains work with async/await syntax?

Asynchronous programming (or async programming) is a paradigm that allows a program to perform multiple tasks concurrently without blocking the execution of other tasks.

LangChain.js integrates with JavaScript's async/await syntax for handling asynchronous operations. 

```

	// Example using async/await with a chain and streaming output
	import { ChatOpenAI } from "@langchain/openai";
	import { ChatPromptTemplate } from "@langchain/core/prompts";
	import { StringOutputParser } from "@langchain/core/output_parsers";

	const prompt = ChatPromptTemplate.fromTemplate("Tell me a short story about {animal}.");
	const model = new ChatOpenAI({});
	const parser = new StringOutputParser();

	const chain = prompt.pipe(model).pipe(parser);

	async function generateStory(animal) {
	  console.log(`Generating a story about a ${animal}...`);
	  const stream = await chain.stream({ animal });

	  let story = "";
	  for await (const chunk of stream) {
	    story += chunk;
	    // Stream output to the console as it comes
	    process.stdout.write(chunk); 
	  }
	  console.log("\nStory generation complete!");
	  return story;
	}

	generateStory("dragon");

```

## LangGraph

## Ollama

## vLLM
