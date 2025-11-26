CONTENT:
```python
import unittest
from unittest.mock import patch
from hello_world import print_hello_world

class TestHelloWorld(unittest.TestCase):
    """
    Unit tests for the hello_world module.
    """

    @patch('builtins.print')
    def test_print_hello_world(self, mock_print):
        """
        Test that print_hello_world calls print with 'Hello, World!'.
        """
        print_hello_world()
        mock_print.assert_called_once_with("Hello, World!")

if __name__ == '__main__':
    unittest.main()
```