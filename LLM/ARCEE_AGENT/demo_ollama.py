#!/usr/bin/env python3
"""
Simple demonstration of Arcee Agent function calling with Ollama

This script shows how to use Ollama to run the Arcee Agent model locally
and perform function calling on a small sample.
"""

import json
import subprocess
import time
import sys
import os
from openai import OpenAI

def check_ollama_installed():
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def pull_arcee_agent():
    """Pull the Arcee Agent model with Ollama."""
    print("Pulling Arcee Agent model with Ollama...")
    try:
        result = subprocess.run(['ollama', 'pull', 'arcee-ai/arcee-agent'], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✓ Arcee Agent model pulled successfully!")
            return True
        else:
            print(f"✗ Failed to pull model: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ Timeout while pulling model")
        return False
    except Exception as e:
        print(f"✗ Error pulling model: {e}")
        return False

def start_ollama_server():
    """Start Ollama server in the background."""
    print("Starting Ollama server...")
    try:
        # Check if server is already running
        client = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="dummy")
        client.models.list()
        print("✓ Ollama server is already running!")
        return True
    except:
        pass
    
    try:
        # Start server in background
        subprocess.Popen(['ollama', 'serve'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        # Wait for server to start
        for i in range(10):
            try:
                time.sleep(2)
                client = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="dummy")
                client.models.list()
                print("✓ Ollama server started successfully!")
                return True
            except:
                print(f"Waiting for server to start... ({i+1}/10)")
                continue
        
        print("✗ Failed to start Ollama server")
        return False
    except Exception as e:
        print(f"✗ Error starting server: {e}")
        return False

def test_function_calling():
    """Test function calling with a simple example."""
    print("\\nTesting function calling with Arcee Agent...")
    
    # Sample data
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
    
    # Create prompt
    tools_str = json.dumps(tools, indent=2)
    prompt = f"""You are an AI assistant with access to the following tools:

{tools_str}

Based on the user's query, determine which tool(s) to call and with what arguments.
Your response should be a JSON array of tool calls in the format:
[{{"name": "tool_name", "arguments": {{"param": "value"}}}}]

User Query: {query}

Tool Calls:"""
    
    print(f"Query: {query}")
    print(f"Available tools: {tools[0]['name']}")
    
    try:
        client = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="dummy")
        
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant that excels at function calling. Always respond with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="arcee-ai/arcee-agent",
            temperature=0.1,
            max_tokens=512,
        )
        
        response_text = response.choices[0].message.content
        print(f"\\nModel response:")
        print(response_text)
        
        # Try to parse the response
        try:
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                tool_calls = json.loads(json_str)
                print(f"\\nParsed tool calls:")
                print(json.dumps(tool_calls, indent=2))
                return True
            else:
                print("\\n⚠️  Could not find JSON array in response")
                return False
        except json.JSONDecodeError as e:
            print(f"\\n⚠️  Could not parse tool calls: {e}")
            return False
            
    except Exception as e:
        print(f"\\n✗ Error calling model: {e}")
        return False

def main():
    """Main demonstration function."""
    print("Arcee Agent Function Calling Demo with Ollama")
    print("=" * 50)
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        print("✗ Ollama is not installed or not in PATH")
        print("Please install Ollama from: https://ollama.ai/")
        sys.exit(1)
    
    print("✓ Ollama is installed")
    
    # Pull Arcee Agent model
    if not pull_arcee_agent():
        print("\\nFailed to pull Arcee Agent model. You can try manually:")
        print("ollama pull arcee-ai/arcee-agent")
        sys.exit(1)
    
    # Start Ollama server
    if not start_ollama_server():
        print("\\nFailed to start Ollama server. You can try manually:")
        print("ollama serve")
        sys.exit(1)
    
    # Test function calling
    if test_function_calling():
        print("\\n🎉 Function calling demo completed successfully!")
        print("\\nYou can now run the full script with:")
        print("python main.py --model arcee-ai/arcee-agent --base_url http://127.0.0.1:11434/v1 --max_samples 5")
    else:
        print("\\n⚠️  Function calling demo had issues, but the setup is complete.")
        print("You can still try running the full script.")

if __name__ == "__main__":
    main()
