import unittest
from io import StringIO
import sys
from hello_world import print_hello_world

class TestHelloWorld(unittest.TestCase):
    """
    Unit test class to test the functionality of the hello_world module.
    """

    def test_print_hello_world(self):
        """
        Test that the print_hello_world function outputs 'Hello, World!'
        """
        # Redirect stdout to capture print statements
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Call the function
        print_hello_world()
        
        # Reset redirect.
        sys.stdout = sys.__stdout__
        
        # Check if the output is as expected
        self.assertEqual(captured_output.getvalue().strip(), 'Hello, World!')

if __name__ == "__main__":
    unittest.main()