import os
import unittest

from src.helpers import get_downloads_folder_path, center_window


class TestYourModule(unittest.TestCase):

    def setUp(self):
        os.environ['LOCALAPPDATA'] = '/path/to/local/app/data'
        pass

    def test_get_downloads_folder_path(self):
        # Test if get_downloads_folder_path returns correct path
        expected_path = os.path.join(os.environ['USERPROFILE'], 'Downloads')
        self.assertEqual(get_downloads_folder_path(), expected_path)

    def test_center_window(self):
        # Mock the window object
        class MockWindow:
            def __init__(self):
                self.width = 800
                self.height = 600
                self.screen_width = 1920
                self.screen_height = 1080
                self.window_geometry = None

            def winfo_screenwidth(self):
                return self.screen_width

            def winfo_screenheight(self):
                return self.screen_height

            def update_idletasks(self):
                pass

            def geometry(self, geometry):
                self.window_geometry = geometry

        # Create a mock window object
        window = MockWindow()

        # Call the function to center the window
        center_window(window, window.width, window.height)

        # Check if the window geometry is set correctly
        expected_geometry = f"{window.width}x{window.height}+{(window.screen_width - window.width) // 2}+{(window.screen_height - window.height) // 2}"
        self.assertEqual(window.window_geometry, expected_geometry)



if __name__ == '__main__':
    unittest.main()