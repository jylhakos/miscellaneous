// session-demo.js - Demonstrate session-based memory management

require('dotenv').config();
const { SessionMemoryStore, SESSION_CONFIG } = require('./src/memory');

async function sessionDemo() {
    console.log('Session Memory Management Demo');
    console.log('=====================================\n');
    
    const memory = new SessionMemoryStore(true);
    
    // Initialize memory
    await memory.initialize();
    
    console.log('   Session Configuration:');
    console.log(`   Session Duration: ${SESSION_CONFIG.SESSION_DURATION}s`);
    console.log(`   Max Conversations per Session: ${SESSION_CONFIG.MAX_CONVERSATIONS_PER_SESSION}`);
    console.log(`   Inactivity Timeout: ${SESSION_CONFIG.INACTIVITY_TIMEOUT}s`);
    console.log(`   Cleanup Interval: ${SESSION_CONFIG.CLEANUP_INTERVAL/1000}s\n`);

    const userId = 'demo_user';
    
    try {
        // Test 1: Create session and add conversations
        console.log('Test 1: Creating session and adding conversations');
        console.log('---------------------------------------------------');
        
        for (let i = 1; i <= 5; i++) {
            const message = `Test message ${i}`;
            const response = `Response to message ${i}`;
            
            await memory.addToConversationHistory(userId, message, response);
            console.log(`Added conversation ${i}`);
            
            // Small delay to see session activity updates
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        // Check session stats
        const stats = await memory.getSessionStats(userId);
        console.log('\n📊 Session Stats:');
        console.log(JSON.stringify(stats, null, 2));
        
        // Test 2: Get conversation history
        console.log('\nTest 2: Retrieving conversation history');
        console.log('--------------------------------------------');
        
        const history = await memory.getConversationHistory(userId);
        console.log(`Retrieved ${history.length} conversations from current session`);
        history.forEach((conv, idx) => {
            console.log(`   ${idx + 1}. ${conv.message} -> ${conv.response}`);
        });
        
        // Test 3: Test session limits
        console.log('\nTest 3: Testing session conversation limits');
        console.log('-----------------------------------------------');
        
        // Add conversations up to the limit
        const currentCount = stats.sessions[0]?.conversationCount || 0;
        const remaining = SESSION_CONFIG.MAX_CONVERSATIONS_PER_SESSION - currentCount;
        
        console.log(`Current conversations: ${currentCount}, Limit: ${SESSION_CONFIG.MAX_CONVERSATIONS_PER_SESSION}`);
        console.log(`Adding ${remaining} more conversations to reach limit...`);
        
        for (let i = currentCount + 1; i <= SESSION_CONFIG.MAX_CONVERSATIONS_PER_SESSION; i++) {
            const message = `Limit test message ${i}`;
            const response = `Limit test response ${i}`;
            
            await memory.addToConversationHistory(userId, message, response);
            console.log(`Added conversation ${i}/${SESSION_CONFIG.MAX_CONVERSATIONS_PER_SESSION}`);
        }
        
        // Try to add one more (should create new session)
        console.log('\nAdding one more conversation (should trigger new session)...');
        await memory.addToConversationHistory(userId, 'This should create a new session', 'New session response');
        
        const updatedStats = await memory.getSessionStats(userId);
        console.log('\n📊 Updated Session Statistics:');
        console.log(JSON.stringify(updatedStats, null, 2));
        
        // Test 4: Memory usage stats
        console.log('\nTest 4: Memory Usage Statistics');
        console.log('------------------------------------');
        
        const memoryStats = await memory.getMemoryStats();
        console.log('Memory Statistics:');
        console.log(JSON.stringify(memoryStats, null, 2));
        
        // Test 5: Manual session cleanup
        console.log('\nTest 5: Manual session cleanup');
        console.log('-----------------------------------');
        
        console.log('Ending all sessions for user...');
        await memory.endUserSession(userId, 'demo_finished');
        
        const finalStats = await memory.getSessionStats(userId);
        console.log('\nFinal Session Statistics:');
        console.log(JSON.stringify(finalStats, null, 2));
        
        // Test 6: Post-cleanup conversation
        console.log('\nTest 6: Starting new conversation after cleanup');
        console.log('---------------------------------------------------');
        
        await memory.addToConversationHistory(userId, 'Hello after cleanup', 'New session started');
        
        const newStats = await memory.getSessionStats(userId);
        console.log('\nNew Session Statistics:');
        console.log(JSON.stringify(newStats, null, 2));
        
        console.log('\nSession demo completed successfully!');
        
    } catch (error) {
        console.error('❌ Demo failed:', error);
    } finally {
        // Cleanup
        await memory.disconnect();
        console.log('\nDisconnected from memory store');
    }
}

// Handle process termination
process.on('SIGINT', async () => {
    console.log('\nDemo interrupted, cleaning up...');
    process.exit(0);
});

process.on('SIGTERM', async () => {
    console.log('\nDemo terminated, cleaning up...');
    process.exit(0);
});

// Run the demo
if (require.main === module) {
    sessionDemo().catch(console.error);
}

module.exports = { sessionDemo };
