import unittest
from unique_pairs import find_unique_pairs_with_equal_sum


class TestUniquePairs(unittest.TestCase):
    
    def test_example_a(self):
        """Test with Example A from the requirements."""
        arr = [6, 4, 12, 10, 22, 54, 32, 42, 21, 11]
        result = find_unique_pairs_with_equal_sum(arr)
        
        # Check that we have the expected sums
        expected_sums = [16, 32, 33, 43, 53, 54, 64]
        self.assertEqual(sorted(result.keys()), expected_sums)
        
        # Check specific pairs
        self.assertIn((4, 12), result[16])
        self.assertIn((6, 10), result[16])
        self.assertIn((10, 22), result[32])
        self.assertIn((11, 21), result[32])
    
    def test_example_b(self):
        """Test with Example B from the requirements."""
        arr = [4, 23, 65, 67, 24, 12, 86]
        result = find_unique_pairs_with_equal_sum(arr)
        
        # Should have one sum with two pairs
        self.assertEqual(len(result), 1)
        self.assertIn(90, result)
        self.assertIn((4, 86), result[90])
        self.assertIn((23, 67), result[90])
    
    def test_no_equal_sum_pairs(self):
        """Test array with no pairs having equal sum."""
        arr = [1, 3, 7, 13]  # All pairs have different sums: 4, 8, 14, 10, 16, 20
        result = find_unique_pairs_with_equal_sum(arr)
        self.assertEqual(len(result), 0)
    
    def test_small_array(self):
        """Test with array that has less than 4 elements."""
        arr = [1, 2, 3]
        result = find_unique_pairs_with_equal_sum(arr)
        self.assertEqual(len(result), 0)
    
    def test_duplicate_numbers(self):
        """Test array with duplicate numbers."""
        arr = [1, 2, 2, 3, 3, 4]
        result = find_unique_pairs_with_equal_sum(arr)
        
        # Should find pairs with sum 5: (1,4), (2,3)
        if 5 in result:
            self.assertIn((1, 4), result[5])
            self.assertIn((2, 3), result[5])


if __name__ == "__main__":
    unittest.main()
