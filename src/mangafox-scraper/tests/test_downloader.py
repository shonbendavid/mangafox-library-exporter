import unittest
from src.downloader import Downloader

class TestDownloader(unittest.TestCase):

    def setUp(self):
        self.downloader = Downloader()

    def test_download_content(self):
        # Assuming we have a method to mock the content
        content = "Test content"
        file_path = "test_output.txt"
        self.downloader.download_content(content, file_path)
        
        with open(file_path, 'r') as file:
            saved_content = file.read()
        
        self.assertEqual(saved_content, content)

    def test_save_to_file(self):
        content = "Another test content"
        file_path = "test_save_output.txt"
        self.downloader.save_to_file(content, file_path)
        
        with open(file_path, 'r') as file:
            saved_content = file.read()
        
        self.assertEqual(saved_content, content)

    def tearDown(self):
        import os
        try:
            os.remove("test_output.txt")
            os.remove("test_save_output.txt")
        except FileNotFoundError:
            pass

if __name__ == '__main__':
    unittest.main()