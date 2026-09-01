import unittest
import os
import tempfile
import zipfile
from pathlib import Path
from src.core.archive_manager import ArchiveManager
from src.core.i18n import i18n
from src.core.utils import is_image_file

class TestCore(unittest.TestCase):

    def test_i18n(self):
        i18n.set_lang('zh')
        self.assertEqual(i18n.get('app_title'), '漫画工具箱')
        i18n.set_lang('en')
        self.assertEqual(i18n.get('app_title'), 'Comic Utilities')

    def test_image_file_detection(self):
        self.assertTrue(is_image_file('page01.jpg'))
        self.assertTrue(is_image_file('page02.png'))
        self.assertTrue(is_image_file('page03.webp'))
        self.assertFalse(is_image_file('readme.txt'))
        self.assertFalse(is_image_file('data.json'))

    def test_archive_pack_and_extract(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            
            # Create dummy images
            src_folder = tmp_path / "chapter_01"
            src_folder.mkdir()
            (src_folder / "01.jpg").write_bytes(b"image_1")
            (src_folder / "02.jpg").write_bytes(b"image_2")

            # Pack to CBZ
            cbz_out = tmp_path / "chapter_01.cbz"
            ArchiveManager.create_archive(src_folder, cbz_out, "cbz")
            self.assertTrue(cbz_out.exists())

            # Extract from CBZ
            extract_folder = tmp_path / "extracted"
            ArchiveManager.extract_archive(cbz_out, extract_folder)
            self.assertTrue((extract_folder / "01.jpg").exists())
            self.assertTrue((extract_folder / "02.jpg").exists())

if __name__ == '__main__':
    unittest.main()
