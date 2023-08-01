import os
import sys
import unittest
from src.helpers import resource_path


class ResourcePathTest(unittest.TestCase):

    def test_relative_path_no_parent(self):
        relative_path = "file.txt"
        expected_path = os.path.join(os.path.abspath("."), relative_path)
        self.assertEqual(resource_path(relative_path), expected_path)

    def test_relative_path_with_parent(self):
        relative_path = os.path.join("folder", "file.txt")
        expected_path = os.path.join(os.path.abspath("."), relative_path)
        self.assertEqual(resource_path(relative_path), expected_path)

    def test_with_sys_meipass(self):
        # Simulate that sys._MEIPASS is set
        sys._MEIPASS = "/some/directory"
        relative_path = "file.txt"
        expected_path = os.path.join(sys._MEIPASS, relative_path)
        self.assertEqual(resource_path(relative_path), expected_path)

    def test_without_sys_meipass(self):
        # Ensure that sys._MEIPASS is not set
        if hasattr(sys, '_MEIPASS'):
            del sys._MEIPASS

        relative_path = "file.txt"
        expected_path = os.path.join(os.path.abspath("."), relative_path)
        self.assertEqual(resource_path(relative_path), expected_path)

    def test_relative_path_parent_access(self):
        relative_path = os.path.join("..", "file.txt")
        expected_path = os.path.join(os.path.abspath("."), relative_path)
        self.assertEqual(resource_path(relative_path), expected_path)

    def test_relative_path_absolute_components(self):
        relative_path = os.path.join("/absolute_path", "file.txt")
        expected_path = os.path.join(os.path.abspath("."), relative_path)
        self.assertEqual(resource_path(relative_path), expected_path)

    def test_nonexistent_relative_path(self):
        relative_path = "nonexistent_file.txt"
        expected_path = os.path.join(os.path.abspath("."), relative_path)
        self.assertEqual(resource_path(relative_path), expected_path)


if __name__ == "__main__":
    unittest.main()
