#!/usr/bin/env python3
"""
Test script for Arcee Agent Function Calling

This script tests the basic functionality without requiring a full model download.
"""

import json
import sys
import os
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from main import (
    create_function_calling_prompt, 
    parse_tool_calls, 
    validate_dataset_row,
    evaluate_predictions
)

def test_function_calling_prompt():
    """Test the prompt creation function."""
    print("Testing function calling prompt creation...")
    
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
    
    prompt = create_function_calling_prompt(query, tools)
    print("Generated prompt:")
    print(prompt)
    print("✓ Prompt creation test passed\n")


def test_tool_call_parsing():
    """Test the tool call parsing function."""
    print("Testing tool call parsing...")
    
    # Test valid JSON array response
    response1 = '[{"name": "live_giveaways_by_type", "arguments": {"type": "beta"}}]'
    result1 = parse_tool_calls(response1)
    expected1 = [{"name": "live_giveaways_by_type", "arguments": {"type": "beta"}}]
    assert result1 == expected1, f"Expected {expected1}, got {result1}"
    
    # Test single object response
    response2 = '{"name": "live_giveaways_by_type", "arguments": {"type": "game"}}'
    result2 = parse_tool_calls(response2)
    expected2 = [{"name": "live_giveaways_by_type", "arguments": {"type": "game"}}]
    assert result2 == expected2, f"Expected {expected2}, got {result2}"
    
    # Test response with extra text
    response3 = 'Here are the tool calls: [{"name": "test_tool", "arguments": {}}] for your query.'
    result3 = parse_tool_calls(response3)
    expected3 = [{"name": "test_tool", "arguments": {}}]
    assert result3 == expected3, f"Expected {expected3}, got {result3}"
    
    # Test invalid response
    response4 = "This is not a valid JSON response"
    result4 = parse_tool_calls(response4)
    assert result4 == [], f"Expected empty list, got {result4}"
    
    print("✓ Tool call parsing tests passed\n")


def test_dataset_validation():
    """Test the dataset row validation function."""
    print("Testing dataset validation...")
    
    # Valid row
    valid_row = {
        "query": "Test query",
        "tools": '[{"name": "test_tool", "description": "Test tool"}]'
    }
    assert validate_dataset_row(valid_row), "Valid row should pass validation"
    
    # Missing query
    invalid_row1 = {
        "tools": '[{"name": "test_tool", "description": "Test tool"}]'
    }
    assert not validate_dataset_row(invalid_row1), "Row missing query should fail validation"
    
    # Invalid JSON in tools
    invalid_row2 = {
        "query": "Test query",
        "tools": "invalid json"
    }
    assert not validate_dataset_row(invalid_row2), "Row with invalid JSON should fail validation"
    
    print("✓ Dataset validation tests passed\n")


def test_evaluation():
    """Test the evaluation function."""
    print("Testing evaluation...")
    
    # Mock dataset with answers and predictions
    class MockDataset:
        def __init__(self):
            self.column_names = ['answers', 'my_answers']
            self.data = {
                'answers': [
                    '[{"name": "tool1", "arguments": {"param": "value1"}}]',
                    '[{"name": "tool2", "arguments": {"param": "value2"}}]'
                ],
                'my_answers': [
                    '[{"name": "tool1", "arguments": {"param": "value1"}}]',  # Exact match
                    '[{"name": "tool2", "arguments": {"param": "different"}}]'  # Different args
                ]
            }
        
        def __getitem__(self, key):
            return self.data[key]
    
    mock_ds = MockDataset()
    metrics = evaluate_predictions(mock_ds)
    
    expected_tool_accuracy = 1.0  # Both tool names are correct
    expected_exact_match = 0.5    # Only one exact match
    
    assert abs(metrics['tool_accuracy'] - expected_tool_accuracy) < 0.001
    assert abs(metrics['exact_match'] - expected_exact_match) < 0.001
    
    print("✓ Evaluation tests passed\n")


def main():
    """Run all tests."""
    print("Running Arcee Agent Function Calling Tests\n")
    print("=" * 50)
    
    try:
        test_function_calling_prompt()
        test_tool_call_parsing()
        test_dataset_validation()
        test_evaluation()
        
        print("=" * 50)
        print("🎉 All tests passed successfully!")
        print("\nYou can now run the main script with:")
        print("python main.py --help")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
