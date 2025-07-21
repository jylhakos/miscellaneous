// tools.js

const axios = require('axios');
require('dotenv').config();

/**
 * Geocode a city name to get latitude and longitude
 * @param {string} city - City name
 * @returns {Object} - Coordinates {latitude, longitude, name}
 */
async function geocodeCity(city) {
    const geocodingUrl = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=1&language=en&format=json`;

    try {
        const response = await axios.get(geocodingUrl);
        const data = response.data;
        
        if (!data.results || data.results.length === 0) {
            throw new Error(`City "${city}" not found`);
        }

        const result = data.results[0];
        return {
            latitude: result.latitude,
            longitude: result.longitude,
            name: result.name,
            country: result.country
        };
    } catch (error) {
        console.error('Error geocoding city:', error.message);
        throw error;
    }
}

/**
 * Fetch weather data using Open-Meteo API
 * @param {string} city - City name
 * @returns {Object} - Weather data
 */
async function fetchWeather(city) {
    try {
        // First, geocode the city to get coordinates
        const location = await geocodeCity(city);
        
        // Then fetch weather data using coordinates
        const weatherUrl = `https://api.open-meteo.com/v1/forecast?latitude=${location.latitude}&longitude=${location.longitude}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,windspeed_10m&timezone=auto`;

        const response = await axios.get(weatherUrl);
        const data = response.data;

        // Format the response to be more user-friendly
        return {
            location: {
                name: location.name,
                country: location.country,
                latitude: location.latitude,
                longitude: location.longitude
            },
            current: {
                temperature: data.current_weather.temperature,
                windspeed: data.current_weather.windspeed,
                winddirection: data.current_weather.winddirection,
                weathercode: data.current_weather.weathercode,
                time: data.current_weather.time
            },
            units: data.current_weather_units || {
                temperature: '°C',
                windspeed: 'km/h'
            }
        };
    } catch (error) {
        console.error('Error fetching weather data:', error.message);
        throw error;
    }
}

/**
 * Get weather condition description from weather code
 * @param {number} code - Weather code from Open-Meteo
 * @returns {string} - Weather description
 */
function getWeatherDescription(code) {
    const weatherCodes = {
        0: 'Clear sky',
        1: 'Mainly clear',
        2: 'Partly cloudy',
        3: 'Overcast',
        45: 'Fog',
        48: 'Depositing rime fog',
        51: 'Light drizzle',
        53: 'Moderate drizzle',
        55: 'Dense drizzle',
        56: 'Light freezing drizzle',
        57: 'Dense freezing drizzle',
        61: 'Slight rain',
        63: 'Moderate rain',
        65: 'Heavy rain',
        66: 'Light freezing rain',
        67: 'Heavy freezing rain',
        71: 'Slight snow fall',
        73: 'Moderate snow fall',
        75: 'Heavy snow fall',
        77: 'Snow grains',
        80: 'Slight rain showers',
        81: 'Moderate rain showers',
        82: 'Violent rain showers',
        85: 'Slight snow showers',
        86: 'Heavy snow showers',
        95: 'Thunderstorm',
        96: 'Thunderstorm with slight hail',
        99: 'Thunderstorm with heavy hail'
    };
    
    return weatherCodes[code] || 'Unknown weather condition';
}

module.exports = {
    fetchWeather,
    geocodeCity,
    getWeatherDescription
};