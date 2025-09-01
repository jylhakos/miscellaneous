def find_unique_pairs_with_equal_sum(arr):
    """
    Find all unique pairs of numbers in an unsorted array with equal sum.
    
    Args:
        arr: List of numbers
    
    Returns:
        Dictionary where keys are sums and values are lists of pairs with that sum
    """
    n = len(arr)
    sum_pairs = {}
    
    # Generate all possible pairs and group them by sum
    for i in range(n):
        for j in range(i + 1, n):
            pair_sum = arr[i] + arr[j]
            pair = (min(arr[i], arr[j]), max(arr[i], arr[j]))  # Store in sorted order to avoid duplicates
            
            if pair_sum not in sum_pairs:
                sum_pairs[pair_sum] = []
            
            # Only add if this exact pair is not already in the list
            if pair not in sum_pairs[pair_sum]:
                sum_pairs[pair_sum].append(pair)
    
    # Filter to only include sums that have more than one unique pair
    result = {sum_val: pairs for sum_val, pairs in sum_pairs.items() if len(pairs) > 1}
    
    return result


def print_pairs_with_equal_sum(arr):
    """
    Print all unique pairs with equal sum in the required format.
    
    Args:
        arr: List of numbers
    """
    pairs_by_sum = find_unique_pairs_with_equal_sum(arr)
    
    if not pairs_by_sum:
        print("No pairs with equal sum found.")
        return
    
    # Sort by sum for consistent output
    for sum_val in sorted(pairs_by_sum.keys()):
        pairs = pairs_by_sum[sum_val]
        
        # Format the output as required
        pairs_str = " ".join([f"( {pair[0]}, {pair[1]})" for pair in pairs])
        print(f"Pairs : {pairs_str} have sum : {sum_val}")


def get_user_input():
    """Get array input from user."""
    while True:
        try:
            user_input = input("\nEnter numbers separated by spaces (or 'quit' to exit): ")
            if user_input.lower() == 'quit':
                return None
            
            # Parse the input into a list of numbers
            numbers = [int(x.strip()) for x in user_input.split()]
            return numbers
        except ValueError:
            print("Invalid input. Please enter only numbers separated by spaces.")


def main():
    print("=== Unique Pairs with Equal Sum Finder ===\n")
    
    # Run examples first
    print("Example A:")
    array_a = [6, 4, 12, 10, 22, 54, 32, 42, 21, 11]
    print(f"Input: A[] = {array_a}")
    print("Output:")
    print_pairs_with_equal_sum(array_a)
    
    print("\n" + "="*50 + "\n")
    
    print("Example B:")
    array_b = [4, 23, 65, 67, 24, 12, 86]
    print(f"Input: A[] = {array_b}")
    print("Output:")
    print_pairs_with_equal_sum(array_b)
    
    print("\n" + "="*50 + "\n")
    
    # Interactive mode
    print("Interactive Mode:")
    print("You can now enter your own arrays to find unique pairs with equal sum.")
    
    while True:
        user_array = get_user_input()
        if user_array is None:
            print("Goodbye!")
            break
        
        print(f"\nInput: A[] = {user_array}")
        print("Output:")
        print_pairs_with_equal_sum(user_array)


if __name__ == "__main__":
    main()
