const { fetchWeather, getWeatherDescription } = require('./src/tools');

async function testWeatherAPI() {
    try {
        console.log('Testing weather API...');
        const weatherData = await fetchWeather('London');
        console.log('Weather data for London:');
        console.log(JSON.stringify(weatherData, null, 2));
        
        const description = getWeatherDescription(weatherData.current.weathercode);
        console.log(`Weather description: ${description}`);
        
        console.log('Weather API test completed successfully!');
    } catch (error) {
        console.error('Weather API test failed:', error.message);
    }
}

testWeatherAPI();
