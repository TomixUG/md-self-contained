import unittest
import os
import sys
import tempfile
import shutil
import base64
from unittest.mock import patch

# Ensure the parent directory is in the python path to import embed_images
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from embed_images import embed_images_in_markdown, find_vault_root, main

class TestEmbedImages(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory structure for testing
        self.test_dir = tempfile.mkdtemp()
        self.vault_dir = os.path.join(self.test_dir, 'vault')
        os.makedirs(self.vault_dir)
        
        # Create .obsidian folder to mark it as a vault
        os.makedirs(os.path.join(self.vault_dir, '.obsidian'))
        
        # Create an images folder inside the vault
        self.images_dir = os.path.join(self.vault_dir, 'images')
        os.makedirs(self.images_dir)
        
        # Create a dummy image
        self.dummy_image_path = os.path.join(self.images_dir, 'test_image.png')
        self.dummy_image_content = b'fake_image_data'
        with open(self.dummy_image_path, 'wb') as f:
            f.write(self.dummy_image_content)
            
        self.expected_base64 = base64.b64encode(self.dummy_image_content).decode('utf-8')
        
        # Note directory inside vault
        self.notes_dir = os.path.join(self.vault_dir, 'notes')
        os.makedirs(self.notes_dir)

    def tearDown(self):
        # Clean up the temporary directory
        shutil.rmtree(self.test_dir)

    def test_find_vault_root(self):
        root = find_vault_root(self.notes_dir)
        self.assertEqual(root, self.vault_dir)

    def test_obsidian_syntax(self):
        md_content = "Here is an image: ![[test_image.png]]"
        result = embed_images_in_markdown(md_content, base_dir=self.notes_dir)
        
        expected_md = f"Here is an image: ![test_image.png](data:image/png;base64,{self.expected_base64})"
        self.assertEqual(result, expected_md)
        
    def test_obsidian_syntax_with_alt(self):
        md_content = "Here is an image: ![[test_image.png|Alt Text]]"
        result = embed_images_in_markdown(md_content, base_dir=self.notes_dir)
        
        expected_md = f"Here is an image: ![Alt Text](data:image/png;base64,{self.expected_base64})"
        self.assertEqual(result, expected_md)

    def test_standard_markdown_syntax(self):
        md_content = "Here is an image: ![Alt Text](../images/test_image.png)"
        result = embed_images_in_markdown(md_content, base_dir=self.notes_dir)
        
        expected_md = f"Here is an image: ![Alt Text](data:image/png;base64,{self.expected_base64})"
        self.assertEqual(result, expected_md)
        
    def test_missing_image(self):
        md_content = "Here is an image: ![[missing.png]]"
        result = embed_images_in_markdown(md_content, base_dir=self.notes_dir)
        self.assertEqual(result, md_content)

    @patch('sys.argv')
    def test_cli_default_output(self, mock_argv):
        # Create a test markdown file
        md_file_path = os.path.join(self.notes_dir, 'test_note.md')
        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write("![[test_image.png]]")
            
        # Mock sys.argv as if running: python embed_images.py test_note.md
        mock_argv.__getitem__.side_effect = lambda x: ['embed_images.py', md_file_path][x]
        mock_argv.__len__.return_value = 2
        mock_argv.__iter__.return_value = iter(['embed_images.py', md_file_path])
        mock_argv.pop.side_effect = lambda x=None: None
        # Better to just set it:
        
    @patch('sys.argv')
    def test_cli_default_output_clean(self, mock_argv):
        md_file_path = os.path.join(self.notes_dir, 'test_note.md')
        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write("![[test_image.png]]")
            
        # Just mock sys.argv directly by replacing the list
        with patch('sys.argv', ['embed_images.py', md_file_path]):
            main()
            
        expected_output_path = os.path.join(self.notes_dir, 'test_note.embedded.md')
        self.assertTrue(os.path.exists(expected_output_path))
        
        with open(expected_output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('data:image/png;base64', content)

    def test_cli_custom_output_folder(self):
        md_file_path = os.path.join(self.notes_dir, 'test_note.md')
        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write("![[test_image.png]]")
            
        custom_out_dir = os.path.join(self.test_dir, 'custom_output')
        
        with patch('sys.argv', ['embed_images.py', md_file_path, '-o', custom_out_dir]):
            main()
            
        expected_output_path = os.path.join(custom_out_dir, 'test_note.embedded.md')
        self.assertTrue(os.path.exists(expected_output_path))
        
        with open(expected_output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('data:image/png;base64', content)

if __name__ == '__main__':
    unittest.main()
