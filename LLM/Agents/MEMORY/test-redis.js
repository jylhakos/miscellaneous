// test-redis.js - Test Redis connection

const { MemoryStore } = require('./src/memory');

async function testRedisConnection() {
    console.log(' Testing Redis Connection...\n');
    
    const memory = new MemoryStore(true); // Enable Redis
    
    try {
        // Test basic operations
        console.log('1. Setting a test value...');
        await memory.setMemory('test:key', 'Hello Redis!');
        
        console.log('2. Getting the test value...');
        const value = await memory.getMemory('test:key');
        console.log(`   Retrieved: ${value}`);
        
        console.log('3. Testing user name storage...');
        await memory.setMemory('user:test123:name', 'Alice');
        const userName = await memory.getMemory('user:test123:name');
        console.log(`   User name: ${userName}`);
        
        console.log('4. Testing conversation history...');
        await memory.addToConversationHistory('test123', 'Hello!', 'Hi there, Alice!');
        await memory.addToConversationHistory('test123', 'How are you?', 'I am doing well, thanks!');
        
        const history = await memory.getConversationHistory('test123');
        console.log(`   History entries: ${history.length}`);
        history.forEach((entry, index) => {
            console.log(`   ${index + 1}. ${entry.message} -> ${entry.response}`);
        });
        
        console.log('\n Redis test completed successfully!');
        
        // Cleanup
        await memory.disconnect();
        
    } catch (error) {
        console.error('❌ Redis test failed:', error.message);
        process.exit(1);
    }
}

testRedisConnection();
