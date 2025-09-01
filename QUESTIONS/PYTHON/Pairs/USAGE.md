# Usage Guide

## Project Setup

A Python 3.12 virtual environment has been created and configured for this project.

## Files

- `unique_pairs.py` - Main script with examples A and B
- `interactive_pairs.py` - Interactive version where you can input your own arrays
- `test_unique_pairs.py` - Unit tests for the implementation
- `requirements.txt` - Dependencies (none required for this project)

## Running the Scripts

### Basic Examples Script
```bash
./.venv/bin/python unique_pairs.py
```

### Interactive Script
```bash
./.venv/bin/python interactive_pairs.py
```

### Running Tests
```bash
./.venv/bin/python -m unittest test_unique_pairs.py -v
```

## An algorithm for the unique pairs in the unsorted array with equal sum

The solution works by:

1. **Generating all possible pairs**: For each element in the array, pair it with every other element that comes after it
2. **Grouping by sum**: Store pairs in a dictionary where the key is the sum and the value is a list of pairs
3. **Avoiding duplicates**: Store pairs in sorted order (smaller number first) to prevent duplicate pairs
4. **Filtering results**: Only return sums that have more than one unique pair
5. **Formatting output**: Display results in the required format

## Time Complexity
- **Time**: O(n²) where n is the length of the array
- **Space**: O(n²) in the worst case for storing all pairs

## Example Usage

The script handles the examples from the requirements:

### Example A
Input: [6, 4, 12, 10, 22, 54, 32, 42, 21, 11]
Output shows 7 different sums with multiple pairs each.

### Example B
Input: [4, 23, 65, 67, 24, 12, 86]
Output shows 1 sum (90) with 2 pairs: (4, 86) and (23, 67).
