import unittest
import os
import tempfile
import shutil
import base64
from embed_images import embed_images_in_markdown, find_vault_root

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
        # For standard markdown, it usually expects relative path to the image
        md_content = "Here is an image: ![Alt Text](../images/test_image.png)"
        result = embed_images_in_markdown(md_content, base_dir=self.notes_dir)
        
        expected_md = f"Here is an image: ![Alt Text](data:image/png;base64,{self.expected_base64})"
        self.assertEqual(result, expected_md)
        
    def test_missing_image(self):
        md_content = "Here is an image: ![[missing.png]]"
        # It should leave the markdown unchanged if the image is missing
        result = embed_images_in_markdown(md_content, base_dir=self.notes_dir)
        
        self.assertEqual(result, md_content)

if __name__ == '__main__':
    unittest.main()
