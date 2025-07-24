// index.js - Entry point for the RAG Chat Application
// For production, use src/server.js instead

const { ragChatSystem } = require('./src/rag');

async function main() {
    try {
        console.log('🚀 Starting RAG Chat Application...');
        
        // Initialize the RAG system
        await ragChatSystem.initialize();
        
        // Example usage
        const question = "What is machine learning and how does it work?";
        console.log(`\nQuestion: ${question}`);
        
        const response = await ragChatSystem.processQuery(question);
        console.log(`\nAnswer: ${response.answer}`);
        
        if (response.sources && response.sources.length > 0) {
            console.log('\nSources:');
            response.sources.forEach((source, index) => {
                console.log(`${index + 1}. ${source.content}`);
            });
        }
        
        console.log('\n✅ RAG system test completed successfully!');
        console.log('\n💡 To run the full web server, use: npm start');
        console.log('   Or with Docker: docker-compose up -d');
        
    } catch (error) {
        console.error('❌ Error:', error.message);
        console.log('\n🔧 Troubleshooting:');
        console.log('1. Make sure Ollama is running: docker-compose up -d ollama');
        console.log('2. Make sure ChromaDB is running: docker-compose up -d chromadb');
        console.log('3. Check if models are downloaded: docker-compose exec ollama ollama list');
        console.log('4. See README.md for detailed setup instructions');
    }
}

// Only run if this file is executed directly
if (require.main === module) {
    main();
}

module.exports = { ragChatSystem };