import unittest
import io
import os
import tempfile
import zipfile
from pathlib import Path
from PIL import Image
from src.core.optimizer.models import OptimizerProfile
from src.core.optimizer.color_detector import ColorDetector
from src.core.optimizer.image_pipeline import ImagePipeline
from src.core.optimizer.estimator import FastSamplingEstimator
from src.core.optimizer.archive_optimizer import ArchiveOptimizer

class TestOptimizer(unittest.TestCase):

    def test_color_detector_grayscale(self):
        # 1. Pure grayscale image
        gray_img = Image.new('L', (100, 100), color=128)
        self.assertTrue(ColorDetector.is_grayscale(gray_img))

        # 2. RGB image with identical R,G,B values (Monochrome in RGB container)
        mono_rgb = Image.new('RGB', (100, 100), color=(128, 128, 128))
        self.assertTrue(ColorDetector.is_grayscale(mono_rgb))

        # 3. Vivid colorful image
        color_img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        self.assertFalse(ColorDetector.is_grayscale(color_img))

    def test_image_pipeline_webp(self):
        color_img = Image.new('RGB', (3000, 2000), color=(200, 100, 50))
        buf = io.BytesIO()
        color_img.save(buf, format='JPEG', quality=95)
        raw_bytes = buf.getvalue()

        profile = OptimizerProfile(
            target_format="webp",
            quality=75,
            cover_quality=90,
            max_dimension=2160,
            auto_grayscale=True
        )

        # Process inner page
        opt_bytes, ext, was_gray = ImagePipeline.process_image(raw_bytes, "002.jpg", is_cover=False, profile=profile)
        self.assertEqual(ext, ".webp")
        self.assertLess(len(opt_bytes), len(raw_bytes))

        # Verify downsampled dimensions
        res_img = Image.open(io.BytesIO(opt_bytes))
        self.assertLessEqual(max(res_img.size), 2160)

    def test_archive_optimizer_and_estimator(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            cbz_path = tmp_path / "test_manga.cbz"

            # Create test comic archive with 5 pages
            with zipfile.ZipFile(cbz_path, 'w') as zf:
                for i in range(5):
                    # Cover is colorful, inner pages are monochrome
                    color = (255, 100, 50) if i == 0 else (128, 128, 128)
                    img = Image.new('RGB', (1200, 1800), color=color)
                    buf = io.BytesIO()
                    img.save(buf, format='JPEG', quality=95)
                    zf.writestr(f"page_{i:02d}.jpg", buf.getvalue())
                zf.writestr("ComicInfo.xml", b"<ComicInfo><Title>Test</Title></ComicInfo>")

            profile = OptimizerProfile.preset_extreme_webp()
            profile.output_mode = "suffix"
            profile.output_suffix = "_opt"

            # 1. Test Fast Estimator
            est = FastSamplingEstimator.estimate_archive(str(cbz_path), profile)
            self.assertEqual(est["total_images"], 5)
            self.assertGreater(est["saved_ratio"], 0.0)

            # 2. Test Full Archive Optimizer
            stats = ArchiveOptimizer.optimize_archive(str(cbz_path), profile)
            self.assertTrue(stats.success)
            self.assertEqual(stats.total_images, 5)
            self.assertGreater(stats.saved_ratio, 0.0)
            self.assertTrue(os.path.exists(stats.output_path))

            # Verify ComicInfo.xml was preserved
            with zipfile.ZipFile(stats.output_path, 'r') as out_z:
                self.assertIn("ComicInfo.xml", out_z.namelist())
                self.assertIn("page_00.webp", out_z.namelist())

if __name__ == '__main__':
    unittest.main()
