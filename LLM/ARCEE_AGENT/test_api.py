#!/usr/bin/env python3
"""
API Testing Script for Arcee Agent

This script provides comprehensive testing for various API endpoints
and deployment configurations of the Arcee Agent model.

Usage:
    python test_api.py --base_url http://127.0.0.1:11434/v1
"""

import requests
import json
import time
import argparse
import sys
from openai import OpenAI

def test_health_endpoint(base_url):
    """Test health endpoint."""
    print("🔍 Testing health endpoint...")
    
    try:
        # Remove /v1 from base_url for health check
        health_url = base_url.replace('/v1', '') + '/health'
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"⚠️  Health check returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_models_endpoint(client):
    """Test models listing endpoint."""
    print("🔍 Testing models endpoint...")
    
    try:
        models = client.models.list()
        print("✅ Models endpoint working")
        print(f"Available models: {len(models.data)}")
        for model in models.data:
            print(f"  - {model.id}")
        return True
    except Exception as e:
        print(f"❌ Models endpoint failed: {e}")
        return False

def test_simple_completion(client, model_name):
    """Test simple completion."""
    print("🔍 Testing simple completion...")
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "Hello! Can you help me with function calling?"}
            ],
            max_tokens=100,
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        print("✅ Simple completion working")
        print(f"Response: {content[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Simple completion failed: {e}")
        return False

def test_function_calling(client, model_name):
    """Test function calling capability."""
    print("🔍 Testing function calling...")
    
    tools = [
        {
            "name": "get_weather",
            "description": "Get current weather for a location",
            "parameters": {
                "location": {
                    "type": "string",
                    "description": "City name"
                }
            }
        }
    ]
    
    tools_str = json.dumps(tools, indent=2)
    prompt = f"""You are an AI assistant with access to the following tools:

{tools_str}

Based on the user's query, determine which tool(s) to call and with what arguments.
Your response should be a JSON array of tool calls in the format:
[{{"name": "tool_name", "arguments": {{"param": "value"}}}}]

User Query: What's the weather like in New York?

Tool Calls:"""
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant that excels at function calling. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=256,
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        print("✅ Function calling test completed")
        print(f"Response: {content}")
        
        # Try to parse the response as JSON
        try:
            # Look for JSON in the response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = content[start_idx:end_idx]
                tool_calls = json.loads(json_str)
                print("✅ Successfully parsed tool calls:")
                print(json.dumps(tool_calls, indent=2))
                return True
            else:
                print("⚠️  No JSON array found in response")
                return False
        except json.JSONDecodeError as e:
            print(f"⚠️  Could not parse response as JSON: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Function calling test failed: {e}")
        return False

def test_dataset_example(client, model_name):
    """Test with actual dataset example."""
    print("🔍 Testing with dataset example...")
    
    # Use actual data from our dataset
    query = "Where can I find live giveaways for beta access and games?"
    tools = [
        {
            "name": "live_giveaways_by_type",
            "description": "Retrieve live giveaways from the GamerPower API based on the specified type.",
            "parameters": {
                "type": {
                    "description": "The type of giveaways to retrieve (e.g., game, loot, beta).",
                    "type": "str",
                    "default": "game"
                }
            }
        }
    ]
    
    tools_str = json.dumps(tools, indent=2)
    prompt = f"""You are an AI assistant with access to the following tools:

{tools_str}

Based on the user's query, determine which tool(s) to call and with what arguments.
Your response should be a JSON array of tool calls in the format:
[{{"name": "tool_name", "arguments": {{"param": "value"}}}}]

User Query: {query}

Tool Calls:"""
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant that excels at function calling. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        print("✅ Dataset example test completed")
        print(f"Query: {query}")
        print(f"Response: {content}")
        
        # Expected answer
        expected = [
            {"name": "live_giveaways_by_type", "arguments": {"type": "beta"}},
            {"name": "live_giveaways_by_type", "arguments": {"type": "game"}}
        ]
        
        print(f"Expected: {json.dumps(expected, indent=2)}")
        return True
        
    except Exception as e:
        print(f"❌ Dataset example test failed: {e}")
        return False

def test_performance(client, model_name, num_requests=5):
    """Test API performance."""
    print(f"🔍 Testing performance with {num_requests} requests...")
    
    times = []
    successful = 0
    
    for i in range(num_requests):
        start_time = time.time()
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": f"Test request {i+1}: What tools would you use for getting weather data?"}
                ],
                max_tokens=100,
                temperature=0.1
            )
            
            end_time = time.time()
            duration = end_time - start_time
            times.append(duration)
            successful += 1
            print(f"  Request {i+1}: {duration:.2f}s")
            
        except Exception as e:
            print(f"  Request {i+1}: Failed - {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"✅ Performance test completed")
        print(f"  Successful requests: {successful}/{num_requests}")
        print(f"  Average time: {avg_time:.2f}s")
        print(f"  Min time: {min_time:.2f}s")
        print(f"  Max time: {max_time:.2f}s")
        print(f"  Estimated throughput: {1/avg_time:.2f} requests/second")
        
        return successful == num_requests
    else:
        print("❌ All performance tests failed")
        return False

def test_curl_equivalent(base_url, model_name):
    """Show equivalent CURL commands."""
    print("🔍 Equivalent CURL commands:")
    
    # Models endpoint
    models_curl = f'''curl -X GET "{base_url}/models" \\
  -H "Content-Type: application/json"'''
    
    # Chat completion
    chat_curl = f'''curl -X POST "{base_url}/chat/completions" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "model": "{model_name}",
    "messages": [
      {{
        "role": "user",
        "content": "Hello, can you help with function calling?"
      }}
    ],
    "temperature": 0.1,
    "max_tokens": 100
  }}'
'''
    
    print("📋 List models:")
    print(models_curl)
    print()
    print("📋 Chat completion:")
    print(chat_curl)
    print()

def main():
    parser = argparse.ArgumentParser(description="Test Arcee Agent API")
    parser.add_argument("--base_url", default="http://127.0.0.1:11434/v1", help="Base URL for API")
    parser.add_argument("--model", default="arcee-ai/arcee-agent", help="Model name")
    parser.add_argument("--api_key", default="dummy", help="API key")
    parser.add_argument("--performance_requests", type=int, default=5, help="Number of performance test requests")
    parser.add_argument("--skip_health", action="store_true", help="Skip health check")
    
    args = parser.parse_args()
    
    print("🚀 Arcee Agent API Test Suite")
    print("=" * 50)
    print(f"Base URL: {args.base_url}")
    print(f"Model: {args.model}")
    print()
    
    # Initialize OpenAI client
    client = OpenAI(base_url=args.base_url, api_key=args.api_key)
    
    # Run tests
    tests_passed = 0
    total_tests = 0
    
    # Health check (optional)
    if not args.skip_health:
        total_tests += 1
        if test_health_endpoint(args.base_url):
            tests_passed += 1
        print()
    
    # Models endpoint
    total_tests += 1
    if test_models_endpoint(client):
        tests_passed += 1
    print()
    
    # Simple completion
    total_tests += 1
    if test_simple_completion(client, args.model):
        tests_passed += 1
    print()
    
    # Function calling
    total_tests += 1
    if test_function_calling(client, args.model):
        tests_passed += 1
    print()
    
    # Dataset example
    total_tests += 1
    if test_dataset_example(client, args.model):
        tests_passed += 1
    print()
    
    # Performance test
    total_tests += 1
    if test_performance(client, args.model, args.performance_requests):
        tests_passed += 1
    print()
    
    # Show CURL equivalents
    test_curl_equivalent(args.base_url, args.model)
    
    # Summary
    print("📊 Test Results")
    print("=" * 50)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    print(f"Success rate: {100 * tests_passed / total_tests:.1f}%")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! API is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
