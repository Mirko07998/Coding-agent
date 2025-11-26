import unittest
from hello_world import print_hello_world
from unittest.mock import patch

class TestHelloWorld(unittest.TestCase):
    @patch('builtins.print')
    def test_print_hello_world(self, mock_print):
        """
        Test the print_hello_world function to ensure it prints 'Hello, World!'.
        """
        print_hello_world()
        mock_print.assert_called_once_with("Hello, World!")

if __name__ == "__main__":
    unittest.main()