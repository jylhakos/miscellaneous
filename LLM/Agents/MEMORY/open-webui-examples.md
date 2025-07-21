# Open WebUI

This file contains example prompts and configurations for testing the LangChain Weather Agent with Open WebUI.

## System Prompt for Open WebUI

```
You are interacting with an intelligent weather assistant powered by LangChain.js. This assistant can:

1. Remember your name and provide personalized responses
2. Fetch real-time weather information for any city worldwide
3. Maintain conversation context across multiple interactions

The assistant uses advanced AI to understand your intent and respond appropriately. You can:
- Introduce yourself: "Hello, my name is [Your Name]"
- Ask for weather: "What's the weather in [City Name]?"
- General greetings: "Hi there!" or "Hello!"

The assistant will remember your name throughout the conversation and provide weather data using real-time APIs.
```

## Conversation Flow

### Initial
```
User: Hello, my name is Sarah
Assistant: Nice to meet you, Sarah! I'm your weather assistant. You can ask me about the weather in any city.

User: What's the weather like in London?
Assistant: Sarah, the weather in London, United Kingdom is currently partly cloudy with a temperature of 18°C. Wind speed is 12 km/h.
```

### Follow-up Interactions
```
User: How about Paris?
Assistant: Sarah, the weather in Paris, France is currently clear sky with a temperature of 22°C. Wind speed is 8 km/h.

User: Hi there!
Assistant: Hello again, Sarah! How can I help you today? You can ask me about the weather in any city.
```

### Default Responses
```
User: What can you do?
Assistant: Sarah, I'm a weather assistant. I can help you with:
- Getting weather information for any city (just ask "What's the weather in [city]?")
- Remembering your name for personalized responses

You can also greet me or introduce yourself. How can I help you today?
```

## API testing with Open WebUI

If you want to integrate directly with the API endpoints, you can use these examples:

### Chat API Integration
```javascript
// Custom function for Open WebUI
async function chatWithWeatherAgent(message, userId = 'openwebui_user') {
    const response = await fetch('http://localhost:3000/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            userId: userId
        })
    });
    
    const data = await response.json();
    return data.response;
}
```

### Using with Open WebUI functions
```python
# Python function for Open WebUI
import requests
import json

def get_weather_response(message: str, user_id: str = "openwebui_user") -> str:
    """
    Get response from LangChain Weather Agent
    """
    url = "http://localhost:3000/chat"
    payload = {
        "message": message,
        "userId": user_id
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "Sorry, I couldn't process your request.")
    except Exception as e:
        return f"Error connecting to weather agent: {str(e)}"

# Example usage in Open WebUI
user_message = "What's the weather in Tokyo?"
agent_response = get_weather_response(user_message)
print(agent_response)
```

## Model Configuration for Open WebUI

When setting up a custom model in Open WebUI that connects to this weather agent:

```yaml
# Model Configuration
name: "Weather Agent"
base_url: "http://localhost:3000"
api_key: "not_required"
model_type: "custom"
description: "LangChain.js Weather Assistant with Memory"

# Custom headers
headers:
  Content-Type: "application/json"
  
# Custom prompt template
prompt_template: |
  User: {prompt}
  Assistant: I'll help you with that weather information.
```

## Scenarios

### Scenario 1: First-time user
```
1. "Hello" → Should ask for name
2. "My name is Alex" → Should remember name
3. "What's the weather in Sydney?" → Should use name in response
4. "Hi!" → Should recognize returning user
```

### Scenario 2: Weather queries
```
1. "Weather in New York?" → Should fetch NYC weather
2. "How about Tokyo?" → Should fetch Tokyo weather  
3. "What about a city that doesn't exist?" → Should handle gracefully
4. "Temperature in London" → Should understand alternate phrasing
```

### Scenario 3: Mixed interactions
```
1. "Hello, I'm John" → Introduction
2. "What can you do?" → Capability explanation
3. "Weather in Paris" → Weather request
4. "Thanks!" → General response
5. "Bye" → Farewell (should remember for next session)
```

## Open WebUI Prompt Engineering

1. **Context Setting**: Start conversations with clear introductions
2. **Error Handling**: The agent handles API failures gracefully
3. **Memory Persistence**: Names and preferences are remembered across sessions
4. **Natural Language**: Use conversational language - the AI understands intent
5. **City Names**: Use common city names - the geocoding API handles most variations

## Advanced

For more complex Open WebUI setups, you can:

1. **Create custom tools** that call the weather API endpoints
2. **Use the conversation history** endpoint to maintain context
3. **Integrate with other Open WebUI models** for enhanced capabilities
4. **Set up webhooks** for real-time notifications

## Troubleshooting Open WebUI

Common issues and solutions:

1. **Connection refused**: Ensure the weather agent is running on port 3000
2. **CORS errors**: The agent includes CORS headers for web integration
3. **Memory not persisting**: Check Redis connection or use the in-memory fallback
4. **OpenAI API errors**: The agent falls back to pattern matching without OpenAI
5. **Weather data unavailable**: The Open-Meteo API is generally reliable and free
