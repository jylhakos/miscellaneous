// simple-test.js - Basic functionality test

const { MemoryStore } = require('./src/memory');
const { fetchWeather, getWeatherDescription } = require('./src/tools');

async function testBasicFunctionality() {
    console.log(' Testing basic functionality...\n');
    
    // Test memory store
    console.log('1. Testing Memory Store...');
    const memory = new MemoryStore();
    await memory.setMemory('test_user', 'John Doe');
    const retrievedName = await memory.getMemory('test_user');
    console.log(`   Stored and retrieved name: ${retrievedName}`);
    
    // Test weather API
    console.log('\n2. Testing Weather API...');
    try {
        const weatherData = await fetchWeather('London');
        const description = getWeatherDescription(weatherData.current.weathercode);
        console.log(`   London weather: ${description}, ${weatherData.current.temperature}°C`);
        console.log(`   Location: ${weatherData.location.name}, ${weatherData.location.country}`);
    } catch (error) {
        console.log(`   Weather API Error: ${error.message}`);
    }
    
    // Test conversation history
    console.log('\n3. Testing Conversation History...');
    await memory.addToConversationHistory('test_user', 'Hello', 'Hi there!');
    const history = await memory.getConversationHistory('test_user');
    console.log(`   History entries: ${history.length}`);
    
    console.log('\n Basic functionality test completed!');
    
    // Cleanup
    await memory.disconnect();
}

testBasicFunctionality().catch(console.error);
